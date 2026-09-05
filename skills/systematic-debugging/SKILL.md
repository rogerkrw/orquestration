---
name: systematic-debugging
description: Investiga bugs e falhas de execução por evidência, causa-raiz e hipóteses testáveis. Use ao diagnosticar comportamento incorreto, testes falhando, incidentes, regressões ou integrações instáveis; não use para implementar uma feature sem falha observada.
---

# Systematic Debugging

Investigue a causa antes de alterar o código. O objetivo é sair com uma reprodução confiável, uma causa sustentada por evidência, um fix mínimo e um teste de regressão.

## Fluxo

1. **Defina a falha.** Registre o comportamento esperado, o observado, o comando ou fluxo que falha e o ambiente. Se a reprodução não for conhecida, construa a menor reprodução possível.
2. **Proteja os dados.** Redija tokens, senhas, cookies, PII, URLs privadas e payloads sensíveis antes de exibir logs ou salvar artefatos. Não use produção para experimentar.
3. **Construa o feedback loop.** Prefira um teste ou comando determinístico que fique vermelho para a falha e verde para o comportamento corrigido. Sem sinal pass/fail, reduza o problema antes de especular.
4. **Colete evidência.** Leia stack trace, logs correlatos, fluxo de dados, configuração relevante e mudanças recentes. Compare uma execução que funciona com a que falha quando isso for possível.
5. **Formule hipóteses.** Liste poucas causas ordenadas por evidência e impacto. Para cada uma, defina uma verificação que possa confirmar ou eliminar a hipótese sem mudar várias coisas ao mesmo tempo.
6. **Teste e refine.** Faça uma alteração diagnóstica por vez. Instrumente somente o necessário e remova a instrumentação temporária depois. Se três tentativas falharem, reavalie a hipótese e a arquitetura em vez de acumular patches.
7. **Corrija e prove.** Depois de localizar a causa, aplique o menor fix que restaure a regra correta, mantenha compatibilidade e não esconda a falha. Adicione ou ajuste o teste de regressão e rode os gates pertinentes.

## Limites

- Não declare causa-raiz por coincidência temporal, mensagem de erro isolada ou suíte verde sem cobertura da falha.
- Não transforme um workaround em solução permanente sem registrar seu limite.
- Em auditoria DevSecOps, permaneça read-only. Em incidente de produção, não altere o sistema ao vivo sem o modo de execução e a confirmação exigidos pelo agente.
- Preserve o escopo: debugging não autoriza refatoração ampla, alteração de produto ou ação externa.

## Saída

Reporte: falha reproduzida, causa-raiz, evidências, fix aplicado ou próximo experimento, testes executados, áreas não cobertas e risco residual. Use caminhos e linhas quando disponíveis.
