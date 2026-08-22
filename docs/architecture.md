# Arquitetura

## Visão geral

```text
AI Glasses
  câmera via DAT + rota de áudio do sistema
          |
          v
App companion Android/Kotlin
  alvo + voz local
          |
          +-> LocalIntentClassifier
          |      +-> intenção operacional -> InteractionEngine -> confirmação -> Command
          |      +-> UNKNOWN -> LanguageRouter -> QwenDomainAssistant -> CHAT | OUT_OF_SCOPE
          |
          v
WebSocket / JSON versionado (somente Command confirmado)
          |
          v
Bridge ROS 2 -> Nav2 / Gazebo -> robô simulado
```

A separação entre controle e conversa é uma restrição arquitetural. O Qwen não tem acesso a `CommandTransport`, ROS, WebSocket, pose, alvo resolvido nem estado do robô. A `MainActivity` usa `LanguageInteractionController` para manter operações e confirmações no `InteractionEngine` e encaminhar somente `UNKNOWN`, nos estados seguros `IDLE` ou `TARGET_READY`, ao assistente.

## Componentes

### AI Glasses

- Entrada visual por stream ou captura do DAT.
- Entrada e saída de voz pela rota Bluetooth disponível no sistema mobile, com microfone e alto-falante do telefone como fallback.
- Sem display e sem lógica pesada embarcada.

O DAT é usado para sessão e câmera. O reconhecimento de fala e o TTS pertencem às APIs nativas do Android; a rota de microfone e áudio dos óculos deve ser validada no hardware e não é tratada como uma API de áudio do DAT.

### Companion app

- Gerencia registro, sessão, permissões e ciclo de vida do stream.
- Captura voz e frame de forma coordenada.
- Detecta a placa `PLOT-03` ou extrai um ID de plot explicitamente falado.
- Exige concordância quando voz e câmera identificam alvos simultaneamente.
- Converte a fala em uma intenção restrita.
- Executa a máquina de estados de confirmação.
- Envia comandos idempotentes ao bridge.

Existe uma única implementação nativa Android/Kotlin. Na entrega pré-hardware de 22/08/2026, `datDebug` foi executado no Android físico com o MockDeviceKit explicitamente habilitado; `mockDebug` continua isolando a fonte simulada de desenvolvimento. O mesmo flavor `dat` será usado sem MockDeviceKit no gate de hardware real, caso a equipe avance. Não há React Native.

### Bridge ROS 2

- Valida versão, schema e identificador do comando.
- Rejeita duplicatas e comandos expirados.
- Mapeia `target_id` para uma pose conhecida no cenário.
- Publica a meta para o stack de navegação.

## Decisão técnica: alvo do MVP

O DAT atual oferece câmera, captura de foto, sessão e Mock Device Kit, mas não expõe pose/IMU dos óculos. O MVP não tentará inferir coordenadas métricas somente pela direção da cabeça.

Para a demonstração, o frame identifica uma placa humana/máquina com o texto e o QR `plot-03`, previamente associado a uma pose do cenário. “Pulverize aqui” depende desse alvo visual; “pulverize no plot-03” pode fornecer o ID por voz. Divergência entre as duas fontes falha de forma segura. Essa escolha:

- preserva a interação “olhar, falar e confirmar”;
- elimina uma dependência inexistente no SDK;
- permite teste determinístico antes do hardware;
- mantém o escopo de interface para maquinário agrícola.

Poeira e obstrução continuam sendo riscos do marcador. Uma evolução posterior pode usar placas industriais redundantes, geofencing como contexto, localização visual contra mapa do campo, fusão com telemetria do robô ou uma futura API de pose do dispositivo. GPS do celular sozinho não informa a direção da cabeça nem vira destino do robô.

## Interfaces para integração antecipada

- `FrameSource`: `PlatformFrameSource` selecionado pelo flavor. A API é assíncrona, entrega somente `TargetObservation` e permite cancelar/encerrar a captura.
- `TargetDetector`: recebe uma foto em memória (`Bitmap` ou HEIC), decodifica o QR e retorna `target_id` e timestamp. Como o leitor de QR não produz probabilidade calibrada, essa fronteira não inventa confiança.
- `TargetResolver`: combina alvo visual e ID falado com estados `RESOLVED`, `NEEDS_VISUAL`, `CONFLICT` ou `UNKNOWN`.
- `IntentClassifier`: recebe a transcrição e retorna rótulo e confiança.
- `LanguageRouter`: mantém qualquer rótulo diferente de `UNKNOWN` no caminho operacional e reserva somente `UNKNOWN` ao assistente.
- `DomainAssistant`/`QwenDomainAssistant`: retorna somente `CHAT` ou `OUT_OF_SCOPE`; saída inválida falha para `OUT_OF_SCOPE`.
- `QwenEngine`: fronteira assíncrona do runtime local; não conhece `Command` nem transporte do robô.
- `CommandTransport`: envia somente o `Command` confirmado produzido pelo `InteractionEngine` e correlaciona a resposta por `command_id`.

Essas fronteiras permitem desenvolver mobile, IA, visão e ROS 2 em paralelo sem esperar pelos óculos.

No flavor `dat`, o ciclo compatível com DAT 0.9.0 é: permissões Android,
`Wearables.initialize()`, seleção do dispositivo, criação da `DeviceSession`,
`DeviceSession.addCamera()`, início do stream, `capturePhoto()` e encerramento da
câmera e da sessão. A propriedade de build `maestroDatMockDevice=true` prepara
explicitamente um dispositivo simulado com o MockDeviceKit. Sem a propriedade,
o mesmo flavor permanece no caminho de registro e hardware real; não existe
fallback silencioso para simulação.

## Contrato de comando

Exemplo inicial:

```json
{
  "schema_version": "1.0",
  "command_id": "9f9a8ef8-94b9-4f4e-a436-92357e5a7a20",
  "created_at": "2026-08-16T15:00:00Z",
  "expires_in_ms": 5000,
  "intent": "SPRAY",
  "target": {
    "type": "MAPPED_PLOT",
    "id": "plot-03"
  },
  "confirmed": true
}
```

Resposta esperada:

```json
{
  "schema_version": "1.0",
  "command_id": "9f9a8ef8-94b9-4f4e-a436-92357e5a7a20",
  "status": "ACCEPTED",
  "reason": "navigation goal queued"
}
```

## Máquina de estados

```text
IDLE -> CAPTURING -> INTERPRETING -> AWAITING_CONFIRMATION
  -> SENDING -> ACCEPTED -> IDLE
  -> CANCELLED / AMBIGUOUS / TIMEOUT / CONNECTION_ERROR -> IDLE
```

## Privacidade e segurança

- Frame e áudio ficam somente em memória durante a interação.
- Logs contêm IDs, estados, latência e erros, nunca mídia bruta.
- O app deve habilitar o opt-out de analytics opcionais do DAT quando essa configuração estiver disponível e for compatível com as regras do programa.
- A política de privacidade deve distinguir o que o Maestro processa do que Android, Meta AI e DAT podem tratar para conexão, permissões e telemetria.
- Comando inclui expiração, ID único e confirmação explícita.
- O bridge deduplica `command_id`.
- O Maestro não substitui as proteções funcionais e a navegação segura do robô.

## Eficiência

- Preferir captura sob demanda a streaming contínuo.
- Manter modelos pequenos e intenções restritas.
- Interromper câmera, áudio e sessão quando a jornada terminar.
- Medir latência, temperatura e bateria com os Meta Wearables reais na fase presencial, se a equipe avançar.

## IA local compartilhada

### Caminho operacional

O classificador operacional continua pequeno, determinístico na borda e independente de LLM. O artefato `shared/ai/intent_model.json` contém seis rótulos: `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`. Regras de alta precisão tratam sinais inequívocos e o classificador linear softmax resolve os demais casos; baixa confiança falha para `UNKNOWN`.

A avaliação histórica de 64 frases cobre as quatro classes originais e continua útil para regressão. Para a evolução com `DOCK`/`UNDOCK`, o corpus `field_evaluation.tsv` contém 48 frases balanceadas entre os seis rótulos e o baseline local classificou 48/48 no gate usado durante a Task 6.

### Assistente Qwen isolado

Qwen2.5-1.5B-Instruct Q4_K_M foi avaliado inicialmente como possível classificador operacional e rejeitado: 36/48, acurácia 0,75, macro-F1 0,7384 e 3 aceites perigosos. A decisão é não substituir `LocalIntentClassifier`.

O modelo foi então restrito ao papel de assistente de domínio. `LanguageRouter` envia somente `UNKNOWN` para `QwenDomainAssistant`. O system prompt canônico limita o domínio ao Maestro Agrícola e a GBNF permite apenas JSON com `CHAT` ou `OUT_OF_SCOPE`. O parser Kotlin normaliza `OUT_OF_SCOPE` para uma mensagem fixa e qualquer JSON inválido ou tipo desconhecido também falha fechado.

O runtime Android usa `llama.cpp` pinado em `873e5d8e39feb34a376e0efd01bf3f665dfffeb5`, JNI/CMake ARM64, 4 threads, contexto 2048 e batch 512. No SM-X510, o smoke final passou 5/5; load ~33,3 s, respostas warm ~5,7–5,9 s, PSS ~1,38 GB e Swap PSS 273 KB. O wiring na `MainActivity` foi validado depois no Edge 40 Neo/API 35. O GGUF não é versionado nem empacotado no APK atual; após reinstalar `datDebug`, ele precisa ser provisionado novamente para habilitar o assistente. Sua ausência não afeta o caminho operacional. A medição combinada com hardware Meta real fica para a fase presencial.

O reconhecimento de fala usa os recursos nativos do Android. STT é uma etapa diferente tanto do classificador operacional quanto do Qwen.

## Estado dos adaptadores

| Adaptador | Estado |
|---|---|
| Mock Android | Implementado e usado nos testes automatizados |
| Classificador operacional Android | Implementado; seis rótulos e caminho de confirmação ativo na `MainActivity` |
| Qwen Android/llama.cpp | Runtime JNI e wiring `UNKNOWN -> assistente` implementados; smoke isolado no SM-X510 e fluxo principal no Edge 40 Neo validados |
| WebSocket Android | Implementado no fluxo principal |
| DAT Android | Ciclo 0.9.0 + MockDeviceKit + ZXing validados no E2E pré-hardware em Android físico; hardware Meta real é gate posterior |
| Voz e TTS Android | Implementados com APIs nativas; rota de áudio dos Meta Wearables fica para o gate de hardware real |
| ROS 2/Nav2 | Bridge e comandos explícitos implementados; E2E `UNDOCK -> SPRAY -> DOCK -> UNDOCK` validado em 22/08/2026 |

## Principais riscos

| Risco | Mitigação do MVP |
|---|---|
| DAT em developer preview | Encapsular SDK e fixar versão validada |
| Sem pose/IMU dos óculos | Alvo visual previamente mapeado |
| DAT não fornece a interface de áudio do Maestro | STT/TTS nativos e fallback no telefone; validar rota Bluetooth no hardware |
| Voz e câmera concorrendo por banda | Captura coordenada e qualidade reduzida |
| Diferenças entre smartphones | Testar no aparelho do evento e manter perfis LOW/MEDIUM |
| Latência de IA | Operacional permanece no classificador pequeno; Qwen é assíncrono, exige preload/feedback de processamento e não bloqueia comandos |
| Comando duplicado | UUID, expiração e deduplicação no bridge |
| Hardware disponível apenas no evento | Mock Device Kit e testes com vídeo H.265 |
| Simulação confundida com câmera real | Label `dat-mockdevice`, ativação explícita por propriedade e evidência pré-hardware separada |