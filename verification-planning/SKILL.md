---
name: verification-planning
description: Planeja evidências verificáveis para mudanças de software, infraestrutura, dados e Edge, ajustando o esforço à afirmação que precisa ser sustentada.
---

# Planejamento de verificação

Use esta skill antes de declarar uma mudança concluída, especialmente quando ela
atravessa aplicação, CI, containers, mensageria, modelos ou hardware Edge.

## Método

1. Escreva a afirmação a comprovar em termos observáveis: por exemplo, “a API
   persiste o evento publicado”, “a imagem inicia sem câmera” ou “o modelo foi
   materializado no dispositivo”.
2. Liste os limites envolvidos: processo, banco, broker, rede, imagem, câmera,
   GPIO ou serviço externo. Separe uma verificação local de uma integração real.
3. Escolha a menor evidência que sustenta a afirmação e registre o comando,
   ambiente, entrada e resultado esperado. A evidência deve ser proporcional ao
   impacto: leitura estática para uma alteração isolada; teste automatizado para
   comportamento de código; integração para contratos entre serviços; ambiente
   físico quando a afirmação envolve câmera, esteira ou sensores.
4. Declare o que a evidência não cobre. Um teste com broker anônimo, por
   exemplo, não comprova ACLs de produção; um build de container não comprova o
   acesso à câmera; ponteiros DVC atualizados não comprovam que o artefato foi
   baixado.
5. Execute as verificações em ordem de menor custo e risco: estática, unidade,
   integração, ambiente implantado e hardware. Pare e investigue ao primeiro
   resultado que contradiga a afirmação.

## Resultado esperado

Entregue um plano curto com:

- afirmação e risco se ela estiver errada;
- evidência proposta, comando ou procedimento e critério de aceitação;
- ambiente necessário e dados de teste;
- lacunas conhecidas e a próxima evidência necessária.

Prefira evidências reproduzíveis e preserve logs relevantes sem incluir tokens,
senhas, URLs privadas ou dados pessoais. Diferencie claramente “verificado”,
“pendente” e “bloqueado pelo ambiente”.
