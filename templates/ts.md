# Stack TypeScript — perfis `min` e `max`

<!--
ts — bloco de stack para projetos TypeScript. Combine com `BASE.md`
(comum a todo projeto) para montar o CLAUDE.md / AGENTS.md / GEMINI.md do projeto novo.
Escolha UM perfil, copie só as seções dele e remova estes comentários.

  min → app SvelteKit full-stack única + xyz/. Descoberta, experimentação, MVP enxuto.
  max → projeto profissional/de terceiro: api/ + web/ + docker/ + xyz/, TDD, deploy.

Na dúvida, comece em `min`.
-->

## Escolha do perfil

| Sinal | `min` | `max` |
| --- | --- | --- |
| Objetivo | descobrir, experimentar, MVP | produto que outros usam, entregável |
| Estrutura | uma app SvelteKit + `xyz/` | `api/` + `web/` + `docker/` + `xyz/` |
| Persistência | SQLite via Drizzle | PostgreSQL, migrations obrigatórias |
| Testes | quando a lógica estabilizar | TDD/EDD, unit + integração |
| Deploy | local; Railway se o TPM pedir | esperado (Railway/Hetzner) |

**Gatilhos de promoção `min` → `max`:** terceiros passam a depender do projeto; API e UI precisam escalar separadas; entram autenticação, multiusuário ou dados sensíveis; o deploy vira requisito.

---

# Perfil `min`

## **Stack Técnica**

- [`TypeScript`](https://www.typescriptlang.org/docs/) (`strict: true`): linguagem;
- [`pnpm`](https://pnpm.io/): package manager;
- [`biome`](https://biomejs.dev/): formatter e linter;
- [`SvelteKit`](https://svelte.dev/docs/kit/introduction): framework full-stack (rotas, SSR, endpoints);
- [`shadcn-svelte`](https://www.shadcn-svelte.com/) + [`Tailwind CSS v4`](https://tailwindcss.com/docs): UI kit e estilo (config em CSS via `@theme`);
- [`zod`](https://zod.dev/): validação e contratos isomórficos;
- [`drizzle`](https://orm.drizzle.team/): ORM sobre **SQLite**, com migrations como fonte de verdade do schema;
- [`Mastra`](https://mastra.ai/docs): framework de IA (agents, workflows, tools, evals, observability);
- [`Ollama`](https://docs.ollama.com/): provider para LLMs locais;
- LLMs: `qwen3:4b-instruct` (default), `qwen3:8b` (LLM-as-a-judge), `nomic-embed-text-v2-moe:latest` (embeddings);
- Env via `$env/dynamic/private` e `$env/static/public` do SvelteKit;
- Estado de página via `$app/state`; evitar `$app/stores` em código novo;
- Testes: [`vitest`](https://vitest.dev/), quando houver suite.

> **Nota:** LLMs proprietários, se introduzidos, o serão sob decisão do TPM. APIs externas exigem secrets no `.env` e justificativa de uso.

**Notas de adoção:**

- **LLM local vs remoto:** Ollama em desenvolvimento e evals (custo zero); remoto em produção quando latência ou qualidade exigirem. LLM-as-a-judge sempre em modelo distinto do gerador.
- **Mastra-first:** para agentes, workflows, tools, scorers e observability, usar os primitivos do Mastra antes de solução ad-hoc. Consultar `mastra.ai/llms.txt` antes de implementar.
- **Vetorização:** adiar `sqlite-vec` até o volume justificar. Match determinístico + LLM cobre a maioria dos casos no MVP.

## **Arquitetura Base**

App SvelteKit única — um processo, um deploy. Lógica de servidor em `lib/server/`, nunca importada pelo cliente.

```
[nome-do-projeto]/
├── src/
│   ├── lib/
│   │   ├── server/               # Só servidor (nunca importado pelo cliente)
│   │   │   ├── ai/               # Agents, tools, workflows (Mastra)
│   │   │   ├── db/               # Drizzle: schema, migrations, queries
│   │   │   ├── integrations/     # APIs externas
│   │   │   └── services/         # Lógica de domínio (use cases)
│   │   ├── shared/               # Schemas Zod, tipos isomórficos
│   │   └── components/           # UI (Svelte + shadcn-svelte)
│   ├── routes/                   # Rotas SvelteKit (+page, +server)
│   ├── hooks.server.ts
│   └── app.css
├── tests/                        # Testes (vitest), quando houver
├── static/
├── xyz/                          # Workspace LOCAL do TPM — 100% gitignored
│   ├── artifacts/                # Requisitos, specs, inputs brutos do TPM
│   ├── docs/                     # Memória do projeto, reports, TODOs arquivados
│   ├── db/                       # SQLite local e dumps
│   ├── evals/                    # Saídas brutas das rodadas de eval
│   ├── logs/
│   ├── inputs/                   # Entradas de dados processáveis
│   ├── outputs/                  # Saídas de dados processados
│   └── scripts/                  # Scripts ad-hoc/one-off
├── .env
├── package.json
├── drizzle.config.ts
├── svelte.config.js
├── README.md
├── TODO.md
├── HANDOFF.md
└── [LLM].md                      # CLAUDE.md, AGENTS.md, GEMINI.md
```

> `xyz/` é o workspace de bagunça do TPM — pensar, juntar artefatos, documentar. Ignorado por inteiro. Arquivos gerados ali seguem pasta do dia + timestamp exato (ver *Medição e Auditoria* na base).

## **Agentes e Skills**

| Subagente | Quando delegar |
| --- | --- |
| `swe-backend` | Server-side: services, DB, integrações, workflows Mastra |
| `swe-frontend` | UI: componentes Svelte, rotas, forms, state |
| `code-reviewer` | Pós-feature, pré-merge (read-only) |
| `qa-tester` | Vitest, evals, investigação de falhas |
| `devsecops` | Deploy, secrets, auditoria de segurança |
| `product-manager` | Validar premissa, viabilidade de negócio, PRD, roadmap, sprint |

| Quem usa | Skill | Para que |
| --- | --- | --- |
| `swe-backend` | `mastra` | Agents, workflows, tools, scorers, evals |
| `swe-frontend` | `sveltekit`, `sveltekit-ui` | Routing, SSR, load functions; shadcn-svelte + Tailwind v4 |
| `qa-tester` | `qa-testing` | Vitest, Playwright, prevenção de flaky tests |
| `qa-tester` | `systematic-debugging`, `browser-e2e-testing`, `handoff` | Investigação de falhas, jornadas web e troca de contexto |
| `devsecops` | `cybersecurity`, `llm-security`, `railway-ops` | Segurança e deploy |
| Todos | `clean-code-principles`, `senior-swe-intuition` | Transversais |
| `swe-backend` | `systematic-debugging`, `domain-modeling`, `handoff` | Causa-raiz, domínio e continuidade |
| `swe-frontend` | `systematic-debugging`, `browser-e2e-testing`, `handoff` | Regressões UI, browser e continuidade |
| `devsecops` | `systematic-debugging`, `handoff` | Incidentes e continuidade |
| `code-reviewer` | `handoff` | Continuidade de revisão |
| `product-manager` | `domain-modeling`, `handoff` | Vocabulário do domínio e continuidade |

## **Regras específicas do perfil**

- **Minimalismo:** este perfil existe para descobrir. Evitar dependências e abstrações prematuras.
- **Type safety:** `strict: true`, sem `any` implícito.
- **Zod no boundary:** entrada/saída de API, form e parse de input externo. Tipos derivam do schema (`z.infer`), nunca duplicados.
- **Migrations** são a fonte de verdade do schema, mesmo em SQLite.
- **Testes por demanda:** quando a lógica central estabilizar e valer proteger contra regressão.
- **Alias de import** (`$lib/...`) em vez de caminho relativo longo.
- **Gate antes de fechar uma etapa:** `pnpm check && pnpm biome check .` (mais `pnpm test`, quando houver suite). Conferir o exit code, não o texto — ver *Verificação* na base.

## **Gotchas conhecidos**

<!-- Acumular aqui as armadilhas deste projeto: sintoma observado + causa + o que não fazer.
     O sintoma vem primeiro, porque é por ele que a próxima pessoa reencontra o problema. -->

- [Nenhum registrado ainda.]

---

# Perfil `max`

## **Stack Técnica**

Mesma base do `min`, com as diferenças:

- **Persistência:** PostgreSQL em produção (SQLite aceitável em dev), Drizzle abstraindo a transição; migrations obrigatórias;
- **Separação api/web:** a API pode ser SvelteKit (endpoints) ou serviço próprio, conforme o projeto;
- **Testes:** [`vitest`](https://vitest.dev/) (unit + integração) e [`playwright`](https://playwright.dev/) (E2E);
- **Observabilidade:** Mastra Observability por padrão; [`logfire`](https://pydantic.dev/docs/logfire/) como alternativa;
- **Infra:** Docker Compose (Postgres, Redis, proxy) quando o projeto exigir.

## **Arquitetura Base**

Separação `api/` + `web/` + `docker/` + `xyz/`. Nem todo projeto precisa de todas: `web/` aparece quando a UI é separada da API; `docker/` quando há infraestrutura containerizada.

```
[nome-do-projeto]/
├── api/                          # API + lógica de negócio
│   ├── src/
│   │   ├── lib/
│   │   │   ├── server/
│   │   │   │   ├── ai/           # Agents, tools, workflows (Mastra)
│   │   │   │   ├── db/           # Drizzle: schema, migrations
│   │   │   │   ├── integrations/ # APIs externas
│   │   │   │   └── services/     # Lógica de domínio
│   │   │   └── shared/           # Schemas Zod, tipos isomórficos
│   │   ├── routes/
│   │   └── hooks.server.ts
│   ├── tests/                    # unit + integração
│   ├── evals/                    # Código dos evals (versionado)
│   ├── .env
│   ├── drizzle.config.ts
│   └── package.json
├── web/                          # UI/frontend, quando separada da API
│   └── ...
├── docker/                       # Infraestrutura containerizada
│   ├── compose.yml               # api + web + postgres + demais serviços
│   ├── api.Dockerfile            # Multi-stage: base → dev → prod
│   ├── web.Dockerfile
│   └── postgres/
│       └── init.sql              # Schema inicial / extensões
├── xyz/                          # Workspace LOCAL do TPM — 100% gitignored
│   ├── artifacts/ · docs/ · db/ · evals/ · logs/ · inputs/ · outputs/ · scripts/
├── README.md
├── TODO.md
├── HANDOFF.md
├── FUTURE.md
├── FLOW.md
└── [LLM].md
```

## **Agentes e Skills**

Os 7 subagentes e 24 skills, invocados por `@nome` ou auto-routing (ver base).

| Subagente | Quando delegar |
| --- | --- |
| `swe-backend` | Server-side: services, DB, integrações, workflows Mastra, endpoints |
| `swe-frontend` | UI: componentes Svelte, rotas, forms, state, fetch |
| `code-reviewer` | Pós-feature, pré-merge (read-only) |
| `qa-tester` | Vitest, Playwright, evals, investigação de falhas |
| `devsecops` | Deploy, infra, secrets, auditoria de segurança, incidentes |
| `ux-designer` | UX/UI ponta a ponta: discovery, direção visual, copy, auditoria |
| `product-manager` | Validar premissa, viabilidade de negócio, PRD, roadmap, sprint |

| Quem usa | Skill | Para que |
| --- | --- | --- |
| `swe-backend` | `mastra` | Agents, workflows, tools, scorers, evals, observability |
| `swe-frontend` | `sveltekit` | Routing, SSR, load functions, form actions, hooks |
| `swe-frontend` / `ux-designer` | `ux-ui-design`, `sveltekit-ui` | UX/UI geral; shadcn-svelte + Svelte 5 runes + Tailwind v4 |
| `swe-frontend` / `ux-designer` | `ux-writing`, `conversion-copywriting` | Microcopy/IA de produto; copy explicativa ou comercial para páginas e apresentações |
| `swe-frontend` / `ux-designer` | `minimalist-ui` | Direção minimalista somente por pedido explícito do TPM |
| `qa-tester` | `qa-testing` | Vitest (browser mode), Playwright, MSW, flaky tests |
| `qa-tester` | `systematic-debugging`, `browser-e2e-testing`, `handoff` | Investigação de falhas, jornadas web e troca de contexto |
| `devsecops` | `cybersecurity` | OWASP Top 10, secrets, CSP, audit pré-deploy |
| `devsecops` / `code-reviewer` | `llm-security` | OWASP LLM Top 10, prompt injection, guardrails, PII |
| `devsecops` | `railway-ops` / `hetzner-coolify-ops` | Deploy conforme a infra escolhida |
| `code-reviewer` | `rigorous-code-review`, `senior-swe-intuition` | Carregadas automaticamente |
| Todos | `clean-code-principles`, `senior-swe-intuition` | Transversais |
| `swe-backend` | `systematic-debugging`, `domain-modeling`, `handoff` | Causa-raiz, domínio e continuidade |
| `swe-frontend` | `systematic-debugging`, `browser-e2e-testing`, `handoff` | Regressões UI, browser e continuidade |
| `swe-frontend` | `ux-writing`, `conversion-copywriting`, `minimalist-ui` | Texto/IA e copy de páginas; minimalismo apenas sob demanda explícita |
| `product-manager` / `ux-designer` | `domain-modeling`, `handoff` | Vocabulário do domínio e continuidade |
| `product-manager` / `ux-designer` | `ux-writing`, `conversion-copywriting` | Terminologia/IA e mensagem de produto, páginas ou apresentações |
| `devsecops` | `systematic-debugging`, `handoff` | Incidentes e continuidade |
| `code-reviewer` | `handoff` | Continuidade de revisão |

**Utilitário (manual copiável, não é skill):** `~/dev/orquestration/utils/RAILWAY.md` — deploy no Railway; copiar para a raiz do projeto (ver *Protocolo de Documentação* na base).

**Receitas de uso proativo:**

```text
DISCOVERY (problem space — antes de construir)
  ux-designer        → valida premissa, mapeia fluxos e friction
  product-manager    → pressure-test da decisão, viabilidade de negócio, kill/build
  ↓ TPM lê os dois reports e decide

DELIVERY (solution space — construção e entrega)
  product-manager    → vira a direção decidida em PRD, stories, roadmap, OKR, sprint
  swe-backend        → services, DB, integrações, Mastra
  swe-frontend       → UI, rotas SvelteKit, componentes
  qa-tester          → testes + evals
  ux-designer        → direção visual, copy e auditoria antes do merge
  code-reviewer      → revisa pré-merge
  devsecops          → AUDIT pré-deploy; EXECUTE com confirmação do TPM
```

## **Regras específicas do perfil**

- **TDD/EDD:** escrever testes e/ou evals antes da implementação.
- **Dois níveis de teste.** Lógica pura → unitário. O que cruza o boundary (rota, banco, integração) → teste de integração contra a API e o Postgres reais de teste, não contra mock — o mock prova o contrato que você imaginou, não o que está no ar. Uma tarefa fecha com os dois verdes.
- **Type safety:** `strict: true`, sem `any` implícito.
- **Zod no boundary**, tipos derivados do schema.
- **Migrations** são a fonte de verdade do schema; não alterar tabela direto em produção.
- **Smoke manual antes do merge de UI ou rota**, com dado real no browser — typecheck e testes verdes não cobrem o que a suite não exercita.
- **Alias de import** (`$lib/...`, `~/...`) em vez de caminho relativo longo.

### Gates

Nesta ordem, todos verdes, antes de considerar uma tarefa concluída:

1. `pnpm test` — unitários e integração
2. `pnpm check` — typecheck (svelte-check + tsc)
3. `pnpm biome check .` — lint e formatação
4. `pnpm build` — build sem erro

```bash
pnpm test && pnpm check && pnpm biome check . && pnpm build
```

Rodar pelo script do `package.json` ou pelo binário em `node_modules/.bin/`, conferindo o exit code (ver *Verificação* na base). Build incremental com cache fora do diretório de saída já produziu build que sai 0 com a pasta vazia — ao mexer na configuração de build, rodar duas vezes seguidas e conferir que o artefato existe nas duas.

## **Gotchas conhecidos**

<!-- Acumular aqui as armadilhas deste projeto: sintoma observado + causa + o que não fazer.
     O sintoma vem primeiro, porque é por ele que a próxima pessoa reencontra o problema. -->

- [Nenhum registrado ainda.]

## **Evals**

- Uma pasta por execução: `xyz/evals/<pasta do dia>/<timestamp completo>/`, gerada com `date` real. Run nova é pasta nova.
- Artefatos gerados pelo próprio código do eval: `summary.json` (métricas agregadas e config da run), `cases.json` (resultado por caso, tokens, latência), `judge_results.json` (vereditos e justificativas), `records.jsonl` (turnos completos), `report.md` (resumo de latência, custo e qualidade).
- **Índice de Qualidade (%)** como métrica de topo, com tokens, latência e custo rastreados.
- **Juiz de fabricante distinto do gerador**, para não medir autopreferência.

### O Índice de Qualidade não é alvo de otimização

A suite é proxy do comportamento do agente, e proxy que vira meta deixa de medir. Os casos são poucos e visíveis: dá para ficar bom neles sem melhorar nada para o usuário.

- A nota serve para detectar regressão entre runs. 100% significa que a suite não pegou nada nesta run, não que o agente está bom.
- **Caso que falha por defeito do teste se corrige no teste, não no prompt.** Ajustar o prompt para o caso passar deixa o comportamento original intacto.
- Mudança de prompt exige hipótese declarada antes da run, e vale por si — não por ter subido a nota. Uma trava por vez.
- **Caso não medido não é caso aprovado.** Erro de rede, 429 ou timeout contam à parte, senão a série histórica registra queda de qualidade onde houve queda de conexão.
