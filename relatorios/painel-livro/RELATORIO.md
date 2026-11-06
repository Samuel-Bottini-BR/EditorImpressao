# D-619 e D-620: relatório curto (04/11/2026)

Ramo `painel-livro-2026-11-04` (saiu de `obra-2026-10-26`, `2329129f`).

## Como cumpri cada decisão

- **D-619**: o quadro do livro do Propriedades se chama "Já feito no livro todo" no Dividir, no Cortar e no
  Endireitar (`_parte_do_livro`). Ele continua só mostrando. O "mudar no Automático..." e a caixinha "Margens
  iguais" (D-554) ficaram. Prints: `prints/1536-01..03`, `prints/1366-01..03`,
  `prints/quadros-ja-feito-no-livro-todo-1920.png`.
- **D-620**: a "Qualidade da prévia" saiu do painel do Cortar e foi para a barra de baixo, logo depois de
  "ajustar à tela".
  - É o jeito que o Samuel pediu: "não tem como colocar só uma setinha e quando aperta nela aparece as opções de
    qualidade?". Um botão pequeno, sem texto, com a setinha desenhada como os outros ícones da barra.
  - Apertar abre o menu Rápida / Média / Alta, com a escolhida marcada. O balão diz "Qualidade da prévia: Alta"
    (ou a escolhida).
  - Continua uma escolha só, gravada em `qualidade_previa`, com o mesmo efeito.
  - Na janela de verdade, escolhi "Alta" no Cortar: cliquei na setinha e usei as setas do teclado no menu. Ficou
    "Alta", gravada, a 300 DPI, no Endireitar, no Mover e no Dividir.
  - Prints: `prints/barra-com-a-setinha-1536-e-1366.png`, `prints/15xx-06-menu-aberto.png`,
    `prints/15xx-07..10`.

## Ressalva: a barra em 1366

Medida na janela de verdade (`anotacoes-1366.txt` e `anotacoes-1536.txt`). Cada caso foi medido com o botão e
sem ele.
- **1536 (a tela do Samuel):** nenhum botão é cortado. A conta "N de M conferidas · K com dúvida" aparece inteira
  com as miniaturas abertas e com elas fechadas, igual a antes.
- **1366, com o Propriedades aberto:** nenhum botão é cortado. A conta, que antes cabia no limite em duas linhas,
  passa a "0 de 140 co..." (inteira no balão).
- **1366, com o Propriedades aberto e as miniaturas fechadas:** a barra já não cabia antes. A conta sumia e
  "Duas lado a lado" e "Confirmar e processar" saíam apertados. Com o botão, "antes / depois" também aperta um
  pouco.
- O botão já é o mais estreito possível (20 pontos, sem o espaço antes dele). Para caber tudo em 1366, outra
  coisa da barra teria que mudar. Pela ordem da gerente, não mexi em mais nada da barra; a queixa "mal
  diagramado" foi para a lista de layout.

## Testes

- Teste novo: `tests/test_decisoes_painel_livro.py`, com 9 casos. Todos falham no código antigo e passam no novo.
- Testes antigos: 3 linhas de `tests/test_paineis_na_tela.py` (255, 378, 425). Só a palavra "PARA O LIVRO TODO"
  virou "JÁ FEITO NO LIVRO TODO", com autorização da gerente.
