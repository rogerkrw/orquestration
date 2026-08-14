# Interface em português do Brasil

A literatura de UI assume inglês. Interface em PT-BR não é interface em inglês traduzida — muda o dimensionamento, os formatos e as convenções de escrita.

## Expansão de texto

**Texto em português ocupa 15-25% mais espaço que o equivalente em inglês.** É a causa mais comum de layout quebrado em projeto brasileiro construído sobre componente ou referência em inglês.

| Inglês | Português | Δ |
| --- | --- | --- |
| Save | Salvar | +50% |
| Settings | Configurações | +75% |
| Sign out | Sair da conta | +62% |
| Search | Buscar | +17% |
| Delete account | Excluir conta | ~0% |
| Loading… | Carregando… | +25% |

Consequências práticas:

- **Dimensionar pelo maior rótulo do conjunto**, com o texto real em português — nunca por lorem nem pelo termo em inglês.
- **Botão com largura fixa** derivada do inglês quebra. Preferir largura fluida com padding, ou testar o pior caso.
- **Nav e tab bar** são o ponto mais frágil: "Configurações" e "Notificações" estouram tab de 4 destinos no mobile. Considerar ícone + rótulo curto.
- **Tabela** precisa de largura de coluna pensada em PT-BR; cabeçalho como "Data de criação" não cabe onde cabia "Created".
- Todo container de texto precisa de estratégia de overflow (`truncate`, `line-clamp`, `break-words`) — ver `review.md`.

## Formatos

| Tipo | Formato | Observação |
| --- | --- | --- |
| Moeda | `R$ 1.234,56` | Ponto no milhar, vírgula no decimal, espaço após `R$` |
| Data | `13/08/2026` | `dd/mm/aaaa`; nunca `mm/dd` |
| Data por extenso | `13 de agosto de 2026` | Mês em minúscula |
| Hora | `14:30` | 24h, sem AM/PM |
| Número | `1.234.567,89` | Inverso do inglês |
| Percentual | `12,5%` | Vírgula decimal |
| Telefone | `(48) 99123-4567` | Celular com o 9 na frente |
| CEP | `88010-000` | Máscara com hífen |
| CPF | `123.456.789-00` | Máscara com pontos e hífen |
| CNPJ | `12.345.678/0001-90` | Máscara completa |

Usar `Intl.NumberFormat('pt-BR')` e `Intl.DateTimeFormat('pt-BR')` em vez de formatar à mão.

**Entrada de dado com máscara:** CPF, CNPJ, CEP, telefone e valor monetário entram com máscara aplicada durante a digitação, mas o valor persistido é o cru (só dígitos). Não bloquear colar — quem cola CPF costuma colar formatado; normalizar na entrada.

**CEP** merece busca automática de endereço (ViaCEP ou equivalente): a pessoa digita o CEP e os campos de rua, bairro, cidade e UF se preenchem. É expectativa consolidada no Brasil, não diferencial.

## Escrita

- **Sem Title Case.** Título, botão e rótulo em frase capitalizada: "Salvar alterações", não "Salvar Alterações". Title Case é convenção do inglês e em português lê como erro.
- **Segunda pessoa implícita:** "Crie sua conta", não "Você deve criar sua conta".
- **Evitar primeira pessoa do plural:** "Enviamos um e-mail" em vez de "Nós enviamos um e-mail".
- **Gerúndio só onde cabe:** "Carregando…" é correto; "Estaremos enviando" é ruído.
- **Termo técnico consagrado fica em inglês** quando a tradução confunde: *login*, *e-mail*, *upload*, *dashboard*, *link*. Traduzir o que tem equivalente natural: *save* → salvar, *delete* → excluir, *settings* → configurações.
- **Consistência de par:** escolher "Excluir" ou "Apagar" e manter no produto inteiro; o mesmo para "Entrar"/"Fazer login" e "Sair"/"Sair da conta".
- **Evitar tradução literal de erro:** "Falha ao processar a requisição" é tradução; "Não foi possível salvar. Tente novamente." é português.

## Pagamento

- **Pix é método de primeira classe**, não alternativa. Em fluxo de checkout brasileiro, costuma vir antes ou junto de cartão — não escondido em "outras formas de pagamento".
- Pix por QR Code precisa de: código copiável (botão "Copiar código"), QR visível, prazo de expiração explícito e confirmação assíncrona (o pagamento não confirma no mesmo instante — a UI precisa de estado de espera).
- Cartão em parcelas é expectativa: mostrar o número de parcelas e o valor de cada uma, não só o total.

## Acessibilidade e idioma

- `<html lang="pt-BR">` — sem isso, leitor de tela pronuncia o conteúdo com fonética inglesa.
- Nome de marca e identificador com `translate="no"`, para tradução automática não deformar.
- `alt` e `aria-label` também em português, com a mesma revisão do texto visível.
