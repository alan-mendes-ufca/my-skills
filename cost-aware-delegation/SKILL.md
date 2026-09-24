---
name: cost-aware-delegation
description: Coordena subagentes para reduzir custo e uso de modelos caros sem sacrificar interpretação, decisões técnicas ou validação final. Use em tarefas não triviais e decomponíveis quando houver trabalho mecânico, exploratório, repetitivo, paralelo ou de validação que possa ser delegado com segurança.
---

# Delegação econômica de agentes

Use esta skill para economizar capacidade de modelos mais fortes sem transformar a tarefa em uma cascata de agentes nem terceirizar decisões importantes.

Princípio central: **delegue execução; retenha julgamento**.

## Responsabilidade do agente principal

O agente principal atua como orquestrador. Ele deve manter responsabilidade por:

- interpretar a intenção e as restrições do usuário;
- resolver ambiguidades relevantes;
- decompor o problema e escolher o que delegar;
- decisões de arquitetura, produto, segurança e trade-offs;
- integrar resultados de múltiplos agentes;
- revisar evidências e rejeitar conclusões fracas;
- executar ou supervisionar a validação final;
- produzir a resposta final e assumir as decisões tomadas.

Não use um subagente barato para reinterpretar requisitos ambíguos ou decidir algo cujo erro tenha impacto material.

## Ciclo de execução

Para tarefas não triviais, siga este ciclo:

1. **Entenda** o objetivo, os limites e o estado atual antes de delegar.
2. **Planeje** uma abordagem curta e identifique dependências entre subtarefas.
3. **Decomponha** em blocos com entradas e saídas claras.
4. **Cheque delegação**: para cada bloco, avalie custo, necessidade de raciocínio, isolamento de contexto, paralelismo e custo do erro.
5. **Execute ou delegue** diretamente ao nível adequado. Não faça escalonamento em cascata por padrão.
6. **Integre** os resultados no contexto principal.
7. **Valide** as conclusões e mudanças relevantes com evidência adequada.
8. **Finalize** somente depois de reconciliar conflitos, lacunas e falhas de validação.

## Roteamento por nível de trabalho

### Worker barato

Prefira o worker mais barato disponível para trabalho delimitado e verificável, como:

- buscas direcionadas no repositório;
- inventários de arquivos, símbolos, chamadas e dependências;
- coleta de evidências estruturadas;
- execução de testes, lint, build e matrizes de validação já definidas;
- edições pequenas e especificadas;
- tarefas repetitivas ou de alto volume;
- documentação mecânica baseada em fatos já decididos.

Peça evidência estruturada, como caminhos, símbolos, resultados e erros. O agente principal sintetiza relações e toma decisões.

### Worker intermediário

Use um worker intermediário quando a subtarefa exigir raciocínio localizado, mas ainda tiver escopo claro, por exemplo:

- investigar um bug restrito a um componente;
- implementar uma alteração moderadamente complexa já especificada;
- escrever ou corrigir testes não triviais;
- refatorar lógica localizada preservando contratos conhecidos;
- comparar poucas alternativas técnicas dentro de critérios definidos pelo agente principal.

Ele pode propor opções e implementar trabalho delimitado, mas não deve assumir a decisão arquitetural ou de produto final.

### Worker profundo

Use um worker do mesmo nível do agente principal, ou outro modelo forte, somente quando houver benefício real de contexto separado ou paralelismo, como:

- investigação difícil que pode ser conduzida de forma independente;
- análise de uma parte grande e desacoplada do sistema;
- revisão técnica profunda de uma proposta já formada;
- implementação complexa suficientemente isolada para justificar um segundo contexto forte.

Não o use apenas porque a tarefa é grande. Se o trabalho estiver fortemente acoplado ao raciocínio principal, mantenha-o no agente principal.

### Worker excepcional

Reserve o modelo mais caro ou excepcional para casos raros:

- falha material dos níveis anteriores em uma questão realmente difícil;
- problema de alta consequência que exija capacidade adicional;
- análise independente excepcionalmente complexa e bem delimitada.

Não use como etapa automática de revisão nem como destino de toda incerteza.

## Quando delegar

Prefira delegação quando uma subtarefa limitada tiver benefício claro de pelo menos um destes tipos:

- menor custo de modelo;
- menor latência por paralelismo;
- isolamento útil de contexto;
- redução de volume na thread principal;
- execução mecânica ou repetitiva;
- validação independente.

Uma tarefa grande e decomponível não deve terminar com zero delegação apenas porque o agente principal conseguiria fazer tudo sozinho, desde que existam subtarefas limitadas com benefício real.

## Quando não delegar

Execute diretamente no agente principal quando:

- a tarefa for trivial ou de uma única etapa;
- o overhead de explicar, aguardar e integrar for maior que o trabalho;
- a subtarefa estiver fortemente acoplada à interpretação em andamento;
- delegar exigiria transferir uma decisão crítica;
- o contexto necessário for tão amplo que duplicá-lo anule a economia;
- a divisão produzir apenas “teatro de agentes” sem ganho mensurável.

Não microdelegue ações minúsculas apenas para demonstrar uso de subagentes.

## Paralelismo

Paralelize somente subtarefas genuinamente independentes. Respeite o limite de concorrência disponível no ambiente e processe em lotes quando houver mais trabalho independente que slots de agentes.

Não paralelize tarefas que dependam do mesmo arquivo, estado mutável, decisão ainda não tomada ou resultado intermediário.

## Falhas e escalonamento

Não use uma cascata automática barato → intermediário → profundo → excepcional.

Quando um worker falhar:

1. determine se a falha é de ambiente, entendimento, escopo ou capacidade;
2. preserve evidências úteis produzidas;
3. reformule a subtarefa se o problema foi especificação ruim;
4. encaminhe diretamente ao nível necessário quando houver justificativa concreta;
5. mantenha no agente principal decisões sobre mudança de estratégia.

Falhas de teste, build, rede, permissões ou infraestrutura não são automaticamente falhas de raciocínio do worker.

## Contrato de retorno dos subagentes

Sempre que possível, peça retornos curtos e verificáveis contendo:

- o que foi inspecionado ou executado;
- evidências concretas;
- resultado ou alteração produzida;
- incertezas e bloqueios;
- arquivos ou componentes afetados;
- comandos e status de validação quando aplicável.

Evite despejos extensos de saída bruta. O agente principal deve sintetizar os resultados e decidir o próximo passo.

## Mapeamento de papéis

Quando o ambiente oferecer papéis equivalentes aos desta configuração, use-os assim:

- `cheap_worker`: trabalho mecânico, exploratório, repetitivo e validação definida;
- `balanced_worker`: raciocínio localizado e implementação moderada;
- `deep_worker`: análise ou implementação forte com benefício de contexto separado;
- `exceptional_worker`: uso raro para complexidade excepcional.

Se os nomes ou modelos disponíveis forem diferentes, preserve a função de cada nível em vez de depender de um identificador específico de modelo.

## Critério de sucesso

A delegação foi bem utilizada quando o agente principal preserva qualidade de interpretação e decisão, enquanto transfere trabalho delimitado para níveis mais baratos ou contextos paralelos, integra os resultados e valida o conjunto antes de concluir.
