# Maestro Agrícola

<p align="center">
  <img src="assets/brand/logo-horizontal.png" alt="Maestro Agrícola por AgroTurtles" width="760">
</p>

Interface hands-free para comandar maquinário agrícola autônomo com visão, voz e confirmação por áudio.

O Maestro Agrícola permite que o operador olhe para um alvo no campo, diga a ação desejada e confirme o comando sem interromper o trabalho para usar notebook ou tablet. O aplicativo companion interpreta a intenção, associa o alvo visual a uma posição conhecida e envia um comando estruturado ao robô.

> Estado: primeira implementação do MVP para o Programa AI Glasses Brasil 2026.

## Jornada principal

1. **Olhar:** a câmera dos óculos captura o alvo centralizado.
2. **Falar:** o operador diz a ação, por exemplo: “pulverizar esta área”.
3. **Confirmar:** o sistema responde por áudio e só executa após confirmação explícita.

## MVP do hackathon

O corte vertical demonstra o fluxo completo:

```text
AI Glasses ou mock -> app Kotlin -> IA local + alvo -> JSON/WebSocket -> ROS 2/Nav2/Gazebo
```

Para manter a demonstração verificável, o alvo do MVP será um marcador visual ou talhão previamente mapeado. A versão atual do Meta Wearables Device Access Toolkit (DAT) não expõe pose/IMU dos óculos; portanto, nenhuma parte crítica do MVP depende desse dado.

## Princípios

- Segurança: nenhum comando de movimento é enviado sem confirmação por áudio.
- Privacidade: imagens são processadas em memória e descartadas; não há persistência por padrão.
- Eficiência: captura sob demanda, sem streaming contínuo quando não for necessário.
- Portabilidade: integração com o robô por contrato JSON, sem acoplamento a um fabricante.
- Testabilidade: desenvolvimento antecipado com Mock Device Kit e ROS/Gazebo.

## O que já existe

- contrato JSON 1.0 com confirmação, expiração e UUID;
- classificador de intenção executado localmente no Android;
- app Android com flavors `mock` (API 26+) e `dat` (API 31+);
- bridge WebSocket/ROS 2 com rejeição de comando inseguro e deduplicação;
- cenário do Gazebo com três placas bifaciais (`plot-01` a `plot-03`), Nav2 e TurtleBot 4;
- resolvedor compartilhado que aceita alvo visual, ID falado ou concordância entre os dois e recusa conflitos;
- Dockerfile e Compose para reproduzir o simulador;
- simulador de óculos por terminal para testar sem hardware.

O adaptador do DAT real está isolado e ainda precisa receber o ciclo oficial de sessão e captura do sample `CameraAccess`. A jornada da semana usa o mock; a troca pelo hardware acontece depois que o sample funcionar no aparelho do evento.

## Estrutura

```text
.
├── AGENTS.md
├── README.md
├── contracts/           # schemas e fixtures JSON
├── mobile/
│   └── android/         # Kotlin, mock API 26+ e DAT API 31+
├── robot_ws/src/        # bridge ROS 2 e cenário Gazebo
├── shared/ai/           # dataset, modelo local e avaliação
├── tests/               # testes portáveis do modelo e do cliente mock
├── tools/               # treino, QR e simulador de óculos
└── docs/                # spec, arquitetura, tarefas, proposta e pitch
```

## Teste em 5 minutos

### Resposta curta: como saber se funciona

Na branch integrada, execute somente:

```bash
make test-quick
make demo
```

O segundo comando já inicia o contêiner, tira o robô da doca, envia o comando simulado, verifica Gazebo/Nav2 e espera o retorno à doca. **Não abra `127.0.0.1:18765` no navegador**: essa é uma porta WebSocket, não uma página. Também não é necessário executar `make simulation-logs` quando a demo passa.

A execução completa passou somente quando o final do terminal mostrar:

```text
DEMO APROVADA: undock, WebSocket, Nav2, movimento e dock verificados.
```

Depois, encerre com `make simulation-down`.

### Pré-requisitos

- Linux com Python 3.10 ou superior;
- Docker Engine ativo e acessível pelo usuário;
- Docker Compose v2 ou superior;
- GNU Make.

Não é necessário instalar ROS 2 ou Gazebo no computador: ambos ficam dentro do contêiner.

### 1. Verifique o ambiente

```bash
make doctor
```

Todos os itens obrigatórios devem aparecer como `[OK]`. É normal o bridge aparecer como `[INFO]` antes da primeira demo.

### 2. Execute os testes rápidos

```bash
make test-quick
```

Esse comando verifica o modelo sem regravá-lo, executa as suítes portáteis e do bridge e valida o Compose. Ele não inicia o Gazebo.

Confira também a placa completa sem abrir o Gazebo:

```bash
make vision-smoke
```

A saída esperada contém três resultados `"status": "DETECTED"`, um para cada ID de `plot-01` a `plot-03`.

### 3. Execute a jornada completa

```bash
make demo
```

Na primeira execução, o download e a construção da imagem podem levar vários minutos. Depois disso, o Gazebo costuma precisar de 1 a 2 minutos para inicializar em máquinas sem GPU. O cliente espera o bridge automaticamente.

O teste passou quando termina com uma resposta semelhante a:

```json
{
  "schema_version": "1.0",
  "command_id": "...",
  "status": "ACCEPTED",
  "reason": "navigation goal queued"
}
```

`ACCEPTED` significa que o mock classificou a intenção localmente, confirmou a ação, enviou o JSON e o bridge validou e enfileirou a meta do `plot-03`. O comando continua verificando Gazebo, Nav2, deslocamento real depois do aceite e o ciclo `undock → meta → dock`. A prova completa termina com `DEMO APROVADA`.

Para testar todos os pontos em uma única rota limpa, headless e acelerada pela NVIDIA:

```bash
make demo-route
```

Esse comando exige o mesmo driver/runtime NVIDIA do modo visual, encerra uma instância anterior, visita `plot-01`, `plot-02` e `plot-03` nessa ordem e só aprova quando o retorno à doca for confirmado. `make demo` permanece como teste portátil por software de um único plot.

> A execução padrão é **headless**: nenhuma janela do Gazebo será aberta. O resultado aparece no terminal e nos logs. Isso é esperado.

### 4. Consulte estado e logs

```bash
make status
make logs
```

Os logs não fazem parte do teste normal. Consulte-os somente se `make demo` terminar sem `DEMO APROVADA`. Para acompanhar continuamente, use `make simulation-logs`. Pressionar `Ctrl+C` nesse comando interrompe apenas a visualização dos logs; o contêiner continua rodando.

### 5. Encerre

```bash
make simulation-down
```

Durante o encerramento, ROS e Gazebo podem registrar `SIGINT`, `SIGTERM`, `process has died` ou código `-15`. Depois que você pediu `simulation-down`, essas mensagens descrevem a finalização dos processos e não invalidam uma demo anteriormente aprovada.

O guia completo, incluindo reinício limpo, erros conhecidos e testes mobile, está em [`docs/testing.md`](docs/testing.md).

## Comandos separados

Como alternativa, execute `make simulation-up` e depois `make demo-client`. Não interrompa o simulador com `Ctrl+C` antes de executar o cliente. Em celular físico, configure no app `ws://IP_DO_COMPUTADOR:18765`. A porta `18765` evita o conflito observado entre a `8765` e serviços do simulador.

O Compose executa Gazebo e sensores em uma tela virtual interna, portanto não exige liberar o monitor do computador para o contêiner. Em máquinas sem GPU, comandos recebidos enquanto o Nav2 termina de iniciar ficam na fila até ele estar realmente ativo.

## Ver o Gazebo e o RViz2 com a NVIDIA

O modo visual segue o fluxo que já funcionava no `pluginbot-turtlebot4`: Gazebo, ROS 2 e RViz rodam dentro do mesmo contêiner, com a sessão X11 do host e `gpus: all`. Ele exige driver NVIDIA, NVIDIA Container Toolkit e uma sessão Linux X11.

Primeiro abra uma simulação visual limpa:

```bash
make gazebo
```

Na primeira execução, aguarde o mundo terminar de baixar e carregar. O cache do Gazebo Fuel é preservado nas próximas aberturas. Quando o cenário aparecer, acompanhe uma jornada em outro terminal:

```bash
make demo-visual
```

Para ver mapa, robô, LiDAR, costmap e planos, abra em um terceiro terminal:

```bash
make rviz
```

`make gazebo` encerra uma instância anterior do projeto antes de iniciar a visual; não execute `make demo` enquanto ela estiver aberta, porque o teste padrão troca para o serviço headless. `make rviz` permanece no terminal até a janela ser fechada. Ao terminar, execute `make simulation-down`; além de remover o contêiner, o comando revoga a permissão X11 concedida ao usuário `root` do contêiner.

O Gazebo mostra o mundo 3D `warehouse`, o TurtleBot 4 e três placas bifaciais distribuídas: `PLOT-01` e `PLOT-02` em lados opostos da área central e `PLOT-03` no ponto original. O RViz mostra o mapa salvo, a pose estimada pelo AMCL, modelo do robô, LiDAR, costmap e planos global/local. Com as janelas abertas, `make demo-visual` envia e verifica o comando para acompanhar o movimento.

O cenário atual não é uma fazenda própria. `warehouse` e seu mapa de ocupação salvo vêm do simulador oficial do TurtleBot 4; o Maestro acrescenta as placas e usa AMCL com pose inicial na doca. As três poses seguras ficam no catálogo versionado do bridge. Esses são três artefatos diferentes: mundo 3D, mapa de ocupação e mapa lógico de alvos.

## Estado visual dos apps

O app Android/Compose já possui uma tela diagnóstica com fonte de frame, estado da jornada, resposta da IA, transcrição, endpoint WebSocket e botões para simular olhar, interpretar, falar e reiniciar. A identidade AgroTurtles também já está aplicada. Ainda é uma tela de MVP para teste, não uma interface final de produto.

Para abrir o app, siga [`mobile/android/README.md`](mobile/android/README.md); é necessário JDK 17, Android SDK e Android Studio ou aparelho via `adb`.

## Testar a escolha do alvo

Com ID visual e fala genérica, a câmera resolve o alvo:

```bash
python3 tools/target_resolver.py "pulverize aqui" --visual-target plot-03
```

Sem QR, a fala explícita pode resolver um alvo que exista no catálogo:

```bash
python3 tools/target_resolver.py "pulverize no plot três"
```

Se voz e câmera divergirem, a saída é `CONFLICT`, sem `target_id`, e o processo termina com status diferente de zero. Isso é o comportamento seguro esperado:

```bash
python3 tools/target_resolver.py "pulverize no plot quatro" --visual-target plot-03
```

## Ambiente mobile da demonstração

| Ambiente | Papel | Evidência do MVP/pitch |
|---|---|---:|
| Android físico compatível com o DAT + Meta Wearables | `datDebug`, câmera dos óculos, áudio Android e IA local | Sim |
| Emulador ou `mockDebug` | desenvolvimento, testes automatizados e contingência | Não substitui a demo com os óculos |

## Próximas tarefas críticas

1. Consultar o quadro executável em [`docs/tasks/mvp-week.md`](docs/tasks/mvp-week.md).
2. Compilar e rodar `datDebug` em um Android físico compatível com o DAT.
3. Parear os Meta Wearables e validar o sample `CameraAccess` no mesmo aparelho.
4. Conectar a leitura real do QR ao frame recebido pelo DAT; o resolvedor visual/falado e a prova estática já estão implementados.
5. Rodar a jornada cinco vezes e registrar latência/falhas.
6. Ensaiar a demo e o pitch de até 3 minutos.

Comece pelo índice em [`docs/README.md`](docs/README.md).

## Trabalho em equipe

A equipe usa `main` sempre demonstrável e branches curtas por tarefa, sem branches permanentes por pessoa. Consulte [`CONTRIBUTING.md`](CONTRIBUTING.md) para nomes das frentes, responsabilidades, revisão e checklist de merge.
