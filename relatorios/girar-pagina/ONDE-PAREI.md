# ONDE-PAREI — girar só a página numa folha dividida (D-618)

Ramo `girar-pagina-2026-11-04` (saiu de `obra-2026-10-26`). Cópia: `.claude/worktrees/girar-pagina`.

## Decisões que esta tarefa precisa cumprir

- **D-618** (04/11, prints a-70 a a-73): "quando ele gira a pagina ele faz ela caber no A4, ele deveria girar o conteudo só
  que é da pagina cortada, mas ele gira a pagina verdadeira do scan. tanto que quando você vai girando ele cai na folha
  branca. Ele gira as duas folhas ao mesmo tempo, faz uma confusão com as paginas." → numa folha já dividida, ¼ e meia
  volta (Propriedades, canto, Ctrl+Seta) giram só a página da tela, já cortada; a outra página e a linha não mudam.
- **Correção do Samuel na D-618 (04/11, recado da gerente):** "não a folha inteira não continua girando como hoje, pois
  hoje quando gira a folha altera a proporção dela para girar ela, e eu não quero que aconteça isso, não sei como deveria
  ser a opção girar duas folhas, mas não deveria ser assim." → proposta da gerente: "girar a folha inteira é como
  girar uma foto. A folha larga, com as duas páginas, fica em pé, inteira, sem esticar, sem apertar e sem cortar
  nada. A proporção não muda." → **Samuel: "girar - sim"** (recado da gerente, 04/11). Feito, com teste que mede.
- D-030 (girar por botões e menu), D-035 ("Todas ficam viradas como a folha da vez"), D-036 / D-556 (aviso "vá a uma
  folha par"), D-049 (bloco no Propriedades + canto), D-053 (canto gira só esta folha), D-361 (R é só Retângulo; girar
  é Ctrl+Seta), D-367 (lista do girar diz "folha"), D-371 ("daqui em diante"), D-487 (girar na grade), D-601 (Dividir
  "Uma página" mostra a metade), D-609 (linha arrastada na folha inteira, com a rotação anotada).
- CLAUDE.md §6 (campo novo no projeto só com aprovação: o Samuel pediu o conserto; projeto antigo tem de abrir igual),
  §7 (recorte e ângulo moram na página; o giro de 90 vem antes de tudo), §11.8 / D-605.
- **D-636** (05/11, resposta à pergunta 1): "1- pode ser, só garanta que não crie mais problemas fazendo isso, você tem
  que pensar na experiencia do usario e no resultado final do livro dentro do programa, quando vai mudar algo, deixe
  isso anotado." → numa folha dividida, o quadro do girar se chama "Girar a página" e o "aplicar em" diz "só esta
  página / todas as páginas / daqui em diante / pares / ímpares"; cada página gira sozinha, como a da tela (D-618),
  também na tela "ver todas". As outras ficam viradas igual à da vez (D-035). Folha inteira (não dividida): fica como
  está.
- **D-637** (05/11, CLAUDE.md §11.9): antes de mexer, a seção "Como fica para quem usa e no livro" (abaixo); na
  entrega, conferir clicando e olhando o PDF, e dizer se a mudança criou problema novo.

## Como fica para quem usa e no livro (D-637; escrito ANTES de mexer, 05/11)

Exemplo: Gradus, livro dividido (cada folha do scan virou duas páginas), o Kaique está na página 14.

**Antes (hoje, depois da D-618):**
1. No Propriedades o quadro diz "Girar a folha" e a lista "aplicar em" diz "só esta folha / todas as folhas / daqui
   em diante / só as pares / só as ímpares".
2. Com "só esta folha", ¼ à esquerda deita só a página 14 (D-618). Certo.
3. Com "todas as folhas", ¼ à esquerda gira as FOLHAS do scan: cada folha larga fica em pé e a linha da divisão corta
   a folha deitada; cada "página" vira meia folha com pedaços das duas, e com meia volta a 14 mostra a 13 (a branca).
   É a confusão do a-70, ainda viva nessas opções. O PDF sai com essas páginas misturadas.
4. Na tela "ver todas", escolher as páginas 14 e 20 e "girar ¼ →" gira as folhas inteiras delas (a 13 e a 19 giram
   junto, e a confusão é a mesma).

**Depois:**
1. Numa página de folha dividida, o quadro diz "Girar a página" e a lista diz "só esta página / todas as páginas /
   daqui em diante / só as pares / só as ímpares" (o menu Página > "Aplicar o giro em" diz o mesmo; o balão dos
   botões do canto diz "só esta página"). Numa folha inteira (não dividida, ou o Dividir em "Duas lado a lado"),
   tudo continua dizendo "folha", como hoje.
2. "só esta página": igual a hoje (D-618).
3. "todas as páginas", ¼ à esquerda na 14: a 14 deita (a partir de onde estava) e TODAS as páginas de folhas
   divididas ficam deitadas igual a ela (D-035), cada uma sozinha, inteira, sem pedaço da vizinha; a linha da
   divisão de cada folha não muda. "daqui em diante": da página 14 até a última. "só as pares"/"só as ímpares":
   contam o número da PÁGINA; numa página ímpar com "só as pares" o programa avisa ("Você está numa página ímpar.
   Para girar só as pares, vá a uma página par e gire de lá.") e não gira nada (D-036, com "página").
4. Um Ctrl+Z desfaz o giro de todas de uma vez, e cada página volta ao giro que tinha.
5. Páginas de folhas que NÃO estão divididas (ex.: a capa aberta inteira) não giram com "todas as páginas": ficam
   como estão (D-636: "Folha inteira: fica como está"). Vira pergunta 2 abaixo.
6. Na tela "ver todas": escolher a 14 e a 20 e "girar ¼ →" gira só a 14 e a 20 (cada uma ¼ a partir de onde está,
   como a grade faz hoje); a 13 e a 19 não mudam. Página escolhida de folha inteira gira a folha dela, como hoje.
   O balão do botão diz "Gira as páginas escolhidas ¼ à direita."
7. A prévia, a tira de miniaturas e a página na tela mostram cada página deitada, inteira.

**No PDF que sai:** as páginas giradas saem deitadas, inteiras, cada uma com o seu conteúdo (a mesma imagem que
sairia sem o giro, girada); as outras páginas e a linha da divisão saem iguais. Folha inteira: nada muda.

**O que pode dar problema (conferir na entrega):** corte à mão, tamanho escolhido e lugar do conteúdo de cada página
girada têm de girar junto (como na D-618); o Ctrl+Z tem de devolver tudo; a palavra do quadro tem de trocar ao ir
de uma página dividida para uma folha inteira e de volta; o menu tem de dizer o mesmo que o quadro.

## O que já está escolhido e testado aqui

Testes do girar: `tests/test_girar.py` (contas, "aplicar em", desfazer, zonas acompanham, prévia = PDF),
`tests/test_girar_na_tela.py` (Propriedades, canto, menu, teclas, aviso pares/ímpares),
`tests/test_girar_cartoes_e_previas.py` (cartões, tira, cache das prévias),
`tests/test_ajustar_pedaco_na_folha_girada.py`, `tests/test_decisoes_automatico.py::test_d334_acoes_nas_escolhidas_girar_e_tirar` (grade),
`tests/test_decisoes_dividir.py::test_lista_3_1_*` e `test_d495_*` (girar a folha inteira e depois dividir),
`tests/test_decisoes_dividir_arrastar.py::test_d609_girar_a_folha_depois_de_arrastar_mostra_a_linha_do_motor`,
`tests/test_paineis_na_tela.py::test_o_bloco_girar_a_folha_fica_no_alto_do_propriedades`,
`tests/test_decisoes.py::test_d095_*`, `tests/test_borda_preta.py::test_regressao_so_o_preto_em_pagina_girada_cunha_branca`,
`tests/test_camadas.py::test_pagina_girada_*`, `tests/test_impressao.py::test_pagina_deitada_gira_de_pe_e_avisa`.

Dividir: `tests/test_decisoes_dividir*.py`, `tests/test_dividir_*.py`, `tests/test_decisoes_dividir_metade.py`.
PDF: `tests/test_pipeline_folha.py`, `tests/test_corte_previa_igual_pdf.py`, `tests/test_cartao_pdf_gerado.py`,
`tests/test_gravar_pdf_sem_parar_a_janela.py`, `tests/test_folhear_pdf.py`.
Cadernos: `tests/test_cadernos.py`, `tests/test_caderno_segue_as_etapas.py`, `tests/test_decisoes_montar_cadernos.py`,
`tests/test_decisoes_caderno_tela_grande.py`, `tests/test_decisoes_impressao.py`.

Regra: nenhum desses muda. A folha inteira (não dividida) continua girando a folha; desde o "girar - sim" a página dela leva junto o corte à mão, o tamanho escolhido e o lugar do conteúdo.

## Perguntas para o Samuel

1. **O "aplicar em" e o nome do bloco numa folha dividida.** Hoje, numa folha dividida, só "só esta folha" gira a
   página; "todas as folhas", "daqui em diante", "só as pares" e "só as ímpares" continuam girando as folhas
   inteiras, como antes (o que, numa folha dividida, ainda faz a confusão do a-70). Sugestão: numa folha dividida o
   bloco passa a se chamar "Girar a página", a lista diz "só esta página / todas as páginas / daqui em diante / só
   as pares / só as ímpares", e cada página gira sozinha, virada como a da tela. O mesmo para o girar da grade "ver
   todas" (hoje gira as folhas das páginas escolhidas). Pode ser assim?
   Print para a pergunta: `prints/antes-02-esquerda-1.png` (o defeito) e `prints/depois-02-painel-esquerda.png`
   (com "só esta folha", já consertado).
   **Respondida em 05/11 (D-636): "1- pode ser [...]".** Em construção.
2. **"todas as páginas" e as folhas que não foram divididas.** Livro dividido, mas com uma folha inteira (ex.: a capa
   aberta). Na página 14 (dividida), "todas as páginas" + ¼ à esquerda deita todas as páginas das folhas divididas;
   a capa inteira fica como está (não gira). Fiz assim porque a D-636 diz "Folha inteira (não dividida): fica como
   está" e porque girar a capa aberta deixaria a folha larga em pé, o que ninguém pediu. Pode ser assim, ou a capa
   também deve girar?
3. **Numa folha inteira, "todas as folhas" ainda gira as folhas já divididas como folha.** Ex.: na capa inteira, com
   "todas as folhas", ¼ à esquerda gira também as folhas divididas do resto do livro como folha inteira, e nelas
   volta a confusão do a-70 (cada página com pedaços das duas). Não mexi (D-636: folha inteira "fica como está").
   Sugestão: nesse caso as folhas divididas giram página por página, como na pergunta 1. Pode ser assim?

## Para a gerente: um teste antigo contradiz a D-618 (não mexi nele)

`tests/test_recomeco_limpa_o_historico.py` (5 testes) falha no GitHub (rodada 41900193119) e no PC. O ajudante
`_conferir_com_o_livro_dividido_e_mexer` divide o livro todo, vai à página 1 (metade esquerda da folha 1) e chama
`_girar_folhas(90)` com "só esta folha"; depois cobra `folhas[0].rotacao == 90` (linha 126). É exatamente o
comportamento que a D-618 tira: numa folha dividida, agora gira só a página 1 (`paginas[0].giro_da_pagina == 90`) e
a folha fica em 0. O assunto do teste é outro (o Ctrl+Z depois de recomeçar); o giro ali é só "uma ação qualquer".
Não mudei o teste (regra). Sugestão para a gerente decidir: no ajudante, cobrar o giro da página 1 em vez do da
folha (ou girar com o livro ainda não dividido).

### Depois da autorização (04/11)

- Ajudante trocado (commit b4a5538c): 4 dos 5 passam.
- Falta 1: `test_desligar_o_dividir_nao_recomeca_e_o_ctrl_z_continua_certo`, linha 170, FORA do ajudante:
  `assert janela.projeto.folhas[0].rotacao == 90  # o trabalho ficou`, logo depois de "desligar o Dividir" no
  Automático. Com a D-618 o giro está na página 1 (`giro_da_pagina == 90`, guardado; a folha não está mais dividida,
  então ele não aparece até o Ctrl+Z dividir de novo, e aí volta). Não mexi (só o ajudante foi autorizado).
  Proposta: `assert janela.projeto.paginas[0].giro_da_pagina == 90  # o trabalho ficou (D-618: na página)`.
- Depois, a gerente autorizou também a linha 170: trocada em commit separado (064b2e4e), com comentário citando a
  D-618. Agora os 13 testes do arquivo passam (PC 05/11 e GitHub 41948211799).
- Achado e consertado (b12d6f61): juntar a folha e dividir noutra linha fazia as metades novas herdarem o giro.

## Andamento

- [x] reproduzir na janela de verdade (antes): `prints/antes-*.png`, `anotacoes-antes.txt`
- [x] provar a causa (medidas no relatório)
- [x] teste de reversão: `tests/test_decisoes_girar_pagina.py` (falha em ce086bb6)
- [x] conserto: commit 93a390ed
- [x] prints depois, e o que funcionava ao redor: `prints/depois-*.png`
- [x] folha inteira: medida (`prints/folha-*.png`) e, depois do "girar - sim", gira como foto (`prints/foto-*.png`)
- [x] GitHub: suíte 41903363460 (só o teste antigo que contradiz a D-618 falha); velocidade 41900198976 igual
- [x] linha 170 do teste do recomeço trocada em commit separado (064b2e4e), autorizada pela gerente, comentário cita a D-618
- [x] 05/11: juntei o `obra-2026-10-26` (f06e0c15) sem conflito (merge b23ad645). O giro da página anda junto com
  a página quando a ordem das páginas muda (core/ordem_das_paginas move os mesmos objetos).
- [x] 05/11, PC (um arquivo por vez, `resultado-testes.txt`): os 40 `test_decisoes*.py` e 15 arquivos do girar,
  Dividir, PDF, camadas e recomeço passam. Na série, `test_d148` (instável conhecido) falhou uma vez; de novo,
  sozinho e com o arquivo inteiro, passou (5 passed). `test_recomeco_limpa_o_historico.py`: 13 passed.
- [x] 05/11, GitHub: rodada **41948211799** em b23ad645, **passou inteira** (success).
- [x] 05/11: resposta à pergunta 1 (D-636) e regra D-637; juntei de novo o `obra-2026-10-26` (d3b613b6, só o
  Livro); "Como fica para quem usa e no livro" escrita antes de mexer (10f74f65); provas de reversão; código
  (78f2e025); prova provisória trocada (18b24395); piloto na janela real e PDF (93e5228d).
- [x] PC (série "D-636 (05/11)" em `resultado-testes.txt`, um arquivo por vez): os 41 `test_decisoes*.py` e 16
  arquivos do girar, Dividir, Endireitar, histórico, recomeço, promessas (267 + 1 falha já esperada), painéis,
  PDF, camadas e impressão: todos passam. Antes, `test_paineis_na_tela::test_a_faixa_tem_esta_certo_e_proxima_duvida`
  caiu uma vez com a máquina carregada; sozinho e com o arquivo inteiro passou (22 passed).
- [x] GitHub: rodada **41970202273** em 93e5228d, **passou inteira**.
- [ ] respostas às perguntas 2 e 3; depois, a gerente junta

## Como cumpri cada decisão

- D-618: `test_reversao_d618_*`, `test_d618_canto_ctrl_seta_e_meia_volta_*`, `test_d618_o_pdf_sai_com_so_a_pagina_girada`;
  prints `depois-02` a `depois-08` (página 13 igual em todos os passos).
- "girar - sim" (folha inteira como foto): `test_reversao_d618_folha_inteira_com_corte_a_mao_gira_como_foto`,
  `test_reversao_d618_folha_inteira_com_tamanho_escolhido_nao_aperta` (falham em ce086bb6 pela proporção),
  `test_d618_folha_inteira_girada_mede_a_proporcao_na_previa_e_no_pdf`; prints `foto-01` a `foto-04`.
- D-030, D-035, D-036, D-049, D-053, D-361, D-367, D-371, D-556: `tests/test_girar.py` e `tests/test_girar_na_tela.py`
  passam sem mudança; textos da tela não mudaram.
- D-487 / D-334: com escolhidas só de folhas inteiras a grade gira as folhas como antes
  (`test_d334_acoes_nas_escolhidas_girar_e_tirar` sem mudança; `test_d636_ver_todas_so_folhas_inteiras_*`); com
  metades, cada uma gira sozinha (D-636). D-601 / D-609: `test_decisoes_dividir_*` passam.
- Projeto antigo abre igual: `test_d618_projeto_antigo_sem_o_campo_abre_igual` e
  `test_d618_a_geometria_das_zonas_de_antes_continua_igual`.
- D-605 (o novo não estraga o testado): nenhum teste antigo mudou, fora a exceção autorizada da D-618
  (ajudante em b4a5538c e linha 170 em 064b2e4e, os dois com comentário citando a D-618). Depois do merge com o
  `obra-2026-10-26`: PC e GitHub (41948211799) passam.
- Pergunta 1: respondida (D-636), ver abaixo.
- **D-636** (05/11): `tests/test_decisoes_girar_paginas_aplicar_em.py` (10 provas; 8 falham em 10f74f65, o código
  de antes: lá "todas" girava as folhas e a grade girava a folha inteira; as 2 que passavam lá são as da folha
  inteira, que não podia mudar). Código: 78f2e025 (`core/girar.py` bloco D-636, `ui/widgets/barra_girar.py`
  `definir_coisa`, `ui/tela_conferir.py` `_girar_as_paginas`, `_acertar_as_palavras_do_girar`,
  `_girar_as_escolhidas_que_sao_metade`, `ui/janela_principal.py` o menu, `ui/widgets/todas_as_paginas.py` o
  balão, `historico_acoes.montar_acao` guarda o "antes" de `folha:<i>.<campo>`).
  A prova provisória da D-618 "continua como antes até o Samuel responder" (escrita nesta tarefa, 04/11) virou
  `test_d618_d636_aplicar_em_todas_numa_folha_dividida_gira_as_paginas`, em commit separado (18b24395).
- **D-637** (conferência clicando e no PDF, 05/11): `piloto.py aplicar`, `anotacoes-aplicar.txt`,
  `prints/aplicar-*.png`. Gradus aberto, "dividir todas" na ferramenta Dividir (70 folhas, 140 páginas), folha 1
  juntada ("não dividir esta", a capa inteira; 139 páginas), Cortar as bordas:
  - página 1 (folha inteira): quadro "Girar a folha", lista e menu "só esta folha / todas as folhas / ...",
    canto "só esta folha" (`aplicar-01`). Página 14: "Girar a página", "só esta página / todas as páginas /
    ...", menu e canto iguais (`aplicar-02`).
  - "todas as páginas" (pelo menu Página) + ¼ à esquerda (clique no Propriedades): "Girar ¼ à esquerda: todas
    as 138 páginas, viradas como a página 14"; páginas 13 a 16 deitadas, inteiras, nenhuma folha girou, as
    linhas da divisão iguais, a capa igual (mesmo resumo da imagem) (`aplicar-03`, `-04`, `-05`). Ctrl+Z:
    todas voltam (mesmos resumos de antes) (`aplicar-06`).
  - "só as pares" na página 14 + meia volta: 69 páginas pares; na página 3: a caixa "Você está numa página
    ímpar. Para girar só as pares, vá a uma página par e gire de lá." e nada gira (`aplicar-07`, `-08`).
  - "ver todas": escolhidas a 1 (capa inteira) e a 14, "girar ¼ →": só a 14 deitou e a folha da capa girou; a
    13 ficou igual; "Girar 2 páginas (escolhidas em Todas as páginas)"; Ctrl+Z devolve tudo (`aplicar-09`,
    `-10`).
  - PDF (só as páginas 1, 13 a 16, numa cópia do projeto): antes 842x595 (capa) e ~421x595 (as outras);
    depois a capa igual (o mesmo arquivo de imagem) e as outras ~595x421, cada uma deitada e inteira, sem pedaço
    da vizinha (`aplicar-pdf-antes-*`, `aplicar-pdf-depois-*`; olhei as imagens).
  - **Problema novo: nenhum visto.** O aviso "Esta página parece estar em branco" na 14 já existia (a página
    14 do Gradus é branca).
