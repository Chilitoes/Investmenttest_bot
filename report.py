# “””
Report Builder

Fetches live prices (if API key set) and generates the full
investment scoring report as a list of Telegram HTML message strings.
“””

import requests
from datetime import datetime
from config import ALPHA_VANTAGE_KEY

# ─── STOCK DATA ────────────────────────────────────────────────────────────────

# Base data: fundamentals, scores, analyst targets

# Prices auto-update if ALPHA_VANTAGE_KEY is set, otherwise use static prices.

STOCKS = {
# ── YOUR PORTFOLIO ──────────────────────────────────────────────────────
“PLTR”: {
“name”: “Palantir Technologies”,
“group”: “YOUR PORTFOLIO”,
“static_price”: 157.00,
“w52high”: 207.52,
“w52low”: 66.12,
“analyst_target”: 186.00,
“ytd”: “+35%”,
“pe”: 241,
“fwd_pe”: 190,
“currency”: “USD”,
# Scores /20 each
“valuation”: 4,
“growth”: 22,
“geo”: 24,
“risk”: 10,
“buy_price”: 12,
“rating”: “HOLD”,
“action”: “HOLD / TRIM”,
“reason”: (
“PLTR is the ultimate Iran-war AI beneficiary — battlefield software demand surging — “
“but 241x P/E means paying 10 years of growth upfront. Hold existing, do NOT add at $157. “
“Consider trimming 20–30% if up significantly from your cost basis.”
),
“entry_note”: “Wait for pullback to $120–130 before adding”,
},
“RTX”: {
“name”: “Raytheon Technologies”,
“group”: “YOUR PORTFOLIO”,
“static_price”: 210.00,
“w52high”: 214.50,
“w52low”: 112.27,
“analyst_target”: 217.00,
“ytd”: “+58%”,
“pe”: 42,
“fwd_pe”: 21,
“currency”: “USD”,
“valuation”: 14,
“growth”: 20,
“geo”: 24,
“risk”: 14,
“buy_price”: 6,
“rating”: “HOLD”,
“action”: “HOLD”,
“reason”: (
“RTX is just 2% from its all-time high ($214.50). Patriot missile demand is surging “
“from Iran conflict — the fundamentals are perfect — but you already own it. “
“Don’t add at ATH. Hold and let the backlog expand.”
),
“entry_note”: “Wait for 10–15% pullback (~$180) to add more”,
},
“DBS”: {
“name”: “DBS Group Holdings”,
“group”: “YOUR PORTFOLIO”,
“static_price”: 55.06,
“w52high”: 60.00,
“w52low”: 35.98,
“analyst_target”: 61.10,
“ytd”: “+22%”,
“pe”: 11,
“fwd_pe”: 10,
“currency”: “SGD”,
“valuation”: 20,
“growth”: 14,
“geo”: 16,
“risk”: 18,
“buy_price”: 16,
“rating”: “BUY”,
“action”: “BUY / HOLD”,
“reason”: (
“DBS at SGD 55 is 8% off its ATH with a 4.46% dividend yield, 10x forward P/E, “
“and analyst target of SGD 61 (11% upside). Asia’s safest bank with growing wealth “
“management. Best entry price in your current portfolio.”
),
“entry_note”: “Solid entry — 11% upside + 4.5% dividend = strong total return”,
},
“AMD”: {
“name”: “Advanced Micro Devices”,
“group”: “YOUR PORTFOLIO”,
“static_price”: 192.00,
“w52high”: 267.08,
“w52low”: 76.48,
“analyst_target”: 145.00,
“ytd”: “-18%”,
“pe”: 95,
“fwd_pe”: 22,
“currency”: “USD”,
“valuation”: 13,
“growth”: 16,
“geo”: 8,
“risk”: 10,
“buy_price”: 15,
“rating”: “HOLD”,
“action”: “REDUCE ⚠️”,
“reason”: (
“Most at-risk stock in your portfolio. Analyst consensus target ($145) is BELOW “
“current price ($192). New U.S. AI chip export restrictions hit AMD harder than NVDA. “
“Losing data center GPU market share to NVIDIA. Consider reducing position size.”
),
“entry_note”: “Analyst target BELOW price — export restrictions = structural headwind”,
},
“XOM”: {
“name”: “Exxon Mobil”,
“group”: “YOUR PORTFOLIO”,
“static_price”: 151.00,
“w52high”: 159.61,
“w52low”: 97.80,
“analyst_target”: 130.00,
“ytd”: “+25%”,
“pe”: 14,
“fwd_pe”: 13,
“currency”: “USD”,
“valuation”: 17,
“growth”: 18,
“geo”: 22,
“risk”: 15,
“buy_price”: 10,
“rating”: “HOLD”,
“action”: “HOLD”,
“reason”: (
“XOM up 25% YTD and only 5% from ATH on oil >$90 Hormuz premium. “
“Outstanding business — 2.68% dividend, Permian growth — but the trade has “
“largely played out. Hold what you have, wait for $140 dip to add.”
),
“entry_note”: “Don’t chase at ATH — wait for $140 entry”,
},
# ── RESEARCH UNIVERSE ────────────────────────────────────────────────────
“LMT”: {
“name”: “Lockheed Martin”,
“group”: “RESEARCH”,
“static_price”: 677.00,
“w52high”: 692.00,
“w52low”: 410.11,
“analyst_target”: 619.00,
“ytd”: “+38%”,
“pe”: 31,
“fwd_pe”: 22,
“currency”: “USD”,
“valuation”: 12,
“growth”: 20,
“geo”: 24,
“risk”: 14,
“buy_price”: 5,
“rating”: “HOLD”,
“action”: “HOLD — wait for pullback”,
“reason”: (
“LMT is the Iran war’s biggest defence beneficiary — F-35, hypersonic missiles, “
“$12B new contracts — BUT at $677 it has SURPASSED analyst consensus of $619. “
“Great company, wrong price. Wait for pullback below $620 to enter.”
),
“entry_note”: “Analyst target BELOW current price — wait for pullback”,
},
“GLD”: {
“name”: “SPDR Gold ETF”,
“group”: “RESEARCH”,
“static_price”: 278.00,
“w52high”: 285.00,
“w52low”: 205.00,
“analyst_target”: 310.00,
“ytd”: “+12%”,
“pe”: None,
“fwd_pe”: None,
“currency”: “USD”,
“valuation”: 16,
“growth”: 18,
“geo”: 25,
“risk”: 21,
“buy_price”: 14,
“rating”: “BUY”,
“action”: “BUY”,
“reason”: (
“Gold at all-time highs but the breakout is structural: central bank accumulation “
“at record pace, Hormuz risk premium, negative real rates. GLD remains a BUY “
“even near highs — this is not just a war spike.”
),
“entry_note”: “Structural breakout — central banks + geopolitics support price”,
},
“NVDA”: {
“name”: “NVIDIA Corporation”,
“group”: “RESEARCH”,
“static_price”: 118.00,
“w52high”: 153.00,
“w52low”: 86.00,
“analyst_target”: 175.00,
“ytd”: “-15%”,
“pe”: 35,
“fwd_pe”: 25,
“currency”: “USD”,
“valuation”: 14,
“growth”: 22,
“geo”: 11,
“risk”: 13,
“buy_price”: 17,
“rating”: “BUY”,
“action”: “BUY 💎”,
“reason”: (
“NVDA pulled back 23% from highs to $118 while analyst target is $175 (48% upside). “
“AI infrastructure thesis is intact — domestic data center demand is immune to export “
“rules. This pullback is the best NVDA entry in 12 months.”
),
“entry_note”: “Best AI chip entry in 12 months — 48% upside to analyst target”,
},
“MSFT”: {
“name”: “Microsoft Corporation”,
“group”: “RESEARCH”,
“static_price”: 409.00,
“w52high”: 555.45,
“w52low”: 344.79,
“analyst_target”: 596.00,
“ytd”: “-15%”,
“pe”: 32,
“fwd_pe”: 28,
“currency”: “USD”,
“valuation”: 14,
“growth”: 19,
“geo”: 14,
“risk”: 16,
“buy_price”: 18,
“rating”: “BUY”,
“action”: “BUY 💎”,
“reason”: (
“MSFT at $409 is 26% off its $555 ATH with a consensus target of $596 (45% upside). “
“Azure growing 37–38%, Copilot monetising. Best big-tech entry point in 18 months. “
“If you’re not in MSFT yet, this is the window.”
),
“entry_note”: “Best big-tech entry in 18 months — 45% upside”,
},
“XLE”: {
“name”: “Energy Select ETF”,
“group”: “RESEARCH”,
“static_price”: 108.00,
“w52high”: 115.00,
“w52low”: 78.00,
“analyst_target”: 120.00,
“ytd”: “+27%”,
“pe”: 12,
“fwd_pe”: 11,
“currency”: “USD”,
“valuation”: 19,
“growth”: 16,
“geo”: 21,
“risk”: 17,
“buy_price”: 12,
“rating”: “HOLD”,
“action”: “HOLD”,
“reason”: (
“XLE up 27% YTD on oil >$90 — the energy ETF trade has mostly played out at sector level. “
“Individual names (XOM, OXY) are better vehicles. XLE near 52-week high limits new entry upside.”
),
“entry_note”: “Oil tailwind real but ETF already priced in — prefer individual names”,
},
}

CRITERIA = [“valuation”, “growth”, “geo”, “risk”, “buy_price”]
CRITERIA_LABELS = {
“valuation”: “Valuation”,
“growth”: “Growth”,
“geo”: “Geo Resilience”,
“risk”: “Risk/Reward”,
“buy_price”: “Buy Price Now”,
}

def get_live_price(ticker: str) -> float | None:
“”“Fetch live price from Alpha Vantage (free tier).”””
if not ALPHA_VANTAGE_KEY:
return None
try:
url = (
f”https://www.alphavantage.co/query”
f”?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}”
)
r = requests.get(url, timeout=10)
data = r.json()
price_str = data.get(“Global Quote”, {}).get(“05. price”, “”)
return float(price_str) if price_str else None
except Exception:
return None

def get_price(ticker: str, data: dict) -> float:
“”“Get live price or fall back to static.”””
live = get_live_price(ticker)
return live if live else data[“static_price”]

def score_total(data: dict) -> int:
return sum(data[c] for c in CRITERIA)

def pct_from_high(price: float, high: float) -> float:
return round(((price - high) / high) * 100, 1)

def rating_emoji(rating: str) -> str:
return {“BUY”: “🟢”, “HOLD”: “🟡”, “SELL”: “🔴”}.get(rating, “⚪”)

def entry_label(buy_price_score: int) -> str:
if buy_price_score >= 16:
return “✅ GOOD ENTRY”
elif buy_price_score >= 11:
return “⚠️ FAIR ENTRY”
else:
return “❌ POOR ENTRY”

def score_bar(score: int, max_score: int = 100) -> str:
“”“Text progress bar for score.”””
filled = round((score / max_score) * 10)
empty = 10 - filled
return “█” * filled + “░” * empty

def build_full_report() -> list[str]:
“””
Returns a list of Telegram HTML message strings.
Split into multiple messages to avoid Telegram’s 4096 char limit.
“””
now = datetime.utcnow().strftime(”%d %b %Y • %H:%M UTC”)
messages = []

```
# ── MESSAGE 1: Header + Portfolio Summary ─────────────────────────────
portfolio_tickers = [t for t, d in STOCKS.items() if d["group"] == "YOUR PORTFOLIO"]
prices = {t: get_price(t, STOCKS[t]) for t in portfolio_tickers}

portfolio_rows = []
for t in portfolio_tickers:
    d = STOCKS[t]
    p = prices[t]
    total = score_total(d)
    pfh = pct_from_high(p, d["w52high"])
    cur = d["currency"]
    portfolio_rows.append(
        f"{rating_emoji(d['rating'])} <b>{t}</b> {cur}{p:,.2f}  "
        f"<code>{score_bar(total)}</code>  <b>{total}/100</b>  "
        f"({pfh:+.1f}% from ATH)"
    )

msg1 = (
    f"📊 <b>DAILY INVESTMENT REPORT</b>\n"
    f"<i>{now}</i>\n"
    f"━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"🌍 <b>CONTEXT:</b> Middle East conflict elevated • Oil &gt;$90 • "
    f"Fed holding 4.25–4.5% • VIX ~28\n\n"
    f"💼 <b>YOUR PORTFOLIO</b>\n"
    + "\n".join(portfolio_rows) +
    f"\n\n<i>Scoring: Valuation + Growth + Geo Resilience + Risk/Reward + Buy Price Now — each /20</i>"
)
messages.append(msg1)

# ── MESSAGE 2: Portfolio Deep Dive ────────────────────────────────────
portfolio_detail = "💼 <b>PORTFOLIO DETAIL</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
for t in portfolio_tickers:
    d = STOCKS[t]
    p = prices[t]
    total = score_total(d)
    pfh = pct_from_high(p, d["w52high"])
    upside = round(((d["analyst_target"] - p) / p) * 100, 1)
    cur = d["currency"]

    portfolio_detail += (
        f"{rating_emoji(d['rating'])} <b>{t}</b> — {d['name']}\n"
        f"  Price: <b>{cur}{p:,.2f}</b>  |  ATH: {cur}{d['w52high']:,.2f}  |  "
        f"From ATH: <b>{pfh:+.1f}%</b>\n"
        f"  Analyst Target: {cur}{d['analyst_target']} (<b>{upside:+.1f}%</b> upside)\n"
        f"  Score: <b>{total}/100</b>  {score_bar(total)}  "
        f"→ {entry_label(d['buy_price'])}\n"
        f"  Action: <b>{d['action']}</b>\n"
        f"  <i>{d['entry_note']}</i>\n\n"
    )
messages.append(portfolio_detail.strip())

# ── MESSAGE 3: Research Universe ──────────────────────────────────────
research_tickers = [t for t, d in STOCKS.items() if d["group"] == "RESEARCH"]
research_prices = {t: get_price(t, STOCKS[t]) for t in research_tickers}

research_msg = "📡 <b>RESEARCH UNIVERSE</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
sorted_research = sorted(
    research_tickers,
    key=lambda t: score_total(STOCKS[t]),
    reverse=True
)
for t in sorted_research:
    d = STOCKS[t]
    p = research_prices[t]
    total = score_total(d)
    pfh = pct_from_high(p, d["w52high"])
    upside = round(((d["analyst_target"] - p) / p) * 100, 1)

    research_msg += (
        f"{rating_emoji(d['rating'])} <b>{t}</b> — {d['name']}\n"
        f"  ${p:,.2f}  |  From ATH: {pfh:+.1f}%  |  "
        f"Analyst PT: ${d['analyst_target']} ({upside:+.1f}%)\n"
        f"  Score: <b>{total}/100</b>  {score_bar(total)}  "
        f"→ {entry_label(d['buy_price'])}\n"
        f"  <b>{d['action']}</b>  •  <i>{d['entry_note']}</i>\n\n"
    )
messages.append(research_msg.strip())

# ── MESSAGE 4: Full Leaderboard ───────────────────────────────────────
all_scored = sorted(
    [(t, score_total(d), d) for t, d in STOCKS.items()],
    key=lambda x: x[1],
    reverse=True
)

leaderboard = "🏆 <b>FULL LEADERBOARD — ALL 10 ASSETS</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
for i, (t, total, d) in enumerate(all_scored, 1):
    portfolio_tag = " 👤" if d["group"] == "YOUR PORTFOLIO" else ""
    leaderboard += (
        f"<b>#{i}</b>  {rating_emoji(d['rating'])} <b>{t}</b>{portfolio_tag}  "
        f"<code>{score_bar(total)}</code>  <b>{total}/100</b>  {d['rating']}\n"
        f"     {entry_label(d['buy_price'])}\n"
    )

leaderboard += (
    "\n<b>SCORE BREAKDOWN KEY</b> (each /20):\n"
    "📌 Valuation  📈 Growth  🌍 Geo Resilience  ⚖️ Risk/Reward  🏷️ Buy Price Now\n\n"
)

# Add score breakdown table
leaderboard += "<b>Detailed Scores:</b>\n"
leaderboard += f"<code>{'Ticker':<6} {'Val':>3} {'Grw':>3} {'Geo':>3} {'Rsk':>3} {'Buy':>3} {'TOT':>3}</code>\n"
for t, total, d in all_scored:
    leaderboard += (
        f"<code>{t:<6} {d['valuation']:>3} {d['growth']:>3} "
        f"{d['geo']:>3} {d['risk']:>3} {d['buy_price']:>3} {total:>3}</code>\n"
    )
messages.append(leaderboard.strip())

# ── MESSAGE 5: CIO Verdict ────────────────────────────────────────────
verdict = (
    "⚖️ <b>CIO FINAL VERDICT</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🏆 <b>TOP BUYS RIGHT NOW:</b>\n"
    "1. 💎 <b>NVDA</b> — Down 23% from ATH, $175 analyst target = <b>48% upside</b>. Best AI chip entry in 12 months.\n"
    "2. 💎 <b>MSFT</b> — Down 26% from ATH, $596 target = <b>45% upside</b>. Best big-tech entry in 18 months.\n"
    "3. 🟡 <b>GLD</b> — Structural gold breakout. Central banks buying + Hormuz premium.\n\n"
    "💼 <b>YOUR PORTFOLIO ACTIONS:</b>\n"
    "✅ <b>DBS</b> — Best entry in portfolio. Add on dips. 4.5% yield + 11% upside.\n"
    "🟡 <b>RTX</b> — Hold. Great stock but 2% from ATH. Don't chase.\n"
    "🟡 <b>XOM</b> — Hold. Up 25% YTD. Wait for $140 to add.\n"
    "🟡 <b>PLTR</b> — Hold/Trim. 241x P/E extreme. Consider taking 20–30% profit.\n"
    "🔴 <b>AMD</b> — Reduce. Analyst target BELOW current price + export rule risk.\n\n"
    "⚠️ <b>AVOID NOW:</b> QQQ, LMT (both above analyst consensus targets)\n\n"
    "📋 <b>STRATEGY:</b>\n"
    "Hold your war-economy exposure (RTX, XOM, PLTR) but deploy new capital into "
    "beaten-down tech (NVDA, MSFT) which have sold off 23–26% with massive analyst upside. "
    "Add GLD as portfolio insurance. Reduce AMD — it faces the most structural headwind.\n\n"
    "🎯 <b>KEY RISKS:</b>\n"
    "• Ceasefire → defence &amp; energy drop 15–25%\n"
    "• AMD export ruling → could push AMD below $150\n"
    "• PLTR earnings miss at 241x P/E → 30–40% crash\n"
    "• Oil below $75 → XOM weakens\n\n"
    "<i>⚠️ Educational purposes only — not financial advice.</i>\n"
    f"<i>Next report: tomorrow at same time</i>"
)
messages.append(verdict)

return messages
```

if **name** == “**main**”:
# Test report generation
sections = build_full_report()
for i, s in enumerate(sections, 1):
print(f”\n{’=’*60}”)
print(f”MESSAGE {i} ({len(s)} chars):”)
print(’=’*60)
# Strip HTML tags for terminal preview
import re
print(re.sub(r’<[^>]+>’, ‘’, s))