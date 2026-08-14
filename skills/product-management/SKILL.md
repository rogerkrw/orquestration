---
name: product-management
description: >
  Gestão de produto de ponta a ponta — do problema ao entregue, com lente de negócio.
  Acione para: discovery e entrevistas, validação de premissa, priorização (RICE, WSJF, MoSCoW, Kano),
  roadmap, OKR e North Star, PRD, user stories, critérios de aceite, DoR/DoD, sprints e cerimônias,
  estimativas, risk log, status report, retrospectiva e métricas de produto e de time.
  Acione também para a camada de negócio: unit economics (CAC, LTV, payback, churn, NRR, Rule of 40),
  pricing e empacotamento, TAM/SAM/SOM, análise competitiva, posicionamento, JTBD e case de negócio.
  Gatilhos: "o que priorizar", "vale a pena construir isso", "como estruturar o roadmap",
  "o que vai no PRD", "como medir o sucesso", "quanto custa e quanto retorna", "como precificar",
  "qual o tamanho desse mercado", "como montar OKR", "como fazer retrospectiva", "como estimar".
---

# Product Management

Gestão de produto e de projetos de software, do problema ao entregue. Cobre três camadas, e a maior parte das decisões ruins vem de tratar uma como se fosse a outra:

| Camada | Pergunta | Onde está |
| --- | --- | --- |
| **Problema** | vale a pena resolver isso, para quem, agora? | seções 2.1-2.2 + `references/discovery.md` |
| **Negócio** | isso se paga? cabe no mercado? por que nós? | `references/business.md` |
| **Entrega** | como e quando entregar? | seções 3-4 + `references/artifacts.md` |

**Sequência que importa:** problema validado → viabilidade de negócio → entrega planejada. Pular a do meio é o erro mais caro: feature bem construída, para problema real, que não se paga nem tem como ser vendida.

---

## 1. Fundamento: PM vs PMO — quando usar o quê

| Dimensão | Product Management (PM) | Project Management (PMO/TPM) |
|---|---|---|
| Pergunta central | *O quê* e *por quê* construir | *Como* e *quando* entregar |
| Orientação | Outcomes (impacto) | Output + prazo + custo |
| Artefatos típicos | PRD, roadmap, OKR, North Star | Cronograma, WBS, risk log, status report |
| Metodologia base | Continuous Discovery, Dual-Track Agile | Scrum, Kanban, PMI/PMBOK, SAFe |
| Sucesso medido por | Resultado para usuário/negócio | Entrega no prazo, escopo e orçamento |

> **Regra prática**: PM responde ao CPO/CEO pelo produto. PMO/TPM responde ao PM ou CTO pela execução. Em startups, um único papel híbrido (TPM) costuma cobrir ambos.

---

## 2. Product Management — Núcleo

### 2.1 Discovery Contínua (Teresa Torres / Marty Cagan)

O modelo contemporâneo de PM abandona o discovery como fase inicial.
Discovery e delivery rodam em paralelo (Dual-Track Agile) de forma contínua.

**Product Trio**: PM + Designer + Engenheiro Sênior — responsáveis conjuntos pelo problema a resolver.

**Ciclo semanal mínimo**:
1. Pelo menos 1 entrevista com usuário/cliente (automatize o recrutamento)
2. Síntese de oportunidades no Opportunity-Solution Tree (OST)
3. Priorização de experimentos a rodar naquele sprint

**Opportunity-Solution Tree**:
```
Outcome desejado (métrica / OKR)
├── Oportunidade A (pain point ou unmet need)
│   ├── Solução A1 → Experimento
│   └── Solução A2 → Experimento
├── Oportunidade B
│   └── Solução B1 → Experimento
```

Leia `references/discovery.md` para roteiro completo de entrevistas e OST.

---

### 2.2 Estratégia e Visão de Produto

**North Star Metric (NSM)**
- Uma métrica que captura o valor entregue ao cliente E gera receita para o negócio.
- Exemplos: DAU fazendo ação-chave, transações completadas, tempo-para-valor em onboarding.
- Evite métricas de vaidade (pageviews, downloads sem ativação).

**OKR — Objectives & Key Results**
```
Objective: Ambicioso, qualitativo, inspiracional (90 dias)
  KR1: Mensurável, resultado — não output (ex: aumentar retenção D30 de 40% → 55%)
  KR2: ...
  KR3: (máx 3–4 KRs por Objective)
```
- OKRs de produto derivam dos OKRs de negócio, nunca ficam soltos.
- KRs são lagging indicators; defina leading indicators para monitoramento semanal.

**Product Vision**: 1–2 frases descrevendo o futuro do produto em 3–5 anos.
**Product Strategy**: como chegar lá — ICP, diferencial, fases de mercado.

Leia `references/strategy.md` para templates de vision, strategy e OKR.

---

### 2.3 Priorização

**Escolha do framework por contexto:**

| Contexto | Framework recomendado |
|---|---|
| Backlog de features com dados de uso | **RICE** |
| Portfólio/epics com urgência de mercado | **WSJF** |
| Decisão rápida sem dados | **ICE** (simplificado) |
| Alinhamento com stakeholders não-técnicos | **MoSCoW** |
| Validação pré-roadmap | **Kano Model** |

**RICE** = (Reach × Impact × Confidence) / Effort
- Reach: usuários afetados em 90 dias
- Impact: 3=massivo, 2=alto, 1=médio, 0,5=baixo, 0,25=mínimo
- Confidence: 100% validado, 80% médio, 50% especulativo
- Effort: pessoa-semanas

**WSJF** = Cost of Delay / Job Duration
- Cost of Delay = Business Value + Time Criticality + Risk Reduction/Opportunity Enablement
- Preferido em SAFe e ambientes com prazos regulatórios ou janelas de mercado

**Regra de ouro**: ainda que use scores, mantenha juízo humano para dependências e estratégia.

---

### 2.4 Roadmap

**Tipos de roadmap por audiência:**

- **Now-Next-Later** (padrão para times ágeis): sem datas rígidas, orientado a outcomes
- **Gantt simplificado**: para stakeholders executivos que exigem datas
- **Tema-based roadmap**: agrupa features por problema de usuário

**Roadmap saudável**:
- Now: comprometido, refinado, com critérios de aceite
- Next: priorizado, não detalhado
- Later: lista de oportunidades, sem comprometimento
- Revisão quinzenal obrigatória

---

### 2.5 Artefatos de PM

**PRD (Product Requirements Document)**
Estrutura mínima:
```
1. Contexto e problema
2. Usuário-alvo e Jobs-to-be-Done
3. Objetivo de negócio (OKR vinculado)
4. Solução proposta (o quê, não o como)
5. Critérios de sucesso (métricas)
6. Escopo: in/out
7. Dependências e riscos
8. Perguntas em aberto
```

**User Story**:
```
Como [persona], quero [ação] para que [benefício].

Critérios de Aceite:
- Dado [contexto], quando [ação], então [resultado esperado]
```

**Definition of Ready (DoR)**: história pode entrar no sprint quando:
- Problema entendido pelo time
- Critérios de aceite definidos
- Estimada (story points ou T-shirt)
- Sem bloqueadores conhecidos

**Definition of Done (DoD)**:
- Código revisado e aprovado em PR
- Testes automatizados passando (unit + integração)
- Documentação atualizada
- Deploy em staging sem erros
- Aceite do PM ou QA

---

## 3. Project Management / PMO — Núcleo

### 3.1 Metodologias e quando usar

| Metodologia | Usar quando |
|---|---|
| **Scrum** | Times cross-funcionais, entregas iterativas, prioridades mudam frequentemente |
| **Kanban** | Fluxo contínuo, suporte/bugs, demanda imprevisível |
| **SAFe** | Múltiplos times Agile com alinhamento de portfólio |
| **Waterfall/Híbrido** | Entregas regulatórias, hardware, contratos com escopo fechado |
| **Shape Up** (Basecamp) | Times pequenos, ciclos de 6 semanas, sem sprint micromanagement |

### 3.2 Cerimônias Scrum — Guia de Execução

| Cerimônia | Freq. | Duração (sprint 2 sem.) | Dono | Output |
|---|---|---|---|---|
| Sprint Planning | Por sprint | ≤ 4h | PM + Dev | Sprint Backlog + Sprint Goal |
| Daily Standup | Diário | 15 min | Scrum Master | Impedimentos expostos |
| Sprint Review | Por sprint | ≤ 2h | PM | Feedback stakeholders |
| Retrospectiva | Por sprint | ≤ 90 min | Scrum Master | Action items com dono |
| Backlog Refinement | 1–2x/sem | ≤ 1h | PM | Histórias prontas para DoR |

**Anti-padrões a eliminar**:
- Daily como status report (fale sobre impedimentos, não tarefas concluídas)
- Sprint Planning sem Sprint Goal definido
- Retrospectiva sem action items com responsável e prazo
- Backlog com centenas de itens sem prioridade

---

### 3.3 Estimativas

**Story Points (Fibonacci: 1, 2, 3, 5, 8, 13, 21)**
- Relativos, não absolutos
- Calibrados com histórias de referência do próprio time
- Velocity: média de pontos entregues por sprint (últimas 3–5 sprints)

**T-shirt Sizing** (XS/S/M/L/XL): para epics e roadmap de alto nível.

**Regra**: nunca comprometer datas com base em estimativas de backlog não refinado.

---

### 3.4 Risk Management

**Registro de riscos (Risk Log)**:
```
| ID | Descrição | Probabilidade | Impacto | Score | Mitigação | Dono | Status |
```
- Probabilidade: 1–5
- Impacto: 1–5
- Score = P × I (priorize ≥ 15)

**Tipos de risco em projetos de software**:
- Técnico (dívida técnica, integrações, performance)
- Escopo (scope creep, requisitos ambíguos)
- Recursos (turnover, dependências de terceiros)
- Mercado (mudança de prioridade, concorrente)
- Regulatório (LGPD, compliance, segurança)

---

### 3.5 Status Report (Executivo)

Template semanal:
```
## Status [Projeto] — Semana de [data]

🟢 No prazo  |  🟡 Atenção  |  🔴 Em risco

### Resumo executivo (3 linhas máx.)
...

### O que foi entregue essa semana
- ...

### O que será entregue semana que vem
- ...

### Riscos/Impedimentos
- [Risco] → [Ação em andamento] → [Dono]

### Métricas
| KPI | Meta | Atual | Tendência |
```

---

### 3.6 Governance e PMO

**Modelos de PMO**:
- **Supportive**: biblioteca de boas práticas, sem autoridade
- **Controlling**: define padrões, audita conformidade
- **Directive**: gerencia projetos diretamente

Em startups e scale-ups, o PMO costuma ser **supportive + controlling híbrido**.

**Portfolio Management**:
- Mapa de projetos: estratégico / operacional / manutenção
- Critérios de entrada: alinhamento com OKR + ROI esperado + custo de oportunidade
- Gate reviews: pontos de decisão go/no-go por fase

---

## 4. Fluxo Integrado PM + PMO

```
Estratégia (CEO/CPO)
       ↓
   OKR trimestral
       ↓
Discovery contínua ←→ Entrevistas + OST
       ↓
Priorização RICE/WSJF
       ↓
Roadmap Now-Next-Later
       ↓
Sprint Planning → Sprint Goal
       ↓
Desenvolvimento (Scrum/Kanban)
       ↓
Sprint Review → Feedback
       ↓
Retrospectiva → Melhoria
       ↓
Métricas → OKR check-in
       ↓ (repete)
```

---

## 5. Métricas de Produto

**North Star + Input Metrics**:
- Defina 1 NSM + 3–5 input metrics que a movem
- Monitore semanalmente; reporte mensalmente vs. OKR

**AARRR (Pirate Metrics)**: Aquisição → Ativação → Retenção → Receita → Referral
- Use para mapear onde o funil quebra

**Métricas de saúde de time (PMO)**:
- Velocity (pontos/sprint) — tendência, não comparação entre times
- Lead time (issue criada → entregue em produção)
- Cycle time (desenvolvimento iniciado → produção)
- Defect escape rate (bugs em produção / total entregue)
- Deployment frequency

---

## 6. Referências por contexto

Para detalhes adicionais, leia os arquivos em `references/`:

| Arquivo | Quando ler |
|---|---|
| `references/discovery.md` | Conduzir entrevistas, OST, experimentos |
| `references/strategy.md` | Montar OKR, visão, estratégia de produto |
| `references/artifacts.md` | Templates de PRD, User Story, DoD, DoR |
| `references/metrics.md` | North Star, AARRR, métricas de saúde de time |
| `references/business.md` | Unit economics, pricing, TAM/SAM/SOM, competitivo, posicionamento, case de negócio |
