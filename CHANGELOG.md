# Changelog

Histórico de mudanças do `orquestration` — a biblioteca canônica de agents e
skills de **engenharia** de IA de Rogério Kreidlow.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
As entradas são organizadas por data (não por versão semântica), já que este é
um repositório de configuração de IA, não um produto de software com releases.

## [2026-06-05]

### Added
- **Skill `pm-software`.** Base de conhecimento de Gestão de Produto (PM) e de
  Projetos de Software (PMO/TPM): discovery, priorização (RICE/WSJF/MoSCoW), OST,
  roadmap, OKR/North Star, PRD/User Stories/DoD/DoR, sprints, métricas e status
  reports. `SKILL.md` (325 linhas) + 4 references (`artifacts`, `strategy`,
  `metrics`, `discovery`). Skills passam de 15 → **16**.
- **Agente `pm-senior-delivery`** (opus). Executor PM/PMO no **solution space**:
  transforma direção de produto já decidida em artefatos (PRD, user stories,
  roadmap, OKR, sprint plan, estimativas, status report) consumindo a skill
  `pm-software`. `tools: Read, Write, Edit, Grep, Glob, WebFetch, WebSearch`.
  Subagentes passam de 8 → **9**.

### Changed
- **`pm-senior` → `pm-senior-discovery`** (via `git mv`, histórico preservado).
  A renomeação explicita o eixo problem/solution space: `discovery` segue como
  challenger adversarial no **problem space** (questiona *se* é a coisa certa);
  o novo `delivery` opera no **solution space** (*como/quando* entregar).
  `description` do `discovery` atualizada para apontar o par.
- **Escopo da pasta ampliado** em `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`: de "só
  engenharia" para "**engenharia + a camada de PM/PMO de software adjacente**"
  (discovery, delivery, roadmap, OKR, sprints). Negócio puro (BeTalent) e
  pessoal seguem fora de escopo.
- **Referências atualizadas** ao par discovery/delivery e às novas contagens
  (9 agentes, 16 skills) em `README.md` (tabelas, diagrama mental, receitas A e C,
  resumo), `templates/python.md` e `templates/typescript.md` (tabela de delegação,
  regra de delegação, receitas DISCOVERY/DELIVERY).

### Reverted
- **`pm-senior-discovery` → `pm-senior`** (decisão do TPM, ainda em 2026-06-05).
  A renomeação do challenger foi desfeita: o agente voltou ao nome e ao conteúdo
  originais (`pm-senior`, problem space). O **par permanece** — agora `pm-senior`
  (problem) + `pm-senior-delivery` (solution); apenas o sufixo `-discovery` saiu.
  `pm-senior-delivery`, a skill `pm-software` e a ampliação de escopo **foram
  mantidos**. Referências em `README.md`/`templates/` reapontadas para `pm-senior`.

## [2026-05-30]

### Added
- **Versionamento Git.** A pasta passou a ser um repositório Git e foi publicada
  em [github.com/rogerkrw/orquestration](https://github.com/rogerkrw/orquestration)
  (público, via SSH). Commit inicial com 84 arquivos: 8 subagentes, 15 skills de
  engenharia, scripts de sync e documentação.
- **`.gitignore` defensivo.** Bloqueia estado local não-canônico
  (`.antigravitycli/`, `.build/`, `.claude/`) e padrões de segredo
  (`.env*`, `*.key`, `*.pem`, `id_rsa*`, `credentials*.json`) por precaução.
- **`CHANGELOG.md`** (este arquivo) para registrar o histórico de ações.

### Changed
- **Política de backup nos docs.** `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` e
  `README.md` foram atualizados: esta pasta é declarada a **fonte canônica** e os
  ambientes (`~/.claude`, `~/.codex`, `~/.gemini`) são regeneráveis via
  `sync.sh`. O Git passa a ser a rede de segurança no lugar dos backups locais.
- **Mapeamento de modelos por engine atualizado** (diretiva TPM). Codex: alias
  `sonnet` sobe de `reasoning_effort` *medium* → **high** (executor padrão mais
  capaz); `opus` segue em `gpt-5.5`, `haiku` em low. Gemini/Antigravity: IDs
  atualizados para os atuais — `gemini-3.1-pro-preview` (opus),
  `gemini-3.5-flash` (sonnet) e `gemini-3.1-flash-lite` (haiku, GA; o *preview*
  será desligado em 2026-07-09). Aplicado nos geradores
  (`scripts/md-to-codex-toml.py`, `scripts/md-to-gemini-md.py`) e nas tabelas de
  `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`/`README.md`/`PLAYBOOK.md`.
- **Consolidação de docs (fim do dia).** O `PLAYBOOK.md` foi **fundido no
  `README.md`**: o conteúdo operacional único (arquitetura mental problem/solution
  space, quando chamar cada papel, invocação por ferramenta, as 4 receitas de
  orquestração, quando NÃO delegar, resumo do dia a dia) virou a seção **"Como
  operar o time no dia a dia"**. A duplicação que existia entre os dois (estrutura
  de pastas, tabela de modelos, regras de autoria, nota Antigravity) **não** foi
  reintroduzida. As referências a `PLAYBOOK.md` em `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`
  passaram a apontar para a seção do README.
- **Templates de bootstrap reunidos em `templates/`.** `PY.md` → `templates/python.md`
  e `TS.md` → `templates/typescript.md` (via `git mv`, histórico preservado);
  agrupá-los alinha com o padrão plural-por-função das demais pastas. O `sync.sh`
  não referencia esses arquivos — a movimentação é inócua para a propagação.

### Removed
- **`PLAYBOOK.md`.** Removido após a fusão do seu conteúdo no `README.md` (ver
  *Changed*). O histórico permanece no Git.
- **Backups locais pré-reorganização.** Excluídos `~/Downloads/orquestration_backup_pre-reorg/`
  (snapshot pré-reorg, 86 arquivos) e `~/orquestration_env_backup_pre-sync/`
  (agents/skills dos 4 ambientes pré-primeiro-sync, ~2.9 MB). Antes da exclusão,
  validou-se que todo o conteúdo era regenerável a partir do canônico — exceto a
  skill de negócio `project-process-management` (GP/BPM), retirada do escopo de
  engenharia de forma intencional.

### Security
- **Auditoria pré-publicação.** Varredura por nome e por conteúdo (chaves
  OpenAI/Anthropic, tokens GitHub, AWS, Google, private keys, Slack) na árvore e
  no conteúdo *staged* antes do push. Nenhum segredo real encontrado; os únicos
  matches de "secret" são skills que *documentam* gestão de secrets.
