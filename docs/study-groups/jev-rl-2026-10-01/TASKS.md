# Tarefas - Jev e Decisoes com Incerteza

Data alvo: 01/10/2026

Regra de execucao: uma tarefa em andamento por vez. Nao promover Jev a caminho
operacional nem adicionar uma nova acao do robo antes de passar pelos criterios
de seguranca escritos abaixo.

## Criterios de aceite globais

- A apresentacao distingue evidencia medida, resultado de terceiros e hipotese.
- O exemplo de xadrez explicita que Fable perdeu no tempo.
- Qualquer demo remota possui captura gravada ou fixture local de reserva.
- Nenhum segredo entra no APK, no repositorio ou nas capturas.
- Nenhum novo intent fisico chega a ROS sem contrato, confirmacao, testes e
  aprovacao humana.

## Sequencia

| Task | Status | Data alvo | Entrega e criterio de aceite |
| --- | --- | --- | --- |
| 0. Separar o estudo do pitch | DONE | 21/09 | Pasta propria, roteiro tecnico e plano de tarefas versionados; `docs/pitch/` permanece historico. |
| 0.1 Preparar agentes de desenvolvimento | DONE | 21/09 | `test/jev` e guardada por preflight; Terra planeja/revisa em read-only e Gemini CLI opera somente em `plan` + sandbox. |
| 1. Congelar escopo e orcamento experimental | NEXT | 22/09 | Registrar que a Fase 1 compara somente os seis rotulos atuais; sem classes novas, filtro Qwen ou RAG. Aprovar o fluxo de transcricao sanitizada para a API, o teto de US$5 e os subtetos. |
| 2. Definir criterios dos seis rotulos | TODO | 22/09 | Criar criterios positivos, negativos e exemplos em pt-BR para `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`; manter `UNKNOWN` como cobertura. |
| 3. Desenhar a fronteira Jev | TODO | 23/09 | Especificar adaptador atras de `IntentClassifier`, versao de modelo, timeout, retries e falha fechada. Mapear `probabilities[choice]` para a probabilidade exibida e registrar vetor e `confidence` do Jev separadamente. |
| 4. Criar fakes e contratos locais | TODO | 23/09 | Testes unitarios simulam probabilidade, timeout, 429 e resposta invalida sem rede ou credenciais. |
| 5. Montar corpus de desenvolvimento | TODO | 24/09 | Frases rotuladas para comandos claros, negacao, historico, ASR, fora de dominio, injecao e conflito de alvo; separar do corpus final. |
| 6. Montar corpus final de seguranca | TODO | 24/09 | Casos congelados e nao usados para ajustar criterios ou limiares; inclui todos os caminhos que nunca podem criar `Command`. |
| 7. Implementar harness e adaptador Jev | TODO | 25/09 | Mesmo contrato para local e Jev; guardar rotulo, probabilidades, `confidence` do Jev, versao, latencia, custo e erro. O local continua selecionavel como baseline. |
| 8. Planejar e implementar visibilidade Jev no app | TODO | 26/09 | Reusar o cartao `INTENCAO`: acao humana, classe, probabilidade escolhida e origem `JEV`; vetor completo apenas no mock. Ver `jev-ui-decision-visibility.md`. |
| 9. Executar avaliacao controlada | TODO | 27/09 | Matriz de confusao, macro-F1, aceites perigosos, Brier, ECE, coverage e p50/p95; preservar falhas em vez de descarta-las. |
| 10. Preparar demo e evidencias visuais | TODO | 28/09 | Capturas equivalentes local/Jev, ticket, xadrez, matriz de confusao e recusa segura; cada numero externo tem fonte e escopo. |
| 11. Escrever slides do estudo | TODO | 29/09 | Deck fora de `docs/pitch/`, com RLCD/calibracao, benchmark local versus Jev, app e roadmap de classes. Conteudo por 46 minutos e quatro de debate. |
| 12. Gravar reserva e ensaiar | TODO | 30/09 | Video ou fixtures locais para os fluxos remotos; dois ensaios cronometrados e revisao de claims contra resultados. |
| 13. Apresentar e registrar resultados | TODO | 01/10 | Usar apenas metricas obtidas; apos o encontro, registrar conclusoes que alterem uma decisao tecnica. |

## Dependencias e pontos de parada

- Task 1 bloqueia Tasks 3, 7 e 8 quando nao houver aprovacao para a API, o
  fluxo de dados externos e o teto de gasto.
- Task 2 bloqueia corpus e implementacao. Uma classe nova fica fora da Fase 1;
  ela precisa de dono, descricao, exemplos negativos e efeito permitido antes
  de entrar em uma fase futura.
- Classes de roadmap, como `STATUS_QUERY`, `INSPECT_TARGET` e
  `COMPOUND_MISSION`, bloqueiam qualquer mudanca no contrato ROS. Elas podem
  aparecer no slide de arquitetura, mas nao autorizam uma nova operacao fisica.
- Falha em timeout, rede, baixa confianca, `CANCEL`, `UNKNOWN` ou conflito de
  alvo deve terminar sem `Command`; qualquer excecao e bloqueadora.

## Fora do escopo ate nova decisao

- hardware Meta real e rota de audio dos oculos;
- controle por Jev em producao;
- filtro Jev para Qwen e RAG;
- parada de emergencia por reconhecimento de fala;
- navegacao livre, dosagem e acoes agronomicas sem contrato fechado;
- alegar calibracao antes de corpus final rotulado e medido.
