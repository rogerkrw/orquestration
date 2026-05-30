# Security review — OWASP 2025 + práticas de borda

Esta referência foca em segurança da perspectiva de **code reviewer**: o que olhar no diff, que perguntas fazer ao autor, que padrões de código sinalizam risco. Não é um curso de segurança — é o que separa um review que "passa" segredos vazando, IDORs e SSRFs de um review que pega.

Use junto com `bug-patterns-catalog.md` (seção "Autenticação e autorização" e "Validação de input").

---

## A ordem das categorias importa: OWASP Top 10 — 2025

Em 2025 a OWASP reorganizou a lista refletindo o que mais aparece em incidentes reais. A ordem reflete prevalência × impacto, e é a ordem em que reviewers devem priorizar atenção:

1. **A01 — Broken Access Control** (continua #1, é onde a maioria dos bugs reais mora)
2. **A02 — Security Misconfiguration** (subiu pela importância de defaults inseguros)
3. **A03 — Software Supply Chain Failures** (nova: dependências, build, CI/CD)
4. **A04 — Cryptographic Failures**
5. **A05 — Injection** (continua importante, mas ferramentas estão pegando mais)
6. **A06 — Insecure Design**
7. **A07 — Authentication Failures**
8. **A08 — Software and Data Integrity Failures**
9. **A09 — Logging and Monitoring Failures**
10. **A10 — Mishandling of Exceptional Conditions** (nova: fail-open, edge cases mal tratadas)

Pesquisa do Veracode (2026): código gerado por IA tem vulnerabilidade em **45% dos casos**; em Java sobe para **72%**. Ou seja: para qualquer código gerado, a expectativa-base é "tem uma vulnerabilidade até prova contrária". Trate cada PR de IA como input não-confiável de segurança.

---

## A01 — Broken Access Control (a categoria que mais mata)

### O que procurar

**Authorization no lugar errado.** Em qualquer endpoint que aceita ID de recurso, faça mentalmente:

> "Se eu, autenticado como usuário Alice, trocar o ID 42 (que é meu) por ID 43 (que é do Bob), o que acontece?"

Se a resposta é "retorna os dados do Bob", você tem IDOR. A correção certa é **filtrar no nível da query**, não verificar dono depois:

```python
# 🚨 Errado — verifica depois
order = Order.objects.get(id=order_id)
if order.user_id != current_user.id:
    raise Forbidden()

# ✅ Certo — filtra na query
order = Order.objects.filter(id=order_id, user_id=current_user.id).first()
if not order:
    raise NotFound()  # nem revela que existe
```

**Authorization em verbo HTTP errado.** Comum: GET tem checagem, POST/PUT/DELETE da mesma rota não. Ou: rota `/admin/*` tem middleware de auth, mas `/internal/admin-action` (esquecida) não tem.

**Tomar permissão do request.** Se a permissão vem do cliente (`role` no body, scope no JWT que o frontend "enriqueceu", flag em cookie editável) — bug. Permissão vem do servidor, derivada do principal autenticado.

**Vertical privilege escalation.** Endpoint admin acessível por user comum.

**Horizontal privilege escalation.** User acessa dados de outro user no mesmo nível.

**Authorization vs Authentication confundidas.** "Sabe-se quem é" não significa "tem permissão pra isso". Toda ação requer ambos.

### Perguntas para fazer no review

- Onde está a checagem de authz desta rota? (Se não estiver no diff, e não houver middleware óbvio aplicado, *pergunte*.)
- O `userId` que define o escopo vem do contexto autenticado ou do request?
- Há rotas administrativas / internas tocadas? Quem pode acessá-las?
- Se a permissão muda enquanto a sessão está ativa, quando ela é re-checada?

---

## A02 — Security Misconfiguration

### O que procurar

**Defaults expostos.**
- Endpoints `/admin`, `/health`, `/metrics`, `/swagger`, `/debug` acessíveis publicamente
- Credenciais default não trocadas
- Banco de dados / Redis / Elasticsearch escutando em `0.0.0.0` sem firewall

**Headers de segurança ausentes** em respostas HTTP:
- `Content-Security-Policy` (mitiga XSS)
- `Strict-Transport-Security` (força HTTPS)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options` ou `frame-ancestors` no CSP (mitiga clickjacking)
- `Referrer-Policy`

**CORS permissivo.** `Access-Control-Allow-Origin: *` é raramente o que se quer. Combinado com `Allow-Credentials: true`, é um erro grave (e violação da spec). Liste origins explicitamente, ou tenha lógica de validação.

**Cookies sem flags.** Cookies de sessão/auth precisam de:
- `Secure` (só envia em HTTPS)
- `HttpOnly` (JS não acessa)
- `SameSite=Lax` ou `Strict` (mitiga CSRF)

**Mensagens de erro verbosas em produção.** Stack trace, query SQL, path interno no response do cliente em ambiente de produção.

**Verbose logging em produção.** Logando body inteiro do request → tokens, senhas, PII em logs.

**Arquivos de config / .env / dumps acessíveis** via web server.

### Perguntas para fazer

- Esta mudança expõe algum endpoint novo? Está atrás de auth/firewall?
- Variáveis sensíveis estão em env / secret manager, ou em arquivo de config commitado?
- Os headers de segurança estão setados? (Se for API pura, qual é a política de CORS?)

---

## A03 — Software Supply Chain Failures

Categoria explodida em 2025 porque é onde mais ataques estão acontecendo.

### O que procurar

**Adição de dependência nova:**
- É de fonte conhecida e mantida? (download counts, mantenedores ativos, último release)
- Existe versão pinada ou está em `^`/`~`/`*`?
- Foi rodado scan (`npm audit`, `pip-audit`, `snyk`, `dependabot`)?
- A licença é compatível com o projeto?

**Typosquatting.** Pacote com nome similar a um popular (`requestz` vs `requests`, `lodash.utils` vs `lodash`). Comum vetor de ataque.

**Pacote pequeno fazendo coisa grande.** Lib obscura de 50 estrelas executando código no install (npm `postinstall`), tocando filesystem, fazendo network calls. Suspicioso.

**Build pipeline modificado.** Mudanças em CI/CD que rodam comandos arbitrários, baixam scripts do net, usam GitHub Actions de terceiros não pinados por SHA.

**Lockfile não atualizado.** Mudança em `package.json` / `requirements.txt` sem mudança correspondente em `package-lock.json` / `poetry.lock` é sinal de algo errado.

### Perguntas para fazer

- Por que precisamos desta dependência? Não dá pra resolver com stdlib / o que já temos?
- Quão grande é o blast radius se esse mantenedor for comprometido?

---

## A04 — Cryptographic Failures

### O que procurar

**Algoritmo errado para o uso:**
- **Senhas:** apenas bcrypt, scrypt, argon2 com cost adequado. NUNCA MD5/SHA1/SHA256 puro.
- **HMAC:** SHA256+ ok
- **Encriptação simétrica:** AES-GCM ou ChaCha20-Poly1305. NUNCA AES-ECB.
- **Hashing genérico:** SHA256/SHA3-256

**Random não-criptográfico para uso criptográfico.** `Math.random()`, `random.random()` para gerar tokens/IDs/segredos. Use CSPRNG (`crypto.randomBytes`, `secrets`, `SecureRandom`).

**Chaves/IVs hardcoded.** Qualquer constante longa que parece base64/hex no código fonte. Está garantido em git history para sempre.

**IV/nonce reutilizado** em AES-GCM ou similar quebra completamente a segurança. IV deve ser único por mensagem.

**Padding errado.** RSA com PKCS#1 v1.5 quando PKCS#1 v2 (OAEP) está disponível.

**Comparação não-constant-time** de tokens/HMACs/MACs. Use `hmac.compare_digest` / `crypto.timingSafeEqual`.

**TLS verification desligada.** `verify=False`, `rejectUnauthorized: false`, `--insecure`. Em qualquer chamada para serviço externo em produção, é vulnerabilidade.

### Perguntas para fazer

- De onde vêm os bytes aleatórios usados aqui?
- Qual é o threat model — protege contra quem com que capacidade?
- Como rotacionamos esse segredo se ele vazar?

---

## A05 — Injection (continua relevante)

### O que procurar

**Toda concatenação de input do usuário em qualquer linguagem de consulta.**

SQL:
```python
# 🚨
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
# ✅
cursor.execute("SELECT * FROM users WHERE email = %s", [email])
```

ORM raw / fragments:
```js
// 🚨
User.findAll({ where: literal(`email = '${email}'`) })
// ✅
User.findAll({ where: { email } })
```

NoSQL:
```js
// 🚨 — Mongo operator injection
db.users.find({ username, password })  // body: { password: { $ne: null } } 
// ✅ — validate types, ensure password is string
```

Comando shell:
```python
# 🚨
os.system(f"convert {filename} out.png")
# ✅
subprocess.run(["convert", filename, "out.png"], shell=False)
```

LDAP / XPath / template engines — mesma lógica.

**XSS:**
- `innerHTML = userInput` ou equivalentes (`dangerouslySetInnerHTML` em React)
- Server-side template rendering input sem escape
- Reflexão de query string em HTML sem encoding
- `eval` ou `new Function(userInput)`

**SSRF.** Endpoint que aceita URL/host do usuário e faz request. Sem allowlist → atacante bate em `169.254.169.254` (cloud metadata), serviços internos, file://.

**Open redirect.** Redirecionar para URL vinda de query string sem validar contra allowlist. Ferramenta de phishing.

### Perguntas para fazer

- Esse input vem do usuário (direta ou indiretamente)?
- Onde ele acaba sendo interpretado (DB, shell, HTML, URL)?
- Estamos usando parameterização / escape do framework?

---

## A07 — Authentication Failures

### O que procurar

**Validação de senha fraca.** Sem regras de tamanho mínimo, sem checagem contra senhas comuns (haveibeenpwned-style), sem MFA opcional.

**Login que diferencia "usuário não existe" de "senha errada".** Permite enumeração de usuários. Sempre retorne erro genérico.

**Sem rate limiting em endpoints de autenticação.** Brute force trivial.

**Sessão sem expiração / sem invalidação on logout.** Logout do front que não invalida no back é segurança performática.

**Tokens em URL.** `?token=...` aparece em logs de servidor, referrers, histórico de browser.

**Reset de senha por email sem token tempo-limitado.** Tokens precisam expirar (15-60 min é razoável) e ser de uso único.

**MFA bypass.** Endpoint que ignora MFA (ex: "remember device" mal feito, MFA só no primeiro login).

### Perguntas para fazer

- Quanto tempo dura uma sessão? E um token JWT?
- Como invalidamos uma sessão se ela vazar?
- Existe MFA? É contornável?

---

## A09 / A10 — Logging Failures + Mishandling of Exceptional Conditions

### O que procurar

**Logging insuficiente em eventos de segurança:**
- Falhas de login não são logadas → não dá pra detectar brute force
- Mudanças de privilégio não são auditadas
- Acessos negados não são correlacionáveis

**Logging excessivo de dados sensíveis:**
- Senha em log (mesmo "só na falha", em texto plano)
- Token de auth em log
- PII (CPF, email, telefone) em logs operacionais

**Fail-open em vez de fail-closed.** Quando a checagem de segurança falha por erro técnico (ex: serviço de autz indisponível), o sistema permite a operação em vez de bloquear. Em segurança, *fail closed* é o default seguro.

```python
# 🚨 Fail open
try:
    is_allowed = check_permission(user, resource)
except Exception:
    is_allowed = True  # "fail safe"... não, fail aberto

# ✅ Fail closed
try:
    is_allowed = check_permission(user, resource)
except Exception as e:
    logger.error("Permission check failed", exc_info=True)
    is_allowed = False
```

**Edge case não testada vira vulnerabilidade.** A categoria A10 nova de 2025 é exatamente isso: atacantes exploram caminhos de erro mal modelados. Toda branch de exceção é superfície de ataque.

### Perguntas para fazer

- Se a checagem de autz cair, o que acontece com a requisição?
- Logs deste fluxo registram eventos de segurança relevantes?
- Algum log tem chance de capturar dados sensíveis?

---

## Checklist condensado para usar no review

Cole essas perguntas mentais ao olhar diff que toca qualquer área sensível:

```
Auth/Authz
  [ ] Endpoint tem autenticação? E autorização?
  [ ] Authz filtra pelo dono na query, não compara depois?
  [ ] Trocar o ID no path/body acessa dados de outro user?

Input
  [ ] Todo input externo é validado no backend (não só no front)?
  [ ] Allowlist de campos no body (sem mass assignment)?
  [ ] Concatenação em SQL/shell/HTML está parameterizada?
  [ ] Há rate limiting onde faz sentido (login, signup, etc)?

Segredos / Crypto
  [ ] Sem segredos hardcoded no diff?
  [ ] Algoritmo de hash/encryption apropriado para o uso?
  [ ] Random vem de CSPRNG quando usado para segurança?
  [ ] TLS verification ligado em todas as chamadas externas?

Config
  [ ] Endpoints novos estão atrás de auth/firewall conforme política?
  [ ] Cookies de sessão têm Secure + HttpOnly + SameSite?
  [ ] CORS é restrito a origins necessários?
  [ ] Erro retornado ao cliente não vaza stack/schema?

Supply chain
  [ ] Dependência nova é confiável e necessária?
  [ ] Lockfile atualizado?
  [ ] Build/CI não roda código de terceiro não-confiável?

Logs
  [ ] Eventos de segurança são logados?
  [ ] Logs não capturam senha/token/PII?
  [ ] Fail-closed em checagens de segurança quando há erro?
```
