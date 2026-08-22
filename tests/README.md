# Catálogo de testes

Esta é a entrada única para localizar e executar os testes do Maestro Agrícola.
O repositório reúne Python, Android/Gradle e ROS 2; por isso, centralizar todos
os arquivos fisicamente quebraria convenções importantes de descoberta. A
organização centraliza o catálogo e os comandos, mas mantém cada suíte no local
esperado por sua ferramenta.

## Estrutura

```text
tests/
├── portable/             # testes Python executáveis sem Android ou ROS no host
│   ├── ai/               # modelo, paridade, treino e resolução de alvo
│   ├── android/          # preflight e evidência Android sanitizada
│   ├── robotics/         # simulação, visão, QR e cliente mock
│   └── qa/               # matriz QA-04 e consistência documental
├── android/              # índice dos testes Kotlin mantidos no source set Gradle
├── ros/                  # índice dos testes mantidos no pacote ROS
└── hardware/             # índice dos ensaios manuais em dispositivos físicos
```

Os testes do submódulo `mobile/android/third_party/llama.cpp` são externos e
não fazem parte da organização nem dos gates próprios deste projeto.

## Comandos principais

Execute a partir da raiz do repositório:

```bash
# todos os testes Python portáteis
python3 -m unittest discover -s tests/portable -t . -p 'test_*.py'

# bridge ROS sem exigir plugins externos do pytest
PYTHONPATH=robot_ws/src/maestro_robot_bridge \
  python3 -m unittest discover \
  -s robot_ws/src/maestro_robot_bridge/test -p 'test_*.py'

# Android mock
cd mobile/android
./gradlew :app:testMockDebugUnitTest --no-daemon
```

Os comandos específicos e os pré-requisitos estão em:

- [testes Python portáteis](portable/README.md);
- [testes Android](android/README.md);
- [testes ROS](ros/README.md);
- [ensaios de hardware](hardware/README.md).

## Regra de classificação

Um teste novo deve ficar:

- em `tests/portable/<domínio>` quando roda apenas com Python e dependências
  portáteis do projeto;
- em `mobile/android/app/src/test` quando testa código Kotlin/Android com o
  runner do Gradle;
- em `mobile/android/app/src/androidTest` quando precisa do runtime Android;
- no diretório `test` do pacote ROS quando pertence a esse pacote;
- documentado como ensaio manual quando exige celular, óculos, robô ou Gazebo
  interativo.

Não duplique o mesmo teste apenas para fazê-lo aparecer nesta pasta. Os índices
apontam para as fontes canônicas.
