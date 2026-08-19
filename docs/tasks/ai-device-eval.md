# Paridade e avaliação da IA local

Branch: `feat/ai-device-eval`

## Objetivo

Evitar divergência silenciosa entre o classificador de referência em Python e o adaptador local Kotlin. A medição física de latência e memória permanece separada porque depende do Android que executará `datDebug` com os Meta Wearables.

## Critérios de aceite desta etapa

- Um fixture versionado fixa textos, rótulos finais após o limiar de 0,40 e confiança esperada.
- Python verifica que o fixture corresponde ao modelo JSON atual.
- Os testes Kotlin consomem o mesmo fixture, sem listas duplicadas de frases.
- Casos incluem acentos, caixa alta, cada intenção operacional, baixa confiança e vocabulário ausente.
- Nenhum áudio, texto de usuário ou telemetria é enviado para serviços externos.

## Plano

1. Gerar o fixture a partir do modelo canônico, com hash do arquivo e expectativas semânticas explícitas.
2. Adicionar um modo `--check` que falha se modelo e fixture divergirem.
3. Fazer os testes nativos lerem o mesmo recurso compartilhado e comparar rótulo e confiança com tolerância numérica.
4. Executar a referência Python nesta máquina.
5. Documentar, sem mascarar, que os testes Kotlin só ficam comprovados quando executados na toolchain Android.

## Não concluído por esta etapa

- Benchmark de latência, memória, bateria ou qualidade de STT nos aparelhos.
- Build do APK.
- Inferência sobre áudio bruto; o classificador recebe somente texto transcrito.

## Resultado em 18 de agosto de 2026

- `shared/ai/parity_cases.json` fixa 11 casos e o SHA-256 do modelo canônico.
- `python3 tools/export_intent_parity.py --check` passou, incluindo duas recusas por confiança abaixo de 0,40.
- Dois testes Python passaram: conteúdo atualizado e IDs únicos.
- O Android agora possui testes que leem exatamente o mesmo fixture e comparam rótulo e confiança.
- Os testes Kotlin não foram executados nesta máquina: não há JDK/Android SDK. AI-03 permanece em andamento até essa evidência existir.
- Nenhuma dependência, credencial ou chamada de rede foi adicionada.

## Handoff para Rafael e Átila

Referência e integridade do fixture:

```bash
python3 tools/export_intent_parity.py --check
python3 -m unittest tests/test_intent_parity.py
```

Android, em uma máquina com a toolchain pronta:

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest
```

Depois dos testes, registrar no Android físico da demonstração pelo menos 30 inferências, relatando mediana e p95 de latência, pico aproximado de memória, versão do sistema e qualquer divergência de rótulo. Não usar esse benchmark como afirmação no pitch antes da medição real com `datDebug` e os Meta Wearables.
