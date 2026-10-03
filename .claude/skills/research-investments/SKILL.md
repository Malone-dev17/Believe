---
name: research-investments
description: Research potential investments for the M.A.R.C Investment Researcher (Trading 212 Stocks & Shares ISA) and add them as brief cards with YES/NO decisions. Use when the user says "research new investment ideas", "research <ticker>", or "refresh my research cards".
---

# Research investment ideas for M.A.R.C

You produce **research and facts, not personal financial advice**. Never tell the user to buy, sell or hold. Never place trades or touch any order function. The user decides with YES/NO.

## Inputs
- `private/profile.json` → `investing`: goal, risk, horizon, account (Stocks & Shares ISA), asset types, markets, current holdings and watchlist. Read it so cards can state facts about overlap (e.g. "VWRP already holds ~60% US"). Overlap is a fact, not a recommendation.
- `private/invest/cards.json`: existing cards. Don't duplicate.

## Picking candidates
Match the user's stated scope (asset types and markets in the profile). The user prefers **individual stocks** (set 3 Oct 2026), so batches are stocks unless they ask for ETFs. Within a batch, vary sector and region (UK, US, Europe, emerging markets), and include at least one company outside AI, chips and data centres, because their holdings are already concentrated there. Don't repeat any company that already has a card. You may also research names on their "watching" list when asked.

Every stock card must state its largest documented fall against the user's 20% limit. Stocks are more volatile than funds: say so plainly, without telling the user what to do.

## Each card needs (scripts/invest.py rejects cards without them)
- `name`, `ticker` (LSE or US symbol), `isin` if known, `type` (ETF / Stock / Investment trust)
- `what`: 1–2 plain sentences
- `numbers`: list of `{label, value}`. Stocks: price, market cap, P/E or EV/EBITDA, dividend yield, 1-yr and 5-yr return. ETFs: price, ongoing charge (OCF/TER), fund size, number of holdings, distribution (Acc/Dist), 1-yr and 5-yr return. Add the largest peak-to-trough fall you can source (the user's stated limit is 20%).
- `data_as_of`: the date the figures refer to
- `case_for` and `case_against`: 2–4 bullets each, balanced, specific
- `risks`: 2–4 bullets
- `portfolio_note` (optional): factual overlap with current holdings
- `sources`: at least 2 reputable sources (company filings/IR, ETF provider factsheet/KID, regulator, major financial press, analyst coverage summaries), each `{title, url, date}`. Use the date of the page or data.

## Checking Trading 212
Run `.venv\Scripts\python.exe scripts\invest.py check <TICKER>` when the instrument list is loaded. If not loaded, the card shows "not yet checked". Never claim availability you haven't verified.

## Adding cards
Pipe JSON (one object or a list) into `.venv\Scripts\python.exe scripts\invest.py add`. Then tell the user how many were added and point them to M.A.R.C → Investments.

## Writing style
Plain English, short sentences, no hype, no em dashes, no "you should". Numbers with units and currency. Use the stop-slop rules.
