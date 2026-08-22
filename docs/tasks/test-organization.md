# Organização das suítes de teste

## Objetivo

Oferecer uma entrada única em `tests/` para localizar e executar as suítes do
projeto sem romper as convenções de Python, Android/Gradle, ROS/ament ou do
submódulo `llama.cpp`.

## Ambiguidades e decisões

- "Uma única pasta" significa um catálogo e ponto de entrada únicos, não mover
  código para fora dos source sets exigidos pelos runners.
- Os testes Python próprios podem ser movidos e foram divididos por domínio.
- Os testes Kotlin permanecem em `mobile/android/app/src/test`.
- Os testes ROS permanecem no diretório `test` do pacote do bridge.
- Testes e utilitários de `third_party/llama.cpp` permanecem intactos.
- Ensaios físicos são indexados, mas não automatizados ou declarados aprovados.

## Estrutura

```text
tests/
├── portable/{ai,android,robotics,qa}
├── android/README.md
├── ros/README.md
└── hardware/README.md
```

## Critérios de aceite

- descoberta recursiva executa todos os testes Python portáteis;
- cada subgrupo portátil pode ser executado separadamente;
- testes Android mock continuam passando pelo Gradle;
- testes portáteis do bridge continuam passando no caminho do pacote ROS;
- Makefile, CI e documentação usam os novos caminhos;
- não há mudança em dataset, modelo, frases aceitas, contrato ou produto;
- nenhum arquivo do submódulo é alterado.

## Plano

1. Classificar e mover apenas os testes Python portáteis.
2. Criar índices para Android, ROS e hardware.
3. Atualizar comandos, workflow e referências canônicas.
4. Executar primeiro cada grupo portátil e depois a descoberta completa.
5. Reexecutar os gates Android mock e bridge afetados pela documentação de
   execução.

## Evidências

Validação local em 2026-08-22:

| Gate | Resultado |
|---|---|
| `tests/portable/ai` | 16 testes aprovados |
| `tests/portable/android` | 13 testes aprovados |
| `tests/portable/robotics` | 22 testes aprovados, 4 opcionais ignorados sem OpenCV/NumPy |
| `tests/portable/qa` | 14 testes aprovados |
| descoberta completa em `tests/portable` | 65 testes, 61 aprovados e 4 opcionais ignorados |
| artefato canônico de IA | 64/64, macro F1 1.000 e zero aceite inseguro |
| matriz QA-04 | válida, mantendo corretamente o status `PARTIAL` |
| bridge portátil | 32 testes aprovados |
| `:app:testMockDebugUnitTest` | `BUILD SUCCESSFUL`, 60 testes sem falha |

Os quatro casos ignorados já dependiam de OpenCV/NumPy opcionais. Nenhuma
dependência foi adicionada para esta reorganização.

## Limitações

- O gate DAT depende do segredo `MWDAT_PACKAGES_TOKEN` e será validado pelo
  workflow completo.
- Testes físicos continuam manuais e não são substituídos pela reorganização.
