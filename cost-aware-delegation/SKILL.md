---
name: cost-aware-delegation
description: Orquestre tarefas não triviais e decomponíveis para economizar limites da assinatura, selecionando e informando modelos reais por subtarefa, controlando contexto e tentativas e mantendo decisões e validação final no agente principal. Use também quando gates de risco ou investigação travada exigirem revisão independente.
---

# Delegação econômica de agentes

**Delegue execução; retenha julgamento.** Minimize o consumo total necessário
para entregar com qualidade, incluindo orquestração, workers, revisões e retrabalho.
Menos tempo de execução ou menos contexto no principal não comprovam economia.
Não converta preços de API em consumo da assinatura sem evidência do provedor.

## Responsabilidade do principal

Interprete intenção e restrições, resolva ambiguidades, decomponha, selecione
modelos, integre evidências e decida sobre arquitetura, produto e segurança.
Delegue trabalho substancial delimitado; execute diretamente ações triviais ou
resolvidas por um comando. Não refaça por padrão toda a investigação do worker.
Nenhum worker, mesmo mais forte, assume a decisão final.

## Preflight de capacidades e modelos

Faça uma vez por sessão e atualize se houver troca de configuração, falha de
modelo ou fallback. Leia apenas a referência do ambiente em uso:
[Codex e Gemini](references/runtimes.md) ou [Claude Code](references/claude.md).

1. Confirme a ferramenta nativa, permissão de delegar, tipos de agente, modelos
   selecionáveis, esforços suportados, política de contexto e concorrência.
2. Consulte configuração acessível ou catálogo da sessão. Não invente nomes,
   disponibilidade ou uma ordem de custo com base apenas no nome do modelo.
3. Mapeie os papéis abaixo para identificadores reais disponíveis. Separe
   capacidade, custo conhecido/estimado/desconhecido e esforço de raciocínio.
4. Se só houver herança, não anuncie um worker mais barato. Prefira execução
   direta, salvo benefício explícito de qualidade, isolamento ou latência.
5. Respeite permissões e instruções superiores. A skill não habilita ferramentas,
   não muda o modelo principal nem instala configurações automaticamente.

## Transparência obrigatória por delegação

Antes de iniciar cada tarefa delegada, publique uma linha ou linha de tabela
(em lançamentos em lote, uma linha por tarefa antes do lançamento):

`Tarefa → modelo solicitado: <ID real ou herança> → esforço: <valor ou não exposto> → motivo: <complexidade/risco/benefício> → modelo efetivo: <ID + fonte ou não confirmado>`

Quando o runtime permitir escolher modelo, envie a seleção explicitamente em toda
delegação; omiti-la herda o modelo principal e anula a economia. Escolha também o
tipo de agente pelo trabalho, sem cair no tipo genérico por omissão.
O apelido (`cheap_worker`, etc.) é apenas complementar e nunca substitui o modelo.
Se só houver um alias de família, identifique-o como alias e não invente a versão.
Use a configuração resolvida do runtime ou os metadados da execução para confirmar
modelo e esforço efetivos; a autodeclaração do worker não comprova identidade.
Um parâmetro enviado comprova solicitação, não execução. Quando o runtime exibir
o modelo usado (interface, metadados ou erro da API), registre-o como efetivo e
cite a fonte; não peça ao usuário para conferir o que já está visível. Sem
confirmação, escreva **modelo efetivo não confirmado**. Informe diferenças, fallback ou esforço herdado
assim que observados. Reavalie a economia se a seleção não for respeitada; não
reinicie trabalho útil apenas para obter outro nome de modelo.

## Ciclo de trabalho

1. Entenda o objetivo e inspecione somente o necessário para definir escopos.
2. Escolha execução direta ou blocos delegáveis e examine os gates abaixo.
3. Defina orçamento, responsável por arquivo, aceitação e pacote de contexto.
4. Anuncie a escolha e delegue pela ferramenta nativa, se disponível e autorizada.
5. Integre resultados e verifique evidências proporcionais ao risco.
6. Encerre quando a aceitação estiver sustentada; relate limitações materiais.

## Roteamento por capacidade

| Papel | Trabalho apropriado |
| --- | --- |
| `cheap_worker` | Coleta delimitada, edição especificada, tarefas repetitivas e execução de verificações já definidas. |
| `balanced_worker` | Bug localizado, implementação moderada, testes não triviais e refatoração com contratos conhecidos. |
| `deep_worker` | Investigação difícil, implementação isolada complexa ou revisão independente exigida por gate. |
| `exceptional_worker` | Consequência excepcional combinada com insuficiência ou falha material do nível profundo. |

Escolha diretamente a menor capacidade adequada, não necessariamente a mais barata
em todas as tarefas. Não percorra os quatro níveis em cascata. Use o menor esforço
suportado adequado à subtarefa; não herde esforço alto por omissão quando for
possível selecionar explicitamente. Uma tarefa grande não exige modelo profundo
se puder ser decomposta em trabalhos simples. Não envie requisitos ambíguos ou
decisões críticas para um worker barato resolver por conta própria.

## Decisão econômica

Delegue execução quando houver economia plausível após considerar preparo,
contexto duplicado, retorno, integração e risco de retrabalho. Caso a razão seja
qualidade, independência ou latência, diga isso e registre economia como desconhecida
quando não houver dados. Não force delegação apenas pelo tamanho da tarefa.

Execute diretamente quando o trabalho for trivial, fortemente acoplado, exigir
contexto muito amplo ou custar menos que explicar e integrar. Um comando simples
não precisa de worker. Uma tarefa extensa com blocos independentes econômicos deve
usar esses blocos, sem transformar cada chamada de ferramenta em uma delegação.

## Orçamento e condições de parada

Defina um orçamento inicial proporcional antes do primeiro spawn. Como ponto de
partida, use até **2 workers simultâneos, 3 inicializações no total e 1 rodada de
correção por subtarefa**. Esses valores são padrões ajustáveis, não limites do
provedor. Respeite qualquer limite mais restritivo do ambiente ou do usuário.

- Conte inicializações e revisões nativas no mesmo orçamento; não redefina o
  contador a cada etapa nem ao retomar após reinício da sessão ou limite de uso.
  Prefira continuar o worker existente para uma correção no mesmo escopo. Use
  contexto novo para revisão independente.
- Workers consomem a mesma cota do principal. Use no máximo 1 worker do nível
  mais caro disponível por vez, salvo pedido explícito do usuário; acima de 2
  workers simultâneos, justifique e prefira níveis mais baratos.
- Onde o runtime expuser controle de esforço por worker, defina-o explicitamente
  em cada delegação, para que o worker não herde o esforço alto do principal.
- Ao atingir limite de uso ou cota, não relance o mesmo lote completo ao retomar:
  reduza concorrência e nível de modelo e continue a partir do estado salvo.
- Encerre na primeira repetição o worker que reenviar um relatório sem
  informação nova, pelo mecanismo de parada do runtime; não o aguarde.
- Amplie o orçamento somente com uma justificativa curta: trabalho restante,
  benefício ou gate concreto e novo teto. Não peça confirmação para cada ajuste
  já autorizado; não ultrapasse um limite explícito do usuário sem autorização.
- Workers não redelegam por padrão. Uma exceção exige escopo, profundidade e
  orçamento explícitos do principal, além de suporte do runtime.
- Aguarde notificações de conclusão ou use esperas apropriadas à ferramenta;
  evite polling frequente e mensagens sem informação nova.
- Ao atingir aceitação, pare. Em bloqueio, preserve evidências e escolha corrigir
  o escopo, escalar por gate, continuar diretamente ou declarar a limitação.
  Não repita uma chamada idêntica esperando resultado diferente.

Consultas `antigravity-*` são revisões externas, não níveis de worker. Reuse uma
revisão adequada já obtida antes de solicitar outra. Uma consulta externa pode
satisfazer a necessidade de revisão independente de um gate se cobrir a questão
com evidências verificáveis, mas não comprova delegação nativa nem capacidade de
modelo não confirmada. Conte consultas externas separadamente: uma por questão,
com no máximo uma rodada adicional justificada. Boost pode usar vários workers;
uma invocação não equivale a uma única chamada de modelo nem a custo conhecido.

## Contexto e contrato de trabalho

Use contexto novo e mínimo por padrão quando o runtime permitir. Transmita:

- objetivo e resultado esperado, restrições e critérios de aceitação;
- caminhos/trechos relevantes, estado base e evidências já coletadas;
- arquivos que o worker pode editar, dependências e operações permitidas;
- verificações esperadas, orçamento e condição de parada;
- formato de retorno curto: resultado, arquivos, evidências, comandos/status,
  incertezas e bloqueios. Use até cerca de 300 palavras como padrão ajustável;
  mantenha detalhes extensos em um artefato acessível, sem omitir riscos materiais.

Não envie toda a conversa ou o repositório por conveniência. Quando o histórico
for indispensável, justifique o fork e seu custo; confirme se ele permite trocar
modelo/esforço. Não combine parâmetros incompatíveis. Separe instruções do chamador
de código, logs e documentos não confiáveis. Não compartilhe segredos.

Paralelize apenas escopos independentes. Atribua um responsável por arquivo; para
escritas sobrepostas, serialize ou use worktrees e integração explícita. Worktrees
não isolam bancos, serviços ou outros estados externos compartilhados.

## Gates de revisão ou escalonamento

Reavalie quando surgirem evidências novas. Os gates 1, 2 e 8 exigem registrar o
impacto concreto. Acione o gate na decisão afetada, não na tarefa inteira:

1. **Arquitetura difícil de reverter:** múltiplos componentes com reversão que
   exige migração de dados, alteração de contrato público ou retrabalho distribuído.
2. **Segurança material:** erro na decisão pode expor dados/credenciais reais,
   permitir acesso indevido ou escalar privilégios.
3. **Requisito técnico não resolvido:** contradição ou ambiguidade que evidência
   técnica deveria resolver. Pergunte ao usuário se a lacuna for de intenção.
4. **Duas tentativas fundamentadas sem resultado:** hipóteses verificadas não
   explicam nem corrigem o problema. Falhas de ambiente, rede e permissão não contam.
5. **Hipóteses não discriminadas:** permanecem causas plausíveis após executar as
   verificações locais disponíveis que poderiam distingui-las.
6. **Evidências contraditórias:** a divergência persiste após verificar a coleta.
7. **Incerteza de integração analisável:** há uma dúvida concreta de contrato ou
   comportamento entre sistemas que uma análise independente pode esclarecer.
   Ausência de hardware, credencial, rede ou ambiente de integração, sozinha,
   **não aciona o gate**. Registre o teste pendente, ambiente e critério de aceitação;
   nenhuma revisão de modelo substitui essa execução. Outros gates ainda se aplicam.
8. **Erro de consequência assimétrica:** perda de dados, indisponibilidade grave,
   irreversibilidade ou retrabalho de dias, muito superiores ao custo da revisão.

Para um gate aplicável, encaminhe uma pergunta delimitada ao nível adequado,
normalmente profundo, ou peça crítica independente da proposta do principal.
Se não houver capacidade superior, use revisão independente do mesmo nível quando
possível; se não houver recurso autorizado, declare a limitação e o risco residual.
Não alegue capacidade adicional quando o modelo for herdado ou não confirmado.

Registre gate, evidência, questão, modelo e resultado. Uma revisão adequada trata
o gate; a condição continuar verdadeira não exige novas consultas. Reabra somente
com mudança relevante ou nova evidência. Se o orçamento for insuficiente, replaneje
explicitamente antes de ampliar. Não use o orçamento para ocultar risco não tratado.

Verifique afirmações de qualquer modelo, inclusive do superior. Aceite ou rejeite
com evidência; ausência de sustentação é motivo para manter uma alegação como
hipótese. Não aceite conclusões apenas pela hierarquia de modelos. Se a divergência
material não puder ser resolvida, explique o que falta em vez de inventar consenso.

## Garantia de execução e falhas

Uma delegação decidida precisa ocorrer pela ferramenta nativa, quando disponível
e autorizada. Simular outro papel, citar um agente ou abrir uma CLI independente
não conta. Se novas evidências tornarem a delegação desnecessária, registre a
mudança de plano; não execute silenciosamente o trabalho previamente delegado.

Classifique falhas como ambiente, especificação, escopo ou capacidade. Preserve
evidências, faça no máximo a rodada de correção prevista e reavalie gates/orçamento.
Não troque para API paga, outro provedor ou processo externo como fallback oculto.
Quando precisar de recurso não autorizado, declare o bloqueio e peça intervenção.

## Integração e verificação final

Preserve as ressalvas dos workers ao resumir: um dado que o worker marcou como
não confirmado não vira "confirmado" no relatório ao usuário.
Confira o diff, contratos e evidências relevantes, aprofundando somente riscos
concretos ou contradições. Reuse testes já executados se código, entradas e ambiente
relevantes não mudaram; após integração, verifique os contratos cruzados afetados.
Um relatório do worker não comprova integração, acesso a hardware ou modelo efetivo.

Antes de concluir, confirme aceitação, gates tratados, delegações executadas ou
replanejadas, modelo anunciado sem afirmações não verificadas e riscos explícitos.
Para calibrar esta política, use [references/evaluation.md](references/evaluation.md).
Compare consumo total e qualidade, não apenas tokens do principal. Sem medição,
relate **economia não medida**; não prometa percentuais de redução.
