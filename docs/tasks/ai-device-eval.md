# Paridade e avaliação da IA local

Branch: `feat/ai-device-eval`

## Objetivo

Evitar divergência silenciosa entre o classificador de referência em Python e os adaptadores locais Kotlin e Swift. A medição física de latência e memória permanece separada porque depende do Motorola e do iPhone 13.

## Critérios de aceite desta etapa

- Um fixture versionado fixa textos, rótulos finais após o limiar de 0,40 e confiança esperada.
- Python verifica que o fixture corresponde ao modelo JSON atual.
- Os testes Kotlin e Swift consomem o mesmo fixture, sem listas duplicadas de frases.
- Casos incluem acentos, caixa alta, cada intenção operacional, baixa confiança e vocabulário ausente.
- Nenhum áudio, texto de usuário ou telemetria é enviado para serviços externos.

## Plano

1. Gerar o fixture a partir do modelo canônico, com hash do arquivo e expectativas semânticas explícitas.
2. Adicionar um modo `--check` que falha se modelo e fixture divergirem.
3. Fazer os testes nativos lerem o mesmo recurso compartilhado e comparar rótulo e confiança com tolerância numérica.
4. Executar a referência Python nesta máquina.
5. Documentar, sem mascarar, que os testes Kotlin/Swift só ficam comprovados quando executados nas toolchains nativas.

## Não concluído por esta etapa

- Benchmark de latência, memória, bateria ou qualidade de STT nos aparelhos.
- Build do APK ou do projeto Xcode.
- Inferência sobre áudio bruto; o classificador recebe somente texto transcrito.
