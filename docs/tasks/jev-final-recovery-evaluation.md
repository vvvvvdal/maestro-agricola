# Task: Avaliacao final de recuperacao Jev

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Objetivo

`JEV-41R` recupera a medicao final sem repetir `final.tsv`, cuja rodada
original ficou indeterminada. Ela usa somente `final-recovery.tsv`, um corpus
novo e congelado de 60 frases sinteticas, separado dos corpora anteriores.

## Guardrails

[`../../tools/jev_remote_recovery_final.py`](../../tools/jev_remote_recovery_final.py)
fixa corpus, hash, modelo, fixture e reserva. Nao aceita argumentos livres de
texto, dataset, modelo ou output; somente `--execute` permite HTTP. Antes da
primeira chamada, cria uma reserva atomica exclusiva. A reserva permanece em
erro ou interrupcao, bloqueando toda repeticao silenciosa.

| Regra | Valor |
| --- | --- |
| Corpus | 60 casos de `final-recovery.tsv`, hash `a157963b...8e7e6d2a` |
| Modelo | `jev-1.13.0` |
| Tentativas | 60 primarias e no maximo um retry para `429`/`529` por caso |
| Teto de tentativas | 120 |
| Subteto aprovado | US$1,50 |
| Limite matematico | US$0,322560: 120 x 64.000 tokens x US$0,042/M token |

Esta e uma amostra independente, nao um ajuste do corpus original. Ela nao
entra no APK, nao emite `Command` e nao muda Qwen, RAG, bridge ou limiar.

## Execucao autorizada

No terminal que possui `TYPESAFE_API_KEY`, sem interromper a execucao:

```bash
timeout 6m python3 tools/jev_remote_recovery_final.py --execute
python3 tools/jev_intent_harness.py \
  --dataset docs/study-groups/jev-rl-2026-10-01/corpus/final-recovery.tsv \
  --jev-fixture docs/study-groups/jev-rl-2026-10-01/results/jev-final-recovery-fixture.json \
  --output docs/study-groups/jev-rl-2026-10-01/results/jev-final-recovery-harness.json
python3 tools/jev_intent_metrics.py \
  --input docs/study-groups/jev-rl-2026-10-01/results/jev-final-recovery-harness.json \
  --output docs/study-groups/jev-rl-2026-10-01/results/jev-final-recovery-metrics.json
```

Antes do commit de evidencia, os JSONs precisam ser verificados contra textos
do corpus, `Authorization`, `Bearer` e `TYPESAFE_API_KEY`. A interpretacao de
metricas continua em JEV-42 e JEV-43; esta task nao permite uma segunda rodada.

## Evidencia da rodada

A rodada unica foi executada no corpus congelado. Os quatro artefatos abaixo
foram verificados contra todos os textos do corpus, `Authorization`, `Bearer`
e `TYPESAFE_API_KEY`; nenhum desses dados aparece nos JSONs versionados.

| Medida | Local | Jev remoto |
| --- | ---: | ---: |
| Casos | 60 | 60 |
| Acertos | 48 | 54 |
| Accuracy | 0,8000 | 0,9000 |
| Macro-F1 | 0,8026 | 0,9010 |
| Falhas remotas | 0 | 0 |
| Aceitacoes inseguras | 3 | 1 |
| Brier multiclasses | 0,3034 | 0,1057 |
| Top-label ECE | 0,0810 | 0,0787 |
| Latencia p50 | 0,175 ms | 742,333 ms |
| Latencia p95 | 0,293 ms | 2.100,575 ms |
| Custo | US$0,00 | US$0,001472394 |

O Jev retornou `jev-1.13.0` nos 60 casos, com 35.057 tokens de entrada. O
achado inseguro Jev e `recovery-045`: rotulo ouro `CANCEL`, predicao
`CONFIRM`, probabilidade 0,75. O local teve tres aceites inseguros:
`recovery-043`, `recovery-047` e `recovery-060`. Esses numeros sao medidos;
nao promovem Jev ao APK nem concluem sobre seguranca de campo. A comparacao e a
decisao pertencem a JEV-42 e JEV-43.

- [`jev-final-recovery-reservation.json`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-reservation.json): reserva atomica da rodada.
- [`jev-final-recovery-fixture.json`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-fixture.json): respostas sanitizadas.
- [`jev-final-recovery-harness.json`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-harness.json): comparacao pareada.
- [`jev-final-recovery-metrics.json`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-metrics.json): metricas calculadas.
