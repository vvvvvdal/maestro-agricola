# Interface Android de demonstração

Status: concluída em 21 de agosto de 2026

Responsável: Átila (app Android/Kotlin)

Referência: `TASKS.md`, prioridade 2 — "Melhorias da interface Android"

## Objetivo

Transformar a tela diagnóstica do MVP em uma interface de demonstração, na qual
um avaliador consiga acompanhar a jornada `olhar -> falar -> confirmar ->
executar` sem explicação verbal e sem ler logs.

A tarefa é exclusivamente de apresentação Android. Contrato JSON, bridge ROS,
modelo de IA e lifecycle de missão não foram alterados.

## Ambiguidades resolvidas antes da implementação

- **Confirmação por toque:** não foi adicionada. `AGENTS.md` exige confirmação
  explícita por áudio, então a tela continua exigindo fala (ou, em contingência,
  transcrição digitada) para confirmar. Apenas o cancelamento ganhou um botão,
  porque cancelar nunca envia movimento.
- **Estado do robô:** o bridge responde `ACCEPTED` quando valida e enfileira o
  comando, não quando o robô conclui a manobra, e não há canal de telemetria no
  contrato atual. O cartão foi rotulado `ROBÔ · ÚLTIMO COMANDO ACEITO` e
  descreve o comando aceito, nunca uma posição confirmada.
- **Elementos de diagnóstico:** endpoint WebSocket e transcrição digitada
  continuam necessários para a demonstração em aparelho físico e como
  contingência do microfone. Em vez de removê-los, foram recolhidos em um painel
  "Ajustes de teste", fechado por padrão.
- **Marca:** o cabeçalho preserva o lockup horizontal com o mesmo enquadramento
  aprovado em [`visual-identity-v2.md`](visual-identity-v2.md), sem redesenho.
- **Cor de falha:** a paleta oficial não tem vermelho. O estado de recusa usa a
  cor semântica de erro do Material 3 (`#B3261E`), declarada como sinal de
  sistema e não como cor de marca.

## Critérios de aceite

- [x] A jornada aparece como uma trilha de quatro passos com estado por passo.
- [x] Alvo detectado, intenção reconhecida, confirmação pendente, comando
      enviado e estado do robô têm destaque próprio na tela.
- [x] A confirmação pendente mostra contagem regressiva do timeout e a frase
      esperada do operador.
- [x] Cancelamento, ambiguidade e recusa nunca aparecem visualmente como
      execução.
- [x] `DOCK` e `UNDOCK` marcam o passo de alvo como dispensado, não como
      pendente.
- [x] As mensagens de voz falam português natural (`talhão 3`, não `plot-03`) e
      orientam o próximo passo.
- [x] Endpoint e transcrição digitada continuam disponíveis, porém recolhidos.
- [x] O conteúdo rola e respeita as barras do sistema com `targetSdk = 36`.
- [x] Testes unitários do mock continuam passando.

## Mudanças

### Domínio

- `domain/CommandNaming.kt` (novo): `plotLabel` e `actionLabel`, usados tanto
  pelo TTS quanto pela tela, para não duplicar vocabulário.
- `domain/InteractionEngine.kt`:
  - `InteractionResult` passou a carregar `intent`, `targetId` e `targetSource`;
    todo resultado é um retrato completo da jornada, então a tela destaca alvo e
    intenção sem consultar o motor;
  - mensagens de voz reescritas por intent, incluindo o anúncio do comando
    aceito e a recusa sem ler o motivo técnico em inglês;
  - `CONFIRMATION_TIMEOUT_SECONDS` virou constante compartilhada com a tela.
  - As transições de estado, as regras de alvo e a exigência de confirmação não
    mudaram.

### Interface

- `ui/JourneyPresentation.kt` (novo): mapeamento puro entre estado e
  apresentação — trilha da jornada, tom de cor, rótulos e cartão do robô. Fica
  fora do Compose para ser coberto por teste unitário.
- `ui/MaestroScreen.kt` (novo): a tela em si — cabeçalho com marca e chips de
  contexto, cartão de estado com contagem regressiva, trilha da jornada,
  cartões de alvo/intenção/robô, ações e painel recolhível de ajustes.
- `ui/MaestroTheme.kt`: tints de apoio derivados da paleta e cores semânticas de
  erro no `colorScheme`.
- `MainActivity.kt`: ficou apenas com composição de dependências, permissão de
  microfone, contagem regressiva e roteamento de eventos.

## Evidências

- `./gradlew :app:testMockDebugUnitTest`: 32 testes aprovados, sendo 11 do
  conjunto de segurança já existente, 11 novos de retrato/voz do motor, 7 de
  apresentação, 2 do classificador e 1 do resolvedor de alvo.
- `./gradlew :app:assembleMockDebug`: aprovado.
- Inspeção visual no emulador (`mockDebug`, Android 16, API 36), com captura de
  tela por estado:
  - `IDLE`: passo 1 ativo, cartões vazios com orientação;
  - `TARGET_READY`: `plot-03` resolvido pela câmera, passo 1 concluído;
  - `AWAITING_CONFIRMATION`: cartão amarelo, frase esperada, barra de contagem
    regressiva e `SPRAY · 100% · regra determinística`;
  - `CANCELLED` por timeout: `Nada foi enviado ao robô`, passo `Confirmar` em
    vermelho e `Executar` intocado.

## Limitações registradas

- `ACCEPTED` e `ERROR` foram validados por teste unitário do mapeamento, não por
  captura de tela: o bridge real depende de Docker/Linux e não roda neste host
  Windows.
- O host usa JDK 25 como padrão, incompatível com AGP 8.11.1. Os comandos Gradle
  foram executados com `JAVA_HOME` apontando para o JDK 21 disponível na
  máquina. Isso é limitação de ambiente, não do projeto.
- `assembleDatDebug` não foi executado: exige `GITHUB_TOKEN` com `read:packages`
  para os artefatos do Meta Wearables DAT, ausente neste host. O código alterado
  está todo em `src/main`, compartilhado pelos dois flavors, e o único arquivo
  específico do flavor `dat` não foi tocado.
- O estado do robô continua sendo inferido do último comando aceito. Telemetria
  real exigiria mudança de contrato e pertence a outra tarefa.
