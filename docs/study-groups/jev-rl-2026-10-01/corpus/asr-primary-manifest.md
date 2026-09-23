# Manifesto do holdout ASR primario

## Status

Congelado em 23/09/2026, antes de qualquer rodada remota Jev. Este arquivo
descreve somente o holdout primario sanitizado; nao e uma reserva, uma chamada
HTTP ou uma decisao de adocao.

## Conteudo congelado

| Campo | Valor |
| --- | --- |
| Arquivo | `asr-primary.tsv` |
| SHA-256 | `36fbb2c81ba336ad2b27d9b8e2e5226244e5bace7e8f2bc872a85735343f44ef` |
| Entradas | 41 |
| `CANCEL` | 15 |
| `UNKNOWN` | 15 |
| `SPRAY` | 2 |
| `DOCK` | 3 |
| `UNDOCK` | 3 |
| `CONFIRM` | 3 |
| Estrato de seguranca | 30 (`CANCEL` + `UNKNOWN`) |
| Cartoes de origem | `jev-asr-primary-cards.md` SHA-256 `50ddec1edae4239cc259bb8c530a3e4487687f3e5721a9d5f327cb4e00f1d943` |
| Exclusao | P33, sem reposicao |
| Rotulagem | duas revisoes humanas independentes, com consenso; P33 excluida por ambiguidade |
| Separacao | falante e sessao distintos de desenvolvimento; codigos de auditoria fora do repositorio |
| Modelo remoto previsto | `jev-1.13.0` |
| Limiar previsto | `0.40` |
| Politicas previstas | `jev_raw` e `jev_guarded`, reportadas separadamente |
| `remote_reservation` | `BLOCKED` |
| `budget_cap` | `BLOCKED` |

## Regras posteriores

Nenhum texto, rotulo, categoria, guard ou limiar deste corpus pode ser alterado
para melhorar uma rodada. JEV-65 continua bloqueada por aprovacao humana nova
de dados e custo; qualquer chamada usa reserva, subteto e fixture distintos.
O holdout de replicacao precisa de outra pessoa e outra sessao antes da
comparacao final.
