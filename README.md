# Maestro Agrícola

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
AI Glasses ou mock -> app Kotlin/Swift -> IA local + alvo -> JSON/WebSocket -> ROS 2/Nav2/Gazebo
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
- classificador local compartilhado por Android e iOS;
- app Android com flavors `mock` (API 26+) e `dat` (API 31+);
- app iOS para iPhone 13/iOS 17.2+;
- bridge WebSocket/ROS 2 com rejeição de comando inseguro e deduplicação;
- cenário do Gazebo com QR `plot-03`, Nav2 e TurtleBot 4;
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
│   ├── android/         # Kotlin, mock API 26+ e DAT API 31+
│   └── ios/             # Swift, iOS 17.2+
├── robot_ws/src/        # bridge ROS 2 e cenário Gazebo
├── shared/ai/           # dataset, modelo local e avaliação
├── tests/               # testes portáveis do modelo e do cliente mock
├── tools/               # treino, QR e simulador de óculos
└── docs/                # spec, arquitetura, tarefas, proposta e pitch
```

## Começo rápido

```bash
make test
make demo
```

`make demo` constrói e inicia o simulador em segundo plano, aguarda o bridge e envia um comando mock. A primeira inicialização pode levar cerca de um minuto. Para acompanhar a inicialização, use `make simulation-logs`; para encerrar, use `make simulation-down`.

Como alternativa, execute `make simulation-up` e depois `make demo-client`. Não interrompa o simulador com `Ctrl+C` antes de executar o cliente. Em celular físico, configure no app `ws://IP_DO_COMPUTADOR:18765`. A porta `18765` evita o conflito observado entre a `8765` e serviços do simulador.

O Compose executa Gazebo e sensores em uma tela virtual interna, portanto não exige liberar o monitor do computador para o contêiner. Em máquinas sem GPU, comandos recebidos enquanto o Nav2 termina de iniciar ficam na fila até ele estar realmente ativo.

## Compatibilidade mobile

| Aparelho | Execução do mock | DAT real |
|---|---:|---:|
| Motorola com Android 8+ | Sim, flavor `mockDebug` | Somente se tiver Android 12+ |
| iPhone 13 com iOS 17.2+ | Sim | Sim, sujeito ao hardware/firmware DAT |

## Próximas tarefas críticas

1. Consultar o quadro executável em [`docs/tasks/mvp-week.md`](docs/tasks/mvp-week.md).
2. Compilar e rodar `mockDebug` no Motorola e o projeto Swift no iPhone 13.
3. Implementar a leitura real do QR a partir do frame.
4. Validar o sample `CameraAccess` e ligar o adaptador DAT.
5. Rodar a jornada cinco vezes e registrar latência/falhas.
6. Ensaiar a demo e o pitch de até 3 minutos.

Comece pelo índice em [`docs/README.md`](docs/README.md).

## Trabalho em equipe

A equipe usa `main` sempre demonstrável e branches curtas por tarefa, sem branches permanentes por pessoa. Consulte [`CONTRIBUTING.md`](CONTRIBUTING.md) para nomes das frentes, responsabilidades, revisão e checklist de merge.
