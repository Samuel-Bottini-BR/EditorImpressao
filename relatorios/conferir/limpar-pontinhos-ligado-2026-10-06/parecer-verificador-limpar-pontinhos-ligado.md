# Parecer do verificador: limpar pontinhos ligado ao programa (06/10/2026)

Ramo `fase2-misto-opcoes` (HEAD `890f214`), cópia de trabalho `.claude/worktrees/misto`. Comparado com o `fase-1` em que o ramo se apoia (`5a90db5`).

> **Defeito conhecido (decisão do Samuel, 28/09):** moldura dourada e iluminura ainda são defeito conhecido (itens 1.4 e 1.5). As imagens abaixo mostram molduras coloridas no Preto e branco; isso não é deste item.

## Veredito

**NÃO ESTÁ PRONTO PARA JUNTAR, por uma razão só: ficou mais lento.** No resto, está pronto. O código do ScanTailor está igual ao original, e um projeto antigo sai idêntico ao do fase-1. A lista funciona na janela de verdade, e o PDF sai com a escolha de cada página. O "pouco" não apagou pingo, vírgula nem acento em nenhuma das seis páginas de 72 DPI. A razão é a regra 6 do plano: nenhum item pode deixar o programa mais lento. Com a máquina parada, o Preto e branco ficou de 0,04 a 0,14 s mais lento por página comum (de 10 a 35%). Nas páginas grandes de "72 DPI", ficou de 0,5 a 0,9 s mais lento (de 17 a 53%). Quem decide se aceita esse custo é o Samuel. Há também ressalvas sobre o "muito" e a prévia (ver abaixo).

| # | O que foi conferido | Como | Resultado |
|---|---|---|---|
| 1 | Código do ScanTailor sem mudança | máquina | Os 78 arquivos de `src/` são iguais aos do GitHub do ScanTailor v1.2.1 (commit `5eaac18`), baixados um por um agora. As somas do `somas-v1.2.1.txt` batem. O teste passou (10 de 10). A `st_gravura.dll` e o detector do 1.2 não mudaram no ramo. |
| 2 | Projeto antigo sai idêntico | máquina | O Palatino antigo (cópia, 134 páginas) foi processado **na janela real**. O PDF saiu igual ao do fase-1 ponto a ponto, nas 134 páginas, com o mesmo tamanho em bytes. O livro abriu com "o nosso". Um livro novo começa em "pouco". |
| 3 | Na janela real | máquina (pilotada) | A lista aparece só com o Preto e branco, na tela "O que fazer" e na aba Filtro. Trocar o valor, desfazer, refazer (pelo menu e por Ctrl+Z), "todas" e "só nas próximas" funcionam. A prévia muda. O PDF saiu com a escolha certa nas 6 páginas. `teste_botoes.py`: 159 ações, 0 falhas. |
| 4 | A olho, nas 6 páginas de "72 DPI" | olho (o Samuel decide) | O DPI foi acertado (de 381 a 518, em vez de 300). O "normal" e o "muito" tiram mais, como esperado. O "pouco" não tirou pingo, vírgula nem acento. Tirou pontinhos de 1 a 5 pontos do pautado fino do Graduale, que a olho não se veem. O "muito" não comeu corpo de letra, mas **tirou a vírgula da Horas 47** e pedaços de traço fino no Graduale. |
| 5 | Velocidade | máquina | **Mais lento** (ver números) |
| 6 | Testes | máquina | 99 arquivos, um por um: 1792 passaram, 59 pulados, 0 falhas. |

## 1. O código do ScanTailor veio sem mudança

- `tests/test_st_ferramentas.py`: 10 passaram.
- **Conferido por mim, fora do teste:** baixei do GitHub, um por um, os 78 arquivos de `terceiros/scantailor-advanced/src`, no commit `5eaac1884cdcabb6514bd632114f688631bd8dbc`. A etiqueta `v1.2.1` aponta para esse commit (`git ls-remote`). Comparei cada um com a nossa cópia, sem considerar o fim de linha: **78 de 78 iguais**. Todas as somas do `somas-v1.2.1.txt` batem com o original. Os 6 arquivos novos (`Despeckle.*`, `ConnectivityMap.*`, `InfluenceMap.*`) estão entre eles.
- As forças "pouco/normal/muito" (1, 2 e 3) dão exatamente os números dos botões antigos do ScanTailor ("cauteloso/normal/agressivo"). Conferi a conta no `Despeckle.cpp`. O padrão do próprio ScanTailor é o 1,0 (`Params.cpp`), que é o "pouco".
- A soma da `st_ferramentas.dll` é a mesma anotada no `.txt` dela. **Não recompilei a DLL.** Não provei que ela saiu exatamente desse código; a ligação (`pontinhos.cpp`) só converte a imagem e chama a função do ScanTailor.
- Detector de gravura do 1.2: no ramo não mudou nem a `st_gravura.dll` nem o código Python do detector (`git diff`). O PDF do projeto antigo saiu idêntico (item 2), e esse PDF passa pelo detector.

## 2. Projeto antigo sai idêntico

Usei uma **cópia** do projeto real "Giovambattista Palatino" (`projeto.json` de 17/09). São 134 páginas em Preto e branco, 16 com marcação. O original do Samuel não foi tocado (mesma soma SHA-256 antes e depois).

| Como foi processado | Resultado contra o fase-1 (`5a90db5`) |
|---|---|
| Ramo, **na janela real** (Continuar → "Não, deixar como está" → Confirmar e processar) | 134 páginas, imagens iguais ponto a ponto, desenho igual, mesmo tamanho (24.271.635 bytes): **TUDO IGUAL** |
| Ramo, sem janela | **TUDO IGUAL** |

- O projeto antigo abriu com o livro em "o nosso", e as páginas seguem o livro. O `projeto.json` gravado pela janela ficou com `"limpar_pontinhos": "nosso"` e sem o campo velho `despeckle`.
- **Livro novo começa em "pouco".** Conferi na janela (livro de teste aberto pelo menu Arquivo) e sem janela, nas 6 páginas do lado a lado.
- Caso que **muda de propósito:** projeto antigo com a caixinha "limpar poeirinha" desligada numa página em que o programa não marcou nada (por exemplo, com "Achar gravuras" desligado). Antes, o programa ignorava a caixinha e limpava assim mesmo. Agora obedece: a página sai sem limpar, com 9.966 pontos pretos a mais num teste com o Palatino. Esse é o conserto descrito no commit `117734f`. **Nenhum dos 8 projetos do Samuel** tem a caixinha desligada em alguma página (conferi os `projeto.json`, sem mexer neles). Com marcação, a página com a caixinha desligada saiu idêntica.

## 3. Na janela real

A janela foi pilotada por mensagens do Windows, fora da tela, com pasta de dados própria. Usei um livro de teste de 6 páginas do gabarito: Palatino 57, 5 e 67, Horas 47, Marial 7 e Graduale 222.

![A lista na tela "O que fazer"](imagens-parecer/t03_o_que_fazer_lista.jpg)

- **Tela "O que fazer":** a lista "Limpar pontinhos:" fica escondida com o Original e o Melhorar. Aparece só com o Preto e branco, já em "pouco", com as cinco opções na ordem: desligado, o nosso, pouco, normal, muito. Troquei para "normal"; ao clicar em Conferir, o livro ficou com `st_normal`.
- **Aba Filtro:** a lista fica no bloco AJUSTE, no lugar da caixinha "limpar poeirinha", e só aparece com o Preto e branco. Ela mostra o valor do livro quando a página segue o livro.
- **Trocar valor (página 4 → muito):** só a página 4 mudou. O menu Editar ficou com "Desfazer: Limpar pontinhos na página 4: muito".
- **Desfazer:** pelo menu Editar e por Ctrl+Z, a página voltou a seguir o livro ("normal"). **Refazer** pelo menu Editar: voltou para "muito".
- **"todas"** (página 4 em "pouco"): as 6 páginas ficaram em "pouco". Desfazer devolveu como estava.
- **"só nas próximas"** (página 4 em "muito"): páginas 4, 5 e 6 em "muito", as 1 a 3 sem mudar.
- **A prévia muda:** a prévia da página 4 com "normal" e com "muito" diferem em 108 pontos (só preto que virou branco).

![Prévia da página 4 ao trocar para muito](imagens-parecer/previa-p4-normal-x-muito.jpg)

- **O PDF sai com o valor escolhido:** processei pela janela com a página 1 seguindo o livro ("normal"), a 2 "desligado", a 3 "o nosso" e as 4 a 6 "muito". Depois desenhei cada página com as cinco escolhas, sem janela, e comparei com o PDF ponto a ponto. **Nas 6 páginas, o PDF é idêntico ao da escolha certa** e diferente de todas as outras.
- `teste_botoes.py` (numa cópia `git archive`, com `saida_teste` própria): **159 ações, 0 falhas**.

## 4. A olho: as seis páginas de "72 DPI"

Formato aprovado pelo Samuel hoje: a folha inteira em cima, com a parte ampliada em amarelo. Embaixo, uma linha: Original · o nosso · pouco · normal · muito. Preto = fica no papel. Vermelho = o programa tirou. As imagens saíram **pelo caminho do programa** (analisar, desenhar a página a 300 DPI, mesma marcação), trocando só a escolha do livro.

Fiz também uma folha de conferência por página e por escolha. Ela mostra **cada pedaço tirado a até 1,5 mm de uma letra**, do maior para o menor, com um anel azul em volta. Olhei todas.

**O DPI foi acertado.** O DPI que chegou ao ScanTailor foi: Horas 11 = 517, Horas 26 = 493, Horas 47 = 502, Graduale 221 = 518, Graduale 222 = 467, Marial 7 = 381 (antes, 300). Pontos que cada força tira, sem o acerto → com o acerto:

| Página | pouco | normal | muito | o nosso (para comparar) |
|---|---|---|---|---|
| Horas 11 | 0 → 41 | 41 → 41 | 122 → 122 | 448 |
| Horas 26 | 38 → 239 | 362 → 574 | 765 → 1204 | 7101 |
| Horas 47 | 0 → 0 | 0 → 0 | 372 → 372 | 352 |
| Graduale 221 | 236 → 523 | 838 → 1873 | 2347 → 3856 | 2611 |
| Graduale 222 | 127 → 322 | 523 → 587 | 1091 → 2151 | 2217 |
| Marial 7 | 671 → 1331 | 2479 → 2798 | 6740 → 9223 | 14830 |

Na Horas 11 e na Horas 47, o "normal" e o "muito" não mudaram com o acerto.

**O que eu vi, página por página:**

- **Horas 11** (capa colorida): o "pouco" tira 2 pedaços na dobra da margem e nada perto de letra. O "muito" tira 4 pedaços, todos sujeira da dobra. O nosso tira 136 pedaços, quase todos lascas da borda da moldura colorida.
- **Horas 26** (calendário): o "pouco" tira 15 pedaços; o único perto de algo é um risco de 4 pontos na beira de cima. O "muito" tira 43; os 13 perto de letras são pontinhos marrons do papel, e o acento "^" de "vê" fica. Nenhuma letra comida. O nosso tira 1967 pedaços colados nas letras, lascas das bordas: confirma o que o Samuel disse.
- **Horas 47** (texto com moldura): o "pouco" e o "normal" não tiram nada. **O "muito" tira a vírgula de "changement, qui"** (46 pontos) e, ao lado dela, pontinhos dourados soltos no papel. Na prévia da janela, o "muito" tira também o dois-pontos de "precieux : mais"; no PDF, esse dois-pontos fica.

![O que o muito tira na Horas 47, no PDF](imagens-parecer/horas47-muito-pecas-no-pdf.jpg)

- **Graduale 221** (pauta): o "pouco" tira 66 pedaços. Os 14 perto de traço são pedacinhos de 1 a 5 pontos do pautado fino (a linha vertical da margem e as guias) e a ponta de um floreio fino (4 pontos), invisíveis na folha. O "normal" tira também uma mancha de 273 pontos no pé da página. **O "muito" corta mais pedaços do pautado fino** (as linhas verticais ficam mais tracejadas) **e um trecho do traço-cabelo de uma capitular** (15 pontos). Letras e notas ficam.
- **Graduale 222:** o "pouco" tira 47 pedaços, os de perto com 1 a 4 pontos no pautado. O "muito" tira 129 pedaços: **trechos da linha fina horizontal do pautado de cima** (um de 124 pontos) e das verticais. Letras e notas ficam.
- **Marial 7** (texto com o verso aparecendo): o "pouco" tira 190 pedaços; os 58 perto de letra têm de 1 a 27 pontos (o maior está na dobra). Não vi letra mexida. O "muito" tira 765 pedaços, quase todos restos do texto do verso entre as linhas, o que ajuda. Nos 60 maiores, não vi letra da frente comida. O nosso tira 4597 pedaços colados nas letras.

**Respostas às duas perguntas:**

- **O "pouco" apaga pingo, vírgula, acento ou tracinho de desenho?** Pingo, vírgula e acento, não, em nenhuma das seis. Tracinho: no Graduale, ele tira pedacinhos de 1 a 5 pontos do pautado fino e a ponta de um floreio. Esse pautado já sai tracejado no Preto e branco, e a olho não se nota.
- **O "muito" come letra?** Corpo de letra, não. Mas ele **tira pontuação**: a vírgula da Horas 47 no PDF, e o dois-pontos na prévia. Também **tira pedaços de traço fino** no Graduale: o pautado e o cabelo de uma capitular.

Imagens do lado a lado (com cópias pequenas em `imagens-parecer/`):

![Horas 11 (1)](imagens-parecer/horas_p011-1.jpg)
![Horas 11 (2)](imagens-parecer/horas_p011-2.jpg)
![Horas 26 (1)](imagens-parecer/horas_p026-1.jpg)
![Horas 26 (2)](imagens-parecer/horas_p026-2.jpg)
![Horas 26 (3)](imagens-parecer/horas_p026-3.jpg)
![Horas 47](imagens-parecer/horas_p047-1.jpg)
![Graduale 221 (1)](imagens-parecer/graduale_p221-1.jpg)
![Graduale 221 (2)](imagens-parecer/graduale_p221-2.jpg)
![Graduale 221 (3)](imagens-parecer/graduale_p221-3.jpg)
![Graduale 222 (1)](imagens-parecer/graduale_p222-1.jpg)
![Graduale 222 (2)](imagens-parecer/graduale_p222-2.jpg)
![Graduale 222 (3)](imagens-parecer/graduale_p222-3.jpg)
![Marial 7 (1)](imagens-parecer/marial_p007-1.jpg)
![Marial 7 (2)](imagens-parecer/marial_p007-2.jpg)
![Marial 7 (3)](imagens-parecer/marial_p007-3.jpg)

Folhas de conferência de cada pedaço tirado perto de letra: `imagens-parecer/candidatos-<página>-st_pouco.jpg`, `-st_muito.jpg` e `-nosso.jpg`. A Horas 11 e a Horas 47 não têm a do "pouco", porque nelas ele não tirou nada perto de letra.

## 5. Velocidade do Preto e branco

Medido com script meu, com pasta de dados própria (o `erros.log` real não foi tocado: mesmo tamanho e mesma hora, 440.660 bytes, 16:18). A máquina estava parada (CPU em 1%). Foram três rodadas, alternando fase-1 e ramo. Em cada página: 1 desenho de aquecimento e 3 medidos a 300 DPI. O número é a mediana. O fase-1 usa o nosso; o ramo, o de fábrica novo ("pouco").

| Página | fase-1 | ramo | a mais |
|---|---|---|---|
| Palatino 5 | 0,76 s | 0,84 s | +0,08 s |
| Palatino 57 | 0,44 s | 0,51 s | +0,07 s |
| Palatino 67 | 0,48 s | 0,55 s | +0,07 s |
| Escola 7 | 0,74 s | 0,88 s | +0,14 s |
| Boécio 22 | 0,11 s | 0,15 s | +0,04 s |
| Opus Majus 11 | 0,81 s | 0,90 s | +0,08 s |
| **Horas 11** (grande) | 4,56 s | 5,29 s | **+0,73 s** |
| **Horas 47** (grande) | 3,02 s | 3,52 s | **+0,50 s** |
| **Graduale 221** (grande) | 1,71 s | 2,61 s | **+0,90 s** |
| **Graduale 222** (grande) | 1,46 s | 2,13 s | **+0,67 s** |
| **Marial 7** (grande) | 1,06 s | 1,60 s | **+0,54 s** |

As três rodadas deram números muito próximos; por exemplo, Graduale 221: fase-1 1,69 / 1,78 / 1,71 s, ramo 2,60 / 2,61 / 2,63 s. **Páginas comuns: em média +0,08 s** (dentro do que o implementador mediu, de +0,1 a 0,2 s). **Grandes: em média +0,67 s** (o implementador mediu de +0,5 a 1,8 s com a máquina ocupada; com ela parada, deu de 0,5 a 0,9 s). Num livro de 300 páginas comuns, isso dá uns 25 s a mais. No Graduale inteiro, uns 0,7 s por página.

## Ressalvas

1. **Mais lento (regra 6 do plano).** Ressalva grave pelas regras do projeto. A decisão é do Samuel.
2. **O "muito" tira pontuação.** Tira a vírgula da Horas 47 no PDF e pedaços de traço fino (pautado e cabelo de capitular) no Graduale. A explicação que aparece na tela, ao parar o mouse sobre a lista, diz que "pouco, normal e muito ... deixam o que está perto da letra (pingo do i, acento, vírgula)". Para o "muito", isso não é verdade na Horas 47.
3. **A prévia nem sempre mostra o mesmo que o PDF no "muito".** Na Horas 47, a prévia (110 DPI) mostra o dois-pontos de "precieux : mais" sumindo; no PDF (300 DPI) ele fica. A vírgula some nos dois. Quem decidir olhando a prévia pode achar que o "muito" tira mais do que tira, ou coisa diferente.
4. **Projeto antigo com a caixinha "limpar poeirinha" desligada, em página sem marcação, muda** (conserto de propósito, ver item 2). Nenhum projeto do Samuel tem esse caso.
5. **O "desligado" não desliga tudo.** Dentro de gravura de traço no Preto e branco, o programa continua usando o nosso limpar pontinhos por dentro (`core/filtros.py`, parte do desenho da gravura). Isso já era assim antes e não é desta mudança. Fica o aviso, porque "desligado" pode dar a ideia de que nada é limpo.
6. **Não recompilei a DLL** (ver item 1).
7. **Não usei a roda do mouse** (não funciona com a janela fora da tela). Para rolar a tela "O que fazer", arrastei a barra.
8. Os nomes na tela ("o nosso", "Limpar pontinhos") continuam provisórios, como combinado. Vão para a rodada 10 do layout.

## Achados fora deste item (para a Lista de bugs, se a gerente achar que vale)

- **O primeiro desenho de uma página ainda sem marcação sai diferente dos seguintes.** Na Horas 47 a 110 DPI, são 64.953 pontos de diferença; o primeiro é o desenho em que o programa acha as gravuras. **Acontece igual no fase-1** (mesmo número), então não é deste item. Atrapalha quem compara prévias.
- Na tela "O que fazer", ao voltar de Conferir e trocar o filtro do livro de Melhorar para Preto e branco, as páginas continuaram em Melhorar; tive de usar "todas" na aba Filtro. Não conferi se o fase-1 faz igual; pode ser de propósito, para não desfazer o que já foi conferido.
- Nos prints, a bolinha dos filtros (Original / Preto e branco...) não aparece, e não se vê qual está marcado. O O1 do Samuel pediu a bolinha visível. Pode ser só do print feito com a janela fora da tela; não conferi na tela.

## Onde estão as coisas

- Imagens do lado a lado em tamanho cheio: `imagens/` (fora do git). Cópias pequenas: `imagens-parecer/`. Prints da janela: `prints/`.
- Scripts do verificador: `scripts/`. Dados de trabalho: `trabalho/`. Nada disso vai para o git.
