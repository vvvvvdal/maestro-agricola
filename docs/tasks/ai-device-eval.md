# Paridade e avaliação da IA local

Branch: `feat/ai-device-eval`

## Objetivo

Evitar divergência silenciosa entre o classificador de referência em Python e o adaptador local Kotlin. A medição física de latência e memória permanece separada porque depende do emulador ou Motorola.

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

## Fora do escopo desta etapa

- Benchmark de bateria ou qualidade de STT.
- Inferência sobre áudio bruto; o classificador recebe somente texto transcrito.

## Resultado em 18 de agosto de 2026

- `shared/ai/parity_cases.json` fixa 13 casos e o SHA-256 do modelo canônico.
- `python3 tools/export_intent_parity.py --check` passou, incluindo duas recusas por confiança abaixo de 0,40 e um caso sem vocabulário conhecido.
- O verificador aceita apenas ruído de ponto flutuante dentro da tolerância declarada; mudanças semânticas, estruturais ou numéricas relevantes continuam falhando.
- Seis testes Python específicos cobrem conteúdo atualizado, IDs únicos, tolerância numérica e rejeição de alterações relevantes.
- O Android agora possui testes que leem exatamente o mesmo fixture, verificam o SHA-256 do modelo e comparam rótulo e confiança usando o limiar compartilhado.
- Em 18 de agosto, os testes Kotlin ainda não haviam sido executados porque o Android SDK não estava configurado; essa lacuna foi encerrada pela validação de 19 de agosto descrita abaixo.
- Nenhuma dependência, credencial ou chamada de rede foi adicionada.

### Continuação da validação em 18 de agosto de 2026

- O verificador do treino passou a tolerar somente ruído de ponto flutuante de até `1e-12`; alterações estruturais ou numéricas relevantes continuam reprovando o artefato.
- `tools/export_intent_parity.py --check` aprovou os 13 casos e o modelo `4ff906a157c8`.
- Nove testes específicos de modelo, fixture e tolerância passaram; os 14 testes do bridge também permaneceram verdes.
- A suíte global não foi declarada aprovada neste host porque a dependência de desenvolvimento `websockets`, já listada em `tools/requirements-dev.txt`, não está instalada.
- O preflight Android confirmou JDK 21 e Gradle wrapper, mas não encontrou Android SDK. Benchmark de emulador/Motorola e teste Gradle permanecem como handoff explícito.

### Validação Android em 19 de agosto de 2026

- O preflight aprovou JDK 21, Android SDK, Platform API 36 e Gradle wrapper.
- A primeira resolução Android detectou que OkHttp 5.5.0 exige `compileSdk 37`, incompatível com o AGP 8.11.1 e o `compileSdk 36` congelados pelo projeto.
- O artefato oficial OkHttp 5.4.0 declara `minCompileSdk=36`; a versão foi fixada em 5.4.0 sem adicionar dependências ou alterar a interface `CommandTransport`.
- `./gradlew testMockDebugUnitTest assembleMockDebug` passou com oito testes Kotlin, incluindo os 13 casos compartilhados de paridade.
- O APK `app-mock-debug.apk` foi gerado com 12 MB e, após incluir o coletor mock, SHA-256 `9746ed29133a424d96850fe7e8d961b573ceeb7a992f7f2a1216db2da36788ee`.
- O APK foi instalado no Motorola Edge 40 Neo com Android 15/API 35 e ABI ARM64.
- O benchmark isolado do flavor mock executou 13 casos, com cinco aquecimentos e 30 medições por caso: 390 inferências medidas, zero divergências, mediana de 446 µs, p95 de 675 µs e máximo de 883 µs.
- O pico de heap observado foi 13.256.176 bytes. A medição usa somente o fixture versionado, sem áudio, transcrição de usuário, rede ou comando ao robô.
- A evidência estruturada está em `shared/ai/device_evaluation.json`. AI-03 concluída.

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

Em uma nova coleta, executar pelo menos 30 inferências no aparelho físico do MVP, relatando mediana e p95 de latência, pico aproximado de memória, versão do sistema e qualquer divergência de rótulo. Não usar um novo benchmark como afirmação no pitch antes da medição real.

O emulador foi dispensado porque o host de 8 GB não o executou com estabilidade. A evidência final foi coletada no aparelho físico do MVP, que representa o ambiente relevante da demonstração.

Para repetir a medição no flavor mock:

```bash
adb logcat -c
adb shell am start -n \
  br.org.agroturtles.maestro.mock/br.org.agroturtles.maestro.benchmark.IntentBenchmarkActivity
adb logcat -d -s MaestroAIBenchmark:I '*:S'
```
