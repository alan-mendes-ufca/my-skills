---
name: security-audit
description: Conduz uma auditoria de segurança com escopo, fronteiras de confiança, evidência rastreável e proteção de segredos antes de qualquer verificação dinâmica.
---

# Auditoria de segurança

Use esta skill para revisar autenticação, autorização, entrada não confiável,
segredos, permissões, dados sensíveis, APIs, filas e mensageria. Uma auditoria
tem escopo definido; ela não autoriza sondagem de produção nem ações fora dos
ativos fornecidos.

## Preparação obrigatória

1. Defina os ativos, ambiente autorizado, objetivo, janela de execução e
   operações permitidas. Se algum desses limites faltar, faça apenas análise
   estática e registre a limitação.
2. Mapeie as fronteiras de confiança: usuário para aplicação, frontend para API,
   serviço para banco, dispositivo Edge para broker e serviço interno para
   serviço externo. Para cada fronteira, identifique identidade, autorização,
   transporte, validação e dados trocados.
3. Proteja segredos desde o início. Não imprima, copie para relatórios, envie a
   terceiros ou use credenciais reais em exemplos. Redija tokens, chaves,
   cookies, senhas, URLs assinadas e dados pessoais nos artefatos de evidência.

## Revisão

Comece pela análise estática de código, configuração, dependências e políticas.
Examine controles de acesso, validação de entrada, tratamento de erros,
armazenamento e rotação de segredos, permissões de processo e rede, TLS, logs,
limites de taxa e regras de broker quando aplicáveis. Relacione cada achado à
fronteira de confiança e ao caminho de exploração plausível.

Só proponha ou execute uma verificação dinâmica depois de confirmar autorização,
ambiente e impacto. Prefira ambientes de teste, contas sem privilégios e dados
sintéticos. Não faça varredura, enumeração, exploração, alteração de dados ou
teste de negação de serviço em produção sem autorização explícita e escopo
documentado.

## Relatório

Para cada achado, registre evidência redigida, ativo afetado, pré-condições,
impacto, severidade justificada, correção e forma de verificar a correção.
Separe fato observado, hipótese e risco residual. Um scanner sem achados ou
testes aprovados cobrem somente os caminhos avaliados e nunca comprovam que um
sistema esteja seguro.
