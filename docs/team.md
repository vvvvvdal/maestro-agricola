# Equipe e responsabilidades

As responsabilidades abaixo indicam liderança técnica e contexto de revisão. Elas não criam exclusividade de arquivos: qualquer integrante pode contribuir em outra frente desde que preserve contratos, registre a evidência e peça revisão quando a mudança atravessar domínios.

## Átila Capozzoli Ribeiro Rodrigues

Desenvolvedor Fullstack Pleno com experiência em aplicativos Kotlin e React Native.

**Responsabilidade principal:** aplicativo companion Android e integração Meta Wearables.

- Android/Kotlin e UI Compose.
- Flavors `mock` e `dat`.
- Meta Wearables Device Access Toolkit (DAT).
- Permissões, sessão, câmera e ciclo de vida.
- Captura de voz, transcrição e resposta por áudio.
- Estados de interação e integração dos componentes no app.
- Evidência pré-hardware via MockDeviceKit e preparação do gate com hardware real.

**Decisão de escopo:** o MVP usa somente Android nativo em Kotlin. React Native não faz parte da implementação atual.

## Felipe Gonçalves Vidal

Estudante de Ciência da Computação no INF/UFG e integrante do Núcleo de Robótica Pequi Mecânico, com atuação em ROS 2, Gazebo, TurtleBot 4 e visão computacional.

**Responsabilidade principal:** percepção visual, robótica e integração ponta a ponta.

- Definição e detecção do alvo visual mapeado.
- Mapa `target_id -> pose` do cenário.
- Bridge WebSocket/ROS 2.
- Integração com Nav2, Gazebo e TurtleBot 4.
- Lifecycle explícito `SPRAY`/`DOCK`/`UNDOCK`.
- Testes de comando, expiração, deduplicação e estado.
- Integração E2E com Android.

## Rafael José de Souza Marques

Estudante de Ciência da Computação no INF/UFG e voluntário no CEIA.

**Responsabilidade principal:** IA local, métricas e evidências.

- Corpus e avaliação do classificador operacional.
- Intenções `SPRAY`, `DOCK`, `UNDOCK`, `CONFIRM`, `CANCEL` e `UNKNOWN`.
- Limiar de confiança e tratamento de ambiguidade.
- Paridade entre implementação de referência e Kotlin.
- Benchmark e evidências de seleção de modelo.
- Apoio à documentação e aos checkpoints de IA.

## Fronteiras atuais de IA

O projeto possui duas funções distintas:

1. `LocalIntentClassifier`: autoridade operacional. Seus rótulos ainda passam por `InteractionEngine`, resolução de alvo, estado e confirmação antes de existir `Command`.
2. Qwen2.5-1.5B local: assistente de domínio. O runtime Android foi validado no SM-X510, mas o wiring na `MainActivity` ainda está pendente. Quando integrado, receberá apenas `UNKNOWN` e retornará `CHAT` ou `OUT_OF_SCOPE`.

Nenhum integrante deve conectar o Qwen diretamente a ROS, WebSocket, target ou estado do robô.

## Pitch e demonstração

- Felipe apresenta problema, jornada e aplicação em robótica.
- Rafael apresenta arquitetura, IA, checkpoints e fechamento.
- Átila prepara o build, apoia a demonstração e responde questões sobre mobile/DAT.
- A divisão pode ser ajustada no ensaio final, desde que o tempo total e a narrativa continuem coerentes com o produto real.

## Acordos de integração

- O contrato JSON é a fronteira entre app e ROS 2.
- `InteractionEngine` continua sendo a fronteira de confirmação e validação antes do envio.
- O detector retorna somente `target_id`, confiança e timestamp.
- `TargetResolver` combina alvo visual/falado e recusa conflito.
- DAT real e MockDeviceKit devem permanecer distinguíveis nos logs e na documentação.
- O assistente Qwen nunca substitui o classificador operacional.
- Mudança em contrato, safety ou fluxo de confirmação exige revisão cruzada.