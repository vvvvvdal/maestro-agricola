# Task: Evidencia Jev para apresentacao

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Objetivo

`JEV-42` transforma somente `jev-final-recovery-metrics.json` em evidencia
reproduzivel para a apresentacao: comparacao local versus Jev, matrizes de
confusao, lista de aceites inseguros e reliability diagram. Nao cria slide,
nao muda o produto e nao decide adocao.

## Artefatos

[`../../tools/jev_presentation_evidence.py`](../../tools/jev_presentation_evidence.py)
valida o schema de metricas e gera no diretorio de resultados:

- `jev-final-recovery-presentation.json`: fonte sanitizada e canonica para
  reuso posterior;
- `jev-final-recovery-presentation.md`: tabela, matrizes, bins e limites;
- `jev-final-recovery-reliability.svg`: reliability diagram pareado, com
  diagonal ideal e tamanho `n` de cada bin ocupado.

Os artefatos incluem o hash das metricas de origem. Eles registram que a
amostra possui 60 falas sinteticas e uma rodada remota; Brier, ECE e o grafico
sao descritivos, nao prova de calibracao generalizavel, seguranca de campo ou
prontidao operacional. A latencia e custo sao do harness neste host, nao do
Android, audio, campo ou robo.

O aceite inseguro Jev `recovery-045 CANCEL -> CONFIRM (0,75)` aparece no
relatorio e no aviso do SVG. Nenhum grafico pode omiti-lo ou sugerir que a
melhor accuracy autoriza movimento.

## Evidencia gerada

- [`jev-final-recovery-presentation.md`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-presentation.md): comparacao, matrizes, bins e limites.
- [`jev-final-recovery-presentation.json`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-presentation.json): fonte sanitizada com SHA das metricas.
- [`jev-final-recovery-reliability.svg`](../study-groups/jev-rl-2026-10-01/results/jev-final-recovery-reliability.svg): reliability diagram pareado.

JEV-43 e a unica task que pode transformar esses achados em uma decisao
experimental. A melhor accuracy observada nao altera o classificador do APK.

## Criterios de aceite

- Tabela, matrizes e diagramas saem somente das metricas versionadas.
- Matriz usa ouro nas linhas e predicao nas colunas, para os seis rotulos.
- Diagrama mostra apenas bins ocupados, `n` por ponto e diagonal ideal.
- Artefatos nao contem texto do corpus, credencial, cabecalho ou corpo HTTP.
- A conclusao sobre adocao permanece bloqueada em JEV-43.
