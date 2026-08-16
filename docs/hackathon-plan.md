# Plano de preparação e hackathon

## Diagnóstico de viabilidade

O MVP cabe em sete dias se a equipe preservar um único corte vertical e trabalhar em paralelo por interfaces estáveis. O objetivo da semana não é suportar toda a agricultura de precisão; é provar uma interação completa, segura e demonstrável.

Os aplicativos serão nativos em Kotlin e Swift para atender aos dois aparelhos disponíveis. Eles compartilham o contrato, o modelo local e a máquina de estados; somente as integrações de sistema e DAT são específicas. React Native fica fora do projeto. Para o pitch ao vivo, a equipe escolhe o aparelho que estiver mais estável.

## Escopo congelado da semana

- Um alvo visual: QR `plot-03`, previamente mapeado.
- Uma ação operacional: `SPRAY` como pedido demonstrativo.
- Três respostas de controle: `CONFIRM`, `CANCEL` e `UNKNOWN`.
- Dois apps companion nativos, com uma única regra de negócio e um único modelo.
- Um bridge WebSocket/ROS 2.
- Um TurtleBot 4 simulado no Gazebo.
- Captura sob demanda e nenhuma mídia bruta persistida.

## Cronograma de sete dias

### Dia 1 - especificar e criar esqueletos

- Congelar jornada, contratos e critérios de aceite.
- Criar app Kotlin, pacote ROS 2, rótulos de IA e QR do cenário.
- Garantir que cada domínio possua fixture ou fake.

### Dia 2 - provar componentes isolados

- Átila: CameraAccess, Mock Device Kit, voz e TTS.
- Felipe: detector do QR e movimento do TurtleBot 4 no Gazebo.
- Rafael: primeiro classificador local e conjunto de avaliação.

### Dia 3 - estabilizar adaptadores

- Integrar classificador e detector por interfaces pequenas.
- Validar schema, expiração, confirmação e deduplicação no bridge.
- Aplicar o gate técnico descrito em [`tasks/mvp-week.md`](tasks/mvp-week.md).

### Dia 4 - fechar o caminho feliz

- Conectar app e ROS 2 por WebSocket.
- Executar a jornada ponta a ponta com mocks.
- Registrar telemetria sem mídia bruta.

### Dia 5 - falhas e checkpoints

- Testar recusa, ambiguidade, timeout, desconexão e duplicata.
- Demonstrar IA, entrada por câmera, áudio, privacidade e eficiência.

### Dia 6 - congelar e gravar

- Não adicionar features.
- Rodar a jornada cinco vezes.
- Gravar app, intenção, JSON, Gazebo e falha segura.
- Felipe e Rafael ensaiam o pitch.

### Dia 7 - entregar

- Verificar build reproduzível e materiais finais.
- Editar o vídeo de até 3 minutos.
- Conferir proposta, pitch e demonstração antes do envio.

## Papéis

- **Átila:** aplicativos Kotlin/Swift, DAT, áudio e orquestração mobile.
- **Felipe:** visão computacional, ROS 2, Gazebo, TurtleBot 4 e integração do simulador.
- **Rafael:** IA local, classificação de intenção, métricas e evidências do checkpoint.
- **Felipe e Rafael:** apresentação do pitch.

Os detalhes e fronteiras estão em [`team.md`](team.md).

## Tempo do hackathon presencial

O hackathon está previsto para 18 de setembro de 2026. A janela bruta vai das 11h00 às 17h30, mas o edital reserva 12h00-14h00 para almoço, 15h00 e 16h00 para checkpoints, 15h30 para coffee break e 16h45-17h30 para a reta final. A equipe deve planejar cerca de 2h45 a 3h de programação previsível, além do tempo usado para demonstrar e receber feedback nos checkpoints.

Nesse período, a equipe deve apenas:

1. parear o hardware e executar o sample oficial;
2. trocar o mock pelo `DatFrameSource`;
3. validar câmera, voz e output por áudio;
4. medir e ajustar estabilidade;
5. passar nos checkpoints e congelar a demo.

O roteiro detalhado está em [`tasks/hackathon-day.md`](tasks/hackathon-day.md).

## Regra diária

Uma tarefa por vez, teste antes ou junto e nenhuma mudança silenciosa de contrato. Ao fim do dia, comparar a spec com a implementação e registrar divergências.
