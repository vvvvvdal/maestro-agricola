# Texto integral para falar — Jev, Reinforcement Learning e decisões calibradas em um sistema robótico

Base: [roteiro canônico](presentation-script.md). Meta: **45 minutos de apresentação e 5 de discussão**. As frases abaixo são uma proposta de fala, não evidência adicional. Os trechos entre **[colchetes]** são ações ou escolhas do apresentador e **não são lidos**. Cronometrar em voz alta: os tempos incluem pausas, leitura de resultados e navegação no Playground.

Antes de começar, deixar o Playground autenticado e o exemplo sem dados pessoais preparado. Preparar os cinco vídeos de terceiros e a gravação do Maestro em arquivos locais ou abas abertas. Se algum vídeo não funcionar, o slide contém a leitura técnica do caso. Não projetar credenciais nem dashboard de cobrança.

## 0:00–4:00 — O que é Jev e por que um “if com IA”

“Imaginem um bot de atendimento no WhatsApp que tenta conversar como uma pessoa. O cliente escreve: ‘Minha cobrança veio duplicada. Consegue resolver?’. O bot pode responder de forma simpática, mas precisa tomar uma decisão operacional bem específica: encaminhar para suporte técnico, financeiro, comercial ou para uma pessoa revisar. A qualidade da conversa e a qualidade desse encaminhamento são problemas diferentes.

Eu poderia enviar a mensagem a um modelo de linguagem e pedir uma resposta em texto: ‘analise o caso, explique seu raciocínio e diga qual equipe deve receber’. Mas, se a próxima etapa do software só precisa de uma categoria, eu passo a gerar uma resposta longa para depois extrair uma palavra dela. Essa é a situação em que Jev tenta ser útil.

Jev é o primeiro modelo público de uma empresa chamada TypeSafe. A proposta é receber um estado, receber uma ou mais perguntas com saídas definidas e retornar decisões tipadas, acompanhadas de probabilidades. No nosso chamado, o estado é a mensagem da pessoa. A pergunta é qual equipe deve recebê-la. As saídas possíveis são as equipes que eu defini antes da chamada.

Quando digo ‘tipada’, não quero dizer correta. Quero dizer que a forma da resposta está limitada por um contrato. A aplicação sabe que a resposta deve ser uma escolha daquele catálogo. Ela também recebe uma distribuição: quanto da probabilidade ficou em suporte técnico, quanto em financeiro e assim por diante. Isso permite que o software tenha uma política para casos incertos.

Uma forma de pensar nisso é: chamado, escolha probabilística, regra da aplicação, fila. O modelo faz a escolha; o código continua responsável pela regra e pela consequência. Por exemplo: eu posso encaminhar automaticamente só acima de certo limiar, pedir revisão humana abaixo dele e recusar uma resposta inválida. Esse limiar não sai magicamente do modelo. A equipe precisa defini-lo e testá-lo.

Vocês talvez tenham visto a frase ‘Jev é um if com IA’. O exemplo clássico é `if (idade >= 18) maiorDeIdade = true`. Se a idade já é um número confiável, usem esse `if`: Jev não acrescenta nada. Agora imaginem uma frase como ‘tenho quase dezoito, faço aniversário mês que vem’. O programa pode perguntar a Jev por uma resposta binária, usando `Noul`: ‘A frase afirma que a pessoa já tem pelo menos 18 anos?’. Ele retorna uma probabilidade de ‘sim’. O software precisa definir o que fazer com a incerteza, e jamais usaria essa inferência para verificar idade em uma decisão legal. O exemplo só mostra a diferença entre regra exata e interpretação de texto.

Um contexto histórico de vinte segundos: o fundador da TypeSafe, Diogo Almeida, relata ter trabalhado na OpenAI em métodos ligados a modelos que seguem instruções. A página da empresa o apresenta como coinventor de RLHF e InstructGPT. É uma origem interessante para uma apresentação de RL, mas currículo não é evidência de que Jev funcione bem em todo problema. O nome ‘System One Model’ faz referência à ideia de decisão rápida do livro *Thinking, Fast and Slow*. É uma inspiração de produto; não vou tratar isso como descrição científica de cognição humana. Jev também remete a William Stanley Jevons, economista associado ao paradoxo de eficiência e aumento de uso.

Então guardem esta primeira definição: estado entra, pergunta tipada entra, decisão e probabilidades saem. Agora vamos comparar essa interface com a de um LLM comum.”

## 4:00–9:00 — Jev, LLM, primitivas e tokens

“Um LLM generativo é extremamente flexível. Ele pode conversar, escrever código, resumir, explicar e produzir texto aberto. Essa flexibilidade é ótima quando eu realmente preciso de uma resposta em linguagem. Para um passo interno de um programa, porém, a resposta aberta costuma exigir parsing e validação. Às vezes usamos JSON mode ou schema, o que ajuda muito, mas ainda precisamos pensar na tarefa, nos erros e na política depois da resposta.

Jev propõe uma interface mais estreita. A primitiva que mais nos interessa hoje se chama `Choice`. Eu forneço uma pergunta e um catálogo: técnico, financeiro, comercial, revisão humana. Jev retorna a opção escolhida e a probabilidade atribuída a cada opção. Um bom catálogo inclui uma saída para ‘nenhuma das anteriores’ ou revisão, porque o mundo real nem sempre cabe nas categorias positivas.

Existem outras duas primitivas que vale conhecer. `Noul` responde uma pergunta binária, como ‘essa mensagem expressa urgência?’. `Score` situa algo numa escala ordenada, como a intensidade de frustração. A documentação permite fazer várias perguntas sobre o mesmo estado numa chamada. Elas são avaliadas em paralelo segundo a TypeSafe. Isso pode ser útil, mas cada pergunta e cada critério também entram no payload e aumentam o tamanho da entrada.

Aqui está um dos pontos que mais me chamaram atenção: tokens de saída. Um LLM generativo normalmente produz uma sequência de tokens de texto. Se eu peço três parágrafos, há três parágrafos a gerar. Jev não escreve uma resposta aberta dessa forma. Ele entrega valores estruturados. A TypeSafe diz que amostra as decisões em paralelo e anuncia preço zero para tokens de saída. Isso pode baratear uma decisão curta e repetida.

Mas preciso separar três coisas: gerar prosa, contabilizar tokens de saída e cobrar por esses tokens. A documentação da própria TypeSafe mostra uma resposta `Choice` com 34 `output_tokens`. Portanto, não vou dizer que Jev consome zero tokens de saída. A afirmação comercial é que a **cobrança** dos tokens de saída é zero. O serviço ainda recebe tokens de entrada, usa rede e tem custo por chamada. Mais tarde vou mostrar o que apareceu no nosso experimento.

Também não quero repetir números de marketing como se fossem uma constante da natureza. Existem demonstrações que falam de centenas de vezes menos custo ou latência. A própria TypeSafe avisa que os ganhos publicados nos workflows dela provavelmente estão na ponta alta dos ganhos reais. Uma comparação justa teria a mesma tarefa, entrada equivalente, qualidade da decisão, custo total e latência ponta a ponta. Comparar uma frase curta com um LLM escrevendo uma dissertação responderia a outra pergunta.

[Na tabela do slide 8, percorrer as linhas de cima para baixo.] “Um LLM aceita tarefas abertas e gera texto, código ou JSON. Jev recebe perguntas tipadas e devolve decisões sobre opções que nós definimos. JSON mode aproxima o formato de um LLM de um contrato, então a diferença interessante não é dizer que LLM não consegue devolver JSON. É comparar a qualidade, a latência e o custo de uma mesma decisão. Nos dois casos, a aplicação valida a resposta e decide a consequência.”

Mais uma distinção técnica antes do exemplo. Em `Choice`, a resposta traz um mapa chamado `probabilities`. Ele diz a probabilidade de cada alternativa. Há também um campo chamado `confidence`, calculado a partir de quão concentrada está a distribuição. Se uma opção tem quase toda a massa, a distribuição é concentrada. Se a massa está espalhada, ela é difusa. A probabilidade da opção vencedora e o campo `confidence` podem ser diferentes; vou apontar os dois se aparecerem no site. Para `Noul`, o contrato não retorna esse mesmo campo.

A pergunta de design que fica é: em que decisões discretas, frequentes e ambíguas vocês hoje fazem uma chamada generativa inteira, embora o código só precise de uma pequena bifurcação? Vamos montar uma dessas decisões no Playground.”

[Slide 9.] “Antes de abrir o console, esta é a fonte que vou usar: a documentação oficial de `Choice`. Ela define uma opção de um conjunto fechado e mostra os campos `state`, `model`, `questions`, `criteria`, `choice`, `probabilities` e `confidence`. O quick start da TypeSafe usa um chamado de suporte muito parecido com o nosso. Vou mostrar a página, não um print de uma resposta da minha conta, e depois construir um caso sintético no Playground.”

## 9:00–13:00 — Exemplo no Playground da TypeSafe

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

## 13:00–25:00 — RL, RLHF, RLVR, RLCD e calibração

### 13:00–16:00 — RL básico

“Antes de falar de RLCD, vale colocar os nomes na mesma mesa sem fingir que são a mesma técnica. No exemplo clássico de reinforcement learning, um agente observa um estado, escolhe uma ação segundo uma política, recebe uma recompensa e encontra um novo estado. Escrevemos isso como estado `s`, ação `a`, recompensa `r`, próximo estado `s'`. A política, que posso escrever como pi de a dado s, é o que o treinamento ajusta para aumentar o retorno esperado.

Vou usar o mesmo esquema visual nos quatro slides: o que entra, de onde vem o sinal de qualidade, o que se ajusta, qual saída queremos e o que esse nome sozinho ainda não prova. Em RL básico, entra o estado, o ambiente devolve recompensa, a política muda e esperamos ações que aumentem o retorno. Isso organiza a comparação sem fingir que as siglas especificam todo o algoritmo.

Imaginem um jogo simples. Em cada posição, o agente escolhe mover para a esquerda ou para a direita. A recompensa pode vir só ao alcançar o objetivo ou ao evitar uma colisão. O agente não recebe uma lista de frases bonitas para escrever; ele recebe um sinal que favorece certos comportamentos ao longo do tempo. O que exatamente é recompensado muda o que a política aprende.

Esse último ponto é a ponte para o restante. ‘Usa RL’ ainda diz pouco. Preciso perguntar: qual é a saída? De onde vem o sinal de qualidade? Ele mede preferência humana, resposta verificável ou qualidade da incerteza? Como o sinal é obtido? E como sabemos que a melhoria veio do treino, e não de uma mudança de arquitetura, do sampler ou da forma de perguntar?

Vou passar por três nomes que aparecem nesta discussão: RLHF, RLVR e RLCD. Não são estágios obrigatórios de uma única receita. Eles destacam objetivos de treino diferentes.”

### 16:00–20:00 — RLHF e RLVR

“RLHF quer dizer reinforcement learning from human feedback. No roteiro clássico, pessoas comparam respostas ou indicam preferências. Essas comparações alimentam um modelo de recompensa, ou algum sinal equivalente, e a política é ajustada para favorecer respostas que esse sinal avalia melhor. Existem variantes; não estou dizendo que todo sistema chamado RLHF implementa o mesmo algoritmo.

Seguindo o esquema: entram respostas para uma tarefa; o sinal vem de comparações humanas; a política é ajustada para produzir respostas preferidas; e a limitação é que preferência não prova calibração. É o mesmo ciclo de ajuste, com outra fonte de qualidade.

Por que isso foi tão importante para modelos de conversa? Porque uma resposta pode ser tecnicamente possível e ainda ser pouco útil para quem perguntou. Preferências humanas ajudam a selecionar o tipo de resposta que as pessoas querem receber. Só que existe uma distinção crucial para hoje: uma resposta preferida não é necessariamente uma estimativa de probabilidade bem calibrada. Se peço a um modelo uma decisão e ele diz ‘tenho 90% de certeza’, posso gostar da explicação, mas ainda preciso medir se esse 90% se comporta como 90% em muitos casos.

RLVR significa reinforcement learning with verifiable rewards. Aqui temos tarefas nas quais parte da qualidade pode ser checada por um verificador relativamente objetivo: um resultado matemático, um teste de código, uma condição formal. A recompensa pode vir dessa checagem, sem precisar perguntar a uma pessoa se gostou de cada resposta. Isso abre espaço para melhorar raciocínio em tarefas verificáveis.

Na mesma matriz: entram problemas com critério verificável; o sinal vem do verificador; a política favorece respostas aprovadas; a saída buscada é maior acerto nessa família de tarefas. O nome não garante que qualquer resposta subjetiva ficou melhor nem que o modelo sabe estimar quando erra.

Mas observem o limite. Eu posso treinar um sistema para acertar mais respostas verificadas e ainda não saber se as probabilidades que ele comunica são boas. Acerto e calibração estão relacionados, mas não são a mesma variável. Se um modelo acerta nove em dez questões, isso não significa automaticamente que ele sabe identificar quais são as dez em que vai errar.

Uma forma curta de resumir: RLHF se apoia em preferência humana; RLVR, em verificação de respostas; a TypeSafe apresenta RLCD como um objetivo voltado a decisões com probabilidades calibradas. Não estou dizendo que as duas primeiras abordagens jamais possam produzir calibração, nem que a terceira tenha exclusividade sobre isso. Estou dizendo qual é o alvo que a empresa escolheu comunicar e que precisamos testar.”

### 20:00–23:00 — O que a TypeSafe chama de RLCD

“RLCD é o nome *Reinforcement Learning for Calibrated Decisions*. Segundo a TypeSafe, Jev foi treinado para responder perguntas tipadas com distribuições de probabilidade úteis para software. A promessa de calibração é simples de enunciar e difícil de cumprir bem. Se, em muitos exemplos comparáveis, o modelo atribui probabilidade 0,8 às suas escolhas, esperamos que aproximadamente 80% delas estejam corretas. Se ele atribui 0,2, esperamos algo perto de 20% para aquele evento. Isso não quer dizer que uma resposta individual de 0,8 está protegida contra erro.

Na matriz comum, entram estado e perguntas tipadas; a saída buscada é uma escolha e probabilidades úteis. A TypeSafe apresenta a qualidade de decisões calibradas como objetivo. O detalhe exato do sinal de treino e de como a política foi ajustada não foi publicado com a profundidade necessária para reprodução. No slide, essas células aparecem como ‘não divulgado em detalhe’, de propósito.

Por que essa promessa interessa? Porque software pode usar incerteza para decidir quando agir, quando pedir confirmação ou quando encaminhar para uma pessoa. Mas há um salto entre ‘o modelo me deu um número’ e ‘esse número é confiável no meu domínio’. O número só ganha sentido com avaliação em dados representativos.

Aqui eu quero ser rigoroso com vocês. Consigo explicar o objetivo público de RLCD. Não consigo reconstruir o treinamento a partir do material publicado. Não temos detalhe suficiente sobre a função de recompensa, dados, algoritmo, arquitetura e ablações para isolar quanto do resultado vem de RLCD, quanto vem da interface de saída e quanto vem do sampler. Se eu dissesse que a empresa usa Brier, ECE ou uma regra própria como recompensa, estaria inventando. Essas são formas que podemos usar para avaliar probabilidades; não conhecemos a receita interna em detalhe.

Portanto, a parte científica da conversa não é repetir o nome do método. É transformar a promessa em perguntas verificáveis. Primeiro: o modelo acerta? Segundo: a confiança acompanha a frequência de acerto? Terceiro: em que tipos de erro ele falha? Quarto: qual é o custo de um erro para o sistema em que eu o coloco?”

### 23:00–25:00 — Como testar a promessa

“Acurácia responde quantas escolhas tiveram o rótulo certo. Calibração responde outra pergunta: quando o modelo atribui uma probabilidade, essa probabilidade corresponde à frequência observada? Imaginem cem decisões agrupadas perto de 0,8. Um modelo calibrado deveria acertar perto de oitenta naquele grupo. Ele ainda erraria por volta de vinte. Isso é esperado; calibração não é infalibilidade.

[Slide 17.] “O desenho tem cem previsões do mesmo nível de confiança. Se oitenta acertam, a fala ‘0,8’ foi honesta em média. Se só cinquenta acertam, há excesso de confiança, mesmo que a accuracy global em outra faixa pareça boa. A diagonal de um gráfico de calibração representa essa correspondência entre confiança declarada e frequência de acerto.”

Uma métrica possível é o Brier multiclasses, que penaliza probabilidades distantes do rótulo verdadeiro. Outra é o ECE, que compara confiança média e acerto médio por faixas. Um reliability diagram desenha esses grupos; a diagonal indica calibração ideal. Só que o desenho de um gráfico bonito não resolve tamanho de amostra, mudança de domínio ou erros raros. Um bin com quatro exemplos é muito menos informativo do que parece quando visto como um ponto isolado.

[Slide 18.] “Aqui separamos três perguntas: o rótulo está certo? A probabilidade informa bem a frequência de acerto? E que tipo de erro ocorreu? Accuracy e macro-F1 ajudam na primeira, Brier e ECE na segunda, e a matriz de confusão com falsos aceites na terceira. Quando eu mostrar nosso conjunto de apenas sessenta falas, nenhum ECE isolado poderá encerrar a discussão.”

Se eu fosse defender adoção em um sistema real, pediria um conjunto de avaliação congelado antes de ajustar critérios, replicação em outra amostra e recortes onde o custo do erro é maior. A pergunta que deixo para o grupo é: que recompensa, que ablações e que holdout vocês exigiriam para separar uma boa história sobre RLCD de evidência de calibração? Guardem essa pergunta. Vou voltar a ela quando mostrar dados de uma aplicação concreta.”

[Slide 19, tabela.] “Agora a comparação cabe em uma página: RL usa recompensa do ambiente; RLHF usa preferência humana em uma família clássica de métodos; RLVR usa verificação da tarefa; RLCD é o objetivo anunciado pela TypeSafe para decisões calibradas. A tabela mostra o que cada nome procura favorecer e o que ainda precisa ser medido. Ela não é uma árvore genealógica nem uma lista de etapas obrigatórias.”

## 25:00–31:00 — Cinco exemplos de Jev, começando pelos emojis

“Agora vou percorrer cinco demos. Em todas, façam a mesma pergunta comigo: qual texto ou estado entrou, quais escolhas foram oferecidas ao Jev e qual parte da aplicação produziu o efeito que vemos na tela? São demonstrações de terceiros, não nosso benchmark.

[Slide 20, vídeo de Stefan se estiver disponível.] O primeiro é propositalmente leve. Há um monte de emojis na tela. Conforme a pessoa digita uma frase, os emojis relacionados sobem ou ganham destaque. ‘Coisas para usar no inverno’ favorece um conjunto; mudar a frase muda o conjunto. A interpretação da frase pode ser rápida e visualmente impressionante. Mas Jev não está desenhando emojis nem simulando a física da pilha. A interface usa um catálogo existente e código para animá-lo. O post mostra o efeito; não publica um protocolo completo de avaliação. Isso é uma boa porta de entrada para entender decisão sobre opções já existentes.

[Slide 21, Daniel Avila.] Agora uma escolha com consequência prática para agentes: qual skill carregar para esta tarefa? Se o agente sempre coloca todas as skills no contexto, ele paga em tokens e pode receber instruções irrelevantes. Jev pode escolher uma skill candidata antes da chamada principal. A opção ‘nenhuma’ é essencial. O teste interessante é se ele reduz o contexto sem descartar a skill que teria evitado um erro. A seleção do modelo não executa a skill; outro código injeta o arquivo escolhido.

[Slide 22, PR Judge.] Um pull request traz um diff limitado. A demo pergunta se o primeiro encaminhamento é algo como seguro, revisar ou bloquear. Uma decisão curta pode evitar pedir uma longa resenha generativa em todo PR. Mas ‘economizar tokens’ só é resultado quando medimos o fluxo completo e a qualidade da triagem. A própria demo diz que não lê o repositório inteiro e não roda testes. Então este exemplo não substitui CI ou revisão humana. Esta demo veio da pesquisa complementar; não é um dos links de tweet que vocês me enviaram.

[Slide 23, xadrez.] Aqui o harness importa mais que a manchete. Em blitz 5+0, uma chamada por lance e sem busca, Jev venceu Fable 5.1 no relógio. Fable tinha grande vantagem material, inclusive segunda dama. Jev foi mais rápido sob aquela regra; não provou maior força em xadrez. Contra Astra, veio mate em 18 lances com tempo sobrando para Astra. Xadrez exige cálculo e busca. A comparação mostra onde decisões curtas podem ficar inadequadas à tarefa.

[Slide 24, JevPilot.] O post fala em Tesla, mas o artefato demonstrado é uma simulação HighwayEnv. O programa fornece estado simbólico e opções de ação, e há regras de segurança fora do modelo. Jev escolhe dentro desse espaço fechado. Não houve câmera real, veículo físico ou validação de direção autônoma. Eu colocaria no slide o vídeo do simulador e chamaria a legenda de ‘simulação’, justamente para não confundir interface com autonomia de carro.

Esses cinco exemplos avançam do reversível ao crítico. Errar um emoji custa pouco; errar uma skill pode empobrecer o agente; errar uma triagem de PR pode atrasar revisão; no xadrez há adversário e relógio; numa simulação de direção já precisamos perguntar por controlador e safety layer. Essa gradação prepara o próximo bloco: onde a velocidade deixa de ser suficiente?”

## 31:00–33:00 — Limites de Jev e o aparecimento de Laya

“Então, Jev é rápido, mas pode parecer burro às vezes? Eu formularia com mais precisão: ele foi desenhado para uma decisão curta, não para desenvolver uma linha longa de raciocínio em texto. Tipagem impede uma classe de erro de formato; não garante a escolha correta. E uma distribuição com uma opção dominante ainda pode estar errada. Para avaliar qualquer aplicação, o risco desse erro precisa entrar na conta.

Pouco depois do lançamento do Jev, apareceu Laya como proposta aberta para decisões tipadas. O projeto `laya-mlx` porta pesos para execução local em Apple Silicon. O repositório reporta medianas de 7,39 a 13,42 milissegundos para **uma pergunta curta** num M3 Max, sem incluir o carregamento do modelo. Isso é um resultado do próprio projeto em hardware específico. A demo de Snake usa três perguntas por ciclo e também uma camada de segurança no software. Não é correto colocar o número de uma pergunta curta ao lado do tempo de um loop inteiro e anunciar que um produto venceu o outro.

Por que mencionar Laya? Porque, se a contribuição mais interessante aqui é uma interface de decisão, faz sentido perguntar se outras implementações conseguem atender ao mesmo contrato. Um serviço remoto e pesos locais têm consequências diferentes para latência, operação e circulação de dados. A comparação que eu gostaria de ver seria pareada: mesmo problema, catálogo, corpus, hardware de destino, política de falha e métricas de qualidade. Eu não tenho essa comparação. Também não vou afirmar que Laya roda bem em qualquer aparelho só porque o port para Mac foi rápido.

Essa é uma boa hora para fechar a parte geral. O que sabemos de Jev? Ele oferece decisões tipadas com probabilidades; evita gerar prosa aberta para uma escolha pequena; a TypeSafe anuncia saída sem cobrança por token; e chama seu objetivo de treino de RLCD. O que ainda precisa de teste? A qualidade das escolhas, a calibração no domínio específico, latência real da aplicação e os erros que mais custam. Agora vou mostrar um domínio em que essas perguntas importam para nós.”

## 33:00–37:00 — O Maestro Agrícola e o contexto do hackathon

“Até aqui falei de Jev sem exigir que vocês conhecessem nosso projeto. Agora vem o caso de aplicação. O Maestro Agrícola nasceu no contexto do Programa AI Glasses Brasil 2026. Nós, da AgroTurtles, queríamos aproveitar óculos e voz para melhorar a interface de um operador com uma máquina agrícola autônoma. A máquina pode navegar; a pessoa ainda costuma precisar parar, abrir uma tela e percorrer comandos para interagir com ela. A ideia do nosso pitch era simples: olhar, falar, confirmar.

[Slide 26, adaptação da abertura do pitch.] A proposta de produto é uma interface hands-free. No recorte de demonstração, usamos Android/Kotlin, Meta DAT 0.9.0 com MockDeviceKit, QR ou talhão mapeado, um contrato JSON versionado, bridge ROS 2 e Gazebo/Nav2. O MVP pré-hardware foi integrado ponta a ponta. Isso não equivale a câmera e áudio comprovados nos óculos Meta físicos, nem a pulverização real. Eu mostro aqui um sistema robótico simulado e a fronteira de decisão que o protege.

[Slide 27, jornada.] A pessoa olha para o alvo, ou informa um talhão do mapa. Uma foto é solicitada sob demanda. O Android decodifica o QR localmente em memória e reduz o frame a um `target_id`. Então a pessoa fala o que quer fazer. O sistema repete a operação e espera uma confirmação explícita por áudio antes de qualquer movimento. Essa confirmação não pode ser presumida por uma probabilidade alta do classificador.

[Slide 28, arquitetura.] A cadeia completa é fala, decisão tipada, regras e estado determinísticos, confirmação, `Command` JSON, WebSocket, bridge ROS 2 e robô no Gazebo. O caminho da câmera alimenta o resolvedor de alvo, não a escolha de intenção. Se a câmera vê `plot-03` e a fala pede `plot-01`, uma classificação correta de `SPRAY` ainda resulta em ambiguidade e nenhum comando. `DOCK` e `UNDOCK` são pedidos explícitos; `SPRAY` não dispara automaticamente saída ou retorno à doca.

Antes de mostrar Jev no Maestro, preciso explicar duas escolhas de privacidade. O frame não é guardado por padrão. E, no modo remoto demonstrativo, não enviamos qualquer transcrição automaticamente para um serviço externo.”

## 37:00–43:00 — Privacidade, classes, código Jev e resultado

[Slides 29 e 30.] “Na visão, ‘só lemos QR’ seria uma simplificação ruim: a câmera entrega um frame. O que implementamos é captura sob demanda, decodificação local do marcador e descarte do frame depois que vira `target_id`. O app não persiste foto, áudio ou transcrição por padrão. O Android, o reconhecimento de fala e o SDK têm suas próprias fronteiras de tratamento; por isso não digo que não existe nenhum dado em trânsito.

A fala, no caminho padrão, fica em memória e vai para `LocalIntentClassifier`. Ele classifica intenção, mas não foi escrito como detector geral de CPF. No caminho Jev remoto, restrito a `mockDebug`, o operador ativa uma sessão depois de um aviso revogável. Antes da rede, `RemoteTranscriptGate` no app e uma checagem no proxy bloqueiam padrões evidentes de CPF/CNPJ, e-mail, telefone, URL, transcrição longa ou fora do escopo. Uma fala bloqueada é descartada localmente; não vira chamada Jev, Qwen nem `Command`. Validamos com um CPF sintético no SM-X510 e a UI mostrou ‘Fala não enviada ao Jev’. Isso é minimização preventiva, não anonimização e não uma auditoria LGPD concluída. Um dado pessoal que não encaixe nesses padrões ainda pode escapar; a pessoa deve usar frases de teste sintéticas na demo.

[Slide 31.] Aqui respondo uma pergunta que pode surgir: são só seis classes? **No experimento Jev, sim.** A pergunta `Choice` fixa `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`, para comparar com o baseline local no mesmo corpus. O Maestro evoluiu em outras rotas, fora desse benchmark. Consultas de histórico e estado, inspeção do alvo e `MISSION_PREVIEW` são reconhecidas localmente antes da classificação operacional. A missão composta não é sétima classe Jev. Um parser determinístico monta um plano tipado de duas a quatro etapas; a pessoa revisa; cada ação física exige confirmação individual. Em `mockDebug` e Gazebo, executamos uma sequência de sair da doca, pulverizar, consultar outro talhão e voltar à doca. Jev não criou nem executou esse plano.

[Slide 32, código.] O Android usa `JevProxyChoiceEvaluator`. Ele envia somente uma transcrição curta ao proxy loopback. A chave e os critérios da pergunta ficam fora do APK. O proxy fixa `jev-1.13.0` e constrói uma `Choice` com seis rótulos. Observem a fronteira: não há foto, áudio bruto, target, estado do robô, `Command` ou acesso ROS no request. A resposta chega como dados, incluindo escolha, distribuição e uso em tokens.

[Slide 33, código.] O `JevIntentClassifier` não entrega qualquer JSON direto à máquina de estados. Ele confere se o rótulo pertence ao catálogo, se a distribuição contém exatamente as seis chaves, se todos os valores são finitos e válidos, se somam aproximadamente um e se a escolha não perdeu para outra opção. Timeout, resposta inválida ou probabilidade insuficiente retornam `UNKNOWN`. O campo operacional `IntentPrediction.confidence` recebe a probabilidade da opção escolhida, não o `confidence` de concentração da API. Há também um guard determinístico de cancelamento explícito, mas ele fica desligado por padrão para preservar o resultado bruto do benchmark. Não vou vender esse guard como resultado já medido no holdout.

[Slide 34.] Na rodada pareada de sessenta falas sintéticas, Jev acertou 54 e o local 48. Macro-F1: 0,9010 versus 0,8026. O resultado descritivo favorece Jev neste corpus. A latência p95 remota foi cerca de 2,1 segundos; a local, 0,293 milissegundo no host do teste. As sessenta chamadas Jev custaram cerca de US$ 0,00147. São números do harness, não do Android no campo. Os ECEs ficaram próximos, 0,0787 para Jev e 0,0810 para local, mas sessenta falas e uma rodada não provam calibração geral. A fixture registrou 69 a 71 `output_tokens` por chamada; o anúncio comercial é preço zero para essa parte, não uso zero.

[Slide 35.] A média não encerra a decisão. Entre os sessenta casos, Jev transformou uma fala cujo esperado era `CANCEL` em `CONFIRM`, com probabilidade 0,75 para essa escolha. O local teve três aceites inseguros; Jev teve um. Mesmo um só é relevante quando uma confirmação pode liberar movimento. A decisão documentada foi `HOLD`: não promover Jev a autoridade operacional. O estudo faz sentido porque mostrou um ganho médio e, ao mesmo tempo, um erro que impede adoção segura. A próxima pesquisa precisa de ASR real, replicação independente, estratos de segurança e avaliação do guard sem contaminar o holdout.”

## 43:00–45:00 — Demonstração e fechamento

**Se o caminho remoto estiver funcionando, falar enquanto executa:**

“Aqui está o modo de demonstração no `mockDebug`, conectado ao proxy e ao Gazebo. Vou dizer uma frase operacional de teste. Primeiro observamos a transcrição, depois a intenção com origem ‘Jev’. Neste ponto ainda não há movimento. A aplicação verifica estado e alvo e pede confirmação por áudio. Só depois de uma confirmação explícita ela constrói o `Command` JSON e o envia ao bridge. A parte que Jev fez foi classificar a intenção; o resto foi validado e executado pelo Maestro. Esta é uma execução no simulador, não no campo.”

**Se houver um vídeo previamente gravado e conferido, substituir a fala anterior por:**

“A conexão não está estável, então vou mostrar uma gravação da mesma jornada. Esta é uma gravação do Android e do Gazebo, não uma execução ao vivo. Observem a origem da intenção, a espera pela confirmação e o momento em que o comando estruturado é enviado. Jev classifica a fala; o Maestro decide se ela pode virar ação.”

**Se não houver execução nem vídeo, usar as três capturas offline e falar:**

“A reserva que temos é visual. Estas três telas foram capturadas com Wi-Fi desligado. A primeira mostra o baseline local; a segunda, uma fixture de interface com `SPRAY` e origem Jev; a terceira, `UNKNOWN` e nenhum comando enviado. Leiam a legenda comigo: **‘fixture mock local — não executa o robô’**. Elas demonstram a apresentação da decisão e da recusa para o operador. Não demonstram chamada Jev remota, reconhecimento de fala ou movimento no Gazebo.”

**Slide 38, fechamento após qualquer uma das três opções:**

“O que levo deste estudo é uma separação de responsabilidades. Jev torna concreta uma interface interessante: pergunta fechada, escolha tipada e distribuição de probabilidades, sem gerar uma resposta longa em texto. RLCD é a proposta de treinamento da TypeSafe para melhorar a qualidade dessas decisões e probabilidades, mas sua receita pública não permite atribuir causalmente os resultados ao método. No nosso corpus, Jev melhorou a média e errou uma recusa crítica. Por isso não o adotei como autoridade operacional. O Maestro continua dependendo de alvo, regras, confirmação e testes próprios. Para mim, o próximo passo é medir melhor, não declarar vitória.”

**Se sobrar tempo, acrescentar em uma frase:** “O Maestro também executou no Gazebo uma missão de várias etapas, com parser local e confirmação por ação física; Jev não criou nem executou esse plano.”

## 45:00–50:00 — Abrir a discussão

“Queria deixar quatro perguntas para o grupo, e vocês podem escolher por qual começamos. Primeira: que descrição de recompensa e que ablações vocês exigiriam para avaliar a alegação específica de RLCD? Segunda: como montar um holdout com ASR real, medindo falso aceite e calibração sem expor transcrições pessoais? Terceira: numa decisão frequente, que custo total conta mais: tokens cobrados, rede, p95, energia ou custo do erro? Quarta: qual evidência faria vocês manterem `HOLD`, mesmo se o macro-F1 continuasse subindo?

Eu trouxe um caso em que a média melhorou e a decisão de adoção continuou negativa. Acho que é exatamente essa tensão que vale discutir num grupo de RL.”

[Depois das perguntas, slide 40.] “Obrigado. Se quiserem, abro o contrato da `Choice`, o código do classificador ou a matriz de erros para discutir uma decisão específica.”

**Se perguntarem “por que não escrever só um `if`?”, responder:** “Se regras escritas à mão resolverem as variações reais, eu prefiro as regras. O experimento mede se um classificador probabilístico melhora cobertura sem aumentar o risco. Ainda não demonstramos isso o suficiente para controle operacional.”

**Se perguntarem “Jev não alucina?”, responder:** “O catálogo fechado limita formato e opções. Não impede que o modelo escolha a opção errada com confiança alta. O `CANCEL → CONFIRM` do nosso teste é um exemplo.”

**Se perguntarem “então RLCD funciona?”, responder:** “Podemos testar a alegação de calibração em tarefas concretas. Nosso conjunto sintético e uma rodada não identificam o efeito causal do algoritmo de treinamento nem provam calibração fora desse conjunto.”

## Fontes para conferência — não ler em voz alta

- [Contrato, primitivas, Playground e exemplo de API da TypeSafe](https://docs.typesafe.ai/introduction/quickstart); [explicação pública de RLCD](https://docs.typesafe.ai/introduction/machine-learning-primer); [anúncio técnico e ressalvas dos benchmarks](https://typesafe.ai/blog/introducing-system-one-models-and-jev).
- [Choice na documentação oficial](https://docs.typesafe.ai/primitives/choice); [vídeo de emojis do Stefan](https://x.com/heystefan_/status/2101369117496521042); [seleção de skills do Daniel](https://x.com/dani_avila7/status/2101885477158547753); [PR Judge](https://jevtypesafeai.com/tools/pr-judge); [JevPilot](https://x.com/jpschroeder/status/2100347770867458384); [avaliação dos casos externos](external-case-assessment.md).
- [Roteiro canônico e links de todos os casos externos](presentation-script.md).
- [Comparação medida JEV-41R](results/jev-final-recovery-presentation.md), [fixture de uso de tokens](results/jev-final-recovery-fixture.json), [decisão `HOLD`](../../tasks/jev-experimental-decision.md).
- [Fluxo de dados](../../privacy-data-flow.md), [gate remoto e CPF sintético](../../tasks/jev-remote-privacy-gate.md), [missão composta](../../tasks/mission-preview-contract.md), [demo offline](../../tasks/jev-offline-reserve-demo.md).
