# Layout: etapa 4, entrega 3 da rodada 14 e etapa 5 - conferência do verificador (21/10/2026)

Ramo `layout-etapas4a7-2026-10-19`, conferido no código mais novo do ramo, `60a0a3d` (contém `d1f92a0`, `e1ef0d3` e `744292d`; as etapas 6 e 7a também estão nele, mas **não as conferi**). Não mudei código; não marco nada como aprovado.

## Veredito

**PRONTO PARA CONFERIR.** O que as três entregas dizem fazer está na janela de verdade e bate com as respostas das rodadas 12 a 14b. Os testes do ramo passam um por um, e o teste de reversão dos menus falha no código de antes. Achei só detalhes de aparência (ver abaixo).

## O que conferi

| O que | Como | Resultado |
|---|---|---|
| Fora de `ui/` nada muda | `git diff 31a9253 60a0a3d` | só `teste_botoes.py` (e testes) |
| Testes de tela do ramo, um arquivo por vez | máquina | 12 arquivos, todos passaram (menus 5, miniaturas 4, menu Painéis 3, painéis 34 + 22, dividir 9, endireitar 5, barra de menu 20, misto 25, ajustar pedaço 8, gravura na Marcar 8, pontinhos 19) |
| Reversão `tests/test_menus_que_nao_faziam_nada.py` | máquina, no `f25c2e9` (antes de `969a3a9`) | 5 falham e 1 dá erro: 10 itens de menu sem ação, "Livros recentes" vazio, sem `mudar_o_zoom`, sem `restaurar_pagina` |
| Janela de verdade (Antiphonal 44 a 49, 1600 x 821) | olho, clique nativo, 18 prints em `img/` | abaixo |

## Na janela, contra as decisões

- **Rodada 14 entrega 3.**
  - **903 B, menu "Painéis":** os cinco painéis, "Fechar o painel" e "Ícones da direita" (`L02-menu-Paineis`).
  - **904 A, menu Ver:** "Miniaturas", "Ícones da direita", "Todas as páginas" e "Filtros em tela cheia". Os quatro "Painel: …" saíram do Ver (`L02-menu-Ver`).
  - **909 B, "Só neste pedaço":** sem "o mesmo da página"; a lista mostra Original, Preto e branco, Melhorar e Mágico pro, nenhum aceso (`L07`).
  - **910 A, ângulo girado à mão:** a linha "ScanTailor -2,0° · Editor -2,0°" continua à vista. A frase "Você girou à mão: -2,1°. As contas voltam com 'usar o ângulo do programa'." fica só no balão do mouse (`L17`).
  - **805, conta "Editor":** aparece na linha do Endireitar e no "Para o livro todo" (`L03`).
  - **907 B, "o do Editor" no Dividir:** está no código (`ui/tela_conferir.py:1208`). **Não vi na janela:** este pedaço não divide folha.
- **Etapa 4.**
  - **Propriedades do Retângulo:** "Girar a folha", "Marcar como" (gravura ou foto, letra e traço, papel), "Marcação desta página" e "Foto" (`L05`).
  - **Painel "Filtro da página":** fila com a página nos 5 filtros e as teclas; partes Ajuste, Só as letras, Limpar a sujeira (lista com amostra), Mais ajustes e Só neste pedaço; "apagar página"; pé "Aplicar em: só nesta · todas · daqui em diante" (`L06`, `L08`).
  - **Propriedades do Endireitar com duas partes (706 B):** "Só nesta página" e "Para o livro todo" (`L03`).
- **Etapa 5.**
  - **Cabeçalho PÁGINAS:** alça, seta, três pontinhos com "Ver em pares", "Lugar" (embaixo, à esquerda, à direita junto da página) e "Fechar as miniaturas" (`L10`, `L12`).
  - **"ver todas" (808 A):** abre "Todas as páginas" em "uma a uma" (901 A), com "em pares", "todas" e "só as que precisam de atenção". Clicar na página 4 levou à página 4 (`L09`).
  - **Em pares:** a página 1 fica sozinha, depois 2-3 e 4-5, como no livro aberto (`L11`, `L14`).
  - **Miniaturas à esquerda ou fechadas (801 A):** o "Confirmar e processar" desce para a barra de baixo, no canto direito (`L14`, `L15`).
  - **Ver > Miniaturas:** traz as miniaturas de volta (`L16`).

## Detalhes vistos (não bloqueiam)

- Na fila do painel Filtro, o nome "Melhorar" sai cortado ("Melhora" / "Melhorai") nas duas larguras (`L06`, `L07`).
- Em "Todas as páginas" as páginas pequenas saem borradas (`L09`).
- Ao clicar num menu, o "Ver" ficou marcado como aberto no print do Endireitar (`L03`); é do print logo depois do Esc, não um defeito confirmado.
- O ramo diz que o GitHub passou (rodadas 39476824315, 39554220929 e 39557719615). Não abri as rodadas.
