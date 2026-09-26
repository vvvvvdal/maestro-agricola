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
| 0:00-4:00 | A pergunta e a metafora do `if` | Hipotese + terceiro | fronteira e decisao probabilistica |
| 4:00-10:00 | Jev, LLM e contrato | Fonte oficial | `Choice`, `Noul`, `Score`, `output_tokens: 0` |
| 10:00-19:00 | RL, RLHF, RLVR, RLCD e calibracao | Fonte oficial + medido | taxonomia e reliability diagram JEV-51 |
| 19:00-24:00 | Xadrez: Fable e Astra | Terceiros | relogio e harness |
| 24:00-29:00 | Casos externos e Laya | Terceiros + fonte primaria | simulador, PR, skills, compaction, contraponto local |
| 29:00-35:00 | Maestro: fronteira e privacidade | Produto e contrato atual | pipeline, anti-exemplo e minimizacao |
| 35:00-40:00 | Experimento Jev no Maestro | Medido | comparacao e matriz JEV-51 |
| 40:00-44:00 | App e demo de reserva | Fixture local | tres capturas JEV-50/JEV-52 |
| 44:00-46:00 | Missao entregue no simulador | E2E mockDebug + Gazebo | plano tipado e confirmacao por etapa |
| 46:00-50:00 | Debate | Perguntas abertas | tela de perguntas |

Total: **46 minutos de conteudo + 4 minutos de debate = 50 minutos**.

## 0:00-2:30 - A pergunta

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

## 2:30-4:00 - A metafora do `if`

Depois da fronteira, usar a frase publica "Jev e um `if` com IA" apenas como
intuicao. Um `if` classico e uma regra deterministica escrita pela equipe; uma
decisao Jev devolve uma distribuicao sobre alternativas de catalogo fechado.
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

**Ponto central sobre tokens**: um `Choice` nao escreve uma resposta em texto
token a token. A resposta e uma decisao fechada, com `choice`, distribuicao e
confianca; no contrato da API, o campo observado e `output_tokens: 0`. Isso
nao significa custo ou latencia zero: ainda ha estado de entrada, chamada
remota e cobranca associada. A diferenca e que a saida nao cresce como uma
resposta generativa longa de LLM.

Fala curta: "Em vez de pedir um paragrafo e depois tentar interpreta-lo, damos
seis alternativas permitidas e recebemos uma escolha. Nao ha texto de saida
para ser gerado, parseado ou usado como comando."

Comparar sem hierarquia: LLM generativo produz texto aberto, normalmente token
a token. E o contrato adequado para conversa, explicacao e escrita, mas exige
schema e validacao antes de entrar em um fluxo operacional. `Choice` faz uma
selecao em catalogo fechado. A pergunta nao e qual e "mais inteligente"; e
qual contrato torna a proxima decisao mais auditavel. No Maestro, Qwen continua
no caminho `UNKNOWN` de conversa e nao recebe ferramentas; Jev so e avaliado
como substituto do roteador de seis intents.

Explicar uma distincao importante: a probabilidade da classe escolhida e o
valor preservado em `IntentPrediction.confidence`. O campo `confidence` do Jev
descreve concentracao da distribuicao; nao deve ser apresentado como se fosse a
probabilidade da classe vencedora. `Noul` nao retorna esse campo.

**Pergunta para a sala**: "Que decisao discreta, frequente e ambigua voces ja
viram que nao deveria virar um agente com ferramentas livres?"

**Fonte**: [S1]-[S3].

## 10:00-19:00 - RL, RLHF, RLVR, RLCD e calibracao

Antes de RLCD, situar os nomes sem forcar equivalencia:

- **RL**: aprender uma politica a partir de retorno/recompensa de um ambiente.
- **RLHF**: usar preferencias ou feedback humano como sinal de treino.
- **RLVR**: usar um verificador objetivo como sinal de treino para tarefas que
  o admitem.
- **RLCD**: nome que a TypeSafe usa para o objetivo de decisoes calibradas; nao
  e receita publica o bastante para auditoria nem uma taxonomia academica
  universal.

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

## 19:00-24:00 - Xadrez: Fable e Astra

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

## 24:00-29:00 - Direcao, PR, selecao de skills, compaction e Laya

Usar casos com limites claros. Cada linha e resultado de terceiros em
dominio diferente.

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

**Fala sobre Laya**: "Laya-MLX e o contraponto interessante: pesos abertos e
runtime local para Apple Silicon. O repositorio reporta latencias locais em M3
Max, mas isso nao o torna 'melhor' que Jev nem candidato Android sem medicao.
Ele muda custo, privacidade, operacao e hardware. A comparacao correta comeca
pela fronteira, nao pelo slogan."

**Fontes**: [S6]-[S12], resultados de terceiros; [S12] e fonte primaria do
projeto Laya.

## 29:00-35:00 - Maestro: onde a decisao para e como os dados sao minimizados

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

### Privacidade: o que realmente acontece

Nao dizer que o app "so le QR Code". No caminho de camera, ele solicita uma
foto sob demanda, processa o QR/marcador localmente em memoria e reduz o frame
a `target_id`; o Maestro nao preve gravar imagem, audio ou transcricao por
padrao. A validacao de camera nos oculos Meta reais continua pendente.

No caminho padrao, a transcricao curta fica na memoria da atividade e entra no
classificador local. No modo remoto de demonstracao, restrito a `mockDebug`, o
operador da consentimento de sessao e app/proxy bloqueiam antes da rede alguns
padroes evidentes: e-mail, telefone, CPF/CNPJ, URL, texto longo ou fora do
escopo. A fala bloqueada e descartada localmente, sem Jev, Qwen ou `Command`.

Isso e **minimizacao preventiva**, nao anonimizacao, detector perfeito de dado
pessoal, auditoria juridica ou declaracao de conformidade LGPD integral. Essa
honestidade e parte da demonstracao: privacidade e uma fronteira de sistema,
nao um aviso decorativo.

## 35:00-40:00 - Experimento Jev no Maestro

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

## 44:00-46:00 - Missao composta entregue: Maestro, nao Jev

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
- "`output_tokens: 0` significa que uma chamada Jev e gratuita ou instantanea."
- "Laya e melhor que Jev" ou que ele e uma alternativa Android sem benchmark.
- "O Maestro so le QR Code"; ha foto sob demanda, embora ela seja processada em
  memoria e nao persistida pelo app por padrao.

## Fontes e evidencia para a numeracao dos slides

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
- **[E1]** [Comparacao medida JEV-41R](results/jev-final-recovery-presentation.md)
- **[E2]** [Visuais de comparacao, matriz e reliability JEV-51](../../tasks/jev-presentation-slides.md)
- **[E3]** [Decisao experimental `HOLD`](../../tasks/jev-experimental-decision.md)
- **[E4]** [Capturas do app JEV-50](../../tasks/jev-app-captures.md)
- **[E5]** [Demo de reserva offline JEV-52](../../tasks/jev-offline-reserve-demo.md)
- **[E6]** [Fluxo de privacidade](../../privacy-data-flow.md)
- **[E7]** [Gate remoto e evidencia JEV-69](../../tasks/jev-remote-privacy-gate.md)
- **[E8]** [Missao composta e validacao JEV-78](TASKS.md)

Todos os casos [S] sao de terceiros ou documentacao do fornecedor. Os itens
[E] sao artefatos versionados do experimento Maestro e carregam seus proprios
limites de interpretacao.
