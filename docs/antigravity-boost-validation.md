# Resultado da investigação: Boost headless

> **Registro histórico.** Este relatório descreve a tentativa anterior com
> `--ro-bind / /`, que foi descartada. O estado descrito em "Estado final" não
> é mais o atual: o modo Boost, `ANTIGRAVITY_REVIEW_MODE` e o filesystem mínimo
> foram implementados depois, conforme
> [antigravity-boost-isolation-investigation.md](antigravity-boost-isolation-investigation.md)
> e [antigravity-reviewer/scripts/README.md](../antigravity-reviewer/scripts/README.md).
> Caminhos em `/tmp` citados abaixo eram artefatos locais e não acompanham o repositório.

Validação em 30/09/2026 (America/Fortaleza), com `agy 1.2.13`, Linux e
Bubblewrap. **Boost funciona com `agy --print`, mas a integração não foi
publicada porque a validação de isolamento dos workers falhou.** O helper e
as quatro skills foram restaurados ao conteúdo anterior. Este relatório fica
local, sem commit, PR ou merge; não representa suporte implementado.

## Base Git

O checkout estava limpo em `feat/cost-aware-escalation-gates`, um commit à frente
de `origin/main`. Após autorização do usuário, foi criada
`feat/antigravity-boost-default` a partir dessa base, preservando
`01515ef2ba7d790dae2fc4c80933b10f84d55f80` (gates de escalada e garantia de delegação).
Nenhum histórico foi reescrito e nenhum force-push foi executado.

## Testes de headless

Os testes copiaram o helper para `/tmp`, mantendo `--sandbox`,
`bwrap --ro-bind / /`, os binds originais de estado/contexto e o overlay de
permissões. Somente tokens, uma soma e pseudocódigo sintéticos foram enviados.
A revisão de segurança usou apenas o helper público. Stdin do `agy` ficou em
`/dev/null`; stderr permaneceu separado de stdout.

`<prompt fixo>` abaixo é o prompt do helper que manda ler o contexto temporário.

| Variante | Comando do CLI dentro do Bubblewrap | Exit code | Resposta |
| --- | --- | --- | --- |
| Standard original | `agy --sandbox --disable-slash-commands --print-timeout 10m --print '<prompt fixo>'` | 0 | `BOOST_HEADLESS_OK`, 18 bytes |
| Boost | `agy --sandbox --print-timeout 10m --print '/boost <prompt fixo>'` | 0 | Não vazia, com `BOOST_HEADLESS_OK`; uma chamada escolheu Solo |
| Boost com expansão desativada | `agy --sandbox --disable-slash-commands --print-timeout 10m --print '/boost <prompt fixo>'` | 0 | `BOOST_HEADLESS_OK`, 18 bytes; resposta do modelo não comprova Boost |

O help define `--disable-slash-commands` como desativação da expansão de comandos
e skills em print. O changelog local registra suporte à expansão desde 1.1.9.
Uma cópia de diagnóstico acrescentou `--output-format stream-json` e registrou
`expanded_commands: [{"name":"boost","type":"system"}]`: prova de interpretação
pelo CLI, não somente texto repetido pelo modelo.

Um diagnóstico explicitamente delegado registrou `invoke_subagent` ACTIVE/DONE
para `DeepInvestigator`. Seu transcript sintético confirmou dois workers de
investigação, respostas e `send_message` concluídos. A chamada terminou com
SUCCESS e resposta não vazia em 128,57 segundos. Não houve shell, escrita de
projeto, MCP ou navegação. Consultas simples também podem seguir Solo: `/boost`
não garante workers em toda consulta. Não foi demonstrada menor latência.

## Falha de isolamento reproduzida

A primeira pipeline leu `settings.json`, `response.txt` e transcripts da própria
sessão sintética além de `context.txt`, contrariando o prompt. A implementação
provisória adicionou denies explícitos para o estado do CLI e arquivos auxiliares,
além de `read_url(*)`. Ela foi validada com uma fixture descartável em `/tmp`,
contendo somente `nested/marker.txt` e um marcador público sintético.

O diagnóstico manteve o mesmo Bubblewrap e as permissões propostas. Acrescentou
`read_file(<fixture>)` ao deny e usou um prompt diagnóstico que autorizava somente
tentativas contra os arquivos sintéticos, sem acessar estado real de autenticação.
Workers herdaram os denies: seus resultados concretos mostraram:

| Operação do worker | Resultado observado |
| --- | --- |
| `view_file(context.txt)` | Permitido |
| `view_file(settings.json)` e `view_file(response.txt)` | Bloqueados por deny |
| `view_file(<fixture>/nested/marker.txt)` | Bloqueado pelo deny do diretório pai |
| `list_dir(<fixture>)` | Bloqueado por deny |
| `grep_search` no diretório e no marcador | Bloqueados por deny |
| `find_by_name` com `Pattern: "*"` e `SearchDirectory: <fixture>` | **Retornou `nested` e `nested/marker.txt` apesar do deny** |

O transcript do worker confirma o resultado de `find_by_name`; não é apenas uma
alegação do modelo. O diagnóstico terminou com exit 0/SUCCESS, mas com verdict
`RESTRICTION_FAILED`. Conteúdo do marcador não foi recuperado pelos leitores
bloqueados; a enumeração de nomes já viola o escopo exigido. A evidência não prova
bypass de leitura de conteúdo nem de escrita e não deve ser descrita assim.

A documentação pública de permissões não oferece uma categoria específica
verificada para negar `find_by_name`. Não foram inventados nomes de regras nem
usados bypasses. Ativar Boost por padrão com essa lacuna não satisfaria a garantia
de acesso somente ao contexto. Uma solução futura precisa de restrição efetiva
verificável dessas ferramentas ou de um desenho de estado/filesystem mais isolado;
essa arquitetura não foi implementada nesta tentativa.

Uma revisão automática rejeitou um diagnóstico anterior que solicitava leitura
no estado autenticado, pelo risco de exposição caso o deny falhasse. Esse comando
não foi executado. A alternativa com fixture descartável foi aprovada e revelou
a falha sem solicitar acesso a tokens, cookies ou arquivos de autenticação.

## Demais validações da implementação provisória

Passaram antes de ela ser retirada:

- `bash -n` e YAML frontmatter das quatro skills;
- três symlinks resolvendo para o helper central;
- modos ausente/boost/standard; valor inválido e variável vazia com exit 2;
- contexto literal com slash command fora do argv do prompt;
- exit code 37 do CLI propagado; resposta vazia com exit 1; stdin vazio com exit 2;
- limpeza de temporários em sucesso/falha e diretório privado 0700;
- timeout override e hash SHA-256 da configuração real preservado;
- tentativa real de escrita sob `bwrap` bloqueada com errno 30 (`EROFS`);
- regressão do reviewer com Boost padrão e standard: respostas não vazias,
  `BOOST_HEADLESS_OK` e exit code 0;
- `git diff --check` e revisão das mudanças. Nenhum estado de autenticação foi
  incorporado ao repositório.

O timeout permaneceu em 10 minutos: os testes concluíram dentro dele. Não há
justificativa para aumentá-lo com base nesta investigação.

## Estado final

O comportamento continua convencional, com `--disable-slash-commands`. Não existe
`ANTIGRAVITY_REVIEW_MODE` implementado. `ANTIGRAVITY_REVIEW_TIMEOUT` continua
aceitando override. As garantias atuais não foram reduzidas, o commit de delegação
foi preservado na base local e nenhum novo commit/push/PR/merge foi realizado.
O CLI pode manter o contexto sintético em seu histórico; os diretórios temporários
do helper foram removidos. Os artefatos locais de diagnóstico ficam em
`/tmp/agy-boost-validation` para investigação, sem autenticação.

Referências oficiais: [Boost](https://antigravity.google/docs/boost/) (pipeline e
herança de permissões) e [permissões do CLI](https://antigravity.google/docs/permissions/)
(categorias `action(target)` e prioridade Deny > Ask > Allow).
