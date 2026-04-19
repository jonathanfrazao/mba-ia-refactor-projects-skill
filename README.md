# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

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

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

## Análise Manual

Análise realizada antes da criação da skill. Para cada projeto foram identificados os principais problemas de arquitetura, segurança e qualidade, com arquivo, linhas e severidade exatos.

---

### Projeto 1 — code-smells-project (Python/Flask — API de E-commerce)

**Stack:** Python · Flask 3.1.1 · flask-cors · SQLite (raw, sem ORM)  
**Domínio:** E-commerce (produtos, usuários, pedidos, relatórios de vendas)  
**Arquitetura atual:** Pseudo-MVC flat — `app.py` (rotas), `controllers.py` (handlers HTTP), `models.py` (acesso a dados + regras de negócio), `database.py` (singleton de conexão). Sem blueprints, sem pacotes, sem autenticação em nenhum endpoint.

| # | Severidade | Problema | Arquivo | Linhas |
|---|---|---|---|---|
| 1 | CRITICAL | SQL Injection em toda a camada de dados — queries construídas por concatenação de strings | `models.py` | 28, 47–49, 57–61, 68, 92, 110, 126–128, 140, 149–150, 155–165, 174, 280–281, 291–297 |
| 2 | CRITICAL | Endpoint `/admin/query` executa SQL arbitrário recebido no body sem autenticação | `app.py` | 59–78 |
| 3 | CRITICAL | Senhas armazenadas em texto plano + SECRET_KEY hardcoded exposta no response do `/health` | `models.py`, `database.py`, `controllers.py` | `models.py:128`, `database.py:76–83`, `controllers.py:287–289` |
| 4 | HIGH | Lógica de negócio (validação de estoque, cálculo de total, decremento de estoque) dentro da camada Model | `models.py` | 133–169 |
| 5 | HIGH | Endpoint `/admin/reset-db` apaga todas as tabelas sem autenticação | `app.py` | 47–57 |
| 6 | MEDIUM | N+1 queries na listagem de pedidos — 3 níveis de cursores aninhados por pedido | `models.py` | 171–201, 203–233 |
| 7 | MEDIUM | Validação de `criar_produto` e `atualizar_produto` duplicada literalmente entre as duas funções | `controllers.py` | 28–55, 73–85 |
| 8 | MEDIUM | Conexão SQLite como singleton global mutável sem thread safety real em ambiente concorrente | `database.py` | 4–10 |
| 9 | LOW | `print()` usado como único mecanismo de logging — sem nível, sem timestamp estruturado | `controllers.py` | 8, 57, 106, 161, 179, 208–210, 219, 248–250 |
| 10 | LOW | Serialização de `Row` para `dict` reimplementada manualmente em cada função de leitura, sem `to_dict()` centralizado | `models.py` | 10–21, 31–40, 79–86, 95–102 |

**Resumo:** 3 CRITICAL · 2 HIGH · 3 MEDIUM · 2 LOW

**Por que é relevante para a skill:** SQL Injection por concatenação é o padrão mecânico mais importante para detectar automaticamente. A ausência de hash de senha e a exposição da `SECRET_KEY` no health check são sinais diretos de credencial insegura. O endpoint `/admin/query` representa o anti-pattern de "operação perigosa sem autenticação" que a skill deve sinalizar.

---

### Projeto 2 — ecommerce-api-legacy (Node.js/Express — LMS API com checkout)

**Stack:** Node.js · Express 4.18.2 · sqlite3 5.1.6 · sem ORM · sem autenticação  
**Domínio:** LMS (cursos, matrículas, pagamentos, usuários)  
**Arquitetura atual:** God Object — `AppManager.js` concentra roteamento, acesso a dados, lógica de negócio, processamento de pagamento e auditoria em 141 linhas. Banco de dados em memória (`:memory:`).

| # | Severidade | Problema | Arquivo | Linhas |
|---|---|---|---|---|
| 1 | CRITICAL | Credenciais de produção hardcoded — chave de gateway live (`pk_live_...`), senha de DB e SMTP | `utils.js` | 1–7 |
| 2 | CRITICAL | Algoritmo de criptografia customizado e inseguro (`badCrypto`) — base64 não é hash; resultado de 10 chars, colisões triviais | `utils.js` | 17–23 |
| 3 | CRITICAL | Banco de dados em memória (`:memory:`) — perda total de dados a cada restart | `AppManager.js` | 7 |
| 4 | CRITICAL | God Object — ausência total de separação de responsabilidades; rotas + DB + pagamento + auditoria em uma classe | `AppManager.js` | 1–141 |
| 5 | HIGH | Lógica de aprovação de pagamento por prefixo de cartão (`cc.startsWith("4")`) + número do cartão logado no console | `AppManager.js` | 44–48 |
| 6 | HIGH | Callback hell de 5 níveis no handler de checkout, sem tratamento uniforme de erros | `AppManager.js` | 36–78 |
| 7 | HIGH | DELETE de usuário sem cascade — matrículas e pagamentos ficam órfãos; documentado na própria resposta HTTP | `AppManager.js` | 131–137 |
| 8 | MEDIUM | Cache global mutável (`globalCache`) sem TTL, compartilhado entre requisições sem sincronização | `utils.js` | 9, 12–15 |
| 9 | MEDIUM | `totalRevenue` declarado e exportado mas nunca incrementado — dead code que simula feature inexistente | `utils.js` | 10, 25 |
| 10 | LOW | Variáveis de payload com nomes de 1–2 letras sem semântica (`u`, `e`, `p`, `cid`, `cc`) | `AppManager.js` | 29–34 |
| 11 | LOW | Erro não verificado no callback do DELETE — resposta de sucesso enviada mesmo em caso de falha no banco | `AppManager.js` | 132–136 |

**Resumo:** 4 CRITICAL · 3 HIGH · 2 MEDIUM · 2 LOW

**Por que é relevante para a skill:** Este projeto representa o cenário mais extremo de violação arquitetural — a skill precisa reconhecer o padrão God Object pelo acúmulo de responsabilidades em uma única classe. A detecção de `Database(':memory:')`, credenciais hardcoded fora de `process.env` e callbacks com mais de 3 níveis de aninhamento são sinais de detecção diretamente acionáveis nos arquivos de referência.

---

### Projeto 3 — task-manager-api (Python/Flask — API de Task Manager)

**Stack:** Python · Flask 3.0.0 · Flask-SQLAlchemy 3.1.1 · flask-cors · marshmallow (instalado, não usado) · python-dotenv (instalado, não usado)  
**Domínio:** Gerenciamento de tarefas (tasks, usuários, categorias, relatórios de produtividade)  
**Arquitetura atual:** MVC incompleto — estrutura de pastas correta (`routes/`, `models/`, `services/`, `utils/`), mas sem autenticação real, com lógica duplicada entre camadas e utilitários definidos porém ignorados pelas rotas.

| # | Severidade | Problema | Arquivo | Linhas |
|---|---|---|---|---|
| 1 | CRITICAL | Senhas hasheadas com MD5 sem salt — algoritmo criptograficamente quebrado desde 2004, vulnerável a rainbow table | `models/user.py` | 27–32 |
| 2 | CRITICAL | Credenciais de email hardcoded na classe `NotificationService` | `services/notification_service.py` | 8–10 |
| 3 | CRITICAL | Token de autenticação fake e previsível (`'fake-jwt-token-' + str(user.id)`) — não verificado em nenhum endpoint | `routes/user_routes.py` | 210 |
| 4 | HIGH | Hash MD5 da senha exposto em todos os responses de usuário via `to_dict()` | `models/user.py` | 16–25 |
| 5 | HIGH | Lógica `is_overdue` duplicada em 6 locais diferentes — método `is_overdue()` existe no Model mas nunca é chamado | `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py`, `models/task.py` | `task_routes.py:30–39,71–80,171–181,284–288` · `report_routes.py:33–44,131–135` · `task.py:50–60` |
| 6 | HIGH | N+1 queries no relatório de produtividade — query individual por usuário dentro de loop | `routes/report_routes.py` | 53–68 |
| 7 | MEDIUM | Funções utilitárias (`validate_email`, `process_task_data`) e constantes (`VALID_STATUSES`, `VALID_ROLES`) em `helpers.py` definidas mas não usadas pelas rotas, que duplicam a mesma lógica inline | `utils/helpers.py`, `routes/task_routes.py`, `routes/user_routes.py` | `helpers.py:19–23,57–116,110–116` |
| 8 | MEDIUM | SECRET_KEY hardcoded — `python-dotenv` instalado mas `load_dotenv()` nunca chamado | `app.py` | 13 |
| 9 | LOW | Imports não utilizados em múltiplos arquivos (`json`, `os`, `sys`, `time`, `math`) | `routes/task_routes.py`, `routes/user_routes.py`, `utils/helpers.py` | `task_routes.py:7` · `user_routes.py:6` · `helpers.py:1–8` |
| 10 | LOW | Serialização manual campo a campo em `get_tasks()` e `get_user_tasks()` quando `task.to_dict()` já existe e é usado em outros handlers do mesmo arquivo | `routes/task_routes.py`, `routes/user_routes.py` | `task_routes.py:16–58` · `user_routes.py:161–182` |

**Resumo:** 3 CRITICAL · 3 HIGH · 2 MEDIUM · 2 LOW

**Por que é relevante para a skill:** Este projeto prova que estrutura de pastas organizada não equivale a arquitetura saudável. A skill precisa ir além da estrutura de diretórios e inspecionar o conteúdo — detectando `hashlib.md5` em métodos de senha, `to_dict()` que expõe campo `password`, tokens gerados por concatenação de string, e métodos do Model definidos porém nunca chamados nas rotas. O `python-dotenv` instalado sem uso é um sinal de configuração incompleta detectável pela análise de dependências vs. código.