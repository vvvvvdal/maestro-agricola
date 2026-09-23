# Task: Proxy local Jev para `mockDebug`

## Status

Implementacao validada em 23/09/2026. O modo e somente demonstrativo no
`mockDebug`; nao promove o Jev ao APK de producao nem revoga `HOLD`.

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
estado do robô, `Command`, WebSocket e ROS nunca seguem para o Jev. Se uma
intenção remota chegar a `ACCEPTED` após confirmação, o `Command` é bloqueado
antes do bridge: a demonstração não movimenta o robô.

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
pessoais e selecione `Jev remoto`. Para encerrar, selecione `Local`, pare o
proxy e execute `adb reverse --remove tcp:8787`.

Os cenarios visuais estaticos e o diagnostico de fixture foram removidos:
`Local` usa o classificador local real e `Jev remoto` usa somente a resposta
real do proxy. O cartao `INTENCAO` identifica a origem escolhida.

## Evidência de validação

No SM-X510, com o APK `mockDebug` e o proxy loopback ativos, uma fala curta e
consentida de comando de doca foi classificada pela chamada remota como `DOCK`
com origem visível `Jev` e 100% para a opção escolhida. Ela entrou em
confirmação e expirou sem confirmação. O cartão do robô permaneceu
"Aguardando comando"; nenhum `Command`, WebSocket ou ROS foi executado.

Os testes portáteis do proxy (4), os testes Kotlin focados (17) e
`assembleMockDebug` passaram antes da instalação. A revisão Terra high aprovou
o endpoint fixo, o teto sincronizado, a declaração de dados, o bloqueio de
controles e o caminho sem bridge. A evidência não registra a fala, chave,
captura, logcat ou custo exato; o painel de uso do provedor é a fonte para
consumo acumulado.
