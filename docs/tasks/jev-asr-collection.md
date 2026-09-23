# Task: Coleta ASR real para o estudo Jev

## Status

Preparada em 23/09/2026. A coleta e revisao continuam bloqueadas ate haver
falantes consentidos no SM-X510 e a separacao de sessoes definida.

## Objetivo

Formar somente o corpus de desenvolvimento ASR da JEV-62. Ele serve para
revisar o guard e o protocolo; nao e holdout, nao chama Jev e nao mede adocao.

## Procedimento no aparelho

1. Abrir somente `mockDebug`, com bridge e endpoint Jev desabilitados. Registrar
   fora do repositorio o provedor e a versao de ASR ativos no Android.
2. Confirmar `pt-BR` e verificar se o `SpeechRecognizer` funciona de fato no
   dispositivo. `EXTRA_PREFER_OFFLINE` e apenas uma preferencia, nao uma prova
   de processamento local: se o provedor exigir rede, parar e pedir aprovacao
   humana separada para atualizar o fluxo de dados antes de coletar.
3. Nao abrir gravador, logcat, captura de tela ou coleta ADB.
4. Manter o app sem alvo e nunca dizer ou tocar confirmacao. Depois de cada
   reconhecimento, resetar a jornada antes da proxima frase.
5. O operador le uma frase neutra de um cartao de coleta. A pessoa que revisa
   transcreve somente a saida textual do ASR e descarta a amostra se houver
   nome, contato, localizacao, ID real de talhao, data/hora ou outro dado
   pessoal. Audio nao e salvo nem copiado.
6. Antes de qualquer repositorio, normalizar alvo para `<ALVO>` e substituir
   cada origem humana por um codigo opaco externo. O vinculo entre codigo e
   pessoa fica fora do repositorio e e apagado ao fim da revisao.

## Cobertura minima de desenvolvimento

- `CANCEL`: cancelamento direto, negacao de executar/confirmar, forma coloquial
  e paragrafo ASR da regressao conhecida sem reutilizar o texto do holdout.
- `CONFIRM`: afirmacao curta e permissao explicita, sem negacao.
- `UNKNOWN`: hesitacao, historico, pergunta e ruido/transcricao incompleta.
- `SPRAY`, `DOCK`, `UNDOCK`: ordem explicita, variacao sem acento/pontuacao e
  palavras que o ASR costuma confundir.
- Cada frase aparece em uma unica particao de sessao: desenvolvimento,
  primaria ou replicacao. Esta task cria somente desenvolvimento.

## Revisao e privacidade

- Dois revisores atribuem `gold_label` e `category` independentemente.
- Divergencia e motivo de exclusao ficam em uma planilha privada sem nomes;
  nenhum caso vai para corpus antes de consenso.
- O TSV versionado tera apenas `id`, `text` sanitizado, `gold_label` e
  `category`; nao tera falante, sessao, aparelho, audio ou texto descartado.
- O auditor confirma que audio, logcat, screenshots e transcricoes brutas nao
  existem antes de versionar o corpus sanitizado.

## Saida esperada

`corpus/asr-development.tsv` e `corpus/asr-label-review.md`, somente depois de
coleta e revisao humanas. O arquivo nao pode conter `recovery-045` nem texto
de nenhum holdout futuro.

## Sem autorizacao remota

Esta task nao envia texto para a API. JEV-65 e JEV-66 seguem bloqueadas por
subteto humano novo e por dois holdouts ASR congelados.
