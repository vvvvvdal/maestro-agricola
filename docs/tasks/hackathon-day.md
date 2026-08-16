# Plano do hackathon presencial - 18 de setembro de 2026

## Tempo real disponível

O edital reserva o dia inteiro e a janela bruta entre início e congelamento vai de 11h00 a 17h30. Porém, o cronograma inclui almoço das 12h00 às 14h00, checkpoint às 15h00, coffee break às 15h30, outro checkpoint às 16h00 e reta final das 16h45 às 17h30. A equipe deve planejar aproximadamente 2h45 a 3h de programação previsível, além do tempo de validação nos checkpoints.

O evento não é o momento de criar a solução. É o momento de substituir mocks pelo hardware, medir, corrigir e demonstrar.

## Pré-condições para viajar

- APK Kotlin e projeto Swift compilando; ao menos um build instalável sem depender da internet.
- Jornada completa funcionando com Mock Device Kit.
- Versão do DAT fixada e sample oficial já compreendido.
- Modelo local e fixtures empacotados no repositório.
- Bridge ROS 2, cenário Gazebo e mapa de alvos reproduzíveis.
- Cabos, notebooks próprios e cópias locais das dependências permitidas.
- Vídeo de contingência claramente identificado, sem substituir a validação ao vivo.

## Distribuição no evento

- **Átila:** pareamento, permissões, DAT, câmera, áudio e build Kotlin/Swift.
- **Felipe:** feed visual, detector, bridge ROS 2, Gazebo e execução ponta a ponta.
- **Rafael:** inferência local, métricas, evidências dos checkpoints e materiais do pitch.

## Roteiro operacional

### 09h30-10h30 - onboarding

- [ ] Registrar modelo do smartphone, versão do sistema, firmware e versão liberada do DAT.
- [ ] Parear os óculos e executar o sample oficial sem modificar o projeto principal.
- [ ] Confirmar permissões, câmera e rota de saída de áudio.

### 10h30-11h00 - checkpoints

- [ ] Anotar exatamente qual evidência os avaliadores esperam em cada checkpoint.
- [ ] Ajustar a ordem da demonstração, sem ampliar o escopo.

### 11h00-12h00 - integração mínima

- [ ] Escolher o aparelho mais estável e trocar `MockFrameSource` por `DatFrameSource` somente nele.
- [ ] Receber um frame real e resolver o QR `plot-03`.
- [ ] Reproduzir TTS na rota de áudio disponível.
- [ ] Fazer smoke test da intenção local com uma transcrição curta.

### 14h00-15h00 - jornada completa

- [ ] Executar olhar, falar, confirmar e mover o robô simulado.
- [ ] Medir latência e verificar descarte de frame e áudio.
- [ ] Ensaiar a evidência de IA, entrada dos óculos e saída por áudio.

### 15h00 - checkpoint técnico 1

- [ ] Demonstrar IA funcional.
- [ ] Demonstrar câmera ou microfone dos óculos como entrada.
- [ ] Demonstrar output por áudio.

### 15h30-16h00 - correções curtas

- [ ] Corrigir somente o que bloqueia checkpoint ou jornada crítica.
- [ ] Se câmera e áudio simultâneos estiverem instáveis, coordenar captura sequencial.

### 16h00 - checkpoint técnico 2

- [ ] Demonstrar que o app não persiste mídia bruta.
- [ ] Mostrar captura sob demanda, liberação de recursos e evidência de consumo.

### 16h45-17h30 - congelamento

- [ ] Parar novas features.
- [ ] Rodar a jornada cinco vezes, incluindo recusa.
- [ ] Salvar o build final e gravar uma execução limpa.
- [ ] Conferir os slides e o tempo de Felipe e Rafael.

### 18h00 - pitch

- [ ] Felipe apresenta slides 1 a 3.
- [ ] Rafael apresenta slides 4 a 6.
- [ ] Átila mantém a demo pronta e responde questões sobre mobile/DAT.

## Planos de contingência

| Falha | Resposta sem mudar o produto |
|---|---|
| Stream real instável | Reduzir qualidade/taxa e capturar um frame por comando |
| Microfone dos óculos indisponível | Manter câmera dos óculos como entrada obrigatória e usar o microfone do smartphone para a voz |
| Saída de áudio não roteia | Reconfigurar o dispositivo de comunicação antes de reiniciar a sessão |
| IA lenta | Usar o modelo local menor já empacotado e reduzir o vocabulário |
| Bridge sem rede | Rodar app e bridge na mesma rede local ou usar o endpoint local preparado |
| Detector falha no ambiente | Aumentar o QR e melhorar iluminação; não trocar de técnica durante o evento |

## Regra de decisão

Depois das 16h45, uma mudança só entra se corrigir um bloqueio dos cinco checkpoints ou impedir um comando indevido. Todo o restante fica para depois do pitch.
