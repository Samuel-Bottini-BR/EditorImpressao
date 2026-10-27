# Obra de 26/10/2026 — etapa 4 (dividir à mão folha por folha): ONDE PAREI

Ramo `obra-etapa4-2026-10-26` (base `obra-2026-10-26` = `427e3ae`, com as etapas 1, 2, 3, 9a, 9c, 10a e a bateria de
promessas), worktree `.claude/worktrees/obra-etapa4`. Agente: layout + implementador. Ordem do Samuel (D-014): fazer até
o fim sem pausas; ele confere tudo no fim.

**Situação: PRONTO PARA CONFERIR** (começada e terminada em 27/10/2026). Ramo enviado ao GitHub.

## Em uma frase

Agora o Kaique pode dividir (ou deixar de dividir) qualquer folha à mão, a qualquer hora — inclusive o Righetti depois de
girado —, sem perder o que fez nas outras páginas; o livro dividido aparece uma página por vez (a folha inteira com a
linha só dentro do Dividir); a faixa preta da tampa do scanner sai quando ele divide ou acerta a linha à mão; e o
ScanTailor não corta mais o "La vida eterna" na linha escura da beirada.

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| Pedido da etapa 4 (sessão 1, 26/10, print `s1-10`) | "quando a tela está assim no dividir, é bom para mudar folhas que sairam erradas, eu posso entrar ali e mudar a marcação de folhas erradas, mas quando eu escolher para começar no automatico e dividir as folhas o livro tem que aparecer em uma pagina por vez para mim." | "dividir esta" sempre aceso (livro sem "Dividir", folha girada); dividir, não dividir e mover a linha mexem só nas páginas daquela folha, sem recomeçar e sem perder o feito nas outras; marca "mexida à mão". Promessa P-059. |
| D-007 (26/10) | a mesma frase acima | A folha inteira com a linha só dentro da ferramenta Dividir (para consertar); fora dela, livro dividido aparece uma página por vez. |
| D-080 (05/10) | G2: "(a) Só quando o Kaique pedir, livro a livro, [...] e trocando numa folha se um ficar ruim" | Livro novo não divide; dividir à mão numa folha. |
| D-074 (24/09) | (paráfrase) dividir a folha sabendo quando é uma página só; bug "Righetti não girado nem dividido" (PD l.400) | O Righetti girado divide. |
| Lista única 3.1 (23/10) | "Não dá para girar o livro antes de dividir: livro escaneado de lado não divide" | Girar e então dividir, no Automático e à mão; a lombada achada na folha girada. Prova no Righetti. |
| D-495 (27/10, escolha da gerente) | "Righetti 96: a faixa preta da tampa do scanner sai quando a folha é girada e dividida à mão (dividir à mão, etapa 4), não por regra geral." | Righetti 96 girada e dividida à mão → sem faixa preta em cima no PDF; moldura impressa preta não some. |
| Bug da etapa 9c (27/10) | "Dividir do ScanTailor erra no 'La vida eterna' (folhas 4 e 5): divide a 10% da largura, na linha vertical escura da beirada" | A linha escura da beirada não é lombada. Teste de reversão. |
| D-016 (09/10) | `g6-endireitar-antes` + "Ordem obrigatória" | A página dividida à mão é montada na ordem obrigatória. |
| D-334 (24/09) | "Ver todas as páginas do livro em grade [...]: seleção múltipla, girar, apagar, extrair, inserir, dividir." | A grade continua; dividir em várias (ver pergunta 3). |
| D-488 / D-489 (27/10) | (escolhas da gerente) a tela "O que fazer" fora do caminho; recomeço só quando o PDF muda, o projeto.json não lê ou falta página | Dividir/não dividir à mão nunca recomeça; toda folha continua com página. |
| D-004 / D-009 | "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas mexidas." · "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo manualmente." | A divisão à mão grava a marca e vale no PDF com o Dividir do livro desligado. |
| D-046 | dois botões ("Deixar em branco" / "Tirar do livro") | Página tirada ou em branco não volta sozinha ao dividir/juntar. |

## Como cumpri cada uma

| Decisão | O que ficou no programa | Prova (teste; `tests/test_decisoes_dividir.py` salvo dito) | Print |
|---|---|---|---|
| Pedido da etapa 4 / P-059 | "dividir esta" fica aceso em toda folha. Na folha de uma página só ele acha a lombada na hora (na folha como ela está, girada se foi girada) e parte a página em duas; só as páginas DESSA folha mudam na lista (as outras são os mesmos objetos, renumerados), numa ação leve do desfazer (`historico_acoes`: `paginas_da_folha:<n>`). Grava a marca "mexida à mão". O aviso "Não parece dupla" ("não dividir esta") nunca divide. | `test_dividir_esta_aceso_no_livro_sem_dividir_e_mexe_so_nesta_folha` (filtro, corte e "está certo" das outras iguais; Histórico com +1; PDF com 4 páginas; Ctrl+Z), `test_o_aviso_nao_parece_dupla_nunca_divide`; promessa P-059 (sem "aguarda"), P-060, P-112 | `antes-03-dividir-esta-cinza.png` × `depois-06/07` |
| "não dividir" / "dividir de novo" | "não dividir esta" junta as duas páginas numa só (a direita não fica mais "apagada" na lista) e as guarda na folha; "dividir esta" devolve as duas como estavam (corte, "tirar do livro"), na linha de antes. D-498. | `test_nao_dividir_e_dividir_de_novo_devolvem_as_paginas_como_estavam`; `tests/test_dividir_na_tela.py` (2 testes reescritos: provam que o antigo saiu) | `depois-05`, `-06`, `-07` |
| Mover a linha | Só a folha da linha muda; marca "mexida à mão". | `test_mover_a_linha_mexe_so_nesta_folha` | — |
| D-489 | Toda folha continua com página; reabrir traz a divisão à mão e o Histórico, sem recomeço. | `test_d489_a_divisao_a_mao_volta_ao_reabrir_sem_recomecar` | — |
| D-007 | O livro nunca abre no Dividir; rodar o Automático com "Dividir" estando no Dividir leva à página (uma por vez); "ver" num aviso de folha só leva ao Dividir quando o aviso é da divisão. O Dividir continua a um clique (trilha, tecla D) para consertar. A tela fica na mesma folha quando a lista de páginas muda. D-501. | `test_d007_dividido_pelo_automatico_aparece_uma_pagina_por_vez`, `test_d007_livro_dividido_nunca_abre_no_dividir` (os dois provam que o antigo saiu) | `depois-04-dividido-uma-pagina-por-vez.png`, `depois-08`, `depois-09` |
| Lista única 3.1 / D-074 | Girar e "dividir esta": a lombada é achada na folha girada. No Automático (girar todas, rodar Dividir) já funcionava desde a etapa 3 — provado no Righetti de verdade (dobra a 0,58). | `test_lista_3_1_girar_a_folha_e_dividir_a_mao`, `test_lista_3_1_girar_o_livro_e_dividir_no_automatico`, `test_lista_3_1_righetti_de_verdade_girado_e_dividido` | `depois-01` a `-04` (135 de 135 folhas divididas) |
| D-495 | Ao dividir à mão (ou acertar a linha à mão) a tampa do scanner é procurada uma vez por rotação; o que fica de fora sai **branco**, na etapa "dividir" (antes de endireitar e cortar). O Automático nunca tira (não é regra geral). Regra em D-499. | `test_d495_a_regra_da_tampa_na_folha_e_na_moldura`, `test_d495_a_faixa_da_tampa_sai_ao_girar_e_dividir_a_mao` (à mão sai, pelo Automático fica), `test_d495_acertar_a_linha_a_mao_tambem_tira_a_tampa`, `test_d495_a_moldura_impressa_preta_nao_some_ao_dividir_a_mao`, `test_d495_righetti_96_de_verdade` (Automático: >60 linhas pretas em cima; à mão: 0) | `depois-08-pagina-da-folha-96-sem-a-faixa.png` × `depois-09-pagina-da-folha-95-pelo-automatico.png` |
| Moldura impressa não some | A regra só pega faixa neutra de 8 mm ou mais que atravessa 97% da folha inteira (em cima/embaixo) ou começa na beirada da imagem (dos lados). Varredura de todo o acervo (2.903 folhas, só lido): nenhuma folha do Horas, Palatino, Siebmacher, Pesel, Escola, Rhetorica e Boécio tem tampa achada; as achadas (Antiphon, Cursus, Matemática, ljs47, Righetti, 2 do Graduale, 1 do Marial) são todas o fundo preto do scanner (olhei as figuras). `relatorios/obra-etapa4/varrer-tampa-acervo.json`. | `test_d495_a_moldura_impressa_preta_nao_some_ao_dividir_a_mao` | — |
| Bug da 9c | `core/dividir_scantailor.na_beirada`: o corte de duas páginas fora de 20% a 80% da largura (a regra do próprio ScanTailor para as linhas) não é lombada → vale a conta do Editor e a folha vai para "Lombada incerta". D-500. | `test_bug_9c_a_linha_escura_da_beirada_nao_e_lombada` (sintético, sem o livro), `test_bug_9c_la_vida_eterna_folhas_4_e_5_de_verdade`, `test_bug_9c_la_vida_eterna_a_analise_ja_nao_faz_a_tira_de_margem` | — |
| D-016 | A divisão à mão passa pelo mesmo `preparar_para_recorte` (girar → tampa → dividir → endireitar → cortar). | `test_d016_dividida_a_mao_sai_igual_a_dividida_pelo_automatico` (com Endireitar e Cortar: páginas iguais ponto a ponto) | — |
| D-004 / D-009 | A marca vem do `_registrar` da tela; a página dividida à mão sai no PDF com o Dividir do livro desligado. | `test_dividir_esta_aceso_...` | — |
| D-046 | "tirar do livro" de uma metade volta com "dividir esta"; juntar só tira a folha do livro se as duas estavam tiradas. | `test_nao_dividir_e_dividir_de_novo_...`, `tests/test_dividir_na_tela.py::test_esquerda_apagada_e_nao_dividir_a_folha_continua_no_pdf` | — |
| D-334 / D-488 | Nada novo na grade; nada leva à tela "O que fazer". | (os testes da etapa 3 continuam passando) | — |

## Causa de cada defeito

1. **"dividir esta" cinza (P-059, lista 3.1):** a lista de páginas não podia mudar na conferência (o desfazer guardava
   páginas pela posição); por isso a folha que entrou como uma página só não tinha "metade" para criar e o botão
   ficava cinza. Conserto: uma ação que troca só as páginas daquela folha (`core/dividir_a_mao.py`,
   `historico_acoes.PREFIXO_PAGINAS_DA_FOLHA`); o desfazer em pilha mantém as ações mais velhas certas.
2. **D-007:** `TelaConferir._aba_de_partida` abria no Dividir sempre que o livro tinha "Dividir"; e rodar o Automático
   não tirava a tela do Dividir.
3. **Bug da 9c:** o ScanTailor tira do meio as linhas perto da beirada (BadTwoPageSplitter), mas não o corte que ele
   acha no espaço em branco (cutAtWhitespace): no "La vida eterna" a linha escura da beirada deixa uma faixa branca a
   10% da largura, e ele cortou ali. Reproduzido numa folha sintética (o teste não depende do livro).
4. **Faixa da tampa (D-495):** o corte de sempre e o "só o preto" andam da beirada para dentro e param na tira clara da
   tampa, antes da faixa preta.

## O que mudou (por arquivo)

- `core/dividir_a_mao.py` (novo): dividir/juntar uma folha (campos da ação), metades guardadas, a página partida (a
  mesma conta do Automático), a tampa do scanner (achar, medir, pintar).
- `historico_acoes.py`: campo `paginas_da_folha:<n>` (aplicar e fotografar o "antes").
- `modelos.py`: `ConfigFolha.metades_guardadas`, `ConfigFolha.tampa_do_scanner` (projeto antigo: None, sai igual).
- `core/pipeline.py`: `achar_divisao` com a regra da beirada; `preparar_para_recorte` pinta a tampa; as chaves das
  contas guardadas ganham a tampa **só quando ela existe** (as contas já guardadas no disco continuam valendo).
- `core/dividir_scantailor.py`: `na_beirada`, `BEIRADA_DA_FOLHA`.
- `core/automatico.py`: `_dividir` usa `metades_da_pagina` e esquece as metades guardadas.
- `ui/tela_conferir.py`: "dividir esta" sempre aceso, `_dividir_esta`, `_nao_dividir`, `_mover_corte` com a tampa,
  `_registrar` que remonta a tira quando a lista muda, `lista_de_paginas_mudou` na mesma folha, `_aba_de_partida`,
  `mostrar_paginas`, `_ir_para_o_aviso`.
- `ui/janela_principal.py`: depois do Automático com Dividir, `mostrar_paginas()`. `ui/tarefas.py`: chave das prévias.
- Testes: `tests/test_decisoes_dividir.py` (novo, 19), `tests/test_dividir_na_tela.py` (2 reescritos),
  `tests/test_decisoes_nucleo.py` (o teste do "La vida eterna" do 9c simula o ScanTailor de antes, ver abaixo),
  `tests/test_trabalho_nao_se_perde.py` (1 comparação sem a nota interna `geometria_das_zonas`, ver abaixo),
  `tests/promessas/promessas.md` (P-059 sem "aguarda"; P-060).
- `docs/plano/DECISOES.md`: D-498 a D-501; situação de D-007, D-495 e D-074.

## Testes (no PC, um arquivo por vez, TEMP e --basetemp em `_tmp/`)

- `tests/test_decisoes_dividir.py`: **19 passaram**. **Reversão** no código antigo (`427e3ae`, cópia em `_tmp/antigo`):
  **15 falham, 4 passam** (`relatorios/obra-etapa4/reversao-no-codigo-antigo.txt`). Os 4 que passam lá são guardas:
  mover a linha só numa folha, o aviso que nunca divide, e o Righetti girado + Dividir **no Automático** (já funcionava
  desde a etapa 3; a lista 3.1 travava na tela "O que fazer", que saiu). Dos 15, 13 falham por asserção; 2 (a regra da
  tampa e o Righetti sintético) falham porque o módulo/campo não existe lá.
- `test_decisoes.py` 23 · `test_decisoes_automatico.py` 24 · `test_decisoes_impressao.py` 22 · `test_decisoes_nucleo.py`
  36 · `test_decisoes_tela.py` 35 · `test_dividir_no_programa.py` 19 · `test_dividir_na_tela.py` 9 ·
  `test_dividir_scantailor.py` 11 (+2 pulados) · `test_girar.py` 53 · `test_girar_na_tela.py` 22 ·
  `test_girar_cartoes_e_previas.py` 23 · `test_paineis_na_tela.py` 22 · `test_recomeco_limpa_o_historico.py` 13 ·
  `test_historico_depois_de_reabrir.py` 11 · `test_core.py` 62 · `test_ordem_do_preparo.py` 56 ·
  `test_zonas_na_folha.py` 25 · `test_mesmo_livro_outro_caminho.py` 17 · `test_trocar_de_livro_grava.py` 6 ·
  `test_trabalho_nao_se_perde.py` 82 · `test_desentortar_protecao.py` 15 · `test_borda_preta.py` 29 ·
  `test_opcoes_da_gravura_na_tela.py` 15: **todos passam**.
- `test_promessas.py -k "dividir or p05 or p06 or p112"`: 38 passaram, 1 xfail (P-061 "usar em todas", etapa 9).
- `test_desentortar_conferir_de_novo.py`: 13 passam, **1 falha que já falhava no código antigo**
  (`test_destino_do_socialismo_18_...`, conferido no `427e3ae`): não é desta etapa.
- `teste_botoes.py`: **312 ações, 0 falhas**.

### Três testes antigos mudados (e por quê)

- `test_opcoes_da_gravura_na_tela.py::test_mudar_as_opcoes_num_livro_com_trabalho_refaz_so_a_gravura_automatica`
  (achado no GitHub): com a D-007 o livro dividido abre na página e a prévia dela ainda estava sendo desenhada quando o
  teste punha marcações "por fora" (sem a geometria anotada); o desenho as levava para o lugar da página. Conferi que
  com o `_aba_de_partida` antigo ele passa. O teste agora vai para o Dividir (como abria antes) e espera a prévia
  terminar antes de marcar; o que ele protege (as opções da gravura) não mudou. 15 passam, 3 vezes seguidas.

- `test_decisoes_nucleo.py::test_la_vida_eterna_pagina_7_...` (etapa 9c) começava da análise de fábrica que dava "Parece
  em branco" nas páginas 2, 7 e 9 — justamente por causa do bug do ScanTailor consertado aqui. Para continuar provando
  o que protege (o aviso sai quando a divisão muda), a análise dele simula o ScanTailor de antes (`na_beirada` sempre
  False). O efeito do conserto no caminho inteiro tem prova própria (`test_bug_9c_la_vida_eterna_a_analise_...`).
- `test_trabalho_nao_se_perde.py::test_projeto_antigo_nao_esc_e_x_nao_mudam_nada` comparava as páginas inteiras do
  projeto.json. Com a D-007 o livro abre numa página (não mais no Dividir), e desenhar a página regrava a nota interna
  `geometria_das_zonas` (onde a página foi medida; sem marcação nenhuma). Conferi que a diferença era só essa (com o
  `_aba_de_partida` antigo o teste passa). A comparação agora deixa essa nota de fora; o resto (filtro, corte, "está
  certo"...) continua comparado.

## GitHub

**40547713739** (a final; código `HEAD` do ramo): **suíte partes 2, 3, 4 e 5 passam inteiras; parte 1 com 2 falhas
que já falham no ramo-base** (P-085 tique do menu Filtro, D-492, etapa 9b; P-127 "Antes de processar" pelo menu,
defeito C) — a rodada do `obra-2026-10-26` (40537146001) tinha 4 falhas nesse arquivo (essas duas + P-090 e P-094).
**`teste_botoes.py` passou** no GitHub; o passo seguinte do mesmo trabalho, "Prints da janela real", quebra no script
do próprio fluxo (`.github/scripts/fotografar_janela.py` ainda usa `janela.tela_opcoes`, que a etapa 3 tirou) — quebra
igual na rodada do ramo-base: **troca para a gerente** (atualizar o script do fluxo, no ramo
`claude/list-server-files-gkos8v`).

A primeira rodada (40544282462) achou um teste antigo que a D-007 mexeu (`test_opcoes_da_gravura_na_tela`, ver
"Testes antigos mudados") e um ERRO de arrumação no P-177 (uma prévia abrindo o PDF de um teste que já tinha sido
apagado; não voltou na rodada final).

## Somas "Desligado de fábrica" (32 páginas do gabarito × Original/Preto e branco/Melhorar, livro novo, `processar`)

**96 de 96 somas iguais** entre o código antigo (`427e3ae`) e o novo (`relatorios/obra-etapa4/somas-antes-427e3ae.json`
× `somas-depois.json`; script `relatorios/obra-etapa4/scripts/somas.sh`, o mesmo das etapas 1 e 10a, lendo o
gabarito da pasta principal). Nenhuma muda: o livro novo não divide sozinho, a tampa só existe depois de dividir à
mão, e a regra da beirada só age quando o ScanTailor corta fora de 20%–80%.

## Prints da janela de verdade (1600×821, fora da tela; `relatorios/obra-etapa4/prints/`)

Roteiro `relatorios/obra-etapa4/roteiro/prints.py` (cliques e teclas por mensagens do Windows; a base é a da etapa 3),
caminho do Kaique do zero, sem caixinha marcada: abrir o Righetti (cópia) → "aplicar em: todas as folhas" + "¼ à
esquerda" → Automático só com "Dividir" (clique na caixinha) → Rodar → a página → tecla D → folha 96 → "não dividir
esta" → "dividir esta" → Mão → a página.

- **Antes (código `427e3ae`, 4 de 4 conferências):** `antes-00` a `antes-02`, e `antes-03-dividir-esta-cinza.png`: na
  folha 96 girada, "dividir esta" cinza e "Esta folha não vai ser dividida".
- **Depois (12 de 12 conferências):** `depois-00` tela dos livros; `-01` o Righetti aberto de lado, nada marcado;
  `-02` girado, todas as folhas; `-03` o Automático só com "Dividir"; `-04` depois de Rodar: **página 192 de 270, uma
  por vez** (135 de 135 folhas divididas; a faixa preta da tampa continua: o Automático não a tira); `-05` o Dividir na
  folha 96 (a folha inteira com a linha, "não dividir esta" aceso); `-06` depois de "não dividir esta" (uma página só,
  "dividir esta" aceso); `-07` dividida à mão de novo; `-08` **a página 192 sem a faixa preta** (D-495); `-09` a
  página 190 (folha 95, dividida pelo Automático) com a faixa, para comparar.
- Abri e olhei todos. Ressalva vista no `-08`: a trilha da esquerda ainda pinta o Dividir aceso, embora a ferramenta
  já seja a Mão (título "Mão"; no `-09` a trilha já mostra a Mão). Conferi o estado: `trilha.ferramenta == "mao"` logo
  depois do clique. Parece só o momento do print (a trilha não tinha sido repintada); não consegui repetir com o Qt.

## Escolhas da gerente (D-014) feitas aqui — no Livro como D-498 a D-501

| Nº | Escolha |
|---|---|
| D-498 | "não dividir esta" junta as duas páginas numa só e as guarda; "dividir esta" devolve as duas como estavam. A página partida herda filtro e ajustes, não corte/ângulo/marcação/mover (como o Automático). |
| D-499 | A tampa do scanner: procurada só ao dividir à mão ou acertar a linha à mão, uma vez por rotação; faixa neutra ≥ 8 mm cobrindo 97% da folha inteira (em cima/embaixo, depois de uma tira clara de até 15%) ou começando na beirada (dos lados, 85% da altura); sai branca, na etapa "dividir"; o Automático nunca tira. |
| D-500 | O corte de duas páginas do ScanTailor fora de 20%–80% não é lombada: vale a conta do Editor e a folha vai para "Lombada incerta". |
| D-501 | Como a D-007 fica na tela: nunca abre no Dividir; o Automático com "Dividir" leva à página; aviso de folha só leva ao Dividir quando é da divisão. |

## Ressalvas

1. **Marcações feitas na folha inteira não passam para as metades** quando ela é dividida pela primeira vez (as metades
   começam sem marcação, como no Automático da etapa 3). Ao juntar e dividir de novo, as marcações das metades voltam.
   Ver pergunta 1.
2. **A tampa é pintada de branco, não cortada:** sem o "Cortar" ligado, a página do Righetti sai com uma margem branca
   alta em cima (onde era a tampa). Com o "Cortar" do Automático, o corte de sempre tira esse branco.
3. **No Righetti a tampa achada é só a de cima** (o fundo preto da esquerda tem, na beirada da imagem, uma coluna mais
   clara e não entra na regra "começa na beirada"). Nas páginas da esquerda sobra esse fundo preto do lado de fora;
   o "Cortar" do Automático o tira (como já tirava).
4. **A tampa não é procurada pelo Automático** (D-495: "não por regra geral"). Num livro como o Righetti, o Kaique que
   divide pelo Automático continua vendo a faixa, até acertar a linha ou dividir à mão cada folha. Ver pergunta 2.
5. **Dividir à mão abre a folha no PDF** (uns décimos de segundo, com o cursor de espera), como a troca de "jeito" já
   fazia; acertar a linha faz isso só na primeira vez em cada rotação.
6. **"Dividir" na grade com várias escolhidas (D-334)** continua sendo "rodar o automático nelas" com "Dividir"; não
   pus um botão "dividir" direto na grade (dividir à mão 135 folhas de uma vez travaria a janela uns 30 s). Ver
   pergunta 3.
7. **Folha de projeto antigo "não dividida" com as duas páginas na lista** (o jeito de antes, a direita "apagada"):
   "dividir esta" a devolve como antes; "não dividir esta" (ou o aviso "Não parece dupla") a junta numa página só.
8. **Velocidade:** não medi (a medida da regra 6 é a do filtro do GitHub, pela gerente). O que entra a mais no caminho
   de sempre: nada (sem tampa, `pintar_a_tampa` devolve a mesma imagem; a regra da beirada é uma comparação). Abrir a
   folha só acontece no clique de "dividir esta" e no primeiro acerto de linha.

## Perguntas para o Samuel (com recomendação; nenhuma trava a etapa)

1. **Marcações ao dividir à mão:** as marcações (gravura, "só neste pedaço"...) feitas na folha inteira devem ir para a
   metade onde estão? Hoje elas não passam (como no Automático). *Recomendo sim: levar cada marcação para a página em
   que ela está.*
2. **Tampa do scanner pelo Automático:** a D-495 diz "não por regra geral". Quer, num livro como o Righetti, uma opção
   no Automático ("Tirar a faixa da tampa do scanner", desligada de fábrica) com a mesma regra? *Recomendo esperar ver
   os prints `depois-08` e `depois-09` e decidir com eles; a regra não pegou moldura nenhuma nas 2.903 folhas do
   acervo.*
3. **"Dividir" na grade (D-334):** basta "rodar o automático nelas" com "Dividir", ou quer um botão "dividir" à mão na
   grade (com andamento, por trás)? *Recomendo o botão com andamento, numa etapa futura.*

## Trocas que outra área precisa

- **Etapa 6 (lado a lado, D-006/D-015):** a página da vez agora fica na mesma folha quando a lista muda
  (`lista_de_paginas_mudou`); quem fizer o "Ver lado a lado" deve usar o mesmo cuidado.
- **Etapa 7 (avisos, D-497):** dividir à mão uma folha cria as duas páginas sem avisos (`alertas` vazios); o "Parece em
  branco" de uma metade só aparece se a etapa 7 medir de novo depois de mudar a divisão (é a D-497).
- **Etapa 10b (filtros):** não mexi em `core/filtros.py` nem `core/camadas.py`.

## Commits (ramo `obra-etapa4-2026-10-26`)

- `081f1bf` ONDE-PAREI com as decisões que a tarefa precisa cumprir
- `4d521de` dividir à mão folha por folha (núcleo e tela), linha da beirada não é lombada, tampa do scanner, D-007
- `0ea7701` provas das decisões; P-059 sem "aguarda"; tampa só com faixa de 8 mm ou mais
- `ee9f327` a tampa também ao acertar a linha à mão; prova do "La vida eterna" no caminho da análise; D-498 a D-501
- `c66aa9f` test_trabalho_nao_se_perde sem a nota interna geometria_das_zonas
- `a256853` test_opcoes_da_gravura_na_tela espera a prévia; evidências (varredura, reversão, prints)
- (este ONDE-PAREI final, com as somas)
