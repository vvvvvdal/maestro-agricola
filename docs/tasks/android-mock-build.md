# Task: primeiro build Android mock

## Resultado em 19 de agosto de 2026

- O JDK 25 embutido no Android Studio foi corretamente identificado como incompatível com o Gradle 8.14.1 do projeto.
- O build foi repetido com o JDK 21 já instalado em `~/.jdks/jbr-21.0.11`.
- OkHttp foi fixado em `4.12.0`, compatível com `compileSdk 36`; a versão `5.5.0` exigia API 37, acima do máximo recomendado pelo Android Gradle Plugin atual.
- `:app:testMockDebugUnitTest` e `:app:assembleMockDebug` foram aprovados.
- O APK foi gerado em `mobile/android/app/build/outputs/apk/mock/debug/app-mock-debug.apk` com aproximadamente 12 MB.
- O aviso de construção obsoleta de `Locale` no TTS foi removido com `Locale.forLanguageTag("pt-BR")`.

## Limite da evidência

Esse build comprova a base Kotlin, a IA compartilhada e o flavor mock. Não comprova captura DAT, óculos reais, rota Bluetooth ou comportamento no Galaxy A17; esses gates permanecem no roteiro físico.
