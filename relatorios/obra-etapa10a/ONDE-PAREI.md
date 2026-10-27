# ONDE-PAREI — obra de 26/10/2026, etapa 10a: defeitos de geometria na imagem final

Implementador · ramo `obra-etapa10a-2026-10-26` (base `obra-2026-10-26` `11f9ed3`, com a etapa 1) · worktree
`.claude/worktrees/obra-etapa10a` · worktree de apoio (código antigo, só leitura, para o teste de reversão):
`.claude/worktrees/obra-etapa10a-antes` (`11f9ed3`, solta, com as junções `modelos` e `gabarito\paginas`).
Obra D-014: feita até o fim sem pausas; o Samuel confere tudo no fim. Escolhas técnicas minhas anotadas abaixo.

## Decisões que esta tarefa precisa cumprir (do Livro, `docs/plano/DECISOES.md`, e do pedido da gerente)

- **D-104 / D-466 — os "8 lugares que podem comer a página"** (22/10/2026, `a-comer-pagina`): "Tem mais alguma função
  que pode fazer essa mesma coisa de comer parte da pagina sem que a gente queira no nosso programa?" → "B — Só o
  desentortar agora; o resto para o começo da próxima fase" + "escolhi a B, mas quando for feito o teste de bug, ele
  tem que fazer a C — Primeiro provar em páginas de verdade, depois decidir". Os 8 (PD l.401-408): endireitar no livro
  antigo e corte à mão; corte automático deixa de fora peças pequenas e soltas (aviso medido na folha inteira); tinta
  encostada na beirada tratada como borda do scanner; dividir reto em folha torta; Melhorar/Mágico pro branqueiam o
  que parece papel; área "papel" pintada de branco; borda preta (2.13) e pintar de branco (2.14) tomando gravura por
  borda; imprimir acima de 100% corta. Na prática: para cada um, página real que mostra o defeito antes; depois nada
  some sem aviso.
- **D-077** (28/09/2026): "não comer conteúdo" → o corte automático nunca corta tinta; se encostar, avisa.
- **D-097** (13/10 a 21/10/2026): "tem que ficar rente a folha de papel, não pode ter preto ali." (Cursus 3) · "É para
  sumir totalmente." · `pr-cursus-3`: "Está bom" → a borda preta some, o corte fica rente ao papel. (Não pode voltar.)
- **Lista única 4.2** (23/10) texto comido: Matemática 66 e 40, Cursus 3 ("o corte da esquerda comeu a primeira letra
  ou duas das linhas de baixo"). **4.4** "o corte tirou o lado esquerdo da moldura e deixou sobra branca do lado
  direito" (Horas 18). **4.8** corte "até o que está impresso": "cada página sai de um tamanho e sem margem" (ljs47 2,
  11, 52; Graduale "as pautas encostam na beirada"). **4.10** "A sombra da lombada não é cortada" (Boécio 2: risco
  preto fino na beirada esquerda; Siebmacher 74 e 86: faixa preta grossa).
- **D-113 / `d212-1`** (23/10/2026): "C — Deixar como está" + "Mas fica anotado para depois da junção isso ser
  resolvido, porque na verdade, eu acho que o primeiro passo em uma pagina dessas seria tirar essa moldura preta
  transformando a pagina em totalmente branca sem mexer nas letras, ai o desentortador não iria confundir as letras
  com moldura preta. não é?" → tirar a moldura escura do scanner antes de desentortar.
- **D-095 — ressalvas do G6** (12/10/2026): "Se esse trabalho não mexe nele, porque estamos avaliando isso? o
  resultado aqui dessa pagina não seria cortar as bordas pretas?" (depois "Está bom") → moldura colada em cima
  (Siebmacher 9), título colado (Escola 7), cunhas brancas com corte até a beirada (Boécio 8, Marial 7, Graduale 221).
- **Escola 197** (Lista de bugs 13/10): "na ordem nova o corte come os números 1, 2 e 3 dos itens, na margem esquerda"
  (`SOBRA_DE_TINTA`).
- **Lista única 1.4 / D-098** (13/10, `g8-moldura-tinta-fora`): "ele avisa e da opção e de mudar o corte e mostrar ele
  alargado com o que foi tirado." Defeito de 23/10: "usar o corte alargado" deixou a página menor (Antiphon 2: recorte
  40 % → 92 % da largura). Só o lado do processamento (`core/`).
- **D-016** (09/10/2026, escolha pela D-014): "a montagem da página segue sempre a ordem obrigatória (endireita,
  depois corta uma vez só, no fim), para não comer a página." Não quebrar.
- **D-473** (26/10/2026, escolha da gerente, apoiada na D-066 "precisamos que o pdf saia que nem está na tela"):
  "Tela e PDF saem da mesma conta." O que a prévia mostrar do corte, o PDF faz.
- **D-014**: obra sem pausas; detalhes técnicos eu decido e anoto aqui.
- **Regras de teste:** nada de lombada ou capa como página de teste (21/10: "não faça mais testes com lombadas de
  livros"); comer página se prova primeiro em páginas de verdade; caminho inteiro do livro novo (CLAUDE.md §4.10);
  teste de reversão em todo conserto (§4.7); desligado de fábrica com as somas iguais (96/96) quando o conserto não
  deve mudar a página padrão.

## Situação

Começando (26/10/2026). Reprodução das páginas pelos projetos salvos do teste dos 14 livros
(`D:\programas\EditorImpressao-arquivos\testes-livros-saida\<livro>\trab\projetos\<livro>\projeto.json`, só leitura).

## Passos

- [ ] Ferramenta de reprodução (página do projeto salvo pelo caminho inteiro, original × pronta).
- [ ] Reproduzir cada defeito em página de verdade; achar a causa.
- [ ] Consertos, um por vez, com teste de reversão.
- [ ] Somas de fábrica (96/96).
- [ ] Conferência antes/depois (`relatorios/obra-etapa10a/conferencia/`).
- [ ] Entrega.

## Perguntas para o Samuel

(nenhuma por enquanto)
