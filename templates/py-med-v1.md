# **[Nome do Produto]**

## **Responsáveis**

* **Technical Product Manager (TPM):** eu, Rogério Kreidlow, humano. Responsável por decisões de produto, arquitetura, direcionamento e aprovação de mudanças críticas.
* **Principal Engineer:** você (Claude Code, Gemini CLI, Codex, etc.), engenheiro de software. Responsável por arquitetura detalhada, engenharia e desenvolvimento técnico. Atua sob supervisão do TPM e orquestra os subagentes especializados com as skills disponíveis quando necessário.

## **Visão Geral**

[Descrever em 4-5 linhas a visão do produto].

## **Objetivos**

[Descrever, sucinto, o objetivo principal e listar objetivos específicos do produto].

## **Funcionamento**

[Descrever/desenhar, sucinto, o fluxo de processamento da aplicação].

## **Arquitetura lógica**

```
NiceGUI (UI web)
   ↓  chamada Python direta (mesmo processo)
serviços / core Python (lógica de domínio)
   ↓
SQLite (via SQLModel)
```

## **Stack Técnica**

- [`Python 3.14+`](https://docs.python.org/3/): linguagem;
- [`uv`](https://docs.astral.sh/uv/): Python package manager;
- [`ruff`](https://docs.astral.sh/ruff/): linter e formatter;
- `pydantic-settings` e `.env`: para configurações e segredos;
- [`httpx`](https://www.python-httpx.org/): cliente HTTP assíncrono para scraping e chamadas de API;
- [`Pydantic v2`](https://pydantic.dev/docs/validation/latest/get-started) (`>=2.13`): modelagem e validação de dados;
- [`Pydantic AI`](https://pydantic.dev/docs/ai/llms.txt) (`>=2.9`): agente framework;
- [`SQLModel`](https://sqlmodel.tiangolo.com/) (`>=0.0.39`) sobre **SQLite**: ORM + Pydantic num objeto só — persistência primária. JSON/MD servem apenas como **saídas/exports** do SQLite, não como fonte de verdade;
- [`Ollama`](https://docs.ollama.com/): provider para LLMs locais;
- LLMs:
  - `qwen3:4b-instruct`: LLM default;
  - `qwen3:8b`: LLM-as-a-judge;
  - `nomic-embed-text-v2-moe:latest`: embedding model;
- **Interfaces:**
  - [`Typer`](https://typer.tiangolo.com/) (`>=0.26`): CLI (scripts, comandos de manutenção, entrada de dados);
  - [`NiceGUI`](https://nicegui.io/) (`>=3.14`): UI web padrão (chama o core Python direto). Alternativas por projeto: [`Chainlit`](https://docs.chainlit.io/) quando a interface for essencialmente chat; [`Gradio`](https://www.gradio.app/) para demos rápidas de ML;
- [`pytest`](https://docs.pytest.org/en/stable/) (`>=8.4`) + [`pytest-asyncio`](https://pytest-asyncio.readthedocs.io/) (`>=1.2`): testes (TDD/EDD, ver *Regras*).

> **Nota:** LLMs proprietários, se introduzidos, o serão sob decisão do TPM. O projeto nasce local e pode permanecer local, mas o TPM pode decidir por publicá-lo no Railway, para uso via web.

## **Arquitetura Base**

Monorepo flat: um único pacote com um submódulo `ui/` para a camada NiceGUI dentro dele — um processo só, um deploy só.

```
[nome-do-projeto]/
├── src/
│   └── nome-do-projeto/           # Pacote principal (renomear para o nome real do projeto)
│       ├── __init__.py
│       ├── main.py               # Entry point (Typer app)
│       ├── web.py                # Entry point da UI web (NiceGUI, ui.run)
│       ├── config.py             # pydantic-settings
│       ├── agents/               # Definições Pydantic AI
│       ├── tools/                # Funções/ferramentas dos agentes
│       ├── services/             # Lógica de domínio (use cases)
│       ├── database/             # Persistência (SQLModel + engine SQLite)
│       └── ui/                   # Camada NiceGUI (páginas, componentes)
├── tests/                        # Testes determinísticos (pytest)
│   ├── unit/
│   └── integration/
├── evals/                        # Evals dos LLMs (Pydantic AI Evals)
├── oth/                          # Dados, artefatos, docs etc. (gitignored)
│   ├── artifacts/                # Requisitos, specs, chats do TPM
│   ├── docs/                     # Memória do projeto, TODOs arquivados
│   ├── db/                       # SQLite local
│   ├── evals/                    # Outputs de evals (quando houver)
│   ├── logs/                     # Logs (se necessários)
│   ├── inputs/                   # Entradas de dados processáveis (.csv, ,json, .md etc.)
│   ├── outputs/                  # Saídas de dados processados (.csv, ,json, .md etc.)
│   └── scripts/                  # Scripts ad-hoc/one-off e experimentos
├── .env
├── pyproject.toml
├── Procfile / railway.toml       # Config de deploy (Railway, quando solicitado pelo TPM)
├── README.md
├── TODO.md
├── HANDOFF.md
└── [LLM].md                      # CLAUDE.md, AGENTS.md, etc.
```

## **Agentes e Skills**

**Subagentes mais úteis neste contexto:**

| Subagente        | Quando delegar                                          |
| ---------------- | ------------------------------------------------------- |
| `swe-backend`    | Services, modelos SQLModel, agentes, integrações        |
| `swe-frontend`   | UI NiceGUI: páginas, componentes, estado, interações    |
| `code-reviewer`  | Pós-feature, pré-merge (read-only)                      |
| `qa-tester`      | Testes, evals, investigação de falhas                   |
| `devsecops`      | Deploy Railway, secrets, volume, auditoria de segurança |
| `pm-senior`      | Pressure-test de decisão, blind spots (problem space)   |

Há skills disponíveis. O protocolo completo de orquestração vive no contexto global (`~/.claude/CLAUDE.md`).

**Quando delegar vs. fazer direto:**

* Tarefa bem-definida, isolável e verbosa → delega ao subagente.
* Trivial (1 arquivo, 1 mudança) → faz na sessão principal.
* Decisão de produto → reporta ao TPM antes de agir.
* Pré-deploy → sempre passa por `devsecops` (modo AUDIT) + `code-reviewer`.

## **Processo de trabalho**

### **Hierarquia do `TODO.md`**

* **Fases (Macro):** grandes marcos ou objetivos sistêmicos.
* **Etapas (Média):** blocos de ação lógica que entregam sub-funcionalidades.
* **Tarefas (Micro):** checklists atômicos, técnicos e verificáveis.

### **Ciclo de Execução**

1. **Planejamento:** alinhamento com o TPM e atualização do `TODO.md`.
2. **Construção:** desenvolvimento da base, módulos, ferramentas e UI.
3. **Medição:** testes (pytest) sempre; evals quando o comportamento de LLM precisar ser validado.
4. **Retroalimentação:** descobertas alimentam o próximo planejamento.

### **Transição de Contexto**

* **Arquivamento:** ao concluir o que consta no arquivo, mova o `TODO.md` para `oth/docs/` com o prefixo `%Y%m%d_%H%M%S_`. Gere um novo `TODO.md` limpo para a próxima fase.

## **Regras e Padrões Operacionais**

### **Engenharia**

* **TDD/EDD leve:** teste antes da implementação para lógica que vale proteger contra regressão. Evals entram quando o comportamento de LLM/agente for o que precisa ser validado.
* **Minimalismo:** evitar over-engineering, dependências e abstrações prematuras.
* **Persistência:** SQLite via SQLModel; JSON/MD eventualmente para exportações.
* **Mudanças críticas** (arquitetura, modelo, schema de banco, deploy, segurança): consultar TPM antes de implementar.

### **Git**

* **GitHub Flow:** `main` estável + branches de trabalho (Conventional Commits).
* **Commits:** constantes, por bloco de ação lógica, com descrições ricas para auditoria. Assinatura: `Co-authored-by: [Nome do Agente e Modelo do LLM]`.
* **`.md` da raiz são TRACKED** (`README.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `TODO.md`, `HANDOFF.md`). Ignorar no `.gitignore`: `.env`, pacotes/caches, toda a pasta `oth/`.
* **Antes do primeiro push:** varrer histórico por chaves reais (`AIza*`, `sk-*`, `sk-ant-*`, `xkeysib-*`, `ghp_*`, `gho_*`, `github_pat_*`, `Bearer ...`). Zero hits obrigatório.

#### GitHub multi-account SSH (vinculante para qualquer assistente)

O TPM tem 2 contas GitHub com chaves SSH separadas, registradas com host aliases em `~/.ssh/config`:

* **Pessoal `rogerkrw`** → host alias `github.com-personal` → chave `~/.ssh/id_ed25519_personal`
* **Profissional (BeTalent)** → host alias `github.com-work` → chave `~/.ssh/id_ed25519_work`

**Regras ao criar/configurar qualquer remote:**

1. Identificar a conta dona do repo. Em dúvida, perguntar.
2. **Nunca** usar `git@github.com:<owner>/<repo>.git` (host default). Sempre o alias correspondente.
3. Após `gh repo create`, conferir `git remote -v` e corrigir com `git remote set-url origin …` antes de qualquer push. O `gh` configura o host default, que cai na chave errada.
4. Sintoma típico do erro: push falha com `ERROR: Repository not found.` — não é problema de criação, é chave SSH errada.

### **Idiomas e Comunicação**

* **Código:** todo o domínio do código é em inglês técnico — inclui Git, mensagens de commit, deploy etc.
* **Gestão:** português do Brasil (documentos, conversas com TPM, relatórios).
* **Decisões:** nunca tomar decisões críticas sem o TPM. Em ambiguidade, pergunte antes de agir.
* **Ao reportar ao TPM:** comunicar em "língua de gente", de maneira fácil, sucinta e simples de ser entendida, sem "tecniquês" e abstrações crípticas/obscuras.

### **Medição e Auditoria**

* **Timestamps:** arquivos em `oth/` devem portar o prefixo `%Y%m%d_%H%M%S_` (Brasília) e **nunca** serem sobrescritos.
* **Pesquisa Web:** obrigatório pesquisar documentações oficiais e versões estáveis antes de implementar novas tecnologias.
* **Baselines:** quando medir qualidade de LLM/agente, comparar contra um baseline com métrica explícita (mesmo que simples). 
* **Telemetria:** rastrear tokens (input, cached, output), latência e custo estimado do(s) LLM(s) em uso.

## **Protocolo de Documentação**

* **CLAUDE/AGENTS/GEMINI.md:** perenes; alterações exigem autorização do TPM. Use `cp` para mantê-los idênticos.
* **TODO.md:** planejamento por fases, etapas e tarefas (checklists); assinalar a cada conclusão de etapa.
* **HANDOFF.md:** resumo enxuto de transição, atualizado ao fim da sessão de trabalho, sempre a pedido/por ordem do TPM. Útil para retomar contexto.
* **Opcionais sob demanda:** `FUTURE.md` (itens fora do escopo atual, memória de decisão) e `FLOW.md` (diagramas Mermaid) entram só quando o projeto crescer e o TPM pedir.
* **Relatórios:** gerar em `oth/docs/` ao fim de cada etapa relevante do `TODO.md` antes do commit, neste formato:

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
[Evidências de funcionamento, logs de execução, métricas de evals e observações sobre o comportamento].

## 4. Próximos Passos
[Próximas ações, seja prosseguir em melhorias, seja corrigir problemas analisados na etapa].
```