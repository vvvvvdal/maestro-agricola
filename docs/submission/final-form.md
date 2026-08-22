# Entrega final — texto-base para o formulário

Data de preparação: 22 de agosto de 2026.

Este arquivo é a fonte de verdade para o preenchimento. Antes de enviar, adapte apenas o tamanho aos limites reais dos campos e substitua o link do vídeo. A evidência desta etapa é **pré-hardware com DAT 0.9.0 + MockDeviceKit em Android físico**; não afirmar que o frame veio dos Meta Wearables reais.

## Seção A — Documento estruturado

### A1. Problema

Operadores de máquinas e robôs agrícolas trabalham com sol, poeira, luvas, ruído e as mãos ocupadas. Mesmo quando a máquina já navega autonomamente, selecionar um local e iniciar uma tarefa ainda pode exigir parar a operação, abrir um celular, tablet ou notebook e navegar por menus. O Maestro Agrícola reduz essa fricção: transforma olhar, voz e confirmação em um comando estruturado para a máquina sem remover as proteções do próprio robô.

### A2. Usuário-alvo

O usuário inicial é o operador de campo que acompanha robôs ou máquinas agrícolas conectadas e precisa indicar rapidamente uma área de trabalho. No MVP, ele comanda um TurtleBot 4 simulado que representa uma plataforma agrícola.

### A3. Walkthrough — fluxo principal

1. O operador inicia `datDebug` no Android físico com o MockDeviceKit explicitamente habilitado para a etapa pré-hardware.
2. Em “Olhar para o alvo”, o DAT entrega uma captura simulada pela mesma fronteira usada pelo adaptador e o ZXing resolve localmente o QR `plot-03`.
3. O operador diz “pulverizar esta área” ou informa um plot pela fala.
4. O `TargetResolver` combina câmera e voz; divergência entre os IDs termina em ambiguidade sem comando.
5. O `LocalIntentClassifier` classifica a frase em um conjunto operacional restrito.
6. O app repete a operação e exige confirmação explícita por áudio.
7. Somente após `confirmar`, um JSON versionado, expirável e com `command_id` único é enviado pela rede local.
8. O bridge valida schema, confirmação, expiração, duplicidade e estado do robô.
9. `SPRAY` entrega uma pose allowlisted ao Nav2 e termina no alvo sem retorno automático.
10. `DOCK` e `UNDOCK` são operações independentes e só acontecem por comandos explícitos e confirmados.

### A4. Fluxos de exceção e segurança

- `SPRAY` enquanto dockado é recusado e não gera `UNDOCK` automático.
- Se voz e câmera discordarem (`plot-01` × `plot-03`), a UI mostra `AMBÍGUO` e nada é enviado.
- `CANCEL` durante a confirmação encerra a operação localmente.
- `UNKNOWN` nunca cria comando operacional.
- `confirmed=false` e comando expirado são rejeitados pelo contrato.
- Repetição do mesmo `command_id` retorna a resposta anterior e não repete o callback ROS.
- Qwen, quando disponível, só pode responder `CHAT` ou `OUT_OF_SCOPE`; nunca controla WebSocket/ROS.

### A5. Decisões técnicas

**Alvo mapeado em vez de pose/IMU.** O DAT público não fornece pose/IMU suficiente para transformar direção da cabeça em coordenada segura. O MVP usa QR/ID previamente mapeado e fail-closed em divergência.

**Classificador operacional pequeno em vez de LLM como autoridade.** O Qwen foi rejeitado como classificador de comandos críticos após apresentar aceites perigosos. O classificador operacional atual fez 64/64 no corpus final, com macro-F1 1,0 e 0 aceites perigosos.

**Lifecycle explícito.** `SPRAY` não faz undock, retorno ou dock automaticamente. Isso torna a intenção física observável e confirmável.

**DAT/MockDeviceKit nesta etapa.** O `datDebug` exercita a integração do SDK sem fingir hardware real. Se selecionados para a fase presencial, o mesmo adaptador será revalidado com os Meta Wearables físicos.

### A6. Evidência final reproduzida em 22/08/2026

No Samsung SM-X510/API 36, usando `datDebug` + MockDeviceKit e bridge WebSocket local, foi observado:

```text
UNDOCK explícito -> Undock Goal Succeeded
Olhar para o alvo -> plot-03
SPRAY confirmado -> Nav2 accepted/completed plot-03
DOCK explícito -> Nav2 dock approach -> Dock Goal Succeeded
novo UNDOCK explícito -> Undock Goal Succeeded
```

Também passaram os guardrails `SPRAY` dockado sem movimento, conflito `plot-03` visual × `plot-01` falado, `CANCEL` sem envio e `UNKNOWN` sem movimento. A captura do MockDeviceKit foi repetida várias vezes na mesma execução após o rearm da câmera simulada.

Gates automatizados finais:

```text
64/64 no corpus de avaliação
macro-F1 1.000
unsafe accepts: 0
65 testes portáteis
36 testes do bridge
```

### A7. Cinco pilares

| Pilar | Implementação/evidência |
|---|---|
| IA | Classificador local restrito, 64/64 no corpus final e 0 aceites perigosos; Qwen opcional sem autoridade operacional. |
| Câmera/microfone | `datDebug` + DAT 0.9.0 + MockDeviceKit para captura pré-hardware; STT pelo Android. Hardware Meta real é gate posterior. |
| Output por áudio | TTS Android para confirmação, cancelamento, erro e sucesso. |
| Privacidade | Captura sob demanda, processamento local e nenhuma persistência de mídia bruta pelo Maestro por padrão. |
| Eficiência | Classificador operacional pequeno e captura sob demanda; medições completas com hardware Meta ficam para a fase presencial. |

## Seção B — Diagrama de arquitetura

- Código Mermaid: [`architecture.mmd`](architecture.mmd).
- Imagem para upload: `architecture.svg` no mesmo diretório.
- O diagrama deve separar DAT/MockDeviceKit, app Android, IA operacional, confirmação, WebSocket, bridge e ROS 2/Nav2/Gazebo.
- A camada Qwen deve aparecer separada do caminho de `Command`.

## Seção C — Vídeo-pitch

- Duração: 2 a 3 minutos; alvo de 2min40s–2min55s.
- Apresentadores: Felipe (problema, usuário e jornada) e Rafael (arquitetura, evidência e fechamento).
- Mostrar pelo menos: captura `plot-03`, confirmação, `UNDOCK` explícito, `SPRAY`/Nav2, `DOCK` explícito e uma falha segura.
- Na tela ou fala, rotular a câmera como **DAT 0.9.0 + MockDeviceKit / pré-hardware**.
- Link do vídeo: **PENDENTE — inserir após upload e testar em janela anônima**.

Checklist:

- [ ] duração entre 2:00 e 3:00;
- [ ] áudio compreensível e telas legíveis;
- [ ] link acessível sem conta da equipe;
- [ ] deck, fala e formulário usam o mesmo fluxo;
- [ ] não há promessa de pose/IMU, pulverização real ou captura física dos Meta Wearables;
- [ ] a evidência E2E mostrada corresponde ao lifecycle explícito atual.

## Seção D — Confirmações finais

### D1. Manutenção ou alteração de escopo

O propósito foi mantido: permitir que um operador indique uma área, dê um comando por voz e confirme antes de acionar um robô. O mecanismo de localização foi refinado para um QR/ID previamente mapeado porque o DAT público não expõe pose/IMU suficiente para gerar um waypoint seguro. GPS do usuário não vira destino do robô. A operação real de pulverização continua fora de escopo.

### D2. Coerência entre os artefatos

Documento, diagrama, vídeo, apresentação e protótipo devem descrever o mesmo corte vertical: DAT pré-hardware com MockDeviceKit, captura visual sob demanda, voz pelo Android, IA operacional local, confirmação obrigatória, comando JSON pela rede local e execução em ROS 2/Nav2/Gazebo. Hardware Meta real é próximo gate, não evidência já concluída.

### D3. Autoria e uso de IA

A equipe AgroTurtles definiu o problema, escopo, arquitetura, decisões, critérios de aceite e validação. Ferramentas de IA foram usadas como apoio para pesquisa, redação, geração e revisão de código e documentação. A equipe revisou as saídas, executou os testes e assume a autoria e a responsabilidade pela entrega final.

## Revisão humana obrigatória antes do envio

- Felipe e Rafael: ensaiar o roteiro e confirmar que as falas refletem o vídeo gravado.
- Átila: revisar as afirmações sobre Kotlin, DAT, reconhecimento de voz, TTS e Android.
- Rafael: revisar classificador, métricas e limites da IA.
- Felipe: revisar ROS 2, Nav2, Gazebo, QR e evidências da demo.
- Todos: conferir limites de caracteres e caixas de confirmação do formulário.