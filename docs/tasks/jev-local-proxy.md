# Task: Proxy local Jev para `mockDebug`

## Status

Implementacao e jornada E2E no Gazebo validadas em 24/09/2026. O modo e
somente demonstrativo no `mockDebug`; nao promove o Jev ao APK de producao nem
revoga `HOLD`.

## Fluxo e limites

```text
mockDebug -> 127.0.0.1:8787 -> adb reverse -> proxy loopback no notebook -> Jev
```

O endpoint no Android e fixo em `http://127.0.0.1:8787/v1/intent`; nao existe
campo editavel e o proxy escuta somente no loopback do notebook. O proxy aceita
somente `{"transcript":"..."}`, limita corpo e texto, fixa modelo e seis
criterios, nao registra texto ou chave e conta no maximo 24 tentativas HTTP
externas por processo, incluindo retry. O Android nao recebe
`TYPESAFE_API_KEY`; falha retorna `UNKNOWN`.

O operador precisa marcar no app que usara fala de teste sem dados pessoais.
Como barreira complementar, o proxy recusa e-mail, telefone e URL evidentes;
isso nao substitui julgamento humano nem anonimização completa. Alvo,
estado do robô, `Command`, WebSocket e ROS nunca seguem para o Jev. O Jev
devolve somente uma escolha entre os seis rótulos. No flavor `mock`, uma
escolha remota que atravesse a confirmação explícita gera o mesmo `Command`
estruturado do classificador local e o envia ao bridge do Gazebo. `dat` não
oferece Jev remoto; hardware físico não faz parte desta demonstração.

O subteto aprovado e US$0,10. O proxy so sera executado depois dos testes e
deve usar `TYPESAFE_API_KEY` no terminal, seguido de `adb reverse tcp:8787
tcp:8787`. O app bloqueia controles de entrada enquanto uma avaliação está
pendente, evitando chamadas concorrentes acidentais.

## Operação local após a validação

```bash
python3 tools/jev_local_proxy.py --max-requests 24
/home/felipe/Android/Sdk/platform-tools/adb reverse tcp:8787 tcp:8787
```

No `mockDebug`, abra `Ajustes de teste`, marque a fala de teste sem dados
pessoais e selecione `Jev remoto (Gazebo)`. Para usar um tablet sem Wi-Fi,
execute também `adb reverse tcp:18765 tcp:18765` e informe
`ws://127.0.0.1:18765` no endpoint do app. Para encerrar, selecione `Local`,
pare o proxy e execute `adb reverse --remove tcp:8787` e
`adb reverse --remove tcp:18765`.

Os cenarios visuais estaticos e o diagnostico de fixture foram removidos:
`Local` usa o classificador local real e `Jev remoto (Gazebo)` usa somente a resposta
real do proxy. O cartao `INTENCAO` identifica a origem escolhida.

## Evidência de validação

No SM-X510, com o APK `mockDebug` e o proxy loopback ativos, uma fala curta e
consentida de comando de doca foi classificada pela chamada remota como `DOCK`
com origem visível `Jev` e 100% para a opção escolhida. Ela entrou em
confirmação e expirou sem confirmação. O cartão do robô permaneceu
"Aguardando comando"; nenhum `Command`, WebSocket ou ROS foi executado nessa
validação inicial.

Os testes portáteis do proxy (4), os testes Kotlin focados (17) e
`assembleMockDebug` passaram antes da instalação. A revisão Terra high aprovou
o endpoint fixo, o teto sincronizado, a declaração de dados, o bloqueio de
controles e o caminho sem bridge. A evidência não registra a fala, chave,
captura, logcat ou custo exato; o painel de uso do provedor é a fonte para
consumo acumulado.

## JEV-38 - comando no Gazebo

Em 23/09/2026, o bloqueio artificial entre uma confirmação Jev e o
`WebSocketCommandTransport` foi removido somente do flavor `mock`. O teste
focado `JevIntentClassifierTest` passou com nove testes, incluindo
`Jev -> CONFIRM -> Command(UNDOCK)`, e o `mockDebug` atualizado foi instalado
no SM-X510. O ambiente headless do Gazebo e o bridge WebSocket em `18765`
foram iniciados, com `adb reverse tcp:18765 tcp:18765` configurado.

Em 24/09/2026, no SM-X510 com consentimento de fala sem dados pessoais, a
jornada `Jev remoto (Gazebo) -> confirmacao por voz -> UNDOCK` foi executada
uma vez. O app informou que o comando foi aceito e que sairia da doca. O
bridge registrou `Requesting explicit undock action`, o simulador recebeu o
goal e o bridge confirmou `Undock goal accepted`. A consulta ROS posterior
reportou `is_docked: false`.

Nao foram persistidos audio, transcricao, chave, captura de tela ou logcat. Um
probe TCP local usado antes da jornada nao completou handshake WebSocket e
gerou um aviso isolado no log do bridge; ele nao veio do app e nao afetou o
aceite do comando. A evidencia E2E prova somente o caminho `mockDebug` para o
Gazebo; nao prova controle fisico, hardware DAT real ou adocao operacional do
Jev.
