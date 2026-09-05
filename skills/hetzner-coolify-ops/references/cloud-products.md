# Hetzner Cloud — produtos em detalhe

Leia esta reference quando precisar de specs detalhadas de Cloud Servers, Storage, Networking ou limites por conta. Para preços atuais sempre verifique web (Hetzner reestrutura linhas com frequência), mas os números aqui dão base de raciocínio sólida.

## Table of contents

- [Cloud Servers — visão geral e famílias](#cloud-servers)
- [Locations e Network Zones](#locations-e-network-zones)
- [Primary IPs](#primary-ips)
- [Volumes (block storage)](#volumes)
- [Backups vs Snapshots](#backups-vs-snapshots)
- [Object Storage (S3)](#object-storage)
- [Networks privadas e vSwitch](#networks-privadas-e-vswitch)
- [Load Balancers](#load-balancers)
- [Firewalls Cloud](#firewalls-cloud)
- [Floating IPs](#floating-ips)
- [Placement Groups](#placement-groups)
- [Apps (one-click marketplace)](#apps)
- [Limites por conta e por servidor](#limites)
- [Projetos, membros e roles](#projetos-membros-e-roles)
- [hcloud CLI e Hetzner Cloud API](#cli-e-api)

## Cloud Servers

Quatro famílias ativas. As gerações e os preços mudam; confirme o nome exato, disponibilidade e tarifa na [documentação oficial](https://docs.hetzner.com/cloud/servers/overview/) e na API antes de provisionar. Servidores antigos podem continuar funcionando sem aceitar novas criações.

### CX (Cost-Optimized x86, shared vCPU, EU-only)

A linha mais barata. Hardware Intel ou AMD (depende da location), NVMe SSD em RAID10 local, vCPU compartilhado. **Disponível só em FSN, NBG, HEL** (network zone `eu-central`). Disponibilidade pode oscilar em horários de pico — Hetzner declara explicitamente que pode "temporariamente restringir" criação em locais saturados.

Planos típicos Gen3 (sempre confirmar antes de cotar):

| Plano | vCPU | RAM | Disco | Traffic incluso | Preço aprox. |
|---|---|---|---|---|---|
| CX23 | 2 | 4 GB | 40 GB | 20 TB | confirmar |
| CX33 | 4 | 8 GB | 80 GB | 20 TB | confirmar |
| CX43 | 8 | 16 GB | 160 GB | 20 TB | €11.49/mês |
| CX53 | 16 | 32 GB | 320 GB | 20 TB | €22.49/mês |

Bom para: dev, staging, side projects, MVPs, blogs, vitrines de empresa, scrapers de baixa carga.

### CPX (Regular Performance AMD EPYC, shared vCPU, global)

Hardware AMD EPYC (Genoa em deploys recentes). Melhor single-core que CX. **Disponível em todas as 6 locations** (FSN/NBG/HEL/ASH/HIL/SIN). Padrão recomendado para produção pequena/média.

Planos típicos Gen2:

| Plano | vCPU | RAM | Disco | Traffic EU | Traffic US | Traffic SIN | Preço aprox. EU |
|---|---|---|---|---|---|---|---|
| CPX22 | 2 | 4 GB | 80 GB | 20 TB | 1 TB | 0.5 TB | confirmar |
| CPX32 | 4 | 8 GB | 160 GB | 20 TB | 2 TB | 1 TB | €13.10/mês |
| CPX42 | 8 | 16 GB | 240 GB | 20 TB | 3 TB | 2 TB | €24.70/mês |
| CPX52 | 16 | 32 GB | 360 GB | 20 TB | 4 TB | 3 TB | €54.40/mês |
| CPX62 | 16 | 32 GB | 640 GB | 20 TB | 5 TB | 4 TB | (verificar) |

**Atenção** ao corte de tráfego incluído fora da EU (dez/2024 nos EUA, mais agressivo em SIN). Modelar bandwidth explicitamente para essas regiões.

Bom para: produção de SaaS, APIs, sites com tráfego real, ambientes mistos build+run.

### CAX (ARM64 Ampere Altra, shared vCPU, EU-only)

Hardware Ampere Altra (ARM64). ~10-15% mais barato que CPX equivalente, mais eficiente energeticamente. **EU-only**.

| Plano | vCPU | RAM | Disco | Traffic | Preço aprox. |
|---|---|---|---|---|---|
| CAX11 | 2 | 4 GB | 40 GB | 20 TB | confirmar |
| CAX21 | 4 | 8 GB | 80 GB | 20 TB | €6.49/mês |
| CAX31 | 8 | 16 GB | 160 GB | 20 TB | €12.49/mês |
| CAX41 | 16 | 32 GB | 320 GB | 20 TB | €24.49/mês |

**Verificar compatibilidade ARM64** antes de cotar: Node.js sim, Python sim, Go sim, Docker (imagens multi-arch) sim, .NET 6+ sim, Java sim, Rust sim. Software legado x86-only não roda. Algumas imagens Docker públicas ainda não têm tag ARM64 — checar `docker buildx imagetools inspect IMAGE` ou tentar `--platform linux/arm64`.

Bom para: workloads em frameworks modernos onde economia importa.

### CCX (Dedicated vCPU AMD EPYC, global)

Cores dedicados sem vizinhos brigando por CPU. ~3x preço do CPX equivalente. Disponível global.

| Plano | vCPU dedicado | RAM | Disco | Traffic EU | Preço aprox. EU |
|---|---|---|---|---|---|
| CCX13 | 2 | 8 GB | 80 GB | 20 TB | confirmar |
| CCX23 | 4 | 16 GB | 160 GB | 20 TB | confirmar |
| CCX33 | 8 | 32 GB | 240 GB | 30 TB | confirmar |
| CCX43 | 16 | 64 GB | 360 GB | 40 TB | confirmar |
| CCX53 | 32 | 128 GB | 600 GB | 50 TB | confirmar |
| CCX63 | 48 | 192 GB | 960 GB | 60 TB | confirmar |

Bom para: bancos críticos com IO sustentado, CI/CD, jobs longos, multitenant SaaS, jogos online, anything onde noisy neighbor é inaceitável.

### Operating systems disponíveis

Ubuntu, Debian, Fedora, CentOS Stream, Rocky Linux, AlmaLinux. **Recomendado para Coolify**: Ubuntu 24.04 LTS ou 22.04 LTS (o instalador automático só suporta LTS; non-LTS exige instalação manual).

## Locations e Network Zones

4 zonas e 6 locations. **Atenção:** redes privadas, Floating IPs e Load Balancers têm que estar na mesma zona dos servidores. Cross-zone traffic é cobrado como tráfego normal de internet.

| Zona | Locations | Notas |
|---|---|---|
| `eu-central` | `fsn1` (Falkenstein/DE), `nbg1` (Nuremberg/DE), `hel1` (Helsinki/FI) | DCs próprios da Hetzner. Preços mais baixos. Tráfego mais generoso. vSwitch para Robot disponível. |
| `us-east` | `ash` (Ashburn, VA) | Colocation em DC terceiro. Sem Robot. Tráfego reduzido. |
| `us-west` | `hil` (Hillsboro, OR) | Colocation. Sem Robot. Tráfego reduzido. |
| `ap-southeast` | `sin` (Singapore) | Colocation. Sem Robot. Tráfego mais caro (€7.40/TB excedente). |

**Object Storage** disponível só em zonas EU. **Apps marketplace** disponível em todas. **Backups/Snapshots/Volumes/Firewalls/Networks/Floating IPs/Load Balancers/Placement Groups** disponíveis em todas.

Para latência Brasil → escolher `ash` (Ashburn) tipicamente dá menor RTT que FSN. Para latência Europa → FSN/NBG/HEL todos similares. Para latência Sudeste Asiático → SIN.

## Primary IPs

Toda interface pública de Cloud Server precisa de um Primary IP (ou ser IPv6-only).

- **IPv6** — gratuito, /64 por servidor
- **IPv4** — € 0.50/mês excl. VAT por endereço (cobrado mesmo se não anexado a servidor)

Pode-se criar Primary IP separadamente e reaproveitar entre servidores na mesma location (útil para "swap" de IP sem mudar DNS). Limite: 1 IPv4 e 1 IPv6 por servidor.

**Para economizar:** se app é só Coolify privado + apps acessadas via Cloudflare Tunnel, **IPv6-only** funciona e elimina o custo IPv4. Mas isso só vale a pena em casos muito específicos — Cloudflare Tunnel adiciona dependência.

## Volumes

Block storage networked, replicado em 3 servidores físicos da Hetzner. Anexável a um Cloud Server por vez.

- **Tamanho**: 10 GB a 10 TB, incrementos de 1 GB
- **Pode crescer (resize up) a qualquer momento, não pode encolher**
- **Preço**: €0.044/GB-mês (€0.0440 ou ~$0.0480, sempre confirmar)
- **Performance**: IOPS sustentado até 5000 (burst 7500); throughput sustentado 200 MB/s (burst 300 MB/s)
- **Bill horário com cap mensal**

Modos de attach:
- **Automatic** — Hetzner formata e monta em `/mnt/HC_Volume_${VOLUME_ID}`
- **Manually** — você cuida do filesystem (mkfs.ext4, fstab)

**Pegadinha crítica**: Volumes **NÃO** estão inclusos em Backups nem Snapshots do servidor. Para backup de dados em Volume, scriptar dump periódico para Object Storage ou Storage Box.

Limite: 16 Volumes por servidor, total 10 TB.

## Backups vs Snapshots

Ambos são cópias do disco do servidor (sem Volumes anexos).

**Backups**:
- Automáticos, diários
- 7 slots rolling (oldest deletado quando novo é criado)
- Custo: **+20% sobre o preço do servidor** (ativar/desativar a qualquer momento)
- Pensar como "seguro" — paga sempre, raramente usa

**Snapshots**:
- Manuais
- Persistem até deletar (cuidado com custo silencioso acumulando)
- Custo: **€0.011/GB-mês** sobre o tamanho usado do disco
- Funcionam como "imagem dourada" — criar 1 com Coolify configurado, replicar 5 servers idênticos
- Pode-se converter Backup em Snapshot (para preservar antes do rolling deletar)

**Quando usar qual:**
- Produção crítica → Backups ligados sempre
- Antes de mudança grande (upgrade, refactor de infra) → Snapshot manual
- Servidor experimental, dados não-críticos → talvez nenhum dos dois (deletar e recriar é trivial)

Limite default: 30 Snapshots por conta (todos os projetos somados); 7 Backup slots por servidor.

## Object Storage

S3-compatible. Disponível só em zonas EU (FSN/NBG/HEL).

- **Preço base**: € 4.99/mês ($5.99) por hora-ativa de pelo menos 1 bucket
- **Incluso**: 1 TB-mês de storage + 1 TB egress
- **Overage storage**: €0.0067/TB-hora (~€4.96/TB-mês contínuo)
- **Overage egress**: €1.00/TB
- **Mínimo billable por objeto**: 64 KB (objetos menores cobram como se fossem 64 KB)
- **Bills com 4 casas decimais** de precisão em TB

Compatível com AWS S3 SDK. Endpoints: `https://<location>.your-objectstorage.com`. Boto3, aws-cli, MinIO client, etc., funcionam com endpoint e credenciais customizados.

**Casos de uso**: backups (do Coolify, dumps de banco, logs), assets estáticos de aplicação, uploads de usuário, data lake pequeno/médio. Para hot serving de assets, pôr Cloudflare/Bunny CDN na frente (R2 não é gratuito no egress mas tem regra de "Cloudflare-to-origin de graça" se domínio passar pelo CF).

**Não tem versioning robusto nem lifecycle rules avançados** como AWS S3. Se precisa de archive automation (tier para Glacier-like), Hetzner não atende — usar Backblaze B2 ou AWS S3 Glacier.

## Networks privadas e vSwitch

**Networks**: rede privada IPv4 (10.x.x.x ou 192.168.x.x) entre Cloud Servers. Cada Network tem 1+ subnets, cada subnet pertence a uma zona. Todos os locations dentro de uma Network têm que ser da mesma zona. Servers podem estar em até 3 Networks.

Sem cobrança extra para tráfego interno na Network privada.

**vSwitch**: extensão que conecta Network privada Cloud com servidores Robot (dedicados). **Só disponível na zona `eu-central`**. Permite arquitetura híbrida: front-end em Cloud (escalável, hourly billing), banco em Dedicated (poderoso, mensal, sem noisy neighbor) na mesma rede privada.

## Load Balancers

LBs gerenciados que distribuem tráfego entre cloud servers. Algoritmos: Round Robin ou Least Connections. Cada LB tem IPv4 e IPv6 públicos; se em rede privada, ganha IPv4 privado também.

Planos:

| Plano | Targets | Conexões | Services | SSL termination | Preço aprox. |
|---|---|---|---|---|---|
| LB11 | 25 | 10k | 5 | sim | confirmar |
| LB21 | 75 | 20k | 10 | sim | confirmar |
| LB31 | 200 | 50k | 25 | sim | confirmar |

Suporta **target IPs** (público IPv4 ou privado IPv4 de servidores na mesma zona; IP-based targets apenas em `eu-central`). Suporta **target label selector** (auto-adicionar servidores que matchem labels). Health checks HTTP/TCP. SSL com Certificate Hetzner gerenciado ou próprio (Let's Encrypt automático ou upload custom).

**Quando usar:** > 1 servidor de app pra HA. Para single-server, o reverse proxy do Coolify (Traefik) já basta — não use LB Hetzner em cima por padrão.

## Firewalls Cloud

**Grátis**, ilimitado em uso. Stateful, opera no hipervisor antes do servidor (não consome recurso do guest, e funciona mesmo se Docker bypassar UFW local).

- Inbound bloqueado por default; outbound liberado por default. Adicionar regras allow.
- Pode usar **label selector** para auto-aplicar a servidores que matchem (ex.: todo servidor com label `tier=web` ganha firewall web automaticamente).
- Limites: 5 firewalls por servidor, 50 firewalls por projeto, 500 regras "efetivas" por firewall, 80k conexões concorrentes / 10k novas/s por servidor.

Conjunto mínimo de regras pra servidor com Coolify:
- TCP 22 (SSH) — restringir source ao seu IP ou range de office se possível
- TCP 80 (HTTP) — Let's Encrypt + redirecionar para 443
- TCP 443 (HTTPS) — tráfego real

**Após acessar o Coolify dashboard via domínio próprio (com Let's Encrypt), pode-se fechar 8000/6001/6002** — não há mais necessidade de acesso direto.

## Floating IPs

IPs públicos não-anexados-permanentemente, podem ser movidos entre servidores. Padrão antes de Primary IPs; hoje, com Primary IPs separáveis, Floating IPs são úteis principalmente para failover ativo-passivo entre 2 servers.

- Cobram mensalmente mesmo desanexados
- Floating IP tem que ser na mesma zona dos servidores
- Limite: 20 Floating IPs por servidor

## Placement Groups

Garante que servidores no mesmo grupo rodem em hosts físicos diferentes (anti-affinity), reduzindo blast radius de falha de host. **Grátis**.

Use para: par de servidores HA, master+replica de banco, nodes de cluster. **Não usa para single server.** Limite: 1 placement group por servidor.

## Apps

Marketplace de imagens pré-configuradas (one-click) — pode escolher na criação do servidor. Inclui: Docker CE, Plesk, WordPress, etc. Pra setup Coolify, **escolher imagem Ubuntu LTS limpa em vez de "Docker CE"** — o instalador Coolify cuida do Docker e quer Ubuntu fresh. Limite: 1 App por servidor.

## Limites

Defaults (podem ser aumentados via ticket no Console → "Limit increase"):

- 5 servidores Cloud por conta
- 8 dedicated-resource (CCX) servers por conta
- 1 Primary IPv4 + 1 Primary IPv6 por servidor
- 20 Floating IPs por servidor
- 1 App por servidor
- 1 Placement Group por servidor
- 3 Networks por servidor
- 5 Firewalls por servidor
- 16 Volumes por servidor (total 10 TB)
- 20 projetos por conta
- 50 Firewalls por projeto
- 20 Load Balancers por projeto
- 30 Snapshots por conta

## Projetos, membros e roles

Projetos isolam recursos (servidores, IPs, redes, firewalls). Cada conta começa com 1 projeto, default. Limite default: 20 projetos.

**Roles** (em Security → Members):
- **Owner** — paga tudo no projeto, pode mover recursos entre projetos. Um por projeto.
- **Admin** — tudo do Owner exceto cobrança/transferência. Pode gerenciar membros, API tokens, S3 credentials.
- **Member** — CRUD em todos os recursos.
- **Restricted** — leitura + ações limitadas (não cria/deleta server, snapshot, volume, network, load balancer, bucket; não muda plano).

Convites geram **light accounts** (só email+senha, acesso só ao projeto convidado) ou **full accounts** (dados de cobrança próprios, podem criar projetos próprios).

**Mover servidor para outra conta**: receptor cria projeto, convida sender; sender move servidor pro projeto compartilhado; receptor move pro próprio projeto privado. A partir do momento em que recurso é movido, **a cobrança vai pro Owner do projeto destino**.

## CLI e API

- **hcloud CLI** (`hcloud` binary, instalável via Homebrew/apt/binário GitHub) — wrapper oficial sobre a API. Exemplos:
  - `hcloud server create --name web1 --type cpx22 --image ubuntu-24.04 --location fsn1 --ssh-key meu-laptop`
  - `hcloud server rescale web1 --type cpx32`
  - `hcloud volume create --name pgdata --size 50 --location fsn1 --automount --server web1`
- **API REST** (`api.hetzner.cloud/v1`) — documentada em https://docs.hetzner.cloud — usada por Terraform provider, Pulumi, Coolify (integração nativa para criar servidores Hetzner direto da UI do Coolify) e qualquer automação custom.
- **Tokens API** se geram em Security → API Tokens no Console — scope por projeto, read/write separável.
- **Terraform provider** `hetznercloud/hcloud` mantido oficialmente — usar pra qualquer infra séria com >5 recursos.
