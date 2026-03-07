# Etapa 2 — Análise e Tomada de Decisão

> Desafio QA Beedoo 2026 | Sofia Foresto

---

## 1. Análise de Bug — Erro 404 ao acessar curso recém-criado

### Bug identificado

Ao tentar acessar diretamente a URL de um curso recém-criado (por exemplo, `/courses/3`), o sistema retorna erro 404 — página não encontrada — mesmo que o curso esteja visível na listagem.

### Passos para reproduzir

1. Acessar `/new-course` e cadastrar um novo curso com dados válidos
2. Observar que o curso aparece na listagem em `/`
3. Tentar acessar diretamente a URL de detalhe do curso (ex.: `/courses/3`)
4. Resultado: página 404 exibida

### Gravidade

**Alta.** Embora a rota de detalhe por ID possa não existir intencionalmente no MVP atual, do ponto de vista do usuário é esperado poder acessar o curso individualmente. Se existir alguma lógica de redirecionamento ou compartilhamento de link, a funcionalidade estará completamente quebrada.

### Possíveis causas técnicas

1. **Rota não definida no router:** A aplicação usa Vue Router com apenas duas rotas (`/` e `/new-course`). Nenhuma rota dinâmica como `/courses/:id` foi implementada, então qualquer acesso a essa URL cai no handler `/:catchAll(.*)` que exibe o componente de 404.

2. **ID não utilizado para navegação:** O ID gerado no cadastro é salvo no localStorage, mas não é utilizado para criar uma rota de detalhe. A arquitetura atual não prevê visualização individual por ID.

3. **SPA sem fallback configurado no servidor:** Em aplicações Single Page Application (SPA) hospedadas em servidores como Netlify, sem a configuração de rewrite de todas as rotas para `index.html`, o acesso direto a uma URL dinâmica resulta em 404 no nível do servidor, antes mesmo de o Vue Router processar a rota.

4. **Dados apenas em localStorage:** Mesmo que a rota existisse, os dados estão no localStorage do navegador — um acesso de outro dispositivo ou em aba anônima resultaria em um curso "vazio" ou erro de carregamento, pois o recurso não existe no backend.

---

## 2. Identificação de Vulnerabilidades

### Vulnerabilidade 1 — Cross-Site Scripting (XSS) via campos do formulário

**Por que pode ocorrer:**
Os campos do formulário (nome, descrição, instrutor, etc.) não possuem validação nem sanitização de entrada. Um usuário mal-intencionado poderia inserir código JavaScript em tags HTML como `<script>alert('xss')</script>` ou `<img src=x onerror=alert(1)>`. Se o conteúdo for renderizado com `innerHTML` sem escape (ao invés de interpolação segura), o script seria executado para qualquer usuário que visualizar a listagem.

**Como identificar durante os testes:**
- Inserir payloads XSS conhecidos em campos de texto: `<script>alert('XSS')</script>`, `<img src=x onerror="alert(document.cookie)">`
- Cadastrar o curso e verificar se o alerta é disparado na listagem
- Inspecionar o HTML renderizado para ver se o conteúdo foi escapado ou renderizado como HTML bruto
- No caso da aplicação testada, Vue.js escapa por padrão interpolações `{{ }}`, o que mitiga esse vetor — mas campos que usam `v-html` seriam vulneráveis

---

### Vulnerabilidade 2 — Manipulação direta do localStorage (Client-Side Data Tampering)

**Por que pode ocorrer:**
Toda a lógica de dados da aplicação está no `localStorage` do navegador, acessível e modificável por qualquer pessoa via console do DevTools. Um usuário pode:
- Alterar o ID de um curso para sobrescrever outro
- Modificar o número de vagas para um valor absurdo (ex.: 999999)
- Injetar estruturas de dados malformadas que quebram o parse do JSON
- Duplicar ou apagar registros sem passar pelo fluxo da aplicação

**Como identificar durante os testes:**
- Abrir DevTools → Application → Local Storage → `@beedoo-qa-tests/courses`
- Editar manualmente o JSON (ex.: alterar `numberOfVagas` para `-1` ou injetar `"__proto__": {}`)
- Recarregar a aplicação e observar o comportamento com dados adulterados
- Testar o que acontece ao injetar JSON inválido (ex.: `null`, `"texto"`, `[]` corrompido)

---

### Vulnerabilidade 3 — Ausência de controle de acesso e autenticação

**Por que pode ocorrer:**
A aplicação não possui nenhum mecanismo de autenticação ou autorização. Qualquer pessoa que acesse a URL pode:
- Cadastrar cursos ilimitadamente (sem limite de rate ou autenticação)
- Excluir cursos de outras pessoas (se houvesse backend real)
- Preencher a aplicação com dados spam ou conteúdo impróprio
- A chamada DELETE para `/test-api/courses/1` é feita sem nenhum token de autenticação no header

**Como identificar durante os testes:**
- Verificar os headers das requisições no DevTools → Network: checar se há `Authorization`, `Bearer token` ou `Cookie` de sessão
- Tentar acessar a aplicação em uma aba anônima ou de outro dispositivo e verificar se é possível cadastrar/excluir livremente
- Usar ferramentas como Postman ou cURL para enviar requisições DELETE diretamente à API sem nenhum header de autenticação e verificar se a operação é aceita

---

### Vulnerabilidade Bônus — Injeção via URL da imagem de capa (SSRF potencial)

**Por que pode ocorrer:**
O campo de URL da imagem não valida o protocolo nem o domínio. Se o backend eventualmente processar essa URL (ex.: fazer download da imagem para um CDN próprio), um usuário poderia informar endereços internos como `http://169.254.169.254/latest/meta-data/` (AWS metadata endpoint), caracterizando um ataque SSRF (Server-Side Request Forgery).

**Como identificar durante os testes:**
- Inserir URLs de endpoints internos ou suspeitos no campo de capa
- Verificar se a aplicação faz alguma requisição a esses endereços (analisar tráfego de rede)
- No cenário atual (apenas localStorage), o risco é baixo — mas deve ser documentado para quando houver backend real

---

## 3. Análise de Especificação — Pontos Críticos a Esclarecer

### Ponto 1 — Quais campos são obrigatórios e quais são opcionais?

**Por que é importante:**
A especificação atual não define claramente quais campos devem ser obrigatórios para o cadastro de um curso. Sem essa definição, é impossível saber se a ausência de validação é um bug ou uma decisão de produto ("todos os campos são opcionais").

**Impacto na qualidade:**
Se começarmos a testar sem essa definição, podemos abrir bugs que não são bugs (falso positivo) ou deixar de abrir bugs reais (falso negativo). A regra de obrigatoriedade é a base dos testes de validação — sem ela, os testes de campos ficam sem critério claro de aprovação/reprovação.

**Pergunta ao time:** "Quais campos são obrigatórios para salvar um curso? Existe alguma regra de negócio que define o conjunto mínimo de informações válidas?"

---

### Ponto 2 — Como funciona a regra de negócio para os campos condicionais (Online vs Presencial)?

**Por que é importante:**
O campo "Link de inscrição" aparece apenas para cursos Online, e "Endereço" apenas para Presenciais. Precisamos saber:
- Esses campos condicionais são obrigatórios dentro do seu tipo?
- O que deve acontecer com os dados do campo não exibido — devem ser limpos ao trocar o tipo?
- Um curso Online sem link de inscrição é válido?

**Impacto na qualidade:**
Sem essa clareza, o BUG-007 (dados condicionais persistindo) pode ser interpretado de formas diferentes pelo time — para produto pode ser irrelevante, para dev pode ser um comportamento intencional de "rascunho". Esclarecer evita retrabalho.

**Pergunta ao time:** "Campos condicionais por tipo (endereço/link) são obrigatórios? Ao trocar o tipo, os dados preenchidos anteriormente devem ser descartados ou preservados?"

---

### Ponto 3 — Como deve funcionar a exclusão de um curso? Existe confirmação ou soft delete?

**Por que é importante:**
O fluxo atual de exclusão está quebrado (BUG-002). Antes de testar a correção, precisamos entender:
- A exclusão é definitiva (hard delete) ou o curso vai para uma "lixeira" (soft delete)?
- Deve haver uma confirmação ("Tem certeza que deseja excluir?") antes da ação?
- A exclusão deve ser imediata na tela ou requer recarregamento?
- Existe alguma regra de negócio que impeça a exclusão (ex.: curso com vagas preenchidas)?

**Impacto na qualidade:**
Sem essa especificação, ao testar a correção do bug, podemos validar um comportamento diferente do que o produto espera. Por exemplo: aprovar uma exclusão sem confirmação quando o produto esperava um modal de confirmação.

**Pergunta ao time:** "Como deve ser o fluxo completo de exclusão? Hard delete imediato ou com confirmação? Existe alguma restrição para cursos que não podem ser excluídos?"

---

## 4. Investigação de Defeitos — Isolando a Causa do Erro

Quando identifico um erro, sigo um processo de investigação em camadas para isolar onde o problema realmente está:

### Passo 1 — Reproduzir com dados mínimos
Tento reproduzir o bug com o menor conjunto de ações possível. Se o erro ocorre ao cadastrar um curso com 10 campos preenchidos, começo testando com apenas 1 campo para ver se o problema persiste. Isso ajuda a identificar se o erro é causado por um campo específico, uma combinação de valores, ou é genérico.

### Passo 2 — Isolar a camada
Verifico em qual camada o erro ocorre:
- **Frontend (UI):** O problema está na renderização? Testando com DevTools aberto e inspecionando o DOM
- **Lógica de negócio (JS):** Erro aparece no Console do browser? Stack trace aponta para qual função?
- **Comunicação com API:** Erro na requisição? Verifico no DevTools → Network a requisição enviada, o payload e a resposta
- **Backend:** A API retorna código de erro? 400 (dado inválido), 500 (erro interno), 404 (rota não existe)?
- **Banco de dados / Storage:** No caso da aplicação Beedoo (localStorage), verifico diretamente o estado do storage antes e depois da ação

### Passo 3 — Verificar o estado antes e depois
Anoto o estado do sistema antes de executar a ação e verifico o que mudou (ou não mudou) após. Por exemplo: no BUG-002 (exclusão), verifico o localStorage antes de clicar em excluir e depois — se o item ainda estiver lá, o problema está na lógica de remoção do storage, não na API.

### Passo 4 — Testar em ambientes diferentes
Verifico se o erro ocorre em outros browsers, em aba anônima, ou em outro dispositivo. Erros que só ocorrem em um browser específico indicam problema de compatibilidade. Erros que só ocorrem na primeira vez indicam problema de cache ou estado inicial.

### Passo 5 — Cruzar com outras funcionalidades
Avalio se outras funcionalidades relacionadas apresentam o mesmo comportamento. Se o problema é na lógica de geração de ID (BUG-008), verifico se a listagem, o cadastro e a exclusão compartilham a mesma função de geração — se sim, o bug pode afetar os três fluxos.

### Passo 6 — Documentar e comunicar
Com a causa isolada, documento:
- Onde exatamente o problema está (componente, função, linha se possível)
- Se é um bug novo ou regressão (funcionava antes?)
- Se impacta apenas o fluxo testado ou outros módulos também

---

## 5. Priorização de Testes — 15 Minutos para Produção

Com apenas 15 minutos, foco nos testes de maior risco e maior impacto para o usuário final. Escolheria:

### Teste 1 — Cadastro completo de um curso válido (Fluxo Feliz)
**Por quê primeiro:** Se o fluxo principal não funciona, nada mais importa. Preciso garantir que um usuário consegue cadastrar um curso com dados válidos, ver a confirmação de sucesso e encontrar o curso na listagem. É o smoke test essencial — se falhar, a funcionalidade não pode ir para produção.

**O que verifico:** Preencher todos os campos com dados válidos → clicar em cadastrar → ver mensagem de sucesso → conferir se o curso aparece na listagem com todos os dados corretos.

---

### Teste 2 — Tentativa de cadastro com campos obrigatórios vazios (Validação)
**Por quê segundo:** A ausência de validação é o bug de mais alto impacto na qualidade dos dados. Em produção, sem validação, a base de dados (ou localStorage) ficará cheia de registros inúteis. Testar se há algum bloqueio mínimo antes de liberar é crítico para a integridade do sistema.

**O que verifico:** Não preencher nenhum campo → clicar em cadastrar → verificar se há mensagens de validação ou se o cadastro passa. Se passar com campos vazios, é um bloqueador para produção.

---

### Teste 3 — Exclusão de curso
**Por quê terceiro:** A exclusão é a única operação destrutiva disponível e, se estiver quebrada (como identificamos), o usuário ficará preso com cursos que não consegue remover. Além disso, um bug de exclusão que usa ID hardcoded pode estar excluindo o curso errado em produção — risco alto de perda de dados.

**O que verifico:** Cadastrar um curso → excluir → confirmar que sumiu da listagem → recarregar e confirmar que não voltou.

---

**Lógica da priorização:** Os 3 testes cobrem os 3 verbos fundamentais da funcionalidade — Create, Read e Delete. Se qualquer um deles falhar em produção, o impacto é imediato e visível para todos os usuários. Validações e edge cases podem ser adicionados em ciclos de teste posteriores, mas o fluxo CRUD básico deve estar funcionando antes do go-live.

---

## 6. Reflexão sobre o Desafio

### Bug mais interessante encontrado

O **BUG-002 (exclusão fake)** foi o mais interessante. À primeira vista, ao clicar em "Excluir curso" e ver a notificação verde "Curso excluído com sucesso!", qualquer usuário — e qualquer testador desatento — acreditaria que funcionou. O feedback visual é completamente enganoso.

O que torna esse bug fascinante é que ele tem dois problemas em um: a chamada DELETE usa um ID hardcoded (`/test-api/courses/1`) — ou seja, sempre tenta deletar o mesmo curso, independentemente de qual você clicou — e mesmo que a API respondesse com sucesso, o localStorage não é atualizado. O sistema celebra uma operação que não aconteceu. É um exemplo claro de como um sistema pode parecer funcionar e não funcionar ao mesmo tempo.

Só foi possível identificá-lo indo além da interface: analisando o código-fonte JavaScript para entender o comportamento real por baixo da notificação.

---

### Cenário de teste mais difícil de pensar

O **CT-007 (campo condicional persistindo dados — BUG-007)** foi o mais difícil de elaborar. É um cenário de estado interno invisível: o usuário preenche um campo, muda de ideia, troca o tipo do curso e o campo some da tela — mas os dados continuam no objeto de dados. Nenhuma evidência visual indica que o dado ainda está lá.

Pensar nesse cenário exigiu raciocinar sobre o estado interno do componente Vue, não apenas sobre o que está visível na interface. É o tipo de bug que só aparece quando você começa a questionar "o que está acontecendo por baixo do que eu estou vendo?" — e essa é a mentalidade que diferencia um teste superficial de uma análise de qualidade de verdade.

---

### O que faria diferente com mais tempo

1. **Testes automatizados com Cypress ou Playwright:** Criaria testes end-to-end automatizados para os fluxos principais, garantindo que qualquer nova versão da aplicação pudesse ser validada rapidamente sem execução manual.

2. **Testes de performance e estresse do localStorage:** Verificaria o comportamento com centenas de cursos cadastrados — o que acontece com a renderização, com o tempo de carregamento e com o tamanho do storage.

3. **Testes de compatibilidade cross-browser:** Executaria os mesmos cenários em Firefox, Safari e Edge para identificar diferenças de comportamento, especialmente nos campos de data (que têm comportamentos bem distintos entre browsers).

4. **Documentação de evidências mais rica:** Gravaria vídeos de cada cenário executado (não apenas prints) para facilitar a reprodução dos bugs pelo time de desenvolvimento.

5. **Mapeamento completo de acessibilidade (a11y):** Testaria a aplicação com leitor de tela e navegação por teclado para identificar barreiras de acessibilidade — especialmente nos campos do formulário e nos botões de ação.
