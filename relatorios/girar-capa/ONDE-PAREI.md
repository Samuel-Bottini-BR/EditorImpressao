# ONDE-PAREI — girar num livro dividido com uma folha inteira (a capa aberta): D-638 e D-640

Ramo `girar-capa-2026-11-07` (saiu de `obra-2026-10-26`, 6904a634). Cópia: `.claude/worktrees/girar-capa`.
Item 2 da fila de consertos aprovada pelo Samuel em 07/11/2026.

## Decisões que esta tarefa precisa cumprir

- **D-638 (06/11/2026)**, pergunta B do agente girar-pagina: "Agora você está na capa inteira e escolhe girar "todas
  as folhas". Hoje, as outras folhas do livro giram inteiras, e volta a confusão do seu print: cada página com um
  pedaço da vizinha. Sugestão: elas giram página por página, sem confusão. Pode ser assim?" → Samuel: **"Pode ser,
  mas isso vai acontecer se elas estiverem cortadas e se não estiverem cortadas né?"** (gerente: vale só para as
  folhas divididas; as não divididas giram inteiras; o corte das bordas não muda nada, porque o giro vem antes do
  corte; sem objeção dele). Livro: **"Estando numa folha inteira (ex.: a capa aberta), "todas as folhas", "daqui em
  diante", "só as pares" e "só as ímpares" giram as folhas divididas página por página (cada página sozinha, como
  na D-636), e as folhas não divididas giram inteiras, como hoje. Nenhuma página fica com pedaço da vizinha. Vale
  com ou sem o corte das bordas."**
- **D-640 (06/11/2026)**, pergunta A ("Você está numa página do miolo e escolhe girar "todas as páginas". Todas as
  páginas do livro giram, menos a capa inteira, que fica como está. Pode ser assim?") → **"Todas giram, mas porque
  a capa inteira não gira?"** · gerente sugeriu que gire também → **"Não sei o que responder - vamos deixar como
  gira todas as paginas"**. Livro: **"Numa folha dividida, "todas as páginas" gira também as folhas que não foram
  divididas, como a capa aberta (inteira): todas giram."** Se a capa já estava certa, gira-se ela de volta com "só
  esta folha".
- **Não podem mudar:** D-618 ("ele deveria girar o conteudo só que é da pagina cortada [...] Ele gira as duas folhas
  ao mesmo tempo, faz uma confusão com as paginas": numa folha dividida o girar vira só a página da tela) e D-636
  ("1- pode ser, só garanta que não crie mais problemas fazendo isso [...]": em todas as opções do "aplicar em",
  cada página gira sozinha). Também D-035 ("Todas ficam viradas como a folha da vez"), D-036/D-556 (aviso "vá a uma
  folha par"), D-367 (a lista diz "folha"), D-371 ("daqui em diante"), D-053 (canto gira só esta), D-487/D-334
  (girar na grade), e o "girar - sim" da D-618 (folha inteira gira como uma foto, levando o corte à mão, o tamanho
  escolhido e o lugar do conteúdo).
- **D-605 (03/11):** "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e
  testado, coisas novas não podem criar novos problemas". **07/11:** "só não pode arrumar um problema e criar
  outro." e "não que vai sair o livro perfeito, mas que as funcionalidades funcionam. E não dão erro uma nas outras".
- **D-637 / §11.9:** a seção "Como fica para quem usa e no livro" (abaixo), escrita antes de mexer.

## O que já está escolhido e testado aqui

Arquivos que vou tocar: `core/girar.py` (contas novas, sem mudar as que existem) e `ui/tela_conferir.py`
(`_girar_folhas` e `_girar_as_paginas`). Não mexo em `ui/widgets/barra_girar.py`, no menu, no canto, na grade
"ver todas" nem no pipeline.

Decisões já construídas e testadas no girar: D-030, D-035, D-036, D-049, D-053, D-361, D-367, D-371, D-487, D-556,
D-601, D-609, D-618 (com o "girar - sim"), D-636.

Testes que já existem e não podem mudar: `tests/test_girar.py`, `tests/test_girar_na_tela.py`,
`tests/test_girar_cartoes_e_previas.py`, `tests/test_decisoes_girar_pagina.py` (D-618),
`tests/test_decisoes_girar_paginas_aplicar_em.py` (D-636), `tests/test_ajustar_pedaco_na_folha_girada.py`,
`tests/test_decisoes_automatico.py::test_d334_acoes_nas_escolhidas_girar_e_tirar`, `tests/test_decisoes_dividir*.py`
(`test_lista_3_1_*`, `test_d495_*`, `test_d609_*`), `tests/test_paineis_na_tela.py`, `tests/test_decisoes.py`,
`tests/test_recomeco_limpa_o_historico.py`, `tests/test_pipeline_folha.py`, `tests/test_corte_previa_igual_pdf.py`,
`tests/test_decisoes_tira_*.py`, e os `tests/test_decisoes*.py` todos.

**Atenção (achado antes de mexer; depois do conserto apareceram mais dois, ver "Para a gerente": são cinco):** três testes do `tests/test_decisoes_girar_paginas_aplicar_em.py`, escritos pelo
agente girar-pagina enquanto as perguntas A e B estavam abertas, cobram justamente o comportamento que a D-638 e a
D-640 mandam trocar:
- `test_reversao_d636_todas_as_paginas_gira_cada_pagina_sozinha`: cobra `rotacoes == [0, 0, 0]` (a folha inteira, a
  "capa", não gira com "todas as páginas"). A D-640 manda girar.
- `test_d636_folha_inteira_fica_como_esta`: na folha inteira, "todas as folhas" cobra `rotacoes == [90, 90, 90]` e
  nenhuma página girada (as folhas divididas giram como folha, a confusão do a-70). A D-638 manda girar página por
  página. A própria docstring diz: "o que isso faz nas folhas divididas é a pergunta 3 do ONDE-PAREI".
- `test_d636_o_pdf_sai_com_cada_pagina_deitada_inteira`: cobra que a página 5 (a folha inteira) sai igual depois de
  "todas as páginas". A D-640 manda girar.
Não vou mudar esses testes (regra). Eles vão falhar depois do conserto, porque a decisão do Samuel mudou o que eles
cobram. Proposta para a gerente na seção "Para a gerente" (no fim).

## Como fica para quem usa e no livro (D-637; escrito ANTES de mexer, 07/11)

Exemplo: Gradus Primus, "dividir todas" na ferramenta Dividir, e a folha 1 (capa e contracapa abertas) juntada com
"não dividir esta". A página 1 é a capa aberta inteira; as páginas 2 em diante são metades de folhas divididas.

**Situação 1 — na capa (página 1), "todas as folhas" + ¼ à esquerda.**
- Antes (hoje): o quadro diz "Girar a folha" (certo, é folha inteira). A capa fica em pé, inteira (certo). Mas TODAS
  as outras folhas do scan giram inteiras e depois são divididas de novo pela mesma linha: cada página vira meia
  folha deitada com pedaços das duas páginas (a confusão do print a-70). O PDF sai assim, misturado.
- Depois: a capa gira inteira, como hoje (fica em pé, como uma foto, levando o corte à mão se houver). As outras
  páginas giram cada uma sozinha, ¼ à esquerda, inteiras, sem pedaço da vizinha; a linha da divisão não muda. O
  mesmo com "daqui em diante", "só as pares" e "só as ímpares" (contam FOLHAS, como a lista diz "folha" ali): de
  cada folha dividida do alcance, as duas páginas giram, cada uma sozinha. Com ou sem o corte das bordas.
  "só as pares" na capa (folha 1, ímpar): avisa "vá a uma folha par" e não gira, como hoje.
  Um Ctrl+Z desfaz tudo de uma vez (a capa e as páginas voltam ao giro de antes); Ctrl+Y refaz.

**Situação 2 — no miolo (ex.: página 14), "todas as páginas" + ¼ à esquerda.**
- Antes (hoje, desde a D-636): o quadro diz "Girar a página"; todas as páginas das folhas divididas deitam, cada uma
  sozinha (certo). A capa inteira fica como estava (em pé, sem girar).
- Depois: o mesmo, e a capa aberta também gira, inteira (a folha larga fica em pé, como uma foto). A frase do
  histórico conta a capa junto ("todas as N páginas"). Um Ctrl+Z desfaz tudo; Ctrl+Y refaz. Se a capa já estava
  certa, o Kaique vai à capa e gira de volta com "só esta folha".
- "daqui em diante", "só as pares" e "só as ímpares" no miolo: continuam como hoje (a D-640 fala só de "todas as
  páginas"; perguntei abaixo).

**O que não muda:** "só esta página"/"só esta folha", os botões do canto (giram só a da tela), Ctrl+Seta e o menu
Página com "só esta", a grade "ver todas", as palavras do quadro e da lista, o aviso de pares/ímpares, o giro numa
folha inteira de um livro sem nenhuma folha dividida (igual a hoje, nenhuma página dividida para girar).

**No PDF que sai:** Situação 1: a capa sai girada como hoje; as páginas das folhas divididas saem deitadas, cada uma
com o seu conteúdo inteiro (a mesma imagem que sairia sem o giro, girada), em vez das meias folhas misturadas.
Situação 2: as páginas como hoje, e a capa sai girada (em pé) em vez de igual.

**O que pode dar problema (conferir na entrega):** o Ctrl+Z tem de devolver a capa e cada página ao giro (e ao corte à
mão) que tinham; as miniaturas e a prévia das páginas que mudaram têm de ser refeitas; a página com giro guardado
não pode ganhar giro numa folha inteira (o achado b12d6f61 do girar-pagina: a capa NÃO recebe giro de página, só a
rotação da folha); o Dividir em "Duas lado a lado" numa folha dividida continua como hoje (ver perguntas).

## Perguntas para o Samuel

1. **(D-640, "daqui em diante", "só as pares", "só as ímpares" no miolo.)** A D-640 fala de "todas as páginas". No
   miolo, com "só as ímpares", a capa (página 1, ímpar) continua sem girar, como hoje. Fiz só o "todas as páginas"
   (o que ele mandou). Sugestão: deixar assim. Pode ser?
   **Respondida (Central, 07/11/2026): "Giram também".** Feito (ver "Segunda parte" abaixo).
2. **(D-638, a ferramenta Dividir em "Duas lado a lado" numa folha dividida.)** Ali a tela mostra a folha inteira com
   a linha, e o girar continua girando folhas (D-618, ressalva). Com "todas as folhas" ali, continua como hoje (as
   folhas divididas giram inteiras). Não mexi: a D-638 fala de estar "numa folha inteira (ex.: a capa aberta)".
   **Respondida (Central, 10/11/2026, D-662): "Página por página também".** Feito para "todas as folhas" (ver
   "Terceira parte" abaixo).
3. **(nova, 10/11; para a gerente levar à Central, com print)** No Dividir com "Duas lado a lado", "daqui em diante",
   "só as pares" e "só as ímpares" também giram página por página, como o "todas as folhas"? Hoje continuam girando as
   folhas inteiras (a confusão das tiras). Sugestão: sim. Não mexi (a D-662 fala só de "todas as folhas").

## Segunda parte (07/11): as respostas do Samuel na Central

**1. "Posso trocar 5 testes antigos que cobram o jeito de girar que você mandou mudar?" → "Sim, pode trocar
(recomendo)"** (Central, `girar-capa-testes-antigos`, 07/11). Aplicada a proposta, só aquelas linhas, em commit
separado (16e752e7), com comentário citando a D-638/D-640 e a autorização.

**2. "No miolo, "daqui em diante", "só as pares" e "só as ímpares" giram também a capa aberta?" → "Giram também".**
- *Como fica para quem usa e no livro (escrito antes de mexer):* no miolo (página de folha dividida), com "daqui em
  diante", "só as pares" ou "só as ímpares", a folha inteira (a capa aberta, um encarte) cuja página está no grupo
  escolhido gira também, inteira, como no "todas as páginas", virada como a página da vez. As páginas divididas
  continuam girando cada uma sozinha. Ex.: Gradus, página 3, "só as ímpares" + ¼ à esquerda → a capa (página 1) gira
  em pé, e as páginas 3, 5, 7... deitam; a 2, 4, 6... não mudam. Um Ctrl+Z desfaz tudo; Ctrl+Y refaz. No PDF, a capa
  sai girada junto. Não muda: "só esta página", o canto, a grade, o aviso de pares/ímpares (na página ímpar com "só
  as pares" avisa e nada gira, nem a capa), a capa com "daqui em diante" a partir de uma página depois dela (não gira:
  o "daqui em diante" começa onde se está).
- *A conta de par/ímpar da folha inteira:* não ficou dúvida. No miolo o "aplicar em" já conta PÁGINAS pelo número
  que a tela mostra ("página 1 de 139"; D-636, `girar.folhas_do_alcance` sobre a lista de páginas). A capa aberta é
  a página 1 da lista: ímpar. Usei essa mesma conta, sem conta nova.
- *Feito:* provas novas (3bfa53af; 6 de reversão falham no código de 16e752e7, `reversao-giram-tambem-no-codigo-antigo.txt`)
  e o código (df8db4ec: `_com_as_folhas_inteiras_tambem` recebe o "aplicar em" e pega as folhas inteiras do grupo).
  A prova provisória `test_d640_as_outras_escolhas_do_miolo_continuam_como_antes` (escrita nesta tarefa enquanto a
  pergunta estava aberta) foi trocada pelas novas, no commit das provas.
- **Mais um teste antigo cobra o jeito antigo (não mexi nele):**
  `tests/test_decisoes_girar_paginas_aplicar_em.py::test_d636_daqui_em_diante_conta_paginas` cobra
  `_rotacoes(projeto) == [0, 0, 0]` depois de "daqui em diante" na página 3; nesse livro a folha 3 é inteira (página
  5), fica DEPOIS da página 3 e, pela resposta "Giram também", gira: `[0, 0, 90]`. Proposta (precisa de autorização,
  como a primeira): `relatorios/girar-capa/proposta-teste-daqui.diff` (uma linha + comentário); com ela o arquivo
  passa inteiro (10 passed, numa cópia à parte).

**3. Dividir com "Duas lado a lado":** sem resposta; não mexi.

**Testes da segunda parte (df8db4ec):**
- PC, um arquivo por vez, sem janela na tela (série "Giram tambem" em `resultado-testes.txt`): 70 arquivos; 69 passam
  inteiros; no outro (`test_decisoes_girar_paginas_aplicar_em.py`, 9 de 10) falha só o teste antigo do "daqui em
  diante" acima. `test_decisoes_girar_capa.py`: 26 passed.
- GitHub, suíte 42391132998 (em ece01b15): botões/prints da janela real e as partes 2, 3 e 4 passaram; a parte 1 e a 5
  falharam em: o teste antigo do "daqui em diante" (esperado) e `test_decisoes_so_as_letras.py::test_d148_...` ("não
  aconteceu a tempo", o instável conhecido; no PC passou nas duas séries, 5 passed, e passou na suíte 42381756807).
  Reenviei só as partes que falharam (mesmo número de rodada): a parte 1 passou (o `test_d148` passou); a parte 5
  falhou só no teste antigo do "daqui em diante". Resultado final da 42391132998: tudo passa, menos esse teste.
- Velocidade: não rodei de novo. Nesta parte o `core/` só mudou em comentários; o código mudado é o do clique, em
  `ui/tela_conferir.py`. O filtro 42381758932 (em 99d7d782) deu "nada mais lento".
- Imagens da situação 3 (Gradus, página 3, "só as ímpares" + ¼ à esquerda): `s3-pdf-antes-e-depois.png` e
  `s3-janela-antes-e-depois.png`. Antes, a capa ficava deitada (sem girar); agora ela gira com as ímpares. Ctrl+Z
  devolve tudo e Ctrl+Y refaz (`estado.json` da geração: depois do Ctrl+Z nenhuma folha nem página girada).

## Terceira parte (10/11): D-662 e D-663

Antes de começar: juntado o `obra-2026-10-26` atual (cc5d9850, com o conserto D-659/D-661 da gravura) no ramo, sem
conflito (8f682eaa).

**D-663** (Central, `girar-capa-teste-daqui`: "Posso trocar o teste antigo do "daqui em diante"?" → "Sim, pode trocar
(recomendo)"): aplicada só a proposta `proposta-teste-daqui.diff`, num commit (269f05f3). O arquivo passa inteiro (10).

**D-662** (Central, `girar-capa-dividir-duas`: "No Dividir, com "Duas lado a lado", "todas as folhas": gira a folha
inteira ou página por página?" → "Página por página também").
- *Como fica para quem usa e no livro (escrito antes de mexer):* no Dividir com "Duas lado a lado", numa folha
  dividida (ex.: Gradus, folha 10, páginas 18 e 19), "todas as folhas" + ¼ à direita: cada página do livro gira
  sozinha e inteira, virada como a página da tela; a capa aberta gira inteira; a linha azul não muda. A tela grande do
  Dividir continua mostrando a folha do scan em pé (é o scan, com a linha); a tira de páginas das outras ferramentas e
  o PDF mostram as páginas deitadas, cada uma inteira. Um Ctrl+Z desfaz tudo; Ctrl+Y refaz. No PDF: cada página sai a
  mesma imagem de antes, girada, em vez de uma tira com metade de duas. Não muda: o girar fora do Dividir, o Dividir
  com "Uma página", "só esta folha" no Dividir (gira a folha, D-618), as palavras "Girar a folha"/"todas as folhas",
  a D-638 na capa, e "daqui em diante"/pares/ímpares no Dividir (pergunta 3 acima).
- *Como:* (c76d4b97) em `ui/tela_conferir.py`, `_girar_folhas` desvia o "todas as folhas" para o MESMO
  `_girar_as_paginas` de fora do Dividir (o caminho da simulação de 09/11), com a página da folha da tela como página da
  vez (`_pagina_da_folha_dividida_no_dividir_em_duas`). `_girar_as_paginas` e `_com_as_folhas_inteiras_tambem`
  ganharam o parâmetro `atual` (None = a da tela, o caso de sempre). `core/` não mudou.
- *Provas:* `tests/test_decisoes_girar_dividir_duas.py` (10). No código sem o conserto (3216b885): 6 de reversão
  falham, 4 passam (`reversao-d662-no-codigo-antigo.txt`); no novo: 10 passam.
- *Gradus* (cópia de 70 folhas, a mesma das provas de 09/11; sem janela na tela): `d662-resumo.png`, `d662-1-antes.png`,
  `d662-2-fica.png` (sem o conserto), `d662-3-pagina.png` (com o conserto); números em `d662-estado-*.json`. Medida no
  PDF: sem o conserto as páginas 18 a 21 saem tiras (251x702 em vez de 496x354); com o conserto, inteiras e deitadas
  (diferença 0,02 a 0,09 de 255 para a página de antes girada). A capa gira inteira nos dois. Ctrl+Z: nada girado;
  Ctrl+Y: de novo 1 folha (a capa) e 138 páginas.
- *Testes:* PC, um arquivo por vez, sem janela na tela (série "D-662 e D-663 (10/11)" em `resultado-testes.txt`, commit c76d4b97): 73 arquivos (os do girar, do Dividir, da tira, do PDF, dos cadernos e todos os `test_decisoes*.py`), todos passam inteiros, nenhuma falha. GitHub, suíte 42814866808 (as 5 partes e os botões/prints da janela real): tudo passou. Nenhum teste antigo além do autorizado (D-663) foi mudado. Velocidade: filtro 42814872526 (obra-2026-10-26 → girar-capa e8a8fb4c): "igual (dentro do vai-e-vem)"; abrir +0,3%, trocar de página -0,6%, Mágico pro +0,2%, Preto e branco -0,7%. Nada mais lento (o conserto só roda no clique de girar; `core/` não mudou).

## Andamento

- [x] worktree e ramo criados (07/11); lidos CLAUDE.md, implementador.md, o ONDE-PAREI e o relatório do girar-pagina,
  D-618/D-636/D-638/D-640
- [x] ONDE-PAREI antes de mexer (d4e8c163)
- [x] teste novo `tests/test_decisoes_girar_capa.py` (19 provas) rodado no código de antes (6904a634): 15 falham pelo
  defeito, 4 passam (as que conferem o que não pode mudar) — `reversao-no-codigo-antigo.txt` (e86c5851)
- [x] conserto (99d7d782): `core/girar.campos_do_giro_numa_folha_inteira` (conta nova) e, em `ui/tela_conferir.py`,
  `_girar_as_divididas_pagina_por_pagina` (D-638) e `_com_as_folhas_inteiras_tambem` (D-640)
- [x] PC, um arquivo por vez (`rodar_testes.ps1`, saída em `resultado-testes.txt`): 70 arquivos (o novo, os do girar,
  da tira, do Dividir, do PDF, dos cadernos e os `test_decisoes*.py`; contagem corrigida em 07/11: eram 70, não 72);
  68 passam inteiros; nos outros 2 falham só os 5 testes
  antigos da seção abaixo
- [x] proposta para os 5 testes antigos conferida numa cópia à parte: com ela, 10 passed e 20 passed
- [x] imagens antes/depois (sem janela na tela; Gradus copiado): `s1-pdf-antes-e-depois.png`,
  `s2-pdf-antes-e-depois.png`, `s1-janela-antes-e-depois.png`, `s2-janela-antes-e-depois.png`
- [x] GitHub, suíte 42381756807 (em 99d7d782): partes 1, 2 e 5 e os botões/prints da janela real passaram; as partes 3
  e 4 falharam só nos mesmos 5 testes antigos
- [x] GitHub, filtro de velocidade 42381758932 (obra-2026-10-26 → girar-capa 99d7d782): nada mais lento. Veredito
  "parece mais rápido" (abrir -2,1%, trocar de página -4,9%, no limite do vai-e-vem; Mágico pro -0,4% e Preto e branco
  -0,9%, iguais). A mudança só roda no clique de girar: a diferença é vai-e-vem, não ganho.
- [x] a gerente decidiu sobre os 5 testes antigos (D-644, 16e752e7) e o do "daqui em diante" (D-663, 269f05f3)
- [x] D-662 no Dividir com "Duas lado a lado" ("todas as folhas"): c76d4b97, provas, Gradus, testes (Terceira parte)
- [ ] pergunta 3 (daqui em diante/pares/ímpares no Dividir com "Duas lado a lado"); conferência com a janela aberta
  (outro agente); depois, a gerente junta

## Para a gerente: cinco testes antigos cobram o que a D-638/D-640 trocam (não mexi neles)

Depois do conserto falham 5 testes antigos, todos pelo motivo da decisão nova (PC e GitHub iguais). Foram escritos
pelo agente girar-pagina enquanto as perguntas A e B estavam abertas:
1. `tests/test_decisoes_girar_paginas_aplicar_em.py::test_reversao_d636_todas_as_paginas_gira_cada_pagina_sozinha`:
   `assert _rotacoes(projeto) == [0, 0, 0]` (a folha inteira não gira com "todas as páginas"). Com a D-640 ela gira:
   `[0, 0, 270]`.
2. `...::test_d636_todas_ficam_viradas_como_a_da_vez_e_o_ctrl_z_devolve_cada_uma`: cobra a frase "todas as 4 páginas,
   viradas como a página 2". Com a D-640 a folha inteira gira junto e a frase conta 5 ("todas as 5 páginas"). O
   resto do teste (as 4 páginas em 270, Ctrl+Z e refazer) passa.
3. `...::test_d636_folha_inteira_fica_como_esta`: na folha inteira, "todas as folhas" cobra `rotacoes == [90, 90, 90]`
   e nenhuma página girada (a confusão do a-70). Com a D-638: `rotacoes == [0, 0, 90]` e `giros == [90, 90, 90, 90, 0]`.
   A docstring dele já dizia: "o que isso faz nas folhas divididas é a pergunta 3 do ONDE-PAREI".
4. `...::test_d636_o_pdf_sai_com_cada_pagina_deitada_inteira`: cobra que a página 5 (a folha inteira) sai igual. Com
   a D-640 ela sai girada.
5. `tests/test_decisoes_girar_pagina.py::test_d618_d636_aplicar_em_todas_numa_folha_dividida_gira_as_paginas`: cobra
   `rotacoes == [0, 0]` ("A folha 2 (inteira) fica como está") depois de "todas as páginas". Com a D-640: `[0, 90]`.
Proposta (só se a gerente autorizar, em commit separado, com comentário citando a D-638/D-640): trocar só essas
linhas. O diff pronto está em `relatorios/girar-capa/proposta-testes-d636.diff` (5 trechos); com ele os dois arquivos
passam inteiros (10 passed, 20 passed, numa cópia à parte).

## Como cumpri cada decisão

- **D-638** ("Pode ser, mas isso vai acontecer se elas estiverem cortadas e se não estiverem cortadas né?"):
  `test_reversao_d638_na_capa_todas_as_folhas_gira_as_divididas_pagina_por_pagina`, `..._daqui_em_diante_...`,
  `..._so_as_pares_...`, `..._so_as_impares_...` (as quatro escolhas da lista, contadas em folhas);
  `test_d638_vale_com_e_sem_o_corte_das_bordas_na_tela[cortar|endireitar]` e
  `test_reversao_d638_o_pdf_sai_com_a_capa_e_cada_pagina_girada[False|True]` (o PDF com o corte das bordas desligado e
  ligado: cada página sai a mesma imagem girada, sem pedaço da vizinha); `test_d638_todas_ficam_viradas_como_a_capa_e_o_ctrl_z_e_o_ctrl_y`
  e `test_d638_o_corte_a_mao_gira_junto_e_o_ctrl_z_devolve` (Ctrl+Z e Ctrl+Y pela porta das teclas). Gradus: 70 folhas,
  na capa "todas as folhas" + ¼ à esquerda → 1 folha girada (a capa) e 138 páginas giradas sozinhas, uma ação só;
  Ctrl+Z volta tudo, Ctrl+Y refaz (`s1-*.png`).
- **D-640** ("vamos deixar como gira todas as paginas"): `test_reversao_d640_todas_as_paginas_gira_tambem_a_capa`,
  `test_d640_ctrl_z_e_ctrl_y_devolvem_a_capa_e_as_paginas`, `test_reversao_d640_o_pdf_sai_com_a_capa_girada[False|True]`.
  Gradus: na página 14, "todas as páginas" + ¼ à esquerda → a capa gira inteira e as 138 páginas sozinhas
  ("todas as 139 páginas, viradas como a página 14"); Ctrl+Z/Ctrl+Y (`s2-*.png`).
- **D-618 / D-636 não mudaram:** `test_d640_so_esta_pagina_no_miolo_continua_girando_so_ela`,
  `test_d638_so_esta_folha_na_capa_continua_girando_so_a_capa` (e o canto), `test_d640_as_outras_escolhas_do_miolo_continuam_como_antes`,
  `test_d638_so_as_pares_na_capa_avisa_e_nao_gira` (D-036); `test_decisoes_girar_pagina.py` (19 de 20; o 20º é o item 5
  acima) e os 6 testes da D-636 que não tratam da folha inteira passam; os do girar, da tira e da grade passam.
- **D-605 / "só não pode arrumar um problema e criar outro":** num livro sem folha dividida o caminho é exatamente o de
  antes (a conta nova só entra quando há folha dividida no alcance); nenhum teste antigo foi mudado; os 5 que falham
  cobram o comportamento que o Samuel mandou trocar (seção acima).
- **D-637:** a seção "Como fica para quem usa e no livro" foi escrita antes de mexer e conferida nas imagens (janela
  desenhada na memória e PDF). Problema novo: nenhum visto.
