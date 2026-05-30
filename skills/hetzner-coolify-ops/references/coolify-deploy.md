# Coolify em Hetzner — instalação, deploy e operação

Esta reference é o manual operacional do Coolify rodando sobre Hetzner. Para conceitos de Hetzner Cloud (servidor, firewall, etc.) ver `cloud-products.md`. Para preços ver `pricing.md`.

## Table of contents

- [Coolify self-hosted vs Coolify Cloud](#self-hosted-vs-cloud)
- [Requisitos do servidor](#requisitos-do-servidor)
- [Instalação self-hosted (curl install)](#instalação-self-hosted)
- [Variáveis de ambiente do instalador](#variáveis-do-instalador)
- [Pós-instalação: criar admin, configurar domínio, fechar portas](#pós-instalação)
- [Conectar servidores (multi-server)](#conectar-servidores)
- [Conceitos: Projects, Environments, Resources, Destinations](#conceitos)
- [Conectar fontes Git (GitHub/GitLab/Bitbucket/Gitea)](#conectar-fontes-git)
- [Build Packs: Nixpacks, Static, Dockerfile, Docker Compose](#build-packs)
- [Environment Variables (runtime vs build)](#environment-variables)
- [Domínios e SSL](#domínios-e-ssl)
- [Databases one-click](#databases)
- [Persistent Storage (volumes)](#persistent-storage)
- [Backups do Coolify e dos bancos](#backups)
- [Atualizações e upgrades](#atualizações)
- [Reverse Proxy (Traefik vs Caddy)](#reverse-proxy)
- [Troubleshooting comum](#troubleshooting)

## Self-hosted vs Cloud

- **Self-hosted** (`https://github.com/coollabsio/coolify`): você roda o Coolify no seu próprio servidor Hetzner. **Grátis** (só paga o servidor). Você cuida de uptime do Coolify, updates, backups dele. Recomendado pra quem já gerencia infra.
- **Coolify Cloud** (`https://app.coolify.io`): a Coollabs (empresa do Coolify) gerencia o Coolify; você só conecta seus servidores Hetzner (ou outros) via SSH. Plano mensal pago. Recomendado pra quem não quer gerenciar o próprio Coolify mas quer manter os apps em servidores próprios.

Diferença prática quando se usa Hetzner:
- Self-hosted: 1 servidor Hetzner roda Coolify + apps (ou Coolify num server pequeno e apps em servers separados conectados via SSH)
- Cloud: o Coolify roda na infra deles; servidores Hetzner só recebem SSH do Coolify Cloud (portas 22 + 80 + 443 abertas no firewall)

**Esta reference cobre principalmente self-hosted** — é o caminho default de quem escolhe Hetzner.

## Requisitos do servidor

Mínimo declarado:
- CPU: **2 cores**
- RAM: **2 GB**
- Disco: **30 GB livres**

Realidade: 2 GB de RAM **mal cabe Coolify + 1 app pequena + 1 banco**. Pra qualquer uso real, ir de **4 GB para cima**. Se vai rodar build de Next.js / Nuxt no mesmo servidor, **8 GB+** ou usar Build Server separado (ver abaixo).

**Servidor LIMPO é fortemente recomendado** — o instalador instala Docker, configura `/data/coolify`, mexe em rede. Servidor com Docker pré-existente ou outros serviços em portas conflitantes (80/443) dá problema chato de debugar.

**OS suportados**:
- Debian-based: **Ubuntu LTS (22.04, 24.04)** e Debian — script automático
- Não-LTS Ubuntu (24.10): exige instalação **manual**
- RHEL-based (Rocky, Alma, Fedora, CentOS), SUSE-based, Arch, Alpine, Raspberry Pi OS 64-bit: também suportados
- Arquiteturas: AMD64 e ARM64 (CAX da Hetzner funciona)

**Docker via Snap NÃO é suportado** — se já tem Docker via snap, remover antes.

## Instalação self-hosted

Caminho mais rápido. Em servidor Ubuntu 24.04 LTS limpo:

```bash
ssh root@SEU_IP

# Atualizar antes (sem isso, problemas de Docker network em fresh Hetzner são comuns)
apt update && apt -y upgrade

# Instalar Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

O script faz:
- Instala curl, wget, git, jq, openssl se faltam
- Instala Docker Engine v24+
- Configura `/etc/docker/daemon.json` (logging, etc.)
- Cria diretório `/data/coolify/{source,ssh,applications,databases,backups,services,proxy,webhooks-during-maintenance}`
- Gera SSH key em `/data/coolify/ssh/keys/id.root@host.docker.internal` e adiciona ao `~/.ssh/authorized_keys` (Coolify usa essa pra SSH no próprio host como gerencia o Docker)
- Baixa `docker-compose.yml`, `.env` e sobe os containers Coolify
- Inicia o serviço

Duração: 2-5 min. Ao final imprime URL tipo `http://203.0.113.1:8000`.

### Variáveis do instalador

Passar como env antes do script pra customizar (todas opcionais):

```bash
env ROOT_USERNAME=admin \
    ROOT_USER_EMAIL=admin@example.com \
    ROOT_USER_PASSWORD='SenhaForte123!' \
    AUTOUPDATE=false \
    DOCKER_ADDRESS_POOL_BASE=172.16.0.0/12 \
    DOCKER_ADDRESS_POOL_SIZE=20 \
    bash -c 'curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash'
```

| Variável | Default | Quando setar |
|---|---|---|
| `ROOT_USERNAME` | - | Pra criar admin junto da instalação (evita race com bot que abre URL antes de você) |
| `ROOT_USER_EMAIL` | - | Idem |
| `ROOT_USER_PASSWORD` | - | Idem |
| `DOCKER_ADDRESS_POOL_BASE` | `10.0.0.0/8` | Se sua VPN/rede corporativa conflita com 10.x.x.x; usar `172.16.0.0/12` |
| `DOCKER_ADDRESS_POOL_SIZE` | `24` | Tamanho do subnet pra cada Docker network (16-28) |
| `AUTOUPDATE` | `true` | Setar `false` em produção pra controlar upgrades manualmente |
| `REGISTRY_URL` | `ghcr.io` | Custom registry pra imagens Coolify (raro) |

## Pós-instalação

1. **Abrir `http://SEU_IP:8000`** e **criar conta admin IMEDIATAMENTE** se não usou `ROOT_USERNAME` no install. Se alguém abrir antes de você, controla seu servidor. (Coolify avisa explicitamente.)
2. **Settings → Instance → "Instance URL"**: trocar de IP pra domínio (`https://coolify.seudominio.com`). Criar A record DNS apontando pro IP. Salvar. Coolify negocia Let's Encrypt automaticamente em 1-2 min.
3. **Servers**: o `localhost` (próprio servidor) já está listado. Clique → "Validate Server & Install Docker". Status fica verde "Proxy Running".
4. **Fechar portas que não usa mais**: no firewall (Hetzner Cloud Firewall, não UFW), remover regras 8000/6001/6002 inbound. Manter SSH (22), HTTP (80), HTTPS (443). O Traefik do Coolify recebe tudo em 80/443 e despacha pros containers internamente.
5. **Settings → Notifications**: conectar Discord/Slack/Telegram pra receber alertas de deploy success/fail e server health.
6. **Settings → Backup**: configurar backup do Coolify pra S3 (Object Storage Hetzner ou Backblaze B2 ou Cloudflare R2). Isso salva `/data/coolify/` periodicamente; sem isso, perder o servidor = perder configuração.

## Conectar servidores

Coolify pode gerenciar múltiplos servidores Hetzner a partir de uma única UI. Casos:

- **Servidor de build separado**: Coolify roda em CPX22 leve. Builds pesados (Next.js, Nuxt) rodam em CPX32 dedicado de build (provisionado on-demand ou permanente). Marca como "Build Server" em Coolify; ele faz checkout + build lá e só publica image final pro server de produção.
- **Servidores de aplicação distintos**: prod em FSN, staging em HEL, dev em NBG. Mesmo Coolify gerencia todos.
- **Servidor de banco isolado**: CCX dedicada (consistente em IO) só com bancos; apps em CPX shared.

Passo a passo pra adicionar server:
1. Provisionar Hetzner Cloud Server com Ubuntu LTS limpo
2. Coolify → Servers → New Server
3. Configurar:
   - Name (label legível)
   - IP do server
   - User SSH (root tipicamente)
   - SSH Key (Coolify oferece criar nova ou usar existente; copiar a public key dele)
4. **Adicionar a public key do Coolify no `~/.ssh/authorized_keys` do server destino** (manual via SSH inicial ou usar `ssh-copy-id`)
5. "Validate Server & Install Docker" — Coolify faz SSH, instala Docker, configura

**Coolify tem integração nativa com Hetzner API**: você pode adicionar um Cloud Provider Token (token Hetzner) e o Coolify cria servidores Hetzner direto pela UI sem ir ao Console. Endpoints expostos: `GET /api/v1/hetzner/locations`, `/server-types`, `/images`, `/ssh-keys`, `POST /api/v1/hetzner/servers`. Útil pra automação.

## Conceitos

- **Project**: bucket lógico. Tipicamente 1 project por cliente / 1 por app principal.
- **Environment**: dentro de project, ambientes como `production`, `staging`, `preview`. Cada ambiente é uma "instância" do project.
- **Resource**: o que roda. Tipos: Application (app deployável), Database, Service (one-click do marketplace tipo Plausible, n8n, Supabase). Resource vive dentro de um Environment.
- **Destination**: onde o resource roda. Padrão é o Docker network local (`coolify`). Para multi-server, você cria destination separado apontando pra outro server.
- **Source**: provedor Git (GitHub App, GitLab, Bitbucket, Gitea, Public Repo, Deploy Key).
- **Server**: o host físico/virtual que recebe deploys. Pode ser onde o próprio Coolify roda (`localhost`) ou outro.

## Conectar fontes Git

### GitHub App (recomendado)

Caminho mais limpo. Cria-se um GitHub App específico ligado à sua conta/org. Coolify só vê repos que você autorizou no app.

1. Coolify → Sources → New Source → GitHub App
2. Define nome do app (ex: "Coolify Production"), clica continuar — Coolify redireciona pra GitHub
3. No GitHub: criar app, selecionar repos (all ou specific), instalar
4. Volta pro Coolify: app configurado, repos listados
5. Webhooks são criados automaticamente — push em main → deploy auto

### Deploy Key

Pra repo privado sem instalar GitHub App. Coolify gera uma chave SSH, você adiciona no repo como "Deploy Key" (Settings → Deploy keys). Sem auto-deploy de PR/branches automáticos — você gatilha pela UI ou via webhook manual.

### Public Repository

Repos públicos não precisam de auth. Cola URL `https://github.com/user/repo`, escolhe branch.

## Build Packs

### Nixpacks (default)

Auto-detecta linguagem/framework pelos arquivos do repo (`package.json`, `requirements.txt`, `Gemfile`, etc.) e gera Docker image. Suporta out-of-the-box: Node.js, Python, Go, Rust, Java, Ruby, Elixir/Phoenix, PHP/Laravel, Django, Rails, Next.js, Nuxt, Vite, SvelteKit, Vue, Symfony.

**Versionamento do Node** dentro de Nixpacks: setar via `package.json`:
```json
"engines": {
  "node": "20.x"
}
```
Ou via `.nvmrc`, ou via env var `NIXPACKS_NODE_VERSION=20` em Coolify.

Comandos custom de build/start: env vars `NIXPACKS_BUILD_CMD`, `NIXPACKS_START_CMD`.

**Quando Nixpacks falha**: framework muito novo / não suportado, dependências de sistema incomuns (libs C, drivers), build muito custom. Pular pra Dockerfile.

### Static

Pra sites compilados pra arquivos estáticos (HTML/JS/CSS). Configurar:
- Build command (`npm run build`)
- Publish directory (`dist`, `build`, `out`)
- Custom 404 page (opcional)

Resulta em container nginx servindo `/usr/share/nginx/html`.

### Dockerfile

Quando o repo tem `Dockerfile` próprio. Coolify clona, roda `docker build`, sobe container. Configurações:
- Path do Dockerfile (default `./Dockerfile`)
- Build context (default `.`)
- Build args (passados como `--build-arg`)
- Port exposto (default 3000; Coolify configura Traefik pra rotear pra essa porta)

### Docker Compose

Quando o repo tem `docker-compose.yml` ou `compose.yaml`. Coolify lê e sobe todos os services. Use quando: app precisa de múltiplos containers que se conhecem (app + worker + redis dedicado, etc.) ou quando o app já é distribuído como Compose pra docs/dev local.

Adicionalmente, dá pra subir Compose **sem repo Git** (Coolify mantém o YAML internamente) — útil pra colar um docker-compose copiado de docs de software self-hosted.

## Environment variables

- Application → **Environment Variables**
- Marcar **"Is Build Variable?"** se a var precisa estar disponível durante `docker build` (ex: `NEXT_PUBLIC_API_URL` do Next.js — viralia bundle JS no build, não em runtime). Caso contrário, fica em runtime só (mais seguro pra segredos).
- Coolify suporta **"shared variables"** entre apps no mesmo project / environment / team — útil pra coisas como `DATABASE_URL` que múltiplos apps consomem.
- Tem **secret** flag — não loga valor em UI, embora exposto pro container.

**Pra Next.js especificamente**:
- `NEXT_PUBLIC_*` precisa estar em build vars
- `NODE_ENV=production` já é setado por Nixpacks
- Se app está atrás de proxy reverso (Traefik), setar `NEXT_PUBLIC_API_URL` com `https://` (não `http://`) pra evitar mixed content

## Domínios e SSL

- Application/Service → **Domains** → adicionar `https://app.seudominio.com`
- DNS: A record (IPv4) ou AAAA (IPv6) → IP do servidor
- Coolify pede Let's Encrypt automaticamente via Traefik. Primeira emissão demora ~30s-2min.
- Múltiplos domínios por app: aceita lista separada por vírgulas
- Subdomínio wildcard: usar Traefik DNS challenge (ver "DNS Challenge" nos docs do Coolify, requer credenciais DNS API do provedor)

**SSL não emite, possíveis causas**:
1. DNS ainda propagando (esperar 5-30 min, testar `dig +short app.seudominio.com`)
2. Porta 80 fechada (Let's Encrypt usa HTTP-01 challenge na :80). Verificar firewall Hetzner.
3. Rate limit do Let's Encrypt (5 falhas/hora por domínio) — esperar 1 hora
4. CAA record bloqueando Let's Encrypt — checar `dig CAA seudominio.com`
5. Domínio em RBL ou IP em Spamhaus pode bloquear emissão — incomum mas acontece

## Databases

Coolify provisiona com 1 clique: PostgreSQL, MySQL, MariaDB, MongoDB, Redis, DragonFly, KeyDB, Clickhouse.

- Cada DB roda como container, dados em named volume Docker
- Coolify gera credenciais automáticas
- Connection string disponível em "Show password" no UI
- **Por default não é exposto à internet** — só na network Docker interna. Apps no mesmo Coolify acessam por nome (`postgres-xxxxxx.coolify`).
- Pra expor externamente (cuidado!): Settings do DB → "Public" → habilita uma porta externa. **Sempre** com password forte e firewall restringindo source IP.

### Backup de databases

Database → **Backups** → schedule cron (ex: `0 3 * * *` = 3am diário) + destination (Local ou S3).

Local: armazena em volume Docker no próprio server (ruim, server some = backup some).
S3: aponta pra bucket Object Storage Hetzner / Backblaze / R2 — **sempre fazer assim em produção**.

**Restore**: ainda manual no v4 — abrir terminal no container, `pg_restore`/`mysql` direto. Coolify tem feature de restore UI em roadmap.

## Persistent Storage

Apps stateless ignoram isso. Apps que precisam guardar arquivos (uploads de usuário, cache local pesado, SQLite db do app):

- Application → **Storages** → adicionar volume
- Tipos:
  - **File Mount**: monta arquivo específico do host no container (ex: config file)
  - **Volume Mount**: monta diretório/volume nomeado persistente (ex: `/app/uploads`)
- Coolify gerencia via Docker named volumes; data persiste entre deploys
- **Não é replicado** entre servidores — apps com persistent storage não rolam em multi-server load-balanced facilmente. Solução: **mover storage pra S3** (Object Storage Hetzner) com SDK no código.

## Backups (do Coolify e dos bancos)

Camadas de backup pra produção séria:

1. **Coolify config**: Settings → Backup → S3 destination → frequência
2. **Database backups**: cada DB → Backups → cron + S3
3. **Filesystem do app** (se persistent storage): manual (cron job que tar | aws s3 cp) ou Borg/Restic
4. **Snapshot do servidor Hetzner**: opcional, semanal — "imagem do mundo todo"
5. **Disaster recovery doc**: como recriar do zero: que servidor, que script de install, que backup restaurar, em que ordem

## Atualizações

- **Coolify auto-update padrão LIGADO**. Verifica novas versões periodicamente, baixa, reinicia containers do próprio Coolify. Comportamento OK pra hobbyista, **arriscado pra produção** (atualização pode quebrar workflow num horário ruim).
- **Desligar** auto-update: Settings → Coolify → toggle off. Ou setar `AUTOUPDATE=false` no install original.
- **Atualizar manualmente**: SSH no server, `curl -fsSL https://cdn.coollabs.io/coolify/upgrade.sh | bash`. Ou no UI: Settings → Updates → "Update Coolify" botão.
- **Antes de atualizar major version** (ex: 4.x → 5.x): ler changelog, fazer Snapshot Hetzner do servidor, backup do `/data/coolify/`.

## Reverse Proxy

- **Traefik (padrão)**: configurado automaticamente. Suporta middlewares (basic auth, redirects, rate limit), wildcard SSL via DNS challenge, dashboards. **Recomendado pra 99% dos casos**.
- **Caddy** (opcional): mais simples, sintaxe mais limpa, suporta automatic HTTPS. Trocar em Settings → Proxy. Menos middlewares disponíveis fora-da-caixa.

**Não trocar de proxy com apps já em produção** — mudança de proxy desabilita SSL existente temporariamente; planejar janela.

## Troubleshooting

### Dashboard inacessível (`http://IP:8000` não responde)
- Containers caíram: SSH → `docker ps --filter name=coolify` → se faltam containers, `docker compose -f /data/coolify/source/docker-compose.yml -f /data/coolify/source/docker-compose.prod.yml up -d`
- Firewall fechou 8000: verificar Hetzner Cloud Firewall + UFW local
- Server overloaded (OOM): `dmesg | grep -i oom`, `free -h`, escalar plano

### Bad Gateway 502
- App container crashou pós-deploy: logs do app no Coolify UI
- App não escuta na porta certa: verificar `PORT` env var; Nixpacks usa 3000 default; Dockerfile precisa `EXPOSE 3000`
- App levou tempo demais pra subir: aumentar `Startup Delay` no Health Check

### No Available Server 503
- Coolify perdeu conexão SSH com server destino: Servers → server → re-validate
- Server destino com Docker quebrado: SSH manual, `systemctl status docker`

### Gateway Timeout 504
- App leva > 30s pra responder: otimizar app ou aumentar timeout em Traefik (em advanced)
- Worker travado processando job longo: usar fila assíncrona, não bloquear request HTTP

### Failed to get access token during deployment
- GitHub App PAT expirou: re-autorizar GitHub App em Sources
- Token GitLab expirou: gerar novo, atualizar em Source

### Build crashes com OOM
- Server sem RAM suficiente pra build (Next.js / Nuxt comem RAM grande). Soluções:
  - Aumentar plano (rescale Hetzner pra CPX32+)
  - Configurar Build Server separado (Servers → server → marcar "Build Server")
  - Limitar Node heap: env `NODE_OPTIONS=--max-old-space-size=1024`
  - Buildar em CI externamente, publicar imagem Docker, fazer Coolify pull (Source = "Docker Image")

### SSL Let's Encrypt não emite
- Ver seção "Domínios e SSL" acima

### Coolify dashboard muito lento
- Logs acumulados (em projetos antigos): Settings → cleanup; ou manualmente truncar `/data/coolify/source/storage/logs/*.log`
- Servidor undersized pro número de apps: escalar
- DB do próprio Coolify (SQLite) crescendo demais: raro em < 50 apps; aceitar ou migrar pra PostgreSQL (advanced)

### 2FA travou (admin lockout)
- SSH no server → `docker exec -it coolify php artisan tinker` → `User::where('email','admin@x.com')->first()->update(['two_factor_secret' => null, 'two_factor_recovery_codes' => null]);`

### Hetzner-específico: SMTP outbound não funciona
- Esperado nos primeiros 30 dias da conta (anti-spam Hetzner bloqueia TCP 25/465 outbound)
- Solução: SMTP relay externo (Postmark / Resend / Mailgun / Amazon SES)
- Após 30 dias e ≥1 fatura paga, abrir ticket no Console pedindo unblock com use case explícito
