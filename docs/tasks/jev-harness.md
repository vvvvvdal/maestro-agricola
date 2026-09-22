# Task: Harness comparativo Jev

## Status

**Concluida em 22/09/2026** na branch `test/jev`.

## Decisao

`tools/jev_intent_harness.py` e o ponto unico de comparacao por corpus. Ele
executa o modelo local e uma fixture de resultados Jev para cada mesmo `id` do
TSV, sem enviar a fala ao output. A saida JSON registra por caso apenas:

- `id`, rotulo ouro e categoria;
- predicao local, origem, vetor de probabilidades e latencia;
- predicao Jev, modelo, Choice, uso, latencia, custo e erro;
- hashes do corpus, modelo local e fixture Jev.

O resultado do baseline tambem preserva seu vetor de probabilidades sem texto.
Ele vem do softmax do modelo; regras deterministicas usam vetor one-hot. Isso
permite o calculo comparavel de Brier e ECE na JEV-27.

A fixture deve conter exatamente os IDs do corpus. O harness rejeita CSV/TSV
malformado, ID duplicado, rotulo ouro fora dos seis e fixture com IDs faltando
ou extras. Por caso, ele faz allowlist de modelo, Choice, uso, latencia, custo
e codigo de erro; campos crus, detalhes de erro e respostas integrais nunca
entram no report. A normalizacao da Choice replica a decisao do adaptador:
seis chaves, probabilidades finitas que somam um, `choice` maxima e limiar
`0,40`. Qualquer resposta Jev ausente ou invalida vira `UNKNOWN` com confianca
`0,0` e erro `INVALID_RESPONSE`, sem abortar os outros IDs.

Nesta task a fonte Jev e somente uma fixture local. Nao ha HTTP, SDK, leitura
de `TYPESAFE_API_KEY` ou escrita no APK. JEV-40 podera fornecer a fixture a
partir do smoke remoto dentro do subteto aprovado, sem trocar o formato do
relatorio.

## Uso local

```bash
python3 tools/jev_intent_harness.py \
  --dataset docs/study-groups/jev-rl-2026-10-01/corpus/development.tsv \
  --jev-fixture /caminho/para/fixture-jev.json \
  --output /caminho/para/resultado.json
```

O nome da fixture no exemplo e ilustrativo; ela nao e criada pelo comando.
Resultados remotos versionados devem manter somente os dados permitidos em
[`jev-api-approval.md`](jev-api-approval.md).

## Evidencia

O teste portatil cobre execucao pareada, baixa probabilidade, timeout sem
latencia, ausencia de texto/detalhe cru no report e fixture com IDs incompletos:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m unittest \
  tests.portable.ai.test_jev_intent_harness
```
