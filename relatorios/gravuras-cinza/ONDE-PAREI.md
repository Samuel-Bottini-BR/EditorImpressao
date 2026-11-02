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
22 · test_filtro_com_selecao 22. Nenhuma falha. test_promessas (o arquivo inteiro, com a P-087): 263 passaram, 1 xfail (o de antes).

## GitHub (commit `c44fe5c`, ramo enviado com `git push -u origin gravuras-cinza-2026-11-01`)

- **Testes no Windows**, rodada `41323846070`: **passou** (as 5 partes da suíte, "Botões e prints da
  janela real" e o resumo).
- **Filtro de velocidade** `7fb6e19` -> `gravuras-cinza-2026-11-01`, rodada `41323848831`: **passou,
  veredito "igual (dentro do vai-e-vem)"**: abrir o livro +0,5%; trocar de página +0,2%; Mágico pro 10
  páginas +0,4%; Preto e branco 10 páginas -0,9%.

## Perguntas para o Samuel

1. **Com "Só as letras" ligada.** Hoje, no Preto e branco, se você liga "Só as letras", a caixinha
   "Gravuras em tons de cinza" fica cinza e não dá para clicar; as gravuras ficam com a cor (como o "Só
   as letras" manda). Desligando "Só as letras", ela volta como estava (print 4). É o mesmo jeito da
   caixinha das molduras e da "Respeitar as gravuras achadas". **Está bom assim? (sugestão: sim)**
2. **RESPONDIDA em 02/11: "não"** (ver a seção "02/11 — conserto" abaixo). Texto de 01/11:
   **Com "Respeitar as gravuras achadas" desligada.** Desligada, o filtro vale na página inteira e não
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

---

# 02/11 — conserto: o cinza sem o Respeitar

Ramo `gravuras-cinza-2026-11-01`, cópia `.claude/worktrees/gravuras-cinza`. Antes de mexer, juntei o
`obra-2026-10-26` (a versão que o Samuel testa) no meu ramo: entrou direto, sem conflito (o ramo ficou no
`091b200`). Não juntei nada em nenhum outro ramo.

## Decisões que esta tarefa precisa cumprir (escrito antes de mexer)

- **O pedido de 02/11** (página 13 de 199 do *Na escola de Jesus*, Preto e branco): "1- não consigo trocar
  respeitar gravuras por gravuras em tons de cinza." · "2- para deixar as gravuras cinzas o respeitar gravuras tem
  que estar ligado, por gravuras em tons de cinza sozinho já deveria resolver o problema." É o "não" dele à minha
  pergunta 2 de 01/11. Proposta aprovada ("sim pode"): **"marcar só "Gravuras em tons de cinza" já basta: ela acha
  as gravuras sozinha e pinta de cinza, com o "Respeitar" ligado ou desligado."**
- **D-588**: a caixinha nos três lugares (painel Filtro, tela cheia dos filtros, "Limpar a folha" do Automático,
  com os dois lados do "comparar"); marcada, toda gravura achada sai em tons de cinza, mesmo a que o programa toma
  por enfeite (D-585); segue o "Aplicar em".
- **D-147**: no Preto e branco, foto e pintura em tons de cinza, nunca pontilhadas.
- **D-585**: pintura e foto só guardam a cor com "Só as letras" (D-148).
- **D-586**: com a caixinha do cinza **desmarcada**, o "Respeitar" desligado continua como era (a página toda em
  preto e branco, só as áreas feitas à mão valem).
- **D-066/D-473**: tela = PDF (vale na receita e no PDF de verdade, não só na prévia).
- **Ficam como estão (perguntas abertas):** "Só as letras" ligada (pergunta 1), os lugares da caixinha (pergunta
  3), a gravura de traço e a área marcada à mão (pergunta 4).
- CLAUDE.md §4.6, §4.7, §10 item 5, §11 item 7 ("só o que ele mandou").

## O que mudou

| Arquivo | O quê |
|---|---|
| `core/pipeline.py` | `marcacao_que_o_filtro_usa`: no Preto e branco com "Gravuras em tons de cinza" marcada, devolve a marcação inteira (o mesmo objeto), com o "Respeitar" ligado ou desligado. `gravuras_em_cinza_valem`: não pede mais o "Respeitar" ligado. Função nova `gravuras_em_tons_de_cinza_marcada` (só lê o campo). Docstrings com as palavras dele e o que é arriscado mudar. |
| `ui/tela_conferir.py` | `_mostrar_gravuras_em_cinza`: a caixinha só fica cinza com "Só as letras" (o "Respeitar" desligado não a apaga mais). |
| `ui/widgets/filtros_tela_cheia.py` | A mesma regra na tela cheia. |
| `ui/automatico.py` | A mesma regra no "Limpar a folha" (vale para a janela grande e os dois lados do "comparar": é o mesmo painel). |
| `tests/test_decisoes_gravuras_cinza.py` | 5 provas novas (abaixo); a prova 8 (Automático) e a 9 (que deixava a caixinha cinza com o "Respeitar" desligado, o jeito que ele recusou) acertadas ao pedido de hoje. |
| `tests/dados/na_escola_de_jesus_p1_p13.json` | Cópia só das páginas 1 e 13 do projeto de teste dele (com a marcação do "Gravuras e fotos"), para a prova no livro de verdade. O PDF só existe no PC dele: no GitHub a prova pula. |
| `tests/promessas/promessas.md` | P-087: "vale com a Respeitar ligada ou desligada". |

Com a caixinha marcada, o resultado é **o mesmo, ponto por ponto**, com o "Respeitar" ligado ou desligado. Por
isso as molduras e iluminuras saem exatamente como no caso das duas ligadas (o print a-26, que ele disse que
estava certo): não sobrou nada sem resposta, e não abri pergunta nova.

## Como cumpri cada uma

- **"marcar só Gravuras em tons de cinza já basta ... com o Respeitar ligado ou desligado":**
  - no livro dele, páginas 1, 9, 13, 19 e 45 (`identica-conserto-ao-091b200.txt`): com a caixinha marcada e o
    "Respeitar" desligado, **antes 0,0% de tons de cinza** (preto e branco chapado, o a-27); **depois o mesmo md5
    da página com as duas ligadas** (página 13: 31,9% de tons de cinza; capa: 86,7%);
  - prova `test_d588_conserto_0211_na_escola_de_jesus[capa / página 13]` (igual byte a byte às duas ligadas);
  - prova `test_d588_conserto_0211_painel_so_o_cinza_sem_o_respeitar_sai_igual_as_duas_ligadas` (cliques de
    verdade; a tela mostra; **o PDF de verdade** sai cinza).
- **"não consigo trocar" / a caixinha apagada:** clicável com o "Respeitar" desligado no painel, na tela cheia, no
  Automático e nos dois lados do "comparar" (provas `..._painel_...`, `..._tela_cheia_com_o_respeitar_desligado`,
  `..._automatico_com_o_respeitar_desligado`, e a prova 8). Prints `conserto-1/2/3-...-antes/depois.jpg`.
- **Receita e processamento:** rodar o Automático com "Respeitar" desligada e o cinza marcado grava os dois campos
  nas páginas e a gravura sai cinza, igual às duas ligadas (`..._automatico_com_o_respeitar_desligado`).
- **Desmarcada, nada muda (D-586):** as 40 combinações desmarcadas (5 páginas, 4 filtros, "Respeitar" ligada e
  desligada) têm **o mesmo md5** no `091b200` e depois do conserto (`identica-conserto-ao-091b200.txt`); e as
  provas comparam com a regra de antes byte a byte.
- **D-147:** é o mesmo cinza das duas ligadas (o caminho da foto da D-147).
- **"Só as letras" (pergunta 1):** não mexi; prova `test_d588_cinza_com_so_as_letras_e_volta`.
- **§4.7 (reversão):** `reversao-conserto-no-091b200.txt`: as provas novas rodadas no código de antes do conserto
  → **6 falham** (caixinha apagada no painel, na tela cheia e no Automático; capa e página 13 em preto e branco
  chapado, 0,0% de tons de cinza). Depois do conserto: 19 passaram.

## Prints (janela de verdade sem tela, 1280 x 657, *Na escola de Jesus*, página 13)

Feitos por `fazer_prints_conserto.py` numa cópia do projeto de teste em `_tmp/dados-conserto` (nada gravado na
pasta dele), com o código de antes (`091b200`) e o de depois. Na cópia, a página 13 está sem "Só as letras"
(veja a observação abaixo).

- `conserto-1-painel-pagina-13-antes.jpg` / `-depois.jpg`: painel Filtro, marquei o cinza e desliguei o
  "Respeitar". Antes: caixinha marcada mas apagada e a baleia em preto e branco chapado. Depois: caixinha clicável e
  a baleia em tons de cinza.
- `conserto-2-tela-cheia-pagina-13-antes.jpg` / `-depois.jpg`: a tela cheia dos filtros, com o "Respeitar"
  desligado na página.
- `conserto-3-automatico-pagina-13-antes.jpg` / `-depois.jpg`: o "Limpar a folha" do Automático, como no a-27.
- `pagina-13-antes.jpg` / `pagina-13-depois.jpg`: o desenho da página 13 (o da tela e do PDF) nesse estado.

## Observação para a gerente (não mexi): o print a-25

No a-25 (painel Filtro da página 13, as duas caixinhas apagadas), o motivo é o **"Só as letras"**: no projeto de
teste dele o livro está com "Só as letras" ligado e a página 13 herda (o resumo da parte "Só as letras" no painel
mostra "Guardar a tinta forte", que só aparece com ela ligada). Esse caso é a **pergunta 1**, que ficou como está.
Então, na página 13 do projeto dele, a queixa "1- não consigo trocar..." **continua no painel** enquanto o "Só as
letras" estiver ligado lá; com ele desligado (como no Automático do a-27), está consertado. A pergunta 1 abaixo
ganhou esse caso.

Também vi que, com as duas ligadas (e agora só com o cinza), a gravura da página 13 tem dois recortes brancos no pé
(onde a marcação da máquina pôs "papel" e "letra" dentro da gravura). É o mesmo desenho do a-26, que ele disse estar
certo, e não é deste conserto.

## Testes no PC (um arquivo por vez, offscreen) — `testes-locais-conserto.txt`

Nenhuma falha: test_decisoes_gravuras_cinza 19 · test_decisoes_respeitar_gravuras 19 ·
test_preto_e_branco_regra_30_09 15 · test_decisoes_automatico_opcoes_do_filtro 21 · test_filtros_tela_cheia 11 ·
test_decoracao_no_preto_e_branco 12 · test_decisoes_filtro_automatico 4 · test_decisoes_automatico 24 ·
test_decisoes_automatico_ver_como_fica 22 · test_filtro_com_selecao 22 · test_promessas 263 (1 xfail, o de antes).

## GitHub (commit `00d1ddf`)

- **Testes no Windows**, rodada `41455630372`: 1ª tentativa **falhou só na parte 1**, com 2 erros no fim (na
  limpeza) de `test_promessas` (`test_p083_jeitos_do_so_as_letras[rede]` e
  `test_p083_jeitos_no_automatico[Guardar tudo-tudo]`: "um botão falhou por baixo", a prévia tentou abrir o PDF da
  pasta temporária já apagada). As 263 provas passaram; as partes 2 a 5 e "Botões e prints" passaram. No PC o
  `test_promessas` inteiro passou (263). Disparei de novo a parte que falhou (uma vez, como manda a regra):
  resultado a conferir.
- **Filtro de velocidade** `091b200` -> `gravuras-cinza-2026-11-01`, rodada `41455635198`: (resultado abaixo)

## Perguntas para o Samuel (abertas)

1. A pergunta 1 de 01/11 continua aberta. Caso real: no *Na escola de Jesus* o "Só as letras" está ligado no livro;
   por isso, na página 13 (print `relatorios/testes-guiados/2026-10-29-automatico/a-25-painel-filtro-cinza-nao-troca.png`),
   as duas caixinhas ficam apagadas e não dá para marcar o cinza. Desligando o "Só as letras" da página, a caixinha
   volta a funcionar (com o "Respeitar" ligado ou desligado). **Está bom assim? (sugestão: sim)**
2. (respondida: "não", 02/11 — consertado acima)
3. e 4.: continuam como em 01/11.

---

# 02/11 — o balão da caixinha (aviso de quando usar)

Antes de mexer juntei o `origin/obra-2026-10-26` (`640170d`) no meu ramo: entrou direto, sem conflito (ele já
tinha o conserto do cinza, juntado pela gerente em `be4b9c9`, testado pelo Samuel: print a-40).

## Decisões que esta tarefa precisa cumprir (escrito antes de mexer)

- **O pedido de 02/11:** "é bom botar um aviso quando passa em cima da opção gravuras em cor de cinza, avisando que
  é quando o programa confundir". Texto aprovado por ele ("pode ser esse texto."), **exato**: "Para quando o programa
  se confundir: marcada, toda gravura que ele achou sai em tons de cinza, mesmo a que ele tomou por enfeite."
- Vale como **balão** (o que aparece ao passar o mouse) da caixinha "Gravuras em tons de cinza" nos três lugares:
  painel Filtro, tela cheia dos filtros, "Limpar a folha" do Automático (e os dois lados do "comparar"). Onde já
  havia balão, troca por este.
- **D-588** (a caixinha, o nome e os lugares) e CLAUDE.md §11 item 7: nada além do balão.

## O que mudou

| Arquivo | O quê |
|---|---|
| `ui/automatico.py` | Constante `BALAO_GRAVURAS_CINZA` com o texto aprovado (um lugar só); o balão do "Limpar a folha" (e, por ser o mesmo painel, dos dois lados do "comparar") passa a ser ele. |
| `ui/tela_conferir.py` | O balão da caixinha do painel Filtro passa a ser a mesma constante (antes: "Marcada, toda gravura achada sai em tons de cinza no Preto e branco, mesmo a que o programa acha que é um enfeite; o texto continua preto e branco."). |
| `ui/widgets/filtros_tela_cheia.py` | A tela cheia lê a mesma constante (antes copiava o balão do painel). |
| `tests/test_decisoes_gravuras_cinza.py` | Prova `test_d588_balao_aprovado_nos_tres_lugares`: o texto, letra por letra, nos três lugares e nos dois lados do "comparar". |
| `tests/promessas/promessas.md` | A "dica" da P-087 com o texto novo. |

Nada mais mudou (nome, lugar, comportamento e o balão da "Respeitar" ficam como estavam).

## Como cumpri cada uma

- **O texto exato nos três lugares (e no "comparar"):** prova `test_d588_balao_aprovado_nos_tres_lugares`
  (compara letra por letra com o texto aprovado, escrito na prova, não lido do programa).
- **§4.7 (reversão):** `reversao-balao-no-640170d.txt`: no `640170d` a prova falha (o balão era o antigo).
- Testes no PC e GitHub: abaixo.

## Testes do balão

- PC (um arquivo por vez), nenhuma falha: test_decisoes_gravuras_cinza 20 · test_decisoes_automatico_opcoes_do_filtro
  21 · test_filtros_tela_cheia 11 · test_decisoes_respeitar_gravuras 19 · test_decisoes_automatico 24 ·
  test_promessas 263 (1 xfail, o de antes).
- GitHub (commit `6798a38`), Testes no Windows, rodada `41473778845`: 1ª tentativa falhou só na parte 1, com os
  mesmos 2 erros de limpeza do `test_promessas` da rodada do conserto (`test_p083_jeitos_do_so_as_letras[rede]` e
  `test_p083_jeitos_no_automatico[Guardar tudo-tudo]`: a prévia tenta abrir o PDF da pasta temporária já apagada;
  as 263 provas passam). Disparei de novo a parte 1.

Rodadas do conserto do cinza (commit `00d1ddf`), já fechadas: Testes no Windows `41455630372` **passou** (na 2ª
tentativa da parte 1, mesmos 2 erros de limpeza na 1ª); Filtro de velocidade `41455635198` `091b200` ->
ramo **passou, "igual (dentro do vai-e-vem)"** (abrir -1,5%, trocar de página +0,9%, Mágico pro -1,4%, Preto e
branco +1,0%).

# PAUSA (02/11, pedido do Samuel)

"vamos pausar todos os trabalhos, para continuar depois". Parei os acompanhamentos em segundo plano.

- **Pronto e enviado** (ramo `gravuras-cinza-2026-11-01`): o conserto do cinza sem o "Respeitar" (`00d1ddf`,
  já juntado pela gerente) e o balão aprovado da caixinha nos três lugares (`6798a38`), com prova, reversão e
  testes do PC passando.
- **Falta:** a rodada `41473778845` do balão está **vermelha** depois de 2 tentativas, cada vez numa prova
  diferente, nenhuma do balão. 1ª: os 2 erros de limpeza do p083 (acima). 2ª: o `test_promessas` passou inteiro, e
  falhou `test_decisoes_so_as_letras.py::test_d148_desfazer_o_automatico_devolve_o_so_as_letras_do_livro` por tempo
  ("não aconteceu a tempo: o projeto.json com o 'Só as letras' desfeito"). Ao voltar: rodar essa prova no PC e
  disparar a rodada de novo; se os p083 voltarem, anotar como teste instável em `memoria/bugs.md`. O balão não foi
  juntado na versão de teste.
- **Perguntas abertas:** a 1 (com "Só as letras", caso do a-25), a 3 e a 4, como acima.
