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
DEMO APROVADA: WebSocket, Nav2 e movimento foram verificados.
```

Qualquer aviso anterior pode ser ruído de inicialização do ROS/Gazebo. Se as duas linhas aparecem e o comando retorna ao terminal sem `make: ***`, o teste passou. Encerre depois com `make simulation-down`.

## Visão geral

| Nível | Comando | O que prova | Precisa de Docker |
|---|---|---|---:|
| Ambiente | `make doctor` | ferramentas, daemon, arquivos e porta | Sim, apenas diagnóstico |
| Portátil | `make test` | modelo, cliente e núcleo seguro do bridge | Não |
| Configuração | `make test-quick` | testes portáteis + Compose válido | CLI apenas |
| Integração | `make demo` | mock → IA local → WebSocket → ROS 2/Nav2 | Sim |
| Mobile mock | Gradle/Xcode | comportamento nativo no aparelho | Não para o build |

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

Depois do JSON, o verificador aguarda o Nav2, confirma que o processo do Gazebo continua vivo, encontra o aceite da meta e mede alteração da odometria. O sucesso completo termina com:

```text
SIMULAÇÃO VERIFICADA: protocolo, Nav2 e movimento confirmados
```

Um JSON `ACCEPTED` sem essa linha prova o contrato e a fila, mas não é evidência suficiente de movimento.

Não espere uma janela: o Gazebo usa tela virtual e renderização por software. Consulte o processo com:

```bash
make status
make logs
```

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

Na primeira inicialização, ROS 2, Gazebo, SLAM e Nav2 sobem em etapas. Abra outro terminal e execute:

```bash
make logs
```

Se a imagem ainda estiver sendo baixada ou construída, aguarde. Se o bridge não surgir após dois minutos do início do contêiner, faça o reinício limpo.

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

## Android mock

Na pasta `mobile/android`:

```bash
./gradlew :app:testMockDebugUnitTest
./gradlew :app:assembleMockDebug
```

No emulador, use `ws://10.0.2.2:18765`. No Motorola físico, use `ws://IP_DO_COMPUTADOR:18765`; celular e computador precisam alcançar a mesma rede local. O flavor mock aceita API 26+, enquanto o DAT real exige o nível definido pelo sample oficial.

## iOS mock

Em um Mac com Xcode e XcodeGen:

```bash
cd mobile/ios
xcodegen generate
open MaestroAgricola.xcodeproj
```

Escolha o iPhone 13 como destino, configure a assinatura e substitua `127.0.0.1` pelo IP do computador que executa o bridge. No iPhone, `127.0.0.1` aponta para o próprio telefone.

## Evidência mínima para a entrega

Registre, sem mídia bruta:

1. saída de `make test-quick`;
2. JSON `ACCEPTED` do `make demo`;
3. trecho de log mostrando a meta de navegação;
4. uma recusa local por intenção ou confirmação inválida;
5. versão do build mock executado em cada aparelho.
