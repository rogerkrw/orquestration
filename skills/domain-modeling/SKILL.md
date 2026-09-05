---
name: domain-modeling
description: Esclarece vocabulário, entidades, estados, regras e invariantes de um domínio de software. Use quando uma decisão de produto, API, workflow, banco ou integração atravessar módulos e depender de conceitos ainda ambíguos.
---

# Domain Modeling

Modele o problema antes de cristalizá-lo em endpoints, tabelas, estados ou componentes. O modelo deve reduzir ambiguidade e orientar decisões; não é motivo para criar abstrações que o produto ainda não precisa.

## Fluxo

1. **Leia o que existe.** Comece pela tarefa, código, testes, README, `TODO.md`, `HANDOFF.md`, glossário e ADRs disponíveis. Onde código e documentação divergem, trate o código como fato e registre a divergência.
2. **Separe conhecimento.** Classifique cada afirmação como fato observado, hipótese, decisão ou pergunta aberta. Não transforme um exemplo em regra sem evidência.
3. **Nomeie o domínio.** Liste atores, entidades, value objects, comandos, eventos, estados e relações. Escolha um termo por conceito e preserve-o em código, testes e artefatos.
4. **Explicite comportamento.** Para cada conceito relevante, descreva invariantes, transições válidas, pré-condições, pós-condições, casos-limite e exemplos concretos. Procure estados ocultos em flags, nulos e combinações de campos.
5. **Teste o modelo.** Percorra cenários normais, exceções, concorrência, reprocessamento e permissões quando aplicável. Se dois termos ou regras conflitarem, destaque o conflito antes de escolher.
6. **Conecte à solução.** Só depois derive implicações para API, persistência, UI, integrações e testes. O modelo informa a implementação; não prescreve banco, framework ou arquitetura sem necessidade.

## Documentação local

- Reutilize glossários e ADRs existentes. Não crie documento vivo na raiz sem escopo explícito.
- Em projetos com `xyz/`, rascunhos e relatórios vão para `xyz/docs/`; `xyz/artifacts/` é material-fonte do TPM e não deve ser editado.
- Uma decisão que afeta o comportamento deve ficar no artefato canônico apropriado, com trade-off e consequência. Não publique issues, altere schema ou mude produto automaticamente.

## Saída

Entregue, no tamanho necessário: glossário, mapa de conceitos e relações, regras/invariantes, cenários que validam o modelo, decisões tomadas, conflitos e implicações para implementação. Marque explicitamente o que continua desconhecido.
