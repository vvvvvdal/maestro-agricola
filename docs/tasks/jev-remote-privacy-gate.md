# Task: Barreira de privacidade para Jev remoto

## Status

Especificada em 24/09/2026 como JEV-69. A implementacao e validacao ficam em
JEV-69A e JEV-69B. Esta e uma melhoria do modo demonstrativo `mockDebug`, nao
uma auditoria LGPD completa nem uma conclusao juridica.

## Problema

O modo Jev remoto envia uma transcricao curta ao proxy loopback e este a um
servico externo. O checkbox `Fala de teste sem dados pessoais` reduz o risco,
mas nao impede que uma fala contenha identificador, URL, relato pessoal ou
conteudo fora do escopo. Depois de transmitido, apagar a string local nao
desfaz a divulgacao externa.

## Decisao

Criar `RemoteTranscriptGate` antes de `JevChoiceEvaluator`. A ordem sera:

```text
fala -> transcricao em memoria -> confirmacao de envio por turno
     -> gate deterministico local -> proxy loopback -> Jev
```

O gate bloqueia antes da rede quando encontrar e-mail, telefone, CPF/CNPJ,
URL, tamanho excessivo ou formato fora do escopo remoto. A UI deve dizer que a
fala nao foi enviada e permitir voltar ao processamento local. O bloqueio nao
vai chamar Jev, Qwen, WebSocket ou `Command`.

O filtro nao tentara decidir que todo texto “agricola” e seguro: uma fala pode
misturar comando e dado pessoal. Por isso, a confirmacao por turno mostra que
o texto sera enviado e permite recusa. O app e o proxy nao gravam a
transcricao; o estado Compose e descartado no fim do turno.

## Criterios de aceite

- O caminho padrao continua local; `dat` nunca habilita Jev remoto.
- Cada envio remoto exige declaracao visivel e confirmacao no turno atual.
- Padroes bloqueados falham localmente, sem chamada HTTP externa.
- O bloqueio oferece processamento local e nao pode produzir `Command`.
- Testes cobrem e-mail, telefone, CPF/CNPJ, URL, texto longo, recusa do envio,
  envio permitido e limpeza de estado; os testes nao usam dados pessoais reais.
- O proxy continua sem log de chave ou transcricao e com teto de chamadas.
- A evidencia de apresentacao diz “minimizacao preventiva”; nunca
  “anonimizacao”, “fala segura” ou “conformidade LGPD integral”.

## Limites e referencia

Esta task reduz a divulgacao acidental, mas nao substitui avaliacao juridica,
politica de privacidade, definicao de base legal, acordo com fornecedor ou
auditoria dos provedores Android e TypeSafe. A LGPD inclui coleta,
classificacao, uso e transmissao no conceito de tratamento; os principios de
necessidade e as medidas de seguranca continuam aplicaveis. Referencias:
[Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm)
e [guia de seguranca da ANPD](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/processo-guia-orientativo-sobre-seguranca-da-informacao-para-agentes-de-tratamento-de-pequeno-porte.pdf).
