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
- lifecycle atual de navegação sem dock/undock implícito: `SPRAY` navega e permanece no destino;
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

## Validação rápida do estado atual

A `main` está em uma fase de transição: a **Task 1 já removeu o dock/undock automático do bridge**, enquanto os comandos explícitos `DOCK` e `UNDOCK` ainda serão implementados nas próximas tasks.

O comportamento canônico atual é:

```text
SPRAY
-> validação
-> Nav2 até o plot
-> completion
-> READY / idle
-> robô permanece no destino
```

Se o bridge sabe que o robô está dockado, `SPRAY` deve ser rejeitado. Ele não pode executar `Undock` implicitamente.

### Importante sobre os wrappers antigos de demo

Alguns wrappers/scripts `make demo*` ainda foram escritos para o lifecycle antigo:

```text
undock automático -> missão -> retorno automático -> dock
```

Enquanto a Task 7 não atualizar esses gates, **não use a mensagem final de `make demo`, `make demo-route` ou `make demo-visual` como fonte de verdade do lifecycle atual**. O gate canônico desta fase é a suíte focada + o smoke test manual descrito abaixo.

### Pré-requisitos

- Linux com Python 3.10 ou superior;
- Docker Engine ativo e acessível pelo usuário;
- Docker Compose v2 ou superior;
- GNU Make;
- para o modo visual NVIDIA: driver NVIDIA, NVIDIA Container Toolkit e sessão X11.

ROS 2 e Gazebo rodam dentro do contêiner.

### 1. Verifique o ambiente

```bash
make doctor
```

Todos os itens obrigatórios devem aparecer como `[OK]`.

### 2. Verifique o artefato da IA sem regenerá-lo

```bash
python3 tools/train_intent_model.py --check
```

O comando deve terminar com status zero e indicar que os artefatos estão em dia.

O checker tolera apenas ruído irrelevante de ponto flutuante. **Não execute `make model` apenas para eliminar diferenças numéricas microscópicas.**

### 3. Execute as suítes Python portáteis

Em hosts onde o `pytest` do ambiente Conda carrega plugins ROS externos (`launch_pytest`) e falha antes dos testes com dependências como `lark`, desative apenas o autoload de plugins para estas suítes que não dependem de `launch_pytest`:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest tests -q
```

Para o bridge:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
python3 -m pytest robot_ws/src/maestro_robot_bridge/test -q
```

O teste específico que protege a comparação determinística dos artefatos da IA é:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest tests/test_train_intent_model.py -q
```

### 4. Confira a visão estática

```bash
make vision-smoke
```

A saída esperada contém três resultados `"status": "DETECTED"`, um para cada ID de `plot-01` a `plot-03`.

### 5. Abra a simulação visual

```bash
make gazebo
```

Na primeira execução, aguarde o mundo, sensores, Nav2 e TurtleBot terminarem de inicializar.

Antes de testar movimento:

1. confirme que o Gazebo está em **Play** e não pausado;
2. confirme que o serviço está ativo:

```bash
docker compose --profile visual ps
```

3. confirme que o bridge escuta a porta:

```bash
ss -ltnp | grep 18765
```

Esperado:

```text
0.0.0.0:18765
```

No HMI do TurtleBot use o namespace:

```text
turtlebot1
```

Enquanto `UNDOCK` ainda não estiver integrado ao app, faça `Undock` manualmente no HMI antes de enviar `SPRAY`.

### 6. Rode o smoke test Android/voz

No dispositivo físico, configure o WebSocket para o IP LAN do computador e use o caso principal:

```text
"pulverizar o plot 02"
-> IA: SPRAY
-> confirmação: "sim"
-> bridge: navigation goal queued
-> Nav2 chega ao plot-02
-> robô permanece no plot-02
```

A seção [Smoke tests Android → IA → ROS → TurtleBot](#smoke-tests-android--ia--ros--turtlebot) detalha os casos.

### 7. Consulte logs quando necessário

```bash
make status
make logs
```

Para acompanhar a simulação continuamente:

```bash
make simulation-logs
```

Ou filtre os eventos relevantes:

```bash
docker compose --profile visual logs -f simulation-gui | \
grep --line-buffered -E "Nav2|dock|Dock|Undock|return|maestro_robot_bridge"
```

Depois de um `SPRAY` normal, não deve aparecer retorno automático para a doca iniciado pelo bridge.

### 8. RViz2 opcional

Com a simulação visual ativa:

```bash
make rviz
```

O RViz mostra mapa, pose estimada, LiDAR, costmaps e planos. O cenário 3D atual usa o mundo `warehouse` do simulador do TurtleBot 4 com as placas `PLOT-01`, `PLOT-02` e `PLOT-03` adicionadas pelo Maestro.

### 9. Encerre

```bash
make simulation-down
```

Durante o encerramento, mensagens de `SIGINT`, `SIGTERM`, `process has died` ou código `-15` podem representar apenas a finalização normal dos processos.

O guia mais detalhado continua em [`docs/testing.md`](docs/testing.md).

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

## Testando o aplicativo Android com o simulador

O aplicativo Android envia comandos para o `maestro_robot_bridge` por WebSocket na porta `18765`.

### Endereço do WebSocket

O endereço depende de onde o aplicativo está sendo executado.

**Emulador Android:**

```text
ws://10.0.2.2:18765
```

No emulador, `10.0.2.2` é o endereço especial usado para acessar a máquina host.

**Celular ou tablet físico:**

Use o endereço IPv4 do computador Ubuntu na mesma rede Wi-Fi.

Descubra o IP do computador com:

```bash
hostname -I
```

Exemplo:

```text
192.168.1.9
```

No aplicativo:

```text
ws://192.168.1.9:18765
```

Não use `10.0.2.2` em um dispositivo Android físico.

Confirme que o bridge está escutando:

```bash
ss -ltnp | grep 18765
```

Esperado:

```text
0.0.0.0:18765
```

Confirme também que a simulação está ativa:

```bash
docker compose --profile visual ps
```

### Antes dos testes

1. Inicie/recompile a simulação quando houver alterações no código ROS do container.
2. Aguarde Nav2 e o TurtleBot terminarem a inicialização.
3. Confirme que o Gazebo não está pausado.
4. No HMI do TurtleBot, use o namespace:

```text
turtlebot1
```

5. Se o robô estiver dockado, comandos normais de navegação são rejeitados. Faça `Undock` explicitamente/manualmente até a intent `UNDOCK` estar integrada ao aplicativo.

---

## Smoke tests Android → IA → ROS → TurtleBot

### Caso 1 — Pulverizar plot 02

Fale ou digite:

```text
pulverizar o plot 02
```

Esperado:

```text
IA: SPRAY
Estado: AWAITING_CONFIRMATION
```

Confirme falando ou digitando:

```text
sim
```

Esperado no aplicativo:

```text
Estado: ACCEPTED
navigation goal queued
```

Esperado no bridge:

```text
Nav2 accepted command ... for target plot-02
...
Nav2 completed command ... for target plot-02
```

O robô deve chegar ao `plot-02` e permanecer no destino.

Ele NÃO deve retornar automaticamente para a doca.

### Caso 2 — Variação de linguagem

Teste também frases semanticamente equivalentes, por exemplo:

```text
pulverizar o talhão 2
pulverize o plot 02
vá pulverizar o talhão dois
pulverização no plot 2
```

Registre quais frases foram reconhecidas corretamente e quais resultaram em `UNKNOWN` ou classificação incorreta.

Para testes por voz, registre também a **transcrição produzida pelo ASR**. O dado útil para a evolução da IA é:

```text
frase pretendida | transcrição ASR | intent esperada | target | resultado
```

Essas variações e transcrições reais devem alimentar o corpus/benchmark definido nas Tasks 6A–6F. A métrica perfeita do conjunto atual não deve ser tratada como prova de robustez para paráfrases reais.

### Caso 3 — Confirmação por voz

Com uma ação aguardando confirmação, fale:

```text
sim
```

Esperado:

```text
CONFIRM
```

e somente então o comando pode ser enviado ao robô.

### Caso 4 — Cancelamento

Inicie uma ação e, durante a confirmação, fale:

```text
cancelar
```

Esperado:

```text
CANCEL
```

Nenhuma navegação deve ser enviada ao robô.

### Caso 5 — Robô dockado

Com `dock_status=true`, tente:

```text
pulverizar o plot 02
```

e confirme.

Esperado:

```text
robot unavailable: robot is docked
```

O bridge não deve executar `Undock` automaticamente.

### Comandos de doca ainda não são gate desta fase

Até as Tasks 2–6 estarem concluídas, frases como:

```text
voltar para a doca
vá para a dock
dock the robot
sair da doca
undock
```

não devem ser usadas como evidência de E2E concluído. O roadmap em [`TASKS.md`](TASKS.md) separa contrato, bridge ROS, transporte Android e evolução da IA para esses comandos.

### Logs úteis

Para acompanhar a missão:

```bash
docker compose --profile visual logs -f simulation-gui | \
grep --line-buffered -E "Nav2|dock|Dock|Undock|return|maestro_robot_bridge"
```

Para uma missão `SPRAY` normal, após:

```text
Nav2 completed command ... for target plot-XX
```

não deve aparecer um retorno automático para a doca.

## Ambiente mobile da demonstração

| Ambiente | Papel | Evidência do MVP/pitch |
|---|---|---:|
| Android físico compatível com o DAT + Meta Wearables | `datDebug`, câmera dos óculos, áudio Android e IA local | Sim |
| Emulador ou `mockDebug` | desenvolvimento, testes automatizados e contingência | Não substitui a demo com os óculos |

## Próximas tarefas críticas

A ordem executável está em [`TASKS.md`](TASKS.md). O estado atual é:

1. **Task 1 — concluída:** remover dock/undock automático.
2. **Task 2 — próxima:** adicionar `DOCK`/`UNDOCK` ao contrato sem executar actions.
3. **Task 3:** executar `UNDOCK` explícito no bridge.
4. **Task 4:** executar `DOCK` explícito com Nav2 até a aproximação da doca e depois action `Dock`.
5. **Task 5:** transportar as intents reais no Android sem target fictício e mantendo confirmação.
6. **Tasks 6A–6F:** construir corpus real de fala/ASR, medir o baseline, comparar alternativas locais e testar no smartphone-alvo de 6/8 GB antes de escolher o backend de IA.
7. **Task 7:** E2E final por voz, atualização dos wrappers de demo e documentação final.

A IA atual continua sendo o baseline funcional, mas pequenas paráfrases já mostraram que o conjunto de avaliação existente não mede toda a robustez necessária. A troca de modelo só deve acontecer depois de benchmark reproduzível no mesmo corpus e no hardware-alvo.

Comece pelo índice em [`docs/README.md`](docs/README.md).

## Trabalho em equipe

A equipe usa `main` sempre demonstrável e branches curtas por tarefa, sem branches permanentes por pessoa. Consulte [`CONTRIBUTING.md`](CONTRIBUTING.md) para nomes das frentes, responsabilidades, revisão e checklist de merge.
