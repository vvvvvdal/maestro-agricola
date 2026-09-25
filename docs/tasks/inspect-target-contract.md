# JEV-74 - Inspecao local de marcador

## Objetivo

Expor a captura ja isolada pelo `FrameSource` como `INSPECT_TARGET`: uma acao
local sob demanda que identifica um QR/marcador e deixa o talhao pronto para a
proxima fala. Nao e uma setima classe do experimento Jev e nao cria `Command`.

## Contrato

- O operador toca em `Inspecionar marcador`.
- A interface mostra leitura em andamento e bloqueia nova interacao ate o fim.
- A imagem fica apenas na memoria do `FrameSource`; camera, stream e sessao sao
  encerrados no callback, cancelamento ou timeout.
- Sucesso retorna somente `target_id` permitido e origem `VISUAL`.
- Permissao negada, QR ausente/invalido, desconexao ou timeout falham fechados:
  nao ha alvo pronto nem mensagem para Jev, Qwen, WebSocket ou ROS.

## Evidencia esperada

Os testes unitarios cobrem a transicao `INSPECTING -> TARGET_READY` sem
`Command` e a politica que rejeita QR vazio, multiplo ou fora do mapa. No
SM-X510, `mockDebug` exibiu `Marcador plot-03 identificado` apos o toque, sem
fala, Jev, confirmacao, WebSocket ou ROS.

A fronteira DAT ja mantem cenarios de permissao negada, timeout e desconexao;
essas falhas fechadas devem ser repetidas no hardware DAT real antes de declarar
a captura fisica aprovada.
