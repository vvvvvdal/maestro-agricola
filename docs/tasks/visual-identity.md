# Identidade visual AgroTurtles

Status: em andamento  
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

Os valores definitivos serão extraídos diretamente dos pixels dominantes dos arquivos recebidos e registrados em `docs/brand/README.md`.

## Critérios de aceite

- [ ] Ativos originais, paleta, tipografia e regras mínimas estão versionados em `assets/brand` e `docs/brand`.
- [ ] O launcher Android referencia ícones da tartaruga verde sobre fundo amarelo em densidades adequadas.
- [ ] O app iOS possui `AppIcon.appiconset` completo e selecionado pelo projeto.
- [ ] Android e iOS usam a paleta e League Spartan na interface, sem mudar o fluxo funcional.
- [ ] Os seis slides usam a nova paleta, League Spartan e a marca sem distorção.
- [ ] Todos os slides foram renderizados e inspecionados; não há overflow, sobreposição não intencional ou texto cortado.
- [ ] Testes rápidos e preflights existentes continuam com os mesmos resultados esperados para este host.

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

A preencher ao final da tarefa.
