# AGENTS.md

## Projeto

Maestro Agrícola é uma interface hands-free para comandar robôs agrícolas com câmera, voz e confirmação por áudio.

## Regras permanentes

- Aplicativos do MVP: Android nativo em Kotlin e iOS nativo em Swift.
- Não introduzir React Native.
- Android e iOS devem consumir o mesmo contrato versionado e o mesmo artefato de IA local.
- Integração dos óculos: Meta Wearables Device Access Toolkit (DAT).
- Confirmar a versão atual do DAT antes de alterar dependências ou APIs.
- Nunca assumir que o DAT fornece IMU, pose de cabeça, GPS ou profundidade.
- No MVP, resolver o alvo por marcador visual ou talhão previamente mapeado.
- Não enviar movimento ao robô sem confirmação explícita por áudio.
- Não persistir fotos, áudio ou transcrições por padrão.
- Documentar separadamente os dados tratados pelo app, Android, SDK e serviços externos.
- Desabilitar analytics opcionais do DAT quando permitido e registrar a decisão.
- Nunca colocar tokens, chaves ou segredos no repositório.
- Toda dependência nova precisa de justificativa e aprovação humana.
- Preferir captura sob demanda e processamento local.
- Isolar integrações externas atrás de interfaces pequenas.
- O contrato com ROS deve ser JSON versionado e independente do fabricante.
- Desenvolver com Mock Device Kit antes do hardware real.
- Manter fontes de câmera simulada separadas dos adaptadores DAT reais.
- Testar caminho feliz, recusa, ambiguidade, timeout e desconexão.
- Testar câmera e microfone simultâneos no modelo exato de smartphone do evento.
- Mudança de comportamento exige atualização da spec correspondente.
- Uma tarefa por vez; mudanças pequenas, revisáveis e verificáveis.
- Antes de implementar, listar ambiguidades e critérios de aceite.
- Depois de implementar, comparar código, testes e spec.

## Responsáveis por domínio

- Átila: apps Android/Kotlin e iOS/Swift, DAT, áudio, máquina de estados e integração mobile.
- Felipe: visão computacional, ROS 2, Gazebo, TurtleBot 4 e integração com o simulador.
- Rafael: IA local, classificador de intenção, conjunto de testes e métricas do modelo.
- Felipe e Rafael: apresentação e gravação do pitch.

## Definição de pronto

Uma mudança está pronta quando atende aos critérios escritos, possui teste proporcional ao risco, não persiste mídia indevidamente e mantém a confirmação de segurança.
