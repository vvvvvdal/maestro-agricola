# DAT pré-hardware — sessão, câmera e alvo com MockDeviceKit

Status: `APROVADO NO MOCKDEVICEKIT` em 21 de agosto de 2026.

## Objetivo

Integrar o Meta Wearables Device Access Toolkit (DAT) 0.9.0 ao flavor Android
`datDebug` antes da disponibilidade dos óculos, exercitando com o MockDeviceKit o
mesmo ciclo de sessão e câmera que será usado no hardware real.

O corte termina quando uma foto fornecida pelo MockDeviceKit é processada apenas
em memória e produz um `target_id` conhecido. Essa evidência não comprova
pareamento, câmera, firmware, áudio, latência, bateria ou estabilidade dos Meta
Wearables físicos.

## Decisões e ambiguidades

- O DAT fornece sessão e câmera. Reconhecimento de fala e TTS continuam nas APIs
  nativas do Android.
- A versão fixada é `0.9.0`, confirmada no pacote e changelog oficiais em 21 de
  agosto de 2026.
- O ciclo de câmera usa a API 0.9.0: `DeviceSession.addCamera()`,
  `Camera.stream.start()` e `Stream.capturePhoto()`.
- A captura é sob demanda. Não há gravação de vídeo nem persistência de foto.
- O MockDeviceKit é uma dependência e um modo de desenvolvimento; ele não pode
  virar fallback silencioso no caminho de hardware.
- Os cenários `success`, `permission-denied`, `timeout` e `disconnect` são
  selecionados por propriedade de build e ficam visíveis na interface.
- `mockDebug` permanece como contingência independente e não depende do SDK
  Meta.
- O detector aceita somente IDs presentes no catálogo canônico `targets.json`.
  Ausência, valor desconhecido ou mais de um alvo falham de forma segura.
- A dependência `com.google.zxing:core:3.5.4` foi aprovada pelo responsável em
  21 de agosto de 2026. Ela é usada somente no flavor `dat` para decodificar QR
  localmente e em memória.
- Leitores de QR não fornecem necessariamente uma probabilidade calibrada. O
  MVP registra estado, `target_id` e instante da observação, sem inventar um
  valor de confiança.
- A autenticação no GitHub Packages é uma necessidade de build, não uma
  credencial do aplicativo. Um token clássico com `read:packages` fica somente
  no ambiente ou em `local.properties`, nunca no repositório ou APK.

## Implementação entregue

| Componente | O que foi implementado |
|---|---|
| `app/build.gradle.kts` | Configuração opt-in do MockDeviceKit e seleção dos cenários `success`, `permission-denied`, `timeout` e `disconnect` por propriedades Gradle. |
| `src/dat/.../PlatformFrameSource.kt` | Permissões Android, inicialização do DAT, registro real, seleção de dispositivo, `DeviceSession`, `addCamera()`, stream, captura, timeout, cancelamento e liberação de recursos. |
| `src/dat/.../DatMockAssetProvider.kt` | Provider interno e não exportado que transmite a fixture `plot-03.png` por pipe, sem criar arquivo de mídia no sandbox. |
| `src/dat/.../ZxingPhotoQrDecoder.kt` | Conversão de `PhotoData.Bitmap` ou HEIC, limite de dimensão, tentativas de rotação e leitura local de QR com ZXing. |
| `src/main/.../QrPayloadPolicy.kt` | Normalização de `plot-XX`, filtro da região central, allowlist de `targets.json` e recusa de ausência, desconhecido ou ambiguidade. |
| `FrameSource`, `MainActivity` e `InteractionEngine` | Observação estruturada do alvo, API assíncrona, cancelamento no reset, encerramento no ciclo da Activity e falha visual fail-closed. |
| Manifestos Android | Deep link de registro DAT, permissão de câmera do ensaio e opt-out de analytics/crash reporting opcionais do SDK. |
| Testes e documentação | Testes do QR, centralidade, allowlist e falha segura; roteiro de build, privacidade, arquitetura e gate posterior em hardware. |

O SDK permanece confinado ao source set `dat`; tipos da Meta não escapam para
a máquina de estados nem para o contrato ROS. O flavor `mock` continua
independente dos AARs do DAT.

## Fluxo implementado em runtime

```text
toque em "Olhar para o alvo"
 -> permissões Android
 -> Wearables.initialize()
 -> registro real ou MockDeviceKit explicitamente habilitado
 -> AutoDeviceSelector
 -> DeviceSession.start()
 -> DeviceSession.addCamera()
 -> Camera.stream.start()
 -> Stream.capturePhoto()
 -> ZXing em memória
 -> QR central + ID permitido em targets.json
 -> TargetObservation(target_id, observed_at)
 -> InteractionEngine
```

Qualquer recusa, timeout, erro de sessão, erro de stream, imagem ilegível,
marcador desconhecido ou ambiguidade limpa o contexto visual e termina sem
produzir comando. A confirmação explícita por áudio continua obrigatória nas
etapas posteriores.

## Credencial de build para a equipe

- `mockDebug` não usa GitHub Packages e não precisa de token.
- Cada integrante que baixar ou recompilar `datDebug` em sua máquina deve usar
  o próprio PAT clássico, com somente `read:packages`. O token de outro membro
  não deve ser compartilhado.
- Os AARs podem continuar funcionando temporariamente sem token quando já estão
  no cache local do Gradle. Isso não é uma configuração reproduzível: uma
  máquina nova, limpeza/invalidação do cache ou nova versão do DAT exigirá a
  autenticação novamente.
- Remover `github_token=...` de `local.properties` tira a credencial desta cópia
  do projeto, mas não revoga o token. Para inutilizá-lo definitivamente, ele
  também deve ser excluído em GitHub → Settings → Developer settings →
  Personal access tokens → Tokens (classic).
- Se o token for mantido durante o desenvolvimento, deve ter expiração curta,
  escopo mínimo e permanecer somente em `local.properties` ignorado pelo Git ou
  na variável de ambiente `GITHUB_TOKEN`.

## Critérios de aceite pré-hardware

- [x] O sample oficial `CameraAccess` da release 0.9.0 é compilado e executado
  com MockDeviceKit.
- [x] `datDebug` compila e instala sem segredos versionados.
- [x] Permissões Android são concedidas antes de `Wearables.initialize()`.
- [x] Sessão, câmera e stream tratam seus estados e erros separadamente.
- [x] Uma captura do MockDeviceKit produz um alvo conhecido pelo detector.
- [x] Frame inválido, alvo desconhecido, ambiguidade, permissão recusada,
  timeout e desconexão não produzem alvo nem comando.
- [x] A mídia permanece somente em memória e não aparece em logs.
- [x] Câmera, stream e sessão são encerrados em reset, saída e falha terminal.
- [x] Nenhum movimento é enviado sem confirmação explícita por áudio.
- [x] Testes e build de `mockDebug` continuam passando.
- [x] Documentação e pitch identificam a validação como MockDeviceKit, não como
  hardware real.

## Plano de implementação

1. Executar o build `datDebug` sem token e registrar objetivamente se o GitHub
   Packages exige autenticação neste host.
2. Executar o sample oficial `CameraAccess` 0.9.0 fora do repositório do
   Maestro, usando o MockDeviceKit.
3. Isolar o SDK atrás de uma fonte pequena que entrega somente uma observação
   estruturada de alvo ao restante do app.
4. Solicitar permissões Android, inicializar o DAT, observar registro e criar a
   sessão apenas quando houver dispositivo elegível.
5. Adicionar câmera, iniciar o stream, capturar uma foto sob demanda e encerrar
   os recursos em ordem segura.
6. Decodificar QR localmente com ZXing e validar o ID contra `targets.json`.
7. Exercitar o adaptador com MockDeviceKit e mídia versionada de `plot-03`.
8. Testar sucesso, recusa, ambiguidade, timeout, permissão e desconexão.
9. Comparar código, testes e esta spec; registrar evidência sanitizada.

## Evidências previstas

- hash/commit da release oficial usada como referência;
- saída de `assembleDatDebug` e `assembleMockDebug`;
- testes unitários do detector e do mapeamento de erros;
- execução do CameraAccess e do Maestro com MockDeviceKit;
- registro de estados e resultados sem bytes de imagem ou transcrição;
- revisão de armazenamento confirmando ausência de mídia criada pelo Maestro.

## Gate posterior em hardware

O status físico permanece `BLOCKED — aguardando óculos` até que o sample
oficial e depois o Maestro sejam executados no mesmo smartphone e nos mesmos
Meta Wearables do evento. Esse gate inclui pareamento, câmera real, câmera e
ASR simultâneos, rota de TTS, firmware, desconexão, latência, memória, bateria e
o E2E Android → WebSocket → ROS 2 → Gazebo.

## Evidências de 21 de agosto de 2026

- Fonte oficial consultada: commit
  `81dfb51b9be26de5cd262bb1dcbb4b8d0d6bd2bc` (`Release 0.9.0`) do repositório
  `facebook/meta-wearables-dat-android`.
- `:app:assembleDatDebug` sem credencial falhou antes da compilação com HTTP
  `401 Unauthorized` ao resolver `mwdat-core`, `mwdat-camera` e
  `mwdat-mockdevice` 0.9.0.
- A falha confirma que este host precisa de `GITHUB_TOKEN` ou `github_token`
  com `read:packages`. Ela não é defeito no código do produto.
- Com a credencial somente local, `:app:assembleDatDebug` resolveu os AARs e
  compilou 37 tarefas com JDK 21. Nenhum valor da credencial foi registrado na
  saída ou adicionado ao Git.
- O `CameraAccess` oficial foi compilado, instalado e executado sem alteração
  do sample. O MockDeviceKit emparelhou um Ray-Ban Meta simulado, iniciou a
  sessão, alcançou `Stream: streaming` e retornou `Captured photo`.
- O teste Espresso do sample não inicia na imagem Android 16/API 36.1 por
  `NoSuchMethodException: android.hardware.input.InputManager.getInstance`.
  Essa incompatibilidade do runner foi contornada por execução manual do mesmo
  fluxo; o código oficial não foi modificado.
- No Maestro, o cenário `success` identificou `plot-03` a partir da foto
  simulada. `permission-denied`, `timeout` e `disconnect` recusaram a operação
  sem alvo e sem comando aceito.
- A fixture versionada é lida do APK por um `ContentProvider` não exportado e
  entregue por pipe. A inspeção do sandbox após a captura encontrou
  `NO_PERSISTED_MEDIA_FILES`.
- Testes focados de ZXing, política de QR e máquina de estados passaram. O gate
  final registrou 42 testes em `testDatDebugUnitTest` e 42 testes em
  `testMockDebugUnitTest`, todos sem falhas. `assembleDatDebug` e
  `assembleMockDebug` também passaram.
- Nenhum óculos real foi usado.

## Comparação atual entre spec, código e testes

- O adaptador `src/dat` implementa e compilou permissões antes da inicialização,
  sessão, `addCamera()`, stream, captura sob demanda, timeout e encerramento.
- O MockDeviceKit é opt-in e possui cenários reproduzíveis de sucesso, permissão
  recusada, timeout e desconexão; os quatro foram executados no emulador.
- A foto chega à fronteira `QrTargetDetector` sem arquivo intermediário. A
  política que aceita apenas um alvo cadastrado e o decodificador ZXing possuem
  testes e falham de forma segura.
- A falha visual limpa o contexto da máquina de estados, informa que nada foi
  enviado e possui teste unitário. O fluxo de confirmação e transporte não foi
  relaxado.
- `mockDebug` continua compilando e seus testes unitários passam. Nenhuma
  evidência pré-hardware é apresentada como validação dos óculos reais.
