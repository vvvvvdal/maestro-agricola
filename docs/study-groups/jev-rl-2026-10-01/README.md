# Jev e Decisoes com Incerteza

Grupo de estudos de RL

Data: 08/10/2026

Status: planejamento ativo. Este material pertence ao grupo de estudos e nao
ao pitch do Maestro Agricola.

O roteiro falavel de 50 minutos esta em
[`presentation-script.md`](presentation-script.md). Ele separa evidencia
medida, resultados de terceiros e roadmap antes da criacao dos slides.
O deck tecnico correspondente esta em
[`slides/jev-rl-study.html`](slides/jev-rl-study.html); ele nao faz parte de
`docs/pitch/` e preserva a decisao experimental `HOLD`.

## Como o estudo sera executado

Todo trabalho do estudo fica em `test/jev`. Terra planeja as tasks com effort
medio, um worker Gemini condicional via Antigravity CLI investiga uma duvida
concreta em modo somente leitura e Terra revisa o diff com effort alto. O
integrador humano e o unico writer e decisor. A configuracao e os comandos ficam em
[`../../agent-architecture.md`](../../agent-architecture.md).

## Questao central

Jev recebe um estado e perguntas tipadas. Ele retorna escolhas, scores ou
probabilidades. O estudo pergunta como usar essa probabilidade de forma
responsavel em software e, em especial, por que ela nao e uma autorizacao
suficiente para controlar um robo.

Para uma pergunta `Choice`, a saida e estruturada (`choice`, probabilidades e
confianca), e nao texto gerado token a token. O contrato registra
`output_tokens: 0`; isso reduz uma diferenca importante em relacao a um LLM
generativo, mas nao elimina tokens de entrada, custo remoto ou latencia.

O termo RLCD e uma descricao da TypeSafe para o treino do Jev. A empresa nao
publicou arquitetura, dados ou receita de treino. A apresentacao usa o caso
para discutir calibracao, risco seletivo e avaliacao, sem tratar essas
alegacoes como resultado academico estabelecido.

## Estrutura da apresentacao

| Tempo | Assunto | Pergunta que o bloco responde |
| --- | --- | --- |
| 0:00-3:00 | Decisoes pequenas em software | Quando um `if` precisa de julgamento sem virar um agente? |
| 3:00-9:00 | Jev | O que `Choice`, `Noul` e `Score` retornam? |
| 9:00-16:00 | Calibracao e RL | Quando a probabilidade de 0,90 da classe escolhida corresponde a cerca de 90% de acertos? |
| 16:00-21:00 | Xadrez | O que Jev vs Fable vs Astra realmente mediu? |
| 21:00-27:00 | Casos publicos | Onde decisao rapida parece uma boa fronteira? |
| 27:00-34:00 | Maestro atual | Quais barreiras separam linguagem de movimento? |
| 34:00-40:00 | Jev no intent e no app | Como trocar somente o classificador e mostrar a decisao sem liberar acoes? |
| 40:00-44:00 | App e reserva local | Como mostrar a decisao sem alegar chamada remota ou comando? |
| 44:00-46:00 | Roadmap de classes | Que novas classes exigiriam contrato? |
| 46:00-50:00 | Debate | Qual evidencia escolheria o proximo caminho? |

O encerramento reserva quatro minutos para debate. O roteiro falavel e a fonte
canonica de tempo, transicoes e limites; nao e uma defesa do Jev como
substituto automatico do classificador local.

## Xadrez como caso de leitura de benchmark

Uma partida de blitz 5+0, com uma chamada de API por lance, reportou estes
resultados:

| Partida | Resultado reportado | Interpretacao permitida |
| --- | --- | --- |
| Jev vs Fable 5.1 | Jev venceu no tempo; Fable tinha +16 de material e uma segunda dama no lance 29 | Jev teve menor tempo por decisao naquele formato; isto nao mede forca de xadrez |
| Jev vs Astra | Astra deu mate em 18 lances, com 2:27 restantes | Uma tarefa de calculo e busca favoreceu o modelo de raciocinio nesta partida |

O valor pedagogico do exemplo esta no detalhe do harness. Relogio, uma unica
chamada por lance e ausencia de busca sao restricoes que definem o que venceu.
O resultado nao deve aparecer como "Jev ganhou de Fable no xadrez" sem a
explicacao do relogio.

## Casos de teste para mostrar

### Ticket de suporte

Um unico estado pode produzir departamento (`Choice`), urgencia (`Noul`) e
severidade (`Score`). Serve para explicar a interface, nao para alegar que
Jev domina suporte ao cliente.

### Destinatario de NPC apos ASR

No benchmark publico, cada fala transcrita e julgada para cada NPC: a fala foi
dirigida a ele ou apenas o mencionou? O repositorio reporta F1 de 0,96 em texto
limpo e 0,93 em transcricoes sem pontuacao, em minusculas e com nomes mal
reconhecidos. Ele e um bom paralelo para a entrada de voz do Maestro, mas e
resultado de terceiros em um dominio diferente.

### BANKING77

Uma avaliacao publica aplicou Jev a 3.080 mensagens de teste com 77 intencoes,
usando definicoes e exemplos no pedido, sem ajuste dos pesos. Ela reporta
92,40% contra 93,66% do BERT fine-tuned citado pelo estudo original. O caso
mostra uma troca real: velocidade de prototipacao contra um classificador
especializado e local; nao prova que o segundo se tornou desnecessario.

### Maestro

O experimento deve limitar Jev a escolher entre classes declaradas. Depois da
classe, o sistema atual ainda aplica `TargetResolver`, estado valido,
confirmacao por audio, expiracao, UUID, schema e validacao no bridge antes de
enviar qualquer comando ROS.

Um anti-exemplo obrigatorio: camera identifica `plot-03`, a fala pede
`plot-01` e a intencao e `SPRAY`. O resultado precisa ser `AMBIGUOUS`, sem
`Command`, mesmo que o classificador acerte a intencao.

## Escopo decidido e roadmap de classes

A primeira fase do experimento nao amplia o catalogo: Jev substitui somente a
implementacao do classificador para `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`,
`CANCEL` e `UNKNOWN`. Isso permite uma comparacao direta contra o baseline
local. Cada execucao seleciona uma unica implementacao, `LocalIntentClassifier`
ou `JevIntentClassifier`; os dois nao votam nem classificam a mesma fala no
caminho operacional. Qwen continua recebendo `UNKNOWN` sem filtro Jev de
topico, e RAG foi descartado deste recorte para nao confundir decisao
estruturada com busca de conhecimento.

As fronteiras de linguagem que alimentarao os corpora ficam em
[`rubrics.md`](rubrics.md). A primeira rubrica, `SPRAY`, deixa explicito que a
classe reconhece um pedido atual de pulverizacao, sem resolver alvo nem criar
autorizacao de movimento.

As classes abaixo nasceram como roadmap de produto e viram o bloco final da
apresentacao. Apos JEV-38, elas tambem tem uma sequencia de implementacao em
[`TASKS.md`](TASKS.md): leitura, historico e inspecao ja existem localmente no
`mockDebug`; preview e execucao de missao continuam no roadmap. O corpus de
desenvolvimento das tres rotas locais passou 32/32, mas nao e uma comparacao
com Jev nem evidencia de campo.

Jev permite alterar a lista de opcoes de uma pergunta `Choice`. Isso acelera o
experimento de uma nova classe, mas nao cria um comando seguro por si so. Cada
opcao precisa de criterio que a diferencie das vizinhas, exemplos positivos e
negativos quando a fronteira for ambigua, e uma saida `UNKNOWN` que cumpra o
papel de `other` ou `none of the above`. Toda classe que produz efeito
observavel no robo precisa de contrato versionado, validacao de estado, testes
e aprovacao humana antes de entrar no catalogo operacional.

| Classe candidata | Efeito pretendido | Situacao para o estudo | Condicao para virar operacao |
| --- | --- | --- | --- |
| `STATUS_QUERY` | Ler e narrar estado atual do robo; acompanhar uma operacao aceita ate termino | Implementada localmente no `mockDebug` | Rota `/read-only`, correlacao pelo `command_id` e estados terminais sem novo `Command` |
| `PLOT_STATUS_QUERY` | Informar a ultima missao simulada `SPRAY` concluida para um talhao | Implementada localmente no `mockDebug` | Historico em memoria, rota `/read-only` e resposta sem `Command`; nao afirma aplicacao fisica |
| `INSPECT_TARGET` | Capturar sob demanda e reportar marcador/QR | Implementada localmente no `mockDebug` | Imagem em memoria, permissao, politica de QR e nenhum `Command` |
| `MISSION_PREVIEW` | Reconhecer pedido composto e mostrar `MissionPlan` tipado | Especificada; ainda nao existe no app ou bridge | Parser deterministico, alvo mapeado, confirmacao por etapa e executor que pausa em falha |
| `PAUSE` | Pedir pausa de missao em andamento | Candidata, mas nao usar na demo fisica | Bridge precisa de primitive de pausa segura e estado `PAUSED` |
| `RESUME` | Retomar apenas uma missao pausada valida | Candidata dependente de `PAUSE` | Revalidar missao, alvo, expiracao e confirmacao explicita |
| `SCOUT` | Navegar por rota mapeada para inspecao | Apenas ideia de produto | Novo contrato, rota permitida, alvo mapeado, confirmacao e E2E proprio |
| `EMERGENCY_STOP` | Parar diante de risco imediato | Fora do Jev e fora do reconhecimento de fala comum | Controle fisico e cadeia de seguranca independente do modelo |
| Navegacao livre ou ajuste de dose | Movimento/dosagem fora de um contrato fechado | Fora do escopo | Nao adicionar sem especificacao de seguranca e aprovacao humana |

`STATUS_QUERY` e `INSPECT_TARGET` oferecem a melhor extensao inicial porque nao
transformam uma classificacao em movimento. `PAUSE`, `RESUME` e `SCOUT` devem
ser mostradas como desenho de futuras acoes, nao como capacidades entregues.
Quando forem independentes, como "o usuario pediu status?" e "o usuario pediu
inspecao?", elas podem ser perguntas atomicas paralelas; o codigo resolve
conflitos e decide quais respostas usar.

`PLOT_STATUS_QUERY` foi priorizada antes das outras consultas por representar
uma pergunta agricola concreta: "qual foi a ultima pulverizacao do plot-03?".
Ela precisa de historico de operacoes concluidas; essa infraestrutura e valor
do Maestro e existe independentemente de Jev. Para qualquer classe nova, o
primeiro roteador sera local e separado do benchmark congelado dos seis
intents. Jev so entra em uma comparacao posterior, no mesmo corpus e contra o
mesmo contrato.

`MISSION_PREVIEW` reconhece que o operador pediu uma missao composta, mas nao
produz a missao. O Maestro faz parser e validacao deterministica para um
`MissionPlan`, mostra as etapas e exige confirmacao antes de cada acao fisica.
O contrato e o schema estao em
[`../../tasks/mission-preview-contract.md`](../../tasks/mission-preview-contract.md).

## Arquitetura do experimento

```text
transcricao
  -> LocalIntentClassifier (baseline) ou JevIntentClassifier (somente na branch experimental)
  -> IntentPrediction
  -> InteractionEngine e TargetResolver existentes
  -> confirmacao existente
  -> Command e bridge existentes
```

O Jev nao e um pre-filtro do Qwen. Se a escolha for `UNKNOWN`, o caminho atual
permanece `UNKNOWN -> LanguageRouter -> QwenDomainAssistant -> CHAT |
OUT_OF_SCOPE`. Nao ha RAG neste estudo.

`STATUS` deve seguir uma interface de consulta separada e somente leitura.
`INSPECT_TARGET` deve usar a fronteira de captura existente, sem persistir
imagem por padrao. Nenhuma dessas duas classes deve burlar o
`InteractionEngine` ou conceder acesso a ROS para Jev.

O contrato minimo da chamada experimental esta em
[`choice-contract.md`](choice-contract.md): uma `Choice`, os seis rotulos e
modelo fixo. Ele descreve request e resposta, mas nao realiza chamada nem
autoriza o adaptador antes das tasks seguintes.

### Probabilidade e confidence no adaptador

`Choice` devolve a opcao vencedora, um vetor de probabilidades e um campo
`confidence`. A documentacao da TypeSafe define esse ultimo como uma medida da
concentracao do vetor, nao como a probabilidade da opcao vencedora. `Noul` nao
devolve `confidence`.

O `IntentPrediction.confidence` atual equivale a probabilidade maxima do
softmax local. Por compatibilidade, o adaptador experimental deve preencher
esse campo com `probabilities[choice]`, nunca com o `confidence` do Jev. O
vetor completo e o `confidence` do Jev precisam permanecer no registro de
benchmark, em uma estrutura experimental separada, para permitir analise de
calibracao e abstencao sem mudar o contrato operacional de modo silencioso.

`JevIntentClassifier` ja existe como adaptador experimental injetavel na branch
`test/jev`, validado por fakes locais. Ele nao esta ligado a `MainActivity` e
nao contem cliente HTTP no app. A rodada independente de recuperacao produziu
evidencia remota sanitizada e registrada para apresentacao, mas a decisao e `HOLD`: uma
aceitacao insegura e os limites da amostra impedem adocao operacional. Ver
[`../../tasks/jev-experimental-decision.md`](../../tasks/jev-experimental-decision.md).

### Visualizacao no app

O app ja apresenta o cartao `INTENCAO` com classe, percentual e origem. Na
rodada Jev, ele mantem a mesma composicao e passa a mostrar, por exemplo,
`Pulverizar` e `SPRAY · 87% · Jev`. O percentual e a probabilidade da classe
escolhida; o `confidence` do Jev e o vetor completo continuam no benchmark e
no painel de testes, nao no fluxo do operador. O plano detalhado esta em
[`../../tasks/jev-ui-decision-visibility.md`](../../tasks/jev-ui-decision-visibility.md).

## Avaliacao

Comparar o `LocalIntentClassifier` e Jev nos mesmos corpora separados de
desenvolvimento e avaliacao final. O corpus deve conter portugues brasileiro,
ruido de ASR, negacao, mencao historica, fora de dominio, alvo conflitante,
injecao e falha remota.

Registrar:

- matriz de confusao, macro-F1 e cada aceite perigoso;
- Brier multiclasses, top-label ECE e reliability diagram calculados a partir
  das probabilidades;
- cobertura no erro empirico escolhido;
- p50/p95 fim a fim, custo, falhas e versao exata do modelo;
- diferenca entre resposta estruturalmente valida e decisao correta.

O corpus atual de seis rotulos e pequeno demais para provar calibracao. Sem uma
amostra maior e rotulada, os graficos de calibracao devem aparecer como plano
de avaliacao, nunca como resultado.

O corpus de desenvolvimento fica em [`corpus/development.tsv`](corpus/development.tsv).
Ele e sintetico, sanitizado e ajustavel; o seu formato e as regras de uso ficam
em [`corpus/README.md`](corpus/README.md). O corpus final de seguranca esta em
[`corpus/final.tsv`](corpus/final.tsv) e foi congelado antes da rodada remota
final; seu manifesto registra as restricoes de reproducao. Ele foi reservado
em uma rodada interrompida e permanece inelegivel para repeticao. A medicao
final de recuperacao usou corpus independente, com manifest proprio, sem
alterar os textos originais; sua evidencia nao promove o Jev ao APK.

O harness [`../../../tools/jev_intent_harness.py`](../../../tools/jev_intent_harness.py)
executa o baseline local e uma fixture Jev contra os mesmos IDs e produz um
registro por caso sem repetir a fala. Os runners remotos JEV-40 e JEV-41R
preencheram fixtures somente dentro dos subtetos aprovados; o app Android
continua sem cliente HTTP ou chave Jev.

Os resultados que nunca podem criar `Command`, assim como a diferenca entre
evidencia do baseline e requisitos pendentes do adaptador Jev, estao em
[`safety-gates.md`](safety-gates.md).

O `confidence` do Jev tambem pode orientar abstencao, pois indica se a
distribuicao esta concentrada ou dividida. No Maestro, mesmo alta probabilidade
ou alto `confidence` nunca removem a confirmacao por audio para uma acao fisica.

## Orcamento de creditos

O estudo tem US$5 de creditos. Antes de qualquer chamada remota, definir limite
no console e registrar cada rodada. Foram consumidos US$0,000146832 no smoke e
US$0,001472394 na recuperacao final independente. O corpus `final.tsv` segue
inelegivel, e nenhuma nova rodada, gravacao remota ou repeticao pode ocorrer
sem nova decisao humana e subteto registrado.

## Limites obrigatorios

- Jev e hospedado. Nao colocar chave no APK ou no repositorio.
- Nao enviar fotos, audio ou transcricoes sem aprovar dependencia e fluxo de
  dados.
- Jev nao recebe `Command`, WebSocket, ROS, estado do robo ou resolucao de
  alvo.
- A confirmacao por audio e a validacao do bridge continuam obrigatorias.
- O stop de emergencia nao depende de Jev, Qwen, ASR ou rede.

## Fontes

- [TypeSafe: introducao oficial](https://docs.typesafe.ai/introduction)
- [TypeSafe: Choice](https://docs.typesafe.ai/primitives/choice)
- [TypeSafe: Confidence](https://docs.typesafe.ai/confidence)
- [TypeSafe: AI primer e RLCD](https://docs.typesafe.ai/introduction/machine-learning-primer)
- [Flavio Copes: deep dive sobre Jev](https://flaviocopes.com/jev/)
- [AI/ML API: thread de xadrez republicada](https://threadnavigator.com/thread/2100372930282573876/)
- [Jev Benchmark & Playground](https://github.com/wondertwins/jev-benchmark)
- [Jev em BANKING77](https://github.com/simonmesmith/jev-banking77-experiment)
- [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)
- [Jev como juiz: resultado negativo pre-registrado](https://github.com/clduab11/jev-test)
- [Triagem de incidentes de frota](https://github.com/robokrunch/jev-physical-ai)

Fontes comunitarias servem como casos de estudo. Elas nao substituem um
benchmark reproduzivel no dominio do Maestro.
