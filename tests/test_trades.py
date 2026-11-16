import pytest
from ea_doctor.trades import analyze_trade_csv


def test_trade_statistics():
    metrics,findings=analyze_trade_csv("profit,commission,swap\n20,-2,0\n-10,-2,-1\n5,-1,0\n")
    assert metrics["trades"]==3
    assert metrics["net_pnl"]==9
    assert metrics["win_rate_pct"]==66.67
    assert metrics["max_closed_trade_drawdown_currency"]==13
    assert "TR001" in {x.rule_id for x in findings}


def test_missing_profit_column():
    with pytest.raises(ValueError,match="profit"):
        analyze_trade_csv("amount,name\n12,abc")


def test_no_trades():
    with pytest.raises(ValueError):
        analyze_trade_csv("profit\ninvalid")


def test_invalid_rows():
    metrics,findings=analyze_trade_csv("profit\n2\nhello\n-1")
    assert metrics["invalid_rows"]==1
    assert "TR005" in {x.rule_id for x in findings}


def test_infinity_rejected():
    metrics,findings=analyze_trade_csv("profit\ninf\n2")
    assert metrics["trades"]==1


def test_all_winners_have_null_profit_factor():
    metrics,_=analyze_trade_csv("profit\n10\n10")
    assert metrics["profit_factor"] is None


def test_profit_factor_loss():
    metrics,findings=analyze_trade_csv("profit\n10\n-30")
    assert metrics["profit_factor"]==pytest.approx(0.333,abs=0.001)
    assert "TR002" in {x.rule_id for x in findings}


def test_outlier_detection():
    _,findings=analyze_trade_csv("profit\n10000\n-1\n1\n1")
    assert "TR003" in {x.rule_id for x in findings}


def test_loss_streak():
    _,findings=analyze_trade_csv("profit\n-1\n-1\n-1\n-1\n-1\n-1\n5")
    assert "TR004" in {x.rule_id for x in findings}


def test_max_rows():
    with pytest.raises(ValueError):
        analyze_trade_csv("profit\n1\n2\n3",max_rows=2)


def test_no_default_balance_assumption():
    metrics,_=analyze_trade_csv("profit\n-1\n3")
    assert "drawdown_pct" not in metrics
    assert "no starting balance assumed" in metrics["drawdown_note"]
