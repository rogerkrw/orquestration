---
name: context-engineering
description: "Projeta e revisa o contexto de sistemas com LLMs: task contract, estado, memória, retrieval just-in-time, tool outputs, workspace, compaction, handoff, cache e permissões. Use quando qualidade, custo ou continuidade dependerem do que o modelo vê; não é uma skill de prompt copywriting."
---

# Context Engineering

Contexto é tudo que participa da inferência: instruções, histórico, schemas de tools, documentos recuperados, resultados de tools, estado e memória. O objetivo é maximizar sinal útil dentro do orçamento de atenção e custo, não preencher a janela disponível.

## Camadas do contexto

Monte o contexto por estabilidade e necessidade:

```text
políticas estáveis
  → contrato da tarefa
  → estado atual
  → conhecimento e memória recuperados
  → resultados de tools
  → saída, validação e feedback
```

O contrato da tarefa deve conter objetivo, deliverable, constraints e critérios de sucesso. O estado deve responder onde o trabalho está sem exigir releitura do transcript. Não misture fatos voláteis, histórico bruto e regras estáveis no mesmo bloco sem motivo.

## Seleção progressiva

- carregue apenas a skill, referência ou tool necessária para o passo atual;
- prefira `search → inspect → read(span) → expand` a retornar documentos inteiros;
- filtre e compacte resultados no ambiente antes de enviá-los ao modelo;
- use filesystem, banco ou artifact store para contexto durável e grande;
- deixe o modelo descobrir capacidades long-tail sob demanda quando o runtime suportar isso;
- mantenha o prefixo estável separado do conteúdo dinâmico para favorecer cache.

Mais contexto não é automaticamente melhor. Context flooding, informação stale, duplicação e resultados de tools verbosos competem com a evidência relevante.

## Separações obrigatórias

### Histórico, estado, memória e conhecimento

| Objeto | Função | Regra |
|---|---|---|
| Histórico | registro da conversa/execução | pode ser compactado; não é estado canônico |
| Estado | posição atual do trabalho | explícito, pequeno e atualizável |
| Memória | fato ou preferência que sobrevive ao turno | seletiva, temporal, versionada e com proveniência |
| Conhecimento | fonte externa para responder | recuperado com ACL, freshness e citação |
| Workspace | artefatos grandes e operáveis | endereçável por caminho/ID; não precisa entrar inteiro no prompt |

Uma observação não é automaticamente confiável, durável ou globalmente aplicável. Ao escrever memória, deduplicate, registre origem/data/confiança/escopo/validade e reconcilie conflitos. Ao ler, filtre por relevância, entidade, autorização e recência.

### Contexto do código e contexto do LLM

Dependências locais, conexões, identidade e política podem existir no runtime sem serem enviadas ao modelo. Dados só entram no contexto do LLM por instrução, input, tool, retrieval ou histórico. Nunca trate a existência de uma dependência local como autorização para o modelo usar todos os seus recursos.

## Tools como interfaces de contexto

Cada tool deve informar claramente o que faz, quando usar, parâmetros, retorno, limites e recuperação de erro. Prefira tools pequenas e response-aware:

- `search` retorna IDs, títulos, snippets e scores;
- `inspect` retorna metadados e estrutura;
- `read` retorna somente o trecho pedido;
- operações de escrita exigem identidade, escopo, idempotência e aprovação quando o efeito for relevante.

Conteúdo de web, e-mail, PDF, ticket ou RAG é dado não confiável. Separe trust zones e não permita que texto recuperado redefina políticas, permissions ou instruções do sistema.

## Long-running e compaction

Antes de compactar ou transferir, preserve:

```yaml
goal:
success_criteria:
current_status:
completed:
open_tasks:
decisions:
constraints:
assumptions:
failed_attempts:
important_artifacts:
evidence:
risks:
next_action:
```

Teste a compactação com informações que só serão necessárias muitos passos depois. Não apague approval state, permissões, decisões irreversíveis, artefatos alterados ou falhas anteriores. Use handoff/reset deliberado antes do overflow.

## Evals do contexto

Avalie o contexto separadamente da resposta:

- **context recall:** a evidência necessária foi encontrada?
- **context precision:** o que entrou era relevante?
- **utilization:** o modelo usou a evidência disponível?
- **groundedness:** as afirmações são sustentadas?
- **state fidelity:** decisões, constraints e progresso sobreviveram?
- **end-task success:** a tarefa completa foi concluída?

Instrumente o trace para saber o que foi recuperado, filtrado, inserido, descartado, escrito em memória e compactado. Não aumente `top-k`, janela ou histórico como primeira resposta a uma falha; localize qual camada perdeu sinal.

## Segurança e custo

- aplique ACL no retrieval, não somente na pergunta;
- não persista PII ou secrets em memória, logs, embeddings ou traces sem política;
- mantenha tenant, identidade, autorização e validade no contexto estruturado;
- limite tamanho de input/tool output, requests, steps, tokens, tempo e custo;
- trate cache como otimização, nunca como fonte de autorização ou verdade;
- invalide memória e contexto quando fonte, entidade, permissão ou versão mudar.

## Skills relacionadas

- `ai-application-engineering` — para decidir a arquitetura maior;
- `llm-evaluation` — para construir regressões de contexto e trajetória;
- `building-pydantic-ai-agents` — para capabilities, histórico, tools e harness no Pydantic AI;
- `llm-security` — para prompt injection, memória, RAG e permissões;
- `handoff` — para continuidade entre sessões.

## Entrega

Reporte: task contract; camadas de contexto; fontes e trust boundaries; política de retrieval/memória; formato de tools; compaction/handoff; budgets/cache; evals e risco residual.
