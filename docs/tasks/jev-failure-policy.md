# Task: Politica de falhas Jev

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Decisao

`JevRequestPolicy` representa a politica do futuro cliente de benchmark, sem
executar HTTP nem entrar no APK. Cada tentativa possui deadline de 2.000 ms; a
politica permite no maximo duas tentativas totais, portanto apenas uma repeticao
apos a primeira falha.

| Falha | Codigo local | Repetir? | Resultado para o adaptador |
| --- | --- | --- | --- |
| Deadline local | `TIMEOUT` | Nao | Falha fechada, sem `IntentPrediction` novo. |
| `401` | `UNAUTHORIZED` | Nao | Falha fechada; nunca expor chave. |
| `422` | `INVALID_REQUEST` | Nao | Falha fechada; corrigir contrato fora da rodada. |
| `429` | `RATE_LIMITED` | Uma vez, depois da primeira falha | Usar `Retry-After` somente ate 1.000 ms; sem header, 250 ms. |
| `529` | `OVERLOADED` | Uma vez, depois da primeira falha | Mesma regra de `429`. |
| JSON ou Choice invalida | `INVALID_RESPONSE` | Nao | Falha fechada, sem inventar rotulo/probabilidade. |
| Transporte/outro HTTP | `TRANSPORT` ou `HTTP_ERROR` | Nao | Falha fechada. |

`Retry-After` acima de 1.000 ms nao gera tentativa tardia: a execucao encerra
como falha. Isto preserva o teto de custo e evita aumentar a latencia de uma
interacao sem conceder um atalho para movimento. A politica deliberadamente nao
usa o retry automatico de um SDK, pois o experimento precisa limitar de forma
observavel o numero de chamadas.

## Limites

- Nenhuma falha retorna `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM` ou `CANCEL` por
  fallback.
- Nenhuma falha chama Qwen, resolve alvo, cria `Command` ou altera estado do
  robo.
- Baixa probabilidade sera definida e exercitada com fake na JEV-24; esta task
  apenas impede retry indevido de uma falha de transporte/protocolo.
- O adaptador real, parser e cliente HTTP pertencem a JEV-24 e JEV-25.

## Evidencia

`JevEvaluationTest` cobre limite de uma repeticao, `Retry-After`, `429`, `529`
e falhas sem retry. O teste focado e:

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest \
  --tests 'br.org.agroturtles.maestro.domain.JevEvaluationTest' \
  --no-daemon
```

Fonte dos status HTTP: [API reference da TypeSafe](https://docs.typesafe.ai/api).
