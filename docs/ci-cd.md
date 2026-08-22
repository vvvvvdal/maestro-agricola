# CI/CD do Maestro Agrícola

## Objetivo

Automatizar os gates portáteis do repositório e entregar APKs de depuração para
validação interna, sem tratar runner de nuvem como evidência de hardware real.

## Decisões e ambiguidades resolvidas

- O CI rápido roda em pull requests, pushes na `main` e por acionamento manual.
- O baseline inicial considera a Task 6 aceita e inclui suas correções de
  avaliação, wiring seguro do Qwen e rastreabilidade QA-04 pós-Task 6.
- O build DAT usa segredo e, por segurança, roda apenas em push na `main` ou por
  acionamento manual. Não é usado `pull_request_target`.
- O CD inicial significa retenção temporária de APKs `debug` no próprio GitHub
  Actions. Publicação na Play Store e assinatura de release permanecem fora do
  escopo até que destino, keystore e versionamento sejam decididos.
- Qwen físico, Meta DAT real e Android -> ROS/Gazebo continuam manuais. O GGUF
  não é baixado, versionado nem publicado pelos workflows.
- A validação do bridge no CI é portátil e focada. Gazebo, GPU e ROS 2 completo
  não são iniciados em runner comum.

## Gates

| Gate | Workflow | Execução | Evidência |
|---|---|---|---|
| Modelo/IA/QA-04 | `CI quick` | PR, `main`, manual | artefato canônico + matriz + testes Python/IA |
| Bridge portátil | `CI quick` | PR, `main`, manual | testes unitários sem ROS no host |
| Android mock | `CI quick` | PR, `main`, manual | unit tests + APK `mockDebug` |
| Android DAT | `Android full` | `main`, manual | unit tests + APK `datDebug` |
| Qwen físico | manual | aparelho alvo | saída, latência, memória e temperatura |
| Meta DAT real | manual | smartphone + óculos | sessão, câmera e áudio simultâneos |
| E2E físico | manual | Android + ROS/Gazebo | comando confirmado até execução |

Os jobs portáteis e Android mock são independentes para reduzir tempo e deixar
a origem de uma falha explícita.

## Dependências fixadas

As actions oficiais são referenciadas por SHA completo:

| Action | Release aprovada | SHA |
|---|---|---|
| `actions/checkout` | v7 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | v7 | `5fda3b95a4ea91299a34e894583c3862153e4b97` |
| `actions/setup-java` | v5 | `b6effb05e454b25005698d916606bdc6ffcbf961` |
| `actions/upload-artifact` | v7 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |

Os runners instalam as versões já exigidas pelo projeto: JDK 17, Platform API
36, Build-Tools 36.0.0, NDK 29.0.13113456 e CMake 3.31.6.

## Segredo do DAT

O repositório precisa do secret `MWDAT_PACKAGES_TOKEN`, contendo um personal
access token classic com apenas `read:packages`. O workflow o injeta como
`GITHUB_TOKEN` somente nos passos Gradle que resolvem o DAT. O valor não deve
ser colocado em `local.properties`, YAML, logs ou documentação.

O token deve ter expiração curta e ser rotacionado antes de vencer. Se ele
estiver ausente ou sem acesso aos pacotes do DAT, `Android full` falha antes dos
testes com uma mensagem explícita.

## Comandos equivalentes locais

Na raiz:

```bash
python3 tools/train_intent_model.py --check
python3 tools/check_qa04_evidence.py
python3 -m unittest discover -s tests/portable -t . -p 'test_*.py'
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
  python3 -m unittest discover \
  -s robot_ws/src/maestro_robot_bridge/test -p 'test_*.py'
```

Em `mobile/android`:

```bash
./gradlew :app:testMockDebugUnitTest --no-daemon
./gradlew :app:assembleMockDebug --no-daemon
./gradlew :app:testDatDebugUnitTest --no-daemon
./gradlew :app:assembleDatDebug --no-daemon
```

Os dois últimos comandos exigem a credencial DAT somente no ambiente local.

## Artefatos entregues

Depois de um push aprovado na `main`:

- `CI quick` publica `app-mock-debug.apk` por sete dias;
- `Android full` publica `app-dat-debug.apk` por sete dias;
- nenhum workflow publica GGUF, mídia capturada, áudio ou transcrição;
- APK `debug` é destinado a QA interna e não equivale a release de produção.

Os artefatos ficam na execução correspondente em **Actions -> workflow ->
Artifacts**.

## Critérios de aceite

1. Pull requests recebem resultados separados para Python/IA/bridge e Android
   mock.
2. O Android mock compila com o submodule `llama.cpp` no hash canônico.
3. O Android DAT falha fechado sem secret e executa testes + build quando a
   credencial está configurada.
4. Actions têm somente `contents: read`, credenciais de checkout não persistem
   e dependências de action usam SHA completo.
5. Nenhum gate automático afirma comprovar Qwen físico, Meta DAT real ou E2E
   Android -> ROS/Gazebo.
6. APKs publicados são temporários, de depuração e não contêm o GGUF.

## Limitações e próxima evolução

- O primeiro resultado real dos runners só existe depois de publicar a branch
  e executar os workflows no GitHub.
- Os testes opcionais de visão que dependem de OpenCV/NumPy podem ser marcados
  como `skipped`, pois essas bibliotecas não pertencem hoje a
  `tools/requirements-dev.txt`. Um gate de visão separado exige aprovação das
  dependências e não deve ser introduzido implicitamente no CI de IA/bridge.
- Branch protection deve ser configurada depois que os nomes dos checks forem
  criados pela primeira execução bem-sucedida.
- CD de release exige decisão humana sobre application ID final, assinatura,
  versionamento, canal de distribuição e proteção dos respectivos segredos.
