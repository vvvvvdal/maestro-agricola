# JEV-76 - Contrato de preview de missao

## Objetivo

`MISSION_PREVIEW` reconhece que a fala pede uma sequencia composta. Ele nao e
um comando, nao e enviado ao bridge e nao movimenta o robo. O resultado desta
task e somente um `MissionPlan` tipado e validado para ser exibido ao operador.

Exemplo de fala:

> Saia da doca, pulverize o plot-02, informe a ultima pulverizacao do plot-03 e volte para a doca.

Exemplo de plano valido: [`valid-mission-plan.json`](../../contracts/fixtures/valid-mission-plan.json).

## Fronteira de linguagem

O roteador local pode reconhecer uma solicitacao composta como
`MISSION_PREVIEW`, mas nao extrai passos nem escolhe alvo. O parser
deterministico aceita apenas a gramatica e os verbos documentados abaixo. Jev
nao participa do catalogo atual de seis labels; qualquer comparacao futura usa
corpus novo, pareado e task separada.

```text
fala livre
  -> roteador local: MISSION_PREVIEW
  -> parser e validador deterministico
  -> MissionPlan DRAFT ou recusa
  -> preview para o operador
  -> confirmacao individual por acao fisica (task posterior)
  -> Command existente por etapa (task posterior)
```

`UNKNOWN`, fala parcialmente entendida, alvo implicito, passo fora do catalogo
ou sequencia invalida recusam o plano. Nao ha fallback para Jev, Qwen, comando
ou acao parcial.

## Schema

O schema versionado e
[`mission-plan.schema.json`](../../contracts/mission-plan.schema.json). A
primeira versao admite de dois a quatro passos e somente:

| Intent do passo | Alvo | Efeito nesta task |
| --- | --- | --- |
| `UNDOCK` | `null` | Sera uma acao fisica futura. |
| `SPRAY` | `MAPPED_PLOT` explicito | Sera uma acao fisica futura. |
| `PLOT_STATUS_QUERY` | `MAPPED_PLOT` explicito | Sera consulta somente leitura futura. |
| `DOCK` | `null` | Sera uma acao fisica futura. |

O schema valida forma, versao, IDs e combinacao `intent`/`target`. O parser e
o validador da task seguinte tambem devem garantir que o alvo esta no mapa
versionado, que IDs de passo nao se repetem e que a ordem e executavel. A
versao 1 nao admite `INSPECT_TARGET`, `PAUSE`, `RESUME`, `SCOUT`, dose, produto,
navegacao livre, coordenada, `EMERGENCY_STOP` ou texto gerado livremente.

`created_at` e `plan_id` permitem rastrear a sessao em memoria. A fala bruta,
audio, imagem e transcricao nao fazem parte do schema e nao devem ser
persistidos com o plano.

## Confirmacao e execucao futura

Um preview nao contem `confirmed` e nunca pode reutilizar uma confirmacao de
plano como confirmacao de movimento. Em JEV-77, o operador somente revisa ou
ancela o plano. Em JEV-78, antes de cada `UNDOCK`, `SPRAY` ou `DOCK`, o app
pede nova confirmacao
por audio e gera um `Command` individual ja existente. `PLOT_STATUS_QUERY` nao
autoriza o proximo passo: resposta invalida, indisponivel ou qualquer falha
pausa o plano e exige revisao do operador.

O executor futuro espera o estado terminal do bridge para cada acao fisica. Se
uma etapa falhar, expirar, for recusada ou tiver alvo invalido, ele nao executa
as etapas seguintes e nao tenta dock, undock ou spray implicitos.

## Criterios de aceite para JEV-77 e JEV-78

- O exemplo de quatro etapas valida contra o schema; o fixture de alvo implicito
  e recusado.
- O parser recusa fala sem dois passos completos, alvo ausente, alvo fora do
  mapa, verbo nao permitido, ordem invalida ou ambiguidade.
- O preview nao chama `CommandTransport`, `/read-only`, Jev, Qwen, WebSocket ou
  ROS.
- O preview mostra que cada acao fisica exigira confirmacao por audio individual
  no momento da etapa; essa confirmacao e o executor pertencem a JEV-78.
- O executor para na primeira falha e registra apenas estado minimo da sessao.

## Fora de escopo

JEV-76 nao implementa parser, UI, confirmacao, transporte, executor, Gazebo ou
hardware. Esta task nao altera `command.schema.json` e nao autoriza
`MissionPlan` como payload de ROS.

## Entrega JEV-77

O `mockDebug` agora reconhece localmente uma fala composta pela gramatica
fechada e produz um `MissionPlan` somente em memoria. O preview mostra as
etapas, identifica quais dependem de confirmacao por voz futura e permite
cancelamento explicito. Ele expira em 60 segundos; expirar e cancelar mantem o
robo em espera e nao chamam Jev, Qwen, `CommandTransport`, WebSocket, ROS ou
`/read-only`.

Evidencias:

- `MissionPreviewParserTest`, `InteractionFeedbackTest` e
  `JourneyPresentationTest` passaram no `mockDebug`;
- `assembleMockDebug` passou;
- no SM-X510, a fala digitada equivalente ao exemplo criou as quatro etapas
  esperadas e `Cancelar plano` voltou ao estado sem preview, com o cartao do
  robo em `Aguardando comando`.

JEV-78 continua sendo a unica task autorizada a transformar etapas em
`Command` individuais e validar o fluxo com Gazebo.
