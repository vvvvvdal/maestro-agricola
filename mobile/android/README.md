# Android/Kotlin

O projeto possui dois flavors:

- `mockDebug`: API 26+, usa uma fonte simulada e permite testar a jornada em aparelhos antigos.
- `datDebug`: API 31+, inclui o Meta Wearables DAT 0.9.0 para integração com os óculos.

O sample oficial atual do DAT usa `minSdk = 31`. Portanto, um Motorola abaixo do Android 12 pode executar o flavor `mock`, mas não pode parear os óculos pelo DAT.

Antes do build `datDebug`, defina `GITHUB_TOKEN` com permissão `read:packages` ou `github_token` em `local.properties`. Nunca versione o token.

## Preflight do mock

Confirme a toolchain antes de iniciar downloads ou builds longos:

```bash
python3 mobile/android/tools/preflight.py
```

O preflight exige JDK 17, Android SDK, Platform API 36 e Gradle wrapper. Para também verificar se o Motorola aparece como autorizado no `adb`:

```bash
python3 mobile/android/tools/preflight.py --require-device
```

Somente depois dos itens `[OK]` execute:

```bash
./gradlew :app:testMockDebugUnitTest
./gradlew :app:assembleMockDebug
./gradlew :app:assembleDatDebug
```

O modelo local é lido diretamente de `../../shared/ai/intent_model.json` como asset, sem cópia manual.

No emulador, o endpoint padrão é `ws://10.0.2.2:18765`. No Motorola físico, edite o campo do app para `ws://IP_DO_COMPUTADOR:18765`.

Gerar o APK não comprova voz, TTS nem conexão com o bridge. Esses três itens devem ser executados no Motorola e registrados separadamente.
