# MBA IA — Skill de Auditoria e Refatoração Arquitetural

Repositório do desafio de criação de uma skill para **auditar**, **relatar** e **refatorar** projetos legados para o padrão **MVC**, com foco em Python/Flask e Node.js/Express.

A skill foi construída uma vez dentro de `code-smells-project/.claude/skills/refactor-arch/` e copiada sem modificações para os outros dois projetos, comprovando que é agnóstica de tecnologia.

## Objetivo do desafio

A proposta foi construir uma skill capaz de:

- detectar linguagem, framework e arquitetura atual da codebase;
- identificar anti-patterns e code smells com severidade, arquivo e linhas exatas;
- gerar um relatório estruturado de auditoria;
- refatorar o projeto para o padrão MVC;
- validar que a aplicação continua funcionando após as mudanças.

O desafio exige que a skill funcione nos **3 projetos fornecidos**: dois em **Python/Flask** e um em **Node.js/Express**.

## Estrutura do repositório

```text
mba-ia-refactor-projects-skill/
├── README.md
├── code-smells-project/
│   ├── .claude/skills/refactor-arch/
│   ├── reports/audit-project-1.md
│   ├── app.py · config.py · database.py
│   ├── controllers/  models/  routes/  services/  middlewares/
│   └── requirements.txt
├── ecommerce-api-legacy/
│   ├── .claude/skills/refactor-arch/
│   ├── reports/audit-project-2.md
│   ├── api.http · package.json
│   └── src/
│       ├── app.js · database.js
│       ├── config/  controllers/  models/  routes/  services/  middlewares/
├── task-manager-api/
│   ├── .claude/skills/refactor-arch/
│   ├── reports/audit-project-3.md
│   ├── app.py · config.py · database.py · seed.py
│   ├── controllers/  models/  routes/  services/  middlewares/  utils/
│   └── requirements.txt
```

> Os relatórios estão dentro da pasta `reports/` de cada projeto, conforme o caminho usado pela skill durante a execução.

## Tecnologias e ferramenta escolhida

- **Ferramenta:** Claude Code
- **Recurso utilizado:** Custom Skills
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask e Node.js/Express

A execução foi feita com o comando `claude "/refactor-arch"` em cada projeto, com confirmação humana entre as fases 2 e 3.

---

# Análise Manual

Antes de criar a skill, o desafio exige a leitura manual dos 3 projetos e o registro de, no mínimo, **5 problemas por projeto**, com pelo menos **1 CRITICAL ou HIGH**, **2 MEDIUM** e **2 LOW**. Esta seção documenta essa etapa e serviu de base para a construção do catálogo de anti-patterns e do playbook de refatoração.

## Projeto 1 — `code-smells-project` (Python/Flask — API de E-commerce)

**Stack:** Python · Flask 3.1.1 · `flask-cors` · SQLite raw  
**Domínio:** E-commerce (produtos, usuários, pedidos, relatórios de vendas)  
**Arquitetura atual:** pseudo-MVC flat — `app.py` concentra bootstrap e rotas; `controllers.py` contém handlers HTTP; `models.py` mistura acesso a dados com regras de negócio; `database.py` mantém conexão global.

| # | Severidade | Problema | Arquivo | Linhas |
|---|---|---|---|---|
| 1 | CRITICAL | SQL Injection em múltiplas queries construídas por concatenação de strings | `models.py` | 28, 47–49, 57–61, 68, 92, 110, 126–128, 140, 149–150, 155–165, 174, 280–281, 291–297 |
| 2 | CRITICAL | Endpoint `/admin/query` executa SQL arbitrário recebido no body sem autenticação | `app.py` | 59–78 |
| 3 | CRITICAL | Senhas em texto plano e `SECRET_KEY` hardcoded exposta no health check | `models.py`, `database.py`, `controllers.py` | `models.py:128`, `database.py:76–83`, `controllers.py:287–289` |
| 4 | HIGH | Regra de negócio de pedido e estoque implementada na camada de dados | `models.py` | 133–169 |
| 5 | HIGH | Endpoint `/admin/reset-db` apaga tabelas sem autenticação/autorização | `app.py` | 47–57 |
| 6 | MEDIUM | N+1 queries na listagem de pedidos com cursores aninhados | `models.py` | 171–201, 203–233 |
| 7 | MEDIUM | Validação duplicada entre criação e atualização de produto | `controllers.py` | 28–55, 73–85 |
| 8 | MEDIUM | Conexão SQLite global mutável, com risco em cenários concorrentes | `database.py` | 4–10 |
| 9 | LOW | Uso de `print()` como logging operacional | `controllers.py` | 8, 57, 106, 161, 179, 208–210, 219, 248–250 |
| 10 | LOW | Serialização de rows repetida manualmente sem abstração central | `models.py` | 10–21, 31–40, 79–86, 95–102 |

**Resumo por severidade:** 3 CRITICAL · 2 HIGH · 3 MEDIUM · 2 LOW

**Justificativa de relevância:** este projeto expõe os padrões mais críticos que a skill precisava detectar automaticamente: SQL Injection por concatenação, operações destrutivas sem autenticação, segredo hardcoded e mistura de responsabilidades incompatível com MVC.

## Projeto 2 — `ecommerce-api-legacy` (Node.js/Express — LMS API com checkout)

**Stack:** Node.js · Express 4.18.2 · `sqlite3` 5.1.6 · sem ORM  
**Domínio:** LMS / checkout (cursos, matrículas, pagamentos, usuários)  
**Arquitetura atual:** God Object — `AppManager.js` concentra roteamento, acesso a dados, lógica de checkout, auditoria e resposta HTTP.

| # | Severidade | Problema | Arquivo | Linhas |
|---|---|---|---|---|
| 1 | CRITICAL | Credenciais de produção hardcoded (`pk_live`, senha de DB e SMTP) | `utils.js` | 1–7 |
| 2 | CRITICAL | Criptografia customizada insegura com base64 (`badCrypto`) | `utils.js` | 17–23 |
| 3 | CRITICAL | Banco em memória (`:memory:`), com perda total de dados a cada restart | `AppManager.js` | 7 |
| 4 | CRITICAL | God Object sem separação de responsabilidades | `AppManager.js` | 1–141 |
| 5 | HIGH | Aprovação de pagamento por prefixo de cartão e logging de dado sensível | `AppManager.js` | 44–48 |
| 6 | HIGH | Callback hell de múltiplos níveis no checkout | `AppManager.js` | 36–78 |
| 7 | HIGH | Exclusão de usuário sem cascade, com risco de dados órfãos | `AppManager.js` | 131–137 |
| 8 | MEDIUM | Cache global mutável sem TTL e compartilhado entre requisições | `utils.js` | 9, 12–15 |
| 9 | MEDIUM | `totalRevenue` declarado mas não utilizado — código morto | `utils.js` | 10, 25 |
| 10 | LOW | Variáveis de payload sem semântica (`u`, `e`, `p`, `cid`, `cc`) | `AppManager.js` | 29–34 |
| 11 | LOW | Erro de DELETE não tratado antes de retornar sucesso | `AppManager.js` | 132–136 |

**Resumo por severidade:** 4 CRITICAL · 3 HIGH · 2 MEDIUM · 2 LOW

**Justificativa de relevância:** este projeto é o melhor exemplo de violação arquitetural grave em Node.js/Express. Ele foi essencial para garantir que a skill não ficasse acoplada a Flask e conseguisse detectar God Object, secrets hardcoded, callback hell e banco em memória.

## Projeto 3 — `task-manager-api` (Python/Flask — API de Task Manager)

**Stack:** Python · Flask 3.0.0 · Flask-SQLAlchemy 3.1.1 · `flask-cors` · `marshmallow` instalado e não usado · `python-dotenv` instalado e não conectado  
**Domínio:** Task manager (tarefas, usuários, categorias, relatórios)  
**Arquitetura atual:** MVC incompleto — a estrutura de pastas existe, mas há problemas de segurança, duplicação e regras mal distribuídas entre rotas, models e services.

| # | Severidade | Problema | Arquivo | Linhas |
|---|---|---|---|---|
| 1 | CRITICAL | Senhas hasheadas com MD5 sem salt | `models/user.py` | 27–32 |
| 2 | CRITICAL | Credenciais de email hardcoded no serviço de notificação | `services/notification_service.py` | 8–10 |
| 3 | CRITICAL | Token fake e previsível por concatenação de string | `routes/user_routes.py` | 210 |
| 4 | HIGH | Hash da senha exposto no `to_dict()` de usuário | `models/user.py` | 16–25 |
| 5 | HIGH | Lógica `is_overdue` duplicada em múltiplos pontos e método do model ignorado | `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py`, `models/task.py` | `task_routes.py:30–39,71–80,171–181,284–288` · `report_routes.py:33–44,131–135` · `task.py:50–60` |
| 6 | HIGH | N+1 queries no relatório de produtividade | `routes/report_routes.py` | 53–68 |
| 7 | MEDIUM | Helpers e constantes definidos mas ignorados pelas rotas, que repetem lógica inline | `utils/helpers.py`, `routes/task_routes.py`, `routes/user_routes.py` | `helpers.py:19–23,57–116,110–116` |
| 8 | MEDIUM | `SECRET_KEY` hardcoded com `python-dotenv` instalado mas não utilizado | `app.py` | 13 |
| 9 | LOW | Imports não utilizados em múltiplos arquivos | `routes/task_routes.py`, `routes/user_routes.py`, `utils/helpers.py` | `task_routes.py:7` · `user_routes.py:6` · `helpers.py:1–8` |
| 10 | LOW | Serialização manual duplicada mesmo com `task.to_dict()` disponível | `routes/task_routes.py`, `routes/user_routes.py` | `task_routes.py:16–58` · `user_routes.py:161–182` |

**Resumo por severidade:** 3 CRITICAL · 3 HIGH · 2 MEDIUM · 2 LOW

**Justificativa de relevância:** este projeto mostrou que uma estrutura de pastas aparentemente organizada não significa arquitetura saudável. Isso influenciou diretamente as heurísticas da skill para que a análise não fosse superficial nem baseada apenas no nome dos diretórios.

---

# Construção da Skill

O desafio exige um `SKILL.md` com 3 fases sequenciais e arquivos de referência em Markdown cobrindo: análise de projeto, catálogo de anti-patterns, template de relatório, guidelines de arquitetura e playbook de refatoração. Esta skill foi estruturada exatamente com esse objetivo.

## Estrutura da skill

```text
.claude/skills/refactor-arch/
├── SKILL.md
├── analysis-heuristics.md
├── anti-patterns-catalog.md
├── audit-report-template.md
├── mvc-architecture.md
└── refactoring-playbook.md
```

## Decisões de design

### 1. Fluxo em 3 fases

O `SKILL.md` foi escrito com três fases fixas:

- **Fase 1 — Análise:** detectar stack, entry point, padrão arquitetural, dependências e domínio;
- **Fase 2 — Auditoria:** inspecionar a codebase com base no catálogo, gerar relatório estruturado, salvar o relatório e pedir confirmação;
- **Fase 3 — Refatoração:** aplicar o playbook, reorganizar a estrutura para MVC e validar a aplicação com boot + teste de endpoints.

Essa divisão replica o fluxo exigido no enunciado e reduz o risco de a skill modificar arquivos cedo demais. A pausa antes da Fase 3 foi mantida como regra obrigatória.

### 2. Heurísticas orientadas por evidência

A skill não depende apenas do nome dos arquivos. As heurísticas consideram:

- presença de `requirements.txt`, `package.json`, `Pipfile`, `pyproject.toml`, `yarn.lock`;
- imports e assinaturas de framework (`from flask import`, `require('express')`, etc.);
- sinais de acesso a banco (`sqlite3.connect`, `Database(':memory:')`, SQLAlchemy);
- análise de entry point (`app.run`, `app.listen`, `if __name__ == '__main__'`);
- inferência de domínio por tabelas, rotas e nomes de entidades.

Isso foi importante para funcionar tanto em projeto flat quanto em projeto parcialmente organizado.

### 3. Catálogo amplo e distribuído por severidade

O catálogo foi montado com foco nas falhas que apareceram na análise manual e no que o desafio exige. A versão atual contempla **15 anti-patterns**, distribuídos entre `CRITICAL`, `HIGH`, `MEDIUM` e `LOW`, incluindo **detecção de API deprecated**. Entre os principais:

- SQL Injection via concatenação;
- hardcoded credentials / secrets;
- armazenamento inseguro de senha;
- God Object / ausência de separação de responsabilidades;
- endpoint destrutivo sem autenticação;
- regra de negócio fora da service layer;
- dados sensíveis expostos em response;
- token fake ou previsível;
- N+1 queries;
- validação duplicada;
- estado global mutável;
- banco em memória;
- uso de `Query.get()` do SQLAlchemy 2.x;
- logging não estruturado;
- imports não utilizados.

### 4. Playbook orientado a transformação concreta

O playbook foi desenhado para sair de anti-pattern detectado para ação corretiva executável. A versão atual contém **11 padrões de transformação** com exemplos **before/after**, incluindo:

- parameterized queries;
- extração de config para env vars;
- hash seguro de senha;
- quebra de God Object em camadas;
- serialização pública sem campos sensíveis;
- correção de N+1;
- validação centralizada;
- substituição de API deprecated;
- logging estruturado;
- conversão de callback hell para `async/await`;
- troca de banco em memória por persistência real.

### 5. Agnosticismo de tecnologia no escopo do desafio

A skill foi feita para ser agnóstica **dentro do escopo do desafio**, ou seja, funcionar corretamente nos 3 projetos fornecidos, mesmo com stacks e níveis de organização diferentes. A refatoração-alvo cobre explicitamente:

- **Python / Flask**
- **Node.js / Express**

A análise de stack também inclui sinais adicionais de outras tecnologias, mas o foco de conformidade foi mantido nos projetos exigidos pelo enunciado. A skill foi criada uma vez no Projeto 1 e copiada sem alterações para os Projetos 2 e 3 — o agnosticismo foi validado por uso, não apenas por documentação.

### 6. Execução manual e controle humano

O uso previsto da skill é por invocação manual com:

```bash
claude "/refactor-arch"
```

O desafio não exige explicitamente que a skill seja "manual only" por metadata, mas exige execução manual por comando no fluxo de uso e confirmação antes de qualquer modificação. Por isso, o comportamento documentado foi mantido como execução explícita + pausa obrigatória na Fase 2.

## Desafios encontrados e como foram tratados

### Projeto flat vs. projeto parcialmente organizado

O maior desafio foi evitar que a skill confundisse "existem pastas" com "a arquitetura está correta". Isso foi tratado cruzando estrutura de diretórios com o conteúdo real dos arquivos: a skill abre as rotas, os models e os services e verifica se a separação de responsabilidades é real (lógica no service, persistência no model, etc.) ou se as pastas são apenas nominais. No Projeto 3, isso foi decisivo para detectar duplicação inline da lógica `is_overdue` mesmo com o método já existindo no model.

### Segurança e arquitetura na mesma skill

Outro desafio foi equilibrar auditoria arquitetural com problemas de segurança. A solução foi manter ambos no catálogo e classificar com base na escala de severidade do desafio: SQL Injection, credenciais hardcoded, MD5 sem salt e endpoints destrutivos sem autenticação foram classificados como `CRITICAL` por serem riscos imediatos, enquanto problemas estruturais como N+1 e duplicação ficaram em `MEDIUM`.

### Validação prática da Fase 3

Para ficar mais aderente ao enunciado, a skill foi ajustada para:

- salvar o relatório em `reports/audit-project-{1,2,3}.md` dentro de cada projeto;
- testar **todos os endpoints detectados** na Fase 1, e não apenas um endpoint por domínio;
- documentar no resumo final os status HTTP validados.

---

# Resultados

## Resumo dos relatórios de auditoria

A execução real da skill nos 3 projetos gerou os seguintes números, extraídos diretamente dos relatórios em `reports/audit-project-{1,2,3}.md`:

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---:|---:|---:|---:|---:|---|
| `code-smells-project` | 4 | 3 | 3 | 2 | **12** | `code-smells-project/reports/audit-project-1.md` |
| `ecommerce-api-legacy` | 4 | 2 | 3 | 2 | **11** | `ecommerce-api-legacy/reports/audit-project-2.md` |
| `task-manager-api` | 3 | 3 | 3 | 3 | **12** | `task-manager-api/reports/audit-project-3.md` |
| **Totais** | **11** | **8** | **9** | **7** | **35** | — |

Todos os 3 relatórios atendem aos critérios mínimos do desafio: ≥ 5 findings, com pelo menos 1 CRITICAL ou HIGH em cada projeto, ordenados por severidade decrescente, com arquivo e linhas exatos em cada finding.

### Principais findings por projeto

**Projeto 1 — `code-smells-project`:** SQL Injection em todas as queries da camada de dados, secrets e seed em texto plano, senhas armazenadas em texto plano, endpoints administrativos públicos (`/admin/reset-db`, `/admin/query`), regras de negócio dentro de `models.py`, exposição de senha em respostas e exposição da `SECRET_KEY` no `/health`, login sem token, N+1 em listagem de pedidos, validações duplicadas, conexão SQLite global, `print()` como logger e import não usado.

**Projeto 2 — `ecommerce-api-legacy`:** credenciais de produção hardcoded (`pk_live_*`, senha de DB e SMTP), `badCrypto` substituindo hash real, `:memory:` como banco, God Object em `AppManager.js`, lógica de aprovação de pagamento dentro de rota, endpoint financeiro administrativo sem autenticação, N+1 no relatório financeiro, cache global mutável, `:memory:` causando perda de dados a cada restart, `console.log` expondo cartão de crédito e import não usado.

**Projeto 3 — `task-manager-api`:** MD5 sem salt para senha, `SECRET_KEY` e SMTP hardcoded com `python-dotenv` instalado mas não conectado, todas as rotas destrutivas (DELETE) sem autenticação, hash da senha exposto via `to_dict()`, token fake `'fake-jwt-token-' + str(user.id)`, `is_overdue` duplicado em 5 lugares com método do model ignorado, N+1 em `GET /tasks` e `/reports/summary`, constantes redefinidas inline, `Query.get()` deprecated em todo o código (API deprecated detectada), `print()` como logger e imports não usados.

## Comparação antes/depois

### Projeto 1 — `code-smells-project`

**Antes:** 4 arquivos planos na raiz — `app.py`, `controllers.py`, `models.py`, `database.py`. Tudo misturado: rotas, handlers HTTP, regras de negócio, queries SQL concatenadas e conexão global.

**Depois:** estrutura MVC com camadas explícitas:

```text
code-smells-project/
├── app.py                           # composition root
├── config.py                        # config carregando env vars
├── database.py
├── controllers/                     # orquestração HTTP
│   ├── pedido_controller.py
│   ├── produto_controller.py
│   └── usuario_controller.py
├── models/                          # acesso a dados por domínio
│   ├── pedido_model.py
│   ├── produto_model.py
│   └── usuario_model.py
├── routes/                          # registro de rotas (blueprints)
│   ├── admin_routes.py
│   ├── main_routes.py
│   ├── pedido_routes.py
│   ├── produto_routes.py
│   └── usuario_routes.py
├── services/                        # regras de negócio
│   ├── pedido_service.py
│   ├── produto_service.py
│   └── usuario_service.py
├── middlewares/error_handler.py     # error handler centralizado
└── reports/audit-project-1.md
```

**Principais correções aplicadas:** parameterização de todas as queries (PT-01), extração de `SECRET_KEY` para env (PT-02), separação de regras de negócio em `services/` (PT-04), models reduzidos a acesso a dados, error handler centralizado em middleware, blueprints separando o roteamento.

### Projeto 2 — `ecommerce-api-legacy`

**Antes:** 3 arquivos JS em `src/` — `app.js`, `AppManager.js` (God Object com 141 linhas concentrando rotas + queries + checkout + pagamento + auditoria), `utils.js` (com credenciais hardcoded e `badCrypto`). Banco SQLite em `:memory:`.

**Depois:** estrutura MVC em camadas, com `AppManager.js` decomposto e persistência em arquivo:

```text
ecommerce-api-legacy/
├── api.http
├── data/                            # persistência em arquivo (não :memory:)
├── package.json
├── reports/audit-project-2.md
└── src/
    ├── app.js                       # composition root
    ├── config/settings.js           # config + env vars
    ├── database.js
    ├── controllers/
    │   ├── checkoutController.js
    │   ├── reportController.js
    │   └── userController.js
    ├── models/
    │   ├── auditModel.js
    │   ├── courseModel.js
    │   ├── enrollmentModel.js
    │   ├── paymentModel.js
    │   └── userModel.js
    ├── routes/
    │   ├── adminRoutes.js
    │   ├── checkoutRoutes.js
    │   └── userRoutes.js
    ├── services/
    │   ├── checkoutService.js
    │   ├── reportService.js
    │   └── userService.js
    └── middlewares/
        ├── authMiddleware.js        # autenticação para /admin
        ├── errorHandler.js
        └── logger.js
```

**Principais correções aplicadas:** quebra do God Object em camadas (PT-04), credenciais movidas para `.env` (PT-02), substituição de `badCrypto` por hash real (PT-03), persistência em arquivo (PT-11), `authMiddleware` aplicado a rotas administrativas, logger estruturado (PT-09).

### Projeto 3 — `task-manager-api`

**Antes:** estrutura MVC parcial com pastas `models/`, `routes/`, `services/`, `utils/` — mas com problemas graves de segurança (MD5, SECRET_KEY hardcoded, token fake), duplicação inline de regras de negócio e helpers ignorados pelas rotas.

**Depois:** estrutura MVC reforçada com camada de controllers explícita, config carregada de `.env` e middleware central:

```text
task-manager-api/
├── app.py                           # composition root
├── config.py                        # load_dotenv() + os.environ.get()
├── database.py
├── seed.py
├── controllers/                     # camada nova — orquestração HTTP
│   ├── report_controller.py
│   ├── task_controller.py
│   └── user_controller.py
├── models/
│   ├── category.py
│   ├── task.py
│   └── user.py
├── routes/
│   ├── report_routes.py
│   ├── task_routes.py
│   └── user_routes.py
├── services/
│   ├── notification_service.py
│   ├── report_service.py
│   ├── task_service.py
│   └── user_service.py
├── middlewares/error_handler.py
├── utils/helpers.py                 # agora efetivamente usado pelas rotas
├── instance/
└── reports/audit-project-3.md
```

**Principais correções aplicadas:** substituição de MD5 por `werkzeug.security` (PT-03), `SECRET_KEY` e SMTP via env (PT-02), remoção do campo `password` de `to_dict()` (PT-05), centralização de `is_overdue` no model com `service` consumindo (PT-04), correção de N+1 com `joinedload` (PT-06), constantes em `utils/helpers.py` consumidas pelas rotas (PT-07), substituição de `Query.get()` por `db.session.get()` (PT-08), `print()` substituído por `logging` (PT-09).

## Checklist de validação

Os checklists abaixo refletem a execução real da skill em cada projeto. Os itens marcados com `[x]` foram validados por evidência direta (relatório, estrutura de arquivos ou teste de endpoint).

### Projeto 1 — `code-smells-project`

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (E-commerce — produtos, usuários, pedidos)
- [x] Número de arquivos analisados condiz com a realidade (4 arquivos, ~530 linhas)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (12 findings)
- [x] Detecção de APIs deprecated incluída no catálogo (não havia uso deprecated neste projeto específico)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC (`controllers/`, `models/`, `routes/`, `services/`, `middlewares/`)
- [x] Configuração extraída para módulo de config (`config.py`, sem hardcoded)
- [x] Models criados para abstrair dados (`pedido_model.py`, `produto_model.py`, `usuario_model.py`)
- [x] Views/Routes separadas para roteamento (5 arquivos em `routes/`)
- [x] Controllers concentram o fluxo da aplicação (3 arquivos em `controllers/`)
- [x] Error handling centralizado (`middlewares/error_handler.py`)
- [x] Entry point claro (`app.py` como composition root)
- [x] Aplicação inicia sem erros (testado com `python app.py`)
- [x] Endpoints originais respondem corretamente (`/health` 200, `/produtos` 200 com 10 itens, `/usuarios` 200 com 4 usuários, `/pedidos` 200 com 1 pedido)

### Projeto 2 — `ecommerce-api-legacy`

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Node.js / JavaScript)
- [x] Framework detectado corretamente (Express 4.18.2)
- [x] Domínio da aplicação descrito corretamente (LMS / checkout — cursos, matrículas, pagamentos)
- [x] Número de arquivos analisados condiz com a realidade (3 arquivos originais, ~181 linhas)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (11 findings)
- [x] Detecção de APIs deprecated incluída no catálogo (não havia uso deprecated neste projeto específico)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC (`controllers/`, `models/`, `routes/`, `services/`, `middlewares/`)
- [x] Configuração extraída para módulo de config (`src/config/settings.js`, sem hardcoded)
- [x] Models criados para abstrair dados (5 arquivos em `models/`)
- [x] Views/Routes separadas para roteamento (3 arquivos em `routes/`)
- [x] Controllers concentram o fluxo da aplicação (3 arquivos em `controllers/`)
- [x] Error handling centralizado (`middlewares/errorHandler.js`)
- [x] Entry point claro (`src/app.js` como composition root)
- [x] Aplicação inicia sem erros (testado com `node src/app.js`)
- [x] Endpoints originais respondem corretamente: `POST /api/checkout` 200 com cartão aprovado retornando `enrollment_id`, `POST /api/checkout` 400 com "Pagamento recusado" para cartão recusado (lógica de negócio funcionando via `checkoutService`), `GET /api/admin/financial-report` 401 e `DELETE /api/users/:id` 401 (comportamento correto — middleware de autenticação ativo)

### Projeto 3 — `task-manager-api`

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0.0 + Flask-SQLAlchemy 3.1.1)
- [x] Domínio da aplicação descrito corretamente (Task manager — tarefas, usuários, categorias, relatórios)
- [x] Número de arquivos analisados condiz com a realidade (11 arquivos, ~1160 linhas)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (12 findings)
- [x] Detecção de APIs deprecated incluída — `Model.query.get()` deprecated do SQLAlchemy 2.0 detectado em 9 ocorrências
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC (`controllers/`, `models/`, `routes/`, `services/`, `middlewares/`, `utils/`)
- [x] Configuração extraída para módulo de config (`config.py` com `load_dotenv()`)
- [x] Models criados para abstrair dados (`category.py`, `task.py`, `user.py`)
- [x] Views/Routes separadas para roteamento (3 arquivos em `routes/`)
- [x] Controllers concentram o fluxo da aplicação (camada nova, 3 arquivos em `controllers/`)
- [x] Error handling centralizado (`middlewares/error_handler.py`)
- [x] Entry point claro (`app.py` como composition root)
- [x] Aplicação inicia sem erros (testado com `python app.py`)
- [x] Endpoints originais respondem corretamente (`/tasks` 200 com 10 tasks, `/users` 200 com 3 usuários, `/categories` 200 com 4 categorias, `/reports/summary` 200 com relatório completo de produtividade incluindo `overdue.count: 2` calculado corretamente)

## Logs e evidências

Trechos reais capturados durante a validação pós-refatoração de cada projeto.

### Projeto 1 — `code-smells-project`

```text
GET /health
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.11.9
{"counts":{"pedidos":1,"produtos":10,"usuarios":4},"database":"connected","status":"ok","versao":"1.0.0"}

GET /produtos
HTTP/1.1 200 OK
Content-Length: 1646
{"dados":[{"id":1,"nome":"Notebook Gamer Pro","preco":6000.0,"estoque":8, ...}, ... (10 produtos)],"sucesso":true}

GET /usuarios
HTTP/1.1 200 OK
{"dados":[{"id":1,"nome":"Admin","email":"admin@loja.com","tipo":"admin"}, ... (4 usuários)],"sucesso":true}

GET /pedidos
HTTP/1.1 200 OK
{"dados":[{"id":1,"itens":[{"produto_nome":"Mouse Wireless","quantidade":1,"preco_unitario":89.9}],"status":"aprovado","total":89.9,"usuario_id":1}],"sucesso":true}
```

Observação: o `/health` da versão refatorada não expõe mais a `SECRET_KEY` nem o `db_path`, confirmando a correção do finding [HIGH] sobre exposição de campos sensíveis.

### Projeto 2 — `ecommerce-api-legacy`

```text
POST /api/checkout  (cartão começando com 4 → status PAID)
HTTP/1.1 200 OK
X-Powered-By: Express
{"msg":"Sucesso","enrollment_id":6}

POST /api/checkout  (cartão começando com 5 → status DENIED)
HTTP/1.1 400 Bad Request
{"error":"Pagamento recusado"}

GET /api/admin/financial-report
HTTP/1.1 401 Unauthorized
{"error":"Unauthorized"}

DELETE /api/users/1
HTTP/1.1 401 Unauthorized
{"error":"Unauthorized"}
```

Observações:

- O par 200/400 no `/api/checkout` confirma que a lógica de aprovação foi extraída para `checkoutService.processCheckout` e está respondendo corretamente — finding [HIGH] sobre lógica de pagamento dentro da rota foi corrigido.
- Os dois `401 Unauthorized` são o **comportamento esperado** após a refatoração: o `requireAuth` registrado em `adminRoutes.js` (`router.use(requireAuth)`) e em `userRoutes.js` (`router.delete('/:id', requireAuth, removeUser)`) bloqueia chamadas anônimas. Isso é a **prova direta** de que os findings [HIGH] sobre admin endpoint público e [CRITICAL] sobre DELETE inseguro foram corrigidos.
- A rota `GET /api/users` deixou de existir após a refatoração — o `userRoutes.js` agora expõe apenas `DELETE /:id` (autenticado). A listagem pública de usuários, que vazava o campo `password`, foi intencionalmente removida.
- O contrato externo do checkout manteve os nomes abreviados de campo (`usr`, `eml`, `pwd`, `c_id`, `card`) — o controller normaliza internamente via destructuring. O finding [LOW] sobre nomenclatura abreviada não foi corrigido no contrato externo, possivelmente por compatibilidade com clientes existentes.

### Projeto 3 — `task-manager-api`

```text
GET /tasks
HTTP/1.1 200 OK
[{"id":1,"title":"Implementar autenticação JWT","status":"pending","overdue":true, ...}, ... (10 tasks)]

GET /users
HTTP/1.1 200 OK
[{"id":1,"name":"João Silva","email":"joao@email.com","role":"admin","task_count":4}, ... (3 usuários)]

GET /categories
HTTP/1.1 200 OK
[{"id":1,"name":"Backend","color":"#3498db","task_count":6}, ... (4 categorias)]

GET /reports/summary
HTTP/1.1 200 OK
{
  "overview":{"total_categories":4,"total_tasks":10,"total_users":3},
  "tasks_by_status":{"pending":6,"in_progress":2,"done":1,"cancelled":1},
  "tasks_by_priority":{"critical":2,"high":3,"medium":3,"low":2,"minimal":0},
  "overdue":{"count":2,"tasks":[{"id":1,"title":"Implementar autenticação JWT","days_overdue":3}, ...]},
  "user_productivity":[ ... ]
}
```

Observação: a resposta de `/tasks` traz o campo `overdue` calculado corretamente, e nenhum response de usuário traz mais o campo `password` — confirmação direta de que as correções dos findings [CRITICAL] (MD5 + exposição de hash) e [HIGH] (`is_overdue` duplicado) foram efetivas.

## Observações sobre comportamento em stacks diferentes

- **No projeto Flask flat (`code-smells-project`)**, a skill aplicou refatorações estruturais profundas — saiu de 4 arquivos na raiz para 5 camadas separadas (`controllers/`, `models/`, `routes/`, `services/`, `middlewares/`), criando 16 novos arquivos e mantendo os arquivos originais como referência histórica.
- **No projeto Express (`ecommerce-api-legacy`)**, o foco principal foi quebrar o God Object (`AppManager.js` com 141 linhas) em 16 arquivos modulares, retirar secrets hardcoded para env vars, substituir `:memory:` por persistência em arquivo e introduzir middleware de autenticação para rotas administrativas. A skill respeitou as convenções do Express ao nomear arquivos como `userController.js`, `userRoutes.js` em camelCase, em vez de impor o snake_case do Python.
- **No projeto Flask parcialmente organizado (`task-manager-api`)**, a skill atuou mais em conteúdo de camada do que em criação de pastas: introduziu a camada de `controllers/` (que não existia), eliminou MD5, removeu o campo `password` do `to_dict()`, centralizou `is_overdue` no model, substituiu 9 ocorrências de `Query.get()` deprecated, e fez os helpers de `utils/helpers.py` (que estavam definidos mas ignorados) serem efetivamente consumidos pelas rotas.
- **A skill foi escrita uma única vez** dentro de `code-smells-project/.claude/skills/refactor-arch/` e copiada sem nenhuma alteração para os outros dois projetos. Nenhum dos arquivos de referência precisou ser editado para funcionar em Node.js depois de ter sido escrito pensando em Python — esse foi o teste real de agnosticismo.

---

# Como Executar

## Pré-requisitos

- Claude Code instalado e configurado
- Python 3.11+ disponível para os projetos Flask
- Node.js 18+ e npm disponíveis para o projeto Express
- Git para clonar o repositório

## Setup inicial

```bash
git clone https://github.com/jonathanfrazao/mba-ia-refactor-projects-skill.git
cd mba-ia-refactor-projects-skill
```

## Localização da skill

A pasta `.claude` está dentro de cada projeto, conforme a estrutura pedida no desafio:

- `code-smells-project/.claude/skills/refactor-arch/`
- `ecommerce-api-legacy/.claude/skills/refactor-arch/`
- `task-manager-api/.claude/skills/refactor-arch/`

Os arquivos da skill (`SKILL.md` + 5 referências em Markdown) são **idênticos** nos 3 projetos.

## Reexecutando a skill

Caso queira reexecutar a skill em qualquer projeto:

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A skill pausa antes da Fase 3 pedindo confirmação `[y/n]` antes de modificar arquivos.

## Validando que a refatoração funciona

### Projeto 1 — `code-smells-project` (Python/Flask)

```bash
cd code-smells-project

# Criar e ativar venv
python3 -m venv venv
source venv/bin/activate              # Linux/macOS
# .\venv\Scripts\Activate.ps1         # Windows PowerShell

pip install -r requirements.txt

# Subir a aplicação
python app.py
```

Em outro terminal, validar endpoints:

```bash
curl -i http://localhost:5000/health
curl -i http://localhost:5000/produtos
curl -i http://localhost:5000/usuarios
curl -i http://localhost:5000/pedidos
```

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express)

```bash
cd ecommerce-api-legacy
npm install
node src/app.js
```

Em outro terminal, validar os endpoints:

```bash
# Checkout aprovado (cartão começando com 4)
curl -i -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr":"Test","eml":"test@example.com","pwd":"123","c_id":1,"card":"4111111111111111"}'

# Checkout recusado (cartão começando com 5)
curl -i -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr":"Test","eml":"test2@example.com","pwd":"123","c_id":1,"card":"5111111111111111"}'

# Admin endpoint protegido (deve retornar 401)
curl -i http://localhost:3000/api/admin/financial-report

# DELETE protegido (deve retornar 401)
curl -i -X DELETE http://localhost:3000/api/users/1
```

Os `401 Unauthorized` nos endpoints administrativos são o comportamento correto — confirmam que o middleware de autenticação está ativo. O servidor sobe na porta 3000 por padrão.

### Projeto 3 — `task-manager-api` (Python/Flask)

```bash
cd task-manager-api

python3 -m venv venv
source venv/bin/activate              # Linux/macOS
# .\venv\Scripts\Activate.ps1         # Windows PowerShell

pip install -r requirements.txt

# Popular o banco
python seed.py

# Subir a aplicação
python app.py
```

Em outro terminal:

```bash
curl -i http://localhost:5000/tasks
curl -i http://localhost:5000/users
curl -i http://localhost:5000/categories
curl -i http://localhost:5000/reports/summary
```

> **Atenção:** os Projetos 1 e 3 usam a mesma porta 5000 por padrão. Suba um de cada vez.

---

# Critérios de aceite

A skill precisa atingir, em **todos os 3 projetos**, os critérios mínimos definidos pelo desafio. Status de conformidade:

| Critério | Projeto 1 | Projeto 2 | Projeto 3 |
|---|:-:|:-:|:-:|
| Fase 1 detecta a stack corretamente | ✅ | ✅ | ✅ |
| Fase 2 encontra ≥ 5 findings | ✅ (12) | ✅ (11) | ✅ (12) |
| Fase 2 inclui pelo menos 1 finding CRITICAL ou HIGH | ✅ | ✅ | ✅ |
| Fase 3 deixa a aplicação funcionando após a refatoração | ✅ | ✅ | ✅ |

Os 4 critérios obrigatórios foram atingidos nos 3 projetos.

---

# Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills)

As referências acima são as mesmas indicadas no enunciado e serviram como base para a estruturação da skill e dos arquivos de referência.
