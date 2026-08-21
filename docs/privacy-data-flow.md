# Privacidade e fluxo de dados

## Objetivo

Documentar separadamente os dados tratados pelo Maestro Agrícola, pelo Android, pelo Meta Wearables Device Access Toolkit (DAT) e pelos componentes externos da demonstração. Este documento descreve o código atual e explicita o que ainda depende de validação física.

## Princípios

- Captura sob demanda e processamento local sempre que possível.
- Nenhuma foto, gravação de áudio ou transcrição é persistida pelo Maestro por padrão.
- Nenhum movimento é enviado antes de confirmação explícita.
- Logs devem conter somente estado, identificadores técnicos, métricas e erros, sem mídia bruta.
- Credenciais, tokens e chaves não pertencem ao repositório.
- Persistência excepcional para evidência exige aprovação humana, finalidade, retenção e remoção documentadas.

## Inventário por responsável pelo tratamento

| Responsável | Dados | Origem e finalidade | Tratamento e destino | Persistência do Maestro | Estado da evidência |
|---|---|---|---|---|---|
| Maestro — câmera | Foto sob demanda ou `target_id` simulado | DAT/MockDeviceKit ou `MockFrameSource`; resolver um talhão conhecido | ZXing local reduz a foto a `target_id` e timestamp; não inventa confiança | Não prevista | MockDeviceKit aprovado; DAT em óculos reais pendente |
| Maestro — voz | Transcrição curta | `SpeechRecognizer`; classificar intenção | Texto permanece na memória da atividade e entra no classificador local | Não prevista | Código implementado; rota física pendente |
| Maestro — assistente Qwen | Transcrição curta somente quando roteada ao assistente | `LanguageRouter`/assistente; responder perguntas do domínio Maestro | Inferência local no GGUF; transcrição e resposta ficam em memória | GGUF é artefato local persistente; prompts/respostas não são salvos pelo Maestro | Runtime/smoke físico validado; wiring na `MainActivity` pendente |
| Maestro — IA | Texto, intenção, confiança e métricas | Classificador JSON local | Resultado alimenta a máquina de estados | Modelo e fixtures versionados; fala do usuário não é salva | Modelo e benchmark aprovados |
| Maestro — comando | UUID, horário, intenção, alvo, confirmação e expiração | Máquina de estados após confirmação | JSON segue por WebSocket ao bridge | Não há banco local; bridge pode registrar telemetria técnica | Contrato e bridge implementados |
| Maestro — áudio de saída | Frases curtas de confirmação, cancelamento, erro e sucesso | Máquina de estados | Texto é entregue ao TTS do Android | O app não grava a saída | TTS ouvido no alto-falante inferior do Edge 40 Neo; rota dos óculos pendente |
| Android | Áudio do microfone, transcrição, síntese de voz, permissões e sandbox | APIs nativas e provedor configurado no aparelho | O sistema operacional ou o provedor de reconhecimento/TTS pode tratar dados conforme sua configuração | Governada pelo Android/provedor, não pelo código do Maestro | Saída TTS física confirmada; provedor STT ainda pendente |
| DAT/Meta | Registro, sessão, permissões, câmera e possível telemetria do SDK | Óculos ou MockDeviceKit e SDK | Fluxo definido pelo DAT e pela configuração da conta/app | Fora do controle direto do Maestro; analytics e crash reporting opcionais desabilitados | Adaptador 0.9.0 aprovado no MockDeviceKit; hardware real pendente |
| Bridge ROS 2 | JSON de comando e ACK, IDs, estados e erros | App Android e simulador | Validação, deduplicação e conversão em meta Nav2 | Logs técnicos podem existir no ambiente da demo | Testes do núcleo aprovados |
| Serviços externos de IA | Nenhum dado de inferência do Maestro | Não aplicável | O classificador de intenção não usa servidor externo | Não aplicável | Comprovado pelo artefato local |

## Fluxo da câmera

```text
Óculos/DAT ou mock -> FrameSource -> detector/resolvedor -> target_id
                                                   -> frame liberado
```

O flavor mock retorna um alvo fixo e não representa captura real. O flavor DAT
0.9.0 implementa sessão, `DeviceSession.addCamera()`, stream e foto sob demanda.
No modo de desenvolvimento explicitamente identificado como `dat-mockdevice`,
uma fixture empacotada é transmitida por pipe de um provider não exportado para
o MockDeviceKit. ZXing processa a foto em memória e libera o bitmap após reduzir
o conteúdo a um alvo permitido.

O Maestro não deve gravar o frame na galeria, armazenamento interno, cache ou logs. A auditoria em runtime verificará nomes e contagens de arquivos criados pelo app, mas essa verificação não substitui inspeção do ciclo real do SDK.

## Fluxo de voz e áudio

```text
Microfone/rota ativa -> SpeechRecognizer do Android -> transcrição em memória
    -> classificador local -> máquina de estados -> texto curto -> TTS Android
```

`EXTRA_PREFER_OFFLINE=true` expressa preferência por reconhecimento offline, mas não garante que todo provedor instalado trabalhe sem rede. A versão do Android, o pacote de idioma e o provedor ativo precisam ser registrados no ensaio. O DAT não é tratado como API de STT ou TTS.

O app não chama APIs de arquivo no caminho de voz atual. A transcrição aparece no estado Compose para diagnóstico durante a interação e deve desaparecer com o ciclo da atividade; ela não deve ser copiada para log ou evidência.

## Fluxo do comando

```text
transcrição operacional -> LocalIntentClassifier -> InteractionEngine
-> confirmação explícita -> Command JSON -> WebSocket -> bridge ROS 2
```

O assistente Qwen não participa desse fluxo. A arquitetura planejada envia somente `UNKNOWN` ao assistente e não oferece a ele referência para `Command`, WebSocket, ROS ou estado do robô.

### Fluxo do assistente Qwen

```text
transcrição UNKNOWN -> LanguageRouter -> QwenDomainAssistant
-> NativeQwenEngine/llama.cpp -> JSON CHAT | OUT_OF_SCOPE -> UI/TTS
```

O GGUF é armazenado localmente no aparelho quando provisionado para o smoke/desenvolvimento. Ele não contém dados pessoais do operador e não é versionado no repositório. O Maestro não grava prompt, resposta ou histórico de conversa em arquivo; o runtime limpa o turno e preserva apenas o cache do system prompt enquanto o processo está ativo. A integração desse fluxo na tela principal ainda está pendente.

## Permissões e configurações Android

| Item | Justificativa | Controle atual | Pendência |
|---|---|---|---|
| `INTERNET` | WebSocket com o bridge e integração DAT quando necessária | Payload sem mídia bruta | Restringir ambiente e revisar transporte para produção |
| `RECORD_AUDIO` | Reconhecimento de fala | Solicitada em runtime | Confirmar provedor e rota usados |
| `BLUETOOTH` até API 30 | Compatibilidade de áudio/dispositivo | Limitada por `maxSdkVersion` | Validar no hardware |
| `BLUETOOTH_CONNECT` | Comunicação em Android recente | Declarada no manifesto | Confirmar solicitação e fluxo real |
| `CAMERA` | Alimentar o stream com a câmera do telefone somente no ensaio MockDeviceKit | Declarada no flavor `dat`; solicitada pelo adaptador apenas quando `maestroDatMockDevice=true` | Não atribuir esse feed aos óculos e validar o caminho físico depois |
| Backup | Evitar cópia de dados do app | `android:allowBackup="false"` | Confirmar manifesto mesclado do build final |
| Analytics DAT | Reduzir telemetria opcional | `ANALYTICS_OPT_OUT=true`, confirmado no README oficial 0.9.0 | Revalidar ao atualizar o SDK |
| Crash reporting DAT | Reduzir telemetria opcional | `CRASH_REPORTING_OPT_OUT=true`, confirmado no README/changelog oficial 0.9.0 | Revalidar ao atualizar o SDK |

## Persistência observada no código

A busca estática atual encontrou leitura de assets empacotados, pipe do provider
interno, decodificação ZXing em memória, estado em memória, WebSocket,
`SpeechRecognizer`, TTS e logs do benchmark mock com fixture fixa. Não encontrou
chamadas do app para gravar foto, áudio, transcrição, banco ou preferências. A
inspeção do sandbox depois da captura DAT simulada retornou
`NO_PERSISTED_MEDIA_FILES`.

Essa conclusão possui limites:

- análise estática não prova o comportamento interno do Android ou DAT;
- ausência de nome de arquivo suspeito não prova que um banco ou preferência não contém texto;
- caches do sistema operacional podem existir fora do controle direto do app;
- uma nova dependência ou mudança de comportamento exige nova auditoria.

## Coleta Android sem mídia

O coletor `tools/collect_android_runtime_evidence.py` registra somente:

- fabricante, modelo, Android, API e ABI;
- versão instalada do pacote;
- SHA-256 do APK e do modelo local;
- bateria, tensão, temperatura e estado térmico disponíveis;
- memória aproximada do processo;
- contagem e nomes suspeitos de arquivos no sandbox e diretório externo do app.

Ele não coleta logcat, conteúdo de arquivo, áudio, imagem, transcrição, contatos, localização, número de série ou identificador pessoal. A inspeção de arquivos é limitada a caminhos e contagens; nenhum conteúdo é aberto.

Exemplo antes de uma jornada:

```bash
python3 tools/collect_android_runtime_evidence.py \
  --phase before \
  --output shared/evidence/android_runtime_before.json
```

Depois da jornada, repetir com `--phase after`. Os dois snapshots devem ser revisados antes de entrar no pitch ou alterar um checkpoint para `PASS`.

### Snapshot inicial em 19 de agosto de 2026

Uma coleta técnica no Edge 40 Neo registrou bateria em 100%, temperatura de bateria em 36,0 °C e estado térmico `NONE`. O sandbox interno do app estava acessível e continha zero arquivos; o diretório externo não pôde ser auditado e o app não estava em execução, portanto a memória PSS não ficou disponível. O resultado correto é `PARTIAL`, sem arquivo suspeito encontrado.

Esse snapshot comprova o funcionamento seguro do coletor, mas só serve como linha de base de uma medição de consumo se a jornada correspondente for executada em seguida. Caso contrário, deve ser repetido imediatamente antes do protocolo final.

### Protocolo QA-03 no Edge 40 Neo

Foram coletados snapshots antes e depois de cinco ciclos seguros no `mockDebug`. Cada ciclo usou alvo fixo, intenção fixa `pulverizar`, cancelamento fixo e reinício. O microfone e o DAT não foram usados, nenhum comando foi confirmado e nenhuma mídia foi capturada. O intervalo total entre snapshots foi de 596 segundos e inclui preparação e inspeção além das interações.

Resultados observados:

- bateria permaneceu em 100%, mas o status mudou de `FULL` para `CHARGING`; por isso, o consumo é inconclusivo e precisa ser medido novamente com o aparelho desconectado da energia;
- temperatura de bateria variou de 36,0 °C para 37,9 °C e o estado térmico permaneceu `NONE`;
- PSS final do processo foi 102585 KB, aproximadamente 100,2 MiB; não há delta porque o app não estava ativo no snapshot inicial;
- a contagem interna passou de zero para um arquivo: `./files/profileInstalled`, marcador técnico do AndroidX Profile Installer; apenas o caminho foi inspecionado, sem leitura de conteúdo;
- nenhum caminho interno com nome ou extensão de foto, áudio ou transcrição foi encontrado;
- o diretório externo continuou indisponível para auditoria;
- Rafael confirmou que ouviu as frases do TTS pelo alto-falante inferior do Edge 40 Neo; nenhuma gravação foi criada para essa evidência.

A comparação estruturada está em `shared/evidence/android_runtime_qa03_comparison.json`. O resultado permanece `PARTIAL`: ele valida o coletor e parte do comportamento mock, não a jornada completa com DAT, câmera e microfone simultâneos.

## Critérios de aceite da auditoria

- [x] Maestro, Android, DAT/Meta e bridge/externos documentados separadamente.
- [x] Dados, finalidade, destino e retenção descritos.
- [x] Permissões e controles estáticos registrados.
- [x] Coletor evita mídia, conteúdo de arquivos, logcat e número de série.
- [x] Par sanitizado before/after coletado para cinco ciclos mock.
- [-] Nenhum caminho interno suspeito encontrado; armazenamento externo e componentes do sistema ainda não foram auditados.
- [-] Rota TTS do telefone identificada; provedor de STT e rota Bluetooth dos óculos permanecem pendentes.
- [x] Opt-outs confirmados contra o README/changelog oficial do DAT 0.9.0.
- [-] Temperatura e memória iniciais registradas; bateria e encerramento de recursos exigem protocolo controlado.

## Handoff

- Rafael mantém o inventário, hashes, matriz e resultados sanitizados.
- Átila executa a jornada física e valida Android, DAT, câmera, STT/TTS e ciclo de recursos.
- Felipe confirma que o frame real é reduzido ao `target_id` esperado.
- A equipe aprova qualquer exceção de persistência e a mudança final de status na QA-03/QA-04.