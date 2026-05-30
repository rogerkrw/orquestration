# Como comunicar feedback que é ouvido e implementado

Esta referência é sobre **a forma do review**, não o conteúdo. A diferença entre um review tecnicamente correto que é seguido vs. ignorado mora aqui.

Premissa: review é uma conversa entre duas pessoas que querem o mesmo resultado. Não é "professor corrigindo aluno", não é "guardião do portão", não é "show de senioridade". Quando vira qualquer uma dessas coisas, o autor para de aprender e começa a se defender.

---

## Princípio fundamental

> "Review o código, não a pessoa."

Toda crítica deve ser sobre **o código** ou **a decisão técnica**, nunca sobre o autor. Sutil, mas conta:

- ❌ "Você esqueceu de tratar o caso null."
- ✅ "Falta tratamento de null aqui."
- ❌ "Você não entendeu o pattern."
- ✅ "Este pattern não está sendo aplicado da forma usual; provavelmente quer X."
- ❌ "Por que você fez assim?"
- ✅ "Curioso sobre a escolha — havia alguma razão para X em vez de Y?"

O segundo prefere "we" / "este código" / "essa abordagem" sobre "você".

---

## A escada de tons (do mais firme ao mais leve)

Use o tom certo para a severidade. Aplicar tom forte a tudo cria fadiga; aplicar tom leve a coisas críticas faz com que escape.

### 🛑 Blocker
> "Este código vai criar uma race condition no transfer. Dois requests concorrentes vão poder debitar o mesmo saldo. Precisamos de uma operação atômica antes de merge — sugiro `UPDATE accounts SET balance = balance - ? WHERE id = ? AND balance >= ?` para falhar atomicamente quando saldo é insuficiente."

Estilo: claro, técnico, justificado, com solução proposta.

### ⚠️ Should fix
> "Esta query vai degradar conforme `posts` cresce — N+1 clássico, uma query por post para pegar `author`. Geralmente resolvemos com prefetch. Não bloqueia se preferir tratar em PR separado, mas vamos abrir issue."

Estilo: indica problema, oferece direção, dá ao autor controle sobre o momento de resolver.

### 💡 Suggestion / Nit
> "Nit: este `useMemo` provavelmente não é necessário aqui — o cálculo é barato e as deps mudam toda hora, então o overhead da memo pode ser maior que o ganho. Opcional."

Estilo: opcional explícito, breve, com porquê.

### 👍 Praise
> "Curti o tratamento do empty state com call-to-action — fica muito mais útil que um placeholder genérico."

Estilo: específico (não "bom trabalho!"), aponta o quê e por quê é bom.

---

## Use perguntas quando há ambiguidade

Reviewers júniores fazem afirmações. Reviewers seniors fazem perguntas — porque sabem que o autor pode ter contexto que eles não têm.

Em vez de:
- "Está errado tratar dessa forma."
- "Deveria usar X."

Prefira:
- "Considerou o caso onde Y? Pergunto porque achei que aqui não estaria coberto."
- "Tem alguma razão específica para essa abordagem em vez de X? X seria meu reflexo, mas você tem mais contexto da feature."

Quando o autor responde, você aprende OU ele percebe a lacuna. Os dois resultados são bons. Afirmar sem perguntar quando há dúvida real frequentemente leva a discussão tensa onde alguém precisa "ceder".

**Quando NÃO usar perguntas:** quando algo está objetivamente errado e perguntar soa passivo-agressivo ("Você acha mesmo que isso compila?"). Para erros claros, afirme com gentileza.

---

## Sempre explique o "porquê"

Comentário sem justificativa é instrução; comentário com justificativa é mentoria.

❌ "Use map em vez de for."

✅ "Aqui um `.map` deixaria a intenção mais óbvia — você está transformando cada item, não acumulando estado. O for funciona, mas leitor precisa parar e processar."

❌ "Tem que tratar o erro."

✅ "Se essa chamada falhar, a função retorna `undefined` silenciosamente e o caller não sabe — isso já causou um incidente parecido aqui [link]. Vale tratar explicitamente ou propagar."

O porquê é onde o autor aprende. Sem ele, o autor implementa por obediência e repete o mesmo erro no próximo PR.

---

## Sugira código, mas com parcimônia

Mostrar uma alternativa de 5-10 linhas é didático. Reescrever 100 linhas no comentário toma o trabalho do autor e é arrogante.

**Bom:**
> "Talvez algo assim seja mais claro:
> ```js
> const total = items.reduce((sum, item) => sum + item.price, 0)
> ```
> Mas é sugestão — se tiver razão para o for explícito, deixa."

**Ruim:** colar 80 linhas reescritas com "fiz assim".

Para mudanças grandes, prefira indicar a direção e deixar o autor implementar:

> "Acho que isso pediria um pequeno refactor para separar a parte de validação da parte de persistência. Não precisa fazer agora — abre uma issue?"

---

## Reconheça o que está bom

Reviews que só apontam problemas treinam o autor a desligar o filtro de aprendizado e ligar o filtro de defesa. Reviews que reconhecem coisas boas mantêm o canal aberto.

Não precisa ser elogio em todo PR — soaria forçado. Mas quando algo está genuinamente bem feito:

- Refactor que ficou mais limpo
- Teste que pega um caso que você não tinha pensado
- Nomenclatura particularmente boa
- Solução criativa para um problema chato

...comente. "Curti essa abstração — fica muito mais legível que a versão anterior."

Especialmente importante quando o autor é júnior e está aprendendo. Saber o que fizeram **certo** é tão pedagógico quanto saber o que erraram.

---

## Estrutura do review (quando é longo)

PRs grandes ou complexos merecem um sumário no topo, não 40 comentários esparsos que o autor tem que costurar.

**Template útil:**

```
## Resumo do review

[1-2 frases sobre o estado geral. Ex: "Aprovo após resolver os blockers; lógica de transfer precisa ser revisitada para concorrência."]

### 🛑 Blockers (precisam resolver antes do merge)
1. [Race condition em transferência - ver comentário no arquivo X]
2. [Falta de tratamento de erro em chamada à API Y]

### ⚠️ Should fix (recomendado, não obrigatório)
1. [N+1 em listagem de posts]
2. [Sem teste para o caminho de cancelamento]

### 💡 Suggestions
- [Nomenclatura de `processData` poderia ser mais específica]
- [Considerar extrair X em hook reutilizável]

### 👍 O que está bom
- [Tratamento de empty states está cuidadoso]
- [Boa cobertura de testes para o happy path]
```

Esse formato permite que o autor entenda imediatamente:
1. Pode mergear depois de quê?
2. O que vai pra próxima sprint?
3. O que é opinião / opcional?
4. O que continuar fazendo?

Para PRs pequenos, basta a parte de blockers + um "LGTM" final no fim.

---

## "LGTM" — quando aprovar

LGTM (Looks Good To Me) é aprovação. Use quando:

- Você revisou todas as linhas atribuídas a você
- Não há blocker pendente
- "Should fix" estão tratados ou explicitamente diferidos

**LGTM com comentários** é prática útil: aprova mas deixa registrado pontos que o autor pode ou não querer abordar antes de mergear. Isso é melhor que reter aprovação por nitpicks.

**O que NÃO é razão para segurar LGTM:**
- Preferência pessoal de estilo que não está no style guide
- "Eu teria feito diferente" sem razão técnica concreta
- "Pode ser melhorado" — quase tudo pode; não é justificativa

---

## Tom em situações difíceis

### Quando o autor é seu chefe ou alguém mais sênior que você

Mesma lógica de qualquer review. Senioridade não imuniza código. Mas tom respeitoso e perguntas funcionam ainda melhor:

> "Posso ter perdido algum contexto, mas aqui parece que `userId` não está validado antes de ser usado em query. Algum motivo específico, ou faltou check de authz?"

### Quando o autor é júnior

Aumente o didatismo sem aumentar a condescendência. Explique o porquê em mais detalhe, link para recursos quando útil, e reconheça quando ele acertou. Pergunte mais — descobrir o que ele estava pensando ensina mais que dizer o que deveria estar pensando.

### Quando você discorda do autor após discussão

Primeiro: você pode estar errado. Releia o argumento dele com mente aberta.

Se ainda discorda:
- Reformule sua preocupação concretamente: o que pode dar errado em que cenário?
- Pergunte como ele resolveria esse cenário
- Se permanecer discórdia, escalonem juntos — pegue um terceiro reviewer, leve para discussão técnica, ou apele à política do time

**Não** segure o PR indefinidamente. **Não** vire questão pessoal. Discordâncias técnicas não resolvidas em review costumam ser sintoma de questão maior (falta de padrão de time, decisão de arquitetura pendente) que precisa ir para outro fórum.

### Quando você é o autor recebendo feedback

A skill é principalmente para reviewers, mas vale notar:

- Resista o impulso de defender. Leia primeiro, responda depois.
- Distinga entre "isso está errado" (revise sua implementação) e "eu teria feito diferente" (opinião — pode ignorar)
- Pergunte ao reviewer quando o feedback não estiver claro. "Você poderia dar um exemplo de como faria isso?" é razoável.
- Agradeça o tempo do reviewer. Não bajulação — só reconhecer que código revisado é melhor que código não revisado.

---

## Anti-padrões a evitar

**Drive-by review.** Comentar em 3 linhas aleatórias sem ler o PR inteiro nem o contexto. Frequentemente acaba sendo pedantia que ignora o problema real.

**Review pedindo "perfeição".** "Perfeito" não existe. A pergunta é: este código é melhor que o que está no main? Continuous improvement, não polimento eterno.

**Review com posicionamento autoritário sem justificativa.** "Isso não é como fazemos aqui" sem explicar por quê e onde está documentado é frustração para o autor (especialmente se ele é novo no time).

**Comentários sarcásticos ou condescendentes.** "Sério que você não testou isso?", "Achei que isso seria óbvio." Mesmo se "engraçado", é tóxico. Custo zero para evitar, custo alto para reparar.

**Bikeshedding.** Gastar mais energia discutindo nomes de variáveis e estilo de chave que discutindo a lógica principal. Sinal de que o reviewer está evitando a parte difícil.

**Approval reflexo.** "LGTM" sem ter olhado. Tira o ponto inteiro do code review e cria culpa cruzada quando bug for para produção.

**Volume sem priorização.** 80 comentários, todos parecendo igualmente importantes. Autor não sabe por onde começar. Sempre indique severidade.

---

## Resumo de uma linha

> Trate o autor como você gostaria de ser tratado revisando código seu — atento, gentil, explicando o porquê, generoso com elogios quando merecidos, firme nos blockers, leve nos nitpicks, e sempre com a mente aberta de que pode estar errado.
