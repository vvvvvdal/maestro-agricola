# Entrega final — texto-base para o formulário

Data de preparação: 18 de agosto de 2026. Prazo informado pelo CEIA: 22 de agosto de 2026.

Este arquivo é a fonte de verdade para o preenchimento. Antes de enviar, a equipe deve apenas adaptar o tamanho dos textos aos limites reais dos campos e substituir os itens marcados como **PENDENTE**.

## Seção A — Documento estruturado

### A1. Problema

Operadores de máquinas e robôs agrícolas trabalham com sol, poeira, luvas, ruído e as mãos ocupadas. Mesmo quando a máquina já navega de forma autônoma, selecionar um local e iniciar uma tarefa ainda pode exigir parar a operação, abrir um celular, tablet ou notebook e navegar por menus. O Maestro Agrícola reduz essa fricção: transforma olhar, voz e confirmação em um comando estruturado para a máquina, sem remover as proteções do próprio robô.

### A2. Usuário-alvo

O usuário inicial é o operador de campo que acompanha robôs ou máquinas agrícolas conectadas e precisa indicar rapidamente uma área de trabalho. No MVP, ele comanda um TurtleBot 4 simulado que representa uma plataforma agrícola. A mesma interface pode evoluir para técnicos de operação e supervisores de frota, mas o projeto não tenta atender todos esses perfis na primeira versão.

### A3. Walkthrough — fluxo principal

1. Durante uma sessão curta do companion app, o operador centraliza o marcador visual `plot-03` e diz “pulverizar esta área”.
2. A câmera dos óculos entrega ao app nativo um frame sob demanda pelo Meta Wearables DAT. No desenvolvimento sem hardware, a mesma interface recebe um frame simulado.
3. O app identifica localmente o QR `plot-03`, já associado a uma pose segura no mapa da demonstração.
4. O reconhecimento de fala nativo do celular produz a transcrição. O app pede processamento offline quando o sistema operacional oferece essa opção.
5. Um classificador pequeno, executado localmente no app, converte a frase na intenção restrita `SPRAY`.
6. O app emite feedback sonoro inicial e fala: “Pulverizar talhão três. Confirmar?”. A meta é iniciar o feedback em menos de 1 segundo e concluir a resposta em até 3 segundos; esses tempos ainda precisam ser medidos nos aparelhos físicos.
7. O operador diz “confirmar”. Uma resposta negativa ou o fim do tempo cancela a interação.
8. Somente após a confirmação, o app envia um JSON versionado e com validade curta pela rede local.
9. O bridge valida schema, validade e duplicidade, traduz `plot-03` para uma meta do ROS 2/Nav2 e responde `ACCEPTED`.
10. O TurtleBot 4 inicia o deslocamento no Gazebo e o app informa “Comando enviado”.

O MVP comprova a sequência completa com mock dos óculos, IA local, WebSocket, ROS 2, Nav2 e Gazebo. A troca do mock pela câmera real fica isolada no adaptador DAT.

### A4. Walkthrough — fluxo de exceção principal

Se nenhum QR conhecido for encontrado, se houver mais de um alvo, se a intenção ficar abaixo do limiar, se o usuário não confirmar ou se a conexão cair, o app informa o motivo em uma frase curta, não envia comando e volta ao estado inicial. Mensagens repetidas usam `command_id`, prazo de validade e deduplicação para não causar movimento duplo. Na demonstração de falha segura, a equipe dirá “cancelar” e mostrará que nenhum comando chega ao robô.

### A5. Decisões técnicas, justificativas e alternativas descartadas

| Decisão do MVP | Por que foi escolhida | Alternativa descartada nesta etapa |
|---|---|---|
| Alvo visual previamente mapeado por QR | O DAT público oferece câmera, mas não uma pose/IMU dos óculos que permita converter a direção da cabeça diretamente em coordenadas. O QR torna a prova determinística. | Raycasting por pose dos óculos, GPS/RTK e localização visual completa. |
| Agente estreito com quatro classes (`SPRAY`, `CONFIRM`, `CANCEL`, `UNKNOWN`) | Cabe no celular, é rápido, testável e transforma ambiguidades em `UNKNOWN` em vez de inventar ações. | LLM em nuvem e linguagem aberta para qualquer tarefa. |
| Captura sob demanda, um frame por interação | Reduz uso de bateria, aquecimento, banda e exposição de terceiros. | Streaming contínuo durante toda a operação. |
| Kotlin e Swift nativos com contrato compartilhado | Os samples e o ciclo de vida do DAT são nativos; Android e iOS consomem o mesmo modelo e JSON sem depender de uma camada que esconda o SDK. | React Native no MVP. |
| WebSocket/JSON versionado entre app e robô | Desacopla óculos, celular e ROS 2; facilita mock, validação, expiração e deduplicação. | Acoplar o app diretamente a tópicos ROS 2 ou a um fabricante de máquina. |

### A6. Concorrentes e diferenciação

**Meta AI nos óculos.** É um assistente multimodal de uso geral, disponível nos AI glasses e voltado a perguntas, tradução e compreensão do ambiente. O Maestro não tenta substituí-lo: é um agente operacional estreito, com protocolo determinístico, confirmação obrigatória e integração com ROS 2 para controlar uma tarefa agrícola.

**John Deere Operations Center e soluções de autonomia.** A plataforma planeja, monitora e envia trabalhos para equipamentos por web, tablet e celular; as soluções autônomas usam o telefone para iniciar e supervisionar tarefas. O Maestro se diferencia como uma camada de interação mãos-livres, agnóstica de fabricante e aberta por contrato, pensada para selecionar um alvo visual e comandar robôs existentes.

Fontes oficiais: [Meta AI](https://ai.meta.com/meta-ai/), [John Deere Operations Center](https://www.deere.com/en/technology-products/precision-ag-technology/operations-center/) e [John Deere Autonomous](https://www.deere.com/en/autonomous/).

### A7. Cinco pilares técnicos obrigatórios

| Pilar | Implementação e evidência do MVP |
|---|---|
| Uso de IA | Classificador softmax local e compartilhado entre Kotlin e Swift. No conjunto de avaliação versionado, a política com limiar 0,40 acertou 15 de 16 frases; a restante virou `UNKNOWN` e não gerou comando. |
| Câmera/microfone | A câmera entra pelo DAT e é consumida sob demanda. A voz usa o reconhecimento nativo do celular; nos óculos reais, o roteamento do microfone por Bluetooth precisa ser validado. O telefone é o fallback explícito. |
| Saída por áudio | TTS nativo do Android/iOS informa pergunta de confirmação, sucesso ou falha. O áudio pode sair pelos open-ear speakers quando a rota Bluetooth do sistema estiver disponível; o alto-falante do telefone é o fallback. |
| Privacidade | Frame e áudio são efêmeros e não são gravados pelo Maestro. Logs guardam apenas IDs, estados, latências e erros. Há confirmação explícita, validade curta e nenhuma execução diante de ambiguidade. |
| Eficiência de bateria | Sessão curta, captura sob demanda, um frame por ação, modelo pequeno local e encerramento de câmera/áudio ao fim da interação. Bateria e temperatura serão medidas no hardware real. |

### Evidências que podem ser demonstradas agora

- `make test-quick`: 10 testes automatizados e validação do Compose.
- `make demo`: bridge aceita o comando, Nav2 fica ativo e a odometria muda no Gazebo.
- Comando positivo: resposta `ACCEPTED`.
- Confirmação “cancelar”: rejeição local, sem envio de movimento.
- Apps nativos, conexão DAT real e rota de áudio nos aparelhos: **PENDENTES de teste físico**; não declarar como validados antes do ensaio.

## Seção B — Diagrama de arquitetura

- Código Mermaid: [`architecture.mmd`](architecture.mmd).
- Imagem para upload: `architecture.svg` no mesmo diretório.
- O diagrama separa óculos, app, rede/bridge e robô; a linha tracejada representa mídia efêmera e a linha sólida representa dados estruturados ou comandos.
- Nota obrigatória: o DAT é a integração de câmera. Voz e TTS pertencem ao sistema mobile e usam a rota de áudio disponível; isso será validado com o hardware.

## Seção C — Vídeo-pitch

- Duração obrigatória: 2 a 3 minutos; roteiro-alvo: 2min45s.
- Apresentadores: Felipe (problema, usuário e jornada) e Rafael (arquitetura, evidência e fechamento).
- Mostrar: comando aceito e uma recusa segura.
- Hospedagem permitida pelo aviso recebido: YouTube não listado, Google Drive ou Vimeo.
- Link do vídeo: **PENDENTE — inserir após upload e testar em janela anônima**.

Checklist antes de colar o link:

- [ ] duração entre 2:00 e 3:00;
- [ ] áudio compreensível e slides legíveis em tela pequena;
- [ ] permissão do link permite acesso sem conta da equipe;
- [ ] deck, fala e formulário usam o mesmo fluxo;
- [ ] não há promessa de pose/IMU, pulverização real ou hardware ainda não testado.

## Seção D — Confirmações finais

### D1. Manutenção ou alteração de escopo

O propósito foi mantido: permitir que um operador indique uma área, dê um comando por voz e confirme antes de acionar um robô. O mecanismo de localização foi refinado. A ideia inicial considerava transformar a direção do olhar em uma coordenada, mas o DAT público não expõe pose/IMU dos óculos. Por isso, o MVP passou a reconhecer um alvo visual previamente mapeado por QR. Essa alteração reduz risco, preserva a jornada “olhar, falar e confirmar” e permite demonstrar de ponta a ponta em uma semana. Operação real de pulverização continua fora de escopo.

### D2. Coerência entre os artefatos

Confirmamos que documento, diagrama, vídeo, apresentação e protótipo descrevem o mesmo corte vertical: captura visual sob demanda, voz pelo sistema mobile, IA local restrita, confirmação obrigatória, comando JSON via rede local e execução em ROS 2/Nav2/Gazebo. Itens ainda dependentes do hardware são identificados como pendentes, sem serem apresentados como evidência concluída.

### D3. Autoria e uso de IA

A equipe AgroTurtles definiu o problema, escopo, arquitetura, decisões, critérios de aceite e validação. Ferramentas de IA foram usadas como apoio para pesquisa, redação, geração e revisão de código e documentação. A equipe revisou as saídas, executou os testes e assume a autoria e a responsabilidade pela entrega final.

## Revisão humana obrigatória antes do envio

- Felipe e Rafael: ensaiar o roteiro e confirmar que as falas refletem o vídeo gravado.
- Átila: revisar as afirmações sobre Kotlin, Swift, DAT, reconhecimento de voz, TTS e aparelhos-alvo.
- Rafael: revisar classificador, métricas e limites da IA.
- Felipe: revisar ROS 2, Nav2, Gazebo, QR e evidências da demo.
- Todos: conferir limites de caracteres do formulário e as três caixas de confirmação da Seção D.
