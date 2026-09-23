# Task: Holdouts ASR pos-HOLD do experimento Jev

## Status

Atualizado em 23/09/2026 para JEV-63. O holdout primario foi congelado com 41
transcricoes sanitizadas. A tentativa de replicacao foi encerrada antes de
formar corpus e a fase pos-HOLD fica adiada ate depois da apresentacao de
08/10. Esta e uma avaliacao piloto: ela nao promove o Jev nem muda a decisao
`HOLD`.

Os cartoes da tentativa nao podem ser retomados nem completados. O registro
sanitizado esta em [`jev-asr-replication-attempt.md`](jev-asr-replication-attempt.md).

## Objetivo

Congelar dois corpus ASR reais, `asr-primary` e `asr-replication`, antes de
qualquer HTTP. Cada um tem alvo inicial de 42 transcricoes sanitizadas:

| Estrato | Casos por holdout | Distribuicao |
| --- | ---: | --- |
| Seguranca | 30 | 15 `CANCEL` e 15 `UNKNOWN` |
| Operacional positivo | 12 | 3 de cada `SPRAY`, `DOCK`, `UNDOCK` e `CONFIRM` |
| Total | 42 | seis rotulos declarados |

Com zero aceitações inseguras em 30 casos de seguranca, o limite superior
aproximado de 95% ainda e 10%. Portanto, esse tamanho serve para comparacao
piloto e para encontrar erros; nao e evidência suficiente de seguranca
operacional.

Se uma frase for excluida depois de a coleta primária começar, ela nao recebe
reposicao. O manifest registra o tamanho e a distribuicao menores. Essa regra
evita escolher uma nova frase depois de observar o comportamento do baseline.

## Separacao obrigatoria

- Uma pessoa nova fala somente `asr-primary`; outra pessoa nova fala somente
  `asr-replication`.
- Nenhuma delas pode ter falado `asr-development.tsv` nem participar do outro
  holdout. Cada sessao tambem e exclusiva.
- Textos, cartoes e variantes normalizadas de desenvolvimento, `final.tsv`,
  `final-recovery.tsv` e dos dois holdouts nao se repetem.
- Cada transcricao recebe dois `gold_label` humanos independentes. Divergencia,
  dado pessoal ou conflito com a ontologia exclui a amostra.
- Codigos opacos de pessoa/sessao ficam fora do repositorio e sao apagados
  depois da auditoria. O repositorio recebe somente texto sanitizado, rotulo e
  categoria.

## Coleta no SM-X510

1. Confirmar consentimento da pessoa antes de falar.
2. Abrir somente `mockDebug`, offline, sem alvo e sem confirmacao.
3. Falar uma frase por vez; resetar a jornada antes da proxima.
4. Copiar apenas a transcricao exibida. Excluir a entrada se ela revelar nome,
   contato, localizacao, data/hora, ID real de talhao ou outro dado pessoal.
5. Nao abrir gravador, `logcat`, screenshot ou ADB durante a coleta.

## Congelamento posterior

So depois de ambas as revisoes humanas, criar para cada holdout ativo:

- TSV `id`, `text`, `gold_label`, `category`;
- manifesto com contagens, estrato de seguranca, hash SHA-256, versao do
  modelo, limiar, politica `jev_raw`/`jev_guarded` e declaracao de separacao;
- campos exclusivos `remote_reservation` e `budget_cap`, ambos `BLOCKED` e sem
  valor ate nova aprovacao humana; a JEV-63 nao cria reserva nem consome custo;
- registro sanitizado de revisao e exclusoes, sem texto descartado.

Depois do hash, nenhum texto, rotulo, guard ou limiar pode mudar antes das
rodadas JEV-65 e JEV-66. Esses dois gates continuam bloqueados por nova
aprovacao humana de dados e custo.

## Fora do escopo

Sem chamada Jev, chave, reserva, custo, alteracao no Android, guard, limiar,
harness, Qwen, RAG, `Command`, ROS ou promocao operacional.
