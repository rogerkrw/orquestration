# Catálogo de bug patterns

Esta referência é o **olho treinado** de um reviewer sênior em formato consultável. Cada item descreve um padrão de código que dispara um alerta imediato em quem já o viu causar incidente real. Não é exaustivo — é o conjunto que paga mais dividendos.

Use-o como lente: ao ler o diff, escaneie procurando essas formas. Quando encontrar, faça a pergunta indicada — não acuse, investigue. Às vezes o autor tem contexto que justifica.

---

## Tratamento de erros e exceções

### Catch vazio ou que só loga
```python
try:
    do_something()
except Exception:
    pass  # 🚨 sumidouro silencioso
```
**Cheiro:** o sistema vai falhar em silêncio. Em produção, sob carga, vai degradar sem alerta. Variante igualmente ruim: `except Exception as e: logger.info(e)` — log em nível baixo, sem alertar, sem propagar.

**Pergunta:** "O que deveria acontecer se essa operação falhar? Quem precisa ser avisado? O fluxo precisa abortar ou pode seguir com fallback explícito?"

### Catch genérico engolindo erros específicos
Capturar `Exception` ou `Throwable` no nível alto faz com que bugs de programação (NullPointer, KeyError, IndexError) se misturem com erros operacionais esperados (timeout, conexão recusada). Diagnóstico vira impossível.

**Padrão correto:** capture tipos específicos no nível mais baixo que faz sentido. Deixe bugs de programação subirem até a borda do processo, que os loga e morre com clareza.

### Mensagem de erro que devolve informação sensível
`return f"User {email} not found"` no endpoint público vaza enumeração de usuários. Stack traces no response em produção vazam estrutura interna. Erros de DB com query embutida vazam schema.

**Pergunta:** "Esse erro chega ao cliente externo? Se sim, está sanitizado?"

### Empilhamento de try/except aninhados
Geralmente sinal de que o fluxo de erros não foi modelado. Cada catch tenta consertar localmente. Resultado: estados inconsistentes (operação A foi feita, B falhou, C nem tentou, e ninguém sabe o estado final).

**Pergunta:** "Qual é a unidade de trabalho atômica aqui? E o que define rollback?"

---

## Concorrência e ordem de operações

### Check-then-act sem atomicidade
```js
if (account.balance >= amount) {
  account.balance -= amount;
  await save(account);
}
```
**Por que quebra:** entre a leitura do balance e a escrita, outro processo lê o mesmo balance. Dois saques aprovados, balance negativo.

**Padrão correto:** lock pessimista, transação com `SELECT ... FOR UPDATE`, operação atômica no banco (`UPDATE ... WHERE balance >= ?`), ou versionamento otimista (`WHERE version = ?`).

### Lost update (read-modify-write)
Carregar entidade → mudar campo → salvar entidade inteira. Sem versão/timestamp na cláusula `WHERE`, a última escrita ganha — mesmo se baseada em estado antigo.

**Pergunta:** "Dois usuários editando o mesmo recurso ao mesmo tempo — qual é o comportamento esperado?"

### TOCTOU (Time-of-check vs time-of-use)
Verificar permissão / existência de arquivo / validade de token, então usar. Entre check e use, algo mudou. Especialmente perigoso em segurança.

### Ordem inconsistente de aquisição de locks
Thread A pega lock X depois Y. Thread B pega lock Y depois X. Deadlock determinístico.

**Padrão correto:** estabeleça uma ordem total de locks no sistema e respeite em todo lugar.

### Falta de timeout em chamada externa
HTTP request, query DB, RPC — sem timeout explícito, default geralmente é "infinito" ou "muito grande". Uma dependência lenta vira saturação de threads/conexões na sua app, depois cascata.

**Pergunta:** "Qual é o timeout configurado? E o que o cliente deveria fazer quando excedido?"

### Retry sem jitter (thundering herd)
Todos os clientes que falharam ao mesmo tempo retentam ao mesmo tempo, batendo no serviço a jusante exatamente quando ele está mais frágil.

**Padrão correto:** exponential backoff *com jitter* (aleatorização). Idealmente capping no máximo de tentativas e respeitando `Retry-After` se vier do servidor.

### Retry de operação não-idempotente
Retry de POST sem idempotency key duplica recursos/cobranças. Retry de DELETE pode ser ok (se já não existe, 404 e segue). Retry de PUT geralmente ok. POST sem chave é minado.

### Estado in-flight quando o processo morre
"E se o pod reiniciar no meio dessa operação?" Se a resposta é "perdemos o trabalho silenciosamente" ou "fica num estado inválido", há um problema. Padrões: outbox, jobs durables, transactional messaging.

---

## Banco de dados e queries

### N+1 queries
```python
posts = Post.objects.all()
for post in posts:
    print(post.author.name)  # 🚨 uma query por post
```
**Cheiro:** loop sobre coleção, acessando relação dentro do loop. Cresce linearmente com o dataset — funciona em dev (10 posts), engasga em produção (10k posts).

**Padrão correto:** eager load (`select_related`, `prefetch_related`, `JOIN`, `IN (...)`).

**Pergunta:** "Quantas queries isso vai gerar para uma página típica? Você rodou com `EXPLAIN` ou contador de queries?"

### Query sem index
Nova `WHERE` em coluna sem index, novo `ORDER BY`, novo `JOIN` em coluna não indexada. Funciona em dev com 1k linhas. Em prod com 10M linhas, full table scan, latência sobe, locks aumentam.

**Pergunta:** "Tem index cobrindo esse predicado? Foi rodado `EXPLAIN`?"

### `SELECT *` em hot path
Trazer colunas não usadas custa rede, memória e quebra implicitamente quando schema muda.

### `LIMIT` sem `ORDER BY`
Sem `ORDER BY`, o banco pode retornar qualquer N linhas, não-deterministicamente. Paginação fica corrompida silenciosamente.

### Paginação por OFFSET em datasets grandes
`OFFSET 100000 LIMIT 20` faz o banco ler 100020 linhas e descartar 100000. Quanto mais fundo a paginação, mais lento. Use **cursor-based pagination** (`WHERE id > last_id ORDER BY id LIMIT 20`).

### Transação longa
Transação que dura segundos segura locks, esgota pool de conexões, cria fila. Especialmente ruim em migrations que rodam DDL dentro de transação.

### Migration sem `IF NOT EXISTS` / não-reentrante
Se a migration roda parcialmente e dá retry, falha pela segunda vez por já existir o objeto. Migrations devem ser idempotentes.

### Migration que adiciona NOT NULL sem default e sem backfill
Em produção com dados existentes, vai quebrar a constraint. Padrão correto: 1) adicionar coluna nullable, 2) backfill em batches, 3) tornar NOT NULL.

### Migration que renomeia/dropa coluna ainda usada por release antiga
Durante rolling deploy, versões antigas e novas convivem. Drop só após código antigo estar fora.

### Falta de constraint de unicidade quando deveria existir
Validação só na aplicação (`if not User.objects.filter(email=email).exists(): create()`) é race condition. Constraint UNIQUE no banco é a única garantia.

### Foreign key sem ON DELETE definido
Default varia por banco. Pode deletar em cascata coisas que não deveria, ou bloquear deletes legítimos, ou deixar órfãos.

---

## Validação de input e fronteiras de confiança

### Confiar em validação client-side
Validação no front é UX, não segurança. Sempre revalide no backend. Toda fronteira de confiança precisa de sua própria validação.

### Mass assignment
```js
const user = await User.create(req.body);  // 🚨
```
`req.body` pode incluir campos como `role: 'admin'` que o usuário não deveria poder setar. Use allowlist explícita de campos.

### String concat em query SQL/LDAP/NoSQL/comando shell
Qualquer concatenação de input do usuário em qualquer linguagem de consulta é injection. **Sempre** use parameterização/prepared statements. Sem exceções "porque é só para query interna".

### Path traversal
`open(f"/uploads/{user_filename}")` permite `../../etc/passwd`. Normalize e valide o path resultante. Para uploads, use UUIDs gerados pelo servidor, não nome do usuário.

### SSRF (Server-Side Request Forgery)
Endpoint que aceita URL do usuário e faz request para ela. Sem allowlist, atacante manda você bater em `http://169.254.169.254/` (cloud metadata) ou em serviços internos.

### Deserialização de input não-confiável
Pickle, YAML.load (vs safe_load), Java deserialization com classes desconhecidas — execução remota de código clássica.

### Falta de rate limiting em endpoints sensíveis
Login, password reset, signup, qualquer endpoint que envia email/SMS, qualquer endpoint custoso. Sem rate limit, brute force / abuse é trivial.

---

## Autenticação e autorização

### Autorização ausente ou no lugar errado
**Sintoma típico:** endpoint pega `userId` do path ou body em vez de do contexto de autenticação. Atacante troca o ID e acessa dados de outros.

**Pergunta-teste:** "Se eu trocar `userId=123` por `userId=456` no request, o que acontece?"

### IDOR (Insecure Direct Object Reference)
`GET /api/orders/42` retorna order 42 sem verificar se o usuário logado é dono. Use sempre filtros por owner no nível da query, não como `if order.owner != current_user: 403` depois.

### Comparação de string sensível a timing
`if token == expected_token:` em alguns runtimes vaza informação por timing. Use `constant_time_compare` / `hmac.compare_digest`.

### Hash de senha fraco ou ausente
MD5, SHA1, SHA256 puro são inadequados para senhas. Use bcrypt, scrypt ou argon2 com cost factor adequado.

### Token sem expiração / sem revogação
JWT com `exp` muito longo e sem mecanismo de revogação: se vazar, atacante tem acesso por meses. Use TTLs curtos e refresh tokens revogáveis.

### Segredos hardcoded
API keys, tokens, senhas, connection strings no código. Mesmo em "código de teste" — eles acabam em git history. Use variáveis de ambiente / secret manager.

### CORS permissivo demais
`Access-Control-Allow-Origin: *` com `Allow-Credentials: true` é inválido pela spec, mas pior: indica que o autor não pensou no problema. Liste origins explicitamente.

---

## API e contratos

### Status code semanticamente errado
- `200 OK` com `{"error": "..."}` no body → faz qualquer middleware de retry/monitoring achar que deu certo
- `200` quando devia ser `201` para criação, `204` para no content
- `500` para erro do cliente (validação inválida) → polui métricas de saúde

### Quebra de backward compatibility silenciosa
- Removendo campo de response
- Mudando tipo de campo (`id: number` → `id: string`)
- Tornando campo opcional → obrigatório no request
- Mudando significado de enum existente

**Pergunta:** "Quais clientes consomem esse contrato? Qual a estratégia de versionamento?"

### Inconsistência de envelope de erro
Alguns endpoints retornam `{"error": "..."}`, outros `{"message": "..."}`, outros `{"errors": [...]}`. Clientes não conseguem tratar uniformemente. Adote um padrão (RFC 7807 Problem Details é bom default) e mantenha.

### Endpoint que retorna lista sem paginação
`GET /api/users` que retorna *todos* os usuários. Funciona em dev com 50 usuários. Mata em produção com 500k. Toda lista precisa de paginação desde o dia 1.

---

## Frontend e UI

### Mutação direta de state
```js
state.items.push(newItem)  // 🚨 React não vai re-renderizar
setState(state)
```
Em React/Redux/Vue, mutação direta quebra detecção de mudança. Use imutabilidade: `setState([...state.items, newItem])`.

### useEffect sem deps ou com deps erradas
- Sem array de deps: roda em todo render → loop ou perf horrível
- Array vazio com referência a state/prop atual → stale closure (usa valor velho)
- Faltando dependência: bug invisível

### Vazamento de listener / subscription / timer
```js
useEffect(() => {
  window.addEventListener('resize', handler)
  // 🚨 sem cleanup → memory leak conforme component remonta
})
```
Sempre retorne cleanup function.

### Form sem estado de erro/loading
Botão de submit que não desabilita durante request → double submit. Sem indicador de loading → usuário acha que travou e clica de novo. Sem mensagem de erro → silêncio confuso.

### Estado pertencente ao server tratado como local
Manter cópia local de dados do server e tentar sincronizar manualmente → infinitas race conditions. Use React Query / SWR / RTK Query, que tratam cache/refetch/invalidate.

### onClick em `<div>` em vez de `<button>`
Não é acessível por teclado, não é anunciado por screen reader, não tem foco visível. Use elementos semânticos. Veja `frontend-review.md` para acessibilidade.

### Texto hardcoded onde deveria ter i18n
Em produtos multilíngues, qualquer string nova precisa entrar no sistema de tradução. Pegar essas no review economiza ciclos.

---

## Performance e recursos

### Loop O(n²) em coleção que vai crescer
`.find` dentro de `.map`, `.filter().forEach` aninhado. Funciona em 100 itens, lenta em 10k.

### Carregar coleção inteira para contar / filtrar / agregar
`users = User.objects.all(); count = len(users)` quando `User.objects.count()` resolve no banco.

### String concatenation em loop (linguagens com strings imutáveis)
Em Java/Python/JS, concatenar string num loop é O(n²). Use builder/join.

### Memory leak de cache sem limite
`cache = {}` que cresce indefinidamente. Use LRU com tamanho máximo, ou TTL.

### Cálculo pesado em render (frontend)
Cálculo de derivado dentro do render sem memoização. A cada re-render refaz tudo. `useMemo` quando vale a pena.

### Imagem/asset não otimizado
PNG de 5MB onde JPG/WebP de 200KB serviria. Sem `width/height` no `<img>` → CLS (Cumulative Layout Shift) terrível.

### Bundle bloated por import errado
`import _ from 'lodash'` traz a lib inteira. `import debounce from 'lodash/debounce'` traz só o necessário.

---

## Tempo, dinheiro, encoding — os "óbvios" que pegam todo mundo

### Comparação de datas com strings
`if date1 > date2` quando date1 e date2 são strings ISO funciona *só* se formato é exatamente o mesmo e em UTC. Caso contrário, comportamento subtilmente errado.

### Timezone ignorado
Salvar `datetime.now()` sem tz, comparar com horário do usuário em outro tz, exibir hora errada. Sempre armazene UTC, converta na borda.

### Float para dinheiro
`0.1 + 0.2 !== 0.3`. Use inteiros (centavos) ou tipo decimal apropriado da linguagem. Discrepâncias de R$ 0,01 acumulam.

### Off-by-one em paginação / range
`for (let i = 0; i <= length; i++)` em vez de `<`. `LIMIT` vs `OFFSET` invertidos. Página 0 vs página 1 inconsistente entre back e front.

### Encoding errado / falta de UTF-8
Banco em latin1, app em utf-8: emojis e acentos viram `?` ou mojibake. Falta de normalização Unicode causa "mesma string" não bater no equality.

### Falta de validação de tamanho máximo
Body sem limite → request de 1GB derruba a app. Campo de texto sem max length → DoS por abuse. Upload sem cap → disco cheio.

---

## Sinais de "AI gerou e ninguém revisou de verdade"

Padrões que delatam código gerado e aprovado sem entendimento:

- **Try/catch que captura `Error` e re-lança como `Error` genérico** (perde stack/contexto)
- **Comentários redundantes que repetem o nome da função em palavras** (`// Function that gets the user → function getUser()`)
- **Validações duplicadas** em camadas diferentes sem coordenação
- **Imports não usados** ou imports de mesma coisa duas vezes (de paths diferentes)
- **Inconsistência sutil de estilo** dentro do mesmo arquivo (autor mudou de modelo no meio)
- **Otimização prematura "best practices" sem justificativa** (memoização agressiva, abstrações genéricas)
- **Boilerplate de teste que só testa que mocks foram chamados**
- **TODO genéricos sem assunto** (`// TODO: handle this`)
- **100% de cobertura em coisa trivial, 0% em lógica crítica**

**Para PRs de AI:** peça ao autor para explicar em uma frase por que escolheu *essa* abordagem em vez de outra simples. Se não conseguir, o review não deveria seguir até a explicação aparecer.
