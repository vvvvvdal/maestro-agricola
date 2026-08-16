# Aplicativo iOS/Swift

Aplicativo nativo para iPhone 13, com o mesmo modelo de intenção e o mesmo contrato JSON do Android.

## Requisitos

- macOS e Xcode 26.4 ou superior;
- iOS 17.2 ou superior no iPhone;
- Swift 6.3;
- XcodeGen 2.44.1 ou superior;
- Developer Mode ativo no Meta AI para testar o DAT.

## Gerar e abrir o projeto

```bash
cd mobile/ios
xcodegen generate
open MaestroAgricola.xcodeproj
```

Escolha a equipe de assinatura no Xcode. Para usar credenciais fora do Developer Mode, preencha `META_APP_ID` e `CLIENT_TOKEN` em uma configuração local, nunca no Git.

O fluxo executável da semana usa `MockFrameSource`, voz local do iOS, IA local e WebSocket. `DatFrameSource` é a fronteira reservada para ligar o ciclo de sessão/captura do sample oficial `CameraAccess` no hardware.

