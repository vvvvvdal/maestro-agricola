# Storyboard do pitch

## Formato

- Proporção: 16:9.
- Duração: até 3 minutos.
- Seis slides, com baixa densidade de texto.
- Paleta oficial: amarelo `#FCC931`, verde `#3C4C1E`, azul `#0F3C65` e branco.
- Tipografia: League Spartan em toda a apresentação.
- Marca completa na abertura e no fechamento; tartaruga verde sobre amarelo como assinatura nos slides 2 a 5.

## Slide 1 — Capa

**Apresentador:** Felipe.

**Texto:** Maestro Agrícola / Olhe. Fale. Confirme.

**Visual:** operador usando óculos inteligentes diante de um robô agrícola em uma linha de cultivo.

**Edição:** abrir com 1 segundo de imagem limpa; entrada suave do título.

## Slide 2 — Problema

**Apresentador:** Felipe.

**Texto principal:** A máquina é autônoma. A interface ainda não.

**Apoio:** parar, limpar as mãos, abrir uma tela, reprogramar.

**Edição:** cortes rápidos de sol, poeira, luvas e tela; não usar números sem fonte.

## Slide 3 — Jornada

**Apresentador:** Felipe.

**Texto:** Olhar → Falar → Confirmar.

**Apoio:** Softmax local · 65 KB · 4 intenções · limiar 0,40. Voz ≠ câmera → nenhum comando.

**Edição:** destacar um passo por vez, sincronizado com a fala.

## Slide 4 — Arquitetura e demo

**Apresentador:** Rafael.

**Texto:** câmera via DAT → app Kotlin + softmax local → WebSocket → ROS 2/Nav2/Gazebo.

**Edição:** animar o fluxo da esquerda para a direita. A fala explica que voz/TTS usam o sistema mobile, a rota Bluetooth será validada e o telefone é fallback. Inserir 3 a 5 segundos da simulação recebendo o comando.

## Slide 5 — Evidência para a banca

**Apresentador:** Rafael.

**Texto:** QR detectado · IA 15/16 operacional · `ACCEPTED` + Nav2 ativo + odometria mudou.

**Edição:** mostrar cada compromisso no momento em que for citado. Sobrepor primeiro o comando aceito e o movimento; depois mostrar “cancelar” sem comando. “0 mídia salva” significa comportamento do MVP, não auditoria externa.

## Slide 6 — Fechamento

**Apresentador:** Rafael.

**Texto:** O futuro do campo não precisa de mais telas.

**Apoio:** Olhe. Fale. Confirme.

**Edição:** manter 1 segundo de silêncio visual ao final para facilitar o corte do vídeo.

## Capturas que a equipe deve gravar

1. Centralização da placa `PLOT-03` no feed recebido dos Meta Wearables pelo DAT.
2. Transcrição e intenção reconhecida no app.
3. Pergunta de confirmação pelo TTS do celular; registrar a rota usada na gravação.
4. JSON aceito pelo bridge.
5. Robô iniciando o deslocamento no Gazebo.
6. Recusa ou ambiguidade sem movimento.

## Ordem sugerida na edição do vídeo

1. Slides 1 e 2 em tela cheia com Felipe em picture-in-picture opcional.
2. Slide 3 com realce sequencial dos três pontos.
3. Slide 4 com 3 a 5 segundos do terminal/bridge e corte para o Gazebo.
4. Slide 5 com duas evidências: `ACCEPTED` + movimento e `cancelar` + ausência de envio.
5. Slide 6 limpo; manter um segundo depois da última palavra para facilitar o corte.
