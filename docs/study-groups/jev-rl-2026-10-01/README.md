# Jev e Decisoes com Incerteza

Grupo de estudos de RL

Data: 01/10/2026

Status: planejamento ativo. Este material pertence ao grupo de estudos e nao
ao pitch do Maestro Agricola. Nenhum deck e versionado nesta pasta ainda.

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

O termo RLCD e uma descricao da TypeSafe para o treino do Jev. A empresa nao
publicou arquitetura, dados ou receita de treino. A apresentacao usa o caso
para discutir calibracao, risco seletivo e avaliacao, sem tratar essas
alegacoes como resultado academico estabelecido.

## Estrutura da apresentacao

| Tempo | Assunto | Pergunta que o bloco responde |
| --- | --- | --- |
| 0:00-4:00 | Decisoes pequenas em software | Quando um `if` precisa de julgamento sem virar um agente? |
| 4:00-11:00 | Jev | O que `Choice`, `Noul` e `Score` retornam? |
| 11:00-19:00 | Calibracao e RL | Quando a probabilidade de 0,90 da classe escolhida corresponde a cerca de 90% de acertos? |
| 19:00-27:00 | Xadrez | O que Jev vs Fable vs Astra realmente mediu? |
| 27:00-34:00 | Casos publicos | Onde decisao rapida parece uma boa fronteira? |
| 34:00-41:00 | Maestro atual | Quais barreiras separam linguagem de movimento? |
| 41:00-47:00 | Jev no intent e no app | Como trocar somente o classificador e mostrar a decisao sem liberar acoes? |
| 47:00-50:00 | Roadmap e debate | Que novas classes exigiriam contrato e qual evidencia escolheria o caminho? |

O encerramento deve deixar quatro minutos para perguntas. Nao e uma defesa do
Jev como substituto automatico do classificador local.

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

As classes abaixo sao roadmap de produto e viram o bloco final da
apresentacao. Elas mostram onde uma `Choice` tipada pode ser util sem alegar
que ja estao implementadas.

Jev permite alterar a lista de opcoes de uma pergunta `Choice`. Isso acelera o
experimento de uma nova classe, mas nao cria um comando seguro por si so. Cada
opcao precisa de criterio que a diferencie das vizinhas, exemplos positivos e
negativos quando a fronteira for ambigua, e uma saida `UNKNOWN` que cumpra o
papel de `other` ou `none of the above`. Toda classe que produz efeito
observavel no robo precisa de contrato versionado, validacao de estado, testes
e aprovacao humana antes de entrar no catalogo operacional.

| Classe candidata | Efeito pretendido | Situacao para o estudo | Condicao para virar operacao |
| --- | --- | --- | --- |
| `STATUS_QUERY` | Ler e narrar estado atual do robo | Boa primeira classe; somente leitura | Criar interface de consulta que nao emite `Command` |
| `PLOT_STATUS_QUERY` | Informar a ultima missao `SPRAY` concluida para um talhao | Boa ideia de produto; ainda nao existe historico | Registrar resultado final, timestamp, plot e origem sem persistir midia |
| `INSPECT_TARGET` | Capturar sob demanda e reportar marcador/QR | Boa primeira classe; sem movimento | Manter imagem em memoria, permissao e politica de privacidade |
| `COMPOUND_MISSION` | Plano tipado, por exemplo `UNDOCK -> SPRAY(plot-02) -> PLOT_STATUS(plot-03) -> DOCK` | Roadmap; nao entra no benchmark inicial | Novo `MissionPlan` versionado, confirmacao explicita do plano, executor deterministico e pause em falha |
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

O repositorio atualmente nao possui um diff versionado de Jev na branch
`test/jev`. Ate que exista implementacao, corpus e resultado reproduzivel, a
apresentacao chama este trecho de proposta experimental.

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
em [`corpus/README.md`](corpus/README.md). O corpus final de seguranca sera
outro artefato, congelado antes da rodada remota final.

O `confidence` do Jev tambem pode orientar abstencao, pois indica se a
distribuicao esta concentrada ou dividida. No Maestro, mesmo alta probabilidade
ou alto `confidence` nunca removem a confirmacao por audio para uma acao fisica.

## Orcamento de creditos

O estudo tem US$5 de creditos. Antes de qualquer chamada remota, definir limite
no console e registrar cada rodada. A alocacao inicial e US$0,50 para smoke e
ajuste de criterios, ate US$3,00 para a rodada reproduzivel do corpus final,
ate US$1,00 para gravacao ou repeticao da demo e US$0,50 de reserva. Nenhuma
rodada deve continuar depois de atingir seu teto sem decisao humana.

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
