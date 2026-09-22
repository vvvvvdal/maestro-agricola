# Task: Avaliacao final remota Jev

## Status

Implementacao local pronta; a rodada final remota permanece pendente.

## Objetivo

`JEV-41` executa uma unica rodada do corpus final congelado, fora do APK e sem
alterar rubrica, limiar, corpus ou comportamento do robo. A comparacao usa o
mesmo harness local versus Jev e preserva somente artefatos sanitizados.

## Guardrails

[`../../tools/jev_remote_final.py`](../../tools/jev_remote_final.py) fixa o
arquivo `corpus/final.tsv`, valida seu SHA-256 do manifesto antes de qualquer
HTTP e nao aceita texto, modelo, dataset ou output por argumento. So `--execute`
autoriza chamadas. Se `results/jev-final-fixture.json` ja existir, o runner
recusa a segunda rodada. Antes do primeiro HTTP, ele cria
`results/jev-final-reservation.json` com exclusao atomica; a reserva permanece
apos erro ou interrupcao e bloqueia qualquer nova rodada ate decisao humana.

| Regra | Valor |
| --- | --- |
| Corpus | 60 casos congelados, hash `d0438948...6188b8b0` |
| Modelo | `jev-1.13.0` |
| Tentativas | 60 primarias e, no maximo, uma repeticao para `429`/`529` por caso |
| Teto de tentativas | 120 |
| Deadline | 2 s por tentativa |
| Subteto aprovado | US$3,00 |
| Limite matematico | US$0,322560: 120 x 64.000 tokens x US$0,042/M token |

O limite considera cada tentativa no contexto maximo publicado, ficando abaixo
do subteto antes de qualquer request. As respostas preservadas nao incluem
texto, chave, cabecalho, corpo bruto ou detalhe de erro.

## Execucao autorizada

No terminal que possui `TYPESAFE_API_KEY`:

```bash
[ -n "$TYPESAFE_API_KEY" ] && echo SET || echo UNSET
timeout 6m python3 tools/jev_remote_final.py --execute
python3 tools/jev_intent_harness.py \
  --dataset docs/study-groups/jev-rl-2026-10-01/corpus/final.tsv \
  --jev-fixture docs/study-groups/jev-rl-2026-10-01/results/jev-final-fixture.json \
  --output docs/study-groups/jev-rl-2026-10-01/results/jev-final-harness.json
python3 tools/jev_intent_metrics.py \
  --input docs/study-groups/jev-rl-2026-10-01/results/jev-final-harness.json \
  --output docs/study-groups/jev-rl-2026-10-01/results/jev-final-metrics.json
```

Antes de versionar, conferir que os tres artefatos nao contem textos do corpus,
`Authorization`, `Bearer` ou `TYPESAFE_API_KEY`. Depois da rodada, somente
JEV-42 calcula a comparacao e JEV-43 interpreta a evidencia; JEV-41 nao abre
uma rodada de ajuste.

## Criterios de aceite

- O hash e as 60 linhas do corpus congelado sao validados antes de HTTP.
- Uma fixture final existente bloqueia nova execucao.
- Uma reserva atomica bloqueia execucoes concorrentes e repeticao apos
  interrupcao.
- A politica de timeout e retry permanece fechada e limitada.
- Testes portateis usam transporte falso e nao fazem rede.
- A rodada remota unica fica abaixo de US$3,00, produz fixture por ID e gera
  harness/metricas sanitizados.
