# Delegação no Claude Code

Confira primeiro o schema da ferramenta `Agent`, os tipos disponíveis e as
configurações da sessão. Esta referência não garante disponibilidade de aliases,
modelos ou recursos em todas as versões/provedores.

## Seleção e confirmação

Quando expostos, use `subagent_type` para comportamento/ferramentas e `model`
para solicitar o modelo. Um alias de família não comprova a versão efetiva.
Configuração, restrições do provedor e fallbacks podem alterar a seleção.
Confira os metadados da tarefa; versões que oferecem `/tasks` mostram o modelo.
Anuncie solicitado e efetivo conforme o contrato da skill, incluindo esforço
somente quando exposto. Não deduza esforço pelo modelo.

Fonte: https://code.claude.com/docs/en/sub-agents

## Mapeamento funcional

| Papel | Recurso a procurar | Critério |
| --- | --- | --- |
| Barato, leitura | Agente de exploração com modelo econômico confirmado | Busca/coleta delimitada; evidência suficiente para o contrato solicitado. |
| Barato, escrita | Agente geral com edição permitida | Alteração especificada e verificável. |
| Intermediário | Agente geral | Raciocínio localizado e implementação moderada. |
| Profundo | Agente geral ou de planejamento, contexto novo | Análise difícil ou revisão independente. |
| Excepcional | Modelo superior realmente disponível | Critério excepcional da skill, não uma revisão automática. |

Não fixe uma família por nível sem conferir capacidade e custo no ambiente atual.
Confira ferramentas permitidas: agentes de leitura/planejamento não substituem
workers com escrita. Solicitar somente leitura no prompt não cria um sandbox.

## Contexto e ciclo de vida

Prefira contexto novo. Quando disponível, um fork pode herdar modelo e histórico;
verifique suas restrições antes de solicitar overrides e justifique a duplicação.
Não use fork como revisão independente se ele carregar as conclusões do principal.

Aguarde o mecanismo de conclusão do runtime. Para uma correção no mesmo escopo,
use a operação de continuação exposta pela versão instalada, sem recriar o agente
por padrão. Respeite o orçamento global e evite polling frequente.

Se houver `isolation: "worktree"`, ele pode separar escritas do repositório, mas
não elimina conflitos de integração nem isola serviços externos compartilhados.
Sem isolamento, serialize edições sobrepostas.

Consultas `antigravity-*` seguem a política de revisões externas da skill principal;
não são uma família Claude nem um fallback silencioso quando `Agent` falta.
