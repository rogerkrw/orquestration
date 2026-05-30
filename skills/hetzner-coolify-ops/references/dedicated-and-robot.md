# Hetzner Robot — servidores dedicados, Auction, Storage Box

Esta reference cobre o lado "Robot" da Hetzner: servidores físicos dedicados (não-virtualizados), o sistema de leilão (Server Auction), Storage Box (file storage) e colocation. Tudo gerenciado pelo painel separado em `robot.hetzner.com` (não pelo Cloud Console).

## Quando Robot e não Cloud

- **Performance física sustentada** importa mais que elasticidade
- Você precisa de **64+ GB de RAM** ou **TB+ de disco local** baratos
- Você precisa de **CPU consistente** (sem noisy neighbor) mas o CCX está caro ou subdimensionado
- App roda em **um único nó grande** (banco grande, ERP, ML inference, render farm)
- Workload com **alto IO local sustentado** (banco escrita-pesada, ETL, video transcoding)

**Robot e Cloud podem coexistir** via vSwitch (rede privada, zona `eu-central` apenas). Comum: front-ends em Cloud (escalam), banco em Dedicated (poderoso e estável).

**Robot não está disponível** em Ashburn, Hillsboro nem Singapore. Só FSN, NBG, HEL (Alemanha + Finlândia). Para US/SIN físico, Hetzner não é fornecedor.

## Linhas de servidores dedicados

### AX — AMD Ryzen/EPYC

A linha "flagship" da Hetzner em performance/preço. DDR5 ECC em modelos novos, NVMe Gen4, 1 Gbit/s incluso.

| Plano exemplo | CPU | RAM | Disco | Preço aprox. |
|---|---|---|---|---|
| AX42 | Ryzen 7 PRO 8700GE 8-core Zen4 | 64 GB DDR5 ECC | 2× 512 GB NVMe | €39-46/mês |
| AX52 | Ryzen 7 7700 | 64 GB DDR5 ECC | 2× 1 TB NVMe | ~€59/mês |
| AX102 | Ryzen 9 7950X3D 16-core | 128 GB DDR5 | 2× 1.92 TB NVMe | ~€119/mês |
| AX162-R | EPYC 9454P 48-core | 256 GB DDR5 ECC reg | 2× 3.84 TB NVMe | ~€279/mês |

Bom para: bancos grandes, app + banco co-localizados, jobs CPU-heavy multi-thread.

### EX — Intel Core (consumer-grade poderoso)

Linha mais barata em Intel. Cores Core i5/i7/i9, performance single-core ótima. Sem ECC nas gerações Core; algumas geracões mais novas com Ultra com ECC opcional.

| Plano exemplo | CPU | RAM | Disco | Preço aprox. |
|---|---|---|---|---|
| EX44 | Intel i5-13500 6P+8E | 64 GB DDR4 | 2× 512 GB NVMe | €36-44/mês |
| EX63 | Intel Core Ultra 7 265 | 64 GB DDR5 | 2× 1 TB NVMe | ~€69/mês |
| EX102 | Intel i9-13900 24-core | 128 GB DDR5 | 2× 3.84 TB NVMe | ~€199/mês |

Bom para: workloads single-threaded, web servers, runtimes Node/Python/Ruby onde clock-speed importa. EX44 é o **melhor preço-performance** da Hetzner por consenso.

### PX — Enterprise Xeon

Servidores enterprise-grade. ECC RAM sempre, mais slots de disco, melhor para racking denso. Mais caro.

### SX — Storage-heavy

Foco em armazenamento (várias HDDs grandes). Para data warehouse, backup target, NextCloud massivo.

## Server Auction

Hetzner "eBay para servidores dedicados". Modelo de **leilão holandês**: o preço começa alto e **decresce ao longo do dia**. Quando alguém compra, o servidor sai do leilão. Sem setup fee. Servidores são "refurbished" — saíram de outro contrato.

URL: https://www.hetzner.com/sb/

Vantagens:
- **Desconto 20-40%** comparado ao mesmo hardware como produto novo
- Sem setup fee (mesmo hardware como produto novo cobra ~1 mês de setup)
- Setup instantâneo (rescue system pronto pra OS install)
- Mesmo hardware, mesmo DC, mesmo SLA

Desvantagens:
- Disponibilidade flutuante — você compra o que estiver em oferta agora; pode não ter exatamente a config que quer
- Hardware é "previous-gen" tipicamente (1-3 anos atrás)
- Sem garantia de re-estocagem do mesmo modelo

**Pegadinhas**:
- O servidor é entregue em **Rescue System** (não tem OS instalado). Você instala via `installimage` (utilitário deles) escolhendo Debian/Ubuntu/CentOS/etc.
- Suporte por escrito tem prioridade menor para aluguéis abaixo de € 37.30/mês.
- Não dá pra rescale (mudar plano) como em Cloud. Quer mais — alugar outro.

**Estratégia**: monitorar Auction durante a semana. Comprar quando a config certa cair no preço-alvo. Sites/scripts terceiros (`servers.live`, "Hetzner Auction Bot") rastreiam ofertas e alertam quando hardware desejado aparece abaixo de X €.

## Setup de servidor Robot pós-compra

1. Email com credenciais do Rescue System (login SSH como root)
2. SSH no servidor (já está no rescue system Linux)
3. Rodar `installimage` — menu pra escolher imagem (Ubuntu 24.04 LTS, Debian 12, etc.)
4. Configurar partições (single ext4 simples ou RAID via mdadm)
5. Reboot — servidor sobe na imagem instalada
6. Configurar firewall (Robot tem firewall gerenciado mas restrito; melhor usar `ufw` ou `iptables` direto no host)
7. Configurar reverse DNS (PTR) no painel Robot se necessário (e-mail outbound, SSL)

Para usar com Coolify igual a Cloud: o instalador Coolify roda igual aqui. **Atenção**: dedicados de 64+ GB RAM são oversized pra Coolify sozinho — geralmente faz sentido virtualizar (instalar Proxmox/KVM e fatiar em VMs) **ou** rodar bastante coisa no mesmo Coolify.

## Traffic em servidores dedicados

- **1 Gbit/s uplink padrão**: tráfego **ilimitado** (sem cobrança por egress)
- **10 Gbit/s uplink (upgrade)**: 20 TB inclusos, €1/TB excedente
- **Cobrança em blocos de 100 MB** quando overage

Por que tráfego é grátis em 1 Gbit/s dedicado mas cobrado em Cloud? Em Cloud o uplink físico é compartilhado pela rede de virtualização; em Robot, sua porta é dedicada. **Em workloads de bandwidth pesada (vídeo, downloads, backup target), Robot 1 Gbit/s costuma sair drasticamente mais barato** que Cloud com overage.

## Adicionais para Robot

- **IPv4 adicional / subnets**: blocos /29 ou /28 cobrados mensalmente. 1 IPv4 já vem com servidor; mais que isso cobra.
- **IPv6 /64**: incluso por servidor.
- **Failover IP** (move-se entre servidores em segundos via API): ~€1/mês cada.
- **vSwitch**: grátis. Liga o Robot a uma Network privada Cloud na zona `eu-central`.
- **Backup Space** (separado de Storage Box): file storage simples, montável via SFTP. Cobrado por GB.
- **Hardware adicional** (mais RAM, mais disco): cotação caso-a-caso, pode adicionar permanentemente ao plano.

## Storage Box

File storage tradicional. **Não tem API S3** — acesso via SMB/CIFS, SFTP, FTPS, WebDAV, Borg, rsync, scp.

| Plano | Storage | Preço aprox. |
|---|---|---|
| BX11 | 1 TB | ~€3.50/mês |
| BX21 | 5 TB | ~€10/mês |
| BX31 | 10 TB | ~€19/mês |
| BX41 | 20 TB | ~€38/mês |

Inclui **10 sub-accounts** (úteis pra dar acesso isolado a clientes diferentes ou backup de servers diferentes sem compartilhar credencial). Replicação inter-DC opcional (+50% no preço).

Casos de uso:
- **Backup target** para servidores (Borg, restic, rsync)
- **NextCloud datastore** (montagem WebDAV ou SMB)
- **Backup de banco** via dump → scp/sftp
- **Storage de arquivos legados** acessíveis por software que só fala SMB/FTP

**Storage Box vs Object Storage Hetzner**: Object Storage para app moderna com SDK S3; Storage Box para infra legada / backups simples / casos de file-level access. Se a dúvida é "preciso dos dois?", quase sempre não — escolher um e padronizar.

## Colocation

Hetzner aluga rack space nos próprios DCs. Cliente leva o hardware (próprio), Hetzner provê espaço, energia, rede, smarthands. Disponível em FSN/NBG/HEL.

Faixa de preço típica: ~€40-100/U/mês dependendo de power/redundancy. Notas:
- Não-tópico desta skill detalhar — colocation é decisão de operação enterprise, geralmente envolve TCO de 3-5 anos com hardware próprio. Se cliente pergunta, redirecionar pra account manager Hetzner.

## Integração Cloud ↔ Robot (vSwitch)

O caso típico de uso é:
1. Comprar 1 Dedicated AX/EX em FSN para banco/serviço pesado
2. Provisionar 1-3 Cloud Servers CPX em FSN para front-end / app stateless
3. Criar Network privada Cloud em `eu-central`
4. Criar vSwitch no Robot e atribuir o Dedicated
5. Conectar Network ↔ vSwitch (no Console)
6. Todos comunicam-se via IPs privados (10.x.x.x), sem custo de egress entre eles

**Limitações**:
- vSwitch só em zona `eu-central`. Não há equivalente para US/SIN.
- Latência adicional pequena (~0.5 ms) entre Cloud e Robot vs servidores no mesmo rack
- Configuração inicial precisa de VLAN tagging no host Robot (`vlan` interface no `/etc/network/interfaces`)

## Quando NÃO usar Robot

- Workload variável (precisa subir/descer servidores conforme demanda): Cloud ganha pela cobrança horária
- Necessidade de location US/SIN: Robot não atende, ir de Cloud lá
- Workload < 4 GB RAM (sub-aproveitamento óbvio do hardware)
- App muito jovem onde requisitos ainda estão sendo descobertos: começar Cloud (descartável), migrar pra Robot quando saturar
