# Roadmap --- Dock e Undock como comandos explícitos

## Status atual

-   Task 0 --- Versionar TASKS.md: DONE
-   Task 1 --- Remover dock/undock automático: DONE
-   Task 2 --- Adicionar DOCK/UNDOCK ao contrato: DONE
-   Task 3 --- Implementar comando explícito UNDOCK: PRÓXIMA
-   Task 4 --- Implementar comando explícito DOCK: TODO
-   Task 5 --- Android transportar intents: TODO
-   Task 6 --- Evolução da IA local: TODO
-   Task 7 --- E2E final: TODO

------------------------------------------------------------------------

# Task 2 --- Adicionar DOCK e UNDOCK ao contrato

Status: DONE

Foram adicionados os intents:

-   SPRAY
-   DOCK
-   UNDOCK

Regras: - SPRAY exige target MAPPED_PLOT. - DOCK não exige target. -
UNDOCK não exige target. - Confirmação, expiração, command_id e
schema_version continuam válidos.

Evidências: - Bridge tests: 24 passed. - Testes gerais: 58 passed.

------------------------------------------------------------------------

# Task 3 --- Implementar comando explícito UNDOCK

Status: PRÓXIMA

Objetivo:

Executar Undock somente via comando explícito:

``` json
{
  "intent": "UNDOCK"
}
```

Fluxo:

    WebSocket
     -> BridgeCore
     -> Bridge Node
     -> /turtlebot1/undock action

Critérios:

-   UNDOCK explícito chama action.
-   SPRAY nunca chama Undock.
-   Falhas são reportadas.
-   Estado seguro após erro.
-   Testes passam.

------------------------------------------------------------------------

# Task 4 --- Implementar comando explícito DOCK

Status: TODO

Fluxo:

    DOCK
     -> Nav2 dock approach
     -> Dock action
     -> estado dockado

------------------------------------------------------------------------

# Próximas tasks

Task 5 --- Android transportar intents\
Task 6 --- Evolução da IA local\
Task 7 --- E2E final

------------------------------------------------------------------------

# Regras

Antes de editar:

-   Ler AGENTS.md.
-   Ler CONTRIBUTING.md.
-   Ler docs/README.md.
-   Verificar git status.

Antes do commit:

``` bash
git diff --check
git diff
git status
```

Usar Conventional Commits.

------------------------------------------------------------------------

# Próximo passo

Executar somente:

Task 3 --- Implementar comando explícito UNDOCK
