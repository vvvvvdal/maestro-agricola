# Plano do hackathon presencial — 18 de setembro de 2026

## Objetivo do dia

O evento não é o momento de criar a solução. O software deve chegar com mock, DAT pré-hardware, bridge, simulação e gates já preparados. O dia serve para substituir mocks pelo hardware real, medir, corrigir incompatibilidades curtas e demonstrar.

## Pré-condições para viajar

- `mockDebug` e `datDebug` compilando.
- Jornada Android -> WebSocket -> ROS 2/Nav2/Gazebo aprovada com lifecycle explícito.
- DAT 0.9.0/MockDeviceKit já validado.
- Versão do DAT e dependências disponíveis localmente.
- Bridge, mundo Gazebo, targets e fixtures reproduzíveis.
- Cabos, carregadores, notebooks e cópias locais de dependências permitidas.
- Credenciais fora do Git.
- Vídeo de contingência claramente identificado.
- Se Qwen fizer parte da demo, wiring seguro concluído e teste de memória com câmera/áudio já executado; caso contrário, deixá-lo fora da jornada operacional.

## Distribuição

- **Átila:** pareamento, permissões, DAT, câmera, áudio e build Android.
- **Felipe:** visão, target, bridge ROS 2, Gazebo/Nav2 e integração E2E.
- **Rafael:** IA local, métricas, checkpoints e materiais do pitch.

## Roteiro

### Onboarding / hardware

- [ ] registrar modelo do Android e versão do sistema;
- [ ] registrar firmware dos Meta Wearables;
- [ ] confirmar versão DAT efetivamente instalada;
- [ ] executar o sample oficial;
- [ ] parear os óculos;
- [ ] confirmar permissões;
- [ ] confirmar frame real;
- [ ] observar rota real de microfone e TTS.

### Integração mínima

- [ ] instalar `datDebug`;
- [ ] confirmar que a UI mostra fonte DAT, não mock;
- [ ] olhar para uma placa/target conhecido e capturar sob demanda;
- [ ] confirmar que `TargetResolver` recebe o mesmo ID esperado;
- [ ] executar uma transcrição curta;
- [ ] ouvir a resposta/confirmação pela rota disponível.

### Jornada operacional

Executar pelo menos:

1. `UNDOCK` explícito, se o robô iniciar dockado;
2. `SPRAY` para target válido;
3. confirmar que o robô permanece no target;
4. `DOCK` explícito, se fizer parte da demo;
5. `CANCEL` ou timeout sem movimento;
6. conflito de target sem movimento.

### Medição

- [ ] latência de captura;
- [ ] latência de STT/ação operacional;
- [ ] uso de memória;
- [ ] temperatura;
- [ ] bateria inicial/final;
- [ ] estabilidade de câmera e áudio simultâneos.

Se o Qwen estiver ativo na experiência final:

- [ ] medir cold/warm no aparelho real da demo;
- [ ] confirmar que operações críticas continuam instantâneas e não passam pelo Qwen;
- [ ] confirmar que `UNKNOWN` é o único caminho conversacional;
- [ ] observar memória com DAT/câmera/áudio simultâneos.

## Checkpoints

Nos checkpoints, mostrar somente evidência que realmente ocorreu:

- IA operacional local;
- frame dos óculos, se já validado;
- áudio na rota observada;
- confirmação antes de movimento;
- não persistência de mídia bruta;
- falha segura;
- consumo/latência medidos, não estimados.

## Contingências

| Falha | Resposta |
|---|---|
| Stream real instável | reduzir taxa/qualidade e capturar sob demanda |
| Microfone dos óculos indisponível | usar microfone do telefone e declarar a rota real |
| TTS não roteia para os óculos | usar saída disponível e registrar a limitação |
| Qwen pressiona memória/latência | desabilitar assistente; manter classificador operacional |
| Bridge sem rede | corrigir rede local/endpoint, sem alterar contrato |
| Detector falha | melhorar enquadramento/iluminação; não trocar de técnica |
| `SPRAY` rejeitado porque está dockado | executar `UNDOCK` explícito; nunca adicionar undock automático |

## Congelamento

Depois que a jornada física estiver estável:

- [ ] parar novas features;
- [ ] executar a jornada cinco vezes;
- [ ] incluir pelo menos uma recusa segura;
- [ ] salvar logs/evidências sem mídia sensível;
- [ ] gravar uma execução limpa;
- [ ] conferir slides, roteiro e afirmações técnicas.

Mudança posterior só entra se corrigir um bloqueio da demonstração ou impedir um comando indevido.