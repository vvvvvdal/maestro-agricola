# Tarefa: inspeção visual dos apps e da simulação

## Objetivo

Permitir que a equipe veja o estado atual do MVP sem confundir a interface WebSocket com uma página e sem depender dos logs internos do ROS. A inspeção deve cobrir a tela diagnóstica mobile, o mundo no Gazebo e mapa, sensores e trajetória no RViz2.

## Estado encontrado

- Android já possui uma tela Compose diagnóstica com estado, mensagem, confiança da IA, transcrição, endpoint e ações de olhar, interpretar, falar e reiniciar.
- Este Linux não possui JDK, Android SDK, `adb` ou emulador configurados; por isso, a tela Android não pode ser compilada localmente ainda.
- A simulação usa o mundo `warehouse` fornecido pelo `turtlebot4_ignition_bringup`, acrescenta a placa `PLOT-03` e executa SLAM online. Não existe ainda um mundo agrícola próprio nem mapa de ocupação pré-salvo.
- O fluxo comprovado do `pluginbot-turtlebot4` executa Gazebo e RViz dentro do mesmo contêiner, compartilha o X11 e usa `--gpus all`.
- A GTX 1650 e o runtime NVIDIA estão disponíveis. O primeiro experimento do Maestro separava servidor headless, GUI no host e renderização por software; essa combinação foi descartada após congelamento.

## Critérios de aceite

- [x] Um comando documentado abre uma simulação visual limpa no Gazebo.
- [x] Um arquivo RViz versionado abre mapa, robô, laser, planos e TF do namespace `/turtlebot1`.
- [x] Os comandos visuais verificam NVIDIA, runtime Docker e sessão X11.
- [x] README e guia de testes explicam o cenário, a origem do mapa e o estado das telas mobile.
- [x] A leitura de odometria pode tentar novamente após um timeout transitório.
- [x] Gazebo e RViz são abertos e inspecionados no computador de desenvolvimento.

## Plano

1. Criar configuração RViz mínima apenas com plugins disponíveis na imagem do simulador.
2. Adicionar comandos `make gazebo`, `make demo-visual` e `make rviz` no mesmo contêiner NVIDIA.
3. Tornar o verificador de odometria tolerante a uma leitura transitória sem resposta.
4. Documentar o teste visual e a diferença entre mundo do Gazebo, mapa SLAM e catálogo de alvos.
5. Executar Gazebo, RViz e a suíte rápida; registrar limitações mobile reais.

## Evidências

- Referência inspecionada: `pluginbot-turtlebot4` usa `docker run --gpus all`, `DISPLAY`, `/tmp/.X11-unix` e abre Gazebo/RViz dentro do contêiner.
- Antes da correção, o serviço headless em software chegou a aproximadamente 212% de CPU, 1,9 GiB de RAM e não recebia dispositivos NVIDIA.
- `simulation-gui` recebeu `DeviceRequests: gpu`, e `nvidia-smi` listou `ign gazebo server`, `ign gazebo gui` e `rviz2` usando a GTX 1650.
- Gazebo e RViz abriram lado a lado; RViz reportou OpenGL 4.6 e carregou o mapa SLAM sem erros de mesh.
- `make demo-visual` terminou com `Nav2 ativo`, `Nav2 aceitou o comando`, odometria `x=-0.353` e `DEMO VISUAL APROVADA`.
- `make test-quick` passou com 26 testes portáteis, 4 testes do bridge e Compose válido.
