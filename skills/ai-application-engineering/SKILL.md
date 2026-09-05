---
name: ai-application-engineering
description: "Orienta a arquitetura de aplicações com LLMs e agentes: escolha de abordagem, fronteiras entre modelo e código, structured output, tools, RAG, memória, workflows, custo, confiabilidade e operação. Use ao projetar, implementar ou revisar um sistema de IA aplicado; não para backend convencional nem pesquisa de foundation models."
---

# AI Application Engineering

Projete o sistema aplicado em torno da tarefa e do risco, não em torno do modelo disponível. O resultado é uma combinação de código determinístico, modelo, contexto, conhecimento, tools, estado, validação, observabilidade e workflow humano.

## Primeiro: contrato da tarefa

Registre, no tamanho necessário:

- objetivo e usuário/processo afetado;
- entrada, saída e critério de sucesso observável;
- risco de erro e nível de autonomia aceitável;
- conhecimento necessário, sua fonte e sua volatilidade;
- ações externas, permissões, aprovação e reversibilidade;
- orçamento de latência, custo e número de chamadas;
- baseline sem LLM e evidência de que IA é adequada.

Separe fato observado, hipótese, decisão e pergunta aberta. Uma saída plausível não prova que o sistema resolveu a tarefa.

## Escada de complexidade

Escolha a menor camada que fecha o contrato:

1. código determinístico para regras, cálculos, validações e transições conhecidas;
2. prompt/instruções + saída estruturada para interpretação ou geração delimitada;
3. tool ou workflow para consultar sistemas e executar passos conhecidos;
4. RAG para conhecimento externo, privado ou mutável;
5. estado/memória para continuidade, progresso e fatos duráveis;
6. agente para selecionar ferramentas ou conduzir um processo variável;
7. multiagente, fine-tuning/PEFT ou adaptação de domínio somente quando evals demonstrarem que as camadas anteriores não bastam.

Não use fine-tuning para resolver conhecimento que muda. Não use RAG para corrigir comportamento que deveria ser validado por código. Não use agente onde um workflow determinístico é suficiente.

## Fronteiras do sistema

Modele explicitamente:

```text
entrada → contrato/contexto → modelo
                         ↘ tools / retrieval
modelo → schema/validator → decisão ou ação
                           ↘ state / trace / feedback
```

O modelo propõe; o sistema valida, autoriza, executa, registra e decide quando pedir aprovação ou recusar. Saídas estruturadas, validators e regras determinísticas devem ficar nas bordas de qualquer efeito relevante.

Em Pydantic AI, escolha conscientemente entre `Agent`, output type, dependências, tools/toolsets, capabilities, hooks, delegation e graph. Consulte `building-pydantic-ai-agents` para a API atual e verifique o lockfile antes de copiar um padrão. A abstração de `Agent` não elimina a necessidade de modelar estado, permissões, evals ou observabilidade.

## Conhecimento, comportamento e ação

Use esta separação para localizar a solução:

| Problema | Solução inicial | Prova necessária |
|---|---|---|
| Conhecimento correto e atual | retrieval com fonte, metadados e proveniência | recall/precision, groundedness, freshness |
| Comportamento ou formato repetitivo | schema, validator, exemplos ou PEFT | task success e regressão por slice |
| Ação em sistemas externos | tool estreita, autorização e aprovação | trajectory, permission e side-effect tests |
| Processo variável de várias etapas | agente com estado e budgets | sucesso de tarefa, limites e fallback |

## Arquitetura e operação

Inclua somente as responsabilidades que o caso exige:

- modelo e provider versionados, com fallback quando necessário;
- context assembler com task contract, estado mínimo e retrieval sob demanda;
- tools com schemas claros, timeout, idempotência, limites e identidade propagada;
- validação de entrada, argumentos, saída e efeitos externos;
- budgets de tokens, requests, steps, tempo e custo;
- tracing de modelo, contexto relevante, retrieval, tools, validações e resultado;
- golden set e regressão antes de trocar prompt, modelo, retriever ou tool;
- fallback humano, abstention ou resposta de erro que não esconda incerteza.

Para sistemas longos, use workspace e estado explícitos. Não dependa do transcript como única representação de progresso. Para multiagente, dê a cada trabalhador contexto local e contrato de retorno; não replique o histórico inteiro.

## Skills relacionadas

- `context-engineering` — quando a decisão envolve seleção, compressão, memória, retrieval ou cache do contexto;
- `llm-evaluation` — quando a mudança altera qualidade, trajetória, grounding, custo ou segurança;
- `building-pydantic-ai-agents` — quando a implementação usa Pydantic AI;
- `llm-security` — sempre que houver dados sensíveis, tools, RAG, ações ou exposição externa;
- `logfire` — para tracing e análise operacional.

## Entrega

Reporte: contrato da tarefa; baseline; abordagem escolhida e alternativas rejeitadas; diagrama ou fronteiras; schemas/tools/state; budgets e permissões; evals; observabilidade; riscos e próximo passo. Identifique o que é fato, o que é hipótese e o que ainda não foi medido.
