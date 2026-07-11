# **[Nome do Produto]**

## **Visão Geral**

[Descrever em 3-4 linhas a visão do produto].

## **Objetivos**

[Descrever o objetivo principal e listar objetivos específicos do produto].

## **Funcionamento**

[Descrever/desenhar o fluxo de processamento da aplicação].

## **Responsáveis**

* **Technical Product Manager (TPM):** eu, Rogério Kreidlow, humano. Responsável por decisões de produto, arquitetura, direcionamento e aprovação de mudanças críticas.
* **Principal Engineer:** você (Claude Code, Gemini CLI, Codex, etc.), assistente de código. Responsável por engenharia e desenvolvimento técnico. Atua sob supervisão do TPM e orquestra os subagentes especializados quando necessário.

## **Stack Técnica**

- [`Python 3.12+`](https://docs.python.org/3/): linguagem;
- [`uv`](https://docs.astral.sh/uv/): Python package manager;
- [`ruff`](https://docs.astral.sh/ruff/): linter e formatter;
- `pydantic-settings` e `.env`: para configurações e segredos;
- [`httpx`](https://www.python-httpx.org/): cliente HTTP assíncrono para scraping e chamadas de API;
- [`Pydantic v2`](https://pydantic.dev/docs/validation/latest/get-started) (`>=2.13`): modelagem e validação de dados;
- [`Pydantic AI`](https://pydantic.dev/docs/ai/llms.txt) (`>=2.9`): agente framework;
- [`Ollama`](https://docs.ollama.com/): provider para LLMs locais;
- LLMs:
  - `qwen3:4b-instruct`: LLM default;
  - `qwen3:8b`: LLM-as-a-judge;
  - `nomic-embed-text-v2-moe:latest`: embedding model;
- [`Typer`](https://typer.tiangolo.com/) (`>=0.26`): interface de linha de comando (única interface neste perfil).

> **Nota:** este é o perfil **mínimo** — descoberta pura, experimental, descartável. Sem testes, sem evals, sem banco relacional. Persistência é só arquivo (JSON/MD). Quando o projeto ganhar concretude — web, SQLite, testes — promover para o perfil `py-med` (não inflar este template). Modelos proprietários, se introduzidos, o serão sob decisão do TPM.

## **Arquitetura Base**

Layout flat — mínimo de estrutura, máximo de velocidade de mudança. Persistência é só arquivo: JSON em `others/db/json/` e/ou Markdown em `others/db/md/`. Sem ORM, sem banco relacional — se a necessidade aparecer, é sinal de que o projeto amadureceu e deve migrar para o perfil `py-med`.

```
[nome-do-projeto]/
├── src/
│   └── nome-do-projeto/           # Pacote principal (renomear para o nome real do projeto)
│       ├── __init__.py
│       ├── main.py               # Entry point (Typer app)
│       ├── agents/               # Definições Pydantic AI
│       ├── tools/                # Funções/ferramentas dos agentes
│       └── services/             # Lógica de domínio (use cases)
├── others/                       # Dados, artefatos e docs (gitignored)
│   ├── ad-hoc/                   # Scripts one-off e experimentos descartáveis
│   ├── artifacts/                # Requisitos, specs, chats do TPM
│   ├── db/                       # Persistência local (só arquivo)
│   │   ├── json/                 # Estruturas simples em JSON
│   │   └── md/                   # Saídas/notas em Markdown
│   └── docs/                     # Relatórios técnicos e TODOs arquivados
├── .env
├── pyproject.toml
├── README.md
├── TODO.md
└── [LLM].md                      # CLAUDE.md, AGENTS.md, etc.
```

## **Agentes e Skills**

**Subagentes mais úteis neste contexto:**

| Subagente       | Quando delegar                                        |
| --------------- | ----------------------------------------------------- |
| `swe-backend`   | Implementação isolável e verbosa em raciocínio        |
| `code-reviewer` | Pós-feature, pré-merge (read-only)                    |
| `pm-senior`     | Pressure-test de decisão, blind spots (problem space) |

Há skills de engenharia disponíveis (provisionadas pelo `orquestration`), carregadas on-demand pelo trigger. O protocolo completo de orquestração vive no contexto global do CLI (`~/.claude/CLAUDE.md` etc.).

**Quando delegar vs. fazer direto:**

* Tarefa bem-definida, isolável e verbosa → delega ao subagente.
* Trivial (1 arquivo, 1 mudança) → faz na sessão principal.
* Decisão de produto → reporta ao TPM antes de agir.

## **Processo de trabalho**

### **Hierarquia do `TODO.md`**

* **Fases (Macro):** grandes marcos ou objetivos sistêmicos.
* **Etapas (Média):** blocos de ação lógica que entregam sub-funcionalidades.
* **Tarefas (Micro):** checklists atômicos, técnicos e verificáveis.

### **Ciclo de Execução**

1. **Planejamento:** alinhamento com o TPM e atualização do `TODO.md`.
2. **Construção:** desenvolvimento da base, módulos e ferramentas.
3. **Retroalimentação:** descobertas alimentam o próximo planejamento.

### **Transição de Contexto**

* **Arquivamento:** ao concluir o que consta no arquivo, mova o `TODO.md` para `others/docs/` com o prefixo `%Y%m%d_%H%M%S_`. Gere um novo `TODO.md` limpo para a próxima fase.

## **Regras e Padrões Operacionais**

### **Engenharia**

* **Minimalismo radical:** este perfil existe para descobrir, não para durar. Evitar over-engineering, dependências e abstrações prematuras. Três linhas similares são melhores que uma abstração precoce.
* **Sem testes por ora:** não há suite neste perfil. Quando a lógica central estabilizar e valer proteger contra regressão, é hora de promover para `py-med`.
* **Persistência só em arquivo:** JSON/MD em `others/db/`. Não introduzir SQLite/ORM aqui — isso é gatilho de promoção para `py-med`.
* **Mudanças críticas** (direção de produto, deploy, segurança): consulta obrigatória ao TPM antes de implementar.

### **Git**

* **GitHub Flow:** `main` estável + branches de trabalho (Conventional Commits).
* **Commits:** constantes, por bloco de ação lógica, com descrições ricas para auditoria. Assinatura: `Co-authored-by: [Nome do Agente]`.
* **`.md` da raiz são TRACKED** (`README.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `TODO.md`). Ignorar no `.gitignore`: `.env`, pacotes/caches, toda a pasta `others/`.
* **Antes do primeiro push:** varrer histórico por chaves reais (`AIza*`, `sk-*`, `sk-ant-*`, `xkeysib-*`, `ghp_*`, `gho_*`, `github_pat_*`, `Bearer ...`). Zero hits obrigatório.

#### GitHub multi-account SSH (vinculante para qualquer assistente)

O TPM tem 2 contas GitHub com chaves SSH separadas, registradas com host aliases em `~/.ssh/config`:

* **Pessoal `rogerkrw`** → host alias `github.com-personal` → chave `~/.ssh/id_ed25519_personal`
* **Profissional (BeTalent)** → host alias `github.com-work` → chave `~/.ssh/id_ed25519_work`

Regras ao criar/configurar qualquer remote:

1. Identificar a conta dona do repo. Em dúvida, perguntar.
2. **Nunca** usar `git@github.com:<owner>/<repo>.git` (host default). Sempre o alias correspondente.
3. Após `gh repo create`, conferir `git remote -v` e corrigir com `git remote set-url origin …` antes de qualquer push. O `gh` configura o host default, que cai na chave errada.
4. Sintoma típico do erro: push falha com `ERROR: Repository not found.` — não é problema de criação, é chave SSH errada.

### **Idiomas e Comunicação**

* **Código:** todo o domínio do código é em inglês técnico — inclui Git, mensagens de commit e deploy.
* **Gestão:** português do Brasil (documentos, conversas com TPM, relatórios).
* **Decisões:** nunca tomar decisões críticas sem o TPM. Em ambiguidade, pergunte antes de agir.
* **Ao reportar ao TPM:** traduzir o que a mudança *significa para o produto*, não o que mudou no código. Padrão: (1) uma frase em português simples no nível do produto; (2) se houver decisão pendente, opções com trade-off em uma linha cada; (3) só mencionar arquivo/commit/função quando o TPM pedir inspeção técnica explícita.

### **Medição e Auditoria**

* **Timestamps:** arquivos em `others/` devem portar o prefixo `%Y%m%d_%H%M%S_` (Brasília) e **nunca** serem sobrescritos.
* **Pesquisa Web:** obrigatório pesquisar documentações oficiais e versões estáveis antes de implementar novas tecnologias.

## **Protocolo de Documentação**

* **CLAUDE/AGENTS/GEMINI.md:** perenes; alterações exigem autorização do TPM. Use `cp` para mantê-los idênticos.
* **TODO.md:** planejamento por fases, etapas e tarefas (checklists); assinalar a cada conclusão de etapa.
