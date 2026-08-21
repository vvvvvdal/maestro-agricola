# Android/Kotlin

O projeto possui dois flavors:

- `mockDebug`: API 26+, usa uma fonte simulada para desenvolvimento e testes automatizados.
- `datDebug`: API 31+, inclui o Meta Wearables DAT 0.9.0 para integração com os óculos.

O sample oficial atual do DAT usa `minSdk = 31`. A demonstração exige um Android compatível com esse nível e com o ciclo oficial de pareamento do DAT.

Antes do build `datDebug`, defina `GITHUB_TOKEN` com permissão `read:packages` ou `github_token` em `local.properties`. Nunca versione o token.

Essa autenticação é usada somente pelo Gradle para baixar os AARs do GitHub
Packages. Em 21 de agosto de 2026, o build sem credencial neste host retornou
HTTP `401 Unauthorized` para os três pacotes DAT 0.9.0. O token não entra no
APK e não é uma credencial dos óculos.

Cada integrante que for compilar `datDebug` em uma máquina nova deve criar seu
próprio PAT clássico com somente `read:packages`; nunca compartilhe o token de
uma pessoa com o grupo. `mockDebug` não precisa dessa credencial. Um build pode
continuar funcionando sem token enquanto todos os AARs estiverem no cache do
Gradle, mas isso deixa de funcionar em uma máquina nova, após invalidação do
cache ou ao atualizar o DAT.

Para remover a credencial local, apague somente a linha `github_token=...` de
`local.properties`. Isso não revoga o token no GitHub. Se ele não for mais
usado, exclua também o PAT em **GitHub → Settings → Developer settings →
Personal access tokens → Tokens (classic)**.

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

## DAT antes dos óculos

O modo real continua sendo o padrão do flavor `dat`. Para criar explicitamente
um APK de desenvolvimento que usa as APIs DAT com o MockDeviceKit oficial:

```bash
./gradlew -PmaestroDatMockDevice=true :app:assembleDatDebug
```

Esse APK mostra `câmera: dat-mockdevice:success` na interface. Sem a propriedade,
mostra `câmera: dat` e nunca ativa o dispositivo simulado. Não use um build
`dat-mockdevice` como evidência de câmera física.

Os cenários de falha são selecionados sem alterar o código:

```bash
./gradlew -PmaestroDatMockDevice=true -PmaestroDatMockScenario=permission-denied :app:assembleDatDebug
./gradlew -PmaestroDatMockDevice=true -PmaestroDatMockScenario=timeout :app:assembleDatDebug
./gradlew -PmaestroDatMockDevice=true -PmaestroDatMockScenario=disconnect :app:assembleDatDebug
```

Os únicos valores aceitos são `success`, `permission-denied`, `timeout` e
`disconnect`. O cenário aparece após `dat-mockdevice:` na interface para que a
evidência seja identificável.

O MockDeviceKit usa a câmera do Android apenas para manter o stream simulado
ativo e devolve, em `capturePhoto()`, a fixture versionada `plot-03.png` por um
provider interno não exportado. A fixture é transmitida por pipe, não copiada
para o armazenamento do app.

A foto é decodificada localmente por `com.google.zxing:core:3.5.4`, dependência
aprovada em 21 de agosto de 2026. O app aceita apenas um QR central cujo ID
exista em `targets.json`; imagem vazia, marcador desconhecido ou ambiguidade
encerram a operação sem criar comando.

O plano, critérios e gate físico estão em
[`../../docs/tasks/dat-prehardware.md`](../../docs/tasks/dat-prehardware.md).

O modelo local é lido diretamente de `../../shared/ai/intent_model.json` como asset, sem cópia manual.

No emulador de desenvolvimento, o endpoint padrão é `ws://10.0.2.2:18765`. No Android físico da demonstração, edite o campo do app para `ws://IP_DO_COMPUTADOR:18765`.

Gerar o APK não comprova câmera dos óculos, voz, TTS nem conexão com o bridge. Esses itens devem ser executados com `datDebug` no Android conectado aos Meta Wearables e registrados separadamente.

O roteiro completo para o Galaxy A17, incluindo JDK portátil, USB/ADB, mock físico, DAT e diagnóstico por camada, está em [`../../docs/testing/galaxy-a17-e2e.md`](../../docs/testing/galaxy-a17-e2e.md).
