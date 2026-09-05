---
name: handoff
description: Registra o estado de uma tarefa para outra sessão ou agente continuar sem reler toda a conversa. Use quando houver troca de contexto, encerramento de sessão, delegação ou pedido explícito de handoff; não atualize artefatos de handoff em toda tarefa.
---

# Handoff

Produza um registro curto, factual e retomável. O handoff aponta para artefatos existentes; não substitui `TODO.md`, `HANDOFF.md`, commits, diffs ou PRDs.

## Antes de escrever

- Leia a tarefa e os artefatos já existentes, especialmente `TODO.md` e `HANDOFF.md` quando presentes.
- Confira `git status`, diff e os testes ou gates realmente executados. Não declare algo como concluído por inferência.
- Identifique o próximo agente ou sessão e escreva somente o contexto necessário para ele agir.
- Redija segredos, tokens, cookies, PII, credenciais e payloads sensíveis. Referencie o arquivo seguro, nunca copie o valor.

## Conteúdo

Use esta ordem, adaptando ao projeto:

1. **Objetivo:** resultado buscado e critério de aceitação.
2. **Status:** concluído, parcial ou bloqueado; indique o motivo.
3. **Verificado:** comandos, testes, gates e evidências observadas.
4. **Decisões:** escolhas feitas, trade-offs e decisões ainda pendentes.
5. **Arquivos e artefatos:** caminhos, commits, diffs e links relevantes, sem duplicar seu conteúdo.
6. **Próxima ação:** a primeira ação concreta para retomar.
7. **Riscos e armadilhas:** dependências, limitações de ambiente e áreas sem cobertura.
8. **Skills sugeridas:** somente skills que o próximo passo realmente deve carregar.

## Destino e limites

- Atualize o `HANDOFF.md` existente quando essa for a convenção do projeto, a tarefa autorizar a atualização e o agente tiver permissão de escrita. Em modo read-only, entregue o conteúdo do handoff no relatório sem tentar gravar arquivo. Se o projeto usar outro artefato, siga sua convenção.
- Não crie documento vivo novo na raiz, não altere `xyz/artifacts/` e não envie mensagens ou publique issues.
- Para um relatório separado, use a pasta de documentação prevista pelo projeto e o timestamp produzido por `date`; nunca invente horário.
- Se não houver informação suficiente, marque `Desconhecido` ou `Não verificado` em vez de preencher com suposição.

## Saída

O próximo agente deve saber o que fazer primeiro, o que não repetir, o que já está provado e qual risco permanece. O resumo da conversa vem depois dos artefatos, nunca no lugar deles.
