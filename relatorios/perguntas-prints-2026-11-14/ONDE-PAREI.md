# ONDE-PAREI: perguntas com prints para a Central (14/11/2026)

Verificador, chamado pela gerente. Ramo `perguntas-prints-2026-11-14` (sai do `obra-2026-10-26`, ponta `c7e34fd8`),
worktree `.claude/worktrees/perguntas-prints`. **Nenhuma linha do programa muda. Não grava na Central.** Prints sem
janela na tela do Samuel (offscreen com as fontes do Windows), dados em `_dados/` desta pasta, livros só em cópia.

## Situação

- [x] Lidos: `.claude/agents/verificador.md`, `CLAUDE.md` inteiro (§10 modelo do girar, §11.13), `memoria/INDICE.md`,
  decisões do Livro (abaixo).
- [x] A2, A3, A4 (Tirar o fundo, Siebmacher em cópia): imagens prontas e abertas; texto em `relatorio_fonte.md`.
- [ ] B1, B3 (capa do Gradus, cópia): texto pronto; desenhos rodando (`scripts/rodar_capa.sh`).
- Lição desta tarefa: o script muda de pasta para a raiz do programa; o livro tem de ir com o caminho inteiro,
  senão o programa abre a caixa "não achei o arquivo" e o processo fica parado sem janela (perdi duas rodadas).
- [ ] C (Girar como ferramenta).
- [ ] Relatório nos três formatos.

## Decisões que esta tarefa precisa cumprir

- **§11.13** (13/11): as dez regras de como perguntar; a lista de conferência em cada pergunta.
- **§10, modelo de print** (10/11): "o jeito como você mostrou o o girar pagina ficou muito bom, pode colocar ele como
  exemplo de como deve ser feito os prints de uma mensagem explicativa".
- **D-605** (03/11): "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e
  testado" — por isso cada pergunta diz o que muda no que já funciona.
- **D-646** (07/11): "É só criar uma opção para desfazer o tirar fundo, e só vai desfazer o tirar fundo quando apertar
  ela. E via de regra, nenhum filtro deve fazer o fundo voltar."
- **D-699** (13/11): "Ok" ao botão "Desfazer o tirar o fundo" logo abaixo do "Tirar o fundo", no menu Filtro e no
  painel.
- **D-172** (05/10): "Sim, do mesmo jeito (só muda se alguém marcar um pedaço)" — o "Tirar o fundo" obedece ao "só
  neste pedaço" (é a decisão que a A2 mudaria).
- **D-586** (29/10): "A" — caixinha "Respeitar as gravuras achadas"; desligada, "no Preto e branco, a capa sairia
  toda em preto e branco" (B1).
- **D-700** (13/11): "Não quero consertar isso agora" — os retângulos brancos ficam parados; não perguntar.
- **D-049** (12/10, rodada 12): "B — No painel Propriedades" + "Quero a opção  B e D" — girar no alto do Propriedades
  e botões no canto da página (C mudaria).
- **D-053** (12/10, rodada 13): "B — Só no painel" — o "aplicar em" do girar só no Propriedades; o canto gira só a
  folha da vez (C mudaria).
- Ordem da gerente: não fazer a pergunta 2 (retângulos) nem a 4 (amarelo da Matemática).

## Perguntas para o Samuel

(em preparo)
