# Integração da demonstração ponta a ponta

## Status

Integração parcial concluída; **Task 7 ainda pendente** para revalidar o E2E conforme o lifecycle explícito atual.

## Objetivo

Fechar uma jornada segura entre Android, alvo mapeado, intenção operacional, confirmação, WebSocket e ROS 2/Nav2/Gazebo sem depender de lifecycle implícito.

## Arquitetura da jornada

```text
câmera/target + voz
-> LocalIntentClassifier
-> TargetResolver/validações
-> InteractionEngine
-> confirmação
-> Command JSON
-> WebSocket
-> bridge ROS 2
-> Nav2/Gazebo
```

O Qwen não participa deste caminho. Com o wiring da Task 6, apenas `UNKNOWN` em estado seguro para conversa pode ser desviado para `CHAT | OUT_OF_SCOPE`.

## Decisões atuais

- QR/target previamente mapeado continua sendo o caminho do MVP.
- `SPRAY` pode usar target visual ou ID falado quando a política permitir.
- IDs visual e falado divergentes resultam em conflito, sem comando.
- `SPRAY` navega até o target e permanece lá.
- `DOCK` e `UNDOCK` são ações operacionais explícitas, separadas e confirmadas.
- `SPRAY` nunca causa `UNDOCK`, retorno à doca ou `DOCK` automaticamente.
- GPS do celular não é direção da cabeça nem pose do alvo.
- Qwen nunca resolve target, inventa pose ou produz `Command`.

## Critérios de aceite da Task 7

1. `mockDebug` executa a jornada operacional contra o bridge atual.
2. Se o robô estiver dockado, `SPRAY` é rejeitado até um `UNDOCK` explícito e confirmado.
3. `UNDOCK` explícito chega à action correspondente.
4. `SPRAY` confirmado navega para um plot válido e termina sem retorno automático.
5. `DOCK` explícito navega para a aproximação configurada e executa Dock.
6. `CANCEL`, timeout, `UNKNOWN`, conflito de target e comando incompatível não produzem movimento.
7. `command_id`, expiração e deduplicação continuam válidos.
8. Os scripts/testes não contêm asserts de dock/undock automático.
9. Android `mockDebug` e `datDebug` continuam compilando.
10. A evidência distingue simulação, MockDeviceKit e hardware Meta real.

## Casos mínimos

### Caso A — SPRAY com robô fora da doca

```text
target plot-03
-> "pulverize aqui"
-> confirmação
-> ACCEPTED
-> Nav2 chega ao plot
-> estado final continua no plot
```

### Caso B — SPRAY com robô dockado

```text
"pulverize aqui"
-> rejeição segura
-> nenhum undock implícito
```

### Caso C — UNDOCK explícito

```text
"saia da doca"
-> confirmação
-> Command UNDOCK
-> action de undock
```

### Caso D — DOCK explícito

```text
"retorne à doca"
-> confirmação
-> Command DOCK
-> aproximação configurada
-> action Dock
```

### Caso E — conflito

```text
câmera = plot-03
voz = plot-04
-> CONFLICT/AMBIGUOUS
-> nenhum Command
```

## Evidência já existente

Há evidência histórica de protocolo, Nav2, alvo visual e movimento, além de testes de expiração/deduplicação. Esses resultados continuam úteis, mas execuções antigas que esperavam dock/undock automático não são prova do lifecycle atual.

A UI Android atual já apresenta target, intenção, confirmação, countdown e último comando aceito. O caminho DAT 0.9.0 pré-hardware também foi integrado e passou com MockDeviceKit.

## Como validar agora

Primeiro:

```bash
make test-quick
```

Android:

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest --no-daemon
./gradlew :app:assembleMockDebug --no-daemon
./gradlew :app:assembleDatDebug --no-daemon
```

Depois execute a simulação e um fluxo manual/automatizado que siga os casos acima. Até os scripts `make demo*` serem reescritos, trate suas mensagens de “demo aprovada” como diagnóstico histórico, não como gate normativo.

## Fora de escopo

- pulverização física;
- navegação criada pelo Maestro;
- pose/IMU/GPS como substituto do target mapeado;
- linguagem natural irrestrita com autoridade de controle;
- Qwen gerando comando;
- afirmar DAT físico sem frame real dos Meta Wearables.

## Resultado esperado

Ao final da Task 7 deve existir uma única evidência coerente entre código, testes e documentação:

```text
ações físicas explícitas + confirmação
-> JSON versionado
-> ROS 2/Nav2
-> nenhum lifecycle escondido
```
