# orquestration

Fonte da verdade dos **agentes** e **skills de engenharia** de IA de Rogério Kreidlow, sincronizados para os quatro assistentes de linha de comando que ele usa: **Claude Code**, **Codex CLI**, **Gemini CLI** e **Antigravity** (`agy` CLI + IDE).

Edita-se aqui; um script propaga para os diretórios de cada ferramenta. Nada deve ser editado direto em `~/.claude`, `~/.codex` ou `~/.gemini` — essas cópias são geradas.

> Esta pasta cobre **só engenharia**. Skills de negócio (BeTalent) e pessoais vivem no Claude Chat/Projects pessoal e de trabalho — não nos CLIs de código.

---

## O que tem aqui

```
orquestration/
├── agents/               # 8 subagentes (.md, formato canônico Claude)
├── skills/               # 15 skills (pasta/SKILL.md + references/)
├── scripts/
│   ├── sync.sh                 # instala agents + skills nos ambientes
│   ├── md-to-codex-toml.py     # gera variantes .toml (Codex)
│   └── md-to-gemini-md.py      # gera variantes .md (Gemini/Antigravity)
├── templates/            # templates de CLAUDE.md/AGENTS.md p/ novos projetos (python.md, typescript.md)
├── CLAUDE.md             # instruções para o agente que abrir ESTA pasta
├── AGENTS.md             # (mesmo conteúdo de CLAUDE.md; lido por Codex/Antigravity)
└── GEMINI.md             # (mesmo conteúdo de CLAUDE.md; lido por Gemini CLI)
```

> `.build/` aparece após o primeiro sync — são as variantes geradas por CLI (efêmeras, não versionar).

---

## Os 9 agentes

| Agente | Papel | Tier |
|---|---|---|
| **swe-backend** | API, modelos de dados, lógica de negócio, integrações, jobs | sonnet |
| **swe-frontend** | Componentes, rotas, forms, state, data fetching | sonnet |
| **ux-ui-designer** | Refino visual: design system, ARIA, contraste, CWV | sonnet |
| **code-reviewer** | Review pós-feature / pré-merge, read-only | sonnet |
| **qa-tester** | Escreve e roda testes, investiga falhas | sonnet |
| **devsecops** | Deploy, infra, secrets, auditoria de segurança | sonnet |
| **ux-senior** | Discovery, pesquisa UX, validação de premissa | opus |
| **pm-senior** | Challenger de decisões de produto, blind spots (problem space) | opus |
| **pm-senior-delivery** | Executor PM/PMO: PRD, roadmap, OKR, sprints, estimativas (solution space) | opus |

## As 16 skills

`clean-code-principles` · `senior-swe-intuition` · `rigorous-code-review` · `qa-testing` · `cybersecurity` · `llm-security` · `fastapi` · `pydantic-ai` · `mastra` · `logfire` · `sveltekit` · `sveltekit-ui` · `python-ui` · `railway-ops` · `hetzner-coolify-ops` · `pm-software`

As skills carregam automaticamente quando a `description` casa com o contexto/stack — não precisam ser invocadas à mão.

---

## Como sincronizar

```bash
bash scripts/sync.sh
```

O sync é idempotente (usa `rsync --delete` por skill e regenera as variantes por CLI). Depois dele:

| Ambiente | Agents | Skills |
|---|---|---|
| Claude Code | `~/.claude/agents/*.md` | `~/.claude/skills/*/` |
| Codex CLI | `~/.codex/agents/*.toml` | `~/.codex/skills/*/` |
| Gemini CLI | `~/.gemini/agents/*.md` | `~/.gemini/skills/*/` |
| Antigravity | `~/.gemini/antigravity-cli/agents/*.md` | `~/.gemini/skills/*/` (shared) |

> **Antigravity** não usa `~/.antigravity` (isso é só o perfil do editor). Lê tudo de `~/.gemini`. Migração Gemini→Antigravity tem prazo **18/jun/2026** para contas não-enterprise.

---

## Modelos por engine

Os `.md` canônicos usam **alias** (`opus`/`sonnet`); os conversores resolvem para o modelo real de cada ferramenta. O valor entre parênteses é o reasoning effort (emitido no `.toml` do Codex; documental no Claude e no Gemini):

| Alias | Claude | Codex | Gemini / Antigravity |
|---|---|---|---|
| `opus` | Opus 4.8 (low) | gpt-5.6-sol (low) | gemini-3.5-flash (high) |
| `sonnet` | Sonnet 5 (low) | gpt-5.6-luna (low) | gemini-3.5-flash (low) |

---

## Adicionar ou editar

1. Edite em `agents/<nome>.md` ou `skills/<nome>/SKILL.md`.
2. **`name:` no frontmatter tem que ser igual ao nome da pasta/arquivo** — senão o Antigravity ignora silenciosamente. (Exceção conhecida: `pydantic-ai` usa `name: building-pydantic-ai-agents`, o nome upstream da skill.)
3. Rode `bash scripts/sync.sh`.

**Regras de autoria** (best practices Anthropic):
- **Agente** — `description` com gatilho ("Invoke when…"); system prompt curto como descrição de cargo; `tools` com menor privilégio necessário; `model` por alias.
- **Skill** — `description` em 3ª pessoa cobrindo *o que faz* + *quando usar* (≤1024 chars); corpo do `SKILL.md` < 500 linhas; `references/` a 1 nível de profundidade; sem informação que envelhece.

---

## Backups e versionamento

Os snapshots locais antigos (`~/Downloads/orquestration_backup_pre-reorg/` e `~/orquestration_env_backup_pre-sync/`) **foram removidos**. Esta pasta passou a ser a **fonte canônica** dos agents e skills de engenharia; os ambientes (`~/.claude`, `~/.codex`, `~/.gemini`) são regeneráveis a qualquer momento pelo `sync.sh` (idempotente).

A rede de segurança agora é o **Git**: este ecossistema é versionado em [github.com/rogerkrw/orquestration](https://github.com/rogerkrw/orquestration) e replicável em outras máquinas (clone + `sync.sh`). O histórico de ações relevantes fica em [`CHANGELOG.md`](CHANGELOG.md) — atualize-o a cada mudança significativa.

---

## Como operar o time no dia a dia

### Arquitetura mental

```text
PROBLEM SPACE                            SOLUTION SPACE
─────────────                            ──────────────
você (PM/TPM master) ────────────┐
swe-senior (sessão principal)  ◄─┤────► swe-senior (orquestra)
                                 │      ├── swe-backend
ux-senior            (opus)      │      ├── swe-frontend
pm-senior            (opus)      │      ├── ux-ui-designer
                                 │      ├── pm-senior-delivery
                                 │      ├── code-reviewer
                                 │      ├── qa-tester
                                 │      └── devsecops
```

- **swe-senior NÃO é um arquivo de subagente.** É a própria sessão principal (Claude Code / Codex / Gemini / agy), instanciada pelo `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` do projeto. Você fala com ela; ela despacha aos subagentes.
- **Você é o orquestrador máximo.** O swe-senior decide tecnicamente; você decide prioridade, aceitação, escalação.
- **Subagentes têm contexto isolado.** O histórico verboso do agente fica isolado — só o resumo volta para a sessão principal.

### Quando chamar cada papel

**Problem space** (planejamento, discovery, estratégia):

| Quem | Quando chamar | Tier |
|---|---|---|
| **você (TPM)** | Sempre — direção, prioridade, aceitação | humano |
| **swe-senior** | Sempre — interlocutor técnico, orquestrador (sessão principal) | opus |
| **ux-senior** | Discovery, validar premissa, mapear fluxos, friction | opus |
| **pm-senior** | Pressure-test de decisão, blind spots, kill/build | opus |

**Solution space** (implementação):

| Quem | Quando chamar | Tier |
|---|---|---|
| **swe-backend** | API, modelo de dados, lógica de negócio, integrações, jobs | sonnet |
| **swe-frontend** | Componentes, rotas, forms, state, fetch | sonnet |
| **ux-ui-designer** | Refino visual, ARIA, contraste, estados, CWV, responsivo | sonnet |
| **code-reviewer** | Pós-feature, pré-merge, read-only, "o que pode dar errado?" | sonnet |
| **qa-tester** | Escrever testes faltantes, rodar suite, investigar falhas | sonnet |
| **devsecops** | Deploy, infra, secrets, auditoria de segurança | sonnet |
| **pm-senior-delivery** | PRD, user stories, roadmap, OKR, sprint plan, estimativas, status report | opus |

> **Escalação para incidente / PR crítico:** subagentes têm tier fixo no arquivo. Para raciocínio mais profundo (incidente de produção, security review de alto risco, PR complexo) — **não delegue ao subagente**; trate na sessão principal (`swe-senior` em opus), que invoca as mesmas skills com mais capacidade de inferência.

### Como invocar (por ferramenta)

| Ferramenta | Auto-routing | Explícito | Gerenciar |
|---|---|---|---|
| **Claude Code** | descreve a tarefa, swe-senior delega pela `description` | `@swe-backend ...` | `/agents` |
| **Gemini CLI** | idem | `@code-reviewer ...` | `/agents` |
| **Codex CLI** | match por descrição | spawn no prompt | `/agent` (switch) |
| **Antigravity (agy)** | idem | — | `/agents`, `/skills` |

### Receitas de orquestração

#### A. Feature nova (do zero ao merge)

```text
você → swe-senior
        ├─ (opc) ux-senior            "valida se faz sentido pro usuário antes"
        ├─ (opc) pm-senior  "o que estou perdendo aqui?"
        ├─ (opc) pm-senior-delivery   "transforma a direção em PRD + stories"
        ├─ swe-backend       "implementa o que decidimos"
        ├─ swe-frontend      "monta a UI"
        ├─ ux-ui-designer    "refine antes de merge"
        ├─ qa-tester         "testes do golden path + 2 edge cases"
        └─ code-reviewer     "revisa antes de merge"
```

#### B. Bug em produção

```text
você → swe-senior: "está caindo X no prod, [logs]"
swe-senior → devsecops (AUDIT)    "investiga, sem alterar nada"
           → swe-backend           "fix"
           → qa-tester             "teste que reproduz o bug + verifica o fix"
           → code-reviewer         "revisa o fix"
           → devsecops (EXECUTE)   "deploy com confirmação"
```

#### C. Decisão de produto importante (discovery → delivery)

```text
você → swe-senior: "estou pensando em [decisão]"
swe-senior → pm-senior   "steelman the case against"
           → ux-senior             "evidência de fluxos / friction"
              ↓ você lê os reports e decide
           → pm-senior-delivery    "decidido: vira PRD + roadmap + OKR"
```

#### D. Auditoria de segurança pré-launch

```text
você → swe-senior: "vamos pra prod amanhã, audita"
swe-senior → devsecops (AUDIT)   "roda audit-checklist + cybersecurity/llm-security"
           → code-reviewer       "diff completo com lente de segurança"
              ↓ você recebe relatório priorizado go/no-go
```

### Quando NÃO usar agentes

- Tarefa trivial de um arquivo só → faça direto na sessão principal.
- Exploração ambígua ("o que tem aqui?") → você precisa do contexto na sessão principal.
- Iteração visual rápida → overhead de spawning não compensa.

Regra prática: delegue quando a tarefa é (1) bem-definida, (2) isolável, (3) potencialmente verbosa em raciocínio. Falhou em um? → sessão principal.

### Resumo do dia a dia

1. Abre o projeto → o CLI lê o `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` → você conversa com o swe-senior.
2. Você descreve em **linguagem de produto** o que precisa.
3. swe-senior decide se delega ou resolve sozinho.
4. Subagentes trabalham em paralelo quando faz sentido (backend + frontend simultâneos).
5. code-reviewer e qa-tester rodam antes de qualquer "considera pronto".
6. devsecops em **AUDIT** antes de deploy; **EXECUTE** com confirmação explícita.
7. pm-senior e ux-senior entram quando você precisa de segunda cabeça no problem space; pm-senior-delivery quando a direção já está decidida e vira artefato (PRD, roadmap, OKR, sprint).
8. Você intervém em decisão de produto, escalação técnica que vira produto, ou trade-off que merece aprovação.
