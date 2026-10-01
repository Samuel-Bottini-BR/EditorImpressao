# Verificador: Preto e branco e Mágico pro com moldura e iluminura (01/10/2026)

Código conferido: ramo `fase-1`, commit `96f050d` (commits `0ec3883`, `8c29a7d`, `6827029`, `df9e3be`, `8a9ff5d`, `60c3c83`; Tentativa 60 em `relatorios/melhorias.md`). Rodada conferida: `relatorios/conferir/pb-mp-decoracao-2026-10-01/` (13 páginas, Preto e branco e Mágico pro, antes = `df09c6f`, depois = `8a9ff5d`; nenhuma linha de `core/`, `ui/` ou `modelos.py` mudou de `8a9ff5d` para `96f050d`).

> **Defeito conhecido (aviso obrigatório até a Fase 1 ficar pronta):** moldura dourada e iluminura ainda são defeito conhecido; os itens 1.2, 1.4 e 1.5 continuam abertos.

## Veredito

**PRONTO PARA CONFERIR, com três ressalvas que o Samuel precisa ver antes de marcar.** O que ele pediu nas conferências 2 e 3 aparece nas imagens: no Mágico pro a moldura dourada sai com a cor do original (Horas 13 não escurece mais), a faixa cinza da Horas 47 sumiu e a iluminura da Horas 11 não tem mais partes lavadas nem sombras; no Preto e branco a moldura e a iluminura ficam com a cor original, a foto e a pintura saem em tons de cinza e o título vermelho da Horas 13 ("TABLE", "CONTENU EN CE LIVRE"), que antes **sumia**, agora sai preto e inteiro. A caixinha nova funciona na janela de verdade. As ressalvas:

1. **Horas 47 no Preto e branco: o "JESUS" dourado e o "C" dourado saem quebrados, quase sumidos** (como antes; a decisão V1 "letra colorida sai preta" não pegou o dourado desta página). Na Horas 11, os títulos vermelhos e azuis dentro do oval ficam **coloridos** no Preto e branco, porque estão dentro da iluminura (o mesmo caso do "NOVEMBRE." da Horas 26, já na Lista de bugs).
2. **Peso do arquivo e tempo nas páginas com decoração no Preto e branco:** a Horas 11 sai com 25,6 MB por página (com a caixinha marcada, 0,4 MB); a Horas 13, 2,8 MB (marcada, 0,11 MB). O processar dessas páginas ficou mais lento (Horas 11: 10,2 → 14,2 s; Horas 13: 5,7 → 7,3 s). As outras páginas medidas ficaram mais rápidas. O botão da tela ainda diz "arquivo pequeno".
3. **Na Horas 11, o papel dentro das letras douradas (o miolo do "O" de LOUIS) e um fio em volta delas fica creme**, não branco: cerca de 21% dos pontos claros em volta de "LOUIS" ficam creme (antes, 2%, mas antes as letras saíam lavadas). A regra pede o centro branco.

## Máquina ou olho, item por item

| Item | Como foi conferido | Resultado |
|---|---|---|
| Testes automáticos (`pytest tests -q`) | máquina | **1327 passaram**, 1 pulado, 0 falhas (7 min 48 s) |
| Pasta real `%LOCALAPPDATA%\EditorImpressao` | máquina | igual antes e depois de tudo (32 arquivos, mesmo tamanho e data) |
| As imagens da rodada são do código atual | máquina + olho | sim: rodei 9 páginas pelo caminho do programa; diferença de 0,02 % a 3,9 % dos pontos, só nas bordas (ver ressalva sobre a variação) |
| PDF de página com decoração no Preto e branco | máquina + olho | Horas 11 e Horas 13: 1 página, 1 imagem, em cor, tamanho inteiro (884×1348 pt e 997×1393 pt); a moldura e a iluminura em cor |
| Antes/depois das 13 páginas, Preto e branco e Mágico pro | olho | abri as 26 folhas (original, rodada anterior, resultado) e 15 ampliações; uma linha por página abaixo |
| Caixinha na tela "O que fazer" | olho (janela real) | funciona: ver passo a passo |
| Velocidade | máquina | medida alternada, 3 passadas; ver tabela |

## O que vi em cada página: Preto e branco

Abri as 13 folhas (original | rodada anterior | resultado) e as ampliações. Comparado ponto a ponto com a rodada anterior: Graduale 221, 222, Opus 256 e Palatino 5 **idênticos**.

| Página | O que vi |
|---|---|
| Horas 11 (iluminura) | Iluminura inteira com a cor original, sem lavar; papel em volta e o oval brancos. **Os títulos do oval (HEURES, LOUIS, FAITES, ROYAL, INVALIDES vermelhos; LE GRAND, DANS L'HOSTEL azuis) ficam coloridos**, não pretos (estão dentro da zona da iluminura). Miolo das letras douradas creme. Antes: traço preto e branco borrado. Muito melhor que antes. |
| Horas 13 (moldura TABLE) | Moldura dourada com a cor do original; papel branco dentro e fora. **"TABLE" e "CONTENU EN CE LIVRE", que sumiam antes, agora saem pretos e cheios**; texto azul preto. Continua um **retângulo preto chapado** na barra de baixo da moldura (já existia antes). |
| Horas 26 (NOVEMBRE) | Moldura dourada em cor, papel branco. **"NOVEMBRE." e as letras da coluna continuam azuis/douradas** no Preto e branco (já está na Lista de bugs, depende do 1.5). Texto da lista preto. |
| Horas 27 (DECEMBRE) | Moldura dourada em cor; "DECEMBRE." e a coluna de letras pretos. **Falta um pedaço da barra de cima da moldura** (fica branco, com pontinhos e um fio preto embaixo); o mesmo buraco existe no Mágico pro, antes e depois. |
| Horas 47 (iluminura) | Moldura, cenas e paisagens com a cor original, sem lavar; papel do bloco de texto branco. Texto preto, mas o azul fino sai um pouco falhado ("Cana", "Changeant"), e **o "JESUS" dourado e o "C" dourado de "C'est" saem quebrados, quase sumidos** (igual antes). |
| Opus Majus 20 (foto) | Foto em tons de cinza, como o exemplo aprovado P1a, mas, no contorno de fábrica ("livre"), a estátua sai **lavada de branco** no rosto e no peito (é a zona do detector, igual antes; o Samuel aprovou "Este livro tem fotos" para esta página). Rodei com "tem fotos": cinza inteiro e fiel, bom. |
| Opus Majus 256 (tabela) | Idêntico ao antes. Tabela preta, papel branco. |
| Escola 35 (anjo) | Pintura em tons de cinza, fiel, sem lavar, papel branco; texto preto. Era em cor; agora segue o P1a. |
| Graduale 221 | Idêntico ao antes. Pauta e notas como estavam. |
| Graduale 222 | Idêntico ao antes. Pauta igual. |
| Graduale 223 | O "offic." vermelho agora sai **preto e cheio** (antes, vazado). As linhas da pauta vermelha saem **um pouco mais grossas e contínuas** que antes (não piorou à vista; ficou diferente). |
| Palatino 5 (retrato) | Idêntico ao antes. |
| Palatino 9 (capitular Q) | Quase igual (0,13 % dos pontos), a capitular igual à vista. |

**O que piorou em relação ao antes no Preto e branco:** nada visível, fora o peso do arquivo e o tempo das páginas com decoração. Os defeitos acima (JESUS dourado, retângulo da Horas 13, buraco da Horas 27, títulos da Horas 11 e 26 em cor) já estavam lá ou vêm da zona do detector.

## O que vi em cada página: Mágico pro

Ponto a ponto, só as cinco páginas das Horas mudaram; as outras oito são **idênticas** à rodada anterior (abri todas mesmo assim).

| Página | O que vi |
|---|---|
| Horas 11 | **Sem partes lavadas nem sombras**: as figuras, os azuis e os dourados ficam como o original (antes o azul de baixo ia a branco e as letras douradas saíam com o miolo vazado). Oval branco, mas o miolo das letras douradas e um fio em volta ficam creme. |
| Horas 13 | Moldura dourada **igual ao original**, sem escurecer (antes era bem mais escura). Papel branco. Na barra de baixo fica um retângulo avermelhado (no original há uma mancha avermelhada ali, mas no resultado ela tem bordas retas). |
| Horas 26 | Moldura igual ao original, papel branco, texto em cor. Bom. |
| Horas 27 | Moldura igual ao original, mas com o mesmo buraco branco na barra de cima (já existia). |
| Horas 47 | **A faixa cinza embaixo de "ayez, pitié de nous" sumiu**: papel totalmente branco. Iluminura com a cor original. |
| Opus 20, Opus 256, Escola 35, Graduale 221, 222, 223, Palatino 5, 9 | Idênticos ao antes. |

**O que piorou no Mágico pro:** nada que eu tenha visto.

## A tela, passo a passo (janela real)

Instância própria do programa (`main.py` da pasta principal), fora da tela desde o primeiro instante, com pasta de dados própria (`LOCALAPPDATA` trocado), cliques por mensagens nativas do Windows, fechada com `WM_CLOSE`. O vigia de janelas não precisou mover nenhuma janela (nada apareceu na tela do Samuel). Tela a 125 %. Livros de teste: Horas 11 + 13 (2 folhas) e Horas 13 + 27 repetidas (40 folhas).

1. **Livro novo: caixinha desmarcada de fábrica**, logo abaixo dos quatro filtros, com a frase explicando embaixo (`p02`, `p13`).
2. **Preto e branco, caixinha desmarcada, "Conferir"**: na aba Filtro, o cartão do Preto e branco mostra a iluminura da Horas 11 **em cor** (`p05`).
3. **Voltar, marcar a caixinha, "Conferir"**: o cartão do Preto e branco passa a mostrar a iluminura **em traço preto e branco** (`p06`, `p09`). A opção vale ao clicar "Conferir".
4. **Fechar e reabrir o programa, "continuar"**: a caixinha **volta marcada** e o Preto e branco escolhido (`p10`, `p11`, `p12`); está gravada no projeto.
5. **"cancelar"**: com a caixinha marcada e já conferida, desmarquei, cliquei "Conferir" e "cancelar" durante a análise: ao voltar para "O que fazer", a caixinha está **marcada de novo** (o "cancelar" devolveu; `p15`–`p17`). Desmarcando e conferindo até o fim, ela fica desmarcada e gravada (`p18`).
6. **Tamanhos pequenos**: a 1366×768 e a 1000×600 (a janela não fica menor que 1268×797) a caixinha e a frase aparecem inteiras, a frase quebra a linha, nada cortado; o grupo "Gravuras e fotos" fica para a rolagem (`p19`).

O que achei estranho na tela:
- **Aviso falso:** com a caixinha desmarcada, a Horas 11 no Preto e branco mostra "Esta página tem cor - o preto e branco vai perder a ilustração." Não perde mais: a iluminura fica em cor (`p04`, `p05`).
- O resumo continua dizendo "deixar tudo em preto e branco" (já está na Lista de bugs de 01/10).

## Velocidade

Não rodei o `teste_velocidade.py` completo (a gerente decide). Medi o botão "processar" (análise já feita, uma página a 300 DPI, PDF gravado) pelo caminho do programa, alternando `df09c6f` e `96f050d`, 3 passadas, cada uma num processo novo. A terceira passada do código novo saiu toda mais lenta, inclusive nas páginas que melhoraram (a máquina estava dividida); a tabela usa as duas primeiras.

| Página | antes (`df09c6f`) | depois (`96f050d`) |
|---|---|---|
| Horas 11, Preto e branco | 10,2 s | **14,2 s (mais lento)** |
| Horas 13, Preto e branco | 5,7 s | **7,3 s (mais lento)** |
| Escola 35, Preto e branco | 4,9 s | 3,0 s |
| Opus 20, Preto e branco | 4,0 s | 2,4 s |
| Horas 11, Mágico pro | 18,3 s | 12,8 s |
| Horas 47, Mágico pro | 16,0 s | 11,6 s |

O implementador mediu só o filtro da Horas 11 no Preto e branco (7,2 → 8,2 s); no processar inteiro a diferença é maior, em parte porque o PDF dessa página passou de traço (0,4 MB) para cor (25,6 MB). Com a caixinha marcada (traço), a Horas 11 processou em 9,8 s e a Horas 13 em 3,1 s.

## Ressalvas

- **Variação de uma rodada para outra:** a mesma página, pelo mesmo código, não sai sempre igual ponto a ponto. Duas rodadas seguidas da Horas 13 no mesmo processo saíram idênticas, e a terceira diferiu em 1,8 % dos pontos; contra a rodada da conferência, 2,6 % a 3,9 %. As diferenças ficam nas bordas da moldura e das linhas; olhando a página inteira, não vi diferença. Não achei a causa (provavelmente a zona do detector) e não testei se já acontecia antes destes commits.
- A extensão da decisão N2 à **iluminura** foi da gerente; o Samuel ainda não confirmou.
- **Opus 20** com o contorno de fábrica ainda lava a estátua, nos dois filtros; com "Este livro tem fotos" (aprovado para ela) fica bom.
- Não testei roda do mouse (não é item deste trabalho).
- O cartão do Preto e branco é pequeno: confirmei por ele que a prévia troca de cor para traço; a imagem grande, conferi pelo caminho do programa (prévia e PDF), não por print ampliado da tela.

## Imagens

![Horas 47 no Preto e branco: JESUS e C dourados somem](imagens/ampliados/a8-BUG-horas47-JESUS-e-C-dourados-somem-no-pb.jpg)

![Horas 13: remendo na barra de baixo da moldura (original, PB antes, PB depois, MP antes, MP depois)](imagens/ampliados/a1-horas13-remendo-na-moldura.jpg)

![Horas 11: miolo das letras douradas creme (original, MP antes, MP depois, PB depois)](imagens/ampliados/a2-horas11-miolo-das-letras-creme.jpg)

![Horas 27: buraco na barra de cima da moldura (MP antes, MP depois, PB depois)](imagens/ampliados/a3-horas27-falha-na-moldura.jpg)

![Horas 47: faixa cinza sumiu (MP antes, MP depois)](imagens/ampliados/a4-horas47-faixa-cinza-sumiu.jpg)

![Opus 20 pelo programa: rodada, minha rodada (livre), com "tem fotos" (retangular)](imagens/ampliados/a5-opus20-rodada-minha-livre-e-retangular.jpg)

![Minha rodada: Horas 11 PB prévia e PDF em cor; com a caixinha, traço; Horas 13 com a caixinha](imagens/ampliados/a6-minha-rodada-horas11-cor-e-traco.jpg)

As 26 folhas (original | rodada anterior | resultado) estão em `imagens/paginas/`; os prints da janela, em `reproducoes/prints/`.

## Bugs para a Lista de bugs (01/10/2026)

1. **Horas 47, Preto e branco: o "JESUS" dourado e o "C" dourado de "C'est" saem quebrados, quase sumidos**; o azul fino sai um pouco falhado. A decisão V1 (letra colorida sai preta) não pega o dourado desta página. Print: `verificador/imagens/ampliados/a8-BUG-horas47-JESUS-e-C-dourados-somem-no-pb.jpg`. Onde: `core/filtros.py` (`_cinza_para_binarizar`).
2. **Horas 11, Preto e branco: os títulos vermelhos e azuis do oval ficam em cor** (estão dentro da zona da iluminura). É o mesmo caso do "NOVEMBRE." da Horas 26; pode ir junto dele para o 1.5. Print: `imagens/paginas/pb-01-horas_p011-cheia.jpg`.
3. **Aviso falso na tela de conferir:** "Esta página tem cor - o preto e branco vai perder a ilustração." aparece na Horas 11 com a caixinha desmarcada, mas a iluminura fica em cor. Onde: `core/analise.py` (texto do alerta). Print: `reproducoes/prints/p05-aba-filtro-pb-caixinha-desmarcada.png`.
4. **Peso do PDF no Preto e branco com decoração em cor:** Horas 11, 25,6 MB por página (com a caixinha, 0,4 MB); Horas 13, 2,8 MB (com a caixinha, 0,11 MB). O botão diz "arquivo pequeno". O Samuel precisa saber disso antes de decidir.
5. **Horas 11: papel creme no miolo das letras douradas e num fio em volta** (21 % dos pontos claros em volta de LOUIS). Print: `imagens/ampliados/a2-horas11-miolo-das-letras-creme.jpg`.
6. Horas 13: **retângulo preto chapado** (PB) ou avermelhado de bordas retas (MP) na barra de baixo da moldura; já existia. Horas 27: **buraco branco na barra de cima da moldura**, nos dois filtros; já existia. Prints `a1` e `a3`.
7. **O resultado varia um pouco de uma rodada para outra** (até ~3,9 % dos pontos, nas bordas da moldura), com o mesmo código e a mesma página.

## Onde está tudo

- Este relatório: `relatorios/conferir/pb-mp-decoracao-2026-10-01/verificador/parecer-verificador-pb-mp-decoracao.html` (.md e .pdf ao lado).
- Scripts e registros: `verificador/reproducoes/` (`rodar.py` roda páginas pelo caminho do programa; `tempo.py` e `tempos.txt`, a medida de velocidade; `lancador.py`, `piloto.py`, `pil.py`, `gui.py`, `vigia.py`, a janela; `pytest.log`; `dados/`, a pasta de dados de teste).
- Nada em `core/`, `ui/`, no acervo ou no `gabarito/` foi alterado; nenhum commit.
