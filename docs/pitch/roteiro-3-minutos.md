# Roteiro final do pitch — 2min50s

Duração-alvo: **2min40s a 2min55s**. O texto falado tem aproximadamente 370 palavras, deixando margem para pausas e a troca de apresentador. Não ultrapassar 3 minutos.

## Slide 1 — Maestro Agrícola (0:00–0:20) — Felipe

Imagine um operador no meio da lavoura, com as mãos ocupadas, acompanhando um robô autônomo. A máquina já navega; mesmo assim, indicar uma nova área ainda pode exigir parar e abrir uma tela. O Maestro Agrícola muda essa conversa: olhar, falar e confirmar.

## Slide 2 — O problema (0:20–0:42) — Felipe

No sol, na poeira e com luvas, um notebook ou tablet adiciona atrito justamente onde a interface deveria desaparecer. Nosso usuário inicial é o operador que acompanha uma máquina conectada e precisa indicar rapidamente uma área de trabalho. O problema não é a autonomia do robô. É a forma como o humano conversa com ela.

## Slide 3 — Olhar, falar e confirmar (0:42–1:18) — Felipe

A jornada tem três ações. Olhar: um QR identifica o talhão três, associado a uma posição segura no mapa. Falar: o reconhecimento nativo transcreve “pulverizar esta área”, e uma IA pequena, local e restrita classifica a intenção. Confirmar: o sistema pergunta “pulverizar talhão três?”. Só o sim libera o JSON. Se houver ambiguidade ou o usuário disser “cancelar”, nenhum comando chega ao robô.

## Slide 4 — Arquitetura (1:18–1:58) — Rafael

Por dentro, a câmera entra pelo DAT. Voz e TTS usam recursos nativos do celular e tentam a rota Bluetooth, com o telefone como fallback. Kotlin e Swift consomem a mesma IA local e o mesmo contrato. Após a confirmação, um JSON com validade curta chega ao bridge, que valida e entrega uma meta ao Nav2 no Gazebo. Como o DAT público não documenta pose ou IMU, o MVP usa QR mapeado e isola a integração real no adaptador de câmera.

## Slide 5 — Evidência e próximo teste (1:58–2:32) — Rafael

Hoje já provamos o ciclo na simulação. O cliente enviou “pulverizar esta área”, recebeu ACCEPTED, o Nav2 ficou ativo e a odometria do TurtleBot mudou. “Cancelar” foi recusado localmente, sem movimento. O desenho cobre os cinco pilares: IA, câmera e voz, saída por áudio, privacidade e eficiência por captura sob demanda. O próximo passo é compilar nos dois aparelhos e validar DAT, latência, bateria e rota Bluetooth com os óculos reais.

## Slide 6 — Fechamento (2:32–2:50) — Rafael

A John Deere mostra o valor de acompanhar máquinas pelo celular; a Meta mostra os óculos como interface multimodal. O Maestro conecta esses mundos com protocolo aberto, confirmação obrigatória e ROS 2, sem se prender a um fabricante. O futuro do campo não precisa de mais uma tela. Precisa entender alvo, intenção e segurança. Maestro Agrícola: olhe, fale, confirme.

## Direção do ensaio

- Fazer uma única troca: Felipe encerra o slide 3; Rafael entra diretamente em “Por dentro...”.
- Falar como conversa, não como leitura. Pausar após “É a forma como o humano conversa com ela”.
- No slide 5, a tela deve mostrar brevemente `ACCEPTED`, o TurtleBot em movimento e a recusa de `cancelar`.
- Cronometrar três vezes. Se passar de 2min55s, cortar exemplos da fala; não acelerar o fechamento.
- Não dizer que DAT, iPhone, Motorola ou áudio Bluetooth já foram validados fisicamente.

## Plano B sem captura de tela

Se a gravação da simulação falhar, manter os slides e dizer exatamente a evidência observada no teste registrado. Não substituir por animação que pareça prova real.
