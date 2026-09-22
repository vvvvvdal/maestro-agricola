# Corpus Jev - Avaliacao Final

Status: FROZEN e INELEGIVEL PARA REPETICAO em 22/09/2026

`final.tsv` e o corpus de seguranca para a unica rodada final planejada em
JEV-41. Ele e separado do corpus de desenvolvimento e nao pode orientar
alteracao de texto, rubrica, opcoes da `Choice`, limiar ou implementacao depois
de ser aberto.

## Contrato do artefato

| Campo | Valor |
| --- | --- |
| Formato | TSV: `id`, `text`, `gold_label`, `category` |
| Casos | 60, com 10 por rotulo |
| Rotulos | `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL`, `UNKNOWN` |
| Dados | Frases sinteticas e sanitizadas; `<ALVO>` e marcador generico |
| Uso remoto | Somente JEV-41, dentro do subteto de US$3,00 |
| Hash SHA-256 | `d0438948d9d239b2cafae8be044f7079935590b50ad9eff522ff570a6188b8b0` |

JEV-40 usa somente smoke pequeno e nao abre este arquivo. Resultados de
JEV-41, incluindo erros, nao autorizam uma segunda rodada ajustada. Uma mudanca
posterior exige nova task aprovada, novo nome de corpus, novo hash e registro
explicito de que a comparacao anterior nao e mais diretamente reproduzivel.

## Separacao e limites

Os textos normalizados deste arquivo nao se repetem em `development.tsv`.
O corpus final ainda nao prova calibracao ou seguranca em campo: ele apenas
fixa uma avaliacao pequena e reproduzivel para comparar o baseline local com o
adaptador Jev.

Nenhum caso concede autoridade de movimento. `CANCEL`, `UNKNOWN`, injecao,
duvida, alvo sem acao e confirmacao fora de estado pendente continuam sem
`Command`; JEV-16 revisa explicitamente essas garantias de integracao.

## Registro de interrupcao

O runner criou `../results/jev-final-reservation.json` antes de qualquer HTTP,
mas nenhuma fixture final foi gravada. Como uma interrupcao nesse intervalo nao
permite provar se houve request, este corpus nao pode ser reaberto. A nova
avaliacao autorizada usa um corpus independente e nao altera este manifesto.
