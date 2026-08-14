# `templates/` — bootstrap de projeto novo

Três arquivos montam o `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` de qualquer projeto novo do TPM:

| Arquivo | O que contém | Muda quando |
| --- | --- | --- |
| `BASE.md` | Comum a todo projeto: responsáveis, processo, autonomia, verificação, timestamps, git, idiomas, comunicação, documentação | A regra vale para Python e TypeScript, `min` e `max` |
| `py.md` | Stack Python, nos perfis `min` e `max` | A regra depende da stack ou do perfil |
| `ts.md` | Stack TypeScript, nos perfis `min` e `max` | idem |

A divisão existe para que uma regra geral seja editada **em um lugar só**. Antes disso os quatro templates duplicavam ~60% do texto, e a correção nunca era aplicada nas quatro cópias — a pasta de trabalho local chegou a se chamar `others/`, `oth/` e `xyz/` ao mesmo tempo, em arquivos que deveriam concordar.

## Perfis

- **`min`** — descoberta e experimentação. Estrutura enxuta (um pacote/app + `xyz/`), UI dentro do próprio código quando houver, persistência progressiva, testes por demanda.
- **`max`** — projeto profissional ou de terceiro. `api/` + `web/` + `docker/` + `xyz/`, TDD, migrations, gates completos, deploy esperado.

Na dúvida, começar em `min`. Cada arquivo de stack abre com uma tabela de escolha e os gatilhos de promoção `min` → `max`.

## Montar o arquivo de um projeto novo

1. Escolher stack (`py.md` ou `ts.md`) e perfil (`min` ou `max`).
2. Concatenar `BASE.md` + as seções do perfil escolhido, nesta ordem:
   - cabeçalho, precedência, "Por onde começar", Responsáveis, Visão/Objetivos/Funcionamento — do `BASE.md`
   - Stack Técnica, Arquitetura Base, Agentes e Skills — do arquivo de stack
   - Processo, Delegação, Regras, Protocolo de Documentação — do `BASE.md`
   - Regras específicas do perfil, Gotchas, Evals — do arquivo de stack
3. Remover os comentários `<!-- ... -->` de instrução e a tabela "Escolha do perfil".
4. Preencher os placeholders `[Nome do Produto]`, `[Descrever...]` e o nome real do pacote.
5. Copiar o resultado para `CLAUDE.md`, `AGENTS.md` e `GEMINI.md` do projeto (`cp`, para os três ficarem idênticos).

O resultado é um arquivo único e autocontido: o projeto novo não sabe que existiu concatenação, e não carrega condicional de perfil que não se aplica a ele.

## Onde colocar uma regra nova

A pergunta é uma só: **a regra depende da stack ou do perfil?**

- **Não depende** → `BASE.md`. Exemplos: como reportar ao TPM, timestamp por `date`, precedência de contexto, idioma dos comentários, quando consultar antes de decidir.
- **Depende da stack** → `py.md` ou `ts.md`, nos dois perfis. Exemplos: comando de gate, alias de import, ORM.
- **Depende do perfil** → só na seção daquele perfil. Exemplos: TDD obrigatório (`max`), testes por demanda (`min`).

Regra que acabou em `py.md` e em `ts.md` com o mesmo texto pertence ao `BASE.md`. É o sinal de que a divisão está se perdendo — foi assim que a duplicação anterior começou.

## Ao editar

- **Registro neutro.** Regra declarada, motivo em uma linha quando não for óbvio. Sem ênfase acumulada, sem "obrigatório"/"não negociável"/"é essencial", sem negrito em frase inteira. O template é lido por um agente que executa; adjetivo não muda a execução e gasta contexto.
- **Uma regra, um lugar.** Repetir a mesma regra em duas seções faz as duas divergirem na próxima edição.
- **Regra com evidência vale mais que regra afirmada.** Havendo medição que a sustente, anotar em meia linha.
- **Sem data que envelhece** no corpo do template — o projeto que nascer dele vai carregar a data para sempre. Versão de dependência é exceção (`>=2.13`).
- **`xyz/` é o nome canônico** da pasta local gitignored, nos dois stacks e nos dois perfis. Não reintroduzir `others/` nem `oth/`.
- Marcadores de lista com `-`, tabelas com espaço dentro dos pipes, linha em branco cercando listas e tabelas, uma frase por linha lógica (sem hard-wrap).

## Manutenção

Estes templates não são sincronizados por `scripts/sync.sh` — são consultados aqui, em `~/dev/orquestration/templates/`. O que aponta para eles:

- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` e `README.md` deste repositório
- os configs globais dos CLIs (`~/.claude/CLAUDE.md` e equivalentes), que instruem os agentes a consultá-los ao iniciar projeto novo

Ao renomear ou dividir um template, atualizar esses ponteiros na mesma mudança — ponteiro órfão faz o agente procurar um arquivo que não existe e seguir sem template.

Mudança aqui afeta todo projeto criado daqui para a frente, mas **não** os já existentes: projeto que já tem o seu `CLAUDE.md` não recebe atualização retroativa. Regra que precise valer para os projetos em andamento tem de ser levada a cada um deles à mão.

## Registrar a mudança

Editou template → entrada no `CHANGELOG.md` da raiz, na seção da data corrente, descrevendo o que muda para quem for criar um projeto novo. Commit junto com a edição.
