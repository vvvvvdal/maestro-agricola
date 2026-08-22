# Entrega final - texto-base atualizado para o formulário

Data de preparação: 22 de agosto de 2026.

Fonte de verdade desta etapa: **pré-hardware com DAT 0.9.0 + MockDeviceKit em Android físico**. Não afirmar que a captura veio dos Meta Wearables reais. O **Qwen2.5-1.5B está funcional no tablet via llama.cpp**, mas não possui autoridade operacional sobre o robô.

## Resumo em uma frase

Interface hands-free que permite a operadores agrícolas comandar máquinas autônomas por visão e voz, com confirmação antes da execução.

## A1 - O problema

Operadores de máquinas e robôs agrícolas trabalham sob sol, poeira, ruído e muitas vezes com luvas e as mãos ocupadas. Ao precisar indicar uma nova área ou iniciar uma tarefa, ainda podem ter que parar o trabalho para usar celular, tablet ou notebook, interrompendo o fluxo da operação.

## A2 - Usuário-alvo

Persona de referência (hipótese de design): operador agrícola de 35 anos, em turno de campo, com mãos ocupadas, luvas, poeira e ruído. Usa o Maestro sempre que precisa indicar uma área ou iniciar uma tarefa sem parar para operar celular ou tablet.

## A3 - Walkthrough de interação

1. O operador centraliza a placa PLOT-03. A câmera é acionada; no estágio pré-hardware, o app Android/Kotlin solicita a captura ao DAT 0.9.0 com MockDeviceKit. O ZXing lê o QR e identifica o alvo como plot-03.
2. O operador diz “pulverizar esta área”. A voz é capturada pelo Android e o SpeechRecognizer gera a transcrição. A IA operacional local, o LocalIntentClassifier, classifica a intenção como SPRAY; o Qwen não participa de decisões que movimentam o robô.
3. O TargetResolver cruza a informação visual com qualquer ID citado na fala. Como não há conflito, resolve o alvo como plot-03. Se houvesse divergência, o fluxo seria bloqueado antes de qualquer comando.
4. O sistema usa Android TTS para responder por áudio: “Pulverizar talhão três, confirmar?”. Nenhum movimento é autorizado nesse momento.
5. O operador responde “confirmar”. O SpeechRecognizer transcreve a resposta e o classificador local reconhece CONFIRM, liberando somente a operação que estava pendente.
6. O app cria um comando JSON versionado com command_id único, tempo de expiração, alvo plot-03 e confirmed=true, e o envia por WebSocket pela rede local.
7. O bridge em ROS 2 valida schema, confirmação, expiração, duplicidade e estado do robô. Depois converte plot-03 em uma pose previamente permitida e envia a meta ao Nav2.
8. O TurtleBot 4 no Gazebo navega até plot-03 e permanece no alvo. O TTS informa ao operador que o comando foi enviado; retorno à doca só ocorre com um comando DOCK explícito e confirmado.

## A4 - Walkthrough de exceção

1) O sistema percebe conflito entre o alvo visual e o falado. Por exemplo: câmera lê plot-03 e a voz indica plot-01. 2) O TargetResolver marca a interação como ambígua e bloqueia o envio ao robô. 3) O Android TTS avisa por áudio que os alvos não conferem e pede nova tentativa. Nenhum comando é executado.

## A5 - Decisões técnicas e trade-offs

### A5[1]
- Decisão: Fizemos captura sob demanda via DAT em vez de stream contínuo.
- Por que: Reduz câmera, Bluetooth, CPU e bateria. Um frame basta para ler o QR e resolver o alvo, respeitando o orçamento de energia dos AI glasses.
- Custo: Custa menos contexto visual e pode falhar com enquadramento ruim. Mitigamos pedindo nova captura e nunca criando um alvo padrão quando o QR não é resolvido.

### A5[2]
- Decisão: Fizemos IA operacional restrita em vez de deixar o Qwen comandar o robô.
- Por que: O classificador local entrega decisão previsível e sem internet: fez 64/64 e zero aceites perigosos. O Qwen fica restrito ao assistente conversacional.
- Custo: Os comandos aceitam menos linguagem aberta. Em troca, o Qwen pode conversar sobre o Maestro sem ter acesso a Command, WebSocket ou ROS.

### A5[3]
- Decisão: Fizemos alvo visual mapeado por QR em vez de inferir coordenadas por pose/IMU.
- Por que: O DAT público não expõe pose/IMU suficiente para gerar um waypoint seguro. O QR entrega um ID determinístico que o ROS mapeia para uma pose conhecida.
- Custo: Custa depender de marcadores no ambiente e perde naturalidade. Mitigamos com ID falado como fallback e rejeição segura quando câmera e voz divergem.

### A5[4]
- Decisão: Fizemos Qwen local no tablet em vez de usar um LLM na nuvem.
- Por que: O Qwen2.5-1.5B roda via llama.cpp no Android, permitindo perguntas sobre o Maestro localmente e sem depender de conexão com um serviço de IA.
- Custo: Custa cerca de 1,1 GB e maior latência no primeiro uso. Mitigamos tirando o Qwen do caminho crítico e usando-o apenas para conversa.

### A5[5]
- Decisão: Fizemos DOCK e UNDOCK explícitos em vez de ciclo automático do robô.
- Por que: Ganhamos previsibilidade e segurança: cada movimento físico exige intenção e confirmação, evitando retorno ou saída da doca sem pedido do operador.
- Custo: Custa mais interações por voz e alguns segundos no fluxo. Aceitamos essa fricção para manter ações físicas visíveis, auditáveis e sob controle humano.

## A6 - Âncora de originalidade

- Concorrente 1: Meta AI nos Ray-Ban Meta.
- Diferencial: A Meta AI informa e descreve o ambiente; o Maestro transforma visão e voz em comandos agrícolas estruturados, confirmados e enviados ao robô.
- Concorrente 2: John Deere Operations Center Mobile.
- Diferencial: O Operations Center opera e monitora máquinas por celular/tablet; o Maestro propõe comando hands-free por visão e voz, com confirmação antes da ação.

## A7 - Mapeamento dos 5 checkpoints

- IA: IA local em duas camadas: classificador restrito para comandos, com 64/64 casos e 0 aceites perigosos, e Qwen2.5-1.5B para perguntas sobre o Maestro, sem acesso ao robô.
- Câmera ou microfone: A câmera via DAT 0.9.0 identifica o QR do talhão; no pré-hardware usamos MockDeviceKit. A voz entra pelo microfone com SpeechRecognizer no Android.
- Output por áudio: O Android TTS fala a operação entendida, pede confirmação e informa erro, cancelamento e sucesso pelo caminho de áudio ativo, sem depender de tela.
- Privacidade e dados: Frames, áudio e transcrições não são persistidos pelo Maestro por padrão. O processamento é local e os logs guardam apenas estado, alvo, intenção e erro.
- Eficiência de bateria: Usamos captura sob demanda, classificador operacional pequeno e Qwen só quando necessário. Câmera, áudio e inferência ficam ativos apenas durante a interação.

## B - Diagrama de arquitetura

- B1: `B1-diagrama-arquitetura-maestro.pdf`
- B2: `B2-codigo-mermaid-maestro.pdf`
- O diagrama explicita os cinco checkpoints, tecnologias/APIs, processamento local, fluxo de dados, confirmação, WebSocket/ROS e separação do Qwen do caminho operacional.

## Evidência interna do MVP

- Android físico Samsung SM-X510 / API 36.
- datDebug + DAT 0.9.0 + MockDeviceKit.
- Captura repetida de plot-03.
- UNDOCK explícito -> SPRAY plot-03 -> permanece no alvo -> DOCK explícito -> novo UNDOCK.
- Guardrails: SPRAY dockado sem movimento; conflito visual/falado sem envio; CANCEL sem envio; UNKNOWN sem movimento.
- IA operacional: 64/64, macro-F1 1.000, zero unsafe accepts.
- 65 testes portáteis e 36 testes do bridge.
- Qwen2.5-1.5B GGUF via llama.cpp provisionado e funcional no tablet; somente CHAT/OUT_OF_SCOPE.
