# Equipe e responsabilidades

## Átila Capozzoli Ribeiro Rodrigues

Desenvolvedor Fullstack Pleno com experiência em aplicativos Kotlin, Swift e React Native.

**Responsabilidade principal:** aplicativo companion nativo.

- Android/Kotlin e iOS/Swift, mantendo a mesma regra de negócio.
- Integração com o Meta Wearables DAT.
- Permissões, sessão, câmera e ciclo de vida.
- Captura de voz, transcrição e resposta por áudio.
- Máquina de estados e integração dos componentes no app.

**Decisão de escopo:** o MVP terá apps nativos Kotlin e Swift para validar o Motorola e o iPhone 13. React Native não será usado. A demo ao vivo pode escolher o aparelho mais estável.

## Felipe Gonçalves Vidal

Estudante de Ciência da Computação no INF/UFG e integrante do Núcleo de Robótica Pequi Mecânico, com atuação em ROS 2, Gazebo, TurtleBot 4 e visão computacional.

**Responsabilidade principal:** percepção visual e robótica.

- Definição e detecção do alvo visual mapeado.
- Mapa `target_id -> pose` do cenário.
- Bridge WebSocket/ROS 2.
- Integração com Nav2, Gazebo e TurtleBot 4.
- Testes de comando, expiração e deduplicação no simulador.
- Integração ponta a ponta com Átila.

## Rafael José de Souza Marques

Estudante de Ciência da Computação no INF/UFG e voluntário no CEIA.

**Responsabilidade principal:** inteligência artificial local.

- Definição das intenções `SPRAY`, `CONFIRM`, `CANCEL` e `UNKNOWN`.
- Conjunto pequeno de frases em português para treino e teste.
- Treino ou adaptação de um classificador leve e exportação para execução local.
- Limiar de confiança, tratamento de ambiguidade e métricas.
- Interface e exemplos para integração do mesmo modelo em Kotlin e Swift.
- Evidências do checkpoint de IA funcional.

## Pitch e demonstração

- Felipe apresenta problema, jornada e aplicação em robótica.
- Rafael apresenta arquitetura, IA, checkpoints e fechamento.
- Átila prepara o build, apoia a demonstração e responde questões de mobile/DAT.
- Deve haver apenas uma troca de apresentador no vídeo, entre os slides 3 e 4.

## Acordos de integração

- O contrato JSON é a fronteira entre app e ROS 2.
- O classificador de Rafael é consumido por uma interface pequena no app.
- O detector de Felipe retorna somente `target_id`, confiança e timestamp.
- Cada domínio deve oferecer um fake ou fixture para que os demais não fiquem bloqueados.
- Mudança no contrato compartilhado exige revisão de Átila e Felipe.
