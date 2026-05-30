# Receitas de arquitetura — Hetzner + Coolify

Quatro receitas prontas para os cenários mais comuns. Cada uma tem (a) quem é o cliente típico, (b) o desenho, (c) custo mensal estimado, (d) onde costuma quebrar primeiro.

Use estas como ponto-de-partida; ajustar para o caso específico. Sempre validar preços atuais antes de cotar.

## Índice

1. [Single-VPS Coolify (€10-20/mês)](#receita-1-single-vps-coolify)
2. [Single-VPS com Build Server separado (€15-30/mês)](#receita-2-single-vps-com-build-server)
3. [App + Database separado (€25-60/mês)](#receita-3-app--database-separado)
4. [HA com Load Balancer + 2-3 nodes (€80-150/mês)](#receita-4-ha-com-load-balancer)
5. [Híbrido Cloud + Dedicated via vSwitch (€60-150/mês)](#receita-5-híbrido-cloud--dedicated)

---

## Receita 1: Single-VPS Coolify

**Cliente típico**: dev solo, side project, MVP de SaaS, blog/portfólio com features dinâmicas, agência pequena com 1-5 sites de cliente leves.

**Desenho**:
- 1 servidor Hetzner Cloud, EU-central
- Coolify self-hosted instalado nele
- Apps, bancos pequenos e reverse proxy tudo no mesmo container Docker network
- Backups configurados pra Object Storage Hetzner ou Backblaze B2

```
┌─────────────────────────────────────────────┐
│  Hetzner Cloud CPX22 ou CAX21 (FSN/NBG/HEL) │
│  ┌─────────────────────────────────────┐    │
│  │ Docker network "coolify"            │    │
│  │  ├─ traefik (proxy + SSL)           │    │
│  │  ├─ coolify (UI + agents)           │    │
│  │  ├─ app-1 (Next.js)                 │    │
│  │  ├─ app-2 (Django)                  │    │
│  │  ├─ postgres-app-1                  │    │
│  │  └─ redis                           │    │
│  └─────────────────────────────────────┘    │
│  Firewall Hetzner: 22, 80, 443              │
└─────────────────────────────────────────────┘
        ↓                          ↓
   Object Storage Hetzner    Cloudflare DNS
   (backups + uploads)       (proxy + cache)
```

**Custo mensal estimado** (EUR, excl. VAT):

| Item | Custo |
|---|---|
| CPX22 EU (2 vCPU, 4 GB, 80 GB, 20 TB) | €7.05 |
| Primary IPv4 | €0.50 |
| Backups +20% | €1.51 |
| Object Storage (1 TB incluso) | €4.99 |
| **Total** | **~€14/mês** |

Variação ARM: CAX21 (€6.49) + IPv4 + backups + storage = ~€13.50/mês.

**Quando cresce, quebra**:
- Build de Next.js / Nuxt come toda a RAM → OOM (→ Receita 2)
- Banco cresce e começa a competir por IO com app → latência sobe (→ Receita 3)
- App vira viral, > 50k requests/dia → CPU satura no pico (→ rescale CPX32 ou Receita 4)

**O que monitorar**: `free -h` (RAM), `df -h` (disco — Docker layers crescem silenciosamente, rodar `docker system prune` mensal), `uptime` (load average). Coolify tem Sentinel embutido em versões recentes.

---

## Receita 2: Single-VPS com Build Server separado

**Cliente típico**: dev/agência rodando ≥1 Next.js / Nuxt / SvelteKit em produção, ou monorepo grande, onde build OOMs no servidor pequeno mas a aplicação rodando é leve.

**Desenho**:
- Mesma topologia da Receita 1, mas com servidor **adicional** marcado como "Build Server" no Coolify
- Coolify usa o build server pra rodar `docker build` e depois publica imagem final no servidor de produção (push pra Docker registry interno ou direto via SSH)

```
┌─────────────────────────────────┐      ┌────────────────────┐
│  Coolify + Apps (CPX22)         │ ──▶  │  Build Server      │
│  - production traffic           │      │  CPX32 ou CPX42    │
│  - banco                        │      │  (sob demanda)     │
└─────────────────────────────────┘      └────────────────────┘
```

**Custo mensal estimado**:

| Item | Custo |
|---|---|
| Coolify+apps server CPX22 | €7.05 |
| Build Server CPX32 (4 vCPU, 8 GB) | €13.10 |
| IPv4 + Backups + Object Storage | ~€7 |
| **Total** | **~€27/mês** |

**Otimização**: o Build Server **pode ser provisionado on-demand via API Hetzner / Coolify integration** — sobe ao iniciar deploy, derruba após terminar. Em Hetzner Cloud (billing horário) isso economiza muito se deploys são raros. Implementação: webhook GitHub → script → `hcloud server create` → aguarda → Coolify build → `hcloud server delete`. Mais complexidade; vale para times com volume.

**Quando cresce, quebra**: mesmas pegadinhas da Receita 1 no servidor de prod (saturação CPU, banco competindo com app no IO).

---

## Receita 3: App + Database separado

**Cliente típico**: SaaS em produção real (milhares de usuários ativos), banco crítico onde noisy neighbor (CCX/dedicado) ou IO consistente importa, ou necessidade de escalar app e banco em ritmos diferentes.

**Desenho**:
- 1 servidor "app" (CPX42) onde Coolify roda + apps stateless
- 1 servidor "db" (CCX23 ou AX42 dedicado) só com PostgreSQL/MySQL principal, gerenciado **também** pelo Coolify
- Os dois conectados via Network privada Hetzner em `eu-central`
- App conecta via IP privado (10.x.x.x) — sem custo egress

```
┌─────────────────────────────────┐
│  Coolify + Apps (CPX42)         │
│  IP público + private 10.0.0.10 │
└───────────┬─────────────────────┘
            │ Network privada Hetzner
            │ (zona eu-central)
┌───────────▼─────────────────────┐
│  DB Server (CCX23 ou AX dedicado)│
│  PostgreSQL gerenciado pelo Coolify
│  IP privado 10.0.0.20 (sem público)│
└─────────────────────────────────┘
```

**Por que separar**:
1. Banco no CCX/dedicado tem CPU consistente — sem brigas por vCPU em pico
2. Pode-se escalar app (rescale CPX42 → CPX52) sem mexer no banco
3. Falha do app server não afeta banco diretamente
4. Snapshot do banco vira "backup dourado" simples (Hetzner Snapshot do disco)

**Custo mensal estimado** (versão Cloud-only):

| Item | Custo |
|---|---|
| App server CPX42 (8 vCPU, 16 GB) | €24.70 |
| DB server CCX23 (4 vCPU dedicado, 16 GB) | €25.99 |
| IPv4s (×2) | €1.00 |
| Backups +20% no app | €4.94 |
| Backups +20% no DB (ou snapshots manuais) | €5.20 |
| Object Storage (backups DB) | €4.99 |
| **Total** | **~€67/mês** |

Versão híbrida (DB em dedicado): substituir CCX23 (€25.99) por AX42 (€39-46) — custo total ~€80/mês, mas hardware muito mais robusto e tráfego inter-Cloud-Robot grátis via vSwitch. Ver Receita 5.

**Quando cresce, quebra**:
- App server CPU/RAM satura → rescale (instant via Hetzner Cloud) ou virar Receita 4
- DB sustained IOPS bate teto Volume (5000 IOPS sustained) → migrar pra Dedicated com NVMe local (Receita 5)
- Single point of failure no DB — para HA, master + replica (precisa 2 DBs + algo gerenciando failover; complexidade alta, considerar managed db terceiro)

---

## Receita 4: HA com Load Balancer + 2-3 nodes

**Cliente típico**: SaaS com SLA contratual, app que **não pode** ficar offline durante deploys ou reinicialização de host. Geralmente B2B.

**Desenho**:
- Hetzner Load Balancer (LB11 ou LB21) recebendo público
- 2-3 servidores idênticos "app", cada um com Coolify ou containers gerenciados externamente
- DB separado em CCX/Dedicado (Receita 3)
- Apps **stateless** (sessions em Redis/DB, uploads em Object Storage)

```
            Internet
               │
        ┌──────▼─────────┐
        │ Hetzner LB     │  (LB11 ou LB21)
        │ Round Robin    │
        └──┬──────┬──────┘
           │      │
    ┌──────▼┐  ┌──▼─────┐
    │ App A │  │ App B  │  (CPX32 cada, Placement Group anti-affinity)
    └───┬───┘  └───┬────┘
        │          │
        │  Network privada Hetzner
        ▼          ▼
    ┌────────────────────┐
    │ DB CCX/Dedicated   │
    └────────────────────┘
```

**Considerações cruciais**:
- **Apps precisam ser stateless**. Sessions em Redis externo, uploads em Object Storage, não em filesystem local. Se app fez `fs.writeFile('/tmp/uploads')`, vai estar em só uma das instâncias.
- **Coolify v4 não gerencia escalonamento horizontal nativamente** (no momento). Deploy "rolling update" em multi-server precisa de ferramentas adicionais ou Docker Swarm mode.
- Alternativa simpler: **2 servidores app idênticos + LB**, deploys são "drain um, deploy, validar, fazer o outro" manual ou via script.

**Custo mensal estimado**:

| Item | Custo |
|---|---|
| Hetzner LB21 | €16.40 |
| 2× CPX32 (app, em placement group) | €26.20 |
| 1× CCX23 (DB) | €25.99 |
| IPv4s + IPs do LB | ~€2 |
| Backups | ~€11 |
| Object Storage | €4.99 |
| **Total** | **~€87/mês** |

3 nodes app em vez de 2: +€13/mês.

**Quando cresce, quebra**: replicação de DB vira gargalo (master só), sessões em Redis viram gargalo (Redis Cluster necessário), deploys precisam orquestração séria (Coolify pode não bastar — considerar Kubernetes ou Nomad ou Docker Swarm).

---

## Receita 5: Híbrido Cloud + Dedicated via vSwitch

**Cliente típico**: SaaS maduro, ou app data-heavy (analytics, ML inference, ETL), onde **hardware físico** para alguma parte traz ganho significativo de custo/performance vs Cloud equivalente.

**Desenho**:
- Coolify em CPX22-32 (orquestra)
- 1-2 servers app em Cloud (CPX, escaláveis)
- 1 servidor dedicado AX/EX (banco + jobs pesados + grandes RAM)
- Tudo na mesma rede privada via Network + vSwitch (zona `eu-central` only)

```
                   Internet
                      │
              ┌───────▼───────┐
              │ Coolify CPX22 │ ◀── Dashboard / Build / SSH gateway
              └───────┬───────┘
                      │ Network privada (10.0.0.0/24)
       ┌──────────────┼──────────────┐
       │              │              │ vSwitch
┌──────▼────┐   ┌─────▼────┐   ┌─────▼─────────────┐
│ App CPX32 │   │ App CPX32│   │ Dedicated AX102   │
│ stateless │   │ stateless│   │ - PostgreSQL      │
└───────────┘   └──────────┘   │ - Redis           │
                               │ - workers BG      │
                               │ - file storage    │
                               └───────────────────┘
```

**Por que faz sentido**:
- Dedicated AX102 = 16-core Ryzen, 128 GB DDR5, 2× 1.92 TB NVMe = ~€119/mês. Em Cloud equivalente (CCX43, 16 vCPU dedicado, 64 GB) = ~€100/mês mas com **metade da RAM** e disco menor.
- Bandwidth ilimitado no dedicated 1 Gbit/s — workloads "exfiltração-pesada" (backups, sync) ficam grátis vs €/TB em Cloud.
- IO local NVMe no Dedicated é faster e mais consistente que Volume networked.

**Custo mensal estimado**:

| Item | Custo |
|---|---|
| Coolify CPX22 | €7.05 |
| 2× App CPX32 | €26.20 |
| Dedicated AX102 | €119.00 |
| IPv4s, backups (Cloud only) | ~€7 |
| Object Storage | €4.99 |
| **Total** | **~€164/mês** |

Para mesmo poder em Cloud-only: ~€300-400/mês.

**Quando cresce, quebra**:
- Dedicated não escala horizontalmente — só vertical (upgrade pra modelo maior, leva semanas)
- Falha do dedicated = downtime; pra HA, dois dedicateds em replicação (cost: 2x), ou DB managed externo
- vSwitch só EU — se precisa servir US/SIN com baixa latência, esse modelo não estende lá

---

## Decisão rápida: qual receita usar

```
                       Quanto vale a operação?
                              │
              ┌───────────────┼───────────────┐
              │               │               │
         <€20/mês          €30-80/mês      >€80/mês
              │               │               │
         Receita 1       Quanta carga real?  HA é requisito?
                              │               │
                    ┌─────────┼────────┐   Sim │  Não
                    │                  │       │     │
                  Build OOM?      DB pesado?  Recipe 4   Workload data-pesada?
                    │                  │                   │
                  Sim │ Não         Sim │ Não           Sim │ Não
                    │     │           │     │             │     │
                Receita 2 │       Receita 3 Receita 1   Receita 5  Receita 3
                          │
                       Receita 1
```

## Sizing rápido (rule of thumb)

- **2 vCPU / 4 GB / 80 GB** = Coolify + 1-3 apps pequenas + 1 banco pequeno. Cabe MVP. **CPX22 ou CAX21**.
- **4 vCPU / 8 GB / 160 GB** = Coolify + 5-10 apps + 2-3 bancos. Cabe agência pequena ou SaaS inicial. **CPX32 ou CAX31**.
- **8 vCPU / 16 GB / 240 GB** = Coolify + ~15 apps incluindo builds. Cabe operação séria. **CPX42 ou CCX23**.
- **16 vCPU / 32 GB** = stage onde faz sentido separar (Receita 3+). Single VPS deste tamanho começa a ter custo cruzando com ter 2 menores + LB.

**Disco**: cresce com docker images (~500 MB-2 GB cada), logs, banco data, uploads. Subestimar disco é mais comum que CPU/RAM. **80 GB cabe ~10-15 apps Coolify + bancos pequenos**, depois disso começa a apertar e Volume virtual extra fica barato (€0.044/GB).

## Tradução custo PaaS → Hetzner

Cliente vindo de Vercel/Heroku/Render frequentemente subestima Hetzner achando "vai precisar de servidor enorme". Quase nunca precisa.

| Está pagando | Workload típico | Equivalente Hetzner |
|---|---|---|
| Vercel Pro $20-50/usuário | Next.js + Postgres pequeno | Receita 1 (€14) |
| Heroku $25 dyno + $50 Postgres + $7 Redis = $82 | Rails / Django + DB + cache | Receita 1 ou 3 (€14-30) |
| Render $20 web + $7 DB + $7 Redis = $34 | Node + Postgres + Redis | Receita 1 (€14) |
| Railway $20-100 ad-hoc | Postgres + 2-3 apps | Receita 1 ou 2 (€14-30) |
| Fly.io $30-100 ad-hoc | Multi-region app | Receita 1 EU + CDN Cloudflare (€14) |
| AWS Elastic Beanstalk + RDS + ELB ~$200 | App + DB managed + LB | Receita 4 (€87) |

Economia típica: **70-90%**. Trade-off: você opera o Coolify, fato (atualizações, backups, monitoramento). Para times pequenos onde 1 dev já saca infra, vale absurdamente. Para times de produto sem DevOps, Coolify Cloud (managed) ainda economiza 50-70% vs PaaS gigante.

## Hosting de software self-hosted popular sobre essa stack

Casos comuns que o Coolify resolve elegantemente sobre Hetzner:

| Software | Recipe recomendada | Notas |
|---|---|---|
| n8n (workflow automation) | Receita 1 (CPX22+) | Coolify tem n8n no marketplace one-click; configurar persistent storage para `/home/node/.n8n` |
| Plausible (analytics) | Receita 1 | Marketplace; precisa de PostgreSQL + Clickhouse; CPX22 mínimo, CPX32 confortável |
| Ghost (newsletter/blog) | Receita 1 | MySQL/MariaDB; Nixpacks ou marketplace |
| Supabase (Postgres+API self-hosted) | Receita 3 | Self-host é várias containers; pesado; CPX42 ou Receita 5 com Dedicated pro DB |
| Outline / BookStack (wikis) | Receita 1 | Standard PostgreSQL/MySQL setup |
| Cal.com | Receita 1 | Next.js + Postgres |
| Listmonk / Mautic (email mkt) | Receita 1 + SMTP externo | Lembrar do bloqueio SMTP Hetzner — usar Postmark/Resend/etc. |
| Mastodon / Pleroma | Receita 3+ | Ruby/Elixir + Postgres + Redis + storage; precisa S3 e media transcoding |
| LLM inference (Ollama, vLLM) | Dedicated com GPU (raro em Hetzner) | Hetzner GPU é pontual; para sério → Lambda/RunPod |
