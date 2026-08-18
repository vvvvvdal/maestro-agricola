# Plano de aceleração das branches — 18 de agosto de 2026

## Objetivo

Usar o tempo disponível de Felipe para reduzir pendências das frentes de Átila e Rafael sem criar silos, sem declarar testes de aparelho que não ocorreram e sem misturar domínios em um único commit.

## Ambiguidades e limites

- As branches `feat/android-mock-smoke`, `feat/ios-mock-smoke`, `feat/vision-qr` e `feat/ai-device-eval` estão no mesmo commit de `main` e não contêm trabalho exclusivo dos colegas neste momento.
- O host atual não possui Java/JDK, Android SDK, Swift, Xcode ou simuladores mobile. Builds físicos não podem ser aprovados aqui.
- OpenCV já está disponível no ambiente e o QR versionado é decodificável. Nenhuma dependência será adicionada ao projeto sem aprovação humana.
- Alterações serão feitas uma branch por vez e permanecerão locais; nenhum push será realizado.
- A integração entre branches será feita somente depois de cada evidência isolada e de revisão pelos responsáveis de domínio.

## Ordem por risco

### 1. `feat/android-mock-smoke` — preflight

Critérios:

1. Confirmar a presença de JDK 17, Android SDK 36 e `adb` antes de tentar o build.
2. Quando a toolchain existir, executar `testMockDebugUnitTest` e `assembleMockDebug`.
3. Não tocar no adaptador DAT nem alterar dependências durante o smoke mock.
4. Instalação no Motorola e voz/TTS continuam sendo evidência manual de Átila.

Estado inicial: bloqueado neste host por ausência de JDK e Android SDK. O bloqueio é ambiental, não uma falha de código já comprovada.

### 2. `feat/vision-qr` — VIS-02

Critérios:

1. Uma imagem do QR versionado retorna `plot-03`.
2. Imagem sem QR retorna `UNKNOWN` e nunca um alvo padrão.
3. QR decodificado mas ausente no mapa de alvos também retorna `UNKNOWN`.
4. A saída é JSON pequeno com estado, `target_id`, confiança operacional e timestamp.
5. Testes entram no conjunto Python sem tornar OpenCV uma dependência silenciosa.

### 3. `feat/ai-device-eval` — AI-03

Critérios:

1. Casos canônicos de paridade são exportados a partir do modelo compartilhado.
2. Fixture registra texto, rótulo e confiança esperados com limiar 0,40.
3. Python verifica que o fixture está atualizado.
4. Kotlin e Swift recebem testes que consomem exatamente o mesmo fixture, sem copiar pesos ou regras.

### 4. `feat/ios-mock-smoke` — preflight e revisão estática

Critérios:

1. Validar estrutura do `project.yml`, recursos e testes sem alegar compilação.
2. Registrar os comandos exatos para gerar o projeto e rodar testes no Mac.
3. Build no iPhone 13, reconhecimento de voz e rota Bluetooth continuam sendo evidências físicas de Átila.

## Estratégia de commits

- `docs: plan cross-branch acceleration`
- `feat(vision): decode allowlisted plot QR`
- `test(ai): add cross-platform parity fixtures`
- `docs(mobile): add reproducible device preflight` somente se houver mudança útil além do bloqueio já documentado.

## Regra de integração

Não fazer merge automático entre as branches. Ao final, entregar a Átila e Rafael a lista de commits locais para revisão ou cherry-pick. Mudanças em contrato, dependência, privacidade ou DAT exigem decisão conjunta antes de integrar.

## Resultado da execução

Todas as branches terminaram com árvore limpa e continuam somente locais, sem push:

| Branch | Commits | Evidência produzida | Limite preservado |
|---|---|---|---|
| `feat/android-mock-smoke` | `9487a84` | preflight e 3 testes | build, voz e TTS aguardam JDK/SDK e Motorola |
| `feat/vision-qr` | `17ec003`, `be94068` | textura `plot-03`, vazio, desconhecido e ambiguidade; 8 testes | VIS-03 aguarda frame dentro do app |
| `feat/ai-device-eval` | `ae36a5e`, `d97c31b` | fixture de 11 casos e 2 testes da referência | testes Kotlin/Swift e benchmark aguardam aparelhos |
| `feat/ios-mock-smoke` | `1cf8b6e`, `21811dd` | preflight e 3 testes | build, voz e TTS aguardam Mac e iPhone 13 |

Verificações adicionais executadas nas branches de implementação:

- visão: 14 testes Python do diretório raiz e 4 do bridge passaram;
- IA: 8 testes Python do diretório raiz e 4 do bridge passaram; JSON e YAML foram validados;
- iOS: 9 testes Python do diretório raiz e 4 do bridge passaram;
- nenhum pacote, token ou credencial foi adicionado.

## Ordem recomendada de revisão e integração

1. Felipe revisa `be94068`, pois é a nova evidência visual que mais fortalece o MVP e o pitch.
2. Rafael revisa `d97c31b` e confirma se os 11 rótulos representam a política operacional desejada.
3. Átila executa `9487a84` no ambiente Android e `21811dd` no Mac; só depois registra build e aparelho como aprovados.
4. A equipe escolhe uma branch de integração e incorpora os pares completos de commits. Se houver conflito apenas em `docs/tasks/README.md`, preservar todas as entradas do índice.
5. Rodar novamente testes, demo no Gazebo e ambos os mocks antes de congelar features.

## Decisão de escopo para o restante da semana

Não adicionar uma segunda ação agrícola, localização sem QR, robô físico ou um modelo maior. A prioridade é fechar uma única jornada demonstrável: QR `plot-03` → intenção local `SPRAY` → confirmação explícita → WebSocket → Nav2/Gazebo. Para o pitch, usar como prova já executada a visão estática, a IA local e o movimento simulado; chamar builds e uso dos óculos de próximos gates até a evidência física existir.
