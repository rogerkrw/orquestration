---
name: hetzner-coolify-ops
description: Operação completa de infraestrutura Hetzner (Cloud, Robot/dedicados, Storage, Networking) e da plataforma Coolify para deploy de aplicações sobre ela. Acione sempre que a tarefa envolver Hetzner ou Coolify, incluindo escolha e dimensionamento de servidor (CX, CPX, CAX, CCX, AX, EX, PX, Auction), seleção de location, estimativa e otimização de custos em EUR/USD, instalação do Coolify self-hosted, deploy de apps (Next.js, Laravel, Django, Docker Compose, Dockerfile, Nixpacks, static sites), bancos (PostgreSQL, MySQL, MongoDB, Redis), reverse proxy (Traefik/Caddy), SSL Let's Encrypt, domínios, firewall, backups, snapshots, volumes, object storage S3, load balancers, vSwitch, troubleshooting (502/503/504, build OOM, SSL falha, SMTP bloqueado) e migrações de Vercel/Heroku/Render para self-host. Acione também quando o usuário disser 'Hetzner', 'Coolify', 'self-host', 'PaaS', 'VPS', 'alternativa ao Heroku/Vercel', 'deploy barato', 'Server Auction', 'sair da Vercel' ou 'rodar n8n/Plausible/Ghost próprio'.
---

# Hetzner + Coolify Operations

Esta skill cobre operação prática do ecossistema Hetzner (Cloud, Robot/dedicados, Storage, Networking) e da plataforma Coolify (PaaS open-source) rodando sobre ele. Combina o "como" da Hetzner (provisionar, dimensionar, precificar) com o "como" do Coolify (instalar, conectar, deployar, gerenciar).

## Como usar esta skill

A skill tem 3 camadas: este SKILL.md é o ponto de partida com decisão, atalhos e princípios. As references/ contêm detalhes profundos — leia somente as relevantes para a tarefa em mãos.

| Pergunta do usuário | O que abrir |
|---|---|
| Quanto custa um setup X? Qual servidor caber em € Y/mês? Vale a pena Auction? | `references/pricing.md` |
| Que tipo de servidor escolher? Diferença entre CX/CPX/CAX/CCX/AX/EX? | `references/cloud-products.md` (Cloud) ou `references/dedicated-and-robot.md` (dedicado) |
| Como instalar/configurar/conectar/usar Coolify? Como fazer deploy? Como configurar domínio? | `references/coolify-deploy.md` |
| Arquitetura — single VPS vs multi-server vs banco separado vs híbrido? | `references/architecture-recipes.md` |
| Backups, snapshots, volumes, object storage, traffic overage, IPs, firewall, load balancer? | `references/cloud-products.md` + `references/pricing.md` |

Antes de responder qualquer coisa específica sobre **preço atual**, **disponibilidade de localização** ou **especificações de plano novo** (como "CX Gen3"), faça uma busca web rápida — a Hetzner reestrutura linhas e preços com frequência (a última grande reestruturação foi a deprecação de CX/CPX antigos em favor de CX Gen3 / CPX Gen2 em out/2025, e a redução de tráfego incluído nos EUA em dez/2024). Os valores nas references aqui são bases de raciocínio, não fontes-de-verdade atemporais.

## O essencial em uma página

### Hetzner — produtos que importam

**Cloud** (`console.hetzner.cloud`): VPS por hora, criados em segundos. 4 famílias:
- **CX** — Cost-Optimized x86 (Intel/AMD), shared vCPU, EU-only. Mais barato. Começa em ~€3.49/mês.
- **CPX** — Regular Performance AMD EPYC, shared vCPU, disponível global. Performance single-core melhor que CX. Padrão para produção pequena/média.
- **CAX** — ARM64 Ampere Altra, shared vCPU, EU-only. ~10-15% mais barato que CPX equivalente, ~30% mais eficiente energeticamente. **Atenção:** software precisa suportar ARM64.
- **CCX** — Dedicated vCPU AMD EPYC, sem vizinhos brigando por CPU. Global. ~3x preço do CPX equivalente. Use quando consistência de performance importa (banco, CI, jobs pesados).

**Robot** (`robot.hetzner.com`): servidores dedicados físicos, contrato mensal, setup fee comum. Linhas:
- **AX** (AMD Ryzen/EPYC), **EX** (Intel Core i5/i7/i9), **PX/SX** (enterprise Xeon/EPYC, mais RAM/disco), **Auction** (refurbished em leilão holandês — preços decrescem até alguém comprar; **sem setup fee** e geralmente 20–40% mais barato).
- Disponível apenas em FSN/NBG/HEL (Alemanha + Finlândia). **Não há dedicados em US/Singapore.**
- 1 Gbit/s com tráfego ilimitado (10 Gbit/s = 20 TB incluso, €1/TB excedente).

**Storage**: Object Storage S3-compatível (€4.99/mês base com 1 TB storage + 1 TB egress, pay-as-you-go acima), Storage Box (file storage tradicional via SMB/SFTP/WebDAV), Volumes (block storage anexável a um Cloud server).

**Networking**: Networks privadas, vSwitch (conecta Cloud + Robot), Load Balancers (LB11/21/31), Floating IPs, Primary IPs (IPv4 €0.50/mês, IPv6 grátis), Firewalls cloud (gratuitos).

### Coolify — o que é e o que faz

PaaS auto-hospedado open-source. Alternativa a Heroku/Vercel/Netlify/Render. Instala em qualquer servidor Linux com SSH e Docker. Recursos:

- Deploy de apps via Git (GitHub App, Deploy Key, Public Repo, GitLab, Bitbucket, Gitea), Dockerfile, Docker image, ou Docker Compose
- Build packs automáticos via **Nixpacks** (detecta Next.js, Laravel, Django, Vue, Nuxt, SvelteKit, Phoenix, Rails, etc.) + **Static** + **Dockerfile** + **Docker Compose**
- Bancos one-click: PostgreSQL, MySQL, MariaDB, MongoDB, Redis, DragonFly, KeyDB, Clickhouse
- Reverse proxy embutido (Traefik por padrão, Caddy opcional) com SSL Let's Encrypt automático
- Environment variables, persistent volumes, health checks, rolling updates, preview deploys de PRs
- Servidores múltiplos (build server separado, workers), notificações (Discord/Slack/Telegram/email), backups S3
- **API REST completa** com endpoints específicos Hetzner (criar servidor via Coolify API → cria via Hetzner Cloud API)
- Duas formas de uso: **self-hosted** (curl install em VPS próprio, grátis) ou **Coolify Cloud** (managed, pago)

**Portas que o Coolify self-hosted precisa abertas**: 22 (SSH), 80 (HTTP/Let's Encrypt), 443 (HTTPS), 8000 (dashboard), 6001 (realtime), 6002 (terminal). Após acessar pelo domínio próprio, pode-se fechar 8000/6001/6002. **Coolify Cloud** precisa só 22/80/443 abertos no servidor gerenciado.

## Decisão: qual produto Hetzner para qual cenário

Pense em três eixos: **carga (estável vs picos)**, **localização (latência do usuário)** e **estágio (dev/staging/produção)**. As recomendações abaixo são ponto-de-partida — sempre confirme preço/specs atuais antes de comprometer com o cliente.

| Cenário | Recomendação inicial | Por quê |
|---|---|---|
| Dev/staging, side project, MVP solo | **CX22** ou **CAX11** (~€3.49–€4.49/mês, 2 vCPU/4 GB/40 GB) | Cabe Coolify (mínimo 2 vCPU/2 GB) + 1-2 apps leves. CAX se app é ARM-compatível. |
| App produção pequena, ~10k usuários/mês | **CPX22** ou **CAX21** (~€7-8/mês, 2-3 vCPU/4 GB/80 GB) | Headroom para Coolify + 2-3 apps + um banco pequeno. |
| App produção média, banco + workers, ~100k usuários/mês | **CPX31/41** ou **CCX13** dedicada (~€16-30/mês) | Quando começa a faltar CPU em horários de pico. CCX se latência tem que ser consistente. |
| App produção grande, vários serviços, ML/AI | **AX42 a AX102** dedicado (~€40-120/mês) ou **EX44/EX63** | Hardware físico, sem vizinhos, RAM grande (64-128 GB), disco grande. |
| Banco crítico, alto IO sustentado | **CCX** ou **AX/EX dedicado** | Dedicado evita "barulho" de vizinhos no IO. |
| Workload AI/ML CPU-pesado | **AX162** (EPYC 32 cores) ou Auction com Xeon + muita RAM | Hetzner não oferece GPUs cloud em larga escala — para GPU, considerar Auction GPU server pontual. |
| Storage de backups, dumps, assets estáticos pesados | **Object Storage** (€4.99/mês base, 1 TB incluso) + CDN externa | S3-compatible. Para hot serving, pôr Cloudflare ou Bunny CDN na frente. |

## Decisão: localização

Para usuário no **Brasil/LATAM**, **Ashburn (ash)** tipicamente dá menor latência (RTT ~120-150 ms vs ~200 ms para FSN). Mas o **CX só existe em EU**, então se quer o produto mais barato e o usuário está nos EUA, escolha **Ashburn** ou **Hillsboro** com CPX/CCX. Para Brasil, considere também colocar CDN (Cloudflare) na frente — assim a origem pode ficar em FSN/NBG (mais barato, mais features) e a borda fica no Brasil pela CDN.

**Atenção a custos por localização:**
- EU (FSN/NBG/HEL): mais barato, tráfego incluso generoso (20 TB nos planos EU para CCX/CPX), overage €1/TB
- US (ASH/HIL): preços ~20% maiores, tráfego incluso bem menor (1-6 TB dependendo do plano), overage €1/TB
- Singapore (SIN): preços maiores ainda, **tráfego excedente € 7.40/TB** (~7x mais caro que EU/US). Modelar bandwidth explicitamente antes de escolher.

## Pegadinhas que custam horas (ou dinheiro)

1. **Backups custam +20% sobre o preço do servidor** — não são grátis. Pra economizar e fazer 7 dias rolling, ative; pra projeto pessoal de baixo risco, snapshot manual ocasional sai mais barato (€0.011/GB-mês).
2. **Snapshots persistem até deletar manualmente** — fácil esquecer e acumular custo silencioso. Auditar mensalmente.
3. **TCP 25/465 (SMTP) bloqueado outbound por padrão** em todo novo Cloud server (antispam). Desbloqueio só após ~30 dias como cliente pagante e abertura de ticket. **Workaround:** usar SMTP relay externo (Postmark, Resend, Mailgun, SendGrid) — quase sempre é o que se quer mesmo.
4. **Hetzner não cobra por entrada (ingress), mas cobra por saída (egress)** acima do incluso. Vídeo, imagens, downloads pesados → calcular bandwidth.
5. **IPv4 é € 0.50/mês extra** desde meados de 2024. IPv6 é grátis. Se app só precisa de IPv6, economize.
6. **CX/CPX da geração antiga foram deprecados em out/2025** — só `CX23`/`CX33`/etc. (Gen3) e `CPX22`/`CPX32`/etc. (Gen2) criáveis pelo Console. Os antigos continuam funcionando mas não dá pra criar novo. **Validar pela API/site antes de assumir.**
7. **Servidores em US/Singapore tiveram corte drástico de tráfego incluído em dez/2024** (de 20 TB para 1-8 TB). Existing servers migrados em fev/2025. Não copiar mentalmente o "20 TB" pra essas regiões.
8. **UFW não bloqueia portas Docker** — o Docker insere regras em iptables que passam por cima. Para fechar portas com Coolify, use **firewall do provedor** (Hetzner Cloud Firewall, grátis) ou ufw-docker.
9. **Volumes não estão em Snapshots nem Backups** do servidor. Para backup de Volume, montar e fazer dump pra Object Storage / Storage Box separadamente.
10. **Cobrança continua para servidor desligado** — só para de cobrar quando **deletar**. Deletar e esquecer não basta; conferir o Console.
11. **Coolify auto-update está ligado por padrão** (`AUTOUPDATE=true`). Para produção, considerar desligar (`env AUTOUPDATE=false` no install) e atualizar manualmente em janelas controladas.

## Workflows mais comuns

### A) Provisionar Hetzner Cloud + instalar Coolify do zero

1. Criar projeto no Hetzner Console (https://console.hetzner.cloud/).
2. Em "Security → SSH Keys", subir a chave pública local (`~/.ssh/id_ed25519.pub` ou gerar novo par com `ssh-keygen -t ed25519`).
3. "Add Server" → escolher Location, escolher Image **Ubuntu 24.04 LTS** (ou 22.04), tipo **CPX22** (ou CAX21 se ARM ok) como ponto de partida razoável para Coolify + 1-2 apps, **anexar a chave SSH**, opcional Backups (+20%), criar Firewall com regras (SSH 22, HTTP 80, HTTPS 443; pode adicionar 8000 temporariamente).
4. SSH no servidor: `ssh root@SEU_IP`.
5. Rodar instalador Coolify: `curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash` (idealmente em servidor LIMPO; o script instala Docker, configura `/data/coolify/`, sobe containers via Docker Compose).
6. Após 2-5 min, abrir `http://SEU_IP:8000` no navegador e **criar imediatamente a conta admin** (se alguém abrir antes, controla seu servidor — daí o uso opcional das envs `ROOT_USERNAME`/`ROOT_USER_EMAIL`/`ROOT_USER_PASSWORD` no install para já provisionar).
7. Em "Servers", o `localhost` (o próprio servidor onde o Coolify roda) já aparece — basta validar.
8. **Configurar domínio do dashboard** (Settings → Instance → Coolify Instance URL) apontando para algo como `coolify.seudominio.com` com DNS A record para o IP. Coolify negocia Let's Encrypt automaticamente. Depois pode fechar 8000/6001/6002 no firewall.

Detalhes profundos: `references/coolify-deploy.md`.

### B) Deploy de um app a partir de Git (caminho mais comum)

1. **Conectar GitHub**: Coolify → Sources → New → GitHub App (recomendado, dá webhooks automáticos para auto-deploy) ou Deploy Key (para repos privados sem instalar app) ou Public Repo (sem auth).
2. **Project → Resource → Application → seu repo, branch**. Coolify lê o repo e propõe um build pack.
3. **Escolher build pack**:
   - **Nixpacks** (padrão) — auto-detecta Next.js, Vue, Nuxt, SvelteKit, Vite, Django, Laravel, Phoenix, Rails, Symfony, Jekyll, Node genérico. Funciona out-of-the-box pra 90% dos casos.
   - **Static** — para sites HTML/JS estáticos puros (build → pasta de saída).
   - **Dockerfile** — quando o repo tem `Dockerfile` próprio. Mais controle, mais responsabilidade.
   - **Docker Compose** — quando o repo tem `docker-compose.yml` ou se quer subir múltiplos containers juntos.
4. **Environment variables**: Application → Environment Variables. Marcar **"Is Build Variable?"** apenas para vars que o build precisa ler (Next.js `NEXT_PUBLIC_*`, etc.). Demais ficam só em runtime.
5. **Domínio**: Application → Domains → `https://app.seudominio.com`. DNS A record para o IP do servidor. SSL via Let's Encrypt automático (não usar wildcard inicialmente — caminho mais rápido).
6. **Deploy** → Coolify clona, builda, sobe container, atualiza Traefik. Logs ao vivo no painel.
7. **Auto-deploy**: se conectou via GitHub App, push em main faz redeploy automático. Para PRs preview, ativar "Preview Deployments".

### C) Estimar custo de um projeto (mensal, EUR, excl. IVA)

Soma de 4 linhas:

```
Compute    = (preço plano servidor) + IPv4 (€0.50 se usar) + Backups (+20% opcional)
Storage    = Volumes anexos (€0.044/GB-mês, mín 10 GB) + Snapshots (€0.011/GB-mês)
Network    = max(0, traffic_real_TB − traffic_incluso_TB) × €1/TB (EU/US) ou €7.40/TB (SIN)
Add-ons    = Load Balancer (LB11 €5.39, LB21 €16.40, LB31 €32.90) + Object Storage (€4.99 base + uso)
```

Adicionar 19-20% de VAT para clientes EU PJ sem VAT ID válido, ou 0% se Reverse Charge aplicável. Para Brasil, geralmente Hetzner não retém IVA mas o cliente pode incidir tributação local na aquisição de serviço do exterior (IRRF, PIS/COFINS-importação) — não é papel desta skill aconselhar tributariamente; deixar claro que é estimativa de fornecedor, não custo final ao caixa do cliente.

**Exemplo** — stack típica "produção pequena com Coolify":
- 1× CPX22 em FSN (€7.05) + IPv4 (€0.50) + Backups +20% (€1.51) = **€9.06/mês**
- 1× Object Storage (€4.99/mês base, dentro do 1 TB incluso) = **€4.99/mês**
- Total = **~€14/mês** (sem VAT)

Detalhes: `references/pricing.md`.

### D) Migrar de Vercel/Heroku/Render para Hetzner+Coolify

Argumento de venda interno: **80-90% mais barato em workloads parados/baixos** (Vercel Pro $20/usuário + bandwidth; Heroku $25 dyno + Postgres $50; Render $7-25 services). Trade-off: mais responsabilidade operacional (você cuida de OS updates, monitoramento, backups, recuperação).

Workflow geral:
1. Inventário do que está no PaaS atual: apps, bancos, env vars, domínios, cron jobs, queues, workers, storage de arquivos.
2. Mapear cada um para Coolify equivalente:
   - App web → Application (Nixpacks ou Dockerfile)
   - Postgres → Database PostgreSQL no Coolify (com backups S3 ativos)
   - Redis → Database Redis no Coolify
   - Cron → Scheduled Task em Application
   - Worker → Application separada (sem domínio) ou serviço no Docker Compose
   - Arquivos do usuário → Object Storage Hetzner (S3 SDK, mudar endpoint)
3. Decidir tamanho do servidor pelo perfil de carga (ver tabela acima).
4. Migrar dados (dump pg → Object Storage → restore no destino), com janela curta de read-only ou dual-write.
5. Cortar DNS para o IP do Hetzner (manter TTL baixo na véspera).
6. Monitorar por 7-14 dias antes de desligar o PaaS antigo.

Pegadinhas comuns: env vars que diferem em build vs runtime, file storage que assumia filesystem efêmero, jobs que dependiam de scheduler do PaaS, conexões SMTP (lembrar do bloqueio Hetzner — usar SMTP externo).

## Princípios operacionais

- **Sempre comece menor do que parece preciso** — o billing horário do Hetzner Cloud premia experimentar. Subir, testar carga real, redimensionar (rescale para cima é instant; para baixo precisa caber no novo disco). Não tente acertar de primeira; itere.
- **Coolify gosta de servidor limpo** — instalação em VPS que já tinha outras coisas dá conflito (Docker pré-existente, portas em uso). Quando puder, comece em fresh server.
- **Não rode build pesado e Coolify no mesmo VPS pequeno** — Next.js builds, especialmente, comem RAM. Em planos 2-4 GB, build de Next pode OOM. Soluções: (a) subir Coolify pra plano maior, (b) configurar Build Server dedicado, (c) buildar localmente / em CI e fazer push de Docker image pronta.
- **Backup do Coolify também** — `/data/coolify/` contém estado completo. Coolify tem feature "Backup & Restore Coolify" para S3. Configurar pra Object Storage Hetzner ou Backblaze/Cloudflare R2.
- **Use Hetzner Cloud Firewall, não só UFW** — Docker bypassa UFW. O firewall gerenciado da Hetzner roda antes do Docker e funciona corretamente.
- **DDOS protection é grátis e ligada por padrão** — não é assunto que precisa contratar. Para ataques aplicacionais (camada 7), pôr Cloudflare na frente.
- **Para qualquer pergunta sobre preço atual ou plano novo, faça web search antes de responder** — a documentação muda. Não assuma valores fixos sem verificar.

## Quando esta skill NÃO se aplica

- Tributação fiscal específica BR → não é o escopo, indicar contador.
- Recomendação entre Hetzner e concorrentes em mercado regulado (HIPAA, FedRAMP) — Hetzner não é certificada para a maioria desses; redirecionar para AWS GovCloud/Azure equivalentes.
- Setup de GPU em larga escala — Hetzner tem oferta limitada; para GPU sério, Lambda Labs / RunPod / Vast.ai são melhores.
- Hospedagem de coisas vedadas pelo Terms of Service Hetzner (mineração, etc.) — não orientar.

## Reference files

- `references/cloud-products.md` — Catálogo detalhado de produtos Hetzner Cloud: servidores (CX/CPX/CAX/CCX) com specs, locations e network zones, Primary IPs, Volumes, Backups/Snapshots, Object Storage, Load Balancers, Networks/vSwitch, Firewalls, Floating IPs, limites por conta.
- `references/dedicated-and-robot.md` — Servidores dedicados (AX/EX/PX/SX), Server Auction (leilão holandês), Storage Box, Colocation, traffic em servidores físicos, setup fees, integração Cloud↔Robot via vSwitch.
- `references/pricing.md` — Tabela de preços e modelo de billing detalhado, EUR + USD, com fórmulas para estimar custo total, comparações por região, traffic overage por zona, custo de backups/snapshots/volumes/object storage.
- `references/coolify-deploy.md` — Manual operacional Coolify: instalação self-hosted vs Cloud, conectar servidores, configurar GitHub App, build packs (Nixpacks/Static/Dockerfile/Compose), domínios e SSL, environment variables, bancos one-click, persistent storage, backups, troubleshooting (502/503/504, Let's Encrypt falha, build OOM).
- `references/architecture-recipes.md` — Receitas prontas: single-VPS Coolify (até €15/mês), multi-server com Build Server, banco separado em CCX/dedicado, hybrid Cloud+Dedicated via vSwitch, alta disponibilidade com Load Balancer + 2-3 nodes, e estimativa de custo de cada uma.
