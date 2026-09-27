# Mapa slide → fala

Este mapa acompanha [o PPTX](jev-rl-maestro-v8-2026-10-01.pptx), o [roteiro](presentation-script.md) e o [texto falado](presentation-speech.md). Os exemplos externos continuam com áreas para vídeo. Os slides 47–49 mostram código do proxy com nomes de arquivo; o 50 mostra fixture JSON.

| Nº | Slide | Como a fala constrói o slide |
| --- | --- | --- |
| 1 | Título | Abre com a tese: decisões tipadas e probabilísticas para uma interface robótica. |
| 2 | O que é Jev? | Define estado, perguntas tipadas, resposta probabilística e papel do código. |
| 3 | System One | Explica o nome da categoria criada pela TypeSafe, a inspiração em Kahneman e a origem do Jev. |
| 4 | Bot de WhatsApp | A mensagem de cobrança separa a conversa humana da escolha de encaminhamento. |
| 5 | `if` × Jev | Contrasta idade numérica decidida por código com interpretação probabilística de uma frase. |
| 6 | Contrato | A fala explica `state`, `questions`, `Choice`, `Noul`, `Score` e validação posterior. |
| 7 | Choice | A fala mostra escolha fechada, probabilidades, confidence e opção de revisão. |
| 8 | Noul | A fala distingue P(sim) de intensidade e coloca o limiar no código. |
| 9 | Score | A fala explica escala ordenada, score entre níveis e distribuição por nível. |
| 10 | Tokens | É o primeiro foco: preço anunciado zero para saída não significa zero tokens. |
| 11 | Velocidade | Pede comparação na mesma tarefa, incluindo p95, rede, qualidade e custo do erro. |
| 12 | LLM × Jev | A tabela resume saída, flexibilidade, validação, tokens e uso mais adequado. |
| 13 | Documentação | O print oficial sustenta a explicação de `Choice` e seus campos. |
| 14 | Playground: caso | A turma prevê a escolha para a mensagem sintética de pagamento. |
| 15 | Playground: tela | Reserva a projeção do site autenticado e a leitura da resposta real. |
| 16 | API | O request de exemplo mostra como programar `state`, modelo e pergunta. |
| 17 | RL | Aplica o padrão entrada → sinal → ajuste → saída → limite à recompensa ambiental. |
| 18 | RLHF | Aplica o mesmo padrão às preferências humanas. |
| 19 | RLVR | Aplica o mesmo padrão a um verificador objetivo. |
| 20 | RLCD | Expõe o objetivo público da TypeSafe e a falta de detalhes para reproduzir ou isolar o efeito do treino. |
| 21 | RLCD: calibração | Distingue acerto de estimativa honesta de probabilidade em grupos comparáveis. |
| 22 | RLCD: teste | Apresenta métricas, classes críticas e necessidade de isolar o efeito do treino. |
| 23 | Calibração | Traduz p=0,8 em frequência de acerto em um grupo comparável. |
| 24 | Medidas | Separa escolha correta, calibração das probabilidades e risco de falso aceite. |
| 25 | Comparação RL | A tabela fecha as quatro famílias pelo sinal, objetivo e limite. |
| 26 | Emojis | Primeiro vídeo: texto seleciona emojis de um catálogo; a UI faz o resto. |
| 27 | Skills | Vídeo: pedido seleciona uma skill antes de carregar contexto maior. |
| 28 | PR/tokens | Demo PR Judge: diff limitado vira rota; economia total deve ser medida. |
| 29 | Xadrez | Relato de blitz Jev × Fable × Astra, com resultado e limite do caso. |
| 30 | JevPilot | Ações fechadas em HighwayEnv; a fala frisa que é simulação. |
| 31 | Por que tantos modelos? | Abre a onda de modelos antes de apresentar cada projeto. |
| 32 | Laya: origem | Distingue pesos abertos, contrato e runtime MLX. |
| 33 | Laya: execução local | Explica execução local e as medidas que faltam no Android. |
| 34 | Julia-1 | Dá destaque à pesquisa brasileira, aos números favoráveis e à falha em Banking77. |
| 35 | CLM | Explica encoders contrastivos, cache de ações e limites do speedup publicado. |
| 36 | Jev, Laya, Julia-1 e CLM | Compara quatro modelos e define o teste justo no Maestro. |
| 37 | Documento público | Exibe a página 2 das notas e distingue as notas compartilhadas por Diogo da síntese de terceiro. |
| 38 | Troca de modelo | Explica por que reler o contexto pode anular a economia de um turno barato. |
| 39 | Contexto dinâmico | Mostra decisões sobre blocos, instruções e ferramentas; o harness monta a janela. |
| 40 | Jev no loop | Localiza decisões tipadas entre observação, política, execução e verificação. |
| 41 | Hackathon | Apresenta AgroTurtles, problema e estágio pré-hardware do MVP. |
| 42 | Ideia | Resume o pitch: olhar, falar e confirmar antes da ação física. |
| 43 | Pipeline | Liga entrada, decisão tipada, regras e estado, confirmação e ROS. |
| 44 | QR | Explica frame sob demanda, decoder local e `target_id`. |
| 45 | Gate remoto | Explica consentimento no mock, bloqueios antes da rede e limite desses filtros. |
| 46 | Seis classes | Esclarece que `MISSION_PREVIEW` e consultas são rotas locais, fora do `Choice` Jev. |
| 47 | Critérios Python 1/2 | Mostra SPRAY, DOCK e UNDOCK reais do proxy. |
| 48 | Critérios Python 2/2 | Mostra CONFIRM, CANCEL e UNKNOWN reais do proxy. |
| 49 | `request_payload` Python | Mostra a função completa que transforma a transcrição em uma pergunta `Choice`. |
| 50 | Fixture JSON | Mostra a resposta real sanitizada `recovery-045`: `CANCEL` esperado, `CONFIRM` escolhido. |
| 51 | `JevIntentClassifier.kt` Kotlin | Explica catálogo, distribuição, limiar e retorno `UNKNOWN` em falha. |
| 52 | Corpus | Traz a rodada pareada de 60 frases e seus limites de inferência. |
| 53 | Erro crítico | O caso `CANCEL → CONFIRM` explica a decisão operacional `HOLD`. |
| 54 | Demo | Espaço para Android, Jev, confirmação e Gazebo ao vivo ou em vídeo. |
| 55 | Reserva | Espaço para gravação offline ou capturas da fixture mock. |
| 56 | Conclusão | Retoma Jev como hipótese útil, RLCD como objetivo a testar e segurança fora do modelo. |
| 57 | O que falta testar? | Traduz as pendências em fala real, calibração e distinção entre cancelar e confirmar. |
| 58 | Obrigado | Encerra sem informação nova. |
