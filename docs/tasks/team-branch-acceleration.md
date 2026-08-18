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
