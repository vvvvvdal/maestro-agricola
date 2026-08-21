# AGENTS.md

## Projeto

Maestro Agrícola é uma interface hands-free para comandar robôs agrícolas com câmera, voz e confirmação por áudio.

## Regras permanentes

- Aplicativo do MVP: Android nativo em Kotlin.
- Não introduzir React Native.
- O Android deve consumir o contrato versionado e o artefato canônico de IA local.
- Integração dos óculos: Meta Wearables Device Access Toolkit (DAT).
- Confirmar a versão atual do DAT antes de alterar dependências ou APIs.
- Nunca assumir que o DAT fornece IMU, pose de cabeça, GPS ou profundidade.
- No MVP, resolver o alvo por marcador visual ou talhão previamente mapeado.
- Não enviar movimento ao robô sem confirmação explícita por áudio.
- Não persistir fotos, áudio ou transcrições por padrão.
- Documentar separadamente os dados tratados pelo app, Android, SDK e serviços externos.
- Desabilitar analytics opcionais do DAT quando permitido e registrar a decisão.
- Nunca colocar tokens, chaves ou segredos no repositório.
- Toda dependência nova precisa de justificativa e aprovação humana.
- Preferir captura sob demanda e processamento local.
- Isolar integrações externas atrás de interfaces pequenas.
- O contrato com ROS deve ser JSON versionado e independente do fabricante.
- Desenvolver com Mock Device Kit antes do hardware real.
- Manter fontes de câmera simulada separadas dos adaptadores DAT reais.
- Testar caminho feliz, recusa, ambiguidade, timeout e desconexão.
- Testar câmera e microfone simultâneos no modelo exato de smartphone do evento.
- Mudança de comportamento exige atualização da spec correspondente.
- Uma tarefa por vez; mudanças pequenas, revisáveis e verificáveis.
- Antes de implementar, listar ambiguidades e critérios de aceite.
- Depois de implementar, comparar código, testes e spec.
- Desde a conclusão da Task 1, `SPRAY` nunca deve causar `Undock`, retorno à doca ou `Dock` implicitamente.
- `DOCK` e `UNDOCK` são comandos operacionais explícitos; não inventar lifecycle automático para compensar uma task ainda não implementada.
- A IA pode interpretar linguagem natural, mas a saída de controle deve continuar estruturada e validada; nenhum modelo deve gerar comandos ROS livres diretamente.
- `LocalIntentClassifier` continua sendo a autoridade operacional para `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`.
- Qwen é somente assistente de domínio: recebe apenas o caminho `UNKNOWN`, produz somente `CHAT` ou `OUT_OF_SCOPE` e nunca recebe acesso a `Command`, WebSocket, ROS, estado do robô ou resolução de alvo.
- `TargetResolver` continua separado do assistente; Qwen não inventa target, pose ou ação.
- Mudanças de modelo de IA devem ser comparadas em corpus/benchmark reproduzível antes da escolha final e, quando houver o aparelho alvo, medidas também em latência e memória no dispositivo.
- O caminho DAT 0.9.0 pré-hardware já existe com MockDeviceKit; a pendência é validar sessão/câmera e áudio nos Meta Wearables reais, sem confundir mock com evidência física.
- Antes de declarar DAT aprovado, validar no mesmo aparelho e com os mesmos óculos o sample oficial de câmera/sessão aplicável à versão do SDK em uso.
- Não assumir de antemão qual microfone/rota de áudio estará disponível com os óculos conectados; validar câmera e ASR/áudio simultaneamente no hardware real.

## Protocolo obrigatório para agentes de código

Estas regras existem para impedir que um agente fique preso em comandos, suites irrelevantes ou correções fora do escopo.

### 1. Escopo

- Execute somente a task explicitamente solicitada.
- Leia `TASKS.md` quando existir e não antecipe tasks posteriores.
- Não corrija defeitos, artefatos, modelos, dependências ou documentação que não sejam necessários para os critérios de aceite da task atual.
- Uma falha fora do escopo deve ser registrada, não automaticamente corrigida.
- Não transforme uma task localizada em refactor geral.
- Preserve mudanças do usuário que não pertencem à task.
- Nunca use `git reset --hard`, force-push, rebase destrutivo ou `git checkout -- <arquivo>` para limpar mudanças do usuário.
- Se houver dúvida se uma mudança pertence ao escopo, pare a edição daquela parte e reporte a dúvida.

### 2. Comandos não podem bloquear indefinidamente

Classifique comandos antes de executá-los:

**Comandos rápidos** — `pwd`, `git status`, `git diff`, `git log`, buscas e inspeções:
- expectativa: segundos;
- se não houver progresso em ~15 segundos, interrompa;
- tente no máximo uma alternativa equivalente e não destrutiva;
- exemplo: se `git status` travar, tente `git status --porcelain`.

**Testes focados/unitários**:
- execute somente os relacionados à task;
- use timeout quando houver risco de hang;
- se não houver progresso observável em ~2 minutos, investigue antes de simplesmente esperar;
- não repita a mesma execução mais de uma vez sem uma hipótese nova.

**Simulação/E2E/Gazebo/builds longos**:
- só execute quando a task realmente exigir;
- podem demorar mais, mas devem produzir progresso/logs;
- se ficarem sem progresso por vários minutos, interrompa e diagnostique;
- nunca deixe uma execução indefinida apenas porque “pode estar trabalhando”.

Quando disponível, prefira limites explícitos, por exemplo:

```bash
timeout 20s git status --porcelain
timeout 2m python3 -m pytest \
  robot_ws/src/maestro_robot_bridge/test/test_mission_cycle.py -q
```

### Regra específica para wrappers `make` no Antigravity/Gemini

O runner do Antigravity já apresentou hangs em comandos `make` mesmo quando o
comando subjacente funciona normalmente no terminal do usuário.

Portanto:

- não use `make` como primeira opção quando o comando direto equivalente for conhecido;
- para a Task 1 de lifecycle do bridge, use obrigatoriamente primeiro:

```bash
python3 -m pytest \
  robot_ws/src/maestro_robot_bridge/test/test_mission_cycle.py -q
```

- se um wrapper `make` ficar sem progresso, interrompa e não repita;
- execute diretamente `python3 -m pytest <arquivo> -q` para os testes focados;
- um hang do wrapper `make` é uma limitação do runner, não motivo para alterar
  código do produto;
- não rode `make test-ai`, `make model` ou suites de outros domínios para validar
  uma task exclusiva do bridge ROS.

Ajuste o timeout quando a própria documentação do projeto justificar uma duração maior.

### Pytest no host com ambiente ROS carregado

Neste host, o `pytest` do Python/Anaconda pode descobrir automaticamente plugins do ROS 2, como `launch_pytest`, mesmo em testes portáteis que não precisam deles. Se isso causar erro de import de dependência do ROS (por exemplo `lark`), execute os testes unitários/portáteis com:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest <arquivo-ou-diretório> -q
```

Use essa variável apenas quando o teste não depender intencionalmente de plugins externos do pytest. Não instale dependências aleatórias nem altere código do produto para corrigir um conflito de plugin do ambiente local.

### 3. Estratégia de testes

- Rode primeiro o menor teste capaz de validar a mudança.
- Prefira invocar `pytest` diretamente em arquivos específicos em vez de passar
  por `make`, especialmente dentro do Antigravity.
- Na Task 1, o gate inicial canônico é:

```bash
python3 -m pytest \
  robot_ws/src/maestro_robot_bridge/test/test_mission_cycle.py -q
```

- Não rode `make test` ou outra suíte global por padrão se a task possui um gate mais focado.
- Só rode uma suíte global quando:
  - a task exigir;
  - houver risco real de regressão transversal; ou
  - for o gate final documentado para aquela task.
- Se uma suíte global falhar em componente não alterado, não saia corrigindo esse componente.

Exemplo:

```text
Task atual: lifecycle ROS
python3 -m pytest robot_ws/src/maestro_robot_bridge/test/test_mission_cycle.py -q: PASS
make test: FAIL ou trava por motivo fora do escopo/runner

Ação correta:
- considerar o pytest focado como evidência primária da Task 1;
- registrar a falha/hang global como fora do escopo ou limitação do ambiente;
- NÃO executar `make model`;
- NÃO alterar dataset/modelo;
- NÃO insistir em wrappers `make`;
- continuar/finalizar a validação com os testes focados relevantes.
```

### 4. Falhas preexistentes ou fora do escopo

Ao encontrar uma falha:

1. Identifique se o arquivo/componente faz parte da task atual.
2. Verifique se a sua mudança causou a falha.
3. Se não houver relação com a task:
   - registre o comando e a mensagem;
   - classifique como `OUT-OF-SCOPE` ou `PRE-EXISTING` quando houver evidência;
   - não corrija;
   - continue com os testes focados.
4. Só trate como bloqueio se impedir diretamente a implementação ou a validação de um critério de aceite da task.

Não afirme que uma falha é preexistente sem evidência. Quando necessário, compare o diff atual e os arquivos tocados ou execute um teste focado que isole o componente.

### 5. Regra anti-loop

- Não execute o mesmo comando falho ou travado repetidamente sem mudar a hipótese.
- Máximo de uma repetição automática.
- Depois disso, escolha uma destas ações:
  - usar um comando alternativo;
  - reduzir o teste;
  - inspecionar logs;
  - registrar limitação;
  - pedir decisão humana, se for realmente bloqueante.
- Nunca fique alternando indefinidamente entre `git status`, `make test`, `make test-ai`, rebuilds ou comandos equivalentes.

### 6. Alterações geradas

- Não regenere artefatos apenas porque um checker global reclamou.
- Modelos, schemas, lockfiles, código gerado e snapshots só devem ser atualizados se:
  - pertencem ao escopo da task; e
  - a task/documentação manda regenerá-los.
- Exemplo: `shared/ai/intent_model.json` não deve ser regenerado durante uma task exclusiva do bridge ROS.

### 6.1. IA local e seleção de modelo

- Preserve uma interface de saída pequena e estruturada, por exemplo intent, target e confidence; validação de schema, target, estado do robô e confirmação continua determinística.
- Não escolha um modelo novo apenas por impressão subjetiva em algumas frases. Compare o baseline e alternativas no mesmo conjunto de avaliação.
- O corpus deve incluir variações reais de fala e, quando disponível, a transcrição produzida pelo ASR.
- `UNKNOWN` e recusa segura são comportamentos válidos; reduzir falso negativo não justifica aumentar aceitações inseguras.
- Não envie transcrições para serviços externos apenas para melhorar o classificador local sem decisão humana explícita e revisão de privacidade.

### 6.1.1. Assistente Qwen

- O benchmark de seis rótulos rejeitou Qwen como classificador operacional; não reabrir essa decisão sem novo benchmark reproduzível.
- O runtime Android local via `llama.cpp` é infraestrutura de conversa, não de controle.
- O GGUF não deve ser commitado nem empacotado silenciosamente no APK.
- Integração na `MainActivity` deve ocorrer somente no caminho `UNKNOWN -> LanguageRouter -> QwenDomainAssistant`.
- Operações críticas não podem esperar pelo Qwen nem depender de cold start/warm-up.
- Saída inválida do assistente deve continuar falhando para `OUT_OF_SCOPE`.
- Mudança no system prompt, grammar, quantização, número de threads ou limite de tokens exige repetir o smoke físico e registrar latência/memória.

### 6.2. Meta Wearables / DAT

- O adaptador DAT 0.9.0 e o fluxo pré-hardware com MockDeviceKit já foram integrados; preserve essa fronteira em vez de reescrevê-la durante tasks de IA/bridge.
- O próximo gate é hardware real: sessão, câmera, permissões e rota de áudio no mesmo Android e nos mesmos Meta Wearables da demonstração.
- Preserve o flavor `mock` e as interfaces existentes para que falhas do hardware não contaminem o pipeline já validado.
- Não declarar DAT, câmera dos óculos, áudio dos óculos ou E2E físico como aprovados sem evidência no hardware real.

### 7. Documentação

- Mudança de comportamento exige atualização da spec/arquitetura/documento correspondente em `docs/`.
- Siga o padrão existente em `docs/`: objetivo, decisões/ambiguidades, critérios de aceite, plano, evidências e limitações quando aplicável.
- Não deixe decisão arquitetural importante somente no chat.
- Não reescreva documentos não relacionados apenas para “melhorar texto”.

### 8. Git e commits

Antes de editar:

```bash
git status --porcelain
```

Antes de cada commit:

```bash
git diff --check
git diff
git status --porcelain
```

Use commits atômicos em Conventional Commits. Exemplos:

```text
docs(tasks): add explicit docking roadmap
refactor(bridge): remove automatic dock mission lifecycle
feat(contract): add dock and undock intents
feat(bridge): add explicit undock command
feat(bridge): add explicit dock command
feat(android): transport dock and undock intents
feat(ai): classify dock and undock commands
test(e2e): validate explicit docking lifecycle
```

Regras:

- Um commit = uma mudança lógica verificável.
- Não misture tasks.
- Não inclua arquivos não relacionados.
- Não faça commit de uma mudança que falha nos critérios essenciais da task.
- Uma falha global fora de escopo não impede commit quando os critérios e testes focados da task passam e a limitação está documentada.

### 9. Quando parar e pedir ajuda

Pare e reporte somente quando houver um bloqueio real, por exemplo:

- critério de aceite é ambíguo e há duas implementações incompatíveis;
- teste essencial da própria task falha e a causa não pode ser isolada;
- é necessária uma dependência nova ou mudança de contrato não prevista;
- seria necessário tocar uma task futura para concluir a atual;
- existe risco de perder mudanças do usuário;
- hardware/serviço externo obrigatório está indisponível e não há mock previsto.

Não pare por:

- warning;
- artefato fora do escopo desatualizado;
- teste de outro domínio falhando;
- suíte global irrelevante;
- comando auxiliar que possui alternativa segura.

## Responsáveis por domínio

- Átila: app Android/Kotlin, DAT, áudio, máquina de estados e integração mobile.
- Felipe: visão computacional, ROS 2, Gazebo, TurtleBot 4 e integração com o simulador.
- Rafael: IA local, classificador de intenção, conjunto de testes e métricas do modelo.
- Felipe e Rafael: apresentação e gravação do pitch.

## Definição de pronto

Uma mudança está pronta quando:

- atende aos critérios escritos;
- possui teste proporcional ao risco;
- os testes focados relevantes passam;
- falhas fora do escopo encontradas estão registradas sem serem “corrigidas por acidente”;
- documentação e comportamento estão coerentes;
- não persiste mídia indevidamente;
- mantém a confirmação de segurança;
- o diff é pequeno, revisável e pertence somente à task atual.