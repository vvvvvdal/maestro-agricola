# Task: Demo de reserva offline Jev

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Objetivo

Criar uma reserva local e reproduzivel dos tres estados visuais que podem ser
usados se a rede estiver indisponivel na apresentacao: baseline local, fixture
Jev `SPRAY` e fixture Jev `UNKNOWN`.

## Decisao e limite

Foram usadas tres capturas de tela, em vez de video. Elas tornam a contingencia
mais estavel e verificavel, mas nao sao inferencia Jev remota, reconhecimento
de fala ou demonstracao de controle do robo. O seletor do `mockDebug` injeta
somente estados visuais locais; nenhum alvo, confirmacao ou `Command` foi
produzido.

Durante toda a captura, o Wi-Fi esteve desligado. ADB permaneceu conectado por
USB. Apos as capturas, o Wi-Fi foi religado antes do encerramento.

## Evidencias

Ambiente: Samsung SM-X510, `mockDebug`, pacote
`br.org.agroturtles.maestro.mock`, paisagem `2304 x 1440`.

| Arquivo | Estado apresentado | Limite visivel |
| --- | --- | --- |
| [`jev52-offline-baseline-local.png`](../study-groups/jev-rl-2026-10-01/results/offline-demo/jev52-offline-baseline-local.png) | `INTENCAO: -; aguardando fala` | Robô continua `Aguardando comando`. |
| [`jev52-offline-jev-spray.png`](../study-groups/jev-rl-2026-10-01/results/offline-demo/jev52-offline-jev-spray.png) | `Pulverizar`; `SPRAY - 87% - Jev` | Sem alvo, confirmacao ou comando aceito. |
| [`jev52-offline-jev-unknown.png`](../study-groups/jev-rl-2026-10-01/results/offline-demo/jev52-offline-jev-unknown.png) | `Nao reconhecida`; `UNKNOWN - 85% - Jev - nenhum comando enviado` | Recusa explicita; robô continua aguardando. |

O [`manifest.json`](../study-groups/jev-rl-2026-10-01/results/offline-demo/manifest.json)
guarda hashes SHA-256, ambiente sanitizado e verificacao booleana do Wi-Fi. Ele
nao contem transcricao, credencial, endpoint de rede ou identificador externo.

## Verificacao

- `tools/agents/preflight.sh`: passou em `test/jev`.
- `python3 mobile/android/tools/preflight.py --require-device`: passou para o
  SM-X510 via ADB USB.
- Antes da primeira captura, `adb shell settings get global wifi_on` retornou
  `0`; apos a ultima, retornou `1`.
- As tres PNGs foram inspecionadas em `2304 x 1440`: wordmark inteiro,
  cartoes legiveis e sem sobreposicao em paisagem.

## Uso na apresentacao

Usar como reserva somente se a demo ao vivo nao puder ocorrer. Toda captura
deve manter a legenda: `fixture mock local - nao executa o robo`. A evidencia
experimental remota continua sendo JEV-41R; a decisao JEV-43 continua `HOLD`.
