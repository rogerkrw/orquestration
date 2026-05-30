# Testing quality & QA heuristics

Esta referência cobre dois ângulos relacionados:

1. **Como avaliar a qualidade dos testes em si** (review de testes — uma das partes mais esquecidas de code review)
2. **Como pensar como um QA senior** (heurísticas para descobrir o que mais precisa de teste e quais cenários estão escondidos)

A grande virada de mentalidade: cobertura % não é qualidade. Um teste pode passar e estar testando exatamente nada. O foco é em **comportamentos verificados**, não em linhas tocadas.

---

## Parte 1 — Como avaliar testes em review

### O teste do teste: "ele falharia se o código quebrasse?"

Faça este experimento mental (ou real) com qualquer teste suspeito:

> "Se eu inverter a condição central do código em produção, este teste fica vermelho?"

Se a resposta é "não" ou "talvez", o teste é decorativo. Exemplos clássicos:

```js
// 🚨 Não testa nada
it('should return user', () => {
  const user = userService.find(1)
  expect(user).toBeDefined()  // qualquer não-null passa
})

// 🚨 Testa o mock, não o código
it('should call repository', () => {
  service.doThing()
  expect(repo.save).toHaveBeenCalled()  // só verifica que mock foi chamado
})

// ✅ Testa comportamento observável
it('should debit balance when transferring', () => {
  account.transfer(100, otherAccount)
  expect(account.balance).toBe(900)
  expect(otherAccount.balance).toBe(1100)
})
```

### Testes de implementação vs. testes de comportamento

**De implementação:** "verifica que `methodX` foi chamado com `arg Y`". Quebra em refactor correto. Acopla o teste à estrutura interna.

**De comportamento:** "dada entrada A, observo saída B". Robusto a refactors. Testa contrato, não código.

Prefira sempre comportamento. Mocks são ferramenta para isolar dependências externas (rede, disco, tempo), não para "testar interações internas".

### O trap do over-mocking

Quando *tudo* é mockado, o teste verifica que sua suposição sobre o sistema está consistente com sua outra suposição sobre o sistema. Falso senso de segurança. Quando o sistema real comporta-se diferente dos mocks (e sempre acaba acontecendo), os testes não pegam.

**Quando mockar:**
- I/O externo (network, disco, clock) que não dá pra controlar de outro jeito
- Componentes muito lentos para tests unitários
- Dependências que não estão prontas

**Quando NÃO mockar:**
- Lógica pura do seu próprio código
- Camadas adjacentes que você pode usar de verdade
- Database — prefira test database em memória ou container

### Sinais de teste podre

- **Asserção genérica:** `expect(result).toBeTruthy()`, `expect(arr.length).toBeGreaterThan(0)` → quase nada testado
- **Sem arrange-act-assert visível:** teste de 60 linhas misturando setup e verificação → ninguém sabe o que tá sendo verificado
- **Setup compartilhado mutável entre testes:** estado vaza, ordem importa, flakiness garantida
- **`sleep(N)` ou `Thread.sleep`:** sinaliza dependência de timing → vai flakar
- **Depende de banco real / network real sem isolation:** flakará por causas externas
- **Múltiplas asserções não relacionadas:** quando falha, não dá pra saber qual problema
- **Snapshot tests gigantes:** atualizar sem ler, todo PR vira "snapshot updated"
- **`@Disabled` / `it.skip` deixados** sem TODO ou link de issue
- **Logs de print/console no teste** = autor estava debugando, nunca limpou

### Sinais de teste bom

- Nome descreve o caso, não o método. "should reject negative amounts" > "testTransfer2"
- Single assertion conceitual (pode ter múltiplas linhas de `expect` se for sobre o mesmo conceito)
- AAA visível ou Given/When/Then explícito
- Independente: pode rodar em qualquer ordem, isoladamente
- Determinístico: 100 runs sem código mudando = 100 mesmo resultado
- Rápido (para unit; integration pode ser mais lento)
- Quebra de uma forma que diz exatamente o que está errado

### Pirâmide / honeycomb / queijo suíço — qual modelo?

Não importa o modelo abstrato. Importam essas perguntas:

- Existe um nível de teste em que esse comportamento crítico esteja verificado?
- O teste pertence ao nível que pega esse tipo de bug mais barato?
  - Bug de lógica isolada → unit
  - Bug de integração entre módulos → integration
  - Bug de comportamento de usuário no produto → e2e
- Para microsserviços, **honeycomb** (mais integration, menos unit) frequentemente é melhor que pirâmide pura

---

## Parte 2 — Pensando como QA senior: descobrir o que precisa de teste

QA senior não testa "tudo". Testa onde os bugs estão mais prováveis, e onde o impacto é maior se aparecerem. Isso é heurística estruturada.

### Heurística SFDIPOT (San Francisco Depot)

Criada por James Bach, é o framework mais usado para mapear cobertura de teste de uma feature/produto. Use ao revisar testes de uma feature inteira: para cada letra, pergunte "isso foi pensado?".

**S — Structure.** O que existe? Arquivos, módulos, schemas, configs. (Não é só sobre o código — é sobre o que constitui o sistema.)

**F — Function.** O que faz? Cada capability declarada da feature.

**D — Data.** Com que dados opera? Tipos, ranges, formatos, default, especiais (vazio, null, max, unicode, negativo, zero, muito grande, malformado).

**I — Interfaces.** Com o que interage? UI, APIs, bibliotecas, sistema operacional, sistemas externos.

**P — Platform.** Em que ambiente roda? OS, browser, dispositivos, versões, locale.

**O — Operations.** Como é usado de verdade? Sequências de ações, fluxos típicos vs. raros, automação, scripts, persona X usando feature Y para fim Z.

**T — Time.** Quando? Ordem, simultaneidade, duração, expiração, schedule, ciclos, intervalos.

Aplicando ao review de teste: pegue cada categoria SFDIPOT e marque mentalmente se aparece coberta na suite. Os buracos óbvios viram comentários no PR.

### Heurística FEW HICCUPPS (oracles de teste)

Quando você olha o resultado de uma operação, **como você sabe se está certo?** São os oráculos de Bach/Bolton. Use para validar que os asserts dos testes estão usando o critério certo:

- **F — Familiar.** Parece com o que já vi funcionar?
- **E — Explainable.** Consigo explicar por que esse resultado é correto?
- **W — World.** Faz sentido contra o mundo real (fato externo)?
- **H — History.** O sistema costumava se comportar assim?
- **I — Image.** Está alinhado com a imagem/branding do produto?
- **C — Comparable products.** Outro produto similar faz isso?
- **C — Claims.** Está consistente com o que documentação/marketing diz?
- **U — User's desires.** O usuário ficaria satisfeito com isso?
- **P — Product.** Outras partes do mesmo produto fazem assim?
- **P — Purpose.** Cumpre o propósito declarado da feature?
- **S — Statutes.** Atende regulamentação/política?

### Tours (testing tours)

Heurísticas de "como caminhar pelo produto" durante exploração:

- **Guidebook tour:** entrar como turista, seguir happy paths principais.
- **Saboteur tour:** tentar quebrar — inputs inválidos, sequências fora de ordem, ações concorrentes.
- **Money tour:** seguir caminhos que envolvem dinheiro/operações críticas.
- **Landmark tour:** tocar todas as features principais em sequência.
- **Back alley tour:** features mais obscuras, raramente usadas.
- **All-nighter tour:** sessão muito longa, sem fechar app — vazamentos, expiração, estado acumulado.
- **Persona tour:** simular comportamento de um tipo específico de usuário (apressado, técnico, idoso, com deficiência).
- **Antisocial tour:** o que aconteceria se múltiplos usuários colaborassem (concorrência distribuída)?

Em review, use isso para sugerir cenários ausentes: "Faltam testes para o caminho de Money tour aqui — o que acontece se a cobrança falhar após o débito?"

### Boundary Value Analysis (BVA)

Para qualquer parâmetro de entrada com limite definido, há 7 valores de interesse:

| Categoria | Valor |
|---|---|
| Inválido baixo | min - 2 |
| Inválido baixo na borda | min - 1 |
| Mínimo válido | min |
| Nominal | meio |
| Máximo válido | max |
| Inválido alto na borda | max + 1 |
| Inválido alto | max + 2 |

Em um teste pragmático, foque em **min-1, min, max, max+1**. Esses são onde 80% dos off-by-one moram.

**Aplicação típica:**
- Tamanhos de strings (campo de 0-255 chars → testar 0, 1, 255, 256)
- Quantidades (carrinho 1-99 → testar 0, 1, 99, 100)
- Datas (futuro próximo, distante, passado, hoje, ontem)
- Coleções (vazia, 1 item, n itens, máximo permitido + 1)

### Equivalence Partitioning

Para inputs sem fronteira numérica clara, agrupe em classes equivalentes e teste *uma* representante de cada:

- Email: válidos com diferentes formatos (RFC), inválidos por estrutura, inválidos por chars
- Cor: hex válido (#fff, #ffffff), hex inválido, named color, rgb()
- Arquivo: ext esperada, ext inesperada, sem ext, ext correta mas conteúdo errado

A combinação BVA + EP geralmente cobre 80%+ dos bugs de input.

### Negative testing

Para cada caminho positivo testado, pergunte "qual é o cenário negativo análogo?":

- Login válido → senha errada, usuário não existe, conta bloqueada, MFA falha
- Create válido → duplicate, sem permissão, payload malformado, payload gigante
- Update válido → versão obsoleta (concurrent edit), recurso já deletado
- Delete válido → recurso não existe (idempotência?), recurso com dependentes

QA senior não pergunta "qual é o teste?" mas "**quais são os 5 testes**?" — um positivo e quatro negativos cobrindo diferentes formas de falha.

---

## Parte 3 — Categorias de teste a verificar em uma feature

Quando o PR introduz uma feature significativa, considere se cada categoria está adequadamente coberta. Não todas precisam ser cobertas — mas a *decisão* de não cobrir uma deve ser consciente.

### Funcional
- Happy path principal
- Branches alternativos (input variations, user states)
- Edge cases (vazio, máximo, especial)

### Erro / falha
- Inputs inválidos (validação)
- Dependências indisponíveis (timeout, 500 do downstream)
- Concorrência (mesmo recurso editado simultaneamente)
- Resource exhaustion (rate limit excedido, banco lento)

### Segurança
- Autorização vertical (admin vs user)
- Autorização horizontal (user A vs user B)
- Validação adequada de input
- Não vazamento de dados em erros

### Performance (se relevante)
- Latência sob carga típica
- Comportamento em pico
- Sem N+1
- Sem regressão vs baseline

### Compatibilidade
- Versões de browser/OS suportadas
- Locales / timezones diferentes
- Tamanhos de tela diferentes (frontend)
- Modo offline / conectividade ruim

### Acessibilidade (frontend)
- Navegação por teclado funciona
- Screen reader anuncia adequadamente
- Contraste suficiente
- Foco visível e gerenciado

### Observabilidade
- Logs aparecem para erros importantes
- Métricas refletem comportamento real
- Alertas disparam quando deveriam (e não quando não deveriam)

---

## Test charter — modelo para sessões de exploração

Quando QA exploratório é necessário para validar feature antes de aprovar, sugira ao autor preparar um charter para sessão exploratória:

```
Explorar: [área da feature]
Com: [recursos, dados de teste, ferramentas]
Para descobrir: [riscos específicos]
Timebox: [tempo]
```

Exemplo:
```
Explorar: o fluxo de checkout com pagamento por cartão
Com: cards de teste do gateway, dados de usuários em vários estados (novo, recorrente, com falha anterior)
Para descobrir: bugs de validação, problemas de UI sob latência, comportamento em falha de pagamento, integridade do estado do pedido
Timebox: 90 minutos
```

Sessões com charter encontram, segundo pesquisa BBST, 40-60% mais bugs acionáveis que exploração sem charter, no mesmo tempo.

---

## Bug report — RIMGEN

Quando você (como reviewer) reporta um problema encontrado, vale a heurística RIMGEN para qualidade do report:

- **R — Reproducível:** passos claros e mínimos para reproduzir
- **I — Isolado:** o menor cenário possível que mostra o problema
- **M — Manageable:** severidade real (não tudo é crítico, não tudo é nit)
- **G — Geral:** funciona em ambientes específicos ou em qualquer um?
- **E — Evidente:** está claro o que está errado vs. esperado
- **N — Notarizado:** ligado ao contexto (PR, commit, ticket)

Reports vagos atrasam fix; reports claros aceleram.

---

## Checklist condensado para review de testes

```
Qualidade individual
  [ ] Cada teste falha se o código quebra?
  [ ] Testa comportamento, não implementação?
  [ ] Não está over-mocked a ponto de não testar nada real?
  [ ] AAA / Given-When-Then visíveis?
  [ ] Single concept per test?
  [ ] Determinístico (sem sleep, sem random sem seed)?

Cobertura por categoria
  [ ] Happy path coberto
  [ ] Pelo menos 2-3 caminhos negativos cobertos
  [ ] Boundary values testados (min-1, min, max, max+1)?
  [ ] Concorrência considerada (se aplicável)?
  [ ] Segurança (authz, validation) testada?

Em features grandes
  [ ] SFDIPOT — cada dimensão pensada?
  [ ] FEW HICCUPPS — oráculos certos sendo usados?
  [ ] Negative path tem 5 testes para cada happy path?
```
