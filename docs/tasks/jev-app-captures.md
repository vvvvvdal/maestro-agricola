# Task: Capturas do app Jev

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Objetivo

Registrar tres estados visuais do `mockDebug` para a apresentacao: baseline
local, fixture Jev `SPRAY` e fixture Jev `UNKNOWN`. As imagens explicam como o
app apresenta classe, probabilidade e recusa sem transformar o cartao em um
controle operacional.

## Ambiente e metodo

- Dispositivo: Samsung SM-X510 via ADB, em paisagem (`2304 x 1440`).
- APK: `mockDebug`, pacote `br.org.agroturtles.maestro.mock`.
- A selecao ocorreu em `Cenario Jev - somente mock`; ela altera somente o
  cartao `INTENCAO` e nao usa rede, Jev remoto, microfone, bridge, ROS ou
  `Command`.
- Todas as capturas permanecem no estado inicial seguro: nenhum alvo, nenhuma
  confirmacao e `ROBO - ULTIMO COMANDO ACEITO: Aguardando comando`.

Neste tablet, `adb exec-out screencap` gerou uma imagem preta. As evidencias
foram, por isso, obtidas com `adb shell screencap` e depois copiadas por ADB.
Isso nao altera o estado do app nem o conteudo registrado.

## Evidencias

| Arquivo | Cenario e cartao | Estado e limite |
| --- | --- | --- |
| [`jev50-baseline-local.png`](../study-groups/jev-rl-2026-10-01/results/app-captures/jev50-baseline-local.png) | `Baseline local` inicial; `INTENCAO: -; aguardando fala` | Espera segura pela entrada; nao e uma predicao Jev nem comando. |
| [`jev50-jev-spray.png`](../study-groups/jev-rl-2026-10-01/results/app-captures/jev50-jev-spray.png) | `Pulverizar`; `SPRAY - 87% - Jev` | Fixture local de apresentacao; ainda sem alvo, confirmacao ou comando. |
| [`jev50-jev-unknown.png`](../study-groups/jev-rl-2026-10-01/results/app-captures/jev50-jev-unknown.png) | `Nao reconhecida`; `UNKNOWN - 85% - Jev - nenhum comando enviado` | Recusa fica visivel por texto; nenhum comando foi enviado. |

SHA-256: `43c07f2e...98ae4d4` (baseline),
`a6c476e1...2e61687b` (SPRAY) e `c2e3489e...3f17520` (UNKNOWN).

## Verificacao

- `python3 tools/preflight.py --require-device`: passou para o SM-X510.
- `:app:testMockDebugUnitTest` produziu os relatorios sem falhas e
  `:app:assembleMockDebug` deixou o APK de captura disponivel.
- Inspecao visual das tres PNGs: wordmark inteiro, cartoes legiveis, sem corte
  ou sobreposicao em paisagem.

Estas imagens sao evidencia de UI local. A comparacao experimental Jev versus
baseline continua limitada a JEV-41R e a decisao JEV-43 permanece `HOLD`.

## Uso na apresentacao

Quando uma captura Jev for usada em slide, incluir a etiqueta curta `fixture
mock local - nao executa o robo`. O aviso do seletor fica abaixo da dobra nas
PNGs do cartao; a legenda impede que `SPRAY - 87% - Jev` seja lido como uma
chamada remota ou decisao operacional.
