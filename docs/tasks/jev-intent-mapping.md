# Task: Mapeamento Jev para `IntentPrediction`

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Decisao

Uma resposta `JevChoiceAnswer` valida usa o mapeamento abaixo:

| Campo Jev | Campo operacional | Regra |
| --- | --- | --- |
| `choice` | `IntentPrediction.label` | Copiar o rotulo escolhido. |
| `probabilities[choice]` | `IntentPrediction.confidence` | Copiar a probabilidade da classe escolhida. |
| - | `IntentPrediction.source` | Usar `JEV`. |
| `confidence` Jev | Nenhum | Permanecer no DTO/benchmark; nao usar como confianca operacional. |

O helper `JevChoiceAnswer.toIntentPrediction()` nao acessa rede, `Command`,
estado do robo, alvo, Qwen, ROS ou WebSocket. Ele tambem nao cria uma operacao:
apenas constroi o mesmo contrato de classificacao que o `InteractionEngine`
ja recebe.

## Falha de forma

Se `probabilities` nao possuir a chave escolhida, o helper rejeita a resposta
com `IllegalArgumentException` em vez de inventar uma confianca. JEV-23 e
JEV-24 definem como o adaptador converte essa falha em resultado fechado, sem
`Command`.

## Evidencia

`JevEvaluationTest` cobre:

- probabilidade escolhida `0.82` diferente do confidence Jev `0.64`;
- origem `JEV`;
- rejeicao da resposta sem probabilidade da escolha.

Teste focado:

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest \
  --tests 'br.org.agroturtles.maestro.domain.JevEvaluationTest' \
  --no-daemon
```
