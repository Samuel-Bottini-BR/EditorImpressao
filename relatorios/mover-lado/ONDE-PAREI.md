# ONDE-PAREI — D-612: o Mover funciona em "Duas lado a lado" (04/11/2026)

Ramo `mover-lado-2026-11-04` (saiu de `obra-2026-10-26`, ponta `dd7a648c`). Cópia:
`D:\programas\EditorImpressao\.claude\worktrees\mover-lado`.

**Situação (04/11, fim):** feito e testado no PC (19 arquivos de teste, piloto 20/20). Commits `6d503cde`
(o conserto), `1aa98650` (a roda nos pares, achado do piloto), `bb11ff93` (piloto e prints). Rodada do GitHub
41856247413 (ver `relatorio.md`). Relatório: `relatorio.md` (.html/.pdf).

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

1. Clicar na outra página do par só a escolhe (como já era); o arrasto vale do próximo aperto. Quer que já
   arraste no mesmo aperto? (print `prints/p09-outra-pagina-do-par.png`)
2. Os cantos azuis só na página da vez (como na "Uma página"). Está bom? (print `prints/p03-F-mover-nos-pares.png`)
3. Ainda em aberto, da gerente: o mesmo vale para Cortar, Endireitar, marcar e "antes / depois"? (não mexidos)

## Como cumpri cada decisão

Ver `relatorio.md`, seção "Decisões: como cumpri cada uma".
