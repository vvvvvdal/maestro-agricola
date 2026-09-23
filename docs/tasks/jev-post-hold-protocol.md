# Task: Protocolo pos-HOLD do experimento Jev

## Status

Concluida em 23/09/2026 na branch `test/jev`. Esta task define o protocolo;
ela nao altera o app, nao chama a API e nao promove o Jev.

## Decisao

O resultado JEV-41R abre uma fase nova de evidencia. A comparacao anterior
permanece historica e congelada: 54/60 para Jev bruto, com o erro
`CANCEL -> CONFIRM (0,75)`. Nenhum corpus, reserva ou fixture anteriores sera
reutilizado.

O novo experimento publica duas leituras distintas:

1. **Jev bruto**: `Choice` valida, os mesmos seis rotulos e o limiar atual.
2. **Jev + guard**: a mesma resposta Jev, seguida de uma politica
   deterministica de cancelamento explicito.

O guard e uma barreira de produto, nao evidencia de que o Jev bruto deixou de
errar. Ele pode apenas devolver `CANCEL`; nunca devolve um rotulo positivo,
alvo, `Command`, fallback ou acesso ao Qwen. O finding `recovery-045` e uma
regressao de desenvolvimento do guard, nunca entra nos novos holdouts.

Falha, indisponibilidade ou entrada nao normalizavel do guard retornam
`CANCEL` localmente. Nao existe fallback para uma predicao positiva bruta, nem
chamada Jev extra, Qwen ou `Command`; o teste do guard precisa provar este
caminho fechado.

## Ordem imutavel da nova fase

1. Implementar e testar o guard com dados de desenvolvimento conhecidos.
2. Coletar e revisar transcricoes ASR reais, sanitizadas e sem audio salvo.
3. Congelar dois holdouts independentes antes de qualquer HTTP.
4. Medir a mesma fixture em modos bruto e guarded, sem alterar regra ou limiar.
5. Executar uma rodada reservada para cada holdout.
6. Decidir `HOLD`, experimento adicional ou integracao isolada com base nas
   duas rodadas; integracao no Android continua exigindo aprovacao humana nova.

## Gates de evidencia

- Os seis rotulos e todas as barreiras atuais permanecem intactos.
- Cada holdout tem falantes e sessoes separados do desenvolvimento e do outro
  holdout; textos, audio e identificadores nao entram no repositorio.
- Cada corpus tem hash, modelo, limiar, politica, teto e reserva exclusivos.
- `CANCEL` e `UNKNOWN` formam estrato de seguranca reforcado.
- Qualquer aceite inseguro em `Jev + guard` mantem `HOLD`; nao ha ajuste ou
  repeticao ad-hoc depois de abrir uma rodada.
- As metricas mostram Jev bruto e guarded lado a lado, inclusive Choice e
  probabilidades originais. Nenhum numero guarded reescreve o resultado bruto.

## Dependencias humanas antes de remoto

- Aprovar novo subteto de custo. O teto anterior de US$5,00 foi consumido como
  alocacao e adicionar credito nao o amplia automaticamente.
- Aprovar o catalogo de "cancelamento explicito" usado pelo guard.
- Disponibilizar ASR Android no aparelho/idioma alvo, falantes consentidos e
  sessoes suficientes para separar desenvolvimento, primaria e replicacao.
- Definir alvo estatistico. Com zero erros em `n` negativos, o limite superior
  aproximado de 95% e `3/n`: 150 casos dao cerca de 2%; 300, cerca de 1%.

## Fora do escopo

Sem chave no Android, HTTP no app, dados brutos de audio, Qwen/RAG, alvo,
`Command`, ROS, alteracao do contrato ou promocao operacional.
