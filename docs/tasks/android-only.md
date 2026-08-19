# Tarefa: consolidar o MVP somente em Android

## Decisão

Em 18/08/2026, a equipe confirmou que o programa permite escolher uma única plataforma mobile. O Maestro Agrícola escolheu Android nativo em Kotlin. Manter uma segunda implementação não aumenta a nota do MVP e divide o tempo crítico de integração com DAT, áudio, IA local e robô.

## Escopo

- Manter `mockDebug` para o emulador e aparelhos Android antigos.
- Manter `datDebug` para Android 12/API 31+ e integração futura com os óculos.
- Remover código, testes, dependências, tarefas e instruções da plataforma descartada.
- Atualizar arquitetura, proposta, pitch, responsabilidades e critérios de pronto para uma única implementação Kotlin.
- Preservar o contrato JSON, o classificador local e a fronteira DAT/ROS independentes do fabricante do robô.

## Fora de escopo

- React Native ou outra camada multiplataforma.
- Reescrever o histórico Git já publicado.
- Alterar branches remotas sem autorização de push.

## Critérios de aceite

- [x] Não existe diretório, fonte, teste ou tarefa da plataforma descartada no estado final.
- [x] Documentação e artefatos de pitch descrevem apenas Android/Kotlin.
- [x] README, proposta e arquitetura apontam `mockDebug` e `datDebug` como os dois caminhos do mesmo app.
- [x] Testes portáteis continuam aprovados; o build Android permanece como gate explícito da equipe porque este host não possui JDK/SDK.
- [x] Todas as branches locais mantidas apontam para o estado Android-only; a branch local específica da plataforma descartada deixou de existir.
- [x] Nenhum push foi realizado automaticamente.

## Estratégia entre branches

Todas as branches locais existentes são ancestrais de `feat/e2e-demo`, e seus trabalhos já foram integrados nessa linha. Depois da validação, elas podem avançar por fast-forward para o mesmo commit Android-only sem perder commits. A branch local específica da plataforma descartada será removida; a referência remota permanecerá intacta até a equipe decidir fazer push/delete remoto.

## Evidências da execução

- Removidos 34 arquivos de implementação, recursos, testes e documentação da plataforma descartada, em um commit próprio.
- Busca por nomes, diretórios e referências da plataforma descartada retornou zero ocorrências nos arquivos rastreados, no texto interno do PPTX e no texto extraído dos dois PDFs.
- `make test-quick`: 31 testes portáteis e 14 testes do bridge aprovados; `docker compose config --quiet` aprovado.
- PPTX: seis slides renderizados individualmente, fidelidade de template aprovada e nenhum overflow detectado.
- PDFs: versão resumida com três páginas e versão técnica com oito páginas, ambas renderizadas e inspecionadas integralmente.
- `main`, `feat/android-mock-smoke`, `feat/ai-device-eval`, `feat/submission-readiness`, `feat/vision-qr` e `ls` avançaram por fast-forward para o mesmo estado integrado.
- A branch local específica da plataforma descartada foi removida com segurança por já ser ancestral da integração. A referência remota permanece sem alteração até um push/delete explícito da equipe.

## Commits atômicos

- decisão Android-only e plano permanente;
- remoção do código e testes descartados;
- alinhamento da documentação e diagramas;
- atualização do PPTX editável;
- reexportação das duas propostas em PDF;
- registro final das evidências.
