# Tarefas do MVP — 16 a 22 de agosto de 2026

> Este quadro começou como o plano da primeira semana. Os checkboxes abaixo foram atualizados para refletir o estado real ao final de 21/08/2026. A ordem canônica das Tasks de evolução está em `../../TASKS.md`.

## Corte atual

A jornada operacional é:

```text
alvo mapeado
-> intenção operacional local
-> resolução/validação
-> confirmação explícita
-> Command JSON
-> WebSocket
-> ROS 2/Nav2/Gazebo
```

`SPRAY` navega para o alvo e permanece lá. `DOCK` e `UNDOCK` são comandos explícitos. O assistente Qwen não participa do controle do robô.

## Estado consolidado

- [x] Contratos JSON 1.0 e fixtures.
- [x] Classificador operacional local.
- [x] Rótulos `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL`, `UNKNOWN`.
- [x] Bridge ROS 2 com expiração/deduplicação.
- [x] Lifecycle sem dock/undock implícito após `SPRAY`.
- [x] `DOCK` e `UNDOCK` explícitos.
- [x] Transporte Android das intenções operacionais.
- [x] UI Compose de demonstração.
- [x] DAT 0.9.0 pré-hardware + MockDeviceKit.
- [x] Visão/QR e `TargetResolver`.
- [x] Runtime Qwen local via `llama.cpp` e smoke físico no SM-X510.
- [x] Wiring `UNKNOWN -> QwenDomainAssistant` na `MainActivity`.
- [ ] E2E final atualizado para o lifecycle explícito.
- [ ] DAT/câmera/áudio provados nos Meta Wearables reais.
- [ ] Jornada física final repetida e registrada.

## Android / DAT

### Concluído

- [x] `mockDebug` compilável e instalável.
- [x] `datDebug` compilável.
- [x] UI com alvo, intenção, confirmação, countdown e estado do último comando aceito.
- [x] voz/TTS por APIs Android.
- [x] adaptador DAT 0.9.0.
- [x] cenários MockDeviceKit de sucesso, permissão recusada, timeout e desconexão.
- [x] detector QR local no caminho DAT.
- [x] builds combinados após sincronização Qwen + UI/DAT:
  - `:app:testMockDebugUnitTest`;
  - `:app:assembleMockDebug`;
  - `:app:assembleDatDebug`.

### Pendente

- [ ] pareamento e sample oficial no hardware real;
- [ ] frame real dos Meta Wearables;
- [ ] validar rota real de microfone/TTS;
- [ ] medir câmera + voz + app simultaneamente.

## IA operacional

### Concluído

- [x] classificador local compartilhado e assets Android;
- [x] seis rótulos operacionais/interativos;
- [x] paridade e testes de segurança;
- [x] corpus de campo de 48 casos para os seis rótulos;
- [x] baseline local 48/48 no gate usado na Task 6.

### Regra

`UNKNOWN` é seguro. Um falso negativo pode impedir uma ação; um falso positivo perigoso pode mover o robô. Por isso a prioridade continua sendo evitar aceites indevidos.

## Assistente Qwen

### Concluído

- [x] benchmark Qwen2.5-1.5B Q4_K_M como classificador;
- [x] rejeição do Qwen como autoridade operacional após 36/48 e 3 aceites perigosos;
- [x] `LanguageRouter`, `QwenDomainAssistant` e saída `CHAT | OUT_OF_SCOPE`;
- [x] system prompt canônico sem RAG;
- [x] `llama.cpp` pinado e compilado no Android ARM64;
- [x] JNI/CMake + `NativeQwenEngine`;
- [x] GBNF estruturada;
- [x] smoke físico 5/5 no SM-X510;
- [x] load ~33,3 s; warm ~5,7–5,9 s; PSS ~1,38 GB; Swap PSS 273 KB.
- [x] wiring e smoke da `MainActivity` no Edge 40 Neo/API 35;
- [x] feedback `Processando resposta local…` e descarte de callback obsoleto.

### Pendente

- [ ] medir convivência com DAT/câmera/áudio;
- [ ] decidir preload antes da demo.

## Visão e alvo

- [x] QR/placas de plots mapeados.
- [x] detector retorna target conhecido ou falha segura.
- [x] política compartilhada visual + voz.
- [x] conflito entre IDs cancela a resolução.
- [x] `TargetResolver` permanece fora do Qwen.

## Robótica e lifecycle

- [x] bridge WebSocket/ROS 2.
- [x] Nav2/Gazebo/TurtleBot 4.
- [x] `SPRAY` sem undock automático.
- [x] `SPRAY` sem retorno automático à doca.
- [x] `UNDOCK` explícito.
- [x] `DOCK` explícito.
- [x] Android transporta as três operações.
- [ ] scripts E2E antigos atualizados para parar de exigir lifecycle automático.

## Segurança

Nenhum movimento deve ocorrer sem:

1. intenção operacional suportada;
2. target válido quando a intenção exigir;
3. estado compatível;
4. confirmação explícita;
5. comando dentro da validade;
6. aceitação pelo bridge.

Qwen não satisfaz nenhuma dessas condições e não pode criar `Command`.

## Gate de fechamento

O MVP está pronto para congelamento quando:

- `mockDebug` e `datDebug` compilam;
- regressões unitárias passam;
- o E2E atualizado demonstra `UNDOCK`/`SPRAY`/`DOCK` apenas quando explícitos;
- a jornada física com Meta Wearables reais foi executada ou a pendência foi declarada com clareza;
- se Qwen aparecer na demo, o wiring está isolado e a jornada operacional continua funcionando sem ele.
