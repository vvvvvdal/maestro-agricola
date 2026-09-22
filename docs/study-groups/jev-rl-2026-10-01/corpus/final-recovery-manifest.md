# Corpus Jev - Avaliacao Final de Recuperacao

Status: FROZEN em 22/09/2026

`final-recovery.tsv` e o corpus independente da unica rodada `JEV-41R`. Ele
foi criado depois que `final.tsv` ficou inelegivel para repeticao e nao altera,
renomeia ou substitui o corpus original. Nenhum texto do recovery repete texto
normalizado de `development.tsv` ou `final.tsv`.

## Contrato do artefato

| Campo | Valor |
| --- | --- |
| Formato | TSV: `id`, `text`, `gold_label`, `category` |
| Casos | 60, com 10 por rotulo |
| Rotulos | `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL`, `UNKNOWN` |
| Dados | Frases sinteticas e sanitizadas; `<ALVO>` e marcador generico |
| Uso remoto | Somente JEV-41R, dentro de US$1,50 |
| Hash SHA-256 | `a157963bd5c63623f1263d1772f72b76fd70e7ebaf333ee5be2ffedc8e7e6d2a` |

Apos esta criacao, os textos, rotulos, rubricas, modelo e limiar nao podem ser
ajustados. Respostas, erros ou custo da rodada nao autorizam uma repeticao.
Qualquer nova alteracao exige nova task humana, corpus com outro nome e hash e
registro de que a comparacao anterior e distinta.

## Limites

Este corpus mede apenas classificacao textual sintetica. Ele nao cria
`Command`, nao resolve alvo, nao recebe audio/imagem/estado do robo e nao muda
Qwen, RAG, bridge ou APK. `UNKNOWN`, `CANCEL`, injecao, duvida e alvo sem acao
continuam sem autorizacao de movimento.
