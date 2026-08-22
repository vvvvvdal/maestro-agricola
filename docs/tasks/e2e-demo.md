# Integração da demonstração ponta a ponta

## Status

**DONE em 22/08/2026 — E2E pré-hardware validado no Android físico com `datDebug` + MockDeviceKit, WebSocket, ROS 2/Nav2 e Gazebo.**

A validação com Meta Wearables físicos fica para a fase posterior caso a equipe avance no programa. O resultado desta task não deve ser apresentado como captura física dos óculos.

## Objetivo

Fechar uma jornada segura entre fonte DAT pré-hardware, alvo mapeado, intenção operacional, confirmação, WebSocket e ROS 2/Nav2/Gazebo sem lifecycle implícito.

## Arquitetura da jornada

```text
DAT 0.9.0 / MockDeviceKit -> câmera/target
voz -> LocalIntentClassifier
     -> TargetResolver/validações
     -> InteractionEngine
     -> confirmação
     -> Command JSON
     -> WebSocket
     -> bridge ROS 2
     -> Nav2/Gazebo
```

O Qwen não participa deste caminho. Apenas `UNKNOWN`, em estado seguro para conversa, pode ser desviado ao assistente `CHAT | OUT_OF_SCOPE`; o assistente nunca produz `Command`.

## Decisões atuais

- QR/target previamente mapeado é o caminho do MVP.
- `SPRAY` pode usar target visual ou ID falado quando a política permitir.
- IDs visual e falado divergentes resultam em conflito, sem comando.
- `SPRAY` navega até o target e permanece lá.
- `DOCK` e `UNDOCK` são ações operacionais explícitas, separadas e confirmadas.
- `SPRAY` nunca causa `UNDOCK`, retorno à doca ou `DOCK` automaticamente.
- `UNDOCK` espera a action nativa terminar; `dock_status=false` antecipado não cancela a manobra.
- Após `DOCKED`, um novo `UNDOCK` explícito é permitido.
- GPS do celular não é direção da cabeça nem pose do alvo.
- Qwen nunca resolve target, inventa pose ou produz `Command`.

## Evidência E2E observada

Ambiente: Samsung SM-X510, Android API 36, `datDebug` com `-PmaestroDatMockDevice=true`, bridge em `:18765`, namespace ROS `/turtlebot1`.

Fluxo positivo observado:

```text
UNDOCK explícito + confirmação
-> Undock Goal Succeeded
-> robot is clear of dock
-> captura DAT/MockDeviceKit resolve plot-03
-> SPRAY + confirmação
-> Nav2 accepted/completed plot-03
-> robô permanece fora da doca
-> DOCK explícito + confirmação
-> Nav2 até dock approach
-> Dock Goal accepted / Dock Servo Goal Succeeded
-> is_docked=true
-> novo UNDOCK explícito
-> Undock Goal Succeeded
```

A captura `Olhar para o alvo` também foi repetida várias vezes na mesma execução após corrigir o rearm do MockDeviceKit; todas voltaram a identificar `plot-03`.

## Guardrails observados

### SPRAY com robô dockado

`SPRAY` foi tentado com `is_docked=true`. Não houve `Nav2 accepted`, não houve `Undock goal accepted` e o estado final permaneceu dockado. PASS.

### Conflito entre visão e voz

```text
visual = plot-03
voz = plot-01
-> AMBÍGUO
-> "Alvo falado e visual não conferem"
-> nenhum Command
-> nenhum movimento
```

PASS.

### CANCEL

Durante `AWAITING_CONFIRMATION`, `cancelar` produziu `CANCELADO / Nada foi enviado ao robô`. O log do bridge permaneceu sem novo comando. PASS.

### UNKNOWN

Uma frase fora do caminho operacional foi classificada como `UNKNOWN` e não criou confirmação nem movimento. O GGUF do Qwen não estava provisionado no `datDebug` instalado naquele momento, então a UI usou o fallback seguro genérico. Isso é uma limitação do assistente opcional, não do caminho operacional. PASS para segurança operacional.

## Contrato, expiração e idempotência

A Task 7 adicionou cobertura explícita para:

- `confirmed=false` -> `REJECTED`;
- comando com `expires_in_ms` vencido -> `REJECTED`;
- mesmo `command_id` recebido novamente -> resposta anterior retornada, sem repetir callback ROS.

O cache de idempotência do bridge é limitado e protegido por lock.

## Gates automatizados finais

Na `main`, após o merge do lifecycle E2E:

```text
model artifacts: up to date (read-only check)
raw accuracy: 1.000 (64/64)
operational accuracy: 1.000 (64/64, threshold=0.4)
macro F1: 1.000; unsafe accepts: 0
portable tests: 65/65
bridge tests: 36/36
```

## Critérios de aceite da Task 7

1. `datDebug` + MockDeviceKit executa a jornada operacional contra o bridge atual: **PASS**.
2. `SPRAY` dockado é rejeitado até `UNDOCK` explícito: **PASS**.
3. `UNDOCK` explícito chega à action e completa a manobra nativa: **PASS**.
4. `SPRAY` confirmado navega para plot válido e termina sem retorno automático: **PASS**.
5. `DOCK` explícito navega para a aproximação e executa Dock: **PASS**.
6. `CANCEL`, `UNKNOWN`, conflito de target e estado incompatível não produzem movimento; timeout permanece coberto pela máquina de estados/testes: **PASS**.
7. `command_id`, expiração e deduplicação possuem cobertura explícita: **PASS**.
8. Scripts legados `make demo*` não são usados como gate normativo do lifecycle atual: **PASS para o MVP; reescrita fica como dívida não bloqueante**.
9. Flavors Android `mockDebug` e `datDebug` permanecem construíveis; o E2E final foi executado no `datDebug`: **PASS**.
10. Evidência distingue simulação, MockDeviceKit e hardware Meta real: **PASS**.

## Fora de escopo desta entrega

- pulverização física;
- navegação criada pelo Maestro;
- pose/IMU/GPS como substituto do target mapeado;
- linguagem natural irrestrita com autoridade de controle;
- Qwen gerando comando;
- afirmar DAT físico sem frame real dos Meta Wearables.

## Resultado

A evidência final é coerente entre código, testes e execução:

```text
ações físicas explícitas + confirmação
-> JSON versionado, expirável e idempotente
-> WebSocket
-> ROS 2/Nav2
-> nenhum lifecycle escondido
```