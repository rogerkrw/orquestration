# Variables e secrets

Variables no Railway são variáveis de ambiente que ficam disponíveis em **build**, **runtime**, **`railway run`** (local) e **`railway shell`**. Servem para configuração e secrets. Esta referência cobre os tipos, sintaxe de referência, sealed vars (cifradas), variáveis providas pela Railway, e patterns comuns.

Documentação canônica: [docs.railway.com/variables](https://docs.railway.com/variables) e [reference](https://docs.railway.com/variables/reference).

## Tipos de variável

### 1. Service variables
Escopo: um serviço. Default. Outras services do projeto **não** veem essa variável a menos que você crie uma reference variable.

UI: `Service → Variables`. CLI: `railway variables set KEY=VALUE`.

### 2. Shared variables
Escopo: todo o projeto (ou pelo menos os services que escolheram usar).

UI: `Project Settings → Shared Variables`. Você define a variável uma vez no projeto, e marca quais serviços têm acesso (ou cada serviço opta por consumir).

Use quando muitos serviços precisam da mesma variável: chaves de API compartilhadas, hosts, flags globais.

### 3. Reference variables
Variáveis cujo valor é derivado de outras variáveis usando a sintaxe `${{ ... }}`. Resolvidas em deploy time.

Padrões:

```bash
# Referenciar uma shared var:
SOMETHING=${{ shared.MINHA_SHARED }}

# Referenciar var de outro serviço do mesmo projeto:
DATABASE_URL=${{ Postgres.DATABASE_URL }}

# Referenciar var do próprio serviço (composição):
FULL_URL=https://${{ RAILWAY_PUBLIC_DOMAIN }}/api

# Combinações:
REDIS_URL=redis://default:${{ Redis.REDIS_PASSWORD }}@${{ Redis.RAILWAY_PRIVATE_DOMAIN }}:6379
```

Reference vars são poderosas porque preservam dependências: se o serviço Postgres for recriado e a senha mudar, todas as services que referenciam `${{ Postgres.DATABASE_URL }}` recebem o valor novo automaticamente, sem você editar nada.

### 4. Sealed variables
Versão "cifrada" da variável: valor fica acessível ao build e ao runtime, mas **nunca é visível no dashboard nem retornado pela API**.

Operações disponíveis em sealed:
- Criar (vira sealed na hora).
- Editar (modal de edição, não Raw Editor).
- Apagar.
- **Não** dá pra "des-selar" — pra ver o valor, recrie a variável.

Trade-offs (importante saber):
- `railway variables list` e `railway run` **não** trazem o valor da sealed (no CLI). Pra ler localmente, precisa criar uma versão não-sealed pro dev environment.
- **Não** são copiadas em PR environments efêmeros (precisa setar separado).
- **Não** são copiadas ao duplicar environment ou serviço.
- **Não** aparecem em diffs de sync entre environments.
- **Não** sincam com integrações externas.

Use sealed para: chaves de produção sensíveis (Stripe, AWS, JWT secrets) que nunca deveriam estar em logs nem ser exportadas.

## Sintaxe de template (`${{ ... }}`)

A documentação chama de "template syntax". Resolve no momento do deploy, não no runtime.

| Sintaxe                                       | Resolve para                                       |
| --------------------------------------------- | -------------------------------------------------- |
| `${{ VAR }}`                                  | Variável local do próprio serviço                  |
| `${{ shared.VAR }}`                           | Shared variable do projeto                         |
| `${{ ServiceName.VAR }}`                      | Variável do serviço `ServiceName`                  |
| `${{ ServiceName.RAILWAY_PRIVATE_DOMAIN }}`   | Domínio privado de outro serviço                   |

Pode compor:
```bash
DATABASE_URL=postgresql://${{ Postgres.POSTGRES_USER }}:${{ Postgres.POSTGRES_PASSWORD }}@${{ Postgres.RAILWAY_PRIVATE_DOMAIN }}:5432/${{ Postgres.POSTGRES_DB }}
```

## Variáveis providas pela Railway

Variáveis automáticas, sempre disponíveis dentro do container. Lista completa em [docs.railway.com/variables/reference](https://docs.railway.com/variables/reference). As mais usadas:

| Variável                       | Valor                                                                   |
| ------------------------------ | ----------------------------------------------------------------------- |
| `RAILWAY_PUBLIC_DOMAIN`        | Domínio público do serviço (sem protocolo). Ex: `app-prod.up.railway.app` |
| `RAILWAY_PRIVATE_DOMAIN`       | Domínio privado dentro do projeto. Ex: `web.railway.internal`          |
| `RAILWAY_TCP_PROXY_PORT`       | Porta exposta no proxy TCP (quando configurado)                         |
| `PORT`                         | Porta que o serviço deve escutar (HTTP)                                |
| `RAILWAY_PROJECT_ID`           | ID do projeto                                                          |
| `RAILWAY_PROJECT_NAME`         | Nome do projeto                                                        |
| `RAILWAY_ENVIRONMENT`          | Nome do environment (`production`, `staging`, etc.)                    |
| `RAILWAY_SERVICE_ID`           | ID do serviço                                                          |
| `RAILWAY_SERVICE_NAME`         | Nome do serviço                                                        |
| `RAILWAY_DEPLOYMENT_ID`        | ID do deploy atual                                                     |
| `RAILWAY_GIT_COMMIT_SHA`       | SHA do commit deployado (quando vindo de GitHub)                       |
| `RAILWAY_GIT_BRANCH`           | Branch deployada                                                       |

`PORT` é o mais importante: sempre bind no `process.env.PORT` (ou equivalente). Hardcode em 3000/8080 vai funcionar local mas Railway atribui dinamicamente em prod.

## Variáveis de configuração (controlam comportamento da plataforma)

Variáveis especiais que mudam o build/deploy. Lista completa em [docs.railway.com/variables/reference#user-provided-configuration-variables](https://docs.railway.com/variables/reference). Algumas úteis:

| Variável                 | Efeito                                                                  |
| ------------------------ | ----------------------------------------------------------------------- |
| `RAILPACK_VERSION`       | Trava versão do Railpack                                                |
| `RAILWAY_DOCKERFILE_PATH`| Path para Dockerfile custom                                             |
| `RAILWAY_RUN_AS_ROOT`    | Roda o container como root (use só se precisar)                        |
| `NIXPACKS_PYTHON_VERSION`| Quando usa Nixpacks como builder, fixa versão                          |

## Operações no CLI

### Listar
```bash
railway variables                       # tabela
railway variables --kv                  # KEY=VALUE (estilo .env)
railway variables --json                # JSON
railway variables --service api --environment staging
```

Sealed vars **não aparecem** na listagem da CLI (security feature).

### Set
```bash
railway variables set NODE_ENV=production
railway variables set DB_POOL=10 LOG_LEVEL=info FEATURE_X=true   # múltiplas

# Valor multilinha ou PEM
cat private.pem | railway variables set --stdin TLS_KEY

# Sem disparar deploy (junta em staged changes)
railway variables set A=1 B=2 C=3 --skip-deploys
railway redeploy
```

### Delete
```bash
railway variables delete OLD_FLAG
railway variables delete OLD_FLAG --service api --environment production
```

### Import .env
A CLI não tem comando direto para importar `.env`. Use o **Raw Editor** no dashboard (cola conteúdo do .env) ou faça via shell:

```bash
# Bash + xargs (cuidado com aspas e escape)
cat .env | grep -v '^#' | grep -v '^$' | xargs -I{} railway variables set {} --skip-deploys
railway redeploy
```

Ou via importer do Heroku se for migração: dashboard → command palette → "Import from Heroku".

## Staged changes (deploy diferido)

Toda alteração de variável (set, delete, update) gera **staged changes** — não aplica imediatamente. Esses changes aparecem no dashboard com botão "Deploy" pra revisar e aplicar.

Para acumular múltiplas mudanças e aplicar de uma vez via CLI:

```bash
railway variables set A=1 --skip-deploys
railway variables set B=2 --skip-deploys
railway variables delete OLD --skip-deploys
railway redeploy   # aplica tudo num único novo deployment
```

Isso evita disparar 3 deployments seguidos.

## Como ler variáveis no código

Linguagem agnóstico — Railway só injeta como env var padrão do sistema.

**Node.js:**
```js
const port = process.env.PORT || 3000;
const db = process.env.DATABASE_URL;
```

**Python:**
```python
import os
port = int(os.environ.get('PORT', '3000'))
db = os.environ['DATABASE_URL']
```

**Go:**
```go
port := os.Getenv("PORT")
```

**Em Dockerfile (durante o build):**

Pra usar variáveis Railway dentro do `Dockerfile`, declare como `ARG`:

```dockerfile
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build
```

Railway injeta automaticamente como build arg.

## Local development com vars do Railway

```bash
railway run npm run dev        # executa com env do serviço linkado
railway shell                  # shell interativo com env carregada
```

Os dois acima **não trazem sealed vars** — pra dev local você precisa setar separado num `.env` local ou criar versão não-sealed no environment de development.

## Padrões importantes

### Pattern 1: Use private networking entre serviços
Quando referenciar outro serviço do mesmo projeto, **sempre use** `RAILWAY_PRIVATE_DOMAIN`:

```bash
# Bom
INTERNAL_API_URL=http://${{ api.RAILWAY_PRIVATE_DOMAIN }}:3000

# Ruim — gera network egress
INTERNAL_API_URL=https://${{ api.RAILWAY_PUBLIC_DOMAIN }}
```

Para DBs Railway-managed, use `DATABASE_URL` (interno) não `DATABASE_PUBLIC_URL`.

### Pattern 2: Separação clara entre config e secret
- **Config** (não-secreto): `NODE_ENV`, `LOG_LEVEL`, `FEATURE_FLAGS` — variável normal, vai pro repo via README/docs.
- **Secret**: API keys, DB creds, JWT — variável sealed se for produção.

### Pattern 3: Defaults seguros em código, override em env
```js
const config = {
  port: parseInt(process.env.PORT) || 3000,
  logLevel: process.env.LOG_LEVEL || 'info',
  jwtSecret: process.env.JWT_SECRET   // sem default — quebra se faltar
};

if (!config.jwtSecret && process.env.NODE_ENV === 'production') {
  throw new Error('JWT_SECRET é obrigatório em produção');
}
```

### Pattern 4: Variáveis por environment
Em vez de `JWT_SECRET_PROD` e `JWT_SECRET_STAGING` no mesmo environment, use **environments separados** (production e staging) com `JWT_SECRET` em cada. Reference variables resolvem corretamente.

### Pattern 5: Migração de variáveis em staged
Vai mudar muita variável de uma vez? Use `--skip-deploys` em todas e dispare um único `railway redeploy`. Evita downtime de múltiplos deploys consecutivos.

### Pattern 6: Doppler / Vault / SOPS para fontes externas de secrets
Railway suporta integração com Doppler para sync automático. Veja [docs.doppler.com/docs/railway](https://docs.doppler.com/docs/railway). Para Vault/SOPS, hoje é manual (script de CI puxa secrets e seta via API ou `railway variables set`).

## Antipatterns a evitar

- **Hardcodar URL pública entre serviços** → custo desnecessário de egress, e latência maior.
- **Variável de senha em texto plano no `railway.toml`** → arquivo no Git, qualquer collaborator vê. Use env var (e sealed se for prod).
- **Mesma `JWT_SECRET` entre staging e production** → vazamento de staging compromete prod.
- **`PORT` hardcoded no app** → Railway atribui dinamicamente; quebra em produção.
- **Renomear serviço sem revisar reference variables** → `${{ velho_nome.X }}` quebra silenciosamente.
- **Sealed em dev environment** → impede `railway run` local funcionar; deixe sealed só em prod.

## Quem altera variáveis dispara o quê

| Ação                             | Dispara deploy? | Visível em staged?  |
| -------------------------------- | --------------- | ------------------- |
| `railway variables set X=Y`      | Sim (default)   | —                   |
| `set` com `--skip-deploys`       | Não             | Sim                 |
| Editar no dashboard              | Sim             | Sim (revisa antes)  |
| Mudar shared variable            | Sim em todos os services que usam | Sim |
| Selar variável existente         | Sim             | Sim                 |
| Apagar variável                  | Sim             | Sim                 |
