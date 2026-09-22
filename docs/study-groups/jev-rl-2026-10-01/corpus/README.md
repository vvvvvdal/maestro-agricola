# Corpus Jev - Desenvolvimento

`development.tsv` e o corpus de desenvolvimento do experimento. Ele existe
para validar contrato, fake, adaptador e harness enquanto o corpus final ainda
esta fechado. Nao representa resultado, cobertura de campo ou calibracao.

## Dados e privacidade

As frases sao sinteticas e sanitizadas. `<ALVO>` e um marcador generico: nao
deve ser substituido por ID, localizacao, imagem, audio ou transcricao real do
operador quando este corpus for enviado ao Jev. A primeira chamada remota segue
bloqueada ate JEV-40 e usa somente os dados permitidos em
[`../../../tasks/jev-api-approval.md`](../../../tasks/jev-api-approval.md).

## Formato

O TSV possui quatro colunas:

| Coluna | Significado |
| --- | --- |
| `id` | Identificador estavel `dev-###`. |
| `text` | Fala sintetica em pt-BR, ja sanitizada. |
| `gold_label` | Um dos seis rotulos operacionais. |
| `category` | Fronteira semantica que o caso exercita. |

Cada um dos seis rotulos possui 12 casos iniciais. As categorias seguem as
rubricas em [`../rubrics.md`](../rubrics.md) e podem crescer durante JEV-14,
desde que a mudanca seja registrada. Este corpus pode ser ajustado antes de
JEV-15; o corpus final sera separado, congelado e nunca usado para ajustar
frases, limiares ou opcoes da `Choice`.

## Limites

- `SPRAY`, `DOCK` e `UNDOCK` continuam exigindo estado valido e confirmacao.
- `CONFIRM` e texto de autorizacao; somente o estado pendente pode criar
  `Command`.
- `CANCEL`, `UNKNOWN`, ruido, injecao e conflito de alvo nunca autorizam acao.
- O corpus nao muda o classificador local, o Qwen, RAG, o app ou ROS.

## Verificacao prevista em JEV-14

Revisar campos obrigatorios, IDs unicos, duplicatas, distribuicao por rotulo,
categorias de fronteira, variacoes de ASR e ausencia de dados pessoais antes
de qualquer harness ou chamada remota.
