# Teste integrado no Galaxy A17

Este é o roteiro de bancada para provar `Android → IA local → WebSocket → ROS 2/Nav2/Gazebo` e, depois, substituir a câmera mock pela captura real dos Meta Wearables via DAT.

## Estado real antes do teste

- `mockDebug` está implementado e retorna `plot-03` ao tocar em **Simular olhar**.
- IA local, confirmação, contrato e transporte WebSocket estão implementados.
- `datDebug` possui a dependência do DAT, mas `PlatformFrameSource` ainda é um adaptador provisório. Enquanto ele responder “Conecte aqui Wearables...”, a câmera real **não está integrada** e o teste DAT não pode ser marcado como aprovado.
- Voz e TTS usam Android; é preciso validar separadamente se o microfone e o áudio são roteados pelos óculos. O telefone é o fallback.

## Portabilidade da instalação

Não versione caminhos pessoais. O Android Studio do Felipe está em `~/Downloads/android-studio`, mas Átila e Rafael podem instalá-lo em qualquer lugar. Pela interface, use **File → Settings → Build Tools → Gradle → Gradle JDK** e selecione o JDK embutido 17 ou superior.

No terminal, cada integrante pode configurar somente a sessão atual. Exemplo do Felipe:

```bash
export JAVA_HOME="$HOME/Downloads/android-studio/jbr"
export PATH="$JAVA_HOME/bin:$PATH"
```

Ou, sem alterar o ambiente do terminal, informe os caminhos diretamente:

```bash
python3 mobile/android/tools/preflight.py \
  --java-home "$HOME/Downloads/android-studio/jbr" \
  --sdk-dir "$HOME/Android/Sdk"
```

Átila e Rafael substituem somente esses dois argumentos pelos caminhos das próprias máquinas.

O SDK deve ser apontado em `mobile/android/local.properties`, que não deve ser commitado:

```properties
sdk.dir=/caminho/individual/Android/Sdk
```

## Gate 1 — preparar o Galaxy A17

1. Ative **Opções do desenvolvedor** tocando sete vezes em **Número da versão**.
2. Ative **Depuração USB**.
3. Conecte com cabo de dados, desbloqueie o aparelho e aceite a chave RSA.
4. Na raiz do repositório, execute:

```bash
python3 mobile/android/tools/preflight.py --require-device
```

Todos os itens devem aparecer como `[OK]`. Se o aparelho estiver `unauthorized`, desbloqueie-o e aceite novamente; se não aparecer, troque cabo/porta USB e confirme que o modo USB permite dados.

## Gate 2 — app físico com câmera mock

Este gate valida o telefone, a IA e o robô sem atribuir o resultado aos óculos.

No computador:

```bash
make test-quick
make simulation-up
hostname -I
```

Use no app um IP da rede local do computador, nunca `127.0.0.1` nem `10.0.2.2`. Computador e Galaxy devem estar na mesma rede e a porta TCP `18765` precisa estar liberada no firewall.

No Android Studio, selecione a variante `mockDebug`, escolha o Galaxy A17 e pressione **Run**. Alternativamente:

```bash
cd mobile/android
./gradlew :app:installMockDebug
```

No app:

1. confirme `Fonte: mock`;
2. informe `ws://IP_DO_COMPUTADOR:18765`;
3. toque **Simular olhar** — deve aparecer `plot-03`;
4. escreva ou fale “pulverize aqui” e toque **Interpretar**;
5. confira `IA: SPRAY (..., RULE)` e o estado de confirmação;
6. escreva ou fale “sim” e interprete em até 10 segundos;
7. confira aceite do transporte e movimento no Gazebo;
8. repita com “cancelar” e confirme que nenhum novo comando é enviado.

Evidência mínima: uma captura da tela do app, `make logs` mostrando o comando aceito e a recusa sem movimento.

## Gate 3 — DAT e óculos reais

Execute somente depois de substituir o adaptador provisório pelo ciclo oficial de sessão/câmera do sample `CameraAccess` da versão fixada do DAT.

1. Configure credenciais apenas em `local.properties` ou variável de ambiente; nunca versione tokens.
2. Compile e instale `datDebug`.
3. Pareie os Meta Wearables pelo fluxo oficial.
4. Centralize uma única placa e capture um frame sob demanda.
5. Confirme que o ID visual chegou ao mesmo `InteractionEngine` usado pelo mock.
6. Faça a jornada “olhar → falar → ouvir confirmação → confirmar → robô”.
7. Teste desconexão, QR ilegível, conflito entre QR e ID falado, cancelamento e timeout.
8. Registre latência, temperatura, bateria inicial/final e rota real de microfone/TTS.

O gate só passa se a imagem vier dos óculos. Digitar `plot-03`, usar a câmera do telefone ou executar `mockDebug` não comprova DAT.

## Localização rápida de falhas

| Sintoma | Camada provável | Primeira verificação |
|---|---|---|
| Galaxy não aparece | USB/ADB | `adb devices` e autorização RSA |
| App não compila | JDK/SDK | `preflight.py --require-device` |
| “Conecte aqui Wearables...” | adaptador DAT | implementação de `PlatformFrameSource` |
| Voz não transcreve | permissão/rota de áudio | permissão de microfone e teste pelo telefone |
| `UNKNOWN` | IA local | frase, confiança e origem `RULE/MODEL` na tela |
| WebSocket falha | rede/firewall | IP do computador, mesma rede e porta `18765` |
| `ACCEPTED`, mas não move | ROS/Nav2 | `make status` e `make logs` |
| QR e voz discordam | regra de segurança | esperado: cancelar sem enviar comando |

## Encerramento

```bash
make simulation-down
```

Não declare DAT, áudio Bluetooth ou consumo como validados até o Gate 3 passar no hardware real.
