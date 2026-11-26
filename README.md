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

## Instalar WSL 2 e Docker Desktop no Windows

O projeto usa **containers Linux**. No Windows, o Docker Desktop pode executá-los pelo WSL 2.
Consulte também os guias oficiais da [Microsoft para instalar WSL](https://learn.microsoft.com/pt-br/windows/wsl/install/),
da [Docker para instalar Docker Desktop no Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
e para [configurar a integração WSL 2](https://docs.docker.com/desktop/features/wsl/).

### 1. Instalar ou atualizar WSL 2

Abra o PowerShell como administrador e execute:

```powershell
wsl --install -d Ubuntu
```

Reinicie o Windows se for solicitado. Se o Ubuntu já estiver instalado, atualize o WSL e confira as
distribuições e versões instaladas:

```powershell
wsl --update
wsl --version
wsl --list --verbose
```

Na lista, confirme que a distribuição Ubuntu está na versão `2`. Se aparecer `1`, converta-a:

```powershell
wsl --set-version Ubuntu 2
```

Abra o Ubuntu pelo menu Iniciar e conclua a configuração inicial de usuário e senha do Linux.

### 2. Instalar e configurar Docker Desktop

1. Baixe o instalador pela página oficial do [Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Execute o instalador e escolha o backend **WSL 2** quando essa opção aparecer.
3. Inicie Docker Desktop e aceite os termos de uso.
4. Em **Settings > General**, confirme **Use the WSL 2 based engine**.
5. Em **Settings > Resources > WSL Integration**, habilite a integração para **Ubuntu** e clique em **Apply**.
6. Aguarde Docker Desktop indicar que o mecanismo está em execução.

Não instale outro Docker Engine dentro do Ubuntu para este fluxo; Docker Desktop fornece o mecanismo
e integra o comando `docker` à distribuição WSL escolhida. Confira no PowerShell ou no terminal do
Ubuntu:

```bash
docker --version
docker compose version
docker info
```

Se esses comandos não conseguirem conectar ao servidor, abra Docker Desktop, aguarde o mecanismo
iniciar e confira **Settings > Resources > WSL Integration**.

### 3. Abrir o projeto

No fluxo mais simples, abra PowerShell na pasta do projeto e execute os comandos Docker abaixo.
Também é possível usar o terminal Ubuntu. Para melhor desempenho com WSL, mantenha uma cópia do
repositório no sistema de arquivos Linux, por exemplo em `~/projetos/Projetodobruno`, em vez de
trabalhar em `/mnt/c`.

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
MODEL_VERSION=v3
IMAGE_TAG=version3
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

Com Docker Desktop aberto e o mecanismo em execução, confira se existe um `.env` na raiz do projeto.
Se não existir, copie `.env.example` para `.env` conforme a seção [Configuração](#configuração).
O Compose envia as variáveis ao container; o arquivo `.env` não é incluído na imagem.

Na raiz do projeto, construa a imagem e inicie o serviço com um único comando:

```powershell
docker compose up --build -d --wait
```

O Compose cria a imagem com a tag configurada em `IMAGE_TAG` (por padrão
`classificador-spam:version3`), inicia o container, publica a porta local `8000` e aguarda o
healthcheck passar. Abra [http://localhost:8000](http://localhost:8000). O Docker Desktop deve
mostrar o container como **healthy** e a porta `127.0.0.1:8000->8000/tcp`.

Para acompanhar os logs e encerrar o serviço:

```powershell
docker compose logs -f api
docker compose down
```

Também é possível iniciar a imagem diretamente, mas inclua a publicação da porta:

```powershell
docker build -t classificador-spam:version3 .
docker run --rm --name classificador-spam -p 127.0.0.1:8000:8000 --env-file .env classificador-spam:version3
```

Só construir a imagem ou iniciar o container pelo botão **Run** do Docker Desktop sem mapear uma
porta deixa a aplicação acessível apenas dentro do container. `EXPOSE 8000` descreve a porta usada
pela imagem, mas não publica essa porta no Windows. O Compose já configura o mapeamento correto.

O log `Uvicorn running on http://0.0.0.0:8000` é normal dentro do container: `0.0.0.0` significa
que o servidor aceita conexões nas interfaces do container; não é o endereço para digitar no
navegador. Use `http://localhost:8000` no Windows depois que a porta aparecer publicada. O Docker
explica a diferença entre a porta interna e a porta publicada na documentação de
[publicação de portas](https://docs.docker.com/engine/network/port-publishing/).

### Criar a próxima versão da imagem

Para gerar `version4`, atualize estas duas variáveis no `.env`:

```dotenv
IMAGE_TAG=version4
MODEL_VERSION=v4
```

Depois construa e inicie a versão nova:

```powershell
docker compose up --build -d --wait
```

O Docker Desktop mostrará `classificador-spam:version4` como outra imagem. As imagens
`classificador-spam:version1`, `classificador-spam:version2` e `classificador-spam:version3`
continuam disponíveis para consulta ou rollback enquanto não forem removidas manualmente. Para
cada entrega seguinte, incremente a tag e `MODEL_VERSION` para a versão correspondente.

A `version3` atual mantém o mesmo modelo de classificação; esta versão atualiza a identificação e
o empacotamento do serviço, sem retreinar o modelo.

O container inclui a API, a interface e `model/modelo.joblib`, e executa o processo como usuário
sem privilégios administrativos. O `.dockerignore` exclui `.env`, ambiente virtual, dados de
treinamento e arquivos de desenvolvimento do contexto de build. Se alterar o código ou as
dependências, execute novamente `docker compose up --build -d --wait` para reconstruir a imagem. Se a
porta local `8000` já estiver ocupada, encerre o outro serviço antes de iniciar o container.

## Configuração

O arquivo `.env.example` serve como ponto de partida e contém uma chave fictícia para uso local.
Copie-o para `.env` e troque os valores se necessário.
O `.gitignore` exclui `.env` do Git. Variáveis definidas diretamente no ambiente do sistema têm
prioridade sobre os valores do arquivo `.env`.

| Variável | Exemplo | Descrição |
|---|---|---|
| `APP_ENV` | `dev` | Nome do ambiente devolvido por `/health`. |
| `MODEL_VERSION` | `v3` | Versão incluída nas respostas e mostrada na página. |
| `IMAGE_TAG` | `version3` | Tag da imagem Docker. Incremente a cada nova versão para manter as imagens anteriores identificáveis. |
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
  "versao": "v3",
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
  "versao": "v3"
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

A aplicação está preparada para Docker e CI no GitHub Actions. Ainda não há URL pública de
produção configurada; o deploy de teste só é acionado quando o segredo `DEPLOY_HOOK_URL` existe
no repositório. Não informe uma URL pública até que uma plataforma tenha concluído o deploy.

## Testes, lint e CI

Instale as dependências de desenvolvimento e execute localmente antes de enviar alterações:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
ruff check .
```

`tests/test_api.py` verifica `/health`, a classificação de spam e mensagem comum, o formato das
respostas, `/metrics`, validação de entrada e que texto/chave não vazam nos logs.
O workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) roda pytest e Ruff em pushes e
pull requests para `main`. A publicação no GHCR só começa depois de ambos passarem; a imagem usa
o hash imutável do commit e a referência da branch/tag. Para cada commit, o hash é a referência
reprodutível. Releases usam tags Git versionadas (`v1`, `v2`, ...); a release corrigida desta
etapa é `v2`, sem mover a tag histórica `v1`.

O job de deploy de teste aceita um hook opcional. Configure `DEPLOY_HOOK_URL` em **Settings >
Secrets and variables > Actions**. O endereço e tokens não devem ser colocados no YAML, no README
ou impressos nos logs. Sem esse segredo, o workflow registra uma notificação e não aciona deploy.
O deploy hook precisa pertencer a uma plataforma configurada para publicar esta imagem.

## Logs, métricas e operação

Cada requisição gera linhas JSON em stdout, com `request_id`, rota, método, status, duração e nível.
Falhas 5xx registram tipo e mensagem genérica. O serviço não registra o conteúdo classificado,
chaves, tokens ou dados pessoais. Os logs não são gravados em arquivos dentro do container.

- `GET /health`: liveness, retorna HTTP 200 quando o processo atende.
- `GET /ready`: readiness, retorna 200 depois que o modelo está carregado.
- `GET /metrics`: contadores em memória `requisicoes`, `erros_5xx` e `latencia_media_ms`.
- `POST /predict`: classifica `{ "texto": "..." }` e devolve `rotulo`, `probabilidade` e `versao`.

Os contadores zeram quando o processo reinicia e são locais a cada réplica. A página inicial
mostra o estado e os valores de `/metrics`; o botão de carga envia 50 mensagens de exemplo e
exibe o status e a versão da resposta. Para inspecionar logs:

```powershell
docker logs -f classificador-spam
docker logs --tail 20 classificador-spam 2>&1 | Select-String 'ERROR'
```

Em Linux/WSL, use `docker logs classificador-spam 2>&1 | grep ERROR`. No Kubernetes, use
`kubectl logs -n mlops -f deployment/spam-service`.

## Kubernetes local

O manifesto pressupõe Docker Desktop Kubernetes configurado com **Kubeadm**, que compartilha o
armazenamento de imagens do Docker. No Docker Desktop, abra **Kubernetes** e crie um cluster
local; consulte o [guia oficial do Kubernetes no Docker Desktop](https://docs.docker.com/desktop/use-desktop/kubernetes/).
Confirme o contexto `docker-desktop`:

```powershell
kubectl config use-context docker-desktop
kubectl get nodes
```

Construa a imagem versionada e aplique os manifestos:

```powershell
docker compose build
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
kubectl get pods -n mlops -w
```

Abra a aplicação em outra janela do PowerShell:

```powershell
kubectl port-forward -n mlops service/spam-service 8001:8000
```

Visite `http://localhost:8001`. A porta 8001 evita conflito com o Compose na 8000. Para conferir
probes, recursos e eventos, use `kubectl describe pod -n mlops <nome-do-pod>`. Logs e tarefas:

```powershell
kubectl logs -n mlops deployment/spam-service
kubectl get cronjobs,jobs -n mlops
```

O Deployment define requests de CPU/memória, limite de memória, startup/readiness em `/ready`,
liveness em `/health` e atualização RollingUpdate com `maxUnavailable: 0`. O CronJob executa
uma verificação HTTP de `/health` a cada cinco minutos e falha se o serviço não responder. Ele
não reinicia o Deployment nem envia notificação externa. Para uma verificação rápida com Docker,
consulte `/health`; o reinício e o CronJob dependem do cluster local ativo.

Limites operacionais documentados: serviço fora do ar após três verificações consecutivas sem
resposta; latência média acima de 500 ms ou mais de cinco erros 5xx em um minuto são condições
para investigação em `/metrics`. O projeto expõe os dados, mas não envia alertas externos.

O manifesto usa `imagePullPolicy: Never` para testar a imagem local no Kubeadm. Não aplique esse
manifesto a um cluster remoto: publique a imagem em um registry e altere a referência e a política
de pull para o ambiente remoto. Se definir `API_KEY`, crie o Secret `spam-api-key` no namespace
`mlops`; não versione valores reais:

```powershell
kubectl create secret generic spam-api-key -n mlops --from-literal=API_KEY='<sua-chave>'
```

## Checklist de entrega e evidências

- CI verde: os jobs `testes` e `lint` passam; somente então o job `publicar` envia a imagem.
- CI vermelho: uma falha de teste impede a publicação. Para evidência, salve a execução/log de
  uma execução falha e a execução corrigida na aba **Actions**.
- Docker: `docker compose ps` mostra a versão `version4` saudável e a porta local publicada.
- Kubernetes: os pods ficam `Running` e `Ready`; `kubectl describe` mostra probes e recursos.
- Evidências recomendadas: captura do Actions verde/vermelho, painel `/metrics`, trecho de log JSON
  e descrição do Pod. Não inclua segredos nem mensagens privadas nas capturas.
- Os links permanentes das execuções verde/vermelha e o registro de verificações locais estão em
  [`docs/evidencias-ci.md`](docs/evidencias-ci.md).
- A atividade tem um integrante: Bruno Coimbra. Não há commits de um segundo integrante a declarar.

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
- **Docker Desktop mostra `8000/tcp`, mas o navegador não conecta:** a porta não foi publicada
  para o Windows. Inicie pelo projeto com `docker compose up --build -d --wait`; o comando
  `docker compose ps` deve mostrar `127.0.0.1:8000->8000/tcp` e o estado `healthy`. Ao criar o
  container manualmente no Docker Desktop, configure o mapeamento da porta do host `8000` para a
  porta `8000` do container.
- **O log mostra `http://0.0.0.0:8000`:** esse é o endereço de escuta dentro do container. Abra
  `http://localhost:8000` no navegador do Windows; confirme antes que a porta está publicada com
  `docker compose ps`.
- **Container não fica saudável:** veja o motivo com `docker compose logs --tail=100 api` e
  confira se Docker Desktop está usando Linux containers e se a porta `8000` está livre.
- **Docker não conecta no terminal do Ubuntu/WSL:** confirme que Docker Desktop está aberto e que
  a integração do Ubuntu está habilitada em **Settings > Resources > WSL Integration**.

