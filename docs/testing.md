# Guia de testes

Este guia separa os testes por nível para que um erro possa ser localizado antes de iniciar o simulador pesado.

## Caminho simples: passou ou não passou

Para regressão local alinhada ao lifecycle atual, execute na raiz:

```bash
make test-quick
```

Na pasta `mobile/android`, os gates combinados usados após integrar Qwen + DAT/UI são:

```bash
./gradlew :app:testMockDebugUnitTest --no-daemon
./gradlew :app:assembleMockDebug --no-daemon
./gradlew :app:testDatDebugUnitTest --no-daemon
./gradlew :app:assembleDatDebug --no-daemon
```

Os quatro devem terminar com `BUILD SUCCESSFUL`.

`make demo`, `make demo-route` e `make demo-visual` ainda são úteis para diagnóstico do WebSocket/Nav2/Gazebo, mas conservam expectativas históricas de lifecycle automático. Enquanto a Task 7 não reescrever esses scripts, eles não são gate final de segurança: `SPRAY` deve terminar no alvo e permanecer lá, e `DOCK`/`UNDOCK` só podem ocorrer por comandos explícitos e confirmados.

Não abra `127.0.0.1:18765` no navegador; é uma porta WebSocket.

## Visão geral

| Nível | Comando | O que prova | Status como gate atual |
|---|---|---|---|
| Ambiente | `make doctor` | ferramentas, daemon, arquivos e porta | diagnóstico |
| Portátil | `make test` | modelo, cliente e núcleo seguro do bridge | válido |
| Configuração | `make test-quick` | testes portáteis + Compose válido | gate local |
| Android mock | `:app:testMockDebugUnitTest` + `:app:assembleMockDebug` | regressão Kotlin, IA e JNI/CMake | gate |
| Android DAT | `:app:testDatDebugUnitTest` + `:app:assembleDatDebug` | regressão Kotlin e compatibilidade de build Qwen + DAT/UI | gate de build, não hardware |
| Qwen físico | `QwenSmokeActivity` no `mockDebug` | runtime local, GBNF, latência e memória | evidência da Task 6 |
| Integração legada | `make demo` | protocolo/WebSocket/Nav2/movimento | diagnóstico até Task 7 |
| Rota legada | `make demo-route` | três plots no cenário | diagnóstico; retorno automático é histórico |
| Visual NVIDIA | `make gazebo` + `make demo-visual` | inspeção visual Gazebo/RViz | diagnóstico visual até Task 7 |

## Teste recomendado do zero

Execute primeiro a regressão que não depende do lifecycle legado:

```bash
make doctor
make test-quick
```

Depois, para Android:

```bash
cd mobile/android
./gradlew :app:testMockDebugUnitTest --no-daemon
./gradlew :app:assembleMockDebug --no-daemon
./gradlew :app:testDatDebugUnitTest --no-daemon
./gradlew :app:assembleDatDebug --no-daemon
```

Para testar movimento no Gazebo antes da Task 7, prefira um smoke manual compatível com o lifecycle explícito: se o robô estiver dockado, envie `UNDOCK` explicitamente; envie e confirme `SPRAY`; verifique que a navegação termina no plot sem retorno automático; envie `DOCK` explicitamente somente quando quiser retornar.

Os comandos `make demo*` continuam documentados abaixo como ferramentas de diagnóstico histórico. Não use a mensagem antiga `DEMO APROVADA: undock ... dock` como evidência do comportamento atual.

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

O script pode terminar com `DEMO VISUAL APROVADA`, mas essa mensagem ainda usa o critério histórico. Use a janela para inspecionar o movimento; não trate dock/undock automático como comportamento aprovado. Para abrir também o RViz no mesmo contêiner:

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

Intenção fora de `SPRAY`, `DOCK` e `UNDOCK`, confirmação ausente/inválida, estado incompatível ou confiança baixa resulta em recusa antes do envio. Isso é uma proteção, não uma falha do bridge.

## Encerramento

```bash
make simulation-down
```

Use `make status` para confirmar que não há serviço ativo.

Ao receber `make simulation-down`, o lançador envia sinais de término a dezenas de processos. Linhas com `SIGINT`, `SIGTERM`, `exit code -15` e até `process has died` para o Gazebo durante essa etapa são mensagens de desligamento, não resultado da execução. Enquanto a Task 7 não atualizar os scripts, não use a mensagem legada `DEMO APROVADA` como evidência do lifecycle atual.

## Android: desenvolvimento e demonstração com DAT

Na pasta `mobile/android`:

```bash
./gradlew :app:testMockDebugUnitTest
./gradlew :app:assembleMockDebug
./gradlew :app:testDatDebugUnitTest
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

## Qwen local: smoke físico de desenvolvimento

O smoke isolado do Qwen existe somente no source set `mock` e, sozinho, não prova integração com a `MainActivity`, DAT ou Meta Wearables. O APK espera que o arquivo `qwen2.5-1.5b-q4_k_m.gguf` seja provisionado no diretório privado `files/` do app de desenvolvimento; o GGUF não faz parte do repositório nem do APK.

Depois de instalar `app-mock-debug.apk` e provisionar o modelo, inicie:

```bash
adb shell am start \
  -n br.org.agroturtles.maestro.mock/br.org.agroturtles.maestro.platform.QwenSmokeActivity

adb logcat \
  MaestroQwen:I MaestroQwenSmoke:I '*:S'
```

O gate registrado em 21/08/2026 no SM-X510 foi `SMOKE_RESULT passed=5 total=5`. Evidência final: 603 tokens de system prompt, load 33.291,911 ms, quatro respostas warm entre 5.714 e 5.909 ms, PSS 1.377.044 KB, RSS 1.451.773 KB e Swap PSS 273 KB.

Após o wiring, a `MainActivity` foi validada em 22/08/2026 no Edge 40 Neo/API 35. `UNKNOWN` exibiu `Processando resposta local…`; pergunta de domínio retornou `CHAT`; pergunta sobre bolo retornou a recusa fixa `OUT_OF_SCOPE`; `DOCK` abriu confirmação sem chamar o Qwen. O load foi 43.783,994 ms, a geração cold 11.106,745 ms, a warm 7.320,504 ms, PSS 1.342.225 KB e RSS 1.389.716 KB. O status térmico Android permaneceu 0.

Detalhes: [`tasks/qwen-android-runtime.md`](tasks/qwen-android-runtime.md).

## Evidência mínima para a entrega

Registre, sem mídia bruta:

1. saída de `make test-quick`;
2. builds `mockDebug` e `datDebug` aprovados;
3. E2E atualizado da Task 7 mostrando o lifecycle explícito;
4. uma recusa local por intenção/confirmação inválida;
5. versão do `datDebug`, modelo do Android e Meta Wearables usados na jornada real;
6. se o Qwen fizer parte da demo final, evidência do wiring na `MainActivity` e de que comandos operacionais continuam sem depender dele.
