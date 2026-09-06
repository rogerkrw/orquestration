# Instruções — pasta `orquestration`

> Este arquivo orienta qualquer agente de IA (OpenCode, Claude Code, Codex, Gemini CLI, Antigravity) que abrir **esta pasta**. Versões `AGENTS.md` e `GEMINI.md` têm conteúdo idêntico.

## O que é esta pasta

`orquestration/` é a **fonte da verdade** da biblioteca de agentes e skills **de engenharia e da gestão de produto/projetos de software (PM/PMO/TPM)** de IA de Rogério Kreidlow. O conteúdo daqui é sincronizado, via `scripts/sync.sh`, para OpenCode (`~/.config/opencode`), `~/.claude`, `~/.codex`, `~/.gemini` e Antigravity (`~/.gemini/antigravity-cli`). Não é um projeto de software — é um repositório de configuração de IA.

> Escopo: **engenharia + a camada de PM/PMO de software adjacente a ela** (discovery, delivery, roadmap, OKR, sprints — o que orbita a construção do produto). Skills de negócio puro (BeTalent) e pessoais ficam no Claude Chat/Projects pessoal e de trabalho — não entram aqui nem nos CLIs de código.

## Responsáveis

- **Technical PM (TPM):** Rogério Kreidlow (humano). Decide produto, prioridade e aprova mudanças críticas.
- **Senior SWE:** você (o assistente). Mantém a qualidade técnica de agents/skills e dos scripts de sync, sob supervisão do TPM.

## Regras ao trabalhar AQUI

1. **A fonte canônica é `agents/*.md` e `skills/*/`.** Nunca edite as cópias em `~/.config/opencode`, `~/.claude`, `~/.codex`, `~/.gemini` ou `~/.gemini/antigravity-cli` — elas são geradas e serão sobrescritas pelo próximo sync.
2. **Os `.toml` (Codex) e os `.md` derivados de OpenCode/Gemini/Antigravity são GERADOS** pelos scripts em `scripts/`. Não edite à mão; edite o `.md` canônico em `agents/` e rode o sync.
3. **`name:` no frontmatter == nome da pasta/arquivo.** Divergência faz o Antigravity ignorar a skill/agente em silêncio. Exceção intencional e única: `pydantic-ai` usa `name: building-pydantic-ai-agents` (nome upstream; idêntico nos cinco ambientes — não "consertar").
4. **`model:` sempre por alias** (`opus`/`sonnet`), nunca ID completo — os conversores dependem do alias para mapear por engine. ID hardcoded quebra a geração multi-CLI.
5. **Antes de propor sync ou mudança ampla, reporte ao TPM** em linguagem de produto/comportamento. Mudança em agente/skill afeta 5 ferramentas de uma vez.
6. **Não há mais backup local.** Os snapshots pré-reorg/pré-sync foram removidos — **esta pasta é a fonte canônica** e os ambientes (`~/.config/opencode`, `~/.claude`, `~/.codex`, `~/.gemini`) são regeneráveis via `sync.sh` (idempotente). Em mudança destrutiva, confirme com o TPM antes; o versionamento de longo prazo deve vir de `git init` (ainda pendente).

## Estrutura

```
agents/   9 subagentes .md (canônico)   → todos os ambientes
skills/   27 skills (pasta/SKILL.md)     → todos os ambientes
antigravity/plugin.json                  manifesto do plugin
scripts/sync.sh       instalador idempotente
scripts/*.py          geradores de variantes Codex/OpenCode/Gemini/Antigravity
templates/            BASE.md + py.md / ts.md (bootstrap de projeto novo)
```

> **Templates de projeto:** ao criar o `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` de um projeto novo, concatenar `BASE.md` (parte comum a todo projeto: processo, regras, git, documentação) com o bloco de stack — `py.md` ou `ts.md` — na seção do perfil adequado: `min` (descoberta e experimentação, estrutura enxuta + `xyz/`) ou `max` (projeto profissional/de terceiro, `api/`+`web/`+`docker/`+`xyz/`). Adaptar ao projeto; não copiar cegamente. Os configs globais (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md`) já orientam os agentes a consultarem esses templates.

## Mapeamento de modelos (alias → engine)

| Alias | OpenCode | Claude | Codex | Gemini / Antigravity |
|---|---|---|---|---|
| `opus` | herda o modelo da sessão (Zen/Go) | Opus 5 (low) | gpt-5.6-sol (low) | gemini-3.5-flash (high) |
| `sonnet` | herda o modelo da sessão (Zen/Go) | Sonnet 5 (low) | gpt-5.6-luna (low) | gemini-3.5-flash (low) |

Diretiva TPM (jul/2026): só dois aliases — `opus` (supervisão) e `sonnet` (execução); `haiku` foi removido. No OpenCode, o modelo é herdado da sessão para compatibilidade com Zen/Go. O valor entre parênteses é o reasoning effort. No Codex ele é emitido no `.toml`; no Claude e no Gemini fica só documentado (não há campo de effort por subagente que possamos setar com segurança).

## Fluxo de mudança

1. Edita `agents/<nome>.md` ou `skills/<nome>/SKILL.md`.
2. Valida `name:` == pasta/arquivo e `model:` por alias.
3. `bash scripts/sync.sh`.
4. Confirma contagem nos ambientes.

## Regras de autoria (best practices Anthropic)

- **Agente:** `description` com gatilho de delegação ("Invoke when…"); system prompt curto, como descrição de cargo, com definition-of-done e formato de output; `tools` com o mínimo necessário (ex.: reviewer read-only); `model` por alias.
- **Skill:** `description` em 3ª pessoa = *o que faz* + *quando usar* (≤1024 chars); corpo do `SKILL.md` < 500 linhas; `references/` a 1 nível; sem datas que envelhecem (ou em seção "old patterns").

## Ambiente

- Antigravity CLI lê agents globais de `~/.gemini/config/agents`, skills globais e plugins de `~/.gemini/antigravity-cli`. **Não** usa `~/.antigravity`. As skills completas do orquestration são distribuídas pelo plugin em `~/.gemini/antigravity-cli/plugins/orquestration/` para preservar referências.
- Há um hook `rtk` que às vezes engole/corrompe a saída do shell. Workaround: prefixar comandos com `RTK_DISABLE=1` e usar heredoc `<<'EOF'`.

Para operação detalhada (quando chamar cada agente, receitas de orquestração), veja a seção **"Como operar o time no dia a dia"** no **README.md**.
