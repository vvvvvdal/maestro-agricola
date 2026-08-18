# Aprendizados dos materiais CEIA

Fonte analisada em 18 de agosto de 2026:

- `Palestra-Agentes-IA-AI-Glasses.pptx.pdf`;
- `Meta AI Glassses.pptx.pdf`;
- `Meta AI Glassses 2.pptx.pdf`.

Os documentos são referência de processo e produto. Quando uma afirmação de SDK pode mudar, a documentação e os samples oficiais do Meta Wearables DAT prevalecem.

## Princípios incorporados

### Agente mínimo viável

- Estruturar a experiência como gatilho, percepção, política e fala.
- Criar um agente estreito: um fluxo nomeado, poucas ações e resposta falada curta.
- Usar estado explícito para impedir que “pulverizar” vire movimento sem confirmação.
- Aplicar uma cascata de custo: QR, reconhecimento nativo e classificador local antes de qualquer solução maior.
- Tratar silêncio como falha em uma interface sem display: meta de feedback inicial abaixo de 1 segundo e resposta completa em até 3 segundos.
- Capturar sob demanda e processar localmente para reduzir latência, bateria e exposição de dados.

### Entrega final

- Os três artefatos precisam contar a mesma história: documento estruturado, arquitetura e pitch.
- Especificidade vale mais do que volume: decisões devem nomear tecnologia, alternativa e motivo.
- O walkthrough de exceção é tão importante quanto o caminho feliz.
- A arquitetura deve mostrar fronteiras, tecnologias, direção dos dados e o que fica local.
- O pitch de 2 a 3 minutos deve dedicar tempo a problema/usuário, jornada, funcionamento interno, diferenciação e viabilidade.

### DAT e hardware

- Óculos não têm display; a experiência precisa fechar o ciclo por áudio.
- Câmera e sessão pertencem ao DAT e precisam respeitar o ciclo de conexão e desconexão.
- Não assumir que câmera, microfone e TTS usam a mesma API. No Maestro, DAT é a entrada visual; STT/TTS são recursos nativos do celular e a rota Bluetooth precisa de teste físico.
- O toolkit público não deve ser tratado como fonte de pose/IMU. Por isso, o MVP usa QR previamente mapeado.
- Mídia sob demanda, descarte imediato, consideração de terceiros no campo e logs sem mídia são requisitos de privacidade, não detalhes opcionais.

## Mudanças feitas no Maestro

1. O formulário passou a declarar metas de latência, não medições ainda inexistentes.
2. A integração de áudio foi descrita com fallback explícito no telefone.
3. O pitch passou a separar evidência já validada em simulação de pendência de hardware.
4. O fluxo de exceção “cancelar e não mover” virou cena obrigatória do vídeo.
5. O diagrama separa mídia efêmera de comando confirmado.

## Checklist derivado dos materiais

- [x] problema e usuário em frases concretas;
- [x] jornada principal e de exceção;
- [x] três a cinco decisões com alternativas descartadas;
- [x] dois concorrentes e diferencial;
- [x] cinco pilares técnicos;
- [x] Mermaid com tecnologias, fronteiras e setas;
- [ ] medir latência, temperatura e bateria nos aparelhos;
- [ ] validar microfone e saída de áudio pela rota Bluetooth dos óculos;
- [ ] gravar vídeo de 2 a 3 minutos e testar o link externamente.
