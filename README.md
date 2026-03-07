# DESAFIO-QA-BEEDOO-2026

Repositório de análise e testes do módulo de cadastro e listagem de cursos — Beedoo QA Tests.

🔗 **Aplicação testada:** https://creative-sherbet-a51eac.netlify.app/
📊 **Planilha de casos de teste:** [Google Sheets — Casos de Teste](https://docs.google.com/spreadsheets/d/1BNAGhR3jvEy_KpSFPlt7W8mRy4xCZ_PV7n2NuW48Y_c/edit?usp=sharing)
📁 **Evidências de execução:** [Google Drive — Prints e Gravações](https://drive.google.com/drive/folders/1i8TS7DL8z_GKjDhiEBtMQFPLfplFHzgd?usp=sharing)

---

## Estrutura do Repositório

```
DESAFIO-QA-BEEDOO-2026/
├── README.md                          ← Análise, fluxos, decisões, bugs
├── etapa-2-respostas.md               ← Respostas da Etapa 2 (análise crítica)
├── test-cases/
│   ├── casos-de-teste.md              ← Casos de teste em Gherkin + passo a passo
│   └── casos-de-teste.csv             ← Versão CSV para importação no Google Sheets
└── bugs/
    └── bug-report.md                  ← Relatório detalhado de todos os bugs
```

---

## 1. Análise Inicial da Aplicação

### O que é a aplicação?

A **Beedoo QA Tests** é um ambiente web para **cadastro e listagem de cursos**. É uma Single Page Application (SPA) construída com **Vue.js + Quasar Framework**, hospedada no Netlify.

> **Detalhe técnico importante descoberto na análise:** A aplicação não possui backend real. Toda a persistência de dados ocorre via `localStorage` do navegador, usando a chave `@beedoo-qa-tests/courses`. Isso significa que os dados existem apenas no navegador local — não há sincronização entre dispositivos.

### Como descobri isso?

Como a aplicação é uma SPA renderizada via JavaScript, o conteúdo não está disponível no HTML estático. Analisei diretamente os **bundles JavaScript** gerados pelo build (`CourseForm.afe3ffdb.js`, `IndexPage.da5f52bb.js`) para entender a lógica interna sem depender de um browser. Esse processo revelou:

- A estrutura de dados de cada curso
- A lógica de geração de ID (sequential length-based)
- O uso de localStorage como única camada de persistência
- Uma chamada DELETE hardcoded para `/test-api/courses/1`
- A ausência total de validação no formulário

---

## 2. Principais Fluxos Disponíveis

### Fluxo 1 — Listagem de Cursos (`/`)
- Lê cursos do `localStorage` e os exibe em cards
- Cada card mostra: imagem de capa, tipo do curso, nome, descrição, instrutor, datas, vagas e link/endereço
- Botão "Excluir curso" em cada card

### Fluxo 2 — Cadastro de Curso (`/new-course`)
Formulário com os campos:

| Campo | Tipo | Condicional |
|-------|------|-------------|
| Nome do curso | Texto | Sempre visível |
| Descrição do curso | Textarea | Sempre visível |
| Instrutor | Texto | Sempre visível |
| Url da imagem de capa | Texto | Sempre visível |
| Data de início | Date | Sempre visível |
| Data de fim | Date | Sempre visível |
| Número de vagas | Número | Sempre visível |
| Tipo de curso | Select (Presencial/Online) | Sempre visível |
| Endereço | Texto | Apenas se Presencial |
| Link de inscrição | Texto | Apenas se Online |

### Fluxo 3 — Exclusão de Curso
- Botão "Excluir curso" no card chama `DELETE /test-api/courses/1` (ID fixo)
- Exibe notificação de sucesso mas **não remove do localStorage**

---

## 3. Pontos Mais Críticos para Teste

| Prioridade | Área | Por que é crítico |
|-----------|------|-------------------|
| 🔴 Alta | Validação de campos | Nenhum campo possui validação — formulário aceita dados vazios |
| 🔴 Alta | Exclusão de curso | Não funciona — ID hardcoded e localStorage não atualizado |
| 🔴 Alta | Validação de datas | Data de fim pode ser anterior à data de início |
| 🟡 Média | Campos condicionais | Dados ocultos persistem no objeto ao trocar tipo |
| 🟡 Média | Número de vagas | Aceita negativos, zero e decimais |
| 🟡 Média | URL da imagem | Sem validação de formato — gera imagens quebradas |
| 🟢 Baixa | Geração de ID | Pode duplicar IDs após exclusões |

---

## 4. Decisões Tomadas para Criação dos Testes

### Por que analisar o código-fonte antes de testar?

A primeira decisão foi **ir além da interface visual** e inspecionar os arquivos JavaScript do bundle. Isso permitiu:

1. Entender a estrutura exata dos dados — sem precisar executar todos os cenários manualmente
2. Identificar bugs que não são visíveis na UI (como o ID hardcoded no DELETE e a persistência de campos ocultos)
3. Mapear todos os campos existentes, incluindo os condicionais, antes de abrir o formulário

Essa abordagem é especialmente útil em SPAs onde o comportamento está encapsulado no JS e não é aparente apenas olhando para a tela.

### Critérios para seleção dos cenários

Priorizei cenários baseado em **risco x probabilidade**:

- **Alto risco, alta probabilidade:** Fluxos principais (cadastro, listagem, exclusão) — testados primeiro e com maior detalhe
- **Alto risco, baixa probabilidade:** Segurança (XSS, injeção) — testados mas com menor profundidade dado o escopo do desafio
- **Baixo risco, alta probabilidade:** Edge cases de campos (caracteres especiais, texto longo) — incluídos para completude
- **Baixo risco, baixa probabilidade:** Bugs de estado interno (ID duplicado) — documentados mas com menor prioridade

### Formato dos casos de teste

Escolhi **Gherkin** como formato primário por três razões:
1. É legível por pessoas técnicas e não-técnicas (produto, dev, stakeholders)
2. Força a pensar em pré-condições, ações e resultados esperados de forma estruturada
3. Serve como base para automação futura com frameworks como Cypress/Playwright

Para casos mais técnicos (análise de estado interno), complementei com **passo a passo estruturado**.

---

## 5. Raciocínio Durante a Análise

### Como pensei nos cenários negativos?

Para cada campo do formulário, me fiz três perguntas:
1. **O que acontece se eu não preencher?** → Testou ausência (CT-004, CT-005)
2. **O que acontece se eu preencher com dados inválidos?** → Testou formato e limites (CT-007, CT-008, CT-009, CT-018)
3. **O que acontece em situações limite?** → Testou valores extremos e combinações (CT-015, CT-016, CT-017)

### Por que testei a exclusão com reload?

A exclusão sem reload poderia passar em memória mesmo sem persistir. O reload foi essencial para confirmar se o dado foi realmente removido do localStorage ou apenas ocultado temporariamente na UI.

### Como identifiquei o bug do DELETE hardcoded?

Ao analisar o JavaScript, encontrei:
```javascript
fetch("/test-api/courses/1", { method: "DELETE" })
```
O ID `1` está literalmente no código-fonte — não é dinâmico. Isso significa que independentemente de qual curso o usuário clica para excluir, a chamada sempre vai para o ID 1. Combinado com o fato de que o localStorage não é atualizado após o DELETE, a exclusão é completamente não-funcional.

---

## 6. Cenários e Casos de Teste

📊 **[Acessar Google Sheets — Casos de Teste](https://docs.google.com/spreadsheets/d/1BNAGhR3jvEy_KpSFPlt7W8mRy4xCZ_PV7n2NuW48Y_c/edit?usp=sharing)**

| Resultado | Quantidade |
|-----------|-----------|
| ✅ Passou | 9 |
| ❌ Falhou | 10 |
| ⚠️ Parcial | 1 |
| **Total** | **20** |

Resumo dos cenários cobertos:
- Fluxos positivos de cadastro (Online e Presencial)
- Validações de campos obrigatórios
- Validação de datas
- Limites e valores inválidos (negativo, zero, decimal, texto longo)
- Campos condicionais e troca de tipo
- Exclusão de cursos
- Segurança (XSS)
- Navegação e rotas
- Persistência de dados

---

## 7. Relatório de Bugs

📄 **[Ver relatório completo em `/bugs/bug-report.md`](./bugs/bug-report.md)**

### Resumo

| ID | Título | Severidade |
|----|--------|------------|
| BUG-001 | Formulário permite cadastro com todos os campos vazios | 🔴 Alta |
| BUG-002 | Exclusão de curso não remove item do localStorage | 🔴 Alta |
| BUG-003 | Data de fim aceita datas anteriores à data de início | 🔴 Alta |
| BUG-004 | Número de vagas aceita negativo, zero e decimal | 🟡 Média |
| BUG-005 | URL da imagem de capa sem validação de formato | 🟡 Média |
| BUG-006 | Tipo "Selecione..." aceito no cadastro | 🟡 Média |
| BUG-007 | Dados de campo condicional persistem ao trocar tipo | 🟢 Baixa |
| BUG-008 | Geração de ID pode criar duplicatas | 🟢 Baixa |

### Exemplo de bug (BUG-002 — o mais crítico)

**Título:** Botão "Excluir curso" não remove curso do localStorage

**Passos para reproduzir:**
1. Cadastrar um curso em `/new-course`
2. Acessar a listagem `/`
3. Clicar em "Excluir curso"
4. Observar a notificação de sucesso
5. Recarregar a página (F5)

**Resultado atual:** Notificação verde exibida, mas o curso permanece após recarregar. A chamada DELETE vai para `/test-api/courses/1` (ID fixo) e não manipula o localStorage.

**Resultado esperado:** Curso removido do localStorage imediatamente e não reaparecer após reload.

**Severidade:** Alta — funcionalidade de exclusão completamente não-funcional com feedback falso ao usuário.

---

## 8. Evidências de Execução

📁 **[Acessar Google Drive — Prints e Gravações](https://drive.google.com/drive/folders/1i8TS7DL8z_GKjDhiEBtMQFPLfplFHzgd?usp=sharing)**

Conteúdo da pasta de evidências:
- `CT-001` — Cadastro válido (Online): print do formulário preenchido + card na listagem
- `CT-004` — Cadastro com campos vazios: print mostrando curso vazio na listagem (BUG-001)
- `CT-006` — Datas invertidas: print do card com data de fim anterior ao início (BUG-003)
- `CT-007` — Vagas negativas: print do card com -5 vagas (BUG-004)
- `CT-013` — Exclusão fake: print do localStorage via DevTools mostrando curso ainda presente após exclusão (BUG-002)
- `CT-016` — Tentativa de XSS: print mostrando texto escapado corretamente

---

## Etapa 2 — Análise Crítica

📄 **[Ver respostas completas em `/etapa-2-respostas.md`](./etapa-2-respostas.md)**

Inclui:
1. Análise do bug 404 ao acessar curso por URL direta
2. Vulnerabilidades identificadas (XSS, localStorage tampering, ausência de autenticação)
3. Pontos críticos a esclarecer com produto/dev antes de testar
4. Metodologia de investigação de defeitos
5. Priorização de testes em 15 minutos
6. Reflexão sobre o desafio

---

*Desafio realizado por Sofia Foresto | Beedoo QA 2026*
*Prazo de entrega: 11/03/2026*
