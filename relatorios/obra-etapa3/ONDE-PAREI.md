# Obra de 26/10/2026 — etapa 3 (layout + core): ONDE PAREI

Ramo `obra-etapa3-2026-10-26` (base `obra-2026-10-26` = `fdabf0d`, com as etapas 1, 2 e 9a), worktree
`.claude/worktrees/obra-etapa3`. Ordem do Samuel (D-014): fazer até o fim sem pausas; ele confere tudo no fim.

**Situação: PRONTA PARA CONFERIR** (começada em 26/10/2026, noite; terminada em 27/10/2026). Ramo enviado ao GitHub.

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| D-002 (25/09) + Kaique 22/09 + 26/10 | "Trabalho automático = painel 'Automático' que abre e fecha (substitui a tela 7). [...] Funciona antes/ao abrir o livro e depois, na área de trabalho (ex.: abrir o PDF sem mexer e rodar as etapas depois)." · Kaique: "Essa pagina não era mais para aparecer – nós tínhamos que abrir direto na área de trabalho" · 26/10: "eu quero poder sim fazer automatico para todo livro, mas também quero pode fazer uma a uma." | O livro abre direto na área de trabalho; a tela "Marque o que você quer fazer" sai do caminho; painel Automático + janela grande, que roda no livro todo, em páginas escolhidas, numa página só ou uma etapa só, ao abrir ou depois. |
| Tudo de "O que fazer" | (pedido da gerente, auditoria de 26/10; rodada 2 nº 5 "Aprovado": "Ter as duas: painel (opção 1) com botão que abre a janela (opção 2). Escolher folhas abrindo a tela de todas as páginas (marcar/desmarcar). Na janela, ver a página ao lado, folhear e dar zoom.") | Grupos Página · Limpeza · Gravuras e fotos · Saída; molduras no Preto e branco; "Tirar o fundo"; jeito de dividir; conta do endireitar; G2; g7/g8; pergunta do fundo; borda preta; reforçar texto falhado; "Só as letras". Lista única 2.2, 2.7, 5.2, 5.3, 5.11. |
| D-003 (28/09) / D-016 (escolha D-014) | "Ordem das etapas: livre. [...] muda arrastando com o mouse. Sem cadeados." | Arrastar muda a ordem em que as etapas RODAM; a montagem da página segue a ordem obrigatória. |
| D-004 (28/09) | "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas mexidas." | Rodar em livro com páginas mexidas pergunta; "pular" mantém essas páginas. |
| Marca "mexida à mão" (etapa 1) | (D-009, 26/10: "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo manualmente.") | Toda edição à mão (corte, ângulo, filtro da página, marcação, dividir/linha, mover, girar) grava a marca. |
| D-071 / D-355 (`fr-219`, 22/10) | "Está bom" + "Mas ainda pode melhorar a caixa de como escolhemos o que vai dentro da receita." | Receitas guardar/pôr/apagar no Automático, caixa do "o que vai na receita" mais clara; "Receita usada" no livro aberto. |
| D-005 (12/10) + D-018 (escolha D-014) | "B — Um aviso embaixo da página" ("Livro novo: ainda não passou pelo automático", "Rodar o automático…", "agora não") | Livro novo mostra o aviso; "Rodar o automático…" abre a janela grande com a receita de sempre marcada. |
| D-284 (`pr-medir-o-livro`, 21/10) + 29/09 | "Medir o livro inteiro por trás, depois de abrir" · "Página sempre abre em 'Original', sem mexer." | Ao abrir, passada leve; medição completa por trás só guardando; nenhuma página muda até rodar o automático. |
| D-334 (24/09) | "Ver todas as páginas do livro em grade, como o 'Organizar páginas' do UPDF: seleção múltipla, girar, apagar, extrair, inserir, dividir." | Grade com várias escolhidas e ações; é onde "rodar em escolhidas" escolhe. |
| D-093 / D-094 (09/10) | `g6-retangulo`: "Fica no mesmo lugar da página (como no ScanTailor)" + "Posso ter as duas opções mas a opção do scantailor ficar como padrão?" · `g6-retangulo-onde`: "Na ferramenta Endireitar, por página" + "quero a b e c juntas." | "Fica no mesmo lugar / Acompanha o texto" em Configurações, no livro (janela do Automático) e na página (Endireitar). |
| Livro aberto (R6, 06/10) | "Sim, fica assim" | "Rodar o automático…" abre o Automático de verdade; "Para revisar" e "Receita usada". |
| Defeito de 29/09 + teste do Kaique 26/10 (tarefas 7 e 8) | (opções jogadas fora em livro já conferido) | O Automático grava no projeto aberto; mudar uma etapa num livro conferido vale e nada se perde; fica no Histórico/`acoes.jsonl`. "Só endireitar" não corta; "Preto e branco" vale. |
| D-068 (24/09) | "Toda função automática tem botão de ligar e desligar." | Cada etapa do Automático liga e desliga. |
| D-069 (30/09) | F5: a pergunta do fundo também dentro do programa, depois de abrir o livro, e a opção de voltar ao original | "Tirar o fundo" e "voltar ao original" com o livro aberto. |
| D-135 (29/09) | "Ao abrir um livro com camadas, o programa pode avisar: 'Este livro tem fundo separado. Quer tirar o fundo?'" · "De acordo" | A pergunta continua ao abrir direto na área de trabalho. |
| D-075, D-080, D-081, D-082, D-092, D-101, D-144, D-148, D-168, D-175, D-186/D-277, D-195, D-212, D-213 | (ver o Livro) | Cada opção que morava em "O que fazer" continua existindo, agora no Automático. |
| Atalhos (pergunta da etapa 2) | o Samuel quer "como o Photoshop" | Letras para Dividir, Cortar e Endireitar, sem conflito. |

## Plano (como vou fazer)

1. `core/etapas.py`: o automático também por página (`ConfigPagina.automatico`), além da caixinha do livro.
2. `core/automatico.py` (novo): as etapas, a ordem, o pedido (etapas + opções + páginas), as páginas mexidas, a
   medida (por trás) e o aplicar no projeto aberto, com a ação do Histórico.
3. Janela: abre direto na área de trabalho (passada leve; trabalho salvo volta sem análise nova), medição por trás,
   aviso do livro novo, painel Automático de verdade, janela grande, grade com várias escolhidas, pergunta das
   mexidas, marca "mexida à mão", retângulo do corte nos 3 lugares, letras dos atalhos.
4. Provas em `tests/test_decisoes_automatico.py`; testes antigos adaptados ao caminho novo.

## Passos

- [x] núcleo (etapas por página, automatico.py, histórico)
- [x] abrir direto na área de trabalho + medição por trás
- [x] painel + janela grande + receitas
- [x] grade com várias escolhidas
- [x] pergunta das mexidas + marca mexida à mão
- [x] retângulo do corte (3 lugares), atalhos
- [x] livro aberto da tela inicial
- [x] provas e testes antigos adaptados
- [x] prints, velocidade, ONDE-PAREI final

## Perguntas para o Samuel

Nenhuma: as escolhas foram feitas pela gerente (D-014) e estão no Livro (D-481 a D-491).

## Como cumpri cada decisão

| Decisão | O que ficou no programa | Prova (teste) | Print |
|---|---|---|---|
| D-002 abrir direto | `abrir_livro` faz uma passada leve (tamanhos das folhas, sem análise) e vai **direto à área de trabalho**; trabalho salvo volta como está (`projetos.motivo_sem_analise`). A tela "O que fazer" saiu do caminho (o arquivo ficou, D-488). | `test_d002_abrir_vai_direto_para_a_area_de_trabalho_e_a_tela_de_opcoes_saiu` | `depois-01-abrir-o-livro.png` (antes: `antes-01-abrir-o-livro.png`) |
| D-002 rodar no livro todo / escolhidas / numa página / uma etapa | Painel Automático (coluna da direita) e janela grande: "Rodar em: no livro todo / só nesta página / nas páginas escolhidas"; cada etapa com caixinha própria. O automático por página mora em `ConfigPagina.automatico` (sem "assar" nada na página). | `test_d002_rodar_so_endireitar_numa_pagina_muda_so_ela`, `test_d002_rodar_no_livro_todo_divide_e_fica_no_historico`, `test_d334_escolher_paginas_na_grade_e_rodar_nelas` | `depois-02-painel-automatico.png`, `depois-03..06-janela-grande-*.png` |
| Tudo de "O que fazer" no Automático | Grupos Página (Dividir, Endireitar, Cortar), Limpeza (Limpar a folha), Gravuras e fotos, Saída (Margens iguais, Montar cadernos). Molduras no PB, Tirar o fundo, jeito de dividir, conta do endireitar, G2, g7/g8, borda preta, reforçar texto falhado, Só as letras, pontinhos: todas na janela grande. | `test_toda_opcao_da_tela_o_que_fazer_existe_no_automatico` (lê o código da tela antiga e confere cada controle), `test_os_grupos_do_desenho_estao_no_automatico` | `depois-04-janela-grande-limpar.png`, `depois-05-janela-grande-gravuras.png` |
| D-003/D-016 ordem | Arrastar as etapas na lista muda a ordem em que RODAM (`Projeto.ordem_do_automatico`); a montagem da página continua na ordem obrigatória (o PDF sai igual). | `test_d003_d016_arrastar_a_ordem_grava_e_a_pagina_sai_igual` | `depois-03-janela-grande-receita-de-sempre.png` |
| D-004 páginas mexidas | Rodar com páginas mexidas pergunta "Pular as N" / "Rodar nelas também" / "cancelar". | `test_d004_*` (3) | — |
| Marca "mexida à mão" | Toda edição à mão passa por `TelaConferir._registrar`, que grava a marca na página/folha. | `test_edicao_a_mao_grava_a_marca_e_o_filtro_a_mao_chega_ao_pdf`; promessas P-005, P-080, P-081, P-109 | — |
| D-071/D-355 receitas | Receita no painel e na janela (pôr, "Salvar receita...", "Apagar a receita"); a caixa da receita mostra uma caixinha por etapa com o que vai dentro, em português, e "Usar esta receita no aviso de todo livro novo". "Receita usada" no livro aberto. | `test_d071_receita_guardar_com_o_que_vai_dentro_e_por`, `tests/test_unidades_e_perfis.py` | `depois-11-livro-aberto.png` |
| D-005 + D-018 aviso | "Livro novo: ainda não passou pelo automático." com "Rodar o automático…" (abre a janela grande com a receita de sempre marcada; nada muda até Rodar) e "agora não". | `test_d005_*`, `test_d018_*`; promessa P-137 | `depois-01-abrir-o-livro.png`, `depois-03-...png` |
| D-284 medir por trás | Ao abrir um livro novo, uma tarefa por trás mede o livro todo e só põe os avisos; a página abre em Original. | `test_d284_a_pagina_abre_em_original_sem_mexer`, `test_d284_a_medida_por_tras_so_poe_os_avisos` | — |
| D-334 grade | Grade com várias escolhidas (caixinha no canto, Ctrl/Shift): girar ¼ ←/→, deixar em branco, tirar do livro, trazer de volta, extrair..., rodar o automático nelas. "Inserir" não (ressalva). | `test_d334_*` | `depois-07-grade-escolhendo-para-o-automatico.png`, `depois-09-grade-varias-escolhidas.png` |
| D-093/D-094 retângulo | Configurações > Medidas e receitas; janela grande (Endireitar); a página (aba Endireitar: segue o livro / fica / acompanha). | `test_d094_retangulo_do_corte_nas_configuracoes_no_livro_e_na_pagina` | `depois-10-pagina-endireitar-retangulo.png`, `depois-12-configuracoes-retangulo.png` |
| Livro aberto (R6) | "Rodar o automático…" abre o livro e a janela grande; "Para revisar: N" e "Receita usada: X". | `test_livro_aberto_rodar_o_automatico_abre_o_automatico_e_mostra_revisar_e_receita`; promessa P-012 | `depois-11-livro-aberto.png` |
| Defeito 29/09 + Kaique tarefas 7 e 8 | O Automático grava no trabalho aberto, numa ação do Histórico (`acoes.jsonl`, tipo "automatico"), com desfazer; nada recomeça. Só endireitar não corta; Preto e branco vale. | `test_29_09_mudar_uma_etapa_num_livro_conferido_vale_e_nada_se_perde`, `test_kaique_tarefa_7_so_endireitar_nao_corta` | `depois-08-depois-de-rodar.png` |
| D-068 ligar e desligar | "desligar as marcadas" no painel e "Desligar" na janela. | `test_d068_desligar_as_marcadas_tira_o_automatico` | — |
| D-069/D-135 fundo | A pergunta do fundo continua ao abrir; "Sim" vale na hora (D-490). | `tests/test_tirar_fundo_no_programa.py`, `teste_botoes.py` | — |
| Atalhos | D = Dividir, X = Cortar, I = Endireitar (D-481), remapeáveis. | `test_letras_d_x_i_escolhem_dividir_cortar_endireitar` | — |

## O que mudou (por arquivo)

- **`core/automatico.py` (novo):** as etapas do Automático (Dividir, Endireitar, Cortar, Limpar, Gravuras e
  fotos, Margens iguais, Montar cadernos), os grupos do desenho, a ordem, o pedido (etapas + opções + onde), as
  páginas mexidas (D-004), a passada leve ao abrir (`livro_leve`), a medida (fio de fundo, 150 DPI, como a análise
  de sempre) e o `aplicar` no trabalho aberto, numa ação só do Histórico (desfaz e refaz, inclusive dividir).
- **`core/etapas.py`:** o automático também por página (`ConfigPagina.automatico`); `corta_sozinho`,
  `endireita_sozinho`, `limpa_sozinho` e `marca_sozinho` aceitam a página.
- **`core/pipeline.py`:** só passa a `pagina` a essas funções (linhas da geometria, chaves de cache, ângulo,
  corte pelo conteúdo/borda, tamanho do livro, filtro). **Atenção na junção com a etapa 10a:** as linhas perto de
  `_geometria` e `_corta_pelo_conteudo` / `_corta_pela_borda` mudaram aqui também (mudança mínima, só o argumento).
- **`core/perfis.py`:** receitas guardam as etapas (`_etapas`) e as opções novas; `receita_de_sempre`.
- **`core/misto.py`:** usa o filtro que vale em cada página.
- **`modelos.py`:** `ConfigPagina.automatico`, `retangulo_do_corte`; `Projeto.ordem_do_automatico`,
  `passou_pelo_automatico`, `receita_usada`, `retangulo_do_corte`.
- **`historico_acoes.py`:** o desfazer troca a lista inteira de folhas/páginas (dividir) e campos de uma folha.
- **`projetos.py`:** `motivo_sem_analise` (o trabalho salvo volta sem análise nova; recomeço só quando o PDF mudou,
  o projeto.json não dá para ler ou falta página); "Para revisar" e "Receita usada" no resumo.
- **`ui/automatico.py` (novo):** o painel Automático, a janela grande e a caixa da receita.
- **`ui/janela_principal.py`:** abre direto na área de trabalho; medida por trás; Automático (rodar, desligar,
  escolher, pergunta das mexidas); o "Sim" do fundo vale na hora; a tela "O que fazer" saiu do caminho.
- **`ui/tela_conferir.py`:** aviso do livro novo; marca "mexida à mão" em toda edição (`_registrar`); retângulo do
  corte na aba Endireitar; "mudar no Automático..."; ações da grade nas escolhidas; letras D, X, I.
- **`ui/widgets/todas_as_paginas.py`:** a grade com várias escolhidas (caixinha, Ctrl/Shift) e a faixa das ações.
- **`ui/widgets/paineis.py`, `trilha_agrupada.py`, `ui/tela_inicio.py`, `ui/tela_configuracoes.py`,
  `ui/barra_de_menu.py`, `ui/tarefas.py`, `configuracoes.py`:** painel novo no lugar do antigo, atalhos, livro
  aberto, Configurações > retângulo, menu Arquivo > "Automático...", as tarefas de medir.

## Escolhas da gerente (D-014) feitas aqui — no Livro como D-481 a D-491

| Nº | Escolha |
|---|---|
| D-481 | Atalhos: D = Dividir, X = Cortar, I = Endireitar (C e E já eram do "Marcar como"). |
| D-482 | "agora não" fecha o aviso do livro novo de vez para aquele livro. |
| D-483 | A medida por trás só roda no livro novo; o livro salvo volta como estava. |
| D-484 | Gravuras, Margens e Cadernos valem sempre no livro todo; desligar nas escolhidas deixa a etapa nas outras. |
| D-485 | Página de trabalho antigo com filtro diferente do livro conta como "mexida" na pergunta da D-004. |
| D-486 | A página ao lado na janela grande é a original (o antes/depois ao vivo fica para a Lista de espera). |
| D-487 | Grade: girar, em branco, tirar, trazer de volta, extrair (as folhas como estão no PDF de entrada), rodar o automático nelas. **"Inserir" não foi feito** (precisa de página que não vem do PDF de entrada: muda o modelo de dados). |
| D-488 | `ui/tela_opcoes.py` fica no repositório, fora do caminho (apagar fica para a gerente). |
| D-489 | Recomeço só quando o PDF mudou, o projeto.json não dá para ler ou falta página; mudar etapa nunca recomeça. |
| D-490 | O "Sim" do aviso do fundo vale na hora (liga Limpar com "Tirar o fundo" no livro todo, numa ação). |
| D-491 | Retângulo do corte: Configurações (de fábrica "fica"), livro (janela grande) e página; a página manda. |

## Velocidade de abrir (Marial, 214 MB, 3 vezes, mediana; janela de verdade sem tela)

| | antes (fdabf0d) | depois |
|---|---|---|
| livro novo até a área de trabalho | **138,8 s** (abrir + "Conferir" com a análise inteira) | **0,66 s** |
| medida por trás (a pessoa já trabalha) | — | 70,4 s |
| continuar um livro salvo | **140,6 s** (a análise rodava de novo) | **0,88 s** |

Arquivos: `relatorios/obra-etapa3/velocidade-antes.txt` e `velocidade-depois.txt`; script
`relatorios/obra-etapa3/roteiro/medir_abrir.py`. Ressalva: o PC tinha outros agentes rodando (a primeira vez do
antes deu 284 s); a mediana tira esse pico. O trabalho do automático não sumiu: ele roda quando o Kaique aperta
"Rodar" (e leva o tempo da medida), mas não segura mais a abertura do livro.

## Testes (um arquivo por vez, TEMP e --basetemp na worktree)

- **Todos os 167 arquivos de `tests/`** (rodada final, código de `24e3298`): **2.990 passaram, 135 pulados,
  8 xfail**; 166 arquivos sem falha nenhuma. Lista por arquivo: `relatorios/obra-etapa3/testes-por-arquivo.txt`.
  - `tests/test_decisoes.py` (fica fora do roteiro por ser da etapa 1): 18 passaram.
  - `tests/test_promessas.py`: 237 passaram, 8 xfail, **4 falham de propósito** — são os defeitos B, C e D da
    bateria, que não são desta etapa e continuam marcados "defeito" na lista: P-075 e P-078 (folha em branco /
    pintar de branco no Original não sai branco no PDF, defeito B), P-085 (tique do menu Filtro, defeito D; o
    conserto está na obra, D-492, e não está neste ramo) e P-127 (menu "Confirmar e processar" sem "Antes de
    processar", defeito C).
  - Provas desta etapa: `tests/test_decisoes_automatico.py` — **24 passaram**.
  - Os de tela e os de "trabalho não se perde": todos passam (`test_trabalho_nao_se_perde.py` 82,
    `test_paineis_na_tela.py` 22, `test_recomeco_limpa_o_historico.py`, `test_trocar_de_livro_grava.py` 6, …).
- **`teste_botoes.py`:** 310 ações, **0 falhas** (achou um defeito no caminho: fechar a janela grande e clicar
  Desfazer dava "already deleted" — consertado, com teste de reversão).
- **`teste_interface.py`, `teste_ampliar.py`, `teste_medidor.py`:** dão o mesmo resultado no código antigo e no
  novo (as falhas deles são antigas: o livro de teste tem 2 páginas, e `conferir.destino` não existe faz tempo).
  `gerar_prints.py` foi adaptado e compila, mas não foi rodado (ele grava por cima de `relatorios/prints/`).
- **Reversão:** `tests/test_decisoes_automatico.py` no código antigo (`fdabf0d`, cópia em
  `saida_teste/obra-etapa3/antigo`): **os 24 falham** (`saida_teste/obra-etapa3/reversao.txt`). Ressalva honesta:
  boa parte falha porque o código antigo nem tem `core/automatico.py`; as provas de comportamento (abrir direto,
  aviso, pergunta das mexidas, marca à mão chegando ao PDF) também falham por si.

## Promessas (pedido da gerente durante a etapa)

- **Defeito A** (filtro escolhido à mão não chegava ao PDF com "Limpar a folha" desmarcada): neste ramo a marca
  "mexida à mão" é gravada em toda edição à mão (`TelaConferir._registrar` → `_com_a_marca_mexida_a_mao`, e
  `etapas.marcar_mexida_a_mao` na marcação). **P-005, P-080, P-081 e P-109 passam: "defeito" retirado.**
- **P-012, P-137, P-139** prontas: "aguarda" retirado e as provas viraram de verdade (abre a janela grande com a
  receita; "agora não" fecha o aviso; rodar só Endireitar numa página muda só ela).
- Saíram com a tela "O que fazer": P-011, P-021 a P-025, P-138. Mudaram: P-062 ("mudar no Automático..."), P-143
  ("Voltar para os livros"), P-083 (os jeitos do "Só as letras" na janela grande).
- Novas: **P-172 a P-188** (menu "Automático...", botões do painel, grade com várias escolhidas, janela grande,
  caixa da receita); a varredura passou a abrir a janela grande e a caixa da receita.
- `abrir_livro_para_teste()`: o livro abre direto; `marcadas` vira rodar essas etapas do Automático.

## Prints da janela de verdade (1280×657, fora da tela; `relatorios/obra-etapa3/prints/`)

`antes-01-abrir-o-livro.png` (a tela "O que fazer") × `depois-01-abrir-o-livro.png` (direto na área de trabalho,
com o aviso); `depois-02` painel; `depois-03` a `06` janela grande (receita de sempre, Limpar, Gravuras,
Endireitar); `depois-07` grade escolhendo para o Automático; `depois-08` depois de Rodar (o aviso sumiu, etapas
"ligada no livro todo"); `depois-09` grade com várias escolhidas e as ações; `depois-10` retângulo do corte na
página; `depois-11` livro aberto com "Para revisar" e "Receita usada"; `depois-12` Configurações. Roteiro:
`relatorios/obra-etapa3/roteiro/prints.py` (13 de 13 conferências certas). Todos abertos e olhados; o que estava
feio foi consertado (ver commit `24e3298`).

## Ressalvas

1. **"Inserir" página na grade não foi feito** (D-487): precisa de página que não vem do PDF de entrada.
2. **Junção com a etapa 10a:** `core/pipeline.py` mudou só para passar a `pagina` às funções de "sozinho", mas em
   linhas vizinhas às do corte (`_geometria`, `_corta_pelo_conteudo`, `_corta_pela_borda`): pode dar conflito
   pequeno de texto.
3. **Numeração:** D-481 a D-491 são minhas (a gerente avisou que a do tique do menu foi para D-492).
4. **Os testes antigos de tela** que dependiam da tela "O que fazer" foram traduzidos para o caminho novo pelo
   ajudante `tests/ajudante_do_automatico.py` (`rodar_como_o_conferir`): o que cada um protege ficou igual, mas
   alguns mudaram de sentido onde o comportamento mudou de propósito — ex.: desligar o Dividir não recomeça mais a
   conferência (o teste agora prova que o trabalho fica e o Ctrl+Z desfaz na página certa); "começar de novo"
   abre o livro limpo na área de trabalho (o projeto.json gravado é o do livro limpo).
5. **A janela grande e o teste de janela de verdade:** o PrintWindow pegava o meio da janela grande sem pintar logo
   que ela abre (o grab do Qt mostra certo); o roteiro passa pela etapa de novo antes do print. Não vi isso na
   tela de verdade, mas o Samuel pode ver ao abrir.
6. **A velocidade foi medida com outros agentes no PC** (ver a tabela); a medida que vale é a da gerente.
7. **A página da capa do Boécio aparece alaranjada na área de trabalho depois de Rodar** (`depois-08`): medi o
   desenho do PDF e a cor é a mesma do original (a média dos canais não muda); parece a cor da marcação de
   gravura/foto por cima da página (a etapa "Gravuras e fotos" da receita marca a capa). Não é desta etapa, mas
   fica anotado para o Samuel olhar.
8. **teste_interface.py / teste_medidor.py** continuam quebrados como já estavam no código antigo (não é desta
   etapa).

## Commits (ramo `obra-etapa3-2026-10-26`)

- `c8b3717` Etapa 3 da obra: ONDE-PAREI com as decisões que a tarefa precisa cumprir
- `4d535ab` Etapa 3: o Automático no núcleo (etapas por página, core/automatico.py, desfazer de lista inteira)
- `e2321b1` Etapa 3: o livro abre direto na área de trabalho; painel Automático e janela grande de verdade
- `1ac35aa` Etapa 3: provas das decisões (tests/test_decisoes_automatico.py, 23 casos)
- `84b57a1` Etapa 3: testes de tela adaptados ao caminho novo (ajudante rodar_como_o_conferir)
- `3dc3f36` Etapa 3: mais testes de tela no caminho novo; grupo Gravuras e fotos com 'Achar' e 'Mais opções'
- `15bb9e1` Etapa 3: testes do recomeço, da força sozinha e das receitas no caminho novo
- `987691a` Etapa 3: test_trabalho_nao_se_perde no caminho novo (o trabalho não se perde continua protegido); cancelar marca a medida já acabada
- `569441f` Etapa 3: teste_botoes.py no caminho novo (testar_automatico com as promessas); lista 'Rodar em:' não fica ligada depois de fechar a janela grande
- `e3952d8` Etapa 3: gerar_prints, teste_interface, teste_ampliar e teste_medidor no caminho novo (Automático no lugar do analisar)
- `ad67328` Etapa 3: test_paineis (painel Automático de verdade) e test_trocar_de_livro_grava (começar de novo abre o livro limpo na área de trabalho) no caminho novo; medir_abrir.py
- `f8e05c2` Etapa 3: escolhas da gerente (D-014) anotadas no DECISOES, D-481 a D-491
- `82f41d1` Etapa 3: bateria de promessas no caminho novo; defeito A (filtro à mão fora do PDF) resolvido
- `24e3298` Etapa 3: acertos vistos nos prints da janela de verdade; prints e velocidade de abrir
- (este ONDE-PAREI final)
