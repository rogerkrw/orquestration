# API & data review

Esta referência cobre revisão de **contratos** (REST, GraphQL, RPC, webhooks), **persistência** (schema, migrations, transações) e **integridade de dados**. Esses são os pedaços do sistema mais difíceis de mudar depois — erros aqui se propagam por todos os clientes e por todo o histórico de dados.

A regra: contratos e schema são **decisões duradouras** que ficam muito caras de reverter. Trate o review desses PRs com mais rigor que features puramente internas.

---

## Review de APIs REST

### Resource naming

- Use **substantivos no plural** (`/users`, `/orders`), não verbos
- Hierarquia reflete relação real (`/users/{id}/orders` se orders são *de* user)
- Evite verbos no path (`/getUser`, `/createOrder`) — use método HTTP
- Casos onde "ação" não é CRUD pura: `POST /users/{id}/password-reset`, `POST /orders/{id}/cancel` — substantivize a ação se possível

### HTTP methods semanticamente corretos

| Método | Semântica | Idempotente? |
|---|---|---|
| GET | Leitura | Sim |
| POST | Cria recurso ou ação não-idempotente | Não |
| PUT | Substituição completa | Sim |
| PATCH | Atualização parcial | Geralmente sim (depende do design) |
| DELETE | Remoção | Sim |

**Sinal de problema:**
- GET que muda estado (`GET /api/jobs/run`) — pior, vai ser chamado por bots, prefetchers, etc.
- POST para tudo (não usa PUT/DELETE) — não-RESTful, mas tolerável se consistente

### Status codes — usar com semântica, não como decoração

**Sinais de uso errado:**
- `200 OK` com `{"error": "..."}` no body → middleware de retry/monitoramento acha que deu certo
- `500 Internal Server Error` para erro de validação do cliente → polui métricas de saúde, é confuso
- `404` para autorização negada → ok para esconder existência, mas seja consistente; `403` é mais honesto na maioria
- `200` para criação (devia ser `201`)
- `200` quando não há body (devia ser `204`)

**Tabela rápida:**

| Código | Quando usar |
|---|---|
| 200 | GET/PUT/PATCH com body de resposta, sucesso |
| 201 | POST criou recurso (com `Location` header apontando) |
| 204 | Sucesso sem body (DELETE típico) |
| 400 | Validação falhou (incluir detalhes no body) |
| 401 | Não autenticado |
| 403 | Autenticado, sem permissão |
| 404 | Recurso não existe |
| 409 | Conflito (versão obsoleta, duplicate) |
| 422 | Semanticamente inválido (sintático OK) |
| 429 | Rate limit (incluir `Retry-After`) |
| 500 | Bug do servidor (não esperado) |
| 502/503/504 | Problema com dependência ou indisponibilidade |

### Envelope de erro consistente

Adote um padrão e siga. **RFC 7807 Problem Details** é o default razoável:

```json
{
  "type": "https://example.com/probs/insufficient-balance",
  "title": "Insufficient balance",
  "status": 422,
  "detail": "Account balance of 50 cannot cover transfer of 100",
  "instance": "/transfers/abc-123"
}
```

Para validação multi-campo, considere estrutura padronizada para listar erros por campo.

**Sinal de problema:** PR introduz endpoint que retorna `{"error": "..."}` enquanto o resto da API usa `{"message": "...", "code": "..."}`. Pergunte por que.

### Paginação

Toda lista deve ser paginada **desde o dia 1**. Não importa se "só vão ter 10 itens" — produtos crescem.

**Offset-based:** `?page=2&size=20` ou `?offset=20&limit=20`
- Fácil de entender, suporta navegação direta para página N
- Mas: ineficiente para offsets grandes, e itens podem ser duplicados/perdidos durante mudança

**Cursor-based:** `?cursor=eyJpZCI6MTIzfQ&limit=20`
- Performático em qualquer profundidade
- Consistente durante inserções
- Mas: não permite "ir para página 7" diretamente

Para listas que podem ficar grandes ou tempo real, prefira cursor.

**Sinal de problema:** novo endpoint que retorna array sem paginação → pergunte como vai escalar.

### Idempotência para POSTs

Para POSTs que criam recursos ou efeitos colaterais (pagamento, envio de email, criação de ordem), suporte chave de idempotência:

```
POST /orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{...}
```

Servidor armazena hash da resposta por TTL (24-48h é comum). Retry com mesma chave retorna mesma resposta sem re-executar.

### Versionamento

Estratégias comuns:
- **URL path:** `/v1/users`, `/v2/users` — explícito, fácil de roteamento
- **Header:** `Accept: application/vnd.example.v2+json` — limpo, mas menos visível
- **Query string:** `/users?version=2` — não-RESTful, evite

A questão real não é "qual estratégia" mas "qual é a política de breaking change":
- Suportamos quantas versões em paralelo?
- Como anunciamos deprecação?
- Como medimos uso de versões antigas antes de remover?

### Cache headers / ETags

Para recursos lidos com frequência:
- `Cache-Control: private, max-age=60` — controle de cache do cliente
- `ETag` + `If-None-Match` — 304 Not Modified evita re-baixar
- `Last-Modified` + `If-Modified-Since` — alternativa mais grosseira

Especialmente importante para mobile (latência + dados).

### Rate limiting

Endpoints públicos ou caros precisam de rate limiting. Quando retornar 429, inclua:
- `Retry-After: <seconds>`
- `X-RateLimit-Limit: <max>`
- `X-RateLimit-Remaining: <remaining>`
- `X-RateLimit-Reset: <unix timestamp>`

---

## Review de schemas e migrations

Migrations em produção são uma das categorias mais perigosas de PRs. Veja `reliability-and-performance.md` para padrões de migration rolling-safe. Aqui foco em **review do diff de migration**.

### O que olhar em um diff de migration

**Reversibilidade.** Existe `down` migration? Foi testada? Para migrations destrutivas (DROP), uma `down` perfeitamente reversível pode ser impossível — nesse caso documente claramente.

**Tempo de execução estimado.** Migration que toca milhões de linhas em uma transação pode bloquear o banco por minutos. Estimativa:
- Se < 1 minuto → ok rodar inline
- Se 1-10 minutos → considere janela de baixo tráfego
- Se > 10 minutos → backfill como job offline batched, separado da migration de schema

**Locks adquiridos.** Em Postgres:
- `ALTER TABLE ... ADD COLUMN` com default → lock pesado (em versões antigas)
- `ALTER TABLE ... ADD COLUMN nullable` → lock leve
- `CREATE INDEX` → lock que bloqueia writes; use `CREATE INDEX CONCURRENTLY`
- `ALTER TABLE ... ADD CONSTRAINT NOT VALID` + `VALIDATE CONSTRAINT` em passo separado → menor impacto

Em MySQL: comportamento varia por engine e versão; online DDL para InnoDB ajuda mas tem caveats.

**Backward compatibility com código atualmente em produção.** Durante rolling deploy, código antigo e novo convivem. Migration:
- ✅ Adicionar coluna nullable → código antigo ignora
- ✅ Adicionar tabela nova → código antigo não usa
- ❌ Dropar coluna ainda lida pelo código antigo → quebra
- ❌ Renomear coluna → código antigo quebra

Quando é breaking, o padrão expand-contract resolve:
1. Add new (deploy)
2. Migrate data
3. Update code to use new (deploy)
4. Drop old (deploy posterior)

### Constraints e integridade

**Foreign keys.** Toda relação que *deve* existir merece FK no banco — não só validação na app. Validação no DB é a única que sobrevive a bugs da app e a inserções via console.

- `ON DELETE`: defina explicitamente (`CASCADE`, `SET NULL`, `RESTRICT`) — não confie no default
- Considere o custo: FKs criam locks em inserts em tabela filha

**Unique constraints.** Se a regra é "não pode ter duplicata", a regra precisa estar no DB. `UNIQUE INDEX` é a única garantia contra race conditions.

**Check constraints.** Use para invariantes simples (idade > 0, status in (...), etc.). Reduz dependência de validação na aplicação.

**NOT NULL.** Default é NOT NULL onde possível. Nullable significa "esse campo pode estar ausente e isso tem significado" — tem que ser intencional.

### Indexes — sinais a procurar

**Index novo necessário:**
- Migration adiciona coluna usada em `WHERE`/`JOIN`/`ORDER BY`
- Sem `CREATE INDEX` correspondente → query vai full table scan

**Index supérfluo:**
- Index numa coluna com baixa cardinalidade (e.g., boolean) raramente ajuda
- Index duplicado por outro (composite que cobre)
- Indexes degradam writes; tenha justificativa para cada um

**Index para uniqueness:** UNIQUE INDEX serve dois propósitos — restrição + performance.

### Tipos de dados

- **Datas:** `TIMESTAMP WITH TIME ZONE` em Postgres, `TIMESTAMP` em MySQL UTC. Nunca string ISO em coluna varchar.
- **Dinheiro:** `DECIMAL(precision, scale)` ou inteiros (centavos). Nunca FLOAT.
- **UUID:** `UUID` nativo (Postgres) ou `BINARY(16)` (MySQL). Não varchar (lento, indexação ruim).
- **Enums:** prefira string + check constraint em vez de tipo ENUM nativo (mais fácil de evoluir).
- **JSON:** ok para dados realmente schemaless, mas perde validação, dificulta query. Não use só para "ser flexível".

### Dados sensíveis

PII / dados sensíveis em colunas novas precisam de:
- Decisão sobre necessidade (princípio da minimização)
- Criptografia em repouso (KMS, TDE, ou app-level)
- Política de retenção e expurgo
- Auditoria de acesso
- Exclusão sob LGPD/GDPR — como?

---

## Review de transações

### Boundaries

Toda transação tem um boundary claro: começa aqui, termina ali. No review, identifique:

- Onde a transação abre e fecha?
- Tudo dentro está mesmo na transação? (Erro comum: query fora do bloco transacional achando que está dentro.)
- I/O externo (API calls, file I/O) dentro de transação? **Bandeira vermelha.** Mantém lock enquanto faz request lento → esgota pool.

### Isolation level

- READ COMMITTED é default em Postgres — ok para maioria, mas vulnerável a lost updates sem versão
- REPEATABLE READ ou SERIALIZABLE para operações sensíveis (transferências, contadores)
- Se o autor não escolheu nível explicitamente, qual é o default e está adequado?

### Locks

- `SELECT ... FOR UPDATE` é lock pessimista — funciona, mas reduz concorrência
- Versão otimista (`WHERE version = ?`) escala melhor mas requer retry no client
- Ordem consistente de aquisição de locks evita deadlocks

### Retry de transação

Conflitos de serialização e deadlocks são esperados em DBs sob carga. Código que abre transação deve estar preparado para retry:

```python
for attempt in range(max_retries):
    try:
        with transaction.atomic():
            # ...
        break
    except SerializationError:
        if attempt == max_retries - 1:
            raise
        sleep_with_jitter()
```

---

## GraphQL — especificidades

Se o diff toca GraphQL, padrões extras a verificar:

**N+1 via lazy resolvers.** Resolver que carrega related field para cada parent → exatamente o N+1 clássico, agravado por GraphQL permitir queries arbitrárias. Use **DataLoader** ou equivalente para batch.

**Query complexity / depth limit.** Sem limite, cliente pode mandar query maliciosa de profundidade 50 e travar o servidor. Limite query depth e/ou complexity.

**Authorization por field.** REST tem o privilégio de ter uma "rota" para autorizar. GraphQL não — cada campo sensível precisa de check explícito ou política declarativa.

**Mutations não-idempotentes.** Mesma lógica de REST POST. Forneça idempotency key onde aplicável.

---

## Webhooks e eventos

### Para quem publica webhooks

- **Retry** em falha do receiver, com backoff exponencial
- **Assinatura** do payload (HMAC) para receiver verificar autenticidade
- **Timestamp** no header para mitigar replay
- **Dead-letter queue** após N falhas — não fica retentando para sempre

### Para quem consome webhooks

- **Dedup por event ID** — providers podem entregar duas vezes
- **Resposta rápida** (ack imediato, processamento assíncrono) — evita timeouts no provider
- **Idempotência** no processamento — se processar duas vezes, resultado é o mesmo

---

## Checklist condensado

```
REST API
  [ ] Resource names são substantivos plurais?
  [ ] HTTP methods refletem semântica (idempotência respeitada)?
  [ ] Status codes corretos (especialmente 4xx vs 5xx)?
  [ ] Envelope de erro consistente com resto da API?
  [ ] Listas têm paginação (e idealmente cursor-based)?
  [ ] POST não-idempotentes aceitam Idempotency-Key?
  [ ] Versionamento e estratégia de deprecação claros?
  [ ] Rate limit em endpoints públicos/caros?

Schema / Migration
  [ ] Migration é reversível (ou impossibilidade documentada)?
  [ ] Estimativa de tempo de execução adequada?
  [ ] Backfill grande está como job separado batched?
  [ ] Index criado CONCURRENTLY (Postgres)?
  [ ] Padrão expand-contract para mudanças breaking?
  [ ] FKs explícitas com ON DELETE definido?
  [ ] UNIQUE constraint onde a regra de negócio exige?
  [ ] Tipo de dado correto (datas com tz, dinheiro decimal)?
  [ ] Dados sensíveis têm plano de proteção?

Transações
  [ ] Boundary claro, sem I/O externo dentro?
  [ ] Isolation level adequado ao caso?
  [ ] Lock ordering consistente onde aplicável?
  [ ] Retry de SerializationError/Deadlock implementado?

GraphQL (se aplicável)
  [ ] Resolvers protegidos contra N+1 (DataLoader)?
  [ ] Query depth/complexity limit?
  [ ] Authorization em cada campo sensível?

Webhooks (se aplicável)
  [ ] Receiver: dedup por event ID + idempotência?
  [ ] Sender: retry com backoff + assinatura HMAC?
```
