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
explicitamente, conforme as regras de cota da skill principal.

Sem seletor ou configuração resolvida, anuncie herança/identidade não confirmada.
Use metadados do runtime para confirmar modelo/esforço quando disponíveis. Nunca
trate o nome `cheap_worker` como garantia de preço ou de capacidade.

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
