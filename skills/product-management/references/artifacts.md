# Artefatos — Templates Completos

## PRD (Product Requirements Document)

```markdown
# PRD: [Nome da Feature/Iniciativa]

**Status**: Rascunho | Em Revisão | Aprovado
**PM**: [nome]
**Trio**: PM [nome] / Design [nome] / Eng [nome]
**OKR vinculado**: [Objective → KR específico]
**Data alvo**: [trimestre ou sprint, não data exata se incerto]

---

## 1. Contexto e Problema
[Por que esse problema existe? Dados quantitativos + insights qualitativos de entrevistas]

## 2. Usuário-Alvo
**Persona/ICP**: [descrição]
**Jobs-to-be-Done**: Como [persona], quando [situação], quero [motivação] para que [resultado esperado].

## 3. Objetivo de Negócio
**OKR**: [Objective → KR]
**Hipótese**: Acreditamos que [solução] resultará em [outcome mensurável] para [usuário-alvo].

## 4. Solução Proposta
[O quê resolver, não como implementar — deixe o como para o time de engenharia]

## 5. Critérios de Sucesso
| Métrica | Baseline | Meta | Prazo |
|---------|----------|------|-------|
| [KR]    |          |      |       |

## 6. Escopo
**In scope**: [o que está incluído]
**Out of scope**: [o que explicitamente não está incluído]

## 7. Dependências e Riscos
| Dependência/Risco | Impacto | Mitigação |
|---|---|---|

## 8. Perguntas em Aberto
- [ ] [Pergunta] — responsável: [nome] — prazo: [data]

## 9. Aprovações
- [ ] PM
- [ ] Engineering Lead
- [ ] Design Lead
- [ ] Stakeholder(s)
```

---

## User Story

```
**Título**: [verbo + substantivo curto]
**Como** [persona/papel],
**Quero** [ação ou funcionalidade],
**Para que** [benefício ou resultado de negócio].

**Critérios de Aceite** (formato BDD):
- **Dado** [contexto inicial],
  **Quando** [ação do usuário],
  **Então** [resultado esperado].

**Pontuação**: [story points]
**Dependências**: [se houver]
**Notas técnicas**: [se houver — opcionais]
```

---

## Definition of Ready (DoR) — Checklist

Uma história está pronta para entrar no sprint quando:
- [ ] Problema entendido pelo time (não apenas pelo PM)
- [ ] Critérios de aceite escritos e revisados
- [ ] Mockups/wireframes disponíveis (se UI)
- [ ] Dependências técnicas mapeadas
- [ ] Estimada pelo time (story points)
- [ ] Sem bloqueadores conhecidos no início do sprint
- [ ] Tamanho ≤ 8 pontos (se maior, fatiada)

---

## Definition of Done (DoD) — Checklist

Uma entrega está pronta para produção quando:
- [ ] Código implementado e funcionando localmente
- [ ] Pull request revisado e aprovado (≥ 1 reviewer)
- [ ] Testes automatizados escritos e passando (unit + integração)
- [ ] Sem regressões em testes existentes
- [ ] Deploy em ambiente de staging
- [ ] Aceite do PM ou QA em staging
- [ ] Documentação atualizada (se pública ou interna relevante)
- [ ] Feature flag configurada (se rollout gradual)
- [ ] Observabilidade: logs/métricas/alertas configurados
- [ ] Sem vulnerabilidades críticas (SAST/dependências)

---

## Retrospectiva — Facilitar

### Formato Start-Stop-Continue (20–30 min)
1. Silêncio individual (5 min): cada um escreve post-its
2. Apresentação em round-robin (10 min): cada um apresenta seus itens
3. Votação por dot (3 votos por pessoa) nas mais importantes
4. Action items para os top 3 temas (5 min):
   - O quê → Quem → Quando
5. Revise action items da retro anterior

### Regras da retro
- Sem julgamentos de pessoas — fale de comportamentos e processos
- Todos participam, inclusive engenheiros seniores
- Action items têm dono e prazo — sem ação = sem retro útil

---

## Sprint Planning — Roteiro

**Pré-requisito**: backlog refinado com histórias no DoR.

1. **Sprint Goal** (15 min): PM propõe, time refina — 1 frase que descreve o valor que o sprint entrega
2. **Seleção do backlog** (60–90 min): time puxa histórias até velocity estimada
3. **Breakdown técnico** (30 min): eng. quebra histórias em tarefas se necessário
4. **Comprometimento** (5 min): time confirma capacidade real (férias, eventos)

**Output**: Sprint Backlog + Sprint Goal documentados no board.
