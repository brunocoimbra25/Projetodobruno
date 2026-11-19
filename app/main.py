"""API e página web do classificador de spam.

Para rodar na raiz do projeto: ``uvicorn app.main:app --reload``.
"""
import hmac
import os
from pathlib import Path

import joblib
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, validator

# Carrega o .env local, se existir. Em hospedagem, as variáveis do ambiente têm prioridade.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

APP_ENV = os.getenv("APP_ENV", "dev")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")
API_KEY = os.getenv("API_KEY")
MODEL_PATH = Path(
    os.getenv("MODEL_PATH", str(Path(__file__).resolve().parent.parent / "model" / "modelo.joblib"))
)
PAGE_PATH = Path(__file__).resolve().parent / "index.html"

# O modelo é carregado uma única vez no início do processo.
modelo = joblib.load(MODEL_PATH)

app = FastAPI(title="API de classificação de spam", version=MODEL_VERSION)


class Mensagem(BaseModel):
    texto: str = Field(min_length=1, max_length=2000)

    @validator("texto")
    def texto_nao_pode_ser_so_espacos(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("O texto não pode estar vazio.")
        return valor


@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(PAGE_PATH, media_type="text/html")


@app.get("/health")
def health():
    return {"status": "ok", "versao": MODEL_VERSION, "ambiente": APP_ENV}


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
