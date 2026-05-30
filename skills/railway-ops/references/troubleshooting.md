# Troubleshooting Railway

Sintomas comuns ao operar Railway e como resolver. Cada seção tem o erro, a causa típica e a sequência de ações pra investigar. Documentação canônica em [docs.railway.com/deployments/troubleshooting](https://docs.railway.com/deployments/troubleshooting) e [networking/troubleshooting](https://docs.railway.com/networking/troubleshooting).

## Triagem inicial (sempre faça antes)

Independente do erro, comece com:

```bash
railway status           # confirma workspace/projeto/env/serviço corretos
railway logs --tail 200  # últimas 200 linhas
railway metrics          # OOM? CPU pegado? Network saturada?
```

Se `railway status` mostrar serviço errado: `railway link` para apontar corretamente. Erros caem nas categorias abaixo.

## Deploy

### "No start command could be found"

**Causa:** Railpack não conseguiu auto-detectar como rodar a app. Comum quando:
- Não há `package.json scripts.start` (Node).
- Não há `Procfile`, `requirements.txt` com app declarada, ou pista equivalente.
- Builder é DOCKERFILE mas o `CMD`/`ENTRYPOINT` está faltando.
- Build command produziu binário em path não-canônico.

**Ações:**
1. Adicione `start` em `package.json`:
   ```json
   "scripts": { "start": "node dist/server.js" }
   ```
2. Ou declare explicitamente no `railway.toml`:
   ```toml
   [deploy]
   startCommand = "node dist/server.js"
   ```
3. Se for Docker: garanta `CMD ["node", "dist/server.js"]` no Dockerfile.

Mais em [docs.railway.com/deployments/troubleshooting/no-start-command-could-be-found](https://docs.railway.com/deployments/troubleshooting/no-start-command-could-be-found).

### Build muito lento

**Causa:** dependências grandes, cache miss, ou layer ordering ruim em Dockerfile.

**Ações:**
1. Olhe os logs de build (`railway logs --build`). Veja qual passo demora mais.
2. **Para Node:** garanta `package-lock.json`/`pnpm-lock.yaml`/`yarn.lock` commitado. Sem lock, install demora muito mais.
3. **Para Dockerfile:** copie `package*.json` antes do código pra cachear `npm install`:
   ```dockerfile
   COPY package*.json ./
   RUN npm ci
   COPY . .
   RUN npm run build
   ```
4. Avalie usar `RAILPACK_VERSION` específica em vez de "default" pra evitar mudança de versão sem aviso.
5. Considere migrar de Nixpacks pra Railpack se ainda estiver usando o antigo.

Mais em [docs.railway.com/deployments/troubleshooting/slow-deployments](https://docs.railway.com/deployments/troubleshooting/slow-deployments).

### "Healthcheck failing"

**Causa:** Railway bate em `healthcheckPath` e não recebe 2xx dentro do timeout. Normalmente:
- App ainda subindo quando o healthcheck começa (cold start lento).
- Endpoint `/health` retorna 503 (DB ainda conectando, dependência indisponível).
- App escutando porta diferente de `process.env.PORT`.

**Ações:**
1. Confirme bind em `PORT`:
   ```js
   app.listen(process.env.PORT || 3000);
   ```
2. Endpoint de health não deve **depender** de DB. Faça simples:
   ```js
   app.get('/health', (req, res) => res.status(200).send('ok'));
   ```
3. Aumente `healthcheckTimeout` se a app demora pra warmar:
   ```toml
   [deploy]
   healthcheckTimeout = 300
   ```
4. Cheque os logs do deploy fail — se o app crashou, o problema não é healthcheck, é o crash.

### Deploy "succeded" mas a app não responde — "Application failed to respond"

**Causa:** Container subiu, mas não está escutando na `$PORT` corretamente, ou está escutando só em `127.0.0.1`.

**Ações:**
1. Bind em `0.0.0.0`, não `localhost`/`127.0.0.1`:
   ```js
   app.listen(process.env.PORT, '0.0.0.0');   // ✅
   app.listen(process.env.PORT, 'localhost'); // ❌ — só vê dentro do container
   ```
2. Pra Django: `gunicorn myapp.wsgi --bind 0.0.0.0:$PORT`.
3. Pra Rails: `RAILS_ENV=production bundle exec rails server -b 0.0.0.0 -p $PORT`.
4. Cheque que **uma** porta exposta — Railway proxy mira a única porta detectada.

Mais em [docs.railway.com/networking/troubleshooting/application-failed-to-respond](https://docs.railway.com/networking/troubleshooting/application-failed-to-respond).

### Variável mudou mas não tá refletindo

**Causa:** Mudança ficou em **staged changes** e não foi deployada.

**Ações:**
1. Olhe no dashboard se há staged changes pendentes.
2. CLI: `railway redeploy` aplica todas as staged changes.
3. Se setou com `--skip-deploys`, precisa `redeploy` manualmente.
4. Verifique se a variável foi setada no environment certo (`railway variables --environment production`).

## Networking

### "ENOTFOUND redis.railway.internal" (ou postgres, mongodb, etc.)

**Causa:** DNS interno do Railway só resolve **dentro de serviços do mesmo projeto** e **com o serviço target rodando**. Causas comuns:

1. Você está chamando `redis.railway.internal` **localmente** (via `railway run`). DNS interno não resolve fora do container Railway.
2. O serviço target (`redis`, `postgres`) está parado ou nunca subiu corretamente.
3. Você renomeou o serviço (era "Postgres", virou "DB") e a URL ainda referencia o nome antigo.
4. IPv6: alguns runtimes (Bun antigo, certos drivers Postgres) não tentam IPv6 por padrão e o DNS interno é IPv6-first.

**Ações:**
1. Localmente: use a URL pública (`DATABASE_PUBLIC_URL`) ou `railway connect`.
2. Em produção: confirme que o serviço target está com deployment "Active".
3. Reference variable: garante que está com nome certo: `${{ Postgres.RAILWAY_PRIVATE_DOMAIN }}`. Renomeou? Atualize.
4. Force IPv4 ou tente IPv6 explicitamente. Em algumas libs, `family=4` ou `family=6` resolve.

Mais em [docs.railway.com/databases/troubleshooting/enotfound-redis-railway-internal](https://docs.railway.com/databases/troubleshooting/enotfound-redis-railway-internal).

### "405 Method Not Allowed" da Railway, não do seu app

**Causa:** Algum middleware/proxy intermediário responde antes do app, ou o método não é suportado naquela rota.

**Ações:**
1. Confirme que a rota e método existem no app.
2. Cheque CORS pré-flight (OPTIONS) — pode estar bloqueando.
3. Veja o response header `Server`. Se vier `Railway` ou similar, é da rede da plataforma; se vier do seu app, é seu.

Mais em [docs.railway.com/networking/troubleshooting/405-method-not-allowed](https://docs.railway.com/networking/troubleshooting/405-method-not-allowed).

### SSL/TLS errado

**Causa:** Custom domain configurado mas cert não emitido ainda, ou DNS apontando errado.

**Ações:**
1. Verifique DNS: `dig <seu-dominio> CNAME` deve apontar pra `<gerado>.up.railway.app`.
2. Custom domain leva alguns minutos pra emitir cert via Let's Encrypt.
3. Force renovação: remova e adicione de novo no dashboard.

Mais em [docs.railway.com/networking/troubleshooting/ssl](https://docs.railway.com/networking/troubleshooting/ssl).

## Runtime

### App crasha logo após receber tráfego (OOM)

**Causa:** RAM alocada insuficiente. Pode ser bug (memory leak), pode ser sizing errado.

**Ações:**
1. `railway metrics` confirma o pico de RAM.
2. Se atingiu limit/replica limit, aumente:
   - Sem replica limits: cresce livremente até o limite do plano.
   - Com replica limits configurados: aumente no Service Settings → Deploy → Replica Limits.
3. Se é leak: profile localmente, fixe, redeploy.
4. Stopgap: configure restart policy `ON_FAILURE` com `maxRetries=10` pra reiniciar quando crashar.

### Node.js não responde a SIGTERM no deploy (deploy fica preso)

**Causa:** Railway manda SIGTERM ao container antigo durante o swap. Apps Node que não escutam SIGTERM travam até o SIGKILL (default ~30s, configurável).

**Ações:**
1. Adicione handler:
   ```js
   process.on('SIGTERM', () => {
     console.log('SIGTERM received, closing server...');
     server.close(() => process.exit(0));
     // Force exit após 25s se conexões não fecharem
     setTimeout(() => process.exit(1), 25000).unref();
   });
   ```
2. Em apps com websockets ou SSE: feche conexões abertas no handler.
3. Aumente `drainingSeconds` se 30s não bastar.

Mais em [docs.railway.com/deployments/troubleshooting/nodejs-sigterm-handling](https://docs.railway.com/deployments/troubleshooting/nodejs-sigterm-handling).

### Cron job não dispara

**Causa:** Cron schedule inválido, restart policy errada, ou serviço não configurado como cron.

**Ações:**
1. Cron schedule no `railway.toml`:
   ```toml
   [deploy]
   cronSchedule = "0 3 * * *"
   restartPolicyType = "NEVER"
   ```
2. Cron usa UTC, não timezone local.
3. Validate sintaxe em [crontab.guru](https://crontab.guru).
4. Cheque deployment history — você deve ver um deploy por execução do cron.

### Volume não persiste dados

**Causa:** Volume não está mountado no path certo, ou app escreve em outro local.

**Ações:**
1. Confirme o **Mount Path** no Service Settings — esse é o path no container.
2. App deve escrever **nesse path**. `/data` é convenção comum.
3. Variável `RAILWAY_VOLUME_MOUNT_PATH` traz o path como env var, use:
   ```js
   const dataDir = process.env.RAILWAY_VOLUME_MOUNT_PATH || './data';
   ```
4. Volume é per-environment-per-service. Volume de staging não persiste em production.

## Billing / custos

### "Recebi cobrança maior que o esperado"

**Causa:** Geralmente uma de:
- Network egress alto (apps usando URL pública entre serviços do mesmo projeto).
- Replicas dimensionadas demais.
- Staging/dev environment esquecido ligado.
- Cron rodando muito frequente (a cada minuto, e.g.).
- Picos de CPU/RAM no fim do mês não previstos.

**Ações:**
1. Workspace Usage no dashboard mostra breakdown por recurso e serviço.
2. Olhe os top consumidores. Egress alto? Migre pra private networking.
3. Cheque environments inativos — staging com 24/7 uptime que ninguém usa é dinheiro evaporando. Ative serverless ou suspenda.
4. Configure usage limit pro próximo mês (hard limit + email alert).

Detalhes em `pricing-and-costs.md`.

### Workloads tomaram offline de repente

**Causa típica:** Atingiu **hard limit** de usage no workspace.

**Ações:**
1. Dashboard → Workspace Usage. Vê o ícone de hard limit atingido.
2. Pra religar: suba o hard limit ou remova (se plano permitir), ou espere próximo ciclo (renova automático).
3. Pra evitar repetir: ajuste o limit acima do uso projetado + buffer.

## CI/CD

### "RAILWAY_TOKEN inválido" no GitHub Actions

**Causa:**
- Token expirado/revogado.
- Project Token mas tentando operação de account-level (criar projeto, criar env).
- Token de outro workspace.

**Ações:**
1. Gere token novo em Project Settings → Tokens.
2. Pra operações que envolvem **criar/deletar projetos ou environments**, use **Account Token** (`RAILWAY_API_TOKEN`), não Project Token.
3. Cole no GitHub Secret. Confirme nome bate com o env var no workflow.

### Deploy passa no CI mas falha real no Railway

**Causa:** Geralmente diferença de ambiente — versões de Node/Python diferentes, variáveis faltando, ou build steps que só rodam localmente.

**Ações:**
1. Confira a versão de runtime no `package.json engines`/`.nvmrc`/`requirements.txt`/`Dockerfile`. Railway deve usar a mesma.
2. Veja variáveis necessárias no build — Railway só injeta o que está no environment. CI pode ter mais.
3. Use `Dockerfile` pra paridade total entre CI e Railway.

## Quando nada faz sentido

Quando você fez tudo o checklist e ainda não bate:

1. **`railway logs --build` + `railway logs --deploy`** — log completo. Quase sempre há um sinal aqui.
2. **Compare com um deployment anterior funcional** — Deployment History → diff de commits, settings, vars.
3. **`railway ssh` no container** — entra dentro do processo em execução, pode rodar `env`, `ps`, etc.
4. **Status da plataforma:** [status.railway.com](https://status.railway.com). Incidents recentes.
5. **Discord da Railway:** [discord.gg/railway](https://discord.gg/railway). Comunidade ativa, suporte rápido.
6. **Central Station:** [station.railway.com](https://station.railway.com). Fórum oficial pra issues.
7. **Suporte Pro/Business:** plano Pro tem suporte priorizado; Business Class é add-on com SLA.

## Quando sugerir contato com Support

Sintomas que indicam problema do lado Railway (não do user):
- Múltiplos serviços em workspaces diferentes falhando ao mesmo tempo.
- Build hangs sem nenhum log por minutos.
- Conexão privada entre serviços que funcionavam sem mudança recente.
- 502/503 do proxy Railway sem o app mudar nada.
- Métricas inconsistentes com realidade.

Antes de contatar, junte: project ID, service ID, deployment ID, e timestamp do incidente. Tudo vem do `railway status --json` e do dashboard.
