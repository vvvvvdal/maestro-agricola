# QA-04 — matriz de evidências dos cinco checkpoints

## Objetivo

Consolidar evidências reproduzíveis para os cinco checkpoints obrigatórios do programa: inteligência artificial, câmera ou microfone, output por áudio, privacidade e dados, e eficiência de bateria.

Rafael mantém a spec, a matriz e as métricas. Isso não transforma em responsabilidade exclusiva de Rafael as coletas físicas que pertencem aos domínios mobile, DAT, áudio e visão.

## Artefato canônico

A situação atual fica registrada em `shared/evidence/qa04_checkpoints.json`. O arquivo contém somente metadados técnicos, referências a arquivos do repositório, resultados resumidos e pendências. Ele não armazena áudio, imagem ou transcrição real.

A rastreabilidade separa os hashes do modelo e APK efetivamente benchmarkados dos hashes do candidato atual. O validador compara o modelo atual com o artefato canônico e o fixture de paridade, compara a geração benchmarkada com `device_evaluation.json` e impede `PASS` enquanto houver divergência ainda não revalidada.

Validação:

```bash
python3 tools/check_qa04_evidence.py
python3 tools/check_qa04_evidence.py \
  --apk mobile/android/app/build/outputs/apk/mock/debug/app-mock-debug.apk
python3 -m unittest tests.portable.qa.test_qa04_evidence
```

O primeiro comando valida somente evidências versionadas e é reproduzível mesmo quando o clone contém builds locais antigos. Depois de montar o APK candidato, o segundo comando confere explicitamente seu SHA-256 contra a matriz.

## Estados permitidos

| Estado | Significado |
|---|---|
| `NOT_STARTED` | Nenhuma evidência útil foi registrada. |
| `PARTIAL` | Há evidência válida, mas falta pelo menos um critério obrigatório. |
| `PASS` | Todos os critérios foram demonstrados no ambiente declarado. |
| `FAIL` | Uma execução foi realizada e contrariou um critério. |
| `BLOCKED` | A coleta depende de hardware, integração ou decisão ainda indisponível. |

Código implementado, mock ou intenção de teste não bastam para marcar `PASS`. A QA-04 só termina quando os cinco checkpoints estiverem `PASS` e `overall_status` também for `PASS`.

**Escopo da entrega de seleção de 22/08/2026:** a demonstração do MVP usa `datDebug` + MockDeviceKit em Android físico. Isso é evidência pré-hardware e não promove automaticamente os checkpoints que exigem entrada dos Meta Wearables físicos. Esses checkpoints permanecem `PARTIAL`/pendentes para a fase presencial caso a equipe seja selecionada; essa pendência não deve ser confundida com falha do E2E operacional da Task 7.

## Responsabilidades

| Pessoa | Responsabilidade na QA-04 |
|---|---|
| Rafael | Manter spec e matriz, validar IA, hashes, métricas, consistência e afirmações do pitch. |
| Átila | Produzir evidências físicas de DAT/câmera, microfone, TTS, ciclo de recursos, bateria e temperatura no Android. |
| Felipe | Apoiar a prova de detecção visual e a ligação do frame ao `target_id`. |
| Equipe | Revisar privacidade, aprovar eventual persistência excepcional de mídia e aceitar a evidência final. |

## Critérios por checkpoint

### 1. Inteligência artificial

Para `PASS`:

- o APK executa o modelo canônico localmente, sem servidor de inferência;
- SHA-256 do modelo, APK e fixture são registrados;
- os 18 casos compartilhados não divergem entre Python e Kotlin;
- mediana, p95, máximo e pico aproximado de heap são coletados no aparelho físico;
- a coleta usada na entrega corresponde ao APK final ou a diferença de build é justificada e aprovada.

Situação atual: a coleta de 19 de agosto permanece como evidência histórica do modelo e APK efetivamente benchmarkados no Edge 40 Neo, com 18 casos, 540 inferências e zero divergências. O candidato pós-Task 6 possui novo modelo canônico e novo APK; seus hashes estão registrados separadamente e divergem da coleta física anterior. `final_build_benchmark_pending` continua `true` e o checkpoint permanece `PARTIAL` até uma nova coleta no candidato final.

Em 22 de agosto de 2026, a rastreabilidade do candidato foi atualizada sem promover evidência física:

- modelo canônico: `a456c00f590152157a7f625c10955aed7f610398f2493155537a466f7f1fa243`;
- APK `mockDebug` pós-Task 6: `618e30963eb190d3df8a9c91974f6431e64439fb5c8374b2bdb47820007f8169`;
- benchmark do dispositivo: preservado nos hashes históricos de `device_evaluation.json`;
- decisão: repetir o benchmark físico antes de atribuir as métricas antigas ao candidato atual.

### 2. Câmera ou microfone

Para `PASS`:

- pelo menos uma entrada dos óculos aceita pelo programa é demonstrada no hardware real;
- a rota escolhida, o smartphone, Android, firmware e versão atual do DAT são registrados;
- se a câmera for usada, um frame sob demanda chega ao app e produz `target_id` conhecido;
- se o microfone dos óculos for usado, a fala chega ao reconhecimento nativo e produz uma transcrição curta;
- a mídia não é gravada pelo Maestro.

O caminho preferencial é a câmera via DAT. Mock, vídeo estático e microfone do telefone não devem ser apresentados como entrada dos óculos. Qualquer fallback precisa ser identificado e aceito explicitamente pelos avaliadores.

### 3. Output por áudio

Para `PASS`:

- TTS reproduz pergunta de confirmação e pelo menos um resultado de cancelamento, erro ou sucesso;
- a rota efetivamente usada é registrada: alto-falantes dos óculos, outro Bluetooth ou telefone;
- a fala é compreensível no aparelho da demonstração;
- o ciclo encerra o TTS ao destruir a atividade;
- nenhuma gravação de áudio é criada pelo app.

Não é necessário persistir áudio para provar o checkpoint. Uma observação humana identificada e logs técnicos sem conteúdo bruto são a evidência padrão.

Em 19 de agosto de 2026, Rafael confirmou que ouviu as frases do TTS pelo alto-falante inferior do Edge 40 Neo durante cinco ciclos mock. A observação comprova audibilidade e rota do telefone sem gravação de áudio; encerramento do TTS em runtime e rota Bluetooth dos óculos continuam pendentes.

### 4. Privacidade e dados

Para `PASS`:

- o código não cria arquivo de foto, áudio ou transcrição por padrão;
- uma execução confirma ausência desses artefatos no armazenamento controlado pelo app;
- logs não contêm mídia bruta nem transcrição de usuário;
- permissões solicitadas são justificadas;
- backup está desabilitado e opt-outs opcionais do DAT são registrados quando suportados;
- o fluxo de dados diferencia Maestro, Android, DAT/Meta e eventuais serviços externos.

Persistir mídia somente para uma evidência excepcional exige aprovação humana, finalidade, retenção e remoção documentadas.

### 5. Eficiência de bateria

Para `PASS`:

- o frame é capturado sob demanda ou a taxa reduzida é justificada;
- câmera, reconhecimento e TTS são encerrados ao fim da jornada;
- tamanho do modelo, latência e memória da IA são registrados;
- bateria e temperatura são medidas antes e depois de um protocolo físico reproduzível;
- aparelho, carga inicial, duração, número de interações e condições da coleta são registrados.

Não existe limiar numérico inventado nesta spec. A matriz registra o resultado bruto; um limite de aprovação só será adicionado se vier do programa ou de uma decisão humana documentada.

## Protocolo de coleta física

1. Registrar aparelho, Android, flavor, SHA-256 do APK e versão atual do DAT.
2. Fechar apps desnecessários e anotar bateria e condição térmica inicial.
3. Executar o fluxo definido por cinco minutos ou pela duração oficial informada no evento.
4. Demonstrar entrada, IA e output por áudio sem salvar mídia bruta.
5. Encerrar a interação e confirmar liberação dos recursos.
6. Anotar bateria, condição térmica final, falhas e rota de áudio.
7. Atualizar a matriz com caminhos de evidência, responsável e horário.
8. Marcar `PASS` somente após revisão dos critérios do checkpoint.

### Evidência E2E pré-hardware de 22 de agosto de 2026

No Samsung SM-X510/API 36, o flavor `datDebug` com MockDeviceKit executou a jornada operacional até o ROS 2/Nav2/Gazebo: `UNDOCK` explícito, captura repetível de `plot-03`, `SPRAY`, `DOCK` explícito e novo `UNDOCK`. Também foram observados `SPRAY` dockado sem movimento, conflito visual/voz e `CANCEL` sem envio.

Essa evidência fortalece os checkpoints de software, segurança, integração e tratamento de mídia simulada, mas continua sendo pré-hardware: não comprova frame, microfone, áudio, bateria ou firmware dos Meta Wearables físicos. Portanto, a matriz QA-04 não deve ser promovida artificialmente a `PASS` por causa deste E2E.

### Execução física parcial de 19 de agosto de 2026

Foi executado no Edge 40 Neo um protocolo sanitizado de 314 segundos com o APK `mockDebug` e o modelo canônico v2. Em cada um dos cinco ciclos, o alvo foi simulado, a intenção fixa de pulverização foi interpretada e a confirmação foi deixada expirar. Todos terminaram em `CANCELLED`, nenhum comando foi confirmado e o bridge não foi acionado.

O estado térmico permaneceu `NONE`, a temperatura de bateria variou de 37,9 °C para 37,0 °C e, com o app ativo nos dois snapshots, o PSS variou de 160140 KB para 149754 KB. A auditoria de caminhos internos continuou com zero nomes suspeitos de foto, áudio ou transcrição. A coleta não leu conteúdos, não capturou logcat, mídia, transcrição nem identificador do dispositivo.

A bateria permaneceu em 95%, porém o celular estava em `CHARGING` antes e depois por causa da conexão USB. Por isso consumo de bateria, armazenamento externo e jornada real com DAT/microfone continuam `PARTIAL`; esses dados não autorizam promover os checkpoints de privacidade ou eficiência para `PASS`.

## Privacidade da própria evidência

- Preferir JSON, hashes, contagens, logs sanitizados e checklist assinado.
- Não colocar fala de usuário, frame, áudio, token, localização precisa ou identificador pessoal na matriz.
- Gravações destinadas ao pitch são artefatos separados e exigem decisão explícita da equipe.
- Evidência local não deve afirmar que DAT ou rota Bluetooth foram validados antes da execução física.

## Critérios de aceite da QA-04

- [x] Spec dos cinco checkpoints criada.
- [x] Matriz JSON versionada com exatamente cinco checkpoints.
- [x] Evidências existentes ligadas a arquivos rastreáveis.
- [x] Lacunas físicas atribuídas aos responsáveis sem falso `PASS`.
- [x] Validador automatizado rejeita matriz inconsistente.
- [ ] Benchmark renovado no APK final.
- [ ] Entrada física dos óculos aprovada.
- [ ] Output por áudio aprovado no aparelho da demonstração.
- [ ] Auditoria de privacidade em runtime aprovada.
- [ ] Protocolo de bateria e temperatura concluído.
- [ ] Cinco checkpoints em `PASS` e checklist semanal encerrado.

## Fora de escopo

- Implementar o adaptador DAT ou o detector de frame real.
- Alterar dependências, permissões ou APIs do DAT.
- Substituir QA-03; suas evidências de privacidade e bateria alimentam esta matriz.
- Gravar o pitch ou armazenar mídia de demonstração.