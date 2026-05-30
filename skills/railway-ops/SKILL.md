---
name: railway-ops
description: Habilidades para operar a plataforma Railway (railway.com) — provisionar infra, deployar projetos, gerenciar configs e secrets, controlar custos e alocar recursos — com foco em Railway CLI. Acione quando o usuário mencionar "Railway" como cloud/deploy/hosting, "railway up", "railway deploy", "railway login", "railway link", "railway run", "railway logs", "railway.toml", "railway.json", deploy/secrets/custos no Railway, planos Hobby/Pro, Railpack, Nixpacks, serverless Railway, private networking, volumes Railway, RAILWAY_TOKEN, RAILWAY_API_TOKEN, ou pedidos envolvendo replicas, healthcheck, restart policy, environments (prod/staging/PR), scaling, billing, usage limits ou cost control no Railway. Acione também ao comparar Railway com Heroku/Render/Fly.io/Vercel/DigitalOcean. NÃO use para "Ruby on Rails", "rails new", "rails generate" — não são Railway. Em dúvida sobre estado atual (preços, recursos novos), prefira buscar em docs.railway.com.
---

# Railway Ops

Skill para operar a Railway (railway.com) — uma plataforma de cloud "all-in-one" que provisiona infra, builda e faz deploy de apps via Railpack (sucessor do Nixpacks) ou Dockerfile. O foco aqui é fazer você operar o Railway via **CLI**, entendendo o modelo mental, configurações, secrets, deploys, custos e alocação de recursos.

A documentação oficial completa vive em [docs.railway.com](https://docs.railway.com). Esta skill condensa o que importa no dia a dia, com pointers para a referência oficial quando precisar de detalhe.

## Quando consultar as referências

A skill segue _progressive disclosure_. Este SKILL.md cobre o modelo mental e os fluxos mais comuns. Para tarefas mais específicas, leia o arquivo de referência apropriado:

- **`references/cli-reference.md`** — tabela completa dos comandos `railway *`, com subcomandos, aliases e flags. Consulte sempre que precisar de um comando que não está nos exemplos deste SKILL.md, ou quando precisar saber as flags exatas de um comando.
- **`references/pricing-and-costs.md`** — preços por recurso, planos, limites por plano, mecanismos de cost control, otimizações de custo. Consulte quando o usuário perguntar sobre custos, billing, planos, limites ou como economizar.
- **`references/config-as-code.md`** — schema completo de `railway.toml` / `railway.json`, environment overrides, PR environment overrides, deployment teardown. Consulte quando o usuário pedir para criar ou modificar config-as-code.
- **`references/secrets-and-variables.md`** — variáveis de serviço, variáveis compartilhadas, reference variables, sealed variables, variáveis providas pela Railway. Consulte quando o trabalho envolver configurar secrets entre serviços ou variáveis derivadas.
- **`references/troubleshooting.md`** — erros comuns (deploy lento, SIGTERM no Node, "no start command found", "application failed to respond", ENOTFOUND no DNS interno, problemas de SSL). Consulte quando algo quebrar.

Para qualquer coisa que essa skill não cobrir ou possa estar desatualizado (ex: preços alterados, comandos novos), **busque em docs.railway.com**. A skill foi escrita com base na documentação oficial mas a plataforma evolui rápido.

## Modelo mental

Internalize esta hierarquia — quase todos os comandos do CLI fazem mais sentido depois dela:

```
Workspace (account ou time pago)
└── Project (cápsula de infra; rede privada própria)
    ├── Environment (production, staging, PRs efêmeros, etc.)
    │   ├── Service (target de deploy — repo, imagem ou função)
    │   │   ├── Deployment (build + container em execução)
    │   │   ├── Variables (env vars + secrets do serviço)
    │   │   ├── Domains (gerados pelo Railway ou custom)
    │   │   └── Volume (storage persistente, opcional)
    │   └── Shared Variables (compartilhadas entre serviços do projeto)
    └── Project Members (colaboradores)
```

Pontos-chave que costumam confundir:

1. **Serviços dentro de um mesmo projeto compartilham automaticamente uma rede privada.** É por isso que `${{ Postgres.DATABASE_URL }}` referenciando outro serviço funciona "magicamente" — e é por isso que usar **private networking** entre serviços (`*.railway.internal`) em vez de URLs públicas reduz custo de network egress.
2. **Variables são versionadas como _staged changes_** — adicionar, alterar ou remover uma variável não aplica imediatamente; ela vira uma mudança pendente que dispara um redeploy.
3. **Configuration as code (railway.toml/json) sempre sobrescreve o dashboard.** Mudar settings no dashboard não atualiza o arquivo, e o arquivo ganha quando há conflito.
4. **Builder padrão é Railpack** (sucessor do Nixpacks). Se houver Dockerfile no repo, Railway usa o Dockerfile.

## Instalação e autenticação

O CLI roda em macOS, Linux e Windows via WSL. Instalação em uma linha (também configura agent skills se disponível):

```bash
bash <(curl -fsSL railway.com/install.sh) --agents -y
```

Outros métodos: `brew install railway` (macOS), `npm i -g @railway/cli`, `scoop install railway` (Windows), `cargo install railwayapp --locked`, ou binários pré-compilados em [github.com/railwayapp/cli/releases](https://github.com/railwayapp/cli/releases). Requer Node ≥16 quando via npm.

**Autenticação interativa** (abre navegador):

```bash
railway login
```

Em SSH ou ambiente sem navegador, use:

```bash
railway login --browserless
```

**Autenticação não-interativa (CI/CD, scripts)** via variável de ambiente:

| Token              | Escopo                                            | Variável             |
| ------------------ | ------------------------------------------------- | -------------------- |
| Project Token      | Apenas ações de deploy num projeto/environment    | `RAILWAY_TOKEN`      |
| Account/Workspace  | Tudo no escopo da conta ou workspace              | `RAILWAY_API_TOKEN`  |

Project Tokens são gerados no dashboard do projeto e são o que você deve usar em GitHub Actions/GitLab CI para deploys — eles só conseguem deployar/redeployar/ver logs, não conseguem deletar projeto nem mexer em billing.

Para confirmar quem está autenticado: `railway whoami`. Para sair: `railway logout`.

## Fluxos de trabalho centrais

### 1. Linkando um diretório local a um projeto Railway

Antes de qualquer comando que toque um projeto remoto, o diretório local precisa estar **linkado**. Há dois caminhos:

**Caminho A — projeto novo:**
```bash
railway init       # cria projeto novo; pergunta o nome
```

**Caminho B — projeto existente:**
```bash
railway link       # mostra picker de workspaces → projetos → environments
```

Ambos gravam o vínculo em `.railway/` no diretório (gitignored). Depois disso, qualquer comando do CLI assume esse projeto a menos que você passe `--project`/`-p` ou `--environment`/`-e` explicitamente.

Pra ver o vínculo atual: `railway status`. Pra desfazer: `railway unlink`.

### 2. Deploy a partir de código local (`railway up`)

Esse é o comando-canivete-suíço de deploy. Comprime o diretório (respeitando `.gitignore`), envia pro Railway, builda com Railpack ou Dockerfile, e roda.

**Modo padrão (attached):** streama logs de build e deploy no terminal.
```bash
railway up
```

**Modo detached** (volta o controle do terminal imediatamente):
```bash
railway up -d
# ou: railway up --detach
```

**Modo CI** (só logs de build, sai com exit code quando o build termina — ideal para pipelines):
```bash
railway up --ci
# ou em JSON: railway up --ci --json
```

**Targeting** (essencial quando o projeto tem múltiplos serviços/environments):
```bash
railway up --service api --environment production
railway up -s api -e production            # forma curta
railway up -p <PROJECT_ID> -e production   # sem precisar de link prévio
```

Quando usa `--project`, o `--environment` é **obrigatório**.

**Outras flags úteis:**
- `--path <caminho>` — deploya outro path em vez do cwd
- `--path-as-root` — usa o path informado como raiz do archive (em vez do root do projeto)
- `--no-gitignore` — inclui arquivos ignorados pelo .gitignore no upload
- `--verbose` — debug detalhado
- `--ci` implica `--json` quando combinado

### 3. Redeploy / restart / down

```bash
railway redeploy                # rebuilda o último deployment do serviço (usa pra aplicar mudança de var)
railway restart                 # reinicia sem rebuild
railway down                    # remove o deployment ativo
```

`railway redeploy` é especialmente útil para:
- Aplicar mudanças de variável que ficaram em staged changes
- Reiniciar um serviço crasheado
- Forçar build fresco com o mesmo código

### 4. Variáveis e secrets

Variables no Railway são env vars que rolam tanto no build quanto no runtime, tanto via `railway run` (local) quanto via `railway shell`. Para detalhes profundos (shared vars, reference vars com `${{ }}`, sealed vars), ver `references/secrets-and-variables.md`. Operações básicas:

```bash
# Listar variáveis do serviço linkado
railway variables                       # alias: variable, vars, var
railway variables --kv                  # formato KEY=VALUE
railway variables --json                # JSON

# Setar uma ou várias variáveis
railway variables set API_KEY=xyz
railway variables set API_KEY=xyz DB_POOL=10 ENV=production

# Setar valor multi-linha ou complexo via stdin
cat private.pem | railway variables set --stdin TLS_KEY

# Setar sem disparar deploy (acumula em staged changes)
railway variables set FEATURE_X=true --skip-deploys

# Apagar
railway variables delete API_KEY        # alias: rm, remove
```

Todos esses comandos aceitam `-s/--service` e `-e/--environment` pra mirar outro serviço/env que não o linkado.

**Carregar .env localmente para o ambiente do Railway:** importe via UI (RAW Editor cola conteúdo do .env). Pela CLI, transforme em comandos `railway variables set`.

### 5. Rodar comandos locais com env do Railway

```bash
railway run <comando>      # injeta as env vars do serviço linkado e executa
railway run npm run dev
railway run psql            # usa o DATABASE_URL do projeto
```

Útil pra rodar migrations contra DB de staging, scripts pontuais, ou apenas pra testar localmente com as mesmas envs do deploy.

`railway shell` abre um shell interativo já com as variáveis injetadas.

### 6. Logs e diagnóstico

```bash
railway logs                                  # logs do serviço linkado
railway logs --service api                    # logs de outro serviço
railway logs --deployment <deploy_id>         # logs de um deploy específico
railway status                                # contexto atual (workspace/projeto/env/service)
railway metrics                               # CPU/RAM/network do serviço
railway list                                  # lista projetos do workspace
railway open                                  # abre o projeto no browser
```

Pra debug interativo dentro do container em produção:

```bash
railway ssh
```

O dashboard tem um botão "Copy SSH Command" no menu de contexto do serviço, que traz o comando completo (com IDs) — copie de lá quando o serviço tiver múltiplas réplicas.

### 7. Bancos de dados e conexão

Templates de banco (Postgres/MySQL/Redis/MongoDB) ficam em `railway add` ou via UI.

```bash
railway add                                  # picker de templates de banco/serviço
railway connect                              # abre cliente SQL do DB linkado
railway connect postgres                     # se houver múltiplos
```

`railway connect` resolve as credenciais e abre `psql`/`mongosh`/`redis-cli` localmente — não precisa expor o DB publicamente.

### 8. Networking e domínios

```bash
railway domain                               # gera um domínio *.up.railway.app
railway domain custom.dominio.com            # adiciona custom domain
```

URL pública gerada pela Railway: `RAILWAY_PUBLIC_DOMAIN` (env var). URL privada interna (entre serviços do mesmo projeto): `RAILWAY_PRIVATE_DOMAIN`, tipicamente `<service>.railway.internal`. **Use sempre a URL privada para comunicação entre serviços** — não vaza network egress.

### 9. Volumes (storage persistente)

```bash
railway volume                               # listar/gerenciar volumes
railway volume add                           # criar volume e attachar ao serviço
```

Volumes são montados num path no container e sobrevivem entre deploys. Cuidado: backups são incrementais (copy-on-write) e cobrados só pelo dado exclusivo daquele snapshot.

### 10. CI/CD pattern (GitHub Actions exemplo)

```yaml
# .github/workflows/deploy.yml
deploy:
  runs-on: ubuntu-latest
  container: ghcr.io/railwayapp/cli:latest
  env:
    RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
  steps:
    - uses: actions/checkout@v4
    - run: railway up --service api --ci
```

Para PR environments efêmeros automatizados, veja a referência em `references/cli-reference.md`.

## Configuration as Code

Crie `railway.toml` ou `railway.json` na raiz do repo. O arquivo configura **build e deploy** do serviço; sobrescreve dashboard. Exemplo TOML mínimo:

```toml
[build]
builder = "RAILPACK"
buildCommand = "pnpm build"

[deploy]
startCommand = "pnpm start"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[deploy.multiRegionConfig."us-west2-eqdc4a"]
numReplicas = 2

[deploy.multiRegionConfig."europe-west4-drams3a"]
numReplicas = 2

# Override só em produção:
[environments.production]
[environments.production.deploy]
startCommand = "pnpm start:prod"

# Override para PR environments (efêmeros):
[environments.pr]
[environments.pr.deploy]
startCommand = "pnpm start:preview"
```

Schema completo em `references/config-as-code.md`. Use o JSON schema oficial em [railway.com/railway.schema.json](https://railway.com/railway.schema.json) para autocomplete em VSCode (`"$schema": "https://railway.com/railway.schema.json"` no topo do JSON).

## Custos e alocação de recursos

Para qualquer pergunta de custo, billing ou otimização, abra `references/pricing-and-costs.md`. O essencial:

- **Cobrança = subscrição fixa + uso de recursos.** Subscrição já inclui uma cota de uso ($5 no Hobby, $20 no Pro). Acima disso, cobra por consumo real.
- **Preços de recursos (independente do plano):**
  - RAM: $10/GB/mês
  - CPU: $20/vCPU/mês
  - Network egress: $0.05/GB
  - Volume storage: $0.15/GB/mês
- **Planos:** Free ($0), Hobby ($5/mês), Pro ($20/mês), Enterprise (custom).
- **Limites por replica e por serviço** dependem do plano (Hobby: até 6 replicas, 48GB RAM, 48 vCPU; Pro: até 42 replicas, 1TB RAM, 1000 vCPU). Detalhes na referência.
- **Cost control:** usage limits (alerta + hard limit) por billing cycle; replica limits (CPU/RAM máximo por replica); serverless (sleep quando inativo); private networking (zera egress entre serviços).

Pra estimar custo de um workload: pegue CPU e RAM alocados em média (não os picos), multiplique pela tarifa e some egress. Reduções fáceis: ativar serverless em serviços não-críticos, usar private networking para DB e service-to-service, e setar replica limits para evitar surpresa em picos.

## Princípios operacionais

Atue como um SRE pragmático em todas as tarefas de Railway:

1. **Nunca commite tokens em código.** `RAILWAY_TOKEN` e `RAILWAY_API_TOKEN` vão em secrets do CI ou em `~/.bashrc`/`.zshrc` local — nunca no repo.
2. **Prefira config-as-code para qualquer setting não-trivial.** Mudança em arquivo é versionada e auditável; mudança em dashboard é fantasma. Quando o usuário pedir mudança ad-hoc no dashboard, sugira mover pra `railway.toml`.
3. **Antes de qualquer mudança destrutiva** (`railway down`, `railway delete`, `railway variables delete`, wipe de volume), confirme com o usuário e mostre o que vai ser afetado.
4. **Para deploys de produção, prefira `railway up --ci` em pipeline ao invés de máquina local.** Local funciona pra dev, mas auditabilidade e rollback são melhores via Git + Actions.
5. **Ative usage limit hard limit em produção.** Sem isso, um bug que vaze memória ou faça loop pode gerar conta de quatro dígitos. Hard limit é a rede de segurança.
6. **Quando o usuário pergunta sobre custo, sempre olhe três alavancas:** (a) plano (Hobby vs Pro), (b) recursos alocados (CPU/RAM por replica × número de replicas × uptime), (c) network egress (público vs privado). Não sugira mudar plano sem entender o consumo atual.
7. **Para troubleshooting, primeiro `railway status` → `railway logs` → `railway metrics`,** nessa ordem. Status confirma que você está apontando pro lugar certo, logs trazem o erro, metrics confirma se é problema de recurso (OOM/CPU).
8. **Quando inseguro sobre comportamento atual da plataforma, busque docs.railway.com.** O que está nesta skill foi escrito com base em snapshot da documentação; coisas podem ter mudado.

## Saída esperada

Quando responder operações Railway, traga:
- O(s) comando(s) CLI exato(s), prontos pra copy-paste, com placeholders explicitamente marcados em `<MAIÚSCULAS>` se houver
- O que cada flag faz, se não for óbvio
- Efeito colateral relevante (dispara deploy? cobra mais? gera staged change?)
- Quando aplicável, a alternativa via dashboard (e o motivo de preferir CLI)
- Link para a página específica em docs.railway.com quando o detalhamento for grande

Para perguntas conceituais ou de custo, traga números concretos (do `pricing-and-costs.md`) ao invés de respostas vagas.
