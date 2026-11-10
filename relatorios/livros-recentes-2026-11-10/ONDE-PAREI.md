# ONDE-PAREI — o programa fecha ao abrir Arquivo > "Livros recentes"

Ramo `livros-recentes-2026-11-10` (saiu de `obra-2026-10-26`, ponta `d9f80eb4`). Cópia:
`.claude/worktrees/livros-recentes`. Pedido da gerente de 10/11/2026.

Origem: teste como o Kaique de 07/11/2026 (`teste-kaique-funcoes`, versão `6904a634`), erro N12 ("O programa fechou
sozinho", Palatino). Resposta do Samuel na Central (`k0711-fechou`): "Consertar"; está entre os graves.

## Decisões que esta tarefa precisa cumprir

- **D-376** (18/07/2026): "nenhuma exceção pode fechar a janela — deve virar aviso em português e registrar no log."
  O programa fechou: este conserto é para cumprir essa decisão no menu "Livros recentes".
- **P-140** (promessa do menu, `tests/promessas/promessas.md`): Arquivo > "Livros recentes" "lista os livros abertos
  antes; clicar num abre aquele livro". A docstring de `_montar_livros_recentes` diz o mesmo: os livros da tela
  inicial (os mesmos cartões), do mexido por último ao mais antigo; clicar abre como o cartão "continuar".
- **P-003 / D-338 / D-351** (a Lista de atalhos, F1): "abre 'Lista de atalhos' com os atalhos tirados dos próprios
  menus (ex.: 'Desfazer — Ctrl+Z')". O texto da lista não pode mudar com o conserto.
- **CLAUDE.md §11.7** (só o que ele mandou): nenhum botão, aviso ou texto novo. **§11.8 / D-605** (o novo não
  estraga o testado). **§4.7** (teste de reversão). **§3** (nenhuma exceção fecha a janela).

## O que já está escolhido e testado aqui (escrito ANTES de mexer)

Decisões: D-376, P-140, P-003 (com D-338 e D-351) — acima. D-652 (07/11, "a fazer"): a lista do F1 vai ser refeita
por outro trabalho (mostrar tudo de cara, diagramação boa); esta tarefa NÃO mexe nisso.

Testes que já existem sobre o menu "Livros recentes", a abertura do livro por ele e a Lista de atalhos:
- `tests/test_menus_que_nao_faziam_nada.py::test_livros_recentes_mostra_os_livros` (o menu lista os livros, "(nenhum
  livro ainda)" quando não há, e clicar passa pela mesma conferência do cartão, `pedir_para_continuar`).
- `tests/test_menus_que_nao_faziam_nada.py::test_nenhum_item_de_menu_fica_sem_fazer_nada`.
- `tests/test_promessas.py::test_p140_livros_recentes` (abre dois livros; o primeiro aparece; clicar abre ele).
- `tests/test_promessas.py::test_p027_atalhos_em_portugues` (a lista de atalhos em português).
- `tests/test_barra_de_menu.py::test_a_lista_de_atalhos_sai_dos_proprios_menus` e
  `::test_todo_atalho_do_menu_aparece_na_ajuda` (a lista de atalhos sai dos próprios menus).
- `tests/test_tela_inicio.py` e `tests/test_trabalho_nao_se_perde.py` (o cartão "continuar", `pedir_para_continuar`).
- `teste_botoes.py` (clica em todos os itens de menu acesos, inclusive Ajuda > "Lista de atalhos").
Nenhum desses testes é mudado por esta tarefa.

## A causa (achada e reproduzida, 10/11/2026)

Em uma frase: **abrir a Lista de atalhos (F1) fazia o Python "esquecer" o menu "Livros recentes"; o Qt ainda o
mostrava, mas, na hora de montar a lista de livros, o programa achava que o menu já não existia, dava erro, e a caixa
de erro aberta no meio do menu derrubava o programa.**

Em detalhe:
1. `ui/barra_de_menu.py`, `texto_dos_atalhos()` (o texto do F1), passa por todos os itens de cada menu e pergunta
   `a.menu()` para pular os submenus. No PySide6 6.11.1, `QAction.menu()` faz o submenu virar "filho", do lado do
   Python, do item temporário `a`. Quando esse item temporário some (na volta seguinte do laço), o Python marca o
   submenu ("Livros recentes") como apagado, embora o Qt continue com ele na tela. Reproduzido fora do programa, com
   quatro linhas de PySide puro (`QMenuBar` > `addMenu("Arquivo")` > `addMenu("Livros recentes")`,
   `arq.actions()[0].menu()`, soltar o item → `shiboken6.isValid(sub)` vira `False`).
2. Na próxima vez que a pessoa passa em Arquivo > "Livros recentes", o Qt avisa "vai abrir" (`aboutToShow`) e
   `_montar_livros_recentes` chama `menu.clear()` no menu que o Python acha apagado: `RuntimeError: Internal C++
   object (PySide6.QtWidgets.QMenu) already deleted` — exatamente a linha do `erros.log` do teste (linha 494).
3. O erro vai para o `sys.excepthook`, que abre a caixa "Aconteceu um problema inesperado" ainda dentro da abertura do
   submenu (`QMenu::internalDelayedPopup`). Quando a pessoa aperta "entendi", o Qt volta para a abertura do menu, que
   já foi fechado pela caixa, e quebra: o Windows anotou a queda em `Qt6Widgets.dll`, deslocamento `0x1d1551`, que cai
   dentro de `QMenu::internalDelayedPopup` (procurado na tabela de exportação da DLL). A queda foi às 10:53:46; o erro
   no log, às 10:53:14: os 32 s são o tempo da caixa aberta.
4. Bate com o teste do Kaique: na rodada de 07/11 o F1 foi apertado no fim do Lusíadas (prints 122-123, notas l.55),
   ANTES do Siebmacher e do Palatino; o "Livros recentes" do Lusíadas (print 104) foi antes do F1 e funcionou; o do
   Palatino (166-167) foi depois e quebrou. Depois de reabrir o programa (sem F1) o menu funcionou de novo
   (prints 174-181), e "repetir os mesmos passos" (sem F1) não repetiu o erro.
5. O caminho "processar → montar para imprimir → gravar → fechar" não tem relação: refeito sem janela, o menu continua
   bom em todos os passos.

## Como fica para quem usa e no livro (escrito ANTES de mexer)

Exemplo: o Kaique está com o Palatino pronto, na tela "Ficou pronto!".

**Antes (hoje):**
1. Em algum momento ele aperta F1 (ou Ajuda > "Lista de atalhos") e fecha a lista.
2. Depois vai em Arquivo > "Livros recentes": aparece "Aconteceu um problema inesperado, mas o programa continua
   funcionando."; ele aperta "entendi" e o programa fecha sozinho. O trabalho já gravado não se perde (os livros
   voltam ao reabrir), mas ele perde o que estava fazendo e leva um susto.

**Depois:**
1. F1 mostra a mesma lista de sempre, com o mesmo texto.
2. Arquivo > "Livros recentes" mostra os livros da tela inicial, do mexido por último ao mais antigo (ou "(nenhum
   livro ainda)"), quantas vezes ele abrir, com ou sem F1 antes; clicar num abre o livro como o cartão "continuar".
3. Nada muda no livro nem no PDF; nenhum botão, aviso ou texto novo.

## Andamento

- [x] Causa achada e reproduzida (acima).
- [x] Teste de reversão `tests/test_livros_recentes_depois_do_f1.py` (2 testes): no código antigo os dois FALHAM
  ("depois do F1 o menu 'Livros recentes' ficou apagado para o Python..."); no novo, 2 passam.
- [x] Conserto (commit `4de59c37`): `ui/barra_de_menu.py`, `texto_dos_atalhos()` troca `a.menu()` por
  `QMenu.menuInAction(a)` (diz a mesma coisa, "este item é um submenu?", sem o efeito colateral do PySide), com o
  comentário de por que e do que é arriscado. Uma linha de código e o import.
- [x] Conferido sem janela, com o menu de verdade: F1, abrir Arquivo, passar em "Livros recentes". Código antigo:
  `RuntimeError: ... QMenu ... already deleted` (o mesmo do `erros.log` do Kaique). Código novo: o menu monta a
  lista, nenhum erro.
- [x] Texto do F1 antes e depois: igual, byte a byte (72 linhas).
- [x] Testes no PC, um arquivo por vez, prioridade baixa, sem janela (10/11, 17:54-18:56): os 55
  `tests/test_decisoes*.py`, `test_livros_recentes_depois_do_f1.py`, `test_barra_de_menu.py`,
  `test_menus_que_nao_faziam_nada.py`, `test_atalhos.py`, `test_tela_inicio.py`, `test_trabalho_nao_se_perde.py`
  e `test_promessas.py` (268 passed, 1 xfailed): todos OK. `teste_botoes.py`: OK.
- [x] GitHub, rodada `42909616068`: as 5 partes da suíte e "Botões e prints da janela real" passaram. O filtro de
  velocidade não rodou (nada em `core/` mudou).

## Como cumpri cada uma

- **D-376** (nenhuma exceção fecha a janela): a exceção que derrubava o programa não acontece mais nesse caminho
  (teste de reversão + conferência com o menu de verdade, acima).
- **P-140** (o menu lista os livros e clicar abre): o teste novo abre o menu duas vezes depois do F1 e confere a lista
  e que o clique passa por `pedir_para_continuar` (o mesmo do cartão "continuar"); `test_p140_livros_recentes` e
  `test_livros_recentes_mostra_os_livros` continuam passando, sem mudança.
- **P-003 / D-338 / D-351** (F1): o texto da lista é o mesmo, byte a byte; `test_barra_de_menu.py` e
  `test_p027_atalhos_em_portugues` passam sem mudança.
- **§11.7**: nenhum botão, aviso ou texto novo. **§11.8 / D-605**: nenhum teste antigo foi mudado; todos passam.
- **§4.7**: teste de reversão mostrado falhando no código antigo.

## Roteiro para o Samuel testar no PC dele (2 minutos)

1. Abrir o programa deste ramo pelo atalho "(desenvolvimento)" e abrir qualquer livro (a linha dos menus só aparece
   com um livro aberto).
2. Apertar **F1** (aparece a "Lista de atalhos") e apertar "fechar".
3. Ir em **Arquivo > Livros recentes**: tem de aparecer a lista dos livros (os mesmos da tela inicial). Fazer duas
   ou três vezes.
4. Clicar num livro da lista: ele abre, como o cartão "continuar".
Antes do conserto, no passo 3 aparecia "Aconteceu um problema inesperado" e, ao apertar "entendi", o programa fechava.

## Perguntas para o Samuel

Nenhuma.

## Achados para a gerente (não consertados, como mandado)

1. **Qualquer erro dentro de um menu que está abrindo derruba o programa, mesmo com o aviso "o programa continua
   funcionando".** O `sys.excepthook` abre a caixa de erro no meio da abertura do menu; ao fechar a caixa, o Qt quebra
   (foi o que transformou o erro deste caso em queda). Vale para todo `aboutToShow` (hoje: "Livros recentes" e o que
   mais for montado na hora de abrir). Isso fere a D-376 por outro caminho. Mexer no excepthook (por exemplo, mostrar
   a caixa logo depois, e não no meio) muda o jeito do aviso: é decisão para a gerente/Samuel.
2. **A mesma armadilha do `a.menu()` existe em código de teste** (não mexi: teste antigo): `tests/promessas/ajudantes.py`
   l.419-420 (`acoes_de_menu_aberto`) e `tests/test_decisoes_desfazer_pagina.py` l.324 e l.438. Num teste que abre um
   menu com submenu e depois usa o submenu guardado, isso pode dar "already deleted" que não existe no programa.
   Também em scripts de piloto antigos em `relatorios/` (`desfazer-pagina/piloto*.py`, `obra-etapa2/3/roteiro/base.py`).
3. **D-652 (refazer a lista do F1, "a fazer")**: quem refizer a lista não pode voltar a usar `a.menu()` ao passar
   pelos menus; o comentário em `texto_dos_atalhos` avisa, e o teste novo pega se voltar.
4. O caminho que o relatório do Kaique descreve (processar → montar para imprimir → gravar → fechar) não tem relação
   com a queda: refeito sem janela, o menu fica bom em todos os passos. O que a provocou foi o F1 apertado antes, no
   Lusíadas. Vale corrigir a anotação do N12 no relatório/plano, se a gerente quiser.
5. Os outros submenus guardados pela barra (`menus_do_giro`, "Aplicar o giro em"; `menu_do_lado_direito`, "Lado
   direito") também ficavam "apagados para o Python" depois do F1; hoje o programa não usa esses dois depois de
   montar, então não dava erro visível. O mesmo conserto cobre os dois (o teste novo confere).
