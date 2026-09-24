---
name: simplify
description: Simplifique código recentemente alterado após entender seu comportamento, mantendo resultados, erros, efeitos colaterais e convenções do projeto. Use para Python, PHP e TypeScript.
---

# Simplify

Simplifique a implementação sem alterar o contrato do código.

## Delimite o trabalho

1. Inspecione o diff e o contexto imediato antes de propor mudanças.
2. Entenda entradas, saídas, erros, efeitos colaterais, ordem de execução e dependências do trecho modificado.
3. Restrinja a simplificação ao código alterado e às correções diretamente necessárias para ele. Não transforme uma tarefa localizada em refatoração ampla.
4. Descubra e siga as convenções já usadas no projeto para nomes, tipos, erros, estilo e organização.

## Simplificações seguras

- Elimine duplicação local, variáveis intermediárias sem função e condições desnecessárias quando a leitura melhorar.
- Prefira fluxo explícito a abstrações novas que escondam regras de negócio.
- Preserve interfaces públicas, formatos de dados, mensagens e tipos de erro, efeitos de I/O, transações, logs relevantes e a ordem observável das operações.
- Respeite os idiomatismos e ferramentas existentes de Python, PHP e TypeScript; não force padrões de outra linguagem.

## Limites

- Não altere comportamento, validação, valores padrão, tratamento de exceção, concorrência, segurança ou desempenho sem que isso faça parte da solicitação.
- Não renomeie APIs públicas, mova módulos, atualize dependências nem faça formatação global como efeito colateral.
- Se o comportamento atual não estiver claro, pare a simplificação e descreva a dúvida com a evidência encontrada.

## Verificação

Execute a verificação mais próxima e relevante disponível: testes do módulo, checagem de tipos, lint ou teste de integração afetado. Se não puder executar uma verificação, informe qual seria a checagem necessária e por quê.

## Entrega

Explique de forma breve o que ficou mais simples, a preservação de comportamento verificada e os comandos de validação executados. Relate riscos ou verificações pendentes de forma explícita.
