# Plano de preparação e hackathon

## Diagnóstico de viabilidade

O MVP já possui a maior parte do caminho pré-hardware: Android nativo, UI, classificador operacional, contrato, bridge ROS 2, Nav2/Gazebo, visão mapeada, lifecycle explícito e adaptador DAT 0.9.0 validado com MockDeviceKit.

O trabalho até o evento não deve ampliar o produto. O foco é fechar a integração, atualizar o E2E para o lifecycle atual, validar hardware real e congelar a demonstração.

## Escopo congelado

- Android nativo em Kotlin.
- Câmera via Meta Wearables DAT; mock permanece como ferramenta de desenvolvimento.
- Alvos previamente mapeados/allowlisted.
- Tarefa agrícola demonstrativa `SPRAY`.
- `DOCK` e `UNDOCK` como comandos explícitos de lifecycle.
- `CONFIRM`, `CANCEL` e `UNKNOWN` como controles de interação.
- Bridge WebSocket/JSON -> ROS 2/Nav2/Gazebo.
- Captura sob demanda e nenhuma mídia bruta persistida por padrão.
- Qwen local somente como assistente de domínio, caso o wiring seguro esteja concluído; nunca como autoridade operacional.

## Estado técnico atual

- Tasks 1–5: concluídas.
- Task 6: runtime Qwen/llama.cpp, wiring seguro e smoke físico da `MainActivity` concluídos.
- DAT: fluxo pré-hardware e MockDeviceKit concluídos; Meta Wearables reais pendentes.
- UI: jornada Compose integrada à `main`.
- Task 7: E2E final precisa substituir expectativas históricas de dock/undock automático.

## Trabalho até o evento

### 1. Fechar software antes do hardware

- manter o fallback `UNKNOWN -> Qwen` fora de operações e confirmações e medir sua convivência com o hardware final;
- reescrever o E2E para `SPRAY` permanecer no alvo;
- validar `DOCK` e `UNDOCK` explícitos;
- executar os gates `mockDebug` e `datDebug`;
- congelar contrato e assets.

### 2. Preparar evidência offline

- APKs/builds reproduzíveis;
- dependências necessárias disponíveis localmente;
- logs e comandos de diagnóstico documentados;
- vídeo de contingência identificado como contingência, não como substituto de validação física.

### 3. Validar hardware no evento

- sample oficial e pareamento;
- sessão/câmera DAT real;
- target visual real;
- STT/TTS e rota de áudio;
- jornada completa Android -> bridge -> ROS 2/Nav2/Gazebo;
- memória, latência, temperatura e bateria.

## Papéis

- **Átila:** Android, DAT, câmera, áudio, permissões e build.
- **Felipe:** visão, bridge ROS 2, Gazebo/Nav2 e integração E2E.
- **Rafael:** IA local, métricas, checkpoints e apoio ao pitch.
- **Equipe:** segurança, evidência física e congelamento final.

Detalhes: [`team.md`](team.md).

## Hackathon presencial — 18 de setembro de 2026

O evento não é o momento de criar arquitetura nova. A janela deve ser usada para substituir mocks pelo hardware, medir, corrigir incompatibilidades curtas e demonstrar.

Prioridade:

1. confirmar versão DAT/firmware e pareamento;
2. receber frame real;
3. validar áudio;
4. executar a jornada completa;
5. medir estabilidade;
6. passar checkpoints;
7. congelar.

Roteiro detalhado: [`tasks/hackathon-day.md`](tasks/hackathon-day.md).

## Regras de corte

- Se Qwen competir por memória/latência com DAT, câmera ou áudio, a jornada operacional tem prioridade.
- Se o microfone dos óculos não estiver disponível, documentar a rota usada; não inventar suporte.
- Se o stream real estiver instável, reduzir frequência/qualidade ou capturar sob demanda.
- Não trocar QR/target mapeado por localização aberta durante o evento.
- Não alterar contrato ROS para acomodar comportamento de UI.
- Depois do congelamento, entram somente correções que desbloqueiam a demonstração ou impedem comando indevido.
