# Proposta do projeto

Estas são as versões revisadas da proposta Maestro Agrícola.

- [`versao-resumida.md`](versao-resumida.md): fonte editável da versão curta.
- [`versao-tecnica.md`](versao-tecnica.md): fonte editável da versão detalhada.
- `Maestro-Agricola-Versao-Resumida-Revisada.pdf`: exportação para compartilhamento.
- `Maestro-Agricola-Versao-Tecnica-Revisada.pdf`: exportação para compartilhamento.

As duas exportações usam na capa o lockup horizontal aprovado em 19 de agosto de 2026. O conteúdo das páginas internas continua derivado dos arquivos Markdown acima.

## Decisões incorporadas

- O MVP não depende de IMU, pose de cabeça ou profundidade dos óculos.
- O alvo é um marcador ou talhão previamente mapeado.
- A câmera passa pelo DAT; o áudio usa as APIs nativas do Android e deve ser validado no aparelho real.
- A IA comprovável é o classificador linear softmax local já exportado para Kotlin; a próxima medição é o benchmark no Android físico da demonstração com `datDebug` e os Meta Wearables.
- A confirmação por áudio é obrigatória antes de qualquer comando de movimento.
- O app não persiste mídia bruta e declara separadamente os fluxos de dados de Android, Meta AI e DAT.

Atualize primeiro os arquivos Markdown e depois regenere os PDFs.
