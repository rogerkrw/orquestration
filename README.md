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
├── PLAYBOOK.md           # como operar o time de agentes no dia a dia
├── PY.md / TS.md         # templates de CLAUDE.md/AGENTS.md para novos projetos (Python / TypeScript)
├── CLAUDE.md             # instruções para o agente que abrir ESTA pasta
├── AGENTS.md             # (mesmo conteúdo de CLAUDE.md; lido por Codex/Antigravity)
└── GEMINI.md             # (mesmo conteúdo de CLAUDE.md; lido por Gemini CLI)
```

> `.build/` aparece após o primeiro sync — são as variantes geradas por CLI (efêmeras, não versionar).

---

## Os 8 agentes

| Agente | Papel | Tier |
|---|---|---|
| **swe-backend** | API, modelos de dados, lógica de negócio, integrações, jobs | sonnet |
| **swe-frontend** | Componentes, rotas, forms, state, data fetching | sonnet |
| **ux-ui-designer** | Refino visual: design system, ARIA, contraste, CWV | sonnet |
| **code-reviewer** | Review pós-feature / pré-merge, read-only | sonnet |
| **qa-tester** | Escreve e roda testes, investiga falhas | sonnet |
| **devsecops** | Deploy, infra, secrets, auditoria de segurança | sonnet |
| **ux-senior** | Discovery, pesquisa UX, validação de premissa | opus |
| **pm-senior** | Challenger de decisões de produto, blind spots | opus |

## As 15 skills

`clean-code-principles` · `senior-swe-intuition` · `rigorous-code-review` · `qa-testing` · `cybersecurity` · `llm-security` · `fastapi` · `pydantic-ai` · `mastra` · `logfire` · `sveltekit` · `sveltekit-ui` · `python-ui` · `railway-ops` · `hetzner-coolify-ops`

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

Os `.md` canônicos usam **alias** (`opus`/`sonnet`/`haiku`); os conversores resolvem para o modelo real de cada ferramenta:

| Alias | Claude | Codex | Gemini / Antigravity |
|---|---|---|---|
| `opus` | Opus 4.8 | gpt-5.5 | gemini-3-pro |
| `sonnet` | Sonnet 4.6 | gpt-5.3-codex | gemini-3-flash |
| `haiku` | Haiku 4.5 | gpt-5.3-codex (low effort) | gemini-3-flash-lite |

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

Para o detalhamento operacional (quando chamar cada agente, receitas de orquestração, escalação), veja **[PLAYBOOK.md](PLAYBOOK.md)**.
