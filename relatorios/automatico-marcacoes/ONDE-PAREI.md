# Automático: botão "marcações" na barra de baixo (D-578, D-580) — ONDE PAREI

Ramo `automatico-marcacoes-2026-10-29` (saiu de `obra-2026-10-26`, commit `ac0b9ec`).
Worktree `D:\programas\EditorImpressao\.claude\worktrees\auto-marcacoes`. Agente de tela, 29/10/2026.

## Decisões que esta tarefa precisa cumprir

(escrito antes de começar a mexer no código)

- **D-578** (29/10/2026): "um bug que acontece quando nós usamos o automatico, de vez as paginas mudarem, elas
  continuam iguais, mas o que aparece são as marcações feitas no pdf, de gravura e de letras, tem que ter um jeito de
  aparecer e desaparecer essas marcações nas paginas." · "não tem nenhuma opção de marcação escolhida, está o zoom
  escolhido". Na prática: depois do Automático, a página deve aparecer como vai sair, não coberta de cores.
- **D-580** (29/10/2026): "A" — "A — Na barra de baixo, começando escondido. O botão "marcações" fica ao lado de "Uma
  página / Duas lado a lado / antes / depois". Com qualquer ferramenta, até com o Zoom, a página aparece limpa, como vai
  sair. Um clique mostra as cores e outro esconde." Na prática: botão de ligar/desligar chamado "marcações" na barra de
  baixo, mesmo estilo dos vizinhos; de fábrica desligado; desligado = sem o colorido e sem o contorno das feitas à mão,
  com qualquer ferramenta; ligado = como hoje. Vale enquanto o programa está aberto (todas as páginas e livros); volta a
  desligado ao abrir o programa; nada gravado no projeto, nada muda no PDF.
  Detalhes fixados pela gerente: o traço que está sendo desenhado continua aparecendo; o contorno laranja da caixinha
  "Mostrar as áreas achadas" e o laranja das páginas do "Para revisar" continuam com as regras deles; a caixa da área
  escolhida pela ferramenta Ajustar continua.
- **D-237** (06/10 e 08/10/2026): "mas quando eu quiser ver as areas achadas, deve ter um botão ou aba para eu fazer
  isso, apertar nele e mostrar as areas achadas delineadas, no para revisar, elas já vão aparecer laranjas [...]" —
  não pode quebrar: o laranja continua aparecendo, com "marcações" ligado ou desligado.
- **D-278 / D-279** (09/10/2026): o lugar onde sumiu já marcado em laranja no aviso do "Para revisar" — não pode quebrar.
- **D-010** (26/10/2026): "eu acho que o botão tem que ser provado que ele faz o que se diz que se faz, e não só se ele
  muda algo na tela." — o botão novo ganha promessa escrita em `tests/promessas/promessas.md` e prova em
  `tests/test_promessas.py`.
- **D-001** (25/09/2026): "Estrutura: Photoshop puro, sem abas. Uma única tela com todas as ferramentas." — nada sai
  de vista; o botão novo só acrescenta à barra de baixo.
- **§11 regra 7** ("Só o que ele mandou"): nada além do nome "marcações" e de um balão de uma frase. Sem atalho, sem
  menu, sem aviso.
