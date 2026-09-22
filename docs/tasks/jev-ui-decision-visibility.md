# Visualizacao da decisao Jev no Android

Status: JEV-30 concluida; JEV-31 a JEV-34 planejadas para `test/jev`

Responsavel sugerido: Atila (Android), com Rafael na evidencia do classificador

## JEV-30 concluida

Em 22/09/2026, `predictionSourceLabel` passou a converter a origem `JEV` em
`Jev`, sem mudar `RULE`, `MODEL` ou o fallback local. A mudanca e apenas de
apresentacao e o cartao existente ja recebe essa funcao; ela nao liga o
adaptador Jev ao app nem adiciona dados ou controles ao layout.

## Objetivo

Permitir que a demonstracao mostre, no mesmo app do Maestro, o que o
classificador Jev entendeu e a probabilidade da classe escolhida. A tela deve
continuar centrada na jornada operacional, sem parecer um console de modelo e
sem transformar a probabilidade em autorizacao de movimento.

## Decisoes

- Reutilizar o cartao `INTENCAO` ja existente. Nao criar uma nova secao,
  grafico ou card aninhado.
- Mostrar uma leitura humana no valor principal, por exemplo `Pulverizar`.
- No detalhe, mostrar `SPRAY · 87% · Jev`. Os 87% sao a probabilidade da
  classe escolhida, nao o campo `confidence` calculado pelo Jev a partir da
  distribuicao.
- Para `UNKNOWN`, mostrar `Nao reconhecida` e `UNKNOWN · 42% · Jev`, junto da
  mensagem segura ja existente. Cor e texto precisam comunicar a recusa; cor
  sozinha nunca e o sinal.
- Para o baseline, manter o formato atual e usar `regra deterministica` ou
  `modelo local` como origem. Isso permite alternar comparativamente na demo
  sem redesenhar a tela.
- A distribuicao completa e o `confidence` do Jev ficam no artefato de
  benchmark. No app, podem aparecer somente em `Ajustes de teste` no flavor
  `mock`, rotulados como diagnostico; nao aparecem no fluxo `dat` da demo.
- Nao exibir transcricao, foto, chave, custo ou log bruto no cartao. A midia
  continua efemera e o cartao deve caber na tela pequena sem mudar de tamanho
  conforme a resposta.

## Fluxo visual

```text
fala
  -> classificacao local ou Jev
  -> cartao INTENCAO
       valor: Pulverizar | Retornar a doca | Nao reconhecida
       detalhe: SPRAY · 87% · Jev
  -> jornada existente
  -> confirmacao por voz, quando a intencao for operacional
```

O cartao comunica a decisao ao operador; ele nao e um controle e nao pode ser
tocado para confirmar, alterar a classe ou enviar um comando.

## Estados de referencia

| Estado | Valor do cartao | Detalhe | Resultado esperado |
| --- | --- | --- | --- |
| Jev escolhe `SPRAY` | `Pulverizar` | `SPRAY · 87% · Jev` | A confirmacao existente continua obrigatoria. |
| Jev escolhe `DOCK` | `Retornar a doca` | `DOCK · 91% · Jev` | Alvo continua dispensado; nenhuma mudanca no lifecycle. |
| Jev escolhe `UNKNOWN` | `Nao reconhecida` | `UNKNOWN · 42% · Jev` | Nenhum `Command`; segue o fluxo atual de conversa. |
| Timeout ou erro Jev | `Classificacao indisponivel` | `sem decisao remota` | Falha fechada, sem `Command`; o estado visual explica a recusa. |
| Baseline local | leitura atual | `... · modelo local` | Usado como comparacao lado a lado em capturas separadas. |

## Criterios de aceite

- [x] `predictionSourceLabel` reconhece `JEV` e nao altera os rótulos locais.
- [ ] O detalhe usa a probabilidade da classe, com arredondamento consistente,
      e nao chama esse valor de confidence do Jev.
- [ ] `UNKNOWN`, timeout e erro ficam claros por texto, sem comando e sem
      confundir o operador com estado de execucao.
- [ ] Detalhes de distribuicao aparecem apenas no painel de testes do mock.
- [ ] O cartao preserva tipografia, espacamento, cores semanticas e rolagem da
      `MaestroScreen`; nenhuma informacao depende apenas de cor.
- [ ] Testes de `JourneyPresentation` cobrem Jev, local, `UNKNOWN` e erro.
- [ ] Inspecao no `mockDebug` valida tela compacta e leitor de tela anuncia uma
      frase contextual, por exemplo: `Intencao: Pulverizar. Jev: 87 por cento.`

## Limites

- Esta task nao implementa Jev, chamadas de rede, RAG, filtro de topico para
  Qwen, classes novas, missao composta, status de plot ou contrato ROS.
- A tela nao prova calibracao. A evidencia vem do corpus final, de Brier, ECE,
  reliability diagram e cobertura.
