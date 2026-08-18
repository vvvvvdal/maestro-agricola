# iOS mock smoke

Branch: `feat/ios-mock-smoke`

## Objetivo

Preparar uma passagem reproduzível do projeto Swift para o Mac e o iPhone 13, sem confundir inspeção estática em Linux com build ou teste real de iOS.

## Critérios de aceite desta etapa

- Um preflight informa claramente se macOS, Xcode, Swift, XcodeGen, projeto e modelo local estão prontos.
- A lógica do preflight possui testes que não exigem Xcode.
- O README separa teste de simulador de voz, TTS, Bluetooth e assinatura no iPhone físico.
- Nenhuma credencial, pacote ou dependência nova é adicionada.

## Plano

1. Automatizar checks da toolchain declarada pelo projeto.
2. Falhar cedo e explicar o próximo passo, sem iniciar downloads ou resolver pacotes silenciosamente.
3. Testar parsers de versão e validação dos recursos locais.
4. Documentar os comandos de geração, teste e execução física.
5. Manter IOS-01 aberta até o app ser realmente compilado e executado no iPhone 13.

## Fora de escopo desta máquina

- Gerar o `.xcodeproj` ou compilar Swift, pois o host não é macOS e não possui Xcode.
- Validar reconhecimento de voz, TTS, rota Bluetooth ou DAT real.
- Configurar equipe de assinatura ou credenciais Meta.

## Resultado em 18 de agosto de 2026

- `mobile/ios/tools/preflight.py` verifica macOS, Xcode 26.4+, Swift 6.3+, XcodeGen 2.44.1+, arquivos do projeto e referência ao modelo local.
- Três testes passaram cobrindo versões, comparação de mínimos e presença dos recursos.
- Nesta máquina, os quatro itens de toolchain falham corretamente; projeto, `Info.plist` e modelo estão presentes. Nenhum build iOS foi declarado como aprovado.
- O README agora separa o teste de simulador da prova física de voz, TTS, Bluetooth, assinatura e DAT.
- Nenhuma dependência ou credencial foi adicionada.

## Handoff para o Mac

```bash
python3 mobile/ios/tools/preflight.py
cd mobile/ios
xcodegen generate
xcodebuild test -project MaestroAgricola.xcodeproj -scheme MaestroAgricola -destination 'platform=iOS Simulator,name=iPhone 13'
open MaestroAgricola.xcodeproj
```

Depois, selecionar o iPhone 13 físico, configurar a equipe de assinatura localmente e executar o app. IOS-01 só deve ser marcada como concluída após essa execução e o registro separado de voz, TTS e conexão WebSocket.
