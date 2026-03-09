# Respostas às Questões Analíticas — Desafio QA Beedoo 2026

---

## 1. Análise de Bug

**Cenário:** Erro 404 ao tentar acessar um curso recém-criado via URL direta

### Bug identificado

Ao tentar acessar a rota `/new-course` diretamente no navegador (ex.: colar a URL ou dar F5 na página), o Netlify retorna uma página de erro 404 ("Page not found") em vez de carregar a aplicação.

### Passos para reproduzir

1. Acessar a aplicação em `https://creative-sherbet-a51eac.netlify.app/`
2. Navegar até "Cadastrar curso" pelo menu
3. Copiar a URL `https://creative-sherbet-a51eac.netlify.app/new-course`
4. Abrir uma nova aba e colar a URL
5. Observar o erro 404

### Gravidade

**Alta** — impede o usuário de acessar a funcionalidade de cadastro caso compartilhe ou marque o link diretamente nos favoritos. Também quebra o fluxo ao usar o botão "voltar" do navegador após redirecionamento.

### Possíveis causas técnicas

A aplicação usa Vue Router em modo **HTML5 History (pushState)**. Nesse modo, o servidor precisa redirecionar todas as rotas para o `index.html`, deixando o Vue Router resolver a rota no cliente.

O Netlify exige um arquivo `_redirects` na pasta `public/` ou uma entrada `netlify.toml` com a regra:

```
/* /index.html 200
```

Sem essa configuração, ao acessar `/new-course` diretamente, o Netlify tenta encontrar um arquivo físico nesse caminho — e como não existe, retorna 404.

---

## 2. Identificação de Vulnerabilidades

### Vulnerabilidade 1 — Ausência de sanitização de entrada (XSS Stored)

**Por que pode ocorrer:** O campo "Nome do curso" aceita qualquer string. Se o valor for renderizado com `innerHTML` (o que ocorre no código: `innerHTML: e.course.name`), scripts injetados podem ser executados no browser de outro usuário.

**Como identificar durante os testes:** Cadastrar um curso com nome `<img src=x onerror=alert('XSS')>` e verificar se o alerta dispara na listagem.

---

### Vulnerabilidade 2 — Manipulação direta do localStorage (Privilege Escalation / Data Tampering)

**Por que pode ocorrer:** Todos os dados são armazenados no `localStorage` sem nenhuma assinatura, criptografia ou token de integridade. Qualquer usuário pode abrir o console do navegador e modificar, inserir ou excluir registros diretamente.

**Como identificar durante os testes:**
1. Abrir o DevTools → Application → LocalStorage
2. Editar manualmente o JSON `@beedoo-qa-tests/courses`
3. Verificar que as alterações são refletidas na interface sem nenhuma validação

---

### Vulnerabilidade 3 — URL de imagem de capa sem validação (SSRF / Open Redirect potencial)

**Por que pode ocorrer:** O campo "URL da imagem de capa" aceita qualquer string e a renderiza como `src` de uma tag `<img>`. Um atacante poderia:
- Usar URLs de terceiros para rastrear acessos (pixel tracking)
- Injetar URLs de recursos maliciosos
- Em sistemas com back-end, explorar SSRF se a URL fosse processada server-side

**Como identificar durante os testes:** Cadastrar um curso com `cover = "https://attacker.com/pixel.png"` e verificar se uma requisição é feita para o domínio externo ao carregar a lista.

---

## 3. Análise de Especificação

Antes de iniciar os testes de uma nova funcionalidade no módulo de cursos, os 3 pontos críticos que eu esclareceria com o time de produto/desenvolvimento:

### Ponto 1 — Quais campos são obrigatórios e quais são suas regras de validação?

**Por que é importante:** Sem uma especificação clara, fica impossível saber se um campo vazio é um bug ou comportamento esperado. Na aplicação atual, nenhum campo possui validação, mas não há spec dizendo quais são obrigatórios.

**Impacto na qualidade:** Sem essa definição, testes podem aprovar comportamentos incorretos ou reprovar comportamentos intencionais, gerando ruído no processo de QA.

### Ponto 2 — Como deve funcionar a persistência de dados? (localStorage, API REST, banco de dados?)

**Por que é importante:** A camada de persistência define toda a estratégia de testes de integração. Se for localStorage, os dados são voláteis por design. Se for uma API, precisamos testar autenticação, erros de rede, timeouts e consistência.

**Impacto na qualidade:** Testes mal direcionados à camada errada geram falsos positivos e deixam lacunas em pontos críticos da aplicação.

### Ponto 3 — Qual é o comportamento esperado ao excluir um curso? Existe confirmação? O dado é permanentemente removido?

**Por que é importante:** O fluxo de exclusão atual está completamente quebrado (BUG-02). Para testar corretamente, preciso saber: há dialog de confirmação? Soft delete ou hard delete? O que acontece com cursos com vagas já preenchidas?

**Impacto na qualidade:** Sem essa clareza, não é possível verificar se o comportamento é um bug ou uma feature incompleta, e os critérios de aceite ficam ambíguos.

---

## 4. Investigação de Defeitos

### Como avaliar se o erro vem da funcionalidade testada ou de outra parte do sistema

Minha abordagem de investigação seria em camadas:

**1. Isolar o escopo**
Verificar se o comportamento ocorre apenas nessa funcionalidade ou também em outras. Se o bug de "submit sem validação" ocorre em todos os formulários da aplicação, provavelmente é um problema de configuração global (ex.: a biblioteca de validação não está inicializada). Se ocorre só em um formulário, é um problema localizado.

**2. Analisar o console e as network requests**
Abrir o DevTools e verificar:
- Erros de JavaScript no console
- Requisições disparadas (ou não) ao submeter
- Respostas de API (status codes, payloads)

**3. Verificar o estado do dado**
Checar o localStorage (ou banco) antes e depois da ação para confirmar se o problema é na escrita, na leitura ou na renderização.

**4. Analisar o código-fonte**
Como neste desafio, inspecionar o JS compilado para entender o comportamento real. No BUG-02 (delete não funciona), a análise do código revelou que `onClick: emit` passava a função `emit` diretamente ao botão, sem chamar `emit("delete")` — um bug de lógica isolado no componente `CourseCard`, não no IndexPage.

**5. Testar com dados controlados**
Reproduzir com entradas mínimas e conhecidas para eliminar variáveis e confirmar a causa raiz.

---

## 5. Priorização de Testes (15 minutos)

Se tivesse apenas 15 minutos para testar antes de ir para produção, executaria:

### Teste 1 — Fluxo principal de cadastro (5 min)
Preencher todos os campos corretamente e verificar se o curso aparece na lista. É o caminho feliz e o mais crítico: se isso falha, tudo falha.

**Por quê:** É a funcionalidade core do módulo. Um bug no caminho principal bloqueia 100% dos usuários.

### Teste 2 — Submissão com campos vazios (5 min)
Tentar cadastrar sem preencher nenhum campo. Verificar se há validação ou se o dado inválido é salvo.

**Por quê:** Dados inválidos no sistema causam falhas em cascata — relatórios quebrados, erros de renderização, inconsistências que são difíceis de rastrear depois.

### Teste 3 — Exclusão de curso (5 min)
Cadastrar um curso e tentar excluí-lo. Confirmar que some da lista e do armazenamento.

**Por quê:** Operações de escrita irreversíveis (ou que deveriam ser) têm alto impacto. Um delete que não funciona é tão crítico quanto um que apaga dados errados.

---

## 6. Reflexão sobre o Desafio

### Bug mais interessante encontrado

O **BUG-02 (delete não funciona)** foi o mais interessante. A interface está completa — botão vermelho com ícone de lixeira, label "Excluir curso" —, mas internamente o código passa a função `emit` do Vue diretamente como `onClick`, ao invés de criar um handler que chame `emit("delete")`. O botão dispara um evento cujo nome é o objeto `MouseEvent`, que ninguém ouve. É um bug silencioso: não há erro no console, nenhuma mensagem de falha — apenas o curso que permanece lá, imperturbável.

### Cenário de teste mais difícil de pensar

O **cenário de colisão de IDs (BUG-09)** foi o mais difícil de identificar porque depende de uma sequência de operações que o delete quebrado torna impossível de testar na prática. Só foi possível detectar via análise de código — o ID é `courses.length + 1`, o que cria a condição de colisão assim que a deleção funcionar corretamente. É o tipo de bug que passa despercebido em testes manuais e só aparece em produção, quando dados começam a sobrescrever outros silenciosamente.

### O que faria diferente com mais tempo

1. **Criar testes de contrato** — verificar a estrutura do objeto salvo no localStorage contra um schema definido (ex.: campos obrigatórios, tipos esperados)
2. **Testes de acessibilidade** — verificar se os campos têm labels acessíveis, se o formulário é navegável por teclado
3. **Testes de responsividade** — o Quasar tem suporte a mobile; verificar se o layout se comporta corretamente em diferentes resoluções
4. **Testes de performance** — verificar comportamento com muitos cursos cadastrados (paginação, renderização)
5. **Explorar mais a fundo a ausência de autenticação** — o sistema não tem login; em um ambiente real, isso significaria que qualquer pessoa pode cadastrar ou "excluir" cursos
