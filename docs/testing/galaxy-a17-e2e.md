# Teste integrado no Android físico

> O arquivo mantém o nome histórico `galaxy-a17-e2e.md`, mas o E2E final pré-hardware de 22/08/2026 foi executado em um Samsung SM-X510/API 36.

Este roteiro prova a jornada `Android -> IA operacional -> WebSocket -> ROS 2/Nav2/Gazebo` com `datDebug` + MockDeviceKit. O gate com Meta Wearables físicos é posterior e só deve ser executado quando o hardware estiver disponível na fase presencial.

## Estado validado

- `MainActivity` mantém `InteractionEngine(LocalIntentClassifier, TargetResolver)` como caminho operacional.
- O classificador reconhece `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`.
- `datDebug` implementa DAT 0.9.0 e MockDeviceKit.
- A captura pré-hardware foi repetida várias vezes na mesma execução e resolveu `plot-03`.
- Voz/TTS usam APIs Android.
- O Qwen é opcional e fica fora do caminho operacional.
- ROS 2/Nav2/Gazebo usa namespace `/turtlebot1` e bridge WebSocket `:18765`.

## Gate 1 — build e testes

```bash
make test

cd mobile/android
./gradlew :app:testMockDebugUnitTest --no-daemon
./gradlew :app:assembleMockDebug --no-daemon
./gradlew -PmaestroDatMockDevice=true :app:assembleDatDebug --no-daemon
```

Resultado final do gate de software em 22/08/2026:

```text
raw accuracy: 1.000 (64/64)
operational accuracy: 1.000 (64/64, threshold=0.4)
macro F1: 1.000; unsafe accepts: 0
portable tests: 65/65
bridge tests: 36/36
```

## Gate 2 — preparar o Android físico

1. Ative Opções do desenvolvedor e Depuração USB.
2. Conecte o aparelho e aceite a chave RSA.
3. Confirme:

```bash
adb devices
```

4. Instale o `datDebug` construído com MockDeviceKit.
5. No app, configure `ws://IP_DO_COMPUTADOR:18765`.
6. Computador e Android devem estar na mesma rede local.

## Gate 3 — lifecycle positivo

Não use os botões Dock/Undock do HMI como parte do teste. O lifecycle deve ser comandado pelo Maestro.

```text
robô inicialmente dockado
-> "sair da doca"
-> confirmar
-> Undock Goal Succeeded
-> "Olhar para o alvo" -> plot-03
-> "pulverizar"
-> confirmar
-> Nav2 accepted/completed plot-03
-> robô permanece no alvo
-> "voltar para a doca"
-> confirmar
-> Nav2 até dock approach
-> Dock Goal Succeeded
-> "sair da doca" novamente
-> confirmar
-> segundo Undock Goal Succeeded
```

O bridge não deve cancelar o `Undock` assim que `dock_status` mudar para `false`; deve aguardar o resultado nativo para o robô terminar de limpar a doca.

## Gate 4 — guardrails

### SPRAY dockado

Com `is_docked=true`, tente `SPRAY`. Resultado esperado: recusa, nenhum `Nav2 accepted`, nenhum `Undock goal accepted` e `is_docked` continua `true`.

### Conflito visão × voz

```text
Olhar para o alvo -> plot-03
voz -> "pulverizar talhão 01"
resultado -> AMBÍGUO / alvo falado e visual não conferem
nenhum Command
```

### CANCEL

Entre em confirmação de `SPRAY` e diga `cancelar`. Resultado esperado: `CANCELADO / Nada foi enviado ao robô`, sem novo log no bridge.

### UNKNOWN

Frase fora do caminho operacional não pode abrir execução nem mover o robô. Se o GGUF do Qwen não estiver provisionado, o fallback seguro genérico é aceitável para a segurança operacional.

### Contrato

- `confirmed=false`: rejeitado;
- expirado: rejeitado;
- `command_id` repetido: resposta deduplicada e callback ROS executado uma única vez.

## Gate 5 — DAT/MockDeviceKit pré-hardware

Construção recomendada:

```bash
cd mobile/android
./gradlew \
  -PmaestroDatMockDevice=true \
  -PmaestroDatMockScenario=success \
  :app:assembleDatDebug --no-daemon
```

O resultado comprova o caminho do código DAT e a integração pré-hardware com MockDeviceKit. Não comprova câmera física dos Meta Wearables.

## Gate futuro — Meta Wearables reais

Execute somente se a equipe avançar para a fase com hardware:

1. remover o modo MockDeviceKit;
2. parear Meta Wearables pelo fluxo oficial;
3. capturar frame real;
4. validar target visual no mesmo `InteractionEngine`;
5. validar rota de microfone/TTS;
6. repetir lifecycle e guardrails;
7. medir latência, memória, temperatura e bateria.

MockDeviceKit, câmera do telefone ou ID digitado nunca devem ser descritos como prova de câmera física dos óculos.

## Qwen opcional

O wiring seguro `UNKNOWN -> QwenDomainAssistant` existe, mas o GGUF de ~1,1 GB não é empacotado no APK. Depois de reinstalar um flavor, confirme que existe:

```text
files/qwen2.5-1.5b-q4_k_m.gguf
```

Sem esse arquivo, o caminho operacional continua funcionando e `UNKNOWN` deve falhar de forma segura; apenas a resposta conversacional fica indisponível.

## Encerramento

```bash
make simulation-down
```