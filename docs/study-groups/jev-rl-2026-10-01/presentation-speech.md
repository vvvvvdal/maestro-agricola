# Texto integral para falar — Jev, Reinforcement Learning e decisões calibradas em um sistema robótico

Base: [roteiro canônico](presentation-script.md). Esta é a versão integral de estudo, estimada originalmente em **58 minutos de apresentação e 5 de discussão**; a contagem de cerca de 8,5 mil palavras indica que sua leitura literal pode passar desse tempo. Para apresentar em 50 minutos, use o [percurso de 45 + 5](slide-study-guide.md). As frases abaixo são uma proposta de fala, não evidência adicional. Os trechos entre **[colchetes]** são ações ou escolhas do apresentador e **não são lidos**.

Antes de começar, deixar o Playground autenticado e o exemplo sem dados pessoais preparado. Preparar os três vídeos de terceiros e a gravação do Maestro em arquivos locais ou abas abertas. Se algum vídeo não funcionar, o slide contém a leitura técnica do caso. Não projetar credenciais nem dashboard de cobrança.

## O mínimo para estudar antes do ensaio

1. **Modelo** é a função treinada. **Harness** é o programa ao redor dela: monta entradas, chama ou simula o modelo, valida saídas e mede resultados. Nosso harness de avaliação compara o classificador local com respostas Jev já salvas numa fixture. Ele não treina Jev.
2. **RL** ajusta uma política usando recompensa. **RLHF** usa preferência humana como sinal. **RLVR** usa um verificador da tarefa. **RLCD** é o nome que a TypeSafe dá ao seu objetivo de decisões calibradas; não conhecemos detalhes suficientes para reproduzir o treino de Jev.
3. **Accuracy** é proporção de escolhas certas. **Calibração** confere se probabilidades declaradas correspondem a frequências de acerto em grupos. **Falso aceite** é uma fala de `CANCEL` ou `UNKNOWN` virar ação ou confirmação; no Maestro, é o erro que mais exige atenção.
4. **Jev no Maestro:** o Android manda transcrição curta ao proxy; o proxy constrói o JSON com `Choice`; Jev responde com seis probabilidades; o Android valida e só depois regras, estado e confirmação podem liberar comando.
5. **Laya** mostra que a interface de decisões tipadas pode existir com pesos abertos e execução local. Não temos uma comparação Laya × Jev no corpus do Maestro.

Leia os blocos acima antes de decorar números. No ensaio, explique cada sigla em uma frase antes de usá-la.

## 0:00–5:00 — Definição, System One e o problema concreto

[Slide 1.] “Hoje eu quero estudar uma ferramenta para tomar decisões pequenas dentro de software e depois mostrar o que aconteceu quando a testamos em um sistema robótico.”

[Slide 2.] “Jev é um modelo da TypeSafe que recebe um estado e uma ou mais perguntas com formatos de resposta definidos. Em vez de pedir um texto aberto, eu digo o que quero decidir. Posso pedir uma escolha entre opções, a probabilidade de um sim, ou uma nota em níveis ordenados. Jev devolve esses valores, e o meu programa decide o que fazer com eles. A palavra ‘tipada’ descreve a forma da resposta; não garante que a decisão esteja certa.”

[Slide 3.] “A TypeSafe chama essa família de System One. O nome remete à ideia de pensamento rápido de Kahneman, mas não é uma afirmação de que o modelo reproduz a mente humana. Jev é o primeiro modelo público dessa família. Diogo Almeida, fundador da empresa, trabalhou na OpenAI. A origem é interessante para um grupo de RL, mas a qualidade do Jev precisa ser medida no problema em que queremos usá-lo.”

[Slide 4.] “Agora imaginem um bot de WhatsApp que conversa como uma pessoa. Alguém escreve: ‘Minha cobrança veio duplicada. Consegue resolver?’. Além de responder educadamente, o bot precisa encaminhar o caso. As opções são técnico, financeiro, comercial ou atendimento humano. Um `Choice` pode avaliar a mensagem contra esse catálogo. A aplicação ainda decide se encaminha automaticamente ou se pede revisão.”

[Slide 5.] “É daí que vem a brincadeira de chamar Jev de um `if` com IA. Se eu tenho uma idade numérica confiável, `if (idade >= 18)` é a solução correta. Se recebo uma frase como ‘faço dezoito mês que vem’, preciso interpretar linguagem: um `Noul` pode estimar a probabilidade de a frase afirmar maioridade. O exemplo mostra a diferença entre regra e interpretação; eu não usaria essa inferência como verificação legal de idade.”

[Slide 6.] “O contrato é o centro da ferramenta: `state` contém o material a analisar, `model` fixa a versão e `questions` descreve as decisões. A resposta volta em `answers`. O modelo não manda uma pessoa para uma fila nem move um robô. Código valida a saída e executa uma regra.”

## 5:00–11:00 — Jev, LLM, primitivas e tokens

“Um LLM generativo é extremamente flexível. Ele pode conversar, escrever código, resumir, explicar e produzir texto aberto. Essa flexibilidade é ótima quando eu realmente preciso de uma resposta em linguagem. Para um passo interno de um programa, porém, a resposta aberta costuma exigir parsing e validação. Às vezes usamos JSON mode ou schema, o que ajuda muito, mas ainda precisamos pensar na tarefa, nos erros e na política depois da resposta.

[Slides 7–9: três formatos de saída.] “`Choice` serve quando uma resposta precisa ser escolhida de um catálogo fechado. No bot, as equipes são as opções. A resposta tem a opção escolhida, uma probabilidade para cada opção e `confidence`, que resume a concentração da distribuição. Vale oferecer uma opção de revisão ou ‘nenhuma’ quando as categorias positivas não cobrem todos os casos.

`Noul` serve para uma proposição binária. ‘A pessoa está pedindo atendimento humano?’ pode voltar como 0,84: isso significa probabilidade de ‘sim’ segundo o modelo, não grau de urgência. Não há `confidence` separado. O código decide se 0,84 basta para agir, e pode mandar a faixa intermediária para revisão.

`Score` serve para níveis com ordem. Posso descrever gravidade de bug como cosmético, recurso afetado ou bloqueante. O resultado `score` pode cair entre níveis, e a resposta inclui probabilidades por nível e `confidence`. Esse número mede posição na escala que eu descrevi; não é uma probabilidade de ‘sim’. As três perguntas podem ser feitas sobre o mesmo `state`, mas cada uma precisa de critério claro.”

Jev propõe uma interface mais estreita. A primitiva que mais nos interessa hoje se chama `Choice`. Eu forneço uma pergunta e um catálogo: técnico, financeiro, comercial, revisão humana. Jev retorna a opção escolhida e a probabilidade atribuída a cada opção. Um bom catálogo inclui uma saída para ‘nenhuma das anteriores’ ou revisão, porque o mundo real nem sempre cabe nas categorias positivas.

Existem outras duas primitivas que vale conhecer. `Noul` responde uma pergunta binária, como ‘essa mensagem expressa urgência?’. `Score` situa algo numa escala ordenada, como a intensidade de frustração. A documentação permite fazer várias perguntas sobre o mesmo estado numa chamada. Elas são avaliadas em paralelo segundo a TypeSafe. Isso pode ser útil, mas cada pergunta e cada critério também entram no payload e aumentam o tamanho da entrada.

Aqui está um dos pontos que mais me chamaram atenção: tokens de saída. Um LLM generativo normalmente produz uma sequência de tokens de texto. Se eu peço três parágrafos, há três parágrafos a gerar. Jev não escreve uma resposta aberta dessa forma. Ele entrega valores estruturados. A TypeSafe diz que amostra as decisões em paralelo e anuncia preço zero para tokens de saída. Isso pode baratear uma decisão curta e repetida.

Mas preciso separar três coisas: gerar prosa, contabilizar tokens de saída e cobrar por esses tokens. A documentação da própria TypeSafe mostra uma resposta `Choice` com 34 `output_tokens`. Portanto, não vou dizer que Jev consome zero tokens de saída. A afirmação comercial é que a **cobrança** dos tokens de saída é zero. O serviço ainda recebe tokens de entrada, usa rede e tem custo por chamada. Mais tarde vou mostrar o que apareceu no nosso experimento.

Também não quero repetir números de marketing como se fossem uma constante da natureza. Existem demonstrações que falam de centenas de vezes menos custo ou latência. A própria TypeSafe avisa que os ganhos publicados nos workflows dela provavelmente estão na ponta alta dos ganhos reais. Uma comparação justa teria a mesma tarefa, entrada equivalente, qualidade da decisão, custo total e latência ponta a ponta. Comparar uma frase curta com um LLM escrevendo uma dissertação responderia a outra pergunta.

[Na tabela do slide 12, percorrer as linhas de cima para baixo.] “Um LLM aceita tarefas abertas e gera texto, código ou JSON. Jev recebe perguntas tipadas e devolve decisões sobre opções que nós definimos. JSON mode aproxima o formato de um LLM de um contrato, então a diferença interessante não é dizer que LLM não consegue devolver JSON. É comparar a qualidade, a latência e o custo de uma mesma decisão. Nos dois casos, a aplicação valida a resposta e decide a consequência.”

Mais uma distinção técnica antes do exemplo. Em `Choice`, a resposta traz um mapa chamado `probabilities`. Ele diz a probabilidade de cada alternativa. Há também um campo chamado `confidence`, calculado a partir de quão concentrada está a distribuição. Se uma opção tem quase toda a massa, a distribuição é concentrada. Se a massa está espalhada, ela é difusa. A probabilidade da opção vencedora e o campo `confidence` podem ser diferentes; vou apontar os dois se aparecerem no site. Para `Noul`, o contrato não retorna esse mesmo campo.

A pergunta de design que fica é: em que decisões discretas, frequentes e ambíguas vocês hoje fazem uma chamada generativa inteira, embora o código só precise de uma pequena bifurcação? Vamos montar uma dessas decisões no Playground.”

[Slide 13.] “Antes de abrir o console, esta é a fonte que vou usar: a documentação oficial de `Choice`. Ela define uma opção de um conjunto fechado e mostra os campos `state`, `model`, `questions`, `criteria`, `choice`, `probabilities` e `confidence`. O quick start da TypeSafe usa um chamado de suporte muito parecido com o nosso. Vou mostrar a página, não um print de uma resposta da minha conta, e depois construir um caso sintético no Playground.”

## 11:00–15:00 — Exemplo no Playground da TypeSafe

[Abrir o Playground já autenticado. Colar **apenas** a frase abaixo no campo `state`.]

“Vou criar uma pergunta do zero e deixar visível cada peça do contrato. O estado será uma mensagem sintética, sem informação pessoal: ‘A integração de pagamento falhou e a fatura foi cobrada duas vezes.’ Esse é o dado que o modelo vai avaliar. Não é a instrução sobre o que fazer com ele.

[Criar pergunta com ID `departamento`, tipo `Choice`. Inserir a instrução ‘Qual equipe deve receber este chamado?’. Adicionar os critérios técnico = falha de integração, bug ou configuração; financeiro = cobrança, pagamento ou fatura; comercial = plano, preço ou contratação; revisão humana = informação insuficiente ou várias equipes igualmente plausíveis.]

“Agora estou definindo a pergunta. Chamei de `departamento`. Escolhi `Choice`, porque preciso selecionar uma opção de um conjunto finito. A instrução é ‘Qual equipe deve receber este chamado?’. Por fim, descrevo o que cada opção significa. Essa descrição importa: nomes de categorias sem fronteiras claras produzem perguntas ruins. A opção de revisão humana evita forçar tudo para uma equipe operacional.

Antes de executar: qual equipe vocês escolheriam? Eu espero que financeiro seja uma hipótese forte por causa da cobrança duplicada. A falha de integração pode puxar parte da probabilidade para técnico. Não vou prometer um resultado fixo, porque o que vale é a resposta que aparecer agora.”

[Executar. Apontar o resultado real. Ler `choice`, duas probabilidades relevantes, `confidence` se exibido, e `usage` se exibido. Não inventar números ausentes.]

“O resultado que apareceu foi **[ler categoria exibida]**. Para essa opção, o modelo atribuiu **[ler probabilidade exibida]**. Também vemos **[ler outra alternativa e probabilidade, se disponível]**. O campo `confidence`, quando está aqui, resume a concentração da distribuição; não é automaticamente a probabilidade da opção escolhida.

Agora vem o passo mais importante: o modelo não encaminhou o chamado. Ele devolveu dados. Eu ainda escreveria uma regra como ‘se a probabilidade da equipe vencedora for suficiente e o risco for baixo, encaminhar; caso contrário, pedir revisão’. Qual limiar usar é uma decisão de produto que precisa ser medida. E uma integração real validaria a resposta, trataria timeout e registraria qual versão do modelo respondeu.

Se eu quisesse fazer a mesma coisa em código, o corpo da requisição teria três partes: `state`, `model` e `questions`. Dentro de `questions` estaria `departamento`, com `type: choice`, `instructions` e `criteria`. A API expõe `POST /v1/systemone`; o SDK tem uma chamada equivalente, `client.system_one(...)`. Eu leria `answers["departamento"].choice` e as probabilidades, e aplicaria minha política no programa. Para uma demonstração, `jev-latest` é conveniente; num experimento reprodutível, eu fixaria e registraria a versão.

Se houvesse mais tempo, eu perguntaria no mesmo estado se há urgência usando `Noul`, e pontuaria frustração com `Score`. O importante é que são perguntas diferentes, cada uma com saída definida antes de executar. Agora que vimos a interface por fora, vamos ao motivo de essa ferramenta aparecer numa conversa sobre reinforcement learning.”

**Se o site não carregar, substituir apenas a execução por esta fala:** “O Playground não respondeu agora. Vou usar o request e a resposta de exemplo publicados no quick start da TypeSafe para mostrar os mesmos campos. Isso demonstra o contrato da API, não uma inferência feita ao vivo.”

## 15:00–29:00 — RL, RLHF, RLVR, RLCD e calibração

### 15:00–18:00 — RL básico

> **Para estudar antes de apresentar:** RL é treinamento por tentativa e consequência. O agente observa o estado, escolhe uma ação e recebe recompensa. A **política** é a regra aprendida que liga estados a ações; não é uma regra escrita à mão. **Retorno** é a soma das recompensas futuras que o treino tenta aumentar. Um jogo simples basta para explicar isso. Não precisa dominar as equações de Bellman para este trecho. Se alguém perguntar, `π(a|s)` lê-se “probabilidade de escolher ação `a` quando o estado é `s`”.

“Antes de falar de RLCD, vale colocar os nomes na mesma mesa sem fingir que são a mesma técnica. No exemplo clássico de reinforcement learning, um agente observa um estado, escolhe uma ação segundo uma política, recebe uma recompensa e encontra um novo estado. Escrevemos isso como estado `s`, ação `a`, recompensa `r`, próximo estado `s'`. A política, que posso escrever como pi de a dado s, é o que o treinamento ajusta para aumentar o retorno esperado.

Vou usar o mesmo esquema visual nos quatro slides: o que entra, de onde vem o sinal de qualidade, o que se ajusta, qual saída queremos e o que esse nome sozinho ainda não prova. Em RL básico, entra o estado, o ambiente devolve recompensa, a política muda e esperamos ações que aumentem o retorno. Isso organiza a comparação sem fingir que as siglas especificam todo o algoritmo.

Imaginem um jogo simples. Em cada posição, o agente escolhe mover para a esquerda ou para a direita. A recompensa pode vir só ao alcançar o objetivo ou ao evitar uma colisão. O agente não recebe uma lista de frases bonitas para escrever; ele recebe um sinal que favorece certos comportamentos ao longo do tempo. O que exatamente é recompensado muda o que a política aprende.

Esse último ponto é a ponte para o restante. ‘Usa RL’ ainda diz pouco. Preciso perguntar: qual é a saída? De onde vem o sinal de qualidade? Ele mede preferência humana, resposta verificável ou qualidade da incerteza? Como o sinal é obtido? E como sabemos que a melhoria veio do treino, e não de uma mudança de arquitetura, do sampler ou da forma de perguntar?

Vou passar por três nomes que aparecem nesta discussão: RLHF, RLVR e RLCD. Não são etapas obrigatórias de um mesmo treinamento. Eles destacam objetivos de treino diferentes.”

### 18:00–22:00 — RLHF e RLVR

> **Para estudar RLHF:** pessoas comparam respostas; o treino favorece as preferidas. Em uma variante clássica, um modelo de recompensa aprende dessas comparações. O ponto que você precisa reter: “preferida” e “probabilidade bem estimada” são critérios diferentes.
>
> **Para estudar RLVR:** um verificador confere se a resposta passou num teste objetivo, como uma conta ou um teste de código. Esse resultado vira o sinal para melhorar a política. O verificador precisa existir; muitas decisões do mundo real não têm um gabarito automático.

“RLHF quer dizer reinforcement learning from human feedback. No roteiro clássico, pessoas comparam respostas ou indicam preferências. Essas comparações alimentam um modelo de recompensa, ou algum sinal equivalente, e a política é ajustada para favorecer respostas que esse sinal avalia melhor. Existem variantes; não estou dizendo que todo sistema chamado RLHF implementa o mesmo algoritmo.

Seguindo o esquema: entram respostas para uma tarefa; o sinal vem de comparações humanas; a política é ajustada para produzir respostas preferidas; e a limitação é que preferência não prova calibração. É o mesmo ciclo de ajuste, com outra fonte de qualidade.

No slide, ChatGPT, Claude, Grok e DeepSeek são exemplos de produtos de conversa, não uma afirmação de que usam a mesma receita exata de RLHF. Por que isso foi tão importante para modelos de conversa? Porque uma resposta pode ser tecnicamente possível e ainda ser pouco útil para quem perguntou. Preferências humanas ajudam a selecionar o tipo de resposta que as pessoas querem receber. Só que existe uma distinção crucial para hoje: uma resposta preferida não é necessariamente uma estimativa de probabilidade bem calibrada. Se peço a um modelo uma decisão e ele diz ‘tenho 90% de certeza’, posso gostar da explicação, mas ainda preciso medir se esse 90% se comporta como 90% em muitos casos.

No slide, o1 e o3 ilustram a família de modelos de raciocínio; não afirmo que suas receitas de treino sejam idênticas. RLVR significa reinforcement learning with verifiable rewards. Aqui temos tarefas nas quais parte da qualidade pode ser checada por um verificador relativamente objetivo: um resultado matemático, um teste de código, uma condição formal. A recompensa pode vir dessa checagem, sem precisar perguntar a uma pessoa se gostou de cada resposta. Isso abre espaço para melhorar raciocínio em tarefas verificáveis.

Na mesma matriz: entram problemas com critério verificável; o sinal vem do verificador; a política favorece respostas aprovadas; a saída buscada é maior acerto nessa família de tarefas. O nome não garante que qualquer resposta subjetiva ficou melhor nem que o modelo sabe estimar quando erra.

Mas observem o limite. Eu posso treinar um sistema para acertar mais respostas verificadas e ainda não saber se as probabilidades que ele comunica são boas. Acerto e calibração estão relacionados, mas não são a mesma variável. Se um modelo acerta nove em dez questões, isso não significa automaticamente que ele sabe identificar quais são as dez em que vai errar.

Uma forma curta de resumir: RLHF se apoia em preferência humana; RLVR, em verificação de respostas; a TypeSafe apresenta RLCD como um objetivo voltado a decisões com probabilidades calibradas. Não estou dizendo que as duas primeiras abordagens jamais possam produzir calibração, nem que a terceira tenha exclusividade sobre isso. Estou dizendo qual é o alvo que a empresa escolheu comunicar e que precisamos testar.”

### 22:00–27:00 — O que a TypeSafe chama de RLCD

> **Para estudar RLCD:** a TypeSafe usa esse nome para o treino voltado a escolhas e probabilidades calibradas. Você pode explicar o **objetivo público**; a empresa não publicou detalhes suficientes para reproduzir o treino. Uma **ablação** é um teste em que retiramos uma peça do método para ver se o ganho continua. O público de RL pode perguntar por isso. Sua resposta segura é: “Eu não encontrei esse teste público para isolar o efeito do RLCD”.

“RLCD é o nome *Reinforcement Learning for Calibrated Decisions*. Segundo a TypeSafe, Jev foi treinado para responder perguntas tipadas com distribuições de probabilidade úteis para software. A promessa de calibração é simples de enunciar e difícil de cumprir bem. Se, em muitos exemplos comparáveis, o modelo atribui probabilidade 0,8 às suas escolhas, esperamos que aproximadamente 80% delas estejam corretas. Se ele atribui 0,2, esperamos algo perto de 20% para aquele evento. Isso não quer dizer que uma resposta individual de 0,8 está protegida contra erro.

Na matriz comum, entram estado e perguntas tipadas; a saída buscada é uma escolha e probabilidades úteis. A TypeSafe apresenta a qualidade de decisões calibradas como objetivo. O detalhe exato do sinal de treino e de como a política foi ajustada não foi publicado com a profundidade necessária para reprodução. No slide, essas células aparecem como ‘não divulgado em detalhe’, de propósito.

Por que essa promessa interessa? Porque software pode usar incerteza para decidir quando agir, quando pedir confirmação ou quando encaminhar para uma pessoa. Mas há um salto entre ‘o modelo me deu um número’ e ‘esse número é confiável no meu domínio’. O número só ganha sentido com avaliação em dados representativos.

Aqui eu quero ser rigoroso com vocês. Consigo explicar o objetivo público de RLCD. Não consigo reconstruir o treinamento a partir do material publicado. A publicação não traz dados, algoritmo e testes que separem o efeito do treino do efeito da arquitetura e da forma de produzir as respostas. Em pesquisa, esses testes de retirar ou trocar uma parte são chamados de ablações. Se eu dissesse que a empresa usa Brier, ECE ou uma regra própria como recompensa, estaria inventando. Essas são formas que podemos usar para avaliar probabilidades; não temos essa descrição completa do treinamento.

Portanto, a parte científica da conversa não é repetir o nome do método. É transformar a promessa em perguntas verificáveis. Primeiro: o modelo acerta? Segundo: a confiança acompanha a frequência de acerto? Terceiro: em que tipos de erro ele falha? Quarto: qual é o custo de um erro para o sistema em que eu o coloco?”

[Slides 20–22: foco em RLCD.] “Quero separar três camadas que facilmente se misturam. A primeira é o **objetivo de treino anunciado**: a TypeSafe diz que RLCD procura decisões corretas e probabilidades calibradas. A segunda é o **contrato de saída**: `Choice`, `Noul` e `Score` entregam números que podemos registrar. A terceira é a **evidência empírica**: só dados de avaliação dizem se esses números refletem frequências no domínio onde o sistema vai operar. O contrato torna a calibração testável; ele não a garante.

Um jeito de pensar é comparar dois classificadores que acertam 80 de 100 casos. O primeiro diz 99% em quase tudo, inclusive nos erros. O segundo distribui suas probabilidades de modo que os grupos de 60%, 80% e 90% acertem aproximadamente nessas proporções. A acurácia total pode ser igual, mas o segundo oferece informação mais útil para uma política de encaminhamento. Mesmo assim, precisamos avaliar cada classe: estar bem calibrado no agregado pode esconder excesso de confiança justamente em `CONFIRM`.

O que sabemos publicamente sobre RLCD é o alvo e a interface, não uma receita de treino que eu possa reproduzir. Não sei qual recompensa exata, quais dados ou quais comparações internas geraram Jev. Também não há, no material público que consultei, um experimento que retire só o RLCD e mantenha o resto igual para atribuir o ganho a ele. Por isso minha pergunta ao grupo é científica: que desenho de experimento isolaria o método? Eu usaria a mesma tarefa, o mesmo catálogo, splits congelados, métricas de decisão e de probabilidade, recortes por erro crítico e uma comparação com arquiteturas e métodos alternativos. Nosso estudo com 60 frases testa um uso de Jev, não resolve a origem do desempenho.”

### 27:00–29:00 — Como testar a promessa

> **Para estudar o slide 23:** imagine uma caixa com 100 previsões, todas feitas com probabilidade perto de 80% para a classe escolhida. Abra a caixa e conte quantas estavam certas. Cerca de 80 acertos seria compatível com boa calibração **nessa faixa**. Se só 50 acertaram, o modelo foi confiante demais. Isso não diz que uma previsão específica está correta. No slide, os 100 casos são exemplo inventado para ensinar, não parte do corpus do Maestro.
>
> **Para estudar o slide 24:** *accuracy* pergunta “quantas escolhas acertou?”. ECE e Brier perguntam “os números de probabilidade foram bons?”. Falso aceite pergunta “houve erro que poderia autorizar algo indevido?”. Com 60 casos, nenhuma dessas medidas prova segurança geral.

“Acurácia responde quantas escolhas tiveram o rótulo certo. Calibração responde outra pergunta: quando o modelo atribui uma probabilidade, essa probabilidade corresponde à frequência observada? Imaginem cem decisões agrupadas perto de 0,8. Um modelo calibrado deveria acertar perto de oitenta naquele grupo. Ele ainda erraria por volta de vinte. Isso é esperado; calibração não é infalibilidade.

[Slide 23.] “O slide usa um exemplo imaginário: reúno cem previsões para as quais o modelo disse algo perto de 80%. Se oitenta acertam, esse número parece adequado para o grupo. Se só cinquenta acertam, o modelo estava confiante demais. O exemplo não usa os dados do Maestro.”

Uma métrica possível é o Brier multiclasses, que penaliza probabilidades distantes do rótulo verdadeiro. Outra é o ECE, que compara confiança média e acerto médio por faixas. Um reliability diagram desenha esses grupos; a diagonal indica calibração ideal. Só que o desenho de um gráfico bonito não resolve tamanho de amostra, mudança de domínio ou erros raros. Um bin com quatro exemplos é muito menos informativo do que parece quando visto como um ponto isolado.

[Slide 24.] “Aqui separamos três perguntas: o rótulo está certo? A probabilidade informa bem a frequência de acerto? E que tipo de erro ocorreu? Accuracy e macro-F1 ajudam na primeira, Brier e ECE na segunda, e a matriz de confusão com falsos aceites na terceira. Quando eu mostrar nosso conjunto de apenas sessenta falas, nenhum ECE isolado poderá encerrar a discussão.”

Se eu fosse defender adoção em um sistema real, pediria um conjunto de avaliação congelado antes de ajustar critérios, replicação em outra amostra e recortes onde o custo do erro é maior. A pergunta que deixo para o grupo é: que sinal de treino, que testes isolariam seu efeito e que conjunto de avaliação vocês exigiriam para separar uma boa história sobre RLCD de evidência de calibração? Guardem essa pergunta. Vou voltar a ela quando mostrar dados de uma aplicação concreta.”

[Slide 25, tabela.] “Agora a comparação cabe em uma página: RL usa recompensa do ambiente; RLHF usa preferência humana em uma família clássica de métodos; RLVR usa verificação da tarefa; RLCD é o objetivo anunciado pela TypeSafe para decisões calibradas. A tabela mostra o que cada nome procura favorecer e o que ainda precisa ser medido. Ela não é uma árvore genealógica nem uma lista de etapas obrigatórias.”

## 29:00–32:00 — Três demonstrações: emojis, PR e JevPilot

“Agora, três demonstrações de terceiros. Em cada uma, quero distinguir a decisão do Jev do trabalho do programa ao redor: o que entra, quais opções existem e quem executa o resultado.

[Slide 26, vídeo de Stefan se estiver disponível.] No caso dos emojis, uma frase favorece itens de um catálogo. A interface os anima. É uma decisão curta e de baixo risco. O post mostra o efeito, mas não traz um protocolo completo de avaliação.

[Slide 27, PR Judge.] Um diff limitado vira uma triagem inicial: seguir, revisar ou bloquear. Isso pode evitar uma resposta longa em toda mudança, mas economia de tokens exige medir o fluxo completo e a qualidade da triagem. A demo não lê o repositório inteiro e não executa os testes; CI e revisão humana continuam necessários.

[Slide 28, JevPilot.] Aqui a consequência cresce. O vídeo usa HighwayEnv, uma simulação com estado simbólico, opções de ação e regras de segurança no programa. Não é direção em um Tesla físico. A pergunta interessante é como validar uma escolha rápida antes que ela afete o ambiente.

Esses três casos mostram a mesma interface em tarefas de riscos diferentes. Agora passo do exemplo isolado para o agente: quem prepara o contexto, decide quando consultar Jev e verifica a resposta?”

## 32:00–36:00 — Notas do Diogo: Jev dentro de um agente

[Slide 29.] “Depois dessas demos, quero mostrar uma proposta de arquitetura para agentes. Diogo Almeida compartilhou notas públicas sobre um agente de código. O post de terceiro fala de um PDF de onze páginas; a exportação das notas públicas gera doze. Não afirmo que sejam o mesmo arquivo. A imagem deste slide vem do documento público. É uma ideia de projeto, sem benchmark do agente.”

> **Para estudar KV cache:** é o armazenamento de cálculos sobre um prefixo já processado por um modelo. Ao trocar de modelo, esses cálculos não são transferidos automaticamente. O custo de reler contexto depende do provedor e do cache disponível.

[Slide 30.] “As notas perguntam: como projetar um agente sem depender do KV cache? Se eu saio de um modelo forte para um barato e depois volto, o forte pode precisar reler muito contexto. A economia daquele turno barato pode desaparecer. A conta do documento é ilustrativa. A pergunta prática é que informação cada chamada precisa realmente receber.”

[Slide 31.] “Em vez de mandar o histórico inteiro, o harness pode montar uma janela para a próxima tarefa. Uma saída longa de ferramenta pode entrar completa, resumida ou ser omitida. Instruções de uma pasta e schemas de ferramentas podem ser carregados quando relevantes. Jev poderia ajudar a pontuar essa relevância; o código seleciona e valida o contexto. O risco é ocultar algo importante, então a proposta precisa ser avaliada em tarefas reais.”

[Slide 32.] “Dentro do loop de um agente, Jev poderia escolher uma ferramenta, selecionar contexto ou sugerir uma rota. O harness prepara as opções e valida a resposta. O LLM ou a ferramenta executa a etapa; testes e observações alimentam o próximo passo. Para ações sensíveis, política e autorização permanecem no código e com a pessoa. Jev só economiza recursos se substituir trabalho real do fluxo.”

Fontes para este bloco: [notas públicas](https://docs.google.com/document/d/1G61uUB0FifUnmmrPzFQojZ3KpczYKmXGpgEXDJ2l_Zg/edit), [post de Diogo](https://x.com/CompleteSkeptic/status/2101894250401271876), [Laya](https://github.com/NandhaKishorM/laya), [Julia-1](https://huggingface.co/SupersonicLabs/Julia-1), [CLM](https://github.com/Contrastive-LM/CLM).

## 36:00–43:00 — Por que apareceram modelos parecidos?

> **Para estudar:** Uma interface comum não significa arquitetura ou treino iguais. Um encoder transforma o texto em vetores; pesos pré-treinados reduzem o trabalho necessário para adaptar uma tarefa. Comparar latência exige mesma entrada, mesmo hardware, rede, cache e qualidade. `p50` é mediana; `p95` é a latência abaixo da qual caem 95% das chamadas.

[Slide 33.] “Antes dos nomes, a pergunta: por que surgiram tantos modelos parecidos depois de Jev? Minha leitura é que Jev tornou visível uma interface atraente: estado, opções fechadas e probabilidades. Outros grupos já tinham encoders, pesos e benchmarks que podiam adaptar. A proximidade dos anúncios não prova que cada modelo tenha sido treinado do zero naquela semana. Também não prova que um substitua o outro. A tarefa, o hardware e o protocolo de medição mudam bastante.”

[Slide 34.] “Laya veio com pesos abertos e uma interface semelhante de `Choice`, `Score` e `Noul`. Isso permite executar e inspecionar mais do que uma API fechada. `laya-mlx` é uma adaptação para Apple Silicon, não o nome de outro modelo lançado junto. Peso aberto também não significa, por si, treino totalmente reproduzível.”

[Slide 35.] “A vantagem prática que vale investigar no Maestro é a execução local. O README do runtime MLX relata p50 entre 7,39 e 13,42 ms em um M3 Max, para pergunta curta e modelo carregado. Não comparem isso diretamente com nossos 742 ms medianos de Jev remoto: rede, máquina e tarefa são diferentes. Para decidir, precisamos do mesmo corpus de seis classes, no Android alvo, medindo acerto, erro perigoso, p95, memória e energia.”

[Slide 36.] “Julia-1 merece destaque porque é de uma equipe brasileira, a Supersonic Labs. Parte de mmBERT-small e tem 144,3 milhões de parâmetros. Aceita de duas a vinte opções e pode rodar em CPU; há exportação ONNX. No benchmark publicado, Julia e a referência Jev ficaram próximas numa tarefa de decisões tipadas, mas Julia foi pior na tarefa bancária de categorias parecidas. A referência Jev veio do protocolo anterior, não de uma nova execução lado a lado. Falta pt-BR e a nossa tarefa.”

[Slide 37.] “CLM toma outro caminho. Ele codifica estado e ações como vetores e aprende a aproximar os pares corretos. Se as ações são reutilizadas, seus vetores podem ficar em cache. O repositório relata até 9 vezes menos latência em tarefas selecionadas; a configuração usa um backbone de 8B e GPU. Isso é interessante para catálogos repetidos, mas não transforma o número publicado em velocidade do nosso Android.”

[Slide 38.] “Agora a comparação faz sentido, porque vimos cada proposta. Jev é API remota já medida no nosso corpus; Laya e Julia oferecem caminhos locais; CLM usa similaridade e cache. Não há vencedor nessa tabela. A última linha é o experimento que faltaria: dar a todos as mesmas transcrições e seis rótulos, medir macro-F1, probabilidades, p95, memória, custo e especialmente `CANCEL` confundido com `CONFIRM`. Se o modelo for rápido mas falhar na classe de segurança, não serve como autoridade operacional.”

## 43:00–46:00 — O Maestro Agrícola e o contexto do hackathon

“Até aqui falei de Jev sem exigir que vocês conhecessem nosso projeto. Agora vem o caso de aplicação. O Maestro Agrícola nasceu no contexto do Programa AI Glasses Brasil 2026. Nós, da AgroTurtles, queríamos aproveitar óculos e voz para melhorar a interface de um operador com uma máquina agrícola autônoma. A máquina pode navegar; a pessoa ainda costuma precisar parar, abrir uma tela e percorrer comandos para interagir com ela. A ideia do nosso pitch era simples: olhar, falar, confirmar.

[Slide 39, adaptação da abertura do pitch.] A proposta de produto é uma interface hands-free. No recorte de demonstração, usamos Android/Kotlin, Meta DAT 0.9.0 com MockDeviceKit, QR ou talhão mapeado, um contrato JSON versionado, bridge ROS 2 e Gazebo/Nav2. O MVP pré-hardware foi integrado ponta a ponta. Isso não equivale a câmera e áudio comprovados nos óculos Meta físicos, nem a pulverização real. Eu mostro aqui um sistema robótico simulado e a fronteira de decisão que o protege.

[Slide 40, jornada.] A pessoa olha para o alvo, ou informa um talhão do mapa. Uma foto é solicitada sob demanda. O Android decodifica o QR localmente em memória e reduz o frame a um `target_id`. Então a pessoa fala o que quer fazer. O sistema repete a operação e espera uma confirmação explícita por áudio antes de qualquer movimento. Essa confirmação não pode ser presumida por uma probabilidade alta do classificador.

[Slide 41, arquitetura.] A cadeia completa é fala, decisão tipada, regras e estado determinísticos, confirmação, `Command` JSON, WebSocket, bridge ROS 2 e robô no Gazebo. O caminho da câmera alimenta o resolvedor de alvo, não a escolha de intenção. Se a câmera vê `plot-03` e a fala pede `plot-01`, uma classificação correta de `SPRAY` ainda resulta em ambiguidade e nenhum comando. `DOCK` e `UNDOCK` são pedidos explícitos; `SPRAY` não dispara automaticamente saída ou retorno à doca.

Antes de mostrar Jev no Maestro, preciso explicar duas escolhas de privacidade. O frame não é guardado por padrão. E, no modo remoto demonstrativo, não enviamos qualquer transcrição automaticamente para um serviço externo.”

## 46:00–54:00 — Privacidade, classes, JSON Jev e resultado

[Slides 42 e 43.] “Na visão, ‘só lemos QR’ seria uma simplificação ruim: a câmera entrega um frame. O que implementamos é captura sob demanda, decodificação local do marcador e descarte do frame depois que vira `target_id`. O app não persiste foto, áudio ou transcrição por padrão. O Android, o reconhecimento de fala e o SDK têm suas próprias fronteiras de tratamento; por isso não digo que não existe nenhum dado em trânsito.

A fala, no caminho padrão, fica em memória e vai para `LocalIntentClassifier`. Ele classifica intenção, mas não foi escrito como detector geral de CPF. No caminho Jev remoto, restrito a `mockDebug`, o operador ativa uma sessão depois de um aviso revogável. Antes da rede, `RemoteTranscriptGate` no app e uma checagem no proxy bloqueiam padrões evidentes de CPF/CNPJ, e-mail, telefone, URL, transcrição longa ou fora do escopo. Uma fala bloqueada é descartada localmente; não vira chamada Jev, Qwen nem `Command`. Validamos com um CPF sintético no SM-X510 e a UI mostrou ‘Fala não enviada ao Jev’. Isso é minimização preventiva, não anonimização e não uma auditoria LGPD concluída. Um dado pessoal que não encaixe nesses padrões ainda pode escapar; a pessoa deve usar frases de teste sintéticas na demo.

[Slide 44.] Aqui respondo uma pergunta que pode surgir: são só seis classes? **No experimento Jev, sim.** A pergunta `Choice` fixa `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`, para comparar com o baseline local no mesmo corpus. O Maestro evoluiu em outras rotas, fora desse benchmark. Consultas de histórico e estado, inspeção do alvo e `MISSION_PREVIEW` são reconhecidas localmente antes da classificação operacional. A missão composta não é sétima classe Jev. Um parser determinístico monta um plano tipado de duas a quatro etapas; a pessoa revisa; cada ação física exige confirmação individual. Em `mockDebug` e Gazebo, executamos uma sequência de sair da doca, pulverizar, consultar outro talhão e voltar à doca. Jev não criou nem executou esse plano.

[Slides 45–46, `tools/jev_local_proxy.py` · Python.] “Antes da requisição, o proxy define `CRITERIA`. Aqui estão os seis rótulos completos, divididos em dois slides para leitura: `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`. Cada descrição delimita pedido atual, histórico, hesitação e confirmação. Leiam especialmente `CONFIRM`: o rótulo sozinho não cria uma operação pendente. Esses textos são parte do experimento; trocar uma frase mudaria a pergunta feita ao modelo.”

[Slide 47, `tools/jev_local_proxy.py` · Python.] “Esta é a função real e completa que monta o payload. O Android envia `transcript` ao proxy local. A função põe o texto em `state`, fixa `MODEL`, usa a chave `operational_intent`, define `type: choice`, a instrução que proíbe planejar ou autorizar movimento e injeta os seis critérios. A chave da API fica no proxy. O JSON enviado à TypeSafe é o objeto produzido por esta função; `CRITERIA` foi expandido nos dois slides anteriores.”

[Slide 48, JSON de resposta.] “Isto é uma resposta sanitizada real, guardada como fixture do nosso teste. O caso `recovery-045` deveria ser `CANCEL`. Jev escolheu `CONFIRM`. Reparem que `probabilities.CONFIRM` é 0,75 e o campo `confidence` é 0,70. Eles não são a mesma coisa. A resposta também contabilizou 70 tokens de saída. O preço anunciado para esses tokens é zero; os tokens continuam existindo. O Android usa a probabilidade da classe escolhida para a política operacional.”

[Slide 49, validação.] “O `JevIntentClassifier` não entrega qualquer JSON direto à máquina de estados. Ele confere se o rótulo pertence ao catálogo, se a distribuição contém exatamente as seis chaves, se todos os valores são finitos e válidos, se somam aproximadamente um e se a escolha não perdeu para outra opção. Timeout, resposta inválida ou probabilidade insuficiente retornam `UNKNOWN`. Há um guard determinístico para cancelamento explícito, desligado por padrão no benchmark bruto.”

> **Para estudar o harness:** o corpus é uma tabela de falas sintéticas com rótulo esperado. Uma rodada remota Jev produziu uma *fixture* sanitizada: respostas salvas por ID, sem texto da fala. O harness lê a mesma tabela, roda o classificador local e junta cada resposta Jev pelo ID. Só então outro script calcula as métricas. Isso impede comparar modelos em frases diferentes. Não é um treinador de modelos.

[Slide 50.] Na rodada pareada de sessenta falas sintéticas, Jev acertou 54 e o local 48. Macro-F1: 0,9010 versus 0,8026. O resultado descritivo favorece Jev neste corpus. A latência p95 remota foi cerca de 2,1 segundos; a local, 0,293 milissegundo no host do teste. As sessenta chamadas Jev custaram cerca de US$ 0,00147. São números do harness, não do Android no campo. Os ECEs ficaram próximos, 0,0787 para Jev e 0,0810 para local, mas sessenta falas e uma rodada não provam calibração geral. A fixture registrou 69 a 71 `output_tokens` por chamada; o anúncio comercial é preço zero para essa parte, não uso zero.

[Slide 51.] A média não encerra a decisão. Entre os sessenta casos, Jev transformou uma fala cujo esperado era `CANCEL` em `CONFIRM`, com probabilidade 0,75 para essa escolha. O local teve três aceites inseguros; Jev teve um. Mesmo um só é relevante quando uma confirmação pode liberar movimento. A decisão documentada foi `HOLD`: não promover Jev a autoridade operacional. O estudo faz sentido porque mostrou um ganho médio e, ao mesmo tempo, um erro que impede adoção segura. A próxima pesquisa precisa de ASR real, replicação independente, estratos de segurança e avaliação do guard sem contaminar o holdout.”

## 54:00–58:00 — Demonstração e fechamento

**Se o caminho remoto estiver funcionando, falar enquanto executa:**

“Aqui está o modo de demonstração no `mockDebug`, conectado ao proxy e ao Gazebo. Vou dizer uma frase operacional de teste. Primeiro observamos a transcrição, depois a intenção com origem ‘Jev’. Neste ponto ainda não há movimento. A aplicação verifica estado e alvo e pede confirmação por áudio. Só depois de uma confirmação explícita ela constrói o `Command` JSON e o envia ao bridge. A parte que Jev fez foi classificar a intenção; o resto foi validado e executado pelo Maestro. Esta é uma execução no simulador, não no campo.”

**Se houver um vídeo previamente gravado e conferido, substituir a fala anterior por:**

“A conexão não está estável, então vou mostrar uma gravação da mesma jornada. Esta é uma gravação do Android e do Gazebo, não uma execução ao vivo. Observem a origem da intenção, a espera pela confirmação e o momento em que o comando estruturado é enviado. Jev classifica a fala; o Maestro decide se ela pode virar ação.”

**Se não houver execução nem vídeo, usar as três capturas offline e falar:**

“A reserva que temos é visual. Estas três telas foram capturadas com Wi-Fi desligado. A primeira mostra o baseline local; a segunda, uma fixture de interface com `SPRAY` e origem Jev; a terceira, `UNKNOWN` e nenhum comando enviado. Leiam a legenda comigo: **‘fixture mock local — não executa o robô’**. Elas demonstram a apresentação da decisão e da recusa para o operador. Não demonstram chamada Jev remota, reconhecimento de fala ou movimento no Gazebo.”

**Slide 54, fechamento após qualquer uma das três opções:**

“O que levo deste estudo é uma separação de responsabilidades. Jev torna concreta uma interface interessante: pergunta fechada, escolha tipada e distribuição de probabilidades, sem gerar uma resposta longa em texto. RLCD é a proposta de treinamento da TypeSafe para melhorar a qualidade dessas decisões e probabilidades, mas a descrição pública do treino não permite dizer quanto do resultado veio do RLCD. No nosso corpus, Jev melhorou a média e errou uma recusa crítica. Por isso não o adotei como autoridade operacional. O Maestro continua dependendo de alvo, regras, confirmação e testes próprios. Para mim, o próximo passo é medir melhor, não declarar vitória.”

**Se sobrar tempo, acrescentar em uma frase:** “O Maestro também executou no Gazebo uma missão de várias etapas, com parser local e confirmação por ação física; Jev não criou nem executou esse plano.”

## 58:00–63:00 — O que falta testar

[Slide 55.] “Para fechar, há três perguntas simples que nosso teste ainda não respondeu. Primeiro: Jev classifica bem transcrições de falas reais? Jev recebe texto do reconhecimento de voz, não áudio. As sessenta frases do nosso resultado principal eram sintéticas. Segundo: quando ele dá 80% de probabilidade, acerta perto de 80% dos casos parecidos? É isso que queremos dizer com calibração. Terceiro: consegue distinguir ‘cancelar’ de ‘confirmar’ com segurança? Em um caso do nosso teste, a resposta foi `CONFIRM` quando a pessoa queria cancelar. Esse erro manteve a decisão de não usar Jev como autoridade operacional.

Se alguém quiser aprofundar o RLCD, a pergunta de pesquisa vem depois: que detalhes do treinamento e que comparação permitiriam dizer que a melhora foi causada especificamente por esse método? O material público ainda não permite responder isso. Podemos discutir qualquer uma dessas perguntas.”

[Depois das perguntas, slide 56.] “Obrigado. Se quiserem, abro o contrato da `Choice`, o código do classificador ou a matriz de erros para discutir uma decisão específica.”

**Se perguntarem “por que não escrever só um `if`?”, responder:** “Se regras escritas à mão resolverem as variações reais, eu prefiro as regras. O experimento mede se um classificador probabilístico melhora cobertura sem aumentar o risco. Ainda não demonstramos isso o suficiente para controle operacional.”

**Se perguntarem “Jev não alucina?”, responder:** “O catálogo fechado limita formato e opções. Não impede que o modelo escolha a opção errada com confiança alta. O `CANCEL → CONFIRM` do nosso teste é um exemplo.”

**Se perguntarem “então RLCD funciona?”, responder:** “Podemos testar a alegação de calibração em tarefas concretas. Nosso conjunto sintético e uma rodada não identificam o efeito causal do algoritmo de treinamento nem provam calibração fora desse conjunto.”

## Fontes para conferência — não ler em voz alta

- [Contrato, primitivas, Playground e exemplo de API da TypeSafe](https://docs.typesafe.ai/introduction/quickstart); [explicação pública de RLCD](https://docs.typesafe.ai/introduction/machine-learning-primer); [anúncio técnico e ressalvas dos benchmarks](https://typesafe.ai/blog/introducing-system-one-models-and-jev).
- [Choice na documentação oficial](https://docs.typesafe.ai/primitives/choice); [vídeo de emojis do Stefan](https://x.com/heystefan_/status/2101369117496521042); [PR Judge](https://jevtypesafeai.com/tools/pr-judge); [JevPilot](https://x.com/jpschroeder/status/2100347770867458384); [avaliação dos casos externos](external-case-assessment.md).
- [Roteiro canônico e links de todos os casos externos](presentation-script.md).
- [Comparação medida JEV-41R](results/jev-final-recovery-presentation.md), [fixture de uso de tokens](results/jev-final-recovery-fixture.json), [decisão `HOLD`](../../tasks/jev-experimental-decision.md).
- [Fluxo de dados](../../privacy-data-flow.md), [gate remoto e CPF sintético](../../tasks/jev-remote-privacy-gate.md), [missão composta](../../tasks/mission-preview-contract.md), [demo offline](../../tasks/jev-offline-reserve-demo.md).
