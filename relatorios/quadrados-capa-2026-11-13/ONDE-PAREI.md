# ONDE-PAREI — quadrados na capa (investigação, 13/11/2026)

Verificador (investigação). Ramo `quadrados-capa-2026-11-13`, a partir do `obra-2026-10-26` (`84b32df8`, a versão de
teste). Worktree `.claude/worktrees/quadrados-capa`, com as junções `modelos\` e `gabarito\paginas\`.
**Nenhuma linha do programa muda.** Tudo sem janela (`QT_QPA_PLATFORM=offscreen`), prioridade baixa, dados num
`LOCALAPPDATA` à parte. O projeto do Samuel foi só copiado (`_tmp/samuel-gradus`, fora do git), da pasta de dados
da versão de teste (`D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao\projetos\
pdfcoffee-com_gradus-primus-pdf-pdf-free`; o atalho "(rodada de consertos)" usa essa pasta, não a do
`%LOCALAPPDATA%`). **Situação: TERMINADO.** Relatório: `relatorio.html` (e `.md`, `.pdf`).

## Decisões que esta tarefa precisa cumprir (do pedido da gerente e do Livro)

- **D-147** (30/09): "Cinza (tons de cinza): BOM" — no Preto e branco, foto e pintura em tons de cinza.
- **D-163** (05/10): padrão do "Só as letras" = "(1) A - Guardar a tinta forte".
- **D-583 / D-586** (29/10): "Respeitar as gravuras achadas", "De início vem ligada [...] Desligada, o filtro vale na
  página inteira: no Preto e branco, a capa sairia toda em preto e branco".
- **D-587** (29/10): com "Só as letras" ligado, a "Respeitar" fica cinza.
- **D-588** (29/10, 01/11): "Gravuras em tons de cinza"; nasceu de "essa parece que está dando um negativo".
- **D-659** (09/11): no Preto e branco à mão, a gravura é procurada só na página onde a opção vale.
- **D-668** (10/11, conserto C, fora da versão de teste).
- **D-473** (tela = PDF), **D-605** (o novo não estraga o testado), **D-667** (muda em todos os lugares).
- Regras do pedido: sem janela na tela dele; não mexer na Central nem no Livro; não abrir agentes; apagar só o meu.

## O que já está escolhido e testado aqui (D-605)

Nada foi mexido (só investigação). Provas que guardam o assunto: `tests/test_decisoes_respeitar_gravuras.py`,
`tests/test_decisoes_gravuras_cinza.py`, `tests/test_decisoes_gravura_a_mao.py`,
`tests/test_preto_e_branco_regra_30_09.py`, `tests/test_etapa10b_imagem.py::test_reversao_foto_de_celular_a_sombra_da_mao_nao_vira_mancha`
(o conserto que causa os quadrados: um conserto futuro tem de mantê-la passando), e, no ramo do C,
`tests/test_decisoes_quadrados_brancos.py`.

## Como cumpri cada uma

- **D-586:** conferi que a capa preta do 13-01 é exatamente o que ela diz (Preto e branco na página inteira); com a
  caixinha desmarcada a página sai igual, ponto por ponto, à página nunca procurada (`relatorio`, seção 1). O
  `acoes.jsonl` dele mostra que foi ele que desmarcou (16:09:49, de true para false).
- **D-587:** no 13-02 a "Respeitar" fica cinza; conferi que, com "Só as letras", a marcação vale inteira
  (`core/pipeline.marcacao_que_o_filtro_usa`), por isso a caixa aparece.
- **D-147 / D-588:** no Gradus, Preto e branco com a marcação, a capa sai em tons de cinza (como manda), mas com a
  mesma caixa branca (imagem 5). Na Escola (o caso da D-588), os quadradinhos da sombra aparecem com "Respeitar"
  desmarcada desde 27/10 (imagem 10): ligação provável com o "negativo".
- **D-163:** testei "Guardar a tinta forte" (de fábrica), "Guardar tudo" e "Guardar só o texto": a caixa é igual nos
  três (não é causa).
- **D-659:** a página à mão com "Respeitar" marcada foi procurada (a marcação do projeto dele é a mesma que a minha).
- **D-668:** rodei o conserto C (`quadrados-c`, `adf35fbf`): não muda nada no Preto e branco (todas as 20 escolhas
  iguais ponto por ponto nas 3 capas); na *Matemática*, leva ao Melhorar à mão o branco no amarelo que hoje só sai
  pelo Automático (imagem 11). Risco de D-605 escrito no relatório e na pergunta 4.
- **D-473 / D-667:** tela (prévia 110), cartão do filtro (70) e PDF (300): o mesmo defeito nos três (imagem 4); à mão
  e pelo Automático (imagens 5 a 9).
- Imagens no modelo do girar (faixas azul/laranja/verde/roxo, mesmas páginas, defeito circulado ou em moldura
  vermelha, uma frase do que olhar em cada uma: `imagens/legendas.json`). Abri todas.

## Como fica para quem usa e no livro (D-637)

Só investigação: nada muda para o Kaique nem no PDF. Hoje, quem escolhe Preto e branco numa capa colorida (Gradus,
Escola) recebe no PDF os retângulos/caixa branca que viu na tela.

## Andamento

- [x] Causa do 13-01 (retângulos): `_sombra_em_quadros` (`c8844671`, 27/10 12:02, etapa 10b da obra).
- [x] Causa do 13-02: a letra "ÓNAI" recortada da gravura (regra de 30/09, item 1.2) + o mesmo passo (cor branca).
- [x] Versões antigas, conserto C, matriz de 20 escolhas × 5 capas (C em 3 capas; parei Pesel e Destino do C).
- [x] Imagens, relatório nos três formatos, medidas, scripts. Commit e push.
- Para refazer as imagens 5 a 9 e 11: rodar antes `scripts/rodar_matriz.sh` (apaguei `_trabalho/matriz`, 1,9 GB, e as
  cópias dos livros em `_tmp/livros`; os caminhos dos livros estão no script).

## Perguntas para o Samuel

1. **13-01:** com "Respeitar" desmarcada, a capa azul sai toda preta, como a D-586 diz. Está certo assim, sendo
   defeito só os retângulos brancos? **Sugestão: sim.**
2. **Os retângulos brancos:** pedir o conserto do passo da sombra para ele não agir onde a página tem cor forte
   (capa colorida, pintura), sem perder o conserto da sombra da mão nas fotos de celular? **Sugestão: sim.**
3. **O título escrito em cima da capa colorida** ("ÓNAI", no Preto e branco com a marcação e no "Só as letras"):
   (a) fica como a capa, com a cor, sem caixa (**sugestão**); (b) continua virando preto e branco (caixa preta, como
   antes da obra).
4. **O "papel" achado em cima da cor (capa da *Matemática*) e o conserto C:** (a) consertar isso antes de juntar o C,
   para o Melhorar à mão não passar a branquear o amarelo (**sugestão**); (b) juntar o C como está e pôr este defeito
   na Lista de bugs; (c) só pôr na Lista de bugs, sem mexer agora.
