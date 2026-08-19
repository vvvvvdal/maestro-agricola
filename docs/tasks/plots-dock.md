# Tarefa: três plots e ciclo de docking

> **Status atual:** o ciclo automático `undock → missão → retorno → dock` descrito
> originalmente nesta tarefa foi **substituído** pela arquitetura de docking
> explícito.
>
> A partir da refatoração da Task 1 do roadmap de docking explícito, comandos
> normais de navegação (`SPRAY`) não controlam mais o lifecycle da doca.

## Decisão posterior — docking explícito

O comportamento original desta tarefa fazia o bridge:

```text
Undock automático
→ executar metas Nav2
→ navegar para dock approach
→ Dock automático
```

Esse acoplamento foi removido.

O comportamento atual de uma missão normal passa a ser:

```text
SPRAY
→ Nav2 para o target solicitado
→ conclusão
→ READY
→ robô permanece no destino
```

Consequências:

- uma missão `SPRAY` não chama `Undock`;
- uma missão `SPRAY` não navega automaticamente de volta para a doca;
- uma missão `SPRAY` não chama `Dock`;
- a conclusão da fila deixa o lifecycle em `READY`;
- um segundo comando de navegação pode ser executado depois do primeiro sem um ciclo intermediário de docking;
- se o `DockStatus` conhecido informar que o robô está dockado, uma navegação normal é rejeitada em vez de causar undock implícito;
- a infraestrutura ROS já existente para `Dock` e `Undock` permanece preservada;
- `DOCK` e `UNDOCK` serão adicionados posteriormente como comandos explícitos, com confirmação e tratamento próprio.

A implementação histórica abaixo continua documentada porque contém decisões
válidas sobre TurtleBot 4, Gazebo, Nav2, pose de aproximação da doca, QoS,
timeouts e comportamento físico das actions.

Ela não deve mais ser interpretada como especificação do lifecycle atual de
uma missão `SPRAY`.

---

## Problema observado originalmente

- A placa verde está vertical, mas o plano texturizado foi girado somente no eixo Z. Como a normal continuou apontando para cima, o QR ficou horizontal e atravessou a placa.
- Somente `plot-03` existe no cenário e no catálogo de poses.
- O bridge enviava uma meta Nav2 sem coordenar a saída e o retorno à doca.

## Decisões e ambiguidades resolvidas

- O namespace canônico permanece `/turtlebot1`, igual ao usado no laboratório e no `pluginbot-turtlebot4` (PB).
- Revisão visual solicitada em 18/08: `plot-03` permanece em `(2, 1)`. `plot-01` vai para `(2.2, -1.8)`, no lado direito da área central, e `plot-02` para `(0.5, 1.8)`, no lado esquerdo. Assim os marcadores ocupam os dois pontos indicados na captura, em vez de parecerem uma única fileira.
- `plot-01` e `plot-02` são girados para olhar para o centro. As metas seguras ficam 0,5 m diante das placas: `(2.2, -2.3, +π/2)`, `(0.5, 2.3, -π/2)` e `(1.5, 1, 0)` para `plot-01`, `plot-02` e `plot-03`, respectivamente. A rota continua curta para a demonstração.
- Cada textura fica sobre a face frontal local da placa. A transformação mantém a imagem vertical e 1 mm para fora da superfície; as placas laterais giram o conjunto inteiro para olhar para o centro.
- A revisão visual mostrou que a face traseira continuava verde. Cada placa passa a repetir o mesmo QR na face oposta, também vertical, não espelhado e 1 mm para fora. Assim a identificação funciona por qualquer lado de aproximação; isso melhora a percepção, mas não altera as coordenadas usadas pelo Nav2.

### Decisões históricas do lifecycle automático

As decisões abaixo foram necessárias para implementar e testar o primeiro ciclo
automático. A infraestrutura técnica continua útil, mas o disparo automático foi
substituído pela arquitetura descrita no início deste documento.

- O bridge solicitava `Undock` automaticamente ao iniciar. Comandos ficavam na fila até a saída ser confirmada.
- O bridge executava todas as metas já enfileiradas e solicitava `Dock` quando a fila terminava. Se a navegação falhasse, ainda tentava voltar à doca.
- Falha ou recusa do undock bloqueava navegação; falha do dock ficava explícita no log e bloqueava uma nova missão até reinício limpo. O comportamento do PB de continuar após falha de undock não era seguro para este MVP.
- A primeira prova headless expôs uma corrida de inicialização: o action recusou com “Robot already undocked” enquanto o tópico `dock_status` ainda convergia para `is_docked: true`. O bridge deveria aguardar uma leitura do tópico, aceitar “estado final já atingido” como operação idempotente e repetir uma recusa transitória de forma limitada; estado desconhecido continuava bloqueando navegação.
- A segunda prova mostrou que `/turtlebot1/dock_status` é publicado como `BEST_EFFORT`. Uma assinatura ROS 2 `RELIABLE` aparece no grafo, mas é incompatível e não recebe mensagens; o bridge deve usar o mesmo QoS do Create 3.
- O `warehouse` headless por software avançou apenas cerca de 3 s simulados em mais de 1 minuto real. A prova dos três plots usaria um serviço headless separado com `gpus: all` e NVIDIA, sem abrir a GUI; `make demo` e o serviço `simulation` continuavam como fallback portátil sem GPU.
- Mesmo com GPU, o limite de 120 s de relógio real cancelou um undock que ainda avançava no Gazebo. Os limites do bridge passaram a usar `/clock` (`use_sim_time`), portanto medem tempo simulado: preservam a falha segura sem punir uma máquina que renderiza abaixo do tempo real.
- Na prova seguinte, a odometria chegou a `x=-0,353` e `dock_status=false`, mas o action de undock não devolveu o resultado. O estado estável do tópico passou a ser a confirmação autoritativa: o bridge cancela um goal pendurado e avança quando a condição física desejada já foi atingida; o mesmo vale para `dock_status=true` no retorno.
- A inspeção do pacote instalado revelou que `turtlebot4_ignition.launch.py` não encaminha o argumento `model` ao spawn e que o wrapper oficial sempre acrescenta a GUI. Por isso, o serviço chamado de headless estava executando escondido no Xvfb o modelo Standard completo, inclusive OAK-D, e o relógio simulado avançou menos de 1 s em vários minutos.
- O launch do Maestro passou a iniciar servidor e spawn diretamente, preservando os caminhos oficiais de recursos e o bridge de `/clock`. Todos os modos continuam usando TurtleBot 4 Standard por padrão; `TURTLEBOT4_MODEL=lite` também é respeitado se a equipe optar explicitamente pela variante Lite.
- O primeiro servidor direto mostrou outra restrição do pacote: os sensores do TurtleBot 4 carregam `ignition-rendering-ogre` (OGRE 1), que não completa a inicialização no caminho EGL `--headless-rendering`. O modo automático deve usar somente `-s`: não cria GUI; o fallback portátil conserva o Xvfb interno como display compatível para LiDAR/câmera.
- O Xvfb permite inicializar OGRE 1, porém renderiza os sensores por software e continua lento. O serviço `simulation-gpu` usa o X11 do host apenas como contexto gráfico para a NVIDIA, igual ao PB, enquanto `-s` garante que nenhuma janela do Gazebo seja criada. `make demo-route` concede o acesso local restrito e `make simulation-down` o revoga.
- A primeira rota rápida chegou a `(2.15, -2.14)` e oscilou ao tentar alcançar a meta antiga de `plot-01`. A checagem no mapa oficial `warehouse.pgm` confirmou 56 pixels ocupados em um raio de 0,4 m ao redor de `(0.5, -2.3)`; `(2.2, -2.3)` não possui pixel ocupado nesse mesmo raio. A placa e a meta foram deslocadas juntas para a área livre à direita.
- Com a meta em área livre, a odometria avançou normalmente, mas `/turtlebot1/pose` permaneceu perto da origem. O SLAM síncrono compensou o deslocamento em `map → odom`, fazendo o Nav2 acreditar que o robô não se aproximava da meta. Como o `warehouse` e os plots são previamente mapeados, a demonstração deve usar o `warehouse.yaml` oficial com AMCL e pose inicial `(0, 0, 0)`, não construir outro mapa durante a missão.
- Com AMCL, o robô chegou a cerca de 0,46 m de `plot-01`, mas o progress checker padrão abortou três vezes por exigir 0,5 m de deslocamento em 10 s simulados. Para a dinâmica do Create 3, o raio passa a 0,1 m e a janela a 30 s; o limite de 180 s da missão continua sendo a proteção final. O gate do MVP validava um plot completo e retorno à doca; a rota com três plots permanecia um teste estendido.
- O gate visual criou corretamente as três placas, mas o Gazebo não encontrou as imagens `model://plot_marker/...`: o caminho de recursos continha os pacotes oficiais, porém não o diretório `models` do Maestro instalado. Esse diretório deve fazer parte de `IGN_GAZEBO_RESOURCE_PATH` e `GZ_SIM_RESOURCE_PATH` para que os QRs apareçam também depois do build do contêiner.
- No mesmo gate, bridge, undock e aceite do Nav2 funcionaram, mas uma consulta `ros2 lifecycle get` demorou mais de 10 s enquanto o Gazebo renderizava. Uma consulta de diagnóstico isolada pode ser repetida até o limite geral de inicialização; ela não deve reprovar a missão nem alterar os limites de segurança do robô.
- O gate chegou ao `plot-03`, mas chamar `Dock` diretamente dali terminou em `Dock Servo Goal Exceeded Runtime`: esse action executa somente a aproximação curta por infravermelho, não a navegação global de volta. O launch oficial posiciona a doca 0,157 m à frente da origem e girada para o robô. A prova manual `Nav2 → (-0.5, 0, 0) → Dock` terminou com `SUCCEEDED` e `is_docked: true`; portanto, um futuro comando explícito `DOCK` deve reutilizar essa aproximação interna antes do action de dock.
- Na prova integrada, o robô estabilizou a 0,245 m da meta e entrou em recuperação porque a tolerância padrão era 0,20 m. Alterar dinamicamente para 0,30 m concluiu a meta imediatamente. Essa tolerância mantém a parada entre 0,20 e 0,80 m da placa nominalmente posicionada a 0,50 m; é suficiente para o MVP e evita mover novamente os plots já aprovados visualmente.
- “Saia da doca” e “volte para a doca” por voz foram identificadas como futuras intenções. Elas exigem confirmação, estado do robô, idempotência e feedback por áudio. A implementação será feita em tarefas separadas e não faz parte da refatoração da Task 1.

## Critérios de aceite da implementação original

Os itens abaixo registram o que foi comprovado durante a implementação
histórica do ciclo automático. Eles não representam mais a regra de lifecycle
para uma missão `SPRAY`.

- [x] `plot-01`, `plot-02` e `plot-03` possuem QR distintos, legíveis e fixados verticalmente nas duas faces das placas.
- [x] O catálogo versionado contém os três IDs, com duas placas em lados opostos e metas próximas/seguras.
- [x] O detector estático reconhece as três placas.
- [x] O launch usa `/turtlebot1` e cria um único conjunto de três placas.
- [x] O ciclo automático original confirmou `Undock completed` antes de aceitar uma meta Nav2.
- [x] O ciclo automático original confirmou `Dock completed` ao concluir a última meta.
- [x] Recusa/falha/timeout de dock, undock ou navegação recebeu tratamento explícito e teste proporcional.
- [x] README e guia de testes documentaram o ciclo original.

## Critérios de aceite da refatoração para docking explícito — Task 1

- [x] `MissionCycle` inicia em `READY`.
- [x] Uma navegação normal começa sem `Undock` implícito.
- [x] Conclusão de Nav2 retorna para `READY`, independentemente de haver outra meta na fila.
- [x] Uma segunda navegação pode ser executada depois da primeira sem ciclo intermediário de docking.
- [x] `command_queued()` não altera silenciosamente estados de dock/undock.
- [x] Um lifecycle em `DOCKED` não é convertido automaticamente para `NEEDS_UNDOCK`.
- [x] O bridge rejeita uma nova navegação quando o `DockStatus` conhecido informa `is_docked=true`.
- [x] As utilities/actions existentes de dock e undock permanecem disponíveis para reutilização posterior.
- [x] Testes unitários focados da máquina de estados passam.
- [x] A suíte Python do pacote `maestro_robot_bridge` passa.
- [ ] Gate visual: `SPRAY plot-02` conclui a navegação e o robô permanece no destino.
- [ ] Gate visual: após a conclusão de `SPRAY`, não aparece `Requesting Nav2 return to dock approach`.
- [ ] Gate visual: após a conclusão de `SPRAY`, nenhuma action `Dock` ou `Undock` é iniciada implicitamente.

## Plano de execução original

1. Corrigir a transformação da textura, criar as três placas no SDF e distribuí-las nos três pontos aprovados.
2. Gerar as texturas `plot-01` e `plot-02`, ampliar o catálogo e testar coerência geométrica.
3. Extrair uma máquina de estados testável para a sequência undock, metas e dock.
4. Integrar os actions `/turtlebot1/undock`, `/turtlebot1/navigate_to_pose` e `/turtlebot1/dock` no bridge.
5. Corrigir o launch headless para não abrir uma GUI oculta e renderizar os sensores com NVIDIA.
6. Trocar o SLAM ao vivo por localização AMCL no mapa oficial do warehouse.
7. Validar testes portáteis; depois abrir Gazebo/RViz com NVIDIA e executar a missão.

## Plano da refatoração de docking explícito

1. Remover transições automáticas de dock/undock do fluxo normal de navegação.
2. Preservar a infraestrutura ROS já validada.
3. Impedir que uma navegação provoque undock implicitamente quando o robô estiver dockado.
4. Validar a state machine e todo o pacote Python do bridge.
5. Validar no Gazebo que uma missão `SPRAY` termina no target e permanece lá.
6. Em tarefas posteriores, adicionar `UNDOCK` e `DOCK` como comandos explícitos.
7. Somente depois integrar as novas intents ao contrato, Android e classificador local.

## Evidências da implementação original

- `make test-quick`: 34 testes gerais + 14 testes do bridge aprovados; artefato do classificador atualizado e Compose válido.
- `make vision-smoke`: `plot-01`, `plot-02` e `plot-03` detectados com confiança `1.0`.
- O teste geométrico confirma dois planos verticais por placa, fora das faces opostas, com textura idêntica e orientação não espelhada.
- Gate visual NVIDIA em 18/08/2026: `Undock completed` ocorreu antes do aceite do `plot-03`; a meta foi concluída; o bridge registrou `Nav2 completed return-to-dock approach`; o action curto foi aceito e terminou com `Dock completed: robot is docked (dock status confirmed docked)`.
- O gate original do MVP cobria um plot completo e retorno automático à doca. Esse critério foi posteriormente substituído.

## Evidências da Task 1 — remoção do lifecycle automático

Commit de implementação:

```text
f4456ed refactor(bridge): remove automatic dock mission lifecycle
```

Teste focado da máquina de estados:

```bash
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
python3 -m pytest \
robot_ws/src/maestro_robot_bridge/test/test_mission_cycle.py -q
```

Resultado:

```text
15 passed in 0.09s
```

Teste de todo o pacote Python do bridge:

```bash
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
python3 -m pytest \
robot_ws/src/maestro_robot_bridge/test -q
```

Resultado:

```text
19 passed in 0.10s
```

O gate visual no Gazebo ainda deve ser executado antes de considerar a Task 1
completamente validada em simulação.