# Modelo local de intenção

O artefato canônico é `intent_model.json`. Ele é treinado a partir de `dataset/intents.tsv` e executado localmente no app Android.

O MVP usa um classificador linear softmax sobre unigramas, bigramas e afixos de palavras. Essa escolha é intencional:

- inferência pequena e rápida em aparelhos antigos;
- nenhuma chamada de rede;
- o modelo pode ser interpretado em Kotlin sem runtime externo;
- probabilidades e vocabulário podem ser auditados;
- o classificador é comprovável como IA treinada, enquanto regras determinísticas apenas validam segurança.

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

O limiar de confiança é aplicado pelos apps. Abaixo dele, o resultado obrigatório é `UNKNOWN`.
