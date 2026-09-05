---
name: ux-writing
description: Escreve e revisa textos de interface e arquitetura da informação — navegação, rótulos, botões, formulários, erros, estados vazios, loading, confirmações, onboarding e ajuda. Use ao criar ou auditar fluxos de produto, priorizando clareza, ação, consistência terminológica, acessibilidade e recuperação; não use para copy comercial de landing pages.
---

# UX Writing

UX writing reduz a carga de interpretação no momento em que a pessoa tenta fazer algo. Trabalhe no fluxo inteiro, não em strings isoladas: a mesma ação deve ter o mesmo verbo e a mesma entidade em navegação, título, botão, feedback e ajuda.

## Contexto mínimo

Antes de escrever, identifique tela/fluxo, objetivo da pessoa, estado atual, ação e consequência, público, tom, idioma/localidade, limite de caracteres, glossário existente e restrições legais ou de acessibilidade. Se faltarem dados, declare as premissas e continue. Código, conteúdo existente e decisões de produto são fatos; não invente comportamento para acomodar uma frase.

## Regras de escrita

- Escreva em PT-BR claro, direto e escaneável; prefira voz ativa e palavras que a pessoa usa.
- Rótulos nomeiam o que a pessoa controla; botões começam pelo verbo e descrevem o resultado (“Salvar alterações”, “Baixar relatório”). Evite “OK”, “Enviar”, “Continuar” quando o efeito puder ser específico.
- Hierarquize informação: título orienta, instrução explica, exemplo demonstra, ajuda resolve dúvida. Não faça cada elemento repetir o anterior.
- Erros dizem o que aconteceu, por que aconteceu quando útil e como recuperar. Nunca culpam a pessoa, escondem o problema em jargão ou prometem sucesso sem evidência.
- Empty states, loading, sucesso, disabled, offline e permissões explicam o estado e o próximo passo possível. Confirmações nomeiam a ação e sua consequência, especialmente em operações destrutivas.
- Preserve sentido ao traduzir, acomode expansão de texto, não dependa só de cor/ícone e forneça nomes compreensíveis para leitores de tela.
- Seja humano sem ser espirituoso às custas da compreensão. Não use clichês, urgência artificial, manipulação ou microcopy que introduza uma decisão de produto não tomada.

## Arquitetura da informação

Agrupe pelo modelo mental da pessoa, não pelo organograma ou pela implementação. Audite nomes de seções, níveis de navegação, breadcrumbs, filtros, busca, ordenação e mensagens de orientação. Duas opções só são equivalentes se levam ao mesmo resultado e deixam isso claro; reduza escolhas concorrentes e sinalize a ação primária.

## Entrega

Apresente: objetivo e premissas; inventário do fluxo; tabela com elemento, estado, texto proposto, limite e justificativa; decisões de terminologia/IA; e dúvidas que realmente exigem decisão do TPM. Para uma revisão, registre também o texto atual, problema e severidade. Verifique a cópia contra os estados da UI e contra o conteúdo real antes de concluir.

Consulte `references/principles.md` quando precisar fundamentar decisões de clareza, padrões, acessibilidade ou qualidade editorial.
