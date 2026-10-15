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
3. **Publique a linha de anúncio da skill antes de cada chamada**, com o
   `subagent_type` e o alias enviado em `model` (ex.: `sonnet`).
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
| `deep_worker` (revisão concorrente) | `revisor-opus` | opus / high | não |

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

Para a **revisão concorrente** da skill, use `revisor-opus` em contexto novo:
plano ou diff e arquivos, sem o raciocínio do principal, e a decisão a avaliar.

## Mapeamento genérico de papéis

Use a menor linha adequada. Os aliases abaixo são os valores usuais do `enum`
de `model`; confirme-os no schema da sessão antes de usar.

| Papel | `subagent_type` | `model` | Uso |
| --- | --- | --- | --- |
| `cheap_worker` (leitura) | `Explore` | `haiku` | Localizar código, coletar trechos, mapear arquivos, pesquisa web sem edição. |
| `balanced_worker` (pesquisa) | `Explore` | `sonnet` | Pesquisa web com síntese e checagem de fontes, sem editar arquivos. |
| `cheap_worker` (escrita) | `general-purpose` | `haiku` | Edição totalmente especificada, repetitiva e verificável. |
| `balanced_worker` | `general-purpose` | `sonnet` | Bug localizado, implementação moderada, testes não triviais. |
| `deep_worker` (análise) | `Plan` ou `general-purpose` | `opus` | Investigação difícil, plano ou revisão concorrente. |
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

Os agentes do repositório já fixam o esforço; não envie `effort`. No mapeamento
genérico, se o schema expuser `effort`, use `low` para barato, `medium` para
intermediário e o necessário para profundo.

## Modelo exibido

Os agentes do repositório fixam o modelo no frontmatter. Anuncie o que pediu
(ex.: `implementador-haiku`, haiku). Se o resultado ou um erro da API nomear
outro modelo, avise o usuário. Não peça ao usuário para provar o que foi
pedido; a interface já mostra o modelo na linha do agente.

Exemplo de anúncio:

`Mapear handlers de auth → pesquisador-haiku (haiku) → coleta delimitada`

Em lançamentos em lote, publique uma linha por tarefa no texto da mesma
resposta, antes das chamadas `Agent`.

## Principal em planos com limite

- Em planos com limite de sessão (ex.: Pro), sugira ao usuário, uma vez, rodar
  o principal com esforço `medium`. Não mude modelo ou esforço por conta própria.
- Confira screenshots por amostra, não todas as imagens de todos os workers.

## Limites e concorrência

- Poucos workers por vez. Evite vários `opus` em paralelo: em planos com
  limite de sessão (ex.: Pro) eles esgotam a cota e derrubam todos juntos.
- O limite de uso aparece como `rate_limit` (HTTP 429). Ao retomar, não
  relance o lote inteiro: continue do estado salvo com menos concorrência.
- Encerre um worker que repete relatórios com `TaskStop`.

Fonte: https://code.claude.com/docs/en/sub-agents

## Contexto e ciclo de vida

Prefira contexto novo. Um fork herda modelo e histórico e ignora `model`;
não o use quando a economia depende de outro modelo, nem como revisão
independente se carregar as conclusões do principal.

Aguarde o mecanismo de conclusão do runtime. Para uma correção no mesmo escopo,
continue o worker existente (ex.: `SendMessage` com o ID do agente) em vez de
recriá-lo. Evite polling frequente.

Se houver `isolation: "worktree"`, ele pode separar escritas do repositório, mas
não elimina conflitos de integração nem isola serviços externos compartilhados.
Sem isolamento, serialize edições sobrepostas.

Consultas `antigravity-*` seguem a política de revisões externas da skill principal;
não são uma família Claude nem um fallback silencioso quando `Agent` falta.
