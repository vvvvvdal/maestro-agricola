# Tarefas - Jev e Decisoes com Incerteza

Data alvo: 01/10/2026

Este e o plano executavel do estudo JEV, nao uma promessa imutavel. Ele cobre
da definicao do experimento ate a apresentacao. Uma task fica em andamento por
vez; uma task concluida precisa produzir a evidencia indicada antes de liberar
a proxima.

## Regra de replanejamento

Tasks podem ser divididas, reordenadas, adiadas ou removidas quando uma nova
evidencia, limite de credito, falha de ambiente ou descoberta tecnica justificar
a mudanca. Ao mudar o plano:

1. atualizar este arquivo com data, status, motivo e nova dependencia;
2. preservar o escopo da Fase 1 ou registrar aprovacao humana para amplia-lo;
3. nao esconder uma task nova dentro de outra nem marcar uma task como concluida
   sem sua evidencia;
4. replanejar slides, demo e ensaio se a mudanca alterar uma afirmacao da
   apresentacao.

Nao podem mudar sem decisao humana registrada: teto de US$5, envio de dados a
API, as seis classes iniciais, confirmacao por audio, falha fechada, isolamento
do Qwen e ausencia de RAG neste experimento.

## Criterios globais

- A apresentacao distingue evidencia medida, resultado de terceiros e hipotese.
- O exemplo de xadrez explicita que Fable perdeu no tempo.
- Qualquer demo remota possui captura gravada ou fixture local de reserva.
- Nenhum segredo entra no APK, repositorio, log ou captura.
- Jev nao recebe foto, audio, `Command`, WebSocket, ROS, estado do robo ou
  resolucao de alvo.
- Nenhuma acao fisica ocorre sem a confirmacao por audio e as validacoes atuais.

## Convencoes

- `DONE`: evidencia registrada.
- `NEXT`: unica task que pode iniciar agora.
- `TODO`: aguardando dependencias.
- `BLOCKED`: depende de decisao humana, servico ou ambiente externo.
- Fase 1: somente `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e
  `UNKNOWN`. `STATUS_QUERY`, `PLOT_STATUS_QUERY`, `INSPECT_TARGET` e
  `COMPOUND_MISSION` sao roadmap para slides, nao entregas antes de 01/10.

## Fase 0 - Base do estudo

| ID | Status | Data | Dependencia | Entrega e criterio de aceite |
| --- | --- | --- | --- | --- |
| JEV-00 | DONE | 21/09 | - | Estudo separado de `docs/pitch/`; roteiro tecnico e pasta propria existem. |
| JEV-01 | DONE | 21/09 | - | `test/jev`, preflight, Terra planner/reviewer e worker Gemini condicional via Antigravity CLI read-only configurados. |
| JEV-02 | DONE | 21/09 | JEV-00 | Decisoes iniciais registradas: Jev troca apenas o classificador; Qwen nao recebe filtro Jev e nao ha RAG. |
| JEV-03 | DONE | 22/09 | JEV-02 | Aprovacao, dados permitidos, teto de US$5, subtetos e credencial local registrados em [`../../tasks/jev-api-approval.md`](../../tasks/jev-api-approval.md). Chamadas continuam bloqueadas ate `JEV-40`. |

## Fase 1 - Semantica e corpus

| ID | Status | Data | Dependencia | Entrega e criterio de aceite |
| --- | --- | --- | --- | --- |
| JEV-10 | DONE | 22/09 | JEV-03 | Rubrica de `SPRAY` registrada em [`rubrics.md`](rubrics.md): pedido atual, negacao, historico, hesitacao, alvo sem acao e fronteira de conflito de alvo. Nenhuma chamada Jev ou mudanca operacional. |
| JEV-11 | DONE | 22/09 | JEV-03 | Rubrica de `DOCK` e `UNDOCK` registrada em [`rubrics.md`](rubrics.md): pedidos explicitos, negacao, historico, capacidade, sequencia condicional e estado separado da classificacao. Nenhuma chamada Jev ou mudanca operacional. |
| JEV-12 | DONE | 22/09 | JEV-03 | Rubrica de `CONFIRM`, `CANCEL` e `UNKNOWN` registrada em [`rubrics.md`](rubrics.md): estado pendente, negacao, hesitacao, ruido, conversa, fora de dominio e injecao. Nenhuma chamada Jev ou mudanca operacional. |
| JEV-13 | DONE | 22/09 | JEV-10, JEV-11, JEV-12 | Corpus sintetico de desenvolvimento criado em [`corpus/development.tsv`](corpus/development.tsv): 72 casos, 12 por rotulo, com identificador, texto sanitizado, rotulo ouro e categoria. Nenhuma chamada Jev. |
| JEV-14 | DONE | 22/09 | JEV-13 | Revisao registrada em [`corpus/review.md`](corpus/review.md): 12 casos por rotulo, positivos, fronteiras negativas e ASR para cada classe; sem duplicatas ou dados pessoais. Duas categorias ASR foram explicitadas. |
| JEV-15 | DONE | 22/09 | JEV-10, JEV-11, JEV-12 | Corpus final criado em [`corpus/final.tsv`](corpus/final.tsv): 60 casos, 10 por rotulo, textos distintos do desenvolvimento e manifesto de congelamento em [`corpus/final-manifest.md`](corpus/final-manifest.md). Nenhuma chamada Jev. |
| JEV-16 | DONE | 22/09 | JEV-15 | Matriz de gates registrada em [`safety-gates.md`](safety-gates.md): timeout, baixa probabilidade, `UNKNOWN`, `CANCEL`, conflito e injecao; evidencia do baseline separada de provas Jev pendentes. Teste Kotlin focado passou. |

## Fase 2 - Adaptador, fakes e harness

| ID | Status | Data | Dependencia | Entrega e criterio de aceite |
| --- | --- | --- | --- | --- |
| JEV-20 | DONE | 22/09 | JEV-03 | Contrato minimo em [`choice-contract.md`](choice-contract.md): endpoint, modelo fixo `jev-1.13.0`, uma `Choice`, seis criterios, resposta esperada e limites de dados. Nenhuma chave ou chamada remota. |
| JEV-21 | DONE | 22/09 | JEV-20 | DTO experimental em [`../../tasks/jev-evaluation-dto.md`](../../tasks/jev-evaluation-dto.md): `Choice`, probabilidades, confidence Jev, modelos, uso, latencia, custo e erro, sem alterar `IntentPrediction`. Teste unitario focado incluido. |
| JEV-22 | DONE | 22/09 | JEV-21 | Mapeamento em [`../../tasks/jev-intent-mapping.md`](../../tasks/jev-intent-mapping.md): `choice` vira rotulo, `probabilities[choice]` vira `IntentPrediction.confidence`, confidence Jev fica no benchmark e origem e `JEV`. Teste focado incluido. |
| JEV-23 | DONE | 22/09 | JEV-21 | Politica em [`../../tasks/jev-failure-policy.md`](../../tasks/jev-failure-policy.md): deadline de 2 s, no maximo uma repeticao para `429`/`529`, classificacao de erros e falha fechada sem `Command`. Teste focado incluido. |
| JEV-24 | DONE | 22/09 | JEV-22, JEV-23 | Fake local em [`../../tasks/jev-fake-evaluator.md`](../../tasks/jev-fake-evaluator.md): escolha valida, baixa probabilidade, timeout, `429` e resposta invalida, todos sem rede. Teste focado incluido. |
| JEV-25 | DONE | 22/09 | JEV-24 | Adaptador em [`../../tasks/jev-intent-classifier.md`](../../tasks/jev-intent-classifier.md): seis rotulos, limiar `0,40`, validacao completa da Choice e falha fechada; nao esta ligado ao app nem usa fallback local. Testes focados incluidos. |
| JEV-26 | DONE | 22/09 | JEV-25 | Harness em [`../../tasks/jev-harness.md`](../../tasks/jev-harness.md): executa local e fixture Jev sobre o mesmo corpus, grava uma linha por `id` e hashes, sem texto, rede ou chave. Teste portatil incluido. |
| JEV-27 | DONE | 22/09 | JEV-26 | Calculador em [`../../tasks/jev-metrics.md`](../../tasks/jev-metrics.md): matriz, macro-F1, aceitao perigosa, Brier, ECE, coverage, p50/p95, custo e falhas; fixture so valida pipeline, nao resultado Jev. Teste portatil incluido. |

## Fase 3 - App e experiencia da demonstracao

| ID | Status | Data | Dependencia | Entrega e criterio de aceite |
| --- | --- | --- | --- | --- |
| JEV-30 | TODO | 26/09 | JEV-22 | Adicionar origem `JEV` ao modelo de apresentacao sem alterar semantica de fontes locais. |
| JEV-31 | TODO | 26/09 | JEV-30 | Atualizar `predictionSourceLabel` e o cartao `INTENCAO` para `SPRAY · 87% · Jev`; o percentual e a probabilidade da classe. |
| JEV-32 | TODO | 26/09 | JEV-31 | Cobrir visualmente `SPRAY`, `DOCK`, `UNKNOWN`, timeout e erro; texto deixa claro que `UNKNOWN` nao executou nada. |
| JEV-33 | TODO | 27/09 | JEV-31 | Mostrar vetor e confidence Jev somente em `Ajustes de teste` do `mock`, como diagnostico recolhido. |
| JEV-34 | TODO | 27/09 | JEV-32, JEV-33 | Executar testes unitarios Android focados e inspecao `mockDebug`: cartao compacto, rolagem, semantica e leitura contextual. |

Detalhes de UI e estados: [`../../tasks/jev-ui-decision-visibility.md`](../../tasks/jev-ui-decision-visibility.md).

## Fase 4 - Medicao e decisao experimental

| ID | Status | Data | Dependencia | Entrega e criterio de aceite |
| --- | --- | --- | --- | --- |
| JEV-40 | TODO | 26/09 | JEV-26 | Rodar smoke remoto dentro do subteto de US$0,50; registrar versao, custo e falhas sem ajustar o corpus final. |
| JEV-41 | TODO | 27/09 | JEV-27, JEV-40 | Rodar corpus final uma unica vez dentro do subteto de US$3,00; preservar respostas e erros. |
| JEV-42 | TODO | 27/09 | JEV-41 | Gerar tabela local versus Jev e reliability diagram; separar calibracao medida de limitacoes de tamanho amostral. |
| JEV-43 | TODO | 28/09 | JEV-42 | Escrever decisao experimental: evidencia favoravel, contraria ou inconclusiva. Nenhum resultado promove Jev a producao. |

## Fase 5 - Evidencias e apresentacao

| ID | Status | Data | Dependencia | Entrega e criterio de aceite |
| --- | --- | --- | --- | --- |
| JEV-50 | TODO | 28/09 | JEV-34, JEV-43 | Capturar app em baseline local, Jev `SPRAY` e Jev `UNKNOWN`; cada captura tem fonte e estado. |
| JEV-51 | TODO | 28/09 | JEV-42 | Preparar matriz, reliability diagram e tabela de custo/latencia legiveis; nao ocultar falhas. |
| JEV-52 | TODO | 28/09 | JEV-50 | Gravar demo de reserva ou fixtures locais dos tres fluxos; reproduzir com internet desligada. |
| JEV-53 | TODO | 29/09 | JEV-43, JEV-50, JEV-51 | Escrever roteiro final: RLCD/calibracao, xadrez, casos externos, Maestro e roadmap de classes. |
| JEV-54 | TODO | 29/09 | JEV-53 | Criar slides fora de `docs/pitch/`: 46 minutos de conteudo e quatro de debate; numerar fontes e marcar hipotese versus evidencia. |
| JEV-55 | TODO | 30/09 | JEV-54, JEV-52 | Ensaio 1 cronometrado; registrar cortes e perguntas que exigem explicacao melhor. |
| JEV-56 | TODO | 30/09 | JEV-55 | Ensaio 2 cronometrado com demo de reserva; revisar cada claim contra os resultados registrados. |
| JEV-57 | TODO | 01/10 | JEV-56 | Apresentar usando apenas evidencias medidas; apos o encontro, registrar decisoes tecnicas que realmente mudarem. |

## Pontos de parada

- JEV-03 bloqueia qualquer chamada Jev, JEV-20 a JEV-27 e JEV-40 a JEV-43.
- JEV-15 e JEV-16 bloqueiam a rodada final; nenhum limiar e ajustado depois de
  abrir o corpus final.
- JEV-23 bloqueia o adaptador; timeout ou erro sem falha fechada e bloqueador.
- JEV-34 bloqueia capturas do app; a demonstracao nao usa tela nao validada.
- JEV-43 bloqueia slides que afirmem resultado do Maestro; sem medicao, o slide
  usa somente a arquitetura proposta.
- Classes de roadmap nao autorizam mudanca no contrato ROS antes de uma nova
  task aprovada, especificacao versionada e testes proporcionais ao risco.

## Fora do escopo ate nova decisao

- hardware Meta real e rota de audio dos oculos;
- controle Jev em producao;
- filtro Jev para Qwen e RAG;
- parada de emergencia por reconhecimento de fala;
- navegacao livre, dosagem e acoes agronomicas sem contrato fechado;
- alegar calibracao antes de corpus final rotulado e medido.
