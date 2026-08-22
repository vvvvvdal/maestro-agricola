# Relatório de evolução do Maestro Agrícola

> **Nota de atualização — 22/08/2026:** este relatório preserva o retrato histórico encerrado em 19/08. Desde então, o projeto concluiu o adaptador DAT 0.9.0 com MockDeviceKit, QR local por ZXing, comandos `DOCK`/`UNDOCK` explícitos, wiring seguro do Qwen, UI Compose e o E2E `datDebug → WebSocket → ROS 2/Nav2/Gazebo` no Android físico. O modelo atual tem 213 exemplos, seis rótulos e 729.056 bytes. Para o estado corrente, consulte [`../README.md`](../README.md), [`../TASKS.md`](../TASKS.md), [`tasks/mvp-week.md`](tasks/mvp-week.md) e [`submission/final-form.md`](submission/final-form.md). Menções abaixo a adaptador DAT stub, quatro classes, lifecycle automático ou E2E pendente são históricas e não descrevem a entrega atual.

**Período coberto:** início dos registros disponíveis até 19 de agosto de 2026

**Escopo:** produto, arquitetura, Android, IA local, visão, ROS 2/Gazebo, testes, documentação, pitch e ambiente de desenvolvimento

**Responsável pela consolidação:** equipe Maestro Agrícola

## 1. Resumo executivo

O Maestro Agrícola evoluiu de uma proposta de interface hands-free para um MVP Android nativo com contrato de comando versionado, classificador de intenção local, confirmação explícita de segurança, identificação de talhões por marcadores visuais e bridge para ROS 2/Nav2/Gazebo.

A principal mudança de escopo foi a retirada completa da implementação iOS em 18 de agosto. O projeto passou a manter uma única aplicação Android/Kotlin, com os flavors `mockDebug` e `datDebug`. O mock permite avançar sem os óculos; o flavor DAT preserva uma fronteira separada para a futura integração oficial com o Meta Wearables Device Access Toolkit.

Na frente de IA sob responsabilidade de Rafael, o projeto já possui dataset versionado, modelo compacto, avaliação offline, fixture de paridade Python/Kotlin e medição no Motorola Edge 40 Neo. A tarefa AI-03 foi concluída em 19 de agosto: o APK `mockDebug` passou nos testes, foi instalado no aparelho e executou 390 inferências dos 13 casos de paridade sem divergências.

Depois da AI-03, a equipe concluiu a QA-01 com testes de recusa, ambiguidade e timeout, iniciou a matriz da QA-04 e executou uma coleta parcial da QA-03 no Edge 40 Neo. O TTS foi ouvido pelo alto-falante inferior do telefone e nenhum caminho interno suspeito de foto, áudio ou transcrição foi encontrado.

O MVP ainda não está concluído de ponta a ponta no celular. Permanecem pendentes, principalmente, a integração real do DAT, câmera e microfone simultâneos, QR obtido de um frame real no app, ligação física app–WebSocket–bridge, desconexão ponta a ponta e cinco execuções completas da demonstração.

## 2. Fontes e limite da auditoria

Este relatório foi elaborado a partir do estado atual do código, dos testes, dos artefatos estruturados e dos registros em `docs/tasks/`. A pasta `.git` do workspace principal não contém metadados utilizáveis; os commits já publicados foram operados por uma cópia Git temporária da branch `atualizações-testes`. Por isso, este documento descreve a evolução técnica observável, mas não substitui uma auditoria completa de autoria commit a commit.

As datas e a ordem abaixo são, portanto, baseadas nas evidências documentadas no próprio projeto. Afirmações marcadas como concluídas possuem código, teste, artefato ou registro de execução associado. Itens apenas planejados são apresentados como pendentes.

## 3. Evolução por etapa

### 3.1. Definição do problema e corte do MVP

O projeto definiu como objetivo permitir que um operador use câmera e voz para solicitar uma ação a um robô agrícola, recebendo confirmação por áudio antes da execução.

As decisões que congelaram o escopo foram:

- uma única ação operacional restrita no MVP: `SPRAY`;
- intenções auxiliares `CONFIRM`, `CANCEL` e `UNKNOWN`;
- alvo resolvido por marcador visual ou talhão previamente mapeado;
- nenhuma navegação baseada em pose da cabeça, IMU, GPS ou profundidade presumidos do DAT;
- nenhum movimento enviado sem confirmação explícita;
- processamento local e captura sob demanda;
- fotos, áudio e transcrições não persistidos por padrão;
- integração com o robô por JSON versionado e independente do fabricante.

Essa etapa também separou responsabilidades: Átila no app Android/DAT/áudio, Felipe em visão e ROS 2, Rafael em IA local, testes e métricas, e Felipe com Rafael no pitch.

### 3.2. Fundação técnica e contratos

Foi criado o contrato JSON 1.0 de comando e resposta, incluindo:

- `command_id` em UUID;
- versão explícita do schema;
- instante de criação e expiração;
- intenção e alvo mapeado;
- sinalizador `confirmed`;
- ACK correlacionado pelo mesmo `command_id`.

O bridge passou a validar schema e versão, rejeitar comandos vencidos ou não confirmados e deduplicar UUIDs. As integrações externas foram isoladas atrás de interfaces pequenas, como `FrameSource`, `IntentClassifier`, `TargetResolver` e `CommandTransport`.

### 3.3. IA local — AI-01 e AI-02

Foi montado um conjunto de 96 frases em português, balanceado em quatro classes, com 80 exemplos de treino e 16 de avaliação. O treinamento produz um classificador linear softmax em JSON, com aproximadamente 65 KB, usando palavras, bigramas e afixos.

A avaliação registrada apresenta:

| Métrica | Resultado |
|---|---:|
| Acurácia bruta | 14/16 — 87,5% |
| Acurácia com política operacional | 15/16 — 93,75% |
| Limiar de confiança | 0,40 |
| Tamanho aproximado do modelo | 65 KB |

O limiar transforma previsões de baixa confiança em `UNKNOWN`, privilegiando falha segura. O classificador recebe texto transcrito; ele não processa áudio bruto e não depende de servidor externo.

### 3.4. Visão e resolução de alvo

Foram adicionados marcadores para `plot-01`, `plot-02` e `plot-03`, texturas no cenário e mapeamento de cada ID para uma pose conhecida. O detector estático passou a cobrir:

- marcador conhecido, retornando `DETECTED`;
- imagem vazia ou QR fora do mapa, retornando `UNKNOWN`;
- dois marcadores simultâneos, retornando `AMBIGUOUS`.

O resolvedor aceita alvo apenas visual, apenas falado ou a concordância entre ambos. Se voz e câmera apontarem para alvos diferentes, o fluxo falha de forma segura. A conexão desse detector a um frame real recebido pelo app continua pendente.

### 3.5. ROS 2, Nav2 e Gazebo

Foi criado o bridge WebSocket/ROS 2, o cenário com TurtleBot 4, os três talhões e scripts de demonstração em Docker. A jornada headless registrada cobre recebimento do JSON, validação, conversão do alvo em pose, aceite pelo Nav2 e alteração da odometria.

O fluxo de simulação evoluiu para um ciclo de missão com saída da doca, navegação até o alvo e retorno à doca. Também foram criados comandos de teste rápido, diagnóstico, rota pelos três plots e encerramento do ambiente.

Essa validação comprova o lado mock/simulador. Ela não substitui a execução completa originada pelo app em um celular físico.

### 3.6. Aplicativo Android

Foi criado um app nativo em Kotlin com:

- flavors `mock` e `dat`;
- classificador local consumindo o artefato canônico compartilhado;
- máquina de interação e confirmação;
- resolvedor de alvo;
- transporte WebSocket;
- interfaces separadas para câmera, voz e integrações externas;
- identidade visual, fontes League Spartan e ícones da marca;
- configurações de privacidade, incluindo backup desabilitado e opt-out de analytics opcionais quando aplicável.

O adaptador DAT real ainda é um ponto de integração: a dependência e a fronteira existem, mas o ciclo oficial de sessão e captura do sample `CameraAccess` precisa ser conectado e validado no hardware.

### 3.7. Consolidação Android-only

Em 18 de agosto, a equipe decidiu abandonar iOS e focar exclusivamente em Android. Segundo o registro da tarefa, foram removidos 34 arquivos associados à plataforma descartada e atualizados README, arquitetura, propostas, PDFs, pitch, responsabilidades e tarefas.

O resultado arquitetural passou a ser uma única base Kotlin, sem React Native e sem duplicação de regra de negócio. `mockDebug` atende desenvolvimento e testes sem óculos; `datDebug` fica reservado à integração com o DAT em Android 12/API 31 ou superior.

Uma busca no estado atual não encontrou diretório `mobile/ios` nem fontes Swift/Xcode. Ainda existe, porém, uma frase antiga em `docs/mvp-spec.md` que exige “dois builds nativos”; ela contradiz a decisão Android-only e deve ser corrigida.

### 3.8. Preparação do ambiente Android

O ambiente local foi preparado com:

- Ubuntu 24.04;
- JDK 21, acima do mínimo 17;
- Android SDK em `/home/matheus/Android/Sdk`;
- Platform API 36, Build-Tools e Platform-Tools;
- Gradle wrapper do projeto;
- ADB e Motorola Edge 40 Neo como aparelho de teste.

Um AVD Android 16/API 36 chegou a ser criado, mas o emulador não ficou estável no notebook de 8 GB. A equipe adotou o Edge 40 Neo físico, que é mais representativo para a demonstração. O Android Studio foi removido posteriormente para liberar recursos, preservando o SDK, o projeto e a execução por terminal.

Essas alterações são, em sua maioria, configuração da máquina e não mudança funcional do produto. O arquivo `local.properties`, quando presente, é local e não deve ser versionado.

### 3.9. Conclusão da AI-03 no aparelho físico

O preflight confirmou JDK, SDK, Platform API 36, Gradle e recursos do app. Na primeira resolução do build, foi identificado que OkHttp 5.5.0 exigia `compileSdk 37`, enquanto o projeto está congelado em `compileSdk 36` com AGP 8.11.1. A versão foi ajustada para OkHttp 5.4.0, compatível com API 36, sem introduzir uma nova dependência nem mudar a interface de transporte.

Também foram implementados:

- fixture compartilhado com 18 casos e SHA-256 do modelo;
- verificação de paridade semântica entre Python e Kotlin;
- tolerância numérica explícita para ruído de ponto flutuante;
- testes de regressão contra mudanças estruturais ou numéricas relevantes;
- atividade de benchmark exclusiva do flavor mock;
- evidência estruturada em `shared/ai/device_evaluation.json`.

Resultados no Motorola Edge 40 Neo, Android 15/API 35, ARM64:

| Evidência | Resultado |
|---|---:|
| Testes Kotlin | 12 aprovados |
| Build | `testMockDebugUnitTest assembleMockDebug` aprovado |
| Casos compartilhados | 18 |
| Inferências medidas | 540 |
| Divergências | 0 |
| Latência mediana | 229 µs |
| Latência p95 | 1.013 µs |
| Latência máxima | 1.178 µs |
| Pico de heap observado | 19.254.032 bytes |
| APK | aproximadamente 12 MB |

O benchmark usa somente frases fixas do fixture. Não captura áudio, não usa transcrições reais, não acessa a rede e não envia comandos ao robô.

### 3.10. QA-01 — falhas seguras antes do transporte

A QA-01 foi concluída com nove testes da máquina de estados. Os cenários de recusa, intenção desconhecida, alvo ausente ou desconhecido, conflito entre alvo visual e falado, timeout e confirmação tardia terminam sem produzir comando. Uma confirmação ambígua pode ser repetida dentro do prazo, mas também não cria comando.

Na validação registrada, 12 testes Kotlin e o APK `mockDebug` passaram. Essa evidência comprova a fronteira local antes do transporte; desconexão WebSocket, expiração e duplicata no fluxo integrado continuam pertencendo à QA-02.

### 3.11. QA-03 — privacidade, áudio e eficiência

Foi criado um inventário que separa os dados tratados pelo Maestro, Android, DAT/Meta e bridge externo, além de um coletor Android que não captura logcat, mídia, transcrição, conteúdo de arquivos ou serial do aparelho.

No Edge 40 Neo foram executados cinco ciclos seguros no `mockDebug`, usando alvo e intenção fixos, cancelamento e reinício. O protocolo não usou DAT nem microfone e não confirmou ou enviou comandos. Entre os snapshots:

- nenhum caminho interno com nome ou extensão suspeita foi encontrado;
- o único arquivo criado foi `./files/profileInstalled`, marcador técnico do AndroidX Profile Installer;
- o estado térmico permaneceu `NONE` e a temperatura de bateria variou de 36,0 °C para 37,9 °C;
- o PSS final observado foi 102585 KB, aproximadamente 100,2 MiB;
- Rafael confirmou que ouviu as frases do TTS pelo alto-falante inferior do telefone, sem gravação de áudio.

A medição de consumo permaneceu inconclusiva porque o estado da bateria mudou de `FULL` para `CHARGING` e o nível permaneceu em 100%. O armazenamento externo, o encerramento de recursos em runtime e a jornada simultânea com DAT e microfone também continuam pendentes. Por esses motivos, a QA-03 permanece `PARTIAL`.

### 3.12. QA-04 — matriz dos cinco checkpoints

Foi criada uma spec, uma matriz JSON versionada, um validador e testes automatizados para os cinco checkpoints: IA, câmera ou microfone, output por áudio, privacidade e eficiência. A matriz referencia arquivos rastreáveis, não armazena mídia bruta e só permite `overall_status=PASS` quando os cinco checkpoints estiverem aprovados.

O estado atual é `PARTIAL`: a IA possui modelo, paridade e benchmark físico, mas precisa ser renovada no APK final; entrada física dos óculos permanece `BLOCKED`; o TTS do telefone foi ouvido, mas o encerramento em runtime e a rota dos óculos não foram validados; privacidade e eficiência possuem evidências parciais da execução mock.

## 4. Testes e evidências acumuladas

| Área | Evidência disponível | Estado |
|---|---|---|
| Contrato/bridge | schemas, fixtures e testes de expiração, confirmação e duplicata | Concluído no núcleo |
| IA Python | avaliação, integridade do artefato e paridade | Concluído |
| IA Kotlin | 13 casos compartilhados e hash do modelo | Concluído |
| IA em aparelho | 390 inferências no Edge 40 Neo, sem divergência | Concluído |
| Android mock | oito testes Kotlin e APK `mockDebug` | Concluído |
| Segurança local QA-01 | nove cenários sem comando indevido; 12 testes Kotlin e APK aprovados | Concluído |
| Visão estática | oito testes para conhecido, desconhecido e ambíguo | Concluído |
| ROS/Gazebo | jornada headless e movimentação registradas | Concluído no simulador |
| TTS no aparelho | frases ouvidas pelo alto-falante inferior do Edge 40 Neo | Concluído para a rota do telefone |
| Privacidade em runtime | cinco ciclos mock sem caminho interno suspeito | Parcial |
| Eficiência em runtime | térmico `NONE`, temperatura e PSS registrados | Parcial; bateria inconclusiva durante carregamento |
| Matriz QA-04 | cinco checkpoints, referências rastreáveis e validador automatizado | Parcial |
| DAT real | sessão/captura do sample oficial | Pendente |
| Câmera + microfone no aparelho | execução simultânea no modelo do evento | Pendente |
| App físico até o Gazebo | ACK e movimento originados pelo celular | Pendente |
| Falhas ponta a ponta | desconexão e falhas integradas com bridge/simulador | Pendente |

Há um registro anterior de `make test-quick` com 31 testes portáteis, 14 do bridge e validação do Compose. Em uma execução posterior da suíte Python global, o pacote de desenvolvimento `websockets`, já declarado em `tools/requirements-dev.txt`, não estava instalado no host; por isso, essa execução global específica não deve ser descrita como aprovada até uma nova rodada em ambiente completo.

## 5. Privacidade, segurança e eficiência

As mudanças mantiveram os princípios permanentes do projeto:

- confirmação de áudio antes de produzir um comando confirmado;
- UUID, expiração e deduplicação no bridge;
- conflito de alvo tratado como falha segura;
- mídia somente em memória e sem persistência padrão;
- logs restritos a estado, ID, latência e erros técnicos;
- IA de intenção local, pequena e sem chamada externa;
- captura sob demanda em vez de streaming permanente;
- separação entre dados tratados pelo app, Android, DAT e serviços externos.

A QA-03 avançou com inventário de dados, auditoria estática e um par de snapshots físicos após cinco ciclos mock. Não foram encontrados caminhos internos suspeitos e a saída TTS pelo telefone foi confirmada. A temperatura e a condição térmica foram registradas, mas o consumo de bateria não pode ser concluído porque o aparelho entrou em estado `CHARGING` durante a coleta.

A aprovação final ainda exige repetir a medição com alimentação controlada, auditar o armazenamento externo, comprovar o encerramento dos recursos e executar câmera e microfone simultâneos no aparelho da demonstração. Nenhum resultado parcial deve ser apresentado como validação do comportamento interno do Android ou do DAT.

## 6. Documentação, identidade visual e pitch

O projeto recebeu identidade visual baseada em amarelo, verde, azul e branco, logos, ícones Android e a família League Spartan. Foram criadas propostas resumida e técnica, PDFs exportados, apresentação editável de seis slides, storyboard e roteiro de pitch com alvo entre 2min40s e 2min55s.

Os materiais foram revisados para remover a plataforma descartada. A gravação da demonstração, os três ensaios do pitch e a exportação final do vídeo continuam pendentes.

## 7. Estado atual por responsabilidade

### Rafael — IA, testes e métricas

- AI-01: concluída;
- AI-02: concluída;
- AI-03: concluída e comprovada no Edge 40 Neo;
- QA-01: concluída, em conjunto com Átila;
- QA-03: inventário, auditoria e coleta mock parcial concluídos com a equipe;
- QA-04: spec, matriz e validador concluídos; fechamento dos cinco checkpoints ainda parcial;
- ensaios e edição final do pitch: pendentes, em conjunto com Felipe.

### Átila — Android, DAT, áudio e estados

- base Android mock implementada e compilada;
- classificador integrado e APK validado;
- sessão/câmera DAT real pendente;
- TTS ouvido pelo alto-falante do Edge 40 Neo; STT e rota Bluetooth dos óculos pendentes;
- recusa, ambiguidade e timeout aprovados na fronteira local; caminho feliz integrado ainda pendente.

### Felipe — visão, ROS 2 e simulador

- marcador, detector estático e resolvedor implementados;
- bridge seguro e simulação headless registrados como concluídos;
- frame real no adaptador de visão pendente;
- integração física completa e testes de desconexão pendentes.

## 8. Pendências e inconsistências identificadas

1. `docs/mvp-spec.md` ainda menciona “dois builds nativos”, apesar da decisão Android-only.
2. `docs/tasks/mvp-week.md` mantém “Build Android executado no Motorola” desmarcado, embora o build, a instalação e o benchmark físico da AI-03 estejam registrados.
3. `docs/architecture.md` ainda descreve o build do modelo Android como pendente, informação superada pela validação de 19 de agosto.
4. A versão atual do DAT deve ser confirmada em fonte oficial antes de qualquer alteração de dependência ou API.
5. O adaptador DAT é apenas uma fronteira preparada; ainda não há comprovação de sessão e captura reais.
6. O QR ainda precisa ser detectado a partir de um frame real dentro do app.
7. O TTS foi ouvido pelo telefone, mas STT, rota Bluetooth, câmera e microfone simultâneos ainda precisam ser testados no aparelho exato da demonstração.
8. A jornada Android → WebSocket → bridge → Gazebo ainda precisa de evidência ponta a ponta.
9. O conjunto de avaliação da IA tem apenas 16 exemplos separados; a métrica é útil para o MVP, mas não representa validação ampla em campo.
10. O workspace principal não oferece histórico Git utilizável; este relatório não substitui uma auditoria de commits e autores na cópia Git completa.

## 9. Próximo ponto de partida recomendado

O melhor próximo passo independente para Rafael é consolidar a QA-03/QA-04 e manter as afirmações documentais alinhadas às evidências, enquanto DAT e integração ponta a ponta avançam com os outros responsáveis.

Sequência recomendada:

1. manter a matriz QA-04 sincronizada com cada evidência entregue pela equipe;
2. repetir a coleta de bateria com o Edge 40 Neo desconectado da energia e com condições iniciais registradas;
3. comprovar encerramento de TTS e recursos em runtime sem gravar áudio ou transcrição;
4. renovar hashes, paridade, latência e memória da AI-03 somente após o congelamento do APK final;
5. revisar relatório, proposta e formulário de submissão para remover afirmações superadas ou não comprovadas;
6. deixar a revisão do roteiro do pitch para uma etapa posterior, conforme decisão da equipe.

## 10. Conclusão

O projeto já possui uma base coerente e verificável: Android/Kotlin, IA local versionada, segurança por confirmação, alvo mapeado, bridge independente do fabricante e simulação ROS 2/Gazebo. A mudança para Android-only reduziu o risco de dispersão e permitiu concluir a avaliação da IA no aparelho físico.

Os marcos mais recentes são a conclusão da AI-03 e da QA-01, a coleta parcial da QA-03 no Edge 40 Neo e a criação da matriz verificável da QA-04. O foco agora deve ir para a medição controlada de bateria, o fechamento das evidências físicas e a integração ponta a ponta no celular, mantendo claramente separados o que funciona com mock, o que foi observado no telefone e o que ainda depende do DAT real.
