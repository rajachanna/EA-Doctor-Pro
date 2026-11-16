# Engineering case study: EA Doctor Pro

## Problem
Developers and end users repeatedly troubleshoot MetaTrader EAs that do not place orders, send invalid parameters, or behave unsafely. A bare retcode is actionable, but only if the user knows which parameter to inspect. Existing web backtest analyzers focus mainly on performance numbers; this project focuses on **diagnostic triage**.

## Solution
A free no-signup browser tool plus installable offline Python CLI. Same three data categories are available: explicit journal trade codes, MQL textual heuristics and simple closed-trade CSV. Results are explainable and make no unsupported profitability claims.

## Implemented
- 28 explicit MT4/MT5 known trade error codes, with concrete follow-up checks
- MQL source patterns for secrets, progressive lots, unbounded loops, OnTick Sleep, DLL imports and obvious trade safeguards
- CSV sample metrics (net P&L, fees, win rate, profit factor, closed trade DD, streaks)
- HTML/CSS browser dashboard with local file access, sample, report export and redacted summary
- Offline Python CLI, JSON/SARIF formats, error thresholds
- CI regression tests, static JS syntax check, wheel packaging

## Trust boundaries
- No execution of arbitrary source text
- No credentials or MT5 account connections required
- No browser source upload
- No guaranteed outcome, broker execution, strategy reproduction, or validated live use

## What is not implemented
- Native EX4/EX5 support or decompilation
- MQL compiler or real MetaTrader terminal validation
- Provider-backed strategy reports, tick replay, or trade execution
- Global SEO ranking, hosting uptime guarantees, paid client acquisition or enterprise deployment

## Distribution and impact measurement
- The source repo demonstrates reproducible engineering.
- The freely usable page on NextGen Tech Solutions is linked from related MT5 help articles and the homepage.
- Real client acquisition must be measured with ethical visitor/referral analytics, verified inquiries and discovery metrics. GitHub stars or web visits do not equal paying customers.

## Suggested future milestones
1. Real user QA with de-identified logs (explicit permission).
2. Native MT5 HTML or XLSX parser built around documented export fixtures.
3. Diff views for before/after logs and EA code risk changes.
4. Additional MQL source rules with documented false-positive test corpora.
5. VS Code extension and optional locally-run MCP server for developers.
