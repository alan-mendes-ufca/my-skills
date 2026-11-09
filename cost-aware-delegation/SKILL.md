---
name: cost-aware-delegation
description: Divida tarefas não triviais entre o agente principal (planeja, define contratos, integra e decide) e subagentes menores (implementam), escolhendo o modelo de cada um, informando-o ao usuário e pedindo uma revisão concorrente a um modelo maior quando o risco for alto ou o trabalho travar.
---

# Delegação econômica

**O principal planeja, define contratos e integra. Subagentes menores executam.**
O principal costuma rodar no modelo mais caro; cada token que ele gasta
implementando pesa mais na cota do que o mesmo trabalho num worker barato.
Economia vem do consumo total (inclui retrabalho), não de menos chamadas.
Sem medição, diga **economia não medida**; para medir, use
[scripts/usage-report.py](scripts/usage-report.py).

## Fluxo

### 1. Decida

- Trivial, acoplado ou mais barato de fazer do que de explicar: faça direto.
- Cadeia de passos dependentes que cabe num contexto só: faça direto ou use
  um único worker. Vários agentes só pagam quando há peças independentes.
- Trabalho substancial e delimitado: delegue. Peças independentes podem
  rodar em paralelo, poucas por vez.
- Se o ambiente só cria subagentes a pedido do usuário e não há autorização,
  pergunte uma vez, antes de começar, se pode delegar.

**Contrato é o que o principal escreve:** tipos, assinaturas, stubs, pontos de
extensão em arquivos compartilhados e critérios de aceitação. Lógica, dados,
arte, testes e documentação além disso são implementação: delegue. Se você
está prestes a escrever um módulo ou uma suíte de testes inteira, pare e
delegue.

### 2. Escolha o worker

Leia a referência do ambiente: [Claude Code](references/claude.md) ou
[Codex e Gemini](references/runtimes.md). Escolha o menor nível que dá conta:

| Papel | Trabalho |
| --- | --- |
| `cheap_worker` | Coleta, edição especificada, tarefa repetitiva, rodar builds, testes e ler logs longos. |
| `balanced_worker` | Bug localizado, implementação moderada, testes não triviais, análise interpretativa de dados reais. |
| `deep_worker` | Investigação difícil ou implementação isolada complexa. |

- Tarefas equivalentes no mesmo lote usam o mesmo nível: não divida
  análises iguais entre modelos diferentes.
- Interpretar falas, documentos ou dados de pessoas reais começa no
  `balanced_worker`; o `cheap_worker` só extrai e coleta.
- Verificação longa (build, suíte de testes, logs) também é delegável: peça
  ao `cheap_worker` o resultado resumido, não o log inteiro.
- Implementação começa no `cheap_worker` quando valem as três condições:
  contrato fechado, resultado conferível por comando e tarefa curta. O erro
  de um modelo pequeno precisa ser barato de perceber.
- Laço longo (muitos passos encadeados, processos em segundo plano,
  depuração aberta) não vai para o `cheap_worker`: divida em tarefas curtas
  ou use o `balanced_worker`. Compare o custo da tarefa concluída, não o
  preço por token.
- Ao escolher o `balanced_worker` com contrato fechado, o motivo do anúncio
  diz o que exige mais (ambiguidade, decisão de design, laço longo, falha
  anterior do nível barato).

Envie sempre o modelo explicitamente; omitir herda o modelo do principal e
anula a economia. Cada arquivo tem um só responsável. Requisito ambíguo ou
decisão de arquitetura, produto ou segurança fica com o principal.

Use contexto novo e mínimo, com estes campos no prompt:

1. **Objetivo** e contexto já descoberto (não peça para refazer investigação).
2. **Arquivos** que o worker pode editar; todo o resto é somente leitura.
3. **Critério de aceitação** verificável (comando, teste ou saída esperada).
4. **Retorno** curto: o que mudou, resultado da verificação, ressalvas.

Continue um worker existente só para corrigir o mesmo escopo. Escopo novo
pede worker novo, para não acumular contexto alheio.

### 3. Anuncie

Antes de cada delegação, uma linha **no texto visível** da mesma resposta,
antes da chamada. Para vários workers, uma linha por worker, todas antes do
lançamento:

`Tarefa → modelo: <ID ou alias real> → motivo`

Exemplo de lote com três workers:

```text
Sala e passagem do tempo → sonnet → arte procedural com decisões visuais
Itens com efeito → haiku → contrato fechado em game_state.gd
Builds Linux e Windows → haiku → comandos definidos, só verificar
```

Uma frase que resume o lote ("inicio a fase 3 com três workers, dois no
sonnet") não substitui as linhas. Intenção escrita só no raciocínio também
não conta como anúncio: o usuário não a vê.
Se o runtime mostrar um modelo diferente do pedido, avise o usuário.

### 4. Integre e verifique

Confira o diff e rode as verificações proporcionais ao risco. Um relatório do
worker não é prova. Mantenha as ressalvas dele ("não confirmado") no resumo.
Se o worker falhar na aceitação, suba um degrau por vez e registre o motivo:

1. **Verificação:** corrija o escopo e ponha no prompt o comando que o
   worker roda antes de relatar.
2. **Esforço:** um nível acima no mesmo modelo, se o runtime permitir.
3. **Modelo:** o nível seguinte, começando no esforço mais baixo dele.

Depois de dois degraus sem sucesso, trate como travado (revisão concorrente)
ou assuma a tarefa.

### 5. Poupe o principal

O principal relê o contexto inteiro a cada turno; nas sessões medidas ele
consumiu mais do que todos os workers somados. Cada turno seu é o mais caro
da sessão:

- Não espere worker com `sleep` em laço nem polling: use a espera do runtime
  ou encerre o turno.
- Verificação longa, script de bancada e monitoramento vão para um worker
  barato, com condição de parada e retorno resumido.
- Monitores e notificações viram turnos do principal: filtre para os eventos
  que mudam uma decisão.
- Ao fim de uma fase grande, sugira ao usuário compactar ou abrir sessão
  nova com o estado salvo. Não troque o modelo do principal no meio da
  sessão: a troca paga o cache inteiro de novo.

## Revisão concorrente

Quando o risco for alto, peça a um modelo maior (`deep_worker`) uma revisão
**enquanto** você continua o trabalho. Dispare nestes casos:

- **Risco alto:** a decisão é difícil de reverter, mexe em segurança,
  credenciais ou dados reais, ou um erro custaria dias. Corrigir
  autenticação, autorização, papéis ou permissões conta como segurança,
  mesmo quando a correção parece pequena.
- **Travado:** duas tentativas fundamentadas falharam, ou a evidência é
  contraditória.

Como pedir:

1. Contexto novo: passe o plano ou o diff e os arquivos, **sem** o seu
   raciocínio, para a revisão ser independente.
2. Diga qual decisão avaliar e o que procura (o que tornaria errada).
3. Modelo: acima do principal; se o principal já está no nível mais alto
   disponível, o mesmo nível em contexto novo. Nunca um modelo menor.
4. Esforço, se o runtime aceitar por chamada: pelo menos `medium`, nunca o
   mínimo. A revisão existe porque o risco é alto.
5. Uma revisão por decisão; só repita com evidência nova.

`/code-review` ou `antigravity-reviewer` sobre o diff valem como a revisão,
desde que rodem em contexto novo. A revisão informa; a decisão é do
principal. Verifique as alegações dela.

## Fechamento

Antes de concluir, confira:

- Aceitação atendida e verificada por você, não só relatada pelo worker.
- Cada delegação teve linha visível de anúncio e foi feita de fato (não
  simulada).
- Se o diff toca autenticação, permissões, credenciais ou dados reais, a
  revisão concorrente foi feita; se não foi, diga ao usuário por quê.
- Riscos restantes e ressalvas dos workers ditos ao usuário.
- Escaladas de esforço ou de modelo ditas ao usuário, com o motivo.

Para testar esta skill, veja [references/evaluation.md](references/evaluation.md).
