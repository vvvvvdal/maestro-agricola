# Guia de estudo, slide por slide — Jev e Maestro

Este guia acompanha a [versão v8 do deck](jev-rl-maestro-v8-2026-10-01.pptx), o [roteiro](presentation-script.md) e as [falas integrais](presentation-speech.md). **Estudar não significa ler tudo no palco.** As respostas abaixo são cartões de treino oral. Responda com suas palavras antes de conferir.

## Diagnóstico honesto e percurso de 50 minutos

O conteúdo é adequado a um grupo de RL **se** você separar fatos públicos, alegações dos autores e medições do Maestro. O ponto forte da apresentação é não confundir uma interface probabilística com prova de calibração: ela chega ao erro `CANCEL → CONFIRM` e explica a decisão `HOLD`. O ponto em que o grupo mais pode apertar é RLCD: a receita de treino do Jev não está publicada em detalhe suficiente para reprodução ou atribuição causal. Diga isso sem hesitar. A nova sequência é mais clara: conceito → contrato → RL/RLCD → demos → por que apareceu a onda → modelos individuais → comparação → notas do Diogo → Maestro → resultado.

**O speech integral não cabe em 50 minutos.** Antes das fontes, tem cerca de 8,5 mil palavras; só lê-lo a 130 palavras/minuto levaria cerca de 65 minutos, sem vídeos ou demo. Use-o para estudar. Para o palco, mire **45 minutos de exposição + 5 de perguntas**, com esta trilha. Ela é um plano de cortes, ainda não um tempo validado em ensaio:

| Minutos | Slides | O que preservar | Como caber |
| --- | --- | --- | --- |
| 0–7 | 1–9 | definição, System One, bot, três tipos | 1 frase principal por slide; `if` em 20 s |
| 7–11 | 10–16 | tokens, LLM × Jev, Playground | 1 execução ou exemplo salvo; até 90 s de site |
| 11–24 | 17–25 | RL → RLHF → RLVR → RLCD; calibração | maior bloco; gastar 4–5 min só em RLCD |
| 24–27 | 26–30 | cinco casos, especialmente emojis | vídeo de 10–15 s por caso, sem reproduzir inteiro |
| 27–33 | 31–36 | onda, Laya, Julia-1, CLM, tabela | comparação após os três projetos; números só com contexto |
| 33–36 | 37–40 | notas do Diogo e loop | explicar ideia em 3 min; detalhes de KV cache ficam para perguntas |
| 36–43 | 41–53 | Maestro, código, corpus e `HOLD` | mostrar `CRITERIA` sem ler as seis descrições em inglês |
| 43–45 | 54–58 | demo, conclusão, perguntas | 1 vídeo curto ou gravação; slide 55 como reserva; 57 abre Q&A |
| 45–50 | perguntas | erro crítico e evidência necessária | slide 58 é o encerramento visual |

**Regra de ensaio:** grave uma passada cronometrada. Se chegar ao slide 31 depois de 29 minutos, use só uma frase em cada slide de agentes (37–40). Se chegar ao slide 41 depois de 37 minutos, passe pelos slides 47–49 apontando o papel de `CRITERIA` e `request_payload`, sem ler linha por linha. Não corte os slides 20–25 nem 52–53: eles sustentam a tese de RL e o limite do experimento. Vídeos completos, números secundários e perguntas difíceis ficam para a discussão.

## Slide 1 — Título

**Entenda:** O tema é Jev como ferramenta de decisão tipada, RLCD como alegação de treinamento e Maestro como teste de aplicação. O título não promete demonstrar uma nova técnica de RL. **Dica:** anuncie essa rota em uma frase e vá à definição.

**Fácil**
1. **Qual é o objeto central?** Jev, modelo de decisão da TypeSafe.
2. **Por que RL aparece no título?** Porque a empresa apresenta RLCD como objetivo de treinamento do Jev.
3. **Onde entra o Maestro?** Como estudo de integração em um sistema robótico simulado.

**Médio**
4. **Que tese une as três partes?** Uma decisão probabilística pode ajudar um programa, mas precisa de avaliação e regras externas.
5. **Que evidência própria será mostrada?** Um benchmark pareado de 60 frases sintéticas e um erro crítico.
6. **O que não será provado?** O efeito causal do algoritmo RLCD nem segurança em campo.

**Difícil**
7. **Por que “decisões calibradas” é uma hipótese testável?** Porque probabilidades podem ser comparadas à frequência de acerto em grupos de casos.
8. **Qual é o limite científico principal?** A receita de treino do Jev não é pública o bastante para reprodução e ablação.
9. **Qual seria sua frase de defesa?** “Vou separar o que a TypeSafe afirma, o que terceiros demonstram e o que medimos no Maestro.”

## Slide 2 — O que é Jev?

**Entenda:** `state` é o material analisado; `questions` especifica perguntas com formatos fechados; `answers` devolve decisões e números. A aplicação escolhe o que fazer depois. **Dica:** desenhe verbalmente “texto → pergunta → resposta tipada → código”.

**Fácil**
1. **O que entra no Jev?** Um estado e uma ou mais perguntas.
2. **O que sai?** Escolha, probabilidade binária ou nota numa escala, conforme a pergunta.
3. **Jev executa a ação?** Não; devolve uma resposta para o programa.

**Médio**
4. **O que significa “tipada”?** A resposta obedece ao tipo `Choice`, `Noul` ou `Score` definido antes.
5. **Por que limitar saídas?** Facilita validação e integração com uma decisão de software.
6. **Qual é a diferença entre formato correto e decisão correta?** O modelo pode obedecer ao schema e escolher o rótulo errado.

**Difícil**
7. **Por que um catálogo fechado pode falhar?** Porque um caso real pode não caber nas opções; inclua recusa ou revisão.
8. **A probabilidade autoriza agir?** Não; limiar, estado e política são decisões da aplicação.
9. **O que mediria antes de usar Jev?** Erros por classe, calibração, latência, custo e consequência dos falsos aceites.

## Slide 3 — System One

**Entenda:** É o nome da TypeSafe para modelos orientados a decisões rápidas e tipadas. A referência ao Sistema 1 de Kahneman é uma analogia, não uma explicação literal da arquitetura. **Dica:** não gaste mais de 30 segundos em biografia.

**Fácil**
1. **Quem usa o nome System One?** A TypeSafe.
2. **Jev é o quê nessa família?** O primeiro modelo público da empresa.
3. **Quem fundou a TypeSafe?** Diogo Almeida, que trabalhou na OpenAI.

**Médio**
4. **Qual é a ideia do nome?** Evocar decisões rápidas em vez de longas respostas deliberativas.
5. **É uma teoria do cérebro implementada?** Não; é uma inspiração de linguagem.
6. **A biografia do fundador valida o modelo?** Não; validação exige medições na tarefa.

**Difícil**
7. **Que comparação seria conceitualmente injusta?** Jev escolhendo uma classe contra um LLM escrevendo uma dissertação.
8. **“Rápido” em qual medida?** Na latência ponta a ponta da mesma decisão, com rede e validação.
9. **Como evitar antropomorfismo?** Descreva entrada, saída e teste, sem atribuir intuição humana ao modelo.

## Slide 4 — Bot de WhatsApp

**Entenda:** A conversa é aberta, mas o encaminhamento é uma decisão entre equipes. É um exemplo sintético, não um produto implementado. **Dica:** peça à sala que escolha a equipe antes de revelar a ambiguidade entre cobrança e falha técnica.

**Fácil**
1. **Qual mensagem chega?** Uma reclamação de cobrança duplicada.
2. **Que decisão o bot precisa tomar?** Para qual equipe encaminhar.
3. **Quais são as opções?** Técnico, financeiro, comercial ou humano.

**Médio**
4. **Por que o caso é ambíguo?** Cobrança aponta para financeiro; falha de integração pode apontar para técnico.
5. **O que Jev retornaria?** Uma opção e probabilidades para o catálogo.
6. **Quem encaminha de fato?** O código do bot, após validar e aplicar uma política.

**Difícil**
7. **Como desenhar a categoria humano?** Como revisão para ambiguidade ou informação insuficiente.
8. **Qual erro custa mais?** Depende do serviço; roteamento errado pode atrasar uma reclamação importante.
9. **Como testar o exemplo seriamente?** Com mensagens rotuladas, custos de erro e comparação contra regras ou outro classificador.

## Slide 5 — `if` versus Jev

**Entenda:** Use regra determinística quando a entrada estruturada já contém a resposta. `Noul` serve para interpretar uma afirmação em linguagem natural; não transforma uma inferência em verificação legal de idade. **Dica:** a frase-chave é “número conhecido: `if`; frase ambígua: classificar”.

**Fácil**
1. **Se `idade=19`, o que usar?** `if (idade >= 18)`.
2. **Quando surge a ambiguidade?** Quando a entrada é uma frase sobre idade.
3. **Qual tipo Jev cabe no sim/não?** `Noul`.

**Médio**
4. **O que `Noul=0,8` quer dizer?** Probabilidade estimada de a proposição ser verdadeira.
5. **Por que não usar Jev no número estruturado?** A regra já é exata, simples e barata.
6. **Quem decide o limiar?** A aplicação, conforme custo do erro.

**Difícil**
7. **Uma frase pode comprovar idade?** Não; ela não fornece verificação de identidade ou documento.
8. **Que falso positivo é perigoso?** Interpretar “faço 18 mês que vem” como já maior de idade.
9. **Qual é a generalização do exemplo?** Modelos ajudam a interpretar texto; regras exatas seguem no código.

## Slide 6 — Contrato do Jev

**Entenda:** A API recebe `state`, `model` e `questions`; a resposta vem em `answers`, ligada aos IDs definidos pelo programa. O contrato delimita formato, não política. **Dica:** mostre os quatro nomes e siga para os tipos.

**Fácil**
1. **Onde vai o conteúdo?** Em `state`.
2. **Onde vão as perguntas?** Em `questions`.
3. **Onde lemos o resultado?** Em `answers`.

**Médio**
4. **Por que fixar `model`?** Para reproduzir e comparar resultados entre rodadas.
5. **O que há dentro de uma pergunta?** Tipo, instrução e, quando aplicável, critérios.
6. **O que o programa faz depois?** Valida a resposta e aplica uma política própria.

**Difícil**
7. **Por que IDs estáveis importam?** Eles ligam cada resposta à pergunta esperada no código.
8. **Que falha de contrato deve ser recusada?** Campo ausente, opção desconhecida ou distribuição inválida.
9. **Contrato fechado elimina prompt injection?** Não; limita formato, mas conteúdo adversarial ainda pode induzir escolha errada.

## Slide 7 — Choice

**Entenda:** `Choice` seleciona uma alternativa de um conjunto definido pelo aplicativo. `probabilities` distribui massa pelas opções; `confidence` resume concentração e pode diferir de `probabilities[choice]`. **Dica:** aponte para uma opção de revisão ou `UNKNOWN`.

**Fácil**
1. **Quando usar Choice?** Quando há várias opções fechadas.
2. **O que é `choice`?** A opção selecionada pelo modelo.
3. **O que é `probabilities`?** O mapa de probabilidades das opções.

**Médio**
4. **Por que escrever critérios?** Para explicitar a fronteira de cada classe.
5. **Para que serve `UNKNOWN`?** Para permitir recusa quando nenhuma opção positiva se aplica.
6. **`confidence` é sempre a probabilidade vencedora?** Não; são campos distintos.

**Difícil**
7. **O que validar na distribuição?** Chaves esperadas, valores finitos entre 0 e 1 e soma próxima de 1.
8. **Uma classe dominante dispensa revisão?** Não; calibração e custo do erro precisam ser medidos.
9. **Por que um catálogo ruim piora o modelo?** Opções sobrepostas ou ausentes forçam decisões sem interpretação clara.

## Slide 8 — Noul

**Entenda:** `Noul` avalia uma proposição binária e retorna `noul`, a probabilidade de “sim”. Não há `confidence` separado no contrato TypeSafe. Não use esse valor como intensidade de uma característica. **Dica:** use “pede humano?” como exemplo.

**Fácil**
1. **Qual pergunta cabe aqui?** “A pessoa pede atendimento humano?”
2. **Qual é o intervalo da resposta?** De 0 a 1.
3. **O que significa valor perto de 1?** Forte probabilidade de “sim”.

**Médio**
4. **O que significa valor perto de 0,5?** Incerteza entre sim e não.
5. **Onde fica o limiar?** No código da aplicação.
6. **Noul tem `confidence` separado?** Não na resposta documentada da TypeSafe.

**Difícil**
7. **Por que 0,8 não mede “80% de urgência”?** Porque é P(sim) de uma pergunta binária, não posição numa escala.
8. **Como lidar com zona intermediária?** Encaminhar para revisão ou pedir mais informação.
9. **Como escolher limiar?** Medir falsos positivos e falsos negativos segundo o custo de cada um.

## Slide 9 — Score

**Entenda:** `Score` posiciona um item entre níveis ordenados descritos em `criteria`. A resposta pode ficar entre dois níveis e inclui distribuição por nível e `confidence`. **Dica:** compare com Noul: “é grave?” versus “quão grave?”.

**Fácil**
1. **Quando usar Score?** Quando o resultado ocupa uma escala ordenada.
2. **Qual exemplo do slide?** Gravidade de um bug.
3. **Quais níveis?** Cosmético, recurso afetado, bloqueante.

**Médio**
4. **O que significa `score=1,4` em três níveis?** Posição entre os níveis 1 e 2 definidos no critério.
5. **Por que descrever níveis em palavras?** Para fixar o significado de cada posição.
6. **O score é P(sim)?** Não; é uma posição na escala.

**Difícil**
7. **Por que não usar Noul e inventar faixas de intensidade?** Noul julga uma proposição; não avalia cada nível descrito.
8. **O que pode distorcer a escala?** Níveis sobrepostos, lacunas ou descrições inconsistentes.
9. **Como validar Score?** Comparar com avaliações humanas e examinar erros por nível e distribuição.

## Slide 10 — Tokens de saída

**Entenda:** A TypeSafe anuncia preço zero para tokens de saída. Isso não significa inexistência de tokens: nosso registro mostra 69–71 `output_tokens` por chamada. Também há entrada, rede e latência. **Dica:** nunca diga “zero tokens”; diga “preço anunciado zero para saída”.

**Fácil**
1. **A saída é texto longo?** Normalmente são valores estruturados, não uma resposta em prosa.
2. **O preço anunciado de output tokens?** Zero segundo a TypeSafe.
3. **O harness registrou quantos?** Entre 69 e 71 por chamada na fixture citada.

**Médio**
4. **Por que `output_tokens` ainda aparece?** O serviço contabiliza uso mesmo com preço anunciado zero nessa parcela.
5. **Qual custo permanece?** Entrada, serviço, rede e operação do sistema.
6. **Por que uma resposta curta pode economizar?** Evita gerar uma explicação aberta quando o programa só precisa de um rótulo.

**Difícil**
7. **Zero preço de saída garante chamada barata?** Não; payload grande e custo de rede podem dominar.
8. **Como medir economia real?** Comparar fluxos completos com mesma qualidade e mesmo trabalho posterior.
9. **Que erro de comunicação evitar?** Confundir token contabilizado, token cobrado e latência de geração.

## Slide 11 — Velocidade e qualidade

**Entenda:** Multiplicadores publicados por fornecedores dependem do workflow. Para o Maestro, importa latência ponta a ponta e risco da escolha. **Dica:** se perguntarem “quantas vezes mais rápido?”, responda com a tarefa e o hardware do número.

**Fácil**
1. **O que é p95?** O tempo abaixo do qual ficaram 95% das chamadas medidas.
2. **O que mais importa além de rapidez?** Qualidade e custo dos erros.
3. **Rede entra na medida?** Sim, para uma API remota.

**Médio**
4. **Por que média de latência não basta?** Pode esconder chamadas lentas que atrapalham a operação.
5. **Qual comparação é justa?** Mesma entrada, catálogo, hardware e critério de qualidade.
6. **Por que uma chamada extra pode piorar o fluxo?** Ela adiciona latência sem substituir trabalho relevante.

**Difícil**
7. **Como quantificar utilidade?** Combinar tempo, custo monetário e custo dos erros no fluxo real.
8. **Por que um classificador local pode vencer na prática?** Evita rede e pode falhar de forma previsível na tarefa específica.
9. **Quando aceitar mais latência?** Quando o ganho de qualidade reduz um erro suficientemente caro, respeitando o limite operacional.

## Slide 12 — LLM versus Jev

**Entenda:** LLM generativo serve para resposta aberta; Jev é desenhado para decisões delimitadas. Um LLM também pode devolver JSON, então a diferença útil é qualidade, latência e custo na mesma decisão. **Dica:** não descreva LLM como incapaz de classificar.

**Fácil**
1. **Saída típica de um LLM?** Texto ou JSON gerado.
2. **Saída típica de Jev?** Escolha ou valor tipado com probabilidades.
3. **Quando preferir texto aberto?** Quando a tarefa exige explicar, redigir ou conversar.

**Médio**
4. **JSON mode iguala os sistemas?** Aproxima formato, mas desempenho e custo ainda precisam ser medidos.
5. **Qual tarefa favorece Jev?** Roteamento frequente entre opções conhecidas.
6. **O que ambos exigem após a resposta?** Validação e política de consequência.

**Difícil**
7. **Que baseline usar no estudo?** Um LLM com saída estruturada e o classificador local, no mesmo corpus.
8. **O que acontece se Jev precisar de muitas perguntas longas?** O custo de entrada e a complexidade do contrato crescem.
9. **Qual afirmação evitar?** “Jev é melhor que LLM” sem fixar tarefa, métrica e ambiente.

## Slide 13 — Documentação de Choice

**Entenda:** O print mostra a documentação oficial do contrato, não uma inferência da conta do apresentador. Use-o para localizar `type`, `instructions`, `criteria` e a estrutura de resposta. **Dica:** aponte três campos e avance.

**Fácil**
1. **Que página aparece?** A documentação oficial de `Choice` da TypeSafe.
2. **O que define as opções?** `criteria`.
3. **Que campo seleciona a primitiva?** `type: "choice"`.

**Médio**
4. **Por que mostrar a fonte?** Para separar contrato oficial de interpretação da apresentação.
5. **O print demonstra desempenho?** Não; demonstra apenas interface documentada.
6. **Que dados não projetar?** Credenciais e mensagens pessoais.

**Difícil**
7. **Como saber se o exemplo ainda vale?** Conferir a versão atual da documentação antes da fala.
8. **Por que `criteria` importa mais que nomes curtos?** As descrições delimitam semanticamente as opções.
9. **Como reproduzir a chamada?** Registrar versão do modelo, state, perguntas e resposta completa sanitizada.

## Slide 14 — Caso do Playground

**Entenda:** A frase mistura cobrança duplicada e falha de integração. O exercício é construir um `Choice` de departamento e ouvir a previsão do público antes de executar. **Dica:** não prometa resultado fixo; leia a resposta real.

**Fácil**
1. **Qual é o estado?** Mensagem sintética sobre pagamento e integração.
2. **Qual é a pergunta?** Qual departamento deve receber o chamado.
3. **Quais opções aparecem?** Financeiro, técnico, comercial e humano.

**Médio**
4. **Por que financeiro é plausível?** Há cobrança duplicada.
5. **Por que técnico ainda tem probabilidade?** Há falha de integração.
6. **Por que perguntar à sala primeiro?** Torna a ambiguidade visível antes da resposta do modelo.

**Difícil**
7. **O resultado de uma chamada prova acurácia?** Não; é uma demonstração isolada.
8. **Como tratar escolha incerta?** Revisão humana ou pedido de informação adicional.
9. **Qual seria um teste comparativo?** Muitos chamados rotulados, com custo de roteamento errado.

## Slide 15 — Playground ao vivo

**Entenda:** É uma área para mostrar a ferramenta real. Se a rede falhar, use a resposta documentada como exemplo de contrato e diga que não foi execução ao vivo. **Dica:** prepare abas, vídeo/print reserva e cubra credenciais.

**Fácil**
1. **O que mostrar primeiro?** `state`, pergunta e opções.
2. **O que ler na resposta?** Escolha e probabilidades principais.
3. **Se o site falhar?** Usar a reserva identificada como exemplo, sem simular chamada.

**Médio**
4. **Por que ler `confidence` com cuidado?** Não é automaticamente a probabilidade vencedora.
5. **Por que não usar mensagem real de cliente?** Pode conter dado pessoal desnecessário.
6. **O que a demo ensina?** Como escrever uma pergunta tipada, não que o modelo é universalmente correto.

**Difícil**
7. **Como evitar viés de confirmação?** Definir expectativa antes de ver o resultado.
8. **O que registrar para repetir?** Modelo, pergunta, critérios e entrada sintética.
9. **Qual risco de latência ao vivo?** Rede/serviço podem atrasar; reserva mantém a apresentação.

## Slide 16 — Requisição JSON

**Entenda:** É um exemplo completo do formato `POST /v1/systemone`: `state`, `model`, uma pergunta `choice`, instrução e critérios. Não é um arquivo do Maestro. **Dica:** leia o caminho dos campos, não cada linha.

**Fácil**
1. **Qual endpoint?** `/v1/systemone`.
2. **Qual campo fixa versão?** `model`.
3. **Onde fica o catálogo?** Em `questions.departamento.criteria`.

**Médio**
4. **O que `instructions` pergunta?** Qual equipe atende o caso.
5. **Por que critérios têm texto?** Para explicar o sentido de cada opção.
6. **O que falta para encaminhar?** Ler `answers`, validar e executar política no programa.

**Difícil**
7. **Por que não usar `jev-latest` em benchmark?** Pode mudar a versão sem controle.
8. **Como uma chave de API deve ser tratada?** Fora de slides, app distribuído e repositório.
9. **Que erro a aplicação precisa tratar?** Timeout, resposta inválida ou opção não prevista.

## Slide 17 — RL básico

**Entenda:** RL ajusta uma política para aumentar retorno esperado ao interagir com estados, ações e recompensas. Exemplo: jogo ou navegação simulada. Isso não define sozinho a arquitetura de Jev. **Dica:** pronuncie `π(a|s)` como “probabilidade da ação dado o estado”.

**Fácil**
1. **O que é estado?** Informação disponível antes da decisão.
2. **O que é ação?** Escolha feita pelo agente.
3. **O que é recompensa?** Sinal recebido após uma ação ou sequência.

**Médio**
4. **O que é política?** Regra aprendida que liga estados a distribuições de ações.
5. **O que é retorno?** Acúmulo de recompensas futuras que o treino otimiza.
6. **Por que uma recompensa ruim é perigosa?** O agente pode explorar atalhos indesejados para aumentá-la.

**Difícil**
7. **RL exige recompensa a cada passo?** Não; ela pode ser esparsa ou atrasada.
8. **Uma política com alta recompensa está calibrada?** Não necessariamente; objetivo de retorno e calibração diferem.
9. **Que pergunta fazer sobre qualquer RL?** Qual comportamento é recompensado, como é medido e em que distribuição?

## Slide 18 — RLHF

**Entenda:** Na forma clássica, pessoas comparam respostas, um sinal de preferência é aprendido e a política é ajustada. ChatGPT/InstructGPT é referência pública; Claude, Grok e DeepSeek são exemplos de *chat models*, sem afirmar receita idêntica de treino. **Dica:** destaque a origem do sinal: preferência humana.

**Fácil**
1. **O que significa RLHF?** Reinforcement Learning from Human Feedback.
2. **Quem fornece o sinal?** Pessoas que avaliam ou comparam respostas.
3. **Que produto é exemplo clássico?** ChatGPT/InstructGPT.

**Médio**
4. **O que a política aprende a favorecer?** Respostas preferidas sob o sinal usado.
5. **Por que isso ajuda chat?** Preferência capta utilidade e adequação difíceis de codificar em regra simples.
6. **Preferência garante calibração?** Não; gostar de uma resposta difere de estimar a chance de acerto.

**Difícil**
7. **Todo chat model usa o mesmo RLHF?** Não; métodos de pós-treino e divulgações variam.
8. **Que viés entra nas preferências?** Perfil dos avaliadores, instruções de avaliação e distribuição de exemplos.
9. **Como testar generalização?** Avaliar em tarefas e populações não usadas na seleção ou ajuste.

## Slide 19 — RLVR

**Entenda:** RLVR usa um verificador relativamente objetivo, como teste de código ou gabarito matemático, para fornecer sinal de treino. o1/o3 ilustram modelos de raciocínio; o slide não afirma receita exata idêntica. **Dica:** pergunte “quem ou o que decide se acertou?”.

**Fácil**
1. **O que significa RLVR?** Reinforcement Learning with Verifiable Rewards.
2. **Dê um verificador.** Um teste automatizado de código.
3. **Que tarefas favorecem RLVR?** As que têm resposta ou condição verificável.

**Médio**
4. **Por que reduz dependência de avaliação humana por resposta?** O verificador produz o sinal automaticamente.
5. **O que o treino favorece?** Respostas que passam no teste definido.
6. **Que problema permanece?** O verificador pode ser incompleto ou capturar só parte da qualidade.

**Difícil**
7. **Acerto verificável implica calibração?** Não; precisão da escolha e estimativa de incerteza são distintas.
8. **Como um agente pode explorar um verificador?** Encontrando saída que passa no teste sem cumprir a intenção real.
9. **Por que não aplicar RLVR diretamente a todo atendimento?** Muitas decisões não têm gabarito automático confiável.

## Slide 20 — RLCD: objetivo público

**Entenda:** TypeSafe chama RLCD de *Reinforcement Learning for Calibrated Decisions*: decisões tipadas e probabilidades que pretendem refletir frequências. A descrição pública não detalha recompensa, dados, otimização e ablações suficientes para reproduzir Jev. **Dica:** essa ressalva aumenta, não reduz, sua credibilidade diante do grupo.

**Fácil**
1. **O que significa RLCD?** Reinforcement Learning for Calibrated Decisions.
2. **Qual é o alvo anunciado?** Decisões com probabilidades calibradas.
3. **Quais saídas Jev oferece?** `Choice`, `Noul` e `Score`.

**Médio**
4. **O que calibração acrescenta ao acerto?** Informação sobre quão confiável é uma probabilidade em muitos casos.
5. **Qual sinal exato de recompensa foi publicado?** Não há descrição pública suficiente para afirmá-lo.
6. **O que uma saída probabilística permite?** Construir testes de calibração e políticas de revisão.

**Difícil**
7. **A interface prova o efeito de RLCD?** Não; contrato de saída e método de treino são coisas diferentes.
8. **Que ablação pediria?** Mesmo modelo/dados com e sem o componente RLCD alegado, mantendo avaliação idêntica.
9. **O que dizer se perguntarem “RLCD funciona”?** “Há uma alegação testável; nossos dados avaliam Jev numa tarefa, não isolam o treino.”

## Slide 21 — O que significa “calibrada”?

**Entenda:** Calibração é uma propriedade estatística de muitas previsões. Entre casos aos quais o modelo atribuiu perto de 0,8 para a classe escolhida, cerca de 80% deveriam estar corretos se essa faixa estiver calibrada. **Dica:** diga “grupo de casos”, nunca “este caso vai acertar”.

**Fácil**
1. **Probabilidade 0,8 garante acerto?** Não.
2. **O que observar em muitos casos de 0,8?** Frequência de acerto perto de 80%.
3. **Uma decisão correta pode ter probabilidade ruim?** Sim; pode estar confiante demais ou de menos.

**Médio**
4. **Por que agrupar casos parecidos?** Para comparar probabilidades previstas com frequências observadas.
5. **Um modelo pode ser preciso e mal calibrado?** Sim; pode acertar muito e dizer 99% em erros frequentes.
6. **Por que olhar cada classe?** A média pode ocultar excesso de confiança em `CONFIRM`.

**Difícil**
7. **Qual efeito de mudança de domínio?** Uma calibração medida em um conjunto pode falhar em transcrições reais.
8. **Calibração perfeita implica utilidade?** Não; um modelo sempre pouco informativo pode ser calibrado e inútil.
9. **Qual seria a avaliação crítica para o Maestro?** Confiabilidade por classe e por faixa, com foco em cancelamento e confirmação.

## Slide 22 — O que conseguimos testar em RLCD

**Entenda:** A proposta vira três eixos: rótulo certo, probabilidade honesta e erros críticos. `Macro-F1`, Brier, ECE e p95 ajudam, mas nenhum número isolado resolve segurança. **Dica:** este slide é sua resposta para “qual é o experimento?”.

**Fácil**
1. **Que métrica resume acerto por classe?** Macro-F1.
2. **Que métricas avaliam probabilidades?** Brier e ECE, com limitações.
3. **Que erro interessa mais ao Maestro?** Aceitação indevida, especialmente `CANCEL → CONFIRM`.

**Médio**
4. **Por que congelar corpus e prompt?** Evita ajustar o teste depois de ver resultados.
5. **Por que comparar versões fixas?** Mudanças de modelo podem alterar respostas e invalidar a comparação.
6. **Por que registrar p95?** A cauda lenta importa na interação por voz.

**Difícil**
7. **O teste do Maestro isola RLCD causalmente?** Não; ele testa Jev como produto numa tarefa.
8. **Que desenho isolaria RLCD?** Ablação controlada do treino mantendo arquitetura, dados e inferência comparáveis.
9. **Como evitar “vencedor” por média?** Exigir limites em erros críticos por classe, além de métricas agregadas.

## Slide 23 — Cem previsões a 80%

**Entenda:** Exemplo inventado para ensinar calibração. Em 100 previsões com probabilidade próxima de 80%, 80 acertos seriam compatíveis com essa faixa; 50 indicariam excesso de confiança. **Dica:** diga explicitamente que não são os 60 casos do Maestro.

**Fácil**
1. **Quantos casos há no exemplo?** Cem, hipotéticos.
2. **Se 80 acertam, o que sugere?** Calibração aproximada nessa faixa.
3. **Se 50 acertam?** O modelo foi confiante demais nessa faixa.

**Médio**
4. **Por que “aproximada”?** Há variação amostral e probabilidades não são todas exatamente 0,8.
5. **O que se sabe sobre uma previsão específica?** Só uma estimativa, não certeza de resultado.
6. **E se 95 acertarem?** O modelo pode estar subconfiante nessa faixa.

**Difícil**
7. **Por que grupos muito pequenos enganam?** A taxa observada oscila bastante com poucos casos.
8. **Calibração só da classe vencedora basta?** Não para avaliar toda a distribuição multiclasses.
9. **Qual teste seguinte?** Repetir por faixa, classe e domínio com intervalos de incerteza.

## Slide 24 — Três medidas, três perguntas

**Entenda:** Accuracy/macro-F1 tratam escolha; Brier/ECE tratam qualidade numérica; falsos aceites tratam consequência. No Maestro, um raro erro perigoso pode dominar a decisão. **Dica:** transforme cada métrica em uma pergunta oral simples.

**Fácil**
1. **Accuracy pergunta o quê?** Quantas escolhas foram corretas.
2. **ECE pergunta o quê?** Se confiança média e acerto médio se aproximam por faixas.
3. **Falso aceite é o quê?** Uma recusa ou caso inválido tratado como autorização/ação.

**Médio**
4. **Por que macro-F1?** Dá peso semelhante às classes, em vez de deixar a maioria dominar.
5. **Por que Brier?** Penaliza distribuições probabilísticas distantes do rótulo verdadeiro.
6. **Por que matriz de confusão?** Mostra a direção do erro, como cancelar virar confirmar.

**Difícil**
7. **ECE baixo em 60 casos prova calibração?** Não; é estimativa instável e dependente dos bins.
8. **Como decidir com múltiplas métricas?** Pré-definir critérios de qualidade e segurança antes de abrir o holdout.
9. **Qual métrica agregada pode esconder risco?** Accuracy alta com poucos erros `CANCEL → CONFIRM`.

## Slide 25 — RL, RLHF, RLVR e RLCD

**Entenda:** A tabela compara fontes de sinal e objetivos, não etapas de uma única receita. RLHF busca preferência, RLVR usa verificação; RLCD é a proposta pública da TypeSafe para decisão calibrada. **Dica:** percorra a coluna “sinal” e depois “limite”.

**Fácil**
1. **Sinal do RL básico?** Recompensa do ambiente.
2. **Sinal de RLHF?** Preferência humana.
3. **Sinal de RLVR?** Verificador da tarefa.

**Médio**
4. **O que RLCD procura segundo a TypeSafe?** Escolhas e probabilidades calibradas.
5. **As quatro siglas são fases obrigatórias?** Não.
6. **Qual limite de RLHF/VR para esta fala?** Preferência e acerto não garantem calibração.

**Difícil**
7. **É válido afirmar exclusividade de RLCD na calibração?** Não; outros métodos também podem produzir probabilidades calibradas.
8. **O que falta na descrição pública de Jev?** Detalhes de dados, recompensa, otimização e ablações.
9. **Como impedir uma comparação injusta?** Fixar tarefa, métrica e baseline antes de discutir métodos.

## Slide 26 — Emojis conforme a frase

**Entenda:** Demonstração de terceiro: texto ajuda a selecionar emojis de um catálogo; a interface anima o resultado. O vídeo mostra uma integração, não prova desempenho geral. **Dica:** use este primeiro porque o efeito visual revela a ideia sem risco alto.

**Fácil**
1. **O que entra?** Uma frase digitada.
2. **O que é escolhido?** Emojis de um conjunto existente.
3. **Quem anima os emojis?** A interface programada, não Jev.

**Médio**
4. **Por que é exemplo de Choice?** Há opções já conhecidas a selecionar.
5. **O que mudaria com outra frase?** A relevância das opções e o destaque na UI.
6. **O vídeo mede acurácia?** Não; é uma demonstração visual.

**Difícil**
7. **Que baseline simples caberia?** Busca por palavras-chave ou embeddings, comparados nas mesmas frases.
8. **Que falha importaria pouco aqui?** Escolher emoji irrelevante, por ser uma ação reversível.
9. **O que a demo ensina sobre sistemas?** Modelo decide uma variável; código faz renderização e interação.

## Slide 27 — Seleção de skills

**Entenda:** Jev pode escolher qual skill carregar antes de uma chamada maior. A hipótese é reduzir contexto sem perder instruções necessárias. **Dica:** diga que a opção `NONE` é essencial.

**Fácil**
1. **O que é escolhido?** Uma skill ou nenhuma.
2. **Jev executa a skill?** Não; o harness carrega o arquivo escolhido.
3. **Por que selecionar?** Para evitar carregar todas as instruções sempre.

**Médio**
4. **O que pode ser economizado?** Tokens de contexto no agente principal.
5. **Qual erro perigoso?** Descartar uma skill necessária.
6. **Por que incluir `NONE`?** Muitos pedidos não exigem skill.

**Difícil**
7. **Como medir ganho?** Custo total do loop e sucesso da tarefa com e sem roteador.
8. **O roteador pode aumentar custo?** Sim, se a chamada extra não evitar trabalho suficiente.
9. **Qual política manter no harness?** Regras obrigatórias não devem depender de escolha probabilística.

## Slide 28 — Triagem de PR

**Entenda:** A demo PR Judge classifica um diff limitado em rotas como `SAFE`, `REVIEW` e `BLOCK`. Economia de tokens só é válida se o fluxo completo ficar mais barato sem perder erros importantes. **Dica:** avise que é pesquisa complementar, não um dos tweets originais.

**Fácil**
1. **Qual é a entrada?** Um diff limitado de pull request.
2. **Qual é a saída?** Uma rota de triagem.
3. **A demo roda testes?** Não segundo a descrição estudada.

**Médio**
4. **O que `BLOCK` deveria causar?** Revisão adicional, não julgamento definitivo por si só.
5. **Por que não substitui CI?** Não executa nem verifica o software.
6. **Qual economia é hipótese?** Evitar resenha generativa em cada PR.

**Difícil**
7. **Que falso negativo é crítico?** Rotular como seguro um diff com falha grave.
8. **Qual avaliação adequada?** Mesmo conjunto de PRs, custo total, recall de problemas e revisão humana.
9. **Como evitar vazamento de código?** Minimizar o diff enviado e revisar a fronteira de dados do serviço.

## Slide 29 — Xadrez, Fable e Astra

**Entenda:** O relato é de blitz 5+0, uma chamada por lance e sem busca. Jev venceu Fable no relógio; Astra deu mate em 18. Não use isso como ranking de força enxadrística. **Dica:** explique a regra do harness antes de falar do resultado.

**Fácil**
1. **Qual modalidade?** Blitz de cinco minutos sem incremento.
2. **Como Jev venceu Fable?** No tempo.
3. **O que aconteceu contra Astra?** Astra deu mate em 18 lances.

**Médio**
4. **Por que rapidez importa no teste?** O relógio faz parte do resultado.
5. **Por que xadrez desafia Jev?** Exige cálculo, busca e avaliação de sequências.
6. **Uma vitória no tempo prova maior força?** Não.

**Difícil**
7. **Como comparar força de jogo?** Muitas partidas com relógio, cores e condições controladas.
8. **Qual variável do harness influencia muito?** Uma chamada por lance sem busca adicional.
9. **Qual lição geral?** Uma decisão rápida pode ganhar em latência e perder em qualidade da estratégia.

## Slide 30 — JevPilot em simulação

**Entenda:** O vídeo envolve `HighwayEnv`, estado simbólico e ações fechadas. Há freios/regras fora do modelo. Não é um Tesla físico nem direção autônoma validada. **Dica:** pronuncie “simulação” antes de exibir o vídeo.

**Fácil**
1. **Onde roda?** Em ambiente de simulação HighwayEnv.
2. **Que dados o modelo recebe?** Estado simbólico preparado pelo programa.
3. **Há veículo real?** Não.

**Médio**
4. **Quem limita as ações?** Código e regras de segurança do harness.
5. **Por que catálogo fechado ajuda?** Impede saída livre fora das ações previstas.
6. **Catálogo fechado garante segurança?** Não; uma ação permitida pode ser inadequada ao estado.

**Difícil**
7. **Que avaliação seria necessária antes de uso físico?** Simulação ampla, testes de falhas, controlador seguro e validação em hardware.
8. **Que erro de inferência o vídeo pode induzir?** Confundir uma demo simbólica com percepção e controle de um carro real.
9. **Qual conexão com Maestro?** O modelo só propõe decisão; estado, confirmação e comando ficam em software determinístico.

## Slide 31 — Por que tantos modelos parecidos?

**Entenda:** Jev popularizou uma interface clara, enquanto grupos podiam reutilizar encoders, pesos e benchmarks. A proximidade dos anúncios não prova cópia ou treinamento completo em poucos dias. **Dica:** enquadre como inferência sobre o ecossistema, não história comprovada de cada equipe.

**Fácil**
1. **Qual interface ficou visível?** Estado, perguntas fechadas e probabilidades.
2. **O que outros projetos podiam reutilizar?** Modelos pré-treinados, código e benchmarks.
3. **Todos rodam do mesmo jeito?** Não.

**Médio**
4. **Por que projetos rápidos podem surgir?** Adaptar um backbone existente é mais curto que treinar tudo do zero.
5. **Qual objetivo muda entre eles?** Localidade, latência, custo ou tarefa alvo.
6. **Por que “mais rápido” é ambíguo?** Rede, GPU/CPU, cache, entrada e modelo carregado alteram a medida.

**Difícil**
7. **Anúncio próximo prova causalidade?** Não; não mostra quando o trabalho começou.
8. **Como testar se dois modelos fazem a mesma função?** Mesmo contrato, corpus, classes, hardware e critérios de avaliação.
9. **Por que essa abertura vem antes dos nomes?** Dá ao público uma pergunta para orientar Laya, Julia-1 e CLM.

## Slide 32 — Laya: origem e interface

**Entenda:** Laya publica pesos e oferece tipos `Choice`, `Score` e `Noul` semelhantes aos da interface de Jev. `laya-mlx` é uma adaptação para Apple Silicon. Não confunda interface semelhante com método de treino idêntico. **Dica:** diferencie modelo, pesos e runtime.

**Fácil**
1. **Qual é a diferença operacional básica para Jev?** Laya pode ser executado localmente com pesos abertos.
2. **Quais perguntas oferece?** `Choice`, `Score` e `Noul`.
3. **O que é `laya-mlx`?** Um runtime/adaptação para Apple Silicon.

**Médio**
4. **Peso aberto significa treino reproduzível?** Não necessariamente; dados e procedimento podem faltar.
5. **O contrato semelhante prova qualidade semelhante?** Não; só facilita montar comparação.
6. **Qual vantagem de execução local?** Pode reduzir dependência de rede e mudar a fronteira de dados.

**Difícil**
7. **Que risco novo o local traz?** Memória, energia, atualização e manutenção de runtime.
8. **Pode substituir Jev sem teste?** Não; faltam nossas seis classes e medição no hardware alvo.
9. **Qual pergunta de RL fazer ao repositório?** Que objetivo, dados e ablações sustentam a alegação de calibração?

## Slide 33 — Laya: execução local

**Entenda:** O valor p50 de 7,39–13,42 ms veio do README de `laya-mlx` no M3 Max, para pergunta curta e modelo já carregado. O Maestro precisa medir no Android real e no mesmo corpus. **Dica:** nunca compare esses milissegundos diretamente aos do Jev remoto.

**Fácil**
1. **O que significa p50?** Mediana da latência medida.
2. **Em que hardware foi publicado?** M3 Max, no runtime MLX.
3. **Laya já foi testado no Maestro?** Não neste corpus.

**Médio**
4. **Por que modelo carregado importa?** Cold start pode acrescentar tempo relevante.
5. **O que medir no Android?** Acurácia, p95, memória e energia.
6. **Por que usar as mesmas seis classes?** Para comparação pareada com Jev e o baseline local.

**Difícil**
7. **Latência local sempre vence remota?** Não; depende de hardware, tamanho de entrada e otimização.
8. **Que risco de privacidade ainda existe localmente?** Dados podem aparecer em logs ou outros serviços do app/SDK.
9. **Que resultado faria Laya interessante?** Erros críticos aceitáveis e qualidade comparável com menor custo/latência no dispositivo alvo.

## Slide 34 — Julia-1, do Brasil

**Entenda:** Supersonic Labs apresenta Julia-1 como modelo de decisão sobre 2–20 opções, baseado em mmBERT-small e com 144,3 milhões de parâmetros. Os resultados publicados incluem comparação com referência Jev de protocolo anterior, não uma nova rodada controlada no Maestro. **Dica:** dê destaque à contribuição brasileira sem declarar vencedor.

**Fácil**
1. **De onde vem Julia-1?** Da Supersonic Labs, equipe brasileira.
2. **Qual backbone citado?** mmBERT-small.
3. **Onde pode rodar?** CPU; há exportação ONNX.

**Médio**
4. **O que entra?** Estado/contexto, pergunta e 2–20 opções.
5. **Por que o resultado typed decisions chama atenção?** Julia e referência Jev ficaram próximos naquele protocolo.
6. **O que Banking77 alerta?** Julia foi pior em categorias bancárias semelhantes na comparação publicada.

**Difícil**
7. **Por que a referência Jev não é confronto novo?** Os números foram reaproveitados do protocolo anterior.
8. **Que lacuna importa ao Maestro?** pt-BR, seis classes operacionais e custo dos erros críticos.
9. **Como seria a comparação justa?** Executar Julia e Jev nas mesmas transcrições congeladas, com versões fixas e métricas iguais.

## Slide 35 — CLM

**Entenda:** CLM usa representação vetorial de estado e ações, com treino contrastivo para aproximar pares corretos. Ações repetidas podem ter embeddings em cache. O repositório relata até 9× menor latência em tarefas escolhidas com backbone de 8B/GPU. **Dica:** explique um par positivo e um negativo antes do multiplicador.

**Fácil**
1. **O que é um encoder?** Modelo que converte entrada em representação vetorial.
2. **O que CLM compara?** Estado e ações candidatas.
3. **O que pode ficar em cache?** Vetores de ações reutilizadas.

**Médio**
4. **O que é treino contrastivo aqui?** Aproximar estado/ação correta e afastar alternativas incorretas.
5. **Por que cache pode acelerar?** Evita recalcular representação de ação conhecida.
6. **O “até 9×” vale no Maestro?** Não foi medido no Maestro.

**Difícil**
7. **O que comparar sem cache?** Latência e qualidade quando as opções mudam frequentemente.
8. **Por que 8B/GPU muda a conclusão?** Custo e hardware diferem muito de Julia em CPU ou Jev via rede.
9. **Qual risco de similaridade vetorial?** A ação mais próxima pode estar semanticamente errada; precisa de avaliação e política externa.

## Slide 36 — Jev, Laya, Julia-1 e CLM

**Entenda:** A tabela fecha o bloco de modelos. Jev foi medido nas seis classes; Laya e Julia têm caminho local; CLM usa similaridade/cache. A última linha define comparação comum, sem eleger vencedor. **Dica:** explique primeiro “onde cada um roda”, depois “o que falta medir no Maestro”.

**Fácil**
1. **Qual é API remota?** Jev.
2. **Quais oferecem pesos/execução local?** Laya e Julia-1.
3. **Qual usa encoders e cache de ação?** CLM.

**Médio**
4. **O que já medimos no Maestro?** Jev versus classificador local em 60 frases sintéticas.
5. **Que métricas faltam para os demais?** Macro-F1, Brier/ECE, p95, memória/custo e erros críticos.
6. **Por que mesma entrada e catálogo?** Isolam parte da diferença de modelo e evitam tarefas incompatíveis.

**Difícil**
7. **Qual resultado agregado não decide adoção?** Macro-F1 alto com erro `CANCEL → CONFIRM`.
8. **Como comparar serviço e modelos locais?** Medir ponta a ponta no fluxo real, incluindo rede, carregamento e hardware.
9. **Qual é a conclusão intelectualmente honesta?** Os projetos têm trade-offs distintos; no Maestro ainda falta teste pareado de Laya, Julia e CLM.

## Slide 37 — Documento compartilhado por Diogo

**Entenda:** As notas públicas discutem desenho de agente de código. O post de terceiro descreve um PDF de 11 páginas; a exportação encontrada gera 12. A identidade entre os arquivos não foi comprovada. **Dica:** este slide inicia outro assunto após a tabela.

**Fácil**
1. **Quem compartilhou as notas?** Diogo Almeida.
2. **Sobre que sistema?** Uma proposta de agente de código.
3. **Há benchmark do agente?** Não no material apresentado.

**Médio**
4. **Por que distinguir post e documento?** Para atribuir autoria e evidência corretamente.
5. **Qual pergunta abre as notas?** Como desenhar agente sem depender de KV cache.
6. **O que a imagem mostra?** Um recorte do documento público, identificado como fonte.

**Difícil**
7. **Por que não afirmar que o PDF de terceiros é original?** A página/arquivo não foram verificados como idênticos.
8. **Que natureza tem a proposta?** Hipótese arquitetural, não produto medido.
9. **Que teste faltaria?** Comparar tarefas de agente com e sem as decisões sugeridas, medindo sucesso, custo e perdas de contexto.

## Slide 38 — Custo de trocar de modelo

**Entenda:** Alternar modelo forte → barato → forte pode exigir que o forte reprocesse contexto; a economia intermediária pode desaparecer. A conta nas notas é ilustrativa. **Dica:** use uma história de “reler o caderno inteiro” e não tente ensinar KV cache profundamente no palco.

**Fácil**
1. **O que é KV cache em uma frase?** Reuso de cálculos sobre prefixos já processados pelo mesmo modelo.
2. **Qual sequência é discutida?** Forte, barato, forte.
3. **Que custo pode aparecer na volta?** Reprocessar histórico/contexto.

**Médio**
4. **Por que o cache não passa automaticamente?** Modelos diferentes têm estados internos diferentes.
5. **Quando a troca vale a pena?** Quando a economia supera reprocessamento e não reduz qualidade.
6. **A conta do documento mede produto real?** Não; é uma ilustração.

**Difícil**
7. **Qual variável domina a troca?** Tamanho e forma do contexto que cada chamada precisa receber.
8. **Que mitigação considerar?** Contexto menor, resumo testado, cache do provedor ou roteamento estável.
9. **Que efeito adverso de resumir?** Perder instrução ou evidência essencial para a tarefa.

## Slide 39 — Contexto para a próxima tarefa

**Entenda:** O harness pode escolher bloco completo, resumo ou omissão; também carregar instruções e schemas sob demanda. Jev poderia estimar relevância, mas código monta a janela e preserva regras obrigatórias. **Dica:** apresente um exemplo de saída longa de ferramenta.

**Fácil**
1. **O que é harness aqui?** Programa ao redor do modelo que prepara contexto, valida e executa regras.
2. **Quais opções para um bloco?** Completo, resumido ou fora do contexto.
3. **Quem monta a janela final?** O código do harness.

**Médio**
4. **Onde Jev entra?** Sugerindo relevância ou escolha entre opções tipadas.
5. **Por que carregar schema sob demanda?** Reduzir contexto quando muitas ferramentas existem.
6. **O que nunca deve ser descartado por pontuação?** Instruções obrigatórias e políticas de segurança.

**Difícil**
7. **Como medir o benefício?** Sucesso da tarefa, tokens totais, latência e erros por omissão.
8. **Qual falso negativo é grave?** Omitir um bloco necessário para executar corretamente.
9. **Como criar ground truth de relevância?** Anotar tarefas e verificar se remover cada bloco altera solução e segurança.

## Slide 40 — Jev no loop de agente

**Entenda:** Jev pode decidir contexto, ferramenta ou rota em pontos definidos; o harness valida, e ferramenta/LLM executa. É uma proposta, não evidência de agente TypeSafe já medido. **Dica:** repita “modelo propõe; código confere; ferramenta executa”.

**Fácil**
1. **Quais etapas do loop?** Observar, escolher, executar e verificar.
2. **O que Jev escolhe?** Decisões pequenas e tipadas, como rota ou ferramenta.
3. **Quem executa ferramenta?** O harness após validar.

**Médio**
4. **Por que dar catálogo de ferramentas?** Restringir a opções disponíveis e auditáveis.
5. **O que a validação verifica?** Catálogo, estado, permissão e política.
6. **Qual benefício potencial?** Evitar chamada grande para uma escolha simples.

**Difícil**
7. **Quando Jev atrapalha?** Se adicionar chamada sem reduzir trabalho ou se roteamento errado perder contexto.
8. **Permissão sensível pode depender só dele?** Não; autorização fica em regra e humano quando necessário.
9. **Que experimento provaria utilidade?** Agente com/sem Jev nas mesmas tarefas, medindo sucesso, custo, p95 e falhas de segurança.

## Slide 41 — Maestro e hackathon

**Entenda:** AgroTurtles desenvolveu Maestro no contexto do AI Glasses Brasil 2026: uma interface de operador para máquina agrícola usando voz e visão. O MVP demonstrado é pré-hardware, com simulação Gazebo e MockDeviceKit. **Dica:** marque aqui a mudança de tema: agora o público conhece Jev e vai ver uma aplicação.

**Fácil**
1. **Qual equipe?** AgroTurtles.
2. **Qual problema?** Interação hands-free com um sistema robótico agrícola.
3. **O robô está em campo?** Não; a evidência apresentada é simulada.

**Médio**
4. **Qual papel dos óculos?** Câmera/interface prevista, ainda dependente de validação física.
5. **Qual é o estágio comprovado?** Integração pré-hardware no Android/mock e Gazebo.
6. **Por que mencionar a origem no hackathon?** Explica restrições de tempo, MVP e escolha de demonstrar em simulação.

**Difícil**
7. **Qual claim seria exagerado?** “Óculos Meta e robô físico aprovados ponta a ponta.”
8. **Que gate físico falta?** Câmera/sessão DAT e áudio simultâneos nos óculos e aparelho exatos.
9. **Qual valor do Maestro mesmo sem Jev?** Contrato tipado, resolução de alvo, confirmação e bridge robótico seguro.

## Slide 42 — Olhar, falar, confirmar

**Entenda:** A pessoa identifica um alvo por QR ou talhão mapeado, pede uma ação por voz e confirma por áudio antes de movimento. Uma classificação alta não substitui a confirmação. **Dica:** diga os três verbos pausadamente; é a frase mais fácil de memorizar do Maestro.

**Fácil**
1. **Qual é a sequência de produto?** Olhar, falar, confirmar.
2. **Como o alvo pode ser identificado?** QR/marcador ou talhão já mapeado.
3. **Quando a ação física pode começar?** Depois de confirmação explícita e validações.

**Médio**
4. **Por que alvo e intenção são separados?** Saber onde e saber o que fazer são decisões diferentes.
5. **O que acontece com alvo ambíguo?** Nenhum comando é liberado até resolver o conflito.
6. **Confiança do classificador basta?** Não; confirmações e estado são barreiras próprias.

**Difícil**
7. **Qual ataque pode explorar confirmação implícita?** Uma fala ambígua ser interpretada como autorização de movimento.
8. **Como provar que `SPRAY` não moveu sozinho?** Inspecionar máquina de estados, `Command` emitido e testes de confirmação.
9. **Qual caso de uso preserva hands-free sem perder controle?** O app narra operação e alvo e espera resposta explícita da pessoa.

## Slide 43 — Do comando ao robô

**Entenda:** Voz gera decisão tipada; regras e estado determinísticos verificam alvo/operação; confirmação habilita um `Command` JSON versionado; WebSocket/ROS 2 executam no Gazebo. Jev nunca gera comandos ROS livres. **Dica:** percorra as setas da esquerda para a direita sem saltar o bloco de confirmação.

**Fácil**
1. **O que vem depois da fala?** Classificação de intenção.
2. **O que chega ao bridge?** `Command` estruturado e versionado.
3. **Onde a execução foi demonstrada?** Gazebo/Nav2.

**Médio**
4. **O que as regras verificam?** Estado atual, alvo, operação válida e confirmação.
5. **O que a câmera decide?** O alvo, por resolvedor separado, não a intenção falada.
6. **O que ocorre com `SPRAY` e QR conflitantes?** Ambiguidade e nenhum comando.

**Difícil**
7. **Por que contrato ROS independente do fabricante?** Isola a interface do app do robô específico.
8. **Por que Jev não produz ROS livre?** Seria difícil validar segurança, estado e permissões de uma saída arbitrária.
9. **Qual é a fronteira de autoridade?** Modelo interpreta texto; código determinístico autoriza e forma o comando.

## Slide 44 — QR e minimização

**Entenda:** A câmera fornece um frame sob demanda; o Android decodifica QR localmente, retém `target_id` e descarta imagem. Isso reduz exposição, mas não quer dizer que “a câmera só vê QR” nem conformidade LGPD completa. **Dica:** explique a diferença entre frame capturado e dado que o app conserva.

**Fácil**
1. **Quando ocorre captura?** Sob demanda.
2. **O que o decoder extrai?** `target_id`.
3. **O app guarda foto por padrão?** Não.

**Médio**
4. **O frame existe por um momento?** Sim, em memória durante a leitura.
5. **Por que fazer decoder local?** Evita enviar imagem a serviço remoto para resolver alvo.
6. **O classificador recebe a foto?** Não; a decisão de fala tem caminho separado.

**Difícil**
7. **Minimização equivale a anonimização?** Não; o frame e identificadores ainda podem ser dados relevantes.
8. **Que fronteiras extras existem?** Android, SDK de câmera e serviço de reconhecimento de fala.
9. **Qual teste verificar?** Que erro, timeout e QR inválido não persistem mídia nem criam comando.

## Slide 45 — Antes de enviar transcrição

**Entenda:** No `mockDebug`, um consentimento de sessão e gates no app/proxy bloqueiam padrões evidentes de CPF/CNPJ, e-mail, telefone, URL, tamanho excessivo e fala fora do escopo antes da chamada remota. Filtros de padrão reduzem risco, mas não identificam toda informação pessoal. **Dica:** nunca diga que o classificador local “detecta qualquer CPF”.

**Fácil**
1. **Qual caminho usa o gate remoto?** O Jev experimental em `mockDebug`.
2. **Onde ocorre o bloqueio?** No app e no proxy, antes da rede externa.
3. **O que o app faz com fala bloqueada?** Não a envia ao Jev nem libera comando.

**Médio**
4. **Por que gate duplicado?** Defesa caso uma camada seja contornada ou falhe.
5. **Que dado pode passar pelo gate?** Um dado pessoal escrito de forma não reconhecida pelo padrão.
6. **Consentimento de sessão é permanente?** Não; pode ser revogado e o padrão continua local.

**Difícil**
7. **Isso demonstra conformidade integral com LGPD?** Não; é uma mitigação técnica limitada.
8. **Como melhorar avaliação do gate?** Corpus adversarial sanitizado, falsos bloqueios e escapes, sem dados reais desnecessários.
9. **Qual afirmação precisa ser precisa?** “Bloqueamos padrões evidentes antes da API”, não “nenhum dado sensível pode sair”.

## Slide 46 — Seis classes Jev e outras rotas

**Entenda:** O experimento pareado usa apenas `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL`, `UNKNOWN`. Consulta de estado, inspeção de alvo e `MISSION_PREVIEW` são rotas locais anteriores e separadas. Missão composta é analisada por parser determinístico, com confirmação por ação física. **Dica:** responda “seis no experimento Jev; o produto possui outras rotas locais”.

**Fácil**
1. **Quantas classes o Jev experimental escolhe?** Seis.
2. **`MISSION_PREVIEW` é sétima classe?** Não.
3. **Quem monta a missão composta?** Parser/executor determinístico local.

**Médio**
4. **Por que manter seis rótulos?** Permite comparação com o baseline local no corpus congelado.
5. **Consultas de estado geram movimento?** Não; seguem rota de leitura.
6. **Cada passo físico da missão precisa de quê?** Confirmação individual e validação de estado.

**Difícil**
7. **Por que não adicionar classe durante benchmark?** Mudaria contrato e invalidaria comparação congelada.
8. **Jev planejou a missão demonstrada?** Não; parser e executor locais produziram e executaram etapas.
9. **Qual erro de narrativa evitar?** Atribuir ao Jev capacidades novas do Maestro fora do seu `Choice` operacional.

## Slide 47 — `CRITERIA`, parte 1

**Entenda:** Trecho real de `tools/jev_local_proxy.py` com `SPRAY`, `DOCK`, `UNDOCK`. Os critérios pedem comandos explícitos atuais e negam inferir dock/undock de outra ação. Este e o próximo slide formam um único dicionário Python. **Dica:** traduza o sentido; não leia o inglês inteiro.

**Fácil**
1. **Qual arquivo aparece?** `tools/jev_local_proxy.py`, Python.
2. **Quais classes nesta metade?** `SPRAY`, `DOCK`, `UNDOCK`.
3. **O que `SPRAY` representa?** Pedido atual explícito de pulverizar ou tratar área.

**Médio**
4. **Por que “pedido atual”?** Histórico, dúvida e explicação não devem virar ação.
5. **Por que DOCK não é inferido após SPRAY?** Retorno à doca exige comando explícito.
6. **Por que texto dos critérios é parte do experimento?** Alterá-lo modifica a pergunta enviada ao modelo.

**Difícil**
7. **Um critério perfeito garante classificação perfeita?** Não; o modelo pode errar apesar da definição.
8. **Como testar fronteira DOCK/UNDOCK?** Frases negativas, históricas, condicionais e com estado da doca.
9. **Quem ainda valida o estado físico?** Código determinístico, não a classificação textual.

## Slide 48 — `CRITERIA`, parte 2

**Entenda:** `CONFIRM`, `CANCEL` e `UNKNOWN` completam o dicionário. `CONFIRM` só autoriza operação já pendente; o rótulo sozinho não cria uma. `UNKNOWN` cobre dúvidas, histórico, conversa, ruído e instrução injetada. **Dica:** concentre-se no par `CANCEL`/`CONFIRM`; ele explica o `HOLD`.

**Fácil**
1. **Quais classes nesta metade?** `CONFIRM`, `CANCEL`, `UNKNOWN`.
2. **`CANCEL` inicia outra operação?** Não.
3. **O que cobre `UNKNOWN`?** Casos que não cabem nas outras cinco classes.

**Médio**
4. **`CONFIRM` cria ação pendente?** Não; só se aplica a uma já existente.
5. **Por que `UNKNOWN` inclui ruído?** Uma transcrição insegura não deve ser forçada a comando.
6. **Por que separar cancelamento de confirmação?** As consequências operacionais são opostas.

**Difícil**
7. **Que falha apareceu no benchmark?** Um caso esperado `CANCEL` virou `CONFIRM`.
8. **Como mitigar além do classificador?** Estado pendente, confirmação explícita e guard determinístico avaliado separadamente.
9. **Qual pergunta de segurança fazer?** Quantos cancelamentos reais são aceitos incorretamente por contexto e ruído?

## Slide 49 — `request_payload` completo

**Entenda:** Função real do proxy: pega a transcrição, define `state`, modelo fixo, pergunta `operational_intent` do tipo `choice`, instrução e `CRITERIA`. O Android envia antes um JSON menor com `transcript`; a chave fica no proxy. **Dica:** separe claramente “Android → proxy” de “proxy → TypeSafe”.

**Fácil**
1. **Qual função aparece?** `request_payload` em `tools/jev_local_proxy.py`.
2. **O que vira `state`?** A transcrição recebida.
3. **Qual tipo de pergunta?** `choice`.

**Médio**
4. **Onde estão as seis opções?** No dicionário `CRITERIA`, mostrado nos slides anteriores.
5. **Por que fixar `MODEL`?** Reprodutibilidade do experimento.
6. **Que instrução restringe Jev?** Classificar a fala sem resolver alvo, planejar ou autorizar movimento.

**Difícil**
7. **Por que usar proxy?** Manter chave fora do APK e impor validação/gate antes da API.
8. **O proxy impede todo dado privado?** Não; padrões e escopo são mitigação limitada.
9. **O que mudaria se `CRITERIA` fosse editado?** O contrato semântico; benchmark teria de ser refeito.

## Slide 50 — Fixture JSON de resposta

**Entenda:** Recorte sanitizado real de `recovery-045`: esperado `CANCEL`, Jev escolheu `CONFIRM` com probabilidade 0,75 e `confidence` 0,70. `usage.output_tokens=70` reforça a distinção entre token contabilizado e preço de saída. **Dica:** pare neste slide; é a evidência mais importante.

**Fácil**
1. **Qual rótulo era esperado?** `CANCEL`.
2. **Qual foi escolhido?** `CONFIRM`.
3. **Quantos output tokens aparecem?** 70.

**Médio**
4. **Qual probabilidade da escolha?** 0,75 para `CONFIRM`.
5. **`confidence` é igual a 0,75?** Não; na fixture é 0,70.
6. **Por que o caso é grave?** Confirmação errada pode liberar uma operação pendente.

**Difícil**
7. **O JSON sozinho prova que o robô se moveu?** Não; barreiras posteriores ainda existem.
8. **Por que guardar fixture sanitizada?** Permite reproduzir análise sem nova chamada ou texto pessoal.
9. **Que decisão experimental saiu desse caso?** Não promover Jev a autoridade operacional: `HOLD`.

## Slide 51 — Validação em Kotlin

**Entenda:** `JevIntentClassifier.kt` confere rótulo e seis chaves, valores finitos, soma da distribuição, escolha vencedora e limiar. Resposta inválida/timeout cai em `UNKNOWN`. O trecho no slide é ilustrativo do gate; confira o arquivo para detalhes. **Dica:** explique o comportamento de falha, não a sintaxe linha por linha.

**Fácil**
1. **Qual linguagem/arquivo?** Kotlin em `JevIntentClassifier.kt`.
2. **O que ocorre em falha?** Retorna `UNKNOWN`.
3. **Quantas chaves de probabilidade espera?** Seis.

**Médio**
4. **Por que valores precisam ser finitos?** `NaN` ou infinito quebram limiares e comparações.
5. **Por que a soma deve se aproximar de 1?** A distribuição deve representar probabilidades coerentes.
6. **Que limiar operacional aparece?** Probabilidade da escolha abaixo de 0,40 falha fechado.

**Difícil**
7. **O limiar de 0,40 prova segurança?** Não; depende de calibração e custos por classe.
8. **Por que validar escolha vencedora?** Uma escolha que perde para outra contradiz a própria distribuição.
9. **O guard de cancelamento faz parte do benchmark bruto?** Não; fica desligado por padrão e deve ser avaliado separadamente.

## Slide 52 — Comparação no corpus sintético

**Entenda:** Na rodada pareada de 60 falas sintéticas, Jev acertou 54 e o local 48; macro-F1 0,9010 contra 0,8026. Jev remoto teve p95 de cerca de 2,1 s, o local 0,293 ms no host. Esse desenho descreve aquele corpus, não campo ou hardware final. **Dica:** diga “uma rodada sintética” antes dos números.

**Fácil**
1. **Quantos casos?** Sessenta frases sintéticas.
2. **Quantos acertos Jev/local?** 54 e 48, respectivamente.
3. **Qual decisão operacional depois do estudo?** `HOLD`.

**Médio**
4. **Por que macro-F1 complementa acurácia?** Mostra desempenho médio por classe.
5. **O que p95 remoto inclui?** Chamada de serviço e rede no host do ensaio.
6. **ECE 0,0787 prova calibração geral?** Não com apenas 60 casos e uma rodada.

**Difícil**
7. **Por que latências local/remota não são equivalentes?** Diferem em rede, execução e ambiente de medição.
8. **Qual próximo conjunto de dados?** Transcrições reais de ASR, congeladas e sanitizadas, com replicação independente.
9. **Qual pergunta importa mais que “quem ganhou”?** Em que classes ocorreram os erros e qual custo eles têm?

## Slide 53 — Erro crítico e `HOLD`

**Entenda:** Jev teve média melhor, mas aceitou um cancelamento como confirmação. O local teve três aceites inseguros naquele corpus; Jev, um. O critério de segurança impede promoção operacional. **Dica:** diga “a média melhorou, mas uma falha crítica bastou para manter `HOLD`”.

**Fácil**
1. **Qual confusão ocorreu?** `CANCEL → CONFIRM`.
2. **Qual era a probabilidade da escolha errada?** 0,75.
3. **O que significa `HOLD`?** Não adotar Jev como autoridade operacional.

**Médio**
4. **Por que um erro pesa tanto?** Pode transformar retirada de autorização em aceite.
5. **O local foi perfeito?** Não; teve três aceites inseguros no mesmo corpus.
6. **`HOLD` significa Jev inútil?** Não; indica evidência insuficiente para esse papel crítico.

**Difícil**
7. **Que gate testaria para reabrir?** Guard de cancelamento separado, com holdout ASR novo e critério de zero aceite inseguro.
8. **Por que não ajustar no holdout observado?** Contaminaria a avaliação e inflaria o resultado.
9. **Que decisão de arquitetura permanece?** Modelo sugere intenção; estado, alvo e confirmação continuam determinísticos.

## Slide 54 — Demo Maestro + Jev + Gazebo

**Entenda:** Espaço para vídeo ou execução local: Android chama o caminho Jev experimental, mostra intenção e espera confirmação antes do robô simulado. Identifique o que foi executado ao vivo e o que é gravação. **Dica:** narre “fala → classe → confirmação → `Command` → Gazebo” enquanto o vídeo roda.

**Fácil**
1. **Onde está o robô?** No Gazebo.
2. **Que decisão Jev fornece?** Rótulo de intenção operacional.
3. **O que libera comando?** Regras e confirmação explícita.

**Médio**
4. **Por que não chamar isso de uso em campo?** O robô e parte da integração são simulados.
5. **O que observar no app?** Origem da classificação, operação pendente e estado de confirmação.
6. **Como proceder se a internet falhar?** Usar gravação/fixture identificada, sem dizer que houve chamada ao vivo.

**Difícil**
7. **Que evidência comprovaria comando estruturado?** `Command` JSON e registro do bridge, sem dados pessoais.
8. **Por que o erro `CANCEL → CONFIRM` não invalida a barreira?** Classificador pode errar; confirmação e estado ainda precisam ser testados independentemente.
9. **Qual limitação principal da demo?** Não valida câmera/áudio dos óculos físicos nem pulverização real.

## Slide 55 — Reserva de demonstração

**Entenda:** Capturas locais com Wi-Fi desligado mostram estados visuais do app. São fixtures mock: não fazem chamada Jev remota nem executam robô. **Dica:** use apenas se precisar; leia a legenda para evitar confusão.

**Fácil**
1. **É chamada Jev real?** Não; fixture de reserva.
2. **A reserva move o robô?** Não.
3. **Por que existe?** Para manter a demonstração se rede ou vídeo falhar.

**Médio**
4. **O que ela de fato prova?** Como a interface mostra decisão e recusa.
5. **Por que Wi-Fi desligado foi registrado?** Mostra independência da fixture local em relação à rede.
6. **Que rótulos aparecem?** Exemplos de baseline local, Jev `SPRAY` e `UNKNOWN`.

**Difícil**
7. **Que claim seria enganoso?** “Essa tela prova inferência remota e movimento no Gazebo.”
8. **Como apresentar evidências múltiplas?** Separar fixture de UI, chamada remota e execução no bridge.
9. **Qual utilidade científica da reserva?** Nenhuma medição de modelo; é redundância operacional da apresentação.

## Slide 56 — Conclusão

**Entenda:** Jev é uma interface promissora para decisões tipadas; RLCD é objetivo público que pede avaliação reproduzível; o Maestro mostra utilidade potencial e um erro que mantém `HOLD`. A segurança não pertence ao classificador sozinho. **Dica:** feche em três frases, sem introduzir números novos.

**Fácil**
1. **O que Jev trouxe?** Perguntas tipadas e probabilidades para software.
2. **O que RLCD promete?** Melhor qualidade de decisões calibradas, segundo a TypeSafe.
3. **Qual é a decisão do Maestro?** `HOLD` para autoridade operacional de Jev.

**Médio**
4. **Por que o estudo valeu a pena?** Mostrou ganho médio e um erro crítico concreto.
5. **O que fica fora do modelo?** Alvo, estado, confirmação e formação do comando.
6. **Qual próximo passo?** Avaliação com ASR real e critérios de segurança congelados.

**Difícil**
7. **O benchmark confirma RLCD?** Não; avalia um produto, sem isolar seu treinamento.
8. **Uma falha crítica prova que Jev nunca serve?** Não; limita adoção nesse papel sob esta evidência.
9. **Qual conclusão seria forte demais?** “Jev é calibrado e seguro para robôs porque venceu em macro-F1.”

## Slide 57 — O que ainda precisamos testar?

**Entenda:** Três perguntas acessíveis encerram o raciocínio: classificação de transcrições reais, calibração e separação segura entre cancelar/confirmar. Jev recebe texto do ASR, não áudio bruto. **Dica:** deixe a sala escolher uma pergunta para a discussão.

**Fácil**
1. **Jev recebe áudio?** Não nesse fluxo; recebe transcrição.
2. **O corpus principal era de fala real?** Não; eram frases sintéticas.
3. **Qual par precisa de atenção?** `CANCEL` e `CONFIRM`.

**Médio**
4. **O que significa “80% funciona”?** Acertar perto de 80% em muitos casos comparáveis previstos perto de 80%.
5. **Por que ASR muda o problema?** Introduz ruído, cortes, homófonos e variação real de fala.
6. **Que evidência reabriria `HOLD`?** Novos holdouts ASR, replicação e ausência de aceite inseguro sob critérios pré-definidos.

**Difícil**
7. **Como testar sem expor dados pessoais?** Fala voluntária/sanitizada, minimização e avaliação de gate antes de API.
8. **Como isolar efeito do RLCD?** Acesso a treino/ablação controlada além do benchmark do produto.
9. **Qual pergunta fazer ao grupo?** “Que teste vocês exigiriam antes de confiar nessa classe de decisão?”

## Slide 58 — Obrigado

**Entenda:** O slide encerra. Deixe o público escolher entre discussão de RLCD, código `Choice` ou matriz de confusão. **Dica:** não recapitule a palestra inteira.

**Fácil**
1. **O que dizer?** “Obrigado. Posso abrir o contrato, o código ou o erro crítico.”
2. **Qual foi a decisão do estudo?** `HOLD`.
3. **Qual era o foco de RL?** RLCD e a alegação de calibração.

**Médio**
4. **Se pedirem o exemplo mais forte?** Mostre `recovery-045` e explique a consequência potencial.
5. **Se pedirem utilidade do Maestro?** Mostre separação entre fala, alvo, estado e confirmação.
6. **Se perguntarem por “zero tokens”?** Corrija: zero preço anunciado da saída; tokens foram contabilizados.

**Difícil**
7. **Se disserem que 60 casos são pouco?** Concorde; são evidência descritiva para uma decisão conservadora.
8. **Se disserem que RLCD é marketing?** Concorde que falta reprodução pública; proponha os testes que isolariam o método.
9. **Se perguntarem qual modelo é melhor?** Peça tarefa, hardware, métrica e risco; a tabela define comparação futura no Maestro.

## Fontes para revisão

- Jev: [quick start](https://docs.typesafe.ai/introduction/quickstart), [Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), [Score](https://docs.typesafe.ai/primitives/score), [AI primer](https://docs.typesafe.ai/introduction/machine-learning-primer).
- Modelos próximos: [Laya](https://github.com/NandhaKishorM/laya), [laya-mlx](https://github.com/mizorewww/laya-mlx), [Julia-1](https://huggingface.co/SupersonicLabs/Julia-1), [CLM](https://github.com/Contrastive-LM/CLM). Os números externos devem ser lidos com tarefa, hardware e autoria da medição.
- Maestro: [contrato de Choice](choice-contract.md), [métricas do corpus](results/jev-final-recovery-presentation.md), [decisão `HOLD`](../../tasks/jev-experimental-decision.md), [gate de privacidade](../../tasks/jev-remote-privacy-gate.md), [missão composta](../../tasks/mission-preview-contract.md).
