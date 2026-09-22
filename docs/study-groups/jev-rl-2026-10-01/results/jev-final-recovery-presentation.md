# Evidencia Jev - Avaliacao Final de Recuperacao

Escopo: n=60, corpus sintetico pareado, uma rodada remota.

## Comparacao medida

| Medida | Local | Jev remoto |
| --- | ---: | ---: |
| Casos | 60 | 60 |
| Acertos | 48 | 54 |
| Accuracy | 0,8000 | 0,9000 |
| Macro-F1 | 0,8026 | 0,9010 |
| Aceitacoes inseguras | 3 | 1 |
| Brier multiclasses | 0,3034 | 0,1057 |
| Top-label ECE | 0,0810 | 0,0787 |
| Coverage de probabilidades | 1,0000 | 1,0000 |
| Falhas remotas | 0 | 0 |
| Latencia p50 | 0,175 ms | 742,333 ms |
| Latencia p95 | 0,293 ms | 2100,575 ms |
| Custo | US$0.000000000 | US$0.001472394 |
| Modelo | - | jev-1.13.0 |

## Matriz de confusao

Linhas sao rotulos ouro; colunas sao predicoes operacionais.

### Local

| Ouro \ Predicao | CANCEL | CONFIRM | DOCK | SPRAY | UNDOCK | UNKNOWN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CANCEL | 7 | 1 | 0 | 0 | 1 | 1 |
| CONFIRM | 0 | 8 | 1 | 0 | 0 | 1 |
| DOCK | 0 | 1 | 7 | 0 | 1 | 1 |
| SPRAY | 0 | 0 | 0 | 9 | 0 | 1 |
| UNDOCK | 0 | 0 | 2 | 0 | 8 | 0 |
| UNKNOWN | 0 | 1 | 0 | 0 | 0 | 9 |

### Jev remoto

| Ouro \ Predicao | CANCEL | CONFIRM | DOCK | SPRAY | UNDOCK | UNKNOWN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CANCEL | 7 | 1 | 0 | 0 | 0 | 2 |
| CONFIRM | 0 | 9 | 0 | 0 | 0 | 1 |
| DOCK | 0 | 1 | 9 | 0 | 0 | 0 |
| SPRAY | 0 | 1 | 0 | 9 | 0 | 0 |
| UNDOCK | 0 | 0 | 0 | 0 | 10 | 0 |
| UNKNOWN | 0 | 0 | 0 | 0 | 0 | 10 |

## Aceitacoes inseguras medidas

- Local: `recovery-043 CANCEL -> UNDOCK (0,5930)`, `recovery-047 CANCEL -> CONFIRM (0,9407)`, `recovery-060 UNKNOWN -> CONFIRM (0,4527)`.
- Jev remoto: `recovery-045 CANCEL -> CONFIRM (0,7500)`.

## Reliability diagram

O SVG pareado mostra somente bins ocupados. Cada ponto informa `n`; a diagonal representa calibracao ideal.

- [jev-final-recovery-reliability.svg](jev-final-recovery-reliability.svg)

## Limites de interpretacao

Descritivo: nao prova calibracao generalizavel, seguranca de campo ou prontidao operacional. A amostra tem 60 falas sinteticas, uma unica rodada e nao possui intervalo de confianca ou replicacao.
Latencia e custo sao medidos no harness deste host; nao representam Android, audio, rede de campo ou controle do robo.
O aceite Jev `CANCEL -> CONFIRM` impede qualquer alegacao de seguranca operacional. A decisao de adocao pertence a JEV-43.

Proveniencia: SHA-256 das metricas de entrada `e7984bbc1eb715402809f59d47130068e985789d0efb1d1c5b0db7362f5dddcc`.
