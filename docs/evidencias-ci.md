# Evidências do CI

As execuções estão disponíveis na aba Actions do GitHub:

- [Pipeline verde em `main` (testes, Ruff, publicação e deploy condicional)](https://github.com/brunocoimbra25/Projetodobruno/actions/runs/45730549438)
- [Pipeline vermelho controlado: expectativa do teste propositalmente incorreta](https://github.com/brunocoimbra25/Projetodobruno/actions/runs/45731036573)
- [Pipeline verde depois de corrigir a expectativa](https://github.com/brunocoimbra25/Projetodobruno/actions/runs/45731149751)

A falha controlada foi feita apenas na branch `ci-evidence/red-demo`; a publicação da imagem
foi ignorada nessa branch. O código correto permaneceu em `main` e foi validado com seis testes
locais e seis testes no container Linux Python 3.12, além do Ruff.

## Verificação local da imagem Docker

Imagem: `classificador-spam:version4`. O container ficou `Healthy` com a porta
`127.0.0.1:8000->8000/tcp`. Foram verificados `/`, `/health`, `/ready`, `/metrics` e duas
previsões (`spam` e `nao_spam`). A chave foi lida em memória do `.env` e não foi incluída nos
comandos registrados, nos logs ou no Git.

## Kubernetes

Os manifestos estão em `k8s/`. Não havia contexto Kubernetes configurado nesta máquina durante
a validação (`kubectl config current-context` sem resultado), então não foi possível capturar
uma saída real de `kubectl describe pod` nem confirmar Pods/CronJob em execução. O README traz os
passos para criar o cluster Kubernetes do Docker Desktop e aplicar os arquivos.
