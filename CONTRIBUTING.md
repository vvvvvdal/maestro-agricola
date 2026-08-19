# Como colaborar no Maestro Agrícola

O projeto usa `main` como linha integrada e sempre demonstrável. As branches são curtas e representam uma entrega verificável, não uma pessoa ou uma área permanente.

## Regra principal

- Uma branch por tarefa do quadro em `docs/tasks/mvp-week.md`.
- Duração ideal: algumas horas; no máximo um dia de trabalho.
- Qualquer integrante pode contribuir em qualquer branch.
- Quem lidera a tarefa coordena a decisão e registra os trade-offs no PR.
- Mudanças em `contracts/`, segurança ou privacidade precisam da revisão de dois integrantes.
- Não manter branches `atila`, `felipe` ou `rafael`: elas criariam silos e integrações tardias.

## Frentes iniciais

| Branch | Tarefas | Liderança | Evidência para merge |
|---|---|---|---|
| `feat/android-mock-smoke` | MOB-01 e MOB-03 | Átila | `mockDebug` instalado no Motorola, voz/TTS demonstrados e log sem mídia bruta |
| `feat/vision-qr` | VIS-02 e VIS-03 | Felipe | `plot-03` detectado em imagem conhecida e `UNKNOWN` sem marcador |
| `feat/ai-device-eval` | AI-03 e apoio a QA-01 | Rafael | mesmos casos em Python e Kotlin, com confiança e limiar registrados |

A integração INT-01/INT-02 deve nascer depois, em `feat/e2e-demo`, a partir da `main` já atualizada com as entregas acima. Não use uma branch de integração permanente.

## Fluxo diário

1. Escolha uma tarefa e escreva seus critérios de pronto antes de programar.
2. Atualize a `main` e crie ou entre na branch da tarefa.
3. Faça commits pequenos e executáveis.
4. Atualize testes e documentação na mesma mudança.
5. Abra PR ainda no mesmo dia, mesmo que inicialmente como rascunho.
6. Outro integrante revisa e reproduz a evidência.
7. Faça squash merge; apague a branch depois do merge.
8. Atualize o checkbox no quadro somente quando a evidência existir.

Exemplo:

```bash
git switch main
git pull --ff-only
git switch -c feat/vision-qr

# implementar e testar
make test

git add mobile shared tests docs
git commit -m "feat(vision): detect mapped plot QR"
git push -u origin feat/vision-qr
```

Se a branch já foi criada por outro integrante:

```bash
git fetch origin
git switch feat/vision-qr
git pull --ff-only
```

## Limites de mudança

As pastas indicam a liderança de revisão, não exclusividade:

- `mobile/android/`: Átila.
- `robot_ws/` e visão: Felipe.
- `shared/ai/`, dataset e métricas: Rafael.
- `contracts/`: equipe; Felipe revisa o lado ROS e Átila o lado mobile.
- `docs/pitch/`: Felipe e Rafael.

Ao tocar a frente de outra pessoa, explique no PR o motivo e marque a liderança para revisão. Não copie modelo, schema ou constantes entre plataformas: a fonte compartilhada continua em `shared/` ou `contracts/`.

## Gate antes de merge

- `make test` passa.
- `docker compose config --quiet` passa quando Compose mudar.
- Nenhum segredo, mídia bruta ou arquivo de build foi adicionado.
- O PR mostra como reproduzir a evidência.
- Contrato, modelo e comportamento continuam coerentes entre Android e ROS.
- Falhas de alvo, intenção ou confirmação continuam sem produzir movimento.

## Congelamento

No Dia 6, criar a tag de release somente após cinco jornadas completas. Depois do congelamento entram apenas correções de defeito, documentação e evidências para o pitch.
