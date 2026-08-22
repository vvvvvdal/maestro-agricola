# Storyboard do pitch

## Formato

- Proporção: 16:9.
- Duração: até 3 minutos.
- Seis slides, com baixa densidade de texto.
- Paleta oficial: amarelo `#FCC931`, verde `#3C4C1E`, azul `#0F3C65` e branco.
- Tipografia: League Spartan.

## Slide 1 — Capa

**Apresentador:** Felipe.

**Texto:** Maestro Agrícola / Olhe. Fale. Confirme.

**Visual:** operador com óculos inteligentes diante de maquinário agrícola; tratar como visão de produto, não como evidência de hardware já testado.

## Slide 2 — Problema

**Apresentador:** Felipe.

**Texto principal:** A máquina é autônoma. A interface ainda não.

**Apoio:** sol, poeira, luvas, mãos ocupadas, telas que interrompem o fluxo.

## Slide 3 — Jornada

**Apresentador:** Felipe.

**Texto:** Olhar → Falar → Confirmar.

**Apoio:** `DAT 0.9.0 + MockDeviceKit · pré-hardware` / alvo mapeado / voz ≠ câmera → nenhum comando.

**Edição:** mostrar a tela Android identificando `plot-03` e depois a confirmação.

## Slide 4 — Arquitetura e demo

**Apresentador:** Rafael.

**Texto:** DAT → Kotlin + IA operacional → confirmação → WebSocket → ROS 2/Nav2/Gazebo.

**Apoio:** `DOCK` e `UNDOCK` explícitos; Qwen isolado do caminho de controle.

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

## Slide 6 — Fechamento

**Apresentador:** Rafael.

**Texto principal:** Interface segura entre linguagem natural e máquinas físicas.

**Apoio:** Olhe. Fale. Confirme.

**Fechamento:** “Se avançarmos, o próximo gate é trocar o MockDeviceKit pelos Meta Wearables reais.”

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
5. Slide 6 limpo com um segundo de respiro visual para facilitar o corte.

## O que não mostrar como evidência

- imagem genérica de óculos como se fosse frame real;
- HMI manual para Dock/Undock como parte do fluxo Maestro;
- Qwen emitindo comando;
- script legado `make demo*` como prova do lifecycle atual;
- afirmação de câmera/áudio dos Meta Wearables físicos antes do gate de hardware.