---
name: llm-evaluation
description: "Define e executa avaliações de aplicações LLM e agentes: golden sets, structured output, tools, trajetórias, retrieval, groundedness, segurança, custo, latência e regressão. Use antes de afirmar qualidade ou ao alterar prompt, modelo, contexto, tool, memória ou workflow; não substitui testes unitários nem revisão de segurança."
---

# LLM Evaluation

Evals são o feedback loop de sistemas probabilísticos. Avalie a tarefa e a trajetória no harness real, não apenas o modelo isolado nem uma resposta que parece boa.

## Comece pelo contrato

Defina:

- tarefa, população e distribuição de casos;
- saída esperada e critério de aceitação;
- erros críticos e toleráveis;
- ações ou efeitos que exigem bloqueio/aprovação;
- métrica primária, slices e baseline;
- orçamento de custo, latência, requests, steps e intervenção humana.

Não use um score agregado para esconder regressão em casos críticos. Evals são específicas da tarefa; não existem thresholds universais de qualidade.

## Camadas de avaliação

| Camada | Verifica | Exemplos |
|---|---|---|
| Contrato | forma e limites | schema Pydantic, tipos, campos obrigatórios, validação |
| Tool | escolha e argumentos | tool correctness, argument correctness, autorização, erro recuperável |
| Trajetória | caminho até o resultado | ordem, número de chamadas, loops, budgets, handoff |
| Tarefa | resultado para o usuário | task success, rubric, precisão, recall, completude |
| Knowledge | evidência | context recall/precision, groundedness, citation correctness, freshness |
| Segurança | cauda de risco | prompt injection, leakage, unsafe action, tenant isolation |
| Operação | produção | p50/p95/p99, timeout, disponibilidade, custo por tarefa bem-sucedida |
| Negócio/humano | resultado real | adoção, override, rework, tempo poupado, conversão ou custo evitado |

Teste o retriever separadamente da geração e a trajetória separadamente do texto final quando cada camada puder falhar de forma independente.

## Dataset e casos

Construa um conjunto pequeno, versionado e legível, com:

- golden cases representativos do caminho normal;
- casos-limite e entradas ambíguas;
- slices por idioma, domínio, tenant, tamanho e dificuldade;
- casos adversariais para conteúdo não confiável, permissões e prompt injection;
- casos de abstention, fallback, timeout, tool error e dados ausentes;
- casos de regressão para cada bug real;
- casos de memória e compaction com decisões ou constraints que reaparecem mais tarde.

Cada caso deve carregar contexto suficiente para reproduzir a decisão e, quando possível, saída esperada ou rubric verificável. Não inclua dados reais sensíveis sem minimização e autorização.

## Método experimental

1. registre o baseline e o harness completo;
2. altere uma variável relevante por vez;
3. rode o conjunto inteiro e os slices de risco;
4. examine falhas por camada, não somente a média;
5. compare custo, latência, intervenção e qualidade;
6. promova apenas se não houver regressão crítica;
7. guarde configuração, modelo/provider, dados, versão do código e evidência.

Para comparações de modelo, congele prompt, tools, contexto, retrieval, budgets, temperatura quando aplicável, ambiente e critérios. Uma mudança no harness pode parecer ganho do modelo.

## Pydantic AI

Use `TestModel` para conformidade estrutural e caminhos simples; `FunctionModel` para controlar respostas e testar branches, retries e fallbacks. Use Pydantic Evals para datasets, evaluators e experimentos code-first. Para agentes com tools, avalie spans e trajetória, não apenas `result.output`. Logfire torna modelo, tool calls, tokens, latência e erros observáveis.

Consulte `building-pydantic-ai-agents` e a documentação atual do [Pydantic Evals](https://pydantic.dev/docs/ai/evals/evals/) antes de aplicar APIs. Testes determinísticos não substituem avaliações com modelos reais, e avaliações com LLM-as-a-judge não substituem critérios ou revisão humana em casos críticos.

## Gates e relatório

Um gate deve declarar o conjunto avaliado, versão, baseline, métrica, resultado, incerteza e decisão. Pode bloquear por falha crítica mesmo com média melhor. Relate:

- qualidade por camada e por slice;
- casos que regrediram e causa provável;
- custo, latência, requests, steps e intervenção;
- falhas de segurança e cobertura não verificada;
- decisão: promover, manter, investigar ou reverter;
- próximo caso que aumentará a informação.

Não chame um sistema de “production-ready” porque a suíte unitária passou. Não chame um prompt de “melhor” sem comparação compatível.

## Skills relacionadas

- `ai-application-engineering` — para arquitetura e escolha de baseline;
- `context-engineering` — para avaliar seleção, memória, compaction e uso do contexto;
- `building-pydantic-ai-agents` — para TestModel, FunctionModel e execução;
- `qa-testing` — para testes automatizados e regressões;
- `llm-security` — para ameaças, guardrails e autorização;
- `logfire` — para traces e métricas de execução.
