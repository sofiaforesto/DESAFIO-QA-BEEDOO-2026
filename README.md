# Desafio QA — Beedoo 2026

**Candidata:** Sofia Foresto
**Aplicação testada:** https://creative-sherbet-a51eac.netlify.app/
**Prazo:** até 11/03/2026 às 23:59

---

## 1. Análise Inicial da Aplicação

### Objetivo da Aplicação

A aplicação é um ambiente de teste para QA voltado ao **módulo de gerenciamento de cursos**. Ela simula um sistema institucional onde é possível:

- **Cadastrar cursos** com informações como nome, descrição, instrutor, imagem de capa, datas, número de vagas e tipo (presencial ou online)
- **Listar cursos** cadastrados em formato de cards
- **Excluir cursos** por meio de um botão no card

A aplicação utiliza **Vue.js 3 + Quasar Framework** no front-end e **localStorage** como mecanismo de persistência de dados (sem back-end real). As rotas são gerenciadas pelo Vue Router em modo SPA (Single Page Application), hospedada no Netlify.

### Principais Fluxos Disponíveis

| # | Fluxo | Caminho |
|---|-------|---------|
| 1 | Listar cursos cadastrados | `/` (Home) |
| 2 | Cadastrar novo curso | `/new-course` |
| 3 | Excluir curso da lista | Botão "Excluir curso" no card |

### Fluxo de Cadastro (campos identificados)

- **Nome do curso** (texto, obrigatório)
- **Descrição do curso** (textarea, obrigatório)
- **Instrutor** (texto, obrigatório)
- **URL da imagem de capa** (texto, obrigatório)
- **Data de início** (date)
- **Data de fim** (date)
- **Número de vagas** (number)
- **Tipo de curso** (select: Presencial / Online)
  - Se **Online** → exibe campo adicional: **Link de inscrição**
  - Se **Presencial** → exibe campo adicional: **Endereço**

### Pontos Mais Críticos para Teste

1. **Validação do formulário** — campos obrigatórios, formatos válidos, limites
2. **Fluxo de exclusão** — se o botão realmente remove o curso
3. **Persistência de dados** — se o localStorage é corretamente atualizado após cadastro e exclusão
4. **Acesso às rotas** — se a navegação funciona via URL direta e via SPA
5. **Campos condicionais** — se Link/Endereço aparecem corretamente por tipo
6. **Consistência de datas** — data de início deve ser anterior à data de fim
7. **Regras de negócio** — número de vagas positivo, tipo obrigatório

---

## 2. Cenários e Casos de Teste

Os casos de teste estão documentados na planilha do Google Sheets:

📊 **[Casos de Teste — Google Sheets](https://docs.google.com/spreadsheets/d/1pkiP5jzVziEoXLZSwlOSgP-rk9yFM7GPUUi-2xUpVVU/edit)**

> *(Substituir pelo link real após criação da planilha)*

### Resumo dos Cenários

| ID | Cenário | Tipo | Resultado |
|----|---------|------|-----------|
| CT01 | Cadastrar curso com todos os campos válidos (Online) | Positivo | ✅ Passou |
| CT02 | Cadastrar curso com todos os campos válidos (Presencial) | Positivo | ✅ Passou |
| CT03 | Listar cursos após cadastro | Positivo | ✅ Passou |
| CT04 | Campos condicionais: Link para Online, Endereço para Presencial | Positivo | ✅ Passou |
| CT05 | Submeter formulário com todos os campos vazios | Negativo | 🐛 BUG |
| CT06 | Cadastrar com data de início maior que data de fim | Negativo | 🐛 BUG |
| CT07 | Cadastrar com número de vagas negativo (-5) | Negativo | 🐛 BUG |
| CT08 | Cadastrar sem selecionar tipo de curso ("Selecione...") | Negativo | 🐛 BUG |
| CT09 | Excluir curso da lista | Positivo | 🐛 BUG |
| CT10 | Acessar /new-course diretamente pela URL do navegador | Negativo | 🐛 BUG |
| CT11 | Verificar título da aplicação | Positivo | 🐛 BUG |
| CT12 | URL de imagem de capa com string inválida (não URL) | Negativo | 🐛 BUG |

---

## 3. Bugs Encontrados

### BUG-01 — Formulário aceita submissão com campos vazios (sem validação)

**Severidade:** Crítica
**Passos para reproduzir:**
1. Acessar a aplicação em https://creative-sherbet-a51eac.netlify.app/
2. Clicar em "Cadastrar curso"
3. Não preencher nenhum campo
4. Clicar no botão "CADASTRAR CURSO"

**Resultado atual:** O curso é salvo no localStorage com todos os campos vazios e o usuário é redirecionado para a lista
**Resultado esperado:** O formulário deve exibir mensagens de validação e impedir o cadastro
**Evidência:** `evidencias/screenshots/T01-submit-vazio-resultado.png`

---

### BUG-02 — Botão "Excluir curso" não remove o curso

**Severidade:** Crítica
**Passos para reproduzir:**
1. Cadastrar um curso qualquer
2. Na lista de cursos, clicar no botão "Excluir curso"

**Resultado atual:** O curso permanece na lista. O localStorage não é modificado.
**Resultado esperado:** O curso deve ser removido da lista e do localStorage
**Causa técnica (análise do código-fonte):** O `onClick` do botão está recebendo a função `emit` do Vue diretamente (`onClick: emit`), que ao ser invocada com o evento de clique como argumento tenta emitir um evento cujo nome é o objeto MouseEvent. Nenhum handler de deleção é disparado.
**Evidência:** `evidencias/screenshots/T05-bug-delete-nao-remove.png`

---

### BUG-03 — Datas invertidas são aceitas (início posterior ao fim)

**Severidade:** Alta
**Passos para reproduzir:**
1. Ir para "Cadastrar curso"
2. Preencher todos os campos
3. Data de início: 31/12/2026
4. Data de fim: 01/01/2026 (anterior ao início)
5. Clicar em "CADASTRAR CURSO"

**Resultado atual:** Curso cadastrado com startDate=2026-12-31 e endDate=2026-01-01
**Resultado esperado:** Formulário deve validar e impedir que data de fim seja anterior à data de início
**Evidência:** `evidencias/screenshots/T03-bug-datas-aceitas.png`

---

### BUG-04 — Número de vagas aceita valores negativos

**Severidade:** Alta
**Passos para reproduzir:**
1. Ir para "Cadastrar curso"
2. Preencher todos os campos
3. Número de vagas: -5
4. Clicar em "CADASTRAR CURSO"

**Resultado atual:** Curso cadastrado com numberOfVagas=-5
**Resultado esperado:** Formulário deve exigir valor mínimo de 1 no campo de vagas
**Evidência:** `evidencias/screenshots/T04-bug-vagas-aceitas.png`

---

### BUG-05 — Acesso direto à URL /new-course retorna 404

**Severidade:** Alta
**Passos para reproduzir:**
1. Abrir o navegador
2. Navegar diretamente para https://creative-sherbet-a51eac.netlify.app/new-course

**Resultado atual:** Página exibe "Page not found" (erro 404 do Netlify)
**Resultado esperado:** A página de cadastro deve carregar normalmente
**Causa técnica:** O Netlify não possui arquivo `_redirects` ou `netlify.toml` configurado para redirecionar todas as rotas ao `index.html` (necessário para SPAs com Vue Router)
**Evidência:** `evidencias/screenshots/T06-url-direta-404.png`

---

### BUG-06 — Tipo de curso "Selecione..." (vazio) é aceito no cadastro

**Severidade:** Média
**Passos para reproduzir:**
1. Preencher todos os campos do formulário
2. Deixar "Tipo de curso" no valor padrão "Selecione..."
3. Clicar em "CADASTRAR CURSO"

**Resultado atual:** Curso salvo com type.label="" e type.value=""
**Resultado esperado:** O campo "Tipo de curso" deve ser obrigatório; "Selecione..." não deve ser uma opção válida para submissão
**Evidência:** `evidencias/screenshots/T09-bug-sem-tipo-aceito.png`

---

### BUG-07 — URL de imagem de capa aceita qualquer string (sem validação de URL)

**Severidade:** Média
**Passos para reproduzir:**
1. No campo "Url da imagem de capa", digitar texto inválido: `não é uma url`
2. Cadastrar o curso

**Resultado atual:** Curso salvo com o texto inválido como cover. O card na lista exibe a imagem quebrada.
**Resultado esperado:** O campo deve validar se o conteúdo é uma URL válida

---

### BUG-08 — Typo no título da aplicação

**Severidade:** Baixa
**Local:** Barra de navegação superior
**Resultado atual:** "Beedoo QA Chalenge"
**Resultado esperado:** "Beedoo QA Challenge" (falta o 'd')
**Evidência:** `evidencias/screenshots/T07-typo-chalenge.png`

---

### BUG-09 — Geração de ID com possibilidade de colisão (análise de código)

**Severidade:** Alta (latente, depende do funcionamento do delete)
**Causa técnica:** O ID do novo curso é calculado como `courses.length + 1`. Se cursos fossem deletados corretamente, seria possível gerar IDs duplicados. Exemplo: cursos [1, 2, 3] → deletar ID 2 → nova lista [1, 3] com length=2 → próximo ID = 3 (colisão com curso existente).
**Resultado esperado:** Usar UUID ou auto-increment seguro para garantir unicidade dos IDs

---

## 4. Evidências

As evidências de execução dos testes estão disponíveis na pasta `evidencias/screenshots/`:

| Arquivo | Teste |
|---------|-------|
| `T01-form-vazio.png` | Formulário antes do submit vazio |
| `T01-submit-vazio-resultado.png` | Lista após submit com campos vazios (BUG-01) |
| `T02-form-valido-online.png` | Formulário Online preenchido corretamente |
| `T02-lista-apos-cadastro.png` | Lista após cadastro válido |
| `T03-datas-invertidas-form.png` | Formulário com datas invertidas |
| `T03-bug-datas-aceitas.png` | Lista mostrando curso com datas invertidas aceito (BUG-03) |
| `T04-vagas-negativas-form.png` | Formulário com vagas negativas |
| `T04-bug-vagas-aceitas.png` | Lista mostrando curso com vagas negativas aceito (BUG-04) |
| `T05-antes-delete.png` | Lista antes de tentar excluir |
| `T05-bug-delete-nao-remove.png` | Lista após clicar em excluir — curso permanece (BUG-02) |
| `T06-url-direta-404.png` | Acesso direto à /new-course retorna 404 (BUG-05) |
| `T07-typo-chalenge.png` | Typo "Chalenge" na toolbar (BUG-08) |
| `T08-campo-link-online.png` | Campo "Link de inscrição" visível para tipo Online |
| `T08-campo-endereco-presencial.png` | Campo "Endereço" visível para tipo Presencial |
| `T09-bug-sem-tipo-aceito.png` | Curso sem tipo aceito no cadastro (BUG-06) |

---

## 5. Respostas às Questões Analíticas

As respostas detalhadas estão em [`docs/respostas-analiticas.md`](docs/respostas-analiticas.md)

---

## 6. Testes Automatizados

Stack: **Python 3 + pytest + Playwright (Chromium headless)**

### Como executar

```bash
pip install playwright pytest pytest-playwright
python -m playwright install chromium
pytest tests/test_beedoo.py -v
```

### Resultado esperado

```
PASSED  tests/test_beedoo.py::TestCadastroCurso::test_cadastro_valido_online
PASSED  tests/test_beedoo.py::TestCadastroCurso::test_campos_condicionais_online
PASSED  tests/test_beedoo.py::TestCadastroCurso::test_campos_condicionais_presencial
FAILED  tests/test_beedoo.py::TestCadastroCurso::test_validacao_campos_obrigatorios
FAILED  tests/test_beedoo.py::TestCadastroCurso::test_validacao_datas_invertidas
FAILED  tests/test_beedoo.py::TestCadastroCurso::test_validacao_vagas_negativas
FAILED  tests/test_beedoo.py::TestCadastroCurso::test_validacao_tipo_obrigatorio
FAILED  tests/test_beedoo.py::TestListagem::test_excluir_curso
FAILED  tests/test_beedoo.py::TestNavegacao::test_url_direta_new_course
FAILED  tests/test_beedoo.py::TestNavegacao::test_titulo_sem_typo
```

---

## Estrutura do Repositório

```
DESAFIO-QA-BEEDOO-2026/
├── README.md                          # Este arquivo
├── requirements.txt
├── conftest.py
├── tests/
│   └── test_beedoo.py                 # Testes automatizados
├── docs/
│   └── respostas-analiticas.md        # Questões analíticas respondidas
└── evidencias/
    └── screenshots/                   # Evidências de execução
        ├── T01-form-vazio.png
        ├── T01-submit-vazio-resultado.png
        └── ...
```
