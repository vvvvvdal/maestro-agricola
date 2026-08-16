# Referências

## Fontes oficiais

- [Meta Wearables Developer Center — Getting Started](https://wearables.developer.meta.com/docs/develop/dat/getting-started-toolkit)
- [Meta Wearables DAT Android](https://github.com/facebook/meta-wearables-dat-android)
- [Sample Android CameraAccess](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/CameraAccess)
- [Meta Wearables DAT iOS](https://github.com/facebook/meta-wearables-dat-ios)
- [Sample iOS CameraAccess](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples/CameraAccess)

O projeto mantém implementações nativas Kotlin e Swift. Os samples `CameraAccess` da mesma versão do DAT são a referência de ciclo de vida para cada plataforma.

Versão fixada nesta primeira implementação: DAT 0.9.0. O sample oficial consultado exige Android API 31+ no flavor real e iOS 17.2+ no iPhone.

## Processo de desenvolvimento

- [Fábio Akita — Vibe Code: Do Zero à Produção em 6 Dias](https://akitaonrails.com/2026/02/16/vibe-code-do-zero-a-producao-em-6-dias-the-m-akita-chronicles/)

Princípios adotados: especificação clara, tarefas pequenas, revisão humana, testes de regressão, integração contínua e releases pequenos.

## Materiais do programa

- Edital AI Glasses Brasil 2026.
- Unidade XII — Kotlin/Android, Edge AI, visão, voz e eficiência.
- Unidade XIII — DAT, arquitetura, câmera, áudio e Mock Device Kit.
- Unidade XIV — encerramento e próximos passos.
- Versão resumida e versão técnica do Maestro Agrícola, equipe AgroTurtles.

## Observações de versão

O DAT está em developer preview e muda com frequência. Antes de implementar:

1. confirmar a versão publicada no repositório oficial;
2. conferir requisitos atuais de Android Studio, JDK e Android SDK;
3. validar APIs contra o sample da mesma versão;
4. registrar a versão fixada no projeto.
