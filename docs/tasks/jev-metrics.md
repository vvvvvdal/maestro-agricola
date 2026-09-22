# Task: Metricas do experimento Jev

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Decisao

`tools/jev_intent_metrics.py` recebe o report pareado do harness e produz
metricas separadas para `local` e `jev`, mantendo `id`, rotulo ouro e categoria
como unidade de evidencia. Ele nao recebe texto, chave ou parametros de rede.

| Medida | Definicao |
| --- | --- |
| Matriz e macro-F1 | Usam a predicao operacional, depois do limiar `0,40`. A macro e a media dos seis F1, incluindo classe sem acerto como zero. |
| Aceite perigoso | Ouro `CANCEL` ou `UNKNOWN` previsto como `SPRAY`, `DOCK`, `UNDOCK` ou `CONFIRM`. Cada caso preserva somente ID, ouro, previsao e probabilidade. |
| Brier multiclasses | Media, sobre vetores validos, da soma dos erros quadrados das seis probabilidades contra o vetor ouro one-hot. |
| Top-label ECE | Dez bins iguais de confianca da classe com maior probabilidade; o report inclui os bins para o reliability diagram da JEV-42. |
| Coverage | Fracao de casos com vetor completo e valido. Timeout/erro nao entra em Brier/ECE, mas reduz coverage e aparece em `failures`. |
| Latencia | p50 e p95 por nearest-rank sobre latencias validas em ms. |
| Custo e falhas | Soma custo conhecido, conta casos com custo e preserva apenas o codigo de erro por ID. |

O baseline agora grava seu vetor softmax no harness. Para regras locais e para
o fallback OOV que ja devolve `UNKNOWN` com `1,0`, o vetor e one-hot. Jev usa o
vetor validado de `Choice`; qualquer erro Jev fica fora de Brier/ECE. Assim, calibracao usa a
distribuicao bruta valida, enquanto acuracia e seguranca usam a decisao
operacional que pode ter sido abstida pelo limiar.

## Uso

```bash
python3 tools/jev_intent_metrics.py \
  --input /caminho/para/resultado-pareado.json \
  --output /caminho/para/metricas.json
```

Uma fixture local apenas prova o formato, as formulas e o tratamento de erro.
Ela nao e evidencia de qualidade, custo, latencia ou calibracao do Jev. Esses
campos so passam a ter valor experimental apos o smoke JEV-40 e a rodada final
JEV-41, com seus hashes e versao registrados.

## Evidencia

O teste portatil cobre matriz de seis classes, macro-F1, aceite perigoso,
falha, coverage, Brier, ECE, bins de reliability, p50/p95, custo e modelo:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m unittest \
  tests.portable.ai.test_jev_intent_harness \
  tests.portable.ai.test_jev_intent_metrics
```
