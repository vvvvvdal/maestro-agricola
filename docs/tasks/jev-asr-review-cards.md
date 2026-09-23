# Cartoes revisados para coleta ASR Jev

## Status

Preparados em 23/09/2026. Duas pessoas revisaram os 18 textos de forma
independente e chegaram aos mesmos rotulos. Estes sao cartoes de fala para o
corpus de desenvolvimento; nao sao transcricoes ASR nem holdout.

## Cartoes e consenso humano

| ID | Texto lido | Rotulo consenso | Categoria |
| --- | --- | --- | --- |
| R01 | pulverize o talhão de demonstração | `SPRAY` | acao explicita |
| R02 | aplique o produto no plot do norte | `SPRAY` | acao explicita |
| R03 | comece a pulverizar na área de treino | `SPRAY` | acao explicita |
| R04 | volte para a doca | `DOCK` | doca explicita |
| R05 | leve o robô de volta à base | `DOCK` | sinonimo de doca |
| R06 | vá se recarregar na doca | `DOCK` | doca e recarga |
| R07 | saia da doca | `UNDOCK` | saida explicita |
| R08 | desacople e deixe a base | `UNDOCK` | sinonimo de saida |
| R09 | pode iniciar | `CONFIRM` | permissao explicita |
| R10 | isso está certo | `CONFIRM` | confirmacao curta |
| R11 | cancele essa ação | `CANCEL` | cancelamento direto |
| R12 | não siga com a operação | `CANCEL` | negacao de execucao |
| R13 | deixa isso para amanhã | `UNKNOWN` | adiamento ambiguo |
| R14 | qual foi o último tratamento do plot 03? | `UNKNOWN` | consulta de status |
| R15 | o talhão norte foi pulverizado ontem | `UNKNOWN` | historico |
| R16 | talvez depois a gente faça isso | `UNKNOWN` | hesitacao |
| R17 | não pulverize o plot de treinamento | `CANCEL` | negacao de acao |
| R18 | quando o robô sai da doca? | `UNKNOWN` | pergunta sobre capacidade |

## Uso na coleta

1. Manter o SM-X510 offline, em `mockDebug`, sem alvo e sem confirmacao.
2. Falar um cartao por vez e resetar a jornada antes da proxima fala.
3. Registrar somente a transcricao sanitizada exibida pelo ASR.
4. Excluir qualquer transcricao diferente que introduza dado pessoal; nao
   substituir pelo texto do cartao.
5. Antes de criar `corpus/asr-development.tsv`, confirmar novamente que texto,
   rotulo e categoria continuam validos para cada transcricao real.

Nao usar estes cartoes em `asr-primary` ou `asr-replication` futuros.
