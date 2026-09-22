# Task: Avaliacao final de recuperacao Jev

## Status

Implementacao local pronta; a rodada `JEV-41R` permanece pendente.

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
