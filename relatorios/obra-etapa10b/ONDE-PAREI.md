# ONDE-PAREI — obra de 26/10/2026, etapa 10b: defeitos na imagem final

Implementador · ramo `obra-etapa10b-2026-10-26` (base `obra-2026-10-26` `ab38208`, já com a etapa 10a) · worktree
`.claude/worktrees/obra-etapa10b` · worktree de apoio (código antigo, só leitura, para o teste de reversão):
`.claude/worktrees/obra-etapa10b-antes` (`ab38208`, solta, com as junções `modelos` e `gabarito\paginas`; criada por mim).
Obra D-014: feita até o fim sem pausas; o Samuel confere tudo no fim. **PRONTO PARA CONFERIR** (ver "Situação").

## Decisões que esta tarefa precisa cumprir (do pedido da gerente e do Livro, `docs/plano/DECISOES.md`)

- **Critério do Samuel (D-118):** "Eu quero que o papel saia branco, e o desenho também saia perfeito."
- **D-126:** "Gravura e letras intactas, e todo o papel totalmente branco, inclusive o papel dentro da gravura".
- **Regra do Preto e branco (30/09, itens/1.5.md):** a gravura de traço sai "como desenho em preto e branco [...] sem
  perder o desenho"; "não deve sair [...] preta chapada"; fotos e pinturas em tons de cinza (conferência 2, P1).
- **D-466** (22/10, `a-comer-pagina`): "escolhi a B, mas quando for feito o teste de bug, ele tem que fazer a C —
  Primeiro provar em páginas de verdade, depois decidir" (lugares 5 e 6: Melhorar/Mágico pro e área "papel").
- **D-473** (escolha da gerente, apoiada em D-066: "precisamos que o pdf saia que nem está na tela"): "Tela e PDF saem
  da mesma conta [...] Tela e PDF diferentes é defeito, nunca escolha". **D-327:** "B — como o ScanTailor, a tela igual
  ao PDF". **D-064:** a tela troca sozinha pela imagem do PDF, com as duas bolinhas (parte de tela: da gerente).
- **D-193** (`lu-tc-igual`): "O pdf está saindo diferente da tela gerada, na tela gerada a letra está mais grossa, isso
  é um perigo [...]".
- **D-189** (`211-reduzir`): "Ele está apagando as letras [...]" · "aprovado, mas ainda tem que melhorar, em alguns
  casos, ele acaba apagando a letra."
- **D-493** (escolha da gerente): "O desentortar segue só o bloco do texto, sem as notas da margem".
- **D-304** (01/10, P3): "Eu quero ter a opção 1.6, mas eu quero poder deixar como está também, o tamanho do arquivo
  depois não importa" — tocada pelo 4.5 (ver a pergunta 2).
- **CLAUDE.md §9:** não desfazer o "magic color" (nada dele foi mexido); **§4.7** teste de reversão; **§5** medir antes,
  uma mudança por vez, medir de novo; **§4.10** caminho inteiro e só páginas que vão ser impressas.
- **Lista única, seção 4** (23/10): 4.1, 4.3 (+ Matemática 40 e 66), 4.5, 4.7, 4.11, 4.12; Lista de bugs: T do
  Antiphonal 46 (13/10, grave), "Reduzir cores" apaga letra (21/10), foto de celular (23/10).

## Situação

**PRONTO PARA CONFERIR** (27/10/2026). Conferência: `relatorios/obra-etapa10b/conferencia/conferencia-etapa10b.html`
(também `.md` e `.pdf`; fotos em `conferencia/img/`, JPG até 300 KB). Falta: verificador separado, conferência do
Samuel. Nada juntado.

## Como cumpri cada um (causa → conserto → teste → imagem)

Como reproduzi: `relatorios/obra-etapa10b/scripts/reproduzir.py` (o da etapa 10a, com as páginas-gabarito e os livros
de "Livros para editar"): o projeto salvo do teste dos 14 livros (23/10) ou um livro NOVO de fábrica, pelo mesmo corpo
do processar (`core.pipeline._pagina_pronta`), com o código de qualquer worktree. Todas as medidas abaixo são "antes →
agora" na mesma página.

| Item | Causa achada (página de verdade) | Conserto (núcleo) | Prova (falha no `ab38208`, passa aqui) | Imagem |
|---|---|---|---|---|
| **4.1 gravura estragada** (Palatino 74, Valadés 41) | No desenho de 1 bit da gravura de traço, a "mancha escura pequena" era enchida de preto INTEIRA (feito para a nota do Graduale). A hachura fechada (Valadés 41) e o fundo manchado da gravura em madeira (Palatino 70 e 74) também são manchas escuras pequenas → blocos pretos chapados | `filtros.DESENHO_TINTA_CHEIA`: dentro da mancha só entram os pontos escuros de verdade (abaixo de 0,55 do papel). A nota cheia continua cheia | `test_reversao_4_1_gravura_nao_vira_bloco_preto[palatino-74, valades-41]`: bloco preto sem tinta cheia 1,4% e 2,0% da página → < 0,2% (3·10⁻⁵ e 5·10⁻⁴); `test_4_1_hachura_sintetica...`; guarda: `test_4_1_nota_quadrada_cheia_continua_cheia` | `img/4-1-palatino74.jpg`, `img/4-1-valades41.jpg`, `img/4-1-siebmacher110.jpg` |
| **4.3 folha branca cinza** (Boécio 49, Marial 2) | A folha sem tinta tomada por OBJETO ("capa" automática: textura 4,0 e 7,7, acima de 3,0) vira gravura inteira → foto em cinza com os níveis esticados do mais escuro ao mais claro DELA: na folha quase lisa (161 a 244) a ruga de 10 tons virava 30 | `filtros._niveis_da_capa` (só na "capa" automática): o branco é o papel da folha (percentil 85) e o preto nunca passa de 0,35 dele | `test_reversao_4_3_folha_de_guarda_sai_branca` (Boécio 49: mediana 189 → 238; abaixo de 200: 65% → 6%); `test_4_3_capa_sintetica_segue_o_papel` | `img/4-3-boecio49.jpg`, `img/4-3-marial2.jpg`, `img/4-3-siebmacher74.jpg` |
| **Matemática 66** (4.2/M-1) | A folha encurva na lombada: o papel cai para ~160 numa SOMBRA. O Otsu (um limiar só) pintava a sombra de preto | `filtros._sem_a_sombra_da_lombada`: acha a sombra pela luz de cada coluna; só nela, o cinza é dividido pela luz e o preto é o meio entre a tinta e o papel do Otsu. Sem sombra: a MESMA binária | `test_reversao_matematica_66...` (faixa da esquerda preta: 4,7% → 0,3%); `test_sombra_sintetica_na_beirada...`; `test_pagina_sem_sombra_sai_igual` | `img/4-2-matematica66.jpg` |
| **Matemática 40** (4.2/M-2) | Na sombra a letra fica BORRADA; o Sauvola (janela pequena) achava que o miolo da palavra era fundo e o apagava ("Suponha" → "~cha") | O mesmo conserto (a letra borrada volta como um borrão escuro, legível como no original) | `test_reversao_matematica_40...` (tinta na faixa da sombra: 7,1% → 13%) | `img/4-2-matematica40.jpg` |
| **Foto de celular** (Lista de bugs 23/10; Razões 57, Atanásio 8) | A sombra da mão/da folha (2D, não só na beirada) virava mancha preta no Otsu | `filtros._sombra_em_quadros`: a mesma conta, com a luz medida em quadradinhos de pouca tinta (gravura, foto e pintura escuras têm muita "tinta" e ficam de fora) | `test_reversao_foto_de_celular...` (blocos pretos < 1% da página) | `img/celular.jpg` |
| **4.5 PDF gigante** | Os livros vêm em JPEG de 72 a 200 DPI; o programa guardava cada página de tons SEM PERDA (zlib) a 300 DPI: o grão do scan ia inteiro (Antiphon 56: 20 MB numa página) | `pdf_io.QUALIDADE_DO_JPEG = 92`, 4:4:4: a página de cor/cinza vai em JPEG; o Preto e branco de 1 bit continua sem perda | `test_reversao_4_5_pagina_de_tons_vai_comprimida_e_fiel` (< 40% do sem perda, < 2 tons alisado); guarda `test_4_5_preto_e_branco_de_1_bit...` | tabela abaixo |
| **4.7 Pesel** (51, 59, 67, 75) | Na prancha o detector marca o cartão como gravura (fica marrom), mas os blocos de texto como LETRA: o "papel do bloco" ia a branco (retângulo branco) e a letra ganhava a nitidez; a beirada sem marcação ficava com o Mágico pro da página (tira branca) | `filtros._o_cartao_em_volta_da_gravura`: o fundo escuro (abaixo de 0,6 do papel) que encosta no fundo escuro da gravura e não é gravura (blocos de texto e beirada sobre o cartão) sai como foi escaneado; a gravura continua com o tratamento dela (a prancha clara continua branca — a primeira versão a deixava bege no Pesel 75, corrigido) | `test_reversao_4_7...` (cartão que sai branco: 32% → 5%) | `img/4-7-pesel51.jpg`, `img/4-7-pesel67.jpg` |
| **4.11 Valadés 203** | A mancha de ferrugem pequena e redonda passava pela regra "letra colorida sai preta" (cor longe do papel, borda nítida) → disco preto | `filtros._sem_as_manchas_redondas`: a peça colorida que é BOLA (miolo ≥ 0,8% da altura, cheia, não comprida) é mancha: não vira preta, e dentro dela só fica o escuro de verdade | `test_reversao_4_11...` (preto no quadrado da mancha: 93% → 49%); `test_4_11_mancha_sintetica_e_letra_colorida` (a letra vermelha continua preta) | `img/4-11-valades203.jpg` |
| **4.12 Antiphon 56** | O grão do pergaminho (matiz do papel, saturação 60 a 71, acima da trava 60) era pego como "traço" no bloco de letra e avivado em laranja, com um anel | `filtros._sem_o_grao_no_bloco` (peça pequena, clara, longe de letra → papel, com a orla) e `_graos_do_papel` (o mesmo na limpeza do papel) | `test_reversao_4_12...` (pontinhos laranja na margem: 2.656 → 183); `test_4_12_grao_sintetico...` | `img/4-12-antiphon56.jpg` |
| **T do Antiphonal 46** (grave, 13/10; D-473) | No "Só as letras", a tinta de fora das linhas fica se for tão escura quanto a letra (a mediana da tinta das linhas). Essa mediana muda com a resolução: 61 na prévia (110 DPI) e 44 no PDF; o ponto mais escuro da T: 43 e 50 → ficava na tela e saía do PDF | `misto.SUAVE_DA_TINTA_FORTE`: as duas medidas são feitas no cinza alisado pela altura da linha (a mesma escala na prévia e no PDF) | `test_reversao_t_do_antiphonal_46...` (tinta da T: PDF 3% × tela 12% → 11% × 12%); `test_tinta_forte_e_medida_na_escala_da_linha`; `test_decisoes::test_d473_d066_...` | `img/t-antiphonal46.jpg` |
| **D-193 tela cheia mais grossa** | Os jeitos do ScanTailor fazem a conta pelo DPI da imagem; a tela cheia (150 DPI) saía 10 a 17% mais grossa que o PDF (Otsu, Wolf) | `filtros._preto_e_branco_do_scantailor` + `pipeline._com_o_dpi_do_pdf`: na prévia, a conta é feita no DPI do PDF e o resultado volta ao tamanho da prévia (como o ScanTailor, que mostra a saída reduzida). O PDF não muda | `test_reversao_d193...[st_otsu, st_wolf]` (tinta da tela / do PDF: 1,17 → entre 0,85 e 1,08; medido 0,91 a 0,96); `test_decisoes::test_d193_...` | `img/tela-cheia-boecio22.jpg` |
| **D-189 Reduzir cores** (Horas 26) | No Preto e branco com "Letras com a cor delas", o "forçar preto e branco" da posterização do ScanTailor jogava a cor mais escura das letras no PRETO: metade da palavra preta, metade clara | `cores_scantailor.aplicar`: nesse caso sem o "forçar" (nos outros filtros, o de fábrica) | `test_reversao_d189...` (letra que vira preta: 20% → 0,1%); `test_decisoes::test_d189_...` | `img/reduzir-cores-horas26.jpg` |
| **D-493 desentortar só no bloco** | Na página do D-113 a conta acha a curva (com "aumentando a página" as linhas saem mais retas) | A conta está pronta (`desentortar_scantailor.caixa_do_conteudo(so_o_bloco=True)`), **mas NÃO ligada**: ligada, entortava a Marial 41 reta (tinta no lugar < 0,95) e, no "aumentando", o Righetti 96 perdia o começo das linhas (os testes do 2.12 pegaram) | `test_decisoes::test_d493_a_conta_do_bloco...` (só a conta) | `img/d493-desentortar.jpg` · **pergunta 1** |

### 4.5 — o tamanho do PDF (páginas de verdade, com o filtro que o livro usou; `scripts/tamanho_do_pdf.py`)

| Página | Filtro | Sem perda (antes) | JPEG 92 (agora) | Diferença média (de 255) / 99,9% até |
|---|---|---|---|---|
| Antiphon 30 | Mágico pro | 11,8 MB | 2,5 MB (21%) | 0,4 / 11 |
| Antiphon 56 | Mágico pro | 20,0 MB | 4,0 MB (20%) | 0,8 / 14 |
| Pesel 51 | Mágico pro | 2,8 MB | 2,0 MB (71%) | 1,4 / 14 |
| Pesel 30 | Mágico pro | 1,4 MB | 0,4 MB (27%) | 0,3 / 6 |
| Horas 26 | Melhorar | 4,5 MB | 2,4 MB (54%) | 0,4 / 9 |
| Horas 40 | Melhorar | 7,1 MB | 6,2 MB (87%) | 1,3 / 11 |
| Graduale 50 | Mágico pro | 10,1 MB | 2,6 MB (25%) | 0,6 / 13 |
| Escola 7 / 100 | Mágico pro | 4,7 / 4,4 MB | 1,3 / 1,2 MB (27%) | 0,8 / 8 |
| ljs47 50 | Mágico pro | 7,2 MB | 2,7 MB (37%) | 0,9 / 14 |
| Antiphon 56 | Original | 38,6 MB | 3,9 MB (10%) | 0,1 / 3 |

O PDF fica de 1,4 a 10 vezes menor (o Antiphon de 1.590 MB iria para ~330 MB). **Ainda é grande** quando o livro tem
página grande escaneada em resolução baixa (Horas, Antiphon): o programa guarda a página a 300 DPI, 4 vezes mais
pontos que o scan em cada lado. Guardar até 2 vezes o scan (o resto é só ampliação) daria mais 2 a 4 vezes menos
(Horas 40: 6,2 → 1,6 MB; Antiphon 56: 4,0 → 1,3 MB; ljs47 50: 2,7 → 1,2 MB) — **pergunta 2**.

## Somas "Desligado de fábrica" (32 páginas do gabarito × Original / Preto e branco / Melhorar, livro novo)

`scripts/somas_da_imagem.py` (soma da imagem que vai ao escritor do PDF, antes da compressão: o JPEG mudaria toda
página de cor mesmo sem o filtro mudar). Base `ab38208` × ramo (antes da junção do `obra-2026-10-26`), 96 somas: **53 iguais, 43 mudam** (lista em `_tmp/difs.txt`, fora do git; números abaixo).

- **Original: 32 de 32 iguais.**
- **Preto e branco: mudam 11 de 32** — só páginas com sombra na beirada (Graduale 221 e 222, Rhetorica 73, Siebmacher 7 e
  9), ou com gravura/decoração (Escola 7 e 35, Horas 11 e 47, Opus 20, Palatino 5: a regra nova da mancha cheia e a
  sombra em quadradinhos; diferenças de 0,005% a 0,7% dos pontos). Olhadas todas; as maiores na conferência
  (Graduale 222: a faixa preta da beirada da direita afinou).
- **Melhorar: mudam as 32** — o grão do papel (4.12) na limpeza do papel muda poucos pontos em cada página (0,002% a
  1% dos pontos com mais de 20 tons; olhadas; Marial 7 na conferência); o **Opus 20** muda mais (5,7%): o vão escuro
  atrás da estátua deixou de ter os pontinhos brancos (era a queixa "esses pontos estão horríveis atrás da estátua",
  conferência 6, X2; 6% dos pontos) — na conferência.
- **Projeto começado antes de 09/10:** os consertos são do filtro e do PDF, então também valem nele (é a mesma conta
  para todo livro); o que muda é só o que está acima. Motivo escrito: cada mudança é conserto de defeito da lista.

## Testes (um arquivo por vez, no PC)

Novos: `tests/test_etapa10b_imagem.py` **23 passaram**; `tests/test_decisoes.py` **28 passaram** (5 provas novas: D-493 ×2,
D-189, D-193, D-473/D-066). Rodados também (todos passando): test_trabalho_nao_se_perde 82, test_filtro_com_selecao 22,
test_limpar_papel 5, test_core 62, test_conferencia_5 13, test_conferencia_6 9, test_decoracao_no_preto_e_branco 12,
test_papel_dentro_da_gravura 12, test_melhorar_em_volta_da_gravura 12, test_alerta_pb 5, test_medidor_nas_paginas_otsu 6,
test_escolha_sem_a_trava_de_tinta 12, test_so_neste_pedaco_no_preto_e_branco 8, test_preto_e_branco_regra_30_09 15,
test_misto 31, test_misto_consertos 25, test_misto_desenho_claro 10, test_misto_no_programa 41, test_misto_no_projeto 12,
test_preto_e_branco_scantailor 31, test_filtros_algoritmos 10, test_pontinhos_scantailor 30,
test_limpar_pontinhos_no_programa 42, test_revisar 28, test_cores_scantailor 7, test_desentortar_scantailor 40,
test_desentortar_protecao 15, test_desentortar_medida_por_tras 6, test_filtros_tela_cheia 11, test_corte_previa_igual_pdf 4,
test_previa_composta 12, test_paginas_em_outro_processo 11, test_gravar_pdf_sem_parar_a_janela 5,
test_tirar_fundo_no_programa 54, test_so_neste_pedaco_no_tirar_o_fundo 8, test_ajustar_pedaco_na_folha_girada 8.

**Testes antigos ajustados (por causa do JPEG do 4.5, com o motivo escrito no teste):**
`test_gravar_pdf_sem_parar_a_janela` (o filtro do objeto é `/DCTDecode`; cor e cinza a poucos tons em vez de iguais
ponto a ponto; 1 bit continua idêntico), `test_tirar_fundo_no_programa::test_pdf_final_sai_igual_a_previa`,
`test_so_neste_pedaco_no_tirar_o_fundo::test_pdf_com_pedaco_sai_igual_a_previa`,
`test_ajustar_pedaco_na_folha_girada::test_tirar_o_fundo_com_pedaco_na_folha_girada` (PDF = prévia a poucos tons:
média < 2, 99,9% < 25).

**Teste de reversão no código antigo** (`obra-etapa10b-antes`, `ab38208`, com os dois arquivos de teste copiados e
apagados depois): **26 testes falham lá e passam aqui**: 21 dos 23 de `test_etapa10b_imagem.py` (os 2 que passam lá são guardas de
propósito: "a nota quadrada continua cheia" e "o 1 bit continua sem perda") e as 5 provas novas de `test_decisoes.py`
(D-493 ×2, D-189, D-193, D-473/D-066; as do D-493 porque a conta não existe lá). Saída (`_tmp/reversao.txt`, fora do
git): "26 failed, 25 passed" (os outros 23 que passam são as provas antigas do `test_decisoes.py`).

**Falham no PC também no código antigo (não são desta etapa):**
`test_desentortar_conferir_de_novo::test_destino_do_socialismo_18_...` (a página segurada difere da de hoje num canto
branco: vem da etapa 10a, cunha do giro) e `test_paginas_diferentes::test_na_analise_a_pagina_torta_ganha_o_aviso`
(a fila de medidas falsas é consumida fora de ordem; no GitHub passa). Os de `test_promessas` (p078, p080, p075) falham
no PC também no `ab38208` (janela de verdade; ver GitHub).

## GitHub e velocidade

- **Rodada inteira 1** `40540738467` (no `8b07089`, base `ab38208`): falharam os testes de "PDF = prévia ponto a ponto"
  que o JPEG mudou (3 testes; ajustados no `34d2021`, com o motivo escrito) e 8 de `test_promessas.py`. Os 8 de
  promessas **também falham no `ab38208`** (rodado no PC: 11 falham lá, `_tmp/prom-obra-etapa10b-antes.txt`) e foram
  consertados pelas etapas 3 e 9c, que entraram no `obra-2026-10-26` depois da base desta etapa.
- **Rodada 2** `40544957049` (no `34d2021`): só os mesmos `test_promessas` de antes da base nova.
- **Juntei o `obra-2026-10-26` atual (`83d7ba2`, etapas 3 e 9c) ao ramo** (`a413d69`; um conflito só, em
  `core/filtros.py`: os dois lados acrescentavam funções novas no mesmo lugar; ficaram as duas). Depois da junção, no PC:
  `test_promessas` 3 falham (p085, p094, p127), as mesmas do `obra-2026-10-26` sozinho.
- **Rodada 3** `40548644579` (no `a413d69`, com a junção): **falham só `test_promessas::test_p085` e `::test_p127`, que
  já falham no `obra-2026-10-26` sem esta etapa** (rodada `40537146001`: p085, p090, p094, p127). O resto das 5 partes
  da suíte e o `teste_botoes.py` passaram.
- **Rodada 5 (a final)** `40566825277` (no `5fa738b`): **falham só `test_promessas::test_p085` e `::test_p127`**, as
  mesmas do `obra-2026-10-26` sem esta etapa. (A rodada 4b `40564366174`, no `cb66bfa`, tinha pegado
  `test_misto_desenho_claro::test_sombra_da_lombada_na_borda_nao_volta`: a luz das colunas medida em 400 pontos via a
  faixa fina da beirada como sombra; voltou a 600 no `5fa738b`, passa.)
- **Rodada 4** `40553726768` (no `9fbde20`, com a conta da sombra barata): falham `test_promessas::test_p085`,
  `::test_p092`, `::test_p094` e `::test_p127`. p085 e p127 falham no `obra-2026-10-26` sem esta etapa; p092 e p094
  são de janela e mudam de uma vez para outra (no PC, rodados duas vezes seguidas: na 1ª p094 falhou, na 2ª os dois
  passaram; o p094 também falha na rodada do `obra-2026-10-26`). Nenhum teste de imagem falhou.

- 1ª `40540804774` (`ab38208` × ramo antes da junção): "parece mais lento: Preto e branco, 10 páginas +3,4%"; Mágico
  pro -6,8% (o JPEG). → conta da sombra barateada (`9fbde20`).
- 2ª `40553722386` (`83d7ba2` × `9fbde20`): Preto e branco +2,2% = **igual**; "parece mais lento: Trocar de página
  +4,1%" (vai-e-vem 2,0%); Mágico pro -7,5%. → contas novas do Preto e branco barateadas de novo (`cb66bfa`).
- 3ª `40564361069` (`83d7ba2` × `cb66bfa`, a conta final; o `5fa738b` depois só muda a resolução da luz das colunas
  de volta para a de antes): **nada mais lento** — "parece mais rápido: Mágico pro, 10 páginas -5,2%". Abrir o livro
  -1,5%, Trocar de página +2,3% (igual; vai-e-vem 10,5%), Preto e branco +1,8% (igual).
- Custo medido no PC, na prévia de 110 DPI: achar a sombra ~6 ms por página, mais ~10 ms nas páginas com sombra (11
  de 32 do gabarito). O PDF de Mágico pro/Melhorar ficou mais rápido de gravar (JPEG em vez do zlib nível 9).

## Perguntas para o Samuel (a gerente leva à Central)

1. **D-493 (desentortar só no bloco do texto):** a conta está pronta e, na página curva do D-113, o desentortar
   passa a achar a curva (as linhas saem mais retas com "aumentando a página"). Mas ligada para todo livro ela
   entortava uma página RETA (Marial 41) no automático e, no "aumentando a página", o Righetti 96 voltava a perder o
   começo das linhas. **Recomendo não ligar para todo livro**; ligar só quando a pessoa pedir, numa opção da página
   ("Desentortar seguindo só o texto, sem as notas da margem") — isso é botão novo, decisão dele e da etapa de tela.
2. **4.5 (PDF menor):** a página de cor/cinza agora vai em JPEG de qualidade alta (92): o PDF fica 1,4 a 10 vezes
   menor e a diferença para a tela é de 1 a 3 tons (de 255), invisível. Em 01/10 (D-304) ele disse "o tamanho do arquivo
   depois não importa"; em 23/10 o teste dos livros pôs o PDF gigante como defeito ("Difícil de guardar, copiar e
   mandar para a gráfica"). **Recomendo ficar com o JPEG 92.** E, para os livros de página grande em baixa resolução
   (Horas, Antiphon, Graduale, ljs47), **recomendo também guardar a página no máximo com 2 vezes a resolução do scan**
   (mais 2 a 4 vezes menor; nada do scan se perde, só a ampliação): precisa do "sim" dele (muda a resolução da página
   que sai).
3. **4.1 (gravura no Preto e branco):** os blocos pretos saíram. Mas a gravura em madeira de fundo escuro manchado
   (Palatino 70 e 74) continua "chuviscada": em 1 bit o fundo manchado só sai como chuvisco. A versão em **tons de
   cinza** (como as fotos, conferência 2, P1) fica igual ao original. **Recomendo perguntar:** essa gravura de fundo
   escuro sai em tons de cinza no Preto e branco (como foto), ou fica em 1 bit? (Também as fotos de retícula do
   Righetti 62 e 64, que o detector chama de gravura de traço, saem chuviscadas.)

## Para a gerente (troca de tela — não mexi em `ui/`)

- **D-473 / D-064 (tela = PDF):** o núcleo já dá a mesma conta na prévia e no PDF (T do Antiphonal, jeitos do
  ScanTailor). Falta, em `ui/tarefas.py` (`GerenciadorPrevias`), quando a "medida" no tamanho do PDF
  (`pedir_medida` → `renderizar_pagina(dpi=projeto.qualidade_dpi)`) terminar, guardar essa imagem REDUZIDA
  (`cv2.resize(..., INTER_AREA)` ao tamanho da prévia) na chave da prévia da página e redesenhar — é a "tela troca
  sozinha pela imagem do PDF" com as duas bolinhas (D-064). A tela cheia (`ui/widgets/filtros_tela_cheia.py`, linha ~93,
  `DPI_DA_TELA_CHEIA = 150`) pode fazer o mesmo depois que ficar pronta.

## Ressalvas (escritas, não escondidas)

- **4.1:** o fundo manchado da gravura em madeira (Palatino 70, 74) continua chuviscado em 1 bit (pergunta 3); no
  Valadés 41 os rostos dependem da nitidez do scan (borrado na origem). **Siebmacher 110 NÃO melhorou no projeto do
  teste:** ali a faixa de bordado de cima não está marcada como gravura (só a flor de baixo) e sai como texto, um bloco
  preto; num livro novo de fábrica o detector acha a faixa e ela sai em cinza. Não é desta conta (é a marcação/o
  detector); a marcação à mão resolve.
- **4.3:** Boécio 49 sai quase branco, com a textura bem leve; Marial 2 continua com as rugas claras do papel amassado
  (é uma folha de papel amassada de verdade, com carimbo). **Siebmacher 74** quase não muda: é uma folha com bordados
  muito fracos (não é branca); os borrões pretos do teste de 23/10 já não aparecem desde a etapa 10a, e ela continua
  cinza-clara com o desenho fraco à vista. Siebmacher 86: o desenho muito fraco some no Preto e branco
  (era assim antes; o borrão preto não volta).
- **Matemática 40/66:** as letras borradas na sombra saem como borrões escuros (o original também é borrado); no fim da
  Matemática 40 algumas primeiras letras ainda falham.
- **4.5:** o PDF da página de tons não é mais idêntico ponto a ponto à tela (1 a 3 tons; 99,9% dos pontos até 14 tons
  numa página de Mágico pro) — diferença invisível, mas é diferença (D-473); pergunta 2.
- **4.7:** sobra uma cunha clara fina entre o título e a prancha no Pesel 51; no Pesel 75 a beirada de baixo do cartão
  fica um pouco mais clara; a letra do texto do cartão sai como no scan (não fica mais "engrossada", mas também não
  ganha nitidez).
- **4.11:** o miolo da mancha que é tão escuro quanto a tinta fica (um crescente pequeno junto do "a" de "Idiomate").
- **4.12:** sobram manchas claras e cinzentas em retângulos na margem (o papel do bloco de letra) e o retângulo cinza
  do 4.6 (de outra etapa).
- **D-193:** na tela cheia a letra agora sai 4 a 9% mais FINA que no PDF reduzido (antes 10 a 17% mais grossa): a tela
  é 1 bit em 150 DPI. A troca da tela pela imagem do PDF (D-473, acima) acaba com a diferença.
- **D-466 lugares 5 e 6:** provados em páginas de verdade só no Preto e branco (Matemática 40 e 66); "Melhorar e
  Mágico pro branqueiam o lápis fraco": não achei página onde acontecesse nas olhadas (Pesel, Antiphon, Horas, Escola,
  ljs47, Graduale).
- **Velocidade:** contas novas em toda página de Preto e branco (achar a sombra, a mancha redonda) e no Melhorar/Mágico
  pro com marcação (cartão, grão). O filtro final não vê lentidão (abaixo do vai-e-vem); a prévia do Preto e branco
  paga ~6 a 16 ms por página.

## Ideias para a Lista de espera

- Guardar a página no máximo com 2× a resolução do scan (pergunta 2).
- Gravura de fundo escuro e foto de retícula em tons de cinza no Preto e branco (pergunta 3).
- "Desentortar seguindo só o texto" como opção da página (pergunta 1).

## Bugs para a Lista de bugs (achados, não consertados)

- 27/10, `test_desentortar_conferir_de_novo::test_destino_do_socialismo_18`: falha também no `ab38208` (canto branco
  na página "segurada"; provável cunha do giro da etapa 10a).
- 27/10, Siebmacher 110: o detector acha só parte do bordado como gravura.
- 27/10, Righetti 62 e 64: foto de retícula tomada por gravura de traço no Preto e branco (sai chuviscada).

## Commits (ramo `obra-etapa10b-2026-10-26`, com push)

`93d2c3d` 4.1 · `1c0cd00` 4.5 JPEG, T do Antiphonal, D-193 · `50f0370` 4.3, sombra da lombada, Pesel, 4.11, 4.12 ·
`c884467` D-189, celular, D-493 · `8b07089` testes · `7ffba04` limiar da sombra, D-493 só a conta · `34d2021` testes do
JPEG · `c5a3991` ONDE-PAREI e DECISOES · `46c581e` cartão da Pesel refeito, fotos · `0b00c8d` · `a413d69` junção do
`obra-2026-10-26` · `0c6ca3f` conferência · `9fbde20` e `cb66bfa` contas mais baratas (velocidade) · `5fa738b` luz das colunas em 600 pontos · `183de7e` pausa · (o último) ONDE-PAREI final.
