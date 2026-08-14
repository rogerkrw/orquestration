# **[Nome do Produto]**

<!--
BASE — parte comum a todo projeto do TPM, independente de stack e perfil.
No bootstrap de um projeto novo, concatenar este arquivo com o bloco de stack
(`py.md` ou `ts.md`, seção do perfil escolhido) e salvar o resultado como
CLAUDE.md / AGENTS.md / GEMINI.md do projeto. Remover estes comentários.
Ordem: cabeçalho + Responsáveis + Visão/Objetivos/Funcionamento (aqui)
→ Stack Técnica + Arquitetura Base + Agentes e Skills (do arquivo de stack)
→ Processo + Regras + Protocolo de Documentação (aqui).
-->

> Este arquivo descreve **como** trabalhar neste projeto. O **que** construir vive no `TODO.md`.
> Complementa o contexto global do CLI (`~/.claude/CLAUDE.md`); em conflito, este prevalece para este projeto.
> Precedência geral: **global < este arquivo < o código real.** Onde o código diverge do que está escrito aqui, o código é o fato — corrigir o doc, não o código.

## **Por onde começar**

| Arquivo | Para quê |
| --- | --- |
| `TODO.md` | Onde o projeto está e o que falta fazer |
| `HANDOFF.md` | Onde a sessão parou e por onde retomar |
| este arquivo | Como construir: stack, estrutura, regras |

## **Responsáveis**

* **Technical Product Manager (TPM):** Rogério Kreidlow, humano. Decisões de produto, arquitetura, direcionamento e aprovação de mudanças críticas.
* **Principal Engineer:** você (Claude Code, Codex, Antigravity CLI etc.). Arquitetura detalhada, engenharia e desenvolvimento técnico, sob supervisão do TPM. Orquestra os subagentes especializados.

## **Visão Geral**

[Descrever em 3-5 linhas a visão do produto].

## **Objetivos**

[Descrever, sucinto, o objetivo principal e listar os objetivos específicos].

## **Funcionamento**

[Descrever/desenhar, sucinto, o fluxo de processamento da aplicação].

## **Processo de trabalho**

Desenvolvimento com LLMs e agentes é iterativo e não-linear; o escopo não fica rigorosamente definido. O foco é descoberta, experimentação e melhoria contínua.

### **Hierarquia do `TODO.md`**

**Fase** (marco) → **Etapa** (bloco lógico) → **Tarefa** (checklist atômico e verificável).

### **Ciclo de Execução**

1. **Planejar:** alinhar com o TPM, atualizar o `TODO.md`, definir contratos antes de codar.
2. **Construir:** base, módulos, ferramentas, UI.
3. **Medir:** testes quando houver suite; evals quando o comportamento de LLM for o que precisa ser validado.
4. **Retroalimentar:** as descobertas da medição entram no próximo planejamento.

### **Estimativa de tempo**

Medida em tempo de agente: etapa bem-definida e isolável fecha em ~15–25 min de relógio, incluindo review e fixes. O tempo não-comprimível vai rotulado à parte — runs de eval, build/CI, testes E2E, OAuth, e decisões de produto que dependem do TPM, que costumam dominar o relógio.

## **Delegação a subagentes**

* Tarefa bem-definida, isolável e verbosa em raciocínio → delega.
* Trivial (1 arquivo, 1 mudança) → faz na sessão principal.
* Direção de produto → reporta ao TPM antes.
* Pré-deploy → passa por `devsecops` (AUDIT) e `code-reviewer`.

Subagentes e skills são provisionados pelo repositório [`orquestration`](https://github.com/rogerkrw/orquestration) e sincronizados nos CLIs; o protocolo completo vive no contexto global. O arquivo de stack lista os mais relevantes para este projeto.

## **Regras e Padrões Operacionais**

### **Autonomia e consulta ao TPM**

* **Decidir é o padrão.** Consultar quando errar for caro e irreversível: schema, autenticação, produção, dinheiro, dado real de usuário. Nome de rótulo, formato de tela, ordem de etapa, escolha de biblioteca — decidir, registrar em uma linha no `TODO.md` e seguir. Reverter custa menos que travar.
* **Uma pergunta por vez, quando ela surge.** Lista de perguntas no fim de um relatório transfere ao TPM o trabalho de priorizar as dúvidas do agente.
* **Pergunta bloqueante é exceção.** Se a dúvida não impede o próximo passo, executar sob premissa declarada e registrar a premissa.
* **Sinalizar uma vez, não vetar.** Pedido que cruza uma linha (escopo, custo, risco) se registra uma vez, com o custo estimado, e a decisão fica com o TPM.

### **Engenharia**

* **Minimalismo:** evitar over-engineering, dependências e abstrações prematuras. Três linhas similares custam menos que uma abstração precoce.
* **Net-add zero (heurística):** ao adicionar feature, tabela, endpoint ou módulo, perguntar o que sai ou se consolida em troca. Não é um gate — quando a evolução do produto pede um add limpo, adicionar e anotar a dívida de consolidação no commit.
* **Parametrizar em vez de fixar:** conteúdo (textos, rótulos, listas) e constantes (limites, faixas, tetos) ficam num ponto só, separados da lógica que os consome. Regra de negócio atrás de função pura. Tabela de dados em vez de `if` encadeado quando a regra é "para cada faixa, um resultado".
  * **Limite:** não criar registry, factory ou camada de configuração genérica antes do segundo caso de uso real. A abstração custa mais que a duplicação que evitaria.
* **Governo de mudanças:**
  * *Local* (ajuste de prompt, bug fix pequeno, tuning): autonomia total; evidência é o teste verde.
  * *Relevante* (afeta comportamento, métrica, custo, latência ou cobertura): evidência antes e depois.
  * *Crítica* (arquitetura, modelo champion, schema, contratos, deploy, segurança): consultar o TPM antes, com contexto, riscos e alternativas.
  * Em dúvida, classificar pelo maior impacto plausível.

### **Verificação — o gate é o resultado, não o texto na tela**

O hook `rtk` desta máquina reescreve comandos e filtra a saída, e isso já produziu erro de leitura em duas formas: um `tsc` que falhou com exit 127 foi exibido como "compilation completed", e um JSON com `hasConsent: false` foi exibido como `hasConsent: bool` — o campo aparece, o valor some. Também já devolveu `git diff` vazio e saída de `sed`/`grep` reordenada.

Quando o resultado embasa uma decisão ou serve de gate:

* Rodar pelo binário do projeto ou por script do `package.json`/`pyproject.toml`, não por invocação mediada.
* Conferir o **exit code**, não só o texto.
* Diante de resultado limpo demais — "0 erros" num repo que nunca compilou aqui — validar com um erro proposital antes de tratar o verde como real.
* Inspecionar valor salvando em arquivo e lendo o arquivo, ou via `rtk proxy <cmd>`. Ler código pela ferramenta de leitura, não por `sed`/`grep` no shell.
* Instrução a subagente precisa mandar **rodar o comando**; um subagente instruído a "usar o valor atual" reporta o tipo como se fosse o valor.

**Suíte verde prova só o que ela cobre.** O que está fora da cobertura é invisível no verde — registrar explicitamente as áreas não cobertas, senão o verde vira álibi.

Regra registrada com evidência vale mais que regra afirmada: anotar a medição que a sustenta (ex.: "sem a flag, 0 de 6 execuções verdes; com ela, 3 de 3").

### **Arquivos gerados, timestamps e datas**

Artefatos gerados em `xyz/` (reports, TODOs arquivados, outputs, rodadas de eval, dumps) usam dois níveis:

1. **Pasta do dia:** `%Y%m%d/`
2. **Arquivo:** prefixo `%Y%m%d_%H%M%S_` dentro dela

```
xyz/docs/20260813/20260813_154207_report-fase-2.md
xyz/outputs/20260813/20260813_161022_leads-enriquecidos.csv
```

* **A hora vem da máquina**, por `date '+%Y%m%d_%H%M%S'`, no momento da criação — nunca inferida, estimada ou arredondada. Hora arredondada é hora que não existiu, e a ordem cronológica deixa de ser confiável. Conferir depois com `ls --time-style`. Vale para os subagentes: a instrução precisa mandar rodar `date`.
* **Nunca sobrescrever** artefato timestampado — versão nova é arquivo novo.
* **Código versionado** (fontes, testes, código de evals) não leva prefixo; o git é o histórico.
* **Datas absolutas em qualquer registro** — converter "semana que vem" ou "na próxima sprint" em data.

### **`xyz/` — workspace local do TPM**

Pasta gitignored por inteiro, para pensar, juntar artefatos e documentar.

* `xyz/artifacts/` é **material-fonte do TPM** (requisitos, transcrições, prints, briefings): leitura apenas, não editar.
* O que o agente produz vai para `xyz/docs/`.

### **Git**

* **GitHub Flow:** `main` estável + branches de trabalho, Conventional Commits.
* **Commits** por bloco de ação lógica, com descrição rica. Assinatura ao fim: `Co-authored-by: [Agente - Modelo - Esforço]` — modelo e esforço explícitos permitem auditar depois o que produziu cada mudança.
* **`.md` da raiz são versionados.** No `.gitignore`: `.env`, pacotes/caches/pastas geradas, e toda a pasta `xyz/`.
* **Antes do primeiro push:** varrer o histórico por chaves reais (`AIza*`, `sk-*`, `sk-ant-*`, `xkeysib-*`, `ghp_*`, `gho_*`, `github_pat_*`, `Bearer ...`). Zero hits em todos os blobs.

#### GitHub multi-account SSH

Duas contas com chaves separadas, registradas com host aliases em `~/.ssh/config`:

* **Pessoal `rogerkrw`** → `github.com-personal` → `~/.ssh/id_ed25519_personal`
* **Profissional (BeTalent)** → `github.com-work` → `~/.ssh/id_ed25519_work`

1. Identificar a conta dona do repo; em dúvida, perguntar.
2. Não usar `git@github.com:<owner>/<repo>.git` (host default) — sempre o alias.
3. Após `gh repo create`, conferir `git remote -v` e corrigir com `git remote set-url origin …` antes do push: o `gh` configura o host default.
4. Sintoma de alias errado: `ERROR: Repository not found` — parece repo inexistente, é chave SSH errada.

### **Idiomas**

* **Identificadores, tipos, nomes de arquivo, git, commits, deploy:** inglês técnico.
* **Comentários e docstrings:** PT-BR — comentário é documentação, e quem lê é brasileiro.
* **Strings de UI e mensagens de erro ao usuário:** PT-BR.
* **Comentário explica o porquê, não o quê.** Se repete o que o código diz, sai. Havendo decisão não-óbvia, citar a referência.
* **Comentário que documenta armadilha, com o sintoma e o histórico do bug, permanece.** A regra de minimalismo não se aplica a ele — apagar reintroduz o bug.

### **Comunicação com o TPM**

O TPM é product builder, não engenheiro de código do dia a dia.

1. Uma frase em português simples, no nível do produto: o que a mudança significa.
2. Havendo decisão pendente, opções com trade-off em uma linha cada.
3. Arquivo, função ou commit só quando ele pedir inspeção técnica.

3+ termos de jargão sem definir → reescrever antes de enviar.

**Registro neutro** (vale para `.md`, comentário de código e resposta no chat):

* Fato, não adjetivo sobre o fato: `Trade-off:`, não "o trade-off, que registro com franqueza".
* Sem meta-comentário sobre o próprio texto ("vale registrar", "é importante notar", "sendo honesto"). Se está escrito, já está registrado.
* Ressalva se declara uma vez, no lugar certo. Repetir a cada seção é ruído.
* Rótulos secos: `Trade-off:` · `Efeito:` · `Limite conhecido:` · `Alternativa não adotada:` · `Risco:` · `Status:`
* Responder o que foi perguntado, no tamanho da pergunta. Sem resumo do que acabou de ser dito, sem próximo passo que ninguém pediu.

### **Medição**

* **Pesquisa web** de documentação oficial e versão estável antes de adotar tecnologia nova.
* **Baseline explícito:** melhoria se compara contra a run anterior por métrica nomeada, não por impressão. Uma mudança por vez — alterar duas e ver a métrica cair não diz qual causou.
* **Telemetria de LLM:** tokens (input/cached/output), latência e custo estimado.

## **Protocolo de Documentação**

* **CLAUDE/AGENTS/GEMINI.md:** perenes; alteração exige autorização do TPM. Use `cp` para mantê-los idênticos. Registram como construir — não o estado do trabalho.
* **TODO.md:** fases → etapas → tarefas. Marcar a cada conclusão; `[~]` para o parcial, com o motivo na linha.
* **HANDOFF.md:** onde a sessão parou, o que retomar primeiro, o que já foi verificado e como, e as armadilhas de ambiente que custaram tempo. Atualizado ao fim da sessão, a pedido do TPM.
* **Os dois andam juntos:** `TODO.md` diz o que falta; `HANDOFF.md` diz por onde retomar. Ao mexer num, conferir o outro. O estado do trabalho vive só nesses dois.
* **Não criar documento vivo novo na raiz** sem o TPM pedir. O que precisa de registro vai para o doc da fase em `xyz/docs/<pasta do dia>/`.
* **Opcionais, quando o TPM pedir:** `FUTURE.md` (itens adiados: título + por que foi adiado e o que viabilizaria; é memória de decisão, não lista de desejos) e `FLOW.md` (diagramas Mermaid, com data e commit de referência no cabeçalho).
* **RAILWAY.md** (deploy no Railway): copiar `~/dev/orquestration/utils/RAILWAY.md` para a raiz do projeto e preencher os placeholders `<...>`. Documenta a topologia de serviços e as armadilhas conhecidas. Mantido pelo `devsecops`.
* **Relatórios de etapa** em `xyz/docs/<pasta do dia>/`, antes do commit:

```
---
date: %Y%m%d_%H%M%S
author: [Claude Code, Codex etc.]
task_ref: [ID da tarefa no TODO.md]
---

# Report: [Título da Etapa/Fase]

## 1. Objetivo
[Por que a etapa foi feita e que problema resolve].

## 2. Ações
[Implementações, refatorações e novos arquivos].

## 3. Resultados
[Evidências de funcionamento, logs, métricas, observações].

## 4. Próximos Passos
[Prosseguir ou corrigir o que ficou].
```
