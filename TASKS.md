# Roadmap — Dock e Undock como comandos explícitos

Branch de integração atual: `feat/e2e-demo`

Este arquivo transforma o ciclo automático de dock/undock em comandos explícitos controlados pela IA, mantendo o fluxo seguro de confirmação e o bridge ROS 2 previsível.

> **Regra principal:** execute **uma task por vez**, na ordem deste arquivo. Não antecipe tasks futuras.

---

## Regras permanentes para qualquer agente

Antes de editar código:

1. Leia `AGENTS.md`, `CONTRIBUTING.md`, `docs/README.md` e a documentação relevante para a task.
2. Inspecione a implementação atual antes de propor mudanças.
3. Liste brevemente ambiguidades, riscos e critérios de aceite.
4. Verifique `git status` e não altere, reverta ou inclua no commit mudanças não relacionadas feitas pelo usuário.
5. Não implemente partes de tasks futuras “por conveniência”.

Durante a implementação:

- Faça a menor mudança que satisfaça a task.
- Preserve confirmação explícita antes de qualquer comando que possa mover o robô.
- Não introduza dependências novas sem necessidade e sem registrar a justificativa.
- Não adicione segredos, tokens, mídia bruta ou artefatos de build ao repositório.
- Mantenha contrato, Android, IA e bridge coerentes com as fontes de verdade do projeto.
- Mudança de comportamento exige atualização da documentação correspondente.
- Atualize testes proporcionais ao risco na mesma mudança.
- Siga o padrão já existente em `docs/`: objetivo, decisões/ambiguidades, critérios de aceite, plano, evidências e limitações quando aplicável.
- Registre evidências reais. Não declare build, teste físico ou E2E como aprovado se não foi executado.

### Commits atômicos

Use Conventional Commits, seguindo o padrão já usado no projeto.

Flags/tipos permitidos, conforme o tipo da mudança:

- `docs:`
- `feat:`
- `fix:`
- `refactor:`
- `test:`
- `chore:`

Prefira escopo quando ele deixar o commit mais claro, por exemplo:

```text
docs(tasks): add explicit docking roadmap
refactor(bridge): remove automatic dock mission lifecycle
feat(contract): add dock and undock intents
feat(bridge): add explicit undock command
feat(bridge): add explicit dock command
feat(android): transport dock and undock intents
feat(ai): classify dock and undock commands
test(e2e): validate explicit docking lifecycle
```

Regras de commit:

- Um commit deve representar uma mudança lógica e verificável.
- Não misture tasks diferentes no mesmo commit.
- Não inclua arquivos não relacionados.
- Rode os testes relevantes **antes** do commit.
- Revise `git diff --check`, `git diff` e `git status` antes do commit.
- Não use `--amend`, rebase destrutivo, `reset --hard` ou force-push sem pedido humano explícito.
- Se a task não puder ser concluída com segurança, pare e reporte o bloqueio em vez de criar um commit parcialmente enganoso.
- A documentação que descreve a mudança deve ser atualizada no mesmo trabalho da task; não deixe decisões importantes apenas no chat.

### Status

Marque uma task como concluída somente quando código, testes e documentação estiverem coerentes e houver evidência reproduzível.

---

# Task 0 — Versionar este roadmap

Status: `TODO`

## Objetivo

Adicionar este `TASKS.md` ao repositório antes de iniciar a refatoração.

## Critérios de aceite

- `TASKS.md` está na raiz do repositório.
- Nenhuma outra mudança não relacionada entra no commit.
- `git diff --check` passa.

## Commit sugerido

```bash
git add TASKS.md
git diff --cached
git diff --check
git commit -m "docs(tasks): add explicit docking roadmap"
```

---

# Task 1 — Remover dock/undock automático do ciclo de missão

Status: `TODO`

## Objetivo

Um comando `SPRAY` deve navegar até o talhão solicitado e terminar ali. O bridge não deve fazer undock antes da missão nem retornar/dockar automaticamente depois que a fila terminar.

## Contexto

O bridge atual executa um ciclo automático:

```text
undock -> navigation -> return-to-dock approach -> dock
```

Esse comportamento torna missões consecutivas difíceis de prever e mistura uma intenção agrícola (`SPRAY`) com decisões implícitas de mobilidade (`DOCK`/`UNDOCK`).

## Comportamento desejado

```text
SPRAY
  -> Nav2 target
  -> completion
  -> READY / idle
```

Depois da navegação, o robô permanece no destino até receber outro comando explícito.

## Escopo principal

Inspecione principalmente:

- `robot_ws/src/maestro_robot_bridge/maestro_robot_bridge/mission_cycle.py`
- `robot_ws/src/maestro_robot_bridge/maestro_robot_bridge/bridge_node.py`
- `robot_ws/src/maestro_robot_bridge/test/test_mission_cycle.py`
- testes do bridge diretamente afetados pelo lifecycle

## Requisitos

- `SPRAY` executa somente navegação para o alvo solicitado.
- Quando Nav2 termina, a máquina de estados volta para `READY`/idle.
- Não chamar `Undock` automaticamente.
- Não navegar automaticamente para a aproximação da doca.
- Não chamar `Dock` automaticamente.
- Manter disponível a infraestrutura/action clients existentes de Dock/Undock para as tasks posteriores.
- Remover estados/transições obsoletos somente quando isso puder ser feito sem antecipar `DOCK`/`UNDOCK` explícitos.

## Não fazer

- Não adicionar intents `DOCK`/`UNDOCK` ainda.
- Não alterar Android.
- Não alterar o modelo de IA.
- Não remover os action clients de Dock/Undock se serão reutilizados depois.
- Não refatorar Nav2 fora do necessário.
- Não atualizar os testes E2E globais para a arquitetura final ainda; isso é responsabilidade da Task 7, exceto o mínimo necessário para manter a suíte unitária coerente.

## Critérios de aceite

- [ ] `SPRAY -> Nav2 target -> completion -> READY/idle`.
- [ ] Nenhum undock automático ocorre.
- [ ] Nenhum return-to-dock automático ocorre.
- [ ] Nenhum dock automático ocorre.
- [ ] Uma nova navegação pode ser enfileirada/executada depois da anterior sem ciclo implícito de doca.
- [ ] Testes unitários relevantes passam.

## Testes e evidência

Execute no mínimo:

```bash
make test-robot
```

Se o ambiente permitir, rode também:

```bash
make test-quick
```

Teste manual recomendado no Gazebo:

```text
SPRAY plot-02
-> Nav2 chega em plot-02
-> robô permanece em plot-02
```

Registre na documentação da task o comando executado, resultado real e qualquer teste não executado.

## Documentação

Atualize a spec/arquitetura que ainda descreva o dock automático. Se a evidência da implementação merecer um registro específico, crie ou atualize um arquivo em `docs/tasks/` seguindo o padrão existente.

## Commit sugerido

```bash
git commit -m "refactor(bridge): remove automatic dock mission lifecycle"
```

---

# Task 2 — Adicionar `DOCK` e `UNDOCK` ao contrato do backend

Status: `TODO`

## Objetivo

Tornar `DOCK` e `UNDOCK` intents válidas no protocolo, sem executar ainda as actions do robô.

## Contexto

O contrato atual é centrado em `SPRAY` associado a um `MAPPED_PLOT`. `DOCK` e `UNDOCK` são comandos operacionais que não precisam de um talhão fictício.

## Escopo principal

Inspecione:

- `contracts/command.schema.json`
- `robot_ws/src/maestro_robot_bridge/maestro_robot_bridge/contract.py`
- `robot_ws/src/maestro_robot_bridge/maestro_robot_bridge/bridge_core.py`
- `robot_ws/src/maestro_robot_bridge/test/test_contract.py`
- `robot_ws/src/maestro_robot_bridge/test/test_bridge_core.py`

## Requisitos

Adicionar suporte de contrato para:

- `SPRAY`
- `DOCK`
- `UNDOCK`

Semântica:

- `SPRAY` continua exigindo target do tipo `MAPPED_PLOT`.
- `DOCK` não exige plot.
- `UNDOCK` não exige plot.
- `CONFIRM` e `CANCEL` continuam sendo intenções da interação mobile; não devem virar comandos de navegação do robô por acidente.
- Combinações inválidas devem falhar de forma clara e segura.
- Deduplicação, expiração, `command_id`, `schema_version` e confirmação continuam válidos.

## Não fazer

- Não disparar action `Dock`.
- Não disparar action `Undock`.
- Não alterar Android.
- Não alterar o classificador de intenção.
- Não reintroduzir lifecycle automático de doca.
- Não inventar `target` falso para `DOCK`/`UNDOCK`.

## Critérios de aceite

- [ ] `SPRAY + plot-01` é válido.
- [ ] `SPRAY` sem target é inválido.
- [ ] `DOCK` sem plot é válido.
- [ ] `UNDOCK` sem plot é válido.
- [ ] intent desconhecida é inválida.
- [ ] `DOCK`/`UNDOCK` com payload estruturalmente inválido são rejeitados.
- [ ] Testes de contrato/core passam.

## Payloads esperados

Exemplo `SPRAY`:

```json
{
  "schema_version": "1.0",
  "command_id": "<uuid>",
  "created_at": "<timestamp>",
  "expires_in_ms": 5000,
  "intent": "SPRAY",
  "target": {
    "type": "MAPPED_PLOT",
    "id": "plot-01"
  },
  "confirmed": true
}
```

Exemplo conceitual `DOCK`:

```json
{
  "schema_version": "1.0",
  "command_id": "<uuid>",
  "created_at": "<timestamp>",
  "expires_in_ms": 5000,
  "intent": "DOCK",
  "confirmed": true
}
```

Exemplo conceitual `UNDOCK`:

```json
{
  "schema_version": "1.0",
  "command_id": "<uuid>",
  "created_at": "<timestamp>",
  "expires_in_ms": 5000,
  "intent": "UNDOCK",
  "confirmed": true
}
```

O schema final pode representar ausência de target de outra forma se isso for necessário, desde que a decisão seja documentada e não use target fictício.

## Testes e evidência

Execute no mínimo:

```bash
make test-robot
```

E, se possível:

```bash
make test-quick
```

## Documentação

Atualize `docs/architecture.md` e/ou a spec correspondente para refletir o contrato versionado novo. Documente claramente quais intents são comandos do robô e quais são intents apenas da interação.

## Commit sugerido

```bash
git commit -m "feat(contract): add dock and undock intents"
```

---

# Task 3 — Implementar comando explícito `UNDOCK`

Status: `TODO`

## Objetivo

Executar `UNDOCK` somente quando um comando WebSocket explícito com essa intent for aceito.

## Fluxo desejado

```text
WebSocket intent=UNDOCK
-> validação/dispatch
-> existing /turtlebot1/undock action
-> resultado pelo mecanismo normal do bridge
```

## Requisitos

- Reutilizar o action client de Undock existente.
- `SPRAY` nunca causa undock implícito.
- Preservar `command_id` e o mecanismo normal de status/resposta.
- Falha da action deve falhar de forma segura e ser reportada.
- Se o estado de dock puder ser consultado de forma confiável:
  - `UNDOCK` com robô já fora da doca deve ser tratado de forma segura/idempotente.
- Evitar duplicar lógica ROS já existente.
- Adicionar testes focados no dispatch/status.

## Não fazer

- Não implementar `DOCK`.
- Não alterar Android.
- Não alterar o classificador de IA.
- Não refatorar Nav2 sem necessidade.
- Não fazer undock automático para `SPRAY`.

## Critérios de aceite

- [ ] `UNDOCK` explícito dispara a action de Undock.
- [ ] `SPRAY` continua sem undock implícito.
- [ ] Falha/rejeição/timeout da action é reportada.
- [ ] Repetição idempotente é segura quando o estado do robô puder ser determinado.
- [ ] Testes passam.

## Testes e evidência

Execute:

```bash
make test-robot
```

Depois, com Gazebo disponível, faça um smoke test manual enviando um payload `UNDOCK` direto ao bridge antes de integrar Android/IA.

Registre logs relevantes, sem afirmar sucesso físico se o teste não ocorreu.

## Documentação

Atualize a documentação do bridge/lifecycle e o guia de teste aplicável. Registre o exemplo real de payload e a resposta observada.

## Commit sugerido

```bash
git commit -m "feat(bridge): add explicit undock command"
```

---

# Task 4 — Implementar comando explícito `DOCK`

Status: `TODO`

## Objetivo

Executar docking somente quando houver comando `DOCK` explícito.

## Decisão importante

A action `Dock` não deve ser chamada de uma posição arbitrária.

Reutilize a sequência já existente:

```text
DOCK
-> Nav2 até dock approach configurado
-> aguarda sucesso
-> TurtleBot Dock action
-> status final
```

Use a pose configurada existente para a aproximação da doca. Não duplique coordenadas em código novo se já houver fonte canônica.

## Requisitos

- A sequência roda somente para `intent=DOCK`.
- `SPRAY` concluído nunca dispara return-to-dock.
- Se Nav2 falhar na aproximação, não chamar `Dock`.
- Se a action de Dock falhar, reportar falha.
- Se o estado de dock estiver disponível de forma confiável, tratar “já dockado” com segurança/idempotência.
- Preservar status, `command_id`, deduplicação e comportamento fail-closed.
- Adicionar testes unitários focados na sequência.

## Não fazer

- Não alterar Android.
- Não alterar o modelo de IA.
- Não reintroduzir retorno automático à doca.
- Não esconder falhas de Nav2/Dock como sucesso.

## Critérios de aceite

Caminho feliz:

```text
DOCK
-> Nav2 dock approach
-> Nav2 succeeds
-> Dock action
-> success
```

Falha de aproximação:

```text
DOCK
-> Nav2 dock approach
-> Nav2 fails
-> Dock action NÃO é chamada
-> failed command
```

Checklist:

- [ ] `DOCK` explícito executa a sequência correta.
- [ ] `SPRAY` não aciona a sequência.
- [ ] Falha de aproximação bloqueia o servo de dock.
- [ ] Falha da action Dock é reportada.
- [ ] Testes passam.

## Testes e evidência

Execute no mínimo:

```bash
make test-robot
```

Se o ambiente permitir, valide no Gazebo:

1. robô fora da doca;
2. enviar `DOCK`;
3. observar Nav2 indo até a aproximação;
4. observar action Dock;
5. registrar o resultado real.

Esta task é de alto risco e deve ser revisada antes de seguir para integração mobile.

## Documentação

Atualize arquitetura, lifecycle e guia de teste com a sequência explícita de `DOCK`. Registre falhas conhecidas e condições de pré-requisito.

## Commit sugerido

```bash
git commit -m "feat(bridge): add explicit dock command"
```

---

# Task 5 — Fazer o Android transportar `DOCK` e `UNDOCK`

Status: `TODO`

## Objetivo

Preservar a intent real (`SPRAY`, `DOCK`, `UNDOCK`) no pipeline Android até o JSON enviado por WebSocket.

## Contexto

O Android já implementa a interação `SPRAY`; partes do transporte podem assumir/hardcodar `"SPRAY"`.

## Escopo principal

Inspecione principalmente:

- `mobile/android/app/src/main/java/br/org/agroturtles/maestro/domain/InteractionEngine.kt`
- modelos/domain de comando usados pela máquina de estados
- `mobile/android/app/src/main/java/br/org/agroturtles/maestro/platform/WebSocketCommandTransport.kt`
- `mobile/android/app/src/test/java/br/org/agroturtles/maestro/domain/InteractionEngineTest.kt`
- testes do transport relevantes

## Requisitos

- Um comando deve manter a intent real por todo o pipeline Android.
- `WebSocketCommandTransport` deve serializar `command.intent`, não hardcodar `SPRAY`.
- `SPRAY` continua transportando seu target de plot.
- `DOCK` e `UNDOCK` não inventam target fictício.
- `SPRAY`, `DOCK` e `UNDOCK` exigem confirmação explícita antes de serem enviados.
- Preservar timeout, cancelamento, ambiguidade e conexão segura já existentes.
- O Android deve permanecer coerente com `contracts/command.schema.json`.

## Não fazer

- Não modificar dataset/modelo de IA nesta task.
- Não alterar código ROS.
- Não pular confirmação.
- Não duplicar o schema em listas incompatíveis.

## Critérios de aceite

- [ ] Dada intent `DOCK` já classificada, confirmação envia `intent=DOCK`.
- [ ] Dada intent `UNDOCK`, confirmação envia `intent=UNDOCK`.
- [ ] `SPRAY` continua enviando target correto.
- [ ] `DOCK`/`UNDOCK` não enviam target falso.
- [ ] Cancelamento/timeout continuam sem enviar movimento.
- [ ] Testes Android relevantes passam quando a toolchain está disponível.

## Testes e evidência

Execute, quando houver JDK/SDK configurados:

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest
```

Se houver outros testes específicos de transporte, execute-os também.

Não declare o Android como validado se a toolchain/teste não rodar neste host.

## Documentação

Atualize a documentação da máquina de estados/contrato mobile e registre exemplos do JSON gerado para as três intents.

## Commit sugerido

```bash
git commit -m "feat(android): transport dock and undock intents"
```

---

# Task 6 — Ensinar a IA local a reconhecer `DOCK` e `UNDOCK`

Status: `TODO`

## Objetivo

Estender o classificador local para reconhecer comandos explícitos de dock e undock sem regredir `SPRAY`, `CONFIRM`, `CANCEL` e `UNKNOWN`.

## Intents finais desta etapa

- `SPRAY`
- `DOCK`
- `UNDOCK`
- `CONFIRM`
- `CANCEL`
- `UNKNOWN`

## Escopo principal

Inspecione:

- `shared/ai/dataset/intents.tsv`
- dataset de avaliação existente
- `tools/train_intent_model.py`
- `tools/intent_model.py`
- `shared/ai/intent_model.json`
- fixtures/paridade compartilhada, se afetadas
- `tests/test_intent_model.py`
- testes de paridade Python/Kotlin

## Exemplos desejados

### DOCK

```text
voltar para a doca
retornar para a base
vá para a doca
dock the robot
return to dock
```

### UNDOCK

```text
sair da doca
saia da base
desacoplar
undock
leave the dock
```

## Requisitos

- Adicionar exemplos naturais em português e um conjunto menor em inglês.
- Manter o pipeline canônico/determinístico já existente.
- Atualizar regras de alta precisão apenas quando necessário.
- Não criar regra ampla baseada somente em palavras como `voltar` ou `sair`.
- Manter distinção clara:
  - `voltar para a doca` -> `DOCK`
  - `sair da doca` -> `UNDOCK`
- Regenerar o artefato canônico com as ferramentas do projeto.
- Atualizar fixtures/paridade caso o formato atual exija isso.
- Medir regressão nas intents existentes.

## Não fazer

- Não adicionar LLM ou serviço externo.
- Não enviar transcrições para API externa.
- Não expandir para linguagem natural irrestrita.
- Não alterar ROS ou Android fora do necessário para artefatos compartilhados/paridade.

## Critérios de aceite

- [ ] `"voltar para a doca"` -> `DOCK`.
- [ ] `"retornar para a base"` -> `DOCK`.
- [ ] `"sair da doca"` -> `UNDOCK`.
- [ ] `"undock"` -> `UNDOCK`.
- [ ] `SPRAY`, `CONFIRM` e `CANCEL` não sofrem regressão perigosa.
- [ ] Casos desconhecidos continuam falhando de forma segura.
- [ ] Artefato versionado está em dia.
- [ ] Avaliação e testes passam dentro dos critérios documentados.

## Testes e evidência

Use o pipeline existente, incluindo:

```bash
python3 tools/train_intent_model.py
python3 tools/train_intent_model.py --check
make test-ai
```

Se a paridade Android fizer parte do gate atual, execute ou atualize o fixture e registre explicitamente quando o teste Kotlin não puder ser executado.

Relate:

- exemplos adicionados;
- comando de regeneração;
- métricas antes/depois quando disponíveis;
- falsos positivos/negativos observados;
- arquivos alterados.

## Documentação

Atualize `docs/architecture.md` na seção de IA local, números de classes/dataset/métricas e qualquer task de avaliação/paridade afetada.

## Commit sugerido

```bash
git commit -m "feat(ai): classify dock and undock commands"
```

---

# Task 7 — E2E e limpeza dos testes antigos

Status: `TODO`

## Objetivo

Atualizar demos, testes de integração e documentação para a arquitetura final em que dock/undock são comandos explícitos.

Esta task não adiciona comportamento novo.

## Arquitetura final esperada

### Cenário A — navegação normal

```text
SPRAY plot-02
-> Nav2 reaches plot-02
-> robot remains there
-> no automatic return-to-dock
```

### Cenário B — undock explícito

```text
UNDOCK
-> robot undocks
-> no navigation mission starts automatically
```

### Cenário C — dock explícito

```text
DOCK
-> Nav2 navigates to dock approach
-> Dock action runs
-> robot docks
```

### Cenário D — jornada completa

```text
UNDOCK
-> SPRAY plot-01
-> SPRAY plot-03
-> DOCK
```

## Escopo provável

Inspecione:

- `Makefile`
- `tools/mock_glasses_client.py`
- `tools/check_simulation.py`
- testes do bridge
- testes de contrato
- testes do Android/IA afetados
- `README.md`
- `docs/testing.md`
- `docs/architecture.md`
- documentação em `docs/tasks/` relacionada à demo/lifecycle

## Requisitos

- Remover ou reescrever asserts cujo critério de sucesso seja “toda missão termina dockada”.
- Atualizar `make demo`, `make demo-route` e/ou `make demo-visual` apenas conforme necessário para representar a arquitetura nova.
- O teste padrão de `SPRAY` deve provar navegação/movimento sem exigir dock final.
- Criar/ajustar um teste separado para lifecycle explícito `UNDOCK -> ... -> DOCK`.
- Preservar fail-closed para comando inválido, timeout, confirmação ausente e erro de navegação.
- Atualizar mensagens de sucesso para não afirmarem dock automático.
- Não introduzir feature nova.

## Critérios de aceite

- [ ] Cenário A validado.
- [ ] Cenário B validado.
- [ ] Cenário C validado.
- [ ] Cenário D validado quando o ambiente Gazebo permitir.
- [ ] Testes antigos não exigem dock implícito.
- [ ] Mensagens de demo refletem exatamente o que foi comprovado.
- [ ] Documentação e código descrevem o mesmo lifecycle.
- [ ] Suíte prática mais ampla passa.

## Testes e evidência

Execute o maior conjunto viável:

```bash
make test-quick
```

Quando a simulação estiver disponível, execute as demos atualizadas e registre:

- testes aprovados;
- testes pulados;
- falhas;
- comandos usados;
- logs/evidência suficiente para reproduzir;
- qualquer limitação de hardware/toolchain.

## Documentação

Atualize todos os documentos que ainda descrevam:

```text
SPRAY -> automatic undock -> navigation -> automatic return -> automatic dock
```

para a arquitetura explícita:

```text
UNDOCK -> SPRAY... -> DOCK
```

Não apague histórico útil de tarefas concluídas; registre que o comportamento foi substituído e aponte para a nova decisão.

## Commit sugerido

```bash
git commit -m "test(e2e): validate explicit docking lifecycle"
```

Se houver uma atualização documental separada que seja realmente independente e atômica, use algo como:

```bash
git commit -m "docs(architecture): document explicit docking commands"
```

Não crie um commit extra apenas para “arrumar documentação esquecida” se ela deveria fazer parte da mesma mudança lógica.

---

# Ordem de execução

```text
Task 0 — versionar TASKS.md
  ↓
Task 1 — remover dock/undock automático
  ↓
REVISÃO HUMANA + teste Gazebo
  ↓
Task 2 — contrato DOCK/UNDOCK
  ↓
Task 3 — UNDOCK explícito
  ↓
Task 4 — DOCK explícito
  ↓
REVISÃO HUMANA + teste Gazebo
  ↓
Task 5 — Android transporta novas intents
  ↓
Task 6 — IA reconhece novas intents
  ↓
Task 7 — E2E, demos e documentação final
```

## Pontos obrigatórios de revisão humana

Revisar com atenção antes de seguir depois de:

- **Task 1:** muda o lifecycle base das missões.
- **Task 4:** controla sequência de aproximação + docking físico/simulado.
- qualquer mudança em `contracts/`, segurança ou confirmação.

---

# Prompt reutilizável para o Gemini

Substitua `<TASK>` pelo número da task desejada.

```text
Você está trabalhando no repositório Maestro Agrícola.

Leia primeiro:
- AGENTS.md
- CONTRIBUTING.md
- docs/README.md
- TASKS.md
- a documentação relevante em docs/ para a task solicitada.

Execute SOMENTE a Task <TASK> de TASKS.md.

Regras obrigatórias:
1. Não implemente nenhuma parte de tasks posteriores, mesmo que pareça conveniente.
2. Antes de editar, inspecione a implementação atual e me dê um resumo curto de:
   - como o comportamento funciona hoje;
   - ambiguidades/riscos;
   - arquivos que pretende alterar;
   - critérios de aceite que vai validar.
3. Preserve todas as mudanças do usuário que não pertençam à task. Verifique `git status` antes de começar.
4. Faça a menor mudança possível e não faça refactors fora do escopo.
5. Toda mudança de comportamento deve atualizar a documentação correspondente, seguindo o padrão já usado em `docs/`: objetivo, decisões/ambiguidades, critérios de aceite, plano, evidências e limitações quando aplicável.
6. Não deixe decisões importantes somente na resposta do chat; registre-as na documentação apropriada.
7. Atualize ou adicione testes proporcionais ao risco.
8. Rode os testes relevantes definidos em TASKS.md. Se algum teste não puder ser executado, diga exatamente por quê; não declare que passou.
9. Antes de finalizar, rode:
   - git diff --check
   - git diff
   - git status
10. Faça commit(s) atômico(s), sem incluir arquivos não relacionados, usando Conventional Commits com flag/escopo coerente, por exemplo:
   - docs(tasks): ...
   - refactor(bridge): ...
   - feat(contract): ...
   - feat(bridge): ...
   - feat(android): ...
   - feat(ai): ...
   - test(e2e): ...
11. Não use git reset --hard, force-push, rebase destrutivo ou --amend sem autorização explícita.
12. Não faça commit se os critérios essenciais da task falharem. Pare e reporte o bloqueio.

Ao terminar, retorne:
- resumo do que mudou;
- arquivos alterados;
- documentação atualizada;
- testes executados + resultado;
- testes não executados + motivo;
- riscos/pendências;
- hash e mensagem de cada commit criado;
- confirmação explícita de que nenhuma task posterior foi implementada.

Depois de concluir a Task <TASK>, PARE. Não comece a próxima task.
```

---

# Prompt inicial recomendado

Para começar agora:

```text
Leia AGENTS.md, CONTRIBUTING.md, docs/README.md e TASKS.md.
Execute SOMENTE a Task 1.

Siga integralmente o protocolo de execução e commits definido em TASKS.md.
Antes de editar, explique brevemente o lifecycle automático atual e quais
arquivos você pretende alterar.

Depois implemente, atualize testes e documentação, rode os testes relevantes,
revise o diff e crie apenas commit(s) atômico(s) da Task 1.

Ao terminar, reporte evidências, hashes dos commits e pare.
Não implemente a Task 2.
```
