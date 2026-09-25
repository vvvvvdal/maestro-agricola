# Tarefas

- [`mvp-week.md`](mvp-week.md): execução do MVP antes do envio da proposta e do pitch.
- [`hackathon-day.md`](hackathon-day.md): integração final com os óculos no evento presencial.
- [`e2e-demo.md`](e2e-demo.md): integração do alvo visual ou falado até ROS 2/Nav2/Gazebo.
- [`submission-readiness.md`](submission-readiness.md): testes, formulário final, diagrama e pitch para a entrega de 22 de agosto.
- [`team-branch-acceleration.md`](team-branch-acceleration.md): ordem, critérios e limites para avançar as branches de mobile, visão e IA.
- [`android-mock-smoke.md`](android-mock-smoke.md): preflight da base Kotlin e handoff para a demonstração `datDebug` com os Meta Wearables.
- [`android-only.md`](android-only.md): decisão de plataforma única e remoção dos artefatos da plataforma descartada.
- [`vision-qr.md`](vision-qr.md): plano e evidências da detecção segura do QR em imagem estática.
- [`ai-device-eval.md`](ai-device-eval.md): gate de paridade Python/Kotlin e handoff do benchmark no Android.
- [`qwen-android-runtime.md`](qwen-android-runtime.md): benchmark que rejeitou Qwen como controle, isolamento de domínio, runtime llama.cpp e smoke físico no SM-X510.
- [`jev-ui-decision-visibility.md`](jev-ui-decision-visibility.md): apresentacao da classe, origem e probabilidade Jev no cartao de intencao, com detalhes tecnicos recolhidos.
- [`jev-experimental-decision.md`](jev-experimental-decision.md): decisao HOLD do experimento Jev, seus limites e gates antes de qualquer adocao operacional.
- [`jev-local-proxy.md`](jev-local-proxy.md): demo Jev opt-in no `mockDebug`, com proxy loopback, teto de chamadas e jornada confirmada até o Gazebo.
- [`jev-remote-privacy-gate.md`](jev-remote-privacy-gate.md): plano para confirmação por turno e bloqueio local preventivo antes de qualquer envio de fala ao Jev.
- [`jev-app-captures.md`](jev-app-captures.md): capturas do `mockDebug` no SM-X510 para baseline local, Jev `SPRAY` e Jev `UNKNOWN`, sem rede ou comando.
- [`jev-offline-reserve-demo.md`](jev-offline-reserve-demo.md): fixtures locais de reserva no SM-X510, capturadas com Wi-Fi desligado e sem executar o robo.
- [`jev-presentation-script.md`](jev-presentation-script.md): roteiro falavel de 50 minutos para o grupo de estudos, com fontes, limites e debate final.
- [`jev-presentation-slides.md`](jev-presentation-slides.md): SVGs 16:9 da comparacao, matrizes e reliability do experimento Jev, com limites de interpretacao.
- [`jev-study-group-deck.md`](jev-study-group-deck.md): deck HTML tecnico de 50 minutos para o grupo de estudos de RL, separado do pitch e com evidencia etiquetada.
- [`jev-rehearsal-1.md`](jev-rehearsal-1.md): ficha do ensaio cronometrado JEV-55, ainda pendente de execucao falada.
- [`jev-post-hold-protocol.md`](jev-post-hold-protocol.md): protocolo de reabertura com guard de cancelamento, ASR, dois holdouts e decisoes sem repeticao ad-hoc.
- [`jev-explicit-cancel-guard.md`](jev-explicit-cancel-guard.md): politica local, desligada por padrao, que bloqueia cancelamentos explicitos sem chamar Jev.
- [`jev-asr-collection.md`](jev-asr-collection.md): protocolo de coleta ASR no SM-X510 sem audio salvo, logcat ou dados identificaveis.
- [`jev-asr-review-cards.md`](jev-asr-review-cards.md): cartoes sem dados pessoais, revisados por duas pessoas, para a coleta ASR de desenvolvimento.
- [`jev-asr-holdout-plan.md`](jev-asr-holdout-plan.md): plano piloto para dois holdouts ASR separados, sem HTTP ou dado pessoal.
- [`jev-asr-primary-cards.md`](jev-asr-primary-cards.md): cartoes congelados antes da coleta do holdout ASR primario.
- [`jev-asr-replication-cards.md`](jev-asr-replication-cards.md): cartoes congelados antes da coleta do holdout ASR de replicacao.
- [`jev-asr-replication-attempt.md`](jev-asr-replication-attempt.md): encerramento da tentativa parcial de replicacao, sem corpus ou chamada remota.
- [`../study-groups/jev-rl-2026-10-01/corpus/asr-primary-manifest.md`](../study-groups/jev-rl-2026-10-01/corpus/asr-primary-manifest.md): holdout primario sanitizado, congelado com hash antes de qualquer HTTP.
- [`visual-identity.md`](visual-identity.md): aplicação da marca AgroTurtles nos apps e no pitch.
- [`visual-identity-v2.md`](visual-identity-v2.md): atualização dos lockups no repositório, Android, pitch e propostas.
- [`android-demo-ui.md`](android-demo-ui.md): transformação da tela diagnóstica Android em interface de demonstração.
- [`dat-prehardware.md`](dat-prehardware.md): integração DAT 0.9.0 com MockDeviceKit antes da validação nos óculos reais.
- [`testing-ux.md`](testing-ux.md): caminho de teste local sem ambiguidade e desligamento limpo do bridge.
- [`visual-smoke.md`](visual-smoke.md): inspeção das telas mobile e visualização do Gazebo/RViz2.
- [`plots-dock.md`](plots-dock.md): histórico do ciclo automático e evidência da remoção de dock/undock implícitos, além das poses de aproximação usadas pelo comando explícito `DOCK`.
- [`../paper/README.md`](../paper/README.md): artigo IEEE, fontes de evidência e procedimento de compilação.

## Convenção

- `[ ]` não iniciada.
- `[-]` em andamento.
- `[x]` concluída e verificada.
- Cada tarefa tem um responsável principal, mas integração é responsabilidade da equipe.
- Uma tarefa só termina quando sua evidência ou critério de aceite foi produzido.
