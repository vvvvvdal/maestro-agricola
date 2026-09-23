# Task: Decisao experimental Jev

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Decisao

**HOLD: favoravel para continuar estudando, inconclusiva e insuficiente para
adocao operacional.** O `LocalIntentClassifier` continua a autoridade no APK e
na branch `main`. O adaptador Jev permanece somente como experimento isolado,
com fakes e fixtures; esta decisao nao liga HTTP na `MainActivity`, nao coloca
chave no Android e nao altera nenhum caminho de comando.

## Evidencia favoravel

Na unica rodada de recuperacao, independente e congelada, com 60 falas
sinteticas, o Jev remoto obteve 54/60 acertos contra 48/60 do baseline local,
macro-F1 de 0,9010 contra 0,8026 e um aceite inseguro contra tres. Tambem
registrou Brier de 0,1057 contra 0,3034, top-label ECE de 0,0787 contra 0,0810,
zero falhas remotas e custo de US$0,001472394. A evidencia, matrizes e limites
estao em [`jev-presentation-evidence.md`](jev-presentation-evidence.md).

Esse e um sinal de que uma `Choice` tipada merece investigacao adicional para
o catalogo fechado de seis intents. Nao e uma prova de que o modelo e seguro,
melhor em geral ou calibrado no campo.

## Evidencia contraria e limites

- Jev classificou um `CANCEL` como `CONFIRM` com probabilidade 0,75
  (`recovery-045`), portanto ainda houve uma aceitacao insegura.
- A latencia p95 remota foi 2.100,575 ms, contra 0,293 ms do local, e depende
  de rede, servico hospedado e credito.
- Ha apenas uma rodada remota, sem intervalos de confianca ou replicacao, em
  60 falas sinteticas. Ela nao cobre ASR real, Android, conectividade de
  campo, hardware, operador ou robo.
- O corpus final original ficou inelegivel depois de uma reserva sem fixture;
  a recuperacao e independente, mas nao apaga esse incidente.

Por isso, nao se pode alegar menor risco operacional, calibracao generalizavel,
prontidao para producao ou substituicao do classificador local.

O protocolo de reabertura fica em
[`jev-post-hold-protocol.md`](jev-post-hold-protocol.md). Ele preserva o
resultado bruto JEV-41R e exige que qualquer guard de produto seja medido como
uma camada separada, em novos holdouts ASR congelados antes de chamadas remotas.

## Guardrails que permanecem

- Os seis rotulos continuam `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e
  `UNKNOWN`.
- `UNKNOWN -> LanguageRouter -> QwenDomainAssistant` nao recebe filtro Jev e
  nao introduz RAG.
- Jev nao recebe `Command`, ROS, WebSocket, estado do robo, resolucao de alvo,
  foto ou audio.
- `TargetResolver`, `InteractionEngine`, confirmacao por audio, expiracao,
  schema e bridge continuam determinísticos e obrigatorios. `SPRAY` nao cria
  lifecycle de doca implicito.

## Gates antes de reabrir adocao

1. Definir e congelar um holdout rotulado independente, incluindo transcricoes
   ASR e estratos de seguranca; uma aceitacao insegura deve bloquear a
   promocao ate ser investigada e tratada por uma politica aprovada.
2. Repetir a avaliacao e registrar incerteza estatistica, versao exata do
   modelo, disponibilidade e custo.
3. Medir latencia e falha fechada no Android e na rede prevista para uso, sem
   expor transcricao ou chave fora de um fluxo de dados aprovado.
4. Somente depois de aprovacao humana explicita, implementar uma integracao
   isolada e validar o fluxo completo, incluindo as barreiras fisicas atuais.

Para a apresentacao, a formulacao correta e: "No corpus sintetico independente
medido, Jev teve melhor resultado descritivo que o baseline; ainda nao foi
adotado pelo Maestro porque uma confusao insegura e a evidencia limitada nao
permitem essa conclusao."
