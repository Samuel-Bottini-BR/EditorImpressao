# ONDE-PAREI — D-612: o Mover funciona em "Duas lado a lado" (04/11/2026)

Ramo `mover-lado-2026-11-04` (saiu de `obra-2026-10-26`, ponta `dd7a648c`). Cópia:
`D:\programas\EditorImpressao\.claude\worktrees\mover-lado`.

**Situação (05/11): tudo feito; junção da obra, PC e GitHub feitos — ver a última seção.** Antes: **Situação (04/11, fim):** feito e testado no PC (19 arquivos de teste, piloto 20/20). Commits `6d503cde`
(o conserto), `1aa98650` (a roda nos pares, achado do piloto), `bb11ff93` (piloto e prints). Rodada do GitHub
41856247413 (ver `relatorio.md`). Relatório: `relatorio.md` (.html/.pdf). Entrega do Mover mandada à gerente.

**Segunda parte (04/11, Samuel "1- sim"):** Cortar, Endireitar e marcar em "Duas lado a lado" feitos
(`41963824`), testes no PC passando (`testes-pc-2.txt`), piloto 15/15 (`piloto_ferramentas.py`).
~~Parado na pergunta do "antes / depois"~~ — respondida ("Ok, pode ser assim o antes e depois").

**Terceira parte e defeito do pincel (04/11, fim):** "antes / depois" feito (`18cb692e`, `f85eb4b6`);
defeito do "tamanho" de cima (print a-65) feito em commit separado (`033560c9`); pilotos 16/16
(`piloto_antes_depois.py`); testes no PC em `testes-pc-3.txt`. GitHub: ver `relatorio.md`.
Perguntas ainda abertas com a gerente: (a) arrastar a outra página do par no mesmo aperto; (b) cantos só
na página da vez; e a nova do rótulo "antes" em cima do lado do "depois" (print p406).

## Decisões que esta tarefa precisa cumprir

- **D-612** (04/11): pergunta "Ao escolher Mover, Cortar, Endireitar ou marcar, a tela passa sozinha para Uma
  página?" → "1 - ele tem que funcionar com paginas lado a lado também". Na prática: o Mover (arrastar, puxar o
  canto, o número do tamanho) funciona também com a vista em "Duas lado a lado", nas páginas dos pares; **a vista
  não muda sozinha**. Cortar, Endireitar, marcar e "antes / depois": **ainda não** (perguntado ao Samuel).
- **D-605** (03/11): "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que
  já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os
  agentes precisam ler".
- **D-008** (22/09 e 26/10): "quero conseguir redimensionar o conteudo tambem" · "a ferramenta de mover não deveria
  estar vinculada ao corte de bordas, deveriam ser duas coisas independentes" · "como é no photoshope, que você
  arrasta a hora que quiser e aumenta a hora que quiser".
- **D-541**: arrastar em qualquer lugar da área branca ou da página move (ao vivo); o meio do conteúdo fica dentro
  da área branca; puxar um dos quatro cantos aumenta/diminui na mesma proporção (5% a 4 vezes); o número "Tamanho
  do conteúdo (%)" faz o mesmo; a vista se ajusta para mostrar a área branca e a página inteira, parada no arrasto.
- **D-540** (tecla F), **D-542** (Centralizar e ímã pelo impresso), **D-543**/**D-017** (parte de fora apagada,
  vermelha, com listras; aviso; nada diminui sozinho), **D-544** (Mover separado do Cortar), **D-545** ("usar em
  todas..."), **D-546**/**D-547** (o que cada tela mostra; o lado a lado mostra a página como sai no PDF),
  **D-056** (linhas de apoio, botão direito).
- Vista: **D-006** ("eu não quero padrão eu quero como opção um botão que eu clique e veja pagina lado a lado"; 202
  A pares rolando), **D-015** ("Uma página / Duas lado a lado" na barra de baixo e no menu Ver).
- Dividir: **D-601** (no Dividir, "Duas lado a lado" = a folha inteira com a linha), **D-609** (arrastar a linha na
  folha inteira), **D-610** (dividir em "Duas lado a lado" passa para "Uma página"), **D-611** (tira em pares com
  "Duas lado a lado"). Nada disso muda.

## O que já está escolhido e testado aqui

Telas/arquivos que vou tocar: `ui/tela_conferir.py` (`_acertar_a_vista_da_pagina`, `_acertar_o_lado_a_lado`, o
filtro da roda, o fechar do livro), `ui/widgets/paginas_lado_a_lado.py` (os pares) e, se precisar, uma folga
ajustável em `ui/widgets/visualizador.py` (o padrão continua o de hoje).

- **Mover (etapa 5):** `tests/test_decisoes_mover.py` (13 provas: tecla F, área branca, arrastar → PDF, canto, Kaique,
  Centralizar, %, voltar como veio, D-017 (3), linhas de apoio, "usar em todas...", F com foco na página).
- **Vista (etapa 6, 9b-2):** `tests/test_decisoes_ver.py` (D-015, D-058 menu Ver, D-007 abre em Uma página,
  `test_no_dividir_a_folha_inteira_continua`, pares do livro que vai sair, troca da etapa 4, D-343, antes/depois,
  zoom da barra, roda D-021, Page Down); `tests/test_decisoes_9b2.py` (D-570 zoom no lado a lado, D-571 100%,
  D-547 a página movida aparece como sai no PDF no lado a lado, D-568 a roda com zoom);
  `tests/test_zoom_no_ponteiro.py` (Ctrl+roda e Shift+roda no lado a lado).
- **Dividir:** `tests/test_decisoes_dividir_metade.py` (D-601, 6), `tests/test_decisoes_dividir_arrastar.py`
  (D-609, D-610), `tests/test_decisoes_tira_em_pares.py` (D-611), `tests/test_decisoes_dividir_linha.py`,
  `tests/test_decisoes_dividir.py`, `tests/test_dividir_na_tela.py`.
- **Visualizador e painéis:** `tests/test_visualizador.py`, `tests/test_previa_composta.py`,
  `tests/test_paineis_na_tela.py`, `tests/test_livro_aberto.py` (o folhear do livro aberto, mesma classe-mãe).

O que **não** pode mudar: em "Uma página" o Mover igual; no Dividir o "Duas lado a lado" é a folha inteira com a
linha; os pares continuam pares (clicar numa página faz dela a da vez, a roda rola, Ctrl+roda dá zoom no par); o
"antes / depois" igual; a vista não troca sozinha.

## Plano

1. Teste de reversão em `tests/test_decisoes_mover_lado.py`: arrasto e canto com a MÃO (no que está à vista no
   lugar da página da vez nos pares), vindo do Dividir em "Duas lado a lado" e clicando "Duas lado a lado" no
   Mover; falha em `dd7a648c`.
2. Conserto: com a ferramenta Mover e a vista "Duas lado a lado" (fora do Dividir, sem "antes / depois"), a peça
   da ferramenta (o mesmo visualizador do Mover, com tudo ligado) fica no lugar da página da vez dentro dos pares;
   a outra página do par continua a prévia. Ao sair (Uma página, outra ferramenta, antes/depois, fechar o livro), a
   peça volta para o lugar dela. Para estender depois: uma lista `FERRAMENTAS_NO_PAR` (hoje só o Mover).
3. Testes no PC um arquivo por vez; piloto na janela de verdade com cópia do Gradus; GitHub uma vez no fim.

## Perguntas para o Samuel

Mantive como já era nos pares e na "Uma página" (nada novo decidido); perguntar para confirmar:

1. ~~Clicar na outra página do par só a escolhe (como já era); o arrasto vale do próximo aperto. Quer que já
   arraste no mesmo aperto? (print `prints/p09-outra-pagina-do-par.png`)~~ — respondida ("ok"; D-612 a-75/a-76):
   feito em `d80f0380`.
2. ~~Os cantos azuis só na página da vez (como na "Uma página"). Está bom? (print `prints/p03-F-mover-nos-pares.png`)~~
   — respondida (D-612: os cantos só na página escolhida).
3. ~~Ainda em aberto, da gerente: o mesmo vale para Cortar, Endireitar, marcar e "antes / depois"? (não mexidos)~~
   — respondida ("1- sim"; "Ok, pode ser assim o antes e depois"): feito.
4. **Ainda aberta (o Livro não responde; mantive como já era):** no "antes / depois" com Mover, Cortar ou
   Endireitar, o rótulo "antes: Original" fica no canto esquerdo, em cima do lado onde a ferramenta age (o
   "depois"). Quer o rótulo em outro lugar? (prints `prints/p406-retangulo-no-depois.png` e
   `prints/p507-B-mover-131-antes-depois.png`)

## Como cumpri cada decisão

Ver `relatorio.md`, seção "Decisões: como cumpri cada uma".

**Tamanho da prévia nos pares (pedido do Samuel, 04/11):** feito em commit próprio ("nos pares a página da
ferramenta fica do tamanho da prévia"), teste `tests/test_decisoes_tamanho_no_par.py`, pilotos refeitos
(20/20, 15/15, 16/16), testes no PC em `testes-pc-4.txt`. GitHub final: ver `relatorio.md`.

GitHub final 41892321210 (em 4ede8fd5): 1 falha de tempo em test_gravura_na_aba_marcar (passa no PC 3/3). Entregue a gerente.

## Consertos do teste do Samuel (a-74 a a-78) e D-611 atualizada — retomado em 05/11

**Situação:** código feito em 04/11 (commits `18521ce8` B, `d80f0380` (a), `a5a6caa8` C/D-622, `6d62dd47` e
`3a78c5dd` D-611, `d7d08837` os dois testes antigos do Dividir com autorização da gerente; `af4005d2` piloto 10/10
e prints p501-p508). GitHub em `af4005d2`: rodada 41917141935 **passou inteira**. Pausado no fim da sessão; em 05/11
retomado: juntei a `obra-2026-10-26` (`37926156`, sem conflito: D-590 caixinha e D-617 parte 2), rodei de novo no
PC e no GitHub (resultado abaixo).

### Como cumpri cada decisão (consertos)

- **D-612** ("1 - ele tem que funcionar com paginas lado a lado também"; "Ok, pode ser assim o antes e depois"):
  - Mover, Cortar, Endireitar e marcar nos pares e no "antes / depois", agindo no "depois", sem a vista mudar:
    `test_decisoes_mover_lado` (7), `test_decisoes_ferramentas_lado` (9), `test_decisoes_ferramentas_antes_depois`
    (12), `test_decisoes_tamanho_no_par` (5); prints p03-p11, p301-p307, p401-p406.
  - Um clique escolhe a página clicada e já arrasta (a-75/a-76; no Endireitar só escolhe):
    `test_decisoes_par_escolhe_e_arrasta` (4; falharam 3 em `d2567fab`); print p503.
  - Os cantos só na página escolhida: `test_decisoes_mover_lado`; print p03.
  - O "antes / depois" mostra o depois do Mover, Cortar e Endireitar (a-77/a-78):
    `test_decisoes_antes_depois_da_ferramenta` (5; falharam 4 em `d2567fab`); prints p507, p508.
- **D-622** ("quando eu clicar fora da folha ele desseleciona [...] como no photoshop"): no Mover, clicar no cinza
  larga a escolha (cantos, contorno e o quadro azul do par somem); clicar na página escolhe de novo:
  `test_decisoes_d622_clicar_fora` (3; falharam em `d2567fab`); prints p504, p505, p506.
- **D-611** ("SIm, mas tem que verificar se vai ficar assim em todo os lugares né? a miniatura corresponder com o
  numero real"): no Dividir a tira junta pela folha; o número de cada miniatura é o da página; em Mão, Mover,
  Cortar, Endireitar, Retângulo e Dividir, nas duas vistas, com capa aberta e ordem mudada:
  `test_decisoes_tira_numero_real` (3; falharam 2 no código antigo), `test_decisoes_tira_marca_a_tela` (3);
  prints p501, p502. Testes antigos mudados (só a parte do Dividir, autorizado pela gerente, commit separado
  `d7d08837` com comentário citando a D-611): `test_decisoes_tira_em_pares.py` e
  `test_decisoes_tira_pares_juntas.py`. Nenhum outro teste antigo mudou (conferido com `git diff` contra a obra).
- **D-605**: provas das decisões (`tests/test_decisoes*.py`) e os testes dos arquivos tocados rodados no PC depois
  da junção: `testes-pc-7.txt`.

### Testes depois da junção (05/11)

PC (um arquivo por vez, Python do projeto principal `D:\programas\EditorImpressao\.venv`, a cópia não tem
.venv próprio): os 44 `tests/test_decisoes*.py` e mais 18 arquivos das telas tocadas (com o novo da obra
`test_caixinha_do_dividir_nao_volta`): **62 arquivos, todos passaram** (`testes-pc-7.txt`).

GitHub, rodada **41948184684** (em `37926156`): na 1ª tentativa a parte 4 caiu porque o Python travou
(código 3221225477, "access violation") em `test_dividir_ajustes_03_11.py`, depois de 6,5 s, sem falha de
teste. Esse arquivo não é da lista de instáveis conhecidos, mas passou nas rodadas 41917141935 (esta cópia),
41919662837 (obra) e 41918456756, e no PC 3 de 3 (9 passed cada). Repeti só a parte que caiu (tentativa 2):
**passou inteira** (o arquivo: 9 passed). Ressalva para a gerente: um travamento solto no GitHub, não repetido.
