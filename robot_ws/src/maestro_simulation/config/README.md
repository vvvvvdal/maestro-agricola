# Configuração Nav2

`nav2.yaml` parte da configuração já utilizada no projeto `pluginbot-turtlebot4`, removendo do novo MVP dependências de Ollama, YOLO e controle direto por `cmd_vel`.

Antes da demonstração, valide namespace, frames, tópico do LiDAR e tolerância do goal no container final.

## Mundo, mapa e alvos

- **Mundo 3D:** `warehouse.sdf`, fornecido pelo `turtlebot4_ignition_bringup`. O launch do Maestro adiciona o modelo `plot_marker` em `(2.0, 1.0)`.
- **Mapa de navegação:** produzido em tempo real pelo `slam_toolbox` e publicado em `/turtlebot1/map`. O MVP ainda não versiona um par `.pgm`/`.yaml` de mapa salvo.
- **Catálogo de alvos:** `maestro_robot_bridge/config/targets.json`; converte `plot-03` na meta `(1.5, 1.0, 0.0)`. Ele não substitui o mapa de ocupação.

`maestro.rviz` configura a inspeção do mapa SLAM, modelo do TurtleBot 4, LiDAR, costmap e planos. Na raiz do repositório, execute `make gazebo`, depois `make demo-visual` e `make rviz` em terminais separados. Gazebo e RViz rodam no mesmo contêiner com `gpus: all`, seguindo o fluxo já comprovado no `pluginbot-turtlebot4`.
