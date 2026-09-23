# Cartoes congelados do holdout ASR primario

## Status

Congelados em 23/09/2026, antes da coleta da pessoa consentida. Estes cartoes
nao sao corpus e nao sao mostrados ao revisor com seus rotulos esperados. A
transcricao ASR real so entra no holdout apos revisao humana dupla.

## Composicao

42 cartoes: 15 `CANCEL`, 15 `UNKNOWN` e tres de cada rotulo positivo. Nenhum
texto normalizado repete `asr-development.tsv`, `development.tsv`, `final.tsv`
ou `final-recovery.tsv`.

| ID | Texto lido | Rotulo esperado | Categoria |
| --- | --- | --- | --- |
| P01 | interrompa a tarefa imediatamente | `CANCEL` | cancelamento direto |
| P02 | não execute nada agora | `CANCEL` | negacao de execucao |
| P03 | encerre o procedimento em curso | `CANCEL` | cancelamento direto |
| P04 | desista dessa ação | `CANCEL` | cancelamento coloquial |
| P05 | suspenda imediatamente o tratamento | `CANCEL` | negacao de execucao |
| P06 | cancele o comando atual | `CANCEL` | cancelamento direto |
| P07 | cancele a ação que está em andamento | `CANCEL` | cancelamento explicito |
| P08 | não avance para o próximo passo | `CANCEL` | negacao de execucao |
| P09 | aborte essa tentativa | `CANCEL` | cancelamento direto |
| P10 | não faça a pulverização | `CANCEL` | negacao de acao |
| P11 | cancele tudo por enquanto | `CANCEL` | cancelamento coloquial |
| P12 | não deixe a estação de recarga | `CANCEL` | negacao de saida |
| P13 | não faça o retorno à base agora | `CANCEL` | negacao de retorno |
| P14 | pare antes de começar | `CANCEL` | cancelamento temporal |
| P15 | quero cancelar a atividade | `CANCEL` | cancelamento direto |
| P16 | o que aconteceu no talhão ontem? | `UNKNOWN` | pergunta historica |
| P17 | quanto tempo choveu hoje? | `UNKNOWN` | pergunta fora do contrato |
| P18 | o robô já terminou o serviço? | `UNKNOWN` | consulta de estado |
| P19 | qual é a umidade do solo? | `UNKNOWN` | pergunta fora do contrato |
| P20 | talvez a gente converse depois | `UNKNOWN` | hesitacao |
| P21 | eu ainda não decidi | `UNKNOWN` | hesitacao |
| P22 | mostre a última inspeção | `UNKNOWN` | classe futura |
| P23 | a bateria está cheia? | `UNKNOWN` | consulta de estado |
| P24 | o que significa pulverização? | `UNKNOWN` | pergunta de dominio |
| P25 | o plot do leste foi tratado ontem | `UNKNOWN` | historico |
| P26 | não tenho certeza se devo seguir | `UNKNOWN` | hesitacao |
| P27 | como está o vento agora? | `UNKNOWN` | pergunta fora do contrato |
| P28 | poderia explicar o mapa? | `UNKNOWN` | pergunta fora do contrato |
| P29 | o robô consegue trabalhar à noite? | `UNKNOWN` | pergunta de capacidade |
| P30 | este é só um comentário | `UNKNOWN` | conversa sem acao |
| P31 | aplique defensivo na faixa experimental | `SPRAY` | ordem explicita |
| P32 | distribua produto no lote de demonstração | `SPRAY` | ordem explicita |
| P33 | comece o controle fitossanitário na gleba modelo | `SPRAY` | ordem explicita |
| P34 | conduza o robô para a estação de recarga | `DOCK` | retorno para recarga |
| P35 | recolha o robô na doca | `DOCK` | retorno explicito |
| P36 | faça o retorno à base de carregamento | `DOCK` | retorno explicito |
| P37 | libere o robô da estação de recarga | `UNDOCK` | saida explicita |
| P38 | realize a desatracação | `UNDOCK` | saida tecnica explicita |
| P39 | remova o robô do suporte de estacionamento | `UNDOCK` | saida explicita |
| P40 | autorizo o início | `CONFIRM` | permissao explicita |
| P41 | está autorizado | `CONFIRM` | permissao explicita |
| P42 | sim, confirmei | `CONFIRM` | permissao explicita |

## Regras de coleta

- A pessoa le somente o texto e nao recebe o rotulo esperado.
- `mockDebug` permanece offline, sem alvo e sem confirmacao; resetar entre
  falas e nunca responder a uma confirmacao.
- Registrar somente a transcricao exibida e excluir qualquer dado pessoal.
- Normalizar a transcricao ASR real e exclui-la se ela repetir ou for variante
  proxima de qualquer texto de desenvolvimento, avaliacao final, primaria ou
  replicacao. Nunca substituir a transcricao pelo texto do cartao.
- Duas pessoas revisam a transcricao real sem consultar esta tabela. Consenso
  que conflite com a ontologia operacional tambem e excluido.
- O arquivo do holdout e criado somente depois da revisao; nao ajustar estes
  cartoes, guard, limiar ou as frases da replicacao depois disso.

## Hash de congelamento

Metodo: SHA-256 dos bytes deste arquivo excluindo a linha que comeca por
`SHA-256:`.

SHA-256: `50ddec1edae4239cc259bb8c530a3e4487687f3e5721a9d5f327cb4e00f1d943`
