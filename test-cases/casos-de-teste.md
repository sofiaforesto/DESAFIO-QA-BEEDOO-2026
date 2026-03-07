# Casos de Teste — Beedoo QA Tests

> Módulo: Cadastro e Listagem de Cursos
> Formato: Gherkin (DADO / QUANDO / ENTÃO) + Passo a Passo
> Total de cenários: 20

---

## CT-001 — Cadastro de curso com dados válidos (fluxo feliz — Online)

**Prioridade:** Alta | **Resultado:** ✅ Passou

**Gherkin:**
```gherkin
DADO que o usuário está na página de cadastro de curso (/new-course)
QUANDO preenche todos os campos obrigatórios com dados válidos
  | Campo             | Valor                                 |
  | Nome do curso     | Curso de Introdução ao QA             |
  | Descrição         | Aprenda os fundamentos de QA          |
  | Instrutor         | Ana Lima                              |
  | Url da imagem     | https://picsum.photos/400/200         |
  | Data de início    | 2025-04-01                            |
  | Data de fim       | 2025-05-01                            |
  | Número de vagas   | 30                                    |
  | Tipo de curso     | Online                                |
  | Link de inscrição | https://inscricao.beedoo.com/qa-intro |
E clica em "Cadastrar curso"
ENTÃO o sistema exibe a mensagem "Curso cadastrado com sucesso!"
E o usuário é redirecionado para a listagem (/)
E o curso aparece na listagem com todos os dados preenchidos
```

---

## CT-002 — Cadastro de curso Presencial com endereço

**Prioridade:** Alta | **Resultado:** ✅ Passou

**Gherkin:**
```gherkin
DADO que o usuário está na página /new-course
QUANDO seleciona "Presencial" no campo "Tipo de curso"
ENTÃO o campo "Endereço" deve ser exibido
E o campo "Link de inscrição" não deve ser exibido
QUANDO preenche o endereço com "Av. Paulista, 1000 - São Paulo/SP"
E clica em "Cadastrar curso"
ENTÃO o curso é cadastrado e o endereço aparece no card da listagem
```

---

## CT-003 — Cadastro de curso Online exibe campo de link

**Prioridade:** Alta | **Resultado:** ✅ Passou

**Gherkin:**
```gherkin
DADO que o usuário está na página /new-course
QUANDO seleciona "Online" no campo "Tipo de curso"
ENTÃO o campo "Link de inscrição" deve ser exibido
E o campo "Endereço" não deve ser exibido
```

---

## CT-004 — Cadastro com todos os campos vazios (cenário negativo)

**Prioridade:** Alta | **Resultado:** ❌ Falhou — BUG-001

**Gherkin:**
```gherkin
DADO que o usuário está na página /new-course
QUANDO não preenche nenhum campo
E clica em "Cadastrar curso"
ENTÃO o sistema deve exibir mensagens de validação nos campos obrigatórios
E o cadastro NÃO deve ser realizado
```

**Resultado atual:** Curso é cadastrado com todos os campos vazios. Bug registrado: BUG-001.

---

## CT-005 — Validação de campo obrigatório: Nome do curso

**Prioridade:** Alta | **Resultado:** ❌ Falhou — BUG-001

**Passo a Passo:**
1. Acessar `/new-course`
2. Preencher todos os campos exceto "Nome do curso"
3. Clicar em "Cadastrar curso"

**Resultado esperado:** Mensagem de erro "Nome do curso é obrigatório" exibida  
**Resultado atual:** Curso cadastrado sem nome

---

## CT-006 — Data de fim anterior à data de início (cenário negativo)

**Prioridade:** Alta | **Resultado:** ❌ Falhou — BUG-003

**Gherkin:**
```gherkin
DADO que o usuário está na página /new-course
QUANDO preenche "Data de início" com 31/12/2025
E preenche "Data de fim" com 01/01/2025
E clica em "Cadastrar curso"
ENTÃO o sistema deve exibir erro "Data de fim não pode ser anterior à data de início"
E o cadastro NÃO deve ser realizado
```

**Resultado atual:** Curso cadastrado com datas invertidas. Bug registrado: BUG-003.

---

## CT-007 — Número de vagas negativo (cenário negativo)

**Prioridade:** Média | **Resultado:** ❌ Falhou — BUG-004

**Gherkin:**
```gherkin
DADO que o usuário está na página /new-course
QUANDO insere "-5" no campo "Número de vagas"
E clica em "Cadastrar curso"
ENTÃO o sistema deve exibir erro "Número de vagas deve ser maior que zero"
E o cadastro NÃO deve ser realizado
```

**Resultado atual:** Curso cadastrado com -5 vagas.

---

## CT-008 — Número de vagas igual a zero (cenário negativo)

**Prioridade:** Média | **Resultado:** ❌ Falhou — BUG-004

**Passo a Passo:**
1. Acessar `/new-course`
2. Inserir `0` no campo "Número de vagas"
3. Clicar em "Cadastrar curso"

**Resultado esperado:** Erro de validação  
**Resultado atual:** Curso cadastrado com 0 vagas

---

## CT-009 — URL de imagem de capa inválida (cenário negativo)

**Prioridade:** Média | **Resultado:** ❌ Falhou — BUG-005

**Gherkin:**
```gherkin
DADO que o usuário está na página /new-course
QUANDO insere "nao-e-uma-url" no campo "Url da imagem de capa"
E clica em "Cadastrar curso"
ENTÃO o sistema deve exibir erro de URL inválida
OU exibir preview com erro indicando que a imagem não foi carregada
```

**Resultado atual:** Curso cadastrado; imagem aparece quebrada na listagem.

---

## CT-010 — Cadastro sem selecionar tipo de curso (cenário negativo)

**Prioridade:** Média | **Resultado:** ❌ Falhou — BUG-006

**Gherkin:**
```gherkin
DADO que o usuário está na página /new-course
QUANDO mantém "Tipo de curso" como "Selecione..."
E preenche os demais campos
E clica em "Cadastrar curso"
ENTÃO o sistema deve exibir erro "Selecione um tipo de curso"
E o cadastro NÃO deve ser realizado
```

**Resultado atual:** Curso cadastrado com `type: {label: "Selecione...", value: ""}`.

---

## CT-011 — Visualização da listagem de cursos

**Prioridade:** Alta | **Resultado:** ✅ Passou

**Gherkin:**
```gherkin
DADO que existem cursos cadastrados no sistema
QUANDO o usuário acessa a página principal (/)
ENTÃO a lista de cursos deve ser exibida
E cada card deve mostrar: tipo, nome, descrição, instrutor, datas, vagas
E o botão "Excluir curso" deve estar disponível em cada card
```

---

## CT-012 — Listagem vazia quando não há cursos cadastrados

**Prioridade:** Média | **Resultado:** ✅ Passou parcialmente

**Passo a Passo:**
1. Limpar o localStorage do navegador
2. Acessar a página principal (/)

**Resultado esperado:** Mensagem amigável "Nenhum curso cadastrado" ou estado vazio visual  
**Resultado atual:** Página exibe somente o título "Lista de cursos" sem nenhuma mensagem de estado vazio — UX pode melhorar mas não é bug crítico

---

## CT-013 — Excluir curso da listagem

**Prioridade:** Alta | **Resultado:** ❌ Falhou — BUG-002

**Gherkin:**
```gherkin
DADO que existe ao menos um curso na listagem
QUANDO o usuário clica em "Excluir curso"
ENTÃO o curso deve ser removido da listagem imediatamente
E ao recarregar a página, o curso NÃO deve mais aparecer
```

**Resultado atual:** Notificação de sucesso exibida, mas o curso permanece na listagem após recarregar. Bug registrado: BUG-002.

---

## CT-014 — Múltiplos cursos cadastrados e listados

**Prioridade:** Alta | **Resultado:** ✅ Passou

**Passo a Passo:**
1. Cadastrar 3 cursos com dados diferentes
2. Acessar a listagem

**Resultado esperado:** Todos os 3 cursos aparecem na listagem  
**Resultado atual:** Todos os cursos são listados corretamente

---

## CT-015 — Trocar tipo de curso de Presencial para Online

**Prioridade:** Baixa | **Resultado:** ❌ Falhou parcialmente — BUG-007

**Gherkin:**
```gherkin
DADO que o usuário está na página /new-course
QUANDO seleciona "Presencial" e preenche o campo "Endereço" com "Rua A, 100"
E depois muda para "Online"
ENTÃO o campo "Endereço" deve ser ocultado
E os dados do endereço devem ser limpos do modelo interno
```

**Resultado atual:** Campo é ocultado corretamente, mas o valor `address` persiste no objeto salvo.

---

## CT-016 — Campos com caracteres especiais e emojis

**Prioridade:** Baixa | **Resultado:** ✅ Passou

**Passo a Passo:**
1. Cadastrar curso com nome "Curso de QA 🚀 <script>alert(1)</script>"
2. Verificar na listagem

**Resultado esperado:** Texto exibido sem execução de script (XSS não ocorre)  
**Resultado atual:** Texto exibido com escape correto — Vue/Quasar escapa HTML por padrão ✅

---

## CT-017 — Campo descrição com texto muito longo

**Prioridade:** Baixa | **Resultado:** ✅ Passou

**Passo a Passo:**
1. Cadastrar curso com descrição de 5.000 caracteres
2. Verificar exibição no card

**Resultado esperado:** Texto exibido sem quebrar o layout  
**Resultado atual:** Texto aceito e exibido; layout não quebra (overflow tratado pelo framework)

---

## CT-018 — Número de vagas com valor decimal (cenário negativo)

**Prioridade:** Média | **Resultado:** ❌ Falhou — BUG-004

**Passo a Passo:**
1. Inserir `10.5` no campo "Número de vagas"
2. Cadastrar o curso

**Resultado esperado:** Erro de validação — vagas devem ser número inteiro  
**Resultado atual:** Curso cadastrado com 10.5 vagas

---

## CT-019 — Acessar rota inexistente

**Prioridade:** Baixa | **Resultado:** ✅ Passou

**Passo a Passo:**
1. Acessar `/rota-que-nao-existe`

**Resultado esperado:** Página de erro 404 amigável  
**Resultado atual:** Página 404 exibida pelo framework (ErrorNotFound component) ✅

---

## CT-020 — Persistência de dados após recarregar a página

**Prioridade:** Alta | **Resultado:** ✅ Passou

**Gherkin:**
```gherkin
DADO que o usuário cadastrou um curso
QUANDO recarrega a página de listagem (F5)
ENTÃO o curso deve continuar aparecendo na listagem
```

**Resultado atual:** Dados persistem no localStorage e são carregados corretamente após reload ✅

---

## Resumo de Resultados

| Status | Quantidade |
|--------|-----------|
| ✅ Passou | 9 |
| ❌ Falhou | 9 |
| ⚠️ Passou parcialmente | 1 |
| **Total** | **20** |

| Bugs encontrados | Severidade |
|-----------------|------------|
| BUG-001, BUG-003 | 🔴 Alta |
| BUG-002 | 🔴 Alta |
| BUG-004, BUG-005, BUG-006 | 🟡 Média |
| BUG-007, BUG-008 | 🟢 Baixa |
