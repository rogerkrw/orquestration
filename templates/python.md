# **[Nome do Produto]**


## **Visão Geral**


[Descrever em 3-4 linhas a visão do produto].


## **Responsáveis**


* **Technical PM (TPM):** eu, Rogério Kreidlow, humano. Responsável por decisões de produto, arquitetura, direcionamento e aprovação de mudanças críticas.
* **Senior SWE:** você (Claude Code, Gemini CLI, Codex, etc.), assistente de código. Responsável por arquitetura detalhada, engenharia, ciência e desenvolvimento técnico. Atua sob supervisão do TPM e orquestra os subagentes especializados (ver seção *Agentes e Skills*).


## **Objetivos**


[Descrever o objetivo principal e listar objetivos específicos do produto].


## **Funcionamento**


[Descrever/desenhar o fluxo de processamento da aplicação].


## **Stack Técnica**


- [`Python 3.12+`](https://docs.python.org/3/): linguagem;
- [`uv`](https://docs.astral.sh/uv/): Python package manager;
- [`ruff`](https://docs.astral.sh/ruff/): linter e formatter;
- `pydantic-settings` e `.env`: para configurações e segredos, respectivamente;
- [`pytest`](https://docs.pytest.org/en/stable/): testes determinísticos;
- [`httpx`](https://www.python-httpx.org/): cliente HTTP assíncrono para scraping e chamadas de API;
- [`Pydantic v2`](https://pydantic.dev/docs/validation/latest/get-started): modelagem e validação de dados;
- [`Pydantic AI`](https://pydantic.dev/docs/ai/llms.txt)`: agente framework, do qual usaremos tudo que for conveniente, como agents, pydantic graph, providers, tools, pydantic evals e outros recursos;
- [`Pydantic Logfire`](https://pydantic.dev/docs/logfire/get-started/)`: plataforma de observabilidade;
- [`Ollama`](https://docs.ollama.com/): provider para LLMs locais;
- LLMs:
 - `qwen3:4b-instruct`: LLM default;
 - `qwen3:8b`: LLM-as-a-judge;
 - `nomic-embed-text-v2-moe:latest`: embedding model;
- [`Chainlit`](https://docs.chainlit.io/get-started/overview): user interface chat.


> **Nota:** Modelos proprietários, se introduzidos, o serão sob decisão do Technical AI PM. O projeto vindo a ganhar separação de backend (api) e frontend (ui), stack e arquitetura base serão alterados por orientação do Technical AI PM.


## **Arquitetura Base**


Usamos layout `src` para a arquitetura do projeto. Adaptar a sugestão à seguir para o que usaremos de fato.


```
[nome-do-projeto]/
├── src/
│   └── app/                     # Pacote principal (substitua por 'nome_do_projeto')
│       ├── __init__.py
│       ├── main.py              # Entry point
│       ├── agents/              # Definições Pydantic AI
│       │   ├── __init__.py
│       │   └── research.py
│       ├── tools/               # Funções/ferramentas dos agentes
│       │   ├── __init__.py
│       │   └── db_tools.py
│       ├── database/            # Lógica de conexão SQLite/SQLModel
│       │   └── session.py
│       └── ui/                  # Código frontend
│           └── app_ui.py
├── tests/                       # Testes determinísticos
│   ├── unit/
│   └── integration/
│   └── evals/                   # Benchmarks e avaliações de LLM
├── data/                        # Persistência e arquivos
│   ├── artifacts/               # Artefatos do Technical AI PM
│   ├── artifacts/               # Artefatos do Technical AI PM
│   ├── docs/                    # RAG docs ou memória técnica
│   └── evals/                   # Outputs de métricas
├── .env                         # Chaves de API e configs sensíveis
├── pyproject.toml               # Configuração moderna (uv, poetry ou hatch)
├── README.md
├── TODO.md
├── HANDOFF.md
└── [LLM].md                     # CLAUDE.md, AGENTS.md, etc.
```


## **Agentes e Skills**


O **Senior SWE** (sessão principal) orquestra **8 subagentes especializados** e consome **skills** (conhecimento técnico) on-demand. Esta seção indica o pareamento contextual para este projeto; o protocolo geral está no contexto global do CLI (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md`).

**Subagentes disponíveis** (invocação via `@nome` ou auto-routing):

| Subagente        | Quando o SWE deve delegar                                              |
| ---------------- | ---------------------------------------------------------------------- |
| `swe-backend`    | Implementação de API, modelos, lógica de negócio, integrações, jobs    |
| `swe-frontend`   | UI: componentes, rotas, forms, state, fetch                            |
| `code-reviewer`  | Pós-feature, pré-merge, "o que pode dar errado aqui?" (read-only)      |
| `qa-tester`      | Testes faltantes, suite, investigação de falhas, evals                 |
| `devsecops`      | Deploy, infra, secrets, auditoria de segurança, incidentes             |
| `ux-ui-designer` | Refino visual: ARIA, contraste, estados, Core Web Vitals, responsivo   |
| `ux-senior`      | Discovery, validação de premissa, fluxos, friction (problem space)     |
| `pm-senior`      | Pressure-test de decisão, blind spots, kill/build (challenger)         |


**Skills mais relevantes para o stack deste projeto** (Python + Pydantic AI + Chainlit):

| Quem usa                       | Skill                                            | Para que                                                                |
| ------------------------------ | ------------------------------------------------ | ----------------------------------------------------------------------- |
| `swe-backend`                  | `pydantic-ai`                                    | Agentes, tools, structured output, streaming, testing                   |
| `swe-backend`                  | `fastapi`                                        | Quando o projeto evoluir para API separada                              |
| `swe-backend`                  | `logfire`                                        | Observabilidade (já no stack base)                                      |
| `swe-frontend` / `swe-backend` | `python-ui`                                      | Chainlit (⚠️ ler status de segurança), alternativas NiceGUI/Gradio      |
| `qa-tester`                    | `qa-testing`                                     | Pytest + `pytest-asyncio` + Pydantic AI `TestModel` (essencial p/ evals)|
| `devsecops`                    | `cybersecurity`                                  | OWASP Top 10, secrets, audit-checklist pré-deploy                       |
| `devsecops`                    | `railway-ops` / `hetzner-coolify-ops`            | Deploy conforme escolha de infra                                        |
| `code-reviewer`                | `rigorous-code-review`, `senior-swe-intuition`   | Carregadas automaticamente                                              |
| Todos                          | `clean-code-principles`, `senior-swe-intuition`  | Transversais                                                            |


**Quando o Senior SWE deve delegar:**

* Tarefa bem-definida, isolável e potencialmente verbosa em raciocínio → delega.
* Tarefa trivial (1 arquivo, 1 mudança) → faz direto na sessão principal.
* Decisão envolve direção de produto → reporta ao TPM antes.
* Pré-deploy em produção → sempre passa por `devsecops` (modo AUDIT) e `code-reviewer`.


## **Processo de trabalho**


O desenvolvimento envolvendo AI/LLMs e Agentes é iterativo e não-linear. Não há "escopo" rigorosamente definido. Manter foco em descoberta, experimentação e melhoria contínua. Para isso, o Senior AI Engineer deve seguir este fluxo:


### **1. Hierarquia do `TODO.md`


O `TODO.md` é o core da execução e deve respeitar três níveis:


* **Fases (Macro):** Grandes marcos ou objetivos sistêmicos.
* **Etapas (Média):** Blocos de ação lógica que entregam sub-funcionalidades.
* **Tarefas (Micro):** Checklists atômicos, técnicos e verificáveis.


### **2. Ciclo de Execução**


Cada ciclo percorre obrigatoriamente:


1. **Planejamento:** alinhamento de objetivos da fase com o Technical AI PM e atualização do `TODO.md`.
2. **Construção:** desenvolvimento da base, módulos e ferramentas (predomina no início).
3. **Medição (Evals):** testes de qualidade, de performance, estatísticos, medição de latência e tokens etc. (predomina na maturidade).
4. **Retroalimentação:** descobertas na Medição alimentam o próximo Planejamento.


### **3. Transição de Contexto**


* **Arquivamento:** ao concluir o que consta no arquivo, mova o `TODO.md` para `data/docs/` com o prefixo `%Y%m%d_%H%M%S_`. Gere um novo `TODO.md` limpo para a próxima fase.
* **Maturidade:** com a base estável, o ciclo **Planejar -> Construir -> Medir** torna-se curto. A tarefa só é concluída após validação científica.


## **Regras e Padrões Operacionais**


### **Engenharia**


* **TDD/EDD:** obrigatório. Escrever testes e/ou evals antes da implementação para evitar regressões.
* **Minimalismo:** evitar *over-engineering* e *overfitting*, dependências e comentários desnecessários.


### **Git**


* **GitHub Flow:** `main` estável + branches de trabalho (Conventional Commits).
* **Commits:** constantes, por bloco de ação lógica (etapas do `TODO.md`), e com descrições ricas para auditoria.
   * **Assinatura:** adicionar ao fim da mensagem: `Co-authored-by: [Nome do Agente]`.
* **Ignorar:** ignorar no `.gitignore` `.env` e pastas de pacotes/geradas por ferramentas, toda a pasta `data/`, arquivos `.md` da raiz, exceto `README.md`. 


### **Idiomas e Comunicação**


* **Código:** Inglês técnico (docstrings, variáveis, comentários).
* **Gestão:** Português do Brasil (documentos, conversas com TPM, relatórios).
* **Decisões:** Nunca tomar decisões críticas sem o TPM. Em ambiguidade, pergunte antes de agir.


### **Medição e Auditoria**


* **Timestamps:** Arquivos em `data/` devem portar o prefixo `%Y%m%d_%H%M%S_` (Brasília) e **nunca** serem sobrescritos.
* **Pesquisa Web:** Obrigatório pesquisar documentações oficiais e versões estáveis antes de implementar novas tecnologias.
* **Baselines:** Toda melhoria deve ser comparada com um baseline usando métricas explícitas.
* **Métricas:** elaborar e perseguir **Índice de Qualidade (%)**, rastreando sempre tokens (input/output/cached), latência e custo.
* **Auditoria:** salvar resultados de evals em pastas nomeadas por timestamp `%Y%m%d_%H%M%S` em `data/evals`; criar no código dos evals processo para gerar dentro dessas pastas os seguintes artefatos obrigatórios: 
  * `summary.json`: métricas agregadas, configuração da run e performance de gates;
  * `cases.json`: resultados detalhados por caso, uso de tokens, latência e status dos gates;
  * `judge_results.json`: vereditos e justificativas do LLM-as-a-judge;
  * `records.jsonl`: log completo de turnos, inputs, outputs e estado dos slots;
  * `report.md`: resumo executivo consolidando latência, custo e qualidade.


## **Protocolo de Documentação**


* **CLAUDE/AGENTS/GEMINI.md:** Documentos perenes. Alterações exigem autorização do TPM. Use `cp` para mantê-los idênticos.
* **TODO.md:** documento de planejamento por fases, etapas e tarefas (checklists); assinalar o checklist a cada conclusão de etapa.
* **HANDOFF.md:** resumo enxuto de transição, atualizado apenas ao fim da sessão de trabalho, sob demanda.
* **FUTURE.md:** documentação de itens futuros, ainda não planejados; anotar contítulo e um parágrafo de comentário para memória.
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
[Evidências de funcionamento, logs de execução, métricas de evals (DeepEval/Arize) e observações sobre o comportamento].


## 4. Próximos Passos
[Próximas ações, seja prosseguir em melhorias, seja corrigir problemas analisados na etapa].
```

