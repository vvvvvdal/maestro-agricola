# Task: Smoke remoto Jev

## Status

Implementacao local pronta; a rodada remota permanece pendente nesta etapa.

## Objetivo

`JEV-40` mede uma rodada pequena do endpoint remoto, fora do APK e do caminho
do robo. O corpus possui seis falas sinteticas, uma por rotulo, e serve para
confirmar contrato, versao retornada, custo, latencia e falhas. Ele nao altera
o corpus final, limiar, classificador local ou comportamento do app.

## Runner e limites

[`../../tools/jev_remote_smoke.py`](../../tools/jev_remote_smoke.py) so chama a
API com `--execute`; sem essa flag, ele apenas valida o corpus e informa o
limite calculado. A chave vem exclusivamente de `TYPESAFE_API_KEY` no ambiente
do terminal e nunca e impressa, escrita ou enviada ao APK.

| Regra | Valor |
| --- | --- |
| Casos | 6, em [`../study-groups/jev-rl-2026-10-01/corpus/smoke.tsv`](../study-groups/jev-rl-2026-10-01/corpus/smoke.tsv) |
| Modelo | `jev-1.13.0` |
| Deadline por tentativa | 2 s |
| Tentativas totais | no maximo 8 |
| Retry | somente uma vez para `429` ou `529`, com `Retry-After` de ate 1 s; sem header, 250 ms |
| Subteto aprovado | US$0,50 |
| Limite matematico | US$0,021504: 8 tentativas x 64.000 tokens x US$0,042/M token |

O limite matematico usa o contexto maximo publicado do modelo e ja fica abaixo
do subteto. A fixture de saida guarda somente ID opaco, modelo, escolha,
probabilidades, confidence, uso, latencia, custo e codigo de falha. Ela nao
guarda fala, cabecalhos, corpo bruto, erro detalhado nem credencial.

## Execucao aprovada

Depois de confirmar que a variavel esta definida sem mostrar seu valor:

```bash
[ -n "$TYPESAFE_API_KEY" ] && echo SET || echo UNSET
python3 tools/jev_remote_smoke.py --execute \
  --output docs/study-groups/jev-rl-2026-10-01/results/jev-smoke-fixture.json
python3 tools/jev_intent_harness.py \
  --dataset docs/study-groups/jev-rl-2026-10-01/corpus/smoke.tsv \
  --jev-fixture docs/study-groups/jev-rl-2026-10-01/results/jev-smoke-fixture.json \
  --output docs/study-groups/jev-rl-2026-10-01/results/jev-smoke-harness.json
python3 tools/jev_intent_metrics.py \
  --input docs/study-groups/jev-rl-2026-10-01/results/jev-smoke-harness.json \
  --output docs/study-groups/jev-rl-2026-10-01/results/jev-smoke-metrics.json
```

Antes de versionar os resultados, a revisao confere que os tres JSONs nao
contem os textos do corpus, `Authorization`, `Bearer` ou a chave. `JEV-40` so
vira concluida depois dessa rodada, do harness, das metricas e do registro da
evidencia em `TASKS.md`.

## Criterios de aceite

- O runner usa somente a `Choice` dos seis rotulos do contrato fixado.
- Nenhuma chamada e possivel sem `--execute` e sem a variavel de ambiente.
- Retry, timeout, respostas invalidas e erros HTTP respeitam a politica de
  falha fechada; o teto global tem codigo explicito `ATTEMPT_LIMIT`.
- Testes portateis usam transporte falso; nenhum teste faz rede ou usa chave.
- A chamada real, quando ocorrer, fica abaixo de US$0,50 e gera evidencia
  sanitizada reproduzivel para a comparacao posterior.
