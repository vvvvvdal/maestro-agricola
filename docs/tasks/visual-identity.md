# Identidade visual AgroTurtles

Status: concluída em 18 de agosto de 2026

Responsáveis: Felipe e Rafael (pitch), Átila (validação mobile)

Branch: `feat/e2e-demo`

## Objetivo

Aplicar uma identidade única do Maestro Agrícola nos aplicativos Android e iOS e no pitch, usando a tartaruga verde sobre fundo amarelo, a paleta fornecida e League Spartan como tipografia principal.

## Fonte da decisão

- imagens de marca enviadas pela equipe em 18 de agosto de 2026;
- design Canva `DAHSfjjymqI`, usado como referência visual;
- pedido explícito da equipe para usar a tartaruga verde com fundo amarelo nos ícones dos apps e nos slides.

## Ambiguidades resolvidas antes da implementação

- **Qual símbolo vira ícone:** a tartaruga verde sobre o quadrado amarelo, sem texto, porque permanece legível em tamanhos pequenos.
- **Qual logo vai para o pitch:** o conjunto com tartaruga, nome `MAESTRO AGRÍCOLA`, assinatura `POR AGROTURTLES` e slogan quando houver espaço; o ícone isolado permanece como elemento de apoio.
- **Onde usar League Spartan:** títulos, corpo e interface dos apps. Campos técnicos monoespaçados não existem na interface atual.
- **Como lidar com a fonte ausente no ambiente:** versionar os arquivos oficiais e a licença OFL no repositório; carregar a fonte como recurso nativo no Android/iOS e no ambiente de geração do pitch.
- **Escopo do Canva:** serve como fonte visual. A automação disponível não altera família tipográfica ou fundos, portanto não será criada uma edição parcial divergente; o PPTX versionado é o artefato editável desta tarefa.

## Paleta

- amarelo `#FCC931`;
- verde `#3C4C1E`;
- azul `#0F3C65`;
- branco `#FFFFFF`.

Os valores foram extraídos dos pixels dominantes dos arquivos recebidos e estão documentados em `docs/brand/README.md`.

## Critérios de aceite

- [x] Ativos originais, paleta, tipografia e regras mínimas estão versionados em `assets/brand` e `docs/brand`.
- [x] O launcher Android referencia ícones da tartaruga verde sobre fundo amarelo em densidades adequadas.
- [x] O app iOS possui `AppIcon.appiconset` completo e selecionado pelo projeto.
- [x] Android e iOS usam a paleta e League Spartan na interface, sem mudar o fluxo funcional.
- [x] Os seis slides usam a nova paleta, League Spartan e a marca sem distorção.
- [x] Todos os slides foram renderizados e inspecionados; não há overflow, sobreposição não intencional ou texto cortado.
- [x] Testes rápidos e preflights existentes continuam com os mesmos resultados esperados para este host.

## Fora de escopo

- redesenhar ou reinterpretar a marca;
- alterar o fluxo de segurança, o modelo de IA ou o contrato ROS 2;
- prometer que a fonte será incorporada ao PPTX em todos os visualizadores;
- salvar uma edição parcial no Canva que não respeite fonte e fundo.

## Plano

1. Versionar ativos e tipografia com proveniência e licença.
2. Aplicar marca, cor e fonte aos apps nativos.
3. Reestilizar o PPTX existente preservando sua narrativa de seis slides.
4. Renderizar, inspecionar e corrigir os três artefatos.
5. Registrar evidências e commits atômicos.

## Evidências

### Ativos e licença

- Cinco PNGs originais preservados em `assets/brand` e duas cópias derivadas apenas por recorte de margem branca.
- Cores confirmadas por contagem de pixels dominantes.
- League Spartan 2.220 nas variantes Regular, Medium, SemiBold e Bold, acompanhada da licença OFL 1.1.

### Android

- `AndroidManifest.xml` referencia `@mipmap/ic_launcher` e `@mipmap/ic_launcher_round`.
- Ícones presentes em `mdpi`, `hdpi`, `xhdpi`, `xxhdpi` e `xxxhdpi`.
- Tema Compose usa a paleta oficial e League Spartan nos 15 estilos tipográficos do Material 3.
- Preflight: `Ícones da marca` e `League Spartan` em `OK`.
- Build não executado neste host: JDK 17 e Android SDK continuam ausentes.

### iOS

- `AppIcon.appiconset` contém os slots de iPhone e o ícone App Store de 1024 px.
- `ASSETCATALOG_COMPILER_APPICON_NAME` aponta para `AppIcon`.
- Quatro pesos da fonte são recursos do app e constam em `UIAppFonts`.
- SwiftUI usa a paleta e os nomes PostScript das fontes.
- Preflight: `Ícone da marca`, `League Spartan` e `AppIcon no projeto` em `OK`.
- Build não executado neste host Linux: Xcode, Swift e XcodeGen continuam indisponíveis.

### Pitch

- Seis slides preservados, com logos autênticos, paleta oficial e League Spartan.
- 147 referências à família `League Spartan` no XML do PPTX.
- Todos os slides inspecionados individualmente após renderização do editor e do LibreOffice.
- `slides_test.py`: aprovado, sem overflow.
- Fidelidade de template: aprovada, zero divergências.
- Placeholders vazios: zero.
- Bloco `[Sources]` de identidade visual presente nas seis notas do apresentador.
- Nenhuma edição parcial foi salva no Canva; o editor automatizado não troca família tipográfica ou fundo. O PPTX versionado é o artefato final editável.

### Regressão

- artefatos do modelo local: em dia na verificação somente leitura;
- acurácia bruta: 14/16;
- acurácia operacional: 15/16 no limiar 0,40;
- testes portáteis: 23 aprovados;
- testes do bridge: 4 aprovados;
- configuração Compose: válida.

### Commits atômicos

- `7215639 docs(brand): define visual identity assets`;
- `47108d7 feat(mobile): apply AgroTurtles brand identity`;
- `e61b675 docs(pitch): apply AgroTurtles visual identity`.
