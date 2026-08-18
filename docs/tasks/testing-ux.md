# Tarefa: teste local sem ambiguidade

## Problema observado

O fluxo técnico funciona, mas uma pessoa pode confundir três situações com falha da demo:

- abrir `127.0.0.1:18765` no navegador, embora a porta aceite WebSocket e não HTTP;
- acompanhar `make simulation-logs` durante o uso normal e interpretar avisos internos do ROS/Gazebo como resultado do teste;
- encerrar o contêiner e interpretar `SIGINT`, `SIGTERM` ou o código `-15` dos processos filhos como falha de execução.

O desligamento do bridge também produz um traceback real quando o contexto ROS já foi encerrado pelo manipulador de sinais e o processo chama `rclpy.shutdown()` novamente.

## Ambiguidades resolvidas

- O teste principal é `make demo`; os logs são recurso de diagnóstico, não etapa obrigatória.
- A demo só está completamente aprovada quando o terminal mostra a confirmação de protocolo, Nav2 e movimento.
- Mensagens de encerramento posteriores não invalidam uma demo que já terminou aprovada.
- A porta `18765` não oferece interface visual. A execução padrão é headless.

## Critérios de aceite

- [x] O bridge encerra sem traceback de `rcl_shutdown already called`.
- [x] `make demo` termina com uma mensagem curta e inequívoca de aprovação.
- [x] README e guia de testes apresentam um caminho principal, sem exigir a leitura dos logs.
- [x] A documentação explica navegador, modo headless e mensagens normais de encerramento.
- [x] Testes portáteis e configuração Compose continuam passando.
- [x] Uma execução real confirma WebSocket, Nav2 e alteração da odometria.

## Plano

1. Tornar o desligamento do contexto ROS idempotente no bridge.
2. Acrescentar ao `make demo` um resumo final legível.
3. Reescrever o início dos guias como teste binário: passou ou não passou.
4. Reconstruir, executar e encerrar o contêiner; conferir os logs do desligamento.

## Evidências

- Branch validada: `feat/e2e-demo`.
- O log recebido inicialmente era de encerramento: os processos receberam `SIGINT`/`SIGTERM`. O único traceback próprio do Maestro era `rcl_shutdown already called`, causado pela segunda chamada a `rclpy.shutdown()`; o bridge agora verifica `rclpy.ok()` antes de encerrar o contexto.
- A primeira reprodução após essa correção encontrou outra falha real e intermitente: o spawner oficial e o `controller_guard` tentavam ativar `diffdrive_controller` ao mesmo tempo. O log registrou `Failed to activate controller` e encerrou o launch.
- O guardião agora aguarda até 45 segundos pelo fluxo oficial e só executa o fallback depois desse prazo. Mesmo após o fallback, ele verifica o estado efetivo em vez de confiar apenas no código de saída do spawner.
- `make test-quick`: aprovado; artefatos do modelo atualizados, acurácia operacional `15/16`, 23 testes portáteis, 4 testes do bridge e configuração Compose válidos.
- `make demo`: aprovado após reconstrução; resposta `ACCEPTED`, `Nav2 ativo`, meta aceita e odometria alterada para `x=0.011`, `y=0.000`.
- A saída final mostrou `SIMULAÇÃO VERIFICADA: protocolo, Nav2 e movimento confirmados` e `DEMO APROVADA: WebSocket, Nav2 e movimento foram verificados.`
- O log da execução aprovada registrou `Controller active: diffdrive_controller`, sem `Failed to activate controller`, sem desligamento por `TurtleBot controller did not become active` e sem traceback do bridge.
- O contêiner foi encerrado e removido ao final com `make simulation-down`.

Avisos de frequência do Behavior Tree e do loop de controle ainda podem surgir sob renderização por software. Eles não impediram a validação de movimento, mas devem ser considerados ao medir desempenho; não são apresentados ao usuário como sucesso ou falha.
