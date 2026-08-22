# Testes Android

Os testes Kotlin permanecem em
`mobile/android/app/src/test/java/br/org/agroturtles/maestro`, divididos pelos
pacotes `domain`, `platform` e `ui`. Esse é o source set padrão do Android
Gradle Plugin e deve continuar sendo a fonte canônica.

```bash
cd mobile/android

# flavor sem dependência do DAT
./gradlew :app:testMockDebugUnitTest --no-daemon

# compatibilidade do flavor DAT; exige acesso ao GitHub Packages
GITHUB_TOKEN=<token-read-packages> \
  ./gradlew :app:testDatDebugUnitTest --no-daemon
```

Testes que precisarem de runtime Android devem ser adicionados em
`mobile/android/app/src/androidTest`, não nesta pasta de índice.
