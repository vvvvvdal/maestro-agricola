# Rubricas de Intencao - Experimento Jev

Este documento define as fronteiras semanticas usadas para montar e revisar os
corpora do experimento. Ele nao altera o comportamento do app, o contrato ROS
nem os seis rotulos vigentes.

O Jev, quando implementado, continuara apenas a produzir uma
`IntentPrediction`. `TargetResolver`, `InteractionEngine`, confirmacao por
audio, schema e bridge continuam sendo as fronteiras que decidem se existe um
`Command` valido.

## JEV-10 - `SPRAY`

### Decisao

Classificar como `SPRAY` somente uma fala que pede, no presente, que o robo
inicie ou execute pulverizacao/tratamento. O pedido pode ser imperativo,
polido ou uma solicitacao direta; ele precisa representar vontade atual de
execucao, nao conversa sobre a operacao.

O alvo nao define a classe. Ele pode aparecer na transcricao como `talhao
<ALVO>`, `plot-<ALVO>` ou `aqui`, mas sua resolucao pertence exclusivamente ao
`TargetResolver`. Assim, `pulverize aqui` pode ser `SPRAY` e ainda resultar em
`NEEDS_VISUAL`; `SPRAY` nao significa que o robo tem um alvo valido nem que
recebeu autorizacao para se mover.

### Exemplos positivos

| Categoria | Exemplo sanitizado | Rotulo ouro | Observacao |
| --- | --- | --- | --- |
| Ordem direta | `pulverize este talhao` | `SPRAY` | Pedido imediato e inequivoco. |
| Pedido polido | `pode aplicar o defensivo aqui` | `SPRAY` | A forma polida ainda solicita execucao atual. |
| Vontade atual | `quero pulverizar o talhao <ALVO>` | `SPRAY` | O classificador nao resolve `<ALVO>`. |
| Sinonimo operacional | `trate o plot-<ALVO>` | `SPRAY` | O verbo pertence ao catalogo de pulverizacao. |

Esses exemplos refletem as fronteiras ja presentes no baseline local em
`shared/ai/intent_model.json`, `shared/ai/parity_cases.json` e
`shared/ai/dataset/intents.tsv`. Eles sao rubrica, nao novas linhas de treino
nem resultado de benchmark.

### Exclusoes e rotulos vizinhos

| Categoria | Exemplo sanitizado | Rotulo ouro | Motivo |
| --- | --- | --- | --- |
| Negacao direta | `nao pulverize esse lote` | `CANCEL` | Recusa a uma acao; a regra de cancelamento tem precedencia. |
| Historico | `o produto foi pulverizado ontem` | `UNKNOWN` | Relata fato passado, sem pedido operacional. |
| Pergunta explicativa | `explique como pulverizar` | `UNKNOWN` | Busca conhecimento, nao uma ordem. |
| Risco ou opiniao | `pulverizacao e perigosa` | `UNKNOWN` | Conversa de dominio fora do caminho operacional. |
| Hesitacao | `nao sei se devo pulverizar` | `UNKNOWN` | Nao expressa autorizacao atual. |
| Planejamento futuro | `talvez pulverize depois` | `UNKNOWN` | Nao pede execucao agora. |
| Alvo sem acao | `talhao tres` | `UNKNOWN` | Mencao de alvo nao e comando. |

`CONFIRM`, `DOCK` e `UNDOCK` tambem nao sao `SPRAY`; suas fronteiras serao
registradas nas tarefas JEV-11 e JEV-12.

### Alvo conflitante: fronteira fora da classificacao

Conflito de alvo nao pode ser resolvido pelo Jev. Por exemplo, se a visao
identifica `plot-03` e a fala pede `pulverize no plot-01`, a fala continua um
pedido candidato a `SPRAY`, mas o `TargetResolver` deve produzir `CONFLICT` ou
`AMBIGUOUS` e impedir qualquer `Command`.

O corpus de intencao pode registrar o texto como `SPRAY`; a fixture de
resolucao de alvo e que precisa carregar os dois sinais e provar a recusa. Se
a propria fala tiver uma autocorrecao confusa, como `pulverize o talhao dois,
nao, o tres`, ela nao entra como exemplo positivo ate haver uma regra de
normalizacao e uma decisao de produto separadas. O Jev nunca escolhe entre
alvos concorrentes.

### Criterios para JEV-13 e JEV-15

Os corpora de desenvolvimento e de avaliacao final devem conter exemplos
distintos para cada categoria acima, incluindo variacoes plausiveis de ASR.
Casos de negacao, historico, hesitacao, alvo sem acao e conflito de alvo devem
ser revisados como fronteiras de seguranca, nao apenas como erros comuns de
classificacao.

Nenhum caso de `SPRAY`, mesmo com alta probabilidade, remove a resolucao de
alvo, a validacao de estado ou a confirmacao por audio.

## Evidencia e limites da JEV-10

- Evidencia consultada: regras, fixtures e dataset do classificador local;
  casos de alvo em `shared/target/target_resolution_cases.json`.
- Fora do escopo: chamada remota ao Jev, corpus novo, adaptador Kotlin, UI,
  alteracao de limiar ou mudanca no contrato operacional.
- Verificacao desta task documental: leitura cruzada das fontes canonicas e
  `git diff --check`. Nenhum teste de produto foi necessario, pois nao houve
  mudanca de codigo, modelo ou fixture.
