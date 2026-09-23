# Revisao do holdout ASR primario

## Resultado

Em 23/09/2026, duas pessoas revisaram independentemente as 42 transcricoes
ASR sanitizadas da coleta primaria, sem consultar os rotulos dos cartoes. As
transcricoes exibidas corresponderam exatamente as frases faladas. Houve
consenso para todos os itens, mas P33 foi excluida antes do congelamento: ambas
as revisoes indicaram `SPRAY`, porem a frase foi considerada semantica e
operacionalmente ambigua para um rotulo ouro limpo.

O corpus congelado contem 41 entradas: 15 `CANCEL`, 15 `UNKNOWN`, 2 `SPRAY`,
3 `DOCK`, 3 `UNDOCK` e 3 `CONFIRM`. P33 nao possui linha neste corpus, nao
sera pontuada e nao recebe reposicao. Essa exclusao preserva a separacao entre
coleta e selecao: nenhuma nova frase e escolhida depois de observar o baseline
local.

## Procedimento e privacidade

- A pessoa da coleta consentiu antes da sessao e e distinta da coleta de
  desenvolvimento.
- A coleta ocorreu offline no `mockDebug`, sem alvo, confirmacao, audio salvo,
  screenshot, `logcat` ou ADB durante as falas.
- Cada fala foi feita com a jornada resetada. Nenhum comando foi enviado.
- O repositorio contem apenas transcricao sanitizada, rotulo ouro e categoria;
  nao contem identidade, audio, horario, dispositivo ou identificador de
  sessao.

## Baseline local observado

O classificador local foi observado apenas como baseline durante a coleta; ele
nao alterou o rotulo ouro. Em 41 casos congelados, houve 33 correspondencias e
oito divergencias: P03 `CANCEL -> UNKNOWN`, P05 `CANCEL -> SPRAY`, P13
`CANCEL -> DOCK`, P21 `UNKNOWN -> CANCEL`, P24 `UNKNOWN -> SPRAY`, P26
`UNKNOWN -> CANCEL`, P38 `UNDOCK -> UNKNOWN` e P39 `UNDOCK -> DOCK`.

As predicoes operacionais nao encontraram alvo ou confirmacao, e a jornada foi
resetada antes da proxima fala. Esta observacao nao e resultado Jev, nao usa
rede e nao consome credito.

## Exclusoes

| Cartao | Motivo | Acao |
| --- | --- | --- |
| P33 | A fala de controle fitossanitario nao teve rotulo ouro suficientemente inequivoco para o objetivo operacional. | Excluida; sem texto no TSV e sem reposicao. |
