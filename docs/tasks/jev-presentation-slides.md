# Task: Visuais Jev para slides

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Objetivo

Preparar evidencia visual 16:9 para a futura criacao dos slides. Os tres SVGs
leem somente o JSON sanitizado da JEV-42; eles nao criam deck, nao alteram o
app e nao mudam a decisao `HOLD`.

## Artefatos

- [`jev-final-recovery-comparison-slide.svg`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-comparison-slide.svg): acertos, accuracy,
  macro-F1, aceitacoes inseguras, p50/p95 e custo.
- [`jev-final-recovery-confusion-slide.svg`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-confusion-slide.svg): matrizes Local e Jev,
  com ouro nas linhas, predicao nas colunas e erros fora da diagonal.
- [`jev-final-recovery-reliability-slide.svg`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-reliability-slide.svg): bins ocupados,
  `n` por ponto e diagonal de calibracao ideal.

Cada arquivo tem `1600 x 900`, declara `n=60`, corpus sintetico pareado, uma
rodada remota, SHA da fonte e `Decisao: HOLD - sem adocao operacional`.

## Leitura obrigatoria

- A comparacao mostra 54/60 e macro-F1 0,9010 para Jev, contra 48/60 e 0,8026
  para o local, mas tambem p95 de 2.100,575 ms e custo US$0,001472394 para o
  Jev. Latencia e custo pertencem ao harness deste host, nao a Android, campo
  ou robo.
- A matriz destaca `CANCEL -> CONFIRM (0,75)` como aceite inseguro Jev. Nenhum
  visual transforma o resultado em autorizacao de movimento.
- O reliability diagram e descritivo: amostra sintetica, uma rodada e sem
  replicacao. Ele nao prova calibracao geral nem seguranca.

## Reproducao e verificacao

```bash
python3 tools/jev_presentation_slides.py \
  --evidence docs/study-groups/jev-rl-2026-10-01/results/jev-final-recovery-presentation.json \
  --output-dir docs/study-groups/jev-rl-2026-10-01/results

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  tests/portable/ai/test_jev_presentation_evidence.py \
  tests/portable/ai/test_jev_presentation_slides.py -q
```

O teste valida renderer deterministico, valores obrigatorios, aviso
`CANCEL -> CONFIRM`, `HOLD` e ausencia de texto do corpus, cabecalhos HTTP ou
credenciais. Os tres SVGs foram renderizados em `1600 x 900` por Chrome
headless e inspecionados visualmente: sem corte, sobreposicao ou texto ilegivel.

A fonte canonica e
[`jev-final-recovery-presentation.json`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-presentation.json),
com SHA de metricas `e7984bbc...2f5dddcc`.
