---
name: post-refactor
description: Revisa uma refatoração no escopo alterado para encontrar regressões de comportamento, contratos quebrados e validações ausentes antes da entrega.
---

# Revisão após refatoração

Use esta skill depois de uma refatoração que já preservou a intenção funcional.
Concentre a revisão no diff e nas dependências diretas; amplie o escopo somente
quando a mudança revelar um contrato afetado.

## Procedimento

1. Leia o diff e descreva em uma frase qual comportamento deveria permanecer
   igual e qual estrutura foi alterada.
2. Compare entradas, saídas, erros, efeitos colaterais e ordem de operações
   antes e depois. Inclua contratos públicos, migrações, serialização, tópicos
   de mensageria e variáveis de ambiente quando existirem.
3. Procure referências que ficaram desatualizadas: importações, chamadas,
   documentação, testes, tipos, configurações, nomes de eventos e caminhos de
   execução.
4. Execute a menor validação que atravesse o comportamento alterado. Para uma
   mudança em backend ou frontend, comece pelos testes direcionados; para um
   fluxo Edge/MQTT, confirme também o contrato de tópico, payload e falha de
   entrega que a mudança alcança.
5. Registre achados com severidade, arquivo ou componente, impacto observável e
   correção sugerida. Não transforme melhoria de estilo fora do escopo em parte
   da refatoração sem justificar o risco que ela resolve.

## Critérios de saída

Considere a revisão pronta quando o comportamento preservado tiver evidência
proporcional, as referências diretas estiverem consistentes e os riscos
restantes forem explícitos. Testes verdes demonstram apenas os cenários que
executaram; informe os cenários não exercitados, sobretudo hardware, credenciais
reais e integrações externas.
