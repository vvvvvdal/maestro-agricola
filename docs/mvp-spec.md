# Spec do MVP: demonstração principal

## Objetivo

Demonstrar, de ponta a ponta, que um operador consegue selecionar um alvo visual, expressar uma intenção por voz, confirmar por áudio e enviar um comando estruturado a um robô simulado.

## Jornada crítica

1. O operador centraliza a placa `PLOT-03`, com texto legível e QR previamente mapeado.
2. O sistema captura um frame sob demanda.
3. O operador diz “pulverizar esta área” ou “pulverizar no plot-03” pela entrada de áudio disponível no sistema mobile.
4. O app resolve `plot-03` pela câmera, pela fala ou pela concordância entre as duas e classifica a intenção como `SPRAY`.
5. O sistema diz: “Pulverizar talhão três. Confirmar?”.
6. O operador responde “confirmar”.
7. O app envia o comando via WebSocket.
8. O bridge ROS 2 publica o destino e o robô simulado inicia o deslocamento.
9. O sistema informa por áudio: “Comando enviado”.

## Critérios de aceite em EARS

1. **Quando** o operador iniciar um comando, **o sistema deve** capturar apenas o frame necessário para resolver o alvo.
2. **Quando** houver um alvo reconhecido e uma intenção válida, **o sistema deve** pedir confirmação por áudio antes de enviar o comando.
3. **Se** o alvo ou a intenção forem ambíguos, **então o sistema deve** pedir repetição e não enviar movimento.
4. **Se** o ID falado divergir do QR, **então o sistema deve** cancelar a interação e não escolher uma fonte silenciosamente.
5. **Se** a confirmação não chegar dentro do timeout, **então o sistema deve** cancelar a operação e informar o cancelamento.
6. **Quando** o bridge ROS 2 aceitar o comando, **o sistema deve** emitir confirmação por áudio e registrar apenas telemetria técnica sem mídia bruta.

## Contrato mínimo de sucesso

- Câmera dos Meta Wearables entrega o frame ao Android pelo DAT. O Mock Device Kit testa a mesma interface antes da gravação, mas não satisfaz sozinho este critério.
- Voz é capturada e transcrita pelas APIs nativas do companion app; nos óculos reais, a rota Bluetooth deve ser validada e o telefone permanece como fallback.
- Classificador operacional local retorna `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` ou `UNKNOWN` com confiança.
- Intenção e alvo viram JSON válido.
- WebSocket entrega o comando ao bridge.
- ROS 2/Gazebo reage ao destino.
- Toda execução exige confirmação.
- Nenhuma foto permanece salva após o processamento.

## Fora de escopo

- Navegação, desvio de obstáculos e segurança funcional do robô.
- Precisão centimétrica ou RTK-GPS.
- Operação real de pulverização.
- Múltiplos robôs simultâneos.
- Linguagem natural aberta para qualquer tarefa. O assistente Qwen integrado à UI permanece restrito ao domínio do Maestro e nunca executa ações.
- Estimativa de waypoint baseada em IMU dos óculos.
- Operação sem smartphone companion.
- Reconhecimento visual livre de objetos ou talhões sem marcador no MVP da semana.
- Geofencing por GPS, RTK ou conversão da posição do operador em destino.
- React Native ou uma camada multiplataforma.

## Plataformas do MVP

- Android/Kotlin: `datDebug` em um aparelho físico que cumpra os requisitos da versão fixada do DAT; `mockDebug` existe somente para desenvolvimento e testes automatizados.
- O app Android consome o `intent_model.json` canônico e o contrato JSON 1.0. O runtime Qwen existe como componente opcional de conversa, mas não substitui o classificador operacional nem participa da geração de `Command`.
- A demo ao vivo usa o build `datDebug` conectado aos Meta Wearables; `mockDebug` deve continuar saudável como contingência e teste da lógica compartilhada.
- A fonte simulada antecipa o desenvolvimento. A captura DAT real é parte obrigatória da definição do MVP demonstrado.

## Casos que não podem quebrar

- Recusa explícita cancela o comando.
- Perda de conexão não pode resultar em execução tardia.
- Repetição da mesma mensagem não pode gerar movimento duplicado.
- Alvo desconhecido nunca vira coordenada padrão.
- Alvo falado e visual divergentes nunca produzem comando.

## Definição de pronto

A jornada roda cinco vezes seguidas com `datDebug`, Android físico e Meta Wearables, incluindo pelo menos uma recusa e uma ambiguidade, com evidência em logs estruturados e sem mídia persistida.
