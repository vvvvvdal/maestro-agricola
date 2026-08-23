# Paper IEEE do Maestro Agrícola

O artigo em [`main.tex`](main.tex) descreve o snapshot pré-hardware de 22 de agosto de 2026. O texto segue o formato de conferência da classe `IEEEtran` e separa resultados medidos, evidência histórica e hipóteses ainda não validadas. A versão publicada está em [`Maestro-Agricola-Paper.pdf`](Maestro-Agricola-Paper.pdf).

## Compilação

Com uma distribuição TeX Live que inclua `IEEEtran`, `babel-portuges`, `booktabs`, `cite`, `hyperref` e `microtype`:

```bash
cd docs/paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Alternativa sem `latexmk`:

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

O PDF intermediário gerado é `main.pdf` e continua ignorado. Quando uma revisão for aprovada, valide-a visualmente e substitua o arquivo canônico `Maestro-Agricola-Paper.pdf`.

## Fontes internas de evidência

- `shared/ai/intent_model.json`: modelo operacional canônico.
- `shared/ai/evaluation.json`: avaliação original de 64 casos.
- `shared/ai/dataset/field_evaluation.tsv`: corpus atual de seis rótulos.
- `shared/ai/qwen_evaluation.json`: benchmark que excluiu o Qwen do controle.
- `shared/ai/device_evaluation.json`: benchmark físico histórico, com hashes distintos do candidato atual.
- `shared/evidence/qa04_checkpoints.json`: limites dos cinco checkpoints.
- `docs/testing/galaxy-a17-e2e.md`: execução E2E pré-hardware.
- `contracts/command.schema.json`: contrato operacional.

## Política de atualização

Ao alterar modelo, contrato, DAT, E2E ou número de testes:

1. atualize primeiro a evidência estruturada e os testes;
2. revise resultados, limitações e data do snapshot no artigo;
3. compile novamente e confira warnings, referências e paginação;
4. não transforme o potencial de 20–30% em resultado sem um piloto de campo documentado;
5. não descreva MockDeviceKit como câmera física dos Meta Wearables.
