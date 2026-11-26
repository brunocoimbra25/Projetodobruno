import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture(autouse=True)
def resetar_estado(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", None)
    with main.lock_metricas:
        main.metricas.update(requisicoes=0, erros_5xx=0, ms_total=0.0)


@pytest.fixture
def client():
    return TestClient(main.app)


def test_health_retorna_contrato_e_request_id(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "versao": main.MODEL_VERSION,
        "ambiente": main.APP_ENV,
    }
    uuid.UUID(response.headers["X-Request-ID"])


def test_mensagem_de_spam_retorna_formato_correto(client):
    response = client.post(
        "/predict",
        json={"texto": "Parabéns! Você ganhou um prêmio. Clique para resgatar agora."},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"rotulo", "probabilidade", "versao"}
    assert body["rotulo"] == "spam"
    assert isinstance(body["probabilidade"], float)
    assert 0 <= body["probabilidade"] <= 1
    assert body["versao"] == main.MODEL_VERSION


def test_mensagem_comum_retorna_nao_spam(client):
    response = client.post(
        "/predict",
        json={"texto": "A reunião de amanhã foi adiada para quinta-feira."},
    )

    assert response.status_code == 200
    assert response.json()["rotulo"] == "nao_spam"


def test_texto_vazio_retorna_422_sem_contar_erro_5xx(client):
    response = client.post("/predict", json={"texto": "   "})

    assert response.status_code == 422
    assert main.metricas["erros_5xx"] == 0


def test_metrics_expoe_os_contadores(client):
    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"requisicoes", "erros_5xx", "latencia_media_ms"}
    assert body["requisicoes"] >= 1
    assert body["erros_5xx"] == 0
    assert body["latencia_media_ms"] >= 0


def test_falha_500_incrementa_metrica_sem_registrar_corpo_ou_segredo(
    client, monkeypatch, capsys
):
    texto_privado = "NAO_REGISTRAR_TEXTO_PRIVADO"
    chave_privada = "NAO_REGISTRAR_CHAVE_PRIVADA"
    monkeypatch.setattr(main, "API_KEY", chave_privada)

    def falhar(_textos):
        raise RuntimeError(chave_privada)

    monkeypatch.setattr(main.modelo, "predict_proba", falhar)
    response = client.post(
        "/predict",
        headers={"X-API-Key": chave_privada},
        json={"texto": texto_privado},
    )

    output = capsys.readouterr().out
    events = [json.loads(line) for line in output.splitlines()]
    assert response.status_code == 500
    assert response.json()["request_id"] == response.headers["X-Request-ID"]
    assert main.metricas["erros_5xx"] == 1
    assert texto_privado not in output
    assert chave_privada not in output
    assert {event["request_id"] for event in events} == {
        response.headers["X-Request-ID"]
    }
    end_event = events[-1]
    assert end_event["nivel"] == "ERROR"
    assert end_event["rota"] == "/predict"
    assert end_event["status"] == 500
    assert end_event["erro_tipo"] == "RuntimeError"
