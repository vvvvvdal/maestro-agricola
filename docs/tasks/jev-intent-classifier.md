# Task: Adaptador `JevIntentClassifier`

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Decisao

`JevIntentClassifier` implementa `IntentClassifier` e recebe somente um
`JevChoiceEvaluator` injetado. Assim, cada uso escolhe uma fonte de
classificacao: local ou Jev. O adaptador nao instancia, consulta ou usa
`LocalIntentClassifier` como fallback.

Uma resposta somente e operacionalmente valida quando:

- `choice` pertence exatamente a `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`,
  `CANCEL` ou `UNKNOWN`;
- `probabilities` possui exatamente essas seis chaves, valores finitos entre
  zero e um, soma dentro de `0,001` de um e `choice` e maxima (empate numerico
  dentro dessa tolerancia e aceito);
- `confidence` do Jev tambem e finito e fica entre zero e um.

Para resposta valida, o adaptador usa `probabilities[choice]` em
`IntentPrediction.confidence` e origem `JEV`. O limiar operacional permanece
`0,40`, igual ao baseline local: uma escolha diferente de `UNKNOWN` abaixo dele
vira `UNKNOWN`, mantendo a probabilidade medida. O campo `confidence` do Jev
nao substitui essa probabilidade.

Falha do avaliador, `JevEvaluation` sem resposta, distribuicao invalida ou
rotulo fora do catalogo retornam `UNKNOWN` com confianca `0,0` e origem `JEV`.
O adaptador nao cria `Command`, nao chama Qwen, nao resolve alvo e nao acessa
rede, chave, ROS ou WebSocket.

## Selecao experimental

O adaptador foi criado apenas na branch `test/jev` e ainda nao e conectado a
`MainActivity`. O baseline local permanece a implementacao do app. JEV-26
introduzira o harness que escolhe explicitamente um classificador por rodada;
nao existe voto, fallback local ou dupla classificacao da mesma fala.

## Evidencia

`JevIntentClassifierTest` cobre os seis rotulos, limiar de baixa
probabilidade, timeout, `429`, resposta/distribuicao invalidas, excecao local,
`UNKNOWN`, cancelamento tardio e conflito de alvo. Os ultimos tres cenarios
passam pelo `InteractionEngine` existente e nao criam `Command`.

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest \
  --tests 'br.org.agroturtles.maestro.domain.JevIntentClassifierTest' \
  --tests 'br.org.agroturtles.maestro.domain.FakeJevChoiceEvaluatorTest' \
  --tests 'br.org.agroturtles.maestro.domain.JevEvaluationTest' \
  --no-daemon
```
