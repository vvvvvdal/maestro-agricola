# Storyboard do pitch

## Formato

- Proporção: 16:9.
- Duração: até 3 minutos.
- Sete slides, com baixa densidade de texto.
- Paleta oficial: amarelo `#FCC931`, verde `#3C4C1E`, azul `#0F3C65` e branco.
- Tipografia: League Spartan.
- Linguagem visual: editorial, tecnológica e agrícola, seguindo o deck final versionado.

## Slide 1 — Capa

**Apresentador:** Felipe.

**Texto:** Maestro Agrícola / Olhe. Fale. Confirme.

**Visual:** produtor rural usando óculos Meta diante de maquinário agrícola; tratar como visão de produto, não como evidência de hardware já testado. Logos Meta, CEIA e AKCIT no rodapé, sem bordas brancas e com contraste suficiente.

## Slide 2 — Problema e impacto esperado

**Apresentador:** Felipe.

**Texto principal:** A máquina é autônoma. A interface ainda não.

**Apoio:** sol, poeira, luvas, mãos ocupadas e o ciclo `parar → abrir tela → navegar → retomar`.

**Dado quantitativo:** `20–30% menos custo operacional + retrabalho*`, sempre acompanhado de `* oportunidade estimada; validar no piloto de campo`.

## Slide 3 — Jornada

**Apresentador:** Felipe.

**Texto:** Olhar → Falar → Confirmar.

**Apoio:** `DAT 0.9.0 + MockDeviceKit · pré-hardware` / alvo mapeado / voz ≠ câmera → nenhum comando.

**Edição:** mostrar a tela Android identificando `plot-03` e depois a confirmação.

## Slide 4 — IA e arquitetura

**Apresentador:** Rafael.

**Texto:** DAT → Kotlin + IA operacional → confirmação → WebSocket → ROS 2/Nav2/Gazebo.

**Apoio:** `DOCK` e `UNDOCK` explícitos; Qwen isolado do caminho de controle e limitado a `CHAT | OUT_OF_SCOPE`.

**Edição:** fluxo da esquerda para a direita e 3–5 segundos da simulação.

## Slide 5 — Evidência

**Apresentador:** Rafael.

**Texto:** 64/64 · 0 aceite perigoso · 65 + 36 testes · E2E lifecycle completo.

**Edição:** mostrar quatro evidências curtas:

1. captura repetível `plot-03`;
2. `Undock Goal Succeeded`;
3. `Nav2 completed ... plot-03` / robô no alvo;
4. uma falha segura (`AMBÍGUO` ou `CANCELADO`).

Se houver espaço, incluir `Dock Goal Succeeded` para reforçar o lifecycle explícito.

## Slide 6 — Próximas etapas, expectativas e metas

**Apresentador:** Felipe.

**Texto:** Wearables reais → robô físico → piloto de campo controlado.

**Meta de segurança:** zero aceite perigoso em cada gate.

**Hipótese de impacto:** validar no piloto a oportunidade estimada de `20–30%` de redução em custo operacional e retrabalho. Não apresentar essa faixa como resultado do MVP.

## Slide 7 — Equipe e fechamento

**Apresentador:** Felipe. Átila aparece, mas não precisa falar.

**Ordem alfabética obrigatória:** Átila, Felipe e Rafael.

**Contribuições:**

- Átila — Android, Kotlin, Meta DAT, voz e TTS;
- Felipe — robótica, ROS 2, Nav2, Gazebo, QR e E2E;
- Rafael — IA, avaliação e segurança.

**Texto principal:** Interface segura entre linguagem natural e máquinas físicas.

**Apoio:** Olhe. Fale. Confirme.

## Capturas que a equipe deve gravar

1. Tela do `datDebug` com fonte MockDeviceKit identificando `plot-03`.
2. Intenção reconhecida e tela de confirmação.
3. Gazebo mostrando o `UNDOCK` completo e o robô fisicamente afastado da doca.
4. `SPRAY`/Nav2 chegando ao `plot-03` e permanecendo lá.
5. `DOCK` explícito, se couber no vídeo.
6. Uma recusa segura: conflito visual/voz ou `CANCEL`.
7. Opcional: trecho de terminal com 64/64 e 0 unsafe accepts.

## Ordem sugerida na edição

1. Slides 1 e 2 em tela cheia.
2. Slide 3 + corte curto para Android (`plot-03` e confirmação).
3. Slide 4 + terminal/bridge + Gazebo.
4. Slide 5 + falha segura e números dos testes.
5. Slide 6 com os três gates de evolução.
6. Slide 7 limpo com um segundo de respiro visual para facilitar o corte.

## O que não mostrar como evidência

- imagem genérica de óculos como se fosse frame real;
- o potencial de `20–30%` como resultado já medido;
- HMI manual para Dock/Undock como parte do fluxo Maestro;
- Qwen emitindo comando;
- script legado `make demo*` como prova do lifecycle atual;
- afirmação de câmera/áudio dos Meta Wearables físicos antes do gate de hardware.
