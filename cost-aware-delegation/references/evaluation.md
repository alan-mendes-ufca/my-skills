# Validação da política de delegação

Use ao alterar a skill ou quando o consumo observado contrariar a expectativa.
Separe testes de decisão, confirmação do runtime e medição da assinatura.

## Casos de decisão

Forneça a skill e cada pedido a um agente em contexto novo, sem revelar a decisão
esperada. Para testar planejamento, proíba execução, spawn e alterações. Julgue o
resultado com esta matriz, não apenas pela autodeclaração do agente:

| Cenário | Aceitação |
| --- | --- |
| Corrigir uma palavra | Execução direta; sem worker nem testes de código irrelevantes. |
| Dois endpoints independentes, modelos selecionáveis | Escopos e responsáveis separados, IDs disponíveis anunciados, contexto mínimo, integração verificada. |
| Runtime só herda modelo | Não promete modelo barato; justifica eventual paralelismo por benefício distinto de economia. |
| Principal forte, `model` selecionável | Toda chamada envia `model`; coleta usa tipo de leitura e modelo econômico; nenhum worker herda o principal sem justificativa. |
| Tarefa mista de leitura e escrita | Tipos de agente diferem conforme o trabalho; tipo genérico só onde há escrita. |
| Worker marca dado como não confirmado | Resumo ao usuário mantém a ressalva. |
| Implementação com contrato fechado, nível barato muito mais barato | Começa pelo nível barato; escala só após falha de aceitação, registrando o motivo. |
| Lançamento em lote de 3+ workers | Uma linha de anúncio por tarefa (agente, modelo, motivo) antes das chamadas. |
| Runtime mostra modelo diferente do pedido | Avisa o usuário; não exige que ele prove o modelo pedido. |
| Plano com limite de sessão, várias tarefas pesadas | Poucos workers por vez; sem vários `opus` em paralelo. |
| Decisão irreversível ou de segurança | Revisão concorrente por modelo maior, contexto novo, com a decisão a avaliar; principal decide. |
| Duas tentativas fundamentadas falharam | Revisão concorrente; sem cascata de níveis. |
| Revisão já feita, sem evidência nova | Não repete a revisão. |
| Revisão concorrente com esforço selecionável | Envia modelo e esforço explícitos; não usa o esforço mínimo. |
| Hardware ausente, contratos conhecidos | Registra validação pendente; não aciona revisão só por isso. |
| Tarefa mistura fatos externos e implementação | Pesquisa de fatos separada, com worker de leitura barato. |
| Principal no modelo mais caro, componente a reescrever | Principal delega a reescrita; fica com contrato e integração. |
| Runtime só delega com pedido explícito, sem autorização prévia | Pergunta uma vez antes de executar; não implementa tudo diretamente em silêncio. |

Uma simulação de planejamento não comprova escolha efetiva de modelo, qualidade
da implementação ou redução de consumo.

## Comparação de consumo e qualidade

Compare tarefas representativas a partir do mesmo estado base e critérios de
aceitação, em contextos separados: execução direta versus política de delegação.
Não execute uma campanha custosa sem orçamento específico para a avaliação.

Registre modelo/esforço solicitados e efetivos (ou desconhecidos), contexto herdado,
delegações, correções, revisões, consultas externas, tempo, testes e retrabalho. Some
uso do principal e de todos os workers; registre tokens/cache somente se expostos.
Registre o contador da assinatura antes/depois quando disponível, sem atribuir à
tarefa mudanças causadas por outras sessões, reset de janela ou arredondamento.

Não converta tokens ou preço de API em quota sem regra documentada. Marque dados
indisponíveis como desconhecidos. Compare qualidade primeiro: economia com falhas
não satisfaz o objetivo. Repetições e alternância da ordem ajudam a identificar
variação/cache; reporte valores observados e limitações, sem generalizar uma única
execução. Reduza fragmentação ou reavalie o modelo quando retrabalho apagar o ganho.
