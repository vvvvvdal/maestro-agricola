# Texto integral para falar — Jev, RLCD e Maestro Agrícola

Base: [roteiro canônico](presentation-script.md). Meta: **45 minutos de apresentação e 5 de discussão**. As frases abaixo são uma proposta de fala, não evidência adicional. Os trechos entre **[colchetes]** são ações ou escolhas do apresentador e **não são lidos**. Cronometrar em voz alta: os tempos incluem pausas, leitura de resultados e navegação no Playground.

Antes de começar, deixar o Playground autenticado e o exemplo sem dados pessoais preparado. O deck HTML ainda tem a ordem e a nota sobre tokens anteriores à revisão do roteiro; seguir **este texto** na fala e corrigir oralmente a nota quando necessário. Não projetar credenciais nem dashboard de cobrança.

## 0:00–4:00 — O que é Jev e por que um “if com IA”

“Vou começar com um problema comum de software, fora do nosso projeto. Chega um chamado de cliente: a integração de pagamentos falha há três dias, a pessoa está perdendo vendas e pede ajuda hoje. O programa precisa decidir para onde mandar esse chamado. Suporte técnico? Financeiro? Comercial? Ou revisão humana?

Eu poderia enviar a mensagem a um modelo de linguagem e pedir uma resposta em texto: ‘analise o caso, explique seu raciocínio e diga qual equipe deve receber’. Mas, se a próxima etapa do software só precisa de uma categoria, eu passo a gerar uma resposta longa para depois extrair uma palavra dela. Essa é a situação em que Jev tenta ser útil.

Jev é o primeiro modelo público de uma empresa chamada TypeSafe. A proposta é receber um estado, receber uma ou mais perguntas com saídas definidas e retornar decisões tipadas, acompanhadas de probabilidades. No nosso chamado, o estado é a mensagem da pessoa. A pergunta é qual equipe deve recebê-la. As saídas possíveis são as equipes que eu defini antes da chamada.

Quando digo ‘tipada’, não quero dizer correta. Quero dizer que a forma da resposta está limitada por um contrato. A aplicação sabe que a resposta deve ser uma escolha daquele catálogo. Ela também recebe uma distribuição: quanto da probabilidade ficou em suporte técnico, quanto em financeiro e assim por diante. Isso permite que o software tenha uma política para casos incertos.

Uma forma de pensar nisso é: chamado, escolha probabilística, regra da aplicação, fila. O modelo faz a escolha; o código continua responsável pela regra e pela consequência. Por exemplo: eu posso encaminhar automaticamente só acima de certo limiar, pedir revisão humana abaixo dele e recusar uma resposta inválida. Esse limiar não sai magicamente do modelo. A equipe precisa defini-lo e testá-lo.

Vocês talvez tenham visto a frase ‘Jev é um if com IA’. Gosto dela como metáfora rápida, com cuidado. Um `if` tradicional testa uma condição que nós escrevemos: se o valor for maior que tal número, faz tal coisa. Jev estima qual alternativa parece adequada diante de um estado menos organizado, como uma mensagem em linguagem natural. A decisão probabilística entra no lugar em que uma regra manual poderia ficar frágil. O resto do programa continua sendo programa.

Um contexto histórico de vinte segundos: o fundador da TypeSafe, Diogo Almeida, relata ter trabalhado na OpenAI em métodos ligados a modelos que seguem instruções. A página da empresa o apresenta como coinventor de RLHF e InstructGPT. É uma origem interessante para uma apresentação de RL, mas currículo não é evidência de que Jev funcione bem em todo problema. O nome ‘System One Model’ faz referência à ideia de decisão rápida do livro *Thinking, Fast and Slow*. É uma inspiração de produto; não vou tratar isso como descrição científica de cognição humana. Jev também remete a William Stanley Jevons, economista associado ao paradoxo de eficiência e aumento de uso.

Então guardem esta primeira definição: estado entra, pergunta tipada entra, decisão e probabilidades saem. Agora vamos comparar essa interface com a de um LLM comum.”

## 4:00–9:00 — Jev, LLM, primitivas e tokens

“Um LLM generativo é extremamente flexível. Ele pode conversar, escrever código, resumir, explicar e produzir texto aberto. Essa flexibilidade é ótima quando eu realmente preciso de uma resposta em linguagem. Para um passo interno de um programa, porém, a resposta aberta costuma exigir parsing e validação. Às vezes usamos JSON mode ou schema, o que ajuda muito, mas ainda precisamos pensar na tarefa, nos erros e na política depois da resposta.

Jev propõe uma interface mais estreita. A primitiva que mais nos interessa hoje se chama `Choice`. Eu forneço uma pergunta e um catálogo: técnico, financeiro, comercial, revisão humana. Jev retorna a opção escolhida e a probabilidade atribuída a cada opção. Um bom catálogo inclui uma saída para ‘nenhuma das anteriores’ ou revisão, porque o mundo real nem sempre cabe nas categorias positivas.

Existem outras duas primitivas que vale conhecer. `Noul` responde uma pergunta binária, como ‘essa mensagem expressa urgência?’. `Score` situa algo numa escala ordenada, como a intensidade de frustração. A documentação permite fazer várias perguntas sobre o mesmo estado numa chamada. Elas são avaliadas em paralelo segundo a TypeSafe. Isso pode ser útil, mas cada pergunta e cada critério também entram no payload e aumentam o tamanho da entrada.

Aqui está um dos pontos que mais me chamaram atenção: tokens de saída. Um LLM generativo normalmente produz uma sequência de tokens de texto. Se eu peço três parágrafos, há três parágrafos a gerar. Jev não escreve uma resposta aberta dessa forma. Ele entrega valores estruturados. A TypeSafe diz que amostra as decisões em paralelo e anuncia preço zero para tokens de saída. Isso pode baratear uma decisão curta e repetida.

Mas preciso separar três coisas: gerar prosa, contabilizar tokens de saída e cobrar por esses tokens. A documentação da própria TypeSafe mostra uma resposta `Choice` com 34 `output_tokens`. Portanto, não vou dizer que Jev consome zero tokens de saída. A afirmação comercial é que a **cobrança** dos tokens de saída é zero. O serviço ainda recebe tokens de entrada, usa rede e tem custo por chamada. Mais tarde vou mostrar o que apareceu no nosso experimento.

Também não quero repetir números de marketing como se fossem uma constante da natureza. Existem demonstrações que falam de centenas de vezes menos custo ou latência. A própria TypeSafe avisa que os ganhos publicados nos workflows dela provavelmente estão na ponta alta dos ganhos reais. Uma comparação justa teria a mesma tarefa, entrada equivalente, qualidade da decisão, custo total e latência ponta a ponta. Comparar uma frase curta com um LLM escrevendo uma dissertação responderia a outra pergunta.

Mais uma distinção técnica antes do exemplo. Em `Choice`, a resposta traz um mapa chamado `probabilities`. Ele diz a probabilidade de cada alternativa. Há também um campo chamado `confidence`, calculado a partir de quão concentrada está a distribuição. Se uma opção tem quase toda a massa, a distribuição é concentrada. Se a massa está espalhada, ela é difusa. A probabilidade da opção vencedora e o campo `confidence` podem ser diferentes; vou apontar os dois se aparecerem no site. Para `Noul`, o contrato não retorna esse mesmo campo.

A pergunta de design que fica é: em que decisões discretas, frequentes e ambíguas vocês hoje fazem uma chamada generativa inteira, embora o código só precise de uma pequena bifurcação? Vamos montar uma dessas decisões no Playground.”

## 9:00–13:00 — Exemplo no Playground da TypeSafe

[Abrir o Playground já autenticado. Colar **apenas** a frase abaixo no campo `state`.]

“Vou criar uma pergunta do zero e deixar visível cada peça do contrato. O estado será uma mensagem sintética, sem informação pessoal: ‘Minha integração de pagamentos falha há três dias. Estou perdendo vendas e preciso de ajuda hoje.’ Esse é o dado que o modelo vai avaliar. Não é a instrução sobre o que fazer com ele.

[Criar pergunta com ID `departamento`, tipo `Choice`. Inserir a instrução ‘Qual equipe deve receber este chamado?’. Adicionar os critérios técnico = falha de integração, bug ou configuração; financeiro = cobrança, pagamento ou fatura; comercial = plano, preço ou contratação; revisão humana = informação insuficiente ou várias equipes igualmente plausíveis.]

“Agora estou definindo a pergunta. Chamei de `departamento`. Escolhi `Choice`, porque preciso selecionar uma opção de um conjunto finito. A instrução é ‘Qual equipe deve receber este chamado?’. Por fim, descrevo o que cada opção significa. Essa descrição importa: nomes de categorias sem fronteiras claras produzem perguntas ruins. A opção de revisão humana evita forçar tudo para uma equipe operacional.

Antes de executar: qual equipe vocês escolheriam? Eu espero que suporte técnico seja uma hipótese forte porque a frase fala de uma integração que falha. Mas ‘pagamentos’ pode puxar parte da probabilidade para financeiro. Não vou prometer um resultado fixo, porque o que vale é a resposta que aparecer agora.”

[Executar. Apontar o resultado real. Ler `choice`, duas probabilidades relevantes, `confidence` se exibido, e `usage` se exibido. Não inventar números ausentes.]

“O resultado que apareceu foi **[ler categoria exibida]**. Para essa opção, o modelo atribuiu **[ler probabilidade exibida]**. Também vemos **[ler outra alternativa e probabilidade, se disponível]**. O campo `confidence`, quando está aqui, resume a concentração da distribuição; não é automaticamente a probabilidade da opção escolhida.

Agora vem o passo mais importante: o modelo não encaminhou o chamado. Ele devolveu dados. Eu ainda escreveria uma regra como ‘se a probabilidade da equipe vencedora for suficiente e o risco for baixo, encaminhar; caso contrário, pedir revisão’. Qual limiar usar é uma decisão de produto que precisa ser medida. E uma integração real validaria a resposta, trataria timeout e registraria qual versão do modelo respondeu.

Se eu quisesse fazer a mesma coisa em código, o corpo da requisição teria três partes: `state`, `model` e `questions`. Dentro de `questions` estaria `departamento`, com `type: choice`, `instructions` e `criteria`. A API expõe `POST /v1/systemone`; o SDK tem uma chamada equivalente, `client.system_one(...)`. Eu leria `answers["departamento"].choice` e as probabilidades, e aplicaria minha política no programa. Para uma demonstração, `jev-latest` é conveniente; num experimento reprodutível, eu fixaria e registraria a versão.

Se houvesse mais tempo, eu perguntaria no mesmo estado se há urgência usando `Noul`, e pontuaria frustração com `Score`. O importante é que são perguntas diferentes, cada uma com saída definida antes de executar. Agora que vimos a interface por fora, vamos ao motivo de essa ferramenta aparecer numa conversa sobre reinforcement learning.”

**Se o site não carregar, substituir apenas a execução por esta fala:** “O Playground não respondeu agora. Vou usar o request e a resposta de exemplo publicados no quick start da TypeSafe para mostrar os mesmos campos. Isso demonstra o contrato da API, não uma inferência feita ao vivo.”

## 13:00–25:00 — RL, RLHF, RLVR, RLCD e calibração

### 13:00–16:00 — RL básico

“Antes de falar de RLCD, vale colocar os nomes na mesma mesa sem fingir que são a mesma técnica. No exemplo clássico de reinforcement learning, um agente observa um estado, escolhe uma ação segundo uma política, recebe uma recompensa e encontra um novo estado. Escrevemos isso como estado `s`, ação `a`, recompensa `r`, próximo estado `s'`. A política, que posso escrever como pi de a dado s, é o que o treinamento ajusta para aumentar o retorno esperado.

Imaginem um jogo simples. Em cada posição, o agente escolhe mover para a esquerda ou para a direita. A recompensa pode vir só ao alcançar o objetivo ou ao evitar uma colisão. O agente não recebe uma lista de frases bonitas para escrever; ele recebe um sinal que favorece certos comportamentos ao longo do tempo. O que exatamente é recompensado muda o que a política aprende.

Esse último ponto é a ponte para o restante. ‘Usa RL’ ainda diz pouco. Preciso perguntar: qual é a saída? De onde vem o sinal de qualidade? Ele mede preferência humana, resposta verificável ou qualidade da incerteza? Como o sinal é obtido? E como sabemos que a melhoria veio do treino, e não de uma mudança de arquitetura, do sampler ou da forma de perguntar?

Vou passar por três nomes que aparecem nesta discussão: RLHF, RLVR e RLCD. Não são estágios obrigatórios de uma única receita. Eles destacam objetivos de treino diferentes.”

### 16:00–20:00 — RLHF e RLVR

“RLHF quer dizer reinforcement learning from human feedback. No roteiro clássico, pessoas comparam respostas ou indicam preferências. Essas comparações alimentam um modelo de recompensa, ou algum sinal equivalente, e a política é ajustada para favorecer respostas que esse sinal avalia melhor. Existem variantes; não estou dizendo que todo sistema chamado RLHF implementa o mesmo algoritmo.

Por que isso foi tão importante para modelos de conversa? Porque uma resposta pode ser tecnicamente possível e ainda ser pouco útil para quem perguntou. Preferências humanas ajudam a selecionar o tipo de resposta que as pessoas querem receber. Só que existe uma distinção crucial para hoje: uma resposta preferida não é necessariamente uma estimativa de probabilidade bem calibrada. Se peço a um modelo uma decisão e ele diz ‘tenho 90% de certeza’, posso gostar da explicação, mas ainda preciso medir se esse 90% se comporta como 90% em muitos casos.

RLVR significa reinforcement learning with verifiable rewards. Aqui temos tarefas nas quais parte da qualidade pode ser checada por um verificador relativamente objetivo: um resultado matemático, um teste de código, uma condição formal. A recompensa pode vir dessa checagem, sem precisar perguntar a uma pessoa se gostou de cada resposta. Isso abre espaço para melhorar raciocínio em tarefas verificáveis.

Mas observem o limite. Eu posso treinar um sistema para acertar mais respostas verificadas e ainda não saber se as probabilidades que ele comunica são boas. Acerto e calibração estão relacionados, mas não são a mesma variável. Se um modelo acerta nove em dez questões, isso não significa automaticamente que ele sabe identificar quais são as dez em que vai errar.

Uma forma curta de resumir: RLHF se apoia em preferência humana; RLVR, em verificação de respostas; a TypeSafe apresenta RLCD como um objetivo voltado a decisões com probabilidades calibradas. Não estou dizendo que as duas primeiras abordagens jamais possam produzir calibração, nem que a terceira tenha exclusividade sobre isso. Estou dizendo qual é o alvo que a empresa escolheu comunicar e que precisamos testar.”

### 20:00–23:00 — O que a TypeSafe chama de RLCD

“RLCD é o nome *Reinforcement Learning for Calibrated Decisions*. Segundo a TypeSafe, Jev foi treinado para responder perguntas tipadas com distribuições de probabilidade úteis para software. A promessa de calibração é simples de enunciar e difícil de cumprir bem. Se, em muitos exemplos comparáveis, o modelo atribui probabilidade 0,8 às suas escolhas, esperamos que aproximadamente 80% delas estejam corretas. Se ele atribui 0,2, esperamos algo perto de 20% para aquele evento. Isso não quer dizer que uma resposta individual de 0,8 está protegida contra erro.

Por que essa promessa interessa? Porque software pode usar incerteza para decidir quando agir, quando pedir confirmação ou quando encaminhar para uma pessoa. Mas há um salto entre ‘o modelo me deu um número’ e ‘esse número é confiável no meu domínio’. O número só ganha sentido com avaliação em dados representativos.

Aqui eu quero ser rigoroso com vocês. Consigo explicar o objetivo público de RLCD. Não consigo reconstruir o treinamento a partir do material publicado. Não temos detalhe suficiente sobre a função de recompensa, dados, algoritmo, arquitetura e ablações para isolar quanto do resultado vem de RLCD, quanto vem da interface de saída e quanto vem do sampler. Se eu dissesse que a empresa usa Brier, ECE ou uma regra própria como recompensa, estaria inventando. Essas são formas que podemos usar para avaliar probabilidades; não conhecemos a receita interna em detalhe.

Portanto, a parte científica da conversa não é repetir o nome do método. É transformar a promessa em perguntas verificáveis. Primeiro: o modelo acerta? Segundo: a confiança acompanha a frequência de acerto? Terceiro: em que tipos de erro ele falha? Quarto: qual é o custo de um erro para o sistema em que eu o coloco?”

### 23:00–25:00 — Como testar a promessa

“Acurácia responde quantas escolhas tiveram o rótulo certo. Calibração responde outra pergunta: quando o modelo atribui uma probabilidade, essa probabilidade corresponde à frequência observada? Imaginem cem decisões agrupadas perto de 0,8. Um modelo calibrado deveria acertar perto de oitenta naquele grupo. Ele ainda erraria por volta de vinte. Isso é esperado; calibração não é infalibilidade.

Uma métrica possível é o Brier multiclasses, que penaliza probabilidades distantes do rótulo verdadeiro. Outra é o ECE, que compara confiança média e acerto médio por faixas. Um reliability diagram desenha esses grupos; a diagonal indica calibração ideal. Só que o desenho de um gráfico bonito não resolve tamanho de amostra, mudança de domínio ou erros raros. Um bin com quatro exemplos é muito menos informativo do que parece quando visto como um ponto isolado.

Se eu fosse defender adoção em um sistema real, pediria um conjunto de avaliação congelado antes de ajustar critérios, replicação em outra amostra e recortes onde o custo do erro é maior. A pergunta que deixo para o grupo é: que recompensa, que ablações e que holdout vocês exigiriam para separar uma boa história sobre RLCD de evidência de calibração? Guardem essa pergunta. Vou voltar a ela quando mostrar dados de uma aplicação concreta.”

## 25:00–30:00 — Exemplos públicos e o que cada um realmente demonstra

“Agora que o contrato está claro, as demonstrações ficam mais fáceis de ler. Em cada uma, vou perguntar três coisas: que estado entrou, quais opções o modelo podia escolher e o que o restante do software fez. Esses casos são de terceiros. Não são a nossa medição e não vou tratá-los como benchmark independente.

No projeto de compaction de Tamara Tran, o problema é um histórico longo de um agente de programação. Em vez de pedir a um LLM que reescreva todo o histórico num resumo, a ideia é pontuar chamadas e resultados de ferramentas: isto deve ficar, ser truncado ou sair? Jev participa dessa decisão; o código executa a edição do contexto. A economia de tokens seguintes é interessante, mas a métrica de qualidade não pode ser só tamanho. Se você descarta justamente o erro de teste que explica o bug, o contexto ficou menor e pior. O projeto prevê fallback para resumo. Então a pergunta experimental seria: quantos tokens foram economizados **sem perder** restrições, caminhos e evidências que a tarefa ainda exigia?

Outro caso é seleção de skills. Antes de carregar um bloco grande de instruções, o software pergunta qual skill pode ser relevante para a tarefa atual. É uma decisão pequena colocada antes de uma etapa cara. O catálogo deve admitir ‘nenhuma’. E existe um custo de falso descarte: se a skill certa não for carregada, o agente posterior pode trabalhar com contexto insuficiente. Eu avaliaria esse erro, não apenas a rapidez da primeira decisão.

Há também uma demonstração chamada JevPilot, que ficou conhecida por uma frase chamativa sobre recriar direção autônoma. O experimento apresentado é num ambiente simulado, o HighwayEnv, com estado e ações definidos pelo código. O autor reporta um período sem colisão nesse cenário. Isso mostra como uma escolha tipada pode entrar num loop de simulação; não mostra direção validada em carro real, nem câmera real. A moldura do harness é parte do resultado.

Uma demo de triagem de pull request faz algo semelhante em outro domínio: com um diff limitado, pergunta se o primeiro encaminhamento deve ser algo como seguro, revisar ou bloquear. A própria demo informa que não lê o repositório inteiro nem executa testes. Assim, uma classificação rápida pode ser útil para priorizar revisão; não substitui revisão humana ou pipeline de testes. Seus números de latência e preço são alegações daquela página, não uma lei geral sobre todo PR.

O caso mais divertido para esta sala é xadrez. Num relato público, Jev enfrentou Fable 5.1 em blitz de cinco minutos, uma chamada de API por lance, sem busca. Jev venceu **no tempo**. O detalhe é que Fable tinha grande vantagem material e uma segunda dama. Portanto, eu não diria que Jev era mais forte em xadrez. Eu diria que, sob aquele limite de tempo e aquela regra de uma chamada, ele tomou decisões rapidamente. Contra Astra, houve mate em dezoito lances, com tempo sobrando no relógio de Astra. Xadrez exige cálculo e busca. A partida mostra onde a rapidez de uma decisão curta deixa de compensar a falta de raciocínio mais longo.

Existe ainda um vídeo criativo do Stefan usando Jev numa interface. Só vou comentá-lo se eu conseguir conferir o vídeo original antes do ensaio. Caso use, vou identificar qual é a decisão do modelo e qual é a renderização e a lógica feita pelo programa. Esse cuidado vale para todas as demos: a capacidade do sistema inteiro não deve ser atribuída automaticamente ao modelo.”

## 30:00–33:00 — Limites de Jev e o aparecimento de Laya

“Então, Jev é rápido, mas pode parecer burro às vezes? Eu formularia com mais precisão: ele foi desenhado para uma decisão curta, não para desenvolver uma linha longa de raciocínio em texto. Tipagem impede uma classe de erro de formato; não garante a escolha correta. E uma distribuição com uma opção dominante ainda pode estar errada. Para avaliar qualquer aplicação, o risco desse erro precisa entrar na conta.

Pouco depois do lançamento do Jev, apareceu Laya como proposta aberta para decisões tipadas. O projeto `laya-mlx` porta pesos para execução local em Apple Silicon. O repositório reporta medianas de 7,39 a 13,42 milissegundos para **uma pergunta curta** num M3 Max, sem incluir o carregamento do modelo. Isso é um resultado do próprio projeto em hardware específico. A demo de Snake usa três perguntas por ciclo e também uma camada de segurança no software. Não é correto colocar o número de uma pergunta curta ao lado do tempo de um loop inteiro e anunciar que um produto venceu o outro.

Por que mencionar Laya? Porque, se a contribuição mais interessante aqui é uma interface de decisão, faz sentido perguntar se outras implementações conseguem atender ao mesmo contrato. Um serviço remoto e pesos locais têm consequências diferentes para latência, operação e circulação de dados. A comparação que eu gostaria de ver seria pareada: mesmo problema, catálogo, corpus, hardware de destino, política de falha e métricas de qualidade. Eu não tenho essa comparação. Também não vou afirmar que Laya roda bem em qualquer aparelho só porque o port para Mac foi rápido.

Essa é uma boa hora para fechar a parte geral. O que sabemos de Jev? Ele oferece decisões tipadas com probabilidades; evita gerar prosa aberta para uma escolha pequena; a TypeSafe anuncia saída sem cobrança por token; e chama seu objetivo de treino de RLCD. O que ainda precisa de teste? A qualidade das escolhas, a calibração no domínio específico, latência real da aplicação e os erros que mais custam. Agora vou mostrar um domínio em que essas perguntas importam para nós.”

## 33:00–36:00 — O Maestro Agrícola

“Até aqui falei apenas da ferramenta e dos exemplos públicos. Agora apresento o Maestro Agrícola em três minutos, para então avaliar se Jev acrescenta algo ao nosso sistema.

O Maestro é uma interface hands-free para comandar um robô agrícola. A ideia é permitir que um operador peça uma ação por voz, identifique um talhão por um marcador visual ou por um cadastro conhecido, ouça a confirmação e só então envie um comando estruturado ao robô. A demonstração que temos usa Android e Gazebo, com um bridge ROS 2 no caminho. Não é comprovação de aplicação física de defensivo no campo.

O fluxo essencial é este: fala, decisão de intenção, regras e estado determinísticos, confirmação por áudio, `Command` JSON versionado, bridge ROS e robô no simulador. A câmera é outro caminho de entrada: uma foto sob demanda é processada localmente para ler um QR ou marcador e produzir um `target_id`. O frame não vira um comando. O alvo resolvido entra na validação que acontece depois da classificação da fala.

Agora que vocês sabem o que o projeto faz, faz sentido mostrar seu catálogo. O classificador operacional trabalha com seis rótulos: `SPRAY`, para pedir pulverização; `DOCK`, para voltar à doca; `UNDOCK`, para sair dela; `CONFIRM`; `CANCEL`; e `UNKNOWN`, quando a fala não autoriza uma dessas ações. Estes são **rótulos da intenção**, não ações físicas disparadas automaticamente. A máquina de estados ainda precisa verificar se a ação é permitida, se o alvo é conhecido e se houve confirmação. `SPRAY` não faz o robô sair ou voltar à doca implicitamente; `DOCK` e `UNDOCK` são comandos explícitos.

Uma distinção rápida sobre visão: dizer ‘o app só lê QR’ seria impreciso. Ele precisa receber uma foto sob demanda e processá-la em memória até obter o identificador. Pelo código e pelo fluxo documentado, o Maestro não grava foto, áudio ou transcrição por padrão. O caminho com óculos Meta reais ainda depende de validação física; o que mostro hoje se apoia em mock e simulação.

Com isso, vocês já têm contexto para a pergunta central: se o Jev escolhe categorias, por que não colocá-lo na etapa de intenção?”

## 36:00–42:00 — Jev dentro do Maestro: fronteiras, medição e dados

### 36:00–38:00 — O papel exato do Jev

“No experimento, Jev substitui **uma implementação do classificador**. A execução usa o classificador local **ou** o `JevIntentClassifier` para os mesmos seis rótulos. Não há dois modelos votando na mesma fala. Jev recebe uma transcrição curta no modo remoto de teste, não recebe foto, áudio bruto, pose, alvo visual, estado interno do robô, WebSocket, ROS ou objeto `Command`.

Pensem num caso de conflito. A câmera identificou `plot-03`. A pessoa fala ‘pulverize o talhão um’. Jev pode acertar perfeitamente o rótulo `SPRAY`. Ainda assim, o resolvedor determinístico encontra alvo visual diferente do alvo falado. O resultado é ambíguo, sem comando. A probabilidade de `SPRAY` não substitui a validação do alvo.

Outro detalhe: `UNKNOWN` continua num caminho separado, que pode chegar ao assistente local Qwen para conversa de domínio. Qwen só produz `CHAT` ou `OUT_OF_SCOPE`; não cria comando. Jev não foi colocado para filtrar Qwen, inventar alvos ou gerar um plano de missão. Isso mantém a pergunta experimental pequena: Jev classifica essas seis intenções melhor que o baseline local, com latência e erros aceitáveis?”

### 38:00–40:00 — Resultado da comparação

“Fizemos uma rodada pareada com sessenta falas sintéticas. O Jev remoto acertou cinquenta e quatro de sessenta; o classificador local, quarenta e oito de sessenta. O macro-F1 foi 0,9010 para Jev e 0,8026 para o local. Até aqui, o resultado descritivo favorece Jev.

Só que uma média não é o critério suficiente para essa aplicação. O baseline local teve três aceitações inseguras no corpus; Jev teve uma. Essa única falha é concreta: uma fala cujo rótulo esperado era `CANCEL` foi classificada como `CONFIRM`, com probabilidade 0,75 para a escolha. Em um fluxo com ação física, esse tipo de confusão pesa mais que alguns acertos adicionais em casos fáceis. As outras barreiras do sistema continuam necessárias, e a decisão sobre promover Jev permaneceu `HOLD`.

Também medi latência e custo do harness. O p95 do Jev remoto foi cerca de 2,1 segundos; o local, 0,293 milissegundo nesse host. As sessenta chamadas remotas custaram cerca de 0,00147 dólar. Esses números descrevem o ambiente do teste: não são a latência de áudio num Android no campo, nem a latência do robô. E aqui volto ao tema dos tokens: a fixture registrou de 69 a 71 `output_tokens` por chamada. A saída não foi zero em uso contabilizado, embora a TypeSafe anuncie preço zero para essa parte.

No gráfico de calibração, os ECEs por classe vencedora ficaram próximos: 0,0787 no Jev e 0,0810 no local. Os pontos têm poucos exemplos por faixa, pois são apenas sessenta falas sintéticas em uma rodada. Isso não demonstra calibração generalizável. Se vocês olharem os números de `n` nos bins, a ressalva fica visível. Gostaria de repetir essa avaliação com ASR real, negação, hesitação, conflitos de alvo e amostras independentes, mas essa evidência ainda não existe para justificar adoção.”

### 40:00–41:00 — Ele é útil ou apenas uma vitrine?

“Então, Jev faz sentido no Maestro ou é só uma vitrine de ferramenta nova? Minha resposta é: faz sentido como **hipótese de pesquisa** para rotear falas variadas num catálogo fechado. Poderia poupar parte do trabalho de escrever regras linguísticas para reconhecer novas categorias. O resultado que medimos sugere ganho médio neste corpus. Ainda não demonstramos ganho operacional seguro.

Criar uma função nova no Maestro continua exigindo contrato, política de estado, permissões, tratamento de falha, confirmação quando necessária, corpus novo e teste. Jev não cria essas peças. Aliás, consultas de histórico, inspeção de alvo e uma missão composta já foram implementadas localmente e são úteis mesmo sem Jev. Essa distinção me ajuda a avaliar a tecnologia: primeiro defino o valor do produto e sua fronteira de segurança; depois pergunto se o novo classificador melhora uma etapa específica.”

### 41:00–42:00 — Privacidade do caminho remoto

“Há também a questão dos dados. No caminho padrão, a transcrição curta fica em memória e segue para o classificador local. O classificador local **não** é um detector geral de CPF ou de todo dado pessoal. No modo remoto demonstrativo, restrito a `mockDebug`, o operador precisa ativar a sessão depois de um aviso. Antes da rede, o app e o proxy bloqueiam padrões evidentes: CPF ou CNPJ, e-mail, telefone, URL, texto longo ou fora do escopo. A fala bloqueada não vai para Jev, Qwen nem `Command`; não é reutilizada automaticamente no modo local.

Testamos isso no tablet com uma frase que continha **CPF sintético**. A mensagem foi ‘Fala não enviada ao Jev’. Essa barreira é minimização preventiva. Ela não detecta toda informação pessoal e não é anonimização nem declaração de conformidade integral com a LGPD. Android e o provedor de reconhecimento de fala, o SDK dos óculos e o serviço externo também têm fronteiras próprias de tratamento. Por isso não vou condensar tudo na frase ‘não guardamos nada’.”

## 42:00–45:00 — Demonstração e fechamento

**Se o caminho remoto estiver funcionando, falar enquanto executa:**

“Aqui está o modo de demonstração no `mockDebug`, conectado ao proxy e ao Gazebo. Vou dizer uma frase operacional de teste. Primeiro observamos a transcrição, depois a intenção com origem ‘Jev’. Neste ponto ainda não há movimento. A aplicação verifica estado e alvo e pede confirmação por áudio. Só depois de uma confirmação explícita ela constrói o `Command` JSON e o envia ao bridge. A parte que Jev fez foi classificar a intenção; o resto foi validado e executado pelo Maestro. Esta é uma execução no simulador, não no campo.”

**Se houver um vídeo previamente gravado e conferido, substituir a fala anterior por:**

“A conexão não está estável, então vou mostrar uma gravação da mesma jornada. Esta é uma gravação do Android e do Gazebo, não uma execução ao vivo. Observem a origem da intenção, a espera pela confirmação e o momento em que o comando estruturado é enviado. Jev classifica a fala; o Maestro decide se ela pode virar ação.”

**Se não houver execução nem vídeo, usar as três capturas offline e falar:**

“A reserva que temos é visual. Estas três telas foram capturadas com Wi-Fi desligado. A primeira mostra o baseline local; a segunda, uma fixture de interface com `SPRAY` e origem Jev; a terceira, `UNKNOWN` e nenhum comando enviado. Leiam a legenda comigo: **‘fixture mock local — não executa o robô’**. Elas demonstram a apresentação da decisão e da recusa para o operador. Não demonstram chamada Jev remota, reconhecimento de fala ou movimento no Gazebo.”

**Fechamento, após qualquer uma das três opções:**

“O que levo deste estudo é uma separação de responsabilidades. Jev torna concreta uma interface interessante: pergunta fechada, escolha tipada e distribuição de probabilidades, sem gerar uma resposta longa em texto. RLCD é a proposta de treinamento da TypeSafe para melhorar a qualidade dessas decisões e probabilidades, mas sua receita pública não permite atribuir causalmente os resultados ao método. No nosso corpus, Jev melhorou a média e errou uma recusa crítica. Por isso não o adotei como autoridade operacional. O Maestro continua dependendo de alvo, regras, confirmação e testes próprios. Para mim, o próximo passo é medir melhor, não declarar vitória.”

**Se sobrar tempo, acrescentar em uma frase:** “O Maestro também executou no Gazebo uma missão de várias etapas, com parser local e confirmação por ação física; Jev não criou nem executou esse plano.”

## 45:00–50:00 — Abrir a discussão

“Queria deixar quatro perguntas para o grupo, e vocês podem escolher por qual começamos. Primeira: que descrição de recompensa e que ablações vocês exigiriam para avaliar a alegação específica de RLCD? Segunda: como montar um holdout com ASR real, medindo falso aceite e calibração sem expor transcrições pessoais? Terceira: numa decisão frequente, que custo total conta mais: tokens cobrados, rede, p95, energia ou custo do erro? Quarta: qual evidência faria vocês manterem `HOLD`, mesmo se o macro-F1 continuasse subindo?

Eu trouxe um caso em que a média melhorou e a decisão de adoção continuou negativa. Acho que é exatamente essa tensão que vale discutir num grupo de RL.”

**Se perguntarem “por que não escrever só um `if`?”, responder:** “Se regras escritas à mão resolverem as variações reais, eu prefiro as regras. O experimento mede se um classificador probabilístico melhora cobertura sem aumentar o risco. Ainda não demonstramos isso o suficiente para controle operacional.”

**Se perguntarem “Jev não alucina?”, responder:** “O catálogo fechado limita formato e opções. Não impede que o modelo escolha a opção errada com confiança alta. O `CANCEL → CONFIRM` do nosso teste é um exemplo.”

**Se perguntarem “então RLCD funciona?”, responder:** “Podemos testar a alegação de calibração em tarefas concretas. Nosso conjunto sintético e uma rodada não identificam o efeito causal do algoritmo de treinamento nem provam calibração fora desse conjunto.”

## Fontes para conferência — não ler em voz alta

- [Contrato, primitivas, Playground e exemplo de API da TypeSafe](https://docs.typesafe.ai/introduction/quickstart); [explicação pública de RLCD](https://docs.typesafe.ai/introduction/machine-learning-primer); [anúncio técnico e ressalvas dos benchmarks](https://typesafe.ai/blog/introducing-system-one-models-and-jev).
- [Roteiro canônico e links de todos os casos externos](presentation-script.md).
- [Comparação medida JEV-41R](results/jev-final-recovery-presentation.md), [fixture de uso de tokens](results/jev-final-recovery-fixture.json), [decisão `HOLD`](../../tasks/jev-experimental-decision.md).
- [Fluxo de dados](../../privacy-data-flow.md), [gate remoto e CPF sintético](../../tasks/jev-remote-privacy-gate.md), [demo offline](../../tasks/jev-offline-reserve-demo.md).
