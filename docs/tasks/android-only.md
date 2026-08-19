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

- [ ] Não existe diretório, fonte, teste ou tarefa da plataforma descartada no estado final.
- [ ] Documentação e artefatos de pitch descrevem apenas Android/Kotlin.
- [ ] README, proposta e arquitetura apontam `mockDebug` e `datDebug` como os dois caminhos do mesmo app.
- [ ] Testes portáteis e testes Android continuam aprovados.
- [ ] Todas as branches locais apontam para um estado Android-only; a branch local específica da plataforma descartada deixa de existir.
- [ ] Nenhum push é realizado automaticamente.

## Estratégia entre branches

Todas as branches locais existentes são ancestrais de `feat/e2e-demo`, e seus trabalhos já foram integrados nessa linha. Depois da validação, elas podem avançar por fast-forward para o mesmo commit Android-only sem perder commits. A branch local específica da plataforma descartada será removida; a referência remota permanecerá intacta até a equipe decidir fazer push/delete remoto.

## Evidências

A preencher após a implementação.
