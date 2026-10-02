# Consertos da conferência 6 (02/10/2026): Horas 47 no Preto e branco e Opus 20 no Mágico pro

Feito pelo implementador. **PRONTO PARA CONFERIR** fica para o verificador e a marcação para o Samuel; aqui vai a opinião de quem fez, com as ressalvas.

## Onde estão as imagens

- `cartoes/a1-horas47-pb.jpg` e `cartoes/a1b-horas47-pb.jpg`: Horas 47 no Preto e branco, ORIGINAL · ANTES · AGORA, com os detalhes ampliados.
- `cartoes/x2-opus20-mp.jpg`: Opus Majus 20 no Mágico pro, forma "livre" de fábrica.
- `cartoes/x2b-opus20-mp-com-referencia.jpg`: o mesmo, com uma quarta coluna: a página com "Este livro tem fotos" (forma retangular), feita pelo programa de agora.
- `paginas/<página>-pb.jpg` e `paginas/<página>-mp.jpg`: as 32 páginas do gabarito nos dois filtros, ORIGINAL · ANTES · AGORA, com o detalhe da lista do gabarito.
- ANTES = o programa que o Samuel viu na conferência 6 (rodadas `antes-pb/`, `antes-mp/`). AGORA = com os dois consertos (`depois-pb/`, `depois-mp/`). As duas pelo mesmo caminho do botão "Confirmar e processar" (`conferencia.py`).
- Nenhum desenho por cima do conteúdo: o retângulo de destaque fica por fora, só na página inteira.

## 1. Horas 47 no Preto e branco: as letras saíam finas e falhadas (A1)

**O que o Samuel disse:** "Ainda está apagando as letras, o original está muito melhor para ler".

**A causa, em uma frase:** nas páginas de letra grossa o Preto e branco usa um corte só para a folha inteira, e numa folha com moldura e iluminura esse corte caía no meio do tom da letra, apagando a beirada dela.

**O que mudou:** o programa continua usando esse corte para dizer *onde* há letra, e passa a usar o binarizador de vizinhança (o Sauvola) para dizer *até onde* cada letra vai. Só entra a beirada de uma letra que o primeiro corte já achou em boa parte; risco fraco solto, mancha e a sombra da beirada da folha não entram. Nada que era preto sai.

**Resultado nas páginas (olhei todas):**
- **Horas 47:** as letras do texto inteiro saem cheias e legíveis ("Changeant", "ayez pitié de nous", "Enseignez moy Seigneur"), parecidas com o original; os "JESUS" e o "C" dourados continuam inteiros e ficaram mais cheios.
- **Mudaram, sempre para mais preto (nenhum ponto clareou):** Horas 13 e 14 (letras mais cheias, tabela igual), Escola 7 e 35 (texto mais cheio; o anjo e a foto em cinza iguais), Graduale 221, 222 e 223 (letra e notas um pouco mais cheias), Opus 20 (a legenda).
- **Iguais ponto a ponto:** Palatino 5, 7, 9, 10, 57, 66, 67; Marial 7; Siebmacher 7 e 9; Horas 26 e 27; Rhetorica 18 e 73; Boécio 3, 7, 8, 22; Opus 3, 11, 165, 256. Horas 11: diferença desprezível.
- **Papel e mancha do verso:** nenhuma página ficou com o papel mais escuro.

**Velocidade (só o filtro, antes e agora alternados):** Horas 47 de 10,1 para 4,7 s; Horas 13 de 5,1 para 4,1 s; Graduale 222 de 1,9 para 1,6 s; Graduale 223 de 2,5 para 2,1 s; Escola 35 de 2,4 para 1,5 s; Opus 20 de 1,3 para 0,8 s; Palatino 5 de 0,59 para 0,48 s; Marial 7 igual (1,49 s). **Horas 11 ficou um pouco mais lenta: de 13,0–13,2 para 13,2–13,6 s.** O ganho nas outras páginas vem de não medir duas vezes a grossura da letra.

**Ressalvas:**
- **Horas 11 mais lenta (+0,2 a 0,4 s no Preto e branco):** ali a medida rápida não serve (a iluminura ocupa mais da metade da folha), a medida lenta continua e a etapa nova é paga sem mudar nada na imagem. Não achei como evitar sem mexer em outra coisa.
- **Graduale 221 e 223:** alguns pedacinhos dos riscos finos da pauta ficaram um pouco mais compridos (poucos pontos, só se veem bem ampliados).
- **Horas 13:** sobra um fio curto na beirada de cima, à direita, onde já havia um pedaço antes.
- Nas páginas de letra fina (Palatino, Marial, Boécio, Siebmacher) nada mudou: elas já usavam o binarizador de vizinhança. Se o Samuel achar que alguma delas também sai fina, é outra causa.

## 2. Opus Majus 20 no Mágico pro, forma "livre" (X2)

**O que o Samuel disse:** "não sei porque, agora ficou muito ruim, não consigo ver o rosto mais, esses pontos estão horriveis atras da estatua."

**A causa, em uma frase:** o contorno "livre" deixa de fora da foto o rosto da estátua (que o programa tratava como papel e pintava de branco) e o vão escuro da porta (que tratava como letra, virando branco com pontinhos).

**O retângulo branco novo:** veio do conserto das molduras da conferência 5 (commit `358d27e`, a emenda das barras): ele passou a juntar a gravura ao lado do vão, e o pedaço que sobrou entre ela e o "texto" virou papel. Conferi rodando a mesma página com e sem a emenda. A emenda não foi desfeita, porque é ela que conserta as molduras da Horas 13 e 27 (aprovadas na conferência 6).

**O que mudou:** o mesmo conserto que o Preto e branco já tinha desde a conferência 5 (aprovado como F1), agora no Mágico pro e no Melhorar: a foto que enche quase todo o contorno dela vale como foto inteira. A forma de fábrica continua "livre", a marcação guardada no livro não muda e nada mudou na tela.

**Resultado:** o Opus 20 sai como com "Este livro tem fotos": rosto visível, vão da porta escuro, sem pontinhos e sem o retângulo branco (só 0,04% dos pontos diferem mais de 30 tons da versão com "Este livro tem fotos"). As outras 31 páginas no Mágico pro saem idênticas ponto a ponto.

**Velocidade (Mágico pro, só o filtro):** Opus 20 de 3,12 para 3,02 s; Marial 7 de 4,56 para 4,51 s; Palatino 5 2,24 s nos dois; Horas 11 10,49 e 10,48 s; Horas 13 de 10,86 para 10,76 s; Horas 47 de 9,19 para 9,07 s; Escola 35 4,74 e 4,85 s, Graduale 222 6,12 e 6,20 s (dentro da variação, que antes ia de 4,62 a 5,39 e de 5,74 a 6,12 s).

**Ressalvas:**
- O rosto continua mais claro que no original, **igual à versão com "Este livro tem fotos"** (é o jeito do Mágico pro de clarear a foto). Se o Samuel quiser o rosto mais escuro que isso, é outro pedido, que vale também para "Este livro tem fotos".
- Vale também no Melhorar (mesmo caminho), mas o Melhorar não foi rodado no gabarito.
- Só o Opus 20, entre as 32, tem foto com contorno livre recortado; outra foto recortada em L poderia levar junto um canto de texto (mesmo limite já usado no Preto e branco).

## Testes

`pytest tests -q`: 1355 passaram, 1 pulado. Testes novos em `tests/test_conferencia_6.py`. O tentado e descartado está em `relatorios/melhorias.md`, tentativas 64 e 65.

## Commits (ramo `fase-1`)

- `1b174e4`: Preto e branco: as letras da página não saem mais finas e falhadas (Horas 47, A1).
- `6748949`: Mágico pro: a foto do contorno livre sai inteira (Opus 20, X2).
