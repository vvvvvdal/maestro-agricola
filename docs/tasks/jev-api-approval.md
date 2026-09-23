# Task: Aprovacao e limites da API Jev

## Status

**APROVADA em 22/09/2026** pelo operador do experimento.

## Decisao

O Maestro pode usar a API remota Jev somente no experimento da branch
`test/jev`, para comparar um classificador alternativo dos seis rotulos atuais.
Esta aprovacao nao autoriza uso em producao, no APK, no robo, nem em uma acao
fisica. O `LocalIntentClassifier` continua sendo o baseline operacional.

## Dados permitidos

Cada chamada pode conter somente:

- uma fala textual sintetica ou transcricao sanitizada, limitada ao enunciado
  necessario para classificar a intencao;
- mencao de alvo normalizada, por exemplo `talhao <ALVO>`, sem identificador de
  fazenda, usuario ou localizacao;
- as rubricas estaticas dos seis rotulos `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`,
  `CANCEL` e `UNKNOWN`;
- um identificador opaco do caso, mantido apenas no registro local do benchmark.

O experimento nao envia audio, imagem, nome de pessoa, identificador de conta
ou aparelho, geolocalizacao, data/hora bruta, estado do robo, target resolvido,
`Command`, WebSocket, ROS ou qualquer segredo. Logs locais registram somente
o identificador do caso, modelo, escolha, probabilidades, confidence, uso,
latencia, custo e classe de erro; nunca a chave.

## Orcamento e paradas

O teto cumulativo do experimento atual e **US$5,00**. Nenhuma chamada remota
ocorre antes de `JEV-40`; fakes e corpus continuam locais.

| Uso | Limite | Regra |
| --- | ---: | --- |
| `JEV-40`, smoke remoto | US$0,50 | uma rodada pequena, sem ajustar corpus final |
| `JEV-41A`, final original interrompido | US$3,00 | corpus original nao pode ser repetido; custo real e indeterminado |
| `JEV-41R`, final de recuperacao | US$1,50 | nova rodada unica, em corpus independente e congelado |
| Reserva nao alocada | US$0,00 | alocada explicitamente para `JEV-41R` em 22/09/2026 |

Adicionar credito na conta nao aumenta este teto automaticamente. Qualquer novo
teto exige aprovacao humana registrada, atualizacao deste documento e
replanejamento das tasks afetadas.

## Fase pos-HOLD

A fase registrada em [`jev-post-hold-protocol.md`](jev-post-hold-protocol.md)
nao possui subteto remoto aprovado. JEV-61 a JEV-64 sao locais; JEV-65 e
JEV-66 permanecem bloqueadas ate aprovacao humana de custo, dados ASR e
condicoes de parada. A autorizacao anterior nao pode ser reaproveitada para
uma nova rodada, mesmo que o painel da conta tenha credito disponivel.

## Recuperacao aprovada

Em 22/09/2026, o operador aprovou uma avaliacao final de recuperacao apos a
rodada `JEV-41A` ficar interrompida e indeterminada. A reserva atomica do
corpus original existe, mas a fixture final nao existe. O painel apresentado
pelo operador mostra quatro requests, 1.507 tokens e cerca de US$0,0001, com
aviso de estatisticas atrasadas; esses valores nao podem ser atribuidos com
seguranca a uma etapa especifica.

Portanto, `final.tsv` permanece preservado e inelegivel para repeticao. A
autorizacao permite somente `JEV-41R`, em corpus novo, com manifest, hash,
reserva e outputs novos. O seu pior caso matematico de US$0,322560 cabe nos
US$1,50 alocados e no teto cumulativo de US$5,00. Esta recuperacao nao usa
novos dados pessoais, nao altera a chave e nao autoriza nova tentativa do
corpus original.

## Credencial local

A chave fica somente na variavel de ambiente `TYPESAFE_API_KEY` do terminal que
executara o harness. O SDK oficial tambem usa essa variavel por padrao.

```bash
read -rsp 'TYPESAFE_API_KEY: ' TYPESAFE_API_KEY
echo
export TYPESAFE_API_KEY
```

O valor nao vai em `local.properties`, `.env` do repositorio, APK, CI,
documentacao, commit ou chat. A sessao do terminal termina e descarta a
variavel. O primeiro uso permitido e o smoke da `JEV-40`.

## API prevista

`JEV-20` definira o request minimo para `POST /v1/systemone`, usando uma
pergunta `Choice`. A documentacao informa que `Choice` retorna `choice`,
`probabilities` e `confidence`; a implementacao futura deve preservar estes
campos no DTO experimental, sem transforma-los em comando livre.

Fontes: [Quick start da TypeSafe](https://docs.typesafe.ai/introduction/quickstart)
e [Introduction](https://docs.typesafe.ai/introduction).

## Criterio de aceite concluido

A aprovacao humana, os dados permitidos, os dados proibidos, o teto de custo,
os subtetos, as condicoes de parada e o local da credencial estao registrados.
`JEV-10` pode iniciar; chamadas Jev continuam bloqueadas ate `JEV-40`.
