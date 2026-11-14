# ONDE-PAREI: reescrita da Central (verificador, 13/11/2026)

Tarefa só de texto; nenhuma linha do programa mudou. Nada foi gravado na Central; a entrega é `novas/<aba>.json`.

## Decisões que esta tarefa precisa cumprir
- CLAUDE.md §11.13 (Samuel, 13/11): "precisa ajeitar para isso como regra [...] para responder e fazer perguntas."
- §11.7 (27/10): "é só para fazer o que eu já tinha mandado" — não mudar decisão nem opção já escolhida.
- §11.8 / D-605 (03/11): o novo não estraga o já escolhido e testado — cada pergunta diz o que muda no que funciona.
- §10 (10/11): prints no modelo do girar.

## Como cumpri cada uma
- §11.13: cada pergunta reescrita no molde (onde fica e o que é · de onde veio · como está · o que escolhe), sem
  códigos no meio (busca final: zero nas 141 da auditoria). Detalhe em `relatorio.html`.
- §11.7: ids de perguntas e opções iguais (conferido por script); nenhuma opção saiu; opções novas só onde o
  comentário dele pediu outra coisa (b-abas-nomes, mover-rotulo-antes).
- D-605: as perguntas de conserto (rev-*, mover-rotulo-antes) dizem o que muda no que já funciona.
- §10: 7 imagens novas no modelo do girar (`novas/imagens/`), abertas e conferidas uma por uma.

## Andamento
- [x] Parte 1 (8 perguntas).
- [x] Parte 2 (17 perguntas, aba nomes-28-10).
- [x] Parte 3 (141 perguntas, abas de auditoria 3 a 6) + lista "pode sair" (8).
- [x] Relatório nos três formatos; worktree `central-reescrita` removida (junções tiradas antes; originais conferidos:
  modelos 7 itens, gabarito\paginas 64 itens).
