# Revisao do corpus ASR de desenvolvimento

## Escopo

Este registro cobre somente `asr-development.tsv`. O corpus e de
desenvolvimento: nao e holdout, nao autoriza ajuste apos os holdouts futuros e
nao foi enviado ao Jev.

## Revisao humana

Duas pessoas rotularam, de forma independente, os 28 cartoes em
`docs/tasks/jev-asr-review-cards.md`. Houve consenso integral em `gold_label` e
`category`. Os revisores nao receberam identificador pessoal, audio, data/hora
ou registro de sessao.

## Verificacao ASR

No SM-X510, com Wi-Fi e dados moveis desligados, as 28 transcricoes exibidas
pelo `mockDebug` corresponderam exatamente aos cartoes revisados. A coleta nao
gravou audio, `logcat`, screenshot ou ADB. A jornada foi resetada entre frases;
nenhum comando foi enviado.

## Observacao do baseline local

Durante a mesma verificacao, o classificador local divergiu em duas fronteiras:

| ID | Rotulo ouro | Predicao local observada | Efeito operacional |
| --- | --- | --- | --- |
| `asr-dev-017` | `CANCEL` | `SPRAY` | Sem alvo e sem confirmacao; nenhum comando. |
| `asr-dev-018` | `UNKNOWN` | `UNDOCK` | Sem confirmacao; nenhum comando. |
| `asr-dev-019` | `UNKNOWN` | `CANCEL` | Intencao recusada no estado inicial; nenhum comando. |
| `asr-dev-025` | `UNKNOWN` | `UNDOCK` | Sem confirmacao; nenhum comando. |

As 24 demais predicoes observadas coincidiram com os cartoes. Isto e uma
observacao de desenvolvimento do baseline, nao uma comparacao Jev.

## Limites

O corpus nao contem falante, sessao, aparelho, audio, texto descartado ou
identificador pessoal. Ainda faltam variacao de ruido/ASR antes de encerrar
JEV-62.
