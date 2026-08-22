# Identidade visual v2

> **Atualização de 22/08/2026:** este registro preserva a troca de lockups concluída em 19/08. O pitch canônico agora tem sete slides, sete notas e novo layout editorial; as propostas foram regeneradas a partir dos Markdown revisados e passaram a ter quatro e dez páginas. A marca, a paleta e League Spartan permanecem. Evidência atual: [`../pitch/storyboard.md`](../pitch/storyboard.md), [`../proposta/README.md`](../proposta/README.md) e `docs/pitch/Maestro-Agricola-Pitch.pptx`.

Status: concluída em 19 de agosto de 2026

Responsáveis: Felipe e Rafael (pitch), Átila (validação Android)

Branch de integração: `feat/e2e-demo`

## Objetivo

Substituir os lockups anteriores pela identidade aprovada em 19 de agosto de 2026, preservando paleta, League Spartan e o símbolo da tartaruga. A atualização precisa aparecer nos pontos de contato visíveis do MVP: repositório, app Android, pitch e documentos de proposta.

## Entradas aprovadas

- `3.png`: composição vertical com tartaruga, nome e assinatura;
- `4.png`: wordmark quadrado sem tartaruga;
- `5.png`: composição horizontal com tartaruga, nome e assinatura.

Os três PNGs foram entregues pela equipe em `/home/felipe/Downloads/Agroturtles` e são fontes visuais, não instruções de produto.

## Ambiguidades resolvidas antes da implementação

- **Slogan antigo:** `SEU MELHOR AMIGO DO CAMPO` não aparece nos novos arquivos e deixa de fazer parte do lockup oficial.
- **Assinatura:** `POR AGROTURTLES`, entre linhas azuis, passa a integrar as três versões oficiais.
- **Ícone Android:** permanece a tartaruga verde isolada sobre amarelo. O símbolo não mudou e o lockup completo seria ilegível no launcher.
- **Interface Android:** usa o lockup horizontal completo no cabeçalho; o recorte acontece apenas no enquadramento da tela, sem alterar o PNG original.
- **Pitch:** usa a versão horizontal na abertura e a wordmark no fechamento. A tartaruga isolada continua como assinatura discreta nos slides de conteúdo.
- **Documentos:** as capas das versões técnica e resumida recebem a versão horizontal; o texto técnico e o escopo não mudam.
- **Cores e fonte:** permanecem `#FCC931`, `#3C4C1E`, `#0F3C65`, branco e League Spartan.

## Critérios de aceite

- [x] Os três PNGs aprovados estão versionados sem redesenho ou recoloração.
- [x] Nenhum arquivo ou referência ativa usa o lockup com o slogan antigo.
- [x] O README e o catálogo de marca apontam para a nova versão horizontal.
- [x] O Android mostra a nova marca no cabeçalho e preserva o ícone legível da tartaruga sobre amarelo.
- [x] Os seis slides preservam narrativa, notas e elementos editáveis, com os novos lockups na abertura e no fechamento.
- [x] As duas propostas em PDF usam a nova marca na capa e mantêm todo o conteúdo.
- [x] PPTX e PDFs são renderizados e inspecionados integralmente, sem corte, distorção ou sobreposição.
- [x] Preflight de marca Android e testes portáteis continuam aprovados.

## Fora de escopo

- redesenhar os PNGs recebidos;
- mudar fluxo funcional, IA local, contrato ou integração ROS 2;
- alterar o ícone pequeno para um wordmark ilegível;
- editar o design do Canva sem uma solicitação explícita.

## Plano de execução

1. Atualizar ativos canônicos, README e regras da marca.
2. Aplicar o lockup horizontal ao cabeçalho Compose e validar recursos Android.
3. Editar o PPTX existente por substituição focal dos logos.
4. Regenerar os dois PDFs com a nova capa.
5. Renderizar todos os artefatos, executar testes e registrar evidências.

## Evidências

### Ativos e usos

- `3.png` e `assets/brand/logo-lockup-square.png`: SHA-256 `78e7802295d8e239c586ec6526d62cb6e4ac09a163a408ee340ef0077a29707d`.
- `4.png` e `assets/brand/wordmark.png`: SHA-256 `13522d4c91b75b72826428e3aa3fe632166229f5004516b42b4a38ef3a9cbeeb`.
- `5.png`, `assets/brand/logo-horizontal.png` e o recurso Android: SHA-256 `caa6e665f95017397dfb96ec61157df436ebd0db45627f162dddfcc8de2b451c`.
- Os ativos antigos com `slogan` e as cópias `*-trim.png` foram removidos. O README usa `logo-horizontal.png`.

### Android

- O cabeçalho Compose usa `R.drawable.maestro_logo_horizontal` com crop de enquadramento e altura de 64 dp; o PNG incorporado permanece idêntico ao aprovado.
- O launcher continua com a tartaruga verde sobre amarelo em `mdpi`, `hdpi`, `xhdpi`, `xxhdpi` e `xxxhdpi`.
- Preflight: `Gradle wrapper`, `Ícones da marca`, `Lockup v2` e `League Spartan` em `OK`.
- Build não declarado como aprovado neste host: JDK 17 e Android SDK não estão configurados.

### Pitch

- Seis slides e seis notas preservados; 147 referências a League Spartan e seis blocos `[Sources]`.
- O slide 1 usa a composição horizontal e o slide 6 usa a wordmark. Os PNGs incorporados têm o mesmo SHA-256 dos ativos canônicos.
- O crop é metadado OOXML não destrutivo; não foi criada imagem derivada.
- A sobreposição preexistente entre título e subtítulo no slide 5 foi corrigida.
- Todos os seis slides foram renderizados pelo LibreOffice e inspecionados individualmente sem corte, distorção ou sobreposição.
- `unzip -t` aprovou a integridade do pacote. O `slides_test.py` não pôde usar o renderizador oficial porque o runtime `@oai/artifact-tool` não está instalado neste host; a validação visual completa e a renderização independente pelo LibreOffice foram usadas como fallback documentado.

### Propostas em PDF

- A versão resumida mantém três páginas; a técnica mantém oito páginas; ambas continuam A4 e com os metadados de título e autoria.
- As 11 páginas foram renderizadas com Poppler e inspecionadas individualmente, sem erro de recurso, corte ou sobreposição.
- A comparação de `pdftotext` a partir da página 2 foi idêntica antes e depois nas duas propostas. Apenas a capa recebeu a nova marca e a data da revisão visual.

### Regressão

- artefatos do modelo local em dia;
- acurácia bruta 14/16 e operacional 15/16 no limiar 0,40;
- 31 testes portáteis aprovados;
- 14 testes do bridge ROS 2 aprovados;
- `compileall` aprovado para ferramentas Python e bridge.

### Sequência de commits atômicos

- `docs(brand): plan visual identity v2 rollout`;
- `docs(brand): replace lockups with approved v2`;
- `feat(android): apply visual identity v2 header`;
- `docs(pitch): apply visual identity v2`;
- `docs(proposal): apply visual identity v2 covers`;
- `docs(brand): record visual identity v2 evidence`.
