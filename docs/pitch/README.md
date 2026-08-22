# Integração do deck final

Status: **AGUARDANDO O DECK FINAL**.

Esta branch está preparada para receber a apresentação final do Maestro Agrícola. O PPTX atualmente versionado é apenas a base herdada da `main` e não representa a versão final aprovada.

## Caminho canônico

Substitua o arquivo abaixo, mantendo exatamente o mesmo nome e caminho:

```text
docs/pitch/Maestro-Agricola-Pitch.pptx
```

Não adicione cópias com sufixos como `v2`, `final` ou `final-final`. O histórico do Git deve registrar as versões.

## Contrato do deck final

O arquivo recebido deve:

- ter **sete slides** em formato 16:9 e seguir [`storyboard.md`](storyboard.md);
- sustentar um pitch gravado de no máximo 3 minutos, com ritmo planejado entre 2:45 e 2:55;
- apresentar no slide 2 a hipótese de impacto de **20–30%**, identificada como estimativa a validar em piloto;
- manter um slide exclusivo para próximas etapas, expectativas e metas;
- mostrar a equipe em ordem alfabética no fechamento;
- usar o produtor rural com óculos Meta e os logos oficiais de Meta, CEIA e AKCIT conforme os materiais aprovados;
- preservar transições suaves e coerentes entre os slides;
- registrar nas notas um bloco `[Sources]` para cada alegação ou ativo externo;
- não incluir um roteiro separado em Markdown, DOCX ou PDF. Se a equipe desejar, as notas de apresentação podem permanecer dentro do próprio PPTX.

## Gate de aceite

Antes de mudar o status para concluído:

1. Validar a integridade do pacote com `unzip -t docs/pitch/Maestro-Agricola-Pitch.pptx`.
2. Confirmar sete slides, sem placeholders vazios, cortes, sobreposições ou texto ilegível.
3. Renderizar e inspecionar visualmente todos os slides, em tamanho integral.
4. Confirmar notas e fontes das alegações externas, além das transições previstas.
5. Executar `python3 -m unittest tests.portable.qa.test_pitch_consistency -q`.
6. Atualizar a seção de pitch em [`../../TASKS.md`](../../TASKS.md) com o resultado real da validação.

Commit sugerido para a integração:

```text
docs(pitch): add final seven-slide deck
```
