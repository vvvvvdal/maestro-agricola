# Task: Guard de cancelamento explicito Jev

## Status

Concluida em 23/09/2026 na branch `test/jev`.

## Decisao

`ExplicitCancelGuard` e uma camada local, injetavel e desativada por padrao.
Assim, `JevIntentClassifier` sem guard preserva a medicao Jev bruta. Quando o
guard de desenvolvimento esta ativo, frases de cancelamento explicito retornam
`CANCEL` com fonte `JEV_GUARD` sem chamar o evaluator.

Se o guard falhar, o classificador retorna `CANCEL`, tambem sem chamar Jev.
Esse caminho nao usa Qwen, nao cria alvo e, no `InteractionEngine`, cancela a
confirmacao pendente sem `Command`.

## Catalogo de desenvolvimento

O catalogo e deliberadamente estreito: cancelamento direto, negacao explicita
de uma operacao, `deixa quieto` e a regressao conhecida `segure essa operacao`.
Ele exclui `pare`, pergunta, historico, hesitacao e conversa. O catalogo usado
em avaliacao remota futura continua exigindo aprovacao humana antes de JEV-65.

## Limites

- O guard nao demonstra que Jev bruto deixou de errar.
- `recovery-045` serve apenas como regressao de desenvolvimento; nao pode ir
  para os novos holdouts ASR.
- Nenhum app recebe HTTP, chave ou nova integracao nesta task.

## Verificacao executada

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest \
  --tests 'br.org.agroturtles.maestro.domain.ExplicitCancelGuardTest' \
  --tests 'br.org.agroturtles.maestro.domain.JevIntentClassifierTest' \
  --tests 'br.org.agroturtles.maestro.ui.JourneyPresentationTest' \
  --no-daemon
```

Resultado: `BUILD SUCCESSFUL`; `ExplicitCancelGuardTest` (2),
`JevIntentClassifierTest` (8) e `JourneyPresentationTest` (11) aprovados.
