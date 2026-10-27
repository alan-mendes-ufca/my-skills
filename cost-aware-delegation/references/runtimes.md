# Resolução de modelos por ambiente

Leia apenas a seção do provedor em uso. Esta referência orienta descoberta;
não instala agentes nem substitui a configuração da sessão. Os identificadores
mudam: o catálogo exposto e a configuração resolvida são a fonte operacional.

## Codex CLI e ambientes hospedados

No CLI, confira agentes personalizados e os campos `model` e
`model_reasoning_effort` quando disponíveis. A configuração de agentes pode
sobrepor valores de spawn; não infira o efetivo apenas do parâmetro enviado.
Ambientes hospedados podem ter outra ferramenta e não acessar esses arquivos.

Inspecione o schema da ferramenta real. Se houver seletor de modelo, use um ID
exposto na sessão; se houver controle de histórico, escolha contexto novo para
trabalho independente. Alguns ambientes não permitem override de modelo em fork
completo. Não transplante parâmetros de outro runtime.

Quando `model_reasoning_effort` puder ser definido por worker, defina-o
explicitamente em cada delegação, para o worker não herdar o esforço do
principal: `low` para `cheap_worker`, `medium` para `balanced_worker` e o
necessário para `deep_worker`. A revisão concorrente não usa o esforço mínimo.

Sem seletor ou configuração resolvida, anuncie herança/identidade não confirmada.
Use metadados do runtime para confirmar modelo/esforço quando disponíveis. Nunca
trate o nome `cheap_worker` como garantia de preço ou de capacidade.

### Mapeamento de papéis no Codex CLI

Valores de referência para a família exposta em
`~/.codex/models_cache.json`; confira o catálogo da sessão antes de usar.
Esta tabela é a fonte da skill: se um `AGENTS.md` trouxer outro roteamento,
siga a instrução do usuário e avise da divergência.

| Papel | `model` | `reasoning_effort` |
| --- | --- | --- |
| Principal | o configurado pelo usuário (ex.: `gpt-6.1-sol`) | o configurado; não altere |
| `cheap_worker` | `gpt-6-luna` | `low` |
| `balanced_worker` | `gpt-6.1-terra` | `low` ou `medium` |
| `deep_worker` | `gpt-6.1-sol` | `low` ou `medium` |
| `exceptional_worker` | `gpt-6-astra` | `low` |
| Revisão concorrente | `gpt-6.1-sol` (ou `gpt-6-astra` em risco excepcional) | `medium` ou maior |

- Não use modelos de geração anterior (`gpt-5.6-*`, `gpt-6-sol`) como atalho
  de custo sem custo relativo conhecido; registre o motivo se usar.
- A revisão concorrente não vai para um modelo abaixo do principal: com o
  principal em Sol, use Sol em contexto novo (`fork_turns: "none"`).

### Workers e `followup_task`

- `followup_task` serve para corrigir ou completar o mesmo escopo do worker.
  Escopo novo (outro módulo, arte, documentação, verificação de outra parte)
  pede `spawn_agent` novo, com contexto mínimo; reaproveitar um worker de
  outro escopo acumula contexto alheio e confunde o responsável pelos
  arquivos.
- `agents.max_concurrent_threads_per_session` (em `~/.codex/config.toml`)
  limita os workers simultâneos. No limite, espere um worker terminar ou
  serialize; não converta um worker existente em responsável por outro
  escopo.
- Uma linha de anúncio também antes de cada `followup_task` que muda o
  objetivo; o modelo do worker não muda no followup.

### Consumo do principal

No Codex, o principal costuma somar várias vezes os tokens dos workers,
porque relê o contexto inteiro a cada turno. Para reduzir:

- delegue builds, testes e leitura de logs longos a um `cheap_worker` com
  retorno resumido;
- entre fases grandes, sugira ao usuário uma sessão nova com o estado salvo;
- `approvals_reviewer = "auto_review"` cria threads `codex-auto-review` que
  também consomem cota. É decisão do usuário; mencione o custo uma vez se
  ele relatar cota acabando.

Fonte: https://developers.openai.com/codex/subagents/

## Gemini CLI

Confira os agentes disponíveis e suas definições/configurações de modelo. O
campo `model` pode herdar a sessão quando omitido; overrides do ambiente também
precisam ser verificados. Skills e definições de subagentes são recursos distintos:
instalar um `SKILL.md` não cria automaticamente os quatro workers.

Use somente o mecanismo de delegação realmente exposto. Não suponha que o
orquestrador pode mudar o modelo por chamada. Sem suporte, registre a limitação;
uma invocação do Antigravity é consulta externa, não um worker Gemini nativo.

Fonte: https://geminicli.com/docs/core/subagents/

## Registro mínimo da sessão

Mantenha no plano, sem criar arquivo desnecessário:

| Papel | Modelo solicitado | Esforço | Evidência de disponibilidade | Modelo efetivo/fonte | Custo relativo/fonte |
| --- | --- | --- | --- | --- | --- |
| Nível necessário | ID real ou herança | Valor suportado ou não exposto | Catálogo/configuração/tool schema | ID resolvido ou não confirmado | Conhecido, estimado ou desconhecido |

Um único modelo pode ocupar mais de um papel. Não invente quatro modelos para
preencher a tabela. Só preencha os níveis necessários à tarefa e atualize após
fallback ou mudança de configuração. Consulte documentação da versão instalada
somente se a introspecção local não resolver uma dúvida operacional.
