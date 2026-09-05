# Changelog

Histórico de mudanças do `orquestration` — a biblioteca canônica de agents e
skills de **engenharia** de IA de Rogério Kreidlow.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
As entradas são organizadas por data (não por versão semântica), já que este é
um repositório de configuração de IA, não um produto de software com releases.

## [2026-09-05]

### Added

- **Agente `marketing-ui`** (opus) para superfícies comerciais de software:
  landing pages, homepages de aquisição, pricing, páginas de produto e
  lançamentos. Separa brief, mensagem, direção visual, implementação, auditoria
  e experimentos de conversão, sem assumir branding amplo, UX de produto ou
  claims sem evidência.

## [2026-09-04]

### Changed

- **Atualização de stacks e referências oficiais.** `pydantic-ai` agora orienta Pydantic AI V2 e a migração V1→V2, com links no domínio atual; `llm-security` acompanha o OWASP GenAI LLM Top 10:2026; `railway-ops` prioriza Infrastructure as Code e marca `railway.toml/json` como legado até 01/12/2026; `logfire` usa o fluxo atual de preload TypeScript; `sveltekit`/`sveltekit-ui` reforçam Svelte 5, `$app/state` e o bootstrap atual do shadcn-svelte; QA/E2E e Mastra registram Node 24 LTS como baseline para projetos novos, sem ignorar o lockfile.
- **Referências de infraestrutura corrigidas.** Preços hardcoded de Hetzner/Coolify foram removidos das tabelas de decisão e receitas; continuam apenas fórmulas, dimensões e instrução de consulta à tabela/API vigente. A skill `python-ui` deixou de carregar um diagnóstico permanente e sem fonte sobre Chainlit, passando a exigir verificação de releases e segurança.

### Added

- **Quatro skills de workflow de engenharia:** `systematic-debugging` para investigação por causa-raiz; `domain-modeling` para vocabulário, estados e invariantes; `handoff` para continuidade entre sessões e agentes; e `browser-e2e-testing` para jornadas reais no navegador.
- **Três skills de linguagem e direção visual:** `ux-writing` para microcopy e arquitetura da informação em produtos; `conversion-copywriting` para mensagens explicativas ou comerciais em LPs, sites e apresentações HTML; e `minimalist-ui` para uma direção minimalista opt-in, invocada somente por pedido explícito do TPM.
- **Referências editoriais canônicas** em `ux-writing/references/principles.md`, baseadas em Microsoft Writing Style/Brand Voice, GOV.UK Design Principles e Material Design Writing.
- **Roteamento explícito nos agentes e templates.** Backend, frontend, QA, DevSecOps, produto, UX e code review passaram a apontar para as skills complementares aplicáveis, mantendo a distribuição pelos quatro CLIs via `sync.sh`.

## [2026-08-13]

### Added

- **Skill `ux-ui-design` — UX e UI de ponta a ponta, agnóstica de stack.** Preenche o buraco que existia entre `sveltekit-ui` (só shadcn-svelte) e a auditoria pós-implementação: não havia onde decidir paleta, escala tipográfica e hierarquia. Organizada em três modos — **decidir** (token system com 4-6 cores por papel, tipografia por papel, layout, elemento-assinatura, e a crítica do plano contra o brief antes de codar), **implementar** (estados completos, hierarquia, movimento) e **revisar** (5 dimensões, saída em `arquivo:linha` por severidade). Inclui a calibração anti-clichê: os três looks em que design gerado por IA converge (creme + serifa + terracota; preto + acento ácido; broadsheet com hairlines) são default, não escolha. Três references: `review.md` (~80 regras concretas destiladas das [Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines) da Vercel, estáticas — sem fetch em runtime), `copy.md` (microcopy por contexto: CTA, erro, empty state, confirmação, tom) e `pt-br.md`. Fontes consultadas e descartadas: `ui-ux-pro-max` (2,7 MB de CSV + 180 KB de Python, exige CLI e runtime — não passa pelo `sync.sh`, e o `products.csv` mapeia categoria de produto → estilo, que é a máquina de produzir a média) e `copywriting` da Corey Haines (marketing, não interface).
- **`references/pt-br.md` — o que nenhuma skill de prateleira cobre.** Interface em PT-BR não é interface em inglês traduzida: texto em português ocupa **15-25% mais espaço** (Save→Salvar +50%, Settings→Configurações +75%), o que quebra botão, nav e tabela dimensionados no inglês. Mais formatos brasileiros (`R$ 1.234,56`, `dd/mm/aaaa`, CPF/CNPJ/CEP/telefone com máscara), busca de endereço por CEP, Pix como método de primeira classe (com código copiável, expiração e confirmação assíncrona), e as duas divergências de escrita: **sem Title Case** e segunda pessoa implícita.
- **`references/business.md` na skill de produto — a lente de negócio que faltava.** Unit economics (gross margin, CAC, LTV, LTV/CAC, payback, churn, NRR, burn multiple, Rule of 40) no formato fórmula + benchmark + *por que o PM se importa*; TAM/SAM/SOM bottom-up; pricing e value metric (com a nota de Pix e parcelamento mudando a economia no Brasil); competitivo (Porter, SWOT, matriz de posicionamento) com as perguntas que valem mais que o framework; posicionamento (April Dunford); JTBD; os quatro riscos de Cagan — com destaque para o de **viabilidade de negócio**, o mais esquecido em time técnico; e o case de negócio em uma página. Referência de conteúdo: [`deanpeters/Product-Manager-Skills`](https://github.com/deanpeters/Product-Manager-Skills) (77 skills), consultado e reescrito no padrão da casa, não copiado.

### Changed (agentes e skills)

- **`ux-senior` + `ux-ui-designer` → `ux-designer`** (opus). Os dois se sobrepunham e dividiam mal: um fazia discovery e parava antes da tela, o outro auditava ARIA depois do fato, e ninguém decidia a direção visual. O agente único cobre o arco — discovery, direção, implementação, copy e auditoria —, com a instrução de identificar o modo antes de começar. Consome a skill `ux-ui-design`.
- **`pm-senior` + `pm-senior-delivery` → `product-manager`** (opus). Mesma lógica: a divisão problem space / solution space obrigava a escolher o agente antes de saber em que camada o problema estava. O agente único mantém as três posturas — ceticismo construtivo na premissa, viabilidade de negócio, e a entrega em artefato — e ganha a camada de negócio que não existia.
- **Skill `pm-software` → `product-management`** (via `git mv`, histórico preservado). Novo cabeçalho declarando as três camadas (problema → negócio → entrega) e a sequência que importa: pular a do meio produz feature bem construída, para problema real, que não se paga. O conteúdo anterior (discovery, priorização, roadmap, OKR, cerimônias, artefatos, métricas) foi mantido integralmente.
- **Contagens corrigidas para 7 agentes e 17 skills** em `README.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` e nos dois templates. O README estava defasado em "15 skills".
- **Tabela alias→engine: `opus` agora documenta Opus 5** (era Opus 4.8). Nenhum frontmatter mudou — os agentes seguem por alias, e o alias resolve para o modelo corrente pelo próprio CLI.

### Fixed

- **`sync.sh` deixava agente aposentado vivo em Codex, Gemini e Antigravity.** O `.build/` é regenerado pelos conversores, mas eles só escrevem — nunca apagam. Agente renomeado continuava lá e era copiado para os três CLIs a cada sync: a primeira execução desta leva deixou **12 agentes** nesses ambientes (os 7 corretos + `pm-senior`, `pm-senior-delivery`, `pm-senior-discovery`, `ux-senior`, `ux-ui-designer`), sendo que `pm-senior-discovery` vinha de um rename de junho e sobreviveu a todos os syncs desde então. O Claude escapava porque copia de `agents/` direto. Corrigido com `rm -rf` do `.build/` antes de gerar. Sintoma que isso produzia: auto-routing sorteando um agente que não existe mais no repositório.
- **`sync.sh` não removia skill renomeada ou aposentada do destino.** O `rsync --delete` limpa o *conteúdo* de cada pasta, mas itera sobre a origem — pasta que deixou de existir no canônico sobrevivia como órfã em `~/.claude/skills` e nos demais ambientes, e seguia sendo carregada pelo trigger. Adicionada varredura reversa que remove o que não tem contraparte na origem, com log do que foi apagado. Sem isso, `pm-software` continuaria ativa ao lado de `product-management`.

### Changed (templates)

- **Templates condensados de 6 arquivos para 3: `BASE.md` + `py.md` + `ts.md`.** Os quatro anteriores (`py-min`, `py-med`, `py-max`, `ts-max`, versionados `-vN`) duplicavam ~60% do texto, e a correção nunca chegava às quatro cópias — a pasta local de trabalho chegou a se chamar `others/`, `oth/` e `xyz/` ao mesmo tempo, em arquivos que deveriam concordar. Agora `BASE.md` carrega o comum a todo projeto e os dois arquivos de stack trazem só o que depende de stack ou perfil, em dois perfis (`min` e `max` — o `med` foi absorvido). De ~1360 para ~780 linhas mantidas, sem perda de conteúdo. Novo `templates/README.md` documenta como montar o arquivo de um projeto novo, onde colocar uma regra nova (o critério é "depende da stack ou do perfil?") e o teste reverso: regra igual nos dois arquivos de stack pertence ao `BASE.md`. Sufixo `-vN` abandonado.
- **Regras novas destiladas dos projetos reais (`vals` e `valens`).** No `BASE.md`: precedência de contexto (global < projeto < código real, e onde o código diverge do doc, o código é o fato); "este arquivo descreve **como**, o **quê** vive no `TODO.md`"; decidir é o padrão, consultando só quando errar for caro e irreversível; uma pergunta por vez, no momento em que surge; registro neutro (fato em vez de adjetivo, sem meta-comentário, rótulos secos); **verificação de gate** — o hook `rtk` já exibiu um `tsc` com exit 127 como "compilation completed" e um `hasConsent: false` como `hasConsent: bool`, então gate se confere por exit code, com canary diante de verde suspeito; suíte verde prova só o que cobre; timestamp por `date` real, nunca arredondado, em pasta do dia + arquivo completo; `xyz/artifacts/` read-only para o agente; datas absolutas; e a regra de idioma que estava ambígua — **comentários e docstrings em PT-BR**, explicando o porquê, com **comentário de armadilha preservado** (a regra de minimalismo não se aplica a ele, porque apagar reintroduz o bug). Nos arquivos de stack: gates ordenados com comando único, dois níveis de teste, alias de import, seção "Gotchas conhecidos" para o projeto acumular, parametrizar em vez de fixar (com o limite do segundo caso de uso), e o Índice de Qualidade que não é alvo de otimização.
- **`py-med-v1` — UI opcional e renomeação de `oth/` → `xyz/`.** A camada de UI deixa de ter NiceGUI como padrão: agora é **Chainlit ou NiceGUI, decidida pelo TPM conforme a natureza do projeto, e dispensável no início** (Gradio sai da lista). O comentário de `src/<pkg>/ui/` acompanha ("Camada de UI (Chainlit, NiceGUI etc., se decidida pelo TPM)") e a frase da arquitetura perde o pressuposto de NiceGUI/processo único. A pasta gitignored de trabalho local passa de `oth/` para `xyz/`, e alguns rótulos ficam mais precisos: `evals/` = "scripts de evals", `artifacts/` = "inputs do TPM", `logs/` = "logs rápidos", `scripts/` = "experimentos rápidos e isolados".

## [2026-07-12]

### Added

- **`utils/RAILWAY.md` — manual generalista de deploy no Railway.** Destilado do `RAILWAY.md` real do projeto `sales-crm`, removendo tudo específico (IDs, URLs, senhas, Brevo, seed admin) e preservando as armadilhas vividas: auth de CLI não-interativa (mesmo `$HOME` = sessão compartilhada com o agente), monorepo → `railway up --path-as-root`, cookie cross-domain → proxy no front, TCP proxy do Postgres não habilitado em projeto ressubido (criar via GraphQL), cron dry-run→live com protocolo de ativação segura, e armadilhas de build/deploy. Nomenclatura de serviços alinhada ao padrão de pastas (`api`/`web`/`Postgres`/`cron`). Novo diretório `utils/` para manuais copiáveis (distintos de skills). O template `py-max-v1` instrui copiá-lo para a raiz do projeto ao subir no Railway.

### Changed (templates)

- **`py-max-v1` — revisão de consistência e reestruturação de pastas.** Novo perfil v1 do template profissional, revisado em várias frentes:
  - **Layout de topo `api`/`web`/`docs`/`docker`/`others`** (volta à nomenclatura `api`/`web` do v0; `backend`/`frontend` renomeados). Nova pasta `docs/` na raiz = documentação **perene e pública** (versionada, curada à mão pelo TPM). `others/` volta a ser **100% gitignored** (workspace local do TPM); subpasta `docs/` interna renomeada para `others/memories/` (desambiguação com a `docs/` da raiz). Curadoria por opt-in: o que merece histórico, o TPM promove de `others/` para `docs/`.
  - **`docs/RAILWAY.md`** citado no Protocolo de Documentação, apontando o caminho absoluto `~/dev/orquestration/utils/RAILWAY.md` (evita referência órfã — o template vira o CLAUDE.md do projeto novo, sem memória de `orquestration`). Tabela de **utilitários** separada da de skills.
  - **Regras suavizadas/corrigidas:** `net-add zero` de gate rígido → heurística anti-inchaço que não bloqueia entrega; timestamp `%Y%m%d_%H%M%S_` cobre documentação/auditoria/resultados exportados (código versionado isento); assinatura de commit exige modelo+esforço explícitos (auditoria); CLI removido como camada de UI (SvelteKit é a UI; Typer só como auxiliar opcional de teste). Correções factuais (links Pydantic, contagem 9 subagentes/16 skills, invocação `@nome`, `llm-security` na tabela) e enxugamento de reforços retóricos "é X, não Y".

## [2026-07-11]

### Changed

- **Mapa de modelos reduzido a 2 aliases + família GPT-5.6/Gemini 3.5 atualizada.** Diretiva TPM (jul/2026): manter só `opus` e `sonnet` (alias `haiku` removido) e rodar tudo em **low reasoning effort**. Novo mapa alias→engine:
  - `opus` → Opus 4.8 (low) · Codex `gpt-5.6-sol` (low) · Gemini `gemini-3.5-flash` (high)
  - `sonnet` → Sonnet 5 (low) · Codex `gpt-5.6-luna` (low) · Gemini `gemini-3.5-flash` (low)
  Aposentados `gpt-5.5`/`gpt-5.3-codex` (Codex) e `gemini-3.1-pro-preview`/`gemini-3.1-flash-lite` (Gemini). `gpt-5.6-sol`/`luna` são os tiers flagship/fast da família GPT-5.6 (GA 09/jul/2026). O reasoning effort é emitido no `.toml` do Codex (`REASONING_MAP`); no Claude e no Gemini fica só documentado (sem campo de effort por subagente confiável). Atualizados `scripts/md-to-codex-toml.py` e `scripts/md-to-gemini-md.py` (`MODEL_MAP`/`REASONING_MAP`, docstrings) e a tabela alias→engine + regra 4 + diretiva TPM em `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` e `README.md`. Nenhum frontmatter de agente mudou (segue por alias); Claude `sonnet` → `claude-sonnet-5`.

### Fixed

- **Skill `cybersecurity`: OWASP Top 10:2025 reordenado para a lista oficial.** A tabela estava com ordenação incorreta (Cryptographic em #2, SSRF como #10 próprio). Corrigida para a edição oficial: A02 Security Misconfiguration, A03 Software Supply Chain Failures, A04 Cryptographic, A05 Injection, …, A10 Mishandling of Exceptional Conditions (novo). A ordenação de `rigorous-code-review` já estava correta e serviu de referência cruzada.
- **Skill `cybersecurity`: `python-jose`/`passlib` → `PyJWT`/`pwdlib`.** Ambas as libs estão sem manutenção (python-jose com CVEs; passlib parado desde 2020 e quebrando com bcrypt 4.x). Snippet em `references/fastapi-security.md` migrado para `import jwt` (PyJWT) + `PasswordHash.recommended()` (pwdlib, argon2id), conforme recomendação oficial atual do FastAPI. Gotcha #3 e tabela do `SKILL.md` atualizados.
- **Skill `railway-ops`: limites de recurso por plano reformulados.** A tabela apresentava 48 GB/48 vCPU (Hobby) e 1 TB/1000 vCPU (Pro) como se fossem limite de instância — na verdade são `por réplica × replicas`. Reformulada para destacar o teto **por réplica** (Hobby 8 GB/8 vCPU; Pro ~32 GB/32 vCPU, com ressalva de redução recente) em `references/pricing-and-costs.md` e `SKILL.md`.
- **Agentes `swe-backend`/`swe-frontend`: detecção de stack atualizada.** `PydanticAI` → `Pydantic AI` (branding atual). Frontend: instrução de checar `tailwind.config` trocada por `@theme`/`app.css` (Tailwind v4 é CSS-first, sem `tailwind.config.js`) e detecção SvelteKit passa a assumir Svelte 5 runes salvo `export let` legado — alinhando com as skills `sveltekit`/`sveltekit-ui`.

### Changed (templates)

- **Templates adotam versionamento `-vN`.** Os 3 templates de bootstrap foram renomeados para carregar sufixo de versão: `python-minimal.md` → `python-minimal-v0.md`, `python-complete.md` → `python-complete-v0.md`, `typescript.md` → `typescript-v0.md`. `-v0` é a base preservada; revisões significativas criam um novo `-vN` (N+1) sem sobrescrever o anterior, e a maior `-vN` é a versão ativa. Renomeações puras (conteúdo idêntico).
- **Nomenclatura enxuta `py-{min,med,max}` / `ts-max`.** Os `-v0` foram renomeados para o padrão min/med/max: `python-minimal-v0` → `py-min-v0`, `python-complete-v0` → `py-max-v0`, `typescript-v0` → `ts-max-v0`. O par min/max explicita o eixo de complexidade (min = experimental descartável; max = projeto profissional com api/web/docker separados).
- **Novos perfis Python v1 (`py-min-v1`, `py-med-v1`).** `py-min-v1`: descoberta pura — só Typer, persistência em arquivo (JSON/MD), sem testes/evals/banco; SQLite/web/testes são gatilho de promoção para `py-med`. `py-med-v1` (cavalo de batalha do TPM): monorepo Python único `NiceGUI → core Python → SQLite (SQLModel)`, um processo/um deploy (Railway single service opcional), TDD/EDD leve, docs README+TODO+HANDOFF. Mantém o espírito incremental/experimental do min, mas já pronto para rodar via web. Versões ancoradas ao estável atual (jul/2026): Pydantic AI `>=2.9`, SQLModel `>=0.0.39`, NiceGUI `>=3.14`, Typer `>=0.26`, pytest `>=8.4`.
- **Ponteiros de templates atualizados.** Referências a `python.md`/`typescript.md` substituídas pela nova nomenclatura (`py-min`/`py-med`/`py-max`/`ts-max`, com nota descrevendo cada perfil e a regra da maior `-vN`) em `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `README.md` e no global `~/.claude/CLAUDE.md` (fora do repo).

## [2026-07-05]

### Changed

- **Alias `sonnet` → Sonnet 5.** Atualizada a tabela de mapeamento (alias → engine) em `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` e `README.md` de "Sonnet 4.6" para "Sonnet 5", após o lançamento do modelo. Mudança puramente documental: os 9 agentes já usam o alias `sonnet` e os scripts geradores resolvem o alias por engine — nenhum arquivo de agente ou gerador precisou mudar.

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
