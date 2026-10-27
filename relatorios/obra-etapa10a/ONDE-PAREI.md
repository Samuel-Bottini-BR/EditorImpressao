# ONDE-PAREI — obra de 26/10/2026, etapa 10a: defeitos de geometria na imagem final

Implementador · ramo `obra-etapa10a-2026-10-26` (base `obra-2026-10-26` `11f9ed3`, com a etapa 1) · worktree
`.claude/worktrees/obra-etapa10a` · worktree de apoio (código antigo, só leitura, para o teste de reversão):
`.claude/worktrees/obra-etapa10a-antes` (`11f9ed3`, solta, com as junções `modelos` e `gabarito\paginas`).
Obra D-014: feita até o fim sem pausas; o Samuel confere tudo no fim.

## Decisões que esta tarefa precisa cumprir (do Livro, `docs/plano/DECISOES.md`, e do pedido da gerente)

- **D-104 / D-466 — os "8 lugares que podem comer a página"** (22/10/2026, `a-comer-pagina`): "Tem mais alguma função
  que pode fazer essa mesma coisa de comer parte da pagina sem que a gente queira no nosso programa?" → "B — Só o
  desentortar agora; o resto para o começo da próxima fase" + "escolhi a B, mas quando for feito o teste de bug, ele
  tem que fazer a C — Primeiro provar em páginas de verdade, depois decidir". (PD l.401-408.)
- **D-077** (28/09/2026): "não comer conteúdo" → o corte automático nunca corta tinta; se encostar, avisa.
- **D-097** (13/10 a 21/10/2026): "tem que ficar rente a folha de papel, não pode ter preto ali." (Cursus 3) · "É para
  sumir totalmente." · `pr-cursus-3`: "Está bom" → não pode voltar.
- **D-098** (13/10, `g8-moldura-tinta-fora`): "Só avisa" + "ele avisa e da opção e de mudar o corte e mostrar ele
  alargado com o que foi tirado." (lista única 1.4: o alargado deixou a página menor).
- **Lista única 4.2** texto comido (Matemática 66 e 40, Cursus 3); **4.4** "o corte tirou o lado esquerdo da moldura e
  deixou sobra branca do lado direito" (Horas 18); **4.8** "cada página sai de um tamanho e sem margem" (ljs47,
  Graduale); **4.10** "A sombra da lombada não é cortada" (Boécio 2, Siebmacher 74 e 86).
- **D-113 / `d212-1`** (23/10/2026): "o primeiro passo em uma pagina dessas seria tirar essa moldura preta
  transformando a pagina em totalmente branca sem mexer nas letras, ai o desentortador não iria confundir as letras
  com moldura preta. não é?"
- **D-095 — ressalvas do G6** (12/10/2026): moldura colada em cima (Siebmacher 9), título colado (Escola 7), cunhas
  brancas com corte até a beirada (Boécio 8, Marial 7, Graduale 221).
- **Escola 197** (Lista de bugs 13/10): "o corte come os números 1, 2 e 3 dos itens, na margem esquerda".
- **D-016**: "a montagem da página segue sempre a ordem obrigatória (endireita, depois corta uma vez só, no fim)".
- **D-473**: "Tela e PDF saem da mesma conta." **D-017**: aumentar "não corta nada escondido". **D-014**: obra sem pausas.
- **Regras de teste:** nada de lombada/capa (21/10); comer página se prova primeiro em páginas de verdade; caminho
  inteiro (CLAUDE.md §4.10); teste de reversão (§4.7); somas de fábrica.

## Situação

**PRONTO PARA CONFERIR** (27/10/2026, madrugada). Conferência: `relatorios/obra-etapa10a/conferencia/
conferencia-etapa10a.html` (também .md e .pdf; imagens em `conferencia/img/`). Falta: verificador separado, rodada
inteira do GitHub (disparada, ver "Testes"), filtro de velocidade (disparado), conferência do Samuel. Nada juntado.

## Como reproduzi (páginas de verdade)

Os 14 livros do teste de 23/10 deixaram o projeto salvo (`D:\programas\EditorImpressao-arquivos\testes-livros-saida\
<livro>\trab\projetos\...\projeto.json`, só leitura). `scripts/reproduzir.py` carrega o projeto, troca o PDF pela
cópia do teste e passa a página pelo MESMO corpo do processar (`core.pipeline._pagina_pronta`), com o código de
qualquer worktree (`--raiz`): antes e depois. `fab-<livro>:<pág>` faz um livro novo de fábrica só com a página do
acervo. `scripts/fazer_conferencia.py` monta os antes × depois; `scripts/cortes_do_gabarito.py` compara o corte das
32 páginas do gabarito entre dois códigos; `scripts/varrer_tinta_fora.py` procura tinta deixada de fora no acervo.

## Como cumpri cada um (teste e imagem)

| Defeito / decisão | Causa achada (página de verdade) | Conserto | Prova (teste de reversão: falha no `11f9ed3`, passa aqui) | Imagem |
|---|---|---|---|---|
| **4.2 Cursus 3** (D-104) | O corte da beirada da vizinha (`cortar_sobra`, feito ANTES do endireitar) ficou colado no texto; o endireitar (página inteira girada no mesmo tamanho) empurrou o canto do bloco para fora; a letra encostada na beirada fazia a caixa do ScanTailor ("até a moldura") jogar fora **um quarto da página** (11,6 cm em vez de 15,9 cm) | `pipeline.folga_do_giro_na_sobra`: cada lado do corte da sobra anda para fora meia altura × seno(ângulo + 0,5°) + 1 mm, na análise | `test_reversao_cursus_3_a_sobra_nao_leva_as_primeiras_letras` (letras cortadas pela beirada) | `img/cursus3.jpg` |
| **4.8/4.10 folha quase em branco** (Siebmacher 74, ljs47 2) | A caixa do ScanTailor abraça o pouco que há: tira de 2,6 × 8,6 cm (Siebmacher 74) e 21 × 11 cm (ljs47 2); no Preto e branco a tira vira a "faixa preta" | `pipeline._caixa_sem_comer`: corte comum sem conteúdo, aviso "Parece em branco" ou caixa < 20% da página achada → fica a página achada (dentro do corte comum, se este não for a tira), sem a faixa escura da beirada | `test_reversao_folha_quase_em_branco_nao_vira_tira[siebmacher-74/antiphon-2]`; `test_decisoes::test_d104_folha_quase_em_branco_nao_vira_tira` | `img/siebmacher74.jpg`, `img/ljs47-2.jpg` |
| **1.4 corte alargado menor** (Antiphon 2, D-098) | A guarda manchada tinha o corte = caixa do ScanTailor nas manchas (do meio para a direita); o alargado partia dela | Com a regra acima a página fica inteira e o aviso some; e `corte_alargado` nunca fica menor que o corte que a página tem | `test_reversao_corte_alargado_nunca_fica_menor_que_o_corte_de_agora` | `img/antiphon2.jpg` |
| **D-077 a caixa não parte letra** | A borda da caixa do ScanTailor podia passar no meio de uma peça de tinta | `_caixa_sem_comer`: a borda vai até o fim da peça (mesmo limite e regras do corte comum); peça inteira de fora continua fora, com aviso (D-098 "Só avisa") | `test_decisoes::test_d104_d077_a_caixa_do_scantailor_nao_parte_uma_letra` | — |
| **4.10 Boécio 2** | Corte comum até a beirada, com o fio preto do scan | `recortar.beiradas_escuras`: o lado que vai até a beirada da imagem perde a faixa escura colada nela (só se termina em papel limpo antes de 6% do lado; faixa larga = cartão/capa, fica) | `test_reversao_boecio_2_sem_o_fio_preto_na_beirada` | `img/boecio2.jpg` |
| **Escola 197** | `SOBRA_DE_TINTA` descarta os números soltos da margem | `recortar._numeros_da_margem`: coluna (2+) de peças do tamanho das letras da linha ao lado, a até 5% → dentro | `test_reversao_escola_197_os_numeros_da_margem_ficam` | `img/escola197.jpg` |
| **D-095 cunhas brancas** (Boécio 8, Marial 7, Graduale 221) | O giro pinta de branco as cunhas, e o corte vai até a beirada | `endireitar.rotacionar_e_cortar(cunha_com_o_papel=True)`: a cunha com a mediana do papel; + a faixa escura da beirada sai (Graduale 221, Marial 7, Siebmacher 7) | `test_reversao_boecio_8_sem_cunha_branca_na_beirada`; `test_decisoes::test_d095_cunha_do_giro_nao_fica_branca_na_beirada` | `img/boecio8.jpg`, `img/graduale221.jpg`, `img/marial7.jpg`, `img/siebmacher7.jpg` |
| **D-095 moldura/título colados** (Siebmacher 9, Escola 7) | Medido: 1,7 mm de papel acima da moldura do Siebmacher 9 e 1,3 mm acima do título da Escola 7 (a folga de 1 mm aprovada em 01/10) | Nada a mudar (já resolvido por consertos de 13/10) | — (medida) | — |
| **4.4 Horas 18** | A moldura NÃO era cortada (está inteira no PDF do teste, conferido ponto por ponto com a reprodução); a sobra da direita vinha de riscos de 1 ponto e pontinhos colados na beirada (0,23% da tinta de uma página de calendário, acima dos 0,2% descartados) | `recortar._sem_o_tracejado_da_beirada`: ciscos menores que letra e o tracejado na faixa de 4% da beirada não contam na massa da tinta | (imagem; muda o corte de 4 páginas do gabarito, mostradas) | `img/horas18.jpg`, `img/horas13.jpg`, `img/horas14.jpg`, `img/horas27.jpg` |
| **D-104 lugar 2: aviso "Corte encostou no texto"** | Medido só na folha inteira da análise, antes de dividir e endireitar | No livro novo é medido no corte da página reta (`_anotar_corte_encostou`); nas 32 do gabarito não muda nenhum aviso | (comportamento; sem página que mudasse) | — |
| **D-104 lugar 8: imprimir > 100%** | `_colocar` não desenha o que passa da metade da folha; só havia o aviso de margem | `impressao._avisos_de_corte`: "o que está impresso fica CORTADO (lado, cm)" | `test_reversao_imprimir_aumentado_avisa_que_corta` (Escola 7 a 140%) | `img/imprimir140.jpg` |
| **D-113 moldura antes de desentortar** | Na página de teste (Marial 41 encurvada, com moldura) a curva não é achada; medido direto na DLL: com a caixa só do bloco do texto ela acha, com a caixa que pega as notas da margem não (com ou sem moldura) | A caixa do conteúdo e a marca da proteção são medidas numa cópia com a moldura do scanner pintada de branco; a imagem que vai e que sai é a de sempre | `test_decisoes::test_d113_*` (2 provas) | `img/d212-curvada2.jpg` (igual antes e depois: ressalva) |
| **D-016** ordem obrigatória | — | Nada muda na montagem: endireita a página inteira, corta uma vez no fim | `test_decisoes::test_d016_*` (passa) | — |
| **D-473** tela = PDF | — | Todos os consertos estão na conta que a prévia e o PDF usam (`_geometria`, `_preparar_metade_e_geometria`, `rotacionar_e_cortar`) | `test_corte_previa_igual_pdf.py` (passa) | — |

### Os 8 lugares (D-466: "Primeiro provar em páginas de verdade, depois decidir")

1. **Endireitar no livro antigo e corte à mão comem os cantos** — não provado: Escola 35 (o caso de 28/09) na ordem
   antiga com o corte à mão justo na tinta sai igual ao automático (a folga de 1 mm já cobre). No livro novo o corte à
   mão é da página reta (não come). Projeto antigo tem de sair idêntico (CLAUDE.md): nada mudado.
2. **Corte automático deixa peças pequenas de fora / aviso medido na folha** — provado na Escola 197 (consertado) e o
   aviso agora é medido no corte de verdade. Varredura de 31 páginas de 11 livros (`varrer-fora.json`): as outras
   peças de fora eram beirada da folha, manchas e pontinhos, nenhuma letra.
3. **Tinta encostada na beirada tratada como borda** — não provado em página de verdade (nas 63 páginas olhadas o que
   encosta na beirada é fundo, lombada ou folha vizinha; o número do Graduale 221 já era protegido desde 13/10).
4. **Dividir reto em folha torta** — não provado: Righetti 96, 100 e 123 girados e divididos, nenhuma letra cortada nem
   levada para a outra página perto da dobra (`img/righetti96.jpg`). Mas o corte da sobra (o "dividir" de uma página
   só) comia no Cursus 3: consertado (linha 1 da tabela).
5. **Melhorar/Mágico pro branqueiam o que parece papel** e 6. **área "papel" pintada de branco** — são do filtro, não da
   geometria: ficam para a etapa 10b (não mexi; ver "Para a etapa 10b").
7. **Borda preta/pintar de branco tomando gravura por borda** — não provado: a conta "só o preto" em 12 páginas de
   gravura e cartão (Palatino 74 e 76, Valadés 41 e 163, Escola 7 e 19, Pesel 21, 51 e 59, Horas 30, Graduale 588)
   não tira nada; a regra nova da faixa da beirada também não (Pesel 21 continua inteiro).
8. **Imprimir acima de 100% corta** — provado (Escola 7 a 140%) e agora avisa que corta (linha da tabela).

## Escolhas técnicas (D-014: decido e anoto)

1. Folha quase em branco no "até a moldura": a página achada (não o tamanho do livro), porque a etiqueta da guarda
   fica no canto e o tamanho do livro centrado no papel a cortaria. Limite: caixa < 20% da página achada.
2. **4.8 "cada página de um tamanho, sem margem":** o geométrico que comia (as tiras) foi consertado. Deixar todas as
   páginas do "até a moldura" do mesmo tamanho já existe na opção "Margens iguais" (D-075, "Todas as páginas do tamanho
   da maior: Sim"), que o teste achou escondida (tela: etapas 3/9); e a margem de 1 mm é a aprovada em 01/10 (as
   margens de verdade são da hora de imprimir, 14/10). Não mudei o "até a moldura" para o tamanho do livro: vai como
   pergunta (abaixo).
3. Cunha do giro com a **mediana do papel** do corte (a cor da beirada pintava de preto no Antiphon 260; ver
   `relatorios/melhorias.md`). Só quando o corte chega perto da beirada (sem custo nas outras páginas).
4. Faixa escura da beirada: só o lado do corte que vai até a beirada da imagem, só faixa que termina em papel limpo
   antes de 6% do lado e que tem alguma coluna escura de verdade (amarelado não conta).
5. Matemática 40 e 66 (lista única 4.2): o corte está certo (as letras estão na página pronta em Original); quem apaga é
   o Preto e branco na sombra da lombada e no sombreado cinza → etapa 10b.

## Somas de fábrica (32 páginas do gabarito × Original/Preto e branco/Melhorar, livro novo, `processar`)

Base: `relatorios/obra-etapa1/somas-depois-8abd3e8.json` (o código do `11f9ed3` é o mesmo do `8abd3e8` em `core/` e
`modelos.py`). Depois: `somas-depois-b9437db.json` e `somas-depois-7f816b8.json` (o último: **96 de 96 iguais ao
`b9437db`**).

- **45 de 96 iguais; 17 páginas mudam DE PROPÓSITO** (as consertos mexem no livro de fábrica):
  - 5 só na cunha do giro (Boécio 3, Escola 7, Escola 35, Graduale 222, Siebmacher 9): medido ponto a ponto contra
    o código de antes, os pontos diferentes ficam a até 1,3 mm da beirada e os brancos puros da cunha somem;
  - 12 no corte (`cortes-livro-novo-antes-11f9ed3.json` × `cortes-livro-novo-depois.json`): Boécio 8 e 22,
    Graduale 221 e 223, Horas 13, 14, 26 e 27, Marial 7, Rhetorica 18 e 73, Siebmacher 7. Olhados todos: o que sai é
    beirada escura do scan, cunha, sobra de papel; nenhuma letra, moldura ou número de folha (o "Cvij" do Graduale
    221 continua). Os maiores estão na conferência.
- **Projeto começado antes de 09/10/2026: nada muda** — os consertos do corte comum só valem no livro novo
  (`detectar_bordas(livro_novo=True)`); cortes do gabarito na ordem antiga: **32 de 32 iguais**
  (`cortes-ordem-antiga-*.json`). (A primeira versão mudava a ordem antiga; o GitHub pegou pelo
  `test_ajustar_pedaco_so_figura`.)

## Testes rodados (um arquivo por vez, no PC)

Último passe (`relatorios/conferir/obra-etapa10a/testes-6.txt`, fora do git), todos passando: test_etapa10a_nao_comer
8, test_decisoes 23, test_ajustar_pedaco_so_figura 11, test_borda_preta 29, test_borda_preta_paginas_do_samuel 17,
test_corte_nao_come_conteudo 9, test_corte_folga_1mm 6, test_corte_pelo_conteudo 24, test_corte_pelo_conteudo_livro 4,
test_corte_pelo_conteudo_no_programa 16, test_corte_previa_igual_pdf 4, test_ordem_do_preparo 56, test_core 62,
test_corte_pelo_conteudo_na_tela 13, test_desentortar_scantailor 40, test_desentortar_protecao 15,
test_desentortar_medida_por_tras 6, test_endireitar_no_programa 15, test_endireitar_g5 13, test_dividir_no_programa 19,
test_trabalho_nao_se_perde 82, test_mesmo_livro_outro_caminho 17, test_zonas_na_folha 25, test_girar 53,
test_impressao 17, test_dialogo_impressao 5, test_revisar 28.

**Testes de reversão no código antigo** (worktree `obra-etapa10a-antes`, `11f9ed3`, com os arquivos de teste novos
copiados): `test_etapa10a_nao_comer.py` **8 de 8 falham** lá (e passam aqui); as 5 provas novas de `test_decisoes.py`
(`test_d104_*`, `test_d113_*`, `test_d095_*`) **5 de 5 falham** lá.

Ajustes de testes antigos: nenhum (os testes que falharam no meio do caminho acusaram defeito meu e foram consertados
no código: a tolerância de 1,5 ponto do "não partir peça", o "encostou" fora das medidas do ângulo, a cunha com a
mediana do papel em vez da cor da beirada, e o livro_novo).

**GitHub (rodada inteira):** 1ª rodada `40444878231` no `b9437db`: falhou 1 (`test_ajustar_pedaco_so_figura::
test_escola7_a_pintura_continua_sendo_ajustada`, o projeto antigo mudava) → consertado no `7f816b8`. 2ª rodada
`40447802745` no `7f816b8`: **passou inteira** (as 5 partes da suíte e o `teste_botoes.py` com os prints da janela).
**Filtro de velocidade** `40444881163` (`11f9ed3` × ramo, rodou com o `b9437db`; o `7f816b8` só tira trabalho do
projeto antigo): ver "Velocidade" abaixo.

## Perguntas para o Samuel

1. **D-113 (`d212-1`):** a moldura escura não era a causa na página de teste; a causa são as notas da margem dentro da
   caixa que o desentortar segue. Quer que o desentortar siga só o bloco do texto (deixando as notas da margem de
   fora da caixa)? (Recomendo sim, numa etapa própria, provando em páginas curvas de verdade.)
2. **4.8:** no "até a moldura", quer as páginas do livro todas do mesmo tamanho (a conta do ScanTailor do 2.5) ou basta
   a caixinha "Margens iguais" aparecer na tela? (Recomendo a caixinha à vista: já existe e foi aprovada.)
3. **Righetti 96:** a faixa preta do scanner em cima das páginas (depois de uma tira branca da tampa) continua. Posso
   tirá-la quando a folha é girada e dividida à mão (etapa 4)? Uma regra geral confundiria moldura impressa preta.

## Para a etapa 10b (filtros, não mexi)

- Matemática 40: as primeiras letras na sombra da lombada somem no Preto e branco (o corte as mantém).
- Matemática 66: números com sombreado cinza viram borrão no Preto e branco.
- Siebmacher 74: a folha quase sem tinta sai cinza no Preto e branco.
- Lugares 5 e 6 da D-104 (Melhorar/Mágico pro branqueando lápis fraco; área "papel" pintada de branco).

## Ressalvas (escritas, não escondidas)

- **Cursus 3:** continua um fio preto da lombada no alto à esquerda, ao lado do "A" de "AD" (já existia sem o corte da
  beirada da vizinha; tirá-lo cortaria a letra). A folga nova do corte da sobra vale numa análise nova do livro: o
  projeto já analisado guarda o corte da sobra antigo (o teste do Kaique de 23/10, por exemplo).
- **Siebmacher 74 e ljs47 2:** a beirada larga das outras folhas (castanha) ainda aparece fininha na direita.
- **Antiphon 2:** uma tira da folha vizinha na beirada direita.
- **Horas 13:** a esquerda ainda guarda sobra (manchas do tamanho de letra perto da beirada); a direita ficou certa.
- **Righetti 96:** a faixa preta do scanner em cima (depois da tira branca da tampa) continua (pergunta 3).
- **D-113:** na página de teste a curva continua não achada; a causa medida é outra (pergunta 1).
- **4.8:** o tamanho igual das páginas não foi mudado (pergunta 2).
- **Lugares 1, 3, 4 e 7 da D-104:** não provados nas páginas olhadas (listadas acima); nada mudado neles. Lugares 5 e
  6 são do filtro (etapa 10b).
- **Tela = PDF (D-473):** os consertos estão na conta que a prévia usa, mas não pilotei a janela (não é da etapa; o
  verificador confere). A prévia rápida (110 DPI) mede o corte na imagem pequena só enquanto o guardado não chega.
- **Velocidade:** a cunha com a cor do papel faz mais um giro (só de uma máscara) nas páginas cujo corte chega perto da
  beirada; o corte comum faz uma conta de pedaços a mais (tracejado/ciscos). Medida no filtro do GitHub (ver o fim).
- **Aviso duplo na impressão:** a página aumentada ganha o aviso novo ("CORTADO") e continua com o de margem (o texto
  do de margem fala em "-2,2 cm", que é confuso; é da etapa 9/11).

## Ideias para a Lista de espera

- O desentortar seguir só o bloco do texto (sem as notas da margem) — pergunta 1.
- "Margens iguais" à vista na tela do livro (4.8) — pergunta 2.

## Bugs para a Lista de bugs (achados, não consertados)

- 27/10, aviso de margem da impressão com número negativo ("em cima -2,2 cm (precisa de 1,3 cm)") quando a página
  passa da folha: confuso (`core/impressao.py`, `_avisos_de_margem`).
- 27/10, Righetti (folha dupla deitada): faixa preta da tampa do scanner em cima de cada página, depois de girar e
  dividir.

## Commits (ramo `obra-etapa10a-2026-10-26`, com push)

- `e634299` sobra com folga do giro; caixa do ScanTailor sem comer; faixa escura da beirada; alargado nunca menor;
  roteiros de reprodução.
- `72d1f58` D-113: caixa do conteúdo do desentortar sem a moldura do scanner.
- `f5b915a` números da margem; cunha do giro; testes de reversão e provas das decisões.
- `f8320ee` "Corte encostou no texto" no corte de verdade; imprimir aumentado avisa que corta.
- `b9437db` tracejado e ciscos da beirada (Horas 18); cunha com a mediana do papel; extras.
- `7f816b8` consertos do corte comum só no livro novo; conferência; provas.
- (o último) ONDE-PAREI final.
