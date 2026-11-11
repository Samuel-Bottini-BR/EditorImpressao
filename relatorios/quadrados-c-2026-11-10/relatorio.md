# Quadrados brancos: o conserto C (D-668) no programa

**Agente de conserto, 10/11/2026.** Ramo `quadrados-c-2026-11-10`, a partir do `obra-2026-10-26` (`58806f81`).
Tudo sem janela, em cópia, com dados à parte; o acervo só foi lido. Teste de **máquina** (medidas e provas em
`tests/`); as imagens são para o **olho** do Samuel. PRONTO PARA CONFERIR (só ele aprova).

## Em uma frase

**O Melhorar e o Mágico pro não fazem mais buracos brancos nas pinturas, e o "i" e o "t" finos voltam inteiros.**
O programa consertado saiu igual, ponto por ponto, à simulação C que o Samuel escolheu: na página 13 (tela e PDF)
e no livro inteiro, com os mesmos números.

Decisão: D-668 (Central `quadrados-qual`: "Roxo: o conserto C (recomendo)"; no chat: "c").

## O que mudou no programa

1. **Uma regra só para os três filtros** (D-667: "se mudou a ferramenta, muda em todos os lugares"). Com
   "Respeitar as gravuras achadas" marcada, num filtro escolhido à mão, a página procura a gravura no Preto e
   branco, no Melhorar e no Mágico pro (antes, só no Preto e branco, D-659). Só a página onde a opção vale é
   procurada (a da tela, ou as que o "Aplicar em" alcançou), como a D-659 manda. A lista dos três filtros mora num
   lugar só (`core/filtros.py`, `FILTROS_QUE_RESPEITAM_AS_GRAVURAS`) e responde às duas perguntas da caixinha:
   "marcada, procura?" (`core/etapas.respeitar_procura`) e "desmarcada, o que a máquina achou sai do filtro?"
   (`core/pipeline.marcacao_que_o_filtro_usa`). Não há desvio "se for Melhorar". No Preto e branco nada muda.
2. **A limpeza do papel do Melhorar e do Mágico pro ganhou uma quarta pergunta: "em volta também é papel?"**
   (`core/filtros.py`, `_em_volta_e_papel`, no fim de `_limpar_o_papel_de_verdade`, fora da gravura). Vale com a
   caixinha marcada ou desmarcada (o print 10).
3. Não mudou: a tela (`ui/`), o Original, as páginas com gravura marcada à mão (conferido: iguais ponto por ponto),
   a correção do "magic color" (CLAUDE.md §9) e o papel de dentro da gravura (bug 202).

## As medidas, antes e depois

"Antes" = o programa do `obra-2026-10-26` (`58806f81`). "Depois" = este ramo. Livro novo, sem o Automático, filtro
escolhido à mão (Melhorar "bem forte" e Mágico pro "bem fraco", os ajustes dos prints 09 e 10), página dividida,
endireitada e cortada como o programa faz, como sai no PDF (300 DPI). "Respeitar" marcada, menos onde está escrito.

### Página 13 do *Na escola de Jesus* (Jonas e a baleia)

- **A água da baleia não tem mais buracos.** Pintura de tom médio que virou branco puro, na água: antes 63,9%,
  depois 0,2% (Melhorar e Mágico pro).
- **O "i" de "Vivia" e de "dia" voltou inteiro.** Tinta dessas letras que virou branco: antes 3,3%, depois 0,0%.
- **Pela medida da investigação da origem** (a pintura inteira, sem dividir nem cortar): Melhorar 23,5% → 1,4%;
  Mágico pro 27,4% → 1,4% (a simulação dava 1,4%; antes da obra, 1,4%).
- **Print 10** (Mágico pro, "Respeitar" desmarcada: nada é procurado, D-586): **27,4% → 5,8%**, como a simulação. Na
  água ampliada, 63,9% → 0,0%; os 5,8% que sobram ficam perto da beirada da pintura. **As letras, nesse caso, ficam
  como hoje** (o "i" continua quebrado: 3,3%), porque sem a gravura achada a letra não recebe o tratamento de
  letra. Era o que a simulação já mostrava (imagem 4).
- **Igual à simulação C, ponto por ponto**, na tela (prévia) e no PDF, com "Respeitar" marcada (Melhorar) e
  desmarcada (Mágico pro).

### O livro inteiro (*Na escola de Jesus*, 199 páginas)

| | Melhorar | Mágico pro |
|---|---|---|
| páginas com quadrados, antes (investigação) | 110 (32 muito, 47 visível, 31 poucos pontos) | 112 (34, 50, 28) |
| simulação C | 2 (119 visível, 68 poucos pontos) | 2 (as mesmas) |
| **depois (o programa)** | **2 (119 visível, 68 poucos pontos)** | **2 (as mesmas)** |
| furo de 2% ou mais na pintura, com o céu claro (medida 2): antes / C / **depois** | 113 / 16 / **16** | 136 / 16 / **16** |
| furo de 0,5% ou mais: antes / C / **depois** | 154 / 68 / **68** | 169 / 67 / **67** |

As 16 que sobram são as mesmas da simulação: quase todas brilhos que já são brancos no original e o papel de dentro
de desenho de traço (a basílica da página 43). A pior de verdade é a 173 (o céu em volta dos anjos).

As oito pinturas da investigação da origem (páginas 13, 18, 29, 36, 51, 66, 97 e 119): depois, de 0,4% a 3,9% —
a faixa de antes da obra ("de 0,5% a 3,9%").

### Livro de Horas 47 e as páginas do gabarito do assunto

- **Livro de Horas 47: a pintura sai inteira, com o prédio e o céu de trás.** Medida da origem: 2,6% → 0,07%
  (Melhorar) e 0,08% (Mágico pro). Medida 1: 1,10% → 0,04%.
- **Gabarito da Fase 1 e da Fase 3 (Boécio)**, mais Escola 13, 97, 119 e Boécio 33 (24 páginas, `medidas/paginas_*.json`).
  Pintura que virou branco caiu em quase todas (Escola 7: 1,37% → 0,01%; Escola 35: 1,25% → 0,02%; Escola 97:
  3,2% → 0,03%; Escola 119: 4,8% → 0,06%). A tinta das letras que virou branco caiu em todas (Palatino 7: 2,4% →
  0,2%; Opus Majus 256: 5,4% → 0,2%; Escola 13: 3,3% → 0,01%).

### Tempo (a ressalva já dita ao Samuel)

A primeira vez que cada página é desenhada com Melhorar ou Mágico pro e "Respeitar" marcada, o programa procura a
gravura. **Nas páginas do *Na escola de Jesus*, uns 5 segundos a mais** (ex.: página 13, 2,6 s → 7,4 s). Nas 24
páginas do gabarito, 3,5 s a mais em média; **nas grandes do Livro de Horas, até 10 a 11 s a mais** (Horas 47:
6,5 s → 16,6 s). Livro inteiro, depois: 8,6 s (Melhorar) e 9,1 s (Mágico pro) por página na primeira vez, como na
simulação (9,0 s e 9,3 s). Da segunda vez em diante a gravura fica guardada na página. Medido no PC do Samuel, com
prioridade baixa; a medida que vale é o filtro de velocidade do GitHub (abaixo).

## Números que pioraram (CLAUDE.md §5: os dois resultados, sem decidir sozinho)

Todos vêm da mesma coisa que o Samuel já aceitou na D-668: com "Respeitar" marcada, a página sai **como sai hoje
depois do Automático** (gravura com o tratamento de gravura, letra no tom do original).

1. **"Papel branco" mais baixo em algumas páginas com pintura** (Escola 7: 88% → 86%; Escola 97: 90% → 80%; Horas
   47: 82% → 78%). Olhado: não é papel amarelado; é a parte clara da pintura (céu, nuvens) que a medida conta como
   "papel" e que agora fica com o tom dela em vez de virar branco. É o conserto.
2. **"Pintura que virou branco" sobe no Palatino 5 (1,3% → 5,2%) e no Boécio (página 7: 3,6% → 4,2%; página 33: 4,5% → 5,3%).**
   Olhado: no Palatino 5, é o papel entre os traços do retrato que vai a branco (a regra da Fase 1: "todo o papel
   totalmente branco, inclusive o papel dentro da gravura"); no Boécio, é **mais** mancha do verso indo a branco (a
   faixa cinza entre as linhas some; imagem 5). As duas mudanças são para melhor.
3. **A cor do papel sobe um pouco em páginas de texto com letra achada** (saturação média do papel: Opus Majus 11 e
   165: 0,0 → 0,8 e 0,5). Olhado: as letras ficam no tom do original, um pouco menos escuras, e a orla delas tem um
   pouco do tom do papel. É a ressalva da investigação (Rhetorica 73: "papel branco, mas com contorno bege em volta
   das letras"). Pequena, mas existe.
4. **Tempo**: ver acima.

## Imagens (no modelo do girar: azul = antes, verde = depois, o que olhar circulado em vermelho)

- `imagens/1-resumo-pagina-13.png` — resumo: página 13, Melhorar, página inteira, a água e "Vivia".
- `imagens/2-melhorar.png` e `imagens/3-magico-pro.png` — água (Escola 13), céu (Escola 97), "Vivia" (Escola 13) e
  o prédio (Horas 47), com a faixa do original para comparar.
- `imagens/4-print-10-respeitar-desmarcada.png` — o print 10.
- `imagens/5-o-que-ja-estava-bom.png` — mancha do verso (Boécio 33), xilogravura (Boécio 3), retrato (Palatino 5)
  e o anjo (Escola 35).

## Provas e testes

- **Prova nova** `tests/test_decisoes_quadrados_brancos.py` (17 provas: a conta, a página sintética, a tela no livro
  novo com clique de verdade, a página 13 do livro dele). **Reversão** (CLAUDE.md §4.7): no código de antes
  (`58806f81`) 12 falham e 5 passam (as 5 guardam o que não pode mudar: página de texto igual, nada procurado com a
  caixinha desmarcada, Preto e branco igual ponto por ponto); no ramo, 17 passam. As medidas que falham no código de
  antes: água sintética 48,4% em branco; água da página 13 64,0%; a gravura nunca procurada no Melhorar e no Mágico
  pro (`reversao-no-58806f81.txt`).
- **No PC, um arquivo por vez** (prioridade baixa, sem janela): os 56 `tests/test_decisoes*.py` e mais 22 dos arquivos
  tocados (`test_papel_dentro_da_gravura`, `test_core`, `test_limpar_papel`, `test_melhorar_em_volta_da_gravura`,
  `test_filtro_com_selecao`, `test_etapa10b_imagem`, `test_misto*`, `test_conferencia*`, `test_promessas` e outros):
  **1419 passaram, 2 pularam, 3 falharam** — só as 3 provas antigas da D-659 da ressalva 1 (`medidas/testes_no_pc.txt`).
- **GitHub, todos os testes** (rodada 42932052865): as partes 1, 2, 3 e 5 e os botões e prints da janela real
  passaram; na parte 4, só as mesmas 3 provas da D-659. A prova nova: 13 passaram, 4 pularam (o livro dele não está
  no GitHub).
- **GitHub, filtro de velocidade** (rodada 42932057632, `obra-2026-10-26` × este ramo, mesma máquina, alternado):
  **"igual (dentro do vai-e-vem)"**. Abrir o livro +0,1%; trocar de página +0,7%; Mágico pro 10 páginas +3,5%
  (vai-e-vem 4,1%); Preto e branco 10 páginas +1,1%. Ele mede o livro com "Limpar a folha" ligado, que já procurava a
  gravura; a primeira vez do filtro escolhido à mão está na seção "Tempo".

## Ressalvas

1. **Três provas antigas da D-659 falham, e não foram mudadas** (CLAUDE.md §11.8). Elas guardam justamente o que a
   D-668 manda mudar: "Melhorar e Mágico pro escolhidos à mão não procuram" (`tests/test_decisoes_gravura_a_mao.py`:
   `test_d659_a_conta_quem_procura_com_limpar_desligado`, linha 242-243, e
   `test_d659_g_outros_filtros_a_mao_nada_e_procurado_e_sai_igual_ao_de_antes[melhorar]` e `[magico_pro]`). A do
   Original (`[original]`) continua passando. Ver "Perguntas para o Samuel" no ONDE-PAREI.
2. **Com "Respeitar" desmarcada, o "i" e o "t" continuam quebrados** (print 10): a quarta pergunta tira os buracos
   da pintura, mas a letra só volta inteira quando a gravura é achada. É o que a simulação mostrava; não acrescentei
   nada além do C.
3. **Página com gravura marcada à mão DEPOIS de escolher o Melhorar** (a gravura da máquina já foi achada): a
   marcação à mão vai por cima da achada, como no Preto e branco (D-659). Marcada ANTES de escolher o filtro, a
   página sai igual, ponto por ponto, à de hoje (medido na página 13, Melhorar e Mágico pro).
4. Os números 80% e "uns 2% da página" da quarta pergunta são os da simulação (o Samuel escolheu o C com eles);
   ficaram em constantes com o porquê escrito (`VIZINHANCA_DE_PAPEL`, `VIZINHANCA_JANELA`).
5. Não pilotei a janela. A tela desenha pela mesma conta (`renderizar_pagina`), e as provas de tela rodaram sem
   janela (offscreen), com clique de verdade nos botões do painel.
