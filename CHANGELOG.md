# Changelog

Histórico de mudanças do `orquestration` — a biblioteca canônica de agents e
skills de **engenharia** de IA de Rogério Kreidlow.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
As entradas são organizadas por data (não por versão semântica), já que este é
um repositório de configuração de IA, não um produto de software com releases.

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

### Removed
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
