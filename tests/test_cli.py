import json
from pathlib import Path
import pytest
from ea_doctor.cli import main
from ea_doctor.journal import scan_journal
from ea_doctor.report import to_json,to_sarif,to_text


def test_json_report_structure():
    f=scan_journal("Trade error 130")
    j=json.loads(to_json("journal","secret/path/notes.log",f))
    assert j["file"]=="notes.log"
    assert j["counts"]["high"]==1
    assert j["findings"][0]["rule_id"]=="MT130"


def test_sarif_schema():
    f=scan_journal("Order retcode=10030")
    s=json.loads(to_sarif("file.log",f))
    assert s["version"]=="2.1.0"
    assert s["runs"][0]["results"][0]["ruleId"]=="MT10030"


def test_text_empty_is_not_certificate():
    assert "NOT certify" in to_text("source","test.mq5",[])


@pytest.mark.parametrize("extension,content",[
    (".mq5","void OnTick(){ trade.Buy(0.1); }"),
    (".log","trade retcode=10016"),
    (".csv","profit\n10\n-20"),
])
def test_cli_modes(tmp_path,extension,content):
    p=tmp_path/("file"+extension);p.write_text(content)
    o=tmp_path/"output.json"
    assert main([str(p),"--format","json","--output",str(o)])==0
    assert json.loads(o.read_text())["findings"] is not None


def test_cli_fail_on_high(tmp_path):
    p=tmp_path/"file.log";p.write_text("trade retcode=10016")
    assert main([str(p),"--fail-on","high"])==1


def test_cli_fail_on_medium(tmp_path):
    p=tmp_path/"file.log";p.write_text("trade error 132")
    assert main([str(p),"--fail-on","high"])==0
    assert main([str(p),"--fail-on","medium"])==1


def test_cli_sarif(tmp_path):
    p=tmp_path/"file.mq5";p.write_text("void OnTick(){ trade.Buy(0.1); }")
    o=tmp_path/"res.sarif"
    assert main([str(p),"--format","sarif","--output",str(o)])==0
    assert json.loads(o.read_text())["runs"][0]["tool"]["driver"]["name"]=="EA Doctor Pro"


def test_cli_missing_file_rejected(tmp_path):
    with pytest.raises(SystemExit):
        main([str(tmp_path/"missing.log")])


def test_bad_extension_rejected(tmp_path):
    p=tmp_path/"notes.foo";p.write_text("hello")
    with pytest.raises(SystemExit):
        main([str(p)])


def test_non_string_journal():
    with pytest.raises(TypeError):
        scan_journal(None)
