# Task: Fake local do avaliador Jev

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Decisao

`JevChoiceEvaluator` e a fronteira minima entre um futuro cliente de `Choice`
e o adaptador da JEV-25. Nesta task nao existe cliente HTTP: o
`FakeJevChoiceEvaluator`, em `src/test`, devolve um `JevEvaluation` configurado
por texto e falha para entradas sem configuracao.

O fake exercita localmente cinco resultados deterministas:

| Cenario | Resultado |
| --- | --- |
| Escolha valida | `SPRAY` com probabilidade `0.91`. |
| Baixa probabilidade | `SPRAY` com probabilidade `0.23`. |
| Timeout | Falha `TIMEOUT`, sem `answer`. |
| Limite de taxa | Falha `RATE_LIMITED` com `retryAfterMs = 750`, sem `answer`. |
| Resposta invalida | Falha `INVALID_RESPONSE`, sem `answer`. |

A baixa probabilidade e somente preservada como dado de avaliacao nesta task.
Ela nao cria `IntentPrediction`, `Command`, confirmacao, resolucao de alvo,
Qwen ou chamada ROS. A conversao para o classificador e a decisao de limiar
pertencem ao adaptador JEV-25.

## Limites

- O fake nao le chave, nao usa rede e nao mede custo remoto.
- O fake existe apenas em `src/test`; ele nao pode ser selecionado pelo APK.
- Nenhum cenario de erro inventa rotulo ou probabilidade.
- A politica de retry continua em
  [`jev-failure-policy.md`](jev-failure-policy.md).

## Evidencia

O teste focado cobre os cinco cenarios e texto sem configuracao:

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest \
  --tests 'br.org.agroturtles.maestro.domain.FakeJevChoiceEvaluatorTest' \
  --no-daemon
```
