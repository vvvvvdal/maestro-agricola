# Aplicativo iOS/Swift

Aplicativo nativo para iPhone 13, com o mesmo modelo de intenção e o mesmo contrato JSON do Android.

## Requisitos

- macOS e Xcode 26.4 ou superior;
- iOS 17.2 ou superior no iPhone;
- Swift 6.3;
- XcodeGen 2.44.1 ou superior;
- Developer Mode ativo no Meta AI para testar o DAT.

## Gerar e abrir o projeto

Primeiro, confirme a toolchain e os recursos locais sem iniciar o build:

```bash
python3 mobile/ios/tools/preflight.py
```

Somente depois de todos os itens aparecerem como `[OK]`:

```bash
cd mobile/ios
xcodegen generate
xcodebuild test -project MaestroAgricola.xcodeproj -scheme MaestroAgricola \
  -destination 'platform=iOS Simulator,name=iPhone 13'
open MaestroAgricola.xcodeproj
```

Escolha a equipe de assinatura no Xcode. Para usar credenciais fora do Developer Mode, preencha `META_APP_ID` e `CLIENT_TOKEN` em uma configuração local, nunca no Git.

O fluxo executável da semana usa `MockFrameSource`, voz local do iOS, IA local e WebSocket. `DatFrameSource` é a fronteira reservada para ligar o ciclo de sessão/captura do sample oficial `CameraAccess` no hardware.

O simulador comprova testes unitários e fluxo visual, mas não comprova microfone, TTS, rota Bluetooth, assinatura nem DAT. Selecione o iPhone 13 físico no Xcode, execute o app e registre essas evidências separadamente. Nunca versione `META_APP_ID`, `CLIENT_TOKEN` ou dados de assinatura.
