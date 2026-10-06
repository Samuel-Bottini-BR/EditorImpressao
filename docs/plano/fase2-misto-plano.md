# Fase 2, modo Misto: levantamento e plano (05/10/2026)

Escrito pelo implementador, ramo `fase2-misto` (criado do `fase-1` em `aab746f`). **Não muda o
PLANO-DEFINITIVO.** Pedido do Samuel (conferência 5, X3): "eu quero ter a opção de colocar [o filtro]
onde eu escolher, se quero só nos textos ou nas gravuras, como tem no ScanTailor Advanced". Proposta
aceita (D1, 02/10): "Modo Misto: o Preto e branco só nas letras; gravuras e fotos ficam como estão; e
você corrige à mão, marcando zonas, onde o automático errar." Regra já decidida (30/09, item 1.5):
"Só as letras" marcada, "só as letras viram preto e branco, e gravuras, fotos, molduras, iluminuras e
outros detalhes coloridos ficam como no original. Vale para o livro inteiro ou para uma página só."

Medidas e imagens desta página: `relatorios/fase2-misto-2026-10-05/` (scripts em `scripts/`).

---

## 1. O que já existe e serve

Conferido no código, não só nos documentos.

| Peça | Onde | Serve ao Misto? |
|---|---|---|
| Detector de gravura do ScanTailor (1.2, aprovado) | `core/gravura_scantailor.py`, chamado por `core/detectar_regioes.detectar` | **Sim, é a máscara do Misto.** A zona "gravura" já chega pronta na marcação da página (`Selecao`), com as opções do livro e a forma por página. |
| Marcação da página (aba Marcar) | `core/selecao.py` (`Selecao`, `Regiao`: tipo gravura/letra/papel/fora, somar/tirar, origem máquina/mão, filtro "só neste pedaço") | **Sim.** Uma lista só, máquina e mão juntas, na ordem. Guarda forma, não imagem. Outro agente está mudando onde ela é **guardada** (na folha original); o jeito como o filtro a recebe (um `Selecao` em memória) continua o mesmo. |
| Preto e branco de hoje | `core/filtros.filtro_preto_e_branco` (escolha automática Sauvola/Otsu, `k` pela letra, medidor, vermelho e letra colorida pretos, limpeza de pontinhos) | **Sim, é o preto e branco das letras.** Todas as regras aprovadas moram aqui. |
| Preto e branco com gravura | `core/filtros._preto_e_branco_com_gravura` | **Em parte.** Já separa cada zona em foto, decoração colorida e desenho (`_tipos_das_zonas`), e a decoração já sai com a cor original e a letra solta preta (N2, P4). Hoje a foto sai em cinza e o desenho em 1 bit; no Misto os dois ficam como no original. |
| "Só neste pedaço" | `core/filtros._filtro_so_no_pedaco` | **Sim.** Mas hoje **não vale no Preto e branco** (ver "Achado", abaixo). |
| Tipos de preto e branco | Sauvola, Otsu, Wolf (DoxaPy), campo `ConfigPagina.algoritmo_preto_branco`, "auto" de fábrica | Sim, sem mudança. Os 10 do ScanTailor (`Binarize.cpp`) seriam opções a mais (2.8). |
| Limpar pontinhos | `core/filtros._despeckle` (só o tamanho da mancha), caixinha `ConfigPagina.despeckle` | Sim. O do ScanTailor (`Despeckle.cpp`, poupa o pingo do "i" perto da letra, força 0,5–3,5) é o 2.7. |
| OCRs do 1.3 | `core/ocr_doctr.py`, `core/ocr_kraken.py`, `core/ocr_comparar.py` (voto por linha) | **Hoje só acham onde há texto; não entram em filtro nenhum.** Ver a seção 6. |
| O Misto do ScanTailor | `OutputGenerator.cpp`, `processWithoutDewarping` (resumo em `docs/pesquisa/fase2-mapa-scantailor.md`, seção 5) | É o modelo: página inteira em preto e branco, máscara diz onde fica o original, cinco tipos de zona à mão corrigem a máscara. **O papel dentro da imagem fica creme** (contra a regra R1). |

**Achado (bug que não impede, vai para a Lista de bugs):** no filtro Preto e branco, o "só neste
pedaço" da aba Marcar **é ignorado**. `aplicar_filtro_com_selecao` sai pelo ramo do Preto e branco
antes de chamar `_filtro_so_no_pedaco`. Conferido numa página sintética: zona com "só neste pedaço =
Original" sai preta (letra) ou cinza (gravura) no Preto e branco; no Mágico pro sai com a cor
original. Ou seja, o "Foto em Original dentro de uma página em Preto e branco" da Lista de espera
(01/10) **não funciona hoje**, ao contrário do que ela diz ("parte disso já existe"). No Misto ele vale.
Não consertei no Preto e branco porque isso muda o caminho de hoje (pergunta P6).

## 2. O que falta em `core/`, em passos pequenos

| # | Passo | Muda tela/formato? | Estado |
|---|---|---|---|
| M1 | `core/misto.py`: `aplicar_misto(img, selecao, ...)`: preto e branco da página inteira; onde é imagem, o original (foto como está; decoração e gravura de traço com a cor original e só o papel a branco); zonas à mão mandam; "só neste pedaço" vale; papel marcado a branco. Página sem gravura sai **idêntica** ao Preto e branco de hoje. | Não | **Feito nesta tarefa** (parte B) |
| M2 | `montar_misto.py`: o Misto de um PDF por linha de comando, pelo mesmo caminho do programa (analisar → página preparada → marcação → Misto). | Não | **Feito** |
| M3 | Ligar ao pipeline: `_filtrar` chama o Misto quando a página (ou o livro) pede. | **Sim (formato):** precisa de um campo no projeto | Pergunta P1 |
| M4 | Limpar pontinhos do ScanTailor (2.7), como opção do preto e branco das letras. | Sim (controle de força) | Pergunta P7 |
| M5 | Mais tipos de preto e branco (2.8): os do ScanTailor como opções a mais, sem trocar o "auto". | Sim (lista na aba Filtro) | Pergunta P8 |
| M6 | Claro no escuro (2.9): inverter na entrada e na saída, só à mão. | Sim (caixinha por página) | Pergunta P9 |
| M7 | Cores (2.11): "letras com a cor delas" (segmentação do ScanTailor) como opção do Misto. | Sim | Pergunta P10 |
| M8 | Tipos de zona do ScanTailor que o nosso não tem ("tinta com a cor original e papel branco", "tinta preta e fundo como está", "preencher com uma cor"). | Sim (aba Marcar) | Pergunta P11 |
| M9 | DLL comum (`st_ferramentas`) para 2.7/2.8/2.9/2.11, do jeito do 1.2. Só quando P7–P10 disserem que entram. | Não | depois |

M4–M9 dependem de resposta; nenhum foi feito.

## 3. Perguntas ao Samuel (o que exige mudar tela, controle ou formato do projeto)

Texto pronto, com opções. A recomendação vem marcada.

- **P1. Onde o Kaique liga o Misto?** (muda a tela e o projeto salvo)
  (a) **caixinha "Só as letras" dentro do Preto e branco**, por livro (tela "O que fazer") e por
  página (aba Filtro), como você decidiu em 30/09 *(recomendado: já é a sua decisão, e é um campo a
  mais no livro e um na página)*;
  (b) um quinto filtro "Misto" ao lado dos outros quatro;
  (c) duas listas, "Texto em: [filtro]" e "Gravuras em: [filtro]" (mais geral, mais difícil para o Kaique).
  Posso criar os campos novos no projeto (com projeto antigo abrindo desmarcado)?
- **P2. No Misto, o papel de dentro da gravura:** (a) **vai a branco, só o desenho fica como no
  original** *(recomendado; é a regra R1, "todo o papel totalmente branco, inclusive dentro da
  gravura")*; (b) fica creme, como no original (o Misto do ScanTailor). Imagens:
  `relatorios/fase2-misto-2026-10-05/variantes/`.
- **P3. No Misto, a foto:** (a) **fica como no original, com a cor** *(recomendado: "fotos ficam
  como estão")*; (b) em tons de cinza, como no Preto e branco. Imagens: as mesmas variantes.
- **P4. Letras dentro da moldura ou da iluminura** (títulos do oval da Horas 11, "NOVEMBRE."):
  (a) **pretas, como no Preto e branco de hoje (P4 de 01/10)** *(recomendado)*; (b) com a cor original.
- **P5. A caixinha "No Preto e branco, molduras e iluminuras também em preto e branco" com "Só as
  letras" marcada:** (a) **não vale (o Misto deixa a moldura em cor)** *(recomendado)*; (b) vale.
- **P6. O "só neste pedaço" no Preto e branco de hoje é ignorado (achado acima).** (a) consertar já no
  Preto e branco (muda só as páginas que têm pedaço marcado); (b) deixar valer só no Misto.
- **P7. Limpar pontinhos (2.7):** (a) **trazer o do ScanTailor como opção, com controle "pouco /
  normal / muito"** na aba Filtro, e o nosso continua de fábrica até você comparar; (b) trocar o nosso
  pelo dele; (c) deixar para depois.
- **P8. Tipos de preto e branco (2.8):** a aba Filtro hoje mostra "Algoritmo: Sauvola / Otsu / Wolf"
  (jargão, na Lista de bugs). (a) **manter só "automático" na frente e os três em "mais opções", com
  nomes comuns** *(recomendado)*; (b) trazer os 10 do ScanTailor como opções a mais.
- **P9. Claro no escuro (2.9):** (a) **caixinha por página "Letra clara em fundo escuro", sem
  detecção automática** *(recomendado; a Lista de espera de 28/09 já sugere não trazer a automática)*;
  (b) com detecção automática.
- **P10. Cores (2.11):** "letras com a cor delas" no Misto contraria "o vermelho sai preto".
  (a) **opção desligada de fábrica** *(recomendado)*; (b) não trazer.
- **P11. Tipos de zona à mão (aba Marcar):** hoje há gravura / letra / papel / fora e "só neste
  pedaço". (a) **acrescentar "preencher com uma cor" (apagar carimbo e mancha) e copiar/colar/mover
  zona** *(recomendado: são os que o nosso não tem; "tinta com a cor original" já é o "só neste
  pedaço = Original")*; (b) os cinco tipos do ScanTailor com nomes comuns; (c) nada por enquanto.
- **P12. Usar as linhas dos OCRs no Misto** (seção 6): (a) **ainda não; primeiro o Misto sem OCR,
  e o OCR só como "segunda opinião" depois do estudo do pesquisador** *(recomendado)*; (b) já.

## 4. Páginas-gabarito para conferir o Misto

Obrigatórias (pedido da gerente): **Palatino 5** (retrato, fundo branco), **Palatino 9** (capitular
xilográfica e moldura), **Escola de Jesus 7** (gravura colorida e texto), **Horas 11** (iluminura
inteira), **Horas 13** (moldura dourada, títulos vermelhos), **Horas 47** (iluminuras, A1),
**Opus Majus 20** (foto da estátua), **Graduale 221 e 222** (pauta, notas, capitulares), **Opus
Majus 165** (diagramas com letrinhas). Mais: Horas 26 ("NOVEMBRE." dentro da moldura), Escola 35
(anjo pintado), Palatino 67 (caixa cinza antiga), Marial 7 (canto de papel marcado como foto),
Opus 256 (tabela). A rodada desta tarefa cobriu as 32 do gabarito.

## 5. Riscos

1. **O Misto mostra direto cada erro do detector.** Onde o ScanTailor marca papel ou mancha como
   gravura, o Misto deixa o original ali (Marial 151: mancha de canto; Horas 26: papel liso dentro
   da moldura; Horas 13: triângulo sobre "pag. 54"). Onde ele **não** marca (capitular do Palatino 9,
   as duas molduras do Palatino 9), sai preto e branco como hoje. A correção à mão (zonas) é o remédio,
   e é por isso que a proposta junta as duas coisas.
2. **A letra fica como a do Preto e branco de hoje**, com os mesmos defeitos: o A1 da Horas 47
   ("pixels apagados no meio das letras", Lista de bugs) continua no Misto.
3. **PDF pesado:** toda página com gravura sai em cor (Lista de bugs, 01/10: até 25 MB por página). O
   remédio natural é o 1.6/2.10 (duas camadas).
4. **Velocidade:** o Misto custa o preto e branco mais o tratamento das zonas; medido na rodada
   (relatório da parte B). Desligado, nada muda (provado por imagens idênticas).
5. **Zonas guardadas em outro lugar (D2, outro agente):** o Misto só lê o `Selecao` em memória; se o
   formato em memória mudar, `core/misto.py` muda junto.
6. **"Letra marcada à mão ganha da gravura"** é uma regra nova (o Preto e branco de hoje nem olha a
   zona de letra). Copiei do ScanTailor (zona "subtrair da camada automática"); a letra achada pela
   máquina não fura a gravura.

## 6. Opção: usar as linhas de texto dos OCRs no Misto

**A ideia** (Internet Archive, `archive-pdf-tools/internetarchivepdf/mrc.py`): o preto e branco só
dentro das linhas de texto que o OCR achou; mancha fora das linhas nunca vira tinta.

**O que já existe:** as pontes do docTR e do Kraken e o voto por linha (`core/ocr_comparar.comparar`
devolve a máscara das linhas confirmadas pelos dois). Nada disso está ligado ao pipeline nem à tela.

**O que foi medido** (`relatorios/fase2-misto-2026-10-05/ocr/`, script `scripts/medir_ocr.py`): na
página preparada pelo programa, a 300 DPI, "tinta" = os pontos pretos do Preto e branco de hoje. A
coluna que importa é a tinta **fora das linhas e fora da gravura**: num Misto só pelas linhas, ela
ficaria **sem tratamento**. Linhas = união docTR + Kraken, com folga de 0,35 altura de linha (o voto dá
quase o mesmo).

| Página | Tinta dentro da gravura | Tinta fora das linhas e fora da gravura | O que é (olhando a imagem) |
|---|---|---|---|
| Palatino 5 | 76% | 0,2% | pontinhos |
| Palatino 9 | 0% (o detector não marca nada) | **46%** | a moldura e a capitular "Q" inteiras |
| Escola 7 | 75% | 1,3% | o fio do alto da página e pontinhos |
| Horas 11 | 99,5% | 0,5% | beirada |
| Horas 13 | 49% | **4,8%** | pedaços da moldura fora da zona, beiradas |
| Horas 47 | 93% | 0,1% | — |
| Opus Majus 20 | 89% | **9,8%** | o vão escuro da porta atrás da estátua (o detector marca como letra) |
| Graduale 221 | 0% | **62%** | a pauta, todas as notas, as claves, as capitulares desenhadas e a faixa da lombada |
| Graduale 222 | 0% | **69%** | a pauta, todas as notas, as claves |
| Opus Majus 165 | 0% | **5,6%** | os traços das figuras 7 e 8 e várias letrinhas delas (c, d, a, b da fig. 8) |

Em vermelho nas imagens `ocr/<página>.jpg`; a capitular, as notas e as letrinhas do Opus 165 são
exatamente o que o Samuel exige que não fique sem tratamento. **Conclusão:** no texto corrido os OCRs
pegam quase tudo (Escola 7, Palatino 5: abaixo de 1,5%), mas o Misto "só nas linhas" sozinho perderia
partitura, capitular e diagrama. Se entrar, tem de ser como **segunda opinião** (por exemplo: dentro das
linhas, o preto e branco de sempre; fora das linhas e fora da gravura, um preto e branco mais exigente
que só tira o que é claramente mancha), e isso é assunto do pesquisador.

**Custo de tempo por página** (medido aqui, com outros agentes rodando ao mesmo tempo, então só ordem
de grandeza): docTR 1 a 2,5 s (a primeira página, 24 s, inclui abrir o modelo); Kraken **13 a 160 s**
nesta rodada (na medida do 1.3, com a máquina mais livre, ~9–10 s; estimado 15–25 s no notebook do
Kaique). Num livro de 300 páginas, o Kraken sozinho somaria 45 min a mais de 2 h.

**O que tiraria do 1.5 adiado:** ligar o OCR ao filtro é o núcleo do 1.4 ("tinta só dentro das linhas,
com a cor original") e parte do 1.5 ("juntar os dois detectores", a caixinha "Só as letras", o título
da Horas 26). Fazer agora anteciparia esses dois itens, que o Samuel adiou em 01/10.

**Ressalva da medida:** a "tinta" é a do Preto e branco de hoje, que inclui mancha; separar mancha de
letra é justamente o que não se sabe fazer sozinho. As porcentagens dizem quanto **preto** cai fora
das linhas; as imagens dizem o que ele é. A Horas 13 foi medida duas vezes: na primeira, a detecção de
gravura falhou por falta de memória (a máquina tem 15 GB e estava com 3 livres) e a página saiu sem
gravura; a segunda é a da tabela.
