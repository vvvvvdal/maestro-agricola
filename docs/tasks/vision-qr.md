# Detecção do QR em imagem estática

> **Atualização de 22/08/2026:** o handoff VIS-03 foi concluído no caminho pré-hardware. O `datDebug` recebe `PhotoData` da stack DAT 0.9.0, o `ZxingPhotoQrDecoder` processa a imagem somente em memória e o MockDeviceKit produz `plot-03` de forma repetível no Android físico. A câmera dos Meta Wearables reais continua como gate separado.

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

- Integrar o detector ao app Kotlin e ao frame fornecido pelo DAT.
- Estimar pose ou coordenada a partir da câmera.
- Instalar OpenCV automaticamente ou persistir frames de câmera.

## Resultado em 18 de agosto de 2026

- O comando `make vision-smoke` decodificou a textura versionada como `plot-03` e retornou `DETECTED`.
- Oito testes passaram cobrindo imagem versionada, imagem vazia, QR desconhecido, dois QRs, alvo periférico, timestamp e regras puras de seleção.
- `confidence = 1.0` significa somente "texto do QR decodificado e ID presente na allowlist"; não é uma probabilidade produzida pelo OpenCV.
- OpenCV já estava disponível na máquina usada para a prova. Nenhuma dependência foi adicionada ao projeto.
- O detector lê a imagem em memória e só emite metadados JSON; ele não salva nem copia o frame.

## Handoff para VIS-03

O adaptador foi entregue em `mobile/android/app/src/dat/`: sessão e câmera DAT ficam em `PlatformFrameSource`, a mídia de ensaio é fornecida pelo `DatMockAssetProvider` interno e o QR é decodificado por `ZxingPhotoQrDecoder`. Esta tarefa permanece como registro da prova estática original; o estado atual está em [`dat-prehardware.md`](dat-prehardware.md).
