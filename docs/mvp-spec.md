# Spec do MVP: demonstração principal

## Objetivo

Demonstrar, de ponta a ponta, que um operador consegue selecionar um alvo visual, expressar uma intenção por voz, confirmar por áudio e enviar um comando estruturado a um robô simulado. Na entrega pré-hardware de 22/08/2026, o caminho de câmera usa `datDebug` + Meta Wearables DAT 0.9.0 + MockDeviceKit em Android físico.

O hardware Meta real não faz parte da definição de pronto desta etapa; ele é o próximo gate caso a equipe avance para a fase presencial.

## Jornada crítica

1. O operador centraliza a placa `PLOT-03`, com texto legível e QR previamente mapeado.
2. O DAT entrega ao app uma captura sob demanda; no corte pré-hardware a fonte é o MockDeviceKit explicitamente habilitado.
3. O operador diz “pulverizar esta área” ou “pulverizar no plot-03” pela entrada de áudio disponível no Android.
4. O app resolve `plot-03` pela câmera, pela fala ou pela concordância entre as duas e classifica a intenção como `SPRAY`.
5. O sistema diz: “Pulverizar talhão três. Confirmar?”.
6. O operador responde “confirmar”.
7. O app envia o comando via WebSocket.
8. O bridge valida contrato, validade, confirmação e idempotência e entrega a meta ao ROS 2/Nav2.
9. O robô simulado navega até o alvo e permanece nele.
10. `DOCK` e `UNDOCK` só acontecem por comandos explícitos e confirmados.

## Critérios de aceite em EARS

1. **Quando** o operador iniciar um comando, **o sistema deve** capturar apenas o frame necessário para resolver o alvo.
2. **Quando** houver um alvo reconhecido e uma intenção válida, **o sistema deve** pedir confirmação por áudio antes de enviar o comando.
3. **Se** o alvo ou a intenção forem ambíguos, **então o sistema deve** cancelar/pedir repetição e não enviar movimento.
4. **Se** o ID falado divergir do QR, **então o sistema deve** cancelar a interação e não escolher uma fonte silenciosamente.
5. **Se** a confirmação não chegar dentro do timeout ou o operador disser `CANCEL`, **então o sistema deve** cancelar a operação sem enviar movimento.
6. **Se** o robô estiver dockado e chegar um `SPRAY`, **então o bridge deve** rejeitar o comando sem executar `UNDOCK` implícito.
7. **Quando** `UNDOCK` for confirmado, **o sistema deve** deixar a action nativa terminar completamente antes de considerar o robô disponível.
8. **Quando** `DOCK` for confirmado, **o sistema deve** navegar para a aproximação configurada e então executar a action Dock.
9. **Se** um `command_id` já processado for recebido novamente, **então o bridge deve** retornar a resposta anterior sem repetir o callback ROS.
10. **Se** o comando estiver expirado ou `confirmed=false`, **então o bridge deve** rejeitá-lo.

## Contrato mínimo de sucesso

- `datDebug` usa DAT 0.9.0 com MockDeviceKit explicitamente habilitado no MVP pré-hardware.
- Uma captura repetível produz `target_id` conhecido por ZXing local.
- Voz é capturada/transcrita pelas APIs nativas do Android.
- Classificador operacional local retorna `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` ou `UNKNOWN`.
- Intenção e alvo viram JSON válido, confirmado e de validade curta.
- WebSocket entrega o comando ao bridge.
- ROS 2/Nav2/Gazebo executa apenas comandos compatíveis com o estado do robô.
- Toda execução exige confirmação.
- Nenhuma foto é persistida pelo Maestro por padrão.
- O Qwen é opcional e conversacional; nunca participa da geração de `Command`.

## Fora de escopo

- Navegação, desvio de obstáculos e segurança funcional do robô.
- Precisão centimétrica ou RTK-GPS.
- Operação real de pulverização.
- Múltiplos robôs simultâneos.
- Linguagem natural aberta para qualquer tarefa operacional.
- Estimativa de waypoint baseada em IMU dos óculos.
- Operação sem smartphone companion.
- Reconhecimento visual livre de objetos ou talhões sem marcador no MVP.
- Geofencing por GPS, RTK ou conversão da posição do operador em destino.
- React Native ou camada multiplataforma.
- Alegar captura física dos Meta Wearables antes do gate de hardware real.

## Plataformas do MVP

- Android/Kotlin: `datDebug` em Samsung SM-X510/API 36 no E2E final pré-hardware, com `maestroDatMockDevice=true`.
- `mockDebug`: desenvolvimento, testes automatizados e smoke isolado.
- IA operacional: `intent_model.json` canônico, 64/64 no corpus de avaliação final e 0 aceites perigosos.
- Assistente Qwen: componente opcional; o GGUF não é empacotado no APK e precisa ser provisionado no sandbox privado se for demonstrado.
- Robótica: bridge ROS 2, TurtleBot 4, Nav2 e Gazebo no namespace `/turtlebot1`.

## Casos que não podem quebrar

- Recusa explícita cancela o comando.
- Perda de conexão não pode resultar em execução tardia.
- Repetição da mesma mensagem não pode gerar movimento duplicado.
- Alvo desconhecido nunca vira coordenada padrão.
- Alvo falado e visual divergentes nunca produzem comando.
- `SPRAY` dockado nunca executa `UNDOCK` automaticamente.
- `DOCKED -> UNDOCK` deve funcionar em ciclos consecutivos.

## Definição de pronto — etapa pré-hardware

A etapa está pronta quando:

- `datDebug` + MockDeviceKit no Android físico captura o target de forma repetível;
- `UNDOCK -> SPRAY -> DOCK -> UNDOCK` funciona pelo app e bridge sem HMI manual;
- `SPRAY` termina no plot sem retorno automático;
- `SPRAY` dockado, conflito visual/voz e `CANCEL` não movem o robô;
- contrato rejeita comando sem confirmação ou expirado e deduplica `command_id`;
- `make test` passa com 65 testes portáteis, 36 testes do bridge, 64/64 no corpus e 0 aceites perigosos;
- a documentação chama o resultado de pré-hardware/MockDeviceKit, não de validação física dos Meta Wearables.

Esses critérios foram atendidos em 22/08/2026.