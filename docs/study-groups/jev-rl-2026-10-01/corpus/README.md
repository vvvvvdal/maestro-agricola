# Corpus Jev - Desenvolvimento

`development.tsv` e o corpus de desenvolvimento do experimento. Ele existe
para validar contrato, fake, adaptador e harness enquanto o corpus final ainda
esta separado. Nao representa resultado, cobertura de campo ou calibracao.

`smoke.tsv` e uma amostra ainda menor e imutavel de seis frases, uma por
rotulo. Ele existe somente para a primeira rodada remota da JEV-40 e nao e o
corpus final nem fonte para ajuste de limiar.

`asr-development.tsv` contem 34 transcricoes sanitizadas, obtidas offline no
SM-X510 e revisadas por duas pessoas. Ele serve para desenvolver e revisar o
guard; nao e holdout, nao mede adocao e nunca deve ser enviado ao Jev. A
revisao e as observacoes do baseline local estao em
[`asr-label-review.md`](asr-label-review.md).

## Dados e privacidade

As frases de `development.tsv` sao sinteticas e sanitizadas. `<ALVO>` e um
marcador generico: nao deve ser substituido por ID, localizacao, imagem, audio
ou transcricao real do operador quando este corpus for enviado ao Jev.
`asr-development.tsv` segue uma regra mais restritiva: embora suas
transcricoes sejam sanitizadas, ele nao sai do dispositivo nem e enviado ao
Jev. A primeira chamada remota segue bloqueada ate JEV-40 e usa somente os dados permitidos em
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
JEV-15. O corpus final esta em [`final.tsv`](final.tsv), com regras de
congelamento em [`final-manifest.md`](final-manifest.md), e nunca sera usado
para ajustar frases, limiares ou opcoes da `Choice`.

`final.tsv` foi reservado para uma rodada interrompida e nao pode ser repetido.
A recuperacao autorizada usa corpus final independente, com outro nome, hash e
manifest; ela nao altera o original nem usa seus textos para ajuste.

O corpus de recuperacao esta em [`final-recovery.tsv`](final-recovery.tsv), com
congelamento e separacao registrados em
[`final-recovery-manifest.md`](final-recovery-manifest.md).

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

A revisao inicial foi concluida em 22/09/2026 e esta registrada em
[`review.md`](review.md). O arquivo continua ajustavel ate JEV-15.
