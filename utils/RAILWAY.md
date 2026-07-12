# RAILWAY.md — Manual generalista de deploy no Railway

> Guia reutilizável para subir um projeto **api + web (+ Postgres, + cron)** no [Railway](https://railway.com) sem reaprender as particularidades a cada vez. Foco nas **armadilhas que custam tentativas** (monorepo, cookie cross-domain, auth de CLI não-interativa, TCP proxy do Postgres, cron). Destilado de deploys reais; complementa a doc oficial ([docs.railway.com](https://docs.railway.com)) e a skill `railway-ops`.
>
> **Nomenclatura:** serviços seguem o padrão de pastas do projeto — **`api`** (backend) e **`web`** (frontend), + `Postgres` e `cron`. Alinhado com a Arquitetura Base do template.
>
> **Como usar:** copie este arquivo para a raiz do projeto e vá preenchendo os placeholders `<...>` com os IDs/URLs/vars reais **conforme o deploy acontece**. Onde um valor é snapshot da conta (IDs, URLs, portas de proxy), marque como tal e reconfira com `railway status` / `railway variables` quando não bater. **Nunca** commitar segredos reais — só nomes de variáveis.

---

## 1. Topologia típica

Um único **projeto** Railway, environment `production`, com serviços que compartilham a rede privada. Layout comum de um app full-stack com job agendado:

| Serviço | O quê | URL pública |
| --- | --- | --- |
| **Postgres** | banco managed | (interno) `postgres.railway.internal:5432` |
| **api** | FastAPI/uvicorn (uv) | `https://<api>.up.railway.app` |
| **web** | SvelteKit adapter-node (pnpm/npm) | `https://<web>.up.railway.app` |
| **cron** | job agendado (Cron Service) | sem URL — roda no schedule e encerra |

- A **api** fala com o Postgres pela rede privada via reference var `${{Postgres.DATABASE_URL}}` (sem egress).
- A **web** fala com a api **pela rede privada** (`<api>.railway.internal:<porta>`) via um **proxy interno** (ver §6) — o browser só conversa com o domínio da web.
- Volume (ex.: `/data`) entra em serviços que precisam de disco persistente.

> **Nome dos serviços:** o Railway usa o nome que você der no `railway add --service <nome>`. Este guia usa `api`/`web`/`cron` para casar com o padrão de pastas do projeto.

---

## 2. Autenticação da CLI (a parte chata)

- **`railway login` é interativo** (abre browser). Num shell **não-interativo** (como o do agente de código), falha com `Cannot login in non-interactive mode` — inclusive `--browserless`. **Não há como contornar pelo agente.**
- **Solução que funciona:** o humano roda `railway login` **no terminal dele**. O token de sessão vai para `~/.railway/config.json`. Como o agente compartilha o mesmo `$HOME`, ele passa a operar autenticado (`railway whoami` reconhece a sessão). **Mesmo HOME = sessão compartilhada.**
- **Tokens não-interativos** (CI/headless): `RAILWAY_TOKEN` (Project Token — só deploy/logs/vars num projeto) ou `RAILWAY_API_TOKEN` (Account — cria recursos). Validar direto na API:

  ```bash
  curl -H "Authorization: Bearer $T" https://backboard.railway.com/graphql/v2 \
    --data '{"query":"query{me{email}}"}'
  # Atenção: a API responde 200 com erro no corpo, não 401. "Not Authorized" = token morto.
  ```

- `railway whoami` confirma quem está logado; `railway status` mostra projeto/env/serviço linkados.

---

## 3. Linkar o diretório ao projeto

```bash
railway link --project <PROJECT_ID>   # link por ID (evita o picker interativo)
railway status                        # confirma o vínculo
```

Grava `.railway/` no diretório (gitignored). Depois disso, os comandos assumem esse projeto. Use `--service <nome>` para mirar um serviço específico.

---

## 4. Provisionar recursos (do zero)

```bash
# Postgres managed (não-interativo) — injeta DATABASE_URL (privado),
# DATABASE_PUBLIC_URL (externo via proxy TCP) e PG*
railway add --database postgres

# Serviços vazios (recebem código depois via railway up)
railway add --service api
railway add --service web

# Volume (usa o serviço LINKADO — o comando NÃO aceita --service)
railway service api        # fixa o contexto na api
railway volume add --mount-path /data
```

> `railway volume add` **não aceita `--service`** — pega o serviço linkado no contexto. Fixe com `railway service <nome>` antes.

---

## 5. Variáveis

```bash
# --skip-deploys acumula sem disparar deploy (útil antes do 1º up)
railway variables --service api --skip-deploys \
  --set "DATABASE_URL=\${{Postgres.DATABASE_URL}}" \
  --set "SECRET_KEY=<forte>" \
  --set "APP_ENV=production" \
  --set "ALLOWED_ORIGINS=https://<web>.up.railway.app"

railway variables --service api --kv          # listar (KEY=VALUE)
railway variables --service api delete NOME   # remover
```

- **`${{Postgres.DATABASE_URL}}`** é uma **reference variable** — resolve para a URL **privada** do Postgres (sem egress). Se o app usa asyncpg, converta o scheme (`postgresql://` → `postgresql+asyncpg://`) num validator de config, não na var.
- **`--set` dispara deploy** por padrão; `--skip-deploys` não. Setar `ALLOWED_ORIGINS` depois que a web tiver URL redispara a api de propósito (cross-wire do CORS).

**Padrão recomendado — o app recusa subir inseguro:** faça a config validar e **falhar no boot** se `SECRET_KEY` estiver no default, `APP_ENV != production` em prod, ou `COOKIE_SECURE=false` em prod. Isso transforma erro de configuração de deploy em erro imediato e óbvio, não em vulnerabilidade silenciosa.

> Mantenha uma tabela `Var | Serviço | Valor prod | Nota` no projeto com os **nomes exatos** das vars. O erro clássico é o nome divergir do que a config lê (ex.: `APP_ENV` vs `ENVIRONMENT`) — sobe em modo dev sem as proteções.

---

## 6. ⚠️ Armadilha-mor: cookie cross-domain → PROXY na web

**O problema:** web e api ficam em domínios `*.up.railway.app` **diferentes**. A api seta o cookie de auth (HttpOnly) **no domínio dela**. O browser trata como cookie de terceiros; o servidor SSR da web **nunca recebe** esse cookie → sessão sempre `null` → **loop de login** (volta pro `/login` mesmo com login 200).

`SameSite=None; Secure` deixa o cookie existir, mas ele **pertence ao domínio da api** — não resolve o SSR.

**A solução: a web proxia a API pelo próprio domínio.**

- Um **proxy catch-all** na web (ex.: `src/routes/api/[...path]/+server.ts` no SvelteKit) repassa `/api/*` para a URL **privada** da api, encaminha método/body/headers e **propaga o `Set-Cookie`** na resposta. Como a resposta sai do domínio da web, o cookie passa a viver no **domínio da web**.
- O client HTTP usa `BASE_URL = '/api'` (relativo, mesmo domínio).
- O hook de SSR resolve o `/auth/me` (ou equivalente) direto pela URL interna privada (server-to-server, sem CORS).

**Resultado:** browser só fala com a web; cookie no domínio certo; SSR autentica; CORS some.

> Alternativa: domínio próprio compartilhado (`app.dominio.com` + `api.dominio.com` com cookie de domínio-pai). O proxy é mais simples e não exige DNS.

---

## 7. ⚠️ Armadilhas de build (monorepo + web)

Em ordem de quão cedo mordem:

1. **Monorepo: `railway up` envia a RAIZ do git.** Rodar `railway up` de dentro de `api/` ainda sobe o repo todo → o builder vê `api/` e `web/` como subpastas e falha ("could not determine how to build"). **Fix:** `--path-as-root` (usa o subdir como raiz do archive):

   ```bash
   railway up api --path-as-root --service api --ci
   railway up web --path-as-root --service web --ci
   ```

2. **pnpm workspace: "packages field missing or empty".** Um `pnpm-workspace.yaml` que só tenha `onlyBuiltDependencies` faz o pnpm 9 do builder entrar em modo workspace e exigir `packages:`. **Fix:** adicionar `packages: ['.']` ao yaml.
3. **Lockfile dessincronizado.** Trocar de adapter (ex.: `adapter-auto` → `adapter-node`) sem regerar o lock faz `--frozen-lockfile` falhar. **Fix:** regerar o lock (`pnpm install --lockfile-only`) e commitar.
4. **Node version.** Nixpacks usa Node 18 por default; stacks modernas (Vite recente, Svelte 5, etc.) exigem Node ≥22 — com `.npmrc` `engine-strict=true` vira erro fatal. **Fix duplo (cinto-e-suspensório):** `engines.node >= 22` no `package.json` **e** var `NIXPACKS_NODE_VERSION=22`.

---

## 8. Deploy, migrations e seed

```bash
# Deploy (CI mode = streama build, sai com exit code)
railway up api --path-as-root --service api --ci
railway up web --path-as-root --service web --ci

# Domínio público (1 gerado por serviço; nome é AUTO — o Railway
# NÃO deixa escolher o prefixo em *.up.railway.app; só custom domain resolve)
railway domain --service api
railway domain --service web

railway logs --service api
railway status
```

**Migrations e seed (rodar de fora, contra o DB de produção):** o `DATABASE_URL` privado (`*.railway.internal`) **só resolve dentro do Railway**. Para rodar local, use o `DATABASE_PUBLIC_URL` (proxy TCP externo):

```bash
PUB=$(railway variables --service Postgres --kv | grep '^DATABASE_PUBLIC_URL=' | cut -d= -f2-)
DATABASE_URL="$PUB" uv run alembic upgrade head
```

> Decisão recomendada: **migration é passo manual e consciente**, não roda no boot da api. Rode a migration **antes/junto** do deploy da api — a api nova sobe esperando as colunas/tabelas novas; até a migration rodar, endpoints que as tocam podem dar 500.

### ⚠️ Armadilha: num projeto ressubido do zero, o TCP proxy público do Postgres NÃO vem habilitado

A `DATABASE_PUBLIC_URL` sai com host/porta **vazios** (`postgresql://postgres:***@:/railway`) e qualquer `alembic`/script local falha (DNS `Name or service not known`, ou `invalid literal for int(): ''` na porta). O botão "Generate Domain" da UI cria um domínio **HTTP** — inútil para Postgres. **Solução: criar o TCP proxy via GraphQL:**

```bash
TOKEN=$(python3 -c "import json;print(json.load(open('$HOME/.railway/config.json'))['user']['token'])")
# <ENV_ID> (prod) e <POSTGRES_SVC_ID> vêm de `railway status --json`
curl -s https://backboard.railway.com/graphql/v2 \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"query":"mutation { tcpProxyCreate(input: { environmentId: \"<ENV_ID>\", serviceId: \"<POSTGRES_SVC_ID>\", applicationPort: 5432 }) { domain proxyPort } }"}'
```

Retorna `domain`/`proxyPort` (ex.: `<host>.proxy.rlwy.net:<porta>`) e o Railway repopula a `DATABASE_PUBLIC_URL` completa. **Antes de aplicar migrations, confirme o head com `alembic current`** e só então `upgrade head`.

### Consultar o DB de produção (leitura ad-hoc / diagnóstico)

**Caminho A — de fora, via proxy público.** Mesma `DATABASE_PUBLIC_URL` das migrations; serve para qualquer script local.

**Caminho B — de dentro do serviço, via `railway ssh`.** Três armadilhas:

- `railway run --service api <cmd>` roda o comando **na sua máquina** com as env vars injetadas — mas `DATABASE_URL` é a **privada**, que **não resolve de fora**. Não serve para consultar o banco daqui.
- Dentro do `railway ssh`, o `python` do PATH é o do **nix-profile** e **não tem as deps do app** (`ModuleNotFoundError`). O venv real do app costuma estar em **`/opt/venv`**.
- Mesmo com `/opt/venv/bin/python`, o **SQLAlchemy async pode quebrar** no shell SSH (`greenlet ... libstdc++.so.6: cannot open shared object file`) — as libs certas só carregam quando o processo sobe como o `web:` do Procfile. **Solução: pular o SQLAlchemy e usar `asyncpg` direto**, normalizando o scheme da URL:

  ```bash
  railway ssh --service api "cd /app && /opt/venv/bin/python -c \"
  import asyncio, os, re, asyncpg
  async def main():
      url=re.sub(r'^postgres(ql)?(\+asyncpg)?://','postgresql://',os.environ['DATABASE_URL'])
      c=await asyncpg.connect(url)
      print(await c.fetchval('select 1'))
      await c.close()
  asyncio.run(main())
  \""
  ```

> `railway ssh` exige sessão CLI autenticada (mesmo `$HOME` do humano — §2). Em modo automático, o agente pode pedir aprovação por ser shell no serviço de produção; uma regra `Bash(railway ssh:*)` em `.claude/settings.local.json` libera leituras de diagnóstico.

---

## 9. Cron Service (job agendado)

Um Cron Service executa o start command **uma vez por disparo** e encerra (não serve HTTP, não usa `Procfile`).

### 9.1 Criar

```bash
railway add --service cron

railway variables --service cron --skip-deploys \
  --set "DATABASE_URL=\${{Postgres.DATABASE_URL}}" \
  --set "SECRET_KEY=<mesma da api>" \
  --set "APP_ENV=production"
  # + as chaves que o job efetivamente usa

railway up api --path-as-root --service cron --ci   # deploy inicial (dry-run)
```

> O cron **não precisa** de `COOKIE_SECURE`/`COOKIE_SAMESITE`/`ALLOWED_ORIGINS` (não serve HTTP). Precisa só do que o job consome. Se a `Settings` valida `SECRET_KEY`, setar mesmo assim.

### 9.2 Schedule (cron expression)

O Railway usa **UTC**. Brasil (BRT) é UTC-3 (sem horário de verão desde 2019).

| Expression | UTC | BRT | Quando |
| --- | --- | --- | --- |
| `0 12 * * 1-5` | 12:00 | **09:00** | Dias úteis, abertura comercial BR |
| `0 13 * * 1-5` | 13:00 | 10:00 | Alternativa |

Sábado/domingo excluídos por `1-5`. Se o Brasil readotar horário de verão, ajustar a hora UTC.

### 9.3 Ativação segura de um job que escreve (dry-run → live)

Para jobs que produzem efeito externo irreversível (envio de e-mail, cobrança, etc.), **desligue o efeito por padrão** (flag `--live` ou env) e siga um protocolo antes do 1º live:

1. **Dry-run de reconhecimento** — rode sem `--live` e leia o relatório: quantos itens, para quem. Confirme que os números fazem sentido.
2. **Cap manual (se o volume for grande)** — restrinja a um piloto (ex.: 1 registro/1 cliente) antes do 1º live.
3. **1º live com piloto** — `railway run --service cron <cmd> --live`; confirme no log e no destino (ex.: provedor de e-mail) que o efeito ocorreu.
4. **Habilitar na rotina** — só então trocar o Start Command para incluir `--live`. **Esta é a decisão irreversível.**

### 9.4 Cron não recebe auto-deploy

O Cron Service usa a imagem do **último `railway up` manual**. Após cada deploy da api, sincronize o cron: `railway service cron && railway up`. O dashboard mostra o status do **último run**, não do código atual — após corrigir um bug, o indicador só muda no próximo run (ou force um redeploy).

---

## 10. Armadilhas de deploy diversas

1. **Contexto do serviço é global na CLI.** `railway up` usa o serviço linkado no contexto (`railway status` mostra qual). Sempre confirme com `railway service <nome>` antes de `railway up`.
2. **`railway up` é assíncrono.** Retorna após o upload; o build pode demorar a **começar** (fila). "Waiting for build to start..." é normal.
3. **Warnings ⚠️ no dashboard são do Docker BuildKit, não do código.** `SecretsUsedInArgOrEnv` vêm do Nixpacks injetando env vars como `ARG`/`ENV`. Não são corrigíveis do nosso lado; **não tentar corrigir com `nixpacks.toml`** — aumenta os warnings.
4. **Verificar se o deploy chegou.** Teste um endpoint **novo** (que não existia antes): 401/422 = chegou; **404 = código antigo ainda ativo**.

   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://<api>.up.railway.app/<endpoint-novo>
   ```

---

## 11. Hardening pós-deploy (checklist)

- **Rate-limit** em `/auth/login` (ou equivalente).
- **Security headers** (HSTS, `X-Content-Type-Options: nosniff`, CSP).
- **Expiração de sessão/JWT** curta e sensata.
- **Usage limit (hard)** no projeto Railway — rede de segurança contra conta surpresa.
- **Backup do Postgres** antes de qualquer operação de escrita irreversível.
- Rodar a skill `cybersecurity` (e `llm-security` se houver LLM) no pré-deploy.

---

## 12. Cheatsheet

```bash
railway whoami                                          # quem está logado
railway link --project <ID>                             # linkar projeto
railway status                                          # contexto atual
railway variables --service <s> --kv                    # ver vars
railway variables --service <s> --set K=V               # setar var (dispara deploy)
railway up <subdir> --path-as-root --service <s> --ci   # deploy (monorepo)
railway logs --service <s>                              # logs
railway domain --service <s>                            # gerar/ver domínio
railway connect postgres                                # abre psql no DB
railway redeploy                                        # redeploy do último build (aplica var)
```

> **Regra de ouro:** antes de qualquer escrita irreversível em produção (DB, provedor externo), dry-run/preview e conferir números. Faça a config **recusar subir inseguro** (SECRET_KEY/COOKIE_SECURE/APP_ENV) — é a primeira rede de segurança; o dry-run é a segunda.
