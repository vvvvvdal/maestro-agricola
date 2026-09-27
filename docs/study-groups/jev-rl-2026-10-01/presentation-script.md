# Roteiro: Jev, Reinforcement Learning e decisões calibradas em um sistema robótico

Duração alvo: **58 minutos de apresentação + 5 minutos de debate**. A fala integral está em [presentation-speech.md](presentation-speech.md). Este roteiro é a fonte da ordem e dos limites de cada afirmação.

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
| 31–41 | 34:00–43:00 | Laya, Julia-1, CLM, Span-01 e Jev em agentes |
| 42–44 | 43:00–46:00 | Hackathon e arquitetura do Maestro |
| 45–52 | 46:00–54:00 | Privacidade, seis classes, código real e fixture |
| 52–54 | 54:00–56:00 | Validação, benchmark e decisão `HOLD` |
| 55–57 | 56:00–58:00 | Demo, reserva e conclusão |
| 58–59 | 58:00–63:00 | Debate e “Obrigado” |

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

## Slides 26–57 — Demos, cenário e Maestro

Os slides 26–47 preservam os exemplos e comparações da versão anterior. A ordem agora é: cinco demos (26–30), Laya (31–32), outros modelos e Jev em agentes (33–41), Maestro (42–47).

48–49. **`tools/jev_local_proxy.py` · Python.** Mostrar os seis textos reais de `CRITERIA`, divididos em dois slides por legibilidade. A divisão visual não altera o dicionário do arquivo.
50. **`tools/jev_local_proxy.py` · Python.** Mostrar a função `request_payload` completa, com `state`, versão fixa, pergunta `choice`, instrução e `CRITERIA`. O Android envia antes somente `{"transcript":"..."}` ao proxy.
51. **`results/jev-final-recovery-fixture.json` · JSON.** Resposta sanitizada `recovery-045`: `CANCEL` esperado, `CONFIRM` escolhido, probabilidade 0,75, `confidence` 0,70 e 70 tokens de saída.
52. **`JevIntentClassifier.kt` · Kotlin.** Validação das seis classes, distribuição e limiar; falha retorna `UNKNOWN`.
53. **Comparação.** n=60 sintético, uma rodada: Jev 54/60 e local 48/60; macro-F1 0,9010 vs 0,8026. p95 remoto 2.100,575 ms vs local 0,293 ms no host. ECE próximo não prova calibração geral.
54. **Erro crítico.** `CANCEL → CONFIRM` com 0,75 leva à decisão `HOLD`.
55–56. **Demo e reserva.** Execução no Gazebo ou fixture local explicitamente identificada.
57. **Conclusão.** Interface útil; RLCD pede avaliação reproduzível; Maestro exige barreiras fora do modelo.
58. **Debate.** Perguntas sobre treino, efeito causal, ASR real e risco.
59. **Obrigado.** Fecho simples.

## Claims que devem continuar exatos

- Zero **preço** de output tokens anunciado pela TypeSafe; 69–71 `output_tokens` foram contabilizados no nosso harness.
- `confidence` de `Choice` não é automaticamente `probabilities[choice]`; o adaptador operacional usa esta última em `IntentPrediction`.
- Não atribuir Brier/ECE à recompensa interna do RLCD.
- Emojis, skills, PR, xadrez e JevPilot são demos/relatos de terceiros, com harness diferente.
- `MISSION_PREVIEW` é rota local separada e não participou do benchmark Jev de seis labels.
- QR local e gate de transcrição são minimização preventiva, não anonimização nem conformidade LGPD integral.
- CLM “até 9×” e Span-01 F1 vêm dos próprios autores; Julia reutiliza valores de referência Jev. Não são ranking universal.
- A decisão experimental registrada é `HOLD`.

## Fontes

- [TypeSafe Quick start](https://docs.typesafe.ai/introduction/quickstart), [Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), [Score](https://docs.typesafe.ai/primitives/score), [AI primer](https://docs.typesafe.ai/introduction/machine-learning-primer), [anúncio Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), [equipe](https://typesafe.ai/team).
- [Avaliação dos casos externos](external-case-assessment.md) e links individuais nos slides 26–41; [Laya](https://github.com/NandhaKishorM/laya) e [Laya-MLX](https://github.com/mizorewww/laya-mlx).
- [Notas públicas compartilhadas por Diogo](https://docs.google.com/document/d/1G61uUB0FifUnmmrPzFQojZ3KpczYKmXGpgEXDJ2l_Zg/edit), [post original](https://x.com/CompleteSkeptic/status/2101894250401271876), [síntese de terceiro](https://x.com/N01ennn/status/2103818303642689696).
- [Julia-1 oficial](https://supersoniclabs.ia.br/julia-1/), [modelo e protocolo](https://huggingface.co/SupersonicLabs/Julia-1), [CLM](https://github.com/Contrastive-LM/CLM), [Span-01](https://www.respan.ai/blog/introducing-span-1).
- [Contrato de seis labels](choice-contract.md), [comparação JEV-41R](results/jev-final-recovery-presentation.md), [decisão HOLD](../../tasks/jev-experimental-decision.md).
- [Fluxo de dados](../../privacy-data-flow.md), [gate remoto](../../tasks/jev-remote-privacy-gate.md), [missão composta](../../tasks/mission-preview-contract.md), [storyboard do pitch](../../pitch/storyboard.md).
