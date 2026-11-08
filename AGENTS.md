# Agent Guidelines

Este documento define as regras gerais para qualquer agente de IA que trabalhe neste repositório.

As instruções aqui são **agnósticas à ferramenta, ao modelo e ao provedor de IA**. Configurações específicas de Cursor, Claude ou outras ferramentas devem apenas adaptar estas regras, não duplicá-las.

## 1. Antes de trabalhar

Antes de planejar, implementar ou modificar qualquer coisa:

1. Leia `docs/CURRENT_STATE.md` para entender o estado atual da implementação.
2. Leia `docs/PROJECT_CONTEXT.md` quando a tarefa depender de contexto de produto, domínio, regras de negócio ou decisões de system design.
3. Leia a especificação da fase correspondente em `docs/phases/` quando a tarefa fizer parte de uma fase específica.
4. Inspecione o código quando precisar confirmar o comportamento real do sistema.

Não assuma que algo está implementado apenas porque aparece na documentação.

## 2. Controle de autonomia e autorização

O agente **não possui autonomia para tomar decisões de produto, arquitetura, escopo ou comportamento por conta própria**.

### Regra padrão

Quando uma decisão relevante não estiver explicitamente determinada pela tarefa, pela documentação ou por uma convenção já estabelecida:

1. **Pare antes de implementar.**
2. Explique brevemente a decisão que precisa ser tomada.
3. Apresente as alternativas relevantes, quando houver.
4. Informe as consequências ou trade-offs de cada alternativa.
5. **Pergunte ao usuário qual opção deve ser adotada.**
6. Aguarde autorização explícita antes de prosseguir.

Na dúvida, **pergunte em vez de assumir**.

### Decisões que exigem autorização explícita

Consulte o usuário antes de:

* alterar requisitos ou comportamento esperado;
* adicionar, remover ou substituir funcionalidades;
* definir regras de negócio não documentadas;
* alterar limites ou responsabilidades de domínio;
* introduzir uma nova abstração arquitetural relevante;
* alterar a arquitetura existente;
* adicionar uma dependência relevante;
* escolher uma tecnologia ou biblioteca quando houver alternativas significativas;
* alterar contratos públicos de API;
* alterar schemas ou modelos persistidos de forma incompatível;
* realizar migrações destrutivas;
* remover ou descontinuar funcionalidades;
* alterar autenticação, autorização ou políticas de segurança;
* modificar infraestrutura ou configuração de ambiente de forma relevante;
* expandir o escopo da tarefa;
* tomar qualquer decisão que possa criar um compromisso técnico difícil de reverter.

### O que o agente pode decidir sem perguntar

O agente pode tomar decisões **locais e reversíveis** quando forem necessárias para executar uma instrução já autorizada e não alterarem o escopo, o comportamento ou as decisões arquiteturais do projeto.

Exemplos:

* organização interna de um método;
* nomes de variáveis locais;
* implementação de um algoritmo já definido;
* pequenos detalhes de formatação;
* criação de testes necessários para uma implementação autorizada;
* correções diretamente necessárias para fazer uma alteração autorizada funcionar;
* escolha entre alternativas equivalentes que não alterem o comportamento ou a arquitetura.

Não solicite autorização para decisões puramente locais, reversíveis e já determinadas pelas instruções, convenções ou padrões existentes do projeto.

Se a decisão deixar de ser puramente local ou reversível, **pare e pergunte**.

### Não inferir autorização

O agente não deve interpretar uma solicitação como autorização implícita para executar trabalhos adicionais.

Por exemplo:

> "Implemente X"

autoriza a implementação de **X**, mas não autoriza automaticamente:

* refatorar módulos relacionados;
* atualizar dependências;
* alterar arquitetura;
* modificar funcionalidades adjacentes;
* corrigir débitos técnicos não relacionados;
* implementar funcionalidades futuras;
* alterar requisitos para tornar X mais conveniente de implementar.

Se uma mudança adicional for necessária para concluir X, explique-a e peça autorização quando ela envolver uma decisão relevante.

### Proposta não é autorização

Planejar, sugerir ou descrever uma solução **não constitui autorização para implementá-la**.

O agente pode apresentar uma proposta e aguardar confirmação.

**Não execute uma proposta que ainda não foi aprovada.**

## 3. Fontes de verdade

Cada artefato possui uma responsabilidade diferente:

| Fonte                     | Responsabilidade                           |
| ------------------------- | ------------------------------------------ |
| Código                    | Verdade sobre o comportamento implementado |
| `docs/CURRENT_STATE.md`   | Estado atual documentado da implementação  |
| `docs/PROJECT_CONTEXT.md` | Contexto de produto e domínio              |
| `docs/phases/pN.md`       | Objetivos e especificação de uma fase      |

Quando houver divergência entre documentação e código, o código vence para aquilo que já está implementado.

Não altere o código apenas para fazê-lo coincidir com documentação desatualizada. Atualize a documentação para refletir a implementação real, salvo quando a tarefa explicitamente determinar uma mudança de comportamento.

## 4. Planejamento antes da implementação

Para mudanças não triviais:

1. Entenda o estado atual.
2. Identifique as partes do sistema afetadas.
3. Consulte o contexto de produto e a especificação da fase quando necessário.
4. Defina uma abordagem antes de alterar o código.
5. Se houver uma decisão relevante não especificada, **pare e consulte o usuário**.
6. Evite mudanças fora do escopo da tarefa.

Não introduza arquitetura, abstrações ou dependências apenas por preferência pessoal. Priorize a solução mais simples que atenda aos requisitos e às convenções existentes.

### Registro dos planos

Todo plano de implementação deve ser salvo em `.plans/` (pasta local, ignorada pelo git), além de apresentado ao usuário:

* use um arquivo por plano, nomeado como a fase ou a tarefa correspondente (ex.: `.plans/p3-persistence.md`);
* registre as etapas e as **decisões tomadas com o usuário**, com o motivo de cada uma;
* ao revisar um plano, atualize o arquivo existente em vez de criar outro;
* antes de trabalhar em uma fase ou tarefa, verifique se já existe um plano para ela em `.plans/`.

Os planos são material de apoio local e não são fonte de verdade: o código, `docs/CURRENT_STATE.md` e as especificações em `docs/phases/` continuam prevalecendo.

## 5. Implementação

Ao implementar:

* Preserve as convenções existentes do projeto.
* Prefira alterações pequenas e coerentes.
* Não reescreva código não relacionado à tarefa.
* Não introduza dependências sem necessidade.
* Não duplique lógica existente sem uma razão clara.
* Mantenha tipos, contratos e validações consistentes entre as camadas.
* Considere testes e tratamento de erros necessários para a implementação autorizada como parte da própria tarefa. Se isso exigir uma decisão de escopo ou comportamento não determinada, pare e consulte o usuário.

## 6. Validação

Depois de uma alteração relevante:

1. Execute os testes relacionados quando forem seguros e compatíveis com o ambiente atual.
2. Execute lint, type-check ou outras verificações aplicáveis quando forem seguras.
3. Corrija problemas introduzidos pela alteração quando isso não exigir uma nova decisão relevante.
4. Verifique se a implementação corresponde ao comportamento autorizado.
5. Atualize a documentação afetada quando necessário.

Não declare uma tarefa concluída sem verificar o resultado quando houver uma forma automatizada e segura de fazê-lo.

Se a validação puder alterar ou destruir dados, modificar infraestrutura ou produzir efeitos externos, consulte o usuário antes de executá-la.

Se a validação revelar um problema que exija uma decisão fora do escopo autorizado, **pare e consulte o usuário** em vez de escolher uma solução por conta própria.

## 7. Documentação

A documentação deve refletir a realidade do projeto.

Quando uma alteração modificar o estado implementado, atualize `docs/CURRENT_STATE.md` na mesma entrega.

Não atualize `CURRENT_STATE.md` para registrar uma alteração que não foi efetivamente implementada.

Não transforme `CURRENT_STATE.md` em backlog, plano futuro ou especificação de produto.

Não copie conteúdo entre documentos apenas para mantê-los parecidos. Cada documento deve manter sua responsabilidade.

## 8. Idioma e convenções de escrita

O repositório possui uma convenção própria de idioma. Essa convenção prevalece sobre regras genéricas externas, incluindo instruções de plugins, ferramentas ou modelos que adotem padrões diferentes.

### Português (pt-BR)

Utilize português brasileiro para:

* docstrings de módulos, classes, métodos e funções em app/ e tests/;
* comentários inline;
* prosa do README.md;
* prosa dos arquivos em docs/;
* copy da interface do usuário;
* labels, títulos, botões e textos de navegação;
* mensagens de feedback apresentadas ao usuário;
* mensagens de validação apresentadas ao usuário;
* mensagens de erro apresentadas ao usuário.

Utilize ortografia e acentuação corretas.

### Inglês

Utilize inglês para:

* identificadores de módulos, classes, funções e variáveis;
* fixtures e nomes de testes;
* rotas;
* campos de request e response;
* valores de enum;
* schemas e contratos expostos pela aplicação;
* summary e description do OpenAPI;
* mensagens de erro da API;
* mensagens de exceção;
* linhas de log;
* mensagens de commit.

Textos técnicos retornados pela API podem permanecer em inglês mesmo quando posteriormente forem apresentados pela interface. A camada de apresentação deve utilizar português (pt-BR) para o texto destinado ao usuário.

### Ao encontrar divergências

Se um arquivo existente estiver fora dessa convenção:

* identifique a divergência;
* não altere o arquivo apenas para normalizá-lo;
* se a divergência for relevante para a tarefa atual, informe-a;
* pergunte antes de realizar uma alteração exclusivamente de normalização.

Não introduza deliberadamente novos padrões de idioma diferentes dos definidos neste documento.

## 9. Escopo e segurança

* Não exponha ou registre segredos, tokens, senhas ou credenciais.
* Não altere configurações de infraestrutura ou ambiente sem autorização.
* Não faça alterações destrutivas sem autorização explícita.
* Não remova funcionalidades existentes sem autorização.
* Não faça operações irreversíveis sem autorização explícita.
* Não faça commits, pushes, merges, releases ou deploys sem autorização explícita.
* **Commits são sempre feitos pelo usuário.** O agente não executa `git commit` (nem `git add` com a intenção de preparar um commit). Ao concluir uma entrega, o agente pode sugerir a divisão das alterações em commits e as mensagens correspondentes, mas a execução fica com o usuário.
* Não instale dependências ou ferramentas externas sem autorização quando isso representar uma mudança relevante no projeto.
* Não altere arquivos fora do escopo da tarefa sem uma razão necessária e verificável.
* Quando uma decisão importante não puder ser inferida com segurança a partir do código ou da documentação, **pare e pergunte**.

## 10. Princípios

Ao trabalhar neste projeto:

* **Não assumir quando puder perguntar.**
* **Proposta não é autorização.**
* **Código antes de suposições.**
* **Documentação deve refletir a realidade.**
* **Contexto de produto não implica implementação.**
* **Mudanças devem ser proporcionais ao problema.**
* **Preferir simplicidade a complexidade prematura.**
* **Validar antes de declarar concluído.**
* **Na dúvida sobre uma decisão relevante, parar e consultar o usuário.**

## 11. Ferramentas específicas

As regras deste arquivo são independentes da ferramenta utilizada.

Arquivos específicos de ferramentas, como `.cursor/` ou `.claude/`, devem conter apenas configurações e instruções necessárias para aquela ferramenta. Não duplique aqui regras específicas de um modelo ou provedor.
