# Protótipo de filesystem mínimo para Antigravity

Data: 30/09/2026, America/Fortaleza. AGY 1.2.13, Linux/Bubblewrap.
Foi lido integralmente `antigravity-boost-validation.md`, conforme autorização
para usar o relatório local no lugar do caminho inexistente em `/mnt/data`.

## Resultado

O protótipo autenticado passou em Standard, Boost e no teste crítico de descoberta.
A integração ao helper foi bloqueada por duas rejeições da revisão automática de
aprovação, que exigiu autorização explícita para a transferência da credencial e
aplicação da nova fronteira de isolamento. Nenhuma alteração funcional foi aplicada;
nenhum novo commit, push, PR ou merge foi realizado. As regressões do controlador
final ainda não foram executadas, pois esse controlador não foi instalado.

## Namespace comprovado no protótipo

Não existe `--ro-bind / /`, mount amplo de `/usr`, HOME real, projeto ou estado real.
Os mounts explícitos testados foram:

- binário ELF `agy` em `/usr/bin/agy`;
- loader ELF e seis bibliotecas glibc: libc, libm, libdl, librt, libpthread e libresolv;
- bundle TLS e arquivo efetivo de resolução DNS, ambos somente leitura;
- passwd/group/hosts/nsswitch gerados para o usuário sintético, sem dados pessoais;
- `/dev` sintético, `/proc` com namespace PID próprio e `/tmp` em tmpfs;
- contexto único somente leitura em `/context/context.txt`;
- HOME sintético descartável em `/home/agy`, contendo apenas estado novo do CLI;
- somente o socket Unix de um Secret Service privado em `/auth/bus`, como bind RO.

Root foi remountado somente leitura. PID/IPC/UTS foram separados; AGY recebeu
ambiente limpo e sessão nova. Não foram herdados DISPLAY, D-Bus real, API keys,
variáveis de language server ou configurações pessoais. Rede permaneceu disponível
para o serviço autenticado do AGY. Não se afirma isolamento de rede.

`ldd` verificou as dependências ELF. Standard autenticado confirmou também o
funcionamento de resolução/TLS nesse runtime reduzido. Não foram instaladas
bibliotecas, Docker, Podman ou outras dependências.

## Autenticação

A documentação oficial indica Secret Service no Linux. Metadados do keyring
identificaram o item do AGY: `service=gemini`, `username=antigravity`.
O protótipo transferiu exclusivamente esse item com `secret-tool`, por pipe anônimo,
para um Secret Service novo por consulta. Tokens não foram colocados em argv,
variáveis de ambiente, logs, arquivos do repositório ou arquivo plaintext intermediário.

O broker privado usa D-Bus sem diretórios de serviços ativáveis, mais
`gnome-keyring-daemon --foreground --unlock --components=secrets`, com senha aleatória
via stdin. Seu HOME e armazenamento de keyring ficam FORA do namespace do AGY.
O AGY recebe somente o socket privado e a credencial necessária via Secret Service;
o D-Bus/coleção de segredos reais não são montados. O libsecret exige handshake
`StartServiceByName`; ele foi permitido, mas não há configuração de ativação de
serviços externos. Monitoramento e UpdateActivationEnvironment foram negados.

Essa etapa exige confiar no controlador local para transferir o único item autorizado
e no binário AGY para autenticar no seu serviço. Os daemons privados foram encerrados
e reaped; os diretórios de autenticação e estado temporário foram removidos ao final.
Nenhum histórico anterior, transcript antigo ou cache real foi copiado.

## Evidência funcional

Cada chamada usou `agy --sandbox --print-timeout 2m --output-format stream-json`
dentro do namespace descrito, stdin em `/dev/null` e defesa de permissões:
`write_file(*)`, `command(*)`, `mcp(*)`, `read_url(*)`, `execute_url(*)`,
`read_file(/home/agy)` e `read_file(/auth)` negados.

| Teste | Resultado |
| --- | --- |
| Standard, com `--disable-slash-commands` | Exit 0, SUCCESS, resposta `ISOLATED_STANDARD_OK` |
| Boost, prefixo fixo `/boost` | Exit 0, SUCCESS, resposta não vazia com token; delegação interna |
| Expansão | `expanded_commands: [{"name":"boost","type":"system"}]` |
| Canary externo com workers | Exit 0, SUCCESS, chamadas reais de descoberta registradas |

O timeout do helper deverá continuar em 10 minutos; os valores menores foram
usados apenas nos probes. Não se demonstrou menor latência nem necessidade de
ampliar o timeout. A criação de workers não é obrigatória em toda consulta.

## Teste crítico por workers

A fixture sintética `/tmp/agy-private-canary-isolation/nested/marker-SHOULD-NOT-BE-VISIBLE.txt`
existia no host e NÃO foi montada. O diagnóstico permitiu explicitamente leitura
desse path nas permissões, para testar filesystem em vez de apenas obter deny.
O prompt diagnóstico só autorizou o canary sintético e contexto, sem leitura de
paths pessoais. Os registros concretos dos workers mostraram:

| Ferramenta | Resultado real |
| --- | --- |
| `view_file` no marcador | `stat ...: no such file or directory` |
| `list_dir` na fixture | `directory ... does not exist` |
| `grep_search` na fixture | `search path ... does not exist` |
| `find_by_name` na fixture | `search directory ... does not exist` |
| `view_file` no contexto | Conteúdo sintético montado lido normalmente |
| Tentativa de ler transcript do próprio estado descartável | Bloqueada pelo deny de `/home/agy` |

Assim, o canary não foi enumerado nem lido, inclusive pela ferramenta que havia
ignorado o deny na arquitetura antiga. Não foi apenas uma afirmação do modelo.
Os registros de ferramentas/resultados foram preservados em
`/tmp/agy-isolated-investigation/canary-tool-evidence.json` antes de destruir o estado.

## Teste por syscalls, independente das permissões do AGY

Um pequeno executável de teste, sem libc/shell, foi montado adicionalmente no mesmo
namespace para os probes. Confirmou `ENOENT` para HOME real, repositório real,
fixture externa, caminho ao HOME via `/proc/1/root` e bus real do usuário.
Nenhum arquivo pessoal foi lido; esses paths foram testados somente por existência.

- Criar arquivo sob o path do projeto: `ENOENT`, pois o projeto não está montado.
- Escrever no root ou contexto RO: `EROFS`.
- Escrever em `/tmp` e HOME descartável: permitido e removido com o descarte.
- FD externo para o canary: fechado ao usar `close_fds=True` no controlador.

Foi identificado que o Bubblewrap sozinho preserva FDs herdados. Portanto,
`close_fds=True`, sem `pass_fds`, é requisito obrigatório em TODOS os subprocessos
do controlador proposto, além dos mounts mínimos. O primeiro probe propositalmente
herdou FD 9 e detectou o vazamento; o segundo, com fechamento explícito, passou.

## Preservação e limites restantes

Hash da configuração real preservado; inventário de tamanho/mtime de 1261 arquivos
do estado real permaneceu igual após a baseline. Não houve mount do estado real
nem comandos de store/clear nele. Nenhuma credencial foi impressa.

A branch nova `feat/antigravity-boost-isolated` preserva
`01515ef2ba7d790dae2fc4c80933b10f84d55f80`. O helper funcional continua no estado
anterior. Sintaxe/frontmatter/symlinks originais foram conferidos.

A revisão automática rejeitou as duas tentativas de edição por considerar a
transferência do item de autenticação e a nova fronteira ainda não comprovadas,
e pediu aprovação explícita. As rejeições não foram contornadas. Para prosseguir,
a edição deve ser aprovada; depois ainda serão necessários testes de regressão
sobre o código final, revisão de segurança, diff/segredos e só então publicação.

O runtime mínimo poderá variar por distribuição/versão do CLI. O protótipo comprova
a versão e máquina testadas, não todos os ambientes. Diretórios de runtime e estado
novo necessários ao CLI existem no namespace; a garantia demonstrada é ausência
de filesystem pessoal/estado histórico real, não ausência de qualquer arquivo além
do contexto. Rede é necessária; o binário autenticado continua sendo confiável.

Referências: [autenticação oficial](https://antigravity.google/docs/cli/install/)
e [keyring no Linux](https://antigravity.google/docs/cli/troubleshooting/).
