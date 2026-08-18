# Detecção do QR em imagem estática

Branch: `feat/vision-qr`

## Objetivo

Concluir a prova isolada VIS-02 antes de acoplar visão aos apps: transformar uma imagem em uma decisão explícita e segura sobre o alvo, sem inventar coordenadas ou aceitar um QR desconhecido.

## Critérios de aceite

- A textura versionada do cenário retorna `DETECTED` e `target_id = plot-03`.
- Uma imagem sem QR retorna `UNKNOWN` e nenhum `target_id`.
- Um QR fora de `targets.json` retorna `UNKNOWN`.
- Mais de um QR na região central retorna `AMBIGUOUS`.
- O resultado inclui `schema_version`, estado, confiança operacional e timestamps em UTC.
- Nenhuma imagem é persistida pelo detector e nenhuma dependência do projeto é adicionada sem aprovação.

## Plano

1. Usar o `QRCodeDetector` do OpenCV como prova de bancada, com importação opcional e erro claro quando indisponível.
2. Tratar `targets.json` como allowlist e fonte de verdade dos IDs aceitos.
3. Separar decodificação, regra de seleção e serialização para permitir testes unitários.
4. Validar alvo conhecido, imagem vazia, alvo desconhecido e ambiguidade.
5. Só então marcar VIS-02 como concluída; VIS-03 continuará aberta até um frame do app usar o adaptador.

## Fora de escopo desta task

- Integrar o detector ao Kotlin, Swift ou DAT.
- Estimar pose ou coordenada a partir da câmera.
- Instalar OpenCV automaticamente ou persistir frames de câmera.
