# Onde parei: verificador tc23, "Tinta com a cor original" em dois jeitos (A e B), item 2.18

Pedido da gerente em 22/10/2026 (resposta do Samuel à b-8: "As duas: A e B como opções separadas").
Ramo `verif-tinta-2026-10-23` (de `639136a`), worktree `.claude/worktrees/vtc23`; o "antes" é a worktree
`.claude/worktrees/vtc23-antes` (destacada em `f26407c`). As duas têm as junções `modelos` e `gabarito\paginas`
(desfazer só com `(Get-Item <junção>).Delete()`, nunca apagar a pasta).

## Situação

Tudo conferido. **PRONTO PARA CONFERIR** (nunca "aprovado": quem marca é o Samuel). Detalhe no relatório
`relatorio-tc23.html` e na entrega `conferencia.json` desta pasta.

- Máquina: A igual ao antigo ponto por ponto, 25 de 25 PDFs (5 páginas × Preto e branco, Original e Melhorar, uma
  área só e quatro áreas juntas); projeto antigo sem `tinta_escurecida` abre como A e sai igual (4 de 4); fora da área
  A e B não mudam nada (0 pontos, 10 de 10); onde duas áreas se cruzam manda a última (2 de 2).
- Janela de verdade (fora da tela, cliques do Windows, WM_CLOSE): 24 de 24 (livro novo), 5 de 5 (aberto de novo),
  9 de 9 (código antigo, sem os botões).
- GitHub (lido, sem rodada nova, o código não mudou depois de `41fa7bc`): suíte 39850503362, 2185 passaram, 0 falharam;
  velocidade 39849559789 (`f26407c` → `8226f33`) "igual".

## Perguntas para o Samuel

### tc23-1 (nova, 23/10/2026): no Original, o papel da área vira um retângulo branco

**O que é:** quando a página está em **Original** (ou Melhorar), a área marcada como "tinta com a cor, papel branco"
sai como um **retângulo branco** no meio do papel creme do resto da página. Isso vale para os dois jeitos (A e B); já
era assim antes da mudança (o A é igual ao antigo ponto por ponto). No Preto e branco não aparece, porque a página
inteira já é branca.

**Por que pergunto agora:** a pergunta 9 do Implementador B (se os dois botões aparecem só no Preto e branco ou em
qualquer filtro) depende disto: no Original, o resultado é este retângulo.

Fotos (fora do git, nesta pasta):
- `img/graduale_p221-original-pagina.jpg` (Graduale 221 em Original: o retângulo branco com A e com B)
- `img/horas_p013-original-pagina.jpg` (Livro de Horas 13 em Original)
- `img/jan_06_ver_de_perto_original.jpg` (a mesma coisa na janela do programa, "Ver de perto")
- para comparar, `img/graduale_p221-pb-pagina.jpg` (no Preto e branco não se vê retângulo)

Opções:
1. "Fica assim: o papel da área sai branco em qualquer filtro"
2. "No Original (e no Melhorar), o papel da área fica como o resto da página; só a tinta muda"
3. "Ainda não entendi"

### Pergunta aberta que não é minha (não decidi)

- **9 do Implementador B:** os dois botões aparecem só no Preto e branco ou em qualquer filtro? Hoje aparecem em
  qualquer filtro. Mostro os dois casos: `img/jan_02_pb_dois_botoes_A_de_fabrica.jpg` (Preto e branco) e
  `img/jan_07_original_dois_botoes.jpg` (Original).

## Ressalvas

Ver o relatório. As principais: a B escurece também o dourado e a moldura que caem dentro da área (Horas 11); a
força da cor medida no PDF sobe 10 a 23 %, não 25 %; um defeito antigo da tela (botões que aparecem soltos por um
instante ao escolher o "Marcar como") existe também no código de antes.
