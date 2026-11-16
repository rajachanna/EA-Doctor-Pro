"""Machine-readable reports and CI integration."""
import json
from pathlib import Path
from .models import Finding, summarize


def to_json(kind: str, filename: str, findings: list[Finding]) -> str:
    return json.dumps({
        "tool": "EA Doctor Pro", "version": "0.1.0", "mode": kind,
        "file": Path(filename).name, "counts": summarize(findings),
        "findings": [f.to_dict() for f in findings],
        "limitations": ["Static/heuristic analysis only", "No broker execution, compilation or profit verification"],
    }, indent=2)


def to_sarif(filename: str, findings: list[Finding]) -> str:
    rules = {}
    for f in findings:
        rules[f.rule_id] = {"id": f.rule_id, "shortDescription": {"text": f.title}}
    levels = {"critical":"error","high":"error","medium":"warning","low":"note","info":"note"}
    return json.dumps({
        "version":"2.1.0","$schema":"https://json.schemastore.org/sarif-2.1.0.json",
        "runs":[{
            "tool":{"driver":{"name":"EA Doctor Pro","version":"0.1.0","rules":list(rules.values())}},
            "results":[{
                "ruleId":f.rule_id,"level":levels[f.severity],
                "message":{"text":f.title+" — "+f.detail+" "+f.remediation},
                "locations":[{"physicalLocation":{
                    "artifactLocation":{"uri":Path(filename).name},
                    "region":{"startLine":max(1,f.line)}
                }}],
                "properties":{"confidence":f.confidence,"severity":f.severity},
            } for f in findings]
        }]
    }, indent=2)


def to_text(kind: str, filename: str, findings: list[Finding]) -> str:
    counts = summarize(findings)
    lines = [f"EA Doctor Pro · {kind} · {Path(filename).name}",
             "Findings: " + ", ".join(f"{k}: {v}" for k,v in counts.items()),
             "Static diagnostic suggestions only; no live bot validation."]
    for f in findings:
        lines += [f"",f"{f.severity.upper()} {f.rule_id} at line {f.line}: {f.title}",
                  f"  {f.remediation}"]
    if not findings: lines.append("No known patterns detected. This does NOT certify the bot as safe.")
    return "\n".join(lines)
