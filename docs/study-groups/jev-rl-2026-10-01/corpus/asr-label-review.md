# Revisao do corpus ASR de desenvolvimento

## Escopo

Este registro cobre somente `asr-development.tsv`. O corpus e de
desenvolvimento: nao e holdout, nao autoriza ajuste apos os holdouts futuros e
nao foi enviado ao Jev.

## Revisao humana

Duas pessoas rotularam, de forma independente, os 35 cartoes em
`docs/tasks/jev-asr-review-cards.md`. Houve consenso integral em `gold_label`.
A `category` foi conferida pelo integrador contra a rubrica e o texto
sanitizado; uma categoria/rotulo que conflite com a semantica contratual e
excluida. Os revisores nao receberam identificador pessoal, audio, data/hora
ou registro de sessao.

## Verificacao ASR

No SM-X510, com Wi-Fi e dados moveis desligados, 35 transcricoes exibidas
pelo `mockDebug` corresponderam exatamente aos cartoes revisados. A coleta nao
gravou audio, `logcat`, screenshot ou ADB. A jornada foi resetada entre frases;
nenhum comando foi enviado. Sete delas foram ditas com ruido leve de
ar-condicionado; seis entraram no corpus e uma foi excluida antes de qualquer
medicao.

## Observacao do baseline local

Durante a mesma verificacao, o classificador local divergiu em duas fronteiras:

| ID | Rotulo ouro | Predicao local observada | Efeito operacional |
| --- | --- | --- | --- |
| `asr-dev-017` | `CANCEL` | `SPRAY` | Sem alvo e sem confirmacao; nenhum comando. |
| `asr-dev-018` | `UNKNOWN` | `UNDOCK` | Sem confirmacao; nenhum comando. |
| `asr-dev-019` | `UNKNOWN` | `CANCEL` | Intencao recusada no estado inicial; nenhum comando. |
| `asr-dev-025` | `UNKNOWN` | `UNDOCK` | Sem confirmacao; nenhum comando. |

Das 34 entradas aceitas, as 30 demais predicoes observadas coincidiram com os
cartoes. Isto e uma observacao de desenvolvimento do baseline, nao uma
comparacao Jev.

## Exclusao auditavel

| Texto ASR exato | Consenso humano | Motivo da exclusao |
| --- | --- | --- |
| `saia da doca lentamente` | `DOCK` | O consenso conflita com a semantica contratual de `UNDOCK` para saida da doca. Nao redefinir a ontologia por este cartao; excluir e substituir por formulacao menos ambigua. |

## Limites

`asr-development.tsv` nao contem falante, sessao, aparelho, audio, texto
descartado ou identificador pessoal. Este relatorio registra somente o modelo
do aparelho usado como evidencia de ambiente. A cobertura de desenvolvimento
prevista para JEV-62 foi atingida; as proximas frases ASR devem ser reservadas
para os holdouts de JEV-63, sem reutilizar este corpus.
