---
name: browser-e2e-testing
description: Verifica fluxos reais de aplicações web no navegador, incluindo lifecycle do servidor, interação, estados visuais e erros de integração. Use para validar jornadas de usuário, UI ou rotas web; não substitui testes unitários ou de API.
---

# Browser E2E Testing

Teste o que o usuário consegue fazer no navegador, atravessando a aplicação real e seus boundaries. Prefira o runner, fixtures e comandos já existentes no projeto.

## Preparação

1. Leia a especificação, critérios de aceite e implementação relevante. Identifique a jornada e o estado esperado em cada etapa.
2. Detecte o stack e o runner existentes: Playwright/Vitest no TypeScript ou Playwright/pytest no Python. Não introduza dependência ou configuração nova sem necessidade e escopo. Em projetos TypeScript novos, prefira Node 24 LTS; confirme a compatibilidade das versões instaladas de Playwright/Vitest com o Node e o Vite do projeto.
3. Use ambiente local ou de teste isolado. Descubra o comando de start, URLs, portas, autenticação de teste, seed e teardown. Nunca use credenciais ou dados de produção.
4. Inicie os servidores pelo mecanismo do projeto e espere um sinal de prontidão real. Não substitua espera explícita por `sleep` arbitrário.

## Execução

- Faça uma inspeção inicial da página e da árvore de acessibilidade antes de interagir. Use seletores estáveis e orientados ao papel, nome ou contrato público.
- Cubra primeiro o caminho feliz. Depois teste pelo menos o estado vazio, carregamento, erro e uma fronteira relevante da jornada.
- Aguarde sinais observáveis: elemento visível, resposta específica, mudança de URL, estado acessível ou mensagem de erro. Não dependa de timing acidental.
- Verifique resultado do ponto de vista do usuário: conteúdo, foco, navegação, persistência, feedback e ausência de erros de console/rede relevantes.
- Capture screenshot, trace, console ou HTML somente quando ajudarem a reproduzir ou explicar a falha; salve em local de artefatos do projeto e redija dados sensíveis.
- Limpe dados e processos ao final. Uma execução repetida deve produzir o mesmo resultado sem depender da ordem de outra.

## Limites

- E2E não prova regras internas, cobertura completa da API ou qualidade de dados além do fluxo exercitado.
- Não corrija código de produto em nome do teste. O `qa-tester` pode alterar testes, fixtures e configuração de teste; `swe-frontend` pode corrigir a camada de apresentação quando isso estiver no escopo.
- Se o fluxo não puder ser executado por falta de servidor, fixture, credencial de teste ou seletor estável, reporte o bloqueio e a menor condição necessária para continuar.

## Saída

Reporte jornada e ambiente, comando executado, resultado por cenário, artefatos de falha, erros de console/rede, cobertura não exercitada e condição de reprodução. Separe falha do produto, falha do teste e falha do ambiente.
