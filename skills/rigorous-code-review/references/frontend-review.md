# Frontend review (React, Vue, e padrões web)

Esta referência cobre o que olhar em código de UI: estado, performance de render, efeitos colaterais, acessibilidade, formulários, e os bugs específicos do lado do cliente que reviewers de backend não treinam o olho para pegar.

Princípio organizador: **o frontend tem o usuário humano do outro lado.** Bugs aqui são percebidos imediatamente, prejudicam confiança no produto, e frequentemente não disparam erro alguma — só uma experiência ruim. O reviewer precisa olhar com mente de QA, não só de programador.

---

## React (padrões aplicáveis a Vue/Svelte/Solid com leves adaptações)

### State management — onde está o bug mais provável

**Mutação direta de state.** Mata reatividade silenciosamente:

```js
// 🚨 React não vai re-renderizar
state.items.push(newItem)
setState(state)

// 🚨 Mesma armadilha com objetos
state.user.name = newName
setState(state)
```

Pergunta no review: "Esse update está retornando uma referência nova?" Em Redux, mesma regra com mais ênfase (reducers devem ser puros).

**State levantado/abaixado errado.** Estado deve viver no menor escopo possível, levantando só quando há **necessidade real de compartilhamento**.

- State acessado por vários componentes irmãos → levantar para parent comum
- State usado em um componente só → deixar local
- State global usado por um componente → trazer para local

Anti-padrões opostos: 
- Tudo em Context global → re-renderiza componentes que nem usam o estado
- Tudo local → "prop drilling" 8 níveis de profundidade

**Estado derivado armazenado.** Se você consegue calcular B a partir de A, **não armazene B em state separado**. Vai sair de sincronia inevitavelmente:

```js
// 🚨 Sai de sincronia
const [items, setItems] = useState([])
const [count, setCount] = useState(0)
// quando alguém setItems sem setCount, count fica errado

// ✅
const [items, setItems] = useState([])
const count = items.length  // derivado
// (se for cálculo caro, useMemo)
```

**State pertencente ao server tratado como local.** Cache de API mantido manualmente em useState é receita para race conditions, dados stale, e bugs de invalidação. Use:
- React Query / TanStack Query
- SWR
- RTK Query
- Apollo Client (GraphQL)

Essas libs resolvem cache, refetch, invalidação, race conditions corretamente.

### Hooks — armadilhas comuns

**useEffect com deps erradas:**

```js
// 🚨 array vazio mas usa userId → stale closure
useEffect(() => {
  fetchUser(userId)
}, [])

// 🚨 sem array → roda em todo render
useEffect(() => {
  fetchUser(userId)
})

// ✅
useEffect(() => {
  fetchUser(userId)
}, [userId])
```

Use linter `react-hooks/exhaustive-deps`. Quando o linter reclama e o autor "explicitamente quer ignorar", desconfie.

**Effects sem cleanup → memory leak:**

```js
useEffect(() => {
  const sub = source.subscribe(handler)
  return () => sub.unsubscribe()  // ✅ cleanup
}, [])

useEffect(() => {
  window.addEventListener('resize', handler)
  return () => window.removeEventListener('resize', handler)  // ✅
}, [])

useEffect(() => {
  const timer = setInterval(tick, 1000)
  return () => clearInterval(timer)  // ✅
}, [])
```

**Effects com race condition:**

```js
// 🚨 — se userId mudar rápido, fetch antigo pode resolver depois do novo
useEffect(() => {
  fetchUser(userId).then(setUser)
}, [userId])

// ✅
useEffect(() => {
  let cancelled = false
  fetchUser(userId).then(u => {
    if (!cancelled) setUser(u)
  })
  return () => { cancelled = true }
}, [userId])
```

Bibliotecas de data fetching resolvem isso melhor — outra razão para preferi-las.

**useEffect para sincronizar com estado:** geralmente é code smell. Frequentemente o que se quer é estado derivado (calculado direto no render).

```js
// 🚨
const [fullName, setFullName] = useState('')
useEffect(() => {
  setFullName(`${first} ${last}`)
}, [first, last])

// ✅
const fullName = `${first} ${last}`
```

**useMemo / useCallback prematuro.** Não envolva tudo. Re-criação de função em render geralmente é barata; o overhead de memo + dependências erradas pode piorar. Use quando *medir* perf problema, não preventivamente.

### Performance

**Re-renders desnecessários.**

Sinais a procurar:
- Componente recebe `onClick={() => doX()}` inline → re-cria função todo render → quebra memoização do filho
- Componente recebe `style={{ color: 'red' }}` inline → mesmo
- Pai usa `useState` que muda frequentemente, mas tudo está num componente só → considere extrair filhos para isolar re-render

`React.memo` é útil para componentes folha caros que recebem props estáveis. Mas: se você precisa de `React.memo` em todo componente, o problema é arquitetural — provavelmente o estado está no nível errado.

**Listas grandes sem virtualização.** Renderizar 10.000 itens trava UI. Use `react-window`, `react-virtual`, `TanStack Virtual`.

**Imagens não otimizadas.** PNG de 5MB onde WebP de 200KB serve. Sem `width`/`height` definidos → Cumulative Layout Shift (CLS) ruim. Use componentes de Next.js Image, ou `loading="lazy"` + dimensões.

**Bundle bloated:**
- Import errado: `import _ from 'lodash'` traz tudo. `import debounce from 'lodash/debounce'` traz só.
- Lib pesada para uso pequeno (`moment.js` 67kb para formatar 1 data → `date-fns` ou `Intl.DateTimeFormat`)
- Sem code splitting de rotas → primeiro load carrega o app inteiro

### UX states: loading, error, empty

Reviewers experientes pegam imediatamente: novo componente que faz fetch e só renderiza o sucesso. Os outros três estados são esquecidos:

1. **Loading** — usuário precisa saber que algo está acontecendo. Spinner, skeleton, indicador inline. Botão de submit deve desabilitar para evitar double-click.

2. **Error** — algo deu errado. Mensagem clara (não "An error occurred"), opção de retry, fallback se possível.

3. **Empty** — request retornou sucesso mas com lista vazia. Não mostrar lista vazia sem contexto — mostre "Nenhum item encontrado" com sugestão de ação ("Crie seu primeiro X").

4. **Success** — o estado que todo mundo lembra.

```js
// 🚨 — só pensa no happy path
const { data } = useQuery('users', fetchUsers)
return <List items={data} />  // crash se data undefined, lista vazia confusa

// ✅
const { data, isLoading, error } = useQuery('users', fetchUsers)
if (isLoading) return <Skeleton />
if (error) return <ErrorState onRetry={refetch} error={error} />
if (!data?.length) return <EmptyState message="Nenhum usuário ainda" />
return <List items={data} />
```

### Formulários

**Validação só no client.** Front é UX, mas backend é fonte de verdade. Sempre revalide no server.

**Submit duplicado.** Botão que não desabilita durante request → double-click cria duplicata. Sempre `disabled={isSubmitting}`.

**Feedback de erro de campo.** Erro genérico no topo é ruim — diga *onde* errou. Ainda melhor: marque o campo, descreva o erro abaixo dele, role para o primeiro erro automaticamente.

**Reset de form pós-submit.** Se foi criação, reset. Se foi edição, mantenha valores. Decida e seja consistente.

**Autosave vs explicit save.** Padrão escolhido deve ser óbvio para o usuário. Misto (alguns campos salvam ao perder foco, outros precisam de botão) é confuso.

### Roteamento / navegação

**Botão "Voltar" do browser.** O state da aplicação deve ser restaurado corretamente. Filtros aplicados, modais abertos, posição de scroll — decida o que é importante.

**Deep linking.** URLs devem ser stateful e compartilháveis. Filtros, paginação, tab ativo — geralmente devem estar na URL, não só no state.

**Loading bloqueando navegação.** Não pendurar `isLoading` global que trava toda navegação. Loading deve ser localizado.

### Side effects relacionados

**LocalStorage / sessionStorage:**
- Quota limitada (~5MB) — não dump de tudo
- Síncrono (bloqueia main thread) — não para dados grandes
- Sem expiração nativa — implemente TTL manual se relevante
- Vazamentos: dados de usuário antigo permanecem após logout → limpar explicitamente
- SSR: não disponível no server, código que assume window.localStorage explode

**Cookies:**
- Veja `security-review.md` para flags (Secure, HttpOnly, SameSite)
- Tamanho conta — cookies grandes são enviados em todo request

---

## Acessibilidade — onde reviewers backend falham

**96% dos sites têm violações WCAG detectáveis.** A maioria poderia ser pega em review. As coisas mais frequentes:

### Semântica

```html
<!-- 🚨 — não é clicável por teclado, screen reader não anuncia -->
<div onClick={handler}>Clicar</div>

<!-- ✅ -->
<button onClick={handler} type="button">Clicar</button>

<!-- ou se semântica é "link" (navegação) -->
<a href="/destination">Ir</a>
```

Toda interação clicável deveria ser `<button>` ou `<a>`. `<div onClick>` é forte sinal de pressa.

### Labels em form fields

```html
<!-- 🚨 -->
<input type="text" placeholder="Email" />

<!-- ✅ -->
<label htmlFor="email">Email</label>
<input id="email" type="text" />

<!-- ou label invisível: -->
<label htmlFor="search" className="sr-only">Buscar</label>
<input id="search" type="search" />
```

Placeholder NÃO é label — some quando digita, contraste tipicamente ruim, screen reader não consistente.

### Imagens

`<img alt="">` é correto para imagem decorativa (alt vazio explícito sinaliza "ignore"). `<img>` sem alt é violação.

Ícones com significado precisam de alternativa textual:
```jsx
<button aria-label="Fechar"><IconClose /></button>
```

### Hierarquia de headings

`<h1>` → `<h2>` → `<h3>` em ordem lógica. Não pular níveis ("h1 direto para h4 porque é o estilo que quero"). Estrutura ≠ estilo.

### Foco visível

`*:focus { outline: none }` no CSS sem alternativa é um dos piores anti-padrões. Foco precisa ser visível para quem usa teclado. Customize, mas não remova.

### Foco gerenciado em SPAs

Em navegação client-side, foco não é movido automaticamente como em page load real. Após mudança de rota, considere mover foco para o `<h1>` da nova página. Screen reader users perdem completamente o contexto sem isso.

### Modais e overlays

- Trap de foco dentro do modal enquanto aberto
- ESC fecha
- Foco retorna ao trigger ao fechar
- `aria-modal="true"` e `role="dialog"`
- Conteúdo abaixo (em DOM) tem `aria-hidden` enquanto modal está aberto

Use bibliotecas testadas (Radix UI, Headless UI, React Aria) em vez de implementar do zero — dá errado de muitas formas sutis.

### Contraste de cor

WCAG AA: 4.5:1 para texto normal, 3:1 para texto grande. Texto cinza claro em fundo branco é violação clássica.

### Texto que pode crescer

UI quebra com textos longos? Em outras línguas (alemão, finlandês) palavras são 30% mais longas. Testar com texto exagerado é prática barata.

### Status messages e live regions

Toast de sucesso/erro que aparece visualmente mas screen reader não anuncia → invisível para parte dos usuários. Use `role="status"` ou `aria-live="polite"`.

```jsx
<div role="status" aria-live="polite">
  {message}
</div>
```

---

## Bugs UX clássicos que reviewers experientes pegam

- **Scroll preservation:** voltar a uma lista preservou onde estava? Modal fechou recolocou foco?
- **Race entre clicks:** clicar rápido em 2 tabs diferentes → qual o estado final? Resposta antiga sobrescrevendo nova?
- **Cancelamento de operação:** usuário começou upload de 100MB, mudou de ideia. Tem como cancelar?
- **Reconexão após perda de internet:** o que aparece? Toast? Página em branco?
- **Modo escuro:** PR adicionou componente novo. Funciona em ambos os modos?
- **Mobile:** PR é "desktop-first". Como fica em viewport pequeno? Touch funciona?
- **i18n:** strings nuevas estão no sistema de tradução?
- **RTL:** se app suporta RTL, layout reverte corretamente?
- **Print:** página é imprimível decentemente?

---

## Checklist condensado

```
State
  [ ] Sem mutação direta de state?
  [ ] Estado no menor escopo necessário?
  [ ] Estado derivado calculado, não armazenado?
  [ ] Server state via lib de cache (não useState manual)?

Hooks
  [ ] useEffect tem deps corretas (linter exhaustive-deps ok)?
  [ ] Effects têm cleanup quando necessário?
  [ ] Race condition em fetch tratada (cancellation/cleanup)?
  [ ] Memoização (useMemo/useCallback) justificada, não preventiva?

Performance
  [ ] Sem re-renders óbvios (inline objects/functions desnecessários)?
  [ ] Listas grandes virtualizadas?
  [ ] Imagens com dimensões e otimizadas?
  [ ] Imports específicos para evitar bundle bloat?
  [ ] Code splitting de rota onde apropriado?

UX states
  [ ] Loading state explícito?
  [ ] Error state com retry?
  [ ] Empty state com guidance?
  [ ] Submit desabilita durante request?

Acessibilidade
  [ ] Elementos interativos são <button>/<a> (não <div onClick>)?
  [ ] Inputs têm <label> com htmlFor?
  [ ] Imagens com alt apropriado?
  [ ] Foco visível mantido?
  [ ] Modais com focus trap + ESC + retorno de foco?
  [ ] Status messages têm aria-live?

UX clássicos
  [ ] Scroll/foco preservados em navegação?
  [ ] Cancelamento possível em operações longas?
  [ ] Dark mode funciona (se app tem)?
  [ ] Mobile funciona?
  [ ] i18n não esquecido?
```
