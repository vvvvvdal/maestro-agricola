# Documentação

Para o ensaio físico com Meta Wearables, use [Teste integrado no Galaxy A17](testing/galaxy-a17-e2e.md). Para o runtime Qwen já medido no SM-X510, use [Qwen local no Android](tasks/qwen-android-runtime.md).

Este diretório concentra o contexto permanente do Maestro Agrícola. Atualize o arquivo correspondente quando uma decisão mudar; não deixe decisões importantes apenas no chat.

## Índice

- [`brand/README.md`](brand/README.md): identidade visual, paleta, logos e tipografia.
- [`product-brief.md`](product-brief.md): problema, proposta de valor, público e limites.
- [`mvp-spec.md`](mvp-spec.md): jornada principal, critérios de aceite e definição de pronto.
- [`architecture.md`](architecture.md): componentes, contratos, riscos e decisões técnicas.
- [`tasks/qwen-android-runtime.md`](tasks/qwen-android-runtime.md): decisão de segurança, benchmark, runtime JNI/llama.cpp e evidência física do Qwen.
- [`testing.md`](testing.md): teste guiado, saída esperada, diagnóstico e mobile.
- [`team.md`](team.md): papéis, responsabilidades e acordos de integração.
- [`hackathon-plan.md`](hackathon-plan.md): cronograma de preparação e execução.
- [`tasks/mvp-week.md`](tasks/mvp-week.md): tarefas executáveis para os sete dias do MVP.
- [`tasks/hackathon-day.md`](tasks/hackathon-day.md): plano de integração com os óculos no evento.
- [`references.md`](references.md): fontes oficiais e materiais de apoio.
- [`references/ceia-materials.md`](references/ceia-materials.md): aprendizados aplicados das três palestras do programa.
- [`submission/final-form.md`](submission/final-form.md): respostas A–D, pendências e checklist de envio.
- [`submission/architecture.mmd`](submission/architecture.mmd): código-fonte do diagrama exigido na Seção B.
- [`proposta/versao-resumida.md`](proposta/versao-resumida.md): versão curta revisada e canônica.
- [`proposta/versao-tecnica.md`](proposta/versao-tecnica.md): versão técnica revisada e canônica.
- [`pitch/roteiro-3-minutos.md`](pitch/roteiro-3-minutos.md): fala cronometrada.
- [`pitch/storyboard.md`](pitch/storyboard.md): conteúdo dos slides e sugestões de edição.
- `pitch/Maestro-Agricola-Pitch.pptx`: apresentação editável.

## Fonte de verdade

Em caso de divergência:

1. A spec do MVP define o comportamento esperado.
2. A arquitetura define contratos e decisões técnicas.
3. O código e os testes devem implementar esses documentos.
4. O pitch simplifica a história, mas não pode contradizer a solução real.

Os arquivos Markdown em `proposta/` são as fontes editáveis. Os PDFs da mesma pasta são exportações para compartilhamento.