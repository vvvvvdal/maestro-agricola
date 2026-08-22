# Como colaborar no Maestro Agrícola

O projeto usa `main` como linha integrada e demonstrável. Branches devem representar uma mudança lógica verificável, não uma pessoa ou uma área permanente.

## Princípios

- Trabalhe uma task por vez e leia `TASKS.md` antes de começar.
- Crie branches curtas a partir da `main` atualizada.
- Preserve mudanças de outras frentes e evite refactors fora do escopo.
- Contrato, segurança, privacidade e fronteiras de IA precisam de revisão cuidadosa.
- Não versione segredos, mídia bruta, GGUF, APK/AAB, `.cxx/`, builds Gradle ou caches.
- Atualize testes e documentação quando o comportamento mudar.
- Antes de mergear, registre qual evidência foi executada e qual ainda depende de hardware.

## Estado atual das frentes

As frentes abaixo coexistem no mesmo app e devem continuar desacopladas:

| Frente | Estado atual | Regra de integração |
|---|---|---|
| Android/UI | Compose com jornada operacional e diagnóstico | não esconder estados de confirmação/recusa |
| DAT | fluxo 0.9.0 pré-hardware + MockDeviceKit | hardware real ainda é gate separado |
| IA operacional | `LocalIntentClassifier` com seis rótulos | continua autoridade de controle |
| Assistente Qwen | runtime JNI/llama.cpp e wiring principal validados | somente `UNKNOWN -> CHAT/OUT_OF_SCOPE`; sem autoridade operacional |
| Visão/alvo | QR/target previamente mapeado + `TargetResolver` | não inventar pose ou target via LLM |
| Robótica | WebSocket JSON -> ROS 2/Nav2/Gazebo | `SPRAY`, `DOCK`, `UNDOCK` são explícitos e confirmados |

## Fluxo de Git

Atualize a `main` antes de iniciar:

```bash
git switch main
git pull --ff-only origin main
git switch -c feat/minha-task
```

Durante a task:

```bash
git status --short
git --no-pager diff
```

Antes de cada commit:

```bash
git diff --check
git --no-pager diff
git status --short
```

Use Conventional Commits, por exemplo:

```text
feat(android): wire qwen assistant fallback
test(e2e): validate explicit docking lifecycle
docs(ai): record qwen Android benchmark
fix(dat): handle camera session timeout
```

Ao sincronizar uma branch longa com mudanças recentes da `main`, prefira trazer a `main` para a feature, resolver e testar ali antes do merge final:

```bash
git fetch origin
git switch feat/minha-task
git merge origin/main
```

Se houver conflito, resolva apenas os arquivos realmente conflitantes e execute novamente os gates relevantes.

## Gates por tipo de mudança

### Android / integração

Na pasta `mobile/android`:

```bash
./gradlew :app:testMockDebugUnitTest --no-daemon
./gradlew :app:assembleMockDebug --no-daemon
./gradlew :app:assembleDatDebug --no-daemon
```

Os três comandos foram usados como gate combinado após a sincronização de UI/DAT com o runtime Qwen.

### IA operacional

Use o corpus/fixtures versionados e preserve a regra de zero autoridade implícita. `UNKNOWN` é resultado válido e seguro.

### Qwen

Não avalie Qwen por algumas frases escolhidas. Mudanças em modelo, prompt, grammar ou runtime precisam de benchmark reproduzível e smoke físico. O Qwen não pode ganhar um tipo `COMMAND` nem acessar ROS/WebSocket.

### ROS / E2E

Os scripts antigos de demo ainda podem conter expectativas históricas de retorno automático à doca. Use-os como diagnóstico, não como fonte normativa. O lifecycle atual, validado na Task 7, é:

```text
UNDOCK explícito -> navegação/SPRAY -> permanece no alvo -> DOCK explícito
```

Cada ação física continua exigindo confirmação.

## Revisão

Pastas indicam conhecimento predominante, não exclusividade:

- `mobile/android/`: Android, UI, DAT, voz e runtime local.
- `robot_ws/`: bridge ROS 2, Nav2, Gazebo e lifecycle.
- `shared/ai/`: modelo operacional, datasets e benchmarks de IA.
- `contracts/`: contrato versionado compartilhado.
- `docs/`: decisões, evidências e estado do MVP.

Ao tocar outra frente, explique o motivo no PR e preserve a interface pública existente sempre que possível.

## Merge

Antes do merge:

1. `git diff --check` deve estar limpo.
2. Testes focados da task devem passar.
3. Gates transversais devem ser executados quando a mudança atravessa Android/IA/DAT/bridge.
4. Não pode haver arquivo gerado ou segredo acidental.
5. A documentação deve distinguir claramente:
   - validado em mock;
   - validado em aparelho físico;
   - validado com Meta Wearables reais;
   - ainda pendente.

Não apague branches ou tags de evidência até confirmar que a `main` remota contém o resultado esperado.
