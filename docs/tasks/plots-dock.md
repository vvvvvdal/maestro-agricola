# Tarefa: três plots e ciclo dock → missão → dock

## Problema observado

- A placa verde está vertical, mas o plano texturizado foi girado somente no eixo Z. Como a normal continuou apontando para cima, o QR ficou horizontal e atravessou a placa.
- Somente `plot-03` existe no cenário e no catálogo de poses.
- O bridge envia uma meta Nav2 sem coordenar a saída e o retorno à doca.

## Decisões e ambiguidades resolvidas

- O namespace canônico permanece `/turtlebot1`, igual ao usado no laboratório e no `pluginbot-turtlebot4` (PB).
- Revisão visual solicitada em 18/08: `plot-03` permanece em `(2, 1)`. `plot-01` vai para `(2.2, -1.8)`, no lado direito da área central, e `plot-02` para `(0.5, 1.8)`, no lado esquerdo. Assim os marcadores ocupam os dois pontos indicados na captura, em vez de parecerem uma única fileira.
- `plot-01` e `plot-02` são girados para olhar para o centro. As metas seguras ficam 0,5 m diante das placas: `(2.2, -2.3, +π/2)`, `(0.5, 2.3, -π/2)` e `(1.5, 1, 0)` para `plot-01`, `plot-02` e `plot-03`, respectivamente. A rota continua curta para a demonstração.
- Cada textura fica sobre a face frontal local da placa. A transformação mantém a imagem vertical e 1 mm para fora da superfície; as placas laterais giram o conjunto inteiro para olhar para o centro.
- A revisão visual mostrou que a face traseira continuava verde. Cada placa passa a repetir o mesmo QR na face oposta, também vertical, não espelhado e 1 mm para fora. Assim a identificação funciona por qualquer lado de aproximação; isso melhora a percepção, mas não altera as coordenadas usadas pelo Nav2.
- O bridge solicita `Undock` automaticamente ao iniciar. Comandos ficam na fila até a saída ser confirmada.
- O bridge executa todas as metas já enfileiradas e solicita `Dock` quando a fila termina. Se a navegação falhar, ainda tenta voltar à doca.
- Falha ou recusa do undock bloqueia navegação; falha do dock fica explícita no log e bloqueia uma nova missão até reinício limpo. O comportamento do PB de continuar após falha de undock não é seguro para este MVP.
- A primeira prova headless expôs uma corrida de inicialização: o action recusou com “Robot already undocked” enquanto o tópico `dock_status` ainda convergia para `is_docked: true`. O bridge deve aguardar uma leitura do tópico, aceitar “estado final já atingido” como operação idempotente e repetir uma recusa transitória de forma limitada; estado desconhecido continua bloqueando navegação.
- A segunda prova mostrou que `/turtlebot1/dock_status` é publicado como `BEST_EFFORT`. Uma assinatura ROS 2 `RELIABLE` aparece no grafo, mas é incompatível e não recebe mensagens; o bridge deve usar o mesmo QoS do Create 3.
- O `warehouse` headless por software avançou apenas cerca de 3 s simulados em mais de 1 minuto real. A prova dos três plots usará um serviço headless separado com `gpus: all` e NVIDIA, sem abrir a GUI; `make demo` e o serviço `simulation` continuam como fallback portátil sem GPU.
- Mesmo com GPU, o limite de 120 s de relógio real cancelou um undock que ainda avançava no Gazebo. Os limites do bridge passam a usar `/clock` (`use_sim_time`), portanto medem tempo simulado: preservam a falha segura sem punir uma máquina que renderiza abaixo do tempo real.
- Na prova seguinte, a odometria chegou a `x=-0,353` e `dock_status=false`, mas o action de undock não devolveu o resultado. O estado estável do tópico passa a ser a confirmação autoritativa: o bridge cancela um goal pendurado e avança quando a condição física desejada já foi atingida; o mesmo vale para `dock_status=true` no retorno.
- A inspeção do pacote instalado revelou que `turtlebot4_ignition.launch.py` não encaminha o argumento `model` ao spawn e que o wrapper oficial sempre acrescenta a GUI. Por isso, o serviço chamado de headless estava executando escondido no Xvfb o modelo Standard completo, inclusive OAK-D, e o relógio simulado avançou menos de 1 s em vários minutos.
- O launch do Maestro passa a iniciar servidor e spawn diretamente, preservando os caminhos oficiais de recursos e o bridge de `/clock`. Todos os modos continuam usando TurtleBot 4 Standard por padrão; agora `TURTLEBOT4_MODEL=lite` também é respeitado se a equipe optar explicitamente pela variante Lite.
- O primeiro servidor direto mostrou outra restrição do pacote: os sensores do TurtleBot 4 carregam `ignition-rendering-ogre` (OGRE 1), que não completa a inicialização no caminho EGL `--headless-rendering`. O modo automático deve usar somente `-s`: não cria GUI; o fallback portátil conserva o Xvfb interno como display compatível para LiDAR/câmera.
- O Xvfb permite inicializar OGRE 1, porém renderiza os sensores por software e continua lento. O serviço `simulation-gpu` usa o X11 do host apenas como contexto gráfico para a NVIDIA, igual ao PB, enquanto `-s` garante que nenhuma janela do Gazebo seja criada. `make demo-route` concede o acesso local restrito e `make simulation-down` o revoga.
- A primeira rota rápida chegou a `(2.15, -2.14)` e oscilou ao tentar alcançar a meta antiga de `plot-01`. A checagem no mapa oficial `warehouse.pgm` confirmou 56 pixels ocupados em um raio de 0,4 m ao redor de `(0.5, -2.3)`; `(2.2, -2.3)` não possui pixel ocupado nesse mesmo raio. A placa e a meta foram deslocadas juntas para a área livre à direita.
- Com a meta em área livre, a odometria avançou normalmente, mas `/turtlebot1/pose` permaneceu perto da origem. O SLAM síncrono compensou o deslocamento em `map → odom`, fazendo o Nav2 acreditar que o robô não se aproximava da meta. Como o `warehouse` e os plots são previamente mapeados, a demonstração deve usar o `warehouse.yaml` oficial com AMCL e pose inicial `(0, 0, 0)`, não construir outro mapa durante a missão.
- Com AMCL, o robô chegou a cerca de 0,46 m de `plot-01`, mas o progress checker padrão abortou três vezes por exigir 0,5 m de deslocamento em 10 s simulados. Para a dinâmica do Create 3, o raio passa a 0,1 m e a janela a 30 s; o limite de 180 s da missão continua sendo a proteção final. O gate do MVP valida um plot completo e retorno à doca; a rota com três plots permanece um teste estendido.
- O gate visual criou corretamente as três placas, mas o Gazebo não encontrou as imagens `model://plot_marker/...`: o caminho de recursos continha os pacotes oficiais, porém não o diretório `models` do Maestro instalado. Esse diretório deve fazer parte de `IGN_GAZEBO_RESOURCE_PATH` e `GZ_SIM_RESOURCE_PATH` para que os QRs apareçam também depois do build do contêiner.
- No mesmo gate, bridge, undock e aceite do Nav2 funcionaram, mas uma consulta `ros2 lifecycle get` demorou mais de 10 s enquanto o Gazebo renderizava. Uma consulta de diagnóstico isolada pode ser repetida até o limite geral de inicialização; ela não deve reprovar a missão nem alterar os limites de segurança do robô.
- O gate chegou ao `plot-03`, mas chamar `Dock` diretamente dali terminou em `Dock Servo Goal Exceeded Runtime`: esse action executa somente a aproximação curta por infravermelho, não a navegação global de volta. O launch oficial posiciona a doca 0,157 m à frente da origem e girada para o robô. A prova manual `Nav2 → (-0.5, 0, 0) → Dock` terminou com `SUCCEEDED` e `is_docked: true`; portanto, o bridge deve inserir essa aproximação interna antes do action de dock.
- “Saia da doca” e “volte para a doca” por voz serão intenções futuras. Elas exigirão confirmação, estado do robô, idempotência e feedback por áudio; não entram no contrato `SPRAY` desta tarefa.

## Critérios de aceite

- [ ] `plot-01`, `plot-02` e `plot-03` possuem QR distintos, legíveis e fixados verticalmente nas duas faces das placas.
- [ ] O catálogo versionado contém os três IDs, com duas placas em lados opostos e metas próximas/seguras.
- [ ] O detector estático reconhece as três placas.
- [ ] O launch usa `/turtlebot1` e cria um único conjunto de três placas.
- [ ] No início, o log confirma `Undock completed` antes de aceitar uma meta Nav2.
- [ ] Ao concluir a última meta enfileirada, o log confirma `Dock completed`.
- [ ] Recusa/falha/timeout de dock, undock ou navegação tem tratamento explícito e teste proporcional.
- [ ] README e guia de testes explicam o ciclo e deixam as futuras intenções de voz fora do escopo atual.

## Plano de execução

1. Corrigir a transformação da textura, criar as três placas no SDF e distribuí-las nos três pontos aprovados.
2. Gerar as texturas `plot-01` e `plot-02`, ampliar o catálogo e testar coerência geométrica.
3. Extrair uma máquina de estados testável para a sequência undock, metas e dock.
4. Integrar os actions `/turtlebot1/undock`, `/turtlebot1/navigate_to_pose` e `/turtlebot1/dock` no bridge.
5. Corrigir o launch headless para não abrir uma GUI oculta e renderizar os sensores com NVIDIA.
6. Trocar o SLAM ao vivo por localização AMCL no mapa oficial do warehouse.
7. Validar testes portáteis; depois abrir Gazebo/RViz com NVIDIA e executar a missão.

## Evidências

A preencher após os testes.
