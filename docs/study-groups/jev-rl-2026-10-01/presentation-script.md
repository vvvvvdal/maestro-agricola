# Roteiro falavel: Jev e decisoes com incerteza

Duracao: **50 minutos**. Sao 46 minutos de conteudo e 4 minutos de debate.
Este roteiro e para um grupo de estudos de RL, nao um pitch e nem uma defesa de
adocao do Jev no Maestro Agricola.

## Tese e combinados com a audiencia

Tese: uma decisao tipada com probabilidades pode ser uma boa fronteira entre
linguagem e software deterministico. Ela nao e uma autorizacao para controle
fisico.

Antes de iniciar, distinguir tres tipos de afirmacao:

- **Medido no Maestro**: artefato versionado, com escopo e limite explicitados.
- **Resultado de terceiros**: caso publico em outro dominio; serve para leitura
  de benchmark, nao para provar o nosso produto.
- **Hipotese ou roadmap**: desenho de proxima etapa, ainda sem implementacao.

## Mapa de tempo

| Tempo | Bloco | Tipo dominante | Visual previsto |
| --- | --- | --- | --- |
| 0:00-3:00 | A pergunta | Hipotese de arquitetura | Diagrama de fronteira |
| 3:00-9:00 | O que o Jev retorna | Fonte oficial | `Choice`, `Noul`, `Score` |
| 9:00-16:00 | RLCD, probabilidade e calibracao | Fonte oficial + medido | reliability diagram JEV-51 |
| 16:00-21:00 | Xadrez: Fable e Astra | Terceiros | relogio e harness |
| 21:00-27:00 | Outros casos publicos | Terceiros | tabela de tres casos |
| 27:00-34:00 | Maestro: onde a decisao para | Produto e contrato atual | pipeline e anti-exemplo |
| 34:00-40:00 | Experimento Jev no Maestro | Medido | comparacao e matriz JEV-51 |
| 40:00-44:00 | App e demo de reserva | Fixture local | tres capturas JEV-50/JEV-52 |
| 44:00-46:00 | Roadmap de classes | Hipotese de produto | tabela de fronteiras |
| 46:00-50:00 | Debate | Perguntas abertas | tela de perguntas |

Total: **46 minutos de conteudo + 4 minutos de debate = 50 minutos**.

## 0:00-3:00 - A pergunta

**Fala-guia**: "Quero discutir um problema menor que um agente geral, mas maior
que um `if`: como transformar linguagem em uma decisao estruturada quando ha
ambiguidade? A pergunta nao e se um modelo pode dirigir um robo. No Maestro,
ele nao dirige. A pergunta e se um componente pode escolher uma classe de
linguagem melhor que o baseline, sem atravessar as barreiras que protegem o
movimento."

Desenhar a fronteira:

```text
fala -> decisao tipada -> regras e estado deterministico -> confirmacao -> robo
```

Transicao: "O Jev entra somente no segundo termo dessa linha. Entao vamos ver
o que ele devolve e o que ele nao promete."

## 3:00-9:00 - O que o Jev retorna

Apresentar `Choice` como uma pergunta de catalogo fechado: por exemplo,
`SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`. A resposta contem
uma opcao vencedora e probabilidades para as opcoes. `Noul` responde uma
pergunta booleana; `Score` produz um escore. Para o Maestro, a primitiva
relevante e `Choice`.

**Ponto central sobre tokens**: um `Choice` nao escreve uma resposta em texto
token a token. A resposta e uma decisao fechada, com `choice`, distribuicao e
confianca; no contrato da API, o campo observado e `output_tokens: 0`. Isso
nao significa custo ou latencia zero: ainda ha estado de entrada, chamada
remota e cobranca associada. A diferenca e que a saida nao cresce como uma
resposta generativa longa de LLM.

Fala curta: "Em vez de pedir um paragrafo e depois tentar interpreta-lo, damos
seis alternativas permitidas e recebemos uma escolha. Nao ha texto de saida
para ser gerado, parseado ou usado como comando."

Explicar uma distincao importante: a probabilidade da classe escolhida e o
valor preservado em `IntentPrediction.confidence`. O campo `confidence` do Jev
descreve concentracao da distribuicao; nao deve ser apresentado como se fosse a
probabilidade da classe vencedora. `Noul` nao retorna esse campo.

**Pergunta para a sala**: "Que decisao discreta, frequente e ambigua voces ja
viram que nao deveria virar um agente com ferramentas livres?"

**Fonte**: [S1]-[S3].

## 9:00-16:00 - RLCD, probabilidade e calibracao

**Fala-guia**: "A TypeSafe descreve o treinamento como RLCD. Podemos usar isso
como motivacao da ferramenta, mas nao como receita academica auditavel: a
empresa nao publicou arquitetura, dados ou detalhes suficientes para que a
gente valide esse treinamento."

Separar duas perguntas: o classificador acerta mais neste corpus? E, quando
ele diz 0,90, acerta aproximadamente 90% em exemplos parecidos?

Mostrar o reliability diagram de JEV-51. Brier mede qualidade das
probabilidades; top-label ECE compara confianca e frequencia de acerto por
faixas; a diagonal representa calibracao ideal. Ler a ressalva: sao 60 falas
sinteticas, uma rodada remota e sem replicacao. O grafico descreve a rodada;
nao prova calibracao no campo.

**Pergunta para a sala**: "Que holdout e que estratos de seguranca seriam
necessarios para essa figura sustentar uma decisao operacional? ASR ruidoso,
negacao, hesitacao e conflito de alvo seriam obrigatorios?"

**Fonte**: [S4] para RLCD; evidencia medida em [E1] e [E2].

## 16:00-21:00 - Xadrez: Fable e Astra

**Fala-guia**: "Este e o caso chamativo, mas e principalmente uma licao de
leitura de benchmark. Em uma partida blitz 5+0, com uma chamada de API por
lance e sem busca, Jev venceu Fable 5.1 no tempo. Fable tinha +16 de material e
uma segunda dama no lance 29. Entao nao vou chamar isso de Jev mais forte em
xadrez: naquele harness, ele decidiu mais rapido."

"Contra Astra, houve mate em 18 lances, com Astra ainda tendo 2:27. Calculo e
busca sao partes centrais de xadrez; essa fronteira favoreceu um modelo de
raciocinio naquela partida. O relogio, a politica de uma chamada e a ausencia
de busca definem a conclusao."

**Fonte**: [S5], resultado de terceiros.

## 21:00-27:00 - Direcao em simulador e triagem de PR

Usar dois casos com limites claros. Cada linha e resultado de terceiros em
dominio diferente.

| Caso | O que ilustra | O que nao permite concluir |
| --- | --- | --- |
| Direcao no HighwayEnv | Um estado fechado pode alimentar uma escolha entre acoes permitidas; o autor reporta 60 segundos sem colisao. | Que Jev foi validado em carro real, com camera real, ou que a comparacao contra Codex e um benchmark controlado. |
| Triagem de PR | Um diff limitado pode virar `SAFE / REVIEW / BLOCK`, risco e checks, sem gerar uma longa resenha. | Que a ferramenta le o repositorio inteiro, executa testes, substitui revisao humana ou economiza uma quantidade geral de tokens. |

**Fala-guia**: "No simulador, o estado e as acoes ja sao fechados. Na triagem
de PR, o artefato de entrada e limitado e a saida pode ser uma decisao curta.
Esse segundo caso e interessante porque evita gerar uma resenha longa quando o
primeiro passo e so encaminhar o PR. A pagina da demo anuncia cerca de 300 ms
e US$0,00003 por chamada; trate isso como alegacao da demo, nao como comparacao
de tokens ou benchmark independente. Ela mesma diz que nao le o repo inteiro
nem roda testes."

**Fontes**: [S6]-[S7], resultados de terceiros.

## 27:00-34:00 - Maestro: onde a decisao para

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

**Fala-guia**: "O Jev, se usado, troca somente uma implementacao de
classificador para os mesmos seis rotulos. Cada execucao usa o local ou o Jev;
eles nao votam sobre a mesma fala. Ele nao recebe foto, audio, `Command`,
WebSocket, ROS, estado do robo nem resolucao de alvo."

Usar o anti-exemplo obrigatorio: a camera identifica `plot-03`, a fala pede
pulverizar `plot-01` e o classificador acerta `SPRAY`. Mesmo assim, o resultado
e `AMBIGUOUS`, sem `Command`, porque o alvo esta em conflito.

`UNKNOWN` segue inalterado para `LanguageRouter -> QwenDomainAssistant -> CHAT
| OUT_OF_SCOPE`. Nao ha filtro Jev para o Qwen nem RAG neste experimento.

## 34:00-40:00 - Experimento Jev no Maestro

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

Fechar: "Jev pode substituir localmente apenas o classificador dos seis intents
para ser medido. Ainda nao faz sentido promove-lo ao APK."

**Evidencia medida**: [E1]-[E3].

## 40:00-44:00 - App e demo de reserva

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

## 44:00-46:00 - Roadmap de classes

Apresentar como mapa de fronteiras, nao como backlog entregue.

| Classe | Por que pode fazer sentido | O que falta antes de operar |
| --- | --- | --- |
| `STATUS_QUERY` | Consulta somente leitura do estado do robo. | Interface de consulta sem `Command`. |
| `PLOT_STATUS_QUERY` | Responder ultima missao simulada de pulverizacao de um talhao. | Historico efemero de resultado Nav2, timestamp, talhao e origem; nao comprova aplicacao fisica. |
| `INSPECT_TARGET` | Reutiliza captura sob demanda para reportar QR/marcador. | Privacidade, permissao e imagem somente em memoria. |
| `COMPOUND_MISSION` | Transforma fala longa em `MissionPlan` tipado. | Plano confirmado, executor deterministico e pausa/falha segura. |
| `PAUSE`, `RESUME`, `SCOUT` | Ideias futuras com fronteiras mais sensiveis. | Contrato, estado, revalidacao e E2E proprio. |

Exemplo: "Saia da doca, pulverize o plot-02, informe a ultima pulverizacao do
plot-03 e volte." Jev poderia reconhecer `COMPOUND_MISSION` e extrair um plano
tipado. Ele nao escolhe movimentos: o plano precisa ser mostrado, confirmado e
executado de forma deterministica.

Fechar: "`EMERGENCY_STOP` fica fora de Jev e de reconhecimento de fala comum;
seguranca precisa de cadeia fisica independente do modelo."

## 46:00-50:00 - Debate

Projetar quatro perguntas e deixar a sala escolher a ordem:

1. Qual falso aceite e inaceitavel nesse dominio, mesmo se a accuracy subir?
2. Como montar um holdout com ASR real sem expor transcricoes?
3. Entre `STATUS_QUERY` e `INSPECT_TARGET`, qual classe somente leitura vale
   validar primeiro?
4. Que evidencia faria a equipe trocar `HOLD` por uma integracao experimental
   no Android?

## Claims que precisam permanecer exatos

### Pode dizer

- "No corpus sintetico independente medido, Jev teve resultado descritivo
  melhor que o baseline; ele nao foi adotado pelo Maestro."
- "A decisao e `HOLD` por causa do aceite inseguro, da latencia remota e da
  evidencia limitada."
- "Os casos externos mostram catalogos fechados em outros dominios e devem ser
  lidos junto de seus harnesses."
- "As imagens do app mostram uma fixture local de UI, nao uma execucao."

### Nao dizer

- "Jev e seguro, calibrado, melhor em geral ou ja esta em producao no Maestro."
- "Jev ganhou de Fable no xadrez" sem citar que a vitoria foi no tempo e sob
  aquele harness.
- "RLCD prova que o Jev e superior" ou que sua receita de treinamento e publica.
- "A p95 e o custo medidos representam Android, campo ou robo."
- "Jev controla ROS, resolve alvo, remove confirmacao, filtra o Qwen ou usa RAG."
- "`output_tokens: 0` significa que uma chamada Jev e gratuita ou instantanea."

## Fontes e evidencia para a numeracao dos slides

- **[S1]** [TypeSafe: introducao](https://docs.typesafe.ai/introduction)
- **[S2]** [TypeSafe: Choice](https://docs.typesafe.ai/primitives/choice)
- **[S3]** [TypeSafe: Confidence](https://docs.typesafe.ai/confidence)
- **[S4]** [TypeSafe: AI primer e RLCD](https://docs.typesafe.ai/introduction/machine-learning-primer)
- **[S5]** [Thread de xadrez republicada](https://threadnavigator.com/thread/2100372930282573876/)
- **[S6]** [Jev x HighwayEnv: 60 segundos sem colisao](https://dev.to/trknhr/jev-x-highwayenv-60-seconds-without-a-crash-30ig)
- **[S7]** [Demo Jev PR Judge](https://jevtypesafeai.com/tools/pr-judge)
- **[E1]** [Comparacao medida JEV-41R](results/jev-final-recovery-presentation.md)
- **[E2]** [Visuais de comparacao, matriz e reliability JEV-51](../../tasks/jev-presentation-slides.md)
- **[E3]** [Decisao experimental `HOLD`](../../tasks/jev-experimental-decision.md)
- **[E4]** [Capturas do app JEV-50](../../tasks/jev-app-captures.md)
- **[E5]** [Demo de reserva offline JEV-52](../../tasks/jev-offline-reserve-demo.md)

Todos os casos [S] sao de terceiros ou documentacao do fornecedor. Os itens
[E] sao artefatos versionados do experimento Maestro e carregam seus proprios
limites de interpretacao.
