# Orquestration Playbook

Como operar o ecossistema de agentes + skills no dia a dia, em **Claude Code**, **Codex CLI**, **Gemini CLI** e **Antigravity** (agy CLI + IDE).

`orquestration/` é a **fonte da verdade**. Edita-se aqui; `scripts/sync.sh` propaga para `~/.claude`, `~/.codex`, `~/.gemini` (e Antigravity via `~/.gemini`).

---

## 1. Arquitetura mental

```
PROBLEM SPACE                            SOLUTION SPACE
─────────────                            ──────────────
você (PM/TPM master) ────────────┐
swe-senior (sessão principal)  ◄─┤────► swe-senior (orquestra)
                                 │      ├── swe-backend
ux-senior        (opus)          │      ├── swe-frontend
pm-senior        (opus)          │      ├── ux-ui-designer
                                 │      ├── code-reviewer
                                 │      ├── qa-tester
                                 │      └── devsecops
```

- **swe-senior NÃO é um arquivo de subagente.** É a própria sessão principal (Claude Code / Codex / Gemini / agy), instanciada pelo `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` do projeto. Você fala com ela; ela despacha aos subagentes.
- **Você é o orquestrador máximo.** O swe-senior decide tecnicamente; você decide prioridade, aceitação, escalação.
- **Subagentes têm contexto isolado.** O histórico verboso do agente fica isolado — só o resumo volta para a sessão principal.

---

## 2. Estrutura de pastas

```
orquestration/                       ← fonte canônica versionável (só engenharia)
├── agents/    ← 8 .md (source-of-truth, formato Claude: tools PascalCase, model alias)
├── skills/    ← 15 skills expandidas (pasta/SKILL.md + references/)
├── scripts/
│   ├── sync.sh              ← instala tudo nos ambientes
│   ├── md-to-codex-toml.py  ← gera variantes .toml (Codex)
│   └── md-to-gemini-md.py   ← gera variantes .md (Gemini/Antigravity)
├── .build/        ← variantes geradas por-CLI (efêmero, não editar)
├── README.md, CLAUDE.md, AGENTS.md, GEMINI.md, PLAYBOOK.md, PY.md, TS.md
```

> Skills de negócio (BeTalent) e pessoais **não** ficam aqui — vivem no Claude Chat/Projects pessoal e de trabalho.

**Onde cada ambiente lê** (após o sync):

```
~/.claude/agents/                 ← 8 .md            ~/.claude/skills/   ← skills
~/.gemini/agents/                 ← 8 .md            ~/.gemini/skills/   ← skills (shared p/ Antigravity)
~/.codex/agents/                  ← 8 .toml          ~/.codex/skills/    ← skills
~/.gemini/antigravity-cli/agents/ ← 8 .md (agy)
```

> **Antigravity** não usa `~/.antigravity` (só perfil do editor). Lê de `~/.gemini/`: skills compartilhadas em `~/.gemini/skills/`, agents do CLI em `~/.gemini/antigravity-cli/agents/`. Migração Gemini→Antigravity tem deadline **18/jun/2026** (não-enterprise).

**Fluxo de atualização:**
1. Edita um agente em `agents/<nome>.md` ou uma skill em `skills/<nome>/`
2. Roda `bash scripts/sync.sh`
3. Pronto — Claude Code, Codex, Gemini e Antigravity sincronizados

---

## 3. Modelos por papel (alias → modelo real por engine)

Os `.md` canônicos usam **alias** (`opus`/`sonnet`/`haiku`). Os conversores mapeiam por engine:

| Alias | Claude | Codex | Gemini / Antigravity |
|---|---|---|---|
| `opus` | Opus 4.8 | gpt-5.5 (effort high) | gemini-3.1-pro-preview |
| `sonnet` | Sonnet 4.6 | gpt-5.3-codex (high) | gemini-3.5-flash |
| `haiku` | Haiku 4.5 | gpt-5.3-codex (low) | gemini-3.1-flash-lite |

> Diretiva TPM (mai/2026): só dois tiers ativos no Codex — `gpt-5.5` (supervisão/problem space) e `gpt-5.3-codex` (execução). Ignorar gpt-5.4/5.4-mini/5.2-codex.

---

## 4. Os 9 papéis (8 subagentes + você)

### Problem space (planejamento, discovery, estratégia)

| Quem | Quando chamar | Tier |
|---|---|---|
| **você (TPM)** | Sempre — direção, prioridade, aceitação | humano |
| **swe-senior** | Sempre — interlocutor técnico, orquestrador (sessão principal) | opus |
| **ux-senior** | Discovery, validar premissa, mapear fluxos, friction | opus |
| **pm-senior** | Pressure-test de decisão, blind spots, kill/build | opus |

### Solution space (implementação)

| Quem | Quando chamar | Tier |
|---|---|---|
| **swe-backend** | API, modelo de dados, lógica de negócio, integrações, jobs | sonnet |
| **swe-frontend** | Componentes, rotas, forms, state, fetch | sonnet |
| **ux-ui-designer** | Refino visual, ARIA, contraste, estados, CWV, responsivo | sonnet |
| **code-reviewer** | Pós-feature, pré-merge, read-only, "o que pode dar errado?" | sonnet |
| **qa-tester** | Escrever testes faltantes, rodar suite, investigar falhas | sonnet |
| **devsecops** | Deploy, infra, secrets, auditoria de segurança | sonnet |

> **Escalação para incidente / PR crítico:** subagentes têm tier fixo no arquivo. Para raciocínio mais profundo (incidente de produção, security review de alto risco, PR complexo) — **não delegue ao subagente**; trate na sessão principal (`swe-senior` em opus), que invoca as mesmas skills com mais capacidade de inferência.

---

## 5. Como invocar (por ferramenta)

| Ferramenta | Auto-routing | Explícito | Gerenciar |
|---|---|---|---|
| **Claude Code** | descreve a tarefa, swe-senior delega pela `description` | `@swe-backend ...` | `/agents` |
| **Gemini CLI** | idem | `@code-reviewer ...` | `/agents` |
| **Codex CLI** | match por descrição | spawn no prompt | `/agent` (switch) |
| **Antigravity (agy)** | idem | — | `/agents`, `/skills` |

---

## 6. Padrões de orquestração — receitas

### A. Feature nova (do zero ao merge)
```
você → swe-senior
        ├─ (opc) ux-senior   "valida se faz sentido pro usuário antes"
        ├─ (opc) pm-senior   "o que estou perdendo aqui?"
        ├─ swe-backend       "implementa o que decidimos"
        ├─ swe-frontend      "monta a UI"
        ├─ ux-ui-designer    "refine antes de merge"
        ├─ qa-tester         "testes do golden path + 2 edge cases"
        └─ code-reviewer     "revisa antes de merge"
```

### B. Bug em produção
```
você → swe-senior: "está caindo X no prod, [logs]"
swe-senior → devsecops (AUDIT)    "investiga, sem alterar nada"
           → swe-backend           "fix"
           → qa-tester             "teste que reproduz o bug + verifica o fix"
           → code-reviewer         "revisa o fix"
           → devsecops (EXECUTE)   "deploy com confirmação"
```

### C. Decisão de produto importante
```
você → swe-senior: "estou pensando em [decisão]"
swe-senior → pm-senior   "steelman the case against"
           → ux-senior   "evidência de fluxos / friction"
              ↓ você lê os dois reports e decide
```

### D. Auditoria de segurança pré-launch
```
você → swe-senior: "vamos pra prod amanhã, audita"
swe-senior → devsecops (AUDIT)   "roda audit-checklist + cybersecurity/llm-security"
           → code-reviewer       "diff completo com lente de segurança"
              ↓ você recebe relatório priorizado go/no-go
```

---

## 7. Skills — 15

| Skill | Domínio | Consumida sobretudo por |
|---|---|---|
| clean-code-principles | Princípios universais (DRY/KISS/SOLID/FP) | todos |
| senior-swe-intuition | Julgamento de SWE 10+ anos | code-reviewer, swe-senior |
| rigorous-code-review | Code review rigoroso + QA | code-reviewer |
| qa-testing | pytest/vitest/playwright + PydanticAI | qa-tester |
| cybersecurity | AppSec web (OWASP Top 10:2025) | devsecops, code-reviewer |
| llm-security | Segurança de apps LLM (OWASP LLM Top 10:2025) | devsecops, swe-backend |
| fastapi | FastAPI + Pydantic | swe-backend |
| pydantic-ai | Agentes Pydantic AI | swe-backend |
| mastra | Agentes/workflows TS | swe-backend |
| logfire | Observabilidade (Py/TS/Rust) | swe-backend, devsecops |
| sveltekit | SvelteKit full-stack | swe-frontend |
| sveltekit-ui | shadcn-svelte + Svelte 5 + Tailwind v4 | swe-frontend, ux-ui-designer |
| python-ui | NiceGUI / Gradio / Chainlit | swe-backend, ux-ui-designer |
| railway-ops | Plataforma Railway | devsecops |
| hetzner-coolify-ops | Hetzner + Coolify | devsecops |

As skills carregam automaticamente quando o trigger da `description` casa com o contexto/stack. Não precisa invocar manualmente.

> Skills de negócio (BeTalent) e pessoais vivem no Claude Chat/Projects, fora desta pasta e dos CLIs de código.

---

## 8. Quando NÃO usar agentes

- Tarefa trivial de um arquivo só → faça direto na sessão principal.
- Exploração ambígua ("o que tem aqui?") → você precisa do contexto na sessão principal.
- Iteração visual rápida → overhead de spawning não compensa.

Regra prática: delegue quando a tarefa é (1) bem-definida, (2) isolável, (3) potencialmente verbosa em raciocínio. Falhou em um? → sessão principal.

---

## 9. Manutenção

### Atualizar agente ou skill
1. Edita em `agents/<nome>.md` ou `skills/<nome>/SKILL.md`
2. `bash scripts/sync.sh`

### Adicionar agente / skill
1. Cria `agents/<nome>.md` (segue o padrão dos 8) ou `skills/<nome>/SKILL.md` (+ `references/` opcional)
2. **`name:` no frontmatter DEVE bater com o nome da pasta/arquivo** — senão Antigravity falha em silêncio
3. `bash scripts/sync.sh`

### Regras de autoria (best practices Anthropic)
- **Agent**: descrição com "Invoke when…", system prompt curto como job description, least-privilege em `tools`, `model` por alias.
- **Skill**: descrição 3ª pessoa (what + when, ≤1024 chars), corpo <500 linhas, referências 1 nível de profundidade, sem informação que envelhece (ou em seção "old patterns").

### Versionamento
`orquestration/` deveria ser um repo git (`git init`) — versiona o ecossistema, dá histórico das mudanças e replica em outra máquina via clone + `sync.sh`.

---

## 10. Resumo do dia a dia

1. Abre o projeto → o CLI lê o `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` → você conversa com o swe-senior.
2. Você descreve em **linguagem de produto** o que precisa.
3. swe-senior decide se delega ou resolve sozinho.
4. Subagentes trabalham em paralelo quando faz sentido (backend + frontend simultâneos).
5. code-reviewer e qa-tester rodam antes de qualquer "considera pronto".
6. devsecops em **AUDIT** antes de deploy; **EXECUTE** com confirmação explícita.
7. pm-senior e ux-senior entram quando você precisa de segunda cabeça, não rotineiramente.
8. Você intervém em decisão de produto, escalação técnica que vira produto, ou trade-off que merece aprovação.
