# Instruções — pasta `orquestration`

> Este arquivo orienta qualquer agente de IA (Claude Code, Codex, Gemini CLI, Antigravity) que abrir **esta pasta**. Versões `AGENTS.md` e `GEMINI.md` têm conteúdo idêntico.

## O que é esta pasta

`orquestration/` é a **fonte da verdade** da biblioteca de agentes e skills **de engenharia e da gestão de produto/projetos de software (PM/PMO/TPM)** de IA de Rogério Kreidlow. O conteúdo daqui é sincronizado, via `scripts/sync.sh`, para `~/.claude`, `~/.codex`, `~/.gemini` e Antigravity (`~/.gemini/antigravity-cli`). Não é um projeto de software — é um repositório de configuração de IA.

> Escopo: **engenharia + a camada de PM/PMO de software adjacente a ela** (discovery, delivery, roadmap, OKR, sprints — o que orbita a construção do produto). Skills de negócio puro (BeTalent) e pessoais ficam no Claude Chat/Projects pessoal e de trabalho — não entram aqui nem nos CLIs de código.

## Responsáveis

- **Technical PM (TPM):** Rogério Kreidlow (humano). Decide produto, prioridade e aprova mudanças críticas.
- **Senior SWE:** você (o assistente). Mantém a qualidade técnica de agents/skills e dos scripts de sync, sob supervisão do TPM.

## Regras ao trabalhar AQUI

1. **A fonte canônica é `agents/*.md` e `skills/*/`.** Nunca edite as cópias em `~/.claude`, `~/.codex`, `~/.gemini` — elas são geradas e serão sobrescritas pelo próximo sync.
2. **Os `.toml` (Codex) e os `.md` de Gemini/Antigravity são GERADOS** pelos scripts em `scripts/`. Não edite à mão; edite o `.md` canônico em `agents/` e rode o sync.
3. **`name:` no frontmatter == nome da pasta/arquivo.** Divergência faz o Antigravity ignorar a skill/agente em silêncio. Exceção intencional e única: `pydantic-ai` usa `name: building-pydantic-ai-agents` (nome upstream; idêntico nos 3 ambientes — não "consertar").
4. **`model:` sempre por alias** (`opus`/`sonnet`), nunca ID completo — os conversores dependem do alias para mapear por engine. ID hardcoded quebra a geração multi-CLI.
5. **Antes de propor sync ou mudança ampla, reporte ao TPM** em linguagem de produto/comportamento. Mudança em agente/skill afeta 4 ferramentas de uma vez.
6. **Não há mais backup local.** Os snapshots pré-reorg/pré-sync foram removidos — **esta pasta é a fonte canônica** e os ambientes (`~/.claude`, `~/.codex`, `~/.gemini`) são regeneráveis via `sync.sh` (idempotente). Em mudança destrutiva, confirme com o TPM antes; o versionamento de longo prazo deve vir de `git init` (ainda pendente).

## Estrutura

```
agents/   9 subagentes .md (canônico)   → todos os ambientes
skills/   16 skills (pasta/SKILL.md)     → todos os ambientes
scripts/sync.sh       instalador idempotente
scripts/*.py          geradores de variantes Codex/Gemini
templates/            py-{min,med,max} / ts-max (bootstrap de projeto novo, versionados -vN)
```

> **Templates de projeto:** ao criar o `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` de um projeto novo, usar como base o template do stack e perfil adequados (maior `-vN` é a versão ativa): `py-min` (descoberta pura — Typer, JSON/MD, sem testes/banco), `py-med` (padrão — monorepo NiceGUI→core→SQLite, testes/EDD leve, Railway opcional), `py-max` (projeto profissional/de terceiro — api/web/docker separados) ou `ts-max` (stack TypeScript). Adaptar ao projeto; não copiar cegamente. Os configs globais (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md`) já orientam os agentes a consultarem esses templates.

## Mapeamento de modelos (alias → engine)

| Alias | Claude | Codex | Gemini / Antigravity |
|---|---|---|---|
| `opus` | Opus 4.8 (low) | gpt-5.6-sol (low) | gemini-3.5-flash (high) |
| `sonnet` | Sonnet 5 (low) | gpt-5.6-luna (low) | gemini-3.5-flash (low) |

Diretiva TPM (jul/2026): só dois aliases — `opus` (supervisão) e `sonnet` (execução); `haiku` foi removido. O valor entre parênteses é o reasoning effort. No Codex ele é emitido no `.toml`; no Claude e no Gemini fica só documentado (não há campo de effort por subagente que possamos setar com segurança).

## Fluxo de mudança

1. Edita `agents/<nome>.md` ou `skills/<nome>/SKILL.md`.
2. Valida `name:` == pasta/arquivo e `model:` por alias.
3. `bash scripts/sync.sh`.
4. Confirma contagem nos ambientes.

## Regras de autoria (best practices Anthropic)

- **Agente:** `description` com gatilho de delegação ("Invoke when…"); system prompt curto, como descrição de cargo, com definition-of-done e formato de output; `tools` com o mínimo necessário (ex.: reviewer read-only); `model` por alias.
- **Skill:** `description` em 3ª pessoa = *o que faz* + *quando usar* (≤1024 chars); corpo do `SKILL.md` < 500 linhas; `references/` a 1 nível; sem datas que envelhecem (ou em seção "old patterns").

## Ambiente

- Antigravity lê de `~/.gemini` (skills compartilhadas em `~/.gemini/skills`, agentes do CLI em `~/.gemini/antigravity-cli/agents`). **Não** usa `~/.antigravity`. Migração Gemini→Antigravity: prazo 18/jun/2026 (não-enterprise).
- Há um hook `rtk` que às vezes engole/corrompe a saída do shell. Workaround: prefixar comandos com `RTK_DISABLE=1` e usar heredoc `<<'EOF'`.

Para operação detalhada (quando chamar cada agente, receitas de orquestração), veja a seção **"Como operar o time no dia a dia"** no **README.md**.
