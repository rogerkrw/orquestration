# Checklist de implementação e revisão de UI

Regras concretas, verificáveis, agnósticas de framework. Servem tanto para escrever a UI quanto para revisá-la.

Ao revisar, reportar em `arquivo:linha` com severidade:

- 🔴 **Crítico** — impede uso, quebra acessibilidade, perde dado do usuário
- 🟡 **Moderado** — degrada a experiência, inconsistência visível
- 🟢 **Menor** — polimento

> Base adaptada das [Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines) (Vercel Labs), com ajustes para PT-BR — ver `pt-br.md`.

## Acessibilidade

- Botão só com ícone precisa de `aria-label`
- Campo de formulário precisa de `<label>` ou `aria-label`
- Elemento interativo precisa de handler de teclado, não só de mouse
- `<button>` para ação, `<a>` para navegação — nunca `<div onClick>`
- Imagem precisa de `alt` (ou `alt=""` se decorativa)
- Ícone decorativo leva `aria-hidden="true"`
- Atualização assíncrona (toast, validação) precisa de `aria-live="polite"`
- HTML semântico antes de ARIA (`<button>`, `<a>`, `<label>`, `<table>`)
- Headings hierárquicos `<h1>`–`<h6>`; skip link para o conteúdo principal
- `scroll-margin-top` em âncora de heading
- Contraste WCAG 2.2 AA: ≥ 4.5:1 texto normal, ≥ 3:1 texto grande e elemento de UI
- Alvo de toque ≥ 44×44px

## Foco

- Elemento interativo precisa de foco visível (`focus-visible:ring-*` ou equivalente)
- Nunca `outline: none` sem substituto visível
- `:focus-visible` em vez de `:focus` (evita anel de foco no clique)
- `:focus-within` para agrupar controle composto

## Formulários

- Input com `autocomplete` e `name` significativos
- `type` correto (`email`, `tel`, `url`, `number`) e `inputmode`
- Nunca bloquear colar (`onPaste` + `preventDefault`)
- Label clicável (`for`/`htmlFor` ou envolvendo o controle)
- `spellcheck={false}` em e-mail, código e nome de usuário
- Checkbox/radio: label e controle no mesmo alvo de clique, sem zona morta
- Botão de submit segue habilitado até a requisição começar; spinner durante
- Erro inline junto ao campo; foco no primeiro erro ao submeter
- Placeholder mostra padrão de exemplo e termina com `…`
- Avisar antes de sair com alteração não salva

## Estados

- Todo elemento interativo: `default`, `hover`, `focus`, `active`, `disabled`, `loading`
- Estado de hover e de foco aumentam contraste em relação ao repouso
- Todo container de dados: vazio, carregando, erro
- Estado vazio explica o que é, por que está vazio e como começar
- Não renderizar UI quebrada para string ou array vazio

## Animação

- Respeitar `prefers-reduced-motion`
- Animar só `transform` e `opacity` (compositor-friendly)
- Nunca `transition: all` — listar as propriedades
- `transform-origin` correto; em SVG, transform no `<g>` com `transform-box: fill-box`
- Animação interrompível, respondendo a input no meio
- Máximo 1-2 elementos animados por view

## Conteúdo e overflow

- Container de texto trata conteúdo longo: `truncate`, `line-clamp-*` ou `break-words`
- Filho de flex precisa de `min-w-0` para truncar
- Conteúdo gerado pelo usuário: prever curto, médio e muito longo
- Testar com o texto real em português — ver `pt-br.md`

## Tipografia

- `…` em vez de `...`
- Aspas curvas `"` `"` em vez de retas
- Espaço não-quebrável: `10&nbsp;MB`, `⌘&nbsp;K`, nomes de marca
- Estado de carregamento termina com `…`: "Carregando…", "Salvando…"
- `font-variant-numeric: tabular-nums` em coluna de números e comparações
- `text-wrap: balance` em headings (evita viúvas)

## Imagens

- `<img>` com `width` e `height` explícitos (evita CLS)
- Abaixo da dobra: `loading="lazy"`
- Crítica acima da dobra: `fetchpriority="high"` ou equivalente

## Performance

- Lista grande (>50 itens): virtualizar ou `content-visibility: auto`
- Sem leitura de layout no render (`getBoundingClientRect`, `offsetHeight`, `scrollTop`)
- Agrupar leituras e escritas do DOM, sem intercalar
- Preferir input não-controlado; controlado precisa ser barato por tecla
- `<link rel="preconnect">` para domínios de CDN
- Fonte crítica: `preload` + `font-display: swap`
- Alvos: LCP < 2.5s, CLS < 0.1, INP < 200ms

## Navegação e estado

- URL reflete o estado: filtro, aba, paginação, painel expandido em query params
- Link é `<a>` (suporta Cmd/Ctrl+clique e clique do meio)
- Todo estado navegável tem deep link
- Ação destrutiva precisa de confirmação ou janela de desfazer — nunca imediata

## Toque e interação

- `touch-action: manipulation` (evita atraso do duplo-toque)
- `-webkit-tap-highlight-color` definido intencionalmente
- `overscroll-behavior: contain` em modal, drawer e sheet
- Durante drag: desabilitar seleção de texto
- `autofocus` com parcimônia — desktop, input primário único; evitar no mobile

## Layout e área segura

- Layout full-bleed usa `env(safe-area-inset-*)` para notch
- Evitar scrollbar indesejada: corrigir o overflow, não só esconder
- Flex/grid em vez de medição por JS
- Layout se mantém em 375px, 768px e 1280px

## Tema

- `color-scheme: dark` no `<html>` em tema escuro (corrige scrollbar e inputs nativos)
- `<meta name="theme-color">` combinando com o fundo
- `<select>` nativo com `background-color` e `color` explícitos

## Locale

- Data e hora com `Intl.DateTimeFormat`, nunca formato hardcoded
- Número e moeda com `Intl.NumberFormat`
- Idioma por `Accept-Language`/`navigator.languages`, nunca por IP
- Nome de marca, token de código e identificador com `translate="no"`

## Hidratação (SSR)

- Input com `value` precisa de `onChange` — ou `defaultValue` se não-controlado
- Renderização de data/hora protegida contra divergência servidor/cliente
- `suppressHydrationWarning` só onde for realmente necessário

## Anti-padrões — sinalizar sempre

- `user-scalable=no` ou `maximum-scale=1` desabilitando zoom
- `onPaste` com `preventDefault`
- `transition: all`
- `outline: none` sem substituto de foco
- `<div>`/`<span>` com handler de clique
- Imagem sem dimensão
- Lista grande sem virtualização
- Campo sem label
- Botão de ícone sem `aria-label`
- Formato de data/número hardcoded
- `autofocus` sem justificativa
- Valor avulso (`bg-[#3b82f6]`, `text-[13px]`) onde existe token do design system
