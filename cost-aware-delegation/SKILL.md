---
name: cost-aware-delegation
description: Coordena subagentes para reduzir custo e uso de modelos caros sem sacrificar interpretação, decisões técnicas ou validação final. Use em tarefas não triviais e decomponíveis quando houver trabalho mecânico, exploratório, repetitivo, paralelo ou de validação que possa ser delegado com segurança, e quando uma decisão de alto risco ou uma investigação travada exigir capacidade superior por gates objetivos.
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

Nenhum worker, de qualquer nível, assume a decisão final de arquitetura, produto ou segurança. Um nível superior fornece análise, revisão ou implementação; o agente principal avalia o resultado contra as evidências e decide.

## Ciclo de execução

Para tarefas não triviais, siga este ciclo:

1. **Entenda** o objetivo, os limites e o estado atual antes de delegar.
2. **Planeje** uma abordagem curta e identifique dependências entre subtarefas.
3. **Decomponha** em blocos com entradas e saídas claras.
4. **Cheque delegação e gates**: para cada bloco, avalie custo, necessidade de raciocínio, isolamento de contexto, paralelismo, custo do erro e os gates obrigatórios de escalonamento.
5. **Execute ou delegue** diretamente ao nível adequado, pelo mecanismo nativo de subagentes quando decidir delegar. Não faça escalonamento em cascata por padrão.
6. **Integre** os resultados no contexto principal.
7. **Valide** as conclusões e mudanças relevantes com evidência adequada.
8. **Finalize** somente depois da checagem de capacidade e de reconciliar conflitos, lacunas e falhas de validação.

Reavalie os gates sempre que surgir evidência nova, não apenas no passo 4.

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

Use um worker de nível igual ou superior ao do agente principal, ou outro modelo forte, somente quando houver benefício real de contexto separado ou paralelismo, como:

- investigação difícil que pode ser conduzida de forma independente;
- análise de uma parte grande e desacoplada do sistema;
- revisão técnica profunda de uma proposta já formada;
- implementação complexa suficientemente isolada para justificar um segundo contexto forte;
- encaminhamento exigido por um gate obrigatório de escalonamento.

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
- delegar a execução exigiria transferir uma decisão crítica (quando um gate obrigatório de escalonamento se aplica, transfere-se análise ou revisão independente, nunca a decisão);
- o contexto necessário for tão amplo que duplicá-lo anule a economia;
- a divisão produzir apenas “teatro de agentes” sem ganho mensurável.

Não microdelegue ações minúsculas apenas para demonstrar uso de subagentes.

## Paralelismo

Paralelize somente subtarefas genuinamente independentes. Respeite o limite de concorrência disponível no ambiente e processe em lotes quando houver mais trabalho independente que slots de agentes.

Não paralelize tarefas que dependam do mesmo arquivo, estado mutável, decisão ainda não tomada ou resultado intermediário.

## Gates obrigatórios de escalonamento

A escalada não depende de o agente atual considerar a tarefa "difícil". Cada gate abaixo descreve uma condição observável, não um grau de confiança. Os gates 1, 2 e 8 exigem estimar impacto; nesses casos, aplique o critério indicado e registre-o. Basta um gate para que a decisão afetada exija capacidade superior:

1. **Arquitetura difícil de reverter**: decisão arquitetural que envolva múltiplos componentes (dois ou mais módulos, serviços ou contratos públicos) e cuja reversão exija migração de dados, mudança de contrato público ou retrabalho em mais de um componente.
2. **Segurança com impacto material**: decisão sobre autenticação, autorização, segredos, dados sensíveis ou fronteiras de confiança cujo erro possa expor dados ou credenciais reais, permitir acesso indevido ou escalar privilégios.
3. **Requisitos sem resolução**: requisitos relevantes contraditórios, ou ambiguidade que as evidências disponíveis não resolvem. Se o usuário puder esclarecer, pergunte a ele antes de escalar; o gate cobre o que a evidência técnica deveria resolver e não resolve.
4. **Duas tentativas sem resultado**: duas tentativas fundamentadas, cada uma com hipótese e verificação observável, sem explicar nem corrigir o problema. Falhas de ambiente, permissão ou rede não contam como tentativas.
5. **Hipóteses sem discriminação**: duas ou mais hipóteses plausíveis de causa raiz permanecem sem discriminação depois de uma rodada de verificações locais ao alcance, como ler o código relevante e executar o teste ou o log que separa as hipóteses.
6. **Evidências em contradição**: evidências relevantes se contradizem e a divergência não se explica por erro de coleta, verificado na mesma rodada de verificações locais.
7. **Integração não verificável**: a mudança atravessa múltiplos limites de sistema e a integração não pode ser validada localmente.
8. **Custo assimétrico do erro**: uma conclusão errada teria consequência grave e não reversível a baixo custo, como perda de dados, indisponibilidade, decisão irreversível ou retrabalho de dias, significativamente superior ao custo de consultar um nível mais forte. Correções rotineiras e facilmente reversíveis não acionam este gate.

Quando um gate for satisfeito e houver nível de capacidade superior disponível, antes de finalizar aquela decisão o agente deve:

- **encaminhar** a subtarefa apropriada, isolada e com entradas e saída definidas; ou
- **solicitar revisão independente** desse nível, quando a decisão estiver acoplada ao raciocínio principal: formule antes sua própria análise ou proposta e envie o contexto mínimo necessário para a crítica.

> Um gate não pode ser ignorado apenas porque o agente atual acredita que sua própria resposta é suficiente.

Regras de aplicação:

- O roteamento é direto ao nível necessário, sem cascata. Normalmente é o nível profundo; o excepcional só entra quando o gate combinar consequência excepcional com insuficiência ou falha material do nível profundo.
- O gate escala a decisão que o disparou, não a tarefa inteira. O restante continua no nível adequado.
- Encaminhar por gate pede análise ou revisão; não transfere a decisão, que permanece no agente principal.
- Se não houver nível superior disponível, siga esta ordem: primeiro, uma revisão independente por subagente do mesmo nível, em contexto separado, quando o ambiente oferecer subagentes; se não houver esse recurso, aplique a garantia de execução abaixo, declarando a limitação e a incerteza residual.
- Para divergir do resultado do nível superior, o agente principal precisa de evidência concreta, como código, teste ou saída de comando, e a registra em uma linha. Sem essa evidência, não descarte a conclusão: verifique-a ou leve a divergência ao usuário.
- Sem gate satisfeito, insegurança, tarefa longa ou grande volume de trabalho não justificam escalar; colete evidência primeiro.
- Ao acionar um gate, registre em uma linha, no plano ou na nota de progresso, qual gate foi acionado, a evidência e o destino.

## Garantia de execução da delegação

Quando concluir que uma subtarefa deve ser delegada, seja pelos benefícios de "Quando delegar" ou por um gate, e o ambiente oferecer subagentes compatíveis, a delegação precisa ocorrer pelo mecanismo nativo de agentes ou subagentes do ambiente.

Não conta como delegação:

- simular uma "segunda perspectiva" na mesma thread;
- executar toda a subtarefa no agente principal depois de decidir delegá-la;
- apenas dizer qual agente deveria ter sido usado;
- abrir outro processo independente que não represente um subagente nativo, quando o ambiente oferecer mecanismo próprio de agentes.

Decidir não delegar a execução de uma subtarefa com base em "Quando não delegar" é legítimo, mas não dispensa a revisão independente exigida quando um gate de escalonamento é satisfeito. O que a garantia proíbe é decidir delegar e não executar.

Se o subagente ou o nível necessário não estiver disponível, ou o ambiente exigir uma autorização que não foi concedida, declare explicitamente a limitação e decida de forma consciente entre:

- continuar no agente principal, registrando o risco residual; ou
- solicitar intervenção do usuário.

Quanto maior o custo do erro, mais peso tem a segunda opção.

## Falhas e escalonamento

Não use uma cascata automática barato → intermediário → profundo → excepcional.

Quando um worker falhar:

1. determine se a falha é de ambiente, entendimento, escopo ou capacidade;
2. preserve evidências úteis produzidas;
3. reformule a subtarefa se o problema foi especificação ruim;
4. verifique se algum gate obrigatório foi acionado e encaminhe diretamente ao nível necessário quando houver justificativa concreta;
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

## Checagem de capacidade antes de finalizar

Em tarefas não triviais, antes do passo **Finalize**, confirme internamente:

1. Algum gate obrigatório de escalonamento foi acionado?
2. Se foi, ele foi tratado?
3. Alguma subtarefa marcada para delegação acabou sendo executada silenciosamente pelo agente principal?
4. Existem conflitos ou incertezas relevantes que justifiquem capacidade superior?
5. A validação final sustenta de fato a decisão tomada?

Esta é uma política operacional do agente, não um relatório para o usuário. Se alguma checagem indicar pendência, ou seja, gate acionado e não tratado, delegação decidida e não executada, conflito ou incerteza relevante sem resolução, ou validação insuficiente, resolva-a antes de finalizar: delegue, revalide ou declare a limitação. Comunique ao usuário apenas o que resultar em ação, como limitação declarada, gate com resultado relevante ou risco residual material.

## Mapeamento de papéis

Quando o ambiente oferecer papéis equivalentes aos desta configuração, use-os assim:

- `cheap_worker`: trabalho mecânico, exploratório, repetitivo e validação definida;
- `balanced_worker`: raciocínio localizado e implementação moderada;
- `deep_worker`: análise ou implementação forte com benefício de contexto separado;
- `exceptional_worker`: uso raro para complexidade excepcional.

Se os nomes ou modelos disponíveis forem diferentes, preserve a função de cada nível em vez de depender de um identificador específico de modelo.

### Exemplos por ecossistema (não normativo)

A tabela mostra correspondências aproximadas, apenas como ponto de partida:

| Capacidade | Claude | Codex |
| --- | --- | --- |
| barato | Haiku | Luna |
| intermediário | Sonnet | Terra |
| profundo | Opus | Sol |
| excepcional | Opus ou equivalente excepcional | Astra |

- Os nomes podem mudar e a disponibilidade varia por ambiente.
- Um mesmo modelo pode ocupar mais de um nível.
- Escolha pela função e pela capacidade do nível, não pelo nome do modelo.

No Claude Code, consulte [references/claude.md](references/claude.md) para o mapeamento dos níveis para tipos de agente e modelos da ferramenta `Agent`.

## Critério de sucesso

A delegação foi bem utilizada quando o agente principal preserva qualidade de interpretação e decisão, enquanto transfere trabalho delimitado para níveis mais baratos ou contextos paralelos, integra os resultados e valida o conjunto antes de concluir.
