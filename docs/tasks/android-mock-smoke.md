# Android mock smoke

Branch: `feat/android-mock-smoke`

## Objetivo

Reduzir o tempo perdido antes do primeiro build Kotlin, sem declarar como testado o que depende do Motorola, do Android SDK ou do DAT real.

## Plano executado

1. Verificar a toolchain disponível antes de iniciar o Gradle.
2. Automatizar os mesmos checks de forma reproduzível.
3. Testar a lógica do diagnóstico sem depender do Android SDK.
4. Documentar o próximo passo no computador do Átila.

## Resultado em 18 de agosto de 2026

- `mobile/android/tools/preflight.py` verifica JDK 17+, Android SDK, Platform API 36 e Gradle wrapper.
- A opção `--require-device` também exige um aparelho autorizado no `adb`.
- Três testes unitários validam versões Java, `local.properties` e estados do `adb`.
- Nesta máquina, o preflight falha corretamente porque JDK e Android SDK não estão instalados; portanto, nenhum build Android foi declarado como aprovado.
- Nenhuma dependência ou credencial foi adicionada.

## Entrega para o responsável mobile

No computador com Android Studio instalado:

```bash
python3 mobile/android/tools/preflight.py --require-device
cd mobile/android
./gradlew testMockDebugUnitTest assembleMockDebug
```

Depois, instalar `app/build/outputs/apk/mock/debug/app-mock-debug.apk` no Motorola e registrar separadamente: voz, TTS e conexão WebSocket com o bridge. O build do APK sozinho não comprova esses três critérios.
