"""Read-only heuristic scanner for MQL4/MQL5 Expert Advisor source.

This does not compile MQL, emulate runtime behavior, execute code, or assure safety.
"""
import re
from .models import Finding

_RULES = (
    ("EA001", "high", "Potential hard-coded secret",
     r"(?im)^\s*(?:input\s+)?(?:string|char\[\])?\s*(?:api_?key|password|secret|access_?token)\s*=\s*\"[^\"]{4,}\"",
     "Remove credentials from source and use authorized configuration or secrets management.", "secrets"),
    ("EA002", "high", "Martingale / progressive position sizing",
     r"(?i)\bmartingale\w*|\b(?:lots?|volume)\s*\*=\s*(?:2(?:\.0)?|[3-9])|MathPow\s*\(\s*2\s*,",
     "Bound total exposure, add drawdown/volume limits, and test tail risk; progressive sizing cannot ensure profit.", "risk"),
    ("EA003", "medium", "Sleep inside OnTick handler",
     r"(?is)\b(?:void|int)\s+OnTick\s*\([^)]*\)\s*\{[^}]{0,3500}?\bSleep\s*\(",
     "Avoid blocking the tick event. Use state and OnTimer where appropriate.", "reliability"),
    ("EA004", "high", "Unbounded loop may block execution",
     r"\bwhile\s*\(\s*(?:true|1)\s*\)",
     "Add explicit termination, bounded retries and interval controls.", "reliability"),
    ("EA005", "medium", "Forced DLL imports",
     r"(?im)^\s*#import\s+[\"'][^\n\r\"']+\.dll[\"']",
     "Review trust boundary, platform support and user consent for DLL dependencies.", "dependencies"),
    ("EA006", "low", "Direct file access to outside paths",
     r"(?im)\bFileOpen\s*\([^\n]*\\\\",
     "Review MT terminal sandbox paths and validate filenames before file operations.", "io"),
)


def _without_comments(text: str) -> str:
    """Remove comments while preserving newline positions for diagnostics."""
    pattern = re.compile(r"/\*[\s\S]*?\*/|//[^\r\n]*")
    return pattern.sub(lambda m: "".join("\n" if c == "\n" else " " for c in m.group()), text)


def _line(text: str, start: int) -> int:
    return text.count("\n", 0, start) + 1


def scan_source(content: str, *, max_chars: int = 1_000_000) -> list[Finding]:
    if not isinstance(content, str):
        raise TypeError("Source must be text")
    if len(content) > max_chars:
        raise ValueError("Source exceeds maximum supported size")
    clean = _without_comments(content)
    results = []
    for key, severity, title, pattern, remediation, category in _RULES:
        for m in list(re.finditer(pattern, clean))[:25]:
            # Do not leak raw candidate credential values into the report.
            evidence = "[Source line redacted for credential safety]" if key == "EA001" else clean.splitlines()[_line(clean,m.start())-1].strip()[:130]
            results.append(Finding(
                rule_id=key, severity=severity, title=title,
                detail="Static source pattern requires manual review; the scanner cannot establish runtime behavior.",
                remediation=remediation, line=_line(clean, m.start()),
                evidence=evidence, confidence="heuristic", category=category,
            ))
    # Global checks are intentionally conservative and only activate on clear trade-entry calls.
    order = re.search(r"\bOrderSend\s*\(|\btrade\s*\.\s*(?:Buy|Sell|PositionOpen)\s*\(", clean, re.I)
    if order:
        def add(key, severity, title, remediation, category):
            results.append(Finding(key, severity, title,
                                   "The expected safety/reliability mechanism is not obvious in this file. "
                                   "It may exist in included modules or dynamically computed helpers.",
                                   remediation, _line(clean, order.start()),
                                   "[Order placement found]", "heuristic", category))
        if not re.search(r"(?i)\b(?:sl|stop_?loss|setstoploss|stoploss|sl_points|stop_points)\b", clean):
            add("EA010","high","Stop-loss / exit risk guard not evident",
                "Check how SL and emergency exits are configured; a missing text token is not proof that none exists.","risk")
        if not re.search(r"(?i)\b(?:ResultRetcode|retcode|GetLastError|_LastError|last_error)\b", clean):
            add("EA011","medium","Trade execution result handling not evident",
                "Inspect OrderSend return values and trade server retcodes; handle rejection and partial fills.","execution")
        if not re.search(r"(?i)\b(?:SetExpertMagicNumber|magic_?number|magic)\b", clean):
            add("EA012","low","Order ownership marker not evident",
                "Consider stable magic numbers and account-specific position reconciliation.","reliability")
        if re.search(r"\bOnTick\s*\(", clean) and not re.search(
            r"(?i)\b(?:newbar|lastbar|lasttrade|cooldown|itime|timer|nexttrade|rate_limit)\b", clean
        ):
            add("EA013","medium","Trade-frequency guard not evident",
                "Ensure OnTick cannot create repeated entries on every tick; use a bounded state machine.","rate-limit")
    return sorted(results, key=lambda x: (x.line, x.rule_id))
