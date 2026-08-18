# Arquitetura

## Visão geral

```text
AI Glasses
  câmera via DAT + rota de áudio do sistema
          |
          v
App companion Android/Kotlin ou iOS/Swift
  fonte mock/DAT + voz local + IA local + confirmação
          |
          v
WebSocket / JSON versionado
          |
          v
Bridge ROS 2 -> Nav2 / Gazebo -> robô simulado
```

## Componentes

### AI Glasses

- Entrada visual por stream ou captura do DAT.
- Entrada e saída de voz pela rota Bluetooth disponível no sistema mobile, com microfone e alto-falante do telefone como fallback.
- Sem display e sem lógica pesada embarcada.

O DAT é usado para sessão e câmera. O reconhecimento de fala e o TTS pertencem às APIs nativas do Android/iOS; a rota de microfone e áudio dos óculos deve ser validada no hardware e não é tratada como uma API de áudio do DAT.

### Companion app

- Gerencia registro, sessão, permissões e ciclo de vida do stream.
- Captura voz e frame de forma coordenada.
- Detecta a placa `PLOT-03` ou extrai um ID de plot explicitamente falado.
- Exige concordância quando voz e câmera identificam alvos simultaneamente.
- Converte a fala em uma intenção restrita.
- Executa a máquina de estados de confirmação.
- Envia comandos idempotentes ao bridge.

Existem duas implementações nativas porque a equipe precisa provar o fluxo no Motorola e no iPhone 13. Não há React Native. O modelo exportado e os schemas permanecem únicos para evitar duas regras de negócio divergentes.

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

- `FrameSource`: `MockFrameSource` durante a semana e `DatFrameSource` no hardware real. A API é assíncrona para acomodar sessão e captura.
- `TargetDetector`: recebe um frame e retorna `target_id`, confiança e timestamp.
- `TargetResolver`: combina alvo visual e ID falado com estados `RESOLVED`, `NEEDS_VISUAL`, `CONFLICT` ou `UNKNOWN`.
- `IntentClassifier`: recebe a transcrição e retorna rótulo e confiança.
- `CommandTransport`: envia o JSON e correlaciona a resposta por `command_id`.

Essas fronteiras permitem desenvolver mobile, IA, visão e ROS 2 em paralelo sem esperar pelos óculos.

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
- Medir latência, temperatura e bateria no hardware real.

## IA local compartilhada

O repositório treina um classificador linear softmax pequeno para `SPRAY`, `CONFIRM`, `CANCEL` e `UNKNOWN`. São 96 frases em português, com 80 para treino e 16 para avaliação; as features são palavras, bigramas e afixos. O artefato JSON tem aproximadamente 65 KB e é interpretado diretamente em Kotlin e Swift, sem servidor e sem dependência de inferência externa. No conjunto separado de 16 frases, a política operacional com limiar 0,40 obteve 15/16 acertos; o erro restante virou `UNKNOWN`, portanto não enviou comando.

O reconhecimento de fala usa os recursos locais dos sistemas operacionais quando disponíveis. Ele é uma etapa diferente do classificador de intenção do Maestro.

## Estado dos adaptadores

| Adaptador | Estado |
|---|---|
| Mock Android e iOS | Implementado |
| Modelo local Android e iOS | Implementado; build nativo pendente |
| WebSocket Android e iOS | Implementado; teste em aparelho pendente |
| DAT Android e iOS | Dependência e fronteira de integração presentes; adaptador real e ciclo no hardware pendentes |
| Voz e TTS Android/iOS | Implementados com APIs nativas; builds físicos e rota Bluetooth pendentes |
| ROS 2/Nav2 | Jornada headless validada no Gazebo; Nav2 aceitou a meta e o robô iniciou movimento |

## Principais riscos

| Risco | Mitigação do MVP |
|---|---|
| DAT em developer preview | Encapsular SDK e fixar versão validada |
| Sem pose/IMU dos óculos | Alvo visual previamente mapeado |
| DAT não fornece a interface de áudio do Maestro | STT/TTS nativos e fallback no telefone; validar rota Bluetooth no hardware |
| Voz e câmera concorrendo por banda | Captura coordenada e qualidade reduzida |
| Diferenças entre smartphones | Testar no aparelho do evento e manter perfis LOW/MEDIUM |
| Latência de IA | Modelo local pequeno, feedback sonoro e timeout |
| Comando duplicado | UUID, expiração e deduplicação no bridge |
| Hardware disponível apenas no evento | Mock Device Kit e testes com vídeo H.265 |
