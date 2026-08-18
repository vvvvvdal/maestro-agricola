# Tarefa: três plots e ciclo dock → missão → dock

## Problema observado

- A placa verde está vertical, mas o plano texturizado foi girado somente no eixo Z. Como a normal continuou apontando para cima, o QR ficou horizontal e atravessou a placa.
- Somente `plot-03` existe no cenário e no catálogo de poses.
- O bridge envia uma meta Nav2 sem coordenar a saída e o retorno à doca.

## Decisões e ambiguidades resolvidas

- O namespace canônico permanece `/turtlebot1`, igual ao usado no laboratório e no `pluginbot-turtlebot4` (PB).
- As três placas ficam alinhadas e próximas: marcadores em `(2, -1)`, `(2, 0)` e `(2, 1)`; metas em `(1.5, -1)`, `(1.5, 0)` e `(1.5, 1)`. As metas consecutivas ficam a 1 m entre si.
- Cada textura fica sobre a face da placa voltada para `-X`. A transformação deve mapear os eixos horizontal/vertical da imagem para os eixos Y/Z do mundo, sem atravessar a placa.
- O bridge solicita `Undock` automaticamente ao iniciar. Comandos ficam na fila até a saída ser confirmada.
- O bridge executa todas as metas já enfileiradas e solicita `Dock` quando a fila termina. Se a navegação falhar, ainda tenta voltar à doca.
- Falha ou recusa do undock bloqueia navegação; falha do dock fica explícita no log e bloqueia uma nova missão até reinício limpo. O comportamento do PB de continuar após falha de undock não é seguro para este MVP.
- “Saia da doca” e “volte para a doca” por voz serão intenções futuras. Elas exigirão confirmação, estado do robô, idempotência e feedback por áudio; não entram no contrato `SPRAY` desta tarefa.

## Critérios de aceite

- [ ] `plot-01`, `plot-02` e `plot-03` possuem QR distintos, legíveis e fixados verticalmente na face das placas.
- [ ] O catálogo versionado contém os três IDs e mantém as metas próximas.
- [ ] O detector estático reconhece as três placas.
- [ ] O launch usa `/turtlebot1` e cria um único conjunto de três placas.
- [ ] No início, o log confirma `Undock completed` antes de aceitar uma meta Nav2.
- [ ] Ao concluir a última meta enfileirada, o log confirma `Dock completed`.
- [ ] Recusa/falha/timeout de dock, undock ou navegação tem tratamento explícito e teste proporcional.
- [ ] README e guia de testes explicam o ciclo e deixam as futuras intenções de voz fora do escopo atual.

## Plano de execução

1. Corrigir a transformação da textura e criar as três placas no SDF.
2. Gerar as texturas `plot-01` e `plot-02`, ampliar o catálogo e testar coerência geométrica.
3. Extrair uma máquina de estados testável para a sequência undock, metas e dock.
4. Integrar os actions `/turtlebot1/undock`, `/turtlebot1/navigate_to_pose` e `/turtlebot1/dock` no bridge.
5. Validar testes portáteis; depois abrir Gazebo/RViz com NVIDIA e executar a missão.

## Evidências

A preencher após os testes.
