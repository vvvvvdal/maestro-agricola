# Plano de preparação e hackathon

## Diagnóstico de viabilidade

O MVP pré-hardware está fechado: Android nativo, UI, classificador operacional, contrato, bridge ROS 2, Nav2/Gazebo, visão mapeada, lifecycle explícito e adaptador DAT 0.9.0 com MockDeviceKit foram integrados no mesmo E2E.

A entrega de seleção de 22/08/2026 não depende dos Meta Wearables físicos. O hardware real vira o próximo gate caso a equipe seja selecionada para a fase presencial em São Paulo.

## Escopo congelado

- Android nativo em Kotlin.
- `datDebug` + DAT 0.9.0 + MockDeviceKit no MVP pré-hardware.
- Meta Wearables físicos somente na fase posterior de hardware.
- Alvos previamente mapeados/allowlisted.
- Tarefa agrícola demonstrativa `SPRAY`.
- `DOCK` e `UNDOCK` como comandos explícitos de lifecycle.
- `CONFIRM`, `CANCEL` e `UNKNOWN` como controles de interação.
- Bridge WebSocket/JSON -> ROS 2/Nav2/Gazebo.
- Captura sob demanda e nenhuma mídia bruta persistida por padrão.
- Qwen local somente como assistente de domínio; nunca como autoridade operacional.

## Estado técnico em 22/08/2026

- Tasks 1–7: concluídas para o MVP pré-hardware.
- Classificador operacional: 64/64, macro-F1 1,0 e 0 aceites perigosos.
- Testes: 65 portáteis + 36 bridge, todos verdes.
- DAT: `datDebug` + MockDeviceKit executado em Samsung SM-X510/API 36.
- Captura: `Olhar para o alvo` repetível na mesma execução após rearm da câmera simulada.
- E2E: `UNDOCK -> SPRAY plot-03 -> DOCK -> UNDOCK` observado no Gazebo via app.
- Guardrails: `SPRAY` dockado, conflito visual/voz e `CANCEL` sem movimento.
- Bridge: expiração, confirmação e deduplicação de `command_id` cobertas por teste.
- Qwen: runtime/wiring seguro já validado em testes anteriores; o GGUF não é empacotado e precisa ser provisionado se o assistente for mostrado.

## Trabalho restante até a entrega de seleção

1. Congelar a `main`; somente correções bloqueantes.
2. Fazer push e confirmar CI.
3. Atualizar formulário, docs e roteiro com a evidência final.
4. Gravar o vídeo/pitch usando a demonstração pré-hardware real observada.
5. Rotular claramente `DAT + MockDeviceKit` e não sugerir que o frame veio dos óculos físicos.
6. Manter uma gravação de contingência do E2E.

## Papéis

- **Átila:** Android, DAT, câmera, áudio, permissões e build.
- **Felipe:** visão, bridge ROS 2, Gazebo/Nav2 e integração E2E.
- **Rafael:** IA local, métricas, checkpoints e apoio ao pitch.
- **Equipe:** segurança, evidência e congelamento final.

Detalhes: [`team.md`](team.md).

## Fase presencial — se selecionados

A fase com hardware não é o momento de redesenhar o produto. O objetivo será substituir o MockDeviceKit pelo dispositivo Meta real e medir o que o pré-hardware não pode provar.

Prioridade:

1. confirmar versão DAT/firmware e pareamento;
2. receber frame real dos óculos;
3. validar rota de microfone/TTS;
4. executar a mesma jornada Android -> bridge -> ROS 2/Nav2/Gazebo;
5. medir estabilidade, memória, latência, temperatura e bateria;
6. passar os checkpoints físicos;
7. congelar novamente.

Roteiro detalhado: [`tasks/hackathon-day.md`](tasks/hackathon-day.md).

## Regras de corte

- Se Qwen competir por memória/latência com DAT, câmera ou áudio, a jornada operacional tem prioridade.
- Se o microfone dos óculos não estiver disponível, documentar a rota usada; não inventar suporte.
- Se o stream real estiver instável, reduzir frequência/qualidade ou capturar sob demanda.
- Não trocar QR/target mapeado por localização aberta durante o evento.
- Não alterar contrato ROS para acomodar comportamento de UI.
- Depois do congelamento, entram somente correções que desbloqueiam a demonstração ou impedem comando indevido.