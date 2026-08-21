# Teste integrado no Galaxy A17

Este roteiro é o gate planejado para provar a jornada `Android -> IA operacional -> WebSocket -> ROS 2/Nav2/Gazebo` no Galaxy A17 e, em seguida, validar a câmera/áudio com os Meta Wearables reais via DAT.

O runtime Qwen foi medido separadamente no Samsung SM-X510. Não use esses números como benchmark do Galaxy A17.

## Estado real antes do teste

- `mockDebug` e a UI Compose estão implementados.
- A `MainActivity` usa `InteractionEngine(LocalIntentClassifier, TargetResolver)`.
- O classificador operacional reconhece `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`.
- `datDebug` implementa o ciclo DAT 0.9.0 e passou pelos cenários pré-hardware do MockDeviceKit.
- O caminho DAT pré-hardware não comprova câmera dos óculos reais.
- Voz e TTS usam APIs Android; a rota real de microfone/áudio com os óculos ainda precisa ser observada.
- O runtime Qwen existe e passou em smoke no SM-X510, mas ainda não está conectado à `MainActivity`.

## Portabilidade da instalação

Não versione caminhos pessoais. Use JDK compatível com o Gradle do projeto e configure o Android SDK em `mobile/android/local.properties`:

```properties
sdk.dir=/caminho/individual/Android/Sdk
```

Antes do aparelho:

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest --no-daemon
./gradlew :app:assembleMockDebug --no-daemon
./gradlew :app:assembleDatDebug --no-daemon
```

Os três comandos devem terminar com `BUILD SUCCESSFUL`.

## Gate 1 — preparar o Galaxy A17

1. Ative **Opções do desenvolvedor**.
2. Ative **Depuração USB**.
3. Conecte com cabo de dados e aceite a chave RSA.
4. Confirme:

```bash
adb devices
```

Se o projeto ainda usar o preflight nesta máquina:

```bash
python3 mobile/android/tools/preflight.py --require-device
```

Não prossiga enquanto o aparelho estiver `unauthorized`.

## Gate 2 — app físico com flavor mock

Este gate valida o Android, a lógica operacional e o transporte sem atribuir o resultado aos óculos.

No computador:

```bash
make test-quick
make simulation-up
hostname -I
```

Computador e Galaxy devem estar na mesma rede. No telefone, use `ws://IP_DO_COMPUTADOR:18765`, nunca `127.0.0.1` ou `10.0.2.2`.

Instale o mock:

```bash
cd mobile/android
./gradlew :app:installMockDebug --no-daemon
```

Na UI:

1. confira o chip `câmera: mock`;
2. abra **Ajustes de teste** e configure o endpoint WebSocket;
3. toque **Olhar para o alvo**;
4. fale a operação ou use **Transcrição digitada** como contingência;
5. confira os cards **ALVO DETECTADO** e **INTENÇÃO**;
6. antes de qualquer movimento, confira a tela de confirmação e o countdown;
7. diga `sim` para confirmar ou `cancelar` para abortar;
8. confirme no Gazebo e nos logs que somente comandos confirmados chegam ao bridge.

### Lifecycle que deve ser observado

`SPRAY` não retorna automaticamente à doca.

Se o robô estiver dockado:

```text
UNDOCK explícito + confirmação
-> SPRAY + confirmação
-> robô permanece no alvo
-> DOCK explícito + confirmação, somente se desejado
```

Não trate scripts antigos que esperam dock automático como gate do comportamento atual.

## Gate 3 — comandos e recusas

No mock físico, cubra pelo menos:

- `SPRAY` com alvo válido;
- `DOCK` explícito;
- `UNDOCK` explícito;
- `CANCEL` durante confirmação;
- timeout de confirmação;
- alvo ausente;
- conflito entre alvo visual e alvo falado;
- `UNKNOWN`;
- tentativa incompatível com o estado atual do robô.

Resultado esperado para falhas: nenhum `Command` de movimento enviado.

## Gate 4 — DAT e Meta Wearables reais

Execute somente quando os óculos estiverem disponíveis.

1. Configure credenciais fora do Git.
2. Instale `datDebug`.
3. Pareie os Meta Wearables pelo fluxo oficial.
4. Confirme no app que a fonte não é `mock`.
5. Capture um frame sob demanda dos óculos.
6. Confirme que o target visual chega ao mesmo `InteractionEngine`.
7. Faça a jornada olhar -> falar -> ouvir operação entendida -> confirmar -> robô.
8. Teste permissão recusada, timeout, desconexão, QR ilegível e conflito de alvo.
9. Registre modelo do Android, versão do sistema, firmware dos óculos, versão DAT, rota de microfone/TTS, temperatura, bateria e latência.

O gate só passa se a imagem observada vier dos óculos. MockDeviceKit, câmera do telefone ou ID digitado não comprovam DAT físico.

## Gate opcional — Qwen

O Qwen não faz parte do caminho operacional atual da `MainActivity`. Só execute este gate no Galaxy A17 depois que o wiring seguro `UNKNOWN -> LanguageRouter -> QwenDomainAssistant` estiver implementado.

Antes disso, qualquer teste com `QwenSmokeActivity` prova apenas o runtime isolado.

Quando o wiring existir, validar:

1. `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM` e `CANCEL` não esperam pelo Qwen;
2. somente `UNKNOWN` chega ao assistente;
3. pedido como `Faça dock agora.` não vira ação pelo assistente;
4. resposta inválida falha para `OUT_OF_SCOPE`;
5. câmera DAT + STT/TTS + Qwen cabem na memória sem swap/temperatura inaceitáveis.

## Localização rápida de falhas

| Sintoma | Camada provável | Primeira verificação |
|---|---|---|
| Galaxy não aparece | USB/ADB | `adb devices` e autorização RSA |
| App não compila | JDK/SDK/Gradle | gates de build Android |
| Falha de registro Meta | DAT/configuração | app Meta AI, credenciais e manifesto |
| Voz não transcreve | permissão/rota | `RECORD_AUDIO` e teste local |
| `UNKNOWN` operacional | IA local | frase, confiança e origem RULE/MODEL |
| WebSocket falha | rede/firewall | IP do computador e porta 18765 |
| `ACCEPTED`, mas não move | ROS/Nav2/estado | logs do bridge e lifecycle |
| QR e voz discordam | `TargetResolver` | esperado: conflito, sem comando |
| Qwen lento | runtime local | só relevante após wiring; medir cold/warm e memória |

## Encerramento

```bash
make simulation-down
```

Não declare DAT físico, áudio dos óculos ou benchmark Qwen no Galaxy A17 como aprovados até os respectivos gates ocorrerem nesse hardware.