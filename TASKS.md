# Roadmap — Dock/Undock explícitos e evolução da IA local

Branch de integração atual: `main`

Este arquivo conclui a migração do ciclo automático de dock/undock para comandos explícitos, preserva a confirmação de segurança e define a etapa de avaliação/substituição da IA local antes do E2E final.

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

- No Antigravity/Gemini, prefira comandos de teste diretos (`python3 -m pytest ...`)
  aos wrappers `make` quando o teste subjacente for conhecido. O runner já
  apresentou hangs em comandos `make`; um hang do wrapper não deve bloquear a task.
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
feat(ai): improve/integrate local intent backend
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

## Estado atual da `main`

Baseline já consolidada antes da próxima implementação:

- **Task 0 — concluída:** roadmap versionado.
- **Task 1 — concluída:** `SPRAY` não faz mais undock, return-to-dock ou dock automaticamente.
- **Task 1 — evidência física:** com o robô dockado, `SPRAY` foi rejeitado; após `Undock` manual pelo HMI, o comando falado `pulverizar o talhão 2` + confirmação por voz foi aceito, o TurtleBot chegou ao `plot-02` e permaneceu no destino.
- **Task 1 — evidência unitária:** teste focado do mission cycle passou com 15 casos; suíte Python do bridge passou com 19 testes no momento da validação.
- **Correção de baseline da IA — concluída:** o checker de artefatos tolera apenas ruído irrelevante de ponto flutuante (`1e-12`) e continua rejeitando mudanças reais/estruturais.
- **Checker da IA — evidência:** `python3 tools/train_intent_model.py --check` passou sem regenerar o modelo; o teste específico de comparação de artefatos passou com 3 casos.
- **Próxima task de implementação:** **Task 2 — contrato `DOCK`/`UNDOCK`**.

### Limitação de IA observada no uso real

A avaliação versionada atual pode apresentar métricas perfeitas no conjunto existente e ainda assim não representar bem linguagem natural real. Já foi observado que pequenas paráfrases de um comando válido podem produzir `UNKNOWN` ou classificação inesperada.

Por isso, **não escolher nem trocar o modelo apenas pela métrica atual**. Depois da Task 5, a evolução da IA será feita pelas Tasks 6A–6F usando corpus real de fala/ASR, benchmark reproduzível e teste no smartphone-alvo.

---

# Task 0 — Versionar este roadmap

Status: `DONE`

## Resultado

O roadmap foi versionado antes da refatoração do lifecycle. Nenhuma ação adicional é necessária nesta task.

---

# Task 1 — Remover dock/undock automático do ciclo de missão

Status: `DONE`

## Objetivo concluído

Um comando `SPRAY` navega até o talhão solicitado e termina ali. O bridge não faz undock antes da missão nem retorna/docka automaticamente depois que a navegação termina.

## Comportamento atual validado

```text
SPRAY
  -> valida estado
  -> Nav2 target
  -> completion
  -> READY / idle
```

Se o bridge sabe que o robô está dockado, `SPRAY` é rejeitado em vez de executar `Undock` implicitamente.

## Invariantes que as próximas tasks devem preservar

- `SPRAY` nunca chama `Undock` automaticamente.
- conclusão de `SPRAY` nunca inicia return-to-dock.
- conclusão de `SPRAY` nunca chama `Dock`.
- o robô permanece no destino depois da navegação.
- os action clients/utilidades de Dock/Undock permanecem disponíveis para Tasks 3 e 4.
- um robô dockado não recebe navegação `SPRAY` até existir um `UNDOCK` explícito válido.

## Critérios de aceite — resultado

- [x] `SPRAY -> Nav2 target -> completion -> READY/idle`.
- [x] Nenhum undock automático ocorre.
- [x] Nenhum return-to-dock automático ocorre.
- [x] Nenhum dock automático ocorre.
- [x] Navegação normal não reintroduz lifecycle implícito de doca.
- [x] Testes unitários relevantes passaram.
- [x] Smoke test no Gazebo comprovou chegada ao `plot-02` e permanência no destino.

## Evidência registrada

Teste focado:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
python3 -m pytest \
  robot_ws/src/maestro_robot_bridge/test/test_mission_cycle.py -q
```

Resultado observado na validação da task: `15 passed`.

Suíte do bridge:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
python3 -m pytest robot_ws/src/maestro_robot_bridge/test -q
```

Resultado observado na validação da task: `19 passed`.

Evidência manual no Gazebo:

```text
1. robô dockado
2. SPRAY -> rejeitado com "robot unavailable: robot is docked"
3. Undock manual pelo HMI (`turtlebot1`)
4. voz/ASR: "pulverizar o talhão 2"
5. confirmação por voz: "sim"
6. bridge: "navigation goal queued"
7. Nav2 chega ao plot-02
8. nenhum return-to-dock/dock automático é iniciado
```

Commits de referência já presentes na linha de integração:

```text
f4456ed refactor(bridge): remove automatic dock mission lifecycle
e79e070 docs(bridge): mark automatic docking lifecycle as superseded
```

## Regra para regressões

Qualquer task posterior que faça `SPRAY` voltar a causar undock ou dock implícito deve falhar revisão/teste.

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

Execute primeiro os testes focados, sem depender de wrappers `make`:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
python3 -m pytest \
  robot_ws/src/maestro_robot_bridge/test/test_contract.py \
  robot_ws/src/maestro_robot_bridge/test/test_bridge_core.py -q
```

Depois, se os testes focados passarem:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
python3 -m pytest robot_ws/src/maestro_robot_bridge/test -q
```

`make test-robot`/`make test-quick` podem ser usados como gate adicional no terminal normal quando estiverem estáveis, mas não são a primeira opção no Antigravity/Gemini.

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

Execute primeiro os arquivos de teste do bridge realmente alterados pela task. Depois rode:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
python3 -m pytest robot_ws/src/maestro_robot_bridge/test -q
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

Execute primeiro os testes focados da sequência de docking e depois:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
python3 -m pytest robot_ws/src/maestro_robot_bridge/test -q
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

# Task 6 — Reavaliar e evoluir a IA local

Status: `TODO`

## Motivo da mudança de plano

O classificador atual cumpriu o papel de provar o MVP local/offline, mas o uso real mostrou generalização insuficiente para pequenas variações de linguagem. Uma frase conhecida pode funcionar enquanto uma paráfrase simples falha ou vira `UNKNOWN`.

A decisão de modelo não será tomada apenas pelo tamanho do artefato ou pela métrica do dataset atual. A IA será tratada como um componente substituível atrás do mesmo contrato seguro.

## Invariante de segurança da IA

Nenhum modelo — atual ou futuro — pode gerar livremente comandos ROS.

A saída de compreensão deve continuar restrita a uma estrutura validável, por exemplo:

```json
{
  "intent": "SPRAY",
  "target": "plot-02",
  "confidence": 0.94
}
```

ou:

```json
{
  "intent": "DOCK",
  "confidence": 0.96
}
```

A camada determinística continua responsável por:

- schema/versionamento;
- target permitido;
- estado do robô;
- confirmação explícita;
- expiração/deduplicação;
- rejeição fail-closed.

As intents-alvo permanecem:

- `SPRAY`
- `DOCK`
- `UNDOCK`
- `CONFIRM`
- `CANCEL`
- `UNKNOWN`

---

## Task 6A — Construir corpus real de comandos e ASR

Status: `TODO`

### Objetivo

Criar um conjunto de avaliação que represente como pessoas realmente falam e como o ASR realmente transcreve no Android.

### Requisitos

- Reusar a estrutura de dataset já existente quando ela for adequada; não criar formato paralelo sem necessidade.
- Coletar frases faladas, não apenas exemplos escritos.
- Para cada caso, registrar no mínimo:
  - frase pretendida;
  - transcrição produzida pelo ASR;
  - intent esperada;
  - target esperado quando aplicável;
  - resultado observado;
  - origem (`real`, `paráfrase`, `ruído`, etc.) se o formato permitir.
- Incluir números em formas diferentes: `2`, `02`, `dois`, `talhão dois`, `plot dois`.
- Incluir português natural e um conjunto menor em inglês quando fizer sentido para a demo.
- Incluir negativos/ambíguos para testar `UNKNOWN`.
- Não coletar/persistir áudio bruto por padrão.

### Casos mínimos de `SPRAY`

```text
pulverizar o plot 02
pulverizar o talhão 2
pulverize o plot dois
vá pulverizar o talhão dois
pulverização no plot 2
pode pulverizar a área dois
```

### Casos mínimos futuros de `DOCK`

```text
voltar para a doca
vá para a dock
retornar para a base
dock the robot
return to dock
```

### Casos mínimos futuros de `UNDOCK`

```text
sair da doca
saia da base
desacoplar
undock
leave the dock
```

### Critérios de aceite

- [ ] Corpus real/parafraseado versionado.
- [ ] Há exemplos vindos de transcrição ASR real.
- [ ] Há positivos, negativos e ambiguidades.
- [ ] Há cobertura de `SPRAY`, `DOCK`, `UNDOCK`, confirmação, cancelamento e `UNKNOWN`.
- [ ] O dataset separa claramente texto pretendido de transcrição ASR quando ambos existirem.

### Commit sugerido

```bash
git commit -m "test(ai): add real command and asr corpus"
```

---

## Task 6B — Criar benchmark reproduzível da IA atual

Status: `TODO`

### Objetivo

Medir o baseline atual antes de trocar arquitetura.

### Métricas mínimas

- accuracy global;
- macro F1;
- recall por intent;
- falsos positivos por intent;
- falsos `UNKNOWN`;
- `UNKNOWN` aceito indevidamente;
- `unsafe accepts`;
- acerto de target para `SPRAY`;
- latência de inferência;
- tamanho do artefato.

### Requisitos

- Separar treino de avaliação.
- Não medir apenas exemplos que já fazem parte do treino.
- Reportar resultado em corpus escrito e em transcrições ASR.
- Preservar o `--check` read-only dos artefatos.
- Não considerar ruído de ponto flutuante abaixo da tolerância canônica como alteração real de modelo.
- Registrar erros concretos, não apenas uma média agregada.

### Critérios de aceite

- [ ] Benchmark roda por comando reproduzível.
- [ ] Baseline fica versionado.
- [ ] Falhas por paráfrase ficam visíveis.
- [ ] Métricas do conjunto antigo e do conjunto real não são misturadas silenciosamente.

### Commit sugerido

```bash
git commit -m "test(ai): benchmark local intent baseline"
```

---

## Task 6C — Melhorar o baseline atual antes de trocar modelo

Status: `TODO`

### Objetivo

Descobrir até onde o pipeline leve atual consegue chegar com normalização, features/regras de alta precisão e dataset melhor.

### Requisitos

- Corrigir casos comuns de ASR e variações simples sem criar regras excessivamente amplas.
- Normalizar variações de números/IDs de plot de forma determinística quando seguro.
- Preservar `UNKNOWN` e comportamento fail-closed.
- Não criar regra ampla baseada somente em palavras genéricas como `voltar`, `sair`, `ir` ou `fazer`.
- Regenerar artefato somente se a mudança pertence à task e depois revisar o diff.
- Comparar métricas antes/depois no benchmark da Task 6B.

### Critério de decisão

Se o baseline atingir a meta de qualidade e latência definida pela equipe, ele continua candidato. Caso contrário, seguir para benchmark de modelos alternativos sem esconder a limitação.

### Commit sugerido

```bash
git commit -m "feat(ai): improve local intent baseline"
```

---

## Task 6D — Benchmarkar modelos locais alternativos

Status: `TODO`

### Objetivo

Comparar o baseline com pelo menos uma alternativa semântica local mais robusta, sem acoplar o produto ao primeiro modelo testado.

### Candidatos

Escolher os candidatos somente no momento desta task, considerando suporte real ao Android/hardware disponível. Podem incluir:

- classificador semântico pequeno quantizado;
- encoder de embeddings + classificador;
- LLM on-device pequeno com saída estruturada restrita.

Não escolher um modelo apenas porque é popular ou novo.

### Requisitos

Todos os candidatos devem usar o **mesmo corpus e benchmark**.

Medir:

- qualidade por intent;
- `UNKNOWN`/falsos positivos;
- latência p50/p95;
- cold start;
- RAM de pico;
- tamanho em disco;
- consumo/temperatura quando mensurável;
- execução offline;
- facilidade de integração Android;
- licença/distribuição compatível com o projeto.

### Segurança

Mesmo um LLM local só pode produzir uma representação intermediária validada. Ele não recebe autoridade para criar pose, action ROS ou target inexistente.

### Critérios de aceite

- [ ] Pelo menos baseline + alternativa comparados com o mesmo conjunto.
- [ ] Não há escolha baseada apenas em impressão subjetiva.
- [ ] Trade-offs de qualidade, RAM e latência registrados.

### Commit sugerido

```bash
git commit -m "test(ai): compare on-device intent models"
```

---

## Task 6E — Benchmark no smartphone-alvo de 6/8 GB

Status: `BLOCKED_ON_HARDWARE`

### Objetivo

Testar no aparelho que será usado com os óculos, porque RAM nominal sozinha não determina desempenho de inferência.

### Registrar hardware

- modelo exato do aparelho;
- RAM;
- SoC;
- GPU/NPU quando disponível;
- versão do Android;
- backend/acelerador realmente utilizado.

### Testes mínimos

- 20+ inferências consecutivas;
- cold start;
- latência p50/p95;
- RAM de pico;
- aquecimento/throttling observável;
- execução junto com ASR e fluxo do app;
- câmera/DAT + microfone + IA quando o hardware dos óculos estiver disponível;
- comportamento offline.

### Critérios de aceite

- [ ] O modelo cabe com margem junto do app/ASR/DAT.
- [ ] A latência é aceitável para confirmação por voz.
- [ ] Não há crash/OOM em sequência.
- [ ] Resultado é comparado ao baseline, não avaliado isoladamente.

### Commit sugerido

```bash
git commit -m "test(ai): benchmark intent model on target phone"
```

---

## Task 6F — Escolher e integrar o backend de IA vencedor

Status: `TODO`

### Objetivo

Escolher o backend com base nas Tasks 6A–6E e integrá-lo no Android sem quebrar o contrato do restante do sistema.

### Requisitos

- Documentar a decisão e os números que a justificam.
- Preservar interface de classificação pequena e substituível.
- Preservar confirmação explícita.
- Preservar saída estruturada/validada.
- Preservar fallback seguro para baixa confiança/ambiguidade.
- `UNKNOWN` nunca movimenta o robô.
- Se confiança for insuficiente, pedir esclarecimento ou rejeitar; não adivinhar target.
- Atualizar paridade/testes Android quando aplicável.
- Não misturar integração de modelo com mudanças ROS.

### Critérios de aceite

- [ ] Modelo escolhido por benchmark reproduzível.
- [ ] App funciona offline.
- [ ] `SPRAY`/`DOCK`/`UNDOCK` robustos nas variações definidas.
- [ ] `CONFIRM`/`CANCEL` continuam seguros.
- [ ] Baixa confiança não gera ação.
- [ ] Testes/paridade aplicáveis passam.

### Commit sugerido

```bash
git commit -m "feat(ai): integrate selected on-device intent backend"
```

---

# Task 7 — E2E e limpeza dos testes antigos

Status: `TODO`

## Objetivo

Atualizar demos, testes de integração e documentação para a arquitetura final em que dock/undock são comandos explícitos e a IA escolhida nas Tasks 6A–6F é exercitada pelo caminho de voz/ASR.

Esta task não adiciona comportamento novo; ela prova e documenta o sistema integrado.

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

### Cenário D — jornada completa por voz

```text
"saia da doca"
-> confirmação
-> UNDOCK

"pulverizar o plot 01"
-> confirmação
-> SPRAY plot-01

"pulverizar o talhão três"
-> confirmação
-> SPRAY plot-03

"voltar para a doca"
-> confirmação
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
Task 0 — roadmap                                      ✅ DONE
  ↓
Task 1 — remover dock/undock automático              ✅ DONE
  ↓
baseline docs/checker da IA                          ✅ DONE
  ↓
Task 2 — contrato DOCK/UNDOCK                        ← PRÓXIMA
  ↓
Task 3 — UNDOCK explícito
  ↓
Task 4 — DOCK explícito
  ↓
REVISÃO HUMANA + teste Gazebo
  ↓
Task 5 — Android transporta novas intents
  ↓
PAUSA: backend/ROS/Android estruturais prontos
  ↓
Task 6A — corpus real de comandos + ASR
  ↓
Task 6B — benchmark do baseline
  ↓
Task 6C — melhorar baseline atual
  ↓
Task 6D — comparar modelos locais alternativos
  ↓
Task 6E — benchmark no smartphone-alvo
  ↓
Task 6F — escolher e integrar backend de IA
  ↓
Task 7 — E2E final, demos e documentação final
```

## Pontos obrigatórios de revisão humana

Revisar com atenção antes de seguir depois de:

- **Task 4:** controla sequência de aproximação + docking físico/simulado.
- **Task 5:** fecha o contrato ponta a ponta antes da troca/avaliação de IA.
- **Task 6D/6E:** define candidatos e mede custo real no hardware.
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

Para continuar a partir da `main` atual:

```text
Leia AGENTS.md, CONTRIBUTING.md, docs/README.md e TASKS.md.
Execute SOMENTE a Task 2.

A Task 1 já está concluída e validada. Não reintroduza undock/dock automático
para SPRAY e não altere Android nem o modelo de IA nesta task.

Antes de editar, inspecione o contrato/backend atual e explique brevemente:
- como SPRAY é validado hoje;
- como representar DOCK/UNDOCK sem target fictício;
- quais arquivos serão alterados;
- quais testes focados serão executados.

Depois implemente somente o contrato de DOCK/UNDOCK, atualize testes e
documentação necessária, rode os testes focados, revise o diff e crie apenas
commit(s) atômico(s) da Task 2.

Ao terminar, reporte evidências, hashes dos commits e pare.
Não implemente a Task 3.
```
