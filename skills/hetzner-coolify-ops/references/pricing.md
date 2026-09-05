# Hetzner — preços e modelo de billing

Esta reference dá fórmulas e tabelas para estimar custo total mensal de uma stack Hetzner. **Confirme preços via web search ou API antes de cotar para cliente** — a Hetzner reestrutura preços e tráfego com frequência. O reajuste de 15/06/2026 tornou os valores numéricos abaixo históricos; use-os apenas para entender dimensões e fórmulas, nunca como cotação.

## Princípios gerais

- **Moeda**: EUR padrão; USD para conta criada em USD (escolha do owner do projeto na criação da conta, não muda depois). Conversão aproximada: $1.20 ≈ €1.00.
- **VAT**: preços anunciados em **excl. VAT**. Para PJ EU sem VAT ID válido ou consumidor final EU: +19-20%. Para Reverse Charge (PJ EU com VAT ID) ou cliente fora da EU (incluindo Brasil): 0%. Hetzner não calcula tributos locais do país do cliente (IRRF/PIS-COFINS no Brasil é responsabilidade do tomador).
- **Bill horária com cap mensal** para Cloud (servidores, volumes, load balancers, IPs). Hourly = 1/672 do preço mensal por hora ativa (aproximado, Hetzner arredonda para cima). Cap mensal = preço cheio do mês cheio. Você nunca paga mais que o mensal, mesmo se ativar/desativar várias vezes.
- **Dedicated (Robot)** é cobrança mensal cheia, prorated apenas na entrada/saída do mês. Setup fee único em alguns planos.
- **Cobrança continua para servidor parado/desligado.** Só para quando **deletar**. Snapshots não inclusos no preço de delete.

## Fórmula geral de estimativa mensal (EUR, excl. VAT)

```
Total mensal = Compute + Storage + Network + Add-ons

Compute    = preço plano servidor
           + (€0.50 se usar Primary IPv4)
           + (preço plano × 20% se Backups ativos)
           
Storage    = (GB de Volume × €0.044)
           + (GB de Snapshot × €0.011)
           + (tarifa base vigente + uso pay-as-you-go se Object Storage)
           
Network    = max(0, TB_egress_real - TB_incluído_no_plano) × tarifa_por_TB_da_zona
           # tarifa = €1.00/TB em eu-central e us-east/west, €7.40/TB em ap-southeast
           
Add-ons    = Load Balancer (plano escolhido, tarifa vigente)
           + Floating IPs (tarifa vigente)
```

## Preços de Cloud Servers (EUR/mês, EU-central, excl. VAT)

Valores de referência para projetar — **sempre confirmar via web** antes de cotar oficial.

### CX (Cost-Optimized, EU-only)

| Plano | vCPU | RAM | Disco | Traffic | Preço |
|---|---|---|---|---|---|
| CX23 | 2 | 4 GB | 40 GB | 20 TB | confirmar |
| CX33 | 4 | 8 GB | 80 GB | 20 TB | confirmar |
| CX43 | 8 | 16 GB | 160 GB | 20 TB | €11.49 |
| CX53 | 16 | 32 GB | 320 GB | 20 TB | €22.49 |

### CPX (Regular Performance AMD, global)

| Plano | vCPU | RAM | Disco | Traffic EU | Traffic US | Traffic SIN | Preço EU |
|---|---|---|---|---|---|---|---|
| CPX22 | 2 | 4 GB | 80 GB | 20 TB | 1 TB | 0.5 TB | confirmar |
| CPX32 | 4 | 8 GB | 160 GB | 20 TB | 2 TB | 1 TB | €13.10 |
| CPX42 | 8 | 16 GB | 240 GB | 20 TB | 3 TB | 2 TB | €24.70 |
| CPX52 | 16 | 32 GB | 360 GB | 20 TB | 4 TB | 3 TB | €54.40 |
| CPX62 | 16 | 32 GB | 640 GB | 20 TB | 5 TB | 4 TB | (verificar) |

US (Ashburn/Hillsboro): adicionar ~15-25% sobre preço EU.
Singapore: adicionar ~20-30% sobre preço EU.

### CAX (ARM64 Ampere, EU-only)

| Plano | vCPU | RAM | Disco | Traffic | Preço |
|---|---|---|---|---|---|
| CAX11 | 2 | 4 GB | 40 GB | 20 TB | confirmar |
| CAX21 | 4 | 8 GB | 80 GB | 20 TB | €6.49 |
| CAX31 | 8 | 16 GB | 160 GB | 20 TB | €12.49 |
| CAX41 | 16 | 32 GB | 320 GB | 20 TB | €24.49 |

### CCX (Dedicated vCPU AMD EPYC, global)

| Plano | vCPU ded. | RAM | Disco | Traffic EU | Traffic US | Traffic SIN | Preço EU |
|---|---|---|---|---|---|---|---|
| CCX13 | 2 | 8 GB | 80 GB | 20 TB | 1 TB | (verificar) | confirmar |
| CCX23 | 4 | 16 GB | 160 GB | 20 TB | 2 TB | (verificar) | confirmar |
| CCX33 | 8 | 32 GB | 240 GB | 30 TB | 3 TB | (verificar) | confirmar |
| CCX43 | 16 | 64 GB | 360 GB | 40 TB | 4 TB | (verificar) | confirmar |
| CCX53 | 32 | 128 GB | 600 GB | 50 TB | 6 TB | (verificar) | confirmar |
| CCX63 | 48 | 192 GB | 960 GB | 60 TB | 8 TB | (verificar) | confirmar |

## Adicionais comuns

| Item | Custo | Notas |
|---|---|---|
| Primary IPv4 | €0.50/mês | Cobrado mesmo se não anexado a servidor |
| Primary IPv6 | grátis | /64 por servidor |
| Floating IP | ~€1/mês | Cobrado mesmo desanexado |
| Backups (servidor) | +20% do preço do plano | 7 slots rolling diários |
| Snapshots | €0.011/GB-mês | Persistem até deletar manualmente |
| Volume (block storage) | €0.044/GB-mês | Mín 10 GB; mín billable 10 GB mesmo se menor |
| Object Storage base | confirmar | franquia e uso conforme tabela vigente |
| Object Storage extra storage | €0.0067/TB-hora (~€4.96/TB-mês contínuo) | Mínimo objeto 64 KB para billing |
| Object Storage extra egress | €1.00/TB | |
| Load Balancer LB11 | confirmar | 25 targets, 10k conexões, 5 services |
| Load Balancer LB21 | confirmar | 75 targets, 20k conexões, 10 services |
| Load Balancer LB31 | confirmar | 200 targets, 50k conexões, 25 services |
| Cloud Firewall | grátis | Stateful, no hipervisor |
| Placement Group | grátis | Anti-affinity entre hosts físicos |
| DDoS protection | grátis | Camada 3-4, ativa sempre |
| Tráfego inbound (ingress) | grátis | |
| Tráfego entre servidores na mesma Network privada | grátis | |
| Tráfego entre zonas Hetzner | cobrado como internet | Ex.: FSN ↔ ASH conta como egress dos dois lados |
| Tráfego excedente EU/US | €1.00/TB | Cobrado em blocos de 100 MB |
| Tráfego excedente Singapore | €7.40/TB | ~7x mais caro — modelar explicitamente |

## Preços de dedicados (Robot)

Sem cap mensal — você paga o mês cheio sempre. Setup fee único nos modelos novos (Auction tem setup fee = 0). Tráfego: 1 Gbit/s unlimited padrão; upgrade pra 10 Gbit/s incluí 20 TB com overage €1/TB.

| Linha | Faixa de preço | Exemplo entry-level | Exemplo high-end |
|---|---|---|---|
| AX (AMD Ryzen/EPYC) | €39-279/mês | AX42 Ryzen 5 3600, 64 GB, 2×512 GB NVMe ~€39 | AX162-R EPYC 32-core, 128 GB, 2×3.84 TB NVMe ~€279 |
| EX (Intel Core i5/i7/i9) | €36-199/mês | EX44 i5-13500, 64 GB, 2×512 GB NVMe ~€36 | EX102 i9-13900, 128 GB, 2×3.84 TB NVMe ~€199 |
| PX/SX (Xeon/EPYC enterprise) | €149-659+/mês | PX baseado, ECC, mais slots de disco | SX é storage-heavy (até 16 HDDs) |
| Auction (refurbished) | €20-150/mês | Servidores 1-3 gerações atrás | Sem setup fee, preços caem ao longo do dia |

**Setup fees** em modelos não-Auction: tipicamente igual ao preço de 1 mês, cobrado uma única vez. Auction sempre 0.

**Verificar preço atual** na [página oficial de Cloud](https://www.hetzner.com/cloud) e na [API/Console](https://docs.hetzner.com/cloud/api/). Para dedicados, consulte também a [página de root servers](https://www.hetzner.com/dedicated-rootserver/) e a Auction.

## Storage Box (não confundir com Object Storage)

File storage tradicional, via SMB/CIFS, SFTP, FTPS, WebDAV, Borg, rsync. Sem API S3. Bom para backups simples, sync de arquivos, NextCloud datastore.

| Plano | Storage | Preço aprox. |
|---|---|---|
| BX11 | 1 TB | ~€3.50/mês |
| BX21 | 5 TB | ~€10/mês |
| BX31 | 10 TB | ~€19/mês |
| BX41 | 20 TB | ~€38/mês |

10 sub-accounts inclusas. Inter-DC replication opcional (~+50%).

**Storage Box vs Object Storage**: Object Storage para apps modernas (S3 SDK), Storage Box para backups baseados em filesystem ou software legado que só sabe SMB/SFTP.

## Como o tráfego é cobrado, na prática

- **Calendar month**: ciclo do 1º ao último dia do mês. Reseta no dia 1º.
- **Bloco mínimo**: 100 MB (= 0.0001 TB) — Hetzner cobra blocos arredondados pra cima.
- **Ingress**: grátis sempre.
- **Egress dentro da mesma Network privada**: grátis.
- **Egress dentro do mesmo data center entre Cloud Servers via IP público**: grátis.
- **Egress entre zonas Hetzner**: cobrado dos dois lados como egress normal.
- **Egress para internet**: o ponto onde acontece a cobrança.
- **Multiplicidade**: cada servidor tem sua cota. Não há "pool de conta" — overage de um servidor não é compensado por subuso de outro. (Hetzner pode mudar isso; verificar antes de assumir.)

**Atenção a quotas reduzidas nos EUA pós-dez/2024**: planos CPX/CCX em ASH/HIL tiveram redução drástica (de 20 TB pra 1-8 TB). Se você lia conteúdo antigo dizendo "20 TB inclusos em qualquer plano", está desatualizado para US.

**Singapore overage de € 7.40/TB**: o caso mais caro. Um CPX22 SIN servindo 5 TB acima da cota = €37/mês extra só de bandwidth. Para alta saída em SIN, **pôr CDN na frente** é quase obrigatório.

## Como o billing aparece na fatura

- Fatura mensal emitida primeiros dias do mês seguinte
- Pagamento via cartão de crédito, PayPal, transferência SEPA (EU) ou wire (global)
- **Não há suporte oficial a Boleto/Pix** — Brasil paga em cartão internacional ou wire
- Crédito promocional (referral, código) aparece como linha negativa na fatura
- Recibos / NFs disponíveis pra download no Console

## Custo de migração / experimentação

- **Servidor criado e deletado em 1 hora**: cobrado pela hora cheia, ~€0.005-€0.02 dependendo do plano. Praticamente livre pra experimentar.
- **Servidor mantido 1 dia**: ~1/30 do preço mensal, ex.: CPX22 = ~€0.24
- **Snapshot criado e deletado no mesmo dia**: bill por hora-GB; ~zero se for poucos GB e poucas horas

Isso favorece muito iteração: teste configurações reais, não dimensione "no papel" — provisione, meça, redimensione.

## Estratégia de redução de custo (após estabilizar)

1. **Auditoria mensal**: rodar `hcloud server list`, `hcloud volume list`, `hcloud primary-ip list`, `hcloud snapshot list` e identificar recursos órfãos. Snapshots esquecidos e Primary IPs não-anexados são as causas mais comuns de "fatura cresceu sem motivo".
2. **Rescale para baixo**: se monitoramento (Coolify Sentinel, Netdata, Grafana) mostra CPU médio < 20% e RAM média < 40% por 2 semanas, considerar plano menor. Rescale para baixo precisa caber no disco — pode requerer cleanup antes.
3. **CX/CAX em vez de CPX** quando workload é leve. Compare o preço vigente e a compatibilidade da imagem antes de escolher.
4. **Migrar de US para EU** se latência for tolerável (CDN na frente resolve UX). Mesmo plano custa 15-25% menos.
5. **Mover egress pesado para Object Storage com CDN externa**. CDN (Cloudflare grátis, Bunny ~$0.01/GB) com cache hit rate alto reduz egress de origem drasticamente.
6. **Considerar Auction em vez de Dedicated novo** pra workloads grandes — desconto 20-40%, mesmo hardware, só refurbished.
7. **Backups+20% só onde RPO de 24h é aceitável** — para dados que mudam pouco, snapshot semanal + dump pra Object Storage é mais barato.

## Comparativos rápidos com outras nuvens (ordem de magnitude)

Para um app típico "produção pequena" (2 vCPU, 4 GB, 80 GB, 20 TB egress):

| Provedor | Plano comparável | Preço mensal aprox. (excl. tax) |
|---|---|---|
| **Hetzner Cloud CPX22 EU** | shared 2 vCPU AMD EPYC | confirmar |
| AWS EC2 t3.medium | shared 2 vCPU + 80 GB EBS + 20 TB egress | ~$80-120 |
| DigitalOcean Basic Premium AMD | shared 2 vCPU 4 GB | ~$24 |
| Vultr High Performance | shared 2 vCPU 4 GB | ~$24 |
| Linode/Akamai Dedicated CPU | shared 2 vCPU 4 GB | ~$24 |
| OVH VPS Comfort | shared 2 vCPU 4 GB | ~€14 |

Hetzner é tipicamente **2-3x mais barato que DigitalOcean/Vultr/Linode** no mesmo tamanho, e **8-15x mais barato que AWS** quando bandwidth entra na conta. Vantagem cai um pouco em US/Singapore por causa do tráfego incluso menor.

A vantagem é tão grande que mesmo software com 3x mais overhead operacional sai vencendo financeiramente em workloads que não precisam de managed services proprietários.
