# Parecer do verificador: consertos da conferência 5 e corte com 1 mm (01/10/2026)

**PRONTO PARA CONFERIR, com uma piora nova que o Samuel precisa ver.** Os cinco consertos pedidos na conferência 5 aparecem nas imagens como o Samuel pediu, e o corte deixa pelo menos 1 mm de papel depois das letras. Mas o conserto da letra colorida no Preto e branco fez uma **mancha cor de ferrugem do Palatino 66 virar um borrão preto** (é a página das manchas, R4). Essa página não estava na rodada.

Nada aqui é "aprovado": só o Samuel marca.

> **Defeito conhecido (aviso obrigatório até a Fase 1 ficar pronta):** moldura dourada e iluminura ainda são defeito conhecido (itens 1.2, 1.4 e 1.5).

## 1. O que eu fiz (máquina ou olho)

| O quê | Tipo | Resultado |
|---|---|---|
| `pytest tests -q` inteiro | máquina | 1344 passaram, 1 pulado, 1 falhou: o docTR ficou **sem memória** (MemoryError, 12 MB) no Palatino 57, com a máquina carregada pelo outro agente. Rodado de novo sozinho: 22 de 22 passaram. Não tem a ver com os consertos. |
| Pasta real `%LOCALAPPDATA%\EditorImpressao` | máquina | Igual antes e depois (32 arquivos, mesmos tamanhos e datas). |
| As imagens da rodada são do código atual? | máquina | Rodei Horas 13, 26 e 47 e Opus 20 (Preto e branco) e Horas 11 e 27 (Mágico pro) pelo caminho do botão "Confirmar e processar": **100% iguais ponto por ponto** às da rodada. |
| Prévia igual ao PDF | máquina | Em 16 páginas a prévia tem exatamente metade do tamanho do PDF (150 contra 300 DPI), com o mesmo corte e as cores na ordem certa. |
| Abrir todas as imagens | olho | Abri as 32 ampliações (`ampliados/`), as 152 imagens dos painéis das duas rodadas (em 20 folhas de contato, uma por página e filtro) e as 4 imagens de `corte-folga-1mm-2026-10-01/bordas/`. |
| Páginas que o conserto não visava | olho | Rodei **23 páginas** no Preto e branco com o código de antes (615f05b) e o de agora, e Palatino 67 e Marial 153 também no Mágico pro. Abri todas as comparações. |
| PDF de 3 páginas (corte) | máquina e olho | Escola 7, Palatino 7 e Palatino 67 num PDF só, filtro Original, processado pelo programa; medi a folga no PDF e na prévia e olhei as quatro beiradas de cada página. |
| Velocidade | não medida | Como foi pedido, não rodei o `teste_velocidade.py`. A máquina estava dividida com outro agente: os tempos que vi não servem para comparar. |
| Janela do programa | não usada | Nenhum item era de tela; nenhuma janela foi aberta. |

## 2. Os consertos, página por página

### Preto e branco

| Página | O que vi |
|---|---|
| Horas 11 | Os títulos do oval ("HEURES DE LOUIS LE GRAND… M. DC. LXXXVIII") agora saem **pretos e cheios**, como o resto do texto (P4). O centro do oval está branco e a iluminura tem a cor do original. Sobra: o ponto final de "LXXXVIII." ainda sai azul (já anotado pelo implementador). |
| Horas 13 | "TABLE" e "CONTENU EN CE LIVRE." pretos e inteiros. **O retângulo escuro na barra de baixo, perto de "pag. 54", sumiu**: a barra dourada fica inteira (M1/A4). Já existia antes e continua: um fio preto vertical na beirada esquerda da folha. |
| Horas 26 | **"NOVEMBRE." e a coluna de letras (d, e, f, g, A…) saem pretos e cheios**, sem os pedaços cinzas (M2). A moldura continua dourada. |
| Horas 27 | **O buraco na barra de cima, no canto de cima à esquerda, foi fechado**: a barra fica inteira (M3/A5/V2). As letras "A" douradas da coluna saem pretas. |
| Horas 47 | **"JESUS" e o "C" de "C'est" saem pretos e inteiros** (antes, partidos e quase sumidos), e também o segundo "JESUS Prêchant" (A1/I2). Todo o texto da caixa dá para ler. A iluminura tem a cor do original. |
| Opus Majus 20 | **O rosto e o ombro da estátua voltaram em cinza** na forma "livre" (antes saíam brancos, "esbranquiçados"). A estátua inteira fica parecida com o original (F1/A3). |
| Palatino 5 | Igual a antes; nenhum ponto preto novo no papel âmbar do retrato. |
| Palatino 9 | Igual a antes. |
| Escola 35 | Igual: o anjo em cinza. |
| Graduale 222 | Igual: pauta e notas pretas. |

### Mágico pro

| Página | O que vi |
|---|---|
| Horas 11 | **O papel dentro das letras douradas ("O" de LOUIS) e o fio creme em volta delas ficam brancos** (A2); o dourado das letras ficou igual. A iluminura fica igual a antes. Os tracinhos na margem esquerda continuam (já anotado). |
| Horas 13 | A moldura dourada fica inteira na barra de baixo; o resto fica igual. |
| Horas 26 | Igual a antes (dourado da moldura como no original). |
| Horas 27 | A barra de cima da moldura fica inteira; o resto fica igual. |
| Horas 47 | Igual a antes, sem a faixa cinza. |
| Opus Majus 20 | Igual a antes: **o rosto continua lavado** na forma "livre" (o conserto era só do Preto e branco; está escrito na Tentativa 62). |
| Palatino 5, Palatino 9, Escola 35, Graduale 222 | Iguais a antes (a não ser o enquadramento, que mudou um pouco por causa do corte com 1 mm). |

## 3. O que piorou

**Palatino 66, Preto e branco (página das manchas, R4): duas manchas cor de ferrugem viraram preto.** Uma mancha entre "D." e "Xlv" agora é um **borrão preto** do tamanho de uma letra. Uma outra, no alto do "P" de "Palatinus", vira um ponto preto grudado na letra. Antes as duas sumiam. A causa provável é a regra nova da letra colorida (`_com_a_tinta_colorida`, commit `84c031c`): o ponto que tem cor diferente da do papel sai preto, e essa mancha tem cor. O commit mediu Palatino 5, 9, 10 e 67, Marial 7, Graduale 222 e Opus 20, mas não o Palatino 66.

![Palatino 66, Preto e branco: antes, agora e o que mudou (vermelho = preto novo)](imagens/01-palatino66-pb-antes-agora.jpg)

![Palatino 66: a mancha cor de ferrugem do original vira borrão preto](imagens/02-palatino66-mancha-vira-borrao.jpg)

O Samuel ainda não viu isso. Pela seção 5 do CLAUDE.md, não reverti nada: estou só mostrando os dois resultados.

## 4. Páginas que o conserto não visava (Preto e branco, antes × agora)

- **Palatino 66:** piorou (ver acima).
- **Palatino 67:** os números escritos à mão em vermelho ("8", "28") saem mais cheios. Isso já estava anotado. Não vi borrão.
- **Horas 14 (a tabela):** **melhorou** sem ninguém pedir. Os fios dourados da tabela e as colunas da direita ("La Septuagésime", "Les Cendres", "Pasques") saíam partidos e agora saem inteiros e pretos.
  ![Horas 14, Preto e branco: os fios dourados da tabela voltam](imagens/03-horas14-pb-tabela-dourada-volta.jpg)
- **Marial 153** (também no Mágico pro), **Escola 7, Siebmacher 7 e 9, Opus 3, 11, 165 e 256, Boécio 3, 7, 8 e 22, Graduale 221 e 223, Marial 7, Palatino 7, 10 e 57, Rhetorica 18 e 73:** não vi diferença. Em Palatino 7 e Boécio 3 o contorno muda um pouco porque o ângulo medido mudou (está no LEIA-ME do corte). As diferenças pequenas nas outras páginas são só a página deslocada um ponto.

## 5. Corte com 1 mm de papel

**A folga é de pelo menos 1 mm até as letras e até a moldura, no PDF e na prévia.** Nas três páginas, nenhuma peça de tinta de verdade ficou cortada e nenhuma faixa escura nova apareceu.

| Página (PDF de 3 páginas, 300 DPI) | esquerda | direita | em cima | embaixo | O que é |
|---|---|---|---|---|---|
| Escola 7 | 1,35 mm | 1,10 mm | ver nota | 0,08 mm | Embaixo, o corte já está na beirada do scan (o endereço do site, item 6.4); fica como antes. |
| Palatino 7 | 1,19 mm | 1,35 mm | 1,61 mm | 1,10 mm | Tudo acima de 1 mm (antes: 0,42, 0,34, 1,44 e 0,08). |
| Palatino 67 | 0,85 mm | 0,25 mm | 1,19 mm | 0,08 mm | Os três números abaixo de 1 mm medem até **ciscos** (pontinhos de 3 a 6 pontos). A moldura fica a mais de 1 mm de cada lado. A ponta do fio da moldura não é mais cortada. |

A prévia dá os mesmos números, com até 0,1 a 0,3 mm de diferença por arredondamento. Ela é desenhada a 150 DPI e mostra o mesmo corte (aspecto igual).

**Nota sobre a Escola 7:** na beirada de cima há uma **linha escura** de ponta a ponta, ~0,7 mm abaixo do corte. Ela é a beirada da folha no próprio scan e **já existia antes** (no Preto e branco sai como um fio preto). O corte com 1 mm não mudou esse lado.

![Escola 7: a linha escura no alto já existia](imagens/08-escola7-linha-escura-no-topo-ja-existia.jpg)

![Palatino 67, PDF de 3 páginas: as quatro beiradas (régua de 1 mm por fora)](imagens/07-corte-pdf3-palatino67-beiradas.jpg)

Nas 4 imagens de `bordas/`, a Escola 7 e a 35 passam de 0,6–0,8 para 1,1–1,4 mm, a Rhetorica 73 de 0,6 para 1,2 mm e o Palatino 67 deixa de cortar a ponta do fio. Concordo com o que elas mostram.

## 6. Ressalvas

1. **Piora no Palatino 66 (Preto e branco):** mancha cor de ferrugem vira borrão preto. Vai para a Lista de bugs.
2. A rodada não incluía Palatino 66, Palatino 67 nem Marial 153: rodei eu. No Palatino 67 e no Marial 153 não vi piora.
3. Só há imagens de `bordas/` para 4 das 22 páginas em que o corte mudou. A tabela do LEIA-ME não explica a direita do Palatino 67 (0,25 mm). Medi: é um cisco, e a moldura tem folga.
4. Defeitos que já existiam antes e continuam: o fio preto na beirada esquerda da Horas 13 e no alto da Horas 27 e da Escola 7 (Preto e branco); o rosto lavado do Opus 20 no Mágico pro; o ponto azul de "LXXXVIII."; os tracinhos na margem esquerda da Horas 11 (Mágico pro).
5. A velocidade não foi medida por mim (instrução da gerente). A falha do pytest foi falta de memória numa máquina dividida com outro agente.
6. Durante a conferência, o outro agente fez commit (`49bcfd6`, só o formulário da conferência 6). Ele não mexeu em `core/` nem `ui/`.
7. Não abri a janela do programa (nenhum item era de tela). A caixinha da decoração não foi testada de novo.

## 7. Bug para a Lista de bugs

| Data | Bug | Onde | Print |
|---|---|---|---|
| 01/10 | **Preto e branco, Palatino 66: a mancha cor de ferrugem entre "D." e "Xlv" vira um borrão preto, e outra vira um ponto preto no alto do "P" de "Palatinus"** (antes sumiam; página das manchas, R4). Causa provável: a regra da letra colorida (`_com_a_tinta_colorida`, `COR_DE_TINTA = 21`, commit `84c031c`) também pega mancha com cor. | `core/filtros.py` | `relatorios/conferir/conferencia-5-consertos-2026-10-01/verificador/imagens/02-palatino66-mancha-vira-borrao.jpg` |

## 8. Onde está tudo

- Este parecer: `verificador/parecer-verificador-conferencia-5-consertos.html` (também `.pdf` e `.md`).
- Provas: `verificador/imagens/` (as folhas `09` a `11` são a varredura das outras páginas).
- Scripts que usei (para refazer): `verificador/scripts/`. `reproduzir.py` roda páginas pelo caminho do botão "Confirmar e processar" e faz a prévia; `corte3.py` faz o PDF de 3 páginas e mede a folga; `lado.py` monta o antes × agora.
