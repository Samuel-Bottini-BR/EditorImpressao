# Bugs: ponte para a Lista de bugs

**A lista que vale é a do plano**: [PLANO-DEFINITIVO, seção 5 "Lista de bugs"](../docs/plano/PLANO-DEFINITIVO.md)
(linhas 190 a 394 no `fase-1` `b8e9af7`). Esta ficha só a organiza por item e por situação, e diz se cada conserto
tem teste de reversão. Onde esta ficha e o plano discordarem, vale o plano e a entrada mais nova do Registro de
mudanças (seção 7). Conferido em 20/10/2026.

> **Atualização de 21/10/2026 ([PARTE -17](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)):** as contagens e tabelas abaixo são de 20/10/2026. O que mudou depois está em "Atualização de 21/10/2026" no fim deste arquivo (bugs de 20/10 e o que foi consertado).
## Contagens (20/10/2026)

| | quantos |
|---|---|
| Abertos (inclui os "movidos para o item X" e os aceitos até a Fase 5) | 107 |
| Consertados, a conferir pelo Samuel (52 no `fase-1`, 6 em ramo) | 58 |
| Fechados (aprovados pelo Samuel, decisão dele, não era defeito, resolvidos) | 43 |
| Com teste de reversão que cita o bug (data ou "Lista de bugs" no nome/docstring) | 40 |
| Com teste ligado, mas sem dizer que é de reversão | 29 |
| Sem teste achado (entre os consertados e fechados) | 32 |

Contados por linha das tabelas abaixo (uma linha da Lista de bugs pode ter virado duas, quando metade foi consertada e
metade não). "Teste de reversão" aqui quer dizer: há em `tests/` um teste cujo nome ou docstring cita o bug. **Nenhum
destes testes foi provado no código antigo** (a regra é de 19/10/2026; os testes são de antes): o verificador ainda
não mostrou que eles falham sem o conserto, como a regra pede.

## A regra de 19/10/2026 (teste de reversão)

[CLAUDE.md §4.7](../CLAUDE.md), decisão do Samuel no chat de 19/10/2026: "opção 1" (Registro 19/10/2026: "**Teste de
reversão: "opção 1"**, obrigatório em todo conserto de bug, provado no código antigo; bug de imagem usa medida").

- Todo bug consertado ganha um teste em `tests/` que **falha no código antigo e passa no novo**; o nome ou a docstring
  cita o bug (data e descrição da Lista de bugs).
- O verificador prova: roda o teste no código antigo e mostra que ele acusa o defeito. Teste que passa nos dois não vale.
- Bug de imagem usa uma **medida** que pega o defeito (ex.: mm de preto na beirada do Cursus 3). Sem medida possível:
  ressalva escrita.
- Motivo, nas palavras da explicação aceita: "um defeito consertado nunca volta escondido, nem os de imagem".

Como ler as colunas: **Linha** = número da linha no PLANO-DEFINITIVO (`b8e9af7`); "R" = citado só no Registro de
mudanças. **Teste**: "sim: `arquivo::teste`" (cita o bug), "ligado" (testa o conserto, mas não diz que é de reversão)
ou "não achado" (procurei em `tests/` por datas, nomes de página e palavras do bug).

---

## 1. Abertos, por item

### [1.1](itens/1.1.md) Tirar o fundo (camadas)

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 231 | 29/09 | "Tirar o fundo" ~20% mais lento que a primeira versão | em parte (8,6 s; meta 7,25 s) | não achado | — |
| 239 | 29/09 | Primeira prévia de livro com camadas 2% a 21% mais lenta | aberto (regra 6; ideia na Lista de espera) | não achado | — |

### [1.2](itens/1.2.md) Detector de gravura do ScanTailor

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 361 | 06/10 | Mudar opções da gravura + Ctrl+Z antigo pode devolver seleção de antes | possível, não testado | não achado | — |

### [1.5](itens/1.5.md) Juntar os detectores (inclui o "Só as letras")

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 203 | 28/09 | Moldura dourada com furinhos no Mágico pro (Horas 26, 27) | movido para 1.2, 1.4 e 1.5 (Samuel, 28/09) | não achado | [print](../docs/plano/bugs/2026-09-28-moldura-dourada-furinhos.jpg) |
| 215 | 28/09 | Orla mais cinza nas letras da Rhetorica 18 | movido para 1.2/1.5; com o 1.2 ficou igual (verificador 30/09) | não achado | [print](../docs/plano/bugs/2026-09-28-rhetorica18-orla-cinza.jpg) |
| 216 | 28/09 | Papel cinza-claro dentro de gravura pequena de traço (trava de 200 peças) | movido para 1.5 | não achado | [print](../docs/plano/bugs/2026-09-28-papel-cinza-em-gravura-pequena.jpg) |
| 217 | 28/09 | Opus Majus 20: estátua mais clara e halo na cabeça | movido para 1.5 | não achado | [print](../docs/plano/bugs/2026-09-28-opus20-halo-e-estatua-clara.jpg) |
| 218 | 28/09 | Escola 35: roupa do anjo branco-azulada (era creme) | movido para 1.5 (em 30/09 o Samuel marcou BOM "roupa e céu do anjo", B3: pode ter coberto; não confirmado) | não achado | [print](../docs/plano/bugs/2026-09-28-escola35-roupa-azulada.jpg) |
| 221 | 28/09 | Graduale 222: Mágico pro trata a página de outro jeito com o enquadramento novo | movido para 1.2/1.5 | não achado | `relatorios/conferir/fase1-2026-09-28-1941` |
| 224 | 28/09 | Graduale 222 tratado como texto: orla, ligaduras, fios partidos | movido para 1.4/1.5 | não achado | [print](../docs/plano/bugs/2026-09-28-graduale222-tratado-como-texto.jpg) |
| 227 | 28/09 | Forma livre do ScanTailor enche o miolo da moldura na Horas 26 | movido (forma por livro; 1.5). A moldura da Horas 26 foi aprovada (G2, 30/09) | não achado | [print](../relatorios/fase1-1.2-gravura-scantailor-2026-09-28/obrigatoria_horas_p026.jpg) |
| 229 | 28/09 | Horas 13: triângulo marcado como gravura sobre "pag. 54" | movido para 1.5 | não achado | `relatorios/fase1-1.2-gravura-scantailor-2026-09-28/verificador/` |
| 233 | 29/09 | Opus 20: beirada de baixo da foto perde até 0,35 mm | aberto (1.1 ou 1.5) | não achado | `relatorios/conferir/fase1-2026-09-29-0956/verificador/v01-opus20-beirada-de-baixo.jpg` |
| 234 | 29/09 | Papel azulado ou com véu nas zonas mantidas (Palatino 9, 12, 67; Rhetorica 38) | movido para 1.5 | não achado | `verificador/v07`, `v09`, `v11` |
| 269 | 30/09 | Mancha de canto do Marial 151 e papel liso da Horas 26 como gravura | aberto | não achado | `relatorios/conferir/fase1-1.2-ligacao-2026-09-30/mascaras/` |
| 274 | 30/09 | Horas 26: "NOVEMBRE." entra na gravura | movido para 1.5 (plano, Fase 1) | não achado | `.../verificador/v07-horas26-moldura-e-titulo.jpg` |
| 277 | 30/09 | Marial 153: papel não fica todo branco atrás do título | aberto (G4 "aceitável com ressalva", 30/09) | não achado | `.../verificador/v08-marial153-titulo.jpg` |
| 294 | 30/09 | Números fracos do Opus 256 e letras raspadas do Graduale 221 | tentado em 01/10 e revertido; 1.5 e 6.1 | não achado | `relatorios/conferencia-2-2026-09-30/zonas/` |
| 296 | 30/09 | Horas 13: falta um quadradinho da moldura (O4) | aberto | não achado | `relatorios/conferencia-2-2026-09-30/gravuras/g4-horas13-moldura.jpg` |
| 301 | 01/10 | Resumo de "O que fazer" diz "deixar tudo em preto e branco"; Horas 11 PB mais lenta | aberto | não achado | `relatorios/conferir/pb-mp-decoracao-2026-10-01/` |
| 303 | 01/10 | Tracinhos na margem da Horas 11 (Mágico pro) | em parte: JESUS e Opus 20 resolvidos depois; os tracinhos, abertos | não achado | `relatorios/conferencia-4-2026-10-01/` |
| 307 | 01/10 | Resultado varia até ~3,9% entre rodadas iguais | aberto (sem item; perto do 1.5) | não achado | — |
| 310 | 29/09 | Pesel 2: ferrugem do ex-libris fica rosada | movido para 1.5 (plano, item 1.1, 02/10); decisão do Samuel pendente | não achado | `relatorios/conferir/fase1-2026-09-29-0956/acervo/pesel_p002_original-antes-depois.jpg` |
| 315 | 28/09 | Remendo e faixa cinza do Palatino 10 | em parte; movido para 1.5 (plano, item 1.1). F4: "faixa cinza aceitável no Preto e branco; no Mágico pro melhor tirar" (30/09) | não achado | [print](../docs/plano/bugs/2026-09-28-camadas-remendo-rhetorica38.jpg) |
| 327 | 05/10 | Número de página, cabeçalho e nota de margem não contam como letra (`abandon`) | aberto | não achado | — |
| 347b | 06/10 | Detector marca remendo e mancha do verso como gravura (Marial 454, Antiphon 260) | aberto (1.5 e 2.18) | não achado | `relatorios/revisar-criterios-2026-10-06/imagens/gravura-errada-marial454.jpg` |
| 348 | 06/10 | Leitor de texto sem linhas: Misto vira "Tudo em preto e branco" sem aviso | aberto | não achado | — |
| 355 | 06/10 | Prévia do "Só as letras" não mostra o conserto do desenho (150 × 300 DPI) | aberto (mesma família do 388) | não achado | `relatorios/conferir/misto-desenho-apagado-2026-10-06/verificador/imagens/previa-x-pdf-palatino76.jpg` |
| 356 | 06/10 | Grão de foto de meio-tom (Righetti 6, 30); linhas vermelhas do ljs47 103; borda no Siebmacher 9 | aberto ("Bom por enquanto", 06/10) | não achado | `.../verificador/imagens/novo-righetti6d-grao-volta.jpg` |

### [1.6](itens/1.6.md) PDF em duas camadas

Nada aberto. A linha 304 (PDF pesado) está em "fechados" (decisão do Samuel: esperar o 1.6).

### [2.1](itens/2.1.md) Dividir

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 358 | 06/10 | "não dividir esta" oferecido em folha que já não é dividida | aberto | não achado | — |
| 359 | 06/10 | Restaurar a metade escondida duplica a folha na tira | aberto (raro) | não achado | `.claude/worktrees/geometria/relatorios/conferir/dividir-2026-10-06/verificador-2/` |

### [2.2](itens/2.2.md) Endireitar (inclui o G6)

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 308 | 01/10 | Página endireitada com menos de 1 mm nos cantos (folga do giro de 2 pontos) | aberto | não achado | [LEIA-ME](../relatorios/corte-folga-1mm-2026-10-01/LEIA-ME.md) |
| 373 | 09/10 | Aviso "as contas discordam" em página reta (0,2°; 150 × 300 DPI) | aberto; pede escolha do Samuel | não achado | — |
| R | 12/10 | G6: moldura e título colados na borda (Siebmacher 9, Escola 7); cunhas brancas (Boécio 8, Marial 7, Graduale 221) | aberto: "coisas a consertar depois, não impedimento" (Registro 12/10/2026) | não achado | — |

### [2.4](itens/2.4.md) Margens e a aba Bordas

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 211 | 28/09 | Aba Bordas mostra a folha inteira com corte automático | aberto (decisão da gerente: Fase 2, aba Bordas) | não achado | — |
| 222 | 28/09 | Aviso "encostou no conteúdo" medido a 150 DPI na folha inteira | aberto (Fase 2, aba Bordas) | não achado | — |
| 237 | 29/09 | Botão "tamanho..." não faz nada antes de a imagem chegar | aberto | não achado | — |

### [2.7](itens/2.7.md) Limpar pontinhos

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 368 | 08/10 | Aviso "limpar pontinhos indisponível" no `erros.log` com o nome velho | aberto | não achado | — |

### [2.8](itens/2.8.md) Preto e branco (letra)

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 285 | 30/09 | Fio preto grosso na beirada do Graduale 222 no PB (a moldura da Horas 13 ficou superada pela decisão N2: moldura mantém a cor) | em parte aberto | não achado | `relatorios/conferir/fase1-2026-09-30-rodada-geral/verificador/` |
| 325 | 02/10 | Medidor no 0 picota a letra fina (Horas 26: tinta 6,8% → 3,8%) | aberto | não achado | `relatorios/conferir/medidor-e-horas11-2026-10-02/verificador/para-o-samuel/` |
| 326 | 05/10 | Conferência 7, A1 RUIM: Horas 47 com "pixels apagados no meio das letras" | aberto | não achado | `relatorios/conferencia-7-2026-10-02/cartoes/a1-horas47-pb.jpg` |
| 334 | 05/10 | Conferência 8, H13: letras cortadas no PB ("o E de Exercisse") | aberto | não achado | `relatorios/conferencia-8-2026-10-05/` |
| 354 | 06/10 | Página sem marcação ignora o algoritmo de PB escolhido | aberto | não achado | — |

### [2.13](itens/2.13.md) Página dentro da borda preta (corte)

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 214 | 28/09 | Sobras do corte: número da folha do Graduale 221 e 223 (a clave do 222 foi aprovada, B5, 30/09) | em parte; o número vai para 2.5/2.13, o endereço da Escola 35 para o 6.4 | não achado | [print](../docs/plano/bugs/2026-09-28-graduale-sobras-do-corte.jpg) |
| 300 | 01/10 | Corte come "Cvii" → "Cv" (Graduale 221); ponta do fio do Palatino 67 | aberto (2.5/2.13; endereço no 6.4) | não achado | `relatorios/corte-crista-2026-10-01/` |
| 365 | 08/10 | "usar em todas" da aba Bordas apaga as exceções por página | aberto (o Samuel pediu exceções, 2.13) | não achado | — |
| 391 | 13/10 | Camões 66: nenhum aviso das linhas pretas da beirada | aberto (depende do 2.13) | não achado | ramo `verif-para-revisar-2026-10-13`: `relatorios/conferir/para-revisar-2026-10-13/img/camoes-66-1-recorte.jpg` |
| 393 | 13/10 | Escola 197: o corte come os números 1, 2 e 3 da margem (`SOBRA_DE_TINTA`) | aberto | não achado | ramo `verif-corte-g6-2026-10-13`: `relatorios/conferir/corte-g6-2026-10-13/img/` |
| 394 | 13/10 | Cursus 3: linhas de texto apagadas da conta como "risca de dobra" | risco, sem caso de texto cortado | não achado | — |

### [2.18](itens/2.18.md) Edição das zonas

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 379 | 12/10 | Marcar à mão "letra e traço" não protege a tinta do apagar do "Só as letras" | aberto (ideia na Lista de espera, 12/10) | não achado | — |

### [3.8](itens/3.8.md) Zoom

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 194 | 15-16/09 | Travamento com muito zoom; roda do mouse falha | movido para o 3.8 (28/09) | não achado | — |
| 195 | 24/09 | Zoom não funciona em algumas sessões | movido para o 3.8 (28/09) | não achado | — |

### [5.1](itens/5.1.md) Desempenho (Fase 5)

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 270 | 30/09 | 1.2 ligado: primeira prévia do Marial ~0,5 s mais lenta | **aceito pelo Samuel até a Fase 5** (Registro 30/09/2026) | não achado | `relatorios/conferir/fase1-1.2-ligacao-2026-09-30/scripts/` |
| 288 | 30/09 | Leitura das camadas, folhear e gravar ainda param a janela (0,3 a 0,5 s) | aberto | não achado | — |
| 340 | 05/10 | Tela "O que fazer" para 1,35 s no Siebmacher | aberto | não achado | ramo `fase2-geometria`: `saida_teste/r1/` |
| 341 | 05/10 | Janela ~10 s sem responder na tela inicial ao abrir | aberto, não investigado | não achado | — |
| 378 | 12/10 | Abrir o Marial de 300 folhas leva ~58 s (antes 25,5 a 44,4 s) | aberto, causa não investigada | não achado | `relatorios/velocidade-g6-2026-10-12/` |
| R | 06/10 | Misto 3,4% mais lento (conserto do desenho) | entra pela decisão V do Samuel de 05/10; gerente, a rever pelo Samuel | não achado | — |
| R | 13/10 | Mágico pro +1,1% com o "Para revisar" | **Fase 5** (Samuel, 19/10/2026: "vamos deixar esse concerto de lentidão para o final, para a fase de desempenho.") | não achado | — |

### [6.2](itens/6.2.md), [6.5](itens/6.5.md), [6.8](itens/6.8.md)

| Linha | Data | Bug | Item | Situação | Teste | Print |
|---|---|---|---|---|---|---|
| 297 | 30/09 | Marial 7: várias manchas na folha (B4) | 6.2 | movido (R4, Fase 6) | não achado | — |
| 338 | 05/10 | Depois de "Voltar para as opções", "Montar cadernos" é ignorado | 6.5 | aberto | não achado | `relatorios/conferir/so-neste-pedaco-2026-10-05/verificador/` |
| 289 | 30/09 | Programa empacotado com os servidores de páginas não testado | 6.8 | aberto (conferir no próximo instalador) | não achado | — |

### [Para revisar](itens/para-revisar.md) (avisos e análise)

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 243 | 29/09 | Aviso do PB ("O texto quase sumiu") em página de outro filtro | aberto | não achado | `relatorios/conferir/fase1-2026-09-29-1826/verificador/t04-palatino5-intacta-sai-como-veio.jpg` |
| 298 | 30/09 | Ordem das duas observações do livro muda a cada execução | aberto | não achado | — |
| 305 | 01/10 | Aviso falso "Esta página tem cor" com a caixinha de decoração desmarcada | aberto | não achado | `relatorios/conferir/pb-mp-decoracao-2026-10-01/verificador/reproducoes/prints/p05-aba-filtro-pb-caixinha-desmarcada.png` |
| 388 | 13/10 | **Grave:** no "Só as letras" a tela mostra o que o PDF não tem (T do Antiphonal 46) | aberto; pergunta ao Samuel na conferência do "Para revisar" (mostrar na tela o mesmo que o PDF) | não achado | ramo `verif-para-revisar-2026-10-13`: `relatorios/conferir/para-revisar-2026-10-13/img/tela-engana-1-comparacao.jpg` |
| 390 | 13/10 | Antiphon 260: iluminura chapada no PB, sem aviso | aberto | não achado | ramo `verif-para-revisar-2026-10-13`: `.../img/antiphon-260-1-pagina-recorte.jpg` |

### Aba Marcar e "só neste pedaço" (Fase 3, sem número de item)

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 336 | 05/10 | "Só neste pedaço" ignorado com "Limpar a folha" desligado | aberto | não achado | `relatorios/conferir/so-neste-pedaco-2026-10-05/verificador/` |

### Tela e [layout](itens/layout.md)

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 244 | 29/09 | Botões "Aplicar em" espremidos a 1440 × 880 (Mágico pro) | aberto | não achado | `.../verificador/t23-sem-camadas-botoes-espremidos-tambem.jpg` |
| 245 | 29/09 | "Conferir a pagina 1" sem acento no Histórico (de novo em 13/10, linha 383) | aberto | não achado | — |
| 258 | 29/09 | Resto das caixinhas: o que se muda em "O que fazer" depois de uma conferência se perde | aberto | não achado | — |
| 262 | 29/09 | Clicar num cartão de filtro às vezes abre "Ver de perto" | aberto, não investigado | não achado | `relatorios/conferir/fase1-2026-09-29-trabalho-salvo-2/verificador/q26` |
| 286 | 30/09 | Caixinhas sem quadrado visível no programa inteiro | **decidido pelo Samuel** (O1, 02/10/2026: "todas as caixinhas com o quadrado (e os filtros com a bolinha) visível"); a bolinha ganhou desenho no layout etapa 1 (`7ebbc04`); o quadrado no programa inteiro **não achei feito** (`ui/estilo.py` linha 357 é de 18/07) | não achado | `relatorios/conferir/fase1-1.2-tela-2026-09-30/prints/` |
| 318 | 02/10 | Inventário: 11 itens de menu que não fazem nada, textos sem acento, jargão, tecla R dupla | aberto (os "Painel: ..." continuam no `fase-1`, `ui/barra_de_menu.py`) | não achado | — |
| 319 | 02/10 | Sem a aba Marcar, letras de ferramenta e "Limpar tudo" dão "problema inesperado" | aberto | não achado | — |
| 321 | 02/10 | Confirmados na janela: cabeçalho escondido, tecla R, menus mortos, Ctrl+Enter, deslizante | aberto | não achado | `relatorios/prints-telas-2026-10-02/` |
| 324 | 02/10 | Menores: bloco AJUSTE sumiu uma vez, "1 cadernos", teclas em inglês, caixa de erro preta | aberto | não achado | idem |
| 332 | 05/10 | Cartão continua "PDF gerado" depois de mudar páginas | aberto | não achado | `relatorios/conferir/consertos-janela-2026-10-05/verificador/` |
| 333 | 05/10 | Cartão verde com "abrir a pasta" depois de cancelar | aberto | não achado | idem |
| 337 | 05/10 | Aba Marcar: botão de "só neste pedaço" não acompanha; Histórico "nada ainda" | aberto | não achado | `relatorios/conferir/so-neste-pedaco-2026-10-05/verificador/` |
| 343 | 06/10 | Cartão do filtro antigo fica em "preparando..." para sempre | aberto | não achado | `.claude/worktrees/misto/relatorios/conferir/misto-no-programa-2026-10-05/verificador-2/` |
| 345 | 06/10 | "Mais opções" aberto a 1280 × 657: botões encostam nas miniaturas | aberto | não achado | idem |
| 352 | 06/10 | Aviso diz "desta página" quando a página atingida é outra | aberto | não achado | — |
| 360 | 06/10 | `projeto.json` ilegível: recomeça sem aviso | aberto | não achado | — |
| 362 | 08/10 | "Desfazer" do menu Editar ligado sem nada a desfazer | aberto | não achado | — |
| 377 | 12/10 | "mantem a cor" sem acento no cartão Melhorar | aberto (continua em `ui/tela_conferir.py` linha 298 no `fase-1`) | não achado | ramo `prints-testes`, pasta `2026-10-09_2114_a783bd9_layout-impl-2026-10-08`, print 11 |
| 380 | 12/10 | Observações do livro num rótulo escondido: o Kaique não as vê | aberto | não achado | — |
| 382 | 13/10 | Menu Ver > "Painel: …" não faz nada | aberto | não achado | — |
| 383 | 13/10 | Histórico "Conferir a pagina 5" e nomes antigos de botões | aberto | não achado | ramo `layout-impl-2026-10-08`: `relatorios/layout-impl/etapa3/5-historico-com-uma-desfeita.png` |
| 384 | 13/10 | Zoom: "%" sem o número | aberto | não achado | — |
| 385 | 13/10 | "Só neste pedaço" sem as ferramentas de marcar: sem proteção | aberto | não achado | — |
| 386 | 13/10 | Aviso de `core/analise.py` (linhas 80-81) ainda fala da "aba Marcar" | aberto; frase nova a decidir com o Samuel (continua no `fase-1`) | não achado | — |
| 387 | 13/10 | Endireitar: linha da conta some sem explicação depois de girar à mão | aberto | não achado | — |
| 392 | 13/10 | 1280 × 657: nome do filtro sobre a miniatura; frase encoberta | aberto | não achado | ramo `verif-para-revisar-2026-10-13`: `.../img/antiphon-260-3-tela.jpg` |

### Infraestrutura

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 223 | 28/09 | PDF dos relatórios espreme imagem grande (37 × 9 pontos) | aberto ("junto com o próximo conserto de infraestrutura") | não achado | `relatorios/conferir/fase1-2026-09-28-2058-2/conferencia-fase1.pdf` |
| 246 | 29/09 | Projetos criados por testes na pasta de dados real do Samuel | decidido (Samuel, 29/09: "apagar mostrando a lista antes"); não achei registro de que foi feito | não achado | — |
| 299 | 01/10 | Cartões das conferências desenham o retângulo por cima do conteúdo | aberto | não achado | — |
| 329 | 05/10 | Falta de memória na detecção de gravura vira "página sem gravura", sem aviso | aberto | não achado | — |
| 349 | 06/10 | `compilar_detector_gravura.py` não acha a pasta de ferramentas numa worktree | aberto (ver [scantailor](referencias/scantailor.md)) | não achado | — |
| 351 | 06/10 | "access violation" anotado pelo Windows depois de fechar (33 casos desde 05/10) | aberto | não achado | — |
| 363 | 08/10 | Código morto em `core/filtros.py` 2978-2985 | aberto | não achado | — |

### Testes

| Linha | Data | Bug | Situação | Teste | Print |
|---|---|---|---|---|---|
| 220 | 28/09 | Instável: `test_marcacao_em_todas.py::test_usar_em_todas_copia_a_marcacao_para_as_outras_paginas` | aberto | — | — |
| 250 | 29/09 | Instável: `test_salva_sozinho.py::test_a_janela_liga_o_salvamento_na_tela` | aberto (observar) | — | — |
| 320 | 02/10 | `teste_interface.py` usa `conferir.destino`, que saiu | aberto | — | — |
| 330 | 05/10 | Numa worktree, o Kraken não é achado e ~87 testes pulam sem avisar | aberto | — | — |
| 372 | 09/10 | Instável: `test_gravura_na_aba_marcar.py::test_pagina_de_projeto_antigo_que_muda_de_forma_e_refeita` | aberto | — | — |
| 374 | 09/10 | `tests/test_trilha_e_opcoes.py` testa a trilha antiga | aberto | — | — |

---

## 2. Consertados, a conferir

### No `fase-1` (o programa de hoje), esperando o olho do Samuel

| Linha | Data | Bug | Item | Conserto | Teste | Print |
|---|---|---|---|---|---|---|
| 196 | 25/09 | Instalador sai sem os modelos | [6.8](itens/6.8.md) | `[~]` consertado 28/09; o Samuel vai instalar e testar | sim: `tests/test_empacotar.py` (módulo: "Bug de 25/09/2026") | [txt](../docs/plano/bugs/2026-09-25-instalador-sem-modelos.txt) |
| 201 | 28/09 | Corte de bordas errado (Escola 35, Horas 26 e 27) | [2.13](itens/2.13.md) | 28/09; B1 "corte da Escola 35" BOM em 30/09; Horas 26 e 27 sem marca | sim: `tests/test_corte_nao_come_conteudo.py` (módulo) | [print](../docs/plano/bugs/2026-09-28-corte-de-bordas-6-7.jpg) |
| 204 | 28/09 | `onnxruntime` fora do `requirements.txt` | infra | 28/09 | sim: `tests/test_requirements.py::test_onnxruntime_esta_no_requirements` | — |
| 205 | 28/09 | `python relatorio.py arquivo.md` quebra | infra | 28/09 | sim: `tests/test_relatorio.py::test_linha_de_comando_com_um_md_grava_os_tres_e_nao_quebra` | — |
| 206 | 28/09 | `empacotar.py --modo entrega` apaga `dist\` | infra | 28/09 | ligado: `tests/test_empacotar.py::test_modo_entrega_nao_apaga_o_teste_do_kaique` | — |
| 208 | 28/09 | Corte parte peças de tinta (94 → 25) | [2.13](itens/2.13.md) | 28/09, com sobras (linhas 214, 300) | sim: `tests/test_corte_nao_come_conteudo.py::test_o_corte_nao_parte_o_numero_da_pagina` | [print](../docs/plano/bugs/2026-09-28-corte-parte-pecas-de-tinta.jpg) |
| 209 | 28/09 | Limpeza lava a foto da estátua do Opus 20 | [1.5](itens/1.5.md) | 28/09, com os quadradinhos | ligado: `tests/test_papel_dentro_da_gravura.py` | — |
| 210 | 28/09 | Prévia e PDF com cortes diferentes (até 8%) | [2.13](itens/2.13.md) | `c70b462`; **decisão da regra 6 pendente** (Registro 28/09/2026) | sim: `tests/test_corte_previa_igual_pdf.py` (módulo) | [print](../docs/plano/bugs/2026-09-28-corte-previa-x-pdf.jpg) |
| 213 | 28/09 | Faixa escura de 1,5 a 2,5 mm à direita do Marial 7 | [2.13](itens/2.13.md) | 28/09 | sim: `tests/test_corte_nao_come_conteudo.py::test_a_folga_do_giro_nao_traz_o_fundo_escuro_do_scanner` | [print](../docs/plano/bugs/2026-09-28-marial7-faixa-escura-direita.jpg) |
| 228 | 28/09 | **Grave:** DPI absurdo faz a DLL do ScanTailor corromper a memória | [1.2](itens/1.2.md) | trava em `core/gravura_scantailor.py` (a linha não cita commit) | ligado: `tests/test_gravura_no_processamento.py::test_dpi_absurdo_nao_chega_a_dll`, `tests/test_gravura_scantailor.py::test_trava_recusa_pagina_gigante` | `relatorios/fase1-1.2-gravura-scantailor-2026-09-28/verificador/` |
| 236 | 29/09 | Caixinhas de "O que fazer" contaminadas ao carregar | [layout](itens/layout.md) | parte do carregar, `f0abd32` (o resto, linha 258, aberto) | sim: `tests/test_trabalho_nao_se_perde.py::test_as_caixinhas_do_livro_anterior_nao_contaminam_as_salvas` | — |
| 240 | 29/09 | **Grave:** mesmo PDF com caminho escrito de outro jeito apaga o trabalho | infra (projetos) | `144d29f` | sim: `tests/test_mesmo_livro_outro_caminho.py` (módulo) | `relatorios/conferir/fase1-2026-09-29-1826/verificador/t11-abrir-perdeu-o-trabalho.jpg` |
| 242 | 29/09 | Reabrir pelo "Abrir" mostra o filtro do livro em Original | [layout](itens/layout.md) | `f0abd32` (linha 254) | ligado: `tests/test_trabalho_nao_se_perde.py::test_reabrir_pelo_abrir_traz_as_opcoes_salvas_e_nao_recomeca` | `.../t10-abrir-mostra-original-no-o-que-fazer.jpg` |
| 247 | 29/09 | **Grave:** livro que mudou de pasta perde o trabalho | infra (projetos) | `e04f408`, `3cfb682`, `bd44929` | sim: `tests/test_trabalho_nao_se_perde.py` (módulo), ex. `::test_livro_movido_de_pasta_aberto_pelo_abrir_mantem_o_trabalho` | — |
| 248 | 29/09 | Mensagem diz "outro número de páginas" para tudo | [layout](itens/layout.md) | `e04f408`, `bd44929` | ligado: `tests/test_trabalho_nao_se_perde.py::test_mensagem_do_recomeco_diz_o_motivo_e_onde_esta_a_copia` | — |
| 249 | 29/09 | `test_folhear_pdf.py` grava no `erros.log` real | testes | coberto pelo conftest (linhas 260 e 366) | sim: `tests/test_pasta_de_dados_dos_testes.py` (módulo, 29/09) | — |
| 252 | 29/09 | **Grave:** dois PDFs de mesmo nome: um apaga o trabalho do outro | infra (projetos) | `7bb3905` | ligado: `tests/test_trabalho_nao_se_perde.py::test_fechar_com_outro_livro_de_mesmo_nome_nao_apaga_o_primeiro` | `.../trabalho-salvo/verificador/p15`–`p17` |
| 253 | 29/09 | **Grave:** fechar antes do fim da análise grava projeto vazio | infra (projetos) | `4c01fa6` | ligado: `tests/test_trabalho_nao_se_perde.py::test_abrir_livro_salvo_e_fechar_no_o_que_fazer_nao_apaga_o_trabalho` | `.../p18`–`p20` |
| 254 | 29/09 | Reabrir volta "Dividir" marcado e recomeça | [layout](itens/layout.md) | `f0abd32` | ligado: mesmo teste da linha 242 | `.../p25`, `p26` |
| 255 | 29/09 | Caminho da cópia quebra depois de "D:" | [layout](itens/layout.md) | `39200f3` | ligado (cita o print p23): `tests/test_trabalho_nao_se_perde.py::test_caminho_da_copia_nao_deixa_a_letra_da_unidade_sozinha` | `.../p23` |
| 257 | 29/09 | "continuar" do cartão antigo abre o projeto mais novo | [layout](itens/layout.md) | `6996ae9`; conferido pelo verificador (30/09) | ligado: `tests/test_trabalho_nao_se_perde.py::test_continuar_o_cartao_mais_antigo_abre_ele_e_nao_o_mais_recente` | — |
| 259 | 29/09 | **Grave:** depois de "cancelar" nada mais é gravado | infra (projetos) | `8cbbfdf`; conferido pelo verificador (30/09) | ligado: `tests/test_trabalho_nao_se_perde.py::test_cancelar_a_analise_volta_a_conferencia_e_continua_gravando` | `.../trabalho-salvo-2/verificador/q21`–`q23` |
| 260 | 29/09 | Testes gravam na pasta de dados real | testes | `86725ee` | sim: `tests/test_pasta_de_dados_dos_testes.py` (módulo) | — |
| 261 | 29/09 | Depois de um recomeço, ações antigas no Histórico | [layout](itens/layout.md) | `52ef2b0` (juntado 08/10, `d198081`) | sim: `tests/test_recomeco_limpa_o_historico.py` (módulo, 06/10) | — |
| 263 | 30/09 | Pergunta do fundo: três defeitos e o "Sim" que troca todas | [1.1](itens/1.1.md) | `d4b0430` | sim (cita a decisão de 29/09): `tests/test_trabalho_nao_se_perde.py::test_projeto_antigo_sim_troca_so_as_paginas_em_original_e_da_para_desfazer` | `.../trabalho-salvo-3/verificador/s15`–`s23` |
| 264 | 30/09 | Opção mudada + "cancelar" fica gravada | [layout](itens/layout.md) | `445aa85` | ligado: `tests/test_trabalho_nao_se_perde.py::test_cancelar_depois_de_mudar_uma_opcao_devolve_as_opcoes_de_antes` | `.../s34`–`s36` |
| 265 | 30/09 | "Conferir" logo depois de "cancelar" fecha o programa | infra | `a198703` | sim: `tests/test_cancelar_e_conferir_rapido.py` (módulo, 30/09) | `.../s33` |
| 266 | 30/09 | `projeto.antigo-*` vazio; botões "Yes"/"No" | [layout](itens/layout.md) | `16c4b64` | sim: `tests/test_botoes_em_portugues.py` (módulo, 30/09); ligado: `tests/test_trabalho_nao_se_perde.py::test_livro_novo_com_camadas_nao_ganha_copia_vazia` | `.../s25` |
| 271 | 30/09 | Opção mudada sem "Conferir" vai para o disco | [layout](itens/layout.md) | `19047ff` | ligado: `tests/test_trabalho_nao_se_perde.py::test_opcao_mudada_sem_conferir_nao_vai_para_o_disco` | — |
| 272 | 30/09 | Aviso de DLL ausente não vai ao `erros.log` | [1.2](itens/1.2.md) | `2c6cb15` | ligado: `tests/test_gravura_no_processamento.py::test_dll_ausente_vai_para_o_erros_log_e_para_a_tela_uma_vez` | — |
| 273 | 30/09 | Horas 13 no PB: moldura dourada sai preta | [1.2](itens/1.2.md) | detector `47cabac` (37% → 88%) | não achado | `.../verificador/v04-horas13-pb-moldura-preta.jpg` |
| 280 | 30/09 | Grupo "Gravuras e fotos" ilegível a 1440 × 880 | [layout](itens/layout.md) | `f9ab43a` | ligado: `tests/test_opcoes_da_gravura_na_tela.py::test_janela_baixa_nao_espreme_as_linhas` | `relatorios/conferir/fase1-2026-09-30-rodada-geral/verificador/r01` |
| 281 | 30/09 | Aviso do "não procurar"; caixinha sem quadrado na aba Marcar | [layout](itens/layout.md) | `a20257c`, `749d70f`, `1f30569` | não achado | `.../r06`, `r09` |
| 282 | 30/09 | Depois de desfazer o "Sim", "O que fazer" mostra "Tirar o fundo" | [layout](itens/layout.md) | `6400b5d` | ligado: `tests/test_opcoes_da_gravura_na_tela.py::test_a_tela_o_que_fazer_acompanha_o_desfazer` | `.../r15` |
| 283 | 30/09 | **Grave:** janela ~16 s sem responder no fim da análise | infra | `47bad86` | sim: `tests/test_paginas_em_outro_processo.py` (módulo, 30/09) | `.../reproducoes/sonda4_congela.py` |
| 287 | 30/09 | Janela não cabe no notebook do Kaique a 150% | [layout](itens/layout.md) | `b05fa7d` | sim: `tests/test_janela_cabe_na_tela.py` (módulo, 30/09) | — |
| 309 | 01/10 | PB, Palatino 66: mancha de ferrugem vira borrão preto | [2.8](itens/2.8.md) | `5953b0a` | ligado: `tests/test_conferencia_5.py::test_mancha_de_ferrugem_esmaecida_nao_vira_preto` | `relatorios/conferir/conferencia-5-consertos-2026-10-01/verificador/imagens/02-palatino66-mancha-vira-borrao.jpg` |
| 322 | 02/10 | **Grave:** gerar o mesmo livro de novo trava | [layout](itens/layout.md) | `8081335` (05/10) | sim: `tests/test_gerar_o_mesmo_livro_de_novo.py` (módulo, 02/10) | `confirmar-e-processar-arquivo-ja-existe-1280x657.png` |
| 323 | 02/10 | Cartão nunca mostra "PDF gerado" | [layout](itens/layout.md) | `5e68098` (05/10) | sim: `tests/test_cartao_pdf_gerado.py` (módulo, 02/10) | `inicio-com-cartao-1280x657.png` |
| 331 | 05/10 | **Grave:** "substituir o antigo" + cancelar apaga o PDF antigo | infra | `880bf70` | sim: `tests/test_substituir_e_cancelar.py` (módulo, 05/10) | `relatorios/conferir/consertos-janela-2026-10-05/verificador/` |
| 335 | 05/10 | PDF antigo aberto noutro programa: "(2)" tratado como erro | infra | `pedaco-e-salvo-2` (juntado 06/10, `5588022`) | sim: `tests/test_antigo_aberto_vira_pronto.py` (módulo, 05/10) | `relatorios/conferir/so-neste-pedaco-2026-10-05/verificador/` |
| 339 | 05/10 | Caixa "Antes de processar" diz 12 páginas para 10 | [2.1](itens/2.1.md) | provável: Registro 06/10/2026 ("contador da janela Confirmar = PDF"); a linha da Lista não foi atualizada | ligado: `tests/test_dividir_no_programa.py::test_janela_confirmar_conta_o_mesmo_que_vai_para_o_pdf` | — |
| 342 | 05/10 | Gravar o projeto no fio da janela (disco USB) | infra | `9a367de` (juntado `cd69179`); conferido pelo verificador | ligado: `tests/test_gravar_por_tras.py` (módulo cita o R1 de 05/10) | — |
| 346 | 06/10 | Conversão termina na tela inicial e o cartão volta | infra | `3ecc92e` | sim: `tests/test_tirar_da_lista_nao_volta.py::test_conversao_termina_na_tela_inicial_e_tirar_logo_depois` | ramo `fase2-geometria` |
| 350 | 06/10 | Ctrl+Z desfaz a ação errada depois de reabrir | infra (histórico) | `3427299` (juntado `7445b9d`) | sim: `tests/test_historico_depois_de_reabrir.py` (módulo, 06/10) | `.claude/worktrees/geometria/relatorios/conferir/girar-2026-10-06/verificador-3/` |
| 353 | 06/10 | `teste_velocidade.py` grava no `erros.log` real | testes | `9b4d87d` (juntado `7445b9d`) | sim: `tests/test_pasta_de_dados_dos_scripts.py` (módulo, 06/10) | — |
| 357 | 06/10 | Recomeço automático: Ctrl+Z desfaz ações da conferência anterior | infra (histórico) | `52ef2b0` (juntado `d198081`, 08/10) | sim: `tests/test_recomeco_limpa_o_historico.py` (módulo, 06/10) | `relatorios/conferir/consertos-06-10/` |
| 366 | 08/10 | Testes escrevem no `erros.log` real depois do fim da sessão | testes | `7651a8c`; **juntado em 09/10** (`a358d4e`, "Samuel, 09/10: autorizou juntar ao programa"). A linha da Lista ainda diz "não juntado": desatualizada | sim: `tests/test_dados_isolados_ate_o_fim.py` (módulo, 07 e 08/10) | — |
| R | 30/09 | Incidente: caixa "Tirar da lista?" de um teste ficou 4 min na tela do Samuel | testes | `c1c3cc2` | ligado: `tests/test_sem_janela_na_tela.py` (módulo, 30/09) | — |
| R | 02/10 | Medidor de força incoerente nas páginas de letra grossa | [2.8](itens/2.8.md) | `bf9680f` | ligado: `tests/test_medidor_nas_paginas_otsu.py` (módulo, 02/10) | `relatorios/conferir/medidor-e-horas11-2026-10-02/` |
| R | 02/10 | Horas 11 +0,2 a 0,4 s (trava de 60% de tinta) | [5.1](itens/5.1.md) | `7f50e70`, `514fea3`; 96/96 imagens iguais | ligado: `tests/test_escolha_sem_a_trava_de_tinta.py` (módulo, 02/10) | — |
| R | 06/10 | Dividir: folha some do PDF; "não dividir esta" repetia a folha | [2.1](itens/2.1.md) | `e93c085` e seguintes (juntado 07/10) | sim: `tests/test_dividir_no_programa.py::test_folha_nao_some_com_a_esquerda_apagada_e_nao_dividir` | — |

### Em ramo, não juntados

| Linha | Data | Bug | Item | Ramo e conserto | Teste | Print |
|---|---|---|---|---|---|---|
| 238 | 29/09 | `teste_botoes.py` com PDF de 2 folhas apaga tudo e falha em "processar" | testes | `fase2-para-revisar`, `b5b224f` (13/10: "o roteiro apagava as duas paginas") | — | — |
| 317 / 381 | 02/10 | Botões "usar mais fraco / mais escuro" chamam `_escolher_forca`, que não existe | [para-revisar](itens/para-revisar.md) | `fase2-para-revisar` (12/10). No `fase-1` a chamada continua sem a função (`ui/tela_conferir.py` linha 3920) | não achado | — |
| 344 | 06/10 | Aviso "Tinta forte fora do texto" atrasado nas outras páginas | [para-revisar](itens/para-revisar.md) | superado: no `fase2-para-revisar` esse aviso sai (`280d40f`) | — | `.claude/worktrees/misto/relatorios/conferir/misto-no-programa-2026-10-05/verificador-2/` |
| 364 | 08/10 | "Parece em branco" erra (Gladstone 18 sim; Egenloff 12 e Rariora 8 não) | [para-revisar](itens/para-revisar.md) | em trabalho no `fase2-para-revisar` (avisos separados, "está bom" nos dois); a conferir na 2ª conferência | não achado | — |
| 389 | 13/10 | **Grave:** G6 deixa faixa preta larga no Cursus 3 (e Matemática 32, Antiphon 88 e 260, Camões 104) | [2.2](itens/2.2.md), [2.13](itens/2.13.md) | `conserto-corte-g6-2026-10-13`, `d97b937`. Samuel: **"Melhorar"** (13/10); hoje, o Pesel 21 | sim, no ramo: `tests/test_ordem_do_preparo.py` (6 casos novos, página torta com borda preta; falha sem o conserto, `relatorios/conserto-corte-g6/scripts/teste_sem_o_conserto.py`) | ramo `verif-para-revisar-2026-10-13`: `.../img/cursus-3-1-pagina-recorte.jpg` |
| R | 13/10 | "Para revisar": medida dependia da prévia; dois cliques gravam ação vazia; sem "está bom" nos avisos de página branca; teclado preso; força escureceu o Palatino 66 | [para-revisar](itens/para-revisar.md) | `fase2-para-revisar`, `ce2b835`. Fica como pergunta: as três contagens que não batem | não achado | ramo `verif-para-revisar-2026-10-13` |

---

## 3. Fechados

| Linha | Data | Bug | Item | Como fechou | Teste | Print |
|---|---|---|---|---|---|---|
| 197 | 25/09 | `EditorImpressao.spec` velho | infra | resolvido 28/09: movido para `velhos/` (Samuel: guardar, não apagar) | — | — |
| 198 | 25/09 | PDF dos relatórios com faixas cinzas e página só com rodapé | infra | **aprovado pelo Samuel** (28/09) | sim: `tests/test_relatorio.py::test_fundo_do_cabecalho_da_tabela_nao_se_repete_nas_outras_paginas` e `::test_rodape_nunca_fica_sozinho_numa_pagina` | [print](../docs/plano/bugs/2026-09-25-relatorio-pdf-faixas-e-pagina-vazia.png) |
| 199 | 25/09 | `relatorio.gravar` corta o nome no último ponto | infra | **aprovado pelo Samuel** (28/09) | sim: `tests/test_relatorio.py::test_gravar_mantem_o_nome_inteiro_mesmo_com_ponto` | — |
| 200 | 25/09 | `markdown` fora do `requirements.txt` | infra | **aprovado pelo Samuel** (28/09) | sim: `tests/test_relatorio.py::test_a_biblioteca_markdown_esta_no_requirements` | — |
| 202 | 28/09 | Quadradinhos brancos na roupa do anjo (Escola 35) | [1.5](itens/1.5.md) | consertado 28/09; o Samuel marcou BOM "roupa e céu do anjo" (B3, conferência de 30/09). A linha da Lista ainda diz "a conferir" | sim: `tests/test_papel_dentro_da_gravura.py` (módulo, 28/09), `::test_sem_degraus_na_grade_de_16_pontos_no_pano` | [print](../docs/plano/bugs/2026-09-28-quadradinhos-roupa-do-anjo.jpg) |
| 207 | 28/09 | Mágico pro apaga a iluminura da Horas 11 | [1.5](itens/1.5.md) | movido para 1.2/1.4/1.5; depois `df9e3be` e **aprovado** (conferência 5, 01/10: "iluminura da Horas 11") | não achado | [print](../docs/plano/bugs/2026-09-28-horas11-iluminura-apagada.jpg) |
| 212 | 28/09 | Palatino 67: caixa cinza em volta de uma linha | [1.2](itens/1.2.md) | resolvido pelo detector do ScanTailor (verificador, 30/09); item 1.2 aprovado em 02/10/2026 | não achado | `relatorios/conferir/fase1-2026-09-28-1644` |
| 219 | 28/09 | Opus 20: degrau no alto da foto | [1.2](itens/1.2.md) | sem o degrau na forma retangular; o Samuel escolheu "Este livro tem fotos" para o Opus 20 (conferência 2, 30/09) | não achado | [print](../docs/plano/bugs/2026-09-28-opus20-degrau-no-alto.jpg) |
| 225 | 28/09 | Palatino 9: tira creme entre os fios da moldura | [1.2](itens/1.2.md) | resolvido pelo 1.2 (verificador, 30/09); 1.2 aprovado 02/10 | não achado | [print](../docs/plano/bugs/2026-09-28-palatino9-tira-creme.jpg) |
| 226 | 28/09 | Detector antigo marca 100% do Palatino 5 e 0% das molduras | [1.2](itens/1.2.md) | resolvido ao ligar o 1.2 (verificador, 30/09); 1.2 aprovado 02/10 | não achado | `relatorios/fase1-1.2-gravura-scantailor-2026-09-28/` |
| 230 | 29/09 | Siebmacher 106 perde manuscrito claro sem aviso | [1.1](itens/1.1.md) | consertado 29/09; **item 1.1 aprovado** em 02/10/2026 (M1). A linha ainda diz "a conferir" | ligado: `tests/test_camadas.py::test_acervo_siebmacher_escrita_clara_nunca_some_sem_aviso` | [print](../docs/plano/bugs/2026-09-29-camadas-siebmacher106-escrita-some.jpg) |
| 232 | 29/09 | 1.1: foto do Opus 20 sai mais clara que o original | [1.1](itens/1.1.md) | `06f747e`; F2 BOM (30/09); 1.1 aprovado 02/10 | sim: `tests/test_camadas.py::test_gabarito_opus20_a_foto_fica_igual_ao_original` | `relatorios/conferir/fase1-2026-09-29-0205/verificador/` |
| 235 | 29/09 | Opus Majus 3 sai "conferir" pelo carimbo | [1.1](itens/1.1.md) | registrado sem conserto: está dentro da regra do Samuel ("página duvidosa sai marcada 'conferir'") | — | — |
| 241 | 29/09 | Alerta do fundo pela prévia não entra no "Para revisar" | [1.1](itens/1.1.md) | `766395f`; 1.1 aprovado 02/10 | sim: `tests/test_tirar_fundo_no_programa.py::test_alerta_que_chega_pela_previa_entra_no_para_revisar` | `.../t03-cinco-cartoes-alerta-mas-para-revisar-vazio.jpg` |
| 251 | 29/09 | Projetos que não aparecem na tela inicial | infra | explicado e resolvido em parte pela linha seguinte (256); "começar de novo" sem cópia foi para a Lista de espera (29/09) | — | — |
| 256 | 29/09 | Projetos antigos invisíveis (sem `resumo.json`) | infra | resolvido pela gerente **com autorização do Samuel** (29/09), com cópia de segurança | — | — |
| 267 | 30/09 | Graduale 222: pedaços da pauta como gravura | [1.2](itens/1.2.md) | `47cabac`; **aprovado** (conferência 2, 30/09: opções do detector, "pauta do Graduale") | ligado: `tests/test_gravura_no_processamento.py::test_figura_julgada_escrita_tira_a_gravura_do_scantailor` | `relatorios/conferir/fase1-1.2-ligacao-2026-09-30/mascaras/graduale_p222.jpg` |
| 268 | 30/09 | Opus 20 piora na forma "livre" | [1.2](itens/1.2.md) | **decisão do Samuel**: "Este livro tem fotos" no Opus 20 (conferência 2, 30/09) | — | `relatorios/conferir/fase1-1.2-ligacao-2026-09-30/` |
| 275 | 30/09 | Horas 11 RUIM: "perdemos bastante da cor original" | [1.5](itens/1.5.md) | `df9e3be`; **aprovado** (conferência 5, 01/10) | não achado | `.../verificador/v01-horas11-iluminura.jpg` |
| 276 | 30/09 | Opus 20 no PB RUIM | [1.2](itens/1.2.md) | **aprovado**: F1 "rosto em cinza" (conferência 6, 02/10) | ligado: `tests/test_conferencia_5.py::test_o_rosto_fora_do_contorno_livre_volta_a_foto` | `.../verificador/v02-opus20-livre-x-retangular.jpg` |
| 278 | 30/09 | Zonas do gabarito do OCR RUINS | [1.3](itens/1.3.md) | `e3fb929`; **zonas aprovadas** (conferência 2, 30/09) | não achado | `relatorios/fase1-1.3-comparacao-ocr-2026-09-28/zonas/` |
| 279 | 30/09 | PB: títulos vermelhos fora da gravura somem | [2.8](itens/2.8.md) | `8c29a7d`; V1 BOM (30/09); **aprovado** "vermelho sai preto" (conferência 5, 01/10) | sim: `tests/test_preto_e_branco_regra_30_09.py::test_titulo_colorido_fora_da_gravura_sai_preto` | `relatorios/conferir/pb-regra-30-09/.../02-horas_p013-3-resultado.jpg` |
| 284 | 30/09 | PB: letras douradas claras da Horas 27 somem | [2.8](itens/2.8.md) | mesmo conserto; aprovado (conferência 5, 01/10, Horas 27) | sim: mesmo teste da linha 279 (cita as "A" douradas da Horas 27) | `.../verificador/c01`, `c02` |
| 290 | 30/09 | Incidente: ~6 linhas de teste no `erros.log` real | infra | **decisão do Samuel** (O2, 02/10): deixar como estão | — | — |
| 291 | 30/09 | **Grave, regra 6:** teste oficial das 16:26 mais lento | [5.1](itens/5.1.md) | resolvido 30/09 (medição commit por commit; o PC estava lento; teste das 22:42 dentro do aceito) | — | [relatório](../relatorios/velocidade/velocidade-SAMUEL-PC-2026-09-30-1626.md) |
| 292 | 30/09 | Mágico pro: moldura dourada escurecida | [1.5](itens/1.5.md) | `df9e3be`; **aprovado** (conferência 5, 01/10) | não achado | `relatorios/conferencia-2-2026-09-30/zonas/` |
| 293 | 30/09 | Mágico pro: faixa cinza na Horas 47 | [1.5](itens/1.5.md) | `df9e3be`; **aprovado** (conferência 5, 01/10) | não achado | `relatorios/conferencia-2-2026-09-30/zonas/z-horas47.jpg` |
| 295 | 30/09 | "A" de "CRISTÃ" cortado (Escola 7) | [2.13](itens/2.13.md) | **não era defeito** (01/10, `3e5f9a3`): era o retângulo rosa desenhado no cartão | — | [prova](../relatorios/corte-crista-2026-10-01/prova-cartao-b6.jpg) |
| 302 | 01/10 | PB, Horas 11: título do oval continua em cor | [1.5](itens/1.5.md) | decisão P4 e conserto de 01/10; **aprovado** (P4, conferência 6, 02/10) | não achado | `relatorios/conferencia-4-2026-10-01/` |
| 304 | 01/10 | PB com decoração em cor: PDF pesado | [1.6](itens/1.6.md) | **decisão do Samuel** (P3, 01/10): "quero ter a opção 1.6, mas quero poder deixar como está também; o tamanho do arquivo depois não importa" | — | `relatorios/conferir/pb-mp-decoracao-2026-10-01/verificador/` |
| 306 | 01/10 | Horas 11: miolo creme nas letras douradas | [1.5](itens/1.5.md) | **aprovado** (A2, conferência 6, 02/10) | ligado: `tests/test_conferencia_5.py::test_miolo_da_letra_dourada_vai_a_branco` | `.../a2-horas11-miolo-das-letras-creme.jpg` |
| 311 | 29/09 | Regra 6: PB 8% mais lento | [5.1](itens/5.1.md) | resolvido (teste oficial de 29/09 18:09: 30,1 s) | — | [relatório](../relatorios/velocidade/velocidade-SAMUEL-PC-2026-09-29-0007.md) |
| 312 | 29/09 | Detector toma título corrido por gravura (Marial 146, 153) | [1.2](itens/1.2.md) | resolvido pelo 1.2 (verificador, 30/09) | não achado | — |
| 313 | 28/09 | Siebmacher 104 e 105: manuscrito some sem aviso | [1.1](itens/1.1.md) | em parte em 29/09; o resto na linha 230; 1.1 aprovado 02/10 | ligado: mesmo teste da linha 230 | [print](../docs/plano/bugs/2026-09-28-camadas-siebmacher104-manuscrito-some.jpg) |
| 314 | 28/09 | Palatino 66 título oco; molduras do 9, 10, 57 furadas | [1.1](itens/1.1.md) | consertado 29/09; F3 "quase cheio, no caminho" (30/09); 1.1 aprovado 02/10 | sim: `tests/test_camadas.py::test_gabarito_titulo_e_molduras_do_palatino_continuam_cheios` | [print 66](../docs/plano/bugs/2026-09-28-camadas-palatino66-titulo-oco.jpg), [print 10](../docs/plano/bugs/2026-09-28-camadas-palatino10-moldura.jpg) |
| 316 | 02/10 | "salvar como (2)" dá erro e não gera o PDF | [layout](itens/layout.md) | `25d916e`; o Samuel pediu "Confira você e depois me diga se deu problema" (S1, 05/10); não deu | sim: `tests/test_ja_existe_arquivo_com_esse_nome.py` (módulo, 02/10) | — |
| 328 | 05/10 | PB ignora o "só neste pedaço" | [1.5](itens/1.5.md) | `60d8c58`; **aprovado** (conferência 13, 05/10: Escola 7 e Opus 20 BOM) | sim: `tests/test_so_neste_pedaco_no_preto_e_branco.py` (módulo, 05/10) | — |
| 347 | 06/10 | **Grave:** "Só as letras" apaga desenho não reconhecido (S do Palatino 76) | [1.5](itens/1.5.md) | `04b225d`; Samuel: **"Bom por enquanto"** (06/10). Restos nas linhas 355, 356 e 347b | ligado: `tests/test_misto_desenho_claro.py` | [print](../relatorios/revisar-criterios-2026-10-06/imagens/hoje-com-razao-palatino076.jpg) |
| 367 | 08/10 | Siebmacher 7 e 9 não são mais divididos | [2.1](itens/2.1.md) | efeito da decisão G2 do Samuel (05/10: dividir só quando o Kaique pedir) e do dividir do ScanTailor de fábrica | — | — |
| 371 | 09/10 | "retangulo" sem acento na faixa do Cortar | [layout](itens/layout.md) | consertado no layout etapa 3 (`6c54817`), aprovado em 13/10 e juntado em 14/10; hoje "Arraste o retângulo" (`ui/tela_conferir.py` linha 2836). A linha ainda está `[ ]` | não achado | ramo `prints-testes`, `2026-10-09_1942_8c07656_fase-1/06-conferir-cortar-maximizada-janela.png` |
| R | 01/10 | Folga do corte ~0,6 mm em vez de 1 mm | [2.13](itens/2.13.md) | decisão P2 e `d93625d`; **aprovado** (C1–C4, conferência 6, 02/10) | ligado: `tests/test_corte_folga_1mm.py` | [LEIA-ME](../relatorios/corte-folga-1mm-2026-10-01/LEIA-ME.md) |
| R | 01/10 | Incidente: agente rodou `git stash`/`stash pop` com arquivos de outro agente | infra | registrado; voltaram sem conflito | — | — |
| R | 06/10 | Três livros reais com o histórico do desfazer errado (Consolação ×2, gradus-primus) | infra (histórico) | registrado: o livro não perde nada; o Ctrl+Z só alcança a última ação; cópia guardada; aviso na Lista de espera (06/10) | — | — |

---

## Contradições achadas

- **Linha 366 (conftest) diz "não juntado"**, mas o `fase-1` tem o merge `a358d4e` de 09/10 ("Samuel, 09/10: autorizou
  juntar ao programa"; também no histórico, PARTE -14). Vale: **juntado**. A linha da Lista ficou para trás.
- **Linha 371 ("retangulo") está `[ ]`**, mas o texto já sai com acento no `fase-1` (layout etapa 3, juntado em 14/10).
- **Linhas 202, 230, 241 e 314** dizem "a conferir", mas o Samuel marcou BOM nas conferências seguintes ou aprovou o
  item inteiro (1.1, em 02/10/2026). Vale o mais novo (as aprovações); a linha da Lista não foi atualizada. A linha 201
  (corte da Escola 35) também diz "a conferir", e o Samuel marcou BOM o corte da Escola 35 (B1, 30/09); Horas 26 e 27
  ficaram sem marca, por isso ela continua entre os "a conferir".
- **Linha 317** (02/10, `_escolher_forca`) continua sem marca, e a linha 381 (12/10) é o mesmo bug marcado `[x]`
  "consertado no ramo `fase2-para-revisar`". No `fase-1` o defeito continua (o ramo não foi juntado).

## Atualização de 21/10/2026 (bugs de 20/10 e o que foi consertado)

Fonte: Lista de bugs do [plano](../docs/plano/PLANO-DEFINITIVO.md) (linhas de 20/10) e [PARTE -17](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md).

| Data | Bug | Item | Situação em 21/10/2026 |
|---|---|---|---|
| 20/10 | **Instalador sem a `st_ferramentas.dll`** (achado pelo montador da memória): `empacotar.py` e `instalador.iss` levavam só a `st_gravura.dll`; um instalador novo cairia no caminho "nosso" sem avisar | [6.8](itens/6.8.md) | **consertado** no ramo `consertos-2026-10-21` (`2ff16e7`, as duas DLLs, com teste de que o pacote as contém); verificado até `4c53152`; falta GitHub do `2ff16e7` e a parada no PC para juntar |
| 20/10 | **O mesmo código nem sempre dá a mesma imagem** (Horas 11, Mágico pro; achado pelo Implementador 5): com pouca memória o modelo de regiões ficava desligado a sessão inteira e o detector de gravura caía no antigo; provas de "sai igual" por soma podiam acusar diferença falsa | [para-revisar](itens/para-revisar.md), `core/filtros.py` | **consertado** em `2ff16e7` (tenta de novo); mesmo ramo, não juntado |
| 20/10 | **Teste que depende da ordem**: `tests/test_paineis_na_tela.py::test_espelhado_e_proporcao_travada_sao_caixinhas_e_as_teclas_valem` falhou na suíte inteira no PC ("Espelhado   (tecla )": tecla vazia, herdada da configuração de atalhos de outro teste); passa sozinho; não é do conserto do corte | testes | **consertado** no ramo `consertos-2026-10-21` (teste dos atalhos); não juntado |
| 20/10 | **2.8: a queda para o Automático não vai ao `erros.log`** | [2.8](itens/2.8.md) | mandado ao implementador; o ramo `fase2-scantailor-itens-2026-10-19` traz o erros.log do ScanTailor |
| 21/10 | **"Parece em branco" errava (Gladstone 18)**: consertado; passa a avisar 49% das páginas do Egenloff (versos realmente vazios); acima de 70% vira aviso do livro inteiro | [para-revisar](itens/para-revisar.md) | consertado em `consertos-2026-10-21`; pergunta de aviso único do livro inteiro aberta |
| 21/10 | **Etiqueta do Egenloff 3 cortada ao meio** com as duas opções (caixa do conteúdo + borda preta) | [2.13](itens/2.13.md), [2.5](itens/2.5.md) | **aberto**: o conserto começado (`ed68928`) não funciona na página real |
| 21/10 | **Passada que mede o livro 2-3× mais lenta** com as opções da caixa ligadas (Marial 100 folhas ~140 → ~300 s) | [2.13](itens/2.13.md), [5.1](itens/5.1.md) | **aberto**; rodada de velocidade 39623840809 não lida |
| 22/10 | Aviso "Corte deixou algo de fora" toca sem precisar (82/100 Marial, 12/14 Egenloff: beirada, sombra, sujeira, verso, faixa SLUB); Egenloff 3: corte antigo na 1ª vez na janela; carimbo oval partido | [2.5](itens/2.5.md), [2.13](itens/2.13.md) | **aberto**: decisão "O aviso só conta o que parece impresso"; Samuel: "deixe isso anotado pois vai precisar ser resolvido"; próximo do Implementador A, depois do 2.12 |
| 21/10 | **A janela do programa sumiu uma vez, sem log**, ao clicar "Deixar em branco" (Egenloff 12); 62 cliques depois não repetiu | [6.5](itens/6.5.md) | **aberto**, suspeita de falta de memória com muitos agentes |
| 20/10 | Faixa preta do corte do G6 (Cursus 3, Matemática 32, Antiphon 88 e 260, Camões 104; Pesel 21 como efeito de lado) | [2.2](itens/2.2.md), [2.13](itens/2.13.md) | conserto **juntado** ao `fase-1` (`f418cc3`) com teste de reversão provado; "Melhorar" nas cinco páginas (tirar todo o preto é o 2.13) |
| 19/10 | Mágico pro +1,1% do "Para revisar" | [5.1](itens/5.1.md) | **Fase 5** ("vamos deixar esse concerto de lentidão para o final, para a fase de desempenho.") |

Bug de 13/10 "G6 deixa faixa preta larga" (tabela "Em ramo, não juntados" acima) deixou de estar em ramo: juntado em 20/10/2026. Os três consertos de `consertos-2026-10-21` seguem a regra do teste de reversão (o verificador prova antes de juntar).

## Atualização de 24/10/2026 ([PARTE -20](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §3 e §4)

- **Lista única de 23/10** (`relatorios/testes-guiados/lista-unica-2026-10-23/lista.html`): 50 problemas de uso e de imagem achados pelo Samuel (sessão 0), pelo mapa e pelos 14 livros. É a base da rodada de consertos que vem **depois** dos testes guiados (decisão "A — Tudo junto no fim"). Na Lista de bugs do plano entraram, por ora: "está certo" sem resposta na tela; moldura escura no desentortar; Righetti 96 sem pergunta.
- **Consertado na junção (23/10, `ff1f6cd`):** testes dependentes da ordem pelo aviso "Gravuras e fotos" (fixture `_aviso_da_gravura_limpo` em `tests/conftest.py`). Não é bug do programa.
- **Aberto desde 29/09, reencontrado:** mudar as caixinhas de um livro já conferido não vale (a tela volta igual).

## Atualização de 26/10/2026 (etapa 0 da obra: Livro de decisões)

Conferido no `git` (só leitura), para a etapa 0 não confiar no que ficou velho:

- **"Em ramo, não juntados" (§2) já estão todos no `fase-1`:** `b5b224f` (linha 238), `ce2b835` (`fase2-para-revisar`:
  linhas 317/381, 344, 364 e o R de 13/10) e `d97b937` (linha 389, G6). A tabela continua como registro.
- **Linha 317/381 (`_escolher_forca`):** a função existe no `fase-1` (`ui/tela_conferir.py:5145`, chamada na 5117). O
  "No `fase-1` a chamada continua sem a função" ficou velho.
- **Instalador sem a `st_ferramentas.dll` (20/10):** o conserto `2ff16e7` está no `fase-1` (`empacotar.py:151`). Os
  outros dois consertos do ramo `consertos-2026-10-21` também. O instalador continua `[~]` até o Samuel instalar e
  testar (linha 196).
- Os consertos desta ficha que mudam o que o Samuel vê foram listados, em formato curto, em "Consertos esperando o
  olho do Samuel" no fim do Livro de decisões (`docs/plano/DECISOES.md`): uma página de conferência só, no fim da obra.


## Achados de 28/10/2026 (sessão 2 de testes e agentes da conferência; versão de teste `obra-2026-10-26`)

Todos só anotados; nada consertado. Detalhe e prints em `relatorios/testes-guiados/2026-10-28-sessao-2/sessao-2.md` e
na Central (aba "O que você não gostou: alternativas").

- **Painel Filtro, "Mais ajustes", nomes cortados a 1280 x 657:** "Igualar a luz da página / Suavizar as letras / Tirar
  o chuvisco" saem "Igual / Suav / Tirar o chu"; o resumo ao lado de "Mais ajustes" perde o começo. Contra a D-059.
  Visto em print fora da tela (offscreen); conferir na janela de verdade. (agente das dúvidas, 28/10)
- **Possível: "está bom assim" desenhado por cima do cartão de baixo no "Para revisar"** ao trocar o lado direito para
  "Abas no alto" ou "Painel solto" numa página sem aviso. Só em print fora da tela; não conferido na janela de verdade.
  (agente das perguntas, 28/10)
- **Marcação lenta com muitas marcas (2-1):** dois cliques da Varinha no papel do Cursus p.1 = 151 + 151 marcas
  repetidas; cada mexida grava as 302 no histórico (563 KB) e para a tela 0,7 a 1,5 s.
- **"Ver de perto" espera na fila (2-8):** Palatino p.13, 14 s na fila de prévias (2 fios ocupados) + 6 s desenhando.
- **Aviso de falta de memória culpa o livro (2-12):** `ui/tarefas.py`; faltou memória no PC (pedaços de 3,6 e 18 MB) e
  a frase manda usar uma "qualidade normal" que não existe.

## Achados de 29/10/2026 (trabalho do Automático, versão de teste `obra-2026-10-26`)
- **Figurinhas do painel "Filtro da página" não usam a marcação (achado do agente, investigação da D-582):** com o
  Mágico pro escolhido na capa do *Na escola de Jesus*, a figurinha do Preto e branco mostra a capa toda em preto e
  branco, mas ao clicar a página sai colorida (a marcação do Automático guarda a cor da gravura). Faz parecer que o
  filtro não foi aplicado. Prints em `relatorios/automatico-filtro/1-uma-pagina-preto-e-branco.jpg` e `2-...` (ramo
  `automatico-filtro-2026-10-29`). Pergunta ao Samuel: as figurinhas devem mostrar a página com a marcação?
- **Pintura confundida com enfeite no Preto e branco (D-585), ACEITO ATÉ DEPOIS pelo Samuel em 29/10** ("deixar como
  está e deixar anotado, vamos continuar para o que temos que fazer"): título/escrita por cima da pintura somam traço e a
  pintura cai em "enfeite" (guarda a cor sem "Só as letras"); 4 de 99 pinturas do *Na escola de Jesus* (capa, p.19, 45,
  173). Nenhum limite seguro (tela 110 dpi × PDF inverte a ordem; Horas 11 iria a cinza). Opções B/C/D e imagens em
  `relatorios/automatico-pintura/` (versão de teste).
- **Preto e branco sem marcação: tela ≠ PDF nas gravuras (achado do verificador da D-586, 29/10; já existia no
  `2db002e`):** com a caixinha "Respeitar as gravuras achadas" desligada (ou livro sem "Gravuras e fotos"), a tela
  (110 DPI) mostra rostos e roupas muito mais pretos e com blocos quadrados que o PDF (300 DPI). Diferença média tela ×
  PDF: capa 12,6, página 9 35,3 (*Na escola de Jesus*); com a caixinha ligada, 7,5. Contra a D-066/D-473.
- **Original: o primeiro desenho da página logo depois do Automático sai um pouco diferente dos seguintes (achado do
  construtor da D-586, 29/10; já existia no `2db002e`).**
