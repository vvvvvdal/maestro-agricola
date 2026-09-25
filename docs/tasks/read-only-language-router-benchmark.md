# JEV-75 - Benchmark local de rotas somente leitura

## Objetivo

Medir primeiro o roteador local das tres capacidades novas do Maestro antes de
considerar qualquer catalogo Jev adicional. As rotas sao independentes dos seis
labels operacionais e nao entram no experimento Jev congelado.

| Rota | Efeito permitido |
| --- | --- |
| `PLOT_STATUS_QUERY` | Consultar historico pela rota `/read-only`. |
| `STATUS_QUERY` | Consultar estado do robo pela rota `/read-only`. |
| `INSPECT_TARGET` | Abrir captura local sob demanda e retornar somente um marcador valido. |
| `NONE` | Nao usar nenhuma das tres capacidades. |

## Contrato do roteador

`ReadOnlyLanguageRouter` e local e deterministico. Ele recebe apenas texto e
retorna uma rota fechada. Ele nao instancia `Command`, nao chama Jev ou Qwen e
nao tem acesso a WebSocket, ROS, alvo visual ou estado do robo.

`STATUS_QUERY` tem prioridade sobre `PLOT_STATUS_QUERY` quando a fala pede o
estado de uma operacao. Assim, `me informe a situacao da operacao` nao e
confundida com pedido de historico so porque contem `informe` e `operacao`.
`INSPECT_TARGET` exige verbo de leitura/inspecao e referencia a marcador, QR,
placa ou etiqueta; a captura continua local e sob demanda.

## Corpus e resultado

[`read-only-development.tsv`](../study-groups/jev-rl-2026-10-01/corpus/read-only-development.tsv)
tem 32 falas sinteticas e sanitizadas: oito por rota permitida e oito recusas
`NONE`. O teste Kotlin executa o roteador real contra esse arquivo e exige a
distribuicao balanceada.

Em 25/09/2026, `ReadOnlyLanguageRouterBenchmarkTest` passou com **32/32**.
Os testes dos dois controladores e da transicao de inspecao tambem passaram.
No SM-X510, o `mockDebug` recebeu `leia o qr code` como texto digitado e
exibiu `Marcador plot-03 identificado`; o fluxo ficou local, sem Jev, consulta
ou `Command`.

Este e um corpus de desenvolvimento criado junto da regra. Ele prova contrato
e regressao, nao generalizacao, acuracia de campo, ASR real ou calibracao. Nao
foi enviado a API, nao usa chave e nao pode ser apresentado como comparacao
com Jev.

## Decisao posterior

Uma comparacao com Jev so pode nascer em task nova, com corpus pareado novo e
criterios aprovados. Ela nao altera o catalogo atual de seis labels nem permite
Jev iniciar captura, consulta ou movimento no app.
