# Stack Python — perfis `min` e `max`

<!--
py — bloco de stack para projetos Python. Combine com `BASE.md`
(comum a todo projeto) para montar o CLAUDE.md / AGENTS.md / GEMINI.md do projeto novo.
Escolha UM perfil abaixo, copie só as seções dele e remova estes comentários.

  min → projeto simples: src/ + xyz/ e da-lhe. Descoberta, experimentação, UI direto no pacote.
  max → projeto profissional/de terceiro: api/ + web/ + docker/ + xyz/, TDD, deploy.

Na dúvida, comece em `min`. Promover para `max` é barato; desinflar não é.
-->

## Escolha do perfil

| Sinal | `min` | `max` |
| --- | --- | --- |
| Objetivo | descobrir, experimentar, resolver algo do TPM | produto que outros usam, entregável |
| Estrutura | um pacote em `src/` + `xyz/` | `api/` + `web/` + `docker/` + `xyz/` |
| UI | NiceGUI/Chainlit direto dentro do `src/`, se houver | `web/` separada (SvelteKit) |
| Persistência | arquivo (JSON/MD) ou SQLite via SQLModel | Postgres (ou SQLite), migrations obrigatórias |
| Testes | quando a lógica estabilizar e valer proteger | TDD/EDD obrigatório |
| Deploy | local; Railway se o TPM pedir | esperado (Railway/Hetzner) |

**Gatilhos de promoção `min` → `max`:** terceiros passam a depender do projeto; a UI precisa de stack própria; entram autenticação, multiusuário ou dados sensíveis; o deploy vira requisito e não experimento.

---

# Perfil `min`

## **Stack Técnica**

- [`Python 3.14+`](https://docs.python.org/3/): linguagem;
- [`uv`](https://docs.astral.sh/uv/): package manager;
- [`ruff`](https://docs.astral.sh/ruff/): linter e formatter;
- `pydantic-settings` e `.env`: configurações e segredos;
- [`httpx`](https://www.python-httpx.org/): cliente HTTP assíncrono (scraping, APIs);
- [`Pydantic v2`](https://pydantic.dev/docs/validation/latest/get-started) (`>=2.13`): modelagem e validação de dados;
- [`Pydantic AI`](https://pydantic.dev/docs/ai/llms.txt) (`>=2.9`): framework de agentes;
- [`Typer`](https://typer.tiangolo.com/) (`>=0.26`): CLI (entry point padrão, scripts e comandos de manutenção);
- **UI web (opcional, decidida pelo TPM conforme a natureza do projeto e dispensável no início):** [`Chainlit`](https://docs.chainlit.io/) quando a interface for essencialmente chat, [`NiceGUI`](https://nicegui.io/) quando for uma app web comum. Verificar a versão suportada no lockfile e na documentação oficial. Mora **dentro do pacote**, não em projeto separado;
- **Persistência:** arquivo (JSON/MD em `xyz/db/`) enquanto bastar; [`SQLModel`](https://sqlmodel.tiangolo.com/) (`>=0.0.39`) sobre **SQLite** quando aparecer relação/consulta de verdade — aí JSON/MD viram só exports, não fonte de verdade;
- [`Ollama`](https://docs.ollama.com/): provider para LLMs locais;
- LLMs: `qwen3:4b-instruct` (default), `qwen3:8b` (LLM-as-a-judge), `nomic-embed-text-v2-moe:latest` (embeddings);
- [`pytest`](https://docs.pytest.org/en/stable/) (`>=8.4`) + [`pytest-asyncio`](https://pytest-asyncio.readthedocs.io/) (`>=1.2`): quando houver suite (ver *Regras*).

> **Nota:** LLMs proprietários, se introduzidos, o serão sob decisão do TPM. O projeto nasce local e pode permanecer local — o TPM pode decidir publicá-lo no Railway para uso via web.

## **Arquitetura Base**

Monorepo flat: um pacote em `src/`, um processo, um deploy. A UI (se houver) é um submódulo dentro do pacote e chama o core Python direto — sem camada HTTP intermediária.

```
[nome-do-projeto]/
├── src/
│   └── nome_do_projeto/          # Pacote principal (renomear para o nome real)
│       ├── __init__.py
│       ├── main.py               # Entry point (Typer app)
│       ├── web.py                # Entry point da UI web (quando houver)
│       ├── config.py             # pydantic-settings
│       ├── agents/               # Definições Pydantic AI
│       ├── tools/                # Funções/ferramentas dos agentes
│       ├── services/             # Lógica de domínio (use cases)
│       ├── database/             # Persistência (SQLModel + engine SQLite), quando houver
│       └── ui/                   # Camada de UI (Chainlit/NiceGUI), quando houver
├── tests/                        # Testes (pytest), quando houver
├── evals/                        # Scripts de evals (Pydantic AI Evals), quando houver
├── xyz/                          # Workspace LOCAL do TPM — 100% gitignored
│   ├── artifacts/                # Requisitos, specs, prints, inputs brutos do TPM
│   ├── docs/                     # Memória do projeto, reports, TODOs arquivados
│   ├── db/                       # SQLite local e/ou JSON/MD
│   ├── evals/                    # Saídas brutas das rodadas de eval
│   ├── logs/                     # Logs rápidos (se necessários)
│   ├── inputs/                   # Entradas de dados processáveis (.csv, .json, .md etc.)
│   ├── outputs/                  # Saídas de dados processados
│   └── scripts/                  # Scripts ad-hoc/one-off e experimentos isolados
├── .env
├── pyproject.toml
├── Procfile / configuração IaC   # Deploy (Railway), quando solicitado pelo TPM
├── README.md
├── TODO.md
├── HANDOFF.md
└── [LLM].md                      # CLAUDE.md, AGENTS.md, GEMINI.md
```

> `xyz/` é o workspace de bagunça do TPM — pensar, juntar artefatos, documentar. Ignorado por inteiro no git. Arquivos gerados ali seguem a regra de pasta do dia + timestamp exato (ver *Medição e Auditoria* na base).

## **Agentes e Skills**

| Subagente | Quando delegar |
| --- | --- |
| `swe-backend` | Services, modelos, agentes, integrações |
| `swe-frontend` | UI (Chainlit/NiceGUI): páginas, componentes, estado |
| `code-reviewer` | Pós-feature, pré-merge (read-only) |
| `qa-tester` | Testes, evals, investigação de falhas |
| `devsecops` | Deploy Railway, secrets, auditoria de segurança |
| `product-manager` | Validar premissa, viabilidade de negócio, PRD, roadmap, sprint |

| Quem usa | Skill | Para que |
| --- | --- | --- |
| `swe-backend` | `pydantic-ai` | Agentes, tools, structured output, streaming |
| `swe-frontend` | `python-ui` | NiceGUI/Chainlit/Gradio: escolha, layout, async |
| `qa-tester` | `qa-testing` | pytest + `pytest-asyncio` + `TestModel` |
| `qa-tester` | `systematic-debugging`, `browser-e2e-testing`, `handoff` | Investigação de falhas, jornadas web e troca de contexto |
| `devsecops` | `cybersecurity`, `llm-security`, `railway-ops` | Segurança e deploy |
| Todos | `clean-code-principles`, `senior-swe-intuition` | Transversais |
| `swe-backend` | `systematic-debugging`, `domain-modeling`, `handoff` | Causa-raiz, domínio e continuidade |
| `swe-frontend` | `systematic-debugging`, `browser-e2e-testing`, `handoff` | Regressões UI, browser e continuidade |
| `devsecops` | `systematic-debugging`, `handoff` | Incidentes e continuidade |
| `code-reviewer` | `handoff` | Continuidade de revisão |
| `product-manager` | `domain-modeling`, `handoff` | Vocabulário do domínio e continuidade |

## **Regras específicas do perfil**

- **Minimalismo radical:** este perfil existe para descobrir. Evitar dependências e abstrações prematuras.
- **Testes por demanda:** não há suite desde o início. Quando a lógica central estabilizar e valer proteger contra regressão, escrever pytest para ela.
- **Persistência progressiva:** arquivo enquanto bastar; SQLite via SQLModel quando a relação entre dados justificar. Postgres aqui é gatilho de promoção para `max`.
- **Alias de import** (`from nome_do_projeto.x import y`) em vez de caminho relativo longo.
- **Gate antes de fechar uma etapa:** `ruff check . && ruff format --check . && pytest` (a última parte, quando houver suite). Conferir o exit code, não o texto — ver *Verificação* na base.

## **Gotchas conhecidos**

<!-- Acumular aqui as armadilhas deste projeto: sintoma observado + causa + o que não fazer.
     O sintoma vem primeiro, porque é por ele que a próxima pessoa reencontra o problema. -->

- [Nenhum registrado ainda.]

---

# Perfil `max`

## **Stack Técnica**

* [`Python 3.14+`](https://docs.python.org/3/): linguagem;
* [`uv`](https://docs.astral.sh/uv/): package manager;
* [`ruff`](https://docs.astral.sh/ruff/): linter e formatter;
* [`FastAPI`](https://fastapi.tiangolo.com/): framework backend;
* [`Pydantic v2`](https://pydantic.dev/docs/validation/latest/get-started): modelagem e validação de dados;
* [`Pydantic AI`](https://pydantic.dev/docs/ai/overview/): framework de agentes — usar o que for conveniente (agents, graph, providers, tools, evals);
* [`Pydantic Logfire`](https://pydantic.dev/docs/logfire/get-started/): observabilidade;
* `pydantic-settings` e `.env`: configurações e segredos;
* **Persistência:** [`SQLModel`](https://sqlmodel.tiangolo.com/)/SQLAlchemy sobre **PostgreSQL** em produção (SQLite aceitável em dev); migrations obrigatórias;
* [`pytest`](https://docs.pytest.org/en/stable/): testes determinísticos;
* [`SvelteKit`](https://svelte.dev/docs/kit/introduction): framework de frontend/UI.

> **Nota:** os LLMs (locais via Ollama ou proprietários) serão definidos pelo TPM ao longo do projeto. É provável usar modelos locais/gratuitos em testes iniciais e partir para proprietários quando qualidade/capacidade exigirem.

## **Arquitetura Base**

Separação `api/` + `web/` + `docker/` + `xyz/`. Nem todo projeto precisa de todas: `web/` aparece quando há UI separada da API; `docker/` entra quando há infraestrutura containerizada (Postgres, Redis etc.).

```
[nome-do-projeto]/
├── api/                          # API + lógica de negócio
│   ├── nome_do_projeto/          # Pacote principal (renomear)
│   │   ├── __init__.py
│   │   ├── main.py               # Entry point (FastAPI)
│   │   ├── config.py             # pydantic-settings
│   │   ├── agents/               # Definições Pydantic AI
│   │   ├── tools/                # Funções/ferramentas dos agentes
│   │   ├── database/             # Persistência (SQLModel/SQLAlchemy) + migrations
│   │   └── services/             # Lógica de domínio (use cases)
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── evals/                # Código dos evals: cases, runners, gates (versionado)
│   ├── pyproject.toml
│   └── .env
├── web/                          # UI/frontend (SvelteKit), quando separada da API
│   └── ...
├── docker/                       # Infraestrutura containerizada
│   ├── compose.yml               # Sobe api + web + postgres + outros serviços
│   ├── api.Dockerfile            # Multi-stage: base → dev → prod
│   ├── web.Dockerfile            # Build da UI (quando web/ existir)
│   └── postgres/
│       └── init.sql              # Schema inicial / extensões (uuid-ossp, pgvector)
├── xyz/                          # Workspace LOCAL do TPM — 100% gitignored
│   ├── artifacts/                # Requisitos, specs, prints, PDFs, rascunhos do TPM
│   ├── docs/                     # Memória do projeto, reports de etapa, TODOs arquivados
│   ├── db/                       # SQLite local / dumps
│   ├── evals/                    # Saídas brutas das rodadas de eval (volumoso)
│   ├── logs/                     # Logs (se necessários)
│   ├── inputs/                   # Entradas de dados processáveis
│   ├── outputs/                  # Saídas de dados processados
│   └── scripts/                  # Scripts ad-hoc/one-off e experimentos
├── README.md
├── TODO.md
├── HANDOFF.md
├── FUTURE.md
├── FLOW.md
└── [LLM].md                      # CLAUDE.md, AGENTS.md, GEMINI.md
```

> `xyz/` é o workspace de bagunça do TPM, ignorado por inteiro. Não há pasta `docs/` versionada na raiz: o que merece virar memória pública do projeto entra no `README.md` ou nos `.md` perenes da raiz, por decisão do TPM.

## **Agentes e Skills**

O Principal Engineer orquestra **7 subagentes** e consome **24 skills** on-demand (ver base). Invocação via `@nome` ou auto-routing.

| Subagente | Quando delegar |
| --- | --- |
| `swe-backend` | API, modelos, lógica de negócio, integrações, jobs |
| `swe-frontend` | UI: componentes, rotas, forms, state, fetch |
| `code-reviewer` | Pós-feature, pré-merge, "o que pode dar errado aqui?" (read-only) |
| `qa-tester` | Testes faltantes, suite, investigação de falhas, evals |
| `devsecops` | Deploy, infra, secrets, auditoria de segurança, incidentes |
| `ux-designer` | UX/UI ponta a ponta: discovery, direção visual, copy, auditoria |
| `product-manager` | Pressure-test de decisão, viabilidade de negócio, PRD, roadmap, OKR, sprints |

| Quem usa | Skill | Para que |
| --- | --- | --- |
| `swe-backend` | `pydantic-ai` | Agentes, tools, structured output, streaming, testing |
| `swe-backend` | `fastapi` | Convenções da API, rotas, DI, Pydantic models |
| `swe-backend` | `logfire` | Observabilidade (já no stack base) |
| `swe-frontend` / `ux-designer` | `ux-ui-design`, `sveltekit`, `sveltekit-ui` | UX/UI geral; SvelteKit + shadcn-svelte + Tailwind v4 |
| `swe-frontend` / `ux-designer` | `ux-writing`, `conversion-copywriting` | Microcopy/IA de produto; copy explicativa ou comercial para páginas e apresentações |
| `swe-frontend` / `ux-designer` | `minimalist-ui` | Direção minimalista somente por pedido explícito do TPM |
| `qa-tester` | `qa-testing` | pytest + `pytest-asyncio` + `TestModel` (essencial p/ evals) |
| `qa-tester` | `systematic-debugging`, `browser-e2e-testing`, `handoff` | Investigação de falhas, jornadas web e troca de contexto |
| `devsecops` | `cybersecurity` | OWASP Top 10, secrets, audit-checklist pré-deploy |
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

**Utilitário (manual copiável, não é skill):** `~/dev/orquestration/utils/RAILWAY.md` — deploy no Railway; copiar para a raiz do projeto (ver *Protocolo de Documentação* na base). Mantido pelo `devsecops`.

**Receitas de uso proativo:**

```text
DISCOVERY (problem space — antes de construir)
  ux-designer        → valida premissa, mapeia fluxos e friction do usuário
  product-manager    → pressure-test da decisão, viabilidade de negócio, kill/build
  ↓ TPM lê os dois reports e decide

DELIVERY (solution space — construção e entrega)
  product-manager    → vira a direção decidida em PRD, stories, roadmap, OKR, sprint
  swe-backend        → implementa lógica, modelos, integrações, jobs
  swe-frontend       → monta a UI (SvelteKit): páginas, componentes, forms, state
  qa-tester          → testes + evals (antes ou junto à implementação)
  ux-designer        → direção visual, copy e auditoria antes do merge
  code-reviewer      → revisa pré-merge (implementa → /rigorous-code-review → fixes)
  devsecops          → AUDIT pré-deploy; EXECUTE com confirmação do TPM
```

## **Regras específicas do perfil**

- **TDD/EDD:** escrever testes e/ou evals antes da implementação.
- **Dois níveis de teste.** Lógica pura → unitário. O que cruza o boundary (rota, banco, integração externa) → teste de integração exercitando o caminho real, contra Postgres de teste. Uma tarefa fecha com os dois verdes.
- **Migrations** são a fonte de verdade do schema; não alterar tabela direto em produção.
- **Smoke manual antes do merge de UI** ou de endpoint de fluxo do usuário, com dado real — suite verde não cobre o que ela não exercita.
- **Alias de import** em vez de caminho relativo longo.

### Gates

Nesta ordem, todos verdes, antes de considerar uma tarefa concluída:

1. `pytest` — unitários e integração
2. `ruff check .` — lint
3. `ruff format --check .` — formatação
4. `mypy` (quando configurado) — tipos

```bash
pytest && ruff check . && ruff format --check .
```

Conferir o exit code, não o texto na tela (ver *Verificação* na base).

## **Gotchas conhecidos**

<!-- Acumular aqui as armadilhas deste projeto: sintoma observado + causa + o que não fazer.
     O sintoma vem primeiro, porque é por ele que a próxima pessoa reencontra o problema. -->

- [Nenhum registrado ainda.]

## **Evals**

- Uma pasta por execução: `xyz/evals/<pasta do dia>/<timestamp completo>/`, gerada com `date` real. Run nova é pasta nova.
- Artefatos gerados pelo próprio código do eval, não montados à mão depois: `summary.json` (métricas agregadas e config da run), `cases.json` (resultado por caso, tokens, latência), `judge_results.json` (vereditos e justificativas), `records.jsonl` (turnos completos), `report.md` (resumo de latência, custo e qualidade).
- **Índice de Qualidade (%)** como métrica de topo, com tokens, latência e custo rastreados.
- **Juiz de fabricante distinto do gerador**, para não medir autopreferência.

### O Índice de Qualidade não é alvo de otimização

A suite é proxy do comportamento do agente, e proxy que vira meta deixa de medir. Os casos são poucos e visíveis: dá para ficar bom neles sem melhorar nada para o usuário.

- A nota serve para detectar regressão entre runs. 100% significa que a suite não pegou nada nesta run, não que o agente está bom.
- **Caso que falha por defeito do teste se corrige no teste, não no prompt.** Ajustar o prompt para o caso passar deixa o comportamento original intacto.
- Mudança de prompt exige hipótese declarada antes da run, e vale por si — não por ter subido a nota. Uma trava por vez.
- **Caso não medido não é caso aprovado.** Erro de rede, 429 ou timeout contam à parte, senão a série histórica registra queda de qualidade onde houve queda de conexão.
