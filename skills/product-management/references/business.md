# Lente de negócio

O que sustenta a decisão de produto do lado financeiro e de mercado. Não é relatório de finanças — é o mínimo para responder "isso se paga?", "cabe no mercado?" e "por que nós?".

Cada métrica traz fórmula, benchmark e por que importa para a decisão de produto.

## Unit economics

**Gross Margin** — `(Receita − COGS) / Receita × 100`
COGS inclui hosting, infraestrutura, processamento de pagamento, custo de onboarding. Benchmark SaaS: 70-85% saudável, <60% preocupante.
*Por que importa:* uma feature que gera R$ 1M a 80% de margem vale muito mais que R$ 1M a 30%. Margem decide o que priorizar.

**CAC (Custo de Aquisição de Cliente)** — `Investimento em vendas e marketing / Novos clientes`
Inclui mídia, salários de vendas, ferramentas e comissões. Varia por modelo: enterprise acima de R$ 50k é aceitável; self-service precisa ficar baixo.
*Por que importa:* define quais canais são viáveis e quanto dá para investir em crescimento via produto.

**LTV (Lifetime Value)** — `ARPU × Margem bruta % / Churn`
A versão simples (`ARPU × meses de vida`) serve para ordem de grandeza; a de margem é a que decide investimento.
*Por que importa:* diz quanto se pode gastar para adquirir. LTV alto habilita canal caro e payback longo.

**LTV/CAC** — Benchmark: ≥ 3 saudável, < 1 insustentável, > 5 pode indicar subinvestimento em crescimento.

**CAC Payback** — `CAC / (ARPU mensal × margem bruta)`
Benchmark: < 12 meses bom, > 18 meses exige caixa robusto.
*Por que importa:* é a métrica de fôlego. Payback longo com caixa curto quebra a empresa mesmo com LTV/CAC bom.

**Churn** — mensal e anual, por logo e por receita.
Benchmark: SMB 3-5%/mês tolerável; enterprise > 1%/mês é problema. **Net Revenue Retention (NRR)** acima de 100% significa que a base cresce sozinha — é o número que mais interessa a investidor.

**Burn multiple** — `Queima líquida / Receita nova líquida`. Abaixo de 1,5 é eficiente; acima de 3 é caro demais.

**Rule of 40** — `Crescimento % + Margem de lucro % ≥ 40`. Régua de equilíbrio entre crescer e ser rentável.

## Tamanho de mercado

**TAM** (total endereçável) → **SAM** (servível, dado o produto e a geografia) → **SOM** (obtenível em 3-5 anos, dada a capacidade real).

Duas abordagens:

- **Top-down:** parte de relatório de mercado. Rápido, e quase sempre otimista demais.
- **Bottom-up:** `nº de clientes potenciais × ticket médio anual`. Mais defensável, e é o que se usa em decisão interna.

*Por que importa:* mercado pequeno com produto excelente limita o teto. Serve para decidir entre nichar e ampliar — não para justificar otimismo.

## Pricing e empacotamento

**Modelos:** por assento, por uso, por tier, freemium, híbrido.

**Value metric** — a unidade pela qual o cliente paga (assento, transação, GB, projeto). A boa value metric cresce junto com o valor percebido: se o cliente ganha mais e paga mais, a expansão vem sozinha.

**Regras práticas:**

- Preço é decisão de produto, não de planilha — reflete o posicionamento.
- Três tiers é o padrão que funciona; o do meio é onde a maioria cai por desenho.
- Aumento de preço vale mais que aquisição no curto prazo: 1% de preço rende mais margem que 1% de volume.
- Desconto recorrente vira preço novo. Prefira prazo ou escopo a desconto de tabela.

**No Brasil:** parcelamento e Pix mudam a economia — Pix reduz custo de transação e antecipa caixa; parcelamento no cartão custa antecipação. Considerar no preço, não depois.

## Competitivo

**Porter (5 forças):** rivalidade, entrantes, substitutos, poder do fornecedor, poder do comprador. Usar para entender a estrutura do setor, não para preencher quadro.

**SWOT:** só vale com evidência. Sem dado, vira lista de desejos.

**Matriz de posicionamento:** dois eixos que importam para o cliente (nunca "preço × qualidade"), com você e os concorrentes no plano.

**Perguntas que valem mais que o framework:**

- Contra o que o cliente realmente compara — incluindo planilha, processo manual e não fazer nada?
- O que ele precisa deixar de fazer para nos adotar?
- Qual concorrente ele cita sem ser perguntado?

## Posicionamento

Fórmula (April Dunford, simplificada):

```
Para [segmento] que [necessidade/situação],
o [produto] é [categoria]
que [benefício diferenciador],
diferente de [alternativa concorrente],
porque [prova].
```

A categoria escolhida define contra quem você é comparado — é escolha estratégica, não descritiva.

## Jobs-to-be-Done

`Quando [situação], quero [motivação], para que [resultado esperado].`

Foca no progresso que a pessoa tenta fazer, não no perfil demográfico. Puxa as três forças: o que empurra para fora do estado atual, o que atrai para a solução nova, e o que segura (hábito e ansiedade). Boa parte do trabalho de adoção é reduzir o que segura, não aumentar o que atrai.

## Viabilidade, antes de construir

Quatro riscos (Marty Cagan) — todo os quatro precisam de resposta:

| Risco | Pergunta |
| --- | --- |
| Valor | as pessoas querem isso a ponto de pagar ou trocar de hábito? |
| Usabilidade | conseguem usar? |
| Viabilidade técnica | conseguimos construir e sustentar? |
| Viabilidade de negócio | funciona para vendas, suporte, jurídico, margem e canal? |

O quarto é o mais esquecido em time técnico: feature que aumenta suporte, quebra margem ou não tem como ser vendida não é entregável, é passivo.

## Case de negócio, em uma página

Para levar decisão a quem paga:

1. **Problema** e quem tem, com evidência
2. **Tamanho** — quantos, quanto vale (bottom-up)
3. **Proposta** — o que se constrói, em uma frase
4. **Custo** — esforço em tempo de time, mais custo recorrente
5. **Retorno** — receita nova, receita retida ou custo evitado, com a premissa explícita
6. **Risco** — o que pode dar errado e qual o sinal antecipado
7. **Alternativa não escolhida** — e por quê

Premissa explícita vale mais que número preciso: quem lê precisa poder discordar da premissa, não do arredondamento.
