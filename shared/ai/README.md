# Modelo local de intenção

O artefato canônico é `intent_model.json`. Ele é treinado a partir de `dataset/intents.tsv` e executado localmente no app Android.

O MVP usa uma cascata híbrida local:

1. regras de alta precisão reconhecem cancelamentos, bloqueiam hesitações e capturam ordens inequívocas;
2. um classificador linear softmax resolve as demais frases usando unigramas, bigramas e n-gramas de caracteres de 3 a 5 posições;
3. baixa confiança vira `UNKNOWN`.

O resultado inclui a origem `RULE` ou `MODEL`, o que deixa a demonstração e os logs auditáveis. Essa escolha é intencional:

- inferência pequena e rápida em aparelhos antigos;
- nenhuma chamada de rede;
- o modelo pode ser interpretado em Kotlin sem runtime externo;
- probabilidades e vocabulário podem ser auditados;
- erros comuns de transcrição ainda compartilham n-gramas com palavras conhecidas;
- o classificador continua sendo IA treinada, enquanto as regras cobrem apenas padrões inequívocos e segurança.

Rótulos:

- `SPRAY`: pedido operacional.
- `CONFIRM`: confirmação explícita.
- `CANCEL`: recusa ou cancelamento.
- `UNKNOWN`: frase fora do vocabulário operacional.

Para regenerar:

```bash
python3 tools/train_intent_model.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

O treino usa `dataset/intents.tsv`; a avaliação independente usa `dataset/evaluation.tsv`. O relatório versionado contém métricas por classe e a taxa de aceite perigoso. O limiar de confiança é aplicado pelos apps. Abaixo dele, o resultado obrigatório é `UNKNOWN`.

Um LLM local não faz parte do MVP atual. Antes de considerar Qwen ou equivalente, o time deve medir no Galaxy A17 a RAM de pico, latência, consumo e convivência com DAT, câmera e áudio.
