# Believe: Agent Command Centre

Personal dashboard for running and monitoring AI-assisted workflows. Opens in a web browser.

## Modules
1. Job application system: CV intake, role targeting, master CV, application pipeline, tracker.
2. Investment researcher (Trading 212): research brief cards with YES/NO; watchlist.

## Rules
- Never invent experience or qualifications in CVs; only reframe what is true.
- Never submit job applications, enter passwords or solve CAPTCHAs. The owner does the final click.
- Investment module presents research and facts with dated sources. No personal financial advice, never place trades.
- Every new skill is reviewed (what it does, access needed, risks) before install, then recorded in `data/skills.json`.
- Personal data (CVs, applications, holdings) lives in `private/` and is git-ignored. Never commit it.

## Day to day
- Start/serve: desktop icon or `scripts/launch.pyw` → `scripts/server.py` (127.0.0.1:8765 only).
- Jobs: `scripts/jobs.py` (import/score/tailor), skill `import-job-alerts`, scheduled weekdays 8am.
- Investments: `scripts/invest.py` (cards, Trading 212 read-only check), skill `research-investments`, scheduled Mondays 9am.
- User guide: `MARC/guide.html`. Keep it in sync when behaviour changes.

## Layout
- `MARC/`: the dashboard page (published via GitHub Pages; public, so never put personal data in it)
- `.claude/skills/`: installed skills
- `.claude/commands/`: slash commands (`/generate-prp`, `/execute-prp`)
- `PRPs/`: build plans; `docs/`: reference material and licences
- `data/skills.json`: installed-skills registry shown in the dashboard
