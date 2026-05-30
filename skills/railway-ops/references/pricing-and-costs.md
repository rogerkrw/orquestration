# Pricing, planos e cost control

Referência detalhada de cobrança no Railway, planos, recursos por plano, mecanismos de cost control e padrões de otimização. Documentação oficial: [docs.railway.com/pricing](https://docs.railway.com/pricing).

> **Aviso:** os preços abaixo refletem o que estava na documentação oficial no momento em que esta skill foi escrita. Para qualquer decisão de negócio ou cotação real, **busque docs.railway.com/pricing/plans** — a Railway pode ter atualizado.

## Lógica de cobrança em uma frase

Você paga **subscrição** (fixa por mês, dá direito a usar a plataforma) **mais uso de recursos** (variável, baseado em consumo real de CPU/RAM/storage/egress). A subscrição já inclui uma cota de uso; só passa a cobrar uso extra quando você ultrapassa a cota.

## Planos

| Plano        | Subscrição/mês | Uso incluído na subscrição | Para quem                                                                                |
| ------------ | -------------- | -------------------------- | ---------------------------------------------------------------------------------------- |
| Trial        | $0 (uma vez)   | $5 de crédito grátis       | Experimentação inicial                                                                   |
| Free         | $0/mês         | $1/mês                     | Apps muito pequenos                                                                      |
| Hobby        | $5/mês         | $5/mês                     | Indie hackers, side projects                                                             |
| Pro          | $20/mês        | $20/mês                    | Times de devs profissionais, prod                                                        |
| Enterprise   | Custom         | Custom                     | Compliance, SLAs, account management dedicado                                            |

Subscrição é **flat fee paga independente do uso** — mesmo gastando $0 em recursos, a subscrição é cobrada.

A subscrição inclui um valor de uso. Exemplo Hobby ($5):
- Se você gastar $3 de recursos no mês, paga total **$5** (a subscrição).
- Se você gastar $7 de recursos, paga total **$7** ($5 subscrição + $2 acima da cota).

A cota incluída **não acumula** entre meses.

## Preços de recursos

Independente do plano (Hobby, Pro, Enterprise), o preço por unidade é o mesmo. O que muda entre planos é o **limite máximo** de cada recurso.

| Recurso          | Preço por mês          | Preço por minuto              |
| ---------------- | ---------------------- | ----------------------------- |
| RAM              | $10 / GB               | $0.000231 / GB                |
| CPU              | $20 / vCPU             | $0.000463 / vCPU              |
| Network Egress   | $0.05 / GB             | —                             |
| Volume Storage   | $0.15 / GB             | $0.000003472 / GB             |

Cobrança é **por minuto de consumo real**, não pelo limite alocado. Se sua app está rodando 24/7 com 0.5 vCPU e 512MB de RAM, o cálculo aproximado para um mês de 30 dias é:

- RAM: 0.5 GB × $10 = $5/mês
- CPU: 0.5 vCPU × $20 = $10/mês
- Total: ~$15/mês de recursos + subscrição

## Limites máximos por plano

Estes são os **tetos** por serviço (depois de multiplicação por replicas, no caso de replicas).

| Plano         | Replicas | RAM máx    | CPU máx       | Ephemeral Storage | Volume Storage | Image Size  |
| ------------- | -------- | ---------- | ------------- | ----------------- | -------------- | ----------- |
| Trial         | 2        | 1 GB       | 2 vCPU        | 1 GB              | 0.5 GB         | 4 GB        |
| Free          | 1        | 0.5 GB     | 1 vCPU        | 1 GB              | 0.5 GB         | 4 GB        |
| Hobby         | 6        | 48 GB      | 48 vCPU       | 100 GB            | 5 GB           | 100 GB      |
| Pro           | 42       | 1 TB       | 1.000 vCPU    | 100 GB            | 1 TB *         | Unlimited   |
| Enterprise    | 50       | 2.4 TB     | 2.400 vCPU    | 100 GB            | 5 TB *         | Unlimited   |

\* Volume: Pro pode self-serve até 1 TB; acima precisa contato. Enterprise sobe até 5 TB.

## Política de retenção de imagem

Imagens de deployments removidos são mantidas por um tempo (pra permitir rollback rápido):

| Plano            | Retenção    |
| ---------------- | ----------- |
| Free / Trial     | 24h         |
| Hobby            | 72h         |
| Pro              | 120h        |
| Enterprise       | 360h        |

Rollback dentro da retenção: restaura imagem + settings + variables, sem rebuild. Fora da retenção: precisa redeploy (rebuild do código original).

## Cost control — mecanismos

### 1. Usage limits (Compute e Agent)

Em **Workspace Usage** no dashboard, configure:

- **Custom email alert (soft limit):** quando o uso atinge esse valor no ciclo, Railway manda email. Workloads continuam rodando.
- **Hard limit:** quando o uso atinge esse valor, **Railway desliga todos os workloads** do workspace pra evitar cobrar mais. Aviso aos 75%, 90% e 100%.

Compute e Agent (Railway Agent / LLM) são limitados separadamente:

- **Compute hard limit** atingido → workloads offline, Agent continua disponível.
- **Agent hard limit** atingido → Agent disabled, workloads continuam rodando.

Defaults para Agent: $5/Hobby, $20/Pro. Você pode subir/baixar mas **não pode remover** (sempre tem um teto). Compute hard limit pode ser removido em planos pagos.

> **Recomendação:** sempre configure pelo menos o email alert. Hard limit em produção é arma de dois gumes — protege a carteira mas pode tirar o app do ar. Avalie se é OK.

### 2. Replica limits

Em **Service Settings → Deploy → Replica Limits**, defina os tetos de CPU e RAM por replica do serviço. Se a app tentar passar do teto, ela **crasha** (provavelmente OOM). Use quando:

- Há risco de bug fazer leak/spike e gerar conta alta.
- Crashar é aceitável (não é tier 1).

Não use em DBs nem em serviços críticos sem fallback. É controle de custo, não de qualidade.

### 3. Private networking

Comunicação entre serviços via URLs internas (`*.railway.internal`) é **grátis** — não gera network egress. Use sempre:

- **Para banco:** use `DATABASE_URL` (interno), não `DATABASE_PUBLIC_URL`.
- **Entre serviços:** use o `RAILWAY_PRIVATE_DOMAIN` ou pegue a URL privada em Service Settings.

O egress (`$0.05/GB`) só conta para tráfego saindo da rede da Railway para o mundo (clientes finais). Tráfego interno do mesmo projeto é gratuito.

### 4. Serverless (scale-to-zero)

Em **Service Settings → Deploy → Serverless**, ative o toggle. Quando ativado:

- O serviço entra em "sleep" depois de um período de inatividade.
- Próxima requisição faz cold start (rebuild não, mas startup demora).
- Não cobra recursos durante o sleep.

Bom para: serviços internos, dashboards usados raramente, endpoints de webhook.
Ruim para: APIs com SLA, jobs que precisam acordar rápido, processos always-on.

### 5. Image retention controla custo indiretamente

Imagens em retenção ocupam storage. Em escala, fazer deploy frequente em planos com 120-360h de retenção significa muitos GBs guardados. Não há controle direto disso, mas vale ter consciência.

## Padrões de otimização

Aplicar nesta ordem quando alguém diz "minha conta tá alta":

### Padrão 1: Cortar egress

Quase sempre é a primeira correção barata. Cheque:
- Apps comunicando entre si via URL pública: trocar pra `*.railway.internal`.
- DB usando `DATABASE_PUBLIC_URL`: trocar pra `DATABASE_URL`.
- Health checks de monitoramento externo gerando muito tráfego: avaliar frequência.

### Padrão 2: Right-sizing de replicas

Para cada serviço, olhar **Service Metrics** por uma janela típica (semana). Identificar:
- CPU avg < 30% sustentado? → considerar reduzir replicas ou serverless.
- RAM avg < 50% sustentado? → considerar replica limits ou reduzir instâncias.
- Picos altos isolados? → manter recursos mas considerar restart policy `ON_FAILURE` em vez de `ALWAYS`.

### Padrão 3: Serverless em ambientes não-críticos

Staging, previews de PR, dashboards internos → ligar serverless. Economia substancial pra coisas que não precisam estar 24/7.

### Padrão 4: Replica limits como rede de segurança

Setar replica limits ligeiramente acima do pico observado (ex: pico de 700MB → limite de 1GB). Previne bug de memory leak ou loop de CPU virar surpresa.

### Padrão 5: Reavaliar plano

- Se você está pagando Pro ($20) mas usa < $5/mês de recursos e não precisa dos limites Pro nem colaboração: descer pro Hobby.
- Se você está pagando Hobby ($5) mas batendo no teto (6 replicas, 48GB RAM) ou rateando outra workspace pra colaborar: subir pro Pro.

## Como estimar custo de um workload

Receita rápida pra responder "quanto vai custar essa nova feature?":

1. **CPU/RAM esperado:** quanto sustentado, não pico. Use métricas similares de outros serviços ou rode local e olhe consumo.
2. **Multiplicar por preço:** `CPU_GB × $10 + vCPU × $20 = $/mês de runtime`.
3. **Network egress:** estimar tráfego mensal saindo. `GB × $0.05`. Subestime se for B2B; superestime se for B2C com mídia.
4. **Volume (se houver):** `GB × $0.15`.
5. **Somar subscrição** (já tem? já paga? só adiciona uso).
6. **Aplicar cota incluída:** $5 (Hobby) ou $20 (Pro) sai do total.

**Exemplo:** API Node em produção, 1GB RAM, 1 vCPU, sempre ligada, ~50GB/mês de egress, plano Pro já existente.
- RAM: 1 × $10 = $10
- CPU: 1 × $20 = $20
- Egress: 50 × $0.05 = $2.50
- Subtotal recursos: $32.50/mês
- Cota Pro incluída: -$20
- Uso cobrado extra: **$12.50/mês**
- Total na conta: $20 (subscrição) + $12.50 = **$32.50/mês**

## Free Trial e créditos

- Trial: novos usuários ganham $5 de crédito grátis (uma vez). Não pode comprar créditos sem fazer upgrade pra Hobby.
- Free: $1/mês de uso recorrente. Limites baixos (0.5GB RAM, 1 vCPU, 1 replica).
- Créditos comprados são consumidos antes da carteira ser cobrada. Se créditos zeram com método de pagamento configurado como "credits", **a subscrição é cancelada e workloads são desligados**.

## Hobby waiver

Pode haver waiver automático do $5/mês do Hobby — Railway avalia uso e perfil GitHub. Não dá pra pedir manualmente. Se você qualifica, dashboard mostra. Mais nada.

## Partial month charges

Railway pode cobrar parcial do bill antes do fim do ciclo se identificar risco/fraude. Não é bug — é proteção contra inadimplência.

## Quando sua conta acabar (limit/credits exhaustion)

Comportamento dependendo do mecanismo:

- **Hard limit (compute) atingido:** workloads são parados. Pra religar: aumente o limit ou espere o próximo ciclo (renova automaticamente).
- **Hard limit (agent) atingido:** Agent fica disabled, workloads seguem.
- **Créditos zeraram com método de pagamento = credits:** subscrição cancelada, tudo parado. Comprar créditos novos não reativa — precisa reassinar.
- **Cartão recusado:** Railway dá grace period com avisos antes de derrubar.

## Volume data retention após cancelar plano

Se você cancelar e ficar sem plano pago, Railway apaga seus dados após:

| Plano                  | Dias após cancelamento      |
| ---------------------- | --------------------------- |
| Free ou Trial          | 30 dias após expiração       |
| Hobby                  | 60 dias                     |
| Pro                    | 90 dias                     |

Backup dos seus volumes antes de cancelar é fortemente recomendado.

## AWS Marketplace e committed spend

- Empresas podem comprar Railway via [AWS Marketplace](https://docs.railway.com/pricing/aws-marketplace) (consolida no bill da AWS).
- Pra contratos maiores (~$2k+/mês recorrentes), há [committed spend](https://docs.railway.com/pricing/committed-spend) com desconto.

## Quando o usuário pergunta sobre custo, perguntas a fazer primeiro

1. Em qual plano está hoje? (define cota incluída e limites)
2. Workload tá rodando 24/7 ou intermitente? (define se serverless ajuda)
3. Tem replicas? Quantas? (multiplicador)
4. Tráfego externo é grande? (egress)
5. Tem volume? Tamanho? (custo proporcional)
6. Tem múltiplos environments rodando? (staging "esquecido" é fonte comum)
