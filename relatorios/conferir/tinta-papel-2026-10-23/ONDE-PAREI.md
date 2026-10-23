# Onde parei: verificador tp23, o papel da área "tinta com a cor" (item 2.18)

Pedido da gerente em 22/10/2026 (resposta do Samuel à tc23-1: "As duas: escolher o papel em cada área ('papel
branco' ou 'papel como o resto da página')").
Ramo `verif-tinta-papel-2026-10-23` (da ponta `0acf2c7` do `fase2-ferramentas-2026-10-22`; código em `b0af839` e
`3e95076`), worktree `.claude/worktrees/vtp23`. O "antes" é a worktree `.claude/worktrees/vtc23` (código `639136a`),
usada só para rodar, sem mexer no ramo dela. Junções `modelos` e `gabarito\paginas` (desfazer só com
`(Get-Item <junção>).Delete()`, nunca apagar a pasta).

## Situação (23/10/2026, depois dos ajustes 10 e 11)

Tudo conferido até `d4c820b`. **PRONTO PARA CONFERIR**, com ressalvas pequenas (nunca "aprovado").
Relatório: `relatorio-tp23.html` (.md/.pdf). Entrega para a gerente publicar: `conferencia.json` (id `tp23`, imagens
em `img/`, fora do git; o quadro novo é o `tp23-ajustes`, com as fotos `img/d4c_*`). **Não publiquei nada na Central.**

- [x] Somas de fábrica, 3e95076 x d4c820b: 36 de 36 iguais (`maquina/somas-comparacao-d4c820b.txt`)
- [x] Resposta 10: 5 jeitos x 3 filtros x 4 páginas, 60 de 60 como esperado (`maquina/somas-papel-comparacao.txt`)
- [x] Linha preta: pontos escuros 7342/5421/784/21198 -> 0 (`img-d4c/numeros-papel.json`, fora do git)
- [x] Projeto antigo abre igual: 4 de 4 (`maquina/abrir-antigo-d4c.log`)
- [x] Teste novo: 11 passam no novo; 4 falham no 3e95076 (`maquina/teste-d4c-*.txt`)
- [x] Janela: 31 de 31 e 8 de 8 (`maquina/janela-d4c/fase*/conferencias.txt`); roteiro de 22/10 consertado (duas listas)
- [x] GitHub lido: 39889891066 2206/0; velocidade 39886669584 nada mais lento (`maquina/github-d4c820b.txt`)
- Worktree `.claude/worktrees/vtp23-antes` (destacada em `3e95076`, junções `modelos` e `gabarito\paginas`) criada por
  mim nesta tarefa, só para rodar; pode ficar ou sair (junção só com `(Get-Item <junção>).Delete()`).

## Situação anterior (22/10, código 3e95076)

- [x] Somas de fábrica (papel branco), antigo x novo: 36 de 36 iguais (`maquina/somas-comparacao.txt`)
- [x] Projeto antigo abre como "papel branco": 4 de 4 (`maquina/projeto-antigo/abrir-antigo.json`)
- [x] "papel como o resto da página" no Original e no Melhorar: o retângulo some (`img/numeros-papel.json`)
- [x] As quatro combinações com A e B: a tinta é 100% igual à do papel branco
- [x] A área de cima manda: 36 de 36 faixas; o "tirar" do pincel: 6 de 6 (`img/cruzadas.json`)
- [x] Janela de verdade: 28 de 28, 7 de 7 (uma à mão), 11 de 11 no antigo

## Perguntas para o Samuel

Nenhuma. As b-10 e b-11 foram respondidas (10 e 11) e conferidas.

## Ressalvas

Ver `relatorio-tp23.md`.

## Ajustes das respostas 10 e 11 (pedido da gerente, 23/10/2026) - FEITO em 23/10

Decisões: b-10 "No Preto e branco, tirar a linha preta: as duas opções de papel saem iguais, com a letra limpa";
b-11: botão "manter a cor da tinta" (só o rótulo; a chave no projeto.json continua `tinta_cor`).
Código do Implementador B: ramo `fase2-ferramentas-2026-10-22`, ponta `d4c820b` (código `f8691be`, teste `c95ba9e`).
GitHub, ainda não lido por mim: suíte 39889891066 (a gerente diz 2206/0) e velocidade 39886669584 ("parece mais rápido").

### Já feito
- Li o diff `3e95076..d4c820b`. Em `core/editar_zonas.aplicar_por_cima` entrou o parâmetro `preto_e_branco`, que o
  `core/pipeline._filtrar_com_a_marcacao` liga quando `pagina.filtro == PRETO_E_BRANCO`; no Preto e branco o "papel da
  página" não é desenhado. `core/selecao.NOMES_AMIGAVEIS[TINTA_COR]` = "Manter a cor da tinta"; em
  `ui/widgets/paineis.py` o botão = "manter a cor da tinta". Teste novo `tests/test_tinta_papel_preto_e_branco.py`.
- Nada rodado ainda; a worktree `vtp23` ainda está no código de `3e95076` (meu ramo em cima de `0acf2c7`).

### O que falta (passo a passo)
1. Juntar `origin/fase2-ferramentas-2026-10-22` (`d4c820b`) no ramo `verif-tinta-papel-2026-10-23` (`git merge`, só um
   commit novo; ninguém mais usa este ramo).
2. Criar a worktree destacada `.claude/worktrees/vtp23-antes` em `3e95076`, com as junções `modelos` e
   `gabarito\paginas` (`mklink /J`), para ser o "antes".
3. Somas de fábrica: `scripts/papel.py somas --raiz <vtp23-antes> maquina/somas-antes-3e95076.json` e o mesmo com
   `--raiz <vtp23>` -> `maquina/somas-novo-d4c820b.json`; comparar (os 36 têm de ser iguais). Usar caminho absoluto
   `D:/...` (o Python do Windows não entende `/d/...`), um processo por vez (a memória está curta).
4. Preto e branco: `scripts/papel.py papel --raiz <vtp23> img-d4c/` e conferir, em `numeros-papel.json`, que no Preto e
   branco Ap == Ab e Bp == Bb ponto por ponto nas 4 páginas, e que Original e Melhorar dão os mesmos números de
   `img/numeros-papel.json` (o `3e95076`). Melhor ainda: acrescentar ao `papel.py` um modo que grave as somas dos 5
   jeitos x 3 filtros x 4 páginas e comparar `3e95076` x `d4c820b` (Original e Melhorar iguais; Preto e branco: Ap
   passa a ser igual a Ab).
5. Projeto antigo: `json-antigo --raiz <vtc23>` (já feito em `maquina/projeto-antigo/`) e `abrir-antigo --raiz <vtp23>`
   numa pasta nova (copiar os `*-projeto.json` e `somas-antigo.json`).
6. Teste novo: `pytest tests/test_tinta_papel_preto_e_branco.py -q` no novo e (cópia em %TEMP%) no `vtp23-antes`: tem
   de falhar lá.
7. Janela: no `scripts/janela.py`, trocar `"tinta com a cor, papel branco"` pelo nome novo nas conferências, e
   acrescentar: o texto do botão `mc.botoes[TINTA_COR].text() == "manter a cor da tinta"`, o aviso "Área escolhida: ..."
   (procurar o texto em `ui/`) e a linha "Marcado: ..." sem "papel branco". Rodar a fase 1 e a fase 2 numa pasta nova
   (`maquina/janela-d4c`), com a janela fora da tela e fechando com WM_CLOSE.
8. Fotos de antes e depois: as letras de perto no Preto e branco (`img/*-preto_e_branco-letra-de-perto.jpg` é o antes) e
   o painel (o `img/jan_03`/`jan_05` é o antes). Abrir todas as imagens novas.
9. Ler as rodadas 39889891066 e 39886669584 do GitHub (o commit testado tem de ter o mesmo código de `d4c820b`).
10. `conferencia.json` (id `tp23`): tirar das ressalvas a 1 (b-10) e a 2 (b-11); acrescentar o quadro "Ajustes das suas
    respostas 10 e 11" com as fotos de antes e depois; atualizar o "trabalho" para `d4c820b`; refazer o relatório nos
    três formatos (`scripts/relatorio_tp23.md` + `relatorio.gravar`); commit e push.
