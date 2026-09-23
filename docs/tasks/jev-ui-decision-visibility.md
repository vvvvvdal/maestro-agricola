# Visualizacao da decisao Jev no Android

Status: JEV-30 a JEV-36 concluidas; este documento e historico. A proxima task
da `test/jev` esta em `docs/study-groups/jev-rl-2026-10-01/TASKS.md`.

Responsavel sugerido: Atila (Android), com Rafael na evidencia do classificador

## JEV-30 concluida

Em 22/09/2026, `predictionSourceLabel` passou a converter a origem `JEV` em
`Jev`, sem mudar `RULE`, `MODEL` ou o fallback local. A mudanca e apenas de
apresentacao e o cartao existente ja recebe essa funcao; ela nao liga o
adaptador Jev ao app nem adiciona dados ou controles ao layout.

## JEV-31 concluida

Em 22/09/2026, confirmou-se que o cartao `INTENCAO` existente ja recebe
`predictionDetail`, sem nova secao ou layout. Com a origem JEV, ele mostra
`SPRAY · 87% · Jev` ou `DOCK · 91% · Jev`; o percentual e o valor de
`IntentPrediction.confidence`, que o adaptador JEV-22 preenche com a
probabilidade da classe escolhida. O teste de apresentacao fixa o formato e o
arredondamento. Estados `UNKNOWN` e erro continuam na JEV-32.

## JEV-32 concluida

Em 22/09/2026, o cartao `INTENCAO` passou a apresentar quatro estados no
mesmo espaco: `SPRAY`, `DOCK`, `UNKNOWN` valido e indisponibilidade do Jev.
O fallback fechado do `JevIntentClassifier` ja e `UNKNOWN` com probabilidade
zero e origem `JEV`; como uma Choice valida sempre seleciona uma probabilidade
positiva, a apresentacao usa esse sinal para mostrar `Classificacao
indisponivel` e `sem decisao remota · nenhum comando enviado`.

Um `UNKNOWN` valido permanece diferente: `Nao reconhecida` e `UNKNOWN · 42% ·
Jev · nenhum comando enviado`. O motor tambem informa `Intencao nao
reconhecida. Nenhum comando enviado` no cartao de status. Nenhum desses textos
altera estado operacional, cria `Command`, liga chamadas remotas ou permite
confirmacao.

## JEV-33 concluida

Em 22/09/2026, `Ajustes de teste` ganhou um diagnostico Jev recolhido no
flavor `mock`. A fixture local mostra a classe escolhida, a probabilidade da
classe, a metrica `confidence` propria do Jev e o vetor ordenado dos seis
rotulos. Ela fica em `src/mock`; no source set `dat`, o mesmo provider retorna
`null`, portanto nao ha vetor ou confidence no fluxo da demonstracao.

A fixture e rotulada como local e sem participacao na decisao operacional. Ela
nao altera `IntentPrediction`, `InteractionEngine`, `Command`, classificacao
local, chamadas remotas ou os dados enviados ao Jev.

Os testes tambem acompanham os source sets: o `mock` valida o vetor completo e
o `dat` valida explicitamente a ausencia do diagnostico.

## JEV-34 concluida

Em 22/09/2026, os testes Android focados passaram e `assembleMockDebug` foi
instalado no Samsung SM-X510 por ADB. Na resolucao fisica 1440x2304, em
paisagem, o cartao permaneceu compacto, o `ScrollView` percorreu o painel de
testes e o diagnostico recolhido mostrou os seis rotulos sem sobreposicao.

`FactCard` passou a reunir titulo, valor e detalhe em uma unica
`contentDescription`, por exemplo `INTENCAO: Pulverizar. SPRAY · 87% · Jev.`.
A arvore de acessibilidade do Android expôs esse contrato para o cartao
`INTENCAO`; a reproducao audivel pelo TalkBack nao foi executada porque o
servico de acessibilidade do tablet permaneceu desligado.

A inspecao tambem encontrou dois limites para as proximas tasks, sem corrigir
esses pontos neste gate: o wordmark do cabecalho era cortado em paisagem por
`ContentScale.Crop`, e o `MainActivity` ainda instancia somente
`LocalIntentClassifier`. JEV-35 corrige o cabecalho antes das capturas; JEV-36
cria cenarios Jev apenas no `mock` para capturas demonstraveis, sem chamada
remota ou mudanca no fluxo `dat`.

## JEV-35 concluida

Em 22/09/2026, o cabeçalho deixou de aplicar `Crop` na largura inteira da
tela. Ele agora centraliza o mesmo PNG dentro de um viewport de altura fixa
de 88 dp e largura responsiva limitada a 480 dp. Nesse enquadramento, o
recorte remove somente a margem branca do arquivo e preserva o wordmark e o
simbolo completos.

`mockDebug` foi recompilado e instalado no Samsung SM-X510. Em paisagem, a
captura visual confirmou a marca inteira, legivel e acima dos chips, sem
sobrepor a jornada. A validacao visual fisica posterior em retrato confirmou
o mesmo resultado: o Android reportou configuracao `port` e `ROTATION_0`, e o
wordmark completo permaneceu dentro do cabecalho de `480 x 88 dp`.

Uma tentativa anterior com tamanho logico temporario produziu uma captura de
pixels preta e nao foi usada como evidencia. Ela serviu apenas para confirmar
os bounds antes da verificacao fisica; a configuracao temporaria foi
restaurada.

## JEV-36 concluida

Em 22/09/2026, o `mock` passou a expor tres escolhas explicitas em `Ajustes
de teste`: `Baseline local`, `Jev · Pulverizar` e `Jev · Nao reconhecida`. As
duas fixtures Jev sao locais, possuem vetores completos dos seis rotulos e nao
fazem chamada de rede.

A escolha fica inicialmente em baseline e, quando uma fixture Jev e
selecionada, altera somente a apresentacao do cartao `INTENCAO`. `SPRAY` mostra
`SPRAY · 87% · Jev`; `UNKNOWN` mostra `UNKNOWN · 85% · Jev · nenhum comando
enviado`. `InteractionEngine`, `LanguageInteractionController`, jornada,
acoes, WebSocket e `Command` continuam usando o caminho local normal. Assim,
o painel e uma ferramenta de captura visual, nao um caminho de decisao ou
execucao. O diagnostico existente permanece no baseline; ele se oculta durante
um cenario para que a selecao altere somente o cartao `INTENCAO`.

O source set `dat` devolve uma lista vazia e, por isso, nao mostra seletor,
fixture ou diagnostico Jev. Os testes por flavor verificam essa separacao; no
SM-X510, as capturas de `SPRAY` e `UNKNOWN` mostraram os dois cartoes sem
sobreposicao e a arvore de acessibilidade preservou a frase completa do cartao.

## Simplificacao apos JEV-37

As fixtures de cenario e o diagnostico estatico foram removidos do app em
23/09/2026. Eles eram uteis antes de existir uma chamada remota real, mas
passaram a competir visualmente com ela. No `mockDebug`, a fonte de intencao
agora oferece apenas `Local` ou `Jev remoto (Gazebo)`; o cartao `INTENCAO` sempre mostra
o resultado do caminho realmente escolhido. `dat` continua sem Jev remoto.

Em 23/09/2026, o novo `mockDebug` foi instalado no Samsung SM-X510. A arvore
de acessibilidade confirmou a ausencia de `Cenario Jev`, `Baseline local` e do
diagnostico estatico; o app iniciou em `Aguardando comando`. Depois dessa
verificacao, o pacote antigo `br.org.agroturtles.maestro` foi removido e ficou
instalado apenas `br.org.agroturtles.maestro.mock`. Nenhuma chamada remota nem
comando ao robo foi feito nesta checagem de interface.

## Objetivo

Permitir que a demonstracao mostre, no mesmo app do Maestro, o que o
classificador Jev entendeu e a probabilidade da classe escolhida. A tela deve
continuar centrada na jornada operacional, sem parecer um console de modelo e
sem transformar a probabilidade em autorizacao de movimento.

## Decisoes

- Reutilizar o cartao `INTENCAO` ja existente. Nao criar uma nova secao,
  grafico ou card aninhado.
- Mostrar uma leitura humana no valor principal, por exemplo `Pulverizar`.
- No detalhe, mostrar `SPRAY · 87% · Jev`. Os 87% sao a probabilidade da
  classe escolhida, nao o campo `confidence` calculado pelo Jev a partir da
  distribuicao.
- Para `UNKNOWN`, mostrar `Nao reconhecida` e `UNKNOWN · 42% · Jev`, junto da
  mensagem segura ja existente. Cor e texto precisam comunicar a recusa; cor
  sozinha nunca e o sinal.
- Para o baseline, manter o formato atual e usar `regra deterministica` ou
  `modelo local` como origem. Isso permite alternar comparativamente na demo
  sem redesenhar a tela.
- A distribuicao completa e o `confidence` do Jev ficam no artefato de
  benchmark. No app, podem aparecer somente em `Ajustes de teste` no flavor
  `mock`, rotulados como diagnostico; nao aparecem no fluxo `dat` da demo.
- Nao exibir transcricao, foto, chave, custo ou log bruto no cartao. A midia
  continua efemera e o cartao deve caber na tela pequena sem mudar de tamanho
  conforme a resposta.

## Fluxo visual

```text
fala
  -> classificacao local ou Jev
  -> cartao INTENCAO
       valor: Pulverizar | Retornar a doca | Nao reconhecida
       detalhe: SPRAY · 87% · Jev
  -> jornada existente
  -> confirmacao por voz, quando a intencao for operacional
```

O cartao comunica a decisao ao operador; ele nao e um controle e nao pode ser
tocado para confirmar, alterar a classe ou enviar um comando.

## Estados de referencia

| Estado | Valor do cartao | Detalhe | Resultado esperado |
| --- | --- | --- | --- |
| Jev escolhe `SPRAY` | `Pulverizar` | `SPRAY · 87% · Jev` | A confirmacao existente continua obrigatoria. |
| Jev escolhe `DOCK` | `Retornar a doca` | `DOCK · 91% · Jev` | Alvo continua dispensado; nenhuma mudanca no lifecycle. |
| Jev escolhe `UNKNOWN` | `Nao reconhecida` | `UNKNOWN · 42% · Jev · nenhum comando enviado` | Nenhum `Command`; segue o fluxo atual de conversa. |
| Timeout ou erro Jev | `Classificacao indisponivel` | `sem decisao remota · nenhum comando enviado` | Falha fechada, sem `Command`; o estado visual explica a recusa. |
| Baseline local | leitura atual | `... · modelo local` | Usado como comparacao lado a lado em capturas separadas. |

## Criterios de aceite

- [x] `predictionSourceLabel` reconhece `JEV` e nao altera os rótulos locais.
- [x] O detalhe usa a probabilidade da classe, com arredondamento consistente,
      e nao chama esse valor de confidence do Jev.
- [x] `UNKNOWN`, timeout e erro ficam claros por texto, sem comando e sem
      confundir o operador com estado de execucao.
- [x] Detalhes de distribuicao aparecem apenas no painel de testes do mock.
- [x] O cartao preserva tipografia, espacamento, cores semanticas e rolagem da
      `MaestroScreen`; nenhuma informacao depende apenas de cor.
- [x] Testes de `JourneyPresentation` cobrem Jev, local, `UNKNOWN` e erro.
- [x] Inspecao no `mockDebug` valida tela compacta, rolagem e a arvore de
      acessibilidade expoe uma frase contextual. A reproducao pelo TalkBack
      continua como verificacao presencial complementar.
- [x] O `mock` oferece fixtures locais selecionaveis para `SPRAY` e `UNKNOWN`,
      enquanto baseline, `dat`, classificador e fluxo operacional permanecem
      separados.

## Limites

- Esta task nao implementa Jev, chamadas de rede, RAG, filtro de topico para
  Qwen, classes novas, missao composta, status de plot ou contrato ROS.
- A tela nao prova calibracao. A evidencia vem do corpus final, de Brier, ECE,
  reliability diagram e cobertura.
