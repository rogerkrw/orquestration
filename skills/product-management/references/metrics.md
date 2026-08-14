# Métricas de Produto e Time

## North Star + Inputs (hierarquia)

```
North Star Metric (NSM)
├── Input Metric 1 (Aquisição)
├── Input Metric 2 (Ativação)
├── Input Metric 3 (Engajamento)
├── Input Metric 4 (Retenção)
└── Input Metric 5 (Monetização)
```

Monitore inputs semanalmente. Reporte NSM mensalmente vs. OKR.

---

## AARRR — Pirate Metrics (diagnóstico de funil)

| Etapa | Pergunta | Métricas típicas |
|---|---|---|
| **Aquisição** | De onde vêm os usuários? | CAC, CPL, tráfego por canal |
| **Ativação** | Chegam ao momento "aha"? | Taxa de ativação, time-to-value |
| **Retenção** | Voltam? | D1/D7/D30 retention, churn, DAU/MAU |
| **Receita** | Monetizam? | MRR, ARPU, LTV, conversão free→paid |
| **Referral** | Indicam? | NPS, referral rate, viral coefficient |

Use AARRR para identificar onde o funil quebra antes de priorizar soluções.

---

## Métricas de Retenção

**Cohort Analysis**: agrupe usuários por data de aquisição e acompanhe retenção ao longo do tempo.

**Benchmarks SaaS (referência)**:
- D1 retention (apps consumer): ≥ 40% bom, ≥ 25% aceitável
- D30 retention (apps consumer): ≥ 20% bom
- Monthly churn (SaaS B2B): ≤ 2% bom, ≤ 5% aceitável

---

## Métricas de Saúde de Time (PMO)

| Métrica | Definição | Frequência |
|---|---|---|
| **Velocity** | Story points entregues por sprint | Por sprint |
| **Lead Time** | Issue criada → produção | Por issue (média semanal) |
| **Cycle Time** | Dev iniciado → produção | Por issue (média semanal) |
| **Deployment Frequency** | Deploys por semana/dia | Semanal |
| **Defect Escape Rate** | Bugs pós-produção / total entregue | Por sprint |
| **Sprint Goal Achievement** | % de sprints que atingiram o Sprint Goal | Por sprint |

**DORA Metrics** (DevOps Research):
- Deployment Frequency: com que frequência fazemos deploy
- Lead Time for Changes: código comprometido → em produção
- Change Failure Rate: % deploys que causam incidente
- Time to Restore: tempo para recuperar de incidente

Times de elite: múltiplos deploys/dia, lead time < 1 hora, CFR < 5%, restauração < 1 hora.

---

## Dashboard de Produto — Estrutura recomendada

**Nível estratégico (mensal — para C-level)**:
- NSM vs. meta
- OKR check-in (score 0–1 por KR)
- MRR/ARR e tendência
- NPS ou CSAT

**Nível de produto (semanal — para PM/time)**:
- Input metrics vs. baseline
- Funnel AARRR por etapa
- Features lançadas e impacto medido
- Experimentos em curso e resultados

**Nível de execução (diário — para time de eng)**:
- Velocity do sprint atual vs. planejado
- Itens em progresso, bloqueados, concluídos
- Deploy frequency e status de CI/CD
- Alertas de erros/performance (p99 latência, error rate)
