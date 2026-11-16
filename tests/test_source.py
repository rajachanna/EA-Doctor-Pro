import pytest
from ea_doctor.source import scan_source


def ids(s):
    return {f.rule_id for f in scan_source(s)}


def test_trade_safety():
    checks=ids("void OnTick(){ trade.Buy(0.1,_Symbol); }")
    assert {"EA010","EA011","EA012","EA013"} <= checks


def test_stop_retcode_magic_and_cooldown():
    s="void OnTick(){ if(newbar){ trade.Buy(0.1,_Symbol,0,sl,0); if(trade.ResultRetcode()){} trade.SetExpertMagicNumber(magic); }}"
    checks=ids(s)
    assert not ({"EA010","EA011","EA012","EA013"} & checks)


def test_martingale():
    assert "EA002" in ids("double lots=0.1; lots *= 2;")


def test_hardcoded_secret_redaction():
    f=scan_source('string api_key = "very-secret-token";')
    secret=[x for x in f if x.rule_id=="EA001"]
    assert secret
    assert "very-secret-token" not in secret[0].evidence


def test_comments_do_not_trigger():
    assert scan_source("// martingale lots *= 2\n/* while(true) */") == []


def test_sleep_ontick():
    assert "EA003" in ids("void OnTick(){ Sleep(500); }")


def test_bounded_while_ignored():
    assert "EA004" not in ids("while (attempts < 5) { ++attempts; }")


def test_unbounded_loop():
    assert "EA004" in ids("while(true){ }")


def test_dll_import():
    assert "EA005" in ids('#import "sample.dll"')


def test_source_limit():
    with pytest.raises(ValueError):
        scan_source("a"*1000,max_chars=100)


def test_source_nonstring():
    with pytest.raises(TypeError):
        scan_source(None)


def test_heuristics_not_certificates():
    assert scan_source("int OnInit(){return 0;}")==[]


def test_suspicious_pattern_caseinsensitive():
    assert "EA002" in ids("double MartingaleMultiplier = 1.5;")


def test_line_number():
    x=scan_source("\n\nwhile (1){}")
    assert x[0].line==3
