"""Trade CSV statistical audit. Not a brokerage statement verifier."""
import csv
import io
import math
from .models import Finding

def _as_number(value: str) -> float:
    raw=(value or "").strip().replace("$","").replace("€","").replace("£","").replace(" ","")
    if "," in raw and "." not in raw:raw=raw.replace(",",".")
    elif "," in raw:raw=raw.replace(",","")
    amount=float(raw)
    if not math.isfinite(amount):
        raise ValueError("Non-finite number")
    return amount


def analyze_trade_csv(content: str, *, max_rows: int = 50000) -> tuple[dict, list[Finding]]:
    if not isinstance(content, str):
        raise TypeError("CSV must be text")
    if len(content)>3_000_000:raise ValueError("CSV exceeds supported size")
    header=content[:4096]
    delimiter="\t" if header.count("\t")>header.count(",") else ";" if header.count(";")>header.count(",") else ","
    reader=csv.DictReader(io.StringIO(content),delimiter=delimiter)
    if not reader.fieldnames:
        raise ValueError("Missing CSV headers")
    headers={str(x).strip().lower():x for x in reader.fieldnames if x}
    profit_name=next((headers[x] for x in ("profit","pnl","net_profit","p&l") if x in headers),None)
    if not profit_name:
        raise ValueError("CSV requires a 'profit' or 'pnl' column; provide closed trades only")
    cost_names=[headers[k] for k in ("commission","swap","fee","fees") if k in headers]
    pnl=[]
    invalid=0
    for row_number,row in enumerate(reader,2):
        if len(pnl)+invalid>=max_rows:raise ValueError("Too many rows")
        try:
            val=_as_number(row[profit_name])
            for k in cost_names:
                if row.get(k):val+=_as_number(row[k])
            pnl.append(val)
        except (ValueError,TypeError,KeyError):
            invalid+=1
    if not pnl:
        raise ValueError("No valid closed-trade results found")
    pos=sum(x for x in pnl if x>0)
    neg=-sum(x for x in pnl if x<0)
    net=sum(pnl)
    equity=0.0;peak=0.0;max_drawdown=0.0;max_loss_streak=0;streak=0
    for amount in pnl:
        equity+=amount;peak=max(peak,equity);max_drawdown=max(max_drawdown,peak-equity)
        streak=streak+1 if amount<0 else 0
        max_loss_streak=max(max_loss_streak,streak)
    top_profit=max((abs(x) for x in pnl),default=0)
    total_abs=sum(abs(x) for x in pnl)
    metrics={
        "trades":len(pnl),"invalid_rows":invalid,"net_pnl":round(net,2),
        "win_rate_pct":round(100*sum(x>0 for x in pnl)/len(pnl),2),
        "profit_factor":round(pos/neg,3) if neg else None,
        "expectancy_per_trade":round(net/len(pnl),2),
        "max_closed_trade_drawdown_currency":round(max_drawdown,2),
        "max_consecutive_losses":max_loss_streak,
        "largest_trade_share_of_absolute_pnl_pct":round(100*top_profit/total_abs,2) if total_abs else 0,
        "drawdown_note":"Closed-trade cumulative P&L only, excludes floating/intratrade drawdown; no starting balance assumed.",
        "profit_factor_note":"null means no gross losses; not proof of a robust or profitable strategy."
    }
    findings=[]
    def add(key,sev,title,detail,action):
        findings.append(Finding(key,sev,title,detail,action,1,confidence="computed",category="performance"))
    if len(pnl)<30:
        add("TR001","medium","Small trade sample",
            "Fewer than 30 closed trades may not reveal variation across different markets.",
            "Collect more out-of-sample paper/demo trades before interpreting results.")
    if neg>pos:
        add("TR002","high","Observed gross losses exceed gains",
            "Profit factor is below one for the supplied closed-trade sample.",
            "Investigate execution costs, entry/exit logic and risk sizing without profit guarantees.")
    if total_abs and top_profit/total_abs>=0.45 and len(pnl)>=3:
        add("TR003","medium","Large-trade outlier dependence",
            "One trade accounts for 45% or more of absolute observed results.",
            "Review results excluding unusual outliers and verify robustness.")
    if max_loss_streak>=6:
        add("TR004","medium","Long observed losing streak",
            "Six or more consecutive losing trades appear in the supplied sample.",
            "Inspect worst-case exposure, available margin and daily loss caps.")
    if invalid:
        add("TR005","low","Skipped invalid rows",
            f"{invalid} rows could not be parsed as finite trade P&L.",
            "Fix export column headers and numeric values before relying on statistics.")
    return metrics,findings
