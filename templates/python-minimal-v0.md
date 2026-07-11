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
- [`httpx`](https://www.python-httpx.org/): cliente HTTP assíncrono para scraping e chamadas de API;
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

Layout flat — mínimo de estrutura, máximo de velocidade de mudança. Persistence layer evolui conforme necessidade: arquivos JSON em `others/db/json/` → SQLite em `others/db/sqlite/` → SQLModel (quando o projeto crescer).

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
* Pré-deploy → sempre passa por `devsecops` (modo AUDIT) + `code-reviewer`.

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
* **Persistência:** começar com JSONs em `others/db/json/`; evoluir para SQLite em `others/db/sqlite/` e depois SQLModel apenas quando a necessidade for clara.
* **Mudanças críticas** (arquitetura, modelo, deploy, segurança): consulta obrigatória ao TPM antes de implementar.

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

* **Código:** inglês técnico (docstrings, variáveis, comentários).
* **Gestão:** português do Brasil (documentos, conversas com TPM, relatórios).
* **Decisões:** nunca tomar decisões críticas sem o TPM. Em ambiguidade, pergunte antes de agir.
* **Ao reportar ao TPM:** traduzir o que a mudança *significa para o produto*, não o que mudou no código. Padrão: (1) uma frase em português simples no nível do produto; (2) se houver decisão pendente, opções com trade-off em uma linha cada; (3) só mencionar arquivo/commit/função quando o TPM pedir inspeção técnica explícita.

### **Medição e Auditoria**

* **Timestamps:** arquivos em `others/` devem portar o prefixo `%Y%m%d_%H%M%S_` (Brasília) e **nunca** serem sobrescritos.
* **Pesquisa Web:** obrigatório pesquisar documentações oficiais e versões estáveis antes de implementar novas tecnologias.
* **Auditoria:** salvar resultados de evals em pastas nomeadas por timestamp `%Y%m%d_%H%M%S` em `others/evals/`; criar no código dos evals processo para gerar dentro dessas pastas os seguintes artefatos obrigatórios:
  * `summary.json`: métricas agregadas, configuração da run e performance de gates;
  * `cases.json`: resultados detalhados por caso, uso de tokens, latência e status dos gates;
  * `judge_results.json`: vereditos e justificativas do LLM-as-a-judge;
  * `records.jsonl`: log completo de turnos, inputs, outputs e estado dos slots;
  * `report.md`: resumo executivo consolidando latência, custo e qualidade.

## **Protocolo de Documentação**

* **CLAUDE/AGENTS/GEMINI.md:** perenes; alterações exigem autorização do TPM. Use `cp` para mantê-los idênticos.
* **TODO.md:** planejamento por fases, etapas e tarefas (checklists); assinalar a cada conclusão de etapa.
* **HANDOFF.md:** resumo enxuto de transição, atualizado apenas ao fim da sessão de trabalho, sob demanda.
* **FUTURE.md:** registro acumulativo de itens fora do escopo atual. Formato: título + parágrafo de contexto (o porquê do adiamento, o que seria necessário para viabilizar). Nunca promovido para `TODO.md` sem aprovação explícita do TPM. Não é lista de desejos — é memória de decisão.
* **Relatórios:** gerar em `others/docs/` ao fim de cada etapa do `TODO.md` antes do commit, neste formato:

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
