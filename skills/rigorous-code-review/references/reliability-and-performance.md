# Reliability & Performance review

Esta referência cobre os problemas que **não aparecem em dev**, mas que derrubam produção: concorrência, falhas em cadeia, latência sob carga, idempotência, e como o sistema se comporta quando algo dá errado.

A regra-mãe deste documento: **o happy path é o trabalho fácil; reviewers senior gastam 70% da atenção no que acontece quando *algo* dá errado.**

---

## Concorrência

Concorrência é onde reviewers senior pisam o freio. Bugs aqui são intermitentes, dependentes de timing, irreproduzíveis em dev e devastadores em prod. Se o diff toca código concorrente (threads, async/await sobre estado compartilhado, jobs em paralelo, múltiplas réplicas), a barra de revisão sobe.

### Race condition em check-then-act

Toda lógica "olha o estado, decide com base nele, modifica o estado" sem atomicidade é candidata.

**Onde aparece:**
- Verificação de saldo antes de débito
- Verificação de estoque antes de venda
- Decisão "criar se não existe" (race entre dois processos)
- Reservas, lock de assento, primeira-vez-de-algo
- Counters incrementados manualmente

**Padrões corretos (em ordem de preferência):**
1. Operação atômica no banco: `UPDATE account SET balance = balance - ? WHERE id = ? AND balance >= ?`
2. Transação com `SELECT ... FOR UPDATE` (lock pessimista)
3. Versão otimista: `UPDATE ... WHERE id = ? AND version = ?` + retry no client
4. Constraint UNIQUE no banco para "primeira vez ganha"
5. Lock distribuído (Redis, Zookeeper) — último recurso, tem seus próprios bugs

**Pergunta no review:** "Dois requests chegando no mesmo milissegundo — qual o comportamento esperado e por que esse código garante isso?"

### TOCTOU

Time-of-check vs time-of-use. Verificar uma condição e usar a verificação depois — entre uma coisa e outra, o estado pode ter mudado.

```python
if os.path.exists(filename):
    open(filename)  # 🚨 arquivo pode ter sido deletado entre o check e o open
```

Padrão correto: tentar a operação e tratar o erro, não pré-validar.

### Lost update

Read-modify-write sem versão / lock:
```
Thread A: lê user (name=Alice, age=30)
Thread B: lê user (name=Alice, age=30)
Thread A: escreve (name=Alice, age=31)
Thread B: escreve (name=Bob, age=30)  → Thread A perdeu
```

A correção é a mesma: versão otimista ou lock.

### Deadlock por ordem inconsistente de aquisição

```
Thread A: lock X, então lock Y
Thread B: lock Y, então lock X
→ Deadlock
```

Esse é específico de cada projeto: precisa de uma convenção de ordem total para aquisição. Quando ver código pegando múltiplos locks, pergunte se a ordem é a convencional do projeto.

### Estado in-flight em crash

Pergunta-teste poderosa: **"E se o processo morrer no meio dessa operação, em que estado o sistema fica?"**

- Money transferido da conta A mas não creditado na conta B → inconsistência
- Job processado mas não marcado como done → reprocessamento duplicado
- Email enviado mas não logado → spam para usuário ao retry

Padrões:
- **Outbox pattern:** persistir intent na mesma transação que muda dados, processar outbox idempotentemente
- **Two-phase commit-light:** marcar como "pending", fazer, marcar como "done"
- **Jobs idempotentes** com retry seguro

---

## Performance e escalabilidade

### N+1 queries (o clássico que ainda mata)

```python
# 🚨
posts = Post.objects.all()
for post in posts:
    for comment in post.comments.all():
        print(comment.author.name)
# → 1 query para posts, N para comments, N×M para authors
```

**Como detectar no review:**
- Loop sobre coleção (`for`, `.map`, `.forEach`)
- Acesso a relação ou atributo lazy dentro do loop
- Função utilitária chamada em loop que faz query

**Pergunta:** "Quantas queries isso dispara para uma página típica? Você verificou com query logger / `EXPLAIN`?"

**Correção:** eager loading (`select_related`, `prefetch_related`, `JOIN`, `IN (...)`). Em ORMs modernos, geralmente `User.objects.prefetch_related('posts__comments__author')`.

### Query sem index

Nova `WHERE` em coluna não indexada, novo `ORDER BY`, novo `JOIN`. Em dev com 1k rows: instantâneo. Em produção com 10M rows: full table scan, latência sobe, locks aumentam, downstream sofre.

**Sinais no diff:**
- Migration adiciona coluna nova
- Query filtra por essa coluna ou faz JOIN nela
- Nenhum `CREATE INDEX` correspondente

**Pergunta:** "Esta coluna tem index? Foi rodado `EXPLAIN` na query mais crítica que a usa?"

### Paginação por OFFSET grande

```sql
SELECT * FROM events ORDER BY created_at DESC OFFSET 100000 LIMIT 20
```

O banco lê e descarta 100000 linhas. Quanto mais profunda a paginação, mais lento. Funciona para listagens curtas, é insustentável para "infinite scroll" / exportações.

**Correção:** cursor-based — `WHERE id < last_seen_id ORDER BY id DESC LIMIT 20`. O cliente envia de volta o último cursor visto.

### `SELECT *` em hot path

- Trafega colunas desnecessárias na rede
- Aumenta uso de memória / cache
- Quebra "silenciosamente" quando schema muda (nova coluna pesada)
- Em alguns DBs, perde otimizações de covering index

Use lista explícita de colunas em queries críticas.

### Transação longa demais

Transação aberta enquanto se faz I/O externo (API call, leitura de arquivo grande, espera de mensagem) trava locks no banco e esgota pool de conexões.

**Padrão correto:** transações pequenas, focadas, sem chamadas externas no meio.

### Carregar coleção inteira para agregação trivial

```python
all_users = User.objects.all()
total = sum(u.balance for u in all_users)  # 🚨 traz N rows, calcula em memória
# ✅
total = User.objects.aggregate(Sum('balance'))['balance__sum']
```

### Loop O(n²) onde O(n) é possível

```js
// 🚨
const dupes = list.filter((x, i) => list.findIndex(y => y.id === x.id) !== i)
// ✅
const seen = new Set()
const dupes = list.filter(x => seen.has(x.id) ? true : (seen.add(x.id), false))
```

Em dataset pequeno é igual. Em dataset grande é a diferença entre "rápido" e "trava".

### Sync I/O bloqueando event loop (Node.js)

`fs.readFileSync`, `crypto.pbkdf2Sync` em qualquer hot path bloqueia o event loop e mata throughput.

### Cálculo pesado no main thread (browser)

Operação síncrona pesada (parse de JSON gigante, regex sobre texto enorme, criptografia) trava a UI. Considere Web Workers para offload.

### Cache sem TTL ou sem limite de tamanho

Cache crescendo indefinidamente é memory leak. LRU bound ou TTL.

---

## Chamadas externas (API, RPC, mensageria)

Toda chamada de rede falha eventualmente. Como o código reage importa mais que como ele funciona quando dá certo.

### Falta de timeout

`fetch(url)` sem timeout, `requests.get(url)` sem `timeout=`, cliente RPC com default infinito. Resultado: uma dependência lenta segura sua thread / conexão indefinidamente. Sob carga, cascata.

**Pergunta:** "Qual é o timeout? E o que o caller faz quando dispara?"

**Default razoável:** connect timeout ~2s, read timeout dimensionado pelo p99 esperado × 1.5-2.

### Retry sem exponential backoff e jitter

Cliente que retenta imediatamente em loop:
- Bate em servidor já em apuros, piora a situação
- Quando o servidor volta, *todos* os clientes batem ao mesmo tempo (thundering herd)

**Padrão correto:**
- Exponential backoff (1s, 2s, 4s, 8s, ...)
- Jitter (aleatorização em ±25%) para descorrelacionar clientes
- Cap no número de tentativas
- Respeitar `Retry-After` se o servidor mandar

### Retry de operação não-idempotente

POST sem idempotency key, retentado → duplicação de recurso/cobrança.

**Padrões:**
- Cliente gera UUID por intenção, manda em `Idempotency-Key` header
- Servidor armazena hash da resposta para essa chave por TTL
- Retry com mesma chave retorna mesma resposta

### Falta de circuit breaker

Quando um serviço externo está caindo, continuar batendo em loop é desperdício e propaga falha. Circuit breaker (após N falhas, "abre" e falha rápido por X tempo) protege.

### Bulkhead ausente

Uma chamada externa lenta consumindo todas as conexões do pool deixa outras operações sem recurso. Separar pools por dependência (bulkhead pattern).

---

## Falhas em cadeia e degradação graceful

### O que acontece quando a dependência X cai?

Para cada dependência (DB, cache, fila, serviço A, serviço B), o reviewer deve mentalmente perguntar:

1. **Cliente vê:** erro 500? Erro 503 com mensagem útil? Degradação parcial (algumas features off)?
2. **Outras operações continuam funcionando?** Ou um endpoint caído derruba todos?
3. **Sistema se recupera sozinho** quando a dependência volta? Ou requer reinício?

### Anti-padrões clássicos

- Cache miss → DB sobrecarregado → tudo lento → mais cache misses → death spiral
- "Quick fix" de catchar Exception e retornar `[]` ou `null` → bug se propaga silencioso
- Health check que responde "OK" mesmo com dependência crítica caída → load balancer manda tráfego pra pod morto

---

## Idempotência e exactly-once thinking

Sistemas distribuídos não conseguem "exatamente uma vez" sem cooperação. As únicas formas reais:

- **At-most-once:** envia, esquece. Pode perder. OK para métricas, log analytics.
- **At-least-once + idempotência no consumidor:** envia, retenta se necessário, consumidor reconhece duplicatas. É o padrão usável para a maioria.

### Sinais de que idempotência não foi pensada

- POST que cria recurso sem chave de idempotência
- Webhook handler sem dedup de evento (mesmo evento entregue 2x → ação 2x)
- Job de fila sem checar se já foi processado
- Increment em counter sem operação atômica

**Pergunta:** "Se este consumer receber a mesma mensagem duas vezes, o resultado é diferente?"

---

## Migrations e backward compatibility

Migrations em produção são uma das categorias mais perigosas de PRs. O sistema está rodando, tráfego está vivo, você está mudando schema. Erros aqui não são reversíveis facilmente.

### Padrão "expand-contract" (rolling-safe)

Toda mudança de schema breaking deve ser feita em passos compatíveis com rolling deploy:

**Adicionando coluna NOT NULL:**
1. Adicionar coluna *nullable* com default (release N)
2. Backfill em batches (job offline)
3. Tornar NOT NULL (release N+1)

**Renomeando coluna:**
1. Adicionar nova coluna
2. Código escreve em ambas, lê preferindo nova
3. Backfill
4. Código lê só da nova
5. Drop da velha (vários releases depois)

**Dropando coluna:**
1. Código para de usar
2. Espera deploys completarem
3. Drop em release separada

**Mudando tipo:**
1. Adicionar nova coluna com novo tipo
2. Backfill
3. Cutover de leitura/escrita
4. Drop velha

### Outros sinais de problema em migrations

- DDL pesado dentro de transação (segura lock muito tempo em DBs sem DDL transactional limpo)
- Backfill grande sem batching → trava banco
- Index novo criado sem `CONCURRENTLY` (Postgres) → table lock
- Constraint adicionada `NOT VALID` esperada virar `VALIDATE` depois mas o "depois" foi esquecido
- Falta de DOWN migration ou rollback documentado

### Compatibilidade de API

Mudanças contratuais que quebram clientes existentes silenciosamente:

- Remover campo de response
- Mudar tipo (`number` → `string`)
- Tornar campo opcional do request em obrigatório
- Mudar semântica de enum
- Tornar response paginado quando não era

Veja `api-and-data-review.md` para o framework completo.

---

## Observabilidade — o que verificar no diff

Reviewers experientes sabem que código que não pode ser depurado em produção é código com bug invisível.

### Logging

- **Estruturado:** key-value (JSON ou logfmt), não strings concatenadas. Permite query.
- **Correlation ID / trace ID** propagado em chamadas externas. Sem isso, impossível seguir um request entre serviços.
- **Log em pontos de falha**, não só no happy path. Failure log com contexto suficiente para reproduzir.
- **Nível certo:** ERROR para coisas que precisam de atenção, WARN para anomalia recuperável, INFO para eventos importantes, DEBUG para diagnóstico.
- **Sem secrets/PII.** Cuidado especial com dumping de objetos de request inteiros (Authorization header, body com senha, etc).

### Métricas

Para todo endpoint / job / operação importante:
- Counter de chamadas (total, por status)
- Histograma de latência (p50, p95, p99)
- Counter de erros (com label de tipo de erro)

### Tracing

Para chamadas externas, instrumente com tracing distribuído. Sem isso, debugging de latência em produção é arqueologia.

### Alerting

- **Alerte em sintomas, não em causas.** "Error rate > X" é sintoma. "CPU > 80%" é causa que pode ou não importar.
- **Alerte em SLO violation**, não em "qualquer erro". Ruído de alerta gera fadiga, que gera incidentes ignorados.

---

## Checklist condensado

```
Concorrência
  [ ] Estado compartilhado tem proteção (lock/transação/atomic)?
  [ ] Check-then-act foi convertido para operação atômica?
  [ ] Ordem de aquisição de locks é consistente?
  [ ] "E se o processo morrer aqui?" tem resposta clara?

Performance / DB
  [ ] Sem N+1 (eager loading onde apropriado)?
  [ ] Toda nova query tem index cobrindo?
  [ ] Paginação é cursor-based para listas longas?
  [ ] Sem SELECT * em hot path?
  [ ] Transações são curtas, sem I/O externo?

Chamadas externas
  [ ] Timeout configurado (connect e read)?
  [ ] Retry com backoff + jitter?
  [ ] Idempotency key em POSTs retryáveis?
  [ ] Circuit breaker onde faz sentido?

Falha graceful
  [ ] "Se a dependência X cai, o que acontece?" tem resposta?
  [ ] Sem catch que engole e retorna valor default silencioso?
  [ ] Health check reflete dependências críticas?

Migrations
  [ ] É expand-contract (não breaking direto)?
  [ ] Tem backfill plan se afeta dados existentes?
  [ ] Indexes criados CONCURRENTLY (se Postgres)?
  [ ] Drop de coluna/tabela só depois de release que parou de usar?

Observabilidade
  [ ] Logs estruturados com correlation ID?
  [ ] Log nos pontos de falha, não só happy path?
  [ ] Métricas para novos endpoints/jobs?
  [ ] Sem secrets/PII em logs?
```
