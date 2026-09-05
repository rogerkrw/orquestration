# Config as Code legado — railway.toml e railway.json

Railway ainda suporta declarar configurações de **build** e **deploy** em `railway.toml` ou
`railway.json`, mas esse mecanismo está **deprecated**. A documentação recomenda
Infrastructure as Code para novos projetos; o formato legado permanece funcionando durante a
transição, com suporte indicado até **01/12/2026**. Não crie novos arquivos nesse formato sem
confirmar a orientação atual para o projeto.

Documentação oficial: [Config as Code reference](https://docs.railway.com/config-as-code/reference) e [Railway docs](https://docs.railway.com).

## Onde colocar

Por padrão, Railway procura na **raiz do repo**:
- `railway.toml`, ou
- `railway.json`

Em **Service Settings**, dá pra apontar para um path customizado (ex: `/api/railway.toml`). Útil em monorepos.

Em VSCode, para JSON, adicione no topo:
```json
{
  "$schema": "https://railway.com/railway.schema.json"
}
```
para ganhar autocomplete e tooltips com a documentação inline.

## Como o merge funciona

Quando há `railway.toml`/`railway.json` no repo, ao deployar Railway aplica:

1. Settings do arquivo (em código) — **vencem**.
2. Settings do dashboard — usadas para o que o arquivo não definir.

**Mudar settings no dashboard NÃO atualiza o arquivo.** Se você tem ambos, e algo se comporta de modo inesperado, o arquivo provavelmente está sobrescrevendo. Inspecione **Deployment Details** — settings que vieram do arquivo têm ícone de arquivo, e hover mostra de qual parte vieram.

## Schema completo

### Builder

Define qual engine builda a imagem.

```toml
[build]
builder = "RAILPACK"   # default. Sucessor do Nixpacks.
# ou:
builder = "DOCKERFILE" # usa Dockerfile (auto-detectado se existir; só especifique se custom)
```

```json
{ "build": { "builder": "RAILPACK" } }
```

Se houver um Dockerfile no repo, Railway usa ele por padrão. Para um caminho custom de Dockerfile, use `dockerfilePath` (ver abaixo).

### Build command

```toml
[build]
buildCommand = "pnpm install --frozen-lockfile && pnpm build"
```

`null` desabilita o build command (útil quando o Dockerfile já cuida).

### Dockerfile path

Quando o Dockerfile não está na raiz:

```toml
[build]
dockerfilePath = "docker/api.Dockerfile"
```

### Railpack version

Trava a versão do Railpack. Versão "default" é a estável corrente; trave para builds reprodutíveis.

```toml
[build]
railpackVersion = "0.10.2"
```

Lista de versões: [github.com/railwayapp/railpack/releases](https://github.com/railwayapp/railpack/releases).

Alternativa: variável `RAILPACK_VERSION`.

### Watch patterns

Patterns que disparam (ou pulam) deploy quando arquivos mudam — útil em monorepo pra não rebuildar tudo quando só um app mudou.

```toml
[build]
watchPatterns = [
  "src/**",
  "package.json",
  "!**/*.md"   # exclamação = exclui
]
```

Sem `watchPatterns`, qualquer push faz redeploy. Com, só faz quando os patterns batem.

### Start command

```toml
[deploy]
startCommand = "node dist/server.js"
```

`null` deixa Railway auto-detectar (Railpack tenta inferir de `package.json scripts.start`, etc.).

### Pre-deploy command

Roda antes do container subir. Padrão para migrations:

```toml
[deploy]
preDeployCommand = "pnpm prisma migrate deploy"
```

Pre-deploy roda como **um job efêmero** com as mesmas envs do container. Se falhar, o deploy falha. Útil pra:
- Migrations de schema
- Cache warm-up
- Validação de configuração

### Healthcheck

```toml
[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100   # segundos
```

Railway bate no path com GET. Se receber 2xx dentro do timeout, considera o deploy saudável e faz o swap. Se não, o deploy **falha** e mantém o anterior. **Use sempre que o app tiver HTTP** — é a única garantia de zero-downtime correto.

### Restart policy

```toml
[deploy]
restartPolicyType = "ON_FAILURE"   # ALWAYS | ON_FAILURE | NEVER
restartPolicyMaxRetries = 10
```

- `ON_FAILURE` (recomendado): reinicia só se exit code != 0.
- `ALWAYS`: reinicia sempre que parar (cuidado com loops).
- `NEVER`: morre e fica morto. Útil para jobs/cron.

### Multi-region

Roda replicas distribuídas:

```toml
[deploy.multiRegionConfig."us-west2-eqdc4a"]
numReplicas = 2

[deploy.multiRegionConfig."europe-west4-drams3a"]
numReplicas = 2
```

Lista de regiões em [docs.railway.com/deployments/regions](https://docs.railway.com/deployments/regions). Customer-facing apps geralmente se beneficiam de pelo menos US + EU; B2B regional pode ficar com 1.

### Cron schedule

Torna o serviço um cron job:

```toml
[deploy]
cronSchedule = "0 3 * * *"   # 3am UTC, diário
```

Sintaxe cron padrão. O serviço sobe, roda o startCommand, e morre. Restart policy `NEVER` faz sentido com cron.

### Deployment teardown

Tunna o comportamento de zero-downtime:

```toml
[deploy.deploymentTeardown]
overlapSeconds = 30       # quanto tempo o deploy antigo coexiste com o novo
drainingSeconds = 60      # tempo entre SIGTERM e SIGKILL
```

Útil para apps que precisam drenar conexões abertas longas (websockets, SSE, requests demoradas). Aumente se você vê 502s no momento do deploy.

### Environment overrides

Aplica configs diferentes por environment:

```toml
# Config base (production)
[build]
builder = "RAILPACK"

[deploy]
startCommand = "node dist/server.js"

# Override em staging
[environments.staging.deploy]
startCommand = "node --inspect=0.0.0.0:9229 dist/server.js"

# Override em todos os PR environments (efêmeros)
[environments.pr.deploy]
startCommand = "node dist/server.js --preview"
```

A resolução para um deploy obedece a esta ordem (a primeira que bate vence):

1. Environment com nome exato do environment efêmero (`environments.pr-123`).
2. Environment hardcoded `pr` (para PR environments).
3. Environment base do PR (ex: `staging` se o PR foi aberto contra `staging`).
4. Base config (no nível root do arquivo).
5. Service settings (no dashboard).

## Exemplos completos

### Exemplo 1: Node API simples
```toml
[build]
builder = "RAILPACK"
buildCommand = "pnpm install --frozen-lockfile && pnpm build"

[deploy]
startCommand = "node dist/server.js"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 5
```

### Exemplo 2: Django com migration

```toml
[build]
builder = "RAILPACK"
buildCommand = "pip install -r requirements.txt"

[deploy]
preDeployCommand = "python manage.py migrate --noinput && python manage.py collectstatic --noinput"
startCommand = "gunicorn myapp.wsgi:application --bind 0.0.0.0:$PORT --workers 3"
healthcheckPath = "/healthz"
restartPolicyType = "ON_FAILURE"
```

### Exemplo 3: Cron job (jobs diários)

```toml
[deploy]
startCommand = "node scripts/daily-cleanup.js"
cronSchedule = "0 3 * * *"
restartPolicyType = "NEVER"
```

### Exemplo 4: Monorepo, três environments, multi-region em prod

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "services/api/Dockerfile"
watchPatterns = ["services/api/**", "packages/shared/**"]

[deploy]
startCommand = "node services/api/dist/server.js"
healthcheckPath = "/health"
healthcheckTimeout = 60
restartPolicyType = "ON_FAILURE"

[environments.staging.deploy]
startCommand = "node services/api/dist/server.js --log-level=debug"

[environments.pr.deploy]
startCommand = "node services/api/dist/server.js --log-level=trace"

[environments.production.deploy]
startCommand = "node services/api/dist/server.js --log-level=warn"

[environments.production.deploy.multiRegionConfig."us-west2-eqdc4a"]
numReplicas = 2

[environments.production.deploy.multiRegionConfig."europe-west4-drams3a"]
numReplicas = 1

[environments.production.deploy.deploymentTeardown]
overlapSeconds = 45
drainingSeconds = 90
```

### Versão JSON equivalente (Exemplo 1)

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "RAILPACK",
    "buildCommand": "pnpm install --frozen-lockfile && pnpm build"
  },
  "deploy": {
    "startCommand": "node dist/server.js",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

## Patterns recomendados

### Pattern 1: Sempre commit `railway.toml` em apps de produção
Pelas mesmas razões que `Dockerfile` é commitado. Versionamento, code review, reprodutibilidade.

### Pattern 2: Healthcheck obrigatório em apps HTTP
Sem `healthcheckPath`, Railway considera o deploy saudável assim que o processo começa a ouvir. Isso causa swap pra um app que ainda está warmando, gerando 502s. Sempre adicione.

### Pattern 3: Pre-deploy para migrations
Migration no startup é fonte clássica de race condition entre replicas. Pre-deploy roda **uma única vez** antes do deploy, o que resolve.

### Pattern 4: Watch patterns em monorepo
Sem watch patterns, push de README rebuilda todos os serviços. Defina watch patterns por serviço.

### Pattern 5: Multi-region só onde compensa
Multi-region custa replicas extras. Faz sentido quando:
- Tem usuários geograficamente distribuídos.
- Latência importa (consumer-facing).
- DR é requisito de negócio.

Para B2B regional ou apps internos, 1 região basta.

### Pattern 6: Restart `NEVER` em jobs e migrations
Restart `ALWAYS` num job de migration vira loop infinito. Use `NEVER` ou `ON_FAILURE` com `maxRetries=1`.

### Pattern 7: Variáveis de configuração via env, comportamento via arquivo
- Em env vars: secrets, URLs, feature flags que mudam por ambiente.
- Em `railway.toml`: builder, build/start commands, healthcheck, restart, scaling.

Não bote URL de banco no `railway.toml`. Não bote start command em env var.

## Debugando config-as-code

Quando algo não bate com o esperado:

1. **Vá ao Deployment Details no dashboard.** Cada setting tem indicador da origem (dashboard, arquivo, qual seção do arquivo). Isso resolve 90% dos casos.
2. **Cheque a ordem de override de environment.** Você definiu base + `environments.production` + dashboard? O production override vence sobre o base. O arquivo vence sobre dashboard.
3. **Confirme o caminho do arquivo.** Em Service Settings → Config File, o path tem que apontar pro arquivo certo (default é raiz, mas em monorepo costuma estar em subdir).
4. **TOML é sensível a indentação?** Não, é sensível a syntax — `[a.b.c]` é diferente de `[a]\n[b]\n[c]`. Use validator se duvidar (`tomlcheck`, `tomlv`).
