# Tarefa: inspeção visual dos apps e da simulação

## Objetivo

Permitir que a equipe veja o estado atual do MVP sem confundir a interface WebSocket com uma página e sem depender dos logs internos do ROS. A inspeção deve cobrir a tela diagnóstica mobile, o mundo no Gazebo e mapa, sensores e trajetória no RViz2.

## Estado encontrado

- Android já possui uma tela Compose diagnóstica com estado, mensagem, confiança da IA, transcrição, endpoint e ações de olhar, interpretar, falar e reiniciar.
- iOS possui a mesma jornada em SwiftUI.
- Este Linux não possui JDK, Android SDK, `adb` ou emulador configurados; por isso, a tela Android não pode ser compilada localmente ainda.
- iOS exige macOS/Xcode e deve ser aberto no Mac ou instalado no iPhone 13 a partir de um Mac.
- A simulação usa o mundo `warehouse` fornecido pelo `turtlebot4_ignition_bringup`, acrescenta a placa `PLOT-03` e executa SLAM online. Não existe ainda um mundo agrícola próprio nem mapa de ocupação pré-salvo.
- Gazebo 6.18 e RViz2 estão instalados no host. O host descobre os tópicos do contêiner no domínio ROS `42` usando Fast DDS, interoperando com Cyclone DDS no contêiner.

## Critérios de aceite

- [ ] Um comando documentado abre o Gazebo GUI conectado à simulação ativa.
- [ ] Um arquivo RViz versionado abre mapa, robô, laser, planos e TF do namespace `/turtlebot1`.
- [ ] Os comandos visuais verificam dependências e explicam que precisam de uma sessão X11.
- [ ] README e guia de testes explicam o cenário, a origem do mapa e o estado das telas mobile.
- [ ] A leitura de odometria pode tentar novamente após um timeout transitório.
- [ ] Gazebo e RViz são abertos e inspecionados no computador de desenvolvimento.

## Plano

1. Criar configuração RViz mínima apenas com plugins padrão disponíveis no host.
2. Adicionar comandos `make gazebo-gui` e `make rviz` para uma simulação já ativa.
3. Tornar o verificador de odometria tolerante a uma leitura transitória sem resposta.
4. Documentar o teste visual e a diferença entre mundo do Gazebo, mapa SLAM e catálogo de alvos.
5. Executar Gazebo, RViz e a suíte rápida; registrar limitações mobile reais.

## Evidências

A preencher após a validação.
