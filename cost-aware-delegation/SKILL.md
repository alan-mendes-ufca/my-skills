---
name: cost-aware-delegation
description: Divida tarefas não triviais entre o agente principal (planeja, define contratos, integra e decide) e subagentes menores (implementam), escolhendo o modelo de cada um, informando-o ao usuário e pedindo uma revisão concorrente a um modelo maior quando o risco for alto ou o trabalho travar.
---

# Delegação econômica

**O principal planeja, define contratos e integra. Subagentes menores executam.**
O principal costuma rodar no modelo mais caro; cada token que ele gasta
implementando pesa mais na cota do que o mesmo trabalho num worker barato.
Economia vem do consumo total (inclui retrabalho), não de menos chamadas.
Sem medição, diga **economia não medida**.

## Fluxo

### 1. Decida

- Trivial, acoplado ou mais barato de fazer do que de explicar: faça direto.
- Trabalho substancial e delimitado: delegue. Peças independentes podem
  rodar em paralelo, poucas por vez.
- Se o ambiente só cria subagentes a pedido do usuário e não há autorização,
  pergunte uma vez, antes de começar, se pode delegar.

### 2. Escolha o worker

Leia a referência do ambiente: [Claude Code](references/claude.md) ou
[Codex e Gemini](references/runtimes.md). Escolha o menor nível que dá conta:

| Papel | Trabalho |
| --- | --- |
| `cheap_worker` | Coleta, edição especificada, tarefa repetitiva, rodar verificações. |
| `balanced_worker` | Bug localizado, implementação moderada, testes não triviais. |
| `deep_worker` | Investigação difícil ou implementação isolada complexa. |

Envie sempre o modelo explicitamente; omitir herda o modelo do principal e
anula a economia. Use contexto novo e mínimo: objetivo, arquivos que o worker
pode editar, critério de aceitação e formato de retorno curto. Cada arquivo
tem um só responsável. Requisito ambíguo ou decisão de arquitetura, produto
ou segurança fica com o principal.

### 3. Anuncie

Antes de cada delegação, uma linha, no texto da mesma resposta e antes da
chamada. Para vários workers, uma linha por worker, todas antes do lançamento:

`Tarefa → modelo: <ID ou alias real> → motivo`

Se o runtime mostrar um modelo diferente do pedido, avise o usuário.

### 4. Integre e verifique

Confira o diff e rode as verificações proporcionais ao risco. Um relatório do
worker não é prova. Mantenha as ressalvas dele ("não confirmado") no resumo.
Se o worker falhar na aceitação, corrija o escopo uma vez; persistindo,
assuma ou escale o nível.

## Revisão concorrente

Quando o risco for alto, peça a um modelo maior (`deep_worker`) uma revisão
**enquanto** você continua o trabalho. Dispare nestes casos:

- **Risco alto:** a decisão é difícil de reverter, mexe em segurança,
  credenciais ou dados reais, ou um erro custaria dias.
- **Travado:** duas tentativas fundamentadas falharam, ou a evidência é
  contraditória.

Como pedir:

1. Contexto novo: passe o plano ou o diff e os arquivos, **sem** o seu
   raciocínio, para a revisão ser independente.
2. Diga qual decisão avaliar e o que procura (o que tornaria errada).
3. Se o runtime aceitar esforço por chamada, não use o mínimo: a revisão
   existe porque o risco é alto.
4. Uma revisão por decisão; só repita com evidência nova.

A revisão informa; a decisão é do principal. Verifique as alegações dela.

## Fechamento

Antes de concluir: aceitação atendida, delegações anunciadas feitas de fato
(não simuladas), riscos restantes ditos ao usuário. Para testar esta skill,
veja [references/evaluation.md](references/evaluation.md).
