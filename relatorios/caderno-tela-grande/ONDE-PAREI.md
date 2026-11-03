# ONDE PAREI — D-574, ver as folhas do caderno na etapa 7 do Automático (e a tela grande de caderno)

Ramo `caderno-tela-grande-2026-11-02` (saiu de `obra-2026-10-26` em `110976f`). Cópia: `.claude/worktrees/caderno-tela-grande`.

## Decisões que esta tarefa precisa cumprir

- **D-574** (Livro `docs/plano/DECISOES.md`), palavras do Samuel:
  - 29/10: "quando mostra para fazer os cadernos lá na parte de fazer caderno tem que ter um botão para ver como vai
    ficar o caderno."
  - 31/10 (print da etapa 7 "Montar cadernos"): "Ele vai aparecer quando estiver na aba do montar caderno como no print
    que eu mandei, quando a pessoa for nessa aba ela vai poder ver [...]" · pergunta "mostrar as folhas do livreto nos
    três lugares (etapa 7 do Automático, painel "Montar cadernos" e "Montar para imprimir")?" → "Sim, mas no caso, eu
    estou falando em tela grande, pois no painel automatico, vamos conseguir ver ele só se clicarmos na opção de montar
    cadernos e lá se apertarmos em ver tela grande abriremos o tela grande que já temos mas para versão de caderno."
  - Livro: "**No Automático: clicando na etapa 7 "Montar cadernos", o lado direito mostra as folhas do livreto; o botão
    "tela cheia" abre a tela grande que já existe, na versão de caderno.**" Jeito (opção 1, 31/10): a folha como sai da
    impressora, frente e verso, "Folha N de M", setas para passar as folhas.
  - 02/11: "aonde fica o ver caderno aqui?" (print `relatorios/testes-guiados/2026-10-29-automatico/a-44-...png`, na
    pasta principal) · "ok, pode chamar" · "mas no caso ele vai fazer isso só quando a etapa 7 estiver selecionada no
    montar cadernos né?" → gerente: sim, só quando você clica na etapa 7; nas outras etapas o lado direito continua o
    antes e depois da página.
- **D-577** (29-31/10): nas outras etapas, a página da direita continua o antes e depois de hoje (com a bolinha, o
  "tela cheia" com zoom e "comparar"). Nada muda ali.
- **D-473** (26/10): "Tela e PDF saem da mesma conta." — a folha mostrada tem de ser a que a etapa 7 faz.
- **D-064** (22/10): a bolinha de carregamento enquanto calcula.
- **D-600** (02/11): "o shift tem que funcionar em todas as telas" — na tela grande com zoom, Shift + roda anda de lado.
- **D-577, 3º teste** (30/10): "não consigo dar zoom com o mouse, usando o scrool" — nas telas cheias a roda dá zoom.
- **CLAUDE.md §3**: a interface nunca congela (medir como o `medir.py` do verificador; limite 0,3 s); uma folha por vez
  na memória.
- **CLAUDE.md §11 item 7 (27/10)**: "é só para fazer o que eu já tinha mandado" — nenhum botão, aviso ou texto além do
  decidido. As 4 perguntas do verificador do "Montar para imprimir" ficam como estão (não mexo naquela janela).
- **CLAUDE.md §4.7**: teste de reversão que falha no `110976f`.

## Andamento
- [x] Li CLAUDE.md, layout.md, INDICE, o ONDE-PAREI do livreto-ver e o parecer do verificador.
- [x] Achado: a etapa 7 não monta o livreto A4 do "Montar para imprimir"; ela monta "no tamanho do scan (sem A4, sem
  margem)" (`core/cadernos.impor_pdf`). A `previa_da_folha` desenha o A4 e precisa do PDF já processado, que não
  existe antes do "Rodar". Avisei a gerente na hora (pergunta 1).
- [x] `ui/widgets/folhas_do_caderno.py` (novo): `FolhasDoCaderno` (o lado direito com a etapa 7 aberta) e
  `TelaGrandeDoCaderno` (a tela grande, versão de caderno).
- [x] `ui/automatico.py` (mudança pequena, separada): o lado direito vira uma pilha (antes e depois | folhas);
  `_acertar_o_lado_direito` troca pela etapa aberta; o zoom de baixo (–, +, ajustar à tela) some com as folhas à vista
  (é da página); `PaginaAntesEDepois.pausar` para a conta do antes e depois enquanto ele está escondido. Margens: não
  mexi.
- [x] `core/cadernos.py`: `ordem_das_folhas`, `montar_o_lado`, `montar_a_folha`, `paginas_lado_a_lado` (a mesma
  `montar_ordem` e o mesmo encaixe de `impor_pdf`).
- [x] `core/automatico.folha_do_caderno` + `core/paginas_em_outro_processo.folha_do_caderno` (pedido novo
  `folha_do_caderno` do servidor de páginas): a folha inteira é feita fora do processo da janela.
- [x] Provas: `tests/test_decisoes_caderno_tela_grande.py` (11) e P-211 (`tests/test_promessas.py`, promessa nova em
  `tests/promessas/promessas.md`: as setas "‹" "›" da janela grande com a etapa 7 aberta).
- [x] Reversão: as 11 provas falham no `110976f` (11 de 11; cópia descartável `_tmp/antigo`, já removida).
- [x] "Folha N de M" troca na hora também no "Montar para imprimir" (resposta "já troca"), com prova e reversão.
- [x] Testes no PC, um arquivo por vez (offscreen): test_decisoes_caderno_tela_grande 11/11 · test_decisoes_livreto_ver
  13 + 1 pulado · test_paginas_em_outro_processo 11/11 · test_decisoes_automatico_ver_como_fica 22/22 ·
  test_decisoes_montar_cadernos 13/13 · test_cadernos 28/28 · test_promessas 266 + 1 xfail (numa rodada, 1 erro no
  p083 [rede], o instável conhecido: "Não consegui achar esse arquivo"; repetido sozinho, passou) ·
  test_dialogo_impressao 5/5 · test_decisoes_impressao 22/22 · teste_botoes.py 368 ações, 0 falhas.
  O test_promessas leva 45 a 55 min no PC ocupado (o P-147, troca de tema, ~10 min cada); no GitHub, 7 a 12 min em
  todos os ramos. Uma primeira rodada minha ficou parada e a gerente fechou o processo (21116).
- [x] GitHub: 41554752657 (1c733e1) falhou só na minha prova do cancelar (a folha leve acabava antes do cancelar na
  máquina rápida; prova refeita com folha pesada) · **41565800820 (a9285df): tudo verde** (5 partes: 3407 passaram,
  0 falharam, 140 pulados, 1 xfail; botões e prints da janela real ok; erros.log vazio).
- [x] Filtro de velocidade (mexi em `core/`): 41554768281 (110976f → 1c733e1) "igual" em tudo; 41565812027
  (110976f → a9285df) rodando na entrega.

## Medidas da tela (relógio de 5 ms no fio da tela, janela de verdade do Windows fora da tela; `medir/medir.py`)
Maior parada da tela (limite 0,3 s), código final, De fábrica + "Montar cadernos", 20 por caderno:
- **Gradus Primus** (cópia, sem dividir, como abre: 18 folhas): abrir a etapa 7 0,044 s · setas 0,016 a 0,025 s ·
  trocar o caderno 0,020 a 0,022 s · abrir a tela grande 0,155 s · seta na tela grande 0,018 s · voltar a outra etapa
  0,009 s. A folha leva 13 a 24 s para aparecer (4 páginas com as etapas de fábrica), com a janela respondendo.
- **Palatino** (cópia, 32 folhas): abrir a etapa 7 0,033 s · setas 0,020 a 0,036 s · caderno 0,028 a 0,045 s · tela
  grande 0,042 s · seta na tela grande 0,033 s. Folha em 11 a 18 s.
- Para comparar, o antes e depois de hoje (D-577), mesma medida: Gradus 0,14 a 0,24 s, Palatino 0,06 a 0,33 s por
  página; o "tela cheia" dele 1,2 a 1,4 s ao abrir (`perfil.py`). Não é deste ramo.
- Antes dos consertos: com a folha montada num fio da janela (`ff98a6d`), 0,28 a 0,49 s por seta no Gradus; com a
  tela grande criada no clique (`1c733e1`), 0,57 s ao abrir. Os números de antes estão só aqui (o json foi regravado).
- Arquivos: `medir/medir-gradus.json`, `medir/medir-palatino.json`.

## Prints (offscreen, letra Segoe UI; janela principal 1280 x 657; `prints.py`, `prints.json`)
Gradus (cópia, dividido: 140 páginas, 35 folhas) e Palatino (cópia):
`00` outra etapa (antes e depois) · `01` etapa 7 aberta, montando (bolinha) · `02` folha 1 frente e verso (frente 20
e 1, verso 2 e 19) · `03` seta, folha 2 · `04` 12 por caderno · `05` tela grande de caderno · `06` tela grande com
zoom · `07` voltou a outra etapa · `08` caixinha desmarcada, etapa 7 aberta · `09` painel Automático da área de
trabalho com a etapa 7 escolhida · `10` Palatino folha 1 (frente 20 e 1, verso 2 em branco e 19, como no livreto).
Escolha da P1: `escolha-A-folha-A4.png`, `escolha-B-tamanho-do-scan.png`, `escolha-A-e-B-lado-a-lado.png`.

## Como cumpri cada uma
- **D-574 (etapa 7):** com a etapa 7 aberta, o lado direito mostra "Como vai sair da impressora", "Folha N de M —
  frente" e "— verso", as setas "‹ folha N ›", "(vira o papel)" e "tela cheia" (print 02;
  `test_d574_etapa_7_aberta_mostra_as_folhas_e_as_outras_o_antes_e_depois`, `test_d574_a_folha_tem_as_paginas_na_ordem_da_dobra`).
  As páginas por caderno escolhidas ali refazem a folha (print 04; `test_d574_trocar_as_paginas_por_caderno_refaz_a_folha`).
  "tela cheia" abre a tela grande na versão de caderno (prints 05 e 06; `test_d574_tela_cheia_com_a_etapa_7_abre_a_tela_grande_de_caderno`).
  No tamanho do scan (P1 "mostra como no scan"). Caixinha desmarcada mostra igual (P2; print 08;
  `test_d574_caixinha_desmarcada_mostra_as_folhas_igual`). Sempre a folha 1 ao abrir (resposta "b").
- **D-574 ("só quando a etapa 7 estiver selecionada"; "etapa 6 e não"):** nas outras etapas volta o antes e depois
  (print 07; a mesma prova da etapa 7). O antes e depois fica parado enquanto as folhas estão à vista.
- **D-574 (painel "Montar cadernos"/Automático da área de trabalho, P3 "sim"):** sem lugar para a folha;
  "ajustar a etapa escolhida ›" com a etapa 7 abre a janela grande já nas folhas (print 09;
  `test_d574_ajustar_a_etapa_7_no_painel_abre_a_janela_nas_folhas`). Nenhum botão novo.
- **D-574 ("Folha N de M" troca na hora, "já troca"):** nos dois lugares; prova no test_decisoes_livreto_ver.
- **D-473 (a mesma conta do arquivo):** a ordem é `core/cadernos.montar_ordem` e o encaixe é o de `impor_pdf`; a prova
  `test_d574_a_folha_da_tela_e_a_do_pdf_da_etapa_7` grava o PDF da etapa 7 e compara ponto a ponto (diferença < 4 de
  255); a folha feita no servidor é igual à feita aqui (`test_d574_folha_do_servidor_e_igual_a_feita_aqui`).
- **§3 (a tela nunca para):** a folha é feita no servidor de páginas; medidas acima (máximo 0,045 s nas setas);
  `test_d574_a_tela_nao_para_enquanto_monta_a_folha` (Gradus quando está em `_tmp/livros`) e
  `test_d574_cancelar_para_a_folha_no_servidor`. Uma folha por vez na memória (só a frente e o verso à vista).
- **D-064 (bolinha):** gira ao lado de "Como vai sair da impressora" enquanto monta (print 01), com o mesmo balão do
  "Montar para imprimir".
- **D-600 / D-577 3º teste (roda e Shift na tela grande):** a roda dá zoom e Shift + roda anda de lado
  (`ui/widgets/roda_de_lado`), como no "tela cheia" de hoje.
- **D-577:** o antes e depois das outras etapas não mudou (test_decisoes_automatico_ver_como_fica 22/22).
- **§11 item 7:** nenhum texto novo além dos do "Montar para imprimir" ("Como vai sair da impressora", "Folha N de M
  — frente/verso", "folha N", "(vira o papel)", o balão da bolinha, "Não consegui mostrar esta folha.") e dos botões
  que a tela grande de hoje já tem ("<", ">", "–", "+", "ajustar à tela", "fechar"); o "comparar" não entra na versão
  de caderno (é do antes e depois da página).
- **§4.7:** reversão: as 11 provas falham no `110976f`; a prova do "troca na hora" também.

## Respostas do Samuel
- **P1 (02/11), a folha da etapa 7: A4 do "Montar para imprimir" ou no tamanho do scan?** Prints
  `escolha-A-folha-A4.png`, `escolha-B-tamanho-do-scan.png`, `escolha-A-e-B-lado-a-lado.png` (Gradus dividido, folha
  1). Escolheu **B**: "mostra como no scan, pois eu vou querer ver como vai ficar impresso quando eu estiver no margens
  né." → a etapa 7 mostra a folha no tamanho do scan (como `core/cadernos.impor_pdf` grava); a folha A4 fica no
  "Montar para imprimir". (Pela gerente, 02/11.) A versão A4 ficou guardada pela gerente em
  `relatorios/caderno-etapa7-versao-A4/` no `fase-1`.
- **P2 (02/11): com a etapa 7 clicada e a caixinha "Montar cadernos" desmarcada, mostra as folhas igual?** → "sim".
  (Print `08-caixinha-desmarcada-etapa-7-aberta.png`; prova `test_d574_caixinha_desmarcada_mostra_as_folhas_igual`.)
- **P3 (02/11): o painel "Montar cadernos"/Automático da área de trabalho não tem lugar para a folha; "ajustar a etapa
  escolhida ›" (ou duplo clique na etapa 7) abre a janela grande já na etapa 7, sem botão novo?** → "sim". (Print
  `09-painel-automatico-etapa-7-escolhida.png`; prova `test_d574_ajustar_a_etapa_7_no_painel_abre_a_janela_nas_folhas`.)

- **Perguntas 4 a 7 (02/11, pela gerente), palavras dele:**
  - "Com a etapa 6 "Margens iguais" aberta, o lado direito também mostra as folhas?" → "etapa 6 e não" (só na 7).
  - "Ao abrir a etapa 7 aparece sempre a folha 1?" → "não, eu posso ir em qualquer pagina"; a gerente perguntou A
    (abre na folha da página atual) ou B (sempre a folha 1, setas para qualquer folha) → "b" (fica como está).
  - "Os botões de zoom de baixo somem com as folhas à vista; o zoom das folhas fica no "tela cheia"?" → "3. sim".
  - "Ao apertar a seta, "Folha N de M" já troca na hora, nos dois lugares?" → "já troca": feito também no "Montar
    para imprimir" (`ui/dialogo_impressao._mostrar_carregando`; é a pergunta 2 do verificador de lá). Prova
    `tests/test_decisoes_livreto_ver.py::test_d574_folha_n_de_m_troca_na_hora_ao_apertar_a_seta`: passa no novo e
    falha no `110976f` ("Folha 1 de 10 — frente" no lugar de "Folha 2 de 10 — frente").

## Perguntas para o Samuel
Nenhuma aberta.

## Ressalvas
- **Demora para a folha aparecer:** cada folha desenha 4 páginas com as etapas marcadas (o mesmo "depois" da página
  da direita, 4 vezes). No Gradus, com o "De fábrica", 9 a 30 s por folha conforme o PC estava ocupado (a página
  sozinha, 3 a 6 s). A janela não para nesse tempo (bolinha girando); a folha é feita no servidor de páginas.
- **Tamanho de cada metade:** o arquivo da etapa 7 (`impor_pdf`) faz cada metade do tamanho da MAIOR página do livro
  inteiro; a tela usa a maior página DAQUELA folha (medir o livro inteiro a cada troca levaria minutos). Livro com
  páginas do mesmo tamanho: igual (a prova compara com o PDF gravado). Livro com páginas de tamanhos diferentes: a
  folha da tela pode ficar com as páginas um pouco maiores que no papel.
- **Ordem das páginas:** a folha segue as páginas como estão no livro AGORA. Se "Dividir folhas ao meio" estiver
  marcado e o livro ainda não dividido, a conta da dobra ainda conta a folha inteira como uma página (dividir de
  verdade precisa medir o livro todo). Depois de rodar o Dividir, a ordem fica certa.
- **Memória:** o servidor de páginas que monta uma folha carrega os filtros (e a rede das gravuras, se "Gravuras e
  fotos" estiver marcada) e fica com eles até o programa fechar.
- **Janela de verdade:** prints fora da tela (offscreen) e medidas na janela de verdade do Windows fora da tela; não
  pilotei com mouse de verdade (é do verificador).
- **O "tela cheia" de hoje (antes e depois, D-577)** para a janela 1,2 a 1,4 s ao abrir (medido em `perfil.py`);
  defeito de antes, não deste ramo. A tela grande de caderno abre em 0,26 s.
