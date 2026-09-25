# Task JEV-70: Contrato de consulta somente leitura

## Status

Especificada e implementada parcialmente em 25/09/2026. JEV-71 criou o
historico em memoria do simulador; JEV-72 consome esse contrato para
`PLOT_STATUS_QUERY`.

## Objetivo

Criar uma fronteira de consulta que agregue valor ao Maestro sem transformar
pergunta em comando. O primeiro caso e informar a ultima missao simulada de
pulverizacao concluida para um talhao. `STATUS_QUERY` reutilizara a mesma
fronteira, mas nao e implementada nesta task.

## Decisoes

### O que `SPRAY` significa no simulador

No bridge atual, `SPRAY` valida o talhao e enfileira uma meta Nav2. O `ACCEPTED`
do WebSocket significa apenas que a meta foi aceita para execucao; nao prova
chegada ao talhao nem acionamento de um pulverizador. O simulador tambem nao
modela atuador, dose ou produto.

Portanto, o primeiro registro e uma **missao simulada de pulverizacao concluida**:
ele so existe quando Nav2 retorna `STATUS_SUCCEEDED` para a meta ligada ao
comando `SPRAY`. A resposta ao operador deve citar o simulador. Ela nao pode
afirmar aplicacao fisica real, produto utilizado ou dose aplicada.

### `OperationRecord`

JEV-71 cria em memoria, no bridge do Gazebo, no maximo 100 registros com este
schema conceitual:

```json
{
  "schema_version": "1.0",
  "operation_id": "uuid-do-command",
  "kind": "SIMULATED_SPRAY_ARRIVAL",
  "plot_id": "plot-02",
  "completed_at": "2026-09-25T15:32:18Z",
  "origin": "GAZEBO_SIMULATOR"
}
```

`operation_id` reaproveita o `command_id` confirmado para rastreabilidade e
deduplicacao. Apenas Nav2 concluido com sucesso pode criar o registro. Rejeicao,
cancelamento, expiracao, erro de transporte, meta recusada, timeout e resultado
Nav2 diferente de sucesso nao criam nem atualizam historico.

Os registros existem somente na memoria do processo do bridge durante a sessao
do simulador. Sao descartados ao reiniciar o bridge, ao encerrar a demo ou ao
ultrapassar o limite de 100, quando o mais antigo e removido. A implementacao
fica em `OperationHistory`; nao armazena foto, frame, audio, transcricao, nome
de operador, produto, dose ou coordenada bruta.

### `ReadOnlyQuery`

`ReadOnlyQuery` e um valor tipado, separado de `Command`. A primeira forma
admitida e:

```json
{
  "schema_version": "1.0",
  "request_id": "uuid",
  "requested_at": "2026-09-25T15:34:00Z",
  "kind": "LAST_SIMULATED_SPRAY_FOR_PLOT",
  "plot_id": "plot-02"
}
```

`plot_id` precisa ser um ID cadastrado e resolvido deterministicamente. Uma
consulta nao aceita alvo implicito como "aqui", nao recebe `confirmed`, nao
possui intencao operacional e nao pode conter campos de `Command`.

O futuro `ReadOnlyQueryTransport` usa contrato/versionamento proprio e uma rota
de leitura distinta de `CommandTransport`. Sua implementacao deve aceitar
somente queries permitidas, nao publicar metas ROS, nao chamar Dock/Undock e
nao compartilhar a fila nem o parser de comandos.

### Resposta narravel

O repositorio retorna um `ReadOnlyResponse` tipado com `request_id`, `kind` e
um dos estados `FOUND`, `NOT_FOUND`, `INVALID_QUERY` ou `UNAVAILABLE`. Para
`FOUND`, a projecao exposta ao app contem somente `plot_id`, `completed_at` e
`origin`; o identificador tecnico do comando nao e narrado.

O app transforma a resposta com frases deterministicas, sem LLM:

| Estado | Resposta curta esperada |
| --- | --- |
| `FOUND` | `A ultima missao simulada de pulverizacao no plot 02 foi concluida em <horario> no Gazebo.` |
| `NOT_FOUND` | `Nao ha missao simulada de pulverizacao concluida para o plot 02 nesta sessao.` |
| `INVALID_QUERY` | `Nao consegui identificar um talhao cadastrado para consulta.` |
| `UNAVAILABLE` | `A consulta esta indisponivel. Nenhum comando foi enviado.` |

Formato de data, fuso horario e texto visivel sao responsabilidade do app. O
bridge preserva UTC ISO-8601; o app pode converter para o horario local somente
para apresentar ao operador.

## Limite entre linguagem, leitura e movimento

```text
fala livre
  -> classificador local de consulta (task posterior)
  -> rotulo PLOT_STATUS_QUERY
  -> resolver deterministico de plot
  -> ReadOnlyQuery -> repositorio/ReadOnlyQueryTransport
  -> ReadOnlyResponse -> UI/TTS deterministico

fala operacional
  -> LocalIntentClassifier ou JevIntentClassifier dos seis rotulos
  -> InteractionEngine -> confirmacao explicita -> CommandTransport -> ROS
```

O classificador reconhece somente a categoria da fala; ele nao cria
`OperationRecord`, nao compoe query livre e nao narra resultado. JEV nao entra
na primeira implementacao de consultas: o baseline local novo deve ser medido
antes de uma comparacao pareada. Qwen continua somente no caminho `UNKNOWN` e
nao consulta historico, ROS ou transporte.

Uma `ReadOnlyQuery` nunca chama `InteractionEngine`, `CommandTransport`,
WebSocket de comando, `Dock`, `Undock`, Nav2 ou `TargetResolver.observeTarget`.
Uma resposta de leitura nao pode confirmar, encadear ou disparar uma acao
fisica; uma nova operacao exige uma nova fala operacional e a confirmacao ja
existente.

## Criterios para as tasks seguintes

- JEV-71 prova que `ACCEPTED` nao cria registro e que so o resultado Nav2 bem
  sucedido de `SPRAY` cria um unico `OperationRecord` para o comando.
- JEV-71 prova que falha, cancelamento, expiracao, rejeicao e timeout nao
  aparecem no historico; tambem cobre limite de 100 e reset da sessao.
- JEV-72 exercita `FOUND`, `NOT_FOUND`, `INVALID_QUERY` e `UNAVAILABLE` com
  doubles que falham caso algum `CommandTransport` seja chamado.
- Nenhum teste usa transcricao, audio, imagem ou dado pessoal real como
  evidencia.

## Fora de escopo

Persistencia em banco, historico de aplicacao fisica, dose/produto, telemetria
de pulverizador, consulta por linguagem livre, Jev para as novas classes,
`STATUS_QUERY`, captura de QR e preview/executor de missao pertencem a tasks
posteriores.
