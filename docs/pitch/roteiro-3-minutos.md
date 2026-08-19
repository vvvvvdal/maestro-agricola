# Roteiro final do pitch — 2min50s

Duração-alvo: **2min40s a 2min55s**. O texto falado tem 376 palavras, deixando margem para pausas e a troca de apresentador. Não ultrapassar 3 minutos.

## Slide 1 — Maestro Agrícola (0:00–0:20) — Felipe

Imagine um operador no meio da lavoura, com as mãos ocupadas, acompanhando um robô autônomo. A máquina já navega; mesmo assim, indicar uma nova área ainda pode exigir parar e abrir uma tela. O Maestro Agrícola muda essa conversa: olhar, falar e confirmar.

## Slide 2 — O problema (0:20–0:42) — Felipe

No sol, na poeira e com luvas, um notebook ou tablet adiciona atrito justamente onde a interface deveria desaparecer. Nosso usuário inicial é o operador que acompanha uma máquina conectada e precisa indicar rapidamente uma área de trabalho. O problema não é a autonomia do robô. É a forma como o humano conversa com ela.

## Slide 3 — Olhar, falar e confirmar (0:42–1:22) — Felipe

A jornada tem três ações. Olhar: uma placa legível e seu QR identificam o plot três, associado a uma pose segura. Falar: o reconhecimento nativo transcreve a voz; depois, uma cascata local combina regras de segurança com um classificador treinado e retorna pulverizar, confirmar, cancelar ou desconhecido. São 144 frases de treino, 64 de avaliação separada e um artefato de apenas 367 KiB. Se o operador disser “no plot três”, o ID falado também é validado. Confirmar: o Maestro repete o alvo. Abaixo de 40% de confiança, ou se voz e câmera discordarem, nada é enviado.

## Slide 4 — Arquitetura (1:22–1:59) — Rafael

Por dentro, a câmera entra pelo DAT. Voz e TTS usam recursos nativos do celular, com o telefone como fallback. O app Kotlin consome a IA local, o catálogo de plots e o contrato versionado. Após a confirmação, um JSON com validade curta chega ao bridge, que valida e entrega uma meta ao Nav2 no Gazebo. Como o DAT público não documenta pose ou IMU, o MVP usa um alvo mapeado; GPS do operador não vira destino do robô.

## Slide 5 — Evidência e próximo teste (1:59–2:34) — Rafael

Hoje já provamos três sinais: a placa completa foi decodificada como plot três; a política local classificou os 64 casos controlados e não aceitou nenhum caso perigoso; e o cliente recebeu ACCEPTED, ativou o Nav2 e mudou a odometria do TurtleBot. Isso não substitui o teste de campo. “Cancelar” foi recusado sem movimento. O próximo gate é validar no Android físico o DAT, latência, bateria e rota Bluetooth com os óculos reais.

## Slide 6 — Fechamento (2:34–2:52) — Rafael

O Maestro conecta interface multimodal e robótica com protocolo aberto, confirmação obrigatória e ROS 2, sem se prender a um fabricante. O futuro do campo não precisa de mais uma tela. Precisa entender alvo, intenção e segurança. Maestro Agrícola: olhe, fale, confirme.

## Direção do ensaio

- Fazer uma única troca: Felipe encerra o slide 3; Rafael entra diretamente em “Por dentro...”.
- Falar como conversa, não como leitura. Pausar após “É a forma como o humano conversa com ela”.
- No slide 5, mostrar brevemente a placa detectada, `ACCEPTED`, o TurtleBot em movimento e a recusa de `cancelar`.
- Cronometrar três vezes. Se passar de 2min55s, cortar exemplos da fala; não acelerar o fechamento.
- Não dizer que DAT, Meta Wearables ou áudio Bluetooth já foram validados fisicamente antes do teste real.

## Plano B sem captura de tela

Se a gravação da simulação falhar, manter os slides e dizer exatamente a evidência observada no teste registrado. Não substituir por animação que pareça prova real.
