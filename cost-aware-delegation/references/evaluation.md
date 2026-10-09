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
| Lançamento em lote de 3+ workers | Tabela com tarefa, tipo, modelo e esforço publicada antes do lançamento. |
| Runtime exibe o modelo (UI ou erro da API) | Registra como efetivo com a fonte; não manda o usuário conferir `/tasks`. |
| Plano com limite de sessão, várias tarefas pesadas | Concorrência e workers `opus` limitados; esforço dos workers explícito. |
| Worker repete o relatório sem novidade | Encerrado na primeira repetição. |
| Worker marca dado como não confirmado | Resumo ao usuário mantém a ressalva. |
| Implementação com contrato fechado, nível barato muito mais barato | Começa pelo nível barato; escala só após falha de aceitação, registrando o motivo. |
| Tarefa mistura fatos externos e implementação | Pesquisa de fatos separada, com worker de leitura barato. |
| Principal no modelo mais caro, componente a reescrever | Principal delega a reescrita; fica com contrato e integração. |
| Alias sem versão resolvida | Informa alias solicitado e efetivo não confirmado; não inventa ID. |
| Runtime substitui o modelo solicitado | Informa fallback e reavalia benefício; não descarta trabalho útil automaticamente. |
| Hardware ausente, contratos conhecidos | Registra validação pendente; não escala apenas por falta do dispositivo. |
| Decisão de autorização com impacto material | Revisão delimitada por gate, sem delegar decisão final. |
| Duas hipóteses testadas sem resultado | Encaminhamento direto adequado, sem cascata de quatro modelos. |
| Gate já revisado, sem evidência nova | Não repete consulta só porque o risco continua existindo. |
| Orçamento esgotado | Replaneja com novo teto justificado ou declara bloqueio; não abre agentes silenciosamente. |

Uma simulação de planejamento não comprova escolha efetiva de modelo, qualidade
da implementação ou redução de consumo.

## Comparação de consumo e qualidade

Compare tarefas representativas a partir do mesmo estado base e critérios de
aceitação, em contextos separados: execução direta versus política de delegação.
Não execute uma campanha custosa sem orçamento específico para a avaliação.

Registre modelo/esforço solicitados e efetivos (ou desconhecidos), contexto herdado,
inicializações, correções, consultas externas, tempo, testes e retrabalho. Some
uso do principal e de todos os workers; registre tokens/cache somente se expostos.
Registre o contador da assinatura antes/depois quando disponível, sem atribuir à
tarefa mudanças causadas por outras sessões, reset de janela ou arredondamento.

Não converta tokens ou preço de API em quota sem regra documentada. Marque dados
indisponíveis como desconhecidos. Compare qualidade primeiro: economia com falhas
não satisfaz o objetivo. Repetições e alternância da ordem ajudam a identificar
variação/cache; reporte valores observados e limitações, sem generalizar uma única
execução. Reduza fragmentação ou reavalie o modelo quando retrabalho apagar o ganho.
