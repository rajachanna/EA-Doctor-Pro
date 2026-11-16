import pytest
from ea_doctor.journal import scan_journal, CODES


@pytest.mark.parametrize("code", list(CODES))
def test_known_retcode(code):
    result=scan_journal(f"2026.11.16 trade error {code} while executing order")
    assert len(result)==1
    assert result[0].rule_id == "MT"+str(code)
    assert result[0].line == 1
    assert result[0].remediation


def test_no_fabricated_code():
    assert scan_journal("Trading okay. Connected. 10016 seconds elapsed") == []
    assert scan_journal("Retcode=99999") == []


def test_dedup_line():
    f=scan_journal("trade retcode=10016 [10016]")
    assert len(f)==1


def test_multiple_lines():
    f=scan_journal("trade retcode=10016\nhello\norder error 131")
    assert [x.line for x in f]==[1,3]


def test_redact_password():
    f=scan_journal("Order error 130 password=secret123 token=veryprivate")
    assert len(f)==1
    assert "secret123" not in f[0].evidence
    assert "veryprivate" not in f[0].evidence


def test_limit_lines():
    f=scan_journal("trade error 130\ntrade error 131",max_lines=1)
    assert len(f)==1


def test_no_unsolicited_network_calls(monkeypatch):
    import socket
    def deny(*args,**kwargs):raise AssertionError("network call")
    monkeypatch.setattr(socket,"socket",deny)
    assert scan_journal("Trade error 130")
