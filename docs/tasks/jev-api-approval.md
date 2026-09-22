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
| `JEV-41`, corpus final | US$3,00 | uma rodada congelada, com respostas e erros preservados |
| Reserva nao alocada | US$1,50 | so pode ser usada apos registrar motivo e atualizar `TASKS.md` |

Adicionar credito na conta nao aumenta este teto automaticamente. Qualquer novo
teto exige aprovacao humana registrada, atualizacao deste documento e
replanejamento das tasks afetadas.

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
