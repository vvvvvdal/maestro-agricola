# Roteiro falavel: Jev, RLCD e o experimento no Maestro

Duracao: **50 minutos**. Sao 45 minutos de conteudo/demo e 5 minutos de debate.
Este roteiro e para um grupo de estudos de RL, nao um pitch e nem uma defesa de
adocao do Jev no Maestro Agricola.

## Tese e combinados com a audiencia

Tese: Jev torna barata uma decisao probabilistica tipada. RLCD promete calibrar
suas probabilidades, mas a evidencia disponivel ainda nao autoriza delegar
controle do robo. A pergunta da apresentacao e se ele acrescenta valor
mensuravel ao Maestro, alem de ser uma ferramenta nova e chamativa.

**Ambiguidades resolvidas antes do ensaio:** `output_tokens` nao foi zero no
nosso experimento (69 a 71 por chamada na fixture JEV-41R). O fornecedor anuncia
**preco zero para tokens de saida**; Jev nao gera prosa token a token. Sao
afirmacoes diferentes. RLCD e objetivo declarado pela TypeSafe, sem receita de
treino publicamente reproduzivel. Os posts do X sao demos de terceiros, nao
benchmarks independentes. O conteudo exato do video de Stefan e do post de
Luiz deve ser conferido antes de projetar: aqui eles nao fundamentam claims.

**Alerta de ensaio:** o deck HTML existente ainda exibe `46 MIN + 4 MIN` e
uma nota antiga afirma `output tokens zero`. Como esta task altera somente o
roteiro, usar o relogio deste arquivo e corrigir essa nota **oralmente** ao
apresentar. Nao usar a nota do deck como evidencia de uso ou preco.

Antes de iniciar, distinguir tres tipos de afirmacao:

- **Medido no Maestro**: artefato versionado, com escopo e limite explicitados.
- **Resultado de terceiros**: caso publico em outro dominio; serve para leitura
  de benchmark, nao para provar o nosso produto.
- **Hipotese ou roadmap**: desenho de proxima etapa, ainda sem implementacao.

## Mapa de tempo

| Tempo | Bloco | Tipo dominante | Visual previsto |
| --- | --- | --- | --- |
| 0:00-4:00 | O que e Jev? O `if` e o fundador | Fonte oficial | fronteira e decisao probabilistica |
| 4:00-10:00 | Jev, LLM e custo de saida | Fonte oficial + medido | `Choice` e uso real de tokens |
| 10:00-23:00 | RL, RLHF, RLVR, RLCD e calibracao | Fonte oficial + medido | ciclo RL e reliability JEV-51 |
| 23:00-28:00 | Casos externos e xadrez | Terceiros | compaction, skills, simulador e harness |
| 28:00-32:00 | Limites e Laya | Fonte primaria + medido | tipagem, erro e contraponto local |
| 32:00-35:00 | Maestro em tres minutos | Produto atual | pipeline e alvo |
| 35:00-41:00 | Jev no Maestro, resultado e privacidade | Medido | comparacao, matriz e gate remoto |
| 41:00-45:00 | Demo e conclusao | E2E ou fixture identificada | fluxo e reserva |
| 45:00-50:00 | Debate | Perguntas de RL | perguntas |

Total: **45 minutos de conteudo/demo + 5 minutos de debate = 50 minutos**.
Se atrasar, cortar exemplos externos; preservar RLCD, `CANCEL -> CONFIRM` e
fronteiras de controle.

## 0:00-2:30 - A pergunta

**Fala-guia**: "Toda aplicacao de IA chega a uma bifurcacao: executar,
recusar, pedir revisao ou mandar para outra etapa. Jev foi feito para esse
instante. Ele recebe estado e alternativas; devolve uma decisao tipada e
probabilidades. A pergunta aqui e se essa decisao acrescenta algo mensuravel
ao Maestro sem atravessar as barreiras que protegem o movimento."

Desenhar a fronteira:

```text
fala -> decisao tipada -> regras e estado deterministico -> confirmacao -> robo
```

Transicao: "O Jev entra somente no segundo termo dessa linha. Entao vamos ver
o que ele devolve e o que ele nao promete."

Em 20 segundos: Jev e o primeiro *System One Model* publico da TypeSafe. Seu
fundador, Diogo Almeida, relata ter trabalhado na OpenAI com seguimento de
instrucoes; a [pagina da equipe](https://typesafe.ai/team) o apresenta como
coinventor de RLHF/InstructGPT. Isso contextualiza a origem, nao prova o
desempenho. O nome Jev remete a William Stanley Jevons; "System 1" e uma
inspiracao de produto, nao uma equivalencia cognitiva demonstrada. [S13]

## 2:30-4:00 - A metafora do `if`

Depois da fronteira, usar "Jev e um `if` com IA" apenas como intuicao. Um
`if` classico executa uma condicao definida pela equipe; Jev estima qual
alternativa de um catalogo fechado parece adequada.
Portanto, alguem ainda precisa escrever a politica: limiar, recusa,
confirmacao, efeito permitido e acao para falha remota.

Fala-guia: "A metafora fica boa quando ela nos lembra de manter a saida
pequena. Ela fica ruim se esconder que probabilidade nao escolhe sozinha a
acao do sistema. No Maestro, essa politica continua em codigo deterministico."

**Fonte**: [S8], resultado de terceiro usado como metafora, nao como definicao
formal.

## 4:00-10:00 - O que o Jev retorna e como difere de LLM

Apresentar `Choice` como uma pergunta de catalogo fechado: por exemplo,
`SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`. A resposta contem
uma opcao vencedora e probabilidades para as opcoes. `Noul` responde uma
pergunta booleana; `Score` produz um escore. Para o Maestro, a primitiva
relevante e `Choice`.

**Ponto central sobre tokens**: `Choice` nao escreve uma resposta em prosa
token a token. A API ainda contabiliza tokens de saida: no exemplo da
[documentacao](https://docs.typesafe.ai/primitives/choice), 34; nas 60
respostas da fixture JEV-41R do Maestro, 69 a 71 por chamada. A TypeSafe anuncia
**cobranca zero por tokens de saida**, o que nao equivale a zero tokens nem a
chamada gratuita: ha tokens de entrada, rede e custo. A saida fechada nao
cresce como um texto generativo longo. [S13][E1a]

Fala curta: "Em vez de pedir um paragrafo e depois tentar interpreta-lo, damos
seis alternativas permitidas e recebemos uma escolha. Nao ha texto de saida
para ser gerado, parseado ou usado como comando."

Comparar a **mesma tarefa**, entrada, qualidade, custo e latencia ponta a
ponta. LLM generativo produz texto aberto, normalmente token a token; e
adequado a conversa e escrita, mas precisa de schema/validacao num fluxo de
controle. `Choice` seleciona uma opcao de catalogo fechado. O post de Grajeda
[S14] comunica os grandes ganhos alegados; a propria TypeSafe diz que as
cifras de seus workflows estao provavelmente na ponta alta dos ganhos reais.
No Maestro, Qwen continua no caminho `UNKNOWN` de conversa e Jev so e avaliado
como alternativa ao classificador de seis intents. [S13]

Explicar uma distincao importante: a probabilidade da classe escolhida e o
valor preservado em `IntentPrediction.confidence`. O campo `confidence` do Jev
descreve concentracao da distribuicao; nao deve ser apresentado como se fosse a
probabilidade da classe vencedora. `Noul` nao retorna esse campo.

**Pergunta para a sala**: "Que decisao discreta, frequente e ambigua voces ja
viram que nao deveria virar um agente com ferramentas livres?"

**Fonte**: [S1]-[S3].

## 10:00-23:00 - RL, RLHF, RLVR, RLCD e calibracao (bloco principal)

**10:00-13:00, RL basico.** Desenhar o ciclo `estado s -> acao a -> recompensa
r -> novo estado s'`. Uma politica `pi(a|s)` escolhe acoes; o treinamento busca
maximizar retorno esperado. Usar um jogo como exemplo, sem sugerir que Jev
aprende a controlar o TurtleBot. "RL e uma familia de metodos. Os nomes a
seguir diferem sobretudo pelo sinal de qualidade e pelo comportamento que
incentivam; nenhum nome sozinho especifica arquitetura ou algoritmo."

**13:00-17:00, RLHF e RLVR.** No RLHF, feedback/preferencia humana orienta o
ajuste: uma resposta preferida por pessoas nao e necessariamente uma
probabilidade calibrada ou uma acao segura. No RLVR, uma tarefa admite
verificador relativamente objetivo, como resultado matematico ou teste
executavel. Acertar uma resposta verificavel nao garante, por si, que 0,8
signifique 80% de acerto. Sao objetivos distintos, nao etapas obrigatorias de
uma receita. Evitar dizer que todo RLHF usa exatamente o mesmo algoritmo ou
que necessariamente causa alucinacao. [S4]

**17:00-20:00, a alegacao RLCD.** *Reinforcement Learning for Calibrated
Decisions*, segundo a TypeSafe, otimiza decisoes e probabilidades: em muitos
casos comparaveis, previsoes com 0,8 deveriam estar corretas perto de 80%
das vezes. Isso e propriedade de grupos, nao garantia de um caso individual.
"Consigo explicar o objetivo publico. Nao consigo reconstruir o treino a
partir do material divulgado: faltam recompensa, dados, detalhes de algoritmo,
arquitetura e ablacoes para isolar o efeito de RLCD do efeito da interface e
do sampler." Nao inventar uma funcao de recompensa. [S4][S13]

**20:00-23:00, o teste da promessa.** Acerto de classe e calibracao sao
perguntas diferentes. Brier multiclasses penaliza probabilidades afastadas do
rotulo verdadeiro; top-label ECE compara confianca media e frequencia de acerto
por faixas. Mostrar o reliability diagram JEV-51 e ler o `n` de cada bin.
O ECE de Jev (0,0787) e do local (0,0810) numa unica rodada de 60 falas
sinteticas nao prova calibracao superior generalizavel. O erro
`CANCEL -> CONFIRM (0,75)` demonstra por que tipagem e alta probabilidade nao
sao seguranca. [E1][E2]

**Pergunta para a sala**: "Que holdout congelado, replicacao e estratos de
seguranca seriam necessarios? ASR real, negacao, hesitacao, conflito de alvo e
fora de dominio deveriam ser medidos separadamente?"

## 23:00-28:00 - Casos externos e xadrez: ler o harness

Dar cerca de um minuto por caso. Se atrasar, ficar com compaction, JevPilot e
xadrez. Em todos: "Que estado o modelo recebeu, quais opcoes podia escolher e
o que o codigo ou outro modelo executou?"

1. **Compaction de Tamara Tran**: Jev pontua chamadas e resultados para
   manter, truncar ou descartar. O codigo executa a selecao; sumario pode ser
   fallback. Medir tambem se contexto necessario foi perdido. [S11][S15]
2. **Selecao de skills de Daniel Avila**: uma escolha curta antes de carregar
   contexto maior. Avaliar falso descarte e custo da chamada adicional; a
   opcao "nenhuma skill" importa. [S10]
3. **JevPilot/HighwayEnv**: o post fala em "Tesla Full Self Driving", mas a
   evidencia e simulacao com estado e acoes fechados. Nao e carro nem camera
   real. [S6][S9]
4. **Video de Stefan**: opcional, apos conferir o original. Identificar na
   demonstracao o que e decisao Jev e o que e renderizacao, estado e regra
   implementados fora dele. Sem essa verificacao, pular. [S16]
5. **Xadrez**: usar como contraexemplo ao slogan "mais rapido = melhor".

**Fala-guia**: "Este e o caso chamativo, mas e principalmente uma licao de
leitura de benchmark. Em uma partida blitz 5+0, com uma chamada de API por
lance e sem busca, Jev venceu Fable 5.1 no tempo. Fable tinha +16 de material e
uma segunda dama no lance 29. Entao nao vou chamar isso de Jev mais forte em
xadrez: naquele harness, ele decidiu mais rapido."

"Contra Astra, houve mate em 18 lances, com Astra ainda tendo 2:27. Calculo e
busca sao partes centrais de xadrez; essa fronteira favoreceu um modelo de
raciocinio naquela partida. O relogio, a politica de uma chamada e a ausencia
de busca definem a conclusao."

**Fonte**: [S5], resultado de terceiros. Nao transformar partida isolada em
ranking de forca em xadrez.

## 28:00-32:00 - Rapido, mas limitado; o contraponto Laya

"Rapido em decisao curta nao significa raciocinio longo, e saida tipada nao
significa resposta correta." O xadrez ilustra a primeira limitacao; o erro
`CANCEL -> CONFIRM` do Maestro, a segunda.

Usar os casos abaixo como reserva de explicacao, nao como mais tres demos
obrigatorias. Cada linha e resultado de terceiros em dominio diferente.

| Caso | O que ilustra | O que nao permite concluir |
| --- | --- | --- |
| Direcao no HighwayEnv / JevPilot | Um estado fechado pode alimentar uma escolha entre acoes permitidas; o autor reporta 60 segundos sem colisao. | Que Jev foi validado em carro real, com camera real, ou que a comparacao contra Codex e um benchmark controlado. |
| Triagem de PR | Um diff limitado pode virar `SAFE / REVIEW / BLOCK`, risco e checks, sem gerar uma longa resenha. | Que a ferramenta le o repositorio inteiro, executa testes, substitui revisao humana ou economiza uma quantidade geral de tokens. |
| Skills e compaction | Escolher uma skill relevante, ou manter/descartar contexto de tool calls, pode ser uma decisao pequena antes de uma chamada cara. | Que a decisao esta sempre certa; "nenhuma skill" e fallback para sumario ainda sao necessarios. |

**Fala-guia**: "No simulador, o estado e as acoes ja sao fechados. Na triagem
de PR, o artefato de entrada e limitado e a saida pode ser uma decisao curta.
Esse segundo caso e interessante porque evita gerar uma resenha longa quando o
primeiro passo e so encaminhar o PR. A pagina da demo anuncia cerca de 300 ms
e US$0,00003 por chamada; trate isso como alegacao da demo, nao como comparacao
de tokens ou benchmark independente. Ela mesma diz que nao le o repo inteiro
nem roda testes."

**Fala sobre Laya**: "A chegada rapida de Laya mostra que a interface de
decisao pode ter outras implementacoes. `laya-mlx` oferece pesos abertos e
runtime local para Apple Silicon. Seu repositorio reporta medianas de 7,39 a
13,42 ms para **uma pergunta curta** no M3 Max, sem tempo de carregamento; o
loop de Snake faz tres perguntas e tem camada de seguranca. Isso nao e
comparacao pareada com Jev nem evidencia no Android do Maestro. Para nos,
inferir localmente seria atraente por latencia e minimizacao de dados, mas
exige mesmo corpus, gates, aparelho alvo e medicao." [S12]

O post de Luiz [S17] pode introduzir a discussao **depois de conferido**. Nao
atribuir a ele uma tese tecnica que nao foi verificada.

**Fontes**: [S6]-[S12], resultados de terceiros; [S12] e fonte primaria do
projeto Laya.

## 32:00-35:00 - Maestro em tres minutos

**Fala de abertura**: "Maestro e uma interface hands-free para um robo
agricola: fala para pedir uma acao, marcador visual ou talhao cadastrado para
identificar o alvo, confirmacao por audio e um comando JSON versionado para o
bridge ROS 2. Na demonstracao, a execucao e no Gazebo. `SPRAY` nao aciona
`UNDOCK` nem `DOCK` automaticamente." A captura da camera e sob demanda;
o frame e processado em memoria ate virar `target_id`. A camera dos oculos
Meta reais continua sem validacao fisica. [E6]

Mostrar a cadeia real:

```text
transcricao
  -> LocalIntentClassifier ou JevIntentClassifier
  -> IntentPrediction
  -> InteractionEngine + TargetResolver
  -> confirmacao por audio
  -> Command JSON versionado + bridge
  -> ROS
```

## 35:00-41:00 - Jev no Maestro: utilidade, resultado e privacidade

**35:00-37:00, fronteira. Fala-guia**: "O Jev, se usado, troca somente uma
implementacao de classificador para os mesmos seis rotulos. Cada execucao usa o local ou o Jev;
eles nao votam sobre a mesma fala. Ele nao recebe foto, audio, `Command`,
WebSocket, ROS, estado do robo nem resolucao de alvo."

Usar o anti-exemplo obrigatorio: a camera identifica `plot-03`, a fala pede
pulverizar `plot-01` e o classificador acerta `SPRAY`. Mesmo assim, o resultado
e `AMBIGUOUS`, sem `Command`, porque o alvo esta em conflito.

`UNKNOWN` segue inalterado para `LanguageRouter -> QwenDomainAssistant -> CHAT
| OUT_OF_SCOPE`. Nao ha filtro Jev para o Qwen nem RAG neste experimento.

### Privacidade: o que realmente acontece

Nao dizer que o app "so le QR Code". No caminho de camera, ele solicita uma
foto sob demanda, processa o QR/marcador localmente em memoria e reduz o frame
a `target_id`; o Maestro nao preve gravar imagem, audio ou transcricao por
padrao. A validacao de camera nos oculos Meta reais continua pendente.

No caminho padrao, a transcricao curta fica na memoria da atividade e entra no
classificador local. **O `LocalIntentClassifier` nao e um detector geral de
CPF**; nao dizer que ele reconhece e bloqueia todo dado pessoal. No modo
remoto de demonstracao, restrito a `mockDebug`, o
operador da consentimento de sessao e app/proxy bloqueiam antes da rede alguns
padroes evidentes: e-mail, telefone, CPF/CNPJ, URL, texto longo ou fora do
escopo. A fala bloqueada e descartada localmente, sem Jev, Qwen ou `Command`.
Ela nao e reutilizada automaticamente pelo modo local; o operador precisa
selecionar Local e iniciar nova interacao. No SM-X510, um **CPF sintetico** foi
bloqueado com "Fala nao enviada ao Jev". [E6][E7]

Isso e **minimizacao preventiva**, nao anonimizacao, detector perfeito de dado
pessoal, auditoria juridica ou declaracao de conformidade LGPD integral. Essa
honestidade e parte da demonstracao: privacidade e uma fronteira de sistema,
nao um aviso decorativo.

**37:00-39:00, evidencia medida.**

Mostrar o SVG de comparacao e depois a matriz. Falar os numeros com o escopo:

- Em uma rodada independente, com **60 falas sinteticas**, Jev acertou 54/60,
  macro-F1 0,9010 e teve uma aceitacao insegura.
- O baseline local acertou 48/60, macro-F1 0,8026 e teve tres aceitacoes
  inseguras.
- Jev teve p95 remoto de 2.100,575 ms e custo de US$0,001472394; o local teve
  p95 de 0,293 ms e custo zero nesse harness.
- O erro Jev foi `CANCEL -> CONFIRM` com probabilidade 0,75.

**Fala-guia**: "O resultado e favoravel como sinal de pesquisa, mas a decisao
foi `HOLD`. Uma aceitacao insegura impede dizer que isso esta pronto para
controle; alem disso, temos uma rodada, um corpus sintetico e medidas feitas no
host do harness, nao no Android, no campo ou no robo."

**39:00-40:00, a resposta honesta a 'e util ou e vitrine?'** "Faz sentido como
hipotese para rotear falas variadas num catalogo fechado e pode reduzir o
trabalho de escrever regras para novas *categorias de linguagem*. Mas cada
funcao nova ainda exige contrato, estado, permissoes, tratamento de falhas,
corpus proprio e gates de seguranca. Jev nao cria a funcao. O ganho observado
e experimental e nao justifica adocao operacional." Consultas de historico,
inspecao de alvo e missao composta ja foram implementadas **localmente**,
sem Jev. [E8]

**40:00-41:00, privacidade.** Explicar a diferenca entre caminho local e
remoto acima. A fala bloqueada nao e enviada; isso e minimizacao preventiva,
nao anonimização ou conformidade integral com a LGPD. Android/STT, DAT e
TypeSafe sao fronteiras de tratamento distintas. [E6][E7]

**Evidencia medida**: [E1]-[E3].

## 41:00-45:00 - Demo, reserva e conclusao

**Plano A:** com rede, proxy, tablet e Gazebo estaveis, mostrar uma fala que
Jev remoto classifica no `mockDebug`, a intencao identificada como Jev, a
espera pela confirmacao por audio e so entao `Command` estruturado para
o Gazebo. O caminho remoto ate `UNDOCK` no Gazebo foi observado no SM-X510,
mas a execucao ao vivo continua dependente desses componentes. [E9]

**Plano B:** se houver video gravado e conferido da mesma execucao, mostra-lo
com data, aparelho e indicacao de simulacao. **Nao existe video de reserva
versionado nesta pasta ate agora.** Sem video, usar as capturas offline abaixo
e dizer explicitamente que elas demonstram UI, nao chamada remota nem E2E.

Mostrar as tres capturas: baseline, `SPRAY - 87% - Jev` e `UNKNOWN - 85% - Jev
- nenhum comando enviado`. Manter a legenda inteira:

> fixture mock local - nao executa o robo

**Fala-guia**: "O objetivo visual e tornar a decisao auditavel para o operador:
classe, probabilidade e origem no mesmo cartao `INTENCAO`. A probabilidade nao
e um botao e nao remove a confirmacao por audio. Essas capturas sao fixtures
locais do `mockDebug`; nao sao chamada Jev remota, ASR, alvo, confirmacao,
bridge ou ROS."

Explicar a reserva: tres capturas equivalentes foram geradas com Wi-Fi
desligado e o Wi-Fi foi restaurado depois. Elas evitam dependencia de rede; nao
simulam um resultado remoto.

**Evidencia de UI local**: [E4] e [E5].

**Conclusao falada:** "Jev muda a interface entre modelo e software: escolha
tipada, probabilidades e saida textual minima. RLCD propoe otimizar a
qualidade dessas probabilidades, mas falta descricao de treino reproduzivel e
validacao externa. No nosso dominio, a media melhorou em uma rodada sintetica
e houve uma recusa critica interpretada como confirmacao. Por isso a decisao
continua `HOLD`. O valor do Maestro depende de alvo, regras, confirmacao e
simulacao, independentemente de Jev."

### Se houver 20 segundos: missao composta entregue pelo Maestro

Frase curta: "O Maestro tambem executou uma missao de varias etapas no
Gazebo, com parser local e confirmacao por etapa; Jev nao planejou nem
executou essas acoes." Os detalhes abaixo sao nota de apoio para perguntas,
nao fala adicional dentro dos 20 segundos.

Exemplo validado: "Saia da doca, pulverize o plot-02, informe a ultima
pulverizacao do plot-03 e volte." Um roteador **local** reconhece
`MISSION_PREVIEW`; parser e validador deterministico produzem um plano tipado.
No SM-X510/Gazebo, a execucao chegou a `UNDOCK -> SPRAY plot-02 -> consulta
plot-03 -> DOCK`, com confirmacao individual para cada acao fisica. A consulta
nao cria `Command`; se ela ou qualquer etapa falhar, o plano pausa e nao emite a
proxima acao. O resultado e simulacao Gazebo, nao aplicacao fisica comprovada.

Essa demonstracao e exatamente a separacao que queremos defender: Jev nao
cria historico, nao le QR, nao gera `MissionPlan` e nao move o robo. Essas
capacidades sao valor do Maestro. Jev continua uma hipotese mensuravel para a
seta de linguagem em um catalogo equivalente.

Fechar: "`EMERGENCY_STOP` fica fora de Jev e de reconhecimento de fala comum;
seguranca precisa de cadeia fisica independente do modelo."

**Evidencia de missao**: [E8].

## 45:00-50:00 - Debate

Projetar quatro perguntas e deixar a sala escolher a ordem:

1. Que funcao de recompensa e ablacoes seriam necessarias para avaliar RLCD?
2. Como montar holdout com ASR real sem expor transcricoes e medir falso aceite?
3. Que custo total importa: tokens cobrados, rede, p95, energia e custo do erro?
4. Que evidencia faria a equipe trocar `HOLD` por integracao experimental?

Resposta preparada para "por que nao um `if`?": "Se regras escritas a mao
resolvem as variacoes reais, elas sao preferiveis. O experimento mede se o
classificador probabilistico melhora a cobertura sem aumentar o risco.
Ainda nao demonstramos isso o suficiente para controle operacional."

## Claims que precisam permanecer exatos

### Pode dizer

- "No corpus sintetico independente medido, Jev teve resultado descritivo
  melhor que o baseline; ele nao foi adotado pelo Maestro."
- "A decisao e `HOLD` por causa do aceite inseguro, da latencia remota e da
  evidencia limitada."
- "Os casos externos mostram catalogos fechados em outros dominios e devem ser
  lidos junto de seus harnesses."
- "As imagens do app mostram uma fixture local de UI, nao uma execucao."
- "O modo Jev remoto tem consentimento de sessao e um gate local preventivo;
  isso reduz risco, mas nao prova anonimizacao nem conformidade LGPD integral."
- "A missao composta foi validada em `mockDebug` e Gazebo com confirmacao por
  etapa; nao e evidencia de aplicacao agricola fisica."

### Nao dizer

- "Jev e seguro, calibrado, melhor em geral ou ja esta em producao no Maestro."
- "Jev ganhou de Fable no xadrez" sem citar que a vitoria foi no tempo e sob
  aquele harness.
- "RLCD prova que o Jev e superior" ou que sua receita de treinamento e publica.
- "A p95 e o custo medidos representam Android, campo ou robo."
- "Jev controla ROS, resolve alvo, remove confirmacao, filtra o Qwen ou usa RAG."
- "Jev usa zero tokens de saida" ou "preco zero por saida significa chamada
  gratuita ou instantanea". Nosso registro tem 69 a 71 `output_tokens` por
  chamada.
- "Laya e melhor que Jev" ou que ele e uma alternativa Android sem benchmark.
- "O Maestro so le QR Code"; ha foto sob demanda, embora ela seja processada em
  memoria e nao persistida pelo app por padrao.
- "O classificador local detecta todo CPF"; o gate de padroes evidentes protege
  apenas o caminho remoto demonstrativo e nao e detector geral de dados pessoais.

## Fontes e evidencia para ensaio do roteiro

- **[S1]** [TypeSafe: introducao](https://docs.typesafe.ai/introduction)
- **[S2]** [TypeSafe: Choice](https://docs.typesafe.ai/primitives/choice)
- **[S3]** [TypeSafe: Confidence](https://docs.typesafe.ai/confidence)
- **[S4]** [TypeSafe: AI primer e RLCD](https://docs.typesafe.ai/introduction/machine-learning-primer)
- **[S5]** [Thread de xadrez republicada](https://threadnavigator.com/thread/2100372930282573876/)
- **[S6]** [Jev x HighwayEnv: 60 segundos sem colisao](https://dev.to/trknhr/jev-x-highwayenv-60-seconds-without-a-crash-30ig)
- **[S7]** [Demo Jev PR Judge](https://jevtypesafeai.com/tools/pr-judge)
- **[S8]** [Metafora "if com IA" no X](https://x.com/humbertocortezi/status/2101493117165666714?s=20)
- **[S9]** [JevPilot no X](https://x.com/jpschroeder/status/2100347770867458384?s=20)
- **[S10]** [Selecao de skills para Claude Code no X](https://x.com/dani_avila7/status/2101885477158547753?s=20)
- **[S11]** [Compaction por relevancia no X](https://x.com/tamarajtran/status/2100694549362553153?s=20)
- **[S12]** [Laya-MLX](https://github.com/mizorewww/laya-mlx)
- **[S13]** [TypeSafe: anuncio tecnico, fundador, amostragem e preco](https://typesafe.ai/blog/introducing-system-one-models-and-jev).
- **[S14]** [Post de Grajeda sobre Jev x LLM](https://x.com/k_grajeda/status/2099952715430596710?s=20); verificar o post original antes do ensaio.
- **[S15]** [Codigo de compaction de Tamara Tran](https://github.com/tamaratran/fast-jev-compaction).
- **[S16]** [Video de Stefan](https://x.com/heystefan_/status/2101369117496521042?s=20); detalhes pendentes de inspecao.
- **[S17]** [Post de Luiz sobre Jev/Laya](https://x.com/luizcarvalhocom/status/2102055194070593894?s=20); detalhes pendentes de inspecao.
- **[E1]** [Comparacao medida JEV-41R](results/jev-final-recovery-presentation.md)
- **[E1a]** [Fixture JEV-41R: uso de tokens por chamada](results/jev-final-recovery-fixture.json)
- **[E2]** [Visuais de comparacao, matriz e reliability JEV-51](../../tasks/jev-presentation-slides.md)
- **[E3]** [Decisao experimental `HOLD`](../../tasks/jev-experimental-decision.md)
- **[E4]** [Capturas do app JEV-50](../../tasks/jev-app-captures.md)
- **[E5]** [Demo de reserva offline JEV-52](../../tasks/jev-offline-reserve-demo.md)
- **[E6]** [Fluxo de privacidade](../../privacy-data-flow.md)
- **[E7]** [Gate remoto e evidencia JEV-69](../../tasks/jev-remote-privacy-gate.md)
- **[E8]** [Missao composta e validacao JEV-78](TASKS.md)
- **[E9]** [JEV-38: caminho remoto ate Gazebo](../../tasks/jev-local-proxy.md)

Todos os casos [S] sao de terceiros ou documentacao do fornecedor. Os itens
[E] sao artefatos versionados do experimento Maestro e carregam seus proprios
limites de interpretacao.
