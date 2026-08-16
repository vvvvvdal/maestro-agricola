# Android/Kotlin

O projeto possui dois flavors:

- `mockDebug`: API 26+, usa uma fonte simulada e permite testar a jornada em aparelhos antigos.
- `datDebug`: API 31+, inclui o Meta Wearables DAT 0.9.0 para integração com os óculos.

O sample oficial atual do DAT usa `minSdk = 31`. Portanto, um Motorola abaixo do Android 12 pode executar o flavor `mock`, mas não pode parear os óculos pelo DAT.

Antes do build `datDebug`, defina `GITHUB_TOKEN` com permissão `read:packages` ou `github_token` em `local.properties`. Nunca versione o token.

```bash
./gradlew :app:testMockDebugUnitTest
./gradlew :app:assembleMockDebug
./gradlew :app:assembleDatDebug
```

O modelo local é lido diretamente de `../../shared/ai/intent_model.json` como asset, sem cópia manual.

No emulador, o endpoint padrão é `ws://10.0.2.2:18765`. No Motorola físico, edite o campo do app para `ws://IP_DO_COMPUTADOR:18765`.
