# Roadmap --- Dock e Undock como comandos explícitos

## Status atual

- Task 0 --- Versionar TASKS.md: DONE
- Task 1 --- Remover dock/undock automático: DONE
- Task 2 --- Adicionar DOCK/UNDOCK ao contrato: DONE
- Task 3 --- Implementar comando explícito UNDOCK: DONE
- Task 4 --- Implementar comando explícito DOCK: DONE
- Task 5 --- Android transportar intents: DONE
- Task 6 --- Evolução da IA local: DONE (fallback seguro integrado e validado na MainActivity)
- Task 7 --- E2E final e preparação da demonstração: EM ANDAMENTO

---

# Prioridades até a entrega de sábado

O objetivo principal agora é fechar uma demonstração vertical estável do MVP.

A prioridade é preservar o classificador operacional já validado e integrar o assistente Qwen apenas como fallback conversacional, sem autoridade sobre comandos.

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
APROVADO — PRÉ-HARDWARE COM MOCKDEVICEKIT
```

Objetivo:

Validar o caminho real dos óculos até o aplicativo.

Próximos passos:

- repetir o sample oficial no hardware real quando os óculos chegarem;
- validar sessão/captura de câmera física;
- validar o mesmo adaptador com o frame real;
- substituir o MockDeviceKit somente no ensaio físico;
- manter o mock como fallback de demonstração.

Plano pré-hardware:

- [x] confirmar DAT 0.9.0 e o ciclo oficial `addCamera()`;
- [x] registrar a spec e separar validação simulada da validação física;
- [x] compilar e instalar `datDebug` com autenticação local `read:packages`;
- [x] implementar sessão, câmera, captura sob demanda e encerramento;
- [x] executar o sample oficial `CameraAccess` com MockDeviceKit;
- [x] conectar a foto ao detector QR Android com ZXing 3.5.4 aprovado;
- [x] executar sucesso, permissão recusada, timeout e desconexão no
  MockDeviceKit;
- [x] repetir testes/build de `mockDebug` e registrar a evidência sanitizada;

Detalhes e critérios: [`docs/tasks/dat-prehardware.md`](docs/tasks/dat-prehardware.md).

Validação em hardware real permanece bloqueada até a disponibilidade dos
óculos. Resultado com MockDeviceKit não deve ser apresentado como captura dos
Meta Wearables físicos.

A integração DAT não deve quebrar o pipeline já funcional.

---

## 2. Melhorias da interface Android

Status:

```text
CONCLUÍDA
```

Objetivo:

Transformar a tela atual de diagnóstico em uma interface mais próxima de demonstração.

Entregue:

- jornada apresentada como trilha de quatro passos: `Alvo`, `Intenção`, `Confirmar`, `Executar`;
- destaque próprio para:
  - alvo detectado, com origem (câmera, voz ou concordância);
  - intenção reconhecida, com confiança e origem da classificação;
  - confirmação pendente, com contagem regressiva e a frase esperada;
  - comando enviado;
  - estado do robô, rotulado como último comando aceito pelo bridge;
- mensagens de voz em português natural (`talhão 3`, não `plot-03`), com anúncio por intent e recusa sem ler motivo técnico em inglês;
- endpoint WebSocket e transcrição digitada recolhidos em "Ajustes de teste", fechado por padrão;
- cancelamento, ambiguidade e recusa nunca aparecem como execução.

Regras preservadas:

- confirmação continua exigindo áudio; nenhum botão de toque confirma comando;
- contrato, bridge, lifecycle e modelo de IA não foram alterados.

Detalhes, evidências e limitações: [`docs/tasks/android-demo-ui.md`](docs/tasks/android-demo-ui.md).

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

Status: DONE — benchmark, isolamento de segurança, runtime Android e integração no fluxo principal concluídos.

Objetivo:

Adicionar um assistente local de domínio sem substituir o classificador operacional e sem permitir que um LLM controle ROS, WebSocket ou estado do robô.

Arquitetura decidida:

```text
fala/transcrição
 -> LocalIntentClassifier
 -> rótulo operacional? -> InteractionEngine -> confirmação -> Command -> WebSocket -> ROS
 -> UNKNOWN?            -> LanguageRouter -> QwenDomainAssistant -> CHAT | OUT_OF_SCOPE
```

Regras obrigatórias:

- `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM` e `CANCEL` nunca esperam pelo Qwen;
- Qwen recebe somente o caminho que o classificador operacional marcou como `UNKNOWN`;
- Qwen nunca produz `Command`, pose ROS, payload WebSocket ou mudança de estado;
- saída do assistente é limitada a `CHAT` ou `OUT_OF_SCOPE` e falha fechada para `OUT_OF_SCOPE`;
- `TargetResolver` continua sendo a única fronteira de resolução de alvo; Qwen não duplica esse papel;
- confirmação de movimento permanece no `InteractionEngine`.

## Evidência de seleção do papel do Qwen

O benchmark reproduzível em `shared/ai/qwen_evaluation.json` testou Qwen2.5-1.5B-Instruct Q4_K_M como classificador dos seis rótulos operacionais:

- 48 exemplos;
- 36 corretos;
- acurácia 0,75;
- macro-F1 0,7384;
- 3 aceites perigosos (`CANCEL/UNKNOWN` virando intenção positiva).

Conclusão: Qwen foi rejeitado como classificador operacional. O `LocalIntentClassifier` continua sendo a autoridade de controle.

## Runtime Android concluído

Implementado:

- submodule `llama.cpp` pinado no commit `873e5d8e39feb34a376e0efd01bf3f665dfffeb5`;
- CMake/JNI ARM64 integrado ao app Android;
- Qwen2.5-1.5B-Instruct-GGUF `Q4_K_M` carregado localmente;
- contexto 2048, batch 512, 4 threads e máximo de 64 tokens por resposta;
- system prompt canônico reduzido para 603 tokens no smoke final;
- GBNF restringindo a saída a JSON com `CHAT` ou `OUT_OF_SCOPE`;
- grammar parseada uma vez no carregamento e clonada por geração;
- cache do system prompt preservado entre perguntas sem acumular histórico de conversa;
- Activity de smoke exclusiva do flavor `mock`.

## Wiring seguro na MainActivity

Implementado em 22/08/2026:

- `LanguageInteractionController` mantém o `LocalIntentClassifier` como primeira autoridade;
- operações e todo o estado de confirmação seguem diretamente para o `InteractionEngine`;
- apenas `UNKNOWN` em `IDLE` ou `TARGET_READY` inicia o assistente;
- a UI mostra `Processando resposta local…` sem bloquear novas operações;
- resposta atrasada é descartada depois de operação, captura de alvo, nova escuta ou reinício;
- ausência/falha do GGUF preserva o fallback seguro e nunca cria `Command`.

## Smoke físico no SM-X510

Em 21/08/2026, no Samsung SM-X510 (Android API 36, ARM64), o smoke final passou 5/5:

- carregamento do modelo + cache do prompt: 33.291,911 ms;
- primeira resposta, incluindo cold start: 42.084 ms;
- respostas warm: 5.909 ms, 5.755 ms, 5.780 ms e 5.714 ms;
- PSS após o smoke: 1.377.044 KB;
- RSS: 1.451.773 KB;
- Swap PSS: 273 KB;
- os pedidos `Faça dock agora.` e `Como fazer bolo de chocolate?` retornaram `OUT_OF_SCOPE`;
- perguntas de domínio sobre Maestro, AgroTurtles e confirmação retornaram `CHAT`.

Limitações:

- cold start medido entre ~33 s no SM-X510 e ~43,8 s no Edge 40 Neo; preload continua uma decisão condicionada ao teste de memória combinado;
- warm latency medida entre ~5,7–5,9 s no SM-X510 e ~7,3 s no Edge 40 Neo;
- o GGUF de ~1,1 GB não é versionado nem empacotado no APK atual;
- convivência com DAT, câmera e áudio simultâneos ainda não foi medida;
- o gate físico combinado no aparelho final do evento continua pertencendo à Task 7.

Critério final da Task 6 concluído:

- `testMockDebugUnitTest` e `testDatDebugUnitTest`: 60/60 cada;
- `assembleMockDebug` e `assembleDatDebug`: `BUILD SUCCESSFUL`;
- no Edge 40 Neo/API 35, `CHAT`, `OUT_OF_SCOPE` e `DOCK` direto sem chamada ao Qwen foram observados na `MainActivity`;
- a recriação por rotação descartou a conversa anterior sem crash;
- nenhum erro `AndroidRuntime` e nenhum comando criado nos casos conversacionais.

Evidência detalhada: [`docs/tasks/qwen-android-runtime.md`](docs/tasks/qwen-android-runtime.md).

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

Foco até a entrega:

1. Integrar o fallback conversacional Qwen à `MainActivity` sem tocar na autoridade operacional do `InteractionEngine`.
2. Atualizar e executar o E2E do lifecycle explícito no Gazebo.
3. Validar DAT/câmera/áudio com os Meta Wearables físicos quando disponíveis.
4. Registrar evidência final Android → WebSocket → ROS 2/Nav2/Gazebo.
5. Congelar documentação, formulário e pitch a partir do comportamento realmente demonstrado.
