# Task: Barreira de privacidade para Jev remoto

## Status

JEV-69A foi implementada em 24/09/2026 e recebeu ajuste de UX de consentimento
na mesma data; JEV-69B ainda valida o comportamento no SM-X510. Esta e uma
melhoria do modo demonstrativo `mockDebug`, nao uma auditoria LGPD completa nem
uma conclusao juridica.

## Problema

O modo Jev remoto envia uma transcricao curta ao proxy loopback e este a um
servico externo. Uma autorizacao de sessao reduz a friccao da demonstracao, mas
nao impede que uma fala contenha identificador, URL, relato pessoal ou conteudo
fora do escopo. Depois de transmitido, apagar a string local nao desfaz a
divulgacao externa.

## Decisao

Criar `RemoteTranscriptGate` antes de `JevChoiceEvaluator`. A ordem sera:

```text
ativar demonstracao -> aviso e autorizacao de sessao revogavel
     -> fala -> transcricao em memoria -> gate deterministico local
     -> proxy loopback -> Jev
```

O gate bloqueia antes da rede quando encontrar e-mail, telefone, CPF/CNPJ,
URL, tamanho excessivo ou formato fora do escopo remoto. A UI deve dizer que a
fala nao foi enviada e orientar o operador a voltar ao modo Local para uma nova
interacao. O bloqueio nao vai chamar Jev, Qwen, WebSocket ou `Command`.

O aviso de ativacao enumera o que nao deve ser dito, escrito ou compartilhado:
nomes completos, e-mail, telefone, CPF/CNPJ, link, senha, endereco ou qualquer
informacao pessoal/confidencial. O filtro nao tentara decidir que todo texto
“agricola” e seguro: uma fala pode misturar comando e dado pessoal. O app e o
proxy nao gravam a transcricao; o estado Compose e descartado no fim do turno.

## Criterios de aceite

- O caminho padrao continua local; `dat` nunca habilita Jev remoto.
- Ativar o modo remoto exige declaracao visivel, autorizacao de sessao
  revogavel e alerta sobre o que nao compartilhar.
- Padroes bloqueados falham localmente, sem chamada HTTP externa.
- O bloqueio descarta o turno, permite retornar ao modo Local e nao pode
  produzir `Command`.
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
