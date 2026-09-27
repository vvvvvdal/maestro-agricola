# Roteiro: Jev, Reinforcement Learning e decisões calibradas em um sistema robótico

Duração alvo: **49 minutos de apresentação + 5 minutos de debate**. A fala integral está em [presentation-speech.md](presentation-speech.md). Este roteiro é a fonte da ordem e dos limites de cada afirmação.

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
| 1–4 | 0:00–4:00 | Problema do bot de WhatsApp, `if` e Jev, origem |
| 5–9 | 4:00–9:00 | Primitivas, tokens, LLM x Jev e documentação oficial |
| 10–12 | 9:00–13:00 | Playground ao vivo e request em código |
| 13–19 | 13:00–25:00 | RL, RLHF, RLVR, RLCD, calibração, avaliação e comparação |
| 20–24 | 25:00–30:00 | Emojis, skills, PR, xadrez e JevPilot |
| 25–26 | 30:00–32:00 | Surgimento de Laya e comparação com Jev |
| 27–32 | 32:00–36:00 | Julia-1, CLM, Span-01, Jev em agentes e comparação justa |
| 33–35 | 36:00–39:00 | Hackathon, ideia do Maestro, jornada e arquitetura |
| 36–41 | 39:00–44:00 | QR, barreira remota, seis labels/rotas locais e JSON real |
| 42–43 | 44:00–46:00 | Resultado, erro crítico e decisão `HOLD` |
| 44–46 | 46:00–49:00 | Demo, reserva e conclusão |
| 47–48 | 49:00–54:00 | Debate e “Obrigado” |

Se atrasar, encurtar xadrez e JevPilot. Preservar tokens de saída, RLCD, erro `CANCEL → CONFIRM`, distinção das seis classes e barreiras antes do robô.

## Slides 1–12 — Jev antes do Maestro

1. **Capa.** Título exato: “Jev, Reinforcement Learning e decisões calibradas em um sistema robótico”. Fundo branco, acentos azul claro TypeSafe, amarelo e verde Maestro.
2. **Bot de WhatsApp.** Mensagem sintética chega. O bot conversa como humano, mas precisa decidir um encaminhamento específico: técnico, financeiro, comercial ou humano. O exemplo esclarece a diferença entre comportamento conversacional e decisão de roteamento. Não apresentar como produto existente.
3. **`if` versus Jev.** Código determinístico `if (idade >= 18) "sim" else "não"`. Ao lado, uma pergunta `Noul` sobre uma frase em linguagem natural e um resultado probabilístico de sim/não. Não usar Jev para calcular uma idade numérica já disponível: a comparação serve para mostrar quando a entrada é ambígua ou textual. Se a idade estruturada existe, preferir `if`.
4. **System One.** Nome dado pela TypeSafe à classe de modelos de decisões rápidas e tipadas. Inspiração no Sistema 1 de Kahneman, sem equivalência científica com cognição humana. Jev é o primeiro modelo público da empresa. Diogo Almeida trabalhou na OpenAI; currículo não substitui avaliação.
5. **Contrato.** `state`, `questions` e `answers`; `Choice`, `Noul`, `Score`. `Choice` devolve `choice`, `probabilities` e `confidence`; `Noul` devolve probabilidade de sim e não o mesmo `confidence`.
6. **Tokens.** Jev não gera prosa token a token. A documentação mostra `output_tokens`; nossa fixture registra 69–71 por chamada. A TypeSafe anuncia **preço zero para tokens de saída**, não zero tokens ou chamada gratuita.
7. **Velocidade/custo.** Alegações do fornecedor em workflows próprios; comparar mesma tarefa, qualidade, p95, rede e custo do erro. Não transferir multiplicadores promocionais ao Maestro.
8. **Tabela LLM x Jev.** Entrada, saída, flexibilidade, validação, custo/latência e melhor caso de uso. JSON mode em LLM reduz o problema de formato, mas a política e os testes continuam necessários.
9. **Documentação oficial.** Usar a página [Choice](https://docs.typesafe.ai/primitives/choice) como referência visual principal: definição e campos de request/response. [Quick start](https://docs.typesafe.ai/introduction/quickstart) fundamenta Playground e API. O slide traz print da página oficial capturado em 26/09/2026. Não copiar API key.
10. **Playground.** `state` sintético sobre falha de integração de pagamentos; `Choice` de departamento com quatro opções e critérios. Perguntar a previsão da sala antes de executar. Ler a resposta real, sem número pré-fixado.
11. **Área para tela ao vivo.** Playground da TypeSafe autenticado. Se indisponível, usar o request/response publicados no quick start e nomeá-los como exemplo da documentação.
12. **API.** Mostrar `POST /v1/systemone` ou `client.system_one` com `state`, `model`, `questions`. O código da aplicação lê `answers["departamento"]`, valida e roteia. Em benchmark, fixar e registrar a versão.

## Slides 13–19 — Mesmo esquema para quatro famílias

Usar a mesma matriz em RL, RLHF, RLVR e RLCD: **entrada → sinal de qualidade → ajuste da política → saída esperada → limite da inferência**. Siglas descrevem famílias/objetivos, não uma receita única.

13. **RL básico.** Estado `s`, ação `a`, recompensa `r`, próximo estado `s'`. Política `π(a|s)` otimiza retorno esperado. O sinal é a recompensa do ambiente.
14. **RLHF.** Comparações humanas alimentam sinal de preferência/reward model em uma variante clássica; política favorece respostas preferidas. Preferência não mede, por si, calibração.
15. **RLVR.** Verificador relativamente objetivo, como teste executável ou resposta matemática; política favorece respostas verificadas. Acerto verificável não garante probabilidades calibradas.
16. **RLCD.** Objetivo público anunciado pela TypeSafe: decisões tipadas com probabilidades calibradas. A TypeSafe descreve o objetivo, mas não mostra detalhes suficientes do treino para que possamos reproduzi-lo ou separar o efeito do RLCD do efeito da arquitetura e da forma de gerar as respostas. Não inventar a função de recompensa.
17. **Calibração do zero.** Juntar previsões em que a probabilidade da escolha é próxima de 80%. Se aproximadamente 80 de 100 estiverem corretas, essa faixa parece calibrada. Se só 50 estiverem, há excesso de confiança. Exemplo didático, não dado do Maestro.
18. **O que medir.** Accuracy/macro-F1 para escolha; Brier/ECE/reliability para probabilidades; falsos aceites para risco. Mostrar visual simples, com eixos e bins `n`, e ressalva de amostra pequena.
19. **Tabela de comparação.** RL, RLHF, RLVR e RLCD por fonte do sinal, comportamento buscado, como avaliar e limite. RLCD é uma alegação específica do fornecedor, não uma prova de superioridade.

## Slides 20–26 — Cinco demos e Laya

Cada demo tem a mesma pergunta oral: **o que entra, qual é o catálogo e o que o código faz depois?** O vídeo ocupa a área principal do slide; legenda curta identifica resultado de terceiro e limite. Os links ficam nas notas. Vídeos não verificados ou indisponíveis permanecem como área de inserção, sem simulação falsa.

20. **Emojis primeiro.** [Stefan](https://x.com/heystefan_/status/2101369117496521042): texto digitado altera quais emojis de um conjunto existente ficam em evidência. Exemplo visual de seleção rápida; UI/física dos emojis é código, não saída livre do Jev. O post tem vídeo; não atribuir arquitetura interna não publicada.
21. **Skills.** [Daniel Avila](https://x.com/dani_avila7/status/2101885477158547753): Jev escolhe skill para carregar antes de contexto maior. Incluir `NONE`, medir falso descarte e custo da chamada.
22. **PR/tokens.** [PR Judge](https://jevtypesafeai.com/tools/pr-judge): diff limitado vira encaminhamento `SAFE/REVIEW/BLOCK`; não lê repo inteiro nem executa testes. Economia de tokens é hipótese do fluxo: medir o total e a qualidade da revisão. Este exemplo vem da demo estudada, não de um dos tweets originais.
23. **Xadrez.** [thread republicada](https://threadnavigator.com/thread/2100372930282573876/): Jev venceu Fable 5.1 **no tempo** em blitz 5+0, uma chamada por lance e sem busca; Astra deu mate em 18. Não fazer ranking de força.
24. **JevPilot.** [Justin Schroeder](https://x.com/jpschroeder/status/2100347770867458384): HighwayEnv, estado simbólico, ações fechadas e freio em código. Simulação, não Tesla real, câmera real ou direção validada.
25. **Surgimento de Laya.** Jev foi anunciado em 15/09/2026. Laya apareceu poucos dias depois como implementação com pesos abertos da mesma ideia de perguntas tipadas. `laya-mlx` é um runtime comunitário para Apple Silicon, não o lançamento original de Laya.
26. **Jev × Laya.** Ambos respondem `Choice`, `Score` e `Noul`. Jev é API remota; Laya pode rodar localmente. O runtime MLX reporta p50 de 7,39–13,42 ms no M3 Max para uma pergunta curta, com modelo carregado. Nós medimos Jev no corpus do Maestro; não medimos Laya nele. Portanto, não declarar vencedor.

## Slides 27–32 — A onda de modelos de decisão

27. **Por que a onda apareceu?** Jev popularizou uma interface clara, mas os projetos têm bases, tamanhos, tarefas e modos de execução diferentes. O anúncio próximo no calendário não prova que todos foram treinados do zero em poucos dias. Modelos prévios e benchmarks públicos encurtam o caminho; a conclusão é inferência baseada nos materiais publicados.
28. **Julia-1, do Brasil.** Supersonic Labs se identifica como brasileira. Julia-1 adapta mmBERT-small para decisões entre 2 e 20 opções, com 144,3 milhões de parâmetros e execução em CPU. O grupo reporta 73,15% contra referência Jev de 72,70% em typed decisions, mas 64% contra 87% em Banking77. A referência Jev foi herdada do protocolo, não reexecutada pela equipe; falta pt-BR e corpus Maestro.
29. **CLM (Stanford/NVIDIA).** Encoders de estado e ação treinados por objetivo contrastivo; embeddings de ações podem ser guardados e reutilizados. O repositório relata até 9× menor latência em tarefas escolhidas. O post no X fala em 13×; usar a descrição do repositório e explicar hardware, cache e tarefa. Há autores afiliados a Stanford e NVIDIA; isso não significa anúncio de produto NVIDIA.
30. **Span-01.** Respan criou um modelo de 4B especializado em detectar comportamentos em traces de agentes. A empresa publica F1 0,843 para Span-01 e 0,715 para Jev no seu benchmark. É avaliação conduzida pelo fornecedor em tarefa específica. A provocação sobre multiplicação no post não é comparação válida de classificação.
31. **Jev como peça de um agente.** O post compartilhado resume um PDF atribuído ao fundador da TypeSafe. Mostrar o padrão: o agente reúne contexto e opções; Jev escolhe rota/skill/ferramenta; o harness executa e observa. Não atribuir ao Jev todo o planejamento nem citar detalhes do PDF sem o original.
32. **Tabela de adequação.** Jev, Laya, Julia-1, CLM e Span-01 têm vantagens publicadas para usos distintos. No Maestro, repetir o mesmo corpus de seis classes com ASR real, medir erros críticos, p95, memória, privacidade e custo total antes de escolher.

## Slides 33–46 — Maestro: produto, fronteiras e experimento

33. **Contexto do hackathon.** Programa AI Glasses Brasil 2026, equipe AgroTurtles, MVP pré-hardware. Adaptar a abertura do pitch: máquina autônoma, interface de operador ainda dependente de tela. Não mostrar imagem ilustrativa como evidência física.
34. **Ideia.** “Olhar, falar, confirmar”: alvo por QR/marcador ou talhão mapeado, fala da ação, confirmação por áudio. Adaptar o slide de jornada do pitch.
35. **Arquitetura.** DAT/MockDeviceKit → Android/Kotlin → decisão de intenção + TargetResolver → regras/estado → confirmação → `Command` JSON → WebSocket/ROS 2/Nav2/Gazebo. Adaptar o slide de arquitetura do pitch. No evento, câmera/áudio dos óculos reais seguem gate físico.
36. **QR e minimização.** Foto sob demanda, frame em memória, decoder local, `target_id`; não persistir foto, áudio ou transcrição por padrão. Classificação de fala é fluxo separado.
37. **Gate remoto.** No `mockDebug`, consentimento de sessão revogável; app e proxy bloqueiam antes da rede padrões evidentes de CPF/CNPJ, e-mail, telefone, URL, texto longo e fala fora do escopo. Teste no SM-X510 com CPF sintético. Não chamar isso de anonimização ou conformidade LGPD integral. `LocalIntentClassifier` não é detector geral de CPF.
38. **Seis labels e outras rotas.** Jev compara só `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL`, `UNKNOWN`. `PLOT_STATUS_QUERY`, `STATUS_QUERY`, `INSPECT_TARGET` e `MISSION_PREVIEW` são rotas locais separadas. Missão composta foi executada no Gazebo por parser/executor determinísticos, com confirmação individual por ação física. Não é sétima classe Jev.
39. **JSON de entrada.** Android envia `{"transcript":"<fala>"}` ao proxy local. O proxy monta `state`, `model: jev-1.13.0` e `questions.operational_intent` de tipo `choice`, com critérios para as seis classes. O slide abrevia os textos dos critérios para caber; a estrutura está em `tools/jev_local_proxy.py`.
40. **JSON de resposta.** Mostrar `recovery-045`, retirado da fixture sanitizada: rótulo esperado `CANCEL`, escolha `CONFIRM`, `probabilities["CONFIRM"]=0,75`, `confidence=0,70` e 70 `output_tokens`. É uma resposta real de teste, não uma chamada nova.
41. **Validação.** `JevIntentClassifier` verifica as seis chaves, probabilidades finitas que somam aproximadamente 1, escolha vencedora e limiar 0,40; falha retorna `UNKNOWN`. O guard de cancelamento explícito fica desligado por padrão no benchmark bruto.
42. **Comparação.** n=60 sintético, uma rodada: Jev 54/60, macro-F1 0,9010; local 48/60, macro-F1 0,8026. p95 remoto 2.100,575 ms vs local 0,293 ms no host; US$0,001472394 para 60 chamadas. ECE 0,0787 vs 0,0810 não demonstra calibração geral.
43. **Erro crítico/HOLD.** `CANCEL → CONFIRM` com probabilidade da escolha 0,75 no Jev. A decisão de adoção operacional permanece `HOLD`, apesar da média melhor.
44. **Demo ao vivo/vídeo.** Área grande para Android + Jev + confirmação + Gazebo. Identificar se é ao vivo ou gravação; sem alegar uso em campo.
45. **Reserva.** Área para vídeo offline ou três capturas `results/offline-demo`; se usar estas, legenda obrigatória “fixture mock local — não executa o robô”.
46. **Conclusão.** Jev é uma hipótese útil de classificação tipada. A alegação de calibração pede avaliação reproduzível. O Maestro exige alvo, estado, confirmação, contrato e testes fora do modelo.
47. **Debate.** Perguntar como o modelo foi treinado, que comparação isolaria o efeito desse treino e que amostra com ASR real seria necessária; discutir custo do erro e evidência para reabrir `HOLD`.
48. **Obrigado.** Fecho simples, sem informação nova.

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

- [TypeSafe Quick start](https://docs.typesafe.ai/introduction/quickstart), [Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), [AI primer](https://docs.typesafe.ai/introduction/machine-learning-primer), [anúncio Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), [equipe](https://typesafe.ai/team).
- [Avaliação dos casos externos](external-case-assessment.md) e links individuais nos slides 20–32; [Laya](https://github.com/NandhaKishorM/laya) e [Laya-MLX](https://github.com/mizorewww/laya-mlx).
- [Julia-1 oficial](https://supersoniclabs.ia.br/julia-1/), [modelo e protocolo](https://huggingface.co/SupersonicLabs/Julia-1), [CLM](https://github.com/Contrastive-LM/CLM), [Span-01](https://www.respan.ai/blog/introducing-span-1), [post sobre Jev em agentes](https://x.com/N01ennn/status/2103818303642689696).
- [Contrato de seis labels](choice-contract.md), [comparação JEV-41R](results/jev-final-recovery-presentation.md), [decisão HOLD](../../tasks/jev-experimental-decision.md).
- [Fluxo de dados](../../privacy-data-flow.md), [gate remoto](../../tasks/jev-remote-privacy-gate.md), [missão composta](../../tasks/mission-preview-contract.md), [storyboard do pitch](../../pitch/storyboard.md).
