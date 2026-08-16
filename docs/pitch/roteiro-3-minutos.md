# Roteiro do pitch — até 3 minutos

Duração-alvo: **2min40s a 2min50s**. O texto tem margem para pausas e troca de slides.

## Slide 1 — Maestro Agrícola (0:00–0:20) — Felipe

Imagine um operador no meio da lavoura, com as mãos ocupadas, tentando orientar um robô autônomo. A máquina já sabe navegar, mas a interface ainda exige parar o trabalho e abrir uma tela. O Maestro Agrícola muda isso: o operador olha, fala e comanda.

## Slide 2 — A autonomia ainda depende de uma tela (0:20–0:45) — Felipe

Hoje, reprogramar uma rota no campo pode exigir notebook ou tablet, justamente em um ambiente de sol, poeira e operação contínua. Essa fricção reduz a produtividade e afasta a tecnologia de quem mais precisa usá-la. O problema não é a autonomia do robô. É a forma como o humano conversa com ela.

## Slide 3 — Três ações substituem uma tela (0:45–1:20) — Felipe

Com o Maestro, a jornada tem três passos. Primeiro, olhar: a câmera identifica o talhão ou alvo centralizado. Depois, falar: a inteligência artificial transforma “pulverizar esta área” em uma intenção estruturada. Por fim, confirmar: o sistema responde “pulverizar talhão três, confirmar?”. Só após o sim o comando é enviado. É uma interação natural, mãos-livres e com segurança explícita.

## Slide 4 — Um corte vertical comprovável (1:20–2:05) — Rafael

O protótipo é simples e modular. Os óculos fornecem câmera, microfone e áudio. O app nativo, em Kotlin ou Swift, interpreta voz e alvo localmente e envia um JSON por WebSocket. Um bridge ROS 2 transforma esse comando em uma meta no Gazebo. Antes de receber o hardware, validamos a jornada com fontes simuladas e o Mock Device Kit. E tomamos uma decisão importante de viabilidade: como o DAT atual não expõe pose ou IMU dos óculos, o MVP usa um alvo visual previamente mapeado. Assim demonstramos a experiência completa sem depender de uma API inexistente.

## Slide 5 — Viável, responsável e pronto para validar (2:05–2:35) — Rafael

O Maestro atende aos cinco checkpoints: inteligência artificial funcional, câmera dos óculos como entrada, áudio como saída, privacidade e eficiência. A voz completa a experiência pelo caminho de áudio disponível no aparelho. Capturamos apenas quando há comando e descartamos a imagem após o processamento. Nenhum movimento acontece sem confirmação, e a navegação segura continua sob responsabilidade do próprio robô. O resultado é uma solução agnóstica de fabricante e pronta para validação.

## Slide 6 — Fechamento (2:35–2:50) — Rafael

O futuro do campo não precisa de mais uma tela. Precisa de uma interface que entenda onde o operador olha, o que ele pede e quando é seguro agir. Maestro Agrícola: olhe, fale, confirme.

## Ensaio

- Falar em ritmo conversado, sem acelerar o slide 4.
- Pausar depois de “o problema é a forma como o humano conversa com ela”.
- Dar ênfase à decisão de não depender de IMU.
- Fazer apenas uma troca de apresentador: Felipe encerra o slide 3 e Rafael assume no slide 4.
- Encerrar olhando para a câmera e repetir: “olhe, fale, confirme”.
