# ONDE PAREI — etapa 9a da obra de 26/10/2026 (agente de layout)

Ramo `obra-etapa9a-2026-10-26` (base `66a91d4`), worktree `.claude/worktrees/obra-etapa9a`.
Obra D-014: feita até o fim sem pausas; o Samuel confere tudo no fim. Os detalhes decididos por mim estão em
"Escolhas que fiz sozinho".

## Decisões que esta tarefa precisa cumprir (do Livro, `docs/plano/DECISOES.md`)

1. **D-012** (26/10/2026) — "2" (o "imprimir agora" fica para a etapa 9). Na prática: clicar "imprimir agora" pede
   impressora, cópias e confirmação. Ligada a **D-325** (`imp-5`: "Também manda direto para a impressora") e
   **D-332** (`b-5`). Lista única 5.1: "imprimir agora" manda o livro inteiro à impressora padrão sem perguntar.
2. **D-333** (22/10/2026) — `fr-26`: "Está bom" + "Só tem que melhorar esse layout, cheio de letras uma em cima da
   outra , tudo bagunçado e dificil de saber o que é o que." · `fr-26-qual`: "2- mandei o print." Na prática: janela
   "Montar para imprimir" organizada, o texto do resultado separado das opções; nada sobreposto em 1280×657 (150%) nem
   na janela mínima; singular/plural certos ("são 1 cadernos"). Respeitando as decisões de impressão:
   - **D-314** "o programa tem duas fases separadas" (formato só na hora de imprimir);
   - **D-315** "Quero TODAS essas opções dentro do programa" (nenhuma opção some na arrumação);
   - **D-316** livreto automático na ordem da dobra; **D-317** escala por lado (esquerda/direita/as duas);
   - **D-318** margens 1,3 cm do papel e 1 cm na costura; **D-319** aviso de margem abaixo de 1 cm;
   - **D-320** folha muito maior gira e reduz, com aviso;
   - **D-321** `imp-1` "Uma página só"; **D-322** `imp-2` "Já entra dentro das margens"; **D-323** `imp-3` "No meio
     da sua metade"; **D-324** `imp-4` "Último caderno menor, só com as folhas necessárias"; **D-325** `imp-5`
     "Também manda direto para a impressora"; **D-326** `imp-6` "Precisa: sem ela sai algo errado" (imprimir como
     imagem ligada de fábrica);
   - **D-330** `b-3-cadernos-antigo` "Deixar os dois" (o "Montar cadernos" antigo e o "Montar para imprimir").
3. **Rodinha do mouse** (teste do Kaique, 26/10: "ao rolar a janela 'Montar para imprimir' com a rodinha do mouse, o
   campo 'Páginas da esquerda (pares)' passou de 100% para 60% sozinho"): número e lista só mudam com a rodinha
   quando clicados (com o foco), no diálogo todo; ajuste reaproveitável para o resto do programa.
4. **Janelas de abrir e salvar arquivo em português** (teste do Kaique: "Look in", "File name", "Open"; digitar o
   caminho não abriu e não avisou; sem atalho para Área de trabalho/Downloads). Ligada a **D-301** ("escolher onde
   salvar o PDF [...] lembrar a última pasta usada [...] avisar em português").
5. Lista única **5.12** (dois "montar cadernos" com nomes parecidos; a "Ficou pronto!" não diz qual usar) e **5.15**
   (nome sugerido com acento "mágico pro") — só o que estiver nos meus arquivos.
6. **D-332** (22/10/2026) — `b-5-imprimir-direto`: "Testo uma folha na EPSON quando a conferência chegar
   (recomendado)". Eu não imprimo; deixo o roteiro curto para ele.

## Andamento

- [x] Li CLAUDE.md, layout.md, DECISOES (impressão), o plano, a lista única e o relatório do teste do Kaique.
- [x] Print do "antes": `prints/antes-montar-*.png` (as opções espremidas a uma faixa, texto atrás da barra de
      rolagem, botão "var o arquivo para impri" cortado).
- [x] D-012, D-333, rodinha, janelas de arquivo, 5.12/5.15, roteiro EPSON, testes, prints, entrega.

**Tudo feito (26/10/2026).** Rodada no GitHub **40438168312** (ramo `obra-etapa9a-2026-10-26`, commit `110e33f`):
suíte (5 partes) e "Botões e prints da janela real" **passaram**. Depois dela só entrou o `d050f44` (a pergunta do
"mandar para a impressora" + a prova nova), rodado no PC. Nada a continuar, salvo as trocas da gerente abaixo.

## Como cumpri cada uma

Provas em `tests/test_decisoes_impressao.py` (22 casos, todos passam). Os marcados REVERSÃO foram rodados também no
código antigo (base `66a91d4`, numa cópia temporária já apagada) e **falham lá**: o defeito aparece.

1. **D-012 "imprimir agora" (5.1).** O botão virou "imprimir agora..." e só abre a confirmação `ConfirmarImpressao`
   (`ui/dialogo_impressao.py`): arquivo e nº de páginas; impressora (a de sempre primeiro); páginas de/até; cópias;
   lados do papel; e a frase "Vão para a impressora EPSON…: 37 páginas (o livro inteiro), 1 cópia. Gasta 37 folhas de
   papel." O botão diz "imprimir 37 páginas". Enter cai no "cancelar"; X, Esc e cancelar não mandam nada. Só o
   "imprimir" manda, num fio à parte, com "parar". O "mandar para a impressora" do "Montar para imprimir" (imp-5,
   D-325) também pergunta antes (impressora, lados, cópias, folhas).
   Provas: `test_d012_imprimir_agora_nunca_imprime_sem_confirmacao` (REVERSÃO: no antigo o clique chamava
   `historico.imprimir`), `test_d012_confirmacao_mostra_impressora_paginas_e_copias`,
   `test_d012_so_o_botao_imprimir_da_confirmacao_manda`, `test_d012_mandar_da_janela_montar_tambem_pergunta`
   (REVERSÃO: no antigo o clique já mandava). Prints: `prints/depois-windows150-imprimir-agora-confirmar*.png`,
   `prints/depois-windows150-ficou-pronto.png`.
2. **D-333 "Montar para imprimir" refeita.** Duas colunas: opções à esquerda (rolam); "O QUE VAI SAIR" num cartão à
   direita (resumo antes de gravar, com folhas e cadernos; depois, "Pronto", onde gravou, "Como imprimir", a
   conferência em verde e os avisos). Seções com título curto no lugar das molduras; caixinhas de frase curta com a
   explicação embaixo; nomes de formato curtos com a explicação do escolhido; "0 = todas" virou a palavra "todas";
   caminho comprido quebra na barra. Abre com 1000×640 (cabe nos 680 livres do notebook 150%), mínimo 760×460.
   Singular/plural: "1 caderno", "1 folha", "é 1 caderno pronto"; um caderno só diz "A folha forma um grupo só" (antes
   "grupos de 5; o último grupo tem 1 folha"). Nenhuma opção saiu (D-315); os de fábrica são os de imp-1 a imp-6.
   Provas: `test_d333_montar_sem_texto_cortado_nem_por_cima[ao_abrir|minima]` (mede texto cortado e peças por cima,
   antes e depois de gravar; REVERSÃO na mínima: o botão "gravar…" saía cortado),
   `test_d333_resultado_a_parte_nao_espreme_as_opcoes` (REVERSÃO: no antigo as opções caíam de 456 para 266 px),
   `test_d333_singular_e_plural` (REVERSÃO), `test_d315_nenhuma_opcao_sumiu_na_arrumacao`.
   Prints: antes `prints/antes-montar-*.png`; depois `prints/depois-windows150-montar-*.png` (janela de verdade,
   escala 1,5, tela 1280×720 — o notebook).
3. **Rodinha (100% → 60%).** `ui/rodinha.py`: número e lista só mudam com a rodinha depois de clique ou Tab; o foco que
   a janela dá sozinha ao abrir não conta; sem isso a rodinha rola a janela. Ligado no "Montar para imprimir" e na
   confirmação. Para o programa todo: `rodinha.instalar_no_programa(app)` (ver trocas). Provas:
   `test_rodinha_nao_muda_numero_nem_lista_sem_clique` (REVERSÃO), `test_rodinha_foco_que_a_janela_deu_sozinha_nao_libera`
   (REVERSÃO: a lista "Formato" mudava), `test_rodinha_no_programa_inteiro`.
4. **Janelas de arquivo em português (+ D-301).** `ui/dialogos_de_arquivo.py`: no Windows usa a janela do Windows (já
   em português, com Área de Trabalho/Documentos/Downloads), abrindo na última pasta de onde se abriu um livro, e
   confere o caminho na volta. Quando a do Windows não pode ser usada (o caso do teste: o piloto ligou
   `AA_DontUseNativeDialogs`), a do Qt com a tradução do Qt carregada e os rótulos escritos ("Procurar em", "Nome do
   arquivo", "Tipo", "Abrir/Salvar/Escolher esta pasta", "Cancelar"), atalhos com nome em português (Área de Trabalho,
   Documentos, Downloads, Livros prontos, Última pasta aberta) e aviso claro ("Não achei este arquivo: … Confira se o
   nome e a pasta estão certos"); pasta digitada entra nela; aceita caminho entre aspas e sem ".pdf". Já usam: área de
   arrastar / Arquivo > Abrir, pasta de saída (`destino.py`), gravar o arquivo para imprimir. Provas:
   `test_janela_de_arquivo_em_portugues_com_atalhos[abrir|salvar|pasta]`, `test_caminho_digitado_que_nao_existe_avisa`,
   `test_salvar_ou_pasta_em_lugar_que_nao_existe_avisa[...]`, `test_abrir_o_livro_passa_pela_janela_em_portugues`
   (REVERSÃO), `test_janela_do_windows_conferida_na_volta`. Prints: `prints/depois-janela-*-do-qt.png`.
5. **5.12** — na "Ficou pronto!", uma frase embaixo dos botões diz qual usar ("Para imprimir em cadernos, use
   "montar para imprimir em A4": arruma as folhas com as margens da encadernação. O PDF do livro não muda."); se o PDF
   já saiu em cadernos do jeito antigo, diz isso e como usar o novo. Os dois botões ficam (D-330). Prova
   `test_5_12_ficou_pronto_diz_qual_montar_usar` (REVERSÃO). **5.15** — só a parte minha: o "<livro> - para
   imprimir.pdf" é sugerido sem acento ("Camoes - magico pro - para imprimir.pdf"); prova `test_5_15_nome_sugerido_sem_acento`
   (REVERSÃO). O nome principal vem de `modelos.py` (ver trocas).
6. **D-332 / b-5** — não imprimi nada. A frase "Falando com a impressora (pode demorar um pouco)" continua nos dois
   caminhos (conferida em `test_d012_so_o_botao_imprimir_da_confirmacao_manda`). Roteiro abaixo.

## Roteiro curto para o Samuel: uma folha na EPSON (D-332, b-5)

1. Gere o PDF de um livro curto e chegue em "Ficou pronto!".
2. Clique **"imprimir agora..."**. Confira: abriu uma janela e **nada saiu da impressora**.
3. Impressora = a EPSON; Páginas **de 1 até 2**; Cópias **1**; Lados do papel **"frente e verso (virando na borda
   comprida)"**. A frase deve dizer "2 páginas (da página 1 à 2), 1 cópia. Gasta 1 folha de papel."
4. "imprimir 2 páginas": aparece "Falando com a impressora (pode demorar um pouco)" e depois "Pronto: 2 páginas
   mandadas". Sai **uma folha**, frente e verso, sem cortar a margem.
5. (Livreto) "montar para imprimir em A4 (com margens)..." → em "Folhas de papel" ponha **de 1 até 1** → "mandar para
   a impressora..." → a pergunta mostra impressora, cópias e folhas → "mandar". Dobre ao meio: página 1 na frente,
   margens de 1,3 cm por fora e 1 cm na costura.
6. Foto do que sair errado (cortado, lado trocado, girado).

## Trocas pendentes para a gerente fazer na junção (não mexi nesses arquivos)

1. `ui/janela_principal.py`, `_escolher_pasta_de_saida` (perto da l.462): trocar o `QFileDialog.getExistingDirectory(self,
   "Onde salvar o livro pronto", <pasta>)` por `from ui.dialogos_de_arquivo import escolher_pasta` +
   `pasta = escolher_pasta(self, "Onde salvar o livro pronto", <pasta>)`.
2. `ui/tela_inicio.py`, `procurar_o_livro_a_mao` (perto da l.355): trocar `caminho, _filtro = QFileDialog.getOpenFileName(self,
   f"Onde está o livro de {resumo.nome}?", "", "PDF (*.pdf)")` por `from ui.dialogos_de_arquivo import escolher_pdf_para_abrir` +
   `caminho = escolher_pdf_para_abrir(self, f"Onde está o livro de {resumo.nome}?")`. O
   `tests/test_trabalho_nao_se_perde.py::test_livro_achado_a_mao_mantem_o_trabalho` continua valendo (ele troca
   `QFileDialog.getOpenFileName` por resposta fixa, e o módulo usa a troca quando ela existe).
3. `main.py` (recomendado, logo depois de criar o `QApplication`): `from ui import rodinha; rodinha.instalar_no_programa(app)`
   — a rodinha deixa de mudar número/lista sem clique no programa todo. Opcional: `from ui.dialogos_de_arquivo import
   traduzir_o_qt; traduzir_o_qt(app)` (traduz o resto dos textos do próprio Qt, ex.: menu de copiar/colar). Não liguei
   porque `main.py` não estava na minha lista.
4. `modelos.py`, `nome_de_saida_sugerido` (5.15, etapa 11): o sufixo vem de `NOMES_AMIGAVEIS` com acento. Copiar a função
   `sem_acento` (3 linhas, `unicodedata.normalize("NFKD", ...)`) para `modelos.py` (modelos não importa ui) e aplicar no
   sufixo; rever `tests/test_core.py` l.713-731.

## Escolhas que fiz sozinho (D-014)

- Confirmação própria em vez da janela de impressão do Windows: dá para provar por teste, mostra a frase com páginas e
  folhas, e usa o caminho de impressão já testado (`core/impressora.imprimir`, que imprime cada página como imagem).
- "imprimir agora" de fábrica em "só a frente"; se o PDF já saiu em cadernos (jeito antigo), "frente e verso, borda
  curta" (o mesmo do cartão "Como imprimir").
- Toquei fora da lista por necessidade: `core/cadernos.py` (só as frases de singular/plural de `instrucoes_de_impressao`,
  que aparecem nas duas telas), `teste_botoes.py` (fecha a confirmação do "imprimir agora" e confere que nada foi
  impresso), `relatorios/obra-etapa9a/fazer_prints.py` (novo).
- Rótulos encurtados no "Montar para imprimir": "Ordem de páginas" → "Imprimir"; "Páginas por caderno" → "Cada caderno"
  (itens "20 páginas"); Encadernação "Esquerda/Direita" → "costura à esquerda/à direita"; campo "Escala personalizada" →
  "Escala" (só aparece com "Escala personalizada (%)"); "Rotação automática" → "Girar sozinho a página deitada";
  "Centralizar automático" → "Centralizar sozinho"; "Reverter páginas" → "Ordem invertida"; "Agrupar" → "Agrupar as
  cópias"; "cancelar" (no meio do trabalho) → "parar". A etapa 11 (nomes) pode rever.
- Rodinha protegida só em caixa de número e lista; o deslizante dos filtros ficou de fora (usa a rodinha de propósito e
  tem conserto próprio aberto).

## Ressalvas

- A janela de arquivo do Windows não dá para fotografar pelo Qt; os prints são da janela do Qt (a que o piloto do teste
  do Kaique vê). No PC de verdade aparece a do Windows.
- Na janela do Windows não dá para pôr "Livros prontos"/"Última pasta" do lado esquerdo; ela só abre na última pasta de
  onde se abriu um livro.
- O teste de texto cortado usa a letra Segoe UI de verdade; fora do Windows ele pula.
- Teste de olho do Samuel: a disposição nova da janela; a folha na EPSON.

## Testes rodados (PC, um arquivo por vez)

`tests/test_decisoes_impressao.py` 22 · `test_dialogo_impressao.py` 5 · `test_cadernos.py` 28 · `test_impressao.py` 17 ·
`test_antigo_aberto_vira_pronto.py` 5 · `test_sem_janela_na_tela.py` 8 · `test_trabalho_nao_se_perde.py` 82 — todos
passaram. GitHub 40438168312: suíte inteira + `teste_botoes.py` passaram.

## Perguntas para o Samuel

Nenhuma.

## Achado importante (janelas de arquivo em inglês)

O piloto do teste do Kaique ligou `Qt.AA_DontUseNativeDialogs` (`piloto/piloto.py:372`, "diálogo de arquivo do Qt
(fica fora da tela)"). Com isso o Qt usa a janela **dele**, em inglês, porque o programa não carrega a tradução do Qt
(`ui/perguntas.py:4`). No programa de verdade, no Windows, as janelas de abrir/salvar já são as do Windows (em
português, com Área de Trabalho e Downloads). Mesmo assim o conserto cobre os dois casos (ver "Como cumpri").
