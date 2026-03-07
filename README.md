# DESAFIO-QA-BEEDOO-2026

Repositório de análise e testes do módulo de cadastro e listagem de cursos da aplicação Beedoo QA Tests.

🔗 **Aplicação testada:** https://creative-sherbet-a51eac.netlify.app/

---

## 1. Objetivo da Aplicação

A aplicação **Beedoo QA Tests** é um ambiente web simples para **cadastro e listagem de cursos**. Seu objetivo é permitir que usuários:

- Registrem novos cursos com informações como nome, descrição, instrutor, datas, vagas e tipo (presencial ou online)
- Visualizem a lista de cursos cadastrados
- Excluam cursos da lista

> **Observação técnica:** A aplicação utiliza `localStorage` do navegador como mecanismo de persistência de dados (não há backend real). Os dados existem apenas no navegador local de quem cadastrou.

---

## 2. Principais Fluxos Disponíveis

### Fluxo 1 — Listagem de Cursos (`/`)
- Exibe todos os cursos cadastrados em cards
- Cada card mostra: imagem de capa, tipo do curso, nome, descrição, instrutor, datas, vagas e link/endereço
- Botão "Excluir curso" disponível em cada card

### Fluxo 2 — Cadastro de Curso (`/new-course`)
- Formulário com os campos:
  - **Nome do curso** (texto)
  - **Descrição do curso** (textarea)
  - **Instrutor** (texto)
  - **Url da imagem de capa** (texto)
  - **Data de início** (date picker)
  - **Data de fim** (date picker)
  - **Número de vagas** (número)
  - **Tipo de curso** (select: Presencial / Online)
    - Se **Presencial** → exibe campo "Endereço"
    - Se **Online** → exibe campo "Link de inscrição"
- Botão "Cadastrar curso" salva no localStorage e redireciona para a listagem

### Fluxo 3 — Exclusão de Curso
- Clique em "Excluir curso" no card chama uma API fictícia (`/test-api/courses/1`)
- Exibe mensagem de sucesso, mas **não remove o item do localStorage**

---

## 3. Pontos Mais Críticos para Teste

| Prioridade | Área | Motivo |
|-----------|------|--------|
| 🔴 Alta | Validação de campos no cadastro | Nenhum campo possui validação — formulário aceita dados vazios ou inválidos |
| 🔴 Alta | Funcionalidade de exclusão | O delete não remove o curso do localStorage; usa ID fixo (1) para chamada de API |
| 🔴 Alta | Validação de datas | Data de fim pode ser anterior à data de início sem qualquer bloqueio |
| 🟡 Média | Campos condicionais (Online/Presencial) | Dados preenchidos em um tipo podem persistir internamente ao trocar de tipo |
| 🟡 Média | Número de vagas | Aceita valores negativos, zero e decimais |
| 🟡 Média | URL da imagem de capa | Sem validação de formato; imagem quebrada não é tratada |
| 🟢 Baixa | Geração de ID sequencial | Pode gerar IDs duplicados após exclusões bem-sucedidas |
| 🟢 Baixa | Persistência de dados | Dados armazenados apenas em localStorage — perdidos ao limpar o browser |

---

## 4. Cenários e Casos de Teste

📊 **Planilha com todos os casos de teste:**
> [Acessar Google Sheets — Casos de Teste](https://docs.google.com/spreadsheets/d/1BNAGhR3jvEy_KpSFPlt7W8mRy4xCZ_PV7n2NuW48Y_c/edit?usp=sharing)

---

## 5. Evidências de Execução

📁 **Pasta com evidências (prints e gravações):**
> [Acessar Google Drive — Evidências](https://drive.google.com/drive/folders/placeholder)

---

## 6. Bugs Registrados

| # | Título | Severidade |
|---|--------|------------|
| BUG-001 | Formulário permite cadastro com todos os campos vazios | 🔴 Alta |
| BUG-002 | Exclusão de curso não remove item da listagem (persiste no localStorage) | 🔴 Alta |
| BUG-003 | Data de fim aceita datas anteriores à data de início | 🔴 Alta |
| BUG-004 | Campo "Número de vagas" aceita valores negativos e zero | 🟡 Média |
| BUG-005 | Campo "Url da imagem de capa" aceita qualquer texto sem validação de URL | 🟡 Média |
| BUG-006 | Tipo de curso "Selecione..." permite cadastro sem selecionar tipo válido | 🟡 Média |
| BUG-007 | Dados do campo condicional anterior persistem ao trocar tipo do curso | 🟢 Baixa |
| BUG-008 | ID do curso gerado pode causar duplicatas após exclusões | 🟢 Baixa |

> Detalhamento completo de cada bug na seção abaixo.

---

## 7. Detalhamento dos Bugs

### BUG-001 — Formulário permite cadastro com todos os campos vazios
- **Passos para reproduzir:**
  1. Acessar `/new-course`
  2. Não preencher nenhum campo
  3. Clicar em "Cadastrar curso"
- **Resultado atual:** Curso é cadastrado com sucesso (mensagem verde exibida) e aparece na listagem com todos os campos em branco
- **Resultado esperado:** Formulário deve validar campos obrigatórios (mínimo: nome, tipo, datas) e exibir mensagens de erro antes de permitir o cadastro
- **Severidade:** 🔴 Alta

---

### BUG-002 — Exclusão de curso não remove item da listagem
- **Passos para reproduzir:**
  1. Cadastrar ao menos um curso
  2. Na listagem, clicar em "Excluir curso"
  3. Confirmar mensagem de sucesso
  4. Recarregar a página
- **Resultado atual:** A mensagem "Curso excluído com sucesso!" é exibida, mas o curso permanece na listagem após recarregar. A chamada DELETE vai para `/test-api/courses/1` (ID fixo, não dinâmico) e não manipula o localStorage
- **Resultado esperado:** O curso deve ser removido da listagem imediatamente e não reaparecer após recarregar
- **Severidade:** 🔴 Alta

---

### BUG-003 — Data de fim aceita datas anteriores à data de início
- **Passos para reproduzir:**
  1. Acessar `/new-course`
  2. Preencher "Data de início" com 31/12/2025
  3. Preencher "Data de fim" com 01/01/2025
  4. Clicar em "Cadastrar curso"
- **Resultado atual:** Curso cadastrado sem erro; data de fim é anterior à data de início
- **Resultado esperado:** Sistema deve impedir cadastro quando data de fim for anterior à data de início, exibindo mensagem de erro
- **Severidade:** 🔴 Alta

---

### BUG-004 — Campo "Número de vagas" aceita valores negativos e zero
- **Passos para reproduzir:**
  1. Acessar `/new-course`
  2. Inserir `-5` ou `0` no campo "Número de vagas"
  3. Clicar em "Cadastrar curso"
- **Resultado atual:** Curso cadastrado com -5 ou 0 vagas sem qualquer aviso
- **Resultado esperado:** Campo deve aceitar apenas números inteiros positivos (≥ 1)
- **Severidade:** 🟡 Média

---

### BUG-005 — Campo "Url da imagem de capa" aceita qualquer texto
- **Passos para reproduzir:**
  1. Acessar `/new-course`
  2. Inserir "isso não é uma url" no campo "Url da imagem de capa"
  3. Cadastrar o curso
  4. Ver o card na listagem
- **Resultado atual:** Curso cadastrado; imagem aparece quebrada no card
- **Resultado esperado:** Campo deve validar que o valor é uma URL válida (http/https) ou exibir preview da imagem antes do cadastro
- **Severidade:** 🟡 Média

---

### BUG-006 — Tipo "Selecione..." permite cadastro sem tipo válido
- **Passos para reproduzir:**
  1. Acessar `/new-course`
  2. Não alterar o campo "Tipo de curso" (mantê-lo como "Selecione...")
  3. Clicar em "Cadastrar curso"
- **Resultado atual:** Curso cadastrado com `type: {label: "Selecione...", value: ""}` — sem tipo definido
- **Resultado esperado:** Campo "Tipo de curso" deve ser obrigatório; sem seleção de Presencial ou Online, o cadastro não deve ser permitido
- **Severidade:** 🟡 Média

---

### BUG-007 — Dados de campo condicional persistem ao trocar tipo do curso
- **Passos para reproduzir:**
  1. Acessar `/new-course`
  2. Selecionar "Presencial" e preencher o campo "Endereço" com "Rua das Flores, 123"
  3. Mudar o tipo para "Online"
  4. Preencher "Link de inscrição" e cadastrar
- **Resultado atual:** O objeto salvo contém `address: "Rua das Flores, 123"` mesmo que o tipo seja Online (dado oculto mas persistido)
- **Resultado esperado:** Ao trocar o tipo, o campo condicional anterior deve ser limpo/zerado no modelo de dados
- **Severidade:** 🟢 Baixa

---

### BUG-008 — ID sequencial pode gerar duplicatas
- **Passos para reproduzir:**
  1. Cadastrar 3 cursos (IDs 1, 2, 3)
  2. Remover manualmente o curso de ID 2 do localStorage
  3. Cadastrar um novo curso
- **Resultado atual:** Novo curso recebe ID 3 (`length + 1 = 2 + 1 = 3`), duplicando o ID do curso existente
- **Resultado esperado:** Sistema deve usar IDs únicos (UUID ou auto-increment baseado no maior ID existente, não no tamanho do array)
- **Severidade:** 🟢 Baixa

---

## Estrutura do Repositório

```
DESAFIO-QA-BEEDOO-2026/
├── README.md          # Este arquivo — análise, fluxos, bugs
├── test-cases/
│   └── casos-de-teste.md   # Casos de teste em formato Gherkin + passo a passo
└── bugs/
    └── bug-report.md       # Relatório consolidado de bugs
```

---

*Desafio realizado por Sofia Foresto | Beedoo QA 2026*
