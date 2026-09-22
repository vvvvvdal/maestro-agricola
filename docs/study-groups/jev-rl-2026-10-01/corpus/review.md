# Revisao JEV-14 - Corpus de Desenvolvimento

Data: 22/09/2026

## Escopo

Revisao do `development.tsv` contra as rubricas JEV-10, JEV-11 e JEV-12. Esta
revisao nao altera modelo, limiar, adaptador, app, contrato ou dados enviados
ao Jev.

## Evidencia estrutural

- 72 casos, alem do cabecalho; os seis rotulos possuem 12 casos cada.
- Cada `id` e cada texto normalizado em minusculas aparece uma unica vez.
- Todas as linhas possuem `id`, `text`, `gold_label` e `category` preenchidos.
- As frases sao sinteticas. Nao ha nome de pessoa, contato, localizacao,
  credencial, audio, imagem, transcricao real ou ID de talhao: somente o
  marcador generico `<ALVO>`.

## Cobertura por rotulo

| Rotulo | Exemplos positivos | Fronteiras negativas vizinhas | ASR/ruido |
| --- | --- | --- | --- |
| `SPRAY` | `dev-001`, `dev-002`, `dev-007` | `dev-056` (negacao), `dev-063` (historico), `dev-068` (alvo sem acao) | `dev-005`, `dev-006` |
| `DOCK` | `dev-013`, `dev-014`, `dev-016` | `dev-057` (negacao), `dev-063` (historico), `dev-069` (missao composta) | `dev-024` |
| `UNDOCK` | `dev-025`, `dev-026`, `dev-028` | `dev-058` (negacao), `dev-070` (estado), `dev-071` (capacidade) | `dev-036` |
| `CONFIRM` | `dev-037`, `dev-040`, `dev-048` | `dev-060` (negacao), `dev-061` (hesitacao), `dev-072` (pergunta) | `dev-045` |
| `CANCEL` | `dev-049`, `dev-052`, `dev-054` | `dev-037` (confirmacao), `dev-061` (hesitacao), `dev-063` (historico) | `dev-051` |
| `UNKNOWN` | `dev-061` a `dev-072` | Os cinco outros rotulos funcionam como vizinhos; `dev-067` cobre injecao e `dev-068` alvo sem acao | `dev-066` |

Variacoes sem acento ou pontuacao foram mantidas como casos de ASR plausiveis.
O texto foi revisado para nao confundir variacao de ASR com uma nova acao do
robo.

## Ajustes desta revisao

- `dev-045` recebeu a categoria `asr_without_punctuation`.
- `dev-051` recebeu a categoria `asr_without_accent`.

Os textos e os rotulos ouro permanecem os definidos na JEV-13. Nao foram
encontradas duplicatas para remover nem dados pessoais para sanitizar.

## Limites e proxima fronteira

Este e um corpus de desenvolvimento pequeno e nao mede calibracao, qualidade
de ASR real ou seguranca em campo. JEV-15 cria outro corpus, separado e
congelado, antes de qualquer ajuste usando a rodada final. Chamadas remotas
continuam bloqueadas ate JEV-40.
