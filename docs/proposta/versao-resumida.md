# Maestro Agrícola

## Versão resumida revisada

**Equipe:** AgroTurtles  
**Trilha temática:** Produtividade  
**Área de aplicação:** Agronegócio  
**Revisão:** 18 de agosto de 2026

### Equipe

- Átila Capozzoli Ribeiro Rodrigues - Fullstack Pleno com experiência em Kotlin; lidera app nativo e DAT.
- Felipe Gonçalves Vidal - Integrante do Pequi Mecânico; lidera visão, ROS 2, Gazebo e TurtleBot 4.
- Rafael José de Souza Marques - Voluntário no CEIA; lidera IA local e classificação de intenção.

Felipe e Rafael apresentam o pitch. O MVP mantém um app Android nativo em Kotlin; React Native não será usado.

> Esta revisão preserva o escopo original e corrige premissas técnicas: o DAT atual não expõe pose/IMU dos óculos; por isso, o MVP seleciona um alvo visual previamente mapeado.

## 1. Problema e oportunidade

Robôs móveis e tratores autônomos já conseguem executar navegação e tarefas no campo, mas orientar ou reprogramar essas máquinas ainda pode exigir que o operador pare, limpe as mãos e use notebook ou tablet sob sol e poeira.

O gargalo não é apenas a autonomia da máquina. É a interface entre o trabalhador e essa autonomia. Falta uma interação natural, contextual e hands-free para o ambiente rural.

O Maestro Agrícola reduz essa fricção e pode se integrar a diferentes plataformas sem substituir a inteligência de navegação que já existe no robô.

## 2. Solução: olhar, falar e confirmar

O Maestro Agrícola transforma AI Glasses em uma interface operacional para maquinário autônomo.

1. **Olhar:** o operador centraliza a placa `PLOT-03`, legível por pessoas e pelo QR.
2. **Falar:** diz “pulverizar esta área” ou explicita “pulverizar no plot-03”.
3. **Confirmar:** ouve “pulverizar talhão três, confirmar?” e responde por voz.

Somente após a confirmação o app envia um comando estruturado ao robô. O Maestro não substitui a autonomia da máquina: ele simplifica a forma de comandá-la.

## 3. Arquitetura e viabilidade

O fluxo do MVP é modular:

```text
AI Glasses -> app Kotlin -> alvo + intenção local -> JSON/WebSocket -> ROS 2/Gazebo
```

- **Óculos:** câmera como entrada visual, microfones para voz e alto-falantes para resposta.
- **App companion:** gerencia o DAT, interpreta o comando, identifica o alvo e exige confirmação.
- **Comunicação:** contrato JSON versionado, com ID único e expiração.
- **Robô:** o bridge ROS 2 converte o `target_id` em uma meta de navegação no cenário simulado.

### Seleção do alvo

O DAT atual oferece sessão, streaming e captura de foto, mas não expõe pose de cabeça, IMU ou profundidade para o app. Portanto, o MVP não promete transformar diretamente a direção da cabeça em coordenadas métricas.

Na demonstração, a câmera identifica o QR `plot-03`, previamente mapeado. O ID também pode ser dito por voz como fallback. Quando voz e câmera fornecem IDs diferentes, o app cancela a operação; quando nenhuma das duas identifica um alvo, pede reposicionamento.

A placa do MVP combina texto grande e QR. Em campo, poeira ou obstrução continuam sendo riscos e exigiriam placa selada, redundância e manutenção. GPS do celular pode futuramente ajudar a limitar candidatos por geofencing, mas não informa sozinho para onde a pessoa está olhando. Em uma evolução de produto, o QR pode ser substituído por localização visual contra o mapa da fazenda, RTK ou telemetria fornecida pelo robô.

### Inteligência artificial

O reconhecimento de fala do sistema operacional produz a transcrição; ele é separado da IA do Maestro. Em seguida, um classificador linear softmax local, treinado com 96 frases curtas em português e exportado em JSON com cerca de 65 KB, transforma o texto em `SPRAY`, `CONFIRM`, `CANCEL` ou `UNKNOWN`. O modelo usa palavras, pares de palavras e afixos, e o app Kotlin interpreta seus pesos sem servidor. Com limiar de 0,40, a avaliação separada acertou 15 de 16 frases, e a restante foi recusada como `UNKNOWN`. O benchmark ainda será executado no Android físico da demonstração com `datDebug` e os Meta Wearables.

## 4. Checkpoints obrigatórios

- **Inteligência artificial:** classificador local funcional e demonstrável no companion app.
- **Câmera ou microfone:** câmera dos óculos como entrada visual principal e voz como canal de comando.
- **Output por áudio:** confirmação, erro, cancelamento e sucesso pelos alto-falantes.
- **Privacidade e dados:** o Maestro não salva fotos, áudio ou transcrições por padrão; a mídia é liberada após a interação. A equipe também documentará os fluxos próprios de Android, Meta AI e DAT e desabilitará analytics opcionais quando permitido.
- **Eficiência de bateria:** captura sob demanda ou stream de baixa taxa, inferência pequena e encerramento dos recursos ao fim da jornada.

## 5. Segurança e tratamento de erros

- Nenhum comando de movimento é enviado sem confirmação explícita.
- Alvo ou intenção ambíguos geram pedido de repetição.
- Divergência entre alvo falado e alvo visual cancela a operação.
- Timeout, recusa ou perda de conexão cancelam a operação.
- IDs únicos, validade curta e deduplicação evitam execução repetida.
- Navegação, obstáculos e proteções funcionais continuam sob responsabilidade do robô.

## 6. Prova de conceito

Antes do evento, a equipe desenvolve com o Mock Device Kit, vídeo H.265 e ROS 2/Gazebo. No hardware real, serão validados pareamento, permissões, qualidade do stream, áudio e consumo.

O critério principal é executar cinco vezes a jornada completa, incluindo uma recusa e uma ambiguidade, sem comando indevido e sem mídia persistida pelo app.

## 7. Diferencial e impacto

Enquanto muitas soluções de AI Glasses atuam como assistentes informacionais, o Maestro usa visão e voz para iniciar uma ação física confirmada. O valor será validado comparando tempo, erros e carga de interação entre o fluxo com tela e o hands-free, sem antecipar ganhos ainda não medidos.
