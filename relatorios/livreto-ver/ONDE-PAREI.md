# ONDE PAREI — D-574, ver o livreto pronto no "Montar para imprimir"

Ramo `livreto-ver-2026-10-31` (saiu de `obra-2026-10-26` em d95df6b). Cópia: `.claude/worktrees/livreto-ver`.

## Decisões que esta tarefa precisa cumprir

- **D-574** (28/10, 29/10, 31/10): "eu deveria conseguir ver o livreto pronto aqui nessa tela para que eu possa ver se
  ficou certo, quero tres opções [...]" · 29/10: "quando mostra para fazer os cadernos lá na parte de fazer caderno tem
  que ter um botão para ver como vai ficar o caderno." · 31/10, Central: escolheu "Opção 1: as folhas como saem da
  impressora, frente e verso": "À direita, a folha A4 deitada como vai sair: "Folha 1 de 32 — frente" e embaixo o
  verso, com setas para passar as 32 folhas. [...] Caso real: Palatino, folha 1: frente com as páginas 20 e 1, verso
  com a 2 (em branco) e a 19." · "Não gostei da tela que mostra o livreto, podemos mudar depois, deixe anotado na lista
  de espera. vou escolher a 1, mas não gostei muito". Desenho: `conferencia-versao-teste-2026-10-28/alternativas/img/2-10-A-folhas-da-impressora.jpg`.
- **D-064** (22/10): "é só colocar uma bolinha de carregamento [...] quando passsamos o mouse em cima mostra a mensagem
  de porcentagem e quantas paginas carregaram já."
- **D-473** (26/10): tela e PDF saem da mesma conta (a prévia usa a mesma montagem do PDF).
- **D-315** (14/10): "Quero TODAS essas opções dentro do programa" — nenhuma opção da janela sai.
- **D-333** (22/10): "Só tem que melhorar esse layout, cheio de letras uma em cima da outra" — nada por cima, nada cortado.
- **CLAUDE.md §3**: a interface nunca congela; uma página (aqui: uma folha) por vez na memória.
- **Regra 7 (27/10)**: só o que ele mandou; nada de botão/texto/comportamento a mais.

## Andamento (31/10/2026)
- [x] Prova escrita antes: `tests/test_decisoes_livreto_ver.py`, 9 provas. No código antigo: **9 falharam** (a janela não
  tinha prévia nem o core a `previa_da_folha`). No novo: **9 passaram** (rodado 4 vezes).
- [x] `core/impressao.py`: `folhas_que_saem` e `previa_da_folha` (a MESMA `_montar_livreto` do arquivo, pedindo uma folha
  só; desenhada pequena; trava do MuPDF `pdf_io._TRANCA`).
- [x] `ui/dialogo_impressao.py`: no cartão da direita, em cima, "Como vai sair da impressora" + bolinha; "Folha 1 de 32 —
  frente", a folha, "Folha 1 de 32 — verso", a folha, "‹ folha 1 ›  (vira o papel)". Embaixo continua o "O que vai
  sair" de antes. Fio à parte (`_TarefaPrevia`), uma folha guardada, pedido velho ignorado, opção mudou = refaz (250 ms
  de espera), "gravar" e prévia nunca no MuPDF ao mesmo tempo, fechar espera o fio.
- [x] Testes da impressão, um arquivo por vez: test_decisoes_livreto_ver 9/9, test_dialogo_impressao 5/5,
  test_decisoes_impressao 22/22 (inclui D-333: nada cortado nem por cima), test_impressao 17/17, test_cadernos 28/28.
- [x] Prints com o Palatino (cópia em `_tmp/palatino/`): `relatorios/livreto-ver/*.png`, medidas em `medidas.json`
  (script `prints.py`). Folha 1: frente 20 e 1, verso 2 e 19 (a montagem); primeira folha 2,0 s depois de abrir; seta
  0,25 s; trocar para 16 por caderno 0,47 s.
- [x] Commit e push no ramo `livreto-ver-2026-10-31`.

- [x] Rodada no GitHub 41213885135: 2 falhas. (1) `test_promessas::test_todo_botao_tem_promessa`: as setas "‹" "›"
  não tinham promessa; escrevi a P-163 em `tests/promessas/promessas.md` e a prova `test_p163_setas_da_folha`
  (test_promessas.py inteiro no PC: 263 passaram, 1 xfail de antes). (2) `test_decisoes_so_as_letras::
  test_d148_desfazer_o_automatico_devolve_o_so_as_letras_do_livro` ("não aconteceu a tempo"): não toca a impressão; no
  PC passou. Parece demora da máquina do GitHub.
- [x] Conserto achado ao rever: apertar "gravar" com a prévia montando adiava o começo e deixava `dialogo.tarefa` vazio;
  agora o fio do "gravar" nasce na hora e ele mesmo espera a prévia soltar o MuPDF (prova no
  `test_d574_gravar_com_a_previa_montando_espera_e_grava`).
- [x] Rodada no GitHub 41217021857 (commit 4309a15): **tudo verde** (5 partes da suíte + botões e prints da janela real).

## Como cumpri cada uma
- **D-574, opção 1:** a folha A4 deitada, "Folha 1 de 32 — frente" e embaixo o verso, setas "‹ folha 1 ›". Print
  `2-folha-1-frente-e-verso.png` (Palatino: frente 20 e 1, verso 2 em branco e 19) ao lado do desenho 2-10-A; provas
  `test_d574_folha_1_frente_20_e_1_verso_2_e_19_igual_ao_pdf`, `test_d574_janela_mostra_a_folha_1_frente_e_verso`,
  `test_d574_setas_passam_as_folhas`, `test_d574_trocar_a_opcao_refaz_a_previa`.
- **D-473 (a mesma conta do PDF):** a prévia vem de `_montar_livreto`, a mesma do arquivo; a prova compara os pontos da
  prévia com a folha 1 do PDF gravado.
- **D-064 (bolinha):** a bolinha gira ao lado do título enquanto monta (print `1-ao-abrir-montando.png`); balão
  "Montando a folha (o livreto tem 32 folhas)".
- **§3, não congela / uma folha por vez:** `test_d574_janela_nao_congela_enquanto_monta` (montagem de 1,5 s, o relógio
  da tela continua batendo), `test_d574_uma_folha_por_vez_na_memoria`.
- **D-315 / D-333:** nenhuma opção saiu; o texto "O que vai sair" continua embaixo; `test_decisoes_impressao.py` 22/22
  (nada cortado nem por cima, na janela de 1000x617 e na mínima); prints 5 e 6.
- **Regra 7:** nenhum botão novo além das setas do desenho; nenhum texto novo além dos do desenho ("Como vai sair da
  impressora", "Folha N de M — frente/verso", "folha N", "(vira o papel)"), do balão da bolinha e do aviso de erro
  ("Não consegui mostrar esta folha.", regra §3 de erro virar frase em português).

## Perguntas para o Samuel

1. **O botão do dia 29/10.** Ele escreveu: "quando mostra para fazer os cadernos lá na parte de fazer caderno tem que ter
   um botão para ver como vai ficar o caderno." O desenho da opção 1 não tem botão: a folha já aparece sozinha ao abrir
   o "Montar para imprimir" (foi assim que fiz, seguindo o desenho). Pergunta: "a parte de fazer caderno" era esta
   janela (então está atendido, sem botão) ou a etapa "Montar cadernos" do Automático (lá não mexi; é de outra cópia)?
   Exemplo real: Palatino, abrir "Montar para imprimir" → em 2 s aparece a folha 1, sem apertar nada.
2. **Os outros formatos.** A prévia só aparece no Livreto (é o formato da D-574); em "Página inteira", "Várias páginas
   por folha" e "Pôster" a janela fica como estava, só com o texto. Quer as folhas também nesses? Exemplo real:
   Palatino em "Página inteira" sairia "Folha 1 de 63 — frente" com a página 1 e o verso com a 2.
3. **O livreto do jeito antigo (2 por folha, do Automático).** Quando o PDF já saiu em cadernos pela etapa "Montar
   cadernos" (duas páginas por lado, no tamanho do scan), o botão "montar para imprimir..." fica apagado e não há
   prévia nenhuma. Fica assim? Exemplo real: Rhetorica Christiana, que tem a etapa 7 marcada.
4. **"Folhas de / até".** Escolhendo folhas 3 a 5, a prévia diz "Folha 3 de 32 — frente" (o número de verdade da folha
   no livreto, e o total do livreto inteiro), e as setas andam só de 3 a 5. Ou prefere "Folha 1 de 3"? Exemplo real:
   Palatino, reimprimir só as folhas 3 a 5.
5. **"Só a frente" / "Só o verso".** Aparece só o lado que vai sair ("Folha 1 de 32 — frente"), sem o "(vira o papel)".
   Está bom assim?

## Ideias para a Lista de espera
- Já pedido por ele (31/10), para a gerente anotar se ainda não estiver: "Não gostei da tela que mostra o livreto,
  podemos mudar depois, deixe anotado na lista de espera [...] tem como olha como outros aplicativos fazem isso".

## Ressalvas
- A prévia é desenhada direto da montagem; o arquivo gravado (com "Imprimir como imagem") é a mesma montagem desenhada
  a 300 DPI. No Palatino a diferença média entre a prévia e a folha 1 gravada, reduzida ao mesmo tamanho, foi 4 e 3
  (numa escala de 0 a 255): é só o arredondamento de reduzir a imagem, não página trocada (no livro sintético, < 2).
- O "gravar" (`montar_para_impressao`) continua sem a trava do MuPDF (`pdf_io._TRANCA`), como já era; a prévia usa a
  trava e nunca roda junto com o "gravar" desta janela.
- Prints fora da tela (offscreen, letra Segoe UI carregada à mão); a janela de verdade no PC não foi pilotada.

---

## 02/11 — tirar o travamento

Pedido do Samuel (02/11/2026, pela gerente): "vamos resolver esse problema do travamento agora, coloque um agente para
trabalhar nisso" — o travamento que o verificador achou (parecer em `verif-livreto/relatorios/livreto-ver/verificador/`):
no Opus Majus cada seta deixava a janela parada 1,7 a 2,6 s; trocar o caderno 1,9 s; ao abrir, mais 1,8 s.

### Decisões que esta tarefa precisa cumprir
- **CLAUDE.md §3:** "Interface nunca congela. Todo processamento em QThread, com barra de progresso e botão de cancelar
  que funciona." (a causa: o PyMuPDF segura o Python inteiro enquanto desenha, então o fio à parte não basta).
- **D-473** (26/10): "Tela e PDF saem da mesma conta" — a folha mostrada continua vindo da mesma `_montar_livreto` do
  arquivo gravado.
- **D-574** (31/10, opção 1): a folha A4 deitada, frente e verso, setas — nada muda na tela.
- **CLAUDE.md §11 item 7 (27/10):** "é só para fazer o que eu já tinha mandado" — nada de botão, aviso ou texto novo.
- **CLAUDE.md §4.7:** teste de reversão que falha no `ff0260f`.
- Fora desta tarefa (a gerente mandou não mexer): as 4 perguntas do verificador, a "tela grande" de caderno, o travamento
  ao gravar (defeito antigo).

### Andamento
- [x] Juntei `origin/obra-2026-10-26` (55 commits) no ramo: sem conflito (`cfde703`).
- [x] `core/paginas_em_outro_processo.py`: pedido novo `folha_do_livreto` — o servidor de páginas (o mesmo de 30/09)
  monta e desenha a folha com `core.impressao.previa_da_folha` lá dentro; o fio da janela só espera o cano, com o
  Python solto. Aceita "cancelar" no meio (a opção mudou). Servidor fora do ar: monta aqui, como antes.
- [x] `core/impressao.previa_da_folha`: pede ao servidor primeiro (como `pdf_io.pagina_para_array` já fazia).
- [x] Provas novas em `tests/test_decisoes_livreto_ver.py`: `test_d574_a_tela_nao_para_com_a_montagem_de_verdade`
  (livro pesado de teste + Opus Majus quando está em `_tmp/livros/`), `test_d574_folha_do_servidor_e_igual_a_feita_aqui`,
  `test_d574_cancelar_para_a_folha_no_servidor`.
- [x] Reversão no `ff0260f`: a prova falha (livro pesado: parada 1,0 a 1,1 s; Opus Majus: 1,8 a 3,6 s). No novo: 0,01 a
  0,06 s.
- [x] Folha cancelada (opção mudou, janela fechou) volta na hora; um fio espera a resposta do servidor (`b541caa`).
- [x] Testes no PC, um arquivo por vez: test_decisoes_livreto_ver 13/13, test_paginas_em_outro_processo 11/11,
  test_dialogo_impressao 5/5, test_decisoes_impressao 22/22, test_impressao 17/17, test_cadernos 28/28,
  test_promessas 264 + 1 xfail antigo.
- [x] Medidas antes × depois (`medir/medir.py`, cópia do do verificador com `SEM_GRAVAR=1`; janela de verdade do
  Windows, fora da tela; antigo = `ff0260f`). Maior parada da tela:
  - **Opus Majus:** setas antes 1,5 a 3,0 s → depois 0,007 a 0,014 s; trocar o caderno 0,95 s → 0,008 s; ao abrir
    3,0 s → 0,008 s. A folha leva o mesmo tempo para aparecer (~2 a 3 s), mas a janela não para.
  - **Palatino:** setas 0,08 a 0,14 s → 0,005 a 0,008 s; caderno 0,12 s → 0,008 s; ao abrir 1,4 s → 0,007 s.
  - Arquivos: `medir/medir-antigo-*.json`, `medir/medir-livreto-ver-*.json`.
- [x] Prints do Opus Majus (`medir/prints_opus.py`): `opus-1-seta-montando.png`, `opus-2-ainda-montando-meio-segundo-depois.png`
  (a foto sai na hora, com a folha montando: a janela responde), `opus-3-folha-2-pronta.png`; relógio de 5 ms bateu 421
  vezes em 2,35 s (`prints-opus.json`).

### Ressalvas
- Continua de antes, fora desta tarefa: **abrir a janela** "Montar para imprimir" sozinha para a tela 6,7 s (antes 7 a
  11 s; montagem dos widgets, igual no código antigo) e o **gravar** para a tela 18 s no Palatino e 78 s no Opus. A
  peça de hoje não resolve o gravar de graça: ele grava o arquivo inteiro com progresso e cancelar, e levá-lo para o
  servidor é outra mudança.
- O cancelar no servidor só é visto entre um lado e outro da folha; quem pediu já volta na hora, mas o servidor fica
  ocupado até acabar aquele lado (~1 s no Opus). Há dois servidores, então o pedido seguinte usa o outro.
- Durante a montagem continua escrito "Folha 1 de 113" até a folha nova chegar (pergunta 2 do verificador; não mexi).

### Como cumpri cada uma
- **§3:** a montagem e o desenho saíram do processo da janela; maior parada medida com relógio de 5 ms (ver "Medidas").
- **D-473:** o servidor roda a MESMA `previa_da_folha` (a mesma `_montar_livreto`); a prova compara ponto por ponto a
  folha do servidor com a feita aqui, com 5 jogos de opções: iguais.
- **D-574 / regra 7:** nenhuma linha de tela mudou (só um comentário em `ui/dialogo_impressao.py`).

## Perguntas para o Samuel
(nenhuma nova nesta tarefa)
