# Tarefas - Jev e Decisoes com Incerteza

Data alvo revisada: 08/10/2026

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
  `UNKNOWN`. Capacidades novas do Maestro so iniciam apos JEV-38 e nao alteram
  essa comparacao: cada uma ganha baseline local, contrato, corpus e testes
  proprios antes de uma comparacao JEV opcional.

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
| JEV-37 | DONE | 23/09 | JEV-36, aprovacao mock | Demo interativa opt-in em `mockDebug`: proxy loopback fixo via `adb reverse`, chave fora do APK, teto de 24 tentativas, declaração de fala sem dado pessoal, falha fechada e bloqueio de `Command` antes do bridge. Testes focados passaram; no SM-X510 uma fala curta de doca foi classificada remotamente como `DOCK` com origem `Jev`, ficou pendente e expirou sem comando. Evidência em [`../../tasks/jev-local-proxy.md`](../../tasks/jev-local-proxy.md). |
| JEV-38 | DONE | 24/09 | JEV-37 | No SM-X510, `Jev remoto (Gazebo)` classificou, esperou confirmação por voz e enviou `UNDOCK` estruturado ao bridge. O bridge aceitou a ação explícita e ROS reportou `is_docked: false`; `dat` permanece sem Jev remoto. Nenhuma mídia, transcrição ou chave foi persistida. Evidência em [`../../tasks/jev-local-proxy.md`](../../tasks/jev-local-proxy.md). |

Detalhes de UI e estados: [`../../tasks/jev-ui-decision-visibility.md`](../../tasks/jev-ui-decision-visibility.md).

## Fase 3.5 - Capacidades do Maestro apos JEV-38

Estas tasks entregam valor do Maestro, mesmo se Jev nunca for adotado. Elas nao
alteram a avaliacao congelada de seis labels, nao enviam transcricoes ao Jev e
nao usam Jev para criar plano, resolver alvo ou controlar o robo. A primeira
comparacao de uma capacidade nova so pode ocorrer com corpus novo, pareado e
aprovado contra seu baseline local.

| ID | Status | Dependencia | Entrega e criterio de aceite |
| --- | --- | --- | --- |
| JEV-70 | NEXT | JEV-38 | Especificar o caminho somente leitura: `ReadOnlyQuery`, `OperationRecord` e resposta narravel. Define `plot`, resultado final, timestamp, origem e retencao; nao armazena foto, audio ou transcricao. Define tambem o limite entre roteamento de linguagem, consulta e `Command`. |
| JEV-71 | TODO | JEV-70 | Implementar o historico de operacoes concluidas no simulador: uma pulverizacao so cria `OperationRecord` apos resultado final do bridge, com talhao e timestamp verificaveis. Falha, cancelamento e expiracao nao criam registro. Testes focados de sucesso e recusas passam. |
| JEV-72 | TODO | JEV-70, JEV-71 | Implementar `PLOT_STATUS_QUERY` com baseline local separado do catalogo original: fala pede a ultima pulverizacao de um talhao, o Maestro consulta o historico e responde sem `Command`, WebSocket de comando ou ROS de movimento. Testar talhao encontrado, inexistente, sem historico e fala ambigua. |
| JEV-73 | TODO | JEV-70 | Implementar `STATUS_QUERY`: leitura narravel do estado do robo por interface de consulta, sem emissao de `Command`. Testar estados conectado, aguardando, pendente, executando, desconectado e falha fechada. |
| JEV-74 | TODO | JEV-70 | Especificar e implementar `INSPECT_TARGET` no caminho de captura sob demanda: QR/marcador em memoria, permissao explicita, resultado tipado e descarte da imagem. Sem persistencia de imagem e sem movimento. Testar permissao negada, QR valido, QR invalido e timeout. |
| JEV-75 | TODO | JEV-70, JEV-72, JEV-73, JEV-74 | Criar corpus e benchmark locais para as tres consultas. Somente depois de passar no baseline local, decidir explicitamente se vale comparar Jev contra o mesmo corpus e o mesmo contrato. |
| JEV-76 | TODO | JEV-70, JEV-72 | Especificar `MISSION_PREVIEW` e `MissionPlan` versionado. O roteador apenas reconhece pedido de missao; parser e validacao deterministica extraem passos permitidos, alvos e consultas. Entrada invalida ou ambigua falha fechada, sem `Command`. |
| JEV-77 | TODO | JEV-76 | Implementar preview de missao no app: mostrar etapas e pedir confirmacao antes de cada acao fisica. Consultas podem ser exibidas, mas nao autorizam acao subsequente. Testar revisao, cancelamento, timeout e plano invalido. |
| JEV-78 | TODO | JEV-77 | Implementar executor deterministico no Gazebo para `MissionPlan`: executa somente etapas confirmadas, pausa em falha ou alvo invalido e preserva rastreabilidade por etapa. Exige contrato ROS versionado e E2E proprio; nao usar Jev como planejador. |

Ordem de produto decidida: `PLOT_STATUS_QUERY` primeiro, depois
`STATUS_QUERY` e `INSPECT_TARGET`; `MISSION_PREVIEW` so inicia quando as
consultas e seus contratos estiverem testados. `PAUSE`, `RESUME` e `SCOUT`
permanecem fora desta fase. A apresentacao pode mostrar esta sequencia como
roadmap; uma task so vira evidencia de produto apos seus testes.

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
| JEV-52 | DONE | 22/09 | JEV-50 | Tres fixtures locais de reserva no SM-X510, com Wi-Fi desligado e depois restaurado; evidencia em [`../../tasks/jev-offline-reserve-demo.md`](../../tasks/jev-offline-reserve-demo.md). |
| JEV-53 | DONE | 22/09 | JEV-43, JEV-50, JEV-51 | Roteiro falavel de 50 minutos (46 de conteudo e 4 de debate) em [`presentation-script.md`](presentation-script.md), com fontes, limites e visuais previstos. |
| JEV-54 | DONE | 24/09 | JEV-53 | Deck HTML com 19 laminas em [`slides/jev-rl-study.html`](slides/jev-rl-study.html): 46 minutos de conteudo e quatro de debate; fontes e tipo de claim visiveis; capturas JEV-50 rotuladas `fixture mock local - nao executa o robo`. Em 24/09, o bloco de exemplos externos passou a usar xadrez, HighwayEnv e triagem de PR, com limites explicitos sobre simulacao, testes, revisao humana e economia de tokens. Evidencia em [`../../tasks/jev-study-group-deck.md`](../../tasks/jev-study-group-deck.md). |
| JEV-55 | TODO | 06/10 | JEV-54, JEV-52 | Ensaio 1 cronometrado, agendado para dois dias antes da apresentacao; registrar cortes e perguntas em [`../../tasks/jev-rehearsal-1.md`](../../tasks/jev-rehearsal-1.md). So conclui apos execucao falada real. |
| JEV-56 | TODO | 07/10 | JEV-55 | Ensaio 2 cronometrado com demo de reserva; revisar cada claim contra os resultados registrados. |
| JEV-57 | TODO | 08/10 | JEV-56 | Apresentar usando apenas evidencias medidas; apos o encontro, registrar decisoes tecnicas que realmente mudarem. |

## Fase 6 - Reabertura pos-HOLD

| ID | Status | Data | Dependencia | Entrega e criterio de aceite |
| --- | --- | --- | --- | --- |
| JEV-60 | DONE | 23/09 | JEV-43 | Protocolo pos-HOLD em [`../../tasks/jev-post-hold-protocol.md`](../../tasks/jev-post-hold-protocol.md): Jev bruto e Jev+guard separados, dois holdouts ASR, uma rodada reservada por corpus e `HOLD` para qualquer aceite guarded inseguro. Nenhuma chamada remota. |
| JEV-61 | DONE | 23/09 | JEV-60 | Guard deterministico de cancelamento explicito, desligado por padrao para preservar Jev bruto, em [`../../tasks/jev-explicit-cancel-guard.md`](../../tasks/jev-explicit-cancel-guard.md). `recovery-045` e regressao de desenvolvimento; o guard ou sua falha retornam `CANCEL` sem evaluator, fallback bruto ou Qwen. Testes Kotlin focados aprovados. |
| JEV-62 | DONE | 23/09 | JEV-61 | `asr-development.tsv` tem 34 transcricoes exatas, offline e revisadas por duas pessoas; seis trazem ruido de ar-condicionado. Registro e uma exclusao auditavel em [`corpus/asr-label-review.md`](corpus/asr-label-review.md). O baseline local errou `CANCEL -> SPRAY`, `UNKNOWN -> CANCEL` e duas vezes `UNKNOWN -> UNDOCK`, sem comando. Cobertura de desenvolvimento encerrada; esses textos nao podem ir para holdout. |
| JEV-63 | BLOCKED | 23/09 | JEV-62 | Holdout primario congelado com 41 casos reais e sanitizados: 30 de seguranca, 11 positivos e P33 excluida sem reposicao por ambiguidade. A tentativa de replicacao foi encerrada antes de corpus; seus cartoes foram retirados e nao podem ser reutilizados. Registro em [`../../tasks/jev-asr-replication-attempt.md`](../../tasks/jev-asr-replication-attempt.md). Reabrir so depois de 08/10, com nova task, novos cartoes, nova pessoa/sessao e aprovacao humana. |
| JEV-64 | BLOCKED | 23/09 | JEV-61, JEV-63 | Adiada ate depois da apresentacao: a comparacao `local`, `jev_raw` e `jev_guarded` preserva o primary existente e exige uma nova replicacao valida congelada. |
| JEV-65 | BLOCKED | - | JEV-60, JEV-63, JEV-64 | Rodada primaria unica, com script/reserva/custo novos. Bloqueada por aprovacao humana de custo e dados ASR. |
| JEV-66 | BLOCKED | - | JEV-65 | Rodada de replicacao unica no segundo holdout, sem mudar guard ou limiar. Bloqueada pela primaria congelada e pelo novo subteto. |
| JEV-67 | BLOCKED | 23/09 | JEV-65, JEV-66 | Adiada ate depois da apresentacao. Zero aceite inseguro guarded em cada holdout e requisito minimo; um erro preserva `HOLD`. |

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
