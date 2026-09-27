# Avaliacao de casos externos para a apresentacao

Data da leitura: 26/09/2026. Posts do X sao fontes de terceiros: mostram uma
ideia, nao constituem benchmark independente nem evidencia do Maestro.

## Decisao por caso

| Post | Leitura | Uso no deck | Limite que deve ser dito |
| --- | --- | --- | --- |
| [Luiz Carvalho](https://x.com/luizcarvalhocom/status/2102055194070593894) | Relata Jev rapido e uma resposta ruim para um prompt adaptado, em contraste com Qwen 32B local lento. | Sim, como contraexemplo curto: velocidade nao substitui adequacao da tarefa. | E um teste anedotico, com prompt adaptado e hardware/modelos diferentes; nao mede capacidade geral. |
| [Humberto Filho](https://x.com/humbertocortezi/status/2101493117165666714) | Chama Jev de "if com IA" que devolve probabilidade. | Sim, como metafora inicial e depois correcao. | Um `if` e deterministico; Jev e uma predicao probabilistica e ainda precisa de limiar, regra e fallback. |
| [Kevin Grajeda](https://x.com/k_grajeda/status/2099952715430596710) | Apresenta o contraste entre gerar texto token a token e escolher entre opcoes. | Sim, para explicar por que `Choice` nao gera texto de saida. | "200x" e "400x" sao alegacoes promocionais, nao metricas do Maestro nem promessa geral. |
| [Justin Schroeder](https://x.com/jpschroeder/status/2100347770867458384) | Demo FSD inspirada em Tesla, depois aberta como JevPilot. | Sim, como estudo de harness: estado simbolico, opcoes de trajetoria e freio de seguranca em codigo. | E simulador; Jev nao le pixels nem substitui geometria, colisao ou freio. Nao e validacao em veiculo real. |
| [Daniel Avila](https://x.com/dani_avila7/status/2101885477158547753) | Sugere skill para Claude: Jev escolhe qual skill carregar e injeta somente ela no contexto. | Sim, como exemplo de roteamento de catalogo. | O roteador precisa poder retornar `NONE`; escolher uma skill errada pode ser pior que nao carregar nenhuma. Nao e parte do Maestro. |
| [Stefan](https://x.com/heystefan_/status/2101369117496521042) | Video de interface de designer; discussoes sugerem recomendacao interativa. | Nao como caso principal. | O mecanismo nao ficou verificavel na leitura do post; usar so como inspiracao visual seria fraco para esta audiencia. |
| [Tamara Tran](https://x.com/tamarajtran/status/2100694549362553153) | Propoe compactacao: dar `KEEP/DROP` para cada tool call, em vez de resumir tudo em prosa. | Sim, caso forte para decisao tipada. | E uma alegacao de plugin/demonstracao; preservar relevancia exige avaliar perda de contexto e ter fallback. |
| [mizorewww / Laya-MLX](https://x.com/mizorewww/status/2101473552956555427) | Porta Laya para MLX e relata decisao local rapida em Snake. | Sim, como contraponto de pesquisa: pesos abertos e inferencia local. | Nao e "melhor que Jev": modelos, hardware, idioma, prompt e metodo diferem. O runtime e para Apple Silicon, nao Android. |

## Laya: formulacao segura

O [Laya-MLX](https://github.com/mizorewww/laya-mlx) e um runtime Apache-2.0
para checkpoints de decisoes tipadas, com inferencia local em MLX/Apple Silicon.
O README do projeto relata P50 de 13,42 ms para Laya 421M e 7,39 ms para um
checkpoint multilingual 322M em um M3 Max; tambem explicita que esses numeros
nao sao comparaveis universalmente e que confianca nao garante acuracia.

Na apresentacao, Laya serve para fazer uma pergunta melhor: se a tarefa e uma
decisao de catalogo fechado, quando custo, latencia, privacidade e controle de
pesos tornam uma alternativa local mais interessante? Nao e candidato a
substituir o Jev no Maestro antes de contrato, benchmark pareado e avaliacao no
dispositivo-alvo.

## Linguagem para os slides

Use "resultado de terceiros", "autor reporta" e "demo" para esses casos. Nunca
use "prova", "SOTA", "melhor" ou "validado em producao" sem um benchmark
reproduzivel e comparavel.

## Onda de modelos de decisão (26/09/2026)

| Link enviado | Fonte primária conferida | Leitura para a apresentação |
| --- | --- | --- |
| [Jev em agentes](https://x.com/N01ennn/status/2103818303642689696) | Post recuperado pelo oEmbed oficial do X; [TypeSafe](https://typesafe.ai/blog/introducing-system-one-models-and-jev) documenta a interface | O post atribui um PDF de 11 páginas e um loop de nove etapas a Diogo Almeida. O PDF original não foi localizado nesta revisão. Mostrar apenas o padrão verificável de decisão tipada dentro de um harness; não narrar as nove etapas como verificadas. |
| [CLM](https://x.com/NFT_Chen/status/2103702227332559077) | [Repositório dos autores](https://github.com/Contrastive-LM/CLM) | O post cita “13×”. O README reporta até 9× em tarefas selecionadas e descreve objetivo contrastivo, dois encoders e cache de ações. Autores incluem Stanford e NVIDIA; não chamar de produto NVIDIA. |
| [Span-01](https://x.com/RespanAI/status/2103970381568921704) | [Anúncio](https://www.respan.ai/blog/introducing-span-1) e [documentação](https://www.respan.ai/docs/documentation/span-01/concept) | Modelo de 4B especializado em detecção de comportamento em traces. F1 geral publicado: 0,843 versus 0,715 de Jev no benchmark da própria empresa. A provocação de multiplicação no tweet não mede esse uso. |
| [Julia-1](https://x.com/supersonicai/status/2103922653585162248) | [Site oficial](https://supersoniclabs.ia.br/julia-1/), [organização brasileira](https://supersoniclabs.ia.br/) e [model card](https://huggingface.co/SupersonicLabs/Julia-1) | 144,3M parâmetros, base mmBERT-small, CPU/ONNX. Em typed decisions: 73,15% vs referência Jev 72,70%; em Banking77: 64% vs 87%. Os valores Jev foram herdados do protocolo, não reexecutados. O site oficial declara a equipe “From Brazil”. |

**Síntese inferida:** a proximidade dos anúncios não demonstra que cada modelo foi iniciado após Jev. As fontes mostram reuso de bases anteriores, interfaces tipadas e benchmarks públicos. As promessas de velocidade mudam com GPU/CPU, cache, opções, entrada e rede. A comparação útil ao Maestro exige o mesmo corpus, especialmente o estrato `CANCEL`/`CONFIRM`, o mesmo aparelho e métricas de latência, memória, calibração e erro crítico.
