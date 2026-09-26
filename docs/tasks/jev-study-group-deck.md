# Task: Deck do grupo de estudos Jev

## Status

Concluida em 23/09/2026 e revisada em 24/09 e 26/09/2026.

## Objetivo

Transformar o roteiro de 50 minutos em um deck tecnico, local e editavel para
o grupo de estudos de RL. O deck fica fora de `docs/pitch/` e conduz uma
discussao de evidencia, nao uma venda do projeto.

## Entrega

- [`jev-rl-study.html`](../study-groups/jev-rl-2026-10-01/slides/jev-rl-study.html)
  e [`jev-rl-study.css`](../study-groups/jev-rl-2026-10-01/slides/jev-rl-study.css):
  deck HTML local com 24 laminas, navegacao por teclado/toque e notas do apresentador.
- 46 minutos de conteudo e quatro de debate, conforme o
  [`roteiro`](../study-groups/jev-rl-2026-10-01/presentation-script.md).
- Evidencias medidas, resultados de terceiros e hipoteses/roadmap recebem
  etiquetas visiveis e fontes numeradas.
- As capturas JEV-50 dizem literalmente `fixture mock local - nao executa o robo`.
- O bloco de casos externos usa xadrez, direcao no HighwayEnv/JevPilot, triagem
  de PR, sugestao de skills, compaction por relevancia e Laya-MLX. Cada fonte
  de terceiros e limitada ao seu harness; Laya e contraponto local Apple
  Silicon, nao afirmacao de superioridade nem candidato Android.
- O deck explica RL, RLHF, RLVR e RLCD como sinais/objetivos diferentes; RLCD
  continua sendo descricao do fornecedor, nao receita publicamente auditavel.
- A secao Maestro inclui minimizacao preventiva: foto sob demanda processada em
  memoria para QR, transcricao efemera e gate local antes do modo remoto Jev.
  Ela nao declara anonimizacao ou conformidade LGPD integral.
- O bloco final foi atualizado de roadmap para capacidade entregue: missao
  `UNDOCK -> SPRAY plot-02 -> consulta plot-03 -> DOCK` em `mockDebug`/Gazebo,
  com parser local, `Command` individual por etapa e confirmacao separada.

## Limites

- A decisao do experimento permanece `HOLD`.
- O deck nao afirma integracao Android remota, execucao de ROS, ASR, resolucao
  de alvo, confirmacao ou controle do robo nas capturas locais.
- A evidencia JEV-41R continua limitada a uma rodada de 60 falas sinteticas.
- O caso HighwayEnv e uma simulacao de terceiro; nao e validacao em veiculo
  real nem benchmark controlado contra outro agente.
- A demo de PR nao le o repositorio inteiro nem executa testes. Seus numeros de
  custo e latencia sao alegacoes da propria demo por chamada.
- A validacao da missao e simulacao Gazebo; nao demonstra aplicacao agricola
  fisica. Jev nao cria o plano nem executa suas etapas.
- A privacidade descrita e uma medida tecnica de minimizacao. SDKs/provedores
  externos e a validacao de camera em oculos Meta reais permanecem pendentes.

## Validacao

- As 24 laminas mantem a sequencia, o tempo e os limites do roteiro.
- Os SVGs, capturas e CSS referenciam apenas assets locais versionados; o deck
  nao depende de CDN, internet ou chave para renderizar.
- Validacao visual em viewport desktop e em escala de telefone; sem corte ou
  sobreposicao nao intencional.

## Proxima task

JEV-55: ensaio 1 cronometrado, com registro de cortes e perguntas que ainda
precisam de explicacao melhor.
