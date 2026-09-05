# Railway CLI Reference

Referência completa dos comandos do `railway` CLI, organizados por categoria. Para cada comando há a sintaxe principal, aliases conhecidos, flags relevantes e — quando útil — exemplos práticos.

A documentação canônica fica em [docs.railway.com/cli](https://docs.railway.com/cli). Quando precisar da flag mais nova ou de detalhe de comportamento, consulte ela: a Railway atualiza o CLI com frequência (versionado em [github.com/railwayapp/cli](https://github.com/railwayapp/cli)).

## Global options

Estas flags funcionam na maioria dos comandos:

| Flag                  | Descrição                                              |
| --------------------- | ------------------------------------------------------ |
| `-s, --service <SVC>` | Serviço alvo (nome ou ID)                              |
| `-e, --environment`   | Environment alvo (nome ou ID)                          |
| `-p, --project <ID>`  | Project ID — útil para operar sem precisar de `link`   |
| `--json`              | Saída em JSON (para scripting)                         |
| `-y, --yes`           | Pula prompts de confirmação                            |
| `-h, --help`          | Mostra help do comando                                 |
| `-V, --version`       | Mostra versão do CLI                                   |

## Autenticação

### `railway setup agent`

Configura a integração oficial do Railway com agentes de código, incluindo autenticação,
MCP e skills quando suportados pelo ambiente.

```bash
railway setup agent
railway setup agent --oauth
railway setup agent --local
```

Para instalar ou atualizar somente as skills oficiais, consulte `railway skills install` e
`railway skills update`. Verifique as opções na documentação atual antes de automatizar.

### `railway login`
Login interativo (abre navegador).

```bash
railway login
railway login --browserless     # imprime URL pra colar em outra máquina (SSH, headless)
```

### `railway logout`
Encerra a sessão local.

### `railway whoami`
Mostra quem está autenticado. Útil para confirmar antes de ações sensíveis.

## Gerenciamento de projeto

### `railway init`
Cria um projeto novo no workspace ativo e linka o diretório atual.

```bash
railway init                    # nome interativo
railway init --name my-app      # nome direto
```

### `railway link`
Linka o diretório atual a um projeto existente. Mostra um picker (workspace → projeto → environment → serviço).

```bash
railway link
railway link --project <ID> --environment production --service api
```

### `railway unlink`
Remove o vínculo do diretório (apaga `.railway/`).

### `railway list`
Lista projetos visíveis ao usuário/workspace ativo.

```bash
railway list
railway list --json
```

### `railway status`
Mostra o contexto atual: workspace, projeto, environment, serviço linkados, e o usuário autenticado. Sempre o primeiro comando antes de outros — confirma que você está apontando pro lugar certo.

```bash
railway status
railway status --json
```

### `railway open`
Abre o projeto linkado no browser.

### `railway project`
Comandos avançados de projeto:

```bash
railway project list
railway project delete            # destrutivo — pede confirmação
```

## Deploy

### `railway up`
Deploya o diretório atual. O comando-canivete-suíço. Detalhado no SKILL.md principal — aqui as flags em referência:

| Flag                    | Descrição                                                                 |
| ----------------------- | ------------------------------------------------------------------------- |
| `-d, --detach`          | Volta o controle do terminal logo após o upload                           |
| `-c, --ci`              | Streama apenas logs de build, sai com exit code (ideal pra CI)           |
| `--json`                | Logs em JSON (implica `--ci`)                                             |
| `-s, --service <NAME>`  | Mira um serviço específico                                                |
| `-e, --environment`     | Environment de destino                                                    |
| `-p, --project <ID>`    | Projeto sem precisar de link prévio (`--environment` fica obrigatório)    |
| `--path <PATH>`         | Path a deployar (default: cwd)                                            |
| `--path-as-root`        | Usa o `--path` como raiz do archive (em vez do project root)              |
| `--no-gitignore`        | Não respeita `.gitignore`                                                 |
| `--verbose`             | Debug detalhado                                                           |

Exemplo CI/CD:
```bash
RAILWAY_TOKEN=$TOKEN railway up --service api --environment production --ci
```

### `railway deploy`
Deploya um template de Railway (não confundir com `up`). Use para subir Wordpress, Postgres com configs específicas, etc. via template URL.

```bash
railway deploy --template <URL_OU_ID>
```

### `railway redeploy`
Refaz o build/deploy do último deployment do serviço, sem upload novo. Usa pra aplicar mudança de variável que ficou em staged, pra reiniciar com build fresco, ou pra reativar um deploy crashado.

```bash
railway redeploy
railway redeploy --service api -y       # sem confirmação
```

### `railway restart`
Reinicia o container sem rebuild. Mais rápido que `redeploy` quando você só precisa reiniciar o processo.

```bash
railway restart
```

### `railway down`
Remove o deployment ativo do serviço (mas mantém o serviço configurado). Destrutivo — confirma com `-y`.

```bash
railway down
railway down --yes
```

### `railway deployment`
Inspeciona deployments individuais:

```bash
railway deployment list                       # histórico de deploys
railway deployment <DEPLOYMENT_ID>            # detalhe
```

### `railway templates`
Lista templates publicados.

## Serviços

### `railway add`
Adiciona um novo serviço ao projeto. Pode ser um template (banco), uma imagem Docker, ou um repo conectado.

```bash
railway add                          # picker interativo
railway add --plugin postgresql      # adiciona um Postgres
railway add --image redis:7-alpine   # adiciona uma imagem Docker
railway add --repo owner/repo        # adiciona um repo GitHub
```

### `railway service`
Gerencia o serviço linkado:

```bash
railway service                      # picker para trocar o serviço linkado
railway service create               # cria um serviço vazio
railway service delete               # apaga o serviço (destrutivo)
```

### `railway scale`
Configura recursos e replicas do serviço:

```bash
railway scale                                  # mostra config atual
railway scale --replicas 3
railway scale --region us-west2-eqdc4a --replicas 2
```

### `railway delete`
Apaga o projeto linkado inteiro. **Extremamente destrutivo** — sempre pede confirmação.

## Variables (env vars e secrets)

### `railway variables` (aliases: `variable`, `vars`, `var`)
Listar, setar, deletar variáveis do serviço linkado.

| Subcomando            | Descrição                                  |
| --------------------- | ------------------------------------------ |
| `list` (default, `ls`)| Lista as variáveis                         |
| `set`                 | Cria ou atualiza variáveis                 |
| `delete` (`rm`, `remove`) | Remove uma variável                    |

Flags relevantes:

| Flag               | Aplica em       | Descrição                                       |
| ------------------ | --------------- | ----------------------------------------------- |
| `-s, --service`    | todos           | Serviço alvo                                    |
| `-e, --environment`| todos           | Environment alvo                                |
| `-k, --kv`         | list            | Formato `KEY=VALUE` (estilo .env)               |
| `--json`           | todos           | Saída em JSON                                   |
| `--stdin`          | set             | Lê o valor do stdin (1 KEY por vez)             |
| `--skip-deploys`   | set             | Não dispara deploy; só acumula em staged       |

Exemplos:

```bash
# Listar
railway variables --service api --environment production --kv

# Setar uma
railway variables set NODE_ENV=production

# Setar várias de uma vez
railway variables set DATABASE_POOL=10 LOG_LEVEL=info FEATURE_X=true

# Setar de stdin (pra valores grandes, multilinha, chaves PEM)
cat private.pem | railway variables set --stdin TLS_KEY

# Setar sem disparar deploy (junta em staged changes pra deploy único depois)
railway variables set A=1 B=2 C=3 --skip-deploys
railway redeploy   # aplica tudo de uma vez

# Apagar
railway variables delete OLD_FLAG
```

Variáveis **sealed** (cifradas, não visíveis no dashboard) **não aparecem** em `railway variables list` nem em `railway run`. Veja `secrets-and-variables.md`.

## Environments

### `railway environment`
Gerencia environments do projeto.

```bash
railway environment                          # picker para trocar env linkado
railway environment list
railway environment new staging              # cria novo env
railway environment delete staging           # apaga env
```

Cada environment tem seu próprio set de variáveis, deploys e domains. Duplicar é o padrão pra criar staging a partir de production (clona todas as configs e variáveis não-sealed).

## Local development

### `railway run <comando>`
Executa um comando local com as env vars do serviço linkado injetadas (também resolve reference variables como `${{ Postgres.DATABASE_URL }}`).

```bash
railway run npm run dev
railway run psql                              # usa DATABASE_URL
railway run --service api npm run migrate     # rodar migration de outro serviço
```

### `railway shell`
Abre um shell interativo com as env vars já injetadas. Útil pra debug:

```bash
railway shell
$ echo $DATABASE_URL
$ psql $DATABASE_URL
```

### `railway dev`
Modo de desenvolvimento — proxy local + variáveis sincronizadas com Railway. Use quando quiser testar contra um banco de produção/staging sem expor publicamente.

## Logs, debug e métricas

### `railway logs`
Streama logs do serviço linkado.

```bash
railway logs
railway logs --service api
railway logs --deployment <DEPLOY_ID>          # logs de um deployment específico
railway logs --json
railway logs --build                            # apenas build logs
railway logs --deploy                           # apenas deploy/runtime logs
```

### `railway metrics`
Mostra métricas do serviço (CPU, RAM, network).

```bash
railway metrics
railway metrics --service api --environment production
```

### `railway ssh`
Abre shell SSH dentro do container em execução. Em produção: copie o comando exato pelo dashboard (botão "Copy SSH Command") porque ele inclui IDs de réplica específicos.

```bash
railway ssh
railway ssh --service api --environment production
```

### `railway connect`
Conecta a um banco do projeto via cliente local (psql, mongosh, redis-cli). Resolve credenciais via rede privada.

```bash
railway connect                       # picker se houver múltiplos
railway connect Postgres
railway connect Redis
```

## Networking

### `railway domain`
Gerencia domínios do serviço.

```bash
railway domain                                # lista
railway domain add                            # gera Railway domain *.up.railway.app
railway domain add custom.dominio.com         # adiciona custom (com instruções DNS)
railway domain remove custom.dominio.com
```

## Volumes (storage persistente)

### `railway volume`

```bash
railway volume                                # lista volumes do serviço
railway volume add                            # cria e attacha
railway volume detach
railway volume delete <NAME>                  # destrutivo — sumiço dos dados
```

## Storage buckets

### `railway bucket`
Buckets são S3-compatible storage da Railway.

```bash
railway bucket list
railway bucket create my-bucket
railway bucket delete my-bucket
```

## Functions (serverless)

### `railway functions`
Gerencia [Railway Functions](https://docs.railway.com/functions), código serverless.

```bash
railway functions deploy
railway functions list
railway functions logs
```

## AI / Agents

### `railway agent`
Roda o Railway Agent (LLM-based assistant) localmente.

### `railway setup`
Configura ferramentas de AI agent (Claude Code, Cursor, Codex, Copilot, etc.) com skills da Railway e MCP server.

```bash
railway setup agent                            # auto-detecta e configura
```

### `railway mcp`
Comandos do MCP server da Railway.

```bash
railway mcp install --agent claude-code
railway mcp install --agent cursor
```

### `railway skills`
Instala as agent skills da Railway pra ferramentas de IA.

```bash
railway skills --agent claude-code
```

## Utilitários

### `railway docs`
Abre a documentação no navegador.

### `railway completion`
Gera scripts de autocomplete para shell.

```bash
railway completion bash > /etc/bash_completion.d/railway
railway completion zsh > ~/.zsh/completions/_railway
railway completion fish > ~/.config/fish/completions/railway.fish
```

### `railway upgrade`
Atualiza o CLI pra última versão.

### `railway starship`
Helper pra integrar o status do Railway no prompt do shell Starship.

## CI/CD patterns

### GitHub Actions — deploy básico
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    container: ghcr.io/railwayapp/cli:latest
    env:
      RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
    steps:
      - uses: actions/checkout@v4
      - run: railway up --service api --ci
```

### GitHub Actions — PR environments efêmeros
Cria um environment Railway pra cada PR e destrói quando o PR fecha. Requer `RAILWAY_API_TOKEN` (account-level), não Project Token.

```yaml
name: PR Environment
on:
  pull_request:
    types: [opened, reopened, synchronize, closed]

jobs:
  create-env:
    if: github.event.action != 'closed'
    runs-on: ubuntu-latest
    container: ghcr.io/railwayapp/cli:latest
    env:
      RAILWAY_API_TOKEN: ${{ secrets.RAILWAY_API_TOKEN }}
    steps:
      - uses: actions/checkout@v4
      - run: railway environment new pr-${{ github.event.pull_request.number }}
      - run: railway up --service api --environment pr-${{ github.event.pull_request.number }} --ci

  destroy-env:
    if: github.event.action == 'closed'
    runs-on: ubuntu-latest
    container: ghcr.io/railwayapp/cli:latest
    env:
      RAILWAY_API_TOKEN: ${{ secrets.RAILWAY_API_TOKEN }}
    steps:
      - run: railway environment delete pr-${{ github.event.pull_request.number }} -y
```

A documentação tem guides oficiais em [docs.railway.com/guides/github-actions-pr-environment](https://docs.railway.com/guides/github-actions-pr-environment) e [docs.railway.com/guides/github-actions-post-deploy](https://docs.railway.com/guides/github-actions-post-deploy).

### GitLab CI
```yaml
deploy:
  image: ghcr.io/railwayapp/cli:latest
  variables:
    SVC: api
  script:
    - railway up --service $SVC --ci
  # RAILWAY_TOKEN deve estar configurado como protected variable no GitLab
```

## Patterns para Project/Account Tokens

- Use **Project Token** (`RAILWAY_TOKEN`) sempre que possível em CI — escopo mínimo, só deploy.
- Use **Account/Workspace Token** (`RAILWAY_API_TOKEN`) apenas para operações que mexem em estrutura (criar/deletar projeto, criar environment), tipicamente em ferramentas administrativas e PR environments dinâmicos.
- Tokens podem ser gerados em **Project Settings → Tokens** (Project) ou **Account Settings → Tokens** (Account).
- Nunca commit. Rotacione periodicamente.

## Como achar a flag que falta

Quando uma flag não estiver documentada aqui:
1. `railway <comando> --help` no terminal — sempre traz a lista mais atual da versão instalada.
2. [docs.railway.com/cli/<comando>](https://docs.railway.com/cli/) — referência online.
3. Source no GitHub: [github.com/railwayapp/cli](https://github.com/railwayapp/cli).
