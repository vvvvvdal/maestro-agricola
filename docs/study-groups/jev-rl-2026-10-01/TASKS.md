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
| JEV-30 | DONE | 22/09 | JEV-22 | `predictionSourceLabel` reconhece `JEV` como `Jev`, preservando fontes locais e fallback. Teste de apresentacao incluido. |
| JEV-31 | DONE | 22/09 | JEV-30 | O cartao `INTENCAO` existente usa `predictionDetail`: `SPRAY · 87% · Jev` e `DOCK · 91% · Jev`, com a probabilidade da classe e arredondamento consistente. Teste de apresentacao incluido. |
| JEV-32 | DONE | 22/09 | JEV-31 | Estados visuais para `SPRAY`, `DOCK`, `UNKNOWN` e indisponibilidade fechada; texto explicita que nenhum comando foi enviado. |
| JEV-33 | DONE | 22/09 | JEV-31 | Diagnostico recolhido no `mock`: vetor ordenado e confidence Jev em fixture local; `dat` recebe `null`. Testes incluidos. |
| JEV-34 | DONE | 22/09 | JEV-32, JEV-33 | Testes focados, `assembleMockDebug` e inspecao no SM-X510 em paisagem: cartao, rolagem e arvore de acessibilidade aprovados. TalkBack audivel e complementar. |
| JEV-35 | DONE | 22/09 | JEV-34 | Wordmark limitado a viewport responsivo de 480 x 88 dp, sem corte em paisagem e retrato no SM-X510 em `mockDebug`. |
| JEV-36 | DONE | 22/09 | JEV-34 | `mock` tem selecao explicita de baseline, Jev `SPRAY` e Jev `UNKNOWN`; a selecao so altera o cartao `INTENCAO`. `dat`, classificador local, jornada, transporte e comandos permanecem inalterados. |

Detalhes de UI e estados: [`../../tasks/jev-ui-decision-visibility.md`](../../tasks/jev-ui-decision-visibility.md).

## Fase 4 - Medicao e decisao experimental

| ID | Status | Data | Dependencia | Entrega e criterio de aceite |
| --- | --- | --- | --- | --- |
| JEV-40 | DONE | 22/09 | JEV-26 | Smoke remoto executado uma vez com 6 casos: `jev-1.13.0`, 6/6 acertos, 0 falhas, US$0,000146832 e p95 de 1.694,136 ms. Evidencia sanitizada em [`../../tasks/jev-remote-smoke.md`](../../tasks/jev-remote-smoke.md); nao ajustou o corpus final. |
| JEV-41 | BLOCKED | 22/09 | JEV-27, JEV-40 | O corpus `final.tsv` foi reservado, mas nao gerou fixture; nao pode ser repetido. Registro em [`../../tasks/jev-final-evaluation.md`](../../tasks/jev-final-evaluation.md). |
| JEV-41A | DONE | 22/09 | JEV-41 | Incidente registrado: reserva existente, fixture ausente e uso remoto indeterminado; nenhum corpus ou reserva original foi alterado. |
| JEV-41R | DONE | 22/09 | JEV-27, JEV-40, JEV-41A | Rodada unica no corpus independente: Jev 54/60, 1 aceite inseguro, US$0,001472394 e p95 de 2.100,575 ms. Evidencia em [`../../tasks/jev-final-recovery-evaluation.md`](../../tasks/jev-final-recovery-evaluation.md); nenhuma repeticao autorizada. |
| JEV-42 | DONE | 22/09 | JEV-41R | Tabela, matrizes, fonte sanitizada e reliability diagram gerados a partir das metricas, com `n=60`, limites e aceite inseguro explicitos. Evidencia em [`../../tasks/jev-presentation-evidence.md`](../../tasks/jev-presentation-evidence.md). |
| JEV-43 | DONE | 22/09 | JEV-42 | Decisao `HOLD` registrada em [`../../tasks/jev-experimental-decision.md`](../../tasks/jev-experimental-decision.md): evidencia descritiva favoravel, mas uma aceitacao insegura, latencia remota e amostra limitada impedem adocao operacional. |

## Fase 5 - Evidencias e apresentacao

| ID | Status | Data | Dependencia | Entrega e criterio de aceite |
| --- | --- | --- | --- | --- |
| JEV-50 | DONE | 22/09 | JEV-35, JEV-36, JEV-43 | Tres capturas `mockDebug` no SM-X510 registradas em [`../../tasks/jev-app-captures.md`](../../tasks/jev-app-captures.md): baseline local, Jev `SPRAY` e Jev `UNKNOWN`, sempre sem rede ou comando. |
| JEV-51 | DONE | 22/09 | JEV-42 | Tres SVGs 16:9 gerados da evidencia sanitizada: comparacao, matrizes e reliability, todos com `n=60`, `HOLD` e aceite inseguro. Evidencia em [`../../tasks/jev-presentation-slides.md`](../../tasks/jev-presentation-slides.md). |
| JEV-52 | NEXT | 28/09 | JEV-50 | Gravar demo de reserva ou fixtures locais dos tres fluxos; reproduzir com internet desligada. |
| JEV-53 | TODO | 29/09 | JEV-43, JEV-50, JEV-51 | Escrever roteiro final: RLCD/calibracao, xadrez, casos externos, Maestro e roadmap de classes. |
| JEV-54 | TODO | 29/09 | JEV-53 | Criar slides fora de `docs/pitch/`: 46 minutos de conteudo e quatro de debate; numerar fontes, marcar hipotese versus evidencia e rotular capturas JEV-50 como `fixture mock local - nao executa o robo`. |
| JEV-55 | TODO | 30/09 | JEV-54, JEV-52 | Ensaio 1 cronometrado; registrar cortes e perguntas que exigem explicacao melhor. |
| JEV-56 | TODO | 30/09 | JEV-55 | Ensaio 2 cronometrado com demo de reserva; revisar cada claim contra os resultados registrados. |
| JEV-57 | TODO | 01/10 | JEV-56 | Apresentar usando apenas evidencias medidas; apos o encontro, registrar decisoes tecnicas que realmente mudarem. |

## Pontos de parada

- JEV-03 bloqueia qualquer chamada Jev, JEV-20 a JEV-27 e JEV-40 a JEV-43.
- JEV-15 e JEV-16 bloqueiam a rodada final; nenhum limiar e ajustado depois de
  abrir o corpus final.
- JEV-23 bloqueia o adaptador; timeout ou erro sem falha fechada e bloqueador.
- JEV-40 bloqueia afirmacoes sobre o Jev remoto; as fixtures do app demonstram
  somente apresentacao, nao constituem resultado experimental.
- JEV-41 bloqueia qualquer reuso de `corpus/final.tsv`; somente JEV-41R pode
  produzir a medicao final, em corpus e reserva novos.
- JEV-43 libera somente claims limitados da rodada independente: `n=60`, corpus
  sintetico, uma rodada, resultado descritivo e decisao `HOLD`. Slides nao
  podem alegar seguranca operacional, calibracao generalizavel ou promocao ao
  APK.
- Classes de roadmap nao autorizam mudanca no contrato ROS antes de uma nova
  task aprovada, especificacao versionada e testes proporcionais ao risco.

## Fora do escopo ate nova decisao

- hardware Meta real e rota de audio dos oculos;
- controle Jev em producao;
- filtro Jev para Qwen e RAG;
- parada de emergencia por reconhecimento de fala;
- navegacao livre, dosagem e acoes agronomicas sem contrato fechado;
- alegar calibracao antes de corpus final rotulado e medido.
