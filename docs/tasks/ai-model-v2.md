# Task: classificador local híbrido v2

## Objetivo

Tornar a interpretação de voz do MVP mais robusta no Galaxy A17 sem depender de rede, runtime de LLM ou nova biblioteca. A decisão operacional continua limitada a `SPRAY`, `CONFIRM`, `CANCEL` e `UNKNOWN`.

## Decisões humanas e ambiguidades resolvidas

- Regras determinísticas são usadas apenas quando a frase tem sinal inequívoco. Elas não substituem o classificador treinado.
- A ordem é `CANCEL → bloqueios de ambiguidade → CONFIRM → SPRAY → modelo → UNKNOWN`; uma negação nunca pode cair numa ordem positiva.
- O app expõe se a decisão veio de `RULE` ou `MODEL`, para auditoria e demonstração.
- Não será incluído Qwen/LLM neste MVP: 4 GB de RAM precisam acomodar Android, DAT, câmera e áudio; a latência e a bateria de um LLM ainda não foram medidas no aparelho-alvo.
- Frases históricas, perguntas, hesitações e pedidos de inspeção sem verbo operacional devem resultar em `UNKNOWN`.
- A confirmação explícita do usuário continua obrigatória depois de reconhecer `SPRAY`; classificar uma intenção não autoriza movimento.

## Critérios de aceite

1. Todo processamento acontece localmente e o artefato versionado tem menos de 1 MB.
2. Treino e avaliação usam arquivos separados, sem frases normalizadas repetidas.
3. A avaliação contém ao menos 64 frases e reporta precisão, revocação e F1 por classe.
4. Acurácia operacional e macro-F1 são pelo menos 95% no conjunto versionado.
5. A taxa de aceite perigoso é zero: exemplos esperados como `CANCEL` ou `UNKNOWN` não podem virar `SPRAY` ou `CONFIRM`.
6. Python e Kotlin produzem rótulo, confiança e origem equivalentes para o fixture compartilhado.
7. Há testes para negação, hesitação, fala histórica, confirmação coloquial, erro de ASR e frase contendo apenas o alvo.
8. Nenhuma dependência é adicionada e nenhuma mídia é persistida.

## Casos críticos

- `sim mas espere` → `UNKNOWN`
- `não sei se devo pulverizar` → `UNKNOWN`
- `o produto foi pulverizado ontem` → `UNKNOWN`
- `inspecione o talhão dois` → `UNKNOWN`
- `talhão três` → `UNKNOWN`
- `deixa quieto` → `CANCEL`
- `isso mesmo` → `CONFIRM`
- `aplica no piquete três` → `SPRAY`

## Fora de escopo

- conversa aberta, RAG, nuvem e fila offline de comandos físicos;
- novos comandos de movimento, doca ou inspeção;
- ajuste fino ou inferência de LLM no telefone.
