# ONDE-PAREI — tira em pares (D-611 refeita), ramo `tira-pares-2026-11-04`

Saiu de `obra-2026-10-26` em `5cf4aaed`. Pedido da gerente (04/11): o Samuel testou a D-611 e disse
"4- não está ok coloquei no primeiro print" (print a-57: Dividir, Gradus, "Duas lado a lado", a tira
"FOLHAS" com as miniaturas uma a uma, separadas).

## Decisões que esta tarefa precisa cumprir

- **D-611 (04/11):** "funciou, mas quando estiver duas lado a lado escolhido os icones embaixo tem que estar em duas
  folhas;." · "Quer dizer que, com 'Duas lado a lado' escolhido, as miniaturas embaixo também aparecem de duas em duas,
  juntas como no livro aberto?" → "Sim". Livro: "a tira de miniaturas embaixo mostra as páginas de duas em duas, juntas
  como no livro aberto (a 1 sozinha, à direita), como a vista grande. Em "Uma página", a tira fica como está."
- **D-605 (03/11):** "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e
  testado, coisas novas não podem criar novos problemas".
- **D-006 / D-015:** "Uma página / Duas lado a lado" na barra de baixo e no menu Ver; pares rolando.
- **D-601 (02/11):** no Dividir, "Uma página" mostra a metade; "Duas lado a lado", a folha inteira com a linha. Na tira
  do Dividir, folha dividida = duas miniaturas, não dividida = uma dupla; numeração por página.
- **D-609 (04/11):** arrastar a linha na folha inteira. **D-610 (04/11):** dividir em "Duas lado a lado" passa para
  "Uma página". (Testadas pelo Samuel: "2- ok", "3- ok".)

## O que já está escolhido e testado aqui (antes de mexer)

- **D-032 / ly-pares (21/10, "Está bom"):** o "Ver em pares" do menu dos três pontinhos, com o jeito aprovado (a 1
  sozinha; 2-3; 4-5; vão de 6 pontos dentro do par e um vão maior entre pares) → `tests/test_miniaturas_novas.py`
  (`test_em_pares_como_no_livro_aberto`). **Não muda.**
- **D-060:** o jeito das miniaturas (lugar, aberta, em pares) fica para o próximo livro → `test_miniaturas_novas.py`
  (`test_as_miniaturas_ficam_para_o_proximo_livro`); a D-611 não grava nada → `test_decisoes_tira_em_pares.py`.
- **D-039:** menu dos três pontinhos → `test_miniaturas_novas.py`.
- **D-611 (como entregue):** lugar das miniaturas na grade, escolhida e clique → `tests/test_decisoes_tira_em_pares.py`
  (4). Não mudo esses testes.
- **D-601:** tira do Dividir por páginas/folhas → `tests/test_decisoes_dividir_metade.py`.
- **03/11:** a tira rola até a escolhida depois do Ctrl+Z → `tests/test_dividir_ajustes_03_11.py`.
- **D-609 / D-610 / D-602 / D-498 / D-090:** `test_decisoes_dividir_arrastar.py`, `test_decisoes_dividir_linha.py`,
  `test_decisoes_dividir.py`, `test_dividir_na_tela.py`, `test_decisoes_9b2.py`.
- **D-006 / D-015 / D-343:** `tests/test_decisoes_ver.py`.
- **D-547 (miniatura como sai), giros D2:** `test_decisoes_9b2.py`, `test_girar_cartoes_e_previas.py`.
- Outros que usam a tira: `test_decisoes_9b1.py`, `test_decisoes_avisos.py`, `test_menu_paineis.py`,
  `test_promessas.py`, `test_gerar_o_mesmo_livro_de_novo.py`, `test_mesmo_livro_outro_caminho.py`.

## O que achei (reproduzido na janela de verdade, projeto do Gradus dele, piloto.py)

- A tira **está** em pares no código (a grade põe 1 | 2-3 | 4-5), mas na tela não parece: no projeto dele as folhas
  estão divididas, as miniaturas são páginas em pé, estreitas, no meio de quadros de largura fixa (50 pontos). O vão
  entre os desenhos dentro do par fica **22 pontos**, igual ao vão de "Uma página" (22), e entre pares 32. A diferença
  é 10 pontos: a olho, uma a uma. (anotacoes-abrir-antes.txt, prints `antes-abrir-*`.)
- Não depende de a vista já vir gravada, nem do Automático, nem do tamanho da janela: acontece toda vez que as
  miniaturas são páginas estreitas (folhas divididas). Com folhas inteiras (largas) o vão no par é 14 e entre pares 24.
- Os 4 testes da D-611 só conferiam a coluna de cada quadro na grade, nunca onde os desenhos ficam na tela; e os prints
  do agente anterior foram num livro aberto do zero (folhas inteiras, largas), onde o par aparece um pouco melhor.
- Achado a mais, para perguntar: no Dividir, a vista grande mostra a FOLHA (folha 2 = páginas 3 e 4), mas a tira junta
  pelo livro aberto (2-3, 4-5): a página 3 aparece no par com a capa (2), não com a 4.

## Plano

1. Teste de reversão que mede os desenhos na tela (falha agora). 2. Só com a D-611 ligada (pares pela vista), as duas
miniaturas do par ficam encostadas (como as duas páginas do livro aberto); o "Ver em pares" do menu e "Uma página" ficam
como estão. 3. Prints antes/depois e o que já funcionava ao redor. 4. GitHub.

## Situação

- 04/11: reproduzido; ONDE-PAREI escrito antes do código (`702b3a9e`).
- Conserto `34b07c13` (tira_miniaturas.py + prova nova; reversão falha em `5cf4aaed`: vãos 31/21). Prints depois
  `306f997b`. Testes do PC, um por vez: 19 arquivos, todos passaram (lista no relatório). Prints da pergunta
  (opção A como está, opção B só no piloto). Relatório: `relatorio.md` (.html, .pdf). Falta: rodada do GitHub.

## Perguntas para o Samuel

1. (Dividir, Duas lado a lado) A tira junta como o livro aberto (1 sozinha; 2-3; 4-5) ou como a vista grande do
   Dividir, folha por folha (1-2, 3-4)? Hoje a página 3 fica no par com a capa. Ver o relatório (prints).
