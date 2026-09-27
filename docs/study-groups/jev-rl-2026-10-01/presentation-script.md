# Roteiro: Jev, Reinforcement Learning e decisões calibradas em um sistema robótico

Duração da versão integral: **58 minutos de apresentação + 5 minutos de debate**. A fala integral está em [presentation-speech.md](presentation-speech.md). Para um encontro de 50 minutos, use o percurso de **45 + 5** no [guia de estudo](slide-study-guide.md); não leia o speech inteiro. Este roteiro é a fonte da ordem e dos limites de cada afirmação.

## Tese

Jev oferece uma interface para decisões tipadas e probabilísticas. A TypeSafe chama de RLCD seu objetivo de treino para decisões calibradas, mas não publicou detalhes suficientes para reproduzir o procedimento de treino ou atribuir os resultados só ao método. O Maestro permite testar uma aplicação real dessa interface, com classificador local como baseline e barreiras determinísticas antes do robô.

## Convenção de evidência

- **Oficial:** documentação e anúncio da TypeSafe explicam o contrato e as alegações do fornecedor.
- **Terceiros:** vídeos e posts mostram demos; não são benchmarks controlados.
- **Medido no Maestro:** corpus sintético de 60 falas, uma rodada pareada; não prova campo, Meta Wearables reais nem calibração geral.
- **Implementado no Maestro:** código e contratos da branch `test/jev`; distinguir o Jev experimental das rotas locais de consulta e missão.

## Sequência e mapa de tempo

| Slides | Tempo | Assunto |
| --- | --- | --- |
| 1–6 | 0:00–5:00 | Definição de Jev, System One, bot de WhatsApp, `if` e contrato |
| 7–12 | 5:00–11:00 | `Choice`, `Noul`, `Score`, tokens e LLM × Jev |
| 13–16 | 11:00–15:00 | Documentação, Playground e requisição JSON |
| 17–25 | 15:00–29:00 | RL, RLHF, RLVR, RLCD, calibração e comparação |
| 26–30 | 29:00–34:00 | Cinco demonstrações de Jev |
| 31–36 | 34:00–43:00 | Onda de modelos, Laya, Julia-1, CLM e comparação |
| 37–40 | 43:00–47:00 | Notas do Diogo e Jev em agentes |
| 41–43 | 47:00–50:00 | Hackathon e arquitetura do Maestro |
| 44–53 | 50:00–56:00 | Privacidade, classes, código, resultado e `HOLD` |
| 54–56 | 56:00–58:00 | Demo, reserva e conclusão |
| 57–58 | 58:00–63:00 | Debate e “Obrigado” |

Os tempos são referência para ensaio. Se atrasar, encurtar xadrez e JevPilot. Preservar RLCD, as três saídas do Jev, tokens de saída, erro `CANCEL → CONFIRM` e as barreiras antes do robô.

## Slides 1–16 — Jev antes de RL

1. **Capa.** Título: “Jev, Reinforcement Learning e decisões calibradas em um sistema robótico”.
2. **O que é Jev?** Modelo de decisão da TypeSafe; `state` e perguntas tipadas entram, resultados probabilísticos saem. A aplicação define o catálogo e a consequência.
3. **System One.** Nome da família de decisões rápidas da TypeSafe, inspirado em Kahneman sem equivalência literal à cognição humana. Jev é seu primeiro modelo público; Diogo Almeida trabalhou na OpenAI.
4. **Bot de WhatsApp.** Mensagem sintética de cobrança; a escolha de encaminhamento é distinta da conversa natural.
5. **`if` versus Jev.** Idade estruturada pede `if`; uma frase ambígua pode ser analisada por `Noul`. O exemplo não propõe verificação legal de idade com IA.
6. **Contrato.** `state`, `model`, `questions`, `answers`; código valida e age.
7. **Choice.** Uma entre opções fechadas, com `choice`, distribuição `probabilities` e `confidence`; usar saída de revisão quando o catálogo não for exaustivo.
8. **Noul.** Uma pergunta sim/não retorna `noul=P(sim)` entre 0 e 1, sem `confidence` separado; limiares pertencem ao código.
9. **Score.** Níveis ordenados descritos em `criteria`; `score` pode ficar entre níveis, com probabilidades por nível e `confidence`. Não confundir posição na escala com probabilidade binária.
10. **Tokens.** A TypeSafe anuncia preço zero para `output_tokens`, não inexistência de tokens. Nosso harness contabilizou 69–71 por chamada.
11. **Velocidade e custo.** Comparar qualidade, latência ponta a ponta, rede e custo do erro na mesma tarefa.
12. **LLM × Jev.** Comparar formatos e usos sem sugerir que LLM não possa gerar JSON.
13. **Documentação oficial.** Print de `Choice` com request e resposta.
14. **Playground.** Caso sintético de cobrança e falha de integração; perguntar a previsão da sala.
15. **Área de tela.** Ler resposta real do Playground ou exemplo da documentação se o site falhar.
16. **API.** `POST /v1/systemone`; mostrar JSON completo e a leitura da resposta em código. O exemplo é didático, não arquivo do repo.

## Slides 17–25 — Quatro fontes de sinal e o foco em RLCD

Mesmo esquema nos quatro primeiros: **entrada → sinal de qualidade → ajuste → exemplo → limite**. As siglas não especificam sozinhas um algoritmo inteiro.

17. **RL.** Estado, ação, recompensa do ambiente e política; exemplo de agente em jogo.
18. **RLHF.** Comparações humanas favorecem respostas preferidas; exemplo clássico: pós-treino de modelos de chat, especialmente ChatGPT/InstructGPT. Claude, Grok e DeepSeek são exemplos de *chat models*, mas o slide não afirma que todos usam a mesma receita pública de RLHF.
19. **RLVR.** Verificador dá sinal sobre tarefas com gabarito, como testes de código e matemática; exemplos: modelos de raciocínio nessas tarefas, sem inferir receita exata de um produto específico.
20. **RLCD.** A TypeSafe apresenta Reinforcement Learning for Calibrated Decisions como objetivo de Jev: decisões tipadas e probabilidades que correspondam às frequências. Publicamente não há receita completa do sinal, otimização e ablações para atribuir causalmente o resultado ao treino.
21. **Significado da calibração.** Em muitos casos comparáveis de 80%, esperar perto de 80% de acerto; uma decisão individual ainda pode errar.
22. **Como testar.** Separar acerto da escolha, qualidade da distribuição e erro crítico; congelar corpus, versão e prompt, avaliar por classe e contexto.
23. **Exemplo didático.** Cem previsões a 80%; 80 acertos parecem calibrados nessa faixa, 50 indicam excesso de confiança. Não são dados do Maestro.
24. **Métricas.** Accuracy/macro-F1 para escolha; Brier/ECE/reliability para probabilidade; falsos aceites para risco. N pequeno limita inferência.
25. **Tabela.** RL, RLHF, RLVR e RLCD por fonte do sinal, objetivo e limite.

## Slides 26–58 — Demos, modelos próximos e Maestro

26–30. **Cinco demos.** Emojis, escolha de skill, triagem de PR, xadrez e direção em simulação. São relatos de terceiros; mostrar trecho curto e explicar entrada, catálogo e código ao redor.
31. **Por que surgiram tantos modelos parecidos?** Uma interface clara tornou a tarefa visível; projetos puderam reutilizar encoders, pesos e benchmarks. Proximidade de anúncio não prova treinamento do zero em poucos dias. Comparações de velocidade exigem mesma tarefa e mesmo ambiente.
32. **Laya: origem.** Pesos abertos e contrato de `Choice`, `Score` e `Noul`; `laya-mlx` é um runtime comunitário, não o lançamento original.
33. **Laya: execução local.** Separar checkpoint, interface e runtime. Os 7,39–13,42 ms p50 do README MLX são para M3 Max e pergunta curta com modelo carregado. No Maestro ainda falta medir qualidade, memória, energia e p95 no hardware alvo.
34. **Julia-1.** Projeto brasileiro da Supersonic Labs baseado em mmBERT-small, com 144,3 milhões de parâmetros e execução em CPU/ONNX. Os resultados publicados reutilizam referência Jev de protocolo anterior; não são confronto novo no Maestro.
35. **CLM.** Encoders contrastivos de estado e ação; embeddings de ações conhecidas podem ser guardados. O repositório relata até 9× menor latência em tarefas escolhidas, usando 8B/GPU. Isso não é ranking direto frente ao Jev remoto ou Julia em CPU.
36. **Tabela Jev/Laya/Julia-1/CLM.** Comparar como cada sistema executa e decide. A última linha fixa o teste justo no Maestro: mesmas transcrições, seis classes, macro-F1, Brier/ECE, p95, memória/custo e erros críticos.
37–40. **Notas do Diogo e uso em agentes.** Documento público, custo de reler contexto ao trocar modelos, seleção de contexto e pontos de decisão no loop. Tratar como proposta arquitetural, não benchmark de um agente lançado.
41–43. **Maestro.** Contexto do hackathon, olhar/falar/confirmar e pipeline até o robô simulado.
44–46. **Privacidade e classes.** QR local sob demanda, gate remoto antes da rede e seis classes operacionais do experimento Jev. Consultas e missão composta são rotas locais separadas.
47–48. **`tools/jev_local_proxy.py` · Python.** Seis critérios reais de `CRITERIA`, divididos em dois slides por legibilidade.
49. **`tools/jev_local_proxy.py` · Python.** Função `request_payload` completa: `state`, versão fixa, `Choice`, instrução e catálogo.
50. **`results/jev-final-recovery-fixture.json` · JSON.** Recorte sanitizado `recovery-045`: `CANCEL` esperado, `CONFIRM` escolhido com 0,75; `confidence` 0,70; 70 tokens de saída.
51. **`JevIntentClassifier.kt` · Kotlin.** Validação das seis classes, distribuição e limiar; falha retorna `UNKNOWN`.
52. **Comparação.** n=60 sintético, uma rodada: Jev 54/60 e local 48/60; macro-F1 0,9010 vs 0,8026. p95 remoto 2.100,575 ms vs local 0,293 ms no host. ECE próximo não prova calibração geral.
53. **Erro crítico.** `CANCEL → CONFIRM` com 0,75 mantém adoção operacional em `HOLD`.
54–55. **Demo e reserva.** Execução no Gazebo ou fixture local, cada uma identificada corretamente.
56. **Conclusão.** Interface útil; RLCD pede avaliação reproduzível; Maestro exige barreiras fora do modelo.
57. **O que falta testar?** Transcrições de fala real, calibração e distinção segura entre cancelar e confirmar.
58. **Obrigado.** Fecho simples.

## Claims que devem continuar exatos

- Zero **preço** de output tokens anunciado pela TypeSafe; 69–71 `output_tokens` foram contabilizados no nosso harness.
- `confidence` de `Choice` não é automaticamente `probabilities[choice]`; o adaptador operacional usa esta última em `IntentPrediction`.
- Não atribuir Brier/ECE à recompensa interna do RLCD.
- Emojis, skills, PR, xadrez e JevPilot são demos/relatos de terceiros, com harness diferente.
- `MISSION_PREVIEW` é rota local separada e não participou do benchmark Jev de seis labels.
- QR local e gate de transcrição são minimização preventiva, não anonimização nem conformidade LGPD integral.
- CLM “até 9×” vem dos próprios autores; Julia reutiliza valores de referência Jev. Não são ranking universal.
- A decisão experimental registrada é `HOLD`.

## Fontes

- [TypeSafe Quick start](https://docs.typesafe.ai/introduction/quickstart), [Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), [Score](https://docs.typesafe.ai/primitives/score), [AI primer](https://docs.typesafe.ai/introduction/machine-learning-primer), [anúncio Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), [equipe](https://typesafe.ai/team).
- [Avaliação dos casos externos](external-case-assessment.md) e links individuais nos slides 26–40; [Laya](https://github.com/NandhaKishorM/laya) e [Laya-MLX](https://github.com/mizorewww/laya-mlx).
- [Notas públicas compartilhadas por Diogo](https://docs.google.com/document/d/1G61uUB0FifUnmmrPzFQojZ3KpczYKmXGpgEXDJ2l_Zg/edit), [post original](https://x.com/CompleteSkeptic/status/2101894250401271876), [síntese de terceiro](https://x.com/N01ennn/status/2103818303642689696).
- [Julia-1 oficial](https://supersoniclabs.ia.br/julia-1/), [modelo e protocolo](https://huggingface.co/SupersonicLabs/Julia-1), [CLM](https://github.com/Contrastive-LM/CLM).
- [Contrato de seis labels](choice-contract.md), [comparação JEV-41R](results/jev-final-recovery-presentation.md), [decisão HOLD](../../tasks/jev-experimental-decision.md).
- [Fluxo de dados](../../privacy-data-flow.md), [gate remoto](../../tasks/jev-remote-privacy-gate.md), [missão composta](../../tasks/mission-preview-contract.md), [storyboard do pitch](../../pitch/storyboard.md).
