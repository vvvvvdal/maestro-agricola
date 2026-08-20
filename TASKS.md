# Roadmap --- Dock e Undock como comandos explícitos

## Status atual

- Task 0 --- Versionar TASKS.md: DONE
- Task 1 --- Remover dock/undock automático: DONE
- Task 2 --- Adicionar DOCK/UNDOCK ao contrato: DONE
- Task 3 --- Implementar comando explícito UNDOCK: DONE
- Task 4 --- Implementar comando explícito DOCK: DONE
- Task 5 --- Android transportar intents: DONE
- Task 6 --- Evolução da IA local: EM AVALIAÇÃO (não é foco da entrega atual)
- Task 7 --- E2E final e preparação da demonstração: EM ANDAMENTO

---

# Prioridades até a entrega de sábado

O objetivo principal agora é fechar uma demonstração vertical estável do MVP.

A prioridade não é trocar o modelo de IA neste momento.

O sistema atual já possui:

```text
voz
 -> reconhecimento de fala Android
 -> IntentClassifier local
 -> InteractionEngine
 -> confirmação por áudio
 -> JSON/WebSocket
 -> ROS 2 Bridge
 -> Nav2/Gazebo
```

A entrega deve priorizar:

## 1. Meta Wearables / DAT

Status:

```text
PENDENTE
```

Objetivo:

Validar o caminho real dos óculos até o aplicativo.

Próximos passos:

- executar o sample oficial do DAT;
- validar sessão/captura de câmera;
- integrar o frame real ao fluxo existente;
- substituir o mock somente onde for necessário;
- manter o mock como fallback de demonstração.

A integração DAT não deve quebrar o pipeline já funcional.

---

## 2. Melhorias da interface Android

Status:

```text
EM ANDAMENTO
```

Objetivo:

Transformar a tela atual de diagnóstico em uma interface mais próxima de demonstração.

Melhorias prioritárias:

- melhorar apresentação visual da jornada;
- destacar:
  - alvo detectado;
  - intenção reconhecida;
  - confirmação pendente;
  - comando enviado;
  - estado do robô;
- melhorar mensagens de voz;
- remover elementos exclusivamente de debug quando possível;
- deixar o fluxo claro para avaliadores.

---

## 3. Demonstração completa Gazebo + Android

Status:

```text
EM VALIDAÇÃO
```

Fluxo esperado:

### UNDOCK

```text
READY
 -> UNDOCK explícito
 -> confirmação
 -> robô sai da doca
```

### SPRAY

```text
READY
 -> SPRAY plot-XX
 -> confirmação
 -> Nav2
 -> robô chega ao destino
 -> permanece no destino
```

### DOCK

```text
READY
 -> DOCK explícito
 -> aproximação
 -> docking
 -> DOCKED
```

Critério principal:

Nenhuma ação automática deve acontecer.

O operador sempre inicia a ação.

---

## 4. Pitch e documentação

Status:

```text
PENDENTE
```

Prioridades:

- gravar vídeo/pitch;
- preparar narrativa da solução;
- explicar diferencial:
  - comando hands-free;
  - segurança por confirmação;
  - integração visão + voz + robótica;
  - uso de TurtleBot 4/Nav2/Gazebo como validação antecipada.

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

Evidências:

- suíte do bridge passando;
- suíte geral passando;
- contrato validando os três intents.

---

# Task 3 --- Implementar comando explícito UNDOCK

Status: DONE

Objetivo:

Executar Undock somente via comando explícito.

Fluxo:

```text
WebSocket
 -> BridgeCore
 -> Bridge Node
 -> MissionCycle
 -> /turtlebot1/undock action
```

Regras:

- UNDOCK somente por intent explícita.
- SPRAY nunca chama Undock implicitamente.
- Falhas deixam missão em estado seguro.
- Estado dockado confirmado por `dock_status`.
- Lifecycle retorna a estado seguro após sucesso.

Evidências:

- comando WebSocket UNDOCK aceito em estado válido;
- callback `_request_undock` conectado;
- testes do bridge validados.

---

# Task 4 --- Implementar comando explícito DOCK

Status: DONE

Objetivo:

Executar docking somente por comando explícito.

Fluxo:

```text
DOCK
 -> MissionCycle
 -> Nav2 para aproximação
 -> Dock action
 -> dock_status
 -> DOCKED
```

Regras:

- DOCK não é disparado após SPRAY.
- Navegação ativa não é interrompida implicitamente.
- Aproximação acontece antes da action de Dock.
- Falhas deixam sistema fail-closed.

Evidências:

- comando DOCK aceito pelo bridge;
- callback `_request_dock` conectado;
- lifecycle alinhado.

---

# Task 5 --- Android transportar intents

Status: DONE

Objetivo:

Transportar:

- SPRAY
- DOCK
- UNDOCK

sem acoplamento ao SPRAY.

Alterações:

## InteractionEngine

Command possui:

```text
commandId
createdAt
intent
targetId opcional
```

Regras:

- SPRAY exige alvo.
- DOCK não exige alvo.
- UNDOCK não exige alvo.
- Todos exigem confirmação.

## WebSocketCommandTransport

Agora envia o intent real:

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

Testes:

- Android build passando;
- intents DOCK/UNDOCK gerando comandos corretos;
- teste manual em Android físico;
- bridge aceitando comandos.

---

# Task 6 --- Evolução da IA local

Status: EM AVALIAÇÃO (não é prioridade da entrega)

Objetivo original:

Avaliar evolução do classificador local sem permitir que a IA controle ROS diretamente.

Arquitetura mantida:

```text
fala/transcrição
 -> IntentClassifier
 -> IntentPrediction
 -> InteractionEngine
 -> confirmação
 -> Command
 -> ROS
```

## Estado atual

O classificador atual já suporta:

- SPRAY
- DOCK
- UNDOCK
- CONFIRM
- CANCEL
- UNKNOWN

O modelo atual foi validado no aplicativo.

DOCK e UNDOCK passaram a ser reconhecidos após atualização do asset:

```text
shared/ai/intent_model.json
```

e rebuild do aplicativo.

## Decisão atual

Não implementar Qwen2.5 1.5B antes da entrega.

Motivos:

- risco de integração;
- tempo limitado;
- necessidade de validar memória/latência no aparelho;
- arquitetura atual já atende o fluxo principal.

Qwen2.5 1.5B permanece como trabalho futuro de pesquisa.

Possível evolução futura:

```text
Qwen/NLU
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

# Task 7 --- E2E final e demonstração

Status: EM ANDAMENTO

Objetivo:

Fechar o fluxo completo demonstrável.

Pendências:

- atualizar scripts E2E antigos;
- validar Android -> WebSocket -> Bridge -> ROS -> Gazebo;
- integrar DAT quando possível;
- melhorar interface;
- gravar demonstração.

Critérios:

- nenhuma ação automática de dock/undock;
- confirmação obrigatória;
- comando seguro;
- robô executando no Gazebo;
- narrativa clara para avaliação.

---

# Regras

Antes de editar:

- Ler `AGENTS.md`.
- Ler `CONTRIBUTING.md`.
- Ler documentação relacionada.
- Verificar:

```bash
git status --porcelain
```

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

Foco até sábado:

1. Fechar demo Gazebo.
2. Integrar/verificar DAT.
3. Melhorar interface Android.
4. Gravar pitch.
5. Apenas depois avaliar Qwen ou mudanças maiores de IA.