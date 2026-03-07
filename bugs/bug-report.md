# Relatório de Bugs — Beedoo QA Tests

> Data: 07/03/2026
> Testador: Sofia Foresto
> Ambiente: https://creative-sherbet-a51eac.netlify.app/
> Total de bugs: 8

---

## BUG-001 — Formulário permite cadastro com todos os campos vazios

| Campo | Detalhes |
|-------|---------|
| **ID** | BUG-001 |
| **Título** | Formulário de cadastro permite submissão com campos vazios |
| **Severidade** | 🔴 Alta |
| **Módulo** | Cadastro de Curso (`/new-course`) |
| **Status** | Aberto |

**Passos para reproduzir:**
1. Acessar a URL `/new-course`
2. Não preencher nenhum campo do formulário
3. Clicar no botão "Cadastrar curso"

**Resultado atual:**
- A mensagem "Curso cadastrado com sucesso!" é exibida
- O curso é salvo no localStorage com todos os valores em branco
- O curso aparece na listagem como um card vazio

**Resultado esperado:**
- Campos obrigatórios (nome, tipo, datas) devem ser validados
- Mensagens de erro devem aparecer em cada campo inválido
- O cadastro não deve ser concluído enquanto houver campos obrigatórios em branco

**Impacto:** Alto — permite cadastro de dados sem sentido, corrompendo a listagem com cursos sem informação.

---

## BUG-002 — Exclusão de curso não remove item da listagem

| Campo | Detalhes |
|-------|---------|
| **ID** | BUG-002 |
| **Título** | Botão "Excluir curso" não remove curso do localStorage |
| **Severidade** | 🔴 Alta |
| **Módulo** | Listagem de Cursos (`/`) |
| **Status** | Aberto |

**Passos para reproduzir:**
1. Cadastrar ao menos um curso em `/new-course`
2. Voltar para a listagem `/`
3. Clicar em "Excluir curso" em qualquer card
4. Observar a notificação
5. Recarregar a página (F5)

**Resultado atual:**
- Notificação verde "Curso excluído com sucesso!" é exibida
- O curso permanece visível na listagem
- Após recarregar, o curso ainda aparece (não foi removido do localStorage)
- A chamada DELETE é enviada para `/test-api/courses/1` (ID fixo, hardcoded)

**Resultado esperado:**
- O curso deve ser removido do localStorage imediatamente ao clicar em excluir
- A chamada de API deve usar o ID correto do curso selecionado (não ID fixo = 1)
- O card deve desaparecer da listagem sem necessidade de recarregar

**Impacto:** Alto — funcionalidade de exclusão completamente não funcional; usuário recebe feedback falso de sucesso.

---

## BUG-003 — Data de fim aceita datas anteriores à data de início

| Campo | Detalhes |
|-------|---------|
| **ID** | BUG-003 |
| **Título** | Ausência de validação de intervalo de datas no formulário |
| **Severidade** | 🔴 Alta |
| **Módulo** | Cadastro de Curso (`/new-course`) |
| **Status** | Aberto |

**Passos para reproduzir:**
1. Acessar `/new-course`
2. Preencher "Data de início" com `2025-12-31`
3. Preencher "Data de fim" com `2025-01-01`
4. Clicar em "Cadastrar curso"

**Resultado atual:**
- Curso cadastrado com sucesso, com data de fim anterior à data de início
- Dados inconsistentes aparecem no card da listagem

**Resultado esperado:**
- Sistema deve validar que `endDate >= startDate`
- Mensagem de erro: "A data de fim não pode ser anterior à data de início"

**Impacto:** Alto — cursos com datas incoerentes prejudicam a integridade dos dados e a experiência do usuário.

---

## BUG-004 — Campo "Número de vagas" aceita valores inválidos

| Campo | Detalhes |
|-------|---------|
| **ID** | BUG-004 |
| **Título** | Campo de vagas aceita zero, negativos e decimais |
| **Severidade** | 🟡 Média |
| **Módulo** | Cadastro de Curso (`/new-course`) |
| **Status** | Aberto |

**Passos para reproduzir:**
1. Acessar `/new-course`
2. Inserir um dos seguintes valores em "Número de vagas": `-5`, `0`, `10.5`
3. Preencher os demais campos
4. Clicar em "Cadastrar curso"

**Resultado atual:**
- Curso cadastrado com valor inválido de vagas (-5, 0 ou 10.5)

**Resultado esperado:**
- Campo deve aceitar apenas inteiros positivos (≥ 1)
- Mensagem de erro adequada para cada caso: "Informe um número maior que zero" / "Número de vagas deve ser inteiro"

**Impacto:** Médio — dados inconsistentes; um curso com 0 ou -5 vagas não faz sentido de negócio.

---

## BUG-005 — Campo "Url da imagem de capa" não valida formato de URL

| Campo | Detalhes |
|-------|---------|
| **ID** | BUG-005 |
| **Título** | Texto livre aceito no campo de URL da imagem de capa |
| **Severidade** | 🟡 Média |
| **Módulo** | Cadastro de Curso (`/new-course`) |
| **Status** | Aberto |

**Passos para reproduzir:**
1. Acessar `/new-course`
2. Inserir "texto qualquer sem url" no campo "Url da imagem de capa"
3. Cadastrar o curso
4. Ver o card na listagem

**Resultado atual:**
- Curso cadastrado sem erro
- Card exibe ícone de imagem quebrada

**Resultado esperado:**
- Campo deve validar formato de URL (iniciar com `http://` ou `https://`)
- Ou exibir preview da imagem em tempo real para o usuário verificar antes de salvar

**Impacto:** Médio — experiência visual degradada na listagem; todos os cards com URL inválida mostrarão imagem quebrada.

---

## BUG-006 — Tipo de curso "Selecione..." permite cadastro sem tipo válido

| Campo | Detalhes |
|-------|---------|
| **ID** | BUG-006 |
| **Título** | Campo "Tipo de curso" não é validado como obrigatório |
| **Severidade** | 🟡 Média |
| **Módulo** | Cadastro de Curso (`/new-course`) |
| **Status** | Aberto |

**Passos para reproduzir:**
1. Acessar `/new-course`
2. Preencher todos os campos exceto "Tipo de curso" (manter como "Selecione...")
3. Clicar em "Cadastrar curso"

**Resultado atual:**
- Curso cadastrado com `type: {label: "Selecione...", value: ""}` — tipo inválido/vazio
- Na listagem, o campo de tipo aparece como vazio ou "Selecione..."
- Os campos condicionais (endereço/link) nunca aparecem no cadastro

**Resultado esperado:**
- "Tipo de curso" deve ser campo obrigatório
- Sem seleção de Presencial ou Online, o sistema deve bloquear o cadastro

**Impacto:** Médio — cursos sem tipo definido não fazem sentido de negócio e quebram a exibição na listagem.

---

## BUG-007 — Dados de campo condicional persistem ao trocar tipo do curso

| Campo | Detalhes |
|-------|---------|
| **ID** | BUG-007 |
| **Título** | Troca de tipo de curso não limpa campos condicionais anteriores |
| **Severidade** | 🟢 Baixa |
| **Módulo** | Cadastro de Curso (`/new-course`) |
| **Status** | Aberto |

**Passos para reproduzir:**
1. Acessar `/new-course`
2. Selecionar "Presencial"
3. Preencher o campo "Endereço" com "Rua das Flores, 100"
4. Mudar para "Online"
5. Preencher "Link de inscrição"
6. Cadastrar o curso

**Resultado atual:**
- O objeto salvo contém `address: "Rua das Flores, 100"` mesmo com tipo Online
- Dado fantasma persistido sem exibição ao usuário

**Resultado esperado:**
- Ao trocar o tipo, o campo condicional anterior deve ser resetado para `""`
- Apenas os dados do tipo selecionado devem ser persistidos

**Impacto:** Baixo — dado não visível ao usuário; pode causar confusão se a lógica de exibição for alterada futuramente.

---

## BUG-008 — Geração de ID pode criar duplicatas após exclusões manuais

| Campo | Detalhes |
|-------|---------|
| **ID** | BUG-008 |
| **Título** | ID sequencial baseado em `array.length` pode duplicar IDs |
| **Severidade** | 🟢 Baixa |
| **Módulo** | Cadastro de Curso (lógica de ID) |
| **Status** | Aberto |

**Passos para reproduzir:**
1. Cadastrar 3 cursos (IDs gerados: 1, 2, 3)
2. Remover o item de ID 2 diretamente do localStorage (`@beedoo-qa-tests/courses`)
3. Cadastrar um novo curso

**Resultado atual:**
- Novo curso recebe ID 3 (`array.length(2) + 1 = 3`), duplicando o ID do curso existente

**Resultado esperado:**
- IDs devem ser únicos mesmo após exclusões
- Usar UUID ou calcular como `Math.max(...ids) + 1` em vez de `array.length + 1`

**Impacto:** Baixo no cenário atual (delete não funciona via UI), mas representa risco técnico real se a exclusão for corrigida.

---

## Resumo

| ID | Título Resumido | Severidade |
|----|----------------|------------|
| BUG-001 | Cadastro com campos vazios permitido | 🔴 Alta |
| BUG-002 | Exclusão não remove curso | 🔴 Alta |
| BUG-003 | Data de fim anterior à data de início | 🔴 Alta |
| BUG-004 | Vagas aceita negativo/zero/decimal | 🟡 Média |
| BUG-005 | URL de imagem sem validação | 🟡 Média |
| BUG-006 | Tipo "Selecione..." aceito no cadastro | 🟡 Média |
| BUG-007 | Dados de campo condicional persistem | 🟢 Baixa |
| BUG-008 | Duplicação de ID possível | 🟢 Baixa |
