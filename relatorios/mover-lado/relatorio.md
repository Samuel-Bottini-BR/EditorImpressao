# D-612: o Mover funciona em "Duas lado a lado" — relatório do implementador (04/11/2026)

Ramo `mover-lado-2026-11-04` (saiu de `obra-2026-10-26` em `dd7a648c`). Teste de **máquina** (testes
automáticos e piloto da janela de verdade). O teste de **olho** é do Samuel.

## O que mudou, em uma frase

Com a ferramenta Mover e a vista em "Duas lado a lado", a página da vez dentro dos pares passa a ser o
próprio Mover: arrastar move, puxar o canto muda o tamanho, o número e a tecla F valem. A vista não muda
sozinha.

## Palavras do Samuel

Pergunta: "Ao escolher Mover, Cortar, Endireitar ou marcar, a tela passa sozinha para Uma página?" →
"1 - ele tem que funcionar com paginas lado a lado também".

## Como ficou

- Nos pares, a página da vez mostra o Mover como na "Uma página": a área branca, a página por cima, os
  quatro cantos azuis, a parte que passa da beirada apagada com listras vermelhas (D-543). A vista se
  ajusta para caber a área branca e a página inteira (D-541), dentro do lugar da página no par.
- A outra página do par continua a prévia de sempre. Clicar nela faz dela a página da vez (como já era);
  o Mover passa para ela.
- A roda do mouse em cima da página do Mover faz o mesmo que no resto dos pares: Ctrl+roda dá zoom no par
  (D-570), sem Ctrl rola.
- "Uma página", outra ferramenta, "antes / depois", Dividir: o Mover volta para o lugar de sempre, com o
  zoom que tinha. Nada muda nesses.
- Cortar, Endireitar, marcar e "antes / depois": **não mexidos** (esperando a resposta do Samuel). Para
  estender, basta pôr a ferramenta na lista `FERRAMENTAS_NO_PAR` (`ui/tela_conferir.py`); a de marcar
  precisa também de um lugar de volta.

## Onde (arquivos)

- `ui/tela_conferir.py`: `FERRAMENTAS_NO_PAR`; `_acertar_a_vista_da_pagina` chama
  `_acertar_a_ferramenta_no_par`; novas `_acertar_a_ferramenta_no_par`, `_devolver_a_peca_do_par`,
  `_roda_na_peca_do_par`; `eventFilter` (a roda da peça vai aos pares); `_limpar_abas` (devolve a peça
  antes de fechar o livro).
- `ui/widgets/paginas_lado_a_lado.py`: `definir_ferramenta`, `tirar_ferramenta`,
  `_por_a_ferramenta_no_lugar`; `_arrumar` e `ir_para` acertam o lugar da peça.
- `ui/widgets/visualizador.py`: `folga_da_moldura` (de fábrica a de sempre, 32; 8 só nos pares).
- `tests/test_decisoes_mover_lado.py` (novo, 7 provas).

## Prints (janela de verdade, Gradus, cópia dos dados de teste)

- `prints/p02-dividir-duas-lado-a-lado-folha-inteira.png`: Dividir em "Duas lado a lado", a folha inteira
  com a linha (D-601); a linha anda com o mouse (D-609).
- `prints/p03-F-mover-nos-pares.png`: tecla F, a vista continua nos pares, a página da vez com os cantos
  azuis; a tira embaixo em pares (D-611).
- `prints/p04-arrastou-nos-pares.png`: arrastada 12% para a esquerda; a parte de fora vermelha com
  listras; o aviso "Parte do que está impresso vai ficar de fora".
- `prints/p05-ctrl-z-ctrl-y.png`: Ctrl+Z desfaz, Ctrl+Y refaz.
- `prints/p06-canto-nos-pares.png`: canto puxado, 85%, o número acompanha.
- `prints/p07-numero-80-nos-pares.png`: 80 digitado no número.
- `prints/p08-ctrl-roda-zoom-nos-pares.png`: Ctrl+roda em cima da página do Mover dá zoom no par.
- `prints/p09-outra-pagina-do-par.png`: clique na outra página do par, ela vira a da vez com o Mover.
- `prints/p10-uma-pagina-mover.png`: "Uma página", o Mover de sempre.
- `prints/p11-cortar-nos-pares.png`: Cortar em "Duas lado a lado", os pares de sempre.
- Piloto: `piloto.py`, **20 de 20** conferências (`conferencias.txt`, `anotacoes-piloto.txt`).

## Testes no PC (um arquivo por vez)

| arquivo | resultado |
|---|---|
| test_decisoes_mover | 13 passaram |
| test_decisoes_mover_lado (novo) | 7 passaram |
| test_decisoes_ver | 11 passaram |
| test_decisoes_dividir_metade | 6 passaram |
| test_decisoes_dividir_arrastar | 16 passaram |
| test_decisoes_tira_em_pares | 4 passaram |
| test_previa_composta | 10 passaram |
| test_paineis_na_tela | 22 passaram |
| test_visualizador | 70 passaram |
| test_zoom_no_ponteiro | 5 passaram |
| test_decisoes_9b2 | 30 passaram |
| test_livro_aberto | 14 passaram |
| test_decisoes_dividir_linha | 13 passaram |
| test_decisoes_dividir | 21 passaram |
| test_dividir_na_tela | 9 passaram |
| test_decisoes_marcacoes | 19 passaram |
| test_guias | 14 passaram |
| test_decisoes_shift_todas_as_telas | 10 passaram |
| test_decisoes | 26 passaram |

Depois do segundo conserto (a roda), rodados de novo: test_decisoes_mover_lado 7, test_zoom_no_ponteiro 5,
test_decisoes_9b2 30, test_decisoes_ver 11 — todos passaram. **Nenhum teste antigo foi mudado.**

**Teste de reversão:** `tests/test_decisoes_mover_lado.py` no código antigo (`dd7a648c`, os três arquivos de
`ui/` voltados): **5 falharam** (arrastar nos pares, vindo do Dividir, canto, número/peça nos pares, outra
página do par) e 2 passaram (são guardas do que já funcionava: "Uma página"/outra ferramenta/Dividir, e o
Ctrl+roda nos pares).

## Rodada do GitHub

Rodada **41856247413** (ramo `mover-lado-2026-11-04` em `bb11ff93`): **passou inteira** — as 5 partes da
suíte, os botões e prints da janela real, e o resumo.

## Ressalvas

- **Achado do piloto, já consertado:** na janela de verdade, Ctrl+roda em cima da página do Mover dava zoom
  mas pulava para a última página (a conta do ponto passava pela tela inteira). Consertado (commit
  `1aa98650`); a prova automática confere que a página da vez não muda, mas na janela de teste do PC (sem
  tela) a conta errada não aparecia: quem pegou foi o piloto (`piloto_roda.py`: Cortar e Mover agora iguais).
- Nos pares, a página do Mover fica com 8 pontos de folga em volta (para os cantos azuis aparecerem
  inteiros): ela sai um pouco menor que a outra página do par. Com o conteúdo passando da beirada, a área
  branca fica ainda menor, porque a vista mostra a página inteira (D-541), como na "Uma página".
- Página da vez tirada do livro (não aparece nos pares): o Mover fica fora dos pares, como antes.
- Com o foco do teclado no número "Tamanho do conteúdo" (depois de digitar nele), as letras X e F viram
  texto do número e não trocam de ferramenta. Já era assim; não mexi.

## Bugs para a Lista de bugs (não consertados, já eram assim)

- **Área branca muda de 29,7 × 21,0 para 31,7 × 22,0 cm** no Gradus (página 39, "margens iguais" ligado pelo
  Automático) depois de Ctrl+Z e Ctrl+Y de um arrasto, com o mesmo estado da página. Acontece também na "Uma
  página" (`piloto_area.py`, `anotacoes-piloto-area.txt`, print `p201`), caminho que este conserto não mexe.
  Parece a conta das margens iguais chegando depois; não investigado a fundo.

## Perguntas para o Samuel (escolhas que mantive como já eram)

1. Clicar na outra página do par: hoje (como já era nos pares) o clique só a escolhe; o arrasto vale a
   partir do próximo aperto. Quer que já arraste no mesmo aperto? (print `p09`)
2. Os cantos azuis aparecem só na página da vez, não nas duas (como na "Uma página", que mostra uma).
   Está bom? (print `p03`)
3. "usar em todas..." nos pares: igual à "Uma página" (leva o tamanho e o lugar da página da vez). Não muda.

## Decisões: como cumpri cada uma

- D-612: provas `test_reversao_d612_*` e `test_d612_*`; piloto 20/20; prints p03 a p09.
- D-008/D-541 (arrastar, canto, número, a vista se ajusta): `test_reversao_d612_arrastar...` (tela = PDF até
  1%), `..._puxar_o_canto...`, `test_d612_numero_do_tamanho...`; p04, p06, p07.
- D-540 (F): `test_reversao_d612_vindo_do_dividir...`, `test_d612_numero_do_tamanho_e_tecla_f...`; p03.
- D-543/D-017: a parte de fora vermelha com listras e o aviso nos pares (p04).
- D-006/D-015/D-570 (pares, zoom do par): `test_d612_os_pares_continuam_pares`,
  `test_d612_ctrl_roda...`; p08, p09, p11.
- D-601/D-609/D-610/D-611: provas antigas passando; piloto (linha arrastada no Dividir em "Duas lado a
  lado", p02; tira em pares, p03).
- D-605: nenhum teste antigo mudado; 19 arquivos de teste passando; "Uma página" igual (p10).


---

# Segunda parte: Cortar, Endireitar e marcar em "Duas lado a lado" (04/11/2026)

Palavras do Samuel: "O Cortar, o Endireitar e o marcar também têm que funcionar em 'Duas lado a lado' e
em 'antes / depois', como o Mover?" → "1- sim".

## O que mudou

- Nos pares, com o Cortar, o Endireitar ou uma ferramenta de marcar (Retângulo, Laço, Pincel, Varinha...),
  a página da vez passa a ser a própria ferramenta, do mesmo jeito do Mover: puxar a beirada do corte,
  desenhar a linha do Endireitar ou girar pela bolinha, marcar. A vista não muda sozinha.
- A Mão e o Zoom só olham: nos pares continuam os pares de sempre (sem o editor por cima).
- Com o Pincel, a Varinha ou a Cor, a roda sozinha continua mudando a espessura ou a tolerância (D-600);
  Ctrl+roda dá zoom no par.
- **"antes / depois": ainda não** (pergunta para o Samuel: em qual lado a ferramenta age).
- Onde: `ui/tela_conferir.py` (`FERRAMENTAS_NO_PAR` com as quatro, `_a_ferramenta_vai_no_par`,
  `_peca_da_aba`, `_por_a_vista_da_peca`, `_roda_da_peca_e_da_ferramenta`; `escolher_ferramenta` acerta a
  peça ao trocar entre Mão/Zoom e as de marcar). Teste novo: `tests/test_decisoes_ferramentas_lado.py`.

## Prints (janela de verdade, Gradus)

- `prints/p301-cortar-nos-pares.png`, `prints/p302-cortar-puxou-a-beirada.png`: o Cortar na página da vez.
- `prints/p303-endireitar-nos-pares.png`: a linha torta girou a página (-2,73 graus).
- `prints/p304-retangulo-nos-pares.png`: um retângulo marcado ("gravura ou foto").
- `prints/p305-pincel-ctrl-roda-nos-pares.png`: Ctrl+roda dá zoom no par com o Pincel.
- `prints/p306-mao-nos-pares.png`: a Mão, os pares de sempre.
- `prints/p307-uma-pagina-endireitar.png`: "Uma página" igual.
- Piloto `piloto_ferramentas.py`: **15 de 15** (`ferramentas/conferencias.txt`).

## Testes no PC (um arquivo por vez, todos passaram)

ferramentas_lado (novo) 9, mover_lado 7, mover 13, ver 11, dividir_metade 6, dividir_arrastar 16,
tira_em_pares 4, previa_composta 10, paineis_na_tela 22, visualizador 70, zoom_no_ponteiro 5, 9b2 30,
livro_aberto 14, dividir_linha 13, decisoes_dividir 21, dividir_na_tela 9, marcacoes 19, guias 14,
shift_todas_as_telas 10, decisoes 26, endireitar_no_programa 15, gravura_na_aba_marcar 8,
trilha_e_opcoes 29, selecao 24, nucleo 38, nucleo2 21, corte_previa_igual_pdf 4
(`testes-pc-2.txt`). **Nenhum teste antigo mudado.**

Reversão: no código antes desta parte (`472e410c`), 4 provas novas falharam (Cortar, Endireitar,
Retângulo, Pincel) e 5 passaram (guardas: Mão/Zoom e "Uma página").

## Ressalvas da segunda parte

- No Cortar, a página da vez mostra a página inteira (sem cortar, com o retângulo verde, como na "Uma
  página"); a outra página do par mostra como vai sair. Por isso ela pode parecer de outro tamanho.
- A peça fica 8 pontos menor que o lugar da página no par (só nas ferramentas com moldura: Mover, Cortar,
  Endireitar); o editor de marcar ocupa o lugar inteiro.

## GitHub da segunda parte

Rodada 41862461610 (em `bcae6968`): passou tudo menos `test_decisoes_so_as_letras::test_d148` (parte 5) e
`test_promessas::test_p083_*` (2 erros, parte 1), os dois que às vezes estouram o tempo lá. No PC:
`test_decisoes_so_as_letras` 5 passaram; `test_promessas` 267 passaram, 1 xfailed, nenhum erro.

---

# Terceira parte: as ferramentas no "antes / depois" (04/11/2026)

Palavras do Samuel: "1- sim" e, explicado de novo, "Ok, pode ser assim o antes e depois" (as ferramentas
mexem na imagem do "depois"; o "antes" fica parado, só para comparar).

## O que mudou

- Com "antes / depois" ligado, Mover, Cortar, Endireitar e as de marcar ficam por cima da página **só à
  esquerda da linha azul** (o "depois", D-577). Ali a mão usa a ferramenta. À direita (o "antes") nada muda
  com o mouse. A linha continua se arrastando, e o pedaço da ferramenta acompanha.
- As caixinhas "antes: Original" / "depois: ..." e o aviso escrito continuam à vista por cima.
- A Mão e o Zoom: como antes. O "antes / depois" continua sem zoom (a roda em cima da ferramenta não dá zoom
  nem troca de página; a do Pincel/Varinha/Cor continua da ferramenta).
- Onde: `ui/widgets/filtros_tela_cheia.py` (`VistaAntesDepois`: `definir_ferramenta`, `tirar_ferramenta`,
  `_por_a_ferramenta_no_lugar` com a máscara, `_caixas_dos_rotulos`, `_caixa_do_aviso`);
  `ui/tela_conferir.py` (`_onde_vai_a_peca`, `_acertar_a_casa_da_peca`, a roda). Teste novo:
  `tests/test_decisoes_ferramentas_antes_depois.py` (12). Reversão: em `bcae6968`, 6 falharam e 5 passaram.

## Prints (janela de verdade, Gradus, página 39 em Preto e branco)

- `prints/p401-mover-antes-depois.png`, `prints/p402-mover-arrastou-no-depois.png` (Mover no "depois").
- `prints/p403-linha-arrastada.png` (a linha arrastada; o pedaço da ferramenta acompanhou).
- `prints/p404-cortar-no-depois.png`, `prints/p405-endireitar-no-depois.png`,
  `prints/p406-retangulo-no-depois.png` (rótulos à vista).
- Piloto `piloto_antes_depois.py`: **16 de 16** (`antes-depois/conferencias.txt`).

## Ressalvas da terceira parte

- O rótulo "antes: Original" fica no canto esquerdo e o "depois" no direito (como decidido na D-577: dizem
  para que lado arrastar a linha). A ferramenta age à esquerda da linha, que é o "depois", embaixo do
  rótulo "antes". Pode confundir: ver print p406.
- No Cortar, o lado da ferramenta mostra a página inteira, sem cortar (como na "Uma página"), e o "antes"
  mostra a página como sai: as duas partes não ficam do mesmo tamanho (print p404). No Mover, com o
  conteúdo passando da beirada, o mesmo (a vista mostra a página inteira, D-541).

---

# Defeito de 04/11 (print a-65): o "tamanho" de cima não acompanhava o pincel

Palavras do Samuel: "no modo do pincel, quando eu giro o scrool ele fica aumentando e diminuindo o tamnho do
pincel no painel direito mas no painel de cima 'tamanho' ele não muda nada".

## O que mudou (commit `033560c9`, separado)

- A roda continua mudando o pincel (D-600). Agora o deslizante "tamanho" da barra de cima acompanha.
- Mexer no "tamanho" de cima muda o pincel e também o número do painel ("Pincel: N% da página").
- Escolher o Pincel de novo mostra o tamanho de agora (antes voltava ao de fábrica na barra).
- A mesma peça na Varinha e na Cor: a "tolerância"/"variação" de cima acompanha a roda.
- Onde: `ui/widgets/barra_opcoes.py` (`mostrar_ajuste`), `ui/widgets/editor_selecao.py`
  (`frase_do_ajuste`), `ui/tela_conferir.py` (`_acertar_a_barra_pelo_editor`, `_mudar_no_editor`).
- Teste de reversão: `tests/test_bug_04_11_pincel_tamanho.py` (4): em `18cb692e` os 4 falharam.
- Prints: `prints/p407-pincel-roda-tamanho-de-cima.png`, `prints/p408-pincel-tamanho-de-cima.png`.

## Testes no PC da terceira parte e do defeito (um arquivo por vez, todos passaram)

pincel_tamanho (novo) 4, ferramentas_antes_depois (novo) 11 (12 com a prova dos rótulos), ferramentas_lado 9,
mover_lado 7, mover 13, ver 11, dividir_metade 6, dividir_arrastar 16, tira_em_pares 4, previa_composta 10,
paineis_na_tela 22, visualizador 70, zoom_no_ponteiro 5, 9b2 30, livro_aberto 14, dividir_linha 13,
decisoes_dividir 21, dividir_na_tela 9, marcacoes 19, guias 14, shift_todas_as_telas 10, decisoes 26,
endireitar_no_programa 15, gravura_na_aba_marcar 8, trilha_e_opcoes 29, selecao 24, nucleo 38, nucleo2 21,
corte_previa_igual_pdf 4, filtros_tela_cheia 11, automatico_ver_como_fica 22, 9b1 25, atalhos 15,
barra_de_menu 20, opcoes_da_gravura_na_tela 15 (`testes-pc-3.txt`). **Nenhum teste antigo mudado.**

---

# Pedido do Samuel depois de testar: a página da ferramenta do tamanho da prévia nos pares (04/11/2026)

Palavras dele: "ele funciona mas eu não gostei do tamanho que aparece a pagina quando começa a mover ela,
ela deveria continuar o preview das duas do mesmo tamanho."

## O que mudou (commit próprio)

- Nos pares, a página da ferramenta não encolhe mais. No Mover, a área branca é exatamente o lugar da página
  no par (o tamanho da prévia), antes, durante e depois de arrastar ou mudar o tamanho. A parte que passa da
  beirada (apagada, vermelha, com listras) e os cantos azuis aparecem em volta, no espaço cinza entre as páginas.
- Cortar, Endireitar e marcar: a página da ferramenta na altura da prévia (no par as duas têm a mesma altura),
  no meio do lugar dela.
- As outras páginas ficam por cima: a outra página do par continua inteira à vista e o clique nela continua
  escolhendo ela. Só os cantos azuis (e as alças do corte, a bolinha do Endireitar) ficam por cima de tudo.
- Onde: `ui/widgets/visualizador.py` (`definir_lugar_no_par`, `_area_no_lugar`, `retangulos_das_pegas`; o
  aperto que não pega nada passa para os pares), `ui/widgets/paginas_lado_a_lado.py`
  (`_por_a_ferramenta_no_lugar` com a máscara), `ui/tela_conferir.py` (`_previa_chegou` acerta o lugar).
- Teste: `tests/test_decisoes_tamanho_no_par.py` (5): mede a área da página da ferramenta contra o lugar
  dela no par e a altura da outra página, antes e depois de arrastar e de puxar o canto. Em `07c051fb`: 3
  falharam (Mover, Cortar, Endireitar) e 2 passaram (marcar já ficava da altura no livro de teste; a outra
  página clicável).

## Prints (janela de verdade, refeitos)

- `prints/p03-F-mover-nos-pares.png`, `prints/p04-arrastou-nos-pares.png` (Mover do tamanho da prévia; a
  parte de fora em vermelho à esquerda, na margem), `prints/p06-canto-nos-pares.png`.
- `prints/p301` a `p307` (Cortar, Endireitar, Retângulo, Pincel, Mão nos pares).
- Pilotos: `piloto.py` 20/20, `piloto_ferramentas.py` 15/15, `piloto_antes_depois.py` 16/16.

## Ressalvas

- A parte de fora do Mover que vai para o lado da outra página do par fica por baixo dela (só aparece no
  espaço cinza). Se o conteúdo for todo para esse lado, os cantos podem ficar por baixo da outra página; o
  número "Tamanho do conteúdo" e "Centralizar" continuam valendo, e na "Uma página" aparece tudo.
- No Cortar a página aparece inteira, sem cortar, na altura da prévia: ela pode ficar um pouco mais larga ou
  mais estreita que o lugar da prévia cortada.
- `test_paineis_na_tela::test_a_faixa_tem_esta_certo_e_proxima_duvida` falhou 1 vez numa rodada no PC e passou
  sozinho e em mais 2 rodadas do arquivo inteiro (e nas 3 rodadas anteriores): parece de tempo, não do conserto.
- Os dados de teste do Gradus mudaram durante o dia (de 70 para 140 páginas, já divididas); os prints novos são
  com os dados de agora.

## Testes no PC (rodada 4, um arquivo por vez)

tamanho_no_par (novo) 5, pincel_tamanho 4, ferramentas_antes_depois 12, ferramentas_lado 9, mover_lado 7,
mover 13, ver 11, dividir_metade 6, dividir_arrastar 16, tira_em_pares 4, previa_composta 10,
paineis_na_tela 22 (uma vez 21+1, ver ressalva), visualizador 70, zoom_no_ponteiro 5, 9b2 30, livro_aberto 14,
dividir_linha 13, decisoes_dividir 21, dividir_na_tela 9, marcacoes 19, guias 14, shift_todas_as_telas 10,
decisoes 26, endireitar_no_programa 15, gravura_na_aba_marcar 8, trilha_e_opcoes 29, selecao 24, nucleo 38,
nucleo2 21, corte_previa_igual_pdf 4, filtros_tela_cheia 11, automatico_ver_como_fica 22, 9b1 25, atalhos 15,
barra_de_menu 20, opcoes_da_gravura_na_tela 15 (`testes-pc-4.txt`). **Nenhum teste antigo mudado.**

GitHub da terceira parte e do pincel: rodada 41886245180 (em `07c051fb`) **passou inteira**.
GitHub final (rodada **41892321210**, em `4ede8fd5`): passou tudo menos 1 teste, na parte 4:
`test_gravura_na_aba_marcar::test_pagina_de_projeto_antigo_que_muda_de_forma_e_refeita` (lá a marcação já
tinha sido refeita por trás quando o teste olhou: `'scantailor|...' == 'refazer'`). No PC esse arquivo passou
inteiro 3 vezes seguidas (8 de 8) e nas rodadas 2, 3 e 4; na rodada 41886245180 do GitHub (em `07c051fb`,
com tudo menos o tamanho da prévia) também passou. O teste não usa os pares, o "antes / depois" nem a barra
de cima. Parece de tempo; ressalva para a gerente decidir se roda de novo.

---

# Consertos do teste do Samuel de 04/11 (prints a-74 a a-78) e a ordem dos pares da tira

Commits (cada um separado, ramo `mover-lado-2026-11-04`, depois de juntar a obra duas vezes):
- A, a-75/a-76 (a miniatura marcada): primeiro marquei as duas metades da folha, mas um teste antigo da D-611
  pede uma só. Voltei atrás e fiz o que o Samuel respondeu depois (a D-611 atualizada, abaixo): uma só marcada,
  dentro do par da folha que está na tela.
- B, a-77/a-78 (`"D-612 (a-77/a-78)..."`): com Mover, Cortar e Endireitar, o "antes / depois" sempre compara,
  também com a página em Original e sem o aviso. O "depois" mostra o que a ferramenta fez (131%, por exemplo).
  O "antes" mostra a página como veio: a metade da folha do PDF no Original, sem endireitar, cortar nem mover.
  Nas outras ferramentas (Mão, Zoom, marcar, Filtro), o aviso "Escolha outro filtro..." continua, porque ali a
  comparação é só do filtro. Prova: `tests/test_decisoes_antes_depois_da_ferramenta.py` (5; em `d2567fab`
  falharam 4).
- (a), resposta "ok": nos pares, o mesmo aperto na outra página escolhe e já arrasta, no Mover, no Cortar e nas
  de marcar; no Endireitar só escolhe. Prova: `tests/test_decisoes_par_escolhe_e_arrasta.py` (4; em `d2567fab`
  falharam 3).
- C, D-622: no Mover, clicar no cinza fora da página larga a escolha: somem os cantos azuis e o contorno e, nos
  pares, o quadro azul da página da vez. Clicar na página escolhe de novo, e o arrasto continua movendo. Outra
  página chega escolhida. Fora do Mover, como antes. Prova: `tests/test_decisoes_d622_clicar_fora.py` (3; em
  `d2567fab` falharam).
- D-611 atualizada ("SIm, mas tem que verificar se vai ficar assim em todo os lugares né? a miniatura
  corresponder com o numero real"):
  - no Dividir com "Duas lado a lado", a tira junta as duas metades da mesma folha, igual à tela grande;
  - o número embaixo de cada miniatura é o da página (o mesmo de "página N de M");
  - fora do Dividir, os pares da tira são os da tela grande; a página tirada do livro fica sozinha;
  - prova que percorre Mão, Mover, Cortar, Endireitar, Retângulo e Dividir, em "Uma página" e "Duas lado a
    lado", com a capa aberta (D-616) e a ordem mudada à mão (D-615): `tests/test_decisoes_tira_numero_real.py`
    (3). No código antes do conserto falharam 2: os pares com uma página tirada, e no Dividir duas miniaturas
    marcadas ao mesmo tempo depois da ordem mudada.
  - testes antigos mudados com autorização da gerente, só a parte do Dividir:
    `test_decisoes_tira_em_pares.py::test_reversao_d611_tira_em_pares_no_dividir_em_duas_lado_a_lado` e
    `test_decisoes_tira_pares_juntas.py::test_reversao_d611_par_junto_no_dividir_em_duas_lado_a_lado`.

Janela de verdade (Gradus): `piloto_consertos.py` 10/10, prints `p501` a `p508`. Os pilotos anteriores, refeitos
no código final: 20/20, 15/15 e 16/16. Testes no PC, um arquivo por vez: 47 arquivos, todos passaram
(`testes-pc-6.txt`).

Pergunta (c), o rótulo do "antes / depois", no print `p507`: o rótulo "antes: Original" fica no canto esquerdo,
em cima do lado onde a ferramenta age (o "depois").