# Roadmap --- Dock e Undock como comandos explícitos

## Status atual

- Task 0 --- Versionar TASKS.md: DONE
- Task 1 --- Remover dock/undock automático: DONE
- Task 2 --- Adicionar DOCK/UNDOCK ao contrato: DONE
- Task 3 --- Implementar comando explícito UNDOCK: DONE
- Task 4 --- Implementar comando explícito DOCK: DONE
- Task 5 --- Android transportar intents: DONE
- Task 6 --- Evolução da IA local: PRÓXIMA
- Task 7 --- E2E final: TODO

---

# Task 2 --- Adicionar DOCK e UNDOCK ao contrato

Status: DONE

Foram adicionados os intents:

- SPRAY
- DOCK
- UNDOCK

Regras:

- SPRAY exige target `MAPPED_PLOT`.
- DOCK não exige target.
- UNDOCK não exige target.
- Confirmação, expiração, `command_id` e `schema_version` continuam obrigatórios.
- DOCK e UNDOCK rejeitam `target`.
- O bridge continua validando o contrato antes de qualquer execução ROS.

Evidências registradas durante a implementação:

- suíte do bridge passando;
- suíte geral passando;
- contrato validando os três intents.

---

# Task 3 --- Implementar comando explícito UNDOCK

Status: DONE

Objetivo:

Executar Undock somente via comando explícito:

```json
{
  "intent": "UNDOCK",
  "target": null,
  "confirmed": true
}
```

Fluxo:

```text
WebSocket
 -> BridgeCore
 -> Bridge Node
 -> MissionCycle
 -> /turtlebot1/undock action
```

Regras implementadas:

- UNDOCK é solicitado somente por intent explícita.
- SPRAY nunca chama Undock implicitamente.
- O comando é rejeitado quando o lifecycle não está em estado seguro para undock.
- Falhas deixam a missão em estado seguro/fail-closed.
- O estado dockado é confirmado por `dock_status`.
- O lifecycle retorna a `READY` após undock confirmado.

Evidências:

- comando WebSocket UNDOCK foi aceito pelo bridge em estado válido;
- callback `_request_undock` está conectado ao `BridgeCore`;
- lifecycle explícito e testes do bridge foram validados durante a Task 3.

---

# Task 4 --- Implementar comando explícito DOCK

Status: DONE

Objetivo:

Executar docking somente via comando explícito.

Fluxo:

```text
DOCK
 -> MissionCycle
 -> Nav2 para dock approach configurado
 -> Dock action
 -> confirmação por dock_status
 -> DOCKED
```

Regras implementadas:

- DOCK não é disparado após SPRAY.
- DOCK só é aceito em estado seguro do lifecycle.
- Navegação ativa não é interrompida implicitamente por DOCK.
- O robô navega primeiro até a pose de aproximação da doca.
- A action de Dock só é iniciada depois da aproximação.
- Falhas deixam a missão em estado seguro/fail-closed.

Evidências:

- comando WebSocket DOCK foi aceito pelo bridge em estado válido;
- callback `_request_dock` está conectado ao `BridgeCore`;
- contrato, lifecycle e bridge estão alinhados com docking explícito.

---

# Task 5 --- Android transportar intents

Status: DONE

Branch de implementação:

```text
feat/android-transport-intents
```

Objetivo:

Permitir que o Android transporte corretamente os intents operacionais:

- SPRAY
- DOCK
- UNDOCK

sem acoplar o transporte a SPRAY.

## Alterações principais

### InteractionEngine

`Command` passou a carregar explicitamente:

```text
commandId
createdAt
intent
targetId opcional
```

Regras:

- SPRAY exige alvo resolvido.
- DOCK não exige alvo.
- UNDOCK não exige alvo.
- Todos os três intents exigem confirmação antes de gerar `Command`.
- Cancelamento e timeout continuam sem gerar comando.
- O intent operacional pendente é preservado até a confirmação.

### WebSocketCommandTransport

O transporte deixou de enviar `"intent": "SPRAY"` de forma fixa.

Agora serializa o intent real do comando.

SPRAY:

```json
{
  "intent": "SPRAY",
  "target": {
    "type": "MAPPED_PLOT",
    "id": "plot-03"
  }
}
```

DOCK:

```json
{
  "intent": "DOCK",
  "target": null
}
```

UNDOCK:

```json
{
  "intent": "UNDOCK",
  "target": null
}
```

O transporte continua validando `command_id` na resposta e evita completar o callback mais de uma vez.

### Bridge WebSocket

Foi corrigido o adaptador entre o servidor WebSocket e o `BridgeCore`:

```text
raw WebSocket message
 -> BridgeCore.handle(...)
 -> parse_command(...)
 -> handle_command(...)
 -> callback ROS
```

Erros de contrato retornam `REJECTED` em vez de quebrar o handler da conexão.

## Testes/evidências

Android:

```bash
cd mobile/android
./gradlew test
./gradlew assembleDatDebug
```

Resultados registrados:

```text
BUILD SUCCESSFUL
BUILD SUCCESSFUL
```

Foram adicionados testes explícitos para:

- DOCK gerar `Command(intent="DOCK", targetId=null)` somente após confirmação;
- UNDOCK gerar `Command(intent="UNDOCK", targetId=null)` somente após confirmação.

Teste físico Android:

- APK `datDebug` instalado em tablet Samsung físico;
- tablet conectado ao bridge via WebSocket na rede local;
- SPRAY foi reconhecido, confirmado e retornou:

```text
ACCEPTED
navigation goal queued
```

- Nav2 recebeu a meta e a odometria confirmou movimento do robô.

Teste manual do protocolo:

- DOCK foi aceito pelo bridge em estado válido;
- UNDOCK foi aceito pelo bridge em estado válido;
- rejeições observadas fora de `READY` são comportamento esperado do lifecycle fail-closed.

## Limite da Task 5

O classificador local atual ainda não reconhece de forma confiável frases naturais como:

```text
sair da doca
voltar para a base
```

e pode retornar `UNKNOWN`.

Isso não é falha do transporte da Task 5.

A evolução do classificador e do entendimento de linguagem pertence à Task 6.

---

# Task 6 --- Evolução da IA local

Status: PRÓXIMA

Objetivo:

Evoluir a interpretação local de linguagem sem permitir que o modelo controle ROS diretamente.

Arquitetura obrigatória:

```text
fala/transcrição
 -> IntentClassifier
 -> IntentPrediction estruturado
 -> InteractionEngine
 -> validações e confirmação
 -> Command
 -> WebSocket
 -> ROS
```

A IA interpreta linguagem; ela não executa comandos livres.

## Intents operacionais esperados

- SPRAY
- DOCK
- UNDOCK

Intents de controle:

- CONFIRM
- CANCEL
- UNKNOWN

## Trabalho da Task 6

1. Construir corpus de frases reais e variações de ASR.
2. Adicionar frases de DOCK e UNDOCK ao conjunto de avaliação.
3. Medir:
   - acurácia;
   - macro F1;
   - falsos accepts perigosos;
   - latência;
   - memória;
   - tamanho do artefato.
4. Testar no celular alvo de 6/8 GB de RAM.
5. Comparar a solução atual com alternativas locais.
6. Escolher a evolução com base em benchmark, não apenas em preferência de modelo.
7. Preservar a interface `IntentClassifier` para que o restante do app não dependa da implementação do modelo.

## Candidato para avaliação

Um candidato para a fase de experimentação é:

```text
Qwen2.5 1.5B Instruct quantizado
```

Mas a adoção não está decidida antes do benchmark.

Se um modelo menor/classificador dedicado atingir qualidade suficiente com menor latência e memória, ele deve ser preferido.

## Segurança

Mesmo com um LLM local:

```text
LLM/NLU
 -> saída estruturada
 -> validação
 -> confirmação
 -> Command
```

Nunca:

```text
LLM
 -> comando ROS livre
```

---

# Task 7 --- E2E final

Status: TODO

Objetivo:

Atualizar os testes e scripts E2E para o lifecycle explícito atual.

Fluxos mínimos:

### SPRAY

```text
READY
 -> SPRAY
 -> NAVIGATING
 -> READY
```

O robô permanece no destino.

Não há retorno automático à doca.

### UNDOCK

```text
READY
 -> UNDOCK explícito
 -> NEEDS_UNDOCK
 -> UNDOCKING
 -> READY
```

### DOCK

```text
READY
 -> DOCK explícito
 -> READY_TO_DOCK
 -> RETURNING_TO_DOCK
 -> READY_FOR_DOCK
 -> DOCKING
 -> DOCKED
```

Critérios:

- atualizar `make demo`, `make demo-route` e `make demo-visual` quando ainda tiverem expectativas do lifecycle antigo;
- validar Android físico -> WebSocket -> bridge -> ROS -> Gazebo;
- validar rejeições em estados inseguros;
- nenhuma ação automática de dock/undock após SPRAY;
- documentação final alinhada ao comportamento real.

---

# Regras

Antes de editar:

- Ler `AGENTS.md`.
- Ler `CONTRIBUTING.md`.
- Ler `docs/README.md`.
- Verificar `git status --porcelain`.
- Trabalhar uma task por vez.

Antes do commit:

```bash
git diff --check
git diff
git status
```

Usar Conventional Commits.

Mudanças de contrato, lifecycle ou segurança devem continuar fail-closed e cobertas por teste.

---

# Próximo passo

Executar somente:

```text
Task 6 --- Evolução da IA local
```

Não antecipar DAT/Meta Wearables para compensar pendências da IA ou do pipeline atual.

A integração Meta Wearables/DAT entra depois das Tasks 6 e 7, começando pela validação do sample oficial no aparelho real.
