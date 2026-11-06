# Desfazer nesta página (D-621): entrega

**Em uma frase:** o botão direito na página (em qualquer vista) ou na miniatura dela abre
"Desfazer nesta página", com as etapas que mexeram nela em caixinhas; só as marcadas voltam ao
que veio do scan, só nessa página, e o Ctrl+Z volta tudo de uma vez.

Teste de **máquina** (provas em `tests/test_decisoes_desfazer_pagina.py`) e janela de verdade
pilotada por mensagens do Windows no Gradus Primus (cópia), com prints. **PRONTO PARA CONFERIR**
fica com o verificador e o Samuel; nada aqui está aprovado.

## O pedido (palavras do Samuel)

"eu quero um botão para desfazer ajustes em uma pagina só, por exemplo, vamos supor que eu passei
o automatico e só uma pagina veio com defeito, e eu gostaria de tirar algumas etapas que foram
feitas somente com ela, eu quero poder clicar e falar quais coisas eu quero que sejam tirar [...]
e eu quero fazer só em uma." · jeito escolhido: "A2" (botão direito, caixinhas).

## Como ficou

- Botão direito na página, na área de trabalho: "Uma página", "Duas lado a lado" (vale a página
  clicada), "antes / depois" e no Dividir (com a folha inteira à vista, vale a metade do lado da
  linha em que se clicou). Também na miniatura da tira de baixo (vale a página da miniatura; a
  tela não muda de página).
- Abre um menu com "Desfazer nesta página >". Ao passar o mouse (ou clicar), aparece a lista:
  Endireitar, Corte das bordas, Mover e tamanho, Filtro, Gravuras e fotos. As que não mexeram na
  página ficam apagadas. As caixinhas começam desmarcadas (o exemplo do Livro: "marcar Corte e
  Filtro"). O botão "desfazer" só acende com alguma marcada.
- No Mover, o botão direito já abria o menu das linhas de apoio: ele continua igual, com o
  "Desfazer nesta página" embaixo (print `mover-menu-das-linhas.png`).
- Clicar fora do menu fecha sem mudar nada (é o jeito de todo menu do programa, como o das linhas
  de apoio).

O que cada etapa grava ao ser desfeita (o mesmo valor do botão que a ferramenta já tem):

- Endireitar: ângulo 0, igual a "deixar como veio".
- Corte das bordas: sem corte, igual a "não cortar esta".
- Mover e tamanho: 100% e sem mover, igual a "voltar como veio" do Mover (o tamanho de folha
  escolhido em "tamanho..." fica, como lá).
- Filtro: Original.
- Gravuras e fotos: tira todas as marcações e desliga "Respeitar as gravuras achadas" só nessa
  página. Sem isso, com "Gravuras e fotos" ligada no livro, a máquina acharia as gravuras de novo
  no próximo desenho e elas voltariam. Com a caixinha desligada o filtro da página vale na página
  inteira (D-586).

## Mexida à mão (D-004)

Segui o que o programa já faz com "deixar como veio" e "não cortar esta": a página fica com a
marca "mexida à mão" de cada etapa desfeita e fica "conferida". Assim, se o Automático rodar de
novo, a pergunta "Pular as páginas mexidas" inclui essa página, e o que foi desfeito não volta
sozinho. A marca é só das etapas desfeitas (a caixinha das gravuras não faz o filtro contar como
escolhido à mão).

## A outra página da folha

Nada da folha muda (a divisão, a linha, o giro). A prova compara a página vizinha campo a campo
antes e depois, e o PDF ponto a ponto.

## Testes

- Novos, `tests/test_decisoes_desfazer_pagina.py`: 14 casos, todos passam. Cada etapa sozinha (5);
  as cinco juntas numa ação, Ctrl+Z e Ctrl+Y; o PDF (a página desfeita sai sem corte e em
  Original, a vizinha e as outras saem iguais ponto por ponto); igual ao "deixar como veio" e ao
  "não cortar esta"; etapas do Automático sem valor à mão; gravuras que não voltam pela procura da
  máquina; botão direito na página, na miniatura, em "Duas lado a lado" e no Mover.
- Reversão: os 14 falham no código de antes (`1d2ed264`): `relatorios/desfazer-pagina/reversao.txt`.
- Antigos rodados no PC, um arquivo por vez (`testes-no-pc.txt`): os 38 `test_decisoes*.py` e os
  do desfazer, da tira, do Cortar, do Endireitar, do Mover, do Filtro e das marcações. Todos
  passam. Duas falhas apareceram com o PC carregado de outros agentes
  (`test_corte_pelo_conteudo_na_tela.py`, `test_decisoes_livreto_ver.py`, este de tempo) e
  passaram rodando de novo sozinhos. Nenhum teste antigo foi mudado.

## Janela de verdade (Gradus Primus, cópia, Automático rodado antes)

Anotações em `anotacoes.txt`, prints em `prints/`:

- `03`: o menu aberto pelo botão direito na página 14 (ferramenta Cortar).
- `04`, `05`: a lista; na 14 estavam acesas Corte das bordas, Filtro e Gravuras e fotos (o
  Endireitar não girou a 14). Marcadas Corte e Filtro.
- `06`: a 14 depois: sem corte, em Original ("Esta página vai sair em Original").
- `07`: a 13 (a outra página da mesma folha) igual: os campos dela não mudaram.
- `08`, `09`: Ctrl+Z (a 14 volta cortada e em Preto e branco) e Ctrl+Y.
- `10` a `12`: botão direito na miniatura 13 com a 14 na tela: a lista é da 13.
- `13` a `16`: em "Duas lado a lado", botão direito na página 15 (a da direita do par, com a 14
  sendo a da vez): a lista é da 15.
- `mover-menu-das-linhas.png`: no Mover, as linhas de apoio continuam, com o item embaixo.

## Ressalvas

- O print `02-pagina-14-antes.png` saiu preto (o PC estava sem memória livre naquela hora, com
  outros agentes rodando; o log mostra "Unable to allocate"). O "antes" está no `08` (depois do
  Ctrl+Z, a página volta exatamente como era).
- "Gravuras e fotos" com "Só as letras" ligado na página: as figuras continuam coloridas, porque o
  "Só as letras" manda (D-587). Para tirar, desfazer também o Filtro.
- Com "Gravuras e fotos" ligada no livro, a ferramenta Marcar ainda mostra as áreas que a máquina
  achar de novo na página; o filtro dessa página não as usa (a caixinha "Respeitar as gravuras
  achadas" fica desligada nela).
- Endireitar ainda não medido (a página nunca desenhada) conta como "mexeu" quando o Endireitar
  está ligado: a caixinha fica acesa.

## Perguntas abertas

Nenhuma bloqueou o trabalho. Escolhas que o Livro não diz por extenso e que segui pelo programa:
as caixinhas começam desmarcadas (o exemplo da D-621); clicar fora fecha sem mudar (como os outros
menus); o botão direito na miniatura não muda a página da tela.
