# Android/Kotlin

O projeto possui dois flavors:

- `mockDebug`: API 26+, usa uma fonte simulada para desenvolvimento e testes automatizados.
- `datDebug`: API 31+, inclui o Meta Wearables DAT 0.9.0 para integração com os óculos.

O sample oficial atual do DAT usa `minSdk = 31`. A demonstração exige um Android compatível com esse nível e com o ciclo oficial de pareamento do DAT.

Antes do build `datDebug`, defina `GITHUB_TOKEN` com permissão `read:packages` ou `github_token` em `local.properties`. Nunca versione o token.

## Preflight do mock

Confirme a toolchain antes de iniciar downloads ou builds longos:

```bash
python3 mobile/android/tools/preflight.py
```

O preflight exige JDK 17, Android SDK, Platform API 36 e Gradle wrapper. Para também verificar se o Android físico da demonstração aparece como autorizado no `adb`:

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

No emulador de desenvolvimento, o endpoint padrão é `ws://10.0.2.2:18765`. No Android físico da demonstração, edite o campo do app para `ws://IP_DO_COMPUTADOR:18765`.

Gerar o APK não comprova câmera dos óculos, voz, TTS nem conexão com o bridge. Esses itens devem ser executados com `datDebug` no Android conectado aos Meta Wearables e registrados separadamente.
