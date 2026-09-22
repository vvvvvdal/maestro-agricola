# Arquitetura de agentes de desenvolvimento

Status: aplicada para o experimento JEV em `test/jev`. Esta arquitetura e para
trabalho de engenharia; ela nao participa do runtime Android, nao decide uma
acao do robo e nao muda a autoridade do `LocalIntentClassifier`.

## Topologia

```text
humano integrador (unico writer e decisor)
          |
          v
Terra planner, effort medium, read-only
          |
          +--> Gemini worker condicional via Antigravity CLI, read-only
          |
          v
humano integra uma unica mudanca pequena
          |
          v
Terra reviewer, effort high, read-only
          |
          v
humano aceita, ajusta ou descarta
```

O planner e o reviewer usam `gpt-5.6-terra`. Os perfis locais aplicados sao
`$CODEX_HOME/maestro-planner.config.toml` (effort `medium`) e
`$CODEX_HOME/maestro-reviewer.config.toml` (effort `high`). Eles fixam sandbox
read-only e pedem aprovacao para qualquer acao fora desse limite. O worker usa
Antigravity CLI (`agy`) com o modelo Gemini disponivel na conta ativa, sem pin
de modelo; sua funcao e coletar evidencia, nao produzir autoridade. O wrapper
fixa `--sandbox --print-timeout 2m` e entrega ao worker apenas um pacote de
contexto curado de arquivos rastreados; a proibicao de escrita continua
obrigatoria.

## Contrato dos papeis

| Papel | Entrada | Permissoes | Saida | Quem decide |
| --- | --- | --- | --- | --- |
| Humano integrador | task aprovada e evidencias | unico papel que pode editar e executar a mudanca aprovada | diff, testes e docs | humano |
| Terra planner | descricao da task e repositorio | leitura; `medium` | ambiguidades, aceite, plano e testes focados | humano |
| Gemini worker via Antigravity CLI | uma pergunta concreta + contexto curado | sem ferramentas; sandbox | evidencia para mapear codigo, localizar testes **ou** comparar opcoes | humano |
| Terra reviewer | diff integrado | leitura; `high` | findings acionaveis e lacunas de teste | humano |

Nenhum worker recebe chave JEV, credencial, audio, foto, transcricao ou acesso
a ROS, WebSocket, `Command`, estado do robo ou hardware. Um worker tambem nao
abre worktree nem escreve artefatos. Isso evita escritores concorrentes e
mantem qualquer decisao de seguranca revisavel.

## Fluxo de trabalho

1. **Preflight tecnico.** O integrador roda `tools/agents/preflight.sh`, que
   valida branch, CLIs e diff. A autenticacao do Gemini e verificada somente
   antes de uma chamada real do worker, sem imprimir ou ler credenciais.
2. **Pacote de task aprovado.** O planner ou integrador registra objetivo,
   arquivos de contexto permitidos, fora de escopo, criterios de aceite e um
   teste focado real. Exemplo:
   `tools/agents/plan.sh "definir harness Jev sem rede"`.
3. **Worker condicional.** So use Gemini se houver uma duvida concreta para
   mapear codigo **ou** localizar testes **ou** comparar opcoes. Escolha uma
   dessas perguntas, com o menor pacote de contexto necessario; nao execute as
   tres por padrao.
4. **Um unico responsavel pela implementacao.** O integrador aplica uma unica
   mudanca pequena; nao ha writers concorrentes.
5. **Teste focado real.** Rode o teste definido no pacote antes da revisao.
6. **Revisao delimitada.** Terra `high` revisa o diff contra o pacote de task,
   sem redescobrir o repositorio inteiro. Exemplo:
   `tools/agents/review.sh "a fronteira Jev do IntentClassifier"`.
7. **Correcao limitada.** So corrija finding real e pertencente ao escopo;
   repita o teste focado e encerre ou escale uma ambiguidade/bloqueio real.

Os scripts em `tools/agents/` sao wrappers intencionalmente estreitos. Eles
nao autenticam Gemini, nao leem segredos e nao criam configuracoes de produto.
Autenticacao interativa do Gemini, quando necessaria, continua sendo uma acao
do operador local.

## Guardrails do experimento JEV

- A branch `test/jev` e um ambiente de estudo, nao um caminho de producao e
  nao deve ser apresentada como validacao do JEV no robo.
- `LocalIntentClassifier` continua sendo o baseline e autoridade operacional.
  JEV so pode ser comparado atras da interface `IntentClassifier` em harness
  reproduzivel, com fakes locais e falha fechada.
- Nenhum novo intent, `STATUS`, `INSPECT_TARGET` ou outro, vira `Command` sem
  contrato versionado, revisao humana, confirmacao quando aplicavel e testes.
- Timeout, rede, resposta invalida, baixa confianca, `UNKNOWN`, `CANCEL` e
  conflito de alvo terminam sem `Command`.
- Seguir [`study-groups/jev-rl-2026-10-01/TASKS.md`](study-groups/jev-rl-2026-10-01/TASKS.md)
  para a ordem, o orcamento de US$5 e os gates da apresentacao.

## Validacao da configuracao

O preflight verifica a branch e a presenca dos CLIs sem iniciar uma inferencia:

```bash
tools/agents/preflight.sh
```

Os perfis do Codex seguem a configuracao oficial de profiles e de
`model_reasoning_effort`. A disponibilidade final do modelo depende da conta
autenticada; o preflight nao simula uma tarefa paga para testar isso.

O worker `agy` deve ser executado no terminal desktop autenticado do operador.
Um runner headless sem acesso ao keyring pode informar que nao esta autenticado;
isso nao se corrige copiando token nem liberando permissao ampla.

No headless, o worker nao executa ferramentas de arquivo ou shell. O wrapper
inclui `AGENTS.md` e `GEMINI.md` e aceita arquivos adicionais apenas por
`--file <caminho-relativo-rastreado>`. Caminhos absolutos, fora do repositorio,
nao rastreados ou com nomes de segredo sao rejeitados antes de qualquer envio.
O limite de dois minutos e um guardrail: uma pergunta pequena que o exceder
deve ser investigada antes de ser repetida.

`AGENTS.md` e `GEMINI.md` sao contexto de politica, nao evidencia de
localizacao de codigo/teste, comando de teste, comportamento de runtime ou
resultado. Sem arquivo nao-politico suficiente, o worker responde
`INSUFFICIENT_CONTEXT` e indica os tipos de arquivos adicionais necessarios;
so pode citar um caminho exato se ele ja estiver no contexto fornecido.
