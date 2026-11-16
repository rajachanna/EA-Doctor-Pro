"""Offline EA Doctor CLI: journals, source and closed-trade CSV."""
import argparse
import json
import sys
from pathlib import Path

from .journal import scan_journal
from .source import scan_source
from .trades import analyze_trade_csv
from .report import to_json, to_sarif, to_text

_ALLOWED={".mq4":"source",".mq5":"source",".log":"journal",".txt":"journal",".csv":"trades"}
_WEIGHTS={"critical":4,"high":3,"medium":2,"low":1,"info":0}


def main(argv=None)->int:
    p=argparse.ArgumentParser(prog="ea-doctor",description="Privacy-first MT4/MT5 diagnostic CLI; offline, no trade execution")
    p.add_argument("path",type=Path,help="Local .mq4/.mq5, .log/.txt or trade .csv")
    p.add_argument("--type",choices=["auto","source","journal","trades"],default="auto")
    p.add_argument("--format",choices=["text","json","sarif"],default="text")
    p.add_argument("--output",type=Path)
    p.add_argument("--fail-on",choices=["critical","high","medium","low","none"],default="none")
    args=p.parse_args(argv)
    if not args.path.is_file():
        p.error("Input file does not exist")
    if args.path.stat().st_size>2_000_000:
        p.error("Input exceeds 2 MB")
    kind=args.type if args.type!="auto" else _ALLOWED.get(args.path.suffix.lower())
    if kind is None:
        p.error("Specify --type explicitly for unknown file extension")
    try:content=args.path.read_text(encoding="utf-8-sig")
    except (OSError,UnicodeError) as exc:p.error("Not a supported UTF-8 text export: "+str(exc))
    metrics=None
    try:
        if kind=="source":findings=scan_source(content)
        elif kind=="journal":findings=scan_journal(content)
        else:metrics,findings=analyze_trade_csv(content)
    except (ValueError,TypeError) as exc:p.error(str(exc))
    if args.format=="json":
        parsed=json.loads(to_json(kind,str(args.path),findings))
        if metrics is not None:parsed["metrics"]=metrics
        out=json.dumps(parsed,indent=2)
    elif args.format=="sarif":out=to_sarif(str(args.path),findings)
    else:
        out=to_text(kind,str(args.path),findings)
        if metrics is not None:
            out+="\nMetrics: "+json.dumps(metrics,indent=2)
    try:
        if args.output:args.output.write_text(out+"\n",encoding="utf-8")
        else:print(out)
    except OSError as exc:p.error("Unable to write output: "+str(exc))
    if args.fail_on!="none" and any(_WEIGHTS[f.severity]>=_WEIGHTS[args.fail_on] for f in findings):
        return 1
    return 0


if __name__=="__main__":
    sys.exit(main())
