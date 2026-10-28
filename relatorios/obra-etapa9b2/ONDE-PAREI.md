# Obra de 26/10/2026 — etapa 9b-2 (a área de trabalho): ONDE PAREI

Ramo `obra-etapa9b2-2026-10-26` (base `obra-2026-10-26` = `27b4c52`), worktree `.claude/worktrees/obra-etapa9b2`.
Agente: layout + implementador. Ao mesmo tempo, a etapa 9b-1 mexe em menus, impressão e janelas
(`ui/janela_principal.py`, `ui/barra_de_menu.py`, `ui/dialogo_impressao.py`, `ui/janela_confirmar.py`,
`ui/widgets/paineis.py`, `modelos.nome_de_saida_sugerido`): **não mexi em nenhum deles** (só chamei métodos que já
existiam neles: `paineis.automatico.estado.do_projeto` e o atributo `medida_ao_abrir` da janela).

Regra 7 (Samuel, 27/10/2026): "é só para fazer o que eu já tinha mandado, fazer as ferramentas que colocamos no
programa funcionem como deveriam e como eu tinha escolhido."

**Situação: PRONTO PARA CONFERIR** (27-28/10/2026). Falta: verificador separado, conferência do Samuel. Nada juntado.

## Em uma frase

Agora a grade "Todas as páginas" divide as folhas escolhidas (com a conta do ScanTailor do "dividir esta", com
andamento); a faixa preta da tampa do scanner some também pelo Automático, cortada ou pintada de branco como o livro
escolher; as telas e as miniaturas mostram a página movida como sai no PDF, e a tela troca pela imagem do PDF quando
ela fica pronta, com as duas bolinhas de carregamento; com zoom a roda anda pela página e o lado a lado tem zoom; o
Cortar tem a caixinha "Margens iguais"; o desfazer tira o retângulo marcado (e ele não sai mais impresso) e devolve
os avisos; o "usar em todas" do Dividir pergunta em quais folhas; "letra e traço" à mão protege a tinta; e saíram as
duas contas que o Samuel mandou tirar.

## Decisões que esta tarefa precisa cumprir (número + palavras dele)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| D-558 (27/10) | `ac-grade-inserir`: "quando falei dividir é dividir a pagina, usando a funcionalidade do scantailor que colocamos no aplicativo, é isso que deveria ser feito." | "Dividir" na grade "Todas as páginas", nas folhas escolhidas, com a função de dividir do ScanTailor do programa (a mesma do "dividir esta"), com andamento. Sai a D-529. |
| D-334 (24/09) | (paráfrase) "Ver todas as páginas do livro em grade [...]: seleção múltipla, girar, apagar, extrair, inserir, dividir." | (o "dividir" é a D-558; o "inserir" ficou para depois, D-567) |
| D-559 (27/10) | `ac-tampa`: "Como eu decidi: sumir em todo o livro, e o Kaique escolhe por livro cortar ou pintar de branco (recomendo)" | A faixa preta da tampa do scanner some em todo o livro, também no Automático; por livro, cortar ou pintar de branco. Substitui D-495/D-499 (só à mão). |
| D-097 (13-21/10) | "É para sumir totalmente." · "tem que ficar rente a folha de papel, não pode ter preto ali." | Nada de preto da tampa no PDF. |
| D-092 (09/10) | `rv5-pag-egenloff-047`: "O Kaique escolhe por livro" | A escolha cortar / pintar de branco é do livro. |
| D-547 (27/10) | (escolha da gerente sobre D-066: "precisamos que o pdf saia que nem está na tela") | Todas as telas e miniaturas mostram a página movida/redimensionada como sai no PDF. |
| D-473 / D-066 / D-064 | D-066: "precisamos que o pdf saia que nem está na tela" · D-064: "é só colocar uma bolinha de carregamento, pode ter uma pro livro inteiro e outra para a pagina que estamos, quando passsamos o mouse em cima mostra a mensagem de porcentagem e quantas paginas carregaram já." | Quando a medida no tamanho do PDF termina, a tela troca pela imagem do PDF reduzida (troca da 10b, `ui/tarefas.py`), e as duas bolinhas. |
| D-568 (27/10) | `v-roda`: "Como ficou: sem zoom troca de página; Ctrl + roda dá zoom" | Com zoom, a roda anda pela página. |
| D-570 (27/10) | `v-zoom-pares`: "Sim, zoom também no lado a lado" | O "– N% +" vale no "Duas lado a lado". |
| D-571 (27/10) | `v-100`: "A página inteira cabendo na tela (recomendo)" | Conferir: 100% = página inteira cabendo. |
| D-554 / D-494 / D-075 | `ac-margens-iguais`: "Também na tela do corte" · D-075: "Mas eu vou conseguir alterar isso né?" | Caixinha "Margens iguais" também na tela do Cortar, ligada ao mesmo valor do Automático. |
| D-563 (27/10) | `ac-desentortar-texto`: "Tirar, voltar como era antes (recomendo)" | Sai a conta "desentortar só o bloco do texto" (D-493/D-530), com os testes dela. |
| D-564 (27/10) | `ac-gravura-cinza`: "Não fazer: gravura continua em preto e branco (recomendo)" | Sai a chave `GRAVURA_ESCURA_EM_CINZA` (D-532), com os testes dela. |
| D-020 (18/07) + P-129 | "13. Ctrl+Z desfaz qualquer alteração, sem limite de quantidade, e Ctrl+Shift+Z refaz" | O desfazer tira a marcação do Retângulo (lista 1.3, 1.9, 4.6); o aviso volta (1.6); o desfazer não desfaz o que não está à vista (1.7). |
| D-090 / D-091 + P-061 | "eu devo conseguir abrir uma aba para selecionar as que eu quero ( as paginas) ou também simplismente apertar num botão e selecionar todas." · "'Selecionar todas' e 'Nenhuma'" | "usar em todas" (Cortar e Dividir) abre a lista com as exceções desmarcadas e nunca apaga exceção. |
| D-156 (01/10) | "espero ter a escolha de conseguir deixar a foto em original, caso precise." | "Só neste pedaço" vale também no Preto e branco / sem "Limpar a folha". |
| Lista de bugs 12/10 | (bug) "letra e traço" marcado à mão não protege a tinta do "Só as letras" | A marcação à mão protege a tinta. |
| Lista de bugs 22/10 | (bug) botões que aparecem por um instante como janelinhas soltas ao abrir | Não piscam. |
| Lista de espera 29/09 | "Recuperar o trabalho anterior" no menu do cartão (ideia de agente, "a definir") | Não é decisão do Samuel no Livro: fica como está, vira pergunta. |
| D-114 (18/07) | "PRETO E BRANCO → slider 'Força do preto' [...] MÁGICO PRO → slider 'Intensidade' [...] MELHORAR → slider 'Clareza do fundo'" | (lista 1.2 e 5.9) o aviso da "força do preto" só na página de Preto e branco. |
| D-037 / D-052 | R7 203: "D — Ícones na borda, tudo fechado" · R13 802: "A — Abre sozinho" | (lista 2.3) os painéis começam fechados e o Propriedades abre ao escolher Dividir/Cortar/Endireitar: como ele decidiu, nada a mudar. |
| Lista única 1.2, 5.9, 1.4, 1.5, 1.10, 1.11, 1.13, 3.2, 2.3, 2.6, 5.3, 5.6, 5.7 | (ver `relatorios/testes-guiados/lista-unica-2026-10-23/lista.md`) | Conferir o que as etapas anteriores já resolveram; fazer só o que falta, como o Livro decide. |

## Como cumpri cada uma

Provas em `tests/test_decisoes_9b2.py` (30 testes; todos passam aqui). **Reversão** no código antigo (`27b4c52`):
**25 falham lá, 5 passam** — os 5 são guardas de propósito (ver "Testes"). Prints da janela de verdade (1280×657 fora da
tela; a tela do PC está a 125%, os prints saem 1600×821) em `relatorios/obra-etapa9b2/prints/` (roteiro
`roteiro/prints.py`, cliques por mensagens do Windows; abri e olhei todos).

| Decisão / item | O que ficou no programa | Prova | Print |
|---|---|---|---|
| **D-558** | Botão **"dividir"** na faixa das escolhidas da grade. Divide as folhas das páginas escolhidas que saem como uma página só, pela MESMA conta do "dividir esta" (`core/dividir_a_mao.medir_para_dividir`: a folha girada como está, a tampa, a lombada pelo jeito da folha — o do ScanTailor de fábrica; as marcações à mão vão para a metade em que estão, D-528). Por trás (`ui/tarefas.TarefaDividirFolhas`), com a caixa "Dividindo as folhas escolhidas... 3 de 12" e "parar" (parar não muda nada). O livro muda numa ação só do desfazer; a grade volta com as páginas novas escolhidas. Folha já dividida fica como está. | `test_d558_*` (ScanTailor chamado nas 2 folhas, linha na lombada, só elas divididas, 1 ação, PDF com 6 páginas, Ctrl+Z junta) | `depois-03-grade-dividir.png`, `depois-04-grade-depois-de-dividir.png` |
| **D-559** | O Automático procura a tampa em **toda folha que ele olha** (a regra da etapa 4, que não pega moldura impressa: varredura das 2.903 folhas, `relatorios/obra-etapa4/varrer-tampa-acervo.json`) e mede o resto na folha já sem ela; a folha guarda a tampa na mesma ação do Automático. O que fazer com ela é a escolha do livro **"O que fica fora da página: cortar fora / pintar de branco"** (a mesma da D-092, `Projeto.borda_preta_fazer`; "cortar fora" de fábrica): pintar = a faixa sai branca (como na etapa 4); cortar = sai branca E a página é cortada na beirada da tampa (`dividir_a_mao.corte_sem_a_tampa`; o corte feito à mão vale como está). A escolha agora fica à vista no Automático também com a borda preta desmarcada (vale para as duas). | `test_d559_*` (3 folhas como o Righetti, Automático só com Endireitar: tampa nas 3, nenhuma faixa no PDF; "cortar" → página mais baixa; "pintar" → do tamanho da folha, faixa branca; Ctrl+Z tira; moldura impressa preta inteira; a escolha à vista). Os 3 testes da etapa 4 que provavam "pelo Automático a faixa fica" foram trocados para a regra nova (o Righetti 96 de verdade: 0 linhas pretas também pelo Automático). | `depois-14-righetti-girado-com-a-faixa-da-tampa.png` × `depois-15-righetti-pelo-automatico-sem-a-faixa.png`, `depois-12-automatico-cortar.png` |
| **D-547** | A página movida/redimensionada (ou numa folha escolhida, ou com margens iguais) aparece **como sai no PDF** (`TelaConferir._como_sai_no_pdf`: margens + `core.folha.compor_na_folha`, a mesma conta do PDF) no **lado a lado**, no **"antes / depois"**, na **tela cheia dos filtros**, nos **cartões do painel Filtro** e na **miniatura** dela. As ferramentas em que se marca, corta, divide ou endireita SOBRE a página continuam mostrando a página (D-546: a marcação e o corte são frações da página); o Mover já compunha. | `test_d547_*` (página a 60%: a caixa do texto no lado a lado, no antes/depois, na tela cheia e na miniatura é a do PDF, até 3%) | `depois-08-mover-60-por-cento.png`, `depois-09-lado-a-lado-com-a-pagina-movida.png` |
| **D-473 + D-064 (a troca da 10b)** | Quando o desenho do tamanho do PDF da página da vez termina (`GerenciadorPrevias.pedir_medida`), a imagem volta **reduzida** (INTER_AREA, no fio de fundo) e entra no lugar da prévia na chave da prévia, se a página não mudou; a tela redesenha (`pronta`). Duas **bolinhas** na barra de baixo: a **da página** gira enquanto a prévia não chegou ou a imagem do PDF está sendo feita ("Esta página: preparando a imagem igual ao PDF..."), a **do livro** gira enquanto o livro é medido por trás (D-284) ou as marcações são preparadas, com "Livro: 45% (90 de 200 folhas já carregadas)" no balão. Paradas, não aparecem. | `test_d473_d064_*` (bolinha gira com a frase; quando chega, a prévia da tela é a imagem do PDF; bolinha para) | `depois-10-...png` (a bolinha da página aparece ao lado de "página 11 de 182") |
| **D-568** | Com zoom, a roda **anda pela página** (Shift ou a roda de lado: para os lados), parando na beirada; sem zoom troca de página; Ctrl+roda dá zoom. Na Mão/marcar e nas ferramentas de página. | `test_d568_*` (Mão e Endireitar) | `depois-06-zoom-156-roda-andou-para-baixo.png` |
| **D-570** | O "– N% +", "ajustar à tela" e Ctrl+roda valem no "Duas lado a lado": 100% = o par inteiro na tela; acima, as páginas crescem (a da vez fica à vista; a roda rola, a barra de baixo vai para os lados). | `test_d570_*` (alturas × 1,25; Ctrl+roda; volta a 100%) | `depois-07-lado-a-lado-zoom-125.png` |
| **D-571** | Conferido: "100%" já era a página inteira cabendo na tela (encosta na largura ou na altura, com a moldura). Nada mudou. | `test_d571_*` | `depois-05-zoom-100-pagina-inteira.png` |
| **D-554** | Caixinha **"Margens iguais"** no "Para o livro todo" do Cortar: liga/desliga as margens iguais do LIVRO (o mesmo valor da etapa do Automático, que passa a mostrá-la), numa ação do desfazer; mostra o valor do livro sempre. | `test_d554_*` (Automático acompanha, Ctrl+Z, PDF com as páginas do mesmo tamanho) | `depois-01-cortar-margens-iguais.png`, `depois-02-...marcada.png` |
| **D-563** | Saiu a conta "só o bloco do texto" (`_so_o_bloco_do_texto`, `so_o_bloco`, os números) e os 2 testes dela; a caixa do conteúdo é a de sempre. | `test_d563_*` | — |
| **D-564** | Saiu `GRAVURA_ESCURA_EM_CINZA` e a conta (`_e_gravura_escura_ou_reticula`) e os 4 testes dela; ficou a prova de que o Palatino 74 sai em 1 bit. | `test_d564_*`, `test_decisoes_nucleo2.py::test_d564_palatino_74_continua_em_1_bit` | — |
| **D-020 / P-129 / lista 1.3, 4.6, 1.7** | Toda mudança da marcação (área nova, "Limpar tudo", "Deixar a folha em branco", procurar de novo, mexer numa área) vira **uma ação do Histórico** com a marcação de antes e de depois: o Ctrl+Z, o menu e o desfazer de baixo a tiram e o PDF sai sem ela. Antes ela ficava fora do Histórico, e o desfazer de baixo desfazia a ação ANTERIOR (no Righetti, o giro das 135 folhas: 1.7). O "desfazer" do painel Marcar usa o mesmo desfazer quando a última ação é a marcação da página. | `test_p129_*` (retângulo "pintar" branco sobre o texto: some no PDF; desfazer de baixo o tira, o giro fica, o texto volta; "Limpar tudo" + desfazer traz de volta); promessa P-129 sem "aguarda" | `depois-10-...png`, `depois-11-depois-do-desfazer-de-baixo.png` |
| **lista 1.6** | Toda ação de página e de folha guarda os **avisos de antes** (`alertas`, `alertas_aceitos`), e o desfazer os devolve como eram (nem some, nem vem um a mais). | `test_lista_1_6_*` | — |
| **lista 1.9** | A área feita **à mão** ganha o contorno cheio na cor do tipo, por cima do colorido: aparece mesmo dentro de uma área do mesmo tipo achada pela máquina. | `test_lista_1_9_*` (medida no desenho do editor) | `depois-10-retangulo-a-mao-dentro-da-area-da-maquina.png` |
| **D-090 / P-061 (Dividir)** | O "usar em todas" do Dividir abre **"Em quais páginas?" com as folhas** ("Folha 1"...; "Selecionar todas" / "Nenhuma"); a folha com a linha acertada à mão vem desmarcada ("linha própria") e fica com a dela; cancelar não muda nada. | `test_d090_usar_em_todas_do_dividir_*`; promessa P-061 sem "aguarda" | — (janela de exec: provado no teste) |
| **D-090 (Cortar / Bordas)** | Conferido: já não apagava a exceção (item 2.13). | `test_d090_usar_em_todas_do_cortar_*` (guarda) | — |
| **D-156 "só neste pedaço"** | Conferido: já valia no Preto e branco (conserto `60d8c58`) e sem "Limpar a folha" (etapa 1, D-009). Só a prova. | `test_d156_*` (guarda, nos dois casos) | — |
| **Bug 12/10 "letra e traço"** | A área marcada à mão como "letra e traço" protege a tinta do "Só as letras" (`core/misto._letra_a_mao`, passada a `_fora_do_texto`): não é apagada nem contada como "de fora". Sem essa marcação, nada muda. | `test_bug_12_10_*` (modos "Guardar só o texto" e rede: a nota fica; o resto da página igual) | — |
| **Bug 22/10 botões que piscam** | Os 3 botões do "Só as letras" e o "ver todas" das miniaturas não são mais mostrados antes de ter pai (viravam janelinhas soltas); os quadros da grade também não viram janela ao serem trocados. | `test_bug_22_10_*` (um vigia de janelas soltas) | — |
| **lista 1.2 + 5.9** | O aviso "Ficou escura" / "Texto quase sumiu" (medido no cartão Preto e branco, com o botão da força do preto) só fica na página que sai em **Preto e branco** (como `analise.analisar_resultado` já dizia); ali o "usar mais fraco" muda a força do preto. Nas páginas de Mágico pro e Melhorar ele sai. | `test_lista_1_2_e_5_9_*` | — |
| **lista 1.10** | A Tab da "próxima dúvida" vai à próxima dúvida mesmo com o foco num botão ou lista da área de trabalho (um filtro de teclas da aplicação pega a Tab antes de o Qt usá-la para mudar o foco). Shift+Tab e outra tecla escolhida: como sempre. | `test_lista_1_10_*` | — |
| **lista 1.11** | Esc na grade "Todas as páginas" volta ao trabalho (como o botão; no "escolher páginas..." do Automático, como "cancelar"). | `test_lista_1_11_*` | — |
| **lista 5.3** | A caixinha "Escurecer sozinho a força do preto quando o texto sair falhado" (Automático, Limpar) não fica mais **cinza e marcada**: fica acesa, dá para desmarcar (a frase embaixo continua dizendo que age com "Só as letras"). | `test_lista_5_3_*` | `depois-13-automatico-limpar.png` |
| **lista 1.4** | Já consertado na etapa 10a ("alargado nunca menor"). | (etapa 10a) | — |
| **lista 2.3** | Como ele decidiu (D-037 "tudo fechado", D-052 "Abre sozinho"; nomes no balão, R8 302): nada a mudar. | — | — |

## Testes (um arquivo por vez, no PC; TEMP e --basetemp em `_tmp/`)

- **Novo:** `tests/test_decisoes_9b2.py` **30 passaram**. Reversão (`relatorios/obra-etapa9b2/reversao-no-codigo-antigo.txt`):
  **25 falham no `27b4c52`, 5 passam** — os 5 são guardas: D-563 "a caixa de sempre", D-571 (só conferir), D-090 no
  Cortar e D-156 ×2 (já consertados antes desta etapa).
- **Rodados também (todos passando):** test_decisoes 26 · test_decisoes_automatico 24 · test_decisoes_avisos 13 ·
  test_decisoes_dividir 19 · test_decisoes_impressao 22 · test_decisoes_mover 13 · test_decisoes_nucleo 38 ·
  test_decisoes_nucleo2 21 · test_decisoes_tela 35 · test_decisoes_ver 11 · test_trabalho_nao_se_perde 82 ·
  test_etapa10a_nao_comer 8 · test_etapa10b_imagem 23 · test_promessas `-k "dividir or desfazer or
  retangulo or usar"` 22 (+1 xfail de outra promessa) · test_borda_preta 29 · test_dividir_no_programa 19 ·
  test_previa_composta 10 · test_misto_no_programa 41 · test_misto 31 · test_misto_consertos 25 ·
  test_misto_no_projeto 12 · test_filtros_tela_cheia 11 · test_paineis_na_tela 22 · test_historico_depois_de_reabrir 11 ·
  test_recomeco_limpa_o_historico 13 · test_zonas_na_folha 25 · test_so_neste_pedaco_no_original 22 ·
  test_girar_cartoes_e_previas 23 · test_alerta_pb 5 · test_corte_pelo_conteudo_na_tela 13 ·
  test_corte_pelo_conteudo_no_programa 16 · test_borda_preta_paginas_do_samuel 17 · test_livro_aberto 14 ·
  test_dividir_na_tela 9 · test_avisos 34 · test_revisar 28 · test_para_revisar_na_tela 25.
- **Testes antigos mudados (e por quê):**
  - `test_decisoes.py`: saíram as 2 provas da conta do D-493 (D-563 mandou tirar a conta).
  - `test_decisoes_nucleo2.py`: saíram os 4 testes da conta ligada do D-532 (D-564); o "Palatino 74 sai em 1 bit" ficou,
    renomeado para D-564.
  - `test_decisoes_ver.py`: o zoom com a roda e o zoom apagado no lado a lado (D-568 e D-570 trocam esses dois
    comportamentos; os testes agora provam o novo).
  - `test_decisoes_dividir.py`: os 3 testes da tampa que provavam "pelo Automático a faixa fica" agora provam que sai
    (D-559 substitui a D-495/D-499); nos sintéticos, a medida da faixa conta só linha preta de ponta a ponta (com o
    "cortar fora" a página fica justa e as linhas de "texto" de mentira entram no alto dela).
  - `test_girar_cartoes_e_previas.py`: o "usar em todas" do Dividir agora abre a lista; o teste da pendência D2 responde
    a lista (como já fazia no do Cortar).
  - `tests/promessas/promessas.md`: P-061 e P-129 sem "aguarda".

## GitHub e velocidade

(preenchido abaixo)

## Somas "Desligado de fábrica"

**96 de 96 somas iguais** (32 páginas do gabarito × Original / Preto e branco / Melhorar, livro novo de fábrica, a
imagem que vai ao escritor do PDF; `relatorios/obra-etapa10b/scripts/somas_da_imagem.py` com o código antigo
`27b4c52` e com o desta etapa: `somas-antes-27b4c52.json` × `somas-depois.json`). Nenhuma muda, e é o esperado: a tampa
só existe depois do Automático ou de dividir; a proteção de "letra e traço" só com essa marcação à mão; as duas contas
que saíram estavam desligadas. (Uma primeira rodada deu 49 diferentes porque a cópia do código antigo estava sem a
junção `modelos` — o detector de gravura não carregava; com a junção, 96 de 96.)

## Ressalvas (escritas, não escondidas)

1. **D-559 só no Automático e no dividir:** um livro que nunca passa pelo Automático (nem é dividido à mão ou pela
   grade) continua com a faixa, porque a medida por trás ao abrir só põe avisos (D-483) e "a página sempre abre em
   Original, sem mexer" (D-134). Pergunta 1.
2. **D-559 "cortar fora" é de fábrica** (é o de fábrica da escolha da D-092): as folhas que a etapa 4 só pintava agora
   também são cortadas na beirada da tampa. A escolha muda pelo Automático (etapa Cortar): para trocar só ela é
   preciso rodar a etapa Cortar.
3. **D-547 não vale nas ferramentas em que se mexe sobre a página** (Marcar, Cortar, Dividir, Endireitar): lá a página
   aparece sem o mover (D-546). A miniatura só mostra a página movida depois de a prévia dela ter sido desenhada (a
   página que foi visitada; a que foi movida pelo "usar em todas" e nunca aberta continua crua na tira).
4. **A troca da tela pela imagem do PDF (D-473)** só acontece nas páginas em que a tela já pedia o desenho do tamanho
   do PDF (a regra do "Para revisar" do "Só as letras", e o acerto da marcação provisória sem filtro não traz
   imagem). Nas outras, a prévia já sai da mesma conta (etapa 10b). A tela cheia dos filtros não pede o desenho do PDF.
5. **A roda do mouse de verdade** não chega a uma janela fora da tela (como na etapa 6): o print 06 usou um evento de
   roda do Qt mandado à página (o mesmo caminho da roda).
6. **A grade com "dividir"** precisou de menos folga dos lados nos botões da faixa para nada ficar cortado a 1280.
7. **O desfazer da marcação**: cada área marcada é uma ação do Histórico (o Histórico fica mais comprido quando se
   marca muito). O desfazer próprio do editor de marcar continua só para o "desfazer" do painel Marcar quando a última
   ação não é desta página.
8. **1.10 (Tab):** a Tab não passa mais o foco entre os botões da área de trabalho (é a tecla da "próxima dúvida",
   como a lista de atalhos manda); com outra tecla escolhida nas Configurações, a Tab volta a passar o foco.

## O que não fiz (e por quê)

- **Lista 1.5** ("Confirmar e processar" às vezes não abre; "a conferir", provável jeito de pilotar a janela): é da
  `ui/janela_confirmar.py`/`janela_principal.py`, da etapa 9b-1. Não mexi.
- **Lista 1.13** (a tela vazia ou "Preparando a prévia..." uns segundos): a bolinha da página agora mostra que está
  carregando; deixar mais rápido é da fase de desempenho.
- **Lista 3.2** (girar vendo a página inteira) e **2.6** (a Luz no Original; a "Área" no fim do Propriedades): o Livro
  não decide como; perguntas 2 e 3.
- **Lista 5.6 e 5.7** (o número de dúvidas que muda ao folhear; avisos demais): são a regra do "Para revisar" (D-254,
  D-295, D-296, D-474: "Etapa 9 (avisos demais/falsos)"), conta do núcleo com medida no acervo; não cabem nesta etapa
  da área de trabalho sem mexer no que outros agentes fazem. A etapa 7 já juntou o número (um só em todo lugar).
  Para a gerente.
- **"Recuperar o trabalho anterior"** no menu do cartão: está na Lista de espera (29/09, ideia de agente, "a
  definir"), não é decisão do Samuel no Livro. Pergunta 4.
- **D-555** (nome com acento) e **D-492** (o tique do menu Filtro): são de arquivos da 9b-1.

## Perguntas para o Samuel (com recomendação; nenhuma trava a etapa)

1. **Tampa do scanner em livro que não passa pelo Automático:** hoje ela some quando o Automático roda (qualquer
   etapa que olhe as páginas), ao dividir à mão e no "dividir" da grade. Quer que suma também ao só abrir o livro?
   *Recomendo não: abrir não muda página nenhuma (D-134, D-483); rodar o Automático já tira.*
2. **Lista 3.2, "girar vendo a página inteira, como no Photoshop":** para isso o Endireitar teria de mostrar a página
   ainda sem corte nem filtro, girando inteira (a parte de fora aparece). Hoje mostra a página como sai (cortada e
   com o filtro), e o que gira para fora do retângulo sai também do PDF. *Recomendo: no Endireitar, mostrar a página
   inteira girando, só enquanto se gira; ao soltar, volta a mostrar como sai. Precisa do "sim" dele (muda o que a
   ferramenta mostra).*
3. **Lista 2.6:** "Igualar a luz" também no Original (D-195 disse "Em todos" — os filtros que limpam?) e a "Área" mais
   para cima no Propriedades? *Recomendo deixar a Luz só nos três filtros que limpam (o Original é "como veio") e
   levar a ordem do Propriedades à revisão do layout.*
4. **"Recuperar o trabalho anterior"** no menu do cartão do livro (listar as cópias guardadas antes de recomeçar):
   *recomendo sim, numa etapa futura; hoje as cópias ficam guardadas e o aviso diz onde.*
5. **D-559, uma escolha só para borda preta e tampa:** usei a mesma "O que fica fora da página" (D-092) para as duas.
   *Recomendo manter uma só.*

## Ideias para a Lista de espera

- Mostrar também na tira as páginas movidas que nunca foram abertas (hoje só depois da prévia).

## Bugs para a Lista de bugs (achados, não consertados)

- 28/10: `tests/test_para_revisar_na_tela.py::test_a_janela_lista_as_paginas_e_os_motivos` falhou uma vez no PC com
  outros testes rodando juntos; sozinho e no arquivo inteiro de novo, passa (a `ui/janela_dos_avisos.py` não foi
  mexida nesta etapa).

## Commits (ramo `obra-etapa9b2-2026-10-26`, com push)

(ver `git log 27b4c52..`)
