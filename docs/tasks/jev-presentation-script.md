# Task: Roteiro da apresentacao Jev

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Objetivo

Transformar o plano do grupo de estudos em um roteiro falavel de 50 minutos,
sem criar slides nem reclassificar evidencia. O resultado preserva a
apresentacao como discussao tecnica para um grupo de RL, nao como pitch.

## Entrega

O roteiro canonico esta em
[`presentation-script.md`](../study-groups/jev-rl-2026-10-01/presentation-script.md).
Ele organiza 46 minutos de conteudo e quatro de debate, com fala-guia,
transicoes, visuais previstos, fontes numeradas e claims permitidos/proibidos.

Ele cobre RLCD e calibracao, xadrez Fable/Astra, tres casos de terceiros,
fronteiras do Maestro, resultados JEV-41R, capturas de UI, reserva offline e
roadmap de classes.

## Limites

- RLCD e apresentado como descricao publicada pela TypeSafe, nao como receita
  de treino auditavel ou resultado academico estabelecido.
- Xadrez e resultado de terceiros: Fable perdeu no tempo sob um harness de
  blitz 5+0, uma chamada por lance e sem busca; Astra deu mate em 18 lances.
- A evidencia do Maestro permanece `n=60`, sintetica, uma rodada e `HOLD`.
  O roteiro evidencia `CANCEL -> CONFIRM (0,75)` e nao promove Jev ao APK.
- Capturas do app e reserva offline mantem a legenda `fixture mock local - nao
  executa o robo`; elas nao sao inferencia remota, ASR ou controle fisico.
- Novas classes sao roadmap e nao alteram as seis classes do experimento, o
  contrato ROS, Qwen ou RAG.

## Verificacao

Revisao textual focada confirma que os dez blocos totalizam 50 minutos, que
fontes e evidencias sao separadas e que cada visual tem contexto de uso. Nao
ha mudanca de codigo ou teste de produto nesta task.
