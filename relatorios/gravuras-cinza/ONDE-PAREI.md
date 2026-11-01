# D-588 "Gravuras em tons de cinza": onde parei

Ramo `gravuras-cinza-2026-11-01` (saiu de `obra-2026-10-26`, commit `7fb6e19`), cópia
`.claude/worktrees/gravuras-cinza`. Construtor, 01/11/2026. Não juntei nada em nenhum outro ramo.

## O pedido (palavras dele)

- 29/10, na capa do *Na escola de Jesus* em Preto e branco: "onde está a opção que deixa só cinza e
  branco ,essa parece que está dando um negativo".
- 01/11, depois de tentar o cinza de hoje: "está muito confuso e não deu certo, coloque um agente para
  fazer isso".
- Pergunta da gerente → "ok": "Uma caixinha "Gravuras em tons de cinza" no Preto e branco. Ela fica no
  painel Filtro, na tela cheia dos filtros e no "Limpar a folha" do Automático. Marcada, toda gravura
  achada sai cinza, mesmo quando o programa acha que é um enfeite, como na capa do *Na escola de
  Jesus*. Ela segue o "Aplicar em" (só nesta, todas, daqui em diante), como as outras opções."

## Decisões que esta tarefa precisa cumprir (escrito antes de mexer)

- **D-588**: a caixinha, com esse nome, nos três lugares; marcada, toda gravura achada em tons de
  cinza, mesmo a que o programa toma por enfeite; segue o "Aplicar em".
- **D-147**: foto e pintura no Preto e branco em tons de cinza, nunca pontilhadas.
- **D-144**: moldura e iluminura com a cor de fábrica no Preto e branco; traço preto só com a caixinha
  do livro.
- **D-148**: "Só as letras": a figura guarda a cor.
- **D-168 / D-587**: caixinhas que ficam cinza com "Só as letras" e voltam como estavam.
- **D-585**: a capa do *Na escola de Jesus*: a pintura tomada por enfeite guardou a cor.
- **D-586**: "Respeitar as gravuras achadas" (desligada, o filtro vale na página inteira sem as áreas
  achadas).
- **D-192**: tela cheia dos filtros com as mesmas opções do painel.
- **D-594**: o "Limpar a folha" do Automático com todas as opções do painel Filtro, com os mesmos
  nomes (inclui os dois lados do "comparar").
- **D-020** (Ctrl+Z / Ctrl+Shift+Z), **D-066/D-473** (tela = PDF), **D-010** (promessa do botão).
- CLAUDE.md §4.6, §4.7, regra 7 ("só o que ele mandou").

## O que mudou

| Arquivo | O quê |
|---|---|
| `modelos.py` | Campo novo da página `gravuras_em_tons_de_cinza` (padrão **False**; projeto antigo abre desmarcado). |
| `core/filtros.py` | `_preto_e_branco_com_gravura` e `aplicar_filtro_com_selecao` ganham `gravuras_em_cinza`: ligado, **toda zona de gravura** vai pelo caminho da foto da D-147 (`_foto_em_tons_de_cinza`), sem as perguntas "é foto? é enfeite?" que erram na capa. Desligado: a conta de sempre, linha por linha. |
| `core/pipeline.py` | `gravuras_em_cinza_valem(pagina)`: a caixinha marcada **e** "Respeitar as gravuras achadas" ligada; passada ao filtro em `_filtro_da_pagina` (o "Só as letras" vai antes para o misto e não a vê). |
| `core/perfis.py`, `core/automatico.py` | O campo entra na receita (`CAMPOS`), nos campos da página do Automático (`CAMPOS_DA_PAGINA`) e em `campos_da_pagina_no_filtro` só no Preto e branco. |
| `ui/tela_conferir.py` | `caixa_gravuras_cinza`, `_mudar_gravuras_em_cinza` (ação do desfazer), `_mostrar_gravuras_em_cinza` (só no Preto e branco; cinza com "Só as letras" ou com "Respeitar" desligada); vai junto no "todas" e no "daqui em diante"; marca "mexida a mão" (FILTRO); o "Usar" da tela cheia grava por aqui. |
| `ui/widgets/paineis.py` | Peça "cinza" no painel: logo abaixo da "Respeitar as gravuras achadas". |
| `ui/widgets/filtros_tela_cheia.py` | A caixinha (mesmo nome e balão), logo abaixo do ajuste, só no Preto e branco, cinza nos mesmos casos; entra na página grande e no "Usar". |
| `ui/automatico.py` | `cx_gravuras_cinza` no "Limpar a folha", logo abaixo da "Respeitar"; só no Preto e branco; cinza com "Só as letras" ou "Respeitar" desligada; nome na caixa da receita. Os dois lados do "comparar" usam o mesmo painel. |
| `ui/tarefas.py` | A chave da prévia muda só com a caixinha marcada (desmarcada, a chave é a de sempre). |
| `tests/test_decisoes_gravuras_cinza.py` | 14 provas novas (abaixo). |
| `tests/test_decisoes_automatico_opcoes_do_filtro.py` | A caixinha nas provas da D-594 (nome, aparecer só no Preto e branco, "rodar = escolher no painel"). |
| `tests/promessas/promessas.md`, `tests/test_promessas.py` | Promessa **P-087** e a prova dela. |

## Como cumpri cada uma

- **D-588 (nome e lugares):** prints 2, 6 e 7; provas `test_d588_caixinha_no_painel...`,
  `..._na_tela_cheia_dos_filtros`, `..._no_limpar_a_folha_do_automatico`, e as da D-594.
- **D-588 (marcada → cinza, mesmo o "enfeite"):** capa de verdade (`capa-sem-a-caixinha.jpg` →
  `capa-com-a-caixinha.jpg`): sem a caixinha, 68,8% dos pontos coloridos; com ela, **0,0%** coloridos e
  86,7% de tons do meio (cinza, não 1 bit). Livro de teste: `test_d588_marcada_a_gravura_achada_sai_cinza...`.
- **"Desmarcada: tudo como hoje":** `identica-ao-7fb6e19.txt`: 32 desenhos do *Na escola de Jesus*
  (páginas 1, 9, 19, 45; quatro filtros; "Respeitar" ligada e desligada) com **o mesmo md5** no
  `7fb6e19` e neste ramo. E `test_d588_desmarcada_e_a_conta_de_antes_byte_a_byte`.
- **D-147 (cinza, nunca pontilhado):** é o mesmo `_foto_em_tons_de_cinza` da D-147 (desfoque que tira
  a retícula + níveis esticados).
- **D-144 / D-148 / D-586:** desmarcada, nada muda (md5 iguais); com "Só as letras" a conta nem a vê
  (prova `test_d588_cinza_com_so_as_letras...`: a iluminura guarda a cor).
- **"Aplicar em":** `test_d588_aplicar_em_leva_a_caixinha[todas / daqui em diante]`.
- **D-020:** `test_d588_ctrl_z_desfaz_e_ctrl_shift_z_refaz`.
- **D-066/D-473 (tela = PDF):** `test_d588_o_pdf_sai_como_a_tela`, `test_d588_antes_depois_segue_a_caixinha`, P-087.
- **§4.7 (reversão):** `reversao-no-7fb6e19.txt`: no código de antes, 13 de 14 provas falham; a prova
  pela imagem acusa **96% de pontos coloridos** na gravura (a medida pede 0%). A que passa nos dois é a
  "desmarcada = conta de antes" (tem de passar).

## Prints (janela de verdade, 1280 x 657, *Na escola de Jesus*, capa)

`1-capa-sem-a-caixinha.jpg`, `2-capa-com-a-caixinha.jpg`, `3-antes-depois-com-a-caixinha.jpg`,
`4-so-as-letras-caixinha-cinza.jpg`, `5-respeitar-desligada-caixinha-cinza.jpg`,
`6-tela-cheia-com-a-caixinha.jpg`, `7-automatico-limpar-a-folha.jpg`; e a capa desenhada
`capa-sem-a-caixinha.jpg` / `capa-com-a-caixinha.jpg`. Feitos por `fazer_prints.py` numa cópia do
projeto de teste em `_tmp/dados` (nada gravado na pasta de dados de teste). Saída: `prints-saida.txt`.

## Testes no PC (um arquivo por vez, offscreen) — `testes-locais.txt`

test_decisoes_gravuras_cinza 13 passaram (depois veio a 14ª, a da reversão pela imagem: 14 passaram) ·
test_decisoes_respeitar_gravuras 19 · test_decisoes_automatico_opcoes_do_filtro 21 (com o caso novo) ·
test_filtros_tela_cheia 11 · test_preto_e_branco_regra_30_09 15 · test_decoracao_no_preto_e_branco 12 ·
test_decisoes_filtro_automatico 4 · test_decisoes_automatico 24 · test_decisoes_automatico_ver_como_fica
22 · test_filtro_com_selecao 22. Nenhuma falha. test_promessas: ver abaixo.

## GitHub

(preenchido abaixo, ao fim das rodadas)

## Perguntas para o Samuel

1. **Com "Só as letras" ligada.** Hoje, no Preto e branco, se você liga "Só as letras", a caixinha
   "Gravuras em tons de cinza" fica cinza e não dá para clicar; as gravuras ficam com a cor (como o "Só
   as letras" manda). Desligando "Só as letras", ela volta como estava (print 4). É o mesmo jeito da
   caixinha das molduras e da "Respeitar as gravuras achadas". **Está bom assim? (sugestão: sim)**
2. **Com "Respeitar as gravuras achadas" desligada.** Desligada, o filtro vale na página inteira e não
   sobra gravura achada para pintar de cinza: a página sai toda em preto e branco. Então a caixinha
   "Gravuras em tons de cinza" fica cinza e não dá para clicar; religando "Respeitar", ela volta como
   estava (print 5). **Está bom assim? (sugestão: sim)**
3. **Onde ela aparece.** No painel Filtro, logo abaixo da "Respeitar as gravuras achadas" (fora do
   "Mais ajustes", que vem fechado); na tela cheia, logo abaixo da barra "Força do preto"; no
   Automático, logo abaixo da "Respeitar as gravuras achadas" (prints 2, 6 e 7). **Está bom nesses
   lugares? (sugestão: sim)**
4. **"Toda gravura" vale também para o desenho de traço e para a gravura marcada à mão.** Marcada, não
   só a pintura e o enfeite saem cinza: a gravura de traço (a xilogravura, que hoje sai como desenho
   preto e branco) e a área que você marcou à mão como gravura também saem em tons de cinza. O texto
   continua preto e branco. **Está bom assim? (sugestão: sim — foi o "toda gravura achada")**

## Ressalvas

- Os prints sem janela na tela precisam de `QT_QPA_FONTDIR=C:/Windows/Fonts` (sem isso os textos saem
  como quadradinhos); está escrito no `fazer_prints.py`.
- A cópia do código antigo para a reversão foi tirada com `git archive 7fb6e19` na pasta temporária do
  agente (com uma junção para `modelos`), não é outra cópia do projeto.
- Não mexi no layout do "Mais ajustes" (o outro construtor está nele); a caixinha fica fora dele.
