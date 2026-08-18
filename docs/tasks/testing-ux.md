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

- [ ] O bridge encerra sem traceback de `rcl_shutdown already called`.
- [ ] `make demo` termina com uma mensagem curta e inequívoca de aprovação.
- [ ] README e guia de testes apresentam um caminho principal, sem exigir a leitura dos logs.
- [ ] A documentação explica navegador, modo headless e mensagens normais de encerramento.
- [ ] Testes portáteis e configuração Compose continuam passando.
- [ ] Uma execução real confirma WebSocket, Nav2 e alteração da odometria.

## Plano

1. Tornar o desligamento do contexto ROS idempotente no bridge.
2. Acrescentar ao `make demo` um resumo final legível.
3. Reescrever o início dos guias como teste binário: passou ou não passou.
4. Reconstruir, executar e encerrar o contêiner; conferir os logs do desligamento.

## Evidências

A preencher após a validação.
