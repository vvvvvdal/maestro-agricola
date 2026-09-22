# Task: DTO experimental de avaliacao Jev

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Decisao

[`JevEvaluation`](../../mobile/android/app/src/main/java/br/org/agroturtles/maestro/domain/JevEvaluation.kt)
registra uma avaliacao `Choice` completa sem alterar `IntentPrediction`.
Assim, probabilidades, confidence Jev, modelo, uso, latencia, custo e erro
ficam disponiveis para o harness e o benchmark sem conceder qualquer dado novo
ao caminho operacional.

| Tipo | Campos | Papel |
| --- | --- | --- |
| `JevChoiceAnswer` | `choice`, `probabilities`, `confidence` | Resposta `Choice` valida da API. |
| `JevUsage` | `inputTokens`, `outputTokens` | Uso retornado pela API. |
| `JevEvaluationError` | `code`, `detail` | Falha observada, sem decidir politica de retry. |
| `JevEvaluation` | modelo pedido/respondido, resposta, uso, latencia, custo e erro | Envelope de benchmark para sucesso ou falha. |

## Invariantes

- Sucesso possui `answer`, `responseModel` e `usage`, sem `error`.
- Falha possui `error`, sem `answer` nem `responseModel`; uso e custo podem
  ficar desconhecidos.
- `latencyMs` e custo, quando conhecido, nao podem ser negativos.
- O DTO nao conhece `Command`, estado do robo, alvo, ROS, WebSocket, audio ou
  imagem.
- `IntentPrediction` nao foi modificado. JEV-22 define como uma resposta
  valida entra nele.

## Fora do escopo

- HTTP, serializacao, API key, rede e SDK;
- classificacao de `429`, timeout e resposta invalida, que pertence a JEV-23;
- fake, adaptador e harness;
- qualquer mudanca em `InteractionEngine`, Qwen ou ROS.

## Evidencia

`JevEvaluationTest` cobre resposta bem-sucedida, falha sem resposta e rejeicao
de resposta junto com erro. O teste focado da task e:

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest \
  --tests 'br.org.agroturtles.maestro.domain.JevEvaluationTest' \
  --no-daemon
```
