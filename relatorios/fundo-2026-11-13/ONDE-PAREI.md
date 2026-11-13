# ONDE-PAREI: o fundo tirado não volta mais com a troca de filtro (13/11/2026)

Ramo `fundo-2026-11-13` (a partir do `obra-2026-10-26` em `863cdde3`), worktree `.claude/worktrees/fundo`.
Pedido da gerente de 13/11 (D-646, D-699). Nenhuma página dos Lusíadas no git: os prints usam o Siebmacher
(cópia das 10 primeiras folhas, fora do git, no scratchpad da sessão).

## Situação

- [x] Código: a regra num lugar só (`core/fundo_tirado.py`), o campo novo da página, o botão e o item de menu.
- [x] Prova nova `tests/test_decisoes_fundo_tirado.py` (21 provas); a reversão falha no `863cdde3` e passa aqui.
- [x] Prints no modelo do girar (`prints/fundo-1` a `fundo-4`) e medidas (`medidas-antes.json`, `medidas-depois.json`).
- [ ] **Uma prova antiga quebra** (fora das 3 autorizadas): `test_escolher_o_filtro_na_pagina_mostra_o_alerta`.
  Não mexi nela. Ver "Perguntas para o Samuel", pergunta 1.
- Testes no PC, GitHub e velocidade: ver "Testes" e "Velocidade".

## Decisões que esta tarefa precisa cumprir

- **D-646** (07/11): "Consertar" · "É só criar uma opção para desfazer o tirar fundo, e só vai desfazer o tirar
  fundo quando apertar ela. E via de regra, nenhum filtro deve fazer o fundo voltar."
- **D-699** (13/11, "Ok"): o botão "Desfazer o tirar o fundo" fica logo abaixo do "Tirar o fundo" no menu Filtro e
  no painel "Filtro da página" (embaixo das figurinhas), com o "Aplicar em" de sempre (só nesta / todas / daqui em
  diante). Depois do "Tirar o fundo", o Preto e branco, o Melhorar, o Mágico pro, o Original e o Automático
  trabalham em cima da página já sem o fundo. As três provas antigas que cobravam o jeito velho passam a cobrar o
  novo; projetos salvos com "Tirar o fundo" abrem com o fundo tirado e o filtro Original; o projeto ganha em cada
  página "fundo tirado: sim ou não", separado do filtro.
- **D-134** (29/09): "eu quero poder escolher tirar o fundo sem colocar nenhum filtro." · "Assim eu decido se tiro
  ou não, e o Kaique escolhe um filtro só, sem mudança escondida."
- **D-135** (29/09): a pergunta "Este livro tem fundo separado. Quer tirar o fundo?" uma vez por livro.
- **D-136** (29/09): o "Sim" troca só as páginas em Original.
- **D-490** (27/10): o "Sim" vale na hora, numa ação do desfazer; Ctrl+Z volta.
- **D-069** (30/09, F5): "BOM - mas eu quero poder ter essa opção dentro do app depois de abrir o livro, e também a
  opção de voltar ao original." (pela metade)
- **D-172** (05/10): "Sim, do mesmo jeito (só muda se alguém marcar um pedaço)": o "Tirar o fundo" obedece ao "só
  neste pedaço".
- **D-473** (26/10): "Tela e PDF diferentes é defeito, nunca escolha".
- **D-605** (03/11): "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e
  testado".
- **D-667** (10/11): "se mudou a ferramenta, muda em todos os lugares".
- **CLAUDE.md §11.12** (13/11): "o agente não pode fazer gambiarras [...] funcionava de maneira diferente em vários
  lugares."
- Também lidas (sem mudança): D-133 (substituída), D-137, D-256, D-477, D-492, D-572, D-592, D-596, D-597.

## O que já está escolhido e testado aqui (D-605)

- D-134/D-136/D-490 e o filtro "Tirar o fundo": `tests/test_tirar_fundo_no_programa.py` (54 provas).
- D-172 (o pedaço): `tests/test_so_neste_pedaco_no_tirar_o_fundo.py` (8 provas), entre elas
  `test_pedaco_em_original_mostra_o_papel_como_veio` (um pedaço em "Original" mostra o papel velho).
- D-137, D-256 (alerta "Conferir o fundo tirado"): `tests/test_camadas.py`.
- D-492 (tique do menu Filtro): `tests/test_decisoes_9b1.py`.
- D-473/D-547/D-649: `tests/test_decisoes_9b2.py`, `tests/test_graves_d649_*`.
- D-621 ("Desfazer nesta página"): `tests/test_decisoes_desfazer_pagina.py`.

## Como fica para quem usa e no livro (D-637)

**Antes.** O Kaique abre o Siebmacher, responde "Sim, tirar o fundo": o papel fica branco. Roda o Automático (que
abre com "Limpar a folha" em Original): o papel velho volta em todas as páginas, sem aviso. O mesmo acontecia ao
clicar na figurinha "Original" ou "Preto e branco", na tecla 1 a 4, no menu Filtro, na tela cheia ou no "Aplicar
em". Para voltar o fundo de uma página só havia trocar de filtro.

**Depois.**
1. "Sim, tirar o fundo": igual a antes (papel branco).
2. Automático em Original: o filtro vira Original e o papel continua branco (print `fundo-1-automatico.png`).
3. Qualquer filtro depois disso (figurinha, tecla, menu, tela cheia, "Aplicar em", Automático): o filtro é feito em
   cima da página sem o fundo; o Original é a página sem o fundo, sem filtro (print `fundo-3-preto-e-branco.png`).
   As figurinhas e o "comparar" da tela grande mostram isso mesmo (antes mostravam o papel velho).
4. Para trazer o fundo de volta: **menu Filtro > "Desfazer o tirar o fundo"** (último item, embaixo dos quatro
   filtros) ou o botão **"Desfazer o tirar o fundo"** no painel "Filtro da página", logo abaixo das figurinhas
   (print `fundo-4-botao-e-menu.png`). Vale para a página da vez; para as outras, "Aplicar em" > "todas" ou "daqui em
   diante" (print `fundo-2-desfazer.png`). O botão e o item só aparecem em livro com o "Tirar o fundo" e só ficam
   acesos na página sem o fundo. Ctrl+Z desfaz o botão.
5. Projeto antigo com páginas em "Tirar o fundo": abre com o fundo tirado e a figurinha "Original" acesa (o tique
   do menu Filtro também em "Original"). A página sai igual, ponto por ponto (prova
   `test_d699_projeto_antigo_em_tirar_o_fundo_abre_com_o_fundo_tirado_e_o_original`).

**No PDF.** As páginas sem o fundo continuam sem o fundo, com o filtro escolhido por cima. Páginas que nunca tiveram o
fundo tirado: nada muda. A tela e o PDF saem da mesma conta (prova do PDF = prévia).

**Problema novo que vi:** a faixa de baixo de uma página do projeto antigo (agora "Original com o fundo tirado") diz
"Esta página vai sair em Original." em vez de "Vou tirar o fundo desta página...". Não mudei texto (§11.7):
pergunta 3.

## Por que o defeito acontecia (a causa, §11.12)

O fundo tirado era guardado **só no filtro da página** (`ConfigPagina.filtro == "tirar_fundo"`). Toda troca de
filtro, por qualquer caminho, apagava a única marca de que o fundo tinha sido tirado, e o desenho (prévia e PDF)
voltava a usar a folha com o papel velho. O Automático não era o culpado: ele só trocava o filtro, como os outros.

## A regra da ferramenta (um lugar só: `core/fundo_tirado.py`)

- `ConfigPagina.fundo_tirado` (True = tirado; False = desfeito pelo botão; None = nunca tirado nem desfeito), lido e
  gravado só por `core/fundo_tirado.py`.
- `depois_da_troca(projeto, página, filtro)`: **a regra**. "Tirar o fundo" tira; qualquer outro filtro deixa como
  estava (a página sem o fundo continua sem ele).
- `esta_sem_o_fundo`: a página está sem o fundo (o campo, ou o filtro "Tirar o fundo" valendo).
- `campos_para_desfazer`: o "Desfazer o tirar o fundo" (o único que traz o fundo).
- `campos_do_aplicar_em`, `com_o_fundo_que_fica`, `filtro_por_cima`, `so_o_fundo_tirado`, `migrar_projeto_antigo`.

## Todos os caminhos que trocam filtro → a função que usam (achados com grep por `filtro`, `TIRAR_FUNDO`, `montar_acao`, `usa_tirar_fundo`)

| Caminho | Passa por | Regra |
|---|---|---|
| Figurinha grande (cartão) | `TelaConferir._escolher_filtro` → `_registrar` → `historico_acoes.montar_acao` | `fundo_tirado.com_o_fundo_que_fica` → `depois_da_troca` |
| Figurinha do painel "Filtro da página" | `filtro_escolhido` → `_escolher_filtro` → idem | idem |
| Teclas 1 a 4 | `TelaConferir.tratar_tecla` → `_escolher_filtro` → idem | idem |
| Botão do aviso (mudar o filtro) | `_escolher_filtro` → idem | idem |
| Menu Filtro (Original … Mágico pro) | `janela_principal` → `_escolher_filtro` → idem | idem |
| Tela grande (botões e teclas de filtro) | `TelaAmpliada._escolher_filtro` → `conferir._escolher_filtro` → idem | idem |
| Tela cheia dos filtros, "Usar" | `usar_da_tela_cheia` → `_escolher_filtro` / "Aplicar em" → idem | idem |
| "Aplicar em": só nesta | `_marcar_revisada` (não troca filtro) | — |
| "Aplicar em": todas / daqui em diante | `_filtro_em_todas` / `_filtro_nas_proximas` → `_campos_do_aplicar_em` (lista única, juntada) → `montar_acao` | `campos_do_aplicar_em` (leva o True ou o False da página) ou `depois_da_troca` |
| "Sim, tirar o fundo" | `janela._tirar_o_fundo_do_livro_inteiro` → `montar_acao` | `depois_da_troca` |
| Automático (e "Ver como fica", na cópia) | `core/automatico._ligar_na_pagina` → `_Gravador.na_pagina("filtro")` | `depois_da_troca` |
| "Desfazer nesta página" (Filtro) | `ui/desfazer_nesta_pagina.desfazer` (monta a ação sem `montar_acao`; passou a chamar a mesma função) | `com_o_fundo_que_fica` → `depois_da_troca` (o fundo fica) |
| Desfazer / refazer (Ctrl+Z / Ctrl+Shift+Z) | `historico_acoes.aplicar` com o `antes`/`depois` da ação | o campo vai na mesma ação |
| "Desfazer o tirar o fundo": menu e painel | `TelaConferir.desfazer_o_tirar_o_fundo` (a MESMA para os dois) | `campos_para_desfazer` |
| Prévia, tela, PDF | `pipeline.renderizar_pagina` / `_pagina_pronta` → `usa_tirar_fundo`; filtro por cima → `_filtrar_a_pagina_sem_fundo` (uma função para os dois) | `esta_sem_o_fundo`, `filtro_por_cima` |
| Figurinha "Tirar o fundo", tela cheia, "comparar" Tirar o fundo, miniatura composta (D-649) | `pipeline.renderizar_com_filtro` (cópia da página) | `depois_da_troca` |
| Tela cheia com opções mexidas e ainda não gravadas | `filtros_tela_cheia.pagina_com_as_opcoes` (a cópia) → `renderizar_com_filtro` | `depois_da_troca` na página de verdade |
| Figurinhas Original/PB/Melhorar/Mágico e o "comparar" da tela grande | `TelaConferir._imagem_sem_filtro` (a tela grande passou a chamar a mesma) | `usa_tirar_fundo` |
| Chave das prévias (cache) | `GerenciadorPrevias.chave` | `depois_da_troca` |
| Procurar gravura/letra pulada, marcação provisória | `precisa_do_desenho_do_pdf`, `_vai_detectar`, `_filtrar_preto_no_branco` | `so_o_fundo_tirado` |
| Alerta "Conferir o fundo tirado" | `pipeline.acertar_alertas_do_fundo` | `usa_tirar_fundo` |
| Abrir projeto | `Projeto.de_dicionario` | `migrar_projeto_antigo` |
| "Só neste pedaço" (filtro do pedaço) | grava `selecao`, não o filtro: não mexe no fundo tirado | — (desenho: ver pergunta 2) |
| Miniaturas da tira e da grade das páginas não mexidas | mostram a folha como veio (D-547), como antes | não mudou |

Comentários "é a mesma conta de..." conferidos: corrigi o de `ui/janela_principal._tirar_o_fundo_do_livro_inteiro`
("Original volta ao como veio"), o de `ui/tela_ampliada._imagem_do_outro_filtro` ("o que eles dariam também numa
página que está em Tirar o fundo") e o bloco "Item 1.1" de `core/pipeline.py`. As duas listas do "Aplicar em"
(escritas iguais à mão em dois lugares) viraram uma (`_campos_do_aplicar_em`).

**Prova que cobre os caminhos principais com o mesmo resultado:**
`test_d699_o_original_nao_traz_o_fundo_em_nenhum_caminho[...]` (figurinha, figurinha do painel, tecla 1, menu
Filtro, tela cheia, aplicar em todas, aplicar daqui em diante, Automático): em todos, a página sai **a mesma imagem,
ponto por ponto**, que no "Tirar o fundo", com o papel branco.

## As 3 provas antigas autorizadas

Nenhuma das três citadas pelo agente anterior precisou mudar: `test_original_nao_mexe_na_pagina`,
`test_outro_filtro_nao_tira_o_fundo` e `test_alerta_sai_quando_a_pagina_sai_do_filtro` mexem direto no filtro da
página (sem passar por nenhum botão) e continuam valendo: uma página que nunca teve o fundo tirado não é tocada, e
a regra mora nos caminhos de quem usa. **Não mudei nenhuma prova antiga.**

Quebra outra, do mesmo arquivo e do mesmo jeito velho: `test_escolher_o_filtro_na_pagina_mostra_o_alerta` (escolhe
"Tirar o fundo" e depois "Original" pela tela e cobra que o alerta "Conferir o fundo tirado" suma, porque o fundo
voltava). Agora o fundo fica tirado e o alerta continua. Pergunta 1.

## A reversão (§4.7)

`tests/test_decisoes_fundo_tirado.py::test_d646_sim_tirar_o_fundo_e_o_automatico_nao_traz_o_fundo_de_volta` (e as 8
de `test_d699_o_original_nao_traz_o_fundo_em_nenhum_caminho`):
- No código de antes (`863cdde3`, cópia em worktree à parte): **9 falharam**, todas com "o fundo voltou na página 1"
  (`reversao.txt`).
- No código novo: **9 passaram**.

## Medidas (§5): Siebmacher (cópia), páginas 3 a 6

Brilho do papel (mediana do canal azul da página desenhada; papel branco = 255, papel velho ≈ 150 a 175):

| Passo | Antes (863cdde3) | Depois |
|---|---|---|
| "Sim, tirar o fundo" | 255, 255, 255, 255 | 255, 255, 255, 255 |
| Automático em Original | **147, 166, 171, 175** (o fundo voltou) | **255, 255, 255, 255** |
| "Desfazer o tirar o fundo" na página 3 | (não existia) | 146 na 3; 255 nas outras |
| Automático em Preto e branco | (não existia) | 4 a 6 sem o fundo; a 3 sobre a página como veio |

Velocidade: ver abaixo.

## Testes

(preenchido no fim)

## Velocidade

(preenchido no fim)

## Perguntas para o Samuel

**Pergunta 1 (uma prova antiga do jeito velho).** A prova `test_escolher_o_filtro_na_pagina_mostra_o_alerta` cobra
que, depois de "Tirar o fundo", escolher "Original" tire o aviso "Conferir o fundo tirado" (porque o fundo voltava).
Agora o fundo continua tirado, então o aviso continua (a página ainda pode ter perdido alguma coisa com o fundo). É
do mesmo tipo das três que você autorizou mudar. Posso mudar essa também, para cobrar que o aviso fica?
Sugestão: sim.

**Pergunta 2 (o "só neste pedaço" numa página sem o fundo).** Hoje (D-172, "Sim, do mesmo jeito"), numa página em
"Tirar o fundo", um pedaço marcado em "Original" mostra o papel velho dentro do pedaço; há prova antiga que cobra
isso (`test_pedaco_em_original_mostra_o_papel_como_veio`). Deixei assim no "Tirar o fundo" e no "Original sem o
fundo". Nas páginas com Preto e branco, Melhorar ou Mágico pro por cima da página sem o fundo (o caso novo), o pedaço
é feito em cima da página sem o fundo, e o papel velho não volta. A D-646 diz "nenhum filtro deve fazer o fundo
voltar". O pedaço em "Original" deve também deixar de trazer o papel velho, em todas as páginas sem o fundo (muda
essa prova antiga)? Sugestão: sim, para o pedaço funcionar igual em todo lugar.

**Pergunta 3 (frase da faixa).** Numa página em "Original" com o fundo tirado (todo projeto antigo em "Tirar o
fundo" abre assim), a faixa de baixo diz "Esta página vai sair em Original." Antes dizia "Vou tirar o fundo desta
página. Onde não der, ela sai como veio." Quer que a faixa continue dizendo a frase do fundo nessas páginas?
Sugestão: sim.

**Pergunta 4 (o menu Filtro não tem "Tirar o fundo").** A D-699 diz "logo abaixo do 'Tirar o fundo' no menu Filtro",
mas o menu Filtro só tem os quatro filtros. Pus o "Desfazer o tirar o fundo" no fim do menu, depois de um risco. Quer
também o "Tirar o fundo" no menu, logo acima dele (só em livro com camadas)? Sugestão: sim (está na Lista de espera
de 29/09: "'Tirar o fundo' no menu Filtro, tecla 5").

## Ressalvas

- O "Aplicar em" leva o fundo da página da vez só quando ela tem o fundo tirado ou desfeito (True/False). De uma
  página que nunca teve o fundo tirado, leva só o filtro, e as outras ficam como estão. Escolha minha para cumprir
  "só o botão traz o fundo" junto com "o 'Aplicar em' de sempre" (prova
  `test_d699_aplicar_em_de_pagina_que_nunca_teve_o_fundo_tirado_nao_traz_o_fundo`).
- No Automático, se o "Limpar a folha" estava desligado e a página estava em "Tirar o fundo" sem valer, rodar
  "Limpar a folha" com outro filtro deixa o fundo tirado (o "Limpar" é ligado antes da troca). Caso raro.
- O "Desfazer o tirar o fundo" com "todas" não muda o filtro do livro (o que o Automático abre).
- Projeto antigo: o Ctrl+Z de um "Sim, tirar o fundo" gravado ANTES do conserto (no histórico de ações da sessão
  antiga) não traz o fundo de volta (aquela ação não tem o campo novo). Para isso há o botão.
- A frase de explicação do "Original" no Automático ("a página como veio") não mudou.
- `test_decisoes_desfazer_pagina.py::test_d621_botao_direito...` falhou uma vez na bateria (a marcação da página
  vizinha mudou de lugar) e passou nas duas rodadas seguintes, no código novo e no de antes. É a instabilidade que o
  agente dos graves já tinha visto nesse arquivo; não tem relação com o fundo (o livro do teste não tem camadas).

## Ideias para a Lista de espera

- A figurinha "Tirar o fundo" e as figurinhas dos outros filtros ainda são feitas por caminhos diferentes (a do
  fundo e a do Misto pelo caminho do programa, as outras com a conta simples na amostra). Juntar tudo em uma conta
  (achado A2 da revisão de código) deixaria as figurinhas iguais à página em todos os casos.

## Bugs para a Lista de bugs

(nenhum novo)
