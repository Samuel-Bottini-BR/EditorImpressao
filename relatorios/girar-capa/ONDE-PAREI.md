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

**Atenção (achado antes de mexer):** três testes do `tests/test_decisoes_girar_paginas_aplicar_em.py`, escritos pelo
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
2. **(D-638, a ferramenta Dividir em "Duas lado a lado" numa folha dividida.)** Ali a tela mostra a folha inteira com
   a linha, e o girar continua girando folhas (D-618, ressalva). Com "todas as folhas" ali, continua como hoje (as
   folhas divididas giram inteiras). Não mexi: a D-638 fala de estar "numa folha inteira (ex.: a capa aberta)".

## Andamento

- [x] worktree e ramo criados (07/11)
- [x] lidos CLAUDE.md, implementador.md, o ONDE-PAREI e o relatório do girar-pagina, D-618/D-636/D-638/D-640
- [ ] teste de reversão escrito e falhando no código de antes
- [ ] conserto
- [ ] testes no PC, um arquivo por vez
- [ ] imagens antes/depois
- [ ] GitHub (suíte e velocidade)

## Para a gerente

(ver "Atenção" acima: três testes antigos cobram o que a D-638/D-640 trocam; proposta no fim, depois do conserto)
