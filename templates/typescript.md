# **[Nome do Produto]**


## **Visão Geral**


[Descrever em 3-4 linhas a visão do produto].


## **Responsáveis**


* **Technical Product Manager (TPM):** eu, Rogério Kreidlow, humano. Responsável por decisões de produto, arquitetura, direcionamento e aprovação de mudanças críticas.
* **Principal Engineer:** você (Claude Code, Gemini CLI, Codex, etc.), assistente de código. Responsável por arquitetura detalhada, engenharia, ciência e desenvolvimento técnico. Atua sob supervisão do TPM e orquestra os subagentes especializados (ver seção *Agentes e Skills*).


## **Objetivos**


[Descrever o objetivo principal e listar objetivos específicos do produto].


## **Funcionamento**


[Descrever/desenhar o fluxo de processamento da aplicação].


## **Stack Técnica**


* [`TypeScript`](https://www.typescriptlang.org/docs/): linguagem;
* [`biome`](https://biomejs.dev/pt-br/guides/getting-started/): formatter, linter e demais utilidades;
* [`SvelteKit`](https://svelte.dev/docs/kit/introduction): web framework full-stack;
* [`shadcn-svelte`](https://www.shadcn-svelte.com/docs/installation): UI kit;
* [`Tailwind CSS v4`](https://tailwindcss.com/docs): utility-first CSS (config em CSS via `@theme`);
* [`Mastra`](https://mastra.ai/docs): AI/LLM framework (agents, workflows, tools, evals, observability);
* [`zod`](https://zod.dev/): validação de dados e contratos isomórficos;
* [`drizzle`](https://orm.drizzle.team/docs/overview): TypeScript ORM;
* `SQLite` (dev/staging) → `PostgreSQL` (produção): persistência relacional, com Drizzle abstraindo a transição;
* [`sqlite-vec`](https://github.com/asg017/sqlite-vec): extensão vetorial para SQLite, quando aplicável;
* [`Ollama`](https://docs.ollama.com/): provider para LLMs locais;
* LLMs (ajustar por projeto):
   * default/generator local: `qwen3:4b-instruct`;
   * LLM-as-a-judge local: `qwen3:8b`;
   * default/generator remoto: a definir (ex.: `gemini-3.1-flash-lite`, `gpt-5.4-mini`);
   * LLM-as-a-judge remoto: a definir (ex.: `gemini-3.1-pro-preview`, `gpt-5.4`);
   * embedding model: `nomic-embed-text-v2-moe:latest`;
* `pydantic-settings`-equivalent: variáveis de ambiente via `$env/dynamic/private` e `$env/static/public` do SvelteKit;
* Testes: `vitest` (unit + browser mode), `playwright` (E2E);
* Observabilidade: **Mastra Observability** (SaaS, padrão) — alternativas self-hosted (Arize Phoenix, Langfuse) reavaliáveis em maturidade.


> **Nota:** modelos proprietários, se introduzidos, o serão sob decisão do TPM. APIs externas (Google, OpenAI, Anthropic) exigem secrets no `.env` e justificativa de uso.

**Notas de adoção da stack (recorrentes em projetos TS do TPM):**

* **Persistência:** SQLite + Drizzle em dev/staging; PostgreSQL em produção. O Drizzle abstrai a transição — migrations são a única fonte de verdade de schema.
* **Vetorização e embeddings:** `sqlite-vec` disponível, mas **adiar** até volume justificar. Match determinístico + LLM cobre a maioria dos casos no MVP.
* **LLM local vs remoto:** preferir Ollama em desenvolvimento e evals (custo zero); LLM remoto em produção quando latência/qualidade exigirem. **LLM-as-a-judge sempre em modelo distinto do gerador.**
* **Mastra-first:** para qualquer uso de LLM (agentes, workflows, tools, scorers, evals, observability), priorizar primitivos do Mastra sobre soluções ad-hoc. Antes de implementar algo, consultar `mastra.ai/llms.txt`. Soluções ad-hoc só com justificativa explícita ao TPM.
* **Integrações Google/Workspace:** OAuth user-flow no MVP; Service Account + Domain-Wide Delegation como hardening de produção (registrar em `FUTURE.md`).


## **Arquitetura Base**


Layout SvelteKit padrão, adaptado para aplicações full-stack com camada de IA:

```
[nome-do-projeto]/
├── src/
│   ├── lib/                     # Core Business Logic (Domain)
│   │   ├── server/              # Lógica de servidor (privada — nunca chega ao client)
│   │   │   ├── ai/              # Módulos de IA (Mastra)
│   │   │   │   ├── agents/      # Agents com escopo definido
│   │   │   │   ├── tools/       # Tools tipadas (DB, APIs externas)
│   │   │   │   └── workflows/   # Grafos de estados / orquestrações
│   │   │   ├── db/              # Persistência (Drizzle)
│   │   │   │   ├── schema.ts    # Modelagem relacional
│   │   │   │   └── client.ts    # Instância do DB + extensões
│   │   │   ├── integrations/    # APIs externas (Google, Stripe, etc.)
│   │   │   └── services/        # Serviços de domínio (use cases)
│   │   ├── shared/              # DTOs, schemas Zod, tipos isomórficos
│   │   └── components/          # UI Components (Svelte + shadcn-svelte)
│   ├── routes/                  # Controller layer (SvelteKit Routes)
│   │   ├── api/                 # REST endpoints e webhooks
│   │   └── (app)/               # Rotas agrupadas por contexto
│   ├── hooks.server.ts          # Middleware global
│   └── app.d.ts                 # Tipagens globais
├── tests/                       # Testes de software (unit + E2E)
├── evals/                       # QA para componentes de IA (matcher, summarizer, judge)
├── data/                        # Persistência local e documentação técnica
│   ├── artifacts/               # Requisitos e especificações do TPM
│   ├── docs/                    # Relatórios técnicos e TODOs arquivados
│   └── evals/                   # Outputs das execuções de evals
├── static/                      # Assets estáticos
├── .env                         # Configurações de ambiente e secrets
├── biome.json                   # Linter + formatter
├── drizzle.config.ts            # Configuração de migrations
├── package.json
├── tsconfig.json
├── svelte.config.js
├── README.md
├── TODO.md
├── HANDOFF.md
├── FUTURE.md
├── FLOW.md
└── [LLM].md                     # CLAUDE.md, AGENTS.md, GEMINI.md
```


## **Agentes e Skills**


O **Principal Engineer** (sessão principal) orquestra **8 subagentes especializados** e consome **15 skills de engenharia** on-demand — todos provisionados pelo repositório [`orquestration`](https://github.com/rogerkrw/orquestration) e sincronizados em `~/.claude`, `~/.codex` e `~/.gemini`. São a **base padrão de todo projeto** do TPM; não reinvente o que já existe — consuma antes de implementar qualquer solução ad-hoc. O protocolo completo de orquestração está no contexto global do CLI (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md`).

**Subagentes disponíveis** (invocação via `@nome` ou auto-routing):

| Subagente        | Quando o SWE deve delegar                                              |
| ---------------- | ---------------------------------------------------------------------- |
| `swe-backend`    | Server-side: services, DB, integrações, workflows Mastra, endpoints   |
| `swe-frontend`   | UI: componentes Svelte, rotas, forms, state, fetch                     |
| `code-reviewer`  | Pós-feature, pré-merge, "o que pode dar errado aqui?" (read-only)      |
| `qa-tester`      | Vitest + Playwright + evals (Mastra), investigação de falhas           |
| `devsecops`      | Deploy, infra, secrets, auditoria de segurança, incidentes             |
| `ux-ui-designer` | Refino visual: ARIA, contraste, estados, Core Web Vitals, responsivo   |
| `ux-senior`      | Discovery, validação de premissa, fluxos, friction (problem space)     |
| `pm-senior`      | Pressure-test de decisão, blind spots, kill/build (challenger)         |


**Skills mais relevantes para o stack TS** (SvelteKit + Mastra + Drizzle):

| Quem usa                       | Skill                                            | Para que                                                                |
| ------------------------------ | ------------------------------------------------ | ----------------------------------------------------------------------- |
| `swe-backend`                  | `mastra`                                         | Agents, workflows, tools, scorers, evals, observability                 |
| `swe-frontend`                 | `sveltekit`                                      | Routing, SSR, load functions, form actions, hooks                       |
| `swe-frontend` / `ux-ui-designer` | `sveltekit-ui`                                | shadcn-svelte + Svelte 5 runes + Tailwind v4 + Formsnap/Superforms      |
| `qa-tester`                    | `qa-testing`                                     | Vitest (browser mode), Playwright, MSW, prevenção de flaky tests       |
| `devsecops`                    | `cybersecurity`                                  | OWASP Top 10, secrets, CSP, audit-checklist pré-deploy                  |
| `devsecops`                    | `railway-ops` / `hetzner-coolify-ops`            | Deploy conforme escolha de infra                                        |
| `swe-backend` / `devsecops`    | `logfire`                                        | Observabilidade alternativa quando Mastra Observability não couber      |
| `code-reviewer`                | `rigorous-code-review`, `senior-swe-intuition`   | Carregadas automaticamente                                              |
| Todos                          | `clean-code-principles`, `senior-swe-intuition`  | Transversais                                                            |


**Quando o Principal Engineer deve delegar:**

* Tarefa bem-definida, isolável e potencialmente verbosa em raciocínio → delega.
* Tarefa trivial (1 arquivo, 1 mudança) → faz direto na sessão principal.
* Decisão envolve direção de produto → reporta ao TPM antes (não delega ao `pm-senior` sem ouvir o TPM primeiro).
* Pré-deploy em produção → sempre passa por `devsecops` (modo AUDIT) e `code-reviewer`.

**Receitas de uso proativo dos agents:**

```text
DISCOVERY (problem space — antes de construir)
  ux-senior   → valida premissa, mapeia fluxos e friction do usuário
  pm-senior   → pressure-test da decisão, blind spots, kill/build
  ↓ TPM lê os dois reports e decide

DELIVERY (solution space — construção e entrega)
  swe-backend     → implementa server-side: services, DB, integrações, Mastra
  swe-frontend    → monta UI, rotas SvelteKit, componentes
  qa-tester       → testes + evals (antes ou junto à implementação)
  ux-ui-designer  → refino visual antes do merge
  code-reviewer   → revisa pré-merge (padrão: implementa → /rigorous-code-review → fixes)
  devsecops       → AUDIT pré-deploy; EXECUTE com confirmação do TPM
```

* **Skills transversais** (`clean-code-principles`, `senior-swe-intuition`): ativas em qualquer tarefa. Se o problema for de design ou julgamento — não só sintaxe — invocar explicitamente.
* **Skills de segurança** (`cybersecurity`, `llm-security`): carregam automaticamente no `devsecops` e `code-reviewer`; invocar explicitamente em qualquer feature que toque autenticação, PII ou LLM externo.


## **Processo de trabalho**


O desenvolvimento envolvendo AI/LLMs e Agentes é iterativo e não-linear. Não há "escopo" rigorosamente definido. Manter foco em descoberta, experimentação e melhoria contínua. Para isso, o Principal Engineer deve seguir este fluxo:


### **1. Hierarquia do `TODO.md`**


O `TODO.md` é o core da execução e deve respeitar três níveis:

* **Fases (Macro):** grandes marcos ou entregas de funcionalidade.
* **Etapas (Média):** sprints / blocos de ação lógica que entregam sub-funcionalidades.
* **Tarefas (Micro):** implementações atômicas, técnicas e verificáveis.


### **2. Ciclo de Execução**


Cada ciclo percorre obrigatoriamente:

1. **Planejamento:** definição de contratos (Zod) e schemas de banco antes de codar. Alinhamento de objetivos com o TPM.
2. **Construção:** implementação da lógica de negócio, integração de ferramentas de IA, UI.
3. **Medição (Evals + Testes):** vitest + playwright para software, evals Mastra para componentes de IA. Métricas de latência, tokens e qualidade.
4. **Retroalimentação:** descobertas na medição alimentam o próximo planejamento.


### **3. Transição de Contexto**


* **Arquivamento:** ao concluir o que consta no arquivo, mova o `TODO.md` para `data/docs/` com o prefixo `%Y%m%d_%H%M%S_`. Gere um novo `TODO.md` limpo para a próxima fase.
* **Maturidade:** com a base estável, o ciclo **Planejar → Construir → Medir** torna-se curto. A tarefa só é concluída após validação.


### **4. Estimativa de Tempo — régua de agente, não de humano**

Estimativas de prazo devem ser feitas em **tempo de agente**, não em tempo humano. Separar sempre as duas naturezas:

1. **Tempo de agente (código):** etapa bem-definida e isolável fecha em ~15–25 min de relógio, incluindo review e fixes. Não estimar em dias.
2. **Tempo não-comprimível** — rotular explicitamente à parte: build/CI, testes E2E (Playwright), OAuth e consentimento humano, **decisões de produto que dependem do TPM** (o gargalo real do relógio).

Ao fechar cada etapa, medir o tempo real (carimbar T₀ na delegação e T_fim no commit) e reportar a razão estimado/real, para calibrar o planejamento seguinte.


## **Regras e Padrões Operacionais**


### **Engenharia**


* **TDD/EDD:** obrigatório. Escrever testes e/ou evals antes da implementação para evitar regressões.
* **Type Safety:** TypeScript estrito (`"strict": true` no `tsconfig.json`); sem `any` implícito.
* **Schemas como contrato:** Zod no boundary (entrada/saída de API, validação de form, parse de input externo). Tipos derivados dos schemas, não duplicados.
* **Persistência:** migrations obrigatórias para qualquer alteração em `schema.ts`. Nunca editar tabelas direto via SQL no DB de prod.
* **Minimalismo:** evitar *over-engineering* e *overfitting*, dependências e comentários desnecessários.
* **Net-add zero:** nenhuma feature, tabela, rota ou componente novo entra sem deletar ou consolidar algo equivalente. Toda adição responde à pergunta "o que sai em troca?" — registrada no commit ou no doc-âncora da fase. Exceções exigem aprovação explícita do TPM.
* **Smoke manual obrigatório pré-merge de UI/rotas:** toda mudança em componentes de UI ou rotas SvelteKit exige passada manual no browser com dado real antes do merge — testes e type-check verdes não bastam.
* **Governo de mudanças:**
  * *Local* (ajuste de prompt, bug fix pequeno, estilo de componente): autonomia total; evidência: testes passando, sem regressão.
  * *Relevante* (afeta comportamento de usuário, métrica, custo, latência ou cobertura): evidência obrigatória — testes + eval antes/depois.
  * *Crítica* (arquitetura, modelo champion, schema de banco, deploy, segurança, fluxo OAuth): consulta obrigatória ao TPM antes de implementar; proposta com contexto, riscos e alternativas.
  * Em dúvida, classificar pelo maior impacto plausível e escalar cedo.


### **Git**


* **GitHub Flow:** `main` estável + branches de trabalho.
* **Commits:** no padrão Conventional Commits, constantes, por bloco de ação lógica (etapas do `TODO.md`), e com descrições ricas para auditoria.
   * **Assinatura:** adicionar ao fim da mensagem: `Co-authored-by: [Nome do Agente]`.
* **Ignorar:** ignorar no `.gitignore` `.env` e pastas geradas (`node_modules/`, `.svelte-kit/`, `build/`), toda a pasta `data/`. Markdowns da raiz (`README.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `TODO.md`, `HANDOFF.md`, `FUTURE.md`) são versionados.

#### GitHub multi-account SSH (vinculante para qualquer assistente)

O TPM tem 2 contas GitHub com chaves SSH separadas, registradas com host aliases em `~/.ssh/config`:

* **Pessoal `rogerkrw`** → host alias `github.com-personal` → chave `~/.ssh/id_ed25519_personal`
* **Profissional (BeTalent)** → host alias `github.com-work` → chave `~/.ssh/id_ed25519_work`

Regras ao criar/configurar qualquer remote para o TPM:

1. Identificar antes a conta dona do repo. Em dúvida, perguntar.
2. **Nunca** usar `git@github.com:<owner>/<repo>.git` (host default). Sempre o alias correspondente.
3. Após `gh repo create … --source=. --remote=origin --push`, **conferir** com `git remote -v` e trocar com `git remote set-url origin …` antes de qualquer `git push`. O `gh` configura o host default, que cai na chave errada quando a conta-dona não corresponde.
4. Sintoma típico do erro: `gh repo create` aparenta sucesso e mostra a URL, mas `git push` falha com `ERROR: Repository not found.` (não é problema de criação — é a chave SSH errada).


### **Idiomas e Comunicação**


* **Código:** Inglês técnico (docstrings, variáveis, comentários).
* **Gestão:** Português do Brasil (documentos, conversas com TPM, relatórios).
* **Decisões:** Nunca tomar decisões críticas sem o TPM. Em ambiguidade, pergunte antes de agir.
* **Clareza com o TPM (humano, não engenheiro de código):** ao reportar progresso, conclusões ou bugs, traduza o que cada mudança *significa para o produto*, não só o que mudou no código. Padrão: (1) uma frase em português simples no nível do produto; (2) se houver decisão pendente, opções com trade-off em uma linha cada; (3) só mencionar arquivo/commit/função quando o TPM pedir inspeção técnica explícita. Sinal de alerta: 3+ termos de jargão sem definir → reescrever em humano antes de enviar.


### **Medição e Auditoria**


* **Timestamps:** arquivos em `data/` devem portar o prefixo `%Y%m%d_%H%M%S_` (Brasília) e **nunca** serem sobrescritos.
* **Pesquisa Web:** obrigatório pesquisar documentações oficiais e versões estáveis antes de implementar novas tecnologias.
* **Baselines:** toda melhoria deve ser comparada com um baseline usando métricas explícitas.
* **Métricas:** elaborar e perseguir **Índice de Qualidade (%)**, rastreando sempre tokens (input/output/cached), latência e custo.
* **Auditoria:** salvar resultados de evals em pastas nomeadas por timestamp `%Y%m%d_%H%M%S` em `data/evals`; criar no código dos evals processo para gerar dentro dessas pastas os seguintes artefatos obrigatórios:
   * `summary.json`: métricas agregadas, configuração da run e performance de gates;
   * `cases.json`: resultados detalhados por caso, uso de tokens, latência e status dos gates;
   * `judge_results.json`: vereditos e justificativas do LLM-as-a-judge;
   * `records.jsonl`: log completo de turnos, inputs, outputs e estado dos slots;
   * `report.md`: resumo executivo consolidando latência, custo e qualidade.


### **LGPD / Privacy by Design** *(quando aplicável)*


Se o projeto lida com dados pessoais de residentes no Brasil:

1. **Nunca usar PII em texto plano em logs** — sempre IDs internos.
2. **Sanitizar dados antes de enviar para LLMs externos** — remover CPF, e-mail, telefone; substituir nomes por placeholders.
3. **Toda migration que adiciona coluna PII** deve incluir comentário `-- PII: [finalidade] [prazo_retencao]` e passar por revisão do TPM.
4. **Consentimento versionado:** persistir `policy_version + timestamp + ip + user_agent` na tabela de consents.
5. **Decisão automatizada por LLM (art. 20)** nunca dispara comunicação ao titular sem revisão humana documentada em log de auditoria.

Detalhar diretrizes específicas em `data/docs/` quando o projeto tocar PII.


## **Protocolo de Documentação**


* **CLAUDE/AGENTS/GEMINI.md:** documentos perenes. Alterações exigem autorização do TPM. Use `cp` para mantê-los idênticos.
* **TODO.md:** documento de planejamento por fases, etapas e tarefas (checklists); assinalar o checklist a cada conclusão de etapa.
* **HANDOFF.md:** resumo enxuto de transição, atualizado apenas ao fim da sessão de trabalho, sob demanda.
* **FUTURE.md:** registro acumulativo de itens fora do escopo atual. Formato: título + parágrafo de contexto (o porquê do adiamento, o que seria necessário para viabilizar). Nunca promovido para `TODO.md` sem aprovação explícita do TPM. Não é lista de desejos — é memória de decisão.
* **FLOW.md:** diagramas Mermaid do sistema — fluxo de navegação, arquitetura, ERD, integrações. Atualizado **apenas por comando explícito do TPM**, não a cada entrega. Registra a última data de atualização e o commit de referência no cabeçalho. Pode ter múltiplas seções (visão alvo, estado atual, schema do banco, subsistemas).
* **Relatórios:** gerar em `data/docs/` ao fim de cada etapa do `TODO.md` antes do commit, neste formato:


```
---
date: %Y%m%d_%H%M%S
author: [Claude Code, Gemini CLI, Codex etc.]
task_ref: [Link ou ID da tarefa no TODO.md]
---


# Report: [Título da Etapa/Fase]


## 1. Objetivo
[Breve explicação do porquê a etapa foi realizada e qual problema resolve].


## 2. Ações
[Listagem técnica das implementações, refatorações e novos arquivos].


## 3. Resultados
[Evidências de funcionamento, logs de execução, métricas de evals (Mastra) e observações sobre o comportamento].


## 4. Próximos Passos
[Próximas ações, seja prosseguir em melhorias, seja corrigir problemas analisados na etapa].
```
