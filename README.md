# EA Doctor Pro 🩺

**Privacy-first MetaTrader EA troubleshooting — error logs, source heuristics, and closed-trade evidence.**

**Free live tool:** https://www.nextgentechdev.com/ea-doctor

[![EA Doctor Pro CI](https://github.com/rajachanna/EA-Doctor-Pro/actions/workflows/ci.yml/badge.svg)](https://github.com/rajachanna/EA-Doctor-Pro/actions/workflows/ci.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-66d9b8)](LICENSE)

A reproducible diagnostic utility built by [NextGen Tech Solutions](https://www.nextgentechdev.com/).

> **Not an MT4/MT5 compiler or a live broker/EA tester.** It recognizes explicit trade retcodes, source-code patterns worth reviewing and simple closed-trade statistics. Findings are not guarantees of correctness, safety, future returns or broker compatibility.

## What problem does it solve?

An MT5 EA may fail to trade because of invalid stop distances, unsupported filling modes, volume rules, insufficient margin, account restrictions, missing market ticks or execution error handling. Many users have the actual error recorded in MetaTrader but don't know what it means.

EA Doctor gives clear **evidence → likely area → next checks**, without inventing strategies or promising guaranteed profits.

## Three analyzers

| Analyzer | Accepts | Delivers |
|---|---|---|
| **Journal error decoder** | UTF-8 MT4/MT5 Experts / Journal text (.log, .txt) | 28 explicit documented error code matches, line numbers, tailored troubleshooting steps |
| **MQL source heuristic review** | Text .mq4 / .mq5 source code | Static risk patterns: hard-coded secrets, progressive sizing, Sleep in OnTick, unbounded loops, DLL imports, missing obvious SL / retcode / magic number / cooldown handling |
| **Closed-trade CSV evidence** | CSV with **profit** or **pnl**, optional commission/swap/fee | Net P&L, win rate, closed-trade money drawdown, profit factor, expectancy, streaks, sample-size and outlier cautions |

**Not supported:** binary EX4/EX5 decompilation, MT5 HTML/XLSX report parsing, MT5 compilation, automatic source fixes, unrestricted uploads, tick simulation or live order execution.

## Use the free browser tool

Open **https://www.nextgentechdev.com/ea-doctor**.

No signup. Paste text or select a local file (up to 2MB). Click **Analyze locally**. You can load synthetic samples, download a JSON finding report or copy a **redacted/safe summary** for a developer.

**Privacy:** `web/app.js` does not fetch, post, stream or upload your pasted source/journal text. All scanning and statistics run in your browser; reports are only downloaded on your own device. The hosting website may serve its HTML/CSS/JS assets and may record ordinary access logs; this claim covers the **input content**.

## Install the offline Python CLI

Python **3.10+**, no paid provider, no broker or data API.

```bash
git clone https://github.com/rajachanna/EA-Doctor-Pro.git
cd EA-Doctor-Pro
python -m venv .venv
. .venv/bin/activate
pip install -e .
ea-doctor samples/example-journal.log
ea-doctor samples/example-ea.mq5 --format json
ea-doctor samples/example-trades.csv --format json
ea-doctor samples/example-ea.mq5 --format sarif --output report.sarif
ea-doctor samples/example-ea.mq5 --fail-on high
```

Windows activate: `.venv\Scripts\activate`.

`--type auto|journal|source|trades`, `--format text|json|sarif`, `--output path` and `--fail-on critical|high|medium|low|none` are supported. `--fail-on` exits 1 when matching severity is present; default exit 0 is not proof of a safe EA. Input maximum 2 MB.

You can incorporate SARIF output into developer CI workflows. SARIF reporting does **not** mean GitHub will necessarily accept all security-severity conventions or that source scanning is a comprehensive security audit.

### CSV format

Plain text UTF-8, English header, one closed trade per row:

```csv
date,profit,commission,swap
2026-11-01,30,-1,0
2026-11-02,-40,-1,0
```

The analyzer adds the optional commission and swap values to the supplied profit. **If the original profit column already includes fees, do not include fees again.** Rows are processed in their existing chronological order; order matters for drawdown and consecutive losses. The tool does not assume a beginning balance and cannot estimate floating/intratrade drawdown.

## Run tests and lint checks

```bash
pip install -e '.[dev]'
pytest -q
node --check web/app.js
```

GitHub Actions runs the tests, checks sample CLI/JSON/SARIF output, validates browser asset syntax and creates an installable Python wheel.

## Architecture

```text
ea_doctor/
  journal.py       MT4 + MT5 retcode signatures and remediation catalog
  source.py        MQL4/MQL5 read-only source heuristics
  trades.py        deterministic closed-trade CSV evidence metrics
  report.py        JSON, plain text and SARIF formatter
  cli.py           offline CLI, file type selection and failure thresholds
web/
  index.html       standalone SEO-friendly browser landing page
  styles.css       responsive, accessible dashboard CSS
  app.js           client-only scanners, safe report export and copy
tests/             regression and privacy/safety tests
samples/           clearly labeled synthetic inputs
.github/workflows/ automated CI
```

### Scope and correctness boundaries

- Every journal error match refers to an **explicit** trade code, not a vague phrase or a claimed root cause.
- MQL warnings are **heuristics**. They can be false positives, and includes/helpers may implement safeguards not visible in a single file.
- CSV statistics are **sample statistics**, not independent account verification. A backtest is not a live trading record.
- Does not request account login, API token, broker password, nor access to financial accounts.
- Never sends proposals or contacts prospective clients automatically.

## Client-facing use

If you need a custom MT4/MT5 EA built or debugged, bring a redacted error summary, editable MQL source, broker demo details and concrete expected behavior to [NextGen Tech Solutions](https://www.nextgentechdev.com/#contact).

**This project is a public free resource, not a claim of verified customer wins or guaranteed leads.**

## Security

Read [SECURITY.md](SECURITY.md). Avoid placing credentials in issue reports or exported logs. The tool has no automated code execution and does not operate an MT5 terminal.

## License

MIT · Copyright © 2026 NextGen Tech Solutions.
