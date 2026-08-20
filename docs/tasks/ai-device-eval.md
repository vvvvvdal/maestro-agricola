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

## Fora do benchmark local

- Bateria e qualidade de STT no aparelho.
- Execução com `datDebug` e os Meta Wearables.
- Inferência sobre áudio bruto; o classificador recebe somente texto transcrito.

## Resultado em 18 de agosto de 2026

- `shared/ai/parity_cases.json` fixa 11 casos e o SHA-256 do modelo canônico.
- `python3 tools/export_intent_parity.py --check` passou, incluindo duas recusas por confiança abaixo de 0,40.
- Dois testes Python passaram: conteúdo atualizado e IDs únicos.
- O Android agora possui testes que leem exatamente o mesmo fixture e comparam rótulo e confiança.
- Os testes Kotlin não foram executados nesta máquina: não há JDK/Android SDK. AI-03 permanece em andamento até essa evidência existir.
- Nenhuma dependência, credencial ou chamada de rede foi adicionada.

## Renovação do modelo v2 em 19 de agosto de 2026

- APK `mockDebug`: SHA-256 `6b90e172eba847bf83790cebc7af22afdc782f749d1e3d8ce6a77a9fea5f7e8b`.
- Modelo canônico: SHA-256 `4932a89ac74e82cc41b96936f41e49f439b4b0a998199f06c9434e8e9180c0fd`.
- Motorola Edge 40 Neo, Android 15/API 35, ARM64.
- 18 casos, 30 iterações medidas por caso e 540 inferências no total.
- Zero divergências; mediana 229 µs, p95 1.013 µs e máxima 1.178 µs.
- Pico aproximado de heap observado: 19.254.032 bytes.
- Fixture fixa, sem áudio, transcrição de usuário, rede ou comando ao robô.

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

Se o APK ou o modelo mudar após o congelamento de features, repetir a coleta física antes da entrega. O benchmark local pode ser afirmado com seu escopo exato, mas não deve ser apresentado como validação de STT, `datDebug` ou Meta Wearables.
