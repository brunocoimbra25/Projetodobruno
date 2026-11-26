"""API e página web do classificador de spam."""
import hmac
import json
import os
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any

import joblib
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

APP_ENV = os.getenv("APP_ENV", "dev")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")
API_KEY = os.getenv("API_KEY")
MODEL_PATH = Path(
    os.getenv(
        "MODEL_PATH",
        str(Path(__file__).resolve().parent.parent / "model" / "modelo.joblib"),
    )
)
PAGE_PATH = Path(__file__).resolve().parent / "index.html"

# O modelo é carregado uma vez durante a importação da aplicação.
modelo = joblib.load(MODEL_PATH)

app = FastAPI(
    title="API de classificação de spam",
    version=MODEL_VERSION,
    docs_url=None if APP_ENV == "production" else "/docs",
    redoc_url=None if APP_ENV == "production" else "/redoc",
    openapi_url=None if APP_ENV == "production" else "/openapi.json",
)

metricas = {"requisicoes": 0, "erros_5xx": 0, "ms_total": 0.0}
lock_metricas = Lock()


def log_evento(nivel: str, mensagem: str, **campos: Any) -> None:
    """Escreve um evento JSON em stdout sem incluir dados do corpo da requisição."""
    registro = {
        "hora": datetime.now(UTC).isoformat(),
        "nivel": nivel,
        "mensagem": mensagem,
        **campos,
    }
    print(json.dumps(registro, ensure_ascii=False), flush=True)


log_evento("INFO", "modelo_carregado", versao=MODEL_VERSION)


class Mensagem(BaseModel):
    texto: str = Field(min_length=1, max_length=2000)

    @field_validator("texto")
    @classmethod
    def texto_nao_pode_ser_so_espacos(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("O texto não pode estar vazio.")
        return valor


@app.middleware("http")
async def observar_requisicao(request: Request, call_next):
    request_id = str(uuid.uuid4())
    inicio = time.perf_counter()
    rota = request.url.path
    metodo = request.method
    status = 500
    erro_tipo = None

    log_evento(
        "INFO",
        "requisicao_iniciada",
        request_id=request_id,
        metodo=metodo,
        rota=rota,
    )

    try:
        resposta = await call_next(request)
        status = resposta.status_code
        if status >= 400:
            erro_tipo = f"HTTP_{status}"
    except Exception as erro:  # noqa: BLE001 - log type only; never expose exception text.
        erro_tipo = type(erro).__name__
        resposta = JSONResponse(
            status_code=500,
            content={
                "detail": "Falha interna ao processar a solicitação.",
                "request_id": request_id,
            },
        )

    duracao_ms = (time.perf_counter() - inicio) * 1000
    with lock_metricas:
        metricas["requisicoes"] += 1
        metricas["ms_total"] += duracao_ms
        if status >= 500:
            metricas["erros_5xx"] += 1

    if status >= 500:
        log_evento(
            "ERROR",
            "requisicao_falhou",
            request_id=request_id,
            metodo=metodo,
            rota=rota,
            status=status,
            duracao_ms=round(duracao_ms, 2),
            erro_tipo=erro_tipo,
            erro_mensagem="Falha interna ao processar a solicitação.",
        )
    elif status >= 400:
        log_evento(
            "WARNING",
            "requisicao_rejeitada",
            request_id=request_id,
            metodo=metodo,
            rota=rota,
            status=status,
            duracao_ms=round(duracao_ms, 2),
            erro_tipo=erro_tipo,
            erro_mensagem="Solicitação rejeitada pela API.",
        )
    else:
        log_evento(
            "INFO",
            "requisicao_concluida",
            request_id=request_id,
            metodo=metodo,
            rota=rota,
            status=status,
            duracao_ms=round(duracao_ms, 2),
        )

    resposta.headers["X-Request-ID"] = request_id
    return resposta


@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(PAGE_PATH, media_type="text/html")


@app.get("/health")
def health():
    return {"status": "ok", "versao": MODEL_VERSION, "ambiente": APP_ENV}


@app.get("/ready")
def ready():
    if modelo is None:
        raise HTTPException(status_code=503, detail="Modelo ainda não está pronto.")
    return {"status": "pronto", "versao": MODEL_VERSION}


@app.get("/metrics")
def ver_metricas():
    with lock_metricas:
        requisicoes = metricas["requisicoes"]
        erros_5xx = metricas["erros_5xx"]
        ms_total = metricas["ms_total"]

    latencia_media_ms = ms_total / requisicoes if requisicoes else 0
    return {
        "requisicoes": requisicoes,
        "erros_5xx": erros_5xx,
        "latencia_media_ms": round(latencia_media_ms, 1),
    }


@app.post("/predict")
def predict(msg: Mensagem, x_api_key: str | None = Header(default=None)):
    if API_KEY and (x_api_key is None or not hmac.compare_digest(x_api_key, API_KEY)):
        raise HTTPException(status_code=401, detail="Chave de API inválida ou ausente.")

    probabilidades = modelo.predict_proba([msg.texto])[0]
    indice = probabilidades.argmax()
    return {
        "rotulo": str(modelo.classes_[indice]),
        "probabilidade": round(float(probabilidades[indice]), 4),
        "versao": MODEL_VERSION,
    }
