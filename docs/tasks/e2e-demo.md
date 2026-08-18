# Integração da demonstração ponta a ponta

Branch: `feat/e2e-demo`

## Objetivo

Integrar as entregas já publicadas e fechar uma jornada única e segura: alvo mapeado → intenção local → confirmação → WebSocket → ROS 2/Nav2/Gazebo.

## Decisões humanas

- O QR continua sendo o caminho principal do MVP, não a solução final de localização em campo.
- A placa combina o ID legível `PLOT-03` com o QR para permitir conferência humana.
- “Pulverize aqui” exige um alvo visual central reconhecido.
- “Pulverize no plot-03” pode fornecer um ID explícito por voz; ele sempre é validado contra o mapa.
- Quando voz e câmera fornecem IDs diferentes, o sistema retorna divergência e nunca envia comando.
- Quando não há QR, o fallback por ID falado exige que o sistema repita o alvo completo e receba confirmação explícita.
- GPS do celular não será tratado como direção da cabeça nem como pose do alvo. Geofencing fica como evolução de produto.

## Critérios de aceite

1. As cinco branches publicadas entram na integração com histórico e limites documentados.
2. Casos compartilhados cobrem ID visual, ID falado, concordância, divergência, ausência e alvo fora do mapa.
3. Python, Kotlin e Swift implementam a mesma política de resolução do alvo.
4. A placa `PLOT-03` continua decodificável pelo detector já testado.
5. A proposta e o pitch explicam qual IA local é usada, sem confundir STT, classificador e visão.
6. Nenhuma divergência, intenção desconhecida, timeout ou alvo inexistente produz movimento.

## Fora de escopo

- Estimar coordenadas a partir de GPS do celular ou orientação dos óculos.
- Implementar geofencing, RTK, OCR aberto ou linguagem natural irrestrita.
- Declarar builds ou testes físicos que não ocorreram.
- Adicionar uma segunda ação agrícola.

## Ordem de execução

1. Integrar documentação, diagnósticos, visão, IA e preflights mobile.
2. Congelar o contrato do resolvedor de alvo.
3. Implementar e testar a política compartilhada.
4. Gerar e testar a placa legível.
5. Atualizar os materiais de entrega e o pitch.
6. Rodar a suíte completa e registrar o que ainda depende dos aparelhos.

## Resultado parcial — resolvedor de alvo

- As cinco branches publicadas foram integradas separadamente; os conflitos ficaram restritos ao índice de tarefas e ao `Makefile`.
- `shared/target/target_resolution_cases.json` congela nove casos de visual, voz, concordância, conflito, ausência e alvo desconhecido.
- A referência Python passou e os mesmos casos são consumidos por testes Kotlin e Swift.
- A máquina de estados aceita `plot-03` falado mesmo sem QR, mas continua exigindo confirmação explícita.
- Divergência entre o ID visual e o ID falado entra em `AMBIGUOUS` e não cria comando.
- O catálogo `targets.json` do bridge também virou a allowlist dos dois apps; não foi criada uma segunda lista de alvos.
- O gate da IA agora inclui 13 frases, entre elas `pulverize no plot-03` e `pulverize no plot três`.
- Nesta máquina, 23 testes Python e 4 testes do bridge passaram. Os novos testes Kotlin/Swift aguardam as toolchains nativas já documentadas.

## Resultado parcial — placa legível

- A textura do Gazebo agora é uma placa vertical com `PLOT-03`, QR e indicação de alvo mapeado.
- O QR puro foi preservado em `plot-03-qr.png`, e `tools/generate_qr.py` reproduz os dois arquivos sem a antiga dependência `qrcode`.
- O plano da textura no SDF passou de quadrado para vertical, acompanhando a placa.
- O smoke test decodificou a placa completa como `plot-03`; oito testes de visão passaram.
- A documentação de produto continuará tratando poeira, obstrução e manutenção como risco. A placa não substitui geofencing, RTK ou telemetria do robô em produção.

## Resultado final — materiais de entrega

- README, spec, arquitetura, formulário final e versões técnica/resumida descrevem o mesmo fluxo visual/falado.
- Os PDFs revisados foram regerados e inspecionados visualmente: 3 páginas na versão resumida e 10 na técnica, sem página órfã ou conteúdo cortado.
- O diagrama inclui placa/QR, ID falado, resolvedor de alvo, classificador local, política de confirmação e bridge ROS 2.
- O roteiro tem 376 palavras e duração-alvo de 2min40s a 2min55s.
- Os slides 3 a 5 foram atualizados para mostrar o softmax local de 65 KB, a regra de conflito e três evidências reproduzíveis. A apresentação passou na verificação de overflow e fidelidade ao deck-base; não há placeholder estrutural vazio.

## Validação final — 18 de agosto de 2026

- `make test-quick`: aprovado — 23 testes portáteis, 4 testes do bridge e Compose válido.
- `make vision-smoke`: aprovado — placa completa detectada como `plot-03` com confiança 1,0.
- Resolvedor: voz explícita → `RESOLVED/VOICE`; “aqui” + câmera → `RESOLVED/VISUAL`; voz `plot-04` + câmera `plot-03` → `CONFLICT`, sem alvo.
- `make demo`: aprovado — resposta `ACCEPTED`, Nav2 ativo, meta aceita e odometria alterada (`x=0.022`, `y=0.001`). A execução terminou com `SIMULAÇÃO VERIFICADA: protocolo, Nav2 e movimento confirmados`.
- O contêiner da demonstração foi encerrado após o teste.
- Preflight Android: bloqueado neste computador por ausência de JDK 17 e Android SDK; o Gradle wrapper está presente.
- Preflight iOS: bloqueado porque o host é Linux e não possui Xcode, Swift ou XcodeGen; arquivos do projeto e modelo local estão presentes.

Nenhum build ou teste físico foi declarado como aprovado. Permanecem como gates humanos: compilar no Motorola, compilar no iPhone 13, conectar o detector ao frame mobile, validar o DAT e medir áudio, latência e bateria no hardware real.
