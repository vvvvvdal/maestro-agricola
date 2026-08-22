# Roteiro final do pitch — 2min50s

Duração-alvo: **2min40s a 2min55s**. Não ultrapassar 3 minutos.

## Slide 1 — Maestro Agrícola (0:00–0:20) — Felipe

Imagine um operador no meio da lavoura, com as mãos ocupadas, acompanhando uma máquina autônoma. A máquina já sabe navegar; mesmo assim, indicar uma nova área ainda pode exigir parar e abrir uma tela. O Maestro Agrícola muda essa conversa: olhar, falar e confirmar.

## Slide 2 — O problema (0:20–0:42) — Felipe

No sol, na poeira e com luvas, um notebook ou tablet adiciona atrito justamente onde a interface deveria desaparecer. Nosso usuário inicial é o operador que acompanha uma máquina conectada e precisa indicar rapidamente uma área de trabalho. O problema não é a autonomia do robô. É a forma como o humano conversa com ela.

## Slide 3 — Olhar, falar e confirmar (0:42–1:20) — Felipe

A jornada tem três ações. Olhar: pelo DAT, uma captura identifica uma placa e seu QR, associados a um talhão seguro. Nesta etapa pré-hardware usamos o MockDeviceKit da própria stack do DAT. Falar: o reconhecimento nativo transcreve a voz e um classificador local restrito entende pulverizar, dock, undock, confirmar, cancelar ou desconhecido. Confirmar: antes de qualquer movimento, o Maestro repete a operação. Se voz e câmera discordarem, se faltar confirmação ou se o comando expirar, nada é enviado.

## Slide 4 — Arquitetura (1:20–1:58) — Rafael

Por dentro, a câmera entra pelo DAT 0.9.0; voz e TTS usam recursos nativos do Android. O app Kotlin resolve o alvo e a intenção, exige confirmação e envia um JSON versionado por WebSocket. O bridge valida validade, estado e duplicidade antes de entregar a meta ao ROS 2 e ao Nav2 no Gazebo. Dock e undock também são comandos explícitos. O Qwen fica separado: pode conversar sobre o domínio, mas nunca recebe acesso ao robô.

## Slide 5 — O que já provamos (1:58–2:35) — Rafael

No Android físico com `datDebug` e MockDeviceKit, repetimos a captura do plot três e fechamos o ciclo completo: undock confirmado, navegação até o plot, permanência no alvo, retorno à doca somente quando pedido e um novo undock depois do docking. Também tentamos quebrar o fluxo: pulverizar dockado não moveu o robô; voz no plot um contra câmera no plot três virou ambiguidade; cancelar não enviou nada. Nos testes, o classificador fez 64 de 64 e zero aceites perigosos, além de 65 testes portáteis e 36 do bridge.

## Slide 6 — Fechamento (2:35–2:52) — Rafael

Não construímos só um assistente nos óculos. Construímos uma interface segura entre linguagem natural e uma máquina física: alvo conhecido, intenção restrita, confirmação e execução verificável. Se avançarmos para a fase presencial, o próximo passo é substituir o MockDeviceKit pelos Meta Wearables reais. Maestro Agrícola: olhe, fale, confirme.

## Direção do ensaio

- Fazer uma única troca: Felipe encerra o slide 3; Rafael entra em “Por dentro...”.
- No slide 3 ou 5, deixar visível `DAT 0.9.0 + MockDeviceKit — pré-hardware`.
- No slide 5, mostrar rapidamente `plot-03`, a tela de confirmação, o TurtleBot em movimento e uma recusa/ambiguidade.
- Cronometrar três vezes. Se passar de 2min55s, cortar exemplos, não acelerar o fechamento.
- Não dizer que câmera, microfone ou áudio dos Meta Wearables físicos já foram validados.
- Não usar o Qwen como prova do controle do robô; ele é uma camada conversacional separada.

## Plano B

Se a gravação ao vivo falhar, usar o vídeo de contingência do E2E já observado e narrar exatamente o que foi validado. Não usar animação como se fosse execução real.