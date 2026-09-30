# Parecer do verificador: rodada geral de 30/09/2026

Três blocos: **A** (trabalho salvo e pergunta do fundo), **B** (opções do detector de gravura na tela, item 1.2) e **C** (Preto e branco novo). Testei na cópia limpa do commit `89cbc00` (`.claude\worktrees\verificador`), não na pasta principal.

> **Aviso (decisão do Samuel, 28/09): moldura dourada e iluminura são defeito conhecido** até a Fase 1 ficar pronta (itens 1.2, 1.4 e 1.5).

## Veredito em uma frase por bloco

- **A: PRONTO PARA CONFERIR.** Os três defeitos da pergunta do fundo e os do "cancelar" estão consertados, na janela real e sem janela. **Não achei caminho de perda de trabalho sem cópia**, fora os dois que a pessoa pede e confirma ("Começar de novo" e "Tirar da lista"). Sobrou um defeito pequeno de tela (r15).
- **B: NÃO ESTÁ PRONTO**, por um defeito de tela: **numa janela de 1440 × 880 o grupo "Gravuras e fotos" sai espremido em 40 pontos de altura e ninguém consegue ler nem clicar** (r01). A 1600 × 1000 os textos ainda saem cortados (r02). Só fica legível a 1920 × 1080 (r03). O resto funciona: "Esta página tem foto", "usar em todas", "só nas próximas", desfazer, a cópia com aviso ao mudar opção num livro conferido, a marcação à mão que fica, o "não procurar" e o aviso de DLL ausente.
- **C: PRONTO PARA CONFERIR, com ressalvas.** Moldura em desenho e título preto seguem a regra na Horas 26, 27 e 13. Mas **títulos e letras coloridas claras somem** (Horas 13: "TABLE" e "CONTENU EN CE LIVRE."; e também **Horas 27: as letras "A" douradas da coluna**, c02). E a moldura da Horas 13 sai fina e partida.

Quem decide é o Samuel. Isto não é aprovação.

## Máquina ou olho

| O quê | Tipo | Resultado |
|---|---|---|
| `pytest tests -q` inteiro, na cópia limpa | máquina | **1173 passaram, 86 pulados, nenhum falhou** (6 min). Os 86 pulados precisam de arquivos que não estão na cópia (resultados de OCR, motor do Kraken) |
| Pasta de dados real `%LOCALAPPDATA%\EditorImpressao` antes, depois do pytest e no fim de tudo (nome, tamanho, data e md5 de cada arquivo) | máquina | **Igual nas três vezes** |
| Sonda sem janela `sonda4.py` (57 conferências: casos s13–s36 com o comportamento novo) | máquina | 53 certas. As 4 que falharam eram defeito da sonda (a página em "Tirar o fundo" não procura gravura; "Tirar da lista" sem cópia devolve vazio, como documentado). Refeitas em `sonda4b.py`: certas |
| Sonda sem janela `sonda4b.py` (opções de gravura num livro com gravura achada, marcação à mão, cópia, aviso, "Tirar da lista") | máquina | Certas as de gravura, cópia e "Tirar da lista". As 3 da caixinha da aba Marcar falharam só sem janela; na janela real funcionam (r07, r08) |
| Queda com "Conferir" logo após "cancelar" (`sonda4_thread.py`, 3 casos × 3 vezes) | máquina | **Não caiu em nenhuma das 9** (antes caía) |
| Janela real: 40 prints de trabalho, 22 no relatório, **todos olhados** | olho | Tabelas abaixo |
| Rodada B (`fase1-1.2-opcoes-2026-09-30`): as 27 folhas (9 páginas × gravura, Mágico pro, Preto e branco) | olho | **Abri as 27**, e mais recortes ampliados do Graduale 222 e da Horas 13 |
| Rodada C (`pb-regra-30-09`): os 106 painéis do depois (15 páginas: original, anterior, resultado, referência, com detalhe) | olho | **Abri todos**, montados em 30 folhas (uma inteira e uma de detalhe por página), mais recortes ampliados da Horas 26 e 27 e do Graduale 222 |
| Velocidade | — | **Não rodei** (ordem da gerente) |

**Como pilotei a janela:** instâncias novas da cópia limpa, com a pasta de dados própria (`LOCALAPPDATA` trocado). Cliques e arrastos foram mensagens nativas do Windows, e os prints foram feitos com `PrintWindow`. O lançador da rodada 3 põe toda janela e toda caixa fora da tela antes de ela aparecer. Nesta rodada ganhou um canal só de leitura: diz onde está cada botão e o texto dele, e com isso eu clico no lugar certo, sempre por mensagem nativa (nunca QTest). O vigia **não precisou mover nenhuma janela**. **Nada apareceu na tela do Samuel.**

## Bloco A: trabalho salvo e pergunta do fundo

| Passo | Resultado | Onde |
|---|---|---|
| s13–s15: projeto antigo com trabalho (páginas em Mágico pro, Preto e branco e Melhorar; o resto em Original), "Sim" em "O que fazer" | Enquanto não se clica "Conferir", **o disco não muda** (md5 igual). Depois do "Conferir", **só as 5 páginas em Original viraram "Tirar o fundo"**. As outras 3 ficaram como estavam. O filtro do livro virou "Tirar o fundo", numa ação só ("Tirar o fundo em 5 páginas"). Corte e páginas conferidas ficaram iguais. Nenhuma cópia (não houve recomeço) | janela r14; sonda A1 |
| s16–s17: Desfazer (menu Editar) | **O disco volta inteiro**: os filtros e o filtro do livro, md5 igual ao de antes. O Refazer aplica de novo | janela; sonda A1 |
| ...e a tela "O que fazer" depois do Desfazer | **Defeito pequeno:** a tela continua marcando "Tirar o fundo" e o resumo diz "tirar o fundo de todas as páginas", mas o projeto está em Original. O "Conferir" não muda o disco (fica Original). Não se perde nada, mas a tela mostra uma coisa e o livro está em outra | r15 |
| s19–s21: pelo "continuar", a análise acaba atrás da pergunta, e "Sim" depois | **Consertado:** vale na hora (5 páginas em Original → "Tirar o fundo"). Fica gravado "já perguntou" e a pergunta não volta | r16, r17; sonda A2 |
| "Não" dado depois da análise | Fica gravado "já perguntou" e nada mais muda | sonda A2b |
| s23: "Sim" e fechar antes de "Conferir" | **Consertado:** o disco fica igual (md5), e **a pergunta volta** na abertura seguinte | r18; sonda A3 |
| "Sim" + cancelar + fechar; "Sim" + voltar ao início | A pergunta volta, e o disco fica igual | sonda A3 |
| Livro novo com camadas: "Sim" e fechar antes de "Conferir" | O filtro do livro "Tirar o fundo" fica gravado. Ao reabrir, não pergunta de novo e as páginas nascem em "Tirar o fundo". **Não fica mais cópia vazia** | sonda A4 |
| s33: "Conferir" logo depois do "cancelar" | **Não cai mais** (9 de 9 execuções) | `sonda4_thread.py` |
| s34–s36: desmarcar "Dividir", "Conferir", **cancelar** na janela real (livro de 40 folhas) | A conferência volta (80 páginas) com **"Dividir" marcado de novo**, no projeto e na tela. Trabalhei, fechei e reabri: o "Conferir" **não recomeçou**, sem aviso e sem cópia | r19–r22; sonda A5 |
| Opção mudada e fechar sem "Conferir" (Dividir, Este livro tem fotos, Achar gravuras, imagens claras, filtro do livro) | **A opção nova não vai para o disco** (valor antigo e as mesmas páginas). Reabrir não recomeça | janela (Dividir + fotos); sonda A6 (5 opções) |
| "Este livro tem fotos" + "Conferir" + cancelar | Volta "livre", no projeto e na tela | sonda A7 |
| "Tirar da lista" | As cópias `projeto/acoes/posicao.antigo-*` e o `resumo.json` vão para `copias-de-seguranca\<livro> (tirado da lista em …)`, com um LEIA-ME. Fica fora da pasta de projetos: não aparece cartão falso | sonda B3 (máquina). **Na janela não consegui:** o menu do cartão não aceitou clique nem tecla por mensagem com a janela fora da tela (r38 nos prints de trabalho) |
| Botões em português | Todas as caixas que apareceram nesta rodada estão em português ("Sim, tirar o fundo" / "Não, deixar como está", "entendi"). "Começar de novo?" e "Tirar da lista?": conferido no código (`sim="Começar de novo"`, `sim="Tirar da lista"`, `nao="Não, deixar"`) e no teste que varre o código. Não abri na janela, pelo motivo acima | r13, r09, r12 |

### Ainda existe caminho de perda de trabalho sem cópia?

**Não achei nenhum caminho em que o trabalho se perca sem cópia e sem a pessoa pedir.** Procurei nos lugares novos: opções de gravura mudadas e fechar, mudadas e cancelar, mudadas e "Conferir", e a caixinha da página. Os dois caminhos que apagam sem cópia são pedidos pela pessoa, que confirma, e a frase da pergunta avisa que a conferência se perde:
- **"Começar de novo"** apaga `projeto.json`, `acoes.jsonl` e `posicao.json` sem guardar cópia (já estava na Lista de bugs, 29/09).
- **"Tirar da lista"** guarda as cópias antigas, mas **não** o trabalho atual (`projeto.json`). A pergunta avisa.

Dois riscos pequenos, com desfazer:
- **"Esta página tem foto" (e o desfazer dela) refaz a gravura achada sozinha naquela página.** Um ajuste feito à mão **numa região que a máquina marcou** se perde, sem cópia. O que foi marcado à mão fica. O próprio código avisa disso. É raro, e fica no Histórico.
- **"detectar automaticamente" na aba Marcar** tira o que a máquina marcou, sem entrar no Histórico. Era assim antes.

## Bloco B: opções do detector na tela

| Passo | Resultado | Print |
|---|---|---|
| Tela "O que fazer", janela **1440 × 880** | **Defeito:** as 5 linhas do grupo ficam com 2 a 3 pontos de altura cada, uma por cima da outra, ilegíveis (medido: "Achar gravuras e fotos" com 2 pontos de altura). Os filtros de cima também ficam apertados. O relatório do implementador diz "cabe em 1440 x 880": na janela real, não cabe | r01 |
| 1600 × 1000 | Dá para ler, mas as frases da direita saem cortadas ("separa desenho, foto e moldura do texto, para cada um ser") e as linhas encostam | r02 |
| 1920 × 1080 | Legível e arrumado. Com "Este livro tem fotos" marcada, a frase da sensibilidade ainda sai cortada ("de fora a beirada mais rala" pela metade). No livro com camadas (5 filtros), o mesmo corte aparece | r03, r04, r15 |
| Textos | Sem jargão, com acento. "Sensibilidade" é a palavra mais técnica, mas vem explicada. O resumo diz o que vai ser feito: "separar as gravuras do texto", "achar as fotos em retângulo", "não procurar gravuras e fotos". Obs.: o grupo aparece também com o filtro Original, em que não faz nada | r03–r05 |
| "Este livro tem fotos" → a sensibilidade habilita; "Achar gravuras" desmarcada → as outras somem | Certo | r04, r05 |
| Aba Marcar: "Esta página tem foto" | Marca **só esta página** e entra no Histórico ("Página 3: tem foto…"). Desfazer pelo menu Editar desmarca. "usar em todas" leva para todas; "só nas próximas" (na página 5, desmarcada) deixa a 3 e a 4 marcadas e desmarca a 5 e a 6 | r06–r08 |
| Obs. de tela | A caixinha "Esta página tem foto" não mostra o quadrado quando desmarcada (só o texto em negrito). E há duas linhas iguais de "usar em todas / só nas próximas", uma embaixo da outra: não fica claro qual vale para quê | r06 |
| Mudar opção num livro conferido ("imagens claras", depois "não procurar") | **Cópia guardada + aviso** ("As gravuras achadas pelo programa serão procuradas de novo (6 páginas já marcadas); o que você marcou à mão fica. Guardei uma cópia do trabalho: …"). **O retângulo que desenhei à mão na página 3 ficou.** O resto do trabalho ficou igual. Obs.: no "não procurar" o aviso diz "serão procuradas de novo", e na verdade elas deixam de ser procuradas; o título da caixa é "Um momento" | r09, r10 |
| "Não procurar" desliga | A página 2 tinha 4 regiões de gravura; depois, 0. A caixinha da aba Marcar fica apagada | r11 |
| DLL ausente (renomeei `core\nativo\st_gravura.dll` **só na cópia**, e depois devolvi o nome; `git status` limpo) | **Uma vez na tela** ("O detector de gravuras não pôde ser usado; usei o antigo. As outras funções continuam funcionando.", título "Gravuras e fotos") e **uma vez no `erros.log`** da pasta de teste. Passei pelas 6 páginas seguintes e não apareceu de novo. Não testei o "Confirmar e processar" (abriria a caixa de salvar do Windows, que o lançador não consegue esconder antes de ela aparecer) | r12 |

### As folhas da rodada B (abri as 27)

| Página | O que vi |
|---|---|
| **Graduale 222** | **Conserto confirmado:** a pauta não é mais gravura em **nenhuma** das 10 combinações (0%). No Mágico pro A, sem blocos cinza. No Preto e branco A, a pauta preta e as notas cheias, igual ao antigo (b01) |
| **Horas 13** | **Conserto confirmado do lado do detector:** na A, a faixa dourada inteira é gravura. No Mágico pro A, a moldura sai dourada e inteira, e "TABLE" e "CONTENU EN CE LIVRE." saem vermelhos. Com fotos (E–I), o papel em volta entra na gravura. Continua o quadradinho preto sobre "pag. 54" (c01) |
| Horas 26 | A: moldura cheia, mas "NOVEMBRE." entra na gravura (fica para o 1.5). E, H e I pegam o papel |
| Opus Majus 20 | A: a estátua fica fora e sai lavada, com um bloco branco. E–I (fotos): quase como o original. B e D (imagens claras) também |
| Horas 11 | Iluminura inteira em todas. H marca 100% |
| Horas 27 | A e C: moldura. B, D e H pegam papel |
| Palatino 9 | A, C, E, F, G, I: 0% (sem tira creme). B, D e H marcam moldura e papel |
| Palatino 67 | A: limpo. B: mancha em "5 ꝛ ꝑ ꝝ t9". D e H: metade da página |
| Marial 153 | A, F, G: 0%. B, D, E, H, I: 13% (faixa de baixo e o vão entre colunas). C: canto cinza |

**Minha opinião sobre a recomendação:** concordo com as três partes.
1. **Manter a de fábrica (A).** Nas 9 páginas ela é a melhor ou empata em 8. A única exceção é o Opus 20.
2. **"Tem foto" para o Opus 20.** Prefiro **"Esta página tem foto" só na 20** a marcar o livro inteiro: no Marial 153, "fotos" (E) marca 13% de uma página só de texto. Não conferi as outras páginas do Opus com "fotos" nesta rodada.
3. **"Imagens claras" desmarcada.** Ela estraga o Palatino 9 e 67, o Marial 153 e a Horas 27.

## Bloco C: Preto e branco novo (abri os 106 painéis)

Julguei pela regra do Samuel: moldura como desenho (traço preto, fundo da faixa branco, sem mancha chapada), título preto, iluminura em preto e branco, e foto como hoje.

| Página | O que vi |
|---|---|
| Horas 11 | Iluminura virou desenho em preto e branco, e o centro ficou branco. "HEURES DE LOUIS LE GRAND" saiu todo preto (antes saía colorido). Segue a regra. Fica cheio de pontinhos (folhagem, anjos), com poucas manchas pretas grandes |
| **Horas 13** | Na rodada C (feita antes do conserto do detector), o lado direito e o canto de baixo da moldura saíam **pretos chapados**. Com o detector consertado (rodada B, Preto e branco A), a moldura inteira sai em contorno, **mas fina e partida**: o desenho do dourado quase some. Continua o quadradinho preto sobre "pag. 54". **"TABLE" e "CONTENU EN CE LIVRE." somem** (c01) |
| Horas 26 | Moldura em contorno duplo, com o fundo da faixa branco. **"NOVEMBRE." saiu preto, como pede a regra.** As letras "A" da coluna ficaram (c04). A beirada de cima da moldura sai um pouco partida |
| **Horas 27** | Moldura em contorno, partida em cima. **As letras "A" douradas/alaranjadas da coluna dominical (dias 3, 10, 17, 24, 31) somem**, só fica um risquinho (c02). Já sumiam na rodada anterior |
| Palatino 5 | O retrato virou traço em preto e branco. O fundo hachurado fica, e o rosto fica branco. Parece gravura em madeira. Tem bastante ruído na barba |
| Palatino 9, 10, 67 | Iguais à rodada anterior (moldura e texto pretos, papel branco) |
| Escola 35 | Igual à anterior: a pintura do anjo continua colorida (foto e pintura ficam como hoje até a decisão) |
| Opus 20 | Igual à anterior: a foto continua lavada, com o bloco branco (o Samuel já disse RUIM; depende da decisão das fotos) |
| Opus 165, Rhetorica 18, Marial 146, 153 | Iguais à anterior |
| Graduale 222 | Tudo em 1 bit: pauta preta, notas cheias, a rubrica vermelha "ẏſus." sai **preta**, como pede a regra (c03). Na beirada direita fica um **fio preto vertical grosso** (a borda da folha); antes era uma sombra cinza |

**Títulos vermelhos que somem: confirmado na Horas 13.** Nas outras páginas da rodada:
- **também na Horas 27**: letras "A" coloridas claras da coluna;
- **não** acontece na Horas 26 (as "A" são mais escuras e ficam);
- **não** acontece na Horas 11 (o título colorido está dentro da iluminura, que vira desenho);
- **não** acontece no Graduale 222 ("ẏſus." e a pauta vermelha saem pretas).

Nas outras 10 páginas não há título colorido. O padrão que vi: **somem as letras coloridas claras (vermelho-salmão, dourado claro) fora da gravura**; as escuras ficam. Não é da mudança `decca4a`: na Horas 13 e na 27 o antes também não tinha essas letras.

## Ressalvas

1. **Velocidade não medida** (ordem da gerente).
2. **Janela congelada ~16 s ao terminar a análise do livro de 40 folhas (80 páginas)**, nos dois "Conferir" (livro novo e reaberto): o meu canal de leitura, que roda na thread da janela, ficou 16,9 s sem responder. Medido sem janela (`sonda4_congela.py`): `_analise_pronta` levou 7,3 s, quase tudo desenhando páginas do PDF na thread da janela (`ui/widgets/paineis.py`, `_botao` → `pdf_io.limitar_altura` → `get_pixmap`; e `ir_para_pagina`). **Não sei se é desta rodada:** não comparei com o código de antes. Contraria a regra "a interface nunca congela".
3. "Tirar da lista?" e "Começar de novo?" não foram abertos na janela real (o menu do cartão não obedece a mensagem com a janela fora da tela). Conferidos por máquina e pelo código.
4. O aviso da DLL no "Confirmar e processar" não foi testado. A roda do mouse, como sempre, não.
5. O programa reconhece uma cópia do mesmo PDF com outro nome (`Boecio dll.pdf`) como o mesmo projeto, e troca o caminho gravado sem avisar. Foi decidido assim em 29/09; só anoto que me pegou no teste.
6. A rodada C foi gerada **antes** do conserto do detector da Horas 13 (`47cabac`). Para a moldura da Horas 13 no Preto e branco, vale a folha da rodada B (c01).
7. Material meu, que pode ser apagado: `saida_teste\verificador_rodada_geral_30_09\` (livros copiados, pastas de dados de teste, prints, sondas). **Não criei junções.** A DLL voltou ao nome certo. Não apaguei a cópia nem a junção `modelos`.

## Bugs para a Lista de bugs (30/09/2026)

| Data | Bug | Onde | Print |
|---|---|---|---|
| 30/09 | **Item 1.2: grupo "Gravuras e fotos" ilegível em janela de 1440 × 880** (linhas com 2–3 pontos de altura, uma por cima da outra). A 1600 × 1000, frases cortadas. Só fica bom a 1920 × 1080. No notebook do Kaique com escala 125%, a área útil é de uns 1536 × 864 | `ui/tela_opcoes.py` (grupo "Gravuras e fotos") | `r01`, `r02` |
| 30/09 | Frase da sensibilidade cortada mesmo a 1920 × 1080 com "Este livro tem fotos" marcada, e no livro com camadas | `ui/tela_opcoes.py` | `r04`, `r15` |
| 30/09 | Depois de desfazer o "Sim" da pergunta do fundo, a tela "O que fazer" continua mostrando "Tirar o fundo" e o resumo "tirar o fundo de todas as páginas", com o projeto em Original (o disco está certo) | `ui/janela_principal.py` (o desfazer não chama `tela_opcoes.mostrar_opcoes`) | `r15` |
| 30/09 | Aviso do "não procurar" num livro conferido diz "As gravuras … serão procuradas de novo", mas elas deixam de ser procuradas; título da caixa "Um momento" | `_frase_das_gravuras_refeitas` | `r09` |
| 30/09 | Aba Marcar: a caixinha "Esta página tem foto" não mostra o quadrado quando desmarcada; duas linhas iguais de "usar em todas / só nas próximas" sem dizer a que cada uma se refere | `ui/tela_conferir.py` | `r06` |
| 30/09 | **Preto e branco: letras coloridas claras fora da gravura somem**: além da Horas 13 ("TABLE", "CONTENU EN CE LIVRE."), **as letras "A" da coluna da Horas 27**. As escuras ficam (Horas 26, Graduale 222) | `core/filtros.py` (`_cinza_para_binarizar`) | `c01`, `c02` |
| 30/09 | Preto e branco: moldura da Horas 13 (depois do conserto do detector) sai em contorno fino e partido; quadradinho preto sobre "pag. 54" | detector do 1.2 + `core/filtros.py` | `c01` |
| 30/09 | Preto e branco: fio preto grosso na beirada direita do Graduale 222 (antes, sombra cinza) | `core/filtros.py` / corte | `pb-12-graduale_p222.jpg` |
| 30/09 | Janela sem responder ~16 s ao terminar a análise de um livro de 40 folhas (80 páginas): páginas do PDF desenhadas na thread da janela (`paineis._botao`, `ir_para_pagina`). Não sei se é novo | `ui/widgets/paineis.py`, `ui/tela_conferir.py` | `reproducoes/sonda4_congela.py` |

## Arquivos

- Prints e recortes: esta pasta (`r01`–`r22` janela; `b01` rodada B; `c01`–`c04` e `pb-*` rodada C).
- Sondas, lançador e registros: `reproducoes/` (`sonda4.log`, `sonda4b.log`, `pytest.log`).
- Material de teste e todos os prints de trabalho: `saida_teste\verificador_rodada_geral_30_09\`.

## Os prints

![r01 DEFEITO: 1440x880, grupo espremido](r01-BUG-gravuras-e-fotos-espremido-1440x880.jpg)
![r02 1600x1000: frases cortadas](r02-gravuras-e-fotos-cortado-1600x1000.jpg)
![r03 1920x1080](r03-gravuras-e-fotos-1920x1080.jpg)
![r04 Este livro tem fotos](r04-este-livro-tem-fotos.jpg)
![r05 não procurar](r05-nao-procurar.jpg)
![r06 aba Marcar](r06-aba-marcar.jpg)
![r07 Esta página tem foto](r07-esta-pagina-tem-foto.jpg)
![r08 só nas próximas](r08-so-nas-proximas.jpg)
![r09 aviso de opção mudada com cópia](r09-aviso-opcao-mudada-com-copia.jpg)
![r10 a marcação à mão fica](r10-marcacao-a-mao-fica.jpg)
![r11 não procurar na aba Marcar](r11-nao-procurar-na-aba-marcar.jpg)
![r12 DLL ausente](r12-dll-ausente-aviso.jpg)
![r13 pergunta do fundo](r13-pergunta-do-fundo.jpg)
![r14 Sim: só as de Original](r14-sim-so-as-de-original.jpg)
![r15 DEFEITO: desfeito, mas a tela mostra Tirar o fundo](r15-BUG-desfeito-mas-tela-mostra-tirar-o-fundo.jpg)
![r16 continuar: análise acabou atrás da pergunta](r16-continuar-analise-acabou.jpg)
![r17 continuar: Sim depois vale](r17-continuar-sim-depois-vale.jpg)
![r18 Sim e fechar: a pergunta volta](r18-sim-e-fechar-pergunta-volta.jpg)
![r19 desmarcou Dividir](r19-desmarcou-dividir.jpg)
![r20 Olhando o livro](r20-olhando-o-livro.jpg)
![r21 cancelou](r21-cancelou.jpg)
![r22 cancelar devolveu Dividir](r22-cancelar-devolveu-dividir.jpg)
![b01 Graduale 222 sem gravura na pauta](b01-graduale222-sem-gravura-na-pauta.jpg)
![c01 Horas 13: Preto e branco antigo, A e Mágico pro A](c01-horas13-pb-moldura-e-titulos-vermelhos.jpg)
![c02 DEFEITO: Horas 27, as letras A somem](c02-BUG-horas27-letras-A-somem-no-pb.jpg)
![c03 Graduale 222: rubrica sai preta](c03-graduale222-rubrica-sai-preta.jpg)
![c04 Horas 26: letras A ficam](c04-horas26-letras-A-ficam.jpg)
![pb Horas 11](pb-01-horas_p011.jpg)
![pb Horas 13](pb-02-horas_p013.jpg)
![pb Horas 26](pb-03-horas_p026.jpg)
![pb Horas 27](pb-04-horas_p027.jpg)
![pb Palatino 5](pb-05-palatino_p005.jpg)
![pb Opus 20](pb-10-opusmajus_p020.jpg)
![pb Graduale 222](pb-12-graduale_p222.jpg)
