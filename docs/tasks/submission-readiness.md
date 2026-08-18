# Plano de prontidão para entrega - 18 a 22 de agosto de 2026

## Objetivo

Deixar o MVP reproduzível por uma pessoa que acabou de clonar o repositório e preparar os artefatos exigidos pelo formulário final do Programa AI Glasses Brasil, mantendo o pitch entre 2 e 3 minutos.

## Ambiguidades e premissas

- O texto integral de cada campo do formulário não foi fornecido; as respostas seguem as quatro seções descritas pelo CEIA e devem ser ajustadas apenas se o formulário impor limite de caracteres.
- O link do vídeo ainda não existe e será mantido como item pendente, nunca como link inventado.
- Builds físicos de Android, iOS e DAT dependem dos aparelhos e de um Mac com Xcode; nenhuma evidência física será declarada antes da execução pela equipe.
- A demonstração local obrigatória usa mock de óculos, IA local, WebSocket, ROS 2, Nav2 e Gazebo.
- As palestras anexadas são material de referência e não substituem a documentação oficial do DAT ou as regras do edital.

## Tarefas e critérios de aceite

### TST-01 - Teste guiado do MVP

Responsável principal: Felipe.

Critérios:

1. Uma seção “teste em 5 minutos” explica pré-requisitos, primeiro comando, saída esperada e encerramento.
2. Há diagnóstico automático para Docker, Compose, porta, contêiner, bridge e resposta do comando.
3. O caminho feliz retorna `ACCEPTED`; ausência do Docker ou do bridge gera mensagem acionável, sem traceback.
4. Os testes portáteis continuam passando sem ROS instalado no host.
5. O README distingue teste rápido, teste completo, logs e teste mobile.

### SUB-01 - Documento estruturado do formulário

Responsáveis: Felipe e Rafael, com revisão de Átila nas decisões mobile.

Critérios:

1. Seção A contém problema, usuário, fluxo principal e de exceção, decisões com justificativas, alternativas descartadas, concorrentes e cinco pilares.
2. Seção B aponta para Mermaid versionado e imagem PNG ou SVG legível.
3. Seção C contém checklist do vídeo e campo explícito para o link futuro.
4. Seção D explica a mudança de localização por pose/IMU para alvo visual mapeado e confirma coerência e autoria/uso de IA.
5. Afirmações técnicas permanecem coerentes com código, proposta e pitch.

### ARCH-01 - Diagrama de arquitetura

Responsável: Felipe.

Critérios:

1. O código-fonte Mermaid está em `docs/submission/architecture.mmd`.
2. A imagem exportada é legível em proporção horizontal e não contém texto cortado.
3. O diagrama separa óculos, app nativo, processamento local, rede e robô.
4. Fluxos de mídia efêmera e comando confirmado são distinguíveis.

### PIT-01 - Pitch final

Responsáveis: Felipe e Rafael.

Critérios:

1. Deck e roteiro apresentam problema, solução, demonstração, arquitetura, cinco pilares, diferencial e próximo passo.
2. O roteiro ensaiado cabe entre 2min40s e 2min55s.
3. Nenhum slide promete pose/IMU, pulverização real ou build físico ainda não validado.
4. Texto visível é curto e legível; notas registram fontes quando necessário.
5. O vídeo mostra pelo menos um comando aceito e uma falha segura.

## Ordem de execução

1. Ler e indexar os materiais CEIA.
2. Reproduzir o fluxo de teste do zero e corrigir atritos.
3. Atualizar README e guia de troubleshooting.
4. Preparar Seções A-D e o diagrama.
5. Revisar roteiro e apresentação.
6. Rodar testes, conferir renders e comparar código, docs e spec.

## Estratégia de commits

- `docs: plan submission readiness work`
- `test: add guided MVP diagnostics`
- `docs: prepare final submission answers and architecture`
- `docs: revise three-minute pitch`

Não fazer push nesta rodada.

## Registro de execução

### 18 de agosto - TST-01 concluída

- `make test` deixou de treinar e sobrescrever o modelo; agora compara os artefatos em modo somente leitura.
- `make doctor` validou Python, Docker, Compose, arquivos, daemon e bridge, com mensagens acionáveis.
- A porta canônica permaneceu `18765`; o diagnóstico diferencia bridge ausente de porta ocupada por outro protocolo.
- O entrypoint remove locks antigos e espera o Xvfb ficar pronto antes de iniciar o Gazebo.
- O launch passou de temporizadores fixos para um gate: marcador, SLAM e Nav2 só iniciam após o controlador do TurtleBot ficar ativo.
- `make demo` retornou `ACCEPTED`, ativou o Nav2 e mediu odometria em `x=0,017`, `y=0,001`.
- A confirmação “cancelar” foi recusada localmente como `CANCEL` com 98,4% de confiança, sem traceback e sem comando de movimento.
- `make test-quick`: 10 testes passaram e o Compose foi validado.

Evidência de sucesso final: `SIMULAÇÃO VERIFICADA: protocolo, Nav2 e movimento confirmados`.

### 18 de agosto - SUB-01 redigida

- As três palestras do CEIA foram resumidas em `docs/references/ceia-materials.md`, separando orientação de processo de afirmações que exigem fonte oficial atualizada.
- As respostas-base das Seções A–D estão em `docs/submission/final-form.md`, com revisão humana atribuída e pendências físicas explícitas.
- O áudio foi corrigido em todos os textos novos: câmera via DAT; STT/TTS pelo sistema mobile; rota Bluetooth dos óculos a validar; telefone como fallback.
- As metas de feedback abaixo de 1 segundo e resposta em até 3 segundos foram registradas como orçamento a medir, não como desempenho já comprovado.
- A mudança de pose/IMU para QR previamente mapeado foi explicada como redução consciente de escopo, preservando a jornada.
- A arquitetura Mermaid separa mídia efêmera, processamento local, comando confirmado e execução no ROS 2/Nav2/Gazebo.
