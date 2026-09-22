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
          +--> Gemini research worker, read-only
          +--> Gemini test worker, read-only
          +--> Gemini implementation worker, read-only
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
read-only e pedem aprovacao para qualquer acao fora desse limite. O worker
Gemini usa o modelo disponivel na conta ativa, sem pin de modelo; sua funcao e
coletar evidencia, nao produzir autoridade. O wrapper passa `--skip-trust` para
evitar que um diretorio ainda nao confiavel rebaixe `--approval-mode plan` para
`default`; a sandbox e a proibicao de escrita continuam obrigatorias.

## Contrato dos papeis

| Papel | Entrada | Permissoes | Saida | Quem decide |
| --- | --- | --- | --- | --- |
| Humano integrador | task aprovada e evidencias | unico papel que pode editar e executar a mudanca aprovada | diff, testes e docs | humano |
| Terra planner | descricao da task e repositorio | leitura; `medium` | ambiguidades, aceite, plano e testes focados | humano |
| Gemini research | pergunta limitada | leitura em `plan` + sandbox | fontes locais, riscos e lacunas | humano |
| Gemini test | hipotese de validacao | leitura em `plan` + sandbox | comando focado e expectativa | humano |
| Gemini implementation | recorte de codigo | leitura em `plan` + sandbox | pontos de mudanca e possivel diff textual | humano |
| Terra reviewer | diff integrado | leitura; `high` | findings acionaveis e lacunas de teste | humano |

Nenhum worker recebe chave JEV, credencial, audio, foto, transcricao ou acesso
a ROS, WebSocket, `Command`, estado do robo ou hardware. Um worker tambem nao
abre worktree nem escreve artefatos. Isso evita escritores concorrentes e
mantem qualquer decisao de seguranca revisavel.

## Fluxo de trabalho

1. O integrador roda `tools/agents/preflight.sh`; ele falha fora de `test/jev`.
2. O planner descreve a task e seus criterios. Exemplo:
   `tools/agents/plan.sh "definir harness Jev sem rede"`.
3. Um ou mais workers Gemini investigam perguntas independentes. Exemplo:
   `tools/agents/worker.sh test "localize os testes de IntentClassifier"`.
4. O humano escolhe uma unica mudanca, a implementa e executa apenas os testes
   focados definidos na task.
5. O reviewer avalia o diff. Exemplo:
   `tools/agents/review.sh "a fronteira Jev do IntentClassifier"`.
6. O humano compara diff, testes e spec; so entao pode encerrar a task.

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
