# Classificador de spam

Aplicação de demonstração que classifica mensagens em português como `spam` ou `nao_spam`. O
projeto reúne um modelo de machine learning, uma API HTTP e uma página web para experimentar as
previsões.

> O modelo foi criado para uma atividade de MLOps. Ele usa uma base pequena e pode errar; não use
> as previsões como única base para decisões importantes.

## O que o projeto faz

1. A pessoa abre a página web e informa uma mensagem.
2. A página envia a mensagem à API FastAPI.
3. A API usa o pipeline TF-IDF + Regressão Logística salvo em `model/modelo.joblib`.
4. A resposta informa o rótulo previsto, a probabilidade da classe prevista e a versão do modelo.

A página também consulta a saúde da API, oferece exemplos de mensagens e exibe erros de conexão
ou de chave inválida. Ela é servida pela própria API, então não precisa de uma configuração
separada de CORS.

## Tecnologias

- **Python 3.12**
- **FastAPI** e **Uvicorn** para a API e o servidor web
- **scikit-learn** para carregar e executar o modelo
- **HTML, CSS e JavaScript** para a interface, sem processo de build separado
- **python-dotenv** para carregar a configuração local do arquivo `.env`

## Pré-requisitos

- Python 3.12 instalado e disponível como `python` no terminal.
- Git, caso vá clonar o repositório.
- Acesso à internet na primeira instalação das dependências.

## Instalação e execução local

Execute os comandos a partir da pasta raiz do projeto.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

O `.env.example` já fornece valores locais de exemplo. Depois de copiá-lo, o `.env` deve conter:

```dotenv
APP_ENV=dev
MODEL_VERSION=v1
API_KEY=chave-ficticia-123
```

Essa chave é apenas um exemplo para desenvolvimento; substitua-a por outra chave fictícia se
compartilhar o ambiente. Não use uma chave real neste arquivo nem a envie ao Git.

Inicie o servidor:

```powershell
uvicorn app.main:app --reload
```

### Linux ou macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

O `.env.example` já fornece valores locais de exemplo. Confira se o `.env` contém as variáveis
mostradas acima e inicie o servidor:

```bash
uvicorn app.main:app --reload
```

### Abrir a aplicação

Com o servidor em execução:

- Página web: [http://localhost:8000](http://localhost:8000)
- Documentação interativa da API: [http://localhost:8000/docs](http://localhost:8000/docs)
- Estado do serviço: [http://localhost:8000/health](http://localhost:8000/health)

Para parar o servidor, pressione `Ctrl+C` no terminal.

## Executar com Docker

Com o Docker Desktop aberto e o mecanismo do Docker em execução, crie o arquivo `.env` na raiz
caso ainda não tenha feito isso (veja [Configuração](#configuração)). O Compose passa essas
variáveis ao container; o arquivo `.env` não é incluído na imagem.

Na raiz do projeto, construa a imagem e inicie o serviço. A configuração inicial gera a imagem
com a tag `classificador-spam:version1`; essa tag também fica registrada como metadado da imagem
no Docker Desktop.

```powershell
docker compose up --build -d
```

Acesse a mesma página em [http://localhost:8000](http://localhost:8000). Para acompanhar os logs
e encerrar o serviço:

```powershell
docker compose logs -f
docker compose down
```

Também é possível construir e iniciar a imagem sem Compose:

```powershell
docker build -t classificador-spam:version1 .
docker run --rm --name classificador-spam -p 8000:8000 --env-file .env classificador-spam:version1
```

### Criar uma nova versão da imagem

Antes de gerar uma versão nova, atualize estas duas variáveis no `.env`:

```dotenv
IMAGE_TAG=version2
MODEL_VERSION=v2
```

Depois construa e inicie a versão nova:

```powershell
docker compose up --build -d
```

O Docker Desktop mostrará `classificador-spam:version2` como outra imagem. A imagem
`classificador-spam:version1` continua disponível para consulta ou rollback enquanto não for
removida manualmente. Para cada nova entrega, incremente a tag (`version3`, `version4`...) e
atualize `MODEL_VERSION` para a versão correspondente (`v3`, `v4`...).

O container inclui a API, a interface e `model/modelo.joblib`, e executa o processo como usuário
sem privilégios administrativos. O `.dockerignore` exclui `.env`, ambiente virtual, dados de
treinamento e arquivos de desenvolvimento do contexto de build. Se alterar o código ou as
dependências, execute novamente `docker compose up --build -d` para reconstruir a imagem. Se a
porta local `8000` já estiver ocupada, encerre o outro serviço antes de iniciar o container.

## Configuração

O arquivo `.env.example` serve como ponto de partida e contém uma chave fictícia para uso local.
Copie-o para `.env` e troque os valores se necessário.
O `.gitignore` exclui `.env` do Git. Variáveis definidas diretamente no ambiente do sistema têm
prioridade sobre os valores do arquivo `.env`.

| Variável | Exemplo | Descrição |
|---|---|---|
| `APP_ENV` | `dev` | Nome do ambiente devolvido por `/health`. |
| `MODEL_VERSION` | `v1` | Versão incluída nas respostas e mostrada na página. |
| `IMAGE_TAG` | `version1` | Tag da imagem Docker. Incremente a cada nova versão para manter as imagens anteriores identificáveis. |
| `API_KEY` | `chave-ficticia-123` | Se preenchida, protege `/predict` com o cabeçalho `X-API-Key`. Deixe vazia para desativar a exigência localmente. |
| `MODEL_PATH` | `model/modelo.joblib` | Caminho opcional para outro arquivo de modelo. |

Em uma hospedagem, configure essas variáveis nas configurações do serviço. Não publique o arquivo
`.env` nem coloque chaves no HTML, no JavaScript ou no histórico do Git. O endpoint `/health` é
público mesmo quando `API_KEY` está configurada.

## API

### `GET /health`

Não exige chave. Exemplo de resposta:

```json
{
  "status": "ok",
  "versao": "v1",
  "ambiente": "dev"
}
```

### `POST /predict`

Recebe um texto. Se `API_KEY` estiver preenchida, envie também o cabeçalho `X-API-Key`.

Exemplo de requisição:

```http
POST /predict HTTP/1.1
Content-Type: application/json
X-API-Key: chave-ficticia-123

{"texto":"Parabéns! Você ganhou um prêmio. Clique no link para resgatar."}
```

Exemplo de resposta:

```json
{
  "rotulo": "spam",
  "probabilidade": 0.6742,
  "versao": "v1"
}
```

O valor `probabilidade` é a probabilidade estimada para o rótulo retornado, entre `0` e `1`.
O corpo precisa conter `texto` com até 2.000 caracteres. Campo ausente, texto vazio ou apenas
com espaços recebe erro HTTP `422`. Sem chave ou com chave incorreta, a API responde `401`.

Teste rápido no PowerShell, depois de iniciar o servidor (troque a chave se alterou `.env`):

```powershell
$headers = @{ "X-API-Key" = "chave-ficticia-123" }
$body = @{ texto = "Você ganhou um prêmio! Clique para resgatar." } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -Headers $headers -ContentType "application/json" -Body $body
```

Se `API_KEY` estiver vazia, remova `-Headers $headers` do comando.

## Modelo e dados

- `model/modelo.joblib`: pipeline treinado que a API carrega ao iniciar.
- `data/mensagens.csv`: exemplos rotulados com as colunas `texto` e `rotulo`.
- `model/train.py`: script opcional para retreinar o modelo.
- `model/exemplo_uso.py`: exemplo de previsão diretamente em Python.

O modelo usa TF-IDF e Regressão Logística. A base tem poucas mensagens, portanto as previsões e
probabilidades são apenas demonstrativas. Para carregar o arquivo do modelo, mantenha a versão de
scikit-learn indicada em `requirements.txt`.

Para instalar também as dependências de treinamento e retreinar:

```bash
python -m pip install -r requirements-treino.txt
python model/train.py
```

O script substitui `model/modelo.joblib` pelo modelo treinado com os dados informados. O
retreinamento não é necessário para executar a API.

## Estrutura do projeto

```text
app/
  main.py          # aplicação FastAPI, endpoints e carregamento da configuração
  index.html       # interface web servida em /
data/
  mensagens.csv    # dados de treinamento
docs/
  modelo_de_pagina.md
model/
  modelo.joblib    # pipeline de classificação salvo
  train.py         # script opcional de treinamento
  exemplo_uso.py   # uso do modelo sem a API
.env.example       # exemplo de variáveis; copie para .env
requirements.txt   # dependências para executar o serviço
requirements-treino.txt
```

## Publicação

A aplicação está preparada para ser executada com Uvicorn, mas este README não registra uma URL
pública de produção. Quando publicar o projeto, adicione aqui a URL da página e configure
`APP_ENV`, `MODEL_VERSION` e `API_KEY` na plataforma de hospedagem. Use `APP_ENV=test` ou o nome
de ambiente adotado pela equipe para distinguir a publicação do ambiente local.

## Resolução de problemas

- **Erro ao carregar `modelo.joblib`:** confira se a instalação foi feita com a versão de
  scikit-learn fixada em `requirements.txt` e se o arquivo existe em `model/modelo.joblib`.
- **A ativação do ambiente virtual é bloqueada no PowerShell:** use um terminal novo ou execute
  os comandos chamando diretamente `.\.venv\Scripts\python.exe -m pip ...` e
  `.\.venv\Scripts\uvicorn.exe app.main:app --reload` da pasta do projeto.
- **Resposta `401`:** confira se o cabeçalho `X-API-Key` corresponde ao valor de `API_KEY` em
  `.env`; reinicie o servidor depois de alterar a configuração.
- **Resposta `422`:** envie um JSON com a propriedade `texto`, preenchida e com no máximo 2.000
  caracteres.
- **A página não abre:** verifique se o Uvicorn continua rodando e se está acessando
  `http://localhost:8000`.

## Próximos passos da atividade

Este repositório faz parte de uma atividade de MLOps. A API, a interface e o modelo já podem ser
empacotados com Docker. Etapas futuras podem adicionar testes automatizados, CI/CD, métricas e
logs, implantação e rollback. Registre neste README as URLs, decisões e instruções novas conforme
essas partes forem concluídas.
