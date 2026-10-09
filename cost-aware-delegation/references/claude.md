# Delegação no Claude Code

Confira primeiro o schema da ferramenta `Agent` exposto na sessão: a lista de
`subagent_type` disponíveis, o `enum` do parâmetro `model` e se há `effort`.
Esta referência não garante aliases, modelos ou recursos em todas as versões.

## Regras obrigatórias por chamada

1. **Sempre envie `model` explicitamente** quando o schema o expuser. Omitir
   `model` faz o worker herdar o modelo principal (ou o padrão configurado para
   subagentes); com o principal em Opus, isso significa todo worker em Opus, sem
   economia. Herança só é aceitável como escolha deliberada para o nível
   profundo, e deve ser anunciada como `herança (<modelo principal>)`.
2. **Sempre escolha `subagent_type` pelo trabalho**, não por padrão. Omitir o
   parâmetro cai em `general-purpose`. Use `general-purpose` apenas quando o
   worker precisar editar arquivos ou executar comandos com efeito.
3. **Publique a linha de transparência da skill antes de cada chamada**, com o
   alias exato enviado em `model` (ex.: `sonnet`) e o `subagent_type` escolhido.
4. Ter `model` no schema significa que a seleção existe: não trate a sessão
   como "só herança" nem execute tudo diretamente por esse motivo.

## Autorização para delegar

O Claude Code pode instruir o agente principal a só criar subagentes quando o
usuário pedir. Uma skill não sobrepõe essa instrução. Com isso, o principal
tende a executar tudo sozinho, no modelo mais caro, até o usuário pedir.

- Se o usuário ou um `CLAUDE.md` já autorizar a delegação, siga a skill
  normalmente.
- Sem essa autorização, em tarefa não trivial e decomponível, pergunte **uma
  vez, antes de começar a executar**, se pode delegar. Não execute a tarefa
  inteira diretamente por falta de autorização sem ter perguntado.
- O README do repositório traz um trecho de `CLAUDE.md` que dá essa autorização.

## Agentes do repositório (preferenciais)

Se a sessão listar os agentes abaixo (instalados por `scripts/install-local.sh`
em `~/.claude/agents`), use-os como `subagent_type`. O nome já mostra papel e
modelo na interface, e o frontmatter fixa modelo, esforço e ferramentas.

| Papel | `subagent_type` | Modelo / esforço | Escrita |
| --- | --- | --- | --- |
| `cheap_worker` (leitura) | `pesquisador-haiku` | haiku / low | não |
| `cheap_worker` (escrita) | `executor-haiku` | haiku / low | sim |
| `cheap_worker` (implementação com contrato fechado) | `implementador-haiku` | haiku / medium | sim |
| `balanced_worker` (pesquisa) | `pesquisador-sonnet` | sonnet / medium | não |
| `balanced_worker` | `implementador-sonnet` | sonnet / medium | sim |
| `deep_worker` | `especialista-opus` | opus / high | sim |
| `deep_worker` (revisão de gate) | `revisor-opus` | opus / high | não |

- Envie `model` igual ao do agente (o parâmetro da chamada prevalece sobre o
  frontmatter). Para outro modelo, escolha outro agente; não sobrescreva, ou o
  nome exibido deixa de corresponder ao modelo.
- Não envie `effort`: ele já vem do frontmatter.
- **Haiku primeiro (experimental):** com o contrato fechado pelo principal,
  comece por `implementador-haiku`. Use `implementador-sonnet` quando a tarefa
  for ambígua, exigir decisão de design, ou quando o Haiku falhar a aceitação
  após a rodada de correção. Registre a escalada e o motivo.
- **Fatos separados da implementação:** dados factuais (status de conservação,
  dados científicos, referências) vão para um `pesquisador-haiku` à parte, não
  para o worker que escreve código ou arte.
- Se os agentes não estiverem listados, use o mapeamento genérico abaixo.

## Mapeamento genérico de papéis

Use a menor linha adequada. Os aliases abaixo são os valores usuais do `enum`
de `model`; confirme-os no schema da sessão antes de usar.

| Papel | `subagent_type` | `model` | Uso |
| --- | --- | --- | --- |
| `cheap_worker` (leitura) | `Explore` | `haiku` | Localizar código, coletar trechos, mapear arquivos, pesquisa web sem edição. |
| `balanced_worker` (pesquisa) | `Explore` | `sonnet` | Pesquisa web com síntese e checagem de fontes, sem editar arquivos. |
| `cheap_worker` (escrita) | `general-purpose` | `haiku` | Edição totalmente especificada, repetitiva e verificável. |
| `balanced_worker` | `general-purpose` | `sonnet` | Bug localizado, implementação moderada, testes não triviais. |
| `deep_worker` (análise) | `Plan` ou `general-purpose` | `opus` | Investigação difícil, plano ou revisão independente de gate. |
| `deep_worker` (escrita) | `general-purpose` | `opus` | Implementação isolada complexa. |
| `exceptional_worker` | `general-purpose` | modelo superior do `enum`, se houver | Somente pelo critério excepcional da skill. |

- `Explore` e `Plan` não editam arquivos; não os use para escrita. Pesquisa
  web e coleta de fontes não exigem `general-purpose`: confira no schema se o
  `Explore` da sessão tem busca/fetch web e prefira-o.
  Pedir "somente leitura" no prompt de um `general-purpose` não cria sandbox.
- Se houver agentes customizados (`.claude/agents/*.md`) com papel e modelo
  definidos no frontmatter, prefira-os quando corresponderem ao papel; o
  parâmetro `model` da chamada ainda prevalece sobre o frontmatter.
- Não suba de nível por precaução. Uma tarefa grande decomposta em partes
  simples usa `haiku`/`sonnet` nas partes, não `opus` no todo.
- Se o `enum` não tiver um alias da tabela, use o mais próximo disponível e
  registre a substituição; não invente nomes.

## Esforço

Se o schema expuser `effort`, a skill autoriza defini-lo explicitamente por
tarefa: `low` para `cheap_worker`, `medium` para `balanced_worker` e o nível
necessário para `deep_worker`. Sem o parâmetro, informe esforço como
`não exposto` ou `herdado`; não deduza esforço pelo modelo.

## Confirmação do modelo efetivo

O parâmetro enviado comprova apenas a solicitação. Um alias (`sonnet`) não
identifica a versão. Distinga o que o principal consegue observar do que só o
usuário vê:

- **Observável pelo principal:** texto que chega no resultado ou na notificação
  do agente, como erros da API que nomeiam o modelo enviado
  (ex.: `model sent to the API: claude-sonnet-5-5`). Quando aparecer, registre
  o modelo efetivo e a fonte.
- **Visível só na interface:** a linha do agente (ex.:
  `implementador-haiku(<tarefa>) Haiku 5.5`) e `/tasks`. O principal não
  recebe esse texto e não pode citá-lo como evidência própria.

Com os agentes do repositório, o modelo vem fixo no frontmatter. Registre
`solicitado: <alias> (fixo no agente); efetivo: não observável pelo principal,
exibido na linha do agente`. Não escreva que "o runtime não mostrou" o modelo,
porque a interface mostra. A autodeclaração do worker não comprova identidade.
Fora desses casos, registre `modelo efetivo não confirmado (solicitado: <alias>)`.

Exemplo de anúncio:

`Mapear handlers de auth → Explore / modelo solicitado: haiku (alias) → esforço: low → motivo: coleta delimitada → modelo efetivo: não confirmado`

Lançamentos em lote (`N background agents launched`) não mostram o modelo de
cada tarefa. Publique a tabela de transparência, com uma linha por tarefa, no
texto da mesma resposta e **antes** das chamadas `Agent`. Uma frase-resumo
("delego X ao sonnet e Y ao haiku") não substitui a tabela. Se não for publicar
a tabela, lance um agente por vez com a linha de anúncio.

## Agente principal em planos com limite

O principal costuma rodar no modelo mais caro, então o trabalho feito por ele
pesa mais na cota do que o mesmo trabalho num worker barato.

- O principal escreve contratos, tipos compartilhados e integrações pequenas.
  Reescrever um componente, gerar arte, corrigir ferramentas de teste ou
  montar infraestrutura de verificação são execução: delegue.
- Em planos com limite de sessão (ex.: Pro), sugira ao usuário, uma vez, rodar
  o principal com esforço `medium` em vez de `high`/`xhigh`. Não mude o modelo
  ou o esforço do principal por conta própria.
- Conferência visual (abrir screenshots) também consome cota: confira por
  amostra, não todas as imagens de todos os workers.

## Registro para avaliação

Ao concluir cada worker, registre numa linha: tarefa, `subagent_type`, modelo
efetivo e fonte, tokens e duração (quando o runtime mostrar), rodadas de
correção, escalada e se passou na aceitação. Ao final da sessão, apresente a
tabela completa ao usuário. Isso permite comparar o custo por tarefa concluída
entre Haiku e Sonnet.

## Limites da assinatura e concorrência

As regras gerais de cota e concorrência estão na skill principal. No Claude Code:

- O nível mais caro costuma ser `opus` (`especialista-opus`, `revisor-opus`).
  Em planos com limite de sessão (ex.: Pro), vários workers `opus` em paralelo
  esgotam a cota e derrubam todos os workers ao mesmo tempo.
- O limite de uso aparece como erro `rate_limit` (HTTP 429) no resultado do agente.
- Defina esforço pela seção Esforço; os agentes do repositório já o fixam no
  frontmatter.
- Encerre um worker que repete relatórios com `TaskStop`.

Fonte: https://code.claude.com/docs/en/sub-agents

## Contexto e ciclo de vida

Prefira contexto novo. Um fork herda modelo e histórico e ignora `model`;
não o use quando a economia depende de outro modelo, nem como revisão
independente se carregar as conclusões do principal.

Aguarde o mecanismo de conclusão do runtime. Para uma correção no mesmo escopo,
continue o worker existente (ex.: `SendMessage` com o ID do agente) em vez de
recriá-lo. Respeite o orçamento global e evite polling frequente.

Se houver `isolation: "worktree"`, ele pode separar escritas do repositório, mas
não elimina conflitos de integração nem isola serviços externos compartilhados.
Sem isolamento, serialize edições sobrepostas.

Consultas `antigravity-*` seguem a política de revisões externas da skill principal;
não são uma família Claude nem um fallback silencioso quando `Agent` falta.
