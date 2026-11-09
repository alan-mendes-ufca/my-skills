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
| Intenção de delegar escrita só no raciocínio | Reprovado: a linha de anúncio precisa estar no texto visível antes da chamada. |
| Lote anunciado por uma frase-resumo ("três workers, dois no sonnet") | Reprovado: uma linha `Tarefa → modelo → motivo` por worker. |
| Contrato fechado, worker intermediário escolhido | Começa no nível barato, ou o motivo do anúncio diz o que exige o intermediário. |
| Principal define contrato e começa a escrever módulos, dados ou testes | Para no contrato (tipos, stubs, critérios) e delega a implementação. |
| Correção de permissão ou papel de usuário (ex.: escalada de privilégio) | Revisão concorrente disparada sem o usuário pedir, ou motivo dito no fechamento. |
| Lote de análises equivalentes (ex.: várias transcrições) | Mesmo nível para todas; análise interpretativa de dados reais no nível intermediário. |
| Worker concluído e nova tarefa de outro escopo | Worker novo com contexto mínimo; continuação só para o mesmo escopo. |
| Principal já no modelo mais alto, revisão necessária | Mesmo nível em contexto novo, esforço `medium` ou maior; nunca modelo menor. |
| `isolation: "worktree"` fora de repositório git | Confere o repositório antes; sem git, serializa as edições. |
| Contrato fechado, mas tarefa longa com muitos passos encadeados | Divide em tarefas curtas do nível barato ou usa o intermediário; não entrega laço longo ao nível barato. |
| Resultado do worker não é conferível por comando | Não começa no nível barato, ou o principal define a verificação antes de delegar. |
| Worker barato falha a aceitação | Escada: verificação no prompt, depois esforço um nível acima, depois modelo acima no esforço mais baixo; um degrau por vez, com o motivo. |
| Tarefa é uma cadeia dependente que cabe num contexto só | Execução direta ou um único worker; sem time de agentes. |
| Principal em Fable, revisão necessária | Revisor em Fable em contexto novo (`revisor-fable`); se indisponível, avisa que o revisor ficou abaixo do principal. |
| Principal espera um worker terminar | Uma espera pelo mecanismo do runtime; sem `sleep` em laço nem polling. |
| Verificação em hardware ou monitoramento longo | Delegada com condição de parada e retorno resumido; monitor filtrado para eventos que mudam decisão. |
| Fase grande concluída, sessão longa | Sugere ao usuário compactar ou abrir sessão nova com o estado salvo; não troca o modelo do principal no meio da sessão. |
| Usuário pergunta qual modelo usar no principal | Sugere uma vez o ponto de partida (Opus em `medium`; Fable para arquitetura ou coordenação grande); não muda por conta própria. |

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

Para escolher o modelo, o método descrito pela Anthropic segue estes passos:

- use tarefas reais com verificação automática do resultado;
- rode cada candidato em 2 ou 3 níveis de esforço, cada execução em sessão
  própria, para não compartilhar cache;
- registre o custo por tarefa concluída, não por token;
- mantenha um arranjo com vários modelos só se ele superar todos os pontos de
  modelo único no gráfico de acerto por gasto;
- calcule o preço das tarefas mais difíceis à parte: num benchmark citado, 2 de
  20 problemas responderam por 43% do gasto.

Fonte: `https://claude.dev/blog/which-claude-model-should-you-build-with/`
(9 nov. 2026).

Para sessões reais, `python3 -I scripts/usage-report.py --since <data>` resume
delegações, anúncios visíveis, escrita do principal e tokens do principal,
dos workers e do auto-review no Claude Code e no Codex. Workers em worktree
podem ficar sem transcrição encontrada; o relatório marca esses totais como
parciais. O transcript do Claude Code pode não gravar o texto que precede uma
chamada de ferramenta, então "anúncio não encontrado" ali é indício, não prova:
confirme na tela da sessão antes de concluir que faltou.

O relatório também lista os workers por tipo (os lançados por skills, como
`/code-review`, saem marcados `skill`), mostra turnos e chamadas `Bash` do
principal e aponta indícios: laço longo em modelo barato, contexto de Haiku
acima de 100 mil tokens, principal consumindo mais que os workers e espera
ativa (`sleep`) no Codex. Indício pede conferência na sessão, não é prova.

Não converta tokens ou preço de API em quota sem regra documentada. Marque dados
indisponíveis como desconhecidos. Compare qualidade primeiro: economia com falhas
não satisfaz o objetivo. Repetições e alternância da ordem ajudam a identificar
variação/cache; reporte valores observados e limitações, sem generalizar uma única
execução. Reduza fragmentação ou reavalie o modelo quando retrabalho apagar o ganho.
