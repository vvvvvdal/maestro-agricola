# Product brief

## Problema em uma frase

Operadores rurais precisam interromper o trabalho e recorrer a telas para orientar ou reprogramar maquinário autônomo no campo.

## Público inicial

- Operadores de robôs móveis e tratores autônomos.
- Equipes de agricultura de precisão e manutenção de campo.
- Fabricantes e integradores que já usam ROS ou aceitam comandos por API.

## Proposta de valor

O Maestro Agrícola transforma os óculos em uma interface operacional: o usuário olha para um alvo previamente mapeado, fala a ação e confirma por áudio. A autonomia continua no robô; o Maestro reduz a fricção da interação humana e mantém as decisões críticas explícitas.

## Por que os óculos importam

- A câmera compartilha o ponto de vista do operador.
- O fluxo pode ser iniciado sem ocupar as mãos.
- A resposta por áudio fecha o ciclo sem exigir atenção contínua a uma tela.
- O Android companion concentra percepção, IA local, regras de segurança e conectividade.

A câmera via DAT já possui caminho pré-hardware validado com MockDeviceKit. Câmera e rota de áudio nos Meta Wearables reais ainda precisam do gate físico.

## Diferencial

A maioria das experiências de AI Glasses informa ou descreve. O Maestro usa visão e voz para iniciar uma ação física segura e confirmada em maquinário que já possui sua própria autonomia.

A arquitetura separa interpretação de linguagem e autoridade de controle:

- o classificador operacional reconhece somente intenções versionadas;
- `InteractionEngine` valida estado e exige confirmação;
- `TargetResolver` aceita apenas alvos conhecidos;
- o assistente Qwen, quando ligado à interface principal, fica restrito a `CHAT` ou `OUT_OF_SCOPE` e não controla o robô.

## Jornada demonstrável

```text
olhar para alvo mapeado
-> falar ação
-> classificar intenção
-> resolver alvo
-> repetir operação entendida
-> confirmação explícita
-> Command JSON
-> WebSocket
-> ROS 2 / Nav2
-> robô simulado
```

`SPRAY` navega para o alvo e permanece lá. `DOCK` e `UNDOCK` são ações explícitas separadas; não existe retorno automático à doca depois de `SPRAY`.

## Hipótese de impacto

Uma interação hands-free pode reduzir a fricção operacional, manter o trabalhador atento ao ambiente e tornar sistemas autônomos mais acessíveis a quem não opera interfaces técnicas complexas.

Não há, nesta fase, dados medidos de economia de tempo em campo. Uma validação futura deve comparar tempo, erros e carga de interação entre o fluxo com tela e o fluxo “olhar, falar, confirmar”.

## Limites do MVP

- Uma tarefa agrícola demonstrativa: `SPRAY` em alvo previamente mapeado.
- Comandos de lifecycle explícitos `DOCK` e `UNDOCK`.
- Alvos controlados/allowlisted, hoje representados no cenário por plots mapeados.
- Um robô simulado em ROS 2/Gazebo.
- Sem pulverização física.
- Sem navegação implementada pelo Maestro; planejamento e execução pertencem ao stack do robô/Nav2.
- Sem dependência de IMU, GPS, pose da cabeça ou profundidade dos óculos.
- Sem RAG e sem linguagem aberta com autoridade operacional.
- Qwen local é opcional e conversacional; o classificador operacional continua independente dele.