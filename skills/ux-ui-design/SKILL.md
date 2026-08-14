---
name: ux-ui-design
description: UX e UI de ponta a ponta, agnóstico de stack — direção visual, hierarquia, acessibilidade, estados de interação, microcopy e crítica estruturada de interface. Use ao decidir a aparência de uma tela antes de codar, ao implementar UI, ao escrever ou revisar texto de interface (botão, erro, empty state, confirmação), e ao revisar UI já implementada em busca de problemas de usabilidade, contraste, foco, responsividade ou consistência. Cobre React, Svelte, Vue, HTML/CSS, NiceGUI, Chainlit e qualquer camada de apresentação. Para o sistema de componentes específico de SvelteKit, complementar com a skill `sveltekit-ui`.
---

# UX/UI Design

Camada de decisão, implementação e revisão de interface. Agnóstica de stack: as regras valem para qualquer coisa que renderize pixels para uma pessoa.

## Os três modos

Identifique em qual você está antes de começar — eles pedem trabalho diferente.

| Modo | Quando | Entrega |
| --- | --- | --- |
| **Decidir** | Antes de existir código. Tela nova, produto novo, redesenho | Plano de design: paleta, tipografia, layout, elemento-assinatura |
| **Implementar** | Escrevendo a UI | Código que já nasce acessível, com todos os estados e texto revisado |
| **Revisar** | UI existente, pré-merge | Achados em `arquivo:linha`, por severidade, com a correção |

## Modo Decidir

Antes de escrever CSS, produzir um plano curto e criticá-lo.

1. **Fixar o assunto.** Se o brief não define produto, público e a única tarefa da tela, defina e declare. Decisão distintiva nasce do universo do assunto — vocabulário, materiais, referências do setor —, não de um catálogo de estilos.
2. **Montar o token system:**
   - **Cor:** 4-6 valores hex nomeados por papel (fundo, superfície, texto, ação, destaque, erro).
   - **Tipografia:** 2+ famílias por papel — display com personalidade e uso contido, corpo legível, utilitária para dado/legenda se necessário. Escala e pesos explícitos.
   - **Layout:** conceito em uma frase + wireframe ASCII para comparar alternativas.
   - **Assinatura:** o único elemento pelo qual a tela será lembrada.
3. **Criticar o plano contra o brief.** Se alguma parte é o que sairia para qualquer produto do mesmo segmento, refazer aquela parte e dizer o que mudou e por quê. Só depois codar, seguindo o plano.

**Calibração — os defaults de IA.** Design gerado por IA converge em três looks: fundo creme (~`#F4F1EA`) com serifa de alto contraste e acento terracota; fundo quase-preto com um acento verde-ácido ou vermelhão; layout tipo jornal com fios de 1px, zero border-radius e colunas densas. São legítimos quando o brief pede; como escolha automática, são a ausência de escolha. Onde o brief deixa o eixo livre, não gastar a liberdade num deles.

**Concentre a ousadia num lugar.** O elemento-assinatura carrega a memória; o resto fica quieto e disciplinado. Maximalismo exige execução elaborada, minimalismo exige precisão de espaçamento e tipo — elegância é executar bem a direção escolhida, não escolher a mais segura.

## Modo Implementar

Piso de qualidade, sem anunciar: responsivo até mobile, foco de teclado visível, movimento reduzido respeitado.

**Estados** — todo elemento interativo tem `default`, `hover`, `focus`, `active`, `disabled` e `loading` quando faz I/O. Todo container de dados tem estado vazio, de carregamento e de erro. Estado vazio é convite à ação, não espaço em branco.

**Hierarquia** — a ordem de leitura deve ser deliberada. Um elemento primário por tela; se dois competem, nenhum vence. Espaço em branco é ferramenta de agrupamento, não sobra.

**Estrutura significa algo** — numeração, eyebrows, divisores e rótulos codificam informação real. Marcadores `01 / 02 / 03` só quando a ordem carrega informação que o leitor precisa.

**Movimento** — animar `transform` e `opacity` (compositor-friendly). No máximo 1-2 elementos animados por view. Um momento orquestrado rende mais que efeitos espalhados; excesso de animação é sinal de interface gerada por IA.

Regras detalhadas de implementação e revisão: `references/review.md`.

## Modo Revisar

Cinco dimensões, nesta ordem:

1. **Primeira impressão (2s)** — o que puxa o olho primeiro? É o certo? O propósito da tela é imediato?
2. **Usabilidade** — a pessoa completa a tarefa? Navegação previsível? Elementos interativos parecem interativos? Passos desnecessários?
3. **Hierarquia visual** — ordem de leitura clara, ênfase nos elementos certos, tipografia criando estrutura.
4. **Consistência** — tokens do design system em vez de valores avulsos; elementos parecidos se comportam de forma parecida.
5. **Acessibilidade** — WCAG 2.2 AA: contraste ≥ 4.5:1 (texto normal) e ≥ 3:1 (texto grande), alvo de toque ≥ 44px, navegação por teclado, foco visível, HTML semântico.

**Como reportar:** achado específico, com `arquivo:linha`, severidade e a correção. "O CTA compete com a navegação" em vez de "o layout está confuso". Ligar cada achado ao princípio ou à necessidade que ele viola. Registrar também o que funciona — crítica só com problema não calibra.

**Não redesenhar o que não está quebrado.** Escopo é auditar e corrigir. Decisão visual que parece intencional mas viola um padrão se reporta, não se sobrescreve em silêncio.

Checklist completo de revisão: `references/review.md`.

## Copy é parte do design

Palavras existem na interface por um motivo: tornar o uso mais fácil. São material de design, não decoração.

- **Nomear pelo que a pessoa controla**, nunca pela implementação: "notificações", não "configuração de webhook".
- **Voz ativa, dizendo o que acontece:** "Salvar alterações", não "Enviar". O verbo se mantém pelo fluxo inteiro — botão "Publicar" produz toast "Publicado".
- **Erro = o que aconteceu + por quê + como resolver.** Erro não pede desculpa nem é vago.
- **Confirmação nomeia a ação e a consequência:** "Excluir 3 arquivos? Isso não pode ser desfeito", com botões "Excluir arquivos" / "Manter arquivos" — nunca "OK" / "Cancelar".
- **Cada elemento faz um trabalho.** Rótulo rotula, exemplo demonstra; nada acumula função em silêncio.

Padrões por contexto (CTA, empty state, tooltip, onboarding, tom): `references/copy.md`.

## Português brasileiro

Interface em PT-BR não é interface em inglês traduzida — e a maior parte da literatura de UI assume inglês.

- **Texto em português ocupa 15-25% mais espaço.** Botão, card, nav e tabela dimensionados no inglês quebram. Testar com o texto real, no maior rótulo do conjunto.
- **Formatos:** `R$ 1.234,56` (ponto no milhar, vírgula no decimal), data `dd/mm/aaaa`, telefone com o 9 no celular, CPF/CNPJ e CEP com máscara.

Detalhe e demais convenções: `references/pt-br.md`.

## Quando carregar as references

- Revisando UI ou implementando com rigor técnico → `references/review.md`
- Escrevendo ou revisando texto de interface → `references/copy.md`
- Projeto em português → `references/pt-br.md`
