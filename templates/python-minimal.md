# **[Nome do Produto]**

## **Visão Geral**

[Descrever em 3-4 linhas a visão do produto].

## **Responsáveis**

* **Technical Product Manager (TPM):** eu, Rogério Kreidlow, humano. Responsável por decisões de produto, arquitetura, direcionamento e aprovação de mudanças críticas.
* **Principal Engineer:** você (Claude Code, Gemini CLI, Codex, etc.), assistente de código. Responsável por engenharia e desenvolvimento técnico. Atua sob supervisão do TPM e orquestra os subagentes especializados quando necessário.

## **Objetivos**

[Descrever o objetivo principal e listar objetivos específicos do produto].

## **Funcionamento**

[Descrever/desenhar o fluxo de processamento da aplicação].

## **Stack Técnica**

- [`Python 3.12+`](https://docs.python.org/3/): linguagem;
- [`uv`](https://docs.astral.sh/uv/): Python package manager;
- [`ruff`](https://docs.astral.sh/ruff/): linter e formatter;
- `pydantic-settings` e `.env`: para configurações e segredos;
- [`Pydantic v2`](https://pydantic.dev/docs/validation/latest/get-started): modelagem e validação de dados;
- [`Pydantic AI`](https://pydantic.dev/docs/ai/llms.txt): agente framework;
- [`Ollama`](https://docs.ollama.com/): provider para LLMs locais;
- LLMs:
  - `qwen3:4b-instruct`: LLM default;
  - `qwen3:8b`: LLM-as-a-judge;
  - `nomic-embed-text-v2-moe:latest`: embedding model;
- [`Typer`](https://typer.tiangolo.com/): interface de linha de comando;
- [`pytest`](https://docs.pytest.org/en/stable/): testes (quando a lógica estabilizar).

> **Nota:** Modelos proprietários, se introduzidos, o serão sob decisão do TPM.

## **Arquitetura Base**

Layout flat — mínimo de estrutura, máximo de velocidade de mudança. Persistence layer evolui conforme necessidade: arquivos JSON em `others/db/` → SQLite local → SQLModel (quando o projeto crescer).

```
[nome-do-projeto]/
├── src/
│   └── app/                      # Pacote principal (substitua por 'nome_do_projeto')
│       ├── __init__.py
│       ├── main.py               # Entry point (Typer app)
│       ├── agents/               # Definições Pydantic AI
│       ├── tools/                # Funções/ferramentas dos agentes
│       └── services/             # Lógica de domínio (use cases)
├── tests/                        # Testes — entram quando a lógica estabilizar
├── others/                       # Dados, artefatos e docs (gitignored)
│   ├── ad-hoc/                   # Scripts one-off e experimentos descartáveis
│   ├── artifacts/                # Requisitos, specs, chats do TPM
│   ├── db/                       # Persistência local
│   │   ├── json/                 # Fase experimental: arquivos JSON simples
│   │   └── sqlite/               # Fase seguinte: arquivo .db SQLite
│   ├── docs/                     # Relatórios técnicos e TODOs arquivados
│   └── evals/                    # Outputs das execuções de evals
├── .env
├── pyproject.toml
├── README.md
├── TODO.md
└── [LLM].md                      # CLAUDE.md, AGENTS.md, etc.
```

## **Agentes e Skills**

O **Principal Engineer** (sessão principal) orquestra subagentes e skills on-demand — todos provisionados pelo repositório [`orquestration`](https://github.com/rogerkrw/orquestration). Protocolo completo em `~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md` / `~/.gemini/GEMINI.md`.

**Subagentes mais úteis neste contexto:**

| Subagente       | Quando delegar                                        |
| --------------- | ----------------------------------------------------- |
| `swe-backend`   | Implementação isolável e verbosa em raciocínio        |
| `code-reviewer` | Pós-feature, pré-merge (read-only)                    |
| `qa-tester`     | Testes, evals, investigação de falhas                 |
| `devsecops`     | Deploy, secrets, auditoria de segurança               |
| `pm-senior`     | Pressure-test de decisão, blind spots (problem space) |

Skills transversais ativas em qualquer tarefa: `clean-code-principles`, `senior-swe-intuition`, `pydantic-ai`.

**Quando delegar vs. fazer direto:**

* Tarefa bem-definida, isolável e verbosa → delega ao subagente.
* Trivial (1 arquivo, 1 mudança) → faz na sessão principal.
* Decisão de produto → reporta ao TPM antes de agir.
* Pré-deploy → sempre passa por `devsecops` + `code-reviewer`.

## **Processo de trabalho**

### **Hierarquia do `TODO.md`**

* **Fases (Macro):** grandes marcos ou objetivos sistêmicos.
* **Etapas (Média):** blocos de ação lógica que entregam sub-funcionalidades.
* **Tarefas (Micro):** checklists atômicos, técnicos e verificáveis.

### **Ciclo de Execução**

1. **Planejamento:** alinhamento com o TPM e atualização do `TODO.md`.
2. **Construção:** desenvolvimento da base, módulos e ferramentas.
3. **Medição:** testes/evals quando a lógica estabilizar.
4. **Retroalimentação:** descobertas alimentam o próximo planejamento.

### **Transição de Contexto**

* **Arquivamento:** ao concluir o que consta no arquivo, mova o `TODO.md` para `others/docs/` com o prefixo `%Y%m%d_%H%M%S_`. Gere um novo `TODO.md` limpo para a próxima fase.

## **Regras e Padrões Operacionais**

### **Engenharia**

* **Minimalismo:** evitar over-engineering, dependências e abstrações prematuras. Três linhas similares são melhores que uma abstração precoce.
* **Testes:** não obrigatórios no início — entram quando a lógica central estabilizar. Quando entrar, usar `pytest` + `pytest-asyncio`.
* **Persistência:** começar com JSONs em `others/db/`; evoluir para SQLite e depois SQLModel apenas quando a necessidade for clara.
* **Mudanças críticas** (arquitetura, modelo, deploy, segurança): consulta obrigatória ao TPM antes de implementar.

### **Git**

* **GitHub Flow:** `main` estável + branches de trabalho (Conventional Commits).
* **Commits:** constantes, por bloco de ação lógica, com descrições ricas para auditoria. Assinatura: `Co-authored-by: [Nome do Agente]`.
* **`.md` da raiz são TRACKED** (`README.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `TODO.md`). Ignorar no `.gitignore`: `.env`, pacotes/caches, toda a pasta `others/`.
* **Antes do primeiro push:** varrer histórico por chaves reais (`sk-*`, `sk-ant-*`, `AIza*`, `ghp_*`, `Bearer ...`). Zero hits obrigatório.

### **Idiomas e Comunicação**

* **Código:** inglês técnico.
* **Gestão:** português do Brasil (docs, conversas com TPM, relatórios).
* **Ao reportar ao TPM:** traduzir o que a mudança *significa para o produto*, não o que mudou no código.

### **Medição e Auditoria**

* Arquivos em `others/` com prefixo `%Y%m%d_%H%M%S_` (Brasília), nunca sobrescritos.
* Resultados de evals em `others/evals/<timestamp>/` com os artefatos: `summary.json`, `cases.json`, `judge_results.json`, `records.jsonl`, `report.md`.

## **Protocolo de Documentação**

* **CLAUDE/AGENTS/GEMINI.md:** perenes; alterações exigem autorização do TPM.
* **TODO.md:** planejamento por fases, etapas e tarefas; assinalar a cada conclusão.
* **HANDOFF.md:** resumo de transição, atualizado sob demanda ao fim da sessão.
* **Relatórios:** gerar em `others/docs/` ao fim de cada etapa do `TODO.md`:

```
---
date: %Y%m%d_%H%M%S
author: [Claude Code, Gemini CLI, Codex etc.]
task_ref: [ID da tarefa no TODO.md]
---

# Report: [Título da Etapa/Fase]

## 1. Objetivo
## 2. Ações
## 3. Resultados
## 4. Próximos Passos
```
