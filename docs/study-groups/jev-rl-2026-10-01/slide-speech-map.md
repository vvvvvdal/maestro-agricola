# Mapa slide → fala

Este mapa acompanha [o PPTX](jev-rl-maestro-v5-2026-10-01.pptx), o [roteiro](presentation-script.md) e o [texto falado](presentation-speech.md). A coluna “fala” indica o argumento oral que motivou o slide; não substitui o texto integral. Os exemplos de terceiros ocupam áreas de vídeo para inserir as gravações originais. O slide 9 contém um print da documentação oficial de `Choice`; o slide 31 mostra um recorte da página 2 das notas públicas sobre agente TypeSafe. Os slides 42 e 43 mostram o JSON de entrada e uma resposta real sanitizada.

| Nº | Slide | Como a fala constrói o slide |
| --- | --- | --- |
| 1 | Título | Abre com a tese: decisões tipadas e probabilísticas para uma interface robótica. |
| 2 | Bot de WhatsApp | A mensagem de cobrança separa a conversa humana da escolha de encaminhamento. |
| 3 | `if` × Jev | Contrasta idade numérica decidida por código com interpretação probabilística de uma frase. |
| 4 | System One | Explica o nome da categoria criada pela TypeSafe, a inspiração em Kahneman e a origem do Jev. |
| 5 | Contrato | A fala explica `state`, `questions`, `Choice`, `Noul`, `Score` e validação posterior. |
| 6 | Tokens | É o primeiro foco: preço anunciado zero para saída não significa zero tokens. |
| 7 | Velocidade | Pede comparação na mesma tarefa, incluindo p95, rede, qualidade e custo do erro. |
| 8 | LLM × Jev | A tabela resume saída, flexibilidade, validação, tokens e uso mais adequado. |
| 9 | Documentação | O print oficial sustenta a explicação de `Choice` e seus campos. |
| 10 | Playground: caso | A turma prevê a escolha para a mensagem sintética de pagamento. |
| 11 | Playground: tela | Reserva a projeção do site autenticado e a leitura da resposta real. |
| 12 | API | O request de exemplo mostra como programar `state`, modelo e pergunta. |
| 13 | RL | Aplica o padrão entrada → sinal → ajuste → saída → limite à recompensa ambiental. |
| 14 | RLHF | Aplica o mesmo padrão às preferências humanas. |
| 15 | RLVR | Aplica o mesmo padrão a um verificador objetivo. |
| 16 | RLCD | Expõe o objetivo público da TypeSafe e a falta de detalhes para reproduzir ou isolar o efeito do treino. |
| 17 | Calibração | Traduz p=0,8 em frequência de acerto em um grupo comparável. |
| 18 | Medidas | Separa escolha correta, calibração das probabilidades e risco de falso aceite. |
| 19 | Comparação RL | A tabela fecha as quatro famílias pelo sinal, objetivo e limite. |
| 20 | Emojis | Primeiro vídeo: texto seleciona emojis de um catálogo; a UI faz o resto. |
| 21 | Skills | Vídeo: pedido seleciona uma skill antes de carregar contexto maior. |
| 22 | PR/tokens | Demo PR Judge: diff limitado vira rota; economia total deve ser medida. |
| 23 | Xadrez | Relato de blitz Jev × Fable × Astra, com resultado e limite do caso. |
| 24 | JevPilot | Ações fechadas em HighwayEnv; a fala frisa que é simulação. |
| 25 | Surgimento de Laya | A fala distingue o modelo aberto Laya do runtime comunitário Laya-MLX e situa a sequência de lançamentos. |
| 26 | Jev × Laya | Compara serviço remoto, pesos locais e medições sem chamar números de ambientes diferentes de confronto direto. |
| 27 | Por que tantos modelos? | Explica reuso de modelos, interfaces e benchmarks, sem presumir treino do zero após Jev. |
| 28 | Julia-1 | Dá destaque à pesquisa brasileira, aos números favoráveis e à falha em Banking77. |
| 29 | CLM | Explica encoders contrastivos, cache de ações e limites do speedup publicado. |
| 30 | Span-01 | Distingue a tarefa de detecção em traces da classificação operacional do Maestro. |
| 31 | Documento público | Exibe a página 2 das notas e distingue as notas compartilhadas por Diogo da síntese de terceiro. |
| 32 | Troca de modelo | Explica por que reler o contexto pode anular a economia de um turno barato. |
| 33 | Contexto dinâmico | Mostra decisões sobre blocos, instruções e ferramentas; o harness monta a janela. |
| 34 | Jev no loop | Localiza decisões tipadas entre observação, política, execução e verificação. |
| 35 | Comparação | Converte anúncios em critérios para um teste pareado no Maestro. |
| 36 | Hackathon | Apresenta AgroTurtles, problema e estágio pré-hardware do MVP. |
| 37 | Ideia | Resume o pitch: olhar, falar e confirmar antes da ação física. |
| 38 | Pipeline | Liga entrada, decisão tipada, regras e estado, confirmação e ROS. |
| 39 | QR | Explica frame sob demanda, decoder local e `target_id`. |
| 40 | Gate remoto | Explica consentimento no mock, bloqueios antes da rede e limite desses filtros. |
| 41 | Seis classes | Esclarece que `MISSION_PREVIEW` e consultas são rotas locais, fora do `Choice` Jev. |
| 42 | JSON enviado | Mostra o pequeno JSON Android → proxy e o `Choice` que o proxy monta para a TypeSafe. |
| 43 | JSON recebido | Mostra a resposta real sanitizada `recovery-045`: `CANCEL` esperado, `CONFIRM` escolhido. |
| 44 | Validação | Explica catálogo, distribuição, limiar e retorno `UNKNOWN` em falha. |
| 45 | Corpus | Traz a rodada pareada de 60 frases e seus limites de inferência. |
| 46 | Erro crítico | O caso `CANCEL → CONFIRM` explica a decisão operacional `HOLD`. |
| 47 | Demo | Espaço para Android, Jev, confirmação e Gazebo ao vivo ou em vídeo. |
| 48 | Reserva | Espaço para gravação offline ou capturas da fixture mock. |
| 49 | Conclusão | Retoma Jev como hipótese útil, RLCD como objetivo a testar e segurança fora do modelo. |
| 50 | Debate | Abre questões sobre treino, ASR real e custo do erro. |
| 51 | Obrigado | Encerra sem informação nova. |

## Pontos de edição antes de apresentar

- Inserir os vídeos originais nos slides 20–24 e a demo própria nos slides 47–48. Os links de origem estão nas notas e no [roteiro](presentation-script.md). Os vídeos originais dos posts continuam pendentes de inserção; o texto dos quatro posts novos foi conferido pelo oEmbed oficial do X.
- No slide 22, o PR Judge é uma demo adicional estudada, não um dos cinco tweets enviados inicialmente.
- O print do slide 9 é da [documentação oficial de Choice](https://docs.typesafe.ai/primitives/choice), capturado em 26/09/2026.
- Para a demo do Playground, usar `state` sintético e ler o resultado real. Nunca projetar credenciais.
