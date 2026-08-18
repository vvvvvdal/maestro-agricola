# Tarefas do MVP - 16 a 22 de agosto de 2026

## Corte obrigatório

O MVP demonstra uma única jornada: reconhecer o QR de `plot-03`, classificar a intenção `SPRAY`, pedir confirmação e enviar um comando idempotente para o TurtleBot 4 simulado no Gazebo.

Não entram nesta semana: React Native, múltiplas ações agrícolas, linguagem aberta, localização sem marcador, robô físico ou pulverização real. Kotlin e Swift compartilham o contrato, o modelo e o comportamento; não são dois produtos independentes.

## Estado em 16 de agosto

- [x] Contratos JSON 1.0 e fixtures criados.
- [x] Modelo local treinado e avaliado: 15/16 acertos operacionais.
- [x] Núcleo seguro do bridge ROS 2 testado, incluindo expiração e deduplicação.
- [x] QR `plot-03`, modelo do Gazebo, mapa de pose e launch integrado criados.
- [x] Esqueletos nativos Kotlin e Swift com IA, confirmação, timeout e WebSocket implementados.
- [ ] Build Android executado no Motorola.
- [ ] Build Swift executado no iPhone 13.
- [x] Imagem Docker construída e jornada headless validada: comando aceito pelo Nav2 e odometria alterada.
- [ ] Detector de QR real conectado ao frame.
- [ ] Adaptador DAT real conectado ao ciclo oficial de sessão/captura.

## Dia 1 - contrato e esqueletos

- [x] **ARC-01 - Congelar o contrato JSON** - Felipe + Átila. Evidência: schemas, fixtures e testes de expiração/deduplicação.
- [ ] **MOB-01 - Criar o app Android/Kotlin** - Átila. Evidência: projeto compila e possui módulos ou interfaces para câmera, áudio, IA e transporte.
- [ ] **IOS-01 - Compilar o app iOS/Swift** - Átila. Evidência: projeto gerado e executado no iPhone 13 com a fonte mock.
- [x] **ROS-01 - Criar o pacote do bridge ROS 2** - Felipe. Evidência: núcleo recebe JSON e enfileira uma meta; teste ROS completo depende do container.
- [x] **AI-01 - Congelar rótulos e frases de avaliação** - Rafael. Evidência: 96 frases e split determinístico para `SPRAY`, `CONFIRM`, `CANCEL` e `UNKNOWN`.
- [x] **VIS-01 - Congelar o alvo visual** - Felipe. Evidência: QR `plot-03`, textura e mapa para pose no cenário.

## Dia 2 - provas isoladas

- [ ] **MOB-02 - Rodar CameraAccess e Mock Device Kit** - Átila. Evidência: frame recebido e versão do DAT registrada.
- [ ] **MOB-03 - Provar voz e TTS no Android** - Átila. Evidência: transcrição curta entra no app e resposta falada é reproduzida.
- [x] **AI-02 - Treinar ou adaptar classificador local leve** - Rafael. Evidência: JSON de aproximadamente 65 KB, relatório e limiar 0,40.
- [ ] **VIS-02 - Detectar o QR em imagem estática** - Felipe. Evidência: `plot-03` correto e `UNKNOWN` para imagem sem alvo.
- [x] **ROS-02 - Mover o TurtleBot 4 simulado** - Felipe. Evidência: `plot-03` virou pose, Nav2 aceitou a meta e a odometria saiu de zero no Gazebo.

## Dia 3 - adaptadores e primeiro gate

- [ ] **MOB-04 - Implementar máquina de estados** - Átila. Evidência: caminho feliz, recusa e timeout testados sem SDK real.
- [-] **AI-03 - Entregar adaptador de inferência** - Rafael + Átila. Paridade de 11 casos compartilhados preparada para Kotlin e Swift; falta executar os testes nas toolchains nativas e medir nos aparelhos.
- [ ] **VIS-03 - Entregar adaptador de visão** - Felipe + Átila. Evidência: frame retorna `target_id`, confiança e timestamp no app.
- [x] **ROS-03 - Validar segurança do bridge** - Felipe. Evidência: testes rejeitam comando vencido/não confirmado e deduplicam UUID.

### Gate do fim do Dia 3

Só continuar adicionando componentes se estes quatro sinais estiverem verdes:

1. O app recebe um frame do mock.
2. O classificador retorna uma intenção local.
3. A visão resolve `plot-03` em uma imagem conhecida.
4. Um fixture JSON move o robô simulado.

Se algum sinal estiver vermelho, cortar complexidade e preservar a jornada vertical.

## Dia 4 - integração ponta a ponta

- [ ] **INT-01 - Conectar app ao bridge por WebSocket** - Átila + Felipe. Evidência: ACK correlacionado pelo mesmo `command_id`.
- [ ] **INT-02 - Executar caminho feliz completo** - equipe. Evidência: olhar, falar, confirmar, enviar e mover o robô no Gazebo.
- [ ] **INT-03 - Exibir estados de diagnóstico** - Átila. Evidência: logs mostram estado, latência, intenção e alvo sem mídia bruta.

## Dia 5 - checkpoints e falhas

- [ ] **QA-01 - Testar recusa, ambiguidade e timeout** - Rafael + Átila. Evidência: nenhum dos casos envia movimento.
- [ ] **QA-02 - Testar desconexão, expiração e duplicata** - Felipe. Evidência: nenhum comando tardio ou repetido move o robô.
- [ ] **QA-03 - Revisar privacidade e bateria** - equipe. Evidência: mídia não persistida, sessão encerrada e captura sob demanda.
- [ ] **QA-04 - Montar evidência 5/5 checkpoints** - Rafael. Evidência: IA, câmera ou microfone, áudio, privacidade e eficiência demonstráveis.

## Dia 6 - congelamento e gravação

- [ ] **REL-01 - Congelar features** - equipe. Depois desta tarefa, somente correções.
- [ ] **REL-02 - Rodar a jornada cinco vezes** - Felipe. Evidência: cinco execuções completas, uma recusa e uma ambiguidade.
- [ ] **PIT-01 - Gravar a demonstração** - Felipe + Átila. Evidência: clipes de app, JSON, Gazebo e falha segura.
- [ ] **PIT-02 - Ensaiar o pitch** - Felipe + Rafael. Evidência: três ensaios entre 2min40s e 2min55s.

## Dia 7 - entrega

- [ ] **REL-03 - Conferir build reproduzível** - Átila. Evidência: clone limpo compila e executa com mock.
- [ ] **DOC-01 - Revisar proposta, slides e vídeo** - equipe. Evidência: nenhuma afirmação contradiz o MVP real.
- [ ] **PIT-03 - Editar e exportar o pitch** - Felipe + Rafael. Evidência: vídeo final com até 3 minutos.
- [ ] **REL-04 - Conferir pacote de submissão** - equipe. Evidência: arquivos abrem, áudio está claro e links funcionam.

## Critério de sucesso da semana

O MVP da semana está pronto sem os óculos reais quando ao menos um app executa a jornada completa com fonte mock, voz local e TurtleBot 4 no Gazebo; os builds mock Kotlin e Swift também devem passar nos dois aparelhos disponíveis. A troca do mock pelo DAT real deve permanecer isolada atrás da mesma interface de frame.
