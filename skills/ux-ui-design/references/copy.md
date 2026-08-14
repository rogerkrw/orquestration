# Microcopy — texto de interface

Palavras na interface existem para tornar o uso mais fácil. São material de design, não decoração. A mesma intencionalidade aplicada a espaçamento e cor se aplica ao texto.

## Princípios

1. **Claro** — dizer exatamente o que se quer dizer, sem jargão nem ambiguidade.
2. **Conciso** — o menor número de palavras que transmite o sentido inteiro.
3. **Consistente** — o mesmo termo para a mesma coisa, em toda parte.
4. **Útil** — cada palavra ajuda a pessoa a concluir o que veio fazer.
5. **Humano** — escrever como alguém prestativo, não como sistema.

**Nomear pelo que a pessoa controla**, nunca pela implementação: "notificações", não "configuração de webhook"; "cobrança", não "billing service".

**Voz ativa, dizendo o que acontece.** O verbo do botão se mantém pelo fluxo inteiro: botão "Publicar" → toast "Publicado" → histórico "Publicado em…". Vocabulário de interface é sinalização; consistência é como a pessoa aprende a se mover.

**Cada elemento faz um trabalho.** Rótulo rotula, exemplo demonstra, ajuda explica. Nada acumula função em silêncio.

## Padrões por contexto

### CTA / botão

- Começar por verbo, específico ao resultado: "Criar conta", "Salvar alterações", "Baixar relatório"
- Nunca genérico: "Enviar", "Continuar", "OK" — não dizem o que vai acontecer
- O rótulo descreve o resultado, não a mecânica

### Mensagem de erro

Estrutura: **o que aconteceu + por quê + como resolver.**

> "Pagamento recusado. O banco emissor não autorizou a transação. Tente outro cartão ou entre em contato com seu banco."

- Erro não pede desculpa e não é vago ("Algo deu errado" não é mensagem de erro)
- Erro de campo aparece junto ao campo, não só no topo
- Falar na voz da interface, não na primeira pessoa

### Estado vazio

Estrutura: **o que é + por que está vazio + como começar.**

> "Nenhum projeto ainda. Crie o primeiro para começar a organizar seu trabalho."

Estado vazio é convite à ação — não é lugar para ilustração melancólica nem para "nada por aqui".

### Confirmação

- Nomear a ação e o alvo: "Excluir 3 arquivos?" em vez de "Tem certeza?"
- Declarar a consequência: "Isso não pode ser desfeito."
- Botões nomeiam o que fazem: "Excluir arquivos" / "Manter arquivos" — nunca "OK" / "Cancelar"
- Ação destrutiva: confirmação ou janela de desfazer, nunca execução imediata

### Estado de carregamento

Reduzir ansiedade e ajustar expectativa. Terminar com `…`: "Carregando…", "Salvando…". Para espera longa, dizer o que está acontecendo ou quanto falta.

### Tooltip

Conciso e útil. Tooltip que repete o rótulo visível é ruído.

### Onboarding

Revelação progressiva, um conceito por vez. Não explicar o que a interface já mostra.

## Tom por contexto

| Contexto | Tom |
| --- | --- |
| Sucesso | Comemorativo sem exagero |
| Erro | Empático e prático |
| Aviso | Direto e acionável |
| Neutro | Informativo e curto |

Registro conversacional e ajustado: verbos simples, sem enchimento, tom calibrado à marca e ao público.

## Ao revisar copy

Entregar a recomendação, 2-3 alternativas com o tom de cada uma, e a justificativa ligada ao contexto da pessoa — não à preferência de quem escreve.

## Convenções em português

Ver `pt-br.md`. Em resumo, duas divergem da literatura em inglês:

- **Não usar Title Case.** Em português, título e botão vão em frase capitalizada: "Salvar alterações", não "Salvar Alterações".
- **Segunda pessoa implícita.** "Crie sua conta" em vez de "Você deve criar sua conta"; evitar "nós" ("Nós enviamos um e-mail" → "Enviamos um e-mail").
