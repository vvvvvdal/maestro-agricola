# QA-01 — recusa, ambiguidade e timeout

## Objetivo

Comprovar que recusa explícita, intenção ou confirmação ambígua, conflito de alvo, ausência de alvo e timeout nunca produzem um comando que possa chegar ao `CommandTransport`.

## Fronteira de segurança testada

No app Android, o transporte é chamado exclusivamente quando `InteractionResult.command` não é nulo. Portanto, os testes da máquina de estados devem comprovar simultaneamente o estado resultante e a ausência de `command` em cada caminho inseguro.

Esta tarefa valida a fronteira Android em `InteractionEngine`. A desconexão do WebSocket, a expiração no bridge e a deduplicação pertencem à QA-02.

## Ambiguidades resolvidas

- Uma confirmação classificada como `UNKNOWN` é recuperável: o app continua em `AWAITING_CONFIRMATION`, pede repetição e não cria comando.
- Uma intenção inicial desconhecida mantém o estado seguro atual e não cria comando.
- Conflito entre alvo visual e falado encerra a interação em `AMBIGUOUS` e limpa o contexto do alvo.
- Ausência ou desconhecimento do alvo encerra a interação em `AMBIGUOUS` e não escolhe um valor padrão.
- Recusa explícita encerra a interação em `CANCELLED` e limpa o contexto do alvo.
- Timeout encerra a interação em `CANCELLED`, informa o cancelamento e limpa o contexto do alvo.
- Confirmações recebidas depois de recusa, conflito ou timeout são tardias e nunca criam comando.
- QA-01 não adiciona um estado `TIMEOUT`; o motivo aparece na mensagem e o estado terminal permanece `CANCELLED`, conforme a spec atual.

## Critérios de aceite

- [x] `CANCEL` após a pergunta de confirmação retorna `CANCELLED` e `command == null`.
- [x] Confirmação ambígua retorna `command == null` e permite uma nova resposta dentro do timeout existente.
- [x] Intenção desconhecida retorna `command == null`.
- [x] Alvo ausente ou desconhecido retorna `AMBIGUOUS` e `command == null`.
- [x] Conflito visual/falado retorna `AMBIGUOUS` e `command == null`.
- [x] Timeout retorna `CANCELLED` e `command == null`.
- [x] Confirmação tardia após recusa, conflito ou timeout retorna `command == null`.
- [x] Somente `SPRAY` com alvo resolvido seguido de `CONFIRM` pode produzir `command` e entrar em `SENDING`.
- [x] Testes Kotlin e `assembleMockDebug` passam sem nova dependência.
- [x] Nenhum teste captura ou persiste áudio, imagem ou transcrição real.

## Fora de escopo

- DAT real, câmera, microfone e rota Bluetooth.
- Envio físico ao bridge ou movimento no Gazebo.
- Desconexão, expiração e duplicação de mensagem.
- Alteração do contrato JSON ou do classificador de intenção.

## Evidência esperada

- Testes unitários Android cobrindo todos os critérios acima.
- Relatório Gradle sem falhas.
- APK `mockDebug` montado com sucesso.
- Checklist da QA-01 atualizado somente após a execução aprovada.

## Resultado em 19 de agosto de 2026

- Nove testes de `InteractionEngine` passaram, cobrindo caminho feliz e todos os cenários de segurança desta tarefa.
- Os três conjuntos Android somaram 12 testes: nove da máquina de estados, dois do classificador local e um do resolvedor de alvo, sem falhas ou erros.
- Os nove testes Python de modelo e paridade também permaneceram aprovados nos 13 casos compartilhados.
- `./gradlew testMockDebugUnitTest assembleMockDebug` terminou com `BUILD SUCCESSFUL`.
- O APK gerado possui SHA-256 `1f8d931b5bea848dc2d89ba7892b16f1226580d1cc33424741e1510cd86c2416`.
- Nenhuma dependência, mídia, transcrição real, credencial ou chamada de rede foi adicionada.
