# Guia de testes

Este guia separa os testes por nível para que um erro possa ser localizado antes de iniciar o simulador pesado.

## Caminho simples: passou ou não passou

Para a validação local normal, execute na raiz:

```bash
make test-quick
make demo
```

Não abra `127.0.0.1:18765` no navegador. A porta recebe conexões WebSocket dos apps e do cliente mock, não páginas HTTP. Não execute `make simulation-logs` a menos que `make demo` falhe.

O resultado é aprovado quando a última parte da saída contém:

```text
SIMULAÇÃO VERIFICADA: protocolo, Nav2 e movimento confirmados
DEMO APROVADA: undock, WebSocket, Nav2, movimento e dock verificados.
```

Qualquer aviso anterior pode ser ruído de inicialização do ROS/Gazebo. Se as duas linhas aparecem e o comando retorna ao terminal sem `make: ***`, o teste passou. Encerre depois com `make simulation-down`.

## Visão geral

| Nível | Comando | O que prova | Precisa de Docker |
|---|---|---|---:|
| Ambiente | `make doctor` | ferramentas, daemon, arquivos e porta | Sim, apenas diagnóstico |
| Portátil | `make test` | modelo, cliente e núcleo seguro do bridge | Não |
| Configuração | `make test-quick` | testes portáteis + Compose válido | CLI apenas |
| Integração | `make demo` | undock → mock/IA local → WebSocket → Nav2 → dock | Sim |
| Rota completa | `make demo-route` | visita os três plots em ordem e retorna à doca | Sim + NVIDIA |
| Visual NVIDIA | `make gazebo` + `make demo-visual` | mesma integração com a janela 3D na GPU | Sim + NVIDIA/X11 |
| Mobile mock | Gradle/Android Studio | comportamento nativo no aparelho | Não para o build |

## Teste recomendado do zero

Execute na raiz do repositório:

```bash
make doctor
make test-quick
make demo
```

O primeiro `make demo` baixa uma imagem ROS grande e pode demorar. Repetições aproveitam o cache. O comando deixa o contêiner em segundo plano para permitir novos testes com `make demo-client`.

### Saída de sucesso

O último JSON deve ter:

- `schema_version: "1.0"`;
- o mesmo `command_id` usado pelo cliente;
- `status: "ACCEPTED"`;
- `reason: "navigation goal queued"`.

Depois do JSON, o verificador aguarda o Nav2, confirma que o processo do Gazebo continua vivo, encontra o aceite da meta, mede alteração da odometria a partir daquele momento e espera a confirmação do dock. O sucesso completo termina com:

```text
SIMULAÇÃO VERIFICADA: protocolo, Nav2 e movimento confirmados
```

Um JSON `ACCEPTED` sem `DEMO APROVADA` prova apenas o contrato e a fila; não é evidência suficiente de navegação ou retorno seguro.

### Rota com os três plots

Para reconstruir um contêiner headless limpo, visitar os três pontos e voltar à doca:

```bash
make demo-route
```

O comando fecha uma instância anterior para evitar disputa pela porta e pelos recursos. Ele usa a NVIDIA sem abrir a GUI, enfileira `plot-01`, `plot-02` e `plot-03`, exige a conclusão nessa ordem e termina com `ROTA APROVADA` somente após `Dock completed`. O teste portátil por software continua disponível em `make demo` para um único plot.

Não espere uma janela: o Gazebo usa tela virtual e renderização por software. Consulte o processo com:

```bash
make status
make logs
```

## Inspeção visual opcional

O modo visual usa a mesma abordagem comprovada no `pluginbot-turtlebot4`: Gazebo, ROS 2 e RViz ficam no mesmo contêiner e o Docker entrega todas as GPUs NVIDIA. Ele não conecta uma segunda GUI a um servidor headless.

Pré-requisitos adicionais:

- driver NVIDIA funcionando em `nvidia-smi`;
- NVIDIA Container Toolkit e runtime `nvidia` no Docker;
- sessão gráfica X11 com a variável `DISPLAY` definida.

Na raiz, abra uma instância limpa:

```bash
make gazebo
```

O comando encerra qualquer serviço Maestro anterior, libera X11 apenas para o usuário `root` local do contêiner e inicia `simulation-gui` com `gpus: all`. A primeira abertura pode baixar o `warehouse` e outros modelos do Gazebo Fuel. Aguarde o cenário aparecer; o volume `gazebo-fuel-cache` evita repetir esse download nas próximas aberturas.

Em outro terminal, execute a prova ponta a ponta:

```bash
make demo-visual
```

O resultado aprovado termina com `DEMO VISUAL APROVADA`. Para abrir também o RViz no mesmo contêiner:

```bash
make rviz
```

`make rviz` carrega `config/maestro.rviz` e usa o mesmo runtime NVIDIA e os mesmos pacotes de descrição do simulador.

No Gazebo, procure o mundo `warehouse`, o TurtleBot 4 e as placas verticais `PLOT-01`, `PLOT-02` e `PLOT-03`, agora separadas em três pontos. No RViz, confirme:

- mapa salvo localizado por AMCL em `/turtlebot1/map`;
- `TurtleBot 4` usando `/turtlebot1/robot_description`;
- `LiDAR` em `/turtlebot1/scan`;
- `Global Plan` e `Local Plan`;
- `Global Costmap`.

Feche o RViz com `Ctrl+C` ou pela janela. Encerre tudo com `make simulation-down`; o acesso X11 é revogado nesse momento. Para o caminho sem janela e portátil, continue usando `make demo`.

## Repetir apenas o comando dos óculos

Com o contêiner ativo:

```bash
make demo-client
```

O cliente usa por padrão:

- endpoint `ws://127.0.0.1:18765`;
- alvo `plot-03`;
- comando “pulverizar esta área”;
- confirmação “confirmar”.

Exemplo com valores explícitos:

```bash
python3 tools/mock_glasses_client.py \
  --endpoint ws://127.0.0.1:18765 \
  --target plot-03 \
  --command "pulverizar esta área" \
  --confirmation "confirmar"
```

Para somente enfileirar os três IDs no contêiner já ativo, repita `--target`:

```bash
python3 tools/mock_glasses_client.py \
  --target plot-01 --target plot-02 --target plot-03
```

## Reinício limpo

Se o contêiner ou o bridge estiverem em estado desconhecido:

```bash
make simulation-down
make doctor
make demo
```

`make simulation-down` remove o contêiner e a rede do Compose, mas preserva a imagem em cache.

## Diagnóstico por mensagem

### Docker daemon indisponível

Sintoma: `permission denied ... /var/run/docker.sock` ou `Cannot connect to the Docker daemon`.

Confirme que o Docker está iniciado e que seu usuário tem permissão para acessar o daemon. Depois, abra uma nova sessão de terminal e execute `make doctor` novamente.

### `Address already in use` ou HTTP em vez de WebSocket

O Maestro usa a porta `18765`. A porta `8765` foi abandonada porque entrou em conflito com serviços do simulador. Execute `make doctor`: se a `18765` estiver ocupada por outro protocolo, ele indicará o conflito antes da demo.

Se o navegador mostrar `invalid Connection header: keep-alive`, feche a aba. Isso apenas indica que uma requisição HTTP comum foi enviada ao servidor WebSocket; use `make demo` ou `make demo-client` para conectar corretamente.

### Cliente aguardando por muito tempo

Na primeira inicialização, ROS 2, Gazebo, AMCL e Nav2 sobem em etapas. Abra outro terminal e execute:

```bash
make logs
```

Se a imagem ainda estiver sendo baixada ou construída, aguarde. Se o bridge não surgir após dois minutos do início do contêiner, faça o reinício limpo.

### Gazebo GUI não responde

Na primeira abertura, o Gazebo pode parecer congelado enquanto baixa e descompacta o mundo `warehouse`. Aguarde o carregamento; as próximas execuções reutilizam o volume `gazebo-fuel-cache`. Se continuar sem responder depois que o cenário deveria ter carregado, execute:

```bash
make simulation-down
make gazebo
```

Não abra `ign gazebo -g` separadamente no host. Esse era o caminho instável: ele separava GUI e servidor e ainda forçava renderização por software. O modo atual abre ambos dentro do mesmo contêiner e solicita a GPU NVIDIA, como no `pluginbot-turtlebot4`.

### Leitura de odometria expirou

Sob carga gráfica, uma chamada `ros2 topic echo` pode demorar mais que o limite mesmo com o robô ativo. O verificador trata esse timeout como uma amostra perdida e tenta novamente dentro do tempo total de movimento. A demo só aprova após obter uma posição diferente da origem.

### `command expired`

O payload só deve ser criado depois que o WebSocket conectar. A versão atual já aplica essa regra. Se o erro reaparecer, confirme que o cliente local está atualizado e não reutilize JSON antigo.

### Comando recusado localmente

Intenção diferente de `SPRAY`, confirmação diferente de `CONFIRM` ou confiança baixa resulta em recusa antes do envio. Isso é uma proteção, não uma falha do bridge.

## Encerramento

```bash
make simulation-down
```

Use `make status` para confirmar que não há serviço ativo.

Ao receber `make simulation-down`, o lançador envia sinais de término a dezenas de processos. Linhas com `SIGINT`, `SIGTERM`, `exit code -15` e até `process has died` para o Gazebo durante essa etapa são mensagens de desligamento, não resultado da demo. Avalie a execução pela mensagem `DEMO APROVADA` emitida antes de encerrar.

## Android: desenvolvimento e demonstração com DAT

Na pasta `mobile/android`:

```bash
./gradlew :app:testMockDebugUnitTest
./gradlew :app:assembleMockDebug
```

Para compilar o caminho DAT com o MockDeviceKit de forma explícita:

```bash
./gradlew -PmaestroDatMockDevice=true :app:assembleDatDebug
```

Esse comando exige acesso de leitura ao GitHub Packages para resolver os AARs
do DAT 0.9.0. Defina `GITHUB_TOKEN` no ambiente ou `github_token` no
`local.properties`; não registre nem compartilhe o valor. O APK deve mostrar
`câmera: dat-mockdevice:success`. O modo simulado reutiliza a fixture `plot-03.png`,
transmitida em memória por um provider interno, e não comprova o funcionamento
dos óculos.

Troque `-PmaestroDatMockScenario=success` por `permission-denied`, `timeout` ou
`disconnect` para os casos negativos. O valor do cenário fica visível na mesma
label da fonte de câmera.

O roteiro e os casos de sucesso, recusa, timeout e desconexão estão em
[`tasks/dat-prehardware.md`](tasks/dat-prehardware.md). ZXing 3.5.4 foi aprovado
e os quatro cenários passaram no emulador em 21 de agosto de 2026. O teste
Espresso do sample oficial não inicia na imagem Android 16/API 36.1 por uma
incompatibilidade com `InputManager.getInstance`; o mesmo sample foi validado
manualmente até `Stream: streaming` e `Captured photo`, sem modificação do
código oficial. `mockDebug` continua sendo o gate de regressão independente do
SDK Meta.

No emulador de desenvolvimento, use `ws://10.0.2.2:18765`. No Android físico da demonstração, use `ws://IP_DO_COMPUTADOR:18765`; aparelho e computador precisam alcançar a mesma rede local. O `mockDebug` serve para desenvolvimento. A evidência principal do MVP usa `datDebug`, um Android compatível e os Meta Wearables pareados.

## Evidência mínima para a entrega

Registre, sem mídia bruta:

1. saída de `make test-quick`;
2. JSON `ACCEPTED` do `make demo`;
3. trecho de log mostrando a meta de navegação;
4. uma recusa local por intenção ou confirmação inválida;
5. versão do build `datDebug`, modelo do Android e Meta Wearables usados na jornada real.
