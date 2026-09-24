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
| `antigravity-reviewer` | Pedir uma segunda opinião sobre implementação ou diff relevante. |
| `antigravity-debugger` | Pedir revisão de uma investigação difícil de falha. |
| `antigravity-security` | Pedir revisão adversarial de limites de confiança e segurança. |
| `antigravity-architect` | Pedir uma crítica de arquitetura após formular uma proposta. |

As skills `antigravity-*` requerem Linux, `agy` e `bwrap`. Elas complementam a
análise do agente que as invoca; não substituem sua investigação nem decisão.

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

Ele é idempotente: aceita links que já apontem para esta cópia do repositório e
recusa arquivos, diretórios ou links que apontem para outro destino. Não apaga,
move nem sobrescreve nada. Ele não altera `~/.gemini/config/skills` nem
`~/.codex/skills`.

Após instalar, reinicie a sessão do agente ou use o comando de recarga que ele
oferecer. Exemplos de invocação explícita:

```text
Codex:  Use $humanizer para revisar este documento.
Claude: /humanizer Revise este documento.
Gemini: Use a skill humanizer para revisar este documento.
```

No Codex, use `/skills` para conferir a descoberta. No Gemini CLI, confira com
`/skills list` e recarregue com `/skills reload`. No Claude Code, `/humanizer`
aparece entre os comandos quando a skill está disponível. Cada agente também
pode selecionar uma skill pela descrição em seu `SKILL.md`.

## Limites

Estes links só tornam as skills acessíveis aos aplicativos locais configurados
nesta máquina. Um LLM hospedado na nuvem só poderá usá-las se o aplicativo ou
integração que o hospeda fornecer acesso ao diretório local.

Consulte [ATTRIBUTION.md](ATTRIBUTION.md) para as inspirações e atribuições.
O conteúdo deste repositório está sob a [licença MIT](LICENSE).
