# Identidade visual v2

Status: em andamento em 19 de agosto de 2026

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

- [ ] Os três PNGs aprovados estão versionados sem redesenho ou recoloração.
- [ ] Nenhum arquivo ou referência ativa usa o lockup com o slogan antigo.
- [ ] O README e o catálogo de marca apontam para a nova versão horizontal.
- [ ] O Android mostra a nova marca no cabeçalho e preserva o ícone legível da tartaruga sobre amarelo.
- [ ] Os seis slides preservam narrativa, notas e elementos editáveis, com os novos lockups na abertura e no fechamento.
- [ ] As duas propostas em PDF usam a nova marca na capa e mantêm todo o conteúdo.
- [ ] PPTX e PDFs são renderizados e inspecionados integralmente, sem corte, distorção ou sobreposição.
- [ ] Preflight Android e testes portáteis continuam aprovados.

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

A preencher após a implementação.
