"""Recognize MT4 / MT5 trade server error codes in exported journal text.

No broker connection, auto-trading or claim of root-cause certainty.
"""
import re
from .models import Finding

# Severity, readable meaning, concrete troubleshooting action, category.
CODES = {
    10004: ("medium", "Requote", "Inspect permitted deviation, symbol tick freshness, and broker execution policy.", "execution"),
    10006: ("high", "Trade request rejected", "Review order parameters and broker journal; confirm trading permissions.", "execution"),
    10014: ("high", "Invalid trade volume", "Read SYMBOL_VOLUME_MIN, MAX and STEP; quantize requested lots to the step.", "volume"),
    10015: ("high", "Invalid price", "Refresh tick data and align order price to symbol tick size and execution mode.", "execution"),
    10016: ("high", "Invalid stops", "Compare SL/TP to current bid/ask, stops level, freeze level and symbol digits.", "stops"),
    10017: ("high", "Trading disabled", "Check symbol/session and account trade permissions on the broker and terminal.", "permissions"),
    10018: ("medium", "Market closed", "Check symbol trading sessions and broker holiday schedule before sending orders.", "session"),
    10019: ("high", "Not enough money", "Check free margin, contract size, leverage, requested volume and exposure.", "margin"),
    10020: ("medium", "Price changed", "Refresh tick and review execution-mode-specific retry and deviation policy.", "execution"),
    10021: ("medium", "No current quotes", "Check connection and Market Watch tick freshness for this exact symbol.", "connection"),
    10024: ("high", "Too many trade requests", "Add bounded retry/backoff and per-symbol rate limits; prevent OnTick flooding.", "rate-limit"),
    10026: ("high", "Autotrading disabled by server", "Confirm server-side EA permissions with the broker; do not bypass restrictions.", "permissions"),
    10027: ("high", "Autotrading disabled by terminal", "Verify Algo Trading terminal setting and EA-specific permissions.", "permissions"),
    10030: ("high", "Unsupported filling mode", "Read SYMBOL_FILLING_MODE, choose a supported filling policy and check request flags.", "execution"),
    10031: ("high", "No connection", "Check terminal/server connection, authentication and VPS network availability.", "connection"),
    10033: ("high", "Order limit reached", "Inspect broker order limits and current pending orders before adding more.", "limits"),
    10034: ("high", "Volume limit reached", "Review symbol volume limit and existing directional exposure.", "volume"),
    10040: ("high", "Position limit reached", "Inspect the broker position cap and currently open positions.", "limits"),
    129: ("high", "Invalid price (MT4)", "Refresh quotes, normalize price using symbol digits and verify order type.", "execution"),
    130: ("high", "Invalid stops (MT4)", "Check MODE_STOPLEVEL, pending-order distance and SL/TP against bid/ask.", "stops"),
    131: ("high", "Invalid volume (MT4)", "Check MODE_MINLOT, MODE_MAXLOT and MODE_LOTSTEP for the broker symbol.", "volume"),
    132: ("medium", "Market closed (MT4)", "Check server trading sessions and symbol market hours.", "session"),
    133: ("high", "Trade disabled (MT4)", "Check account, symbol and Expert Advisor permissions.", "permissions"),
    134: ("high", "Not enough money (MT4)", "Inspect free margin and lot size; do not automatically enlarge the risk.", "margin"),
    136: ("medium", "Off quotes (MT4)", "Check tick updates, symbol availability and network connection.", "connection"),
    138: ("medium", "Requote (MT4)", "Inspect tick refresh and allowed slippage in the broker execution context.", "execution"),
    146: ("medium", "Trade context busy (MT4)", "Serialize trade requests and avoid unbounded retry loops.", "concurrency"),
    148: ("high", "Too many orders (MT4)", "Count open and pending orders versus account limits.", "limits"),
}
_CONTEXT = re.compile(r"(?i)\b(?:trade|order|position|request|retcode|error|failed|rejected|buy|sell)\b")
_PATTERN = re.compile(r"(?i)(?:\b(?:retcode|error|err(?:or)?code|code)\s*[:=#-]?\s*|\[|\()(?P<code>100\d{2}|1(?:29|30|31|32|33|34|36|38|46|48))\b")
_SAFE_LINE = re.compile(r"(?i)(?:password|token|secret|api[_-]?key)\s*[:=]\s*[^\s,;]+")


def scan_journal(content: str, *, max_lines: int = 15000) -> list[Finding]:
    if not isinstance(content, str):
        raise TypeError("Journal must be text")
    results = []
    seen = set()
    for number, line in enumerate(content.splitlines()[:max_lines], 1):
        if not _CONTEXT.search(line):
            continue
        for match in _PATTERN.finditer(line):
            code = int(match.group("code"))
            if code not in CODES:
                continue
            signature = (code, number)
            if signature in seen:
                continue
            seen.add(signature)
            severity, label, action, category = CODES[code]
            evidence = _SAFE_LINE.sub("[REDACTED]", line.strip())[:160]
            results.append(Finding(
                rule_id="MT" + str(code), severity=severity, title=label,
                detail=f"An explicit MetaTrader trade error {code} appears on this journal line. "
                       "It identifies a symptom, not necessarily the underlying cause.",
                remediation=action, line=number, evidence=evidence,
                confidence="high", category=category,
            ))
    return results
