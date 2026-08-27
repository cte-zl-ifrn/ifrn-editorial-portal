import json
from unittest.mock import patch

from src.logging import log_metric


def _completed_log_calls(mock_log_event):
    return [call for call in mock_log_event.call_args_list if call.args[1] == "request.completed"]


def test_every_request_produces_a_completed_access_log_line(client):
    with patch("src.app.log_event") as mock_log_event:
        response = client.get("/health")

    assert response.status_code == 200
    calls = _completed_log_calls(mock_log_event)
    assert len(calls) == 1
    fields = calls[0].kwargs
    assert fields["method"] == "GET"
    assert fields["path"] == "/health"
    assert fields["status_code"] == 200
    assert fields["duration_ms"] >= 0


def test_access_log_covers_errors_too(client):
    """Uma rota inexistente também deve produzir a linha de acesso (com o
    status 404), não só requisições bem-sucedidas."""
    with patch("src.app.log_event") as mock_log_event:
        response = client.get("/rota-que-nao-existe")

    assert response.status_code == 404
    calls = _completed_log_calls(mock_log_event)
    assert len(calls) == 1
    assert calls[0].kwargs["status_code"] == 404


def test_access_log_never_includes_extra_fields_beyond_the_safe_set(client):
    """Garante estruturalmente que nenhum dado sensível (cookie, segredo,
    corpo de documento) possa vazar por este log — só os quatro campos
    fixos são logados, nunca dados arbitrários da requisição."""
    with patch("src.app.log_event") as mock_log_event:
        client.get("/health")

    fields = _completed_log_calls(mock_log_event)[0].kwargs
    assert set(fields.keys()) == {"method", "path", "status_code", "duration_ms"}


def test_every_request_emits_a_request_count_metric(client, capsys):
    response = client.get("/health")

    assert response.status_code == 200
    metric_lines = [
        json.loads(line) for line in capsys.readouterr().out.splitlines() if line.strip()
    ]
    request_count_lines = [line for line in metric_lines if "RequestCount" in line]
    assert len(request_count_lines) == 1
    metric = request_count_lines[0]
    assert metric["RequestCount"] == 1
    assert metric["Route"] == "/health"
    assert metric["_aws"]["CloudWatchMetrics"][0]["Metrics"][0]["Name"] == "RequestCount"


def test_error_responses_also_emit_an_error_count_metric(client, capsys):
    response = client.get("/rota-que-nao-existe")

    assert response.status_code == 404
    metric_lines = [
        json.loads(line) for line in capsys.readouterr().out.splitlines() if line.strip()
    ]
    error_count_lines = [line for line in metric_lines if "ErrorCount" in line]
    assert len(error_count_lines) == 1
    assert error_count_lines[0]["StatusCode"] == "404"


def test_successful_responses_do_not_emit_an_error_count_metric(client, capsys):
    client.get("/health")

    metric_lines = [
        json.loads(line) for line in capsys.readouterr().out.splitlines() if line.strip()
    ]
    assert not any("ErrorCount" in line for line in metric_lines)


def test_log_metric_writes_a_single_embedded_metric_format_line(capsys):
    log_metric("SubmissionCompleted")

    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["SubmissionCompleted"] == 1
    emf = payload["_aws"]["CloudWatchMetrics"][0]
    assert emf["Namespace"] == "IfrnEditorialPortal"
    assert emf["Metrics"] == [{"Name": "SubmissionCompleted", "Unit": "Count"}]
    assert emf["Dimensions"] == [[]]
