# my-skills

Coleção compartilhada de Agent Skills para uso local em Codex, Gemini CLI e
Claude Code. Cada pasta de primeiro nível representa uma skill e contém seu
próprio `SKILL.md`.

## Skills incluídas

| Skill | Finalidade |
| --- | --- |
| `humanizer` | Revisar textos preservando fatos, fontes e rastreabilidade. |
| `simplify` | Simplificar código sem alterar seu comportamento observável. |
| `verification-planning` | Planejar evidências e validações proporcionais a uma mudança. |
| `post-refactor` | Examinar um trecho refatorado em busca de regressões. |
| `security-audit` | Estruturar auditorias de segurança com escopo explícito. |
| `cost-aware-delegation` | Orquestrar com modelos identificados, contexto mínimo, orçamento de delegação e gates de risco. |
| `antigravity-reviewer` | Pedir uma segunda opinião sobre implementação ou diff relevante. |
| `antigravity-debugger` | Pedir revisão de uma investigação difícil de falha. |
| `antigravity-security` | Pedir revisão adversarial de limites de confiança e segurança. |
| `antigravity-architect` | Pedir uma crítica de arquitetura após formular uma proposta. |

As skills `antigravity-*` requerem Linux, `agy` e `bwrap`. Elas complementam a
análise do agente que as invoca; não substituem sua investigação nem decisão.
Boost é o padrão; `ANTIGRAVITY_REVIEW_MODE=standard` seleciona o modo convencional.
Consulte os [pré-requisitos e isolamento do helper](antigravity-reviewer/scripts/README.md).

## Instalação local

Pré-requisitos: Bash, `ln`, `readlink` e permissões para criar links em
`~/.agents/skills` e `~/.claude/skills`.

Na raiz deste repositório, confira primeiro o estado atual:

```bash
scripts/install-local.sh --check
```

Para criar os links ausentes:

```bash
scripts/install-local.sh --install
```

O instalador cria um link por skill em:

| Destino | Agentes |
| --- | --- |
| `~/.agents/skills` | Codex e Gemini CLI |
| `~/.claude/skills` | Claude Code |
| `~/.gemini/config/skills` | Antigravity (`agy`) |

Também cria um link por arquivo de `.claude/agents/` em `~/.claude/agents`,
para que os subagentes do Claude Code valham em qualquer projeto.

Ele é idempotente: aceita links que já apontem para esta cópia do repositório e
recusa arquivos, diretórios ou links que apontem para outro destino. Não apaga,
move nem sobrescreve nada. Ele não altera `~/.codex/skills`.

Após instalar, reinicie a sessão do agente ou use o comando de recarga que ele
oferecer. Exemplos de invocação explícita:

```text
Codex:  Use $humanizer para revisar este documento.
Claude: /humanizer Revise este documento.
Gemini: Use a skill humanizer para revisar este documento.
Codex:  Use $cost-aware-delegation para coordenar esta tarefa com economia de modelos.
```

No Codex, use `/skills` para conferir a descoberta. No Gemini CLI, confira com
`/skills list` e recarregue com `/skills reload`. No Claude Code, `/humanizer`
aparece entre os comandos quando a skill está disponível. Cada agente também
pode selecionar uma skill pela descrição em seu `SKILL.md`.

## Delegação e verificação

A `cost-aware-delegation` informa o modelo solicitado por tarefa e distingue o
modelo efetivo confirmado do desconhecido. Os quatro papéis são níveis de
trabalho, não configurações instaladas de modelos. O agente consulta as capacidades
da sessão; a skill não altera o modelo principal nem cria workers no provedor.

No Claude Code, a skill usa os subagentes de `.claude/agents/`, cada um com
papel, modelo, esforço e ferramentas fixos no frontmatter:

| Agente | Papel | Modelo / esforço | Escrita |
| --- | --- | --- | --- |
| `pesquisador-haiku` | Coleta e busca delimitadas | haiku / low | não |
| `executor-haiku` | Edições especificadas e verificações definidas | haiku / low | sim |
| `pesquisador-sonnet` | Pesquisa com síntese de fontes | sonnet / medium | não |
| `implementador-sonnet` | Implementação moderada | sonnet / medium | sim |
| `especialista-opus` | Problema difícil e isolado | opus / high | sim |
| `revisor-opus` | Revisão independente exigida por gate | opus / high | não |

O nome do agente aparece na interface no lugar de `general-purpose`.

O orçamento inicial é ajustável (2 workers simultâneos, 3 inicializações e uma
rodada de correção por subtarefa). A economia depende do consumo total e da
qualidade; sem medição, deve ser declarada como não medida. Consulte o
[protocolo de avaliação](cost-aware-delegation/references/evaluation.md) para
comparar a política com execução direta.

As regressões do helper não precisam de credenciais:

```bash
python3 -B -m unittest discover -s antigravity-reviewer/scripts/tests -p 'test_*.py' -v
```

## Limites

Estes links só tornam as skills acessíveis aos aplicativos locais configurados
nesta máquina. Um LLM hospedado na nuvem só poderá usá-las se o aplicativo ou
integração que o hospeda fornecer acesso ao diretório local.

Consulte [ATTRIBUTION.md](ATTRIBUTION.md) para as inspirações e atribuições.
O conteúdo deste repositório está sob a [licença MIT](LICENSE).
