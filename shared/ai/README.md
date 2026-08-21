# IA local

O Maestro mantém duas funções de IA local separadas por segurança: um classificador operacional que pode alimentar o `InteractionEngine` e um assistente Qwen que só pode responder `CHAT` ou `OUT_OF_SCOPE`.

## Classificador operacional

O artefato canônico é `intent_model.json`, treinado a partir de `dataset/intents.tsv` e interpretado diretamente no Android/Kotlin.

A cascata local usa:

1. regras de alta precisão para cancelamento, ambiguidade e ordens inequívocas;
2. classificador linear softmax com unigramas, bigramas e n-gramas de caracteres;
3. fallback para `UNKNOWN` quando a confiança é insuficiente.

Rótulos atuais:

- `SPRAY`: pulverização/navegação para alvo resolvido;
- `DOCK`: retorno explícito à doca;
- `UNDOCK`: saída explícita da doca;
- `CONFIRM`: confirmação de operação pendente;
- `CANCEL`: cancelamento/recusa;
- `UNKNOWN`: frase fora do caminho operacional seguro.

`UNKNOWN` não autoriza movimento. `SPRAY`, `DOCK` e `UNDOCK` ainda passam pelas validações e confirmação do `InteractionEngine` antes de existir `Command`.

A avaliação histórica `evaluation.tsv` tem 64 frases das quatro classes originais. A avaliação de campo usada na evolução atual é `field_evaluation.tsv`, com 48 frases balanceadas entre os seis rótulos; o baseline local classificou 48/48 no gate da Task 6.

Para regenerar o modelo quando a task exigir explicitamente:

```bash
python3 tools/train_intent_model.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Avaliação do Qwen

`tools/qwen_intent_eval.py` e `qwen_evaluation.json` registram a tentativa de usar `Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M` como classificador dos mesmos seis rótulos. Resultado reproduzível:

- 48 exemplos;
- 36 corretos;
- acurácia 0,75;
- macro-F1 0,7384;
- 3 aceites perigosos;
- mediana de latência ~2,36 s no benchmark desktop e p95 ~10,78 s.

Esse resultado rejeitou o Qwen como autoridade operacional.

## Papel seguro do Qwen

O modelo foi mantido apenas como assistente local de domínio:

```text
LocalIntentClassifier
  -> rótulo operacional -> InteractionEngine
  -> UNKNOWN -> LanguageRouter -> QwenDomainAssistant -> CHAT | OUT_OF_SCOPE
```

A GBNF do runtime Android restringe a estrutura da resposta. O parser Kotlin falha fechado para `OUT_OF_SCOPE` se a saída estiver malformada ou inventar outro tipo. Qwen não conhece `Command`, WebSocket, ROS ou `TargetResolver`.

O runtime Android via `llama.cpp` foi validado em smoke físico no SM-X510, mas a `MainActivity` ainda não usa esse fallback. Veja [`../../docs/tasks/qwen-android-runtime.md`](../../docs/tasks/qwen-android-runtime.md).