# Rodada 4: respostas aos comentários da rodada 3 e a regra ajustada

07/10/2026 · agente das decisões do "Para revisar". Nada do programa foi mudado (`core\`, `ui\`, `modelos.py`
intactos). Tudo rodou com o ramo `fase-1` de hoje: com o conserto do desenho claro (04b225d), o limpar
pontinhos e o dividir do ScanTailor (fa35e86) e o limpar pontinhos desligado de fábrica (1de8e47).

## O que o Samuel pediu (rodada 3, `../rodada-3/respostas-samuel.md`)

- Para cada erro que manda uma página para "Para revisar": o jeito mais rápido e o manual, com opções.
- Um **delineado** em volta das áreas achadas como gravura, para decidir apagar ou não; testes com vários livros.
- Se o programa ou o ScanTailor já acham a borda preta sobrando para cortar, com o Kaique aceitando.
- Um jeito de apagar todos os avisos de uma vez.
- "Por que o jeito de fábrica apagou?" (Antiphonal 6).
- Página só com mancha ou em branco: virar página branca; aviso de folhas de rosto e guardas.
- Os "Não concordo": Camões 27, 66, 104; Egenloff 3, 12, 47; Rariora 169.

Regra nova de 07/10: as respostas a comentários começam com "RESPOSTA AO SEU COMENTÁRIO:" e trazem o campo
`historico` (o comentário literal da rodada 3, para a página fixar no alto; o `em` ficou vazio, porque o
`respostas-samuel.md` só tem o intervalo das respostas).

## As perguntas (`rodada-4-perguntas.json`, 21)

| # | id | O que é |
|---|---|---|
| 1 | rv4-resumo | A regra ajustada e as contas nas 89 páginas |
| 2 | rv4-conserto-desenho | Onde fica o "jeito rápido": botão no aviso, o programa faz sozinho, ou só o aviso |
| 3–8 | rv4-erro-1 … rv4-erro-6 | Um cartão por tipo de erro (desenho apagado, gravura errada, faixa, texto falhado, página sem conteúdo, "Só o texto achado"), com o rápido e o manual |
| 9 | rv4-conserto-gravura | O delineado (como ficaria, em 8 livros) e o teste nas 89 páginas |
| 10 | rv4-conserto-faixa | O que o nosso corte e o do ScanTailor fazem hoje com a borda preta; como cortar |
| 11 | rv4-aviso-so-texto | Apagar todos os avisos de uma vez (desenho da proposta) |
| 12 | rv4-pag-antiphonal1547-006 | Por que o jeito de fábrica apagou as pautas vermelhas |
| 13 | rv4-pag-rariora-008 | Folhas sem conteúdo (rosto, guardas): como avisar |
| 14 | rv4-pag-egenloff-012 | Agora vai, pelo motivo "página sem conteúdo" |
| 15 | rv4-em-branco | Pergunta nova: o aviso "Parece em branco. Quer apagar?" erra (Gladstone 18 tem título) e apagar estraga a encadernação |
| 16–21 | rv4-pag-camoes-027, -066, -104, egenloff-003, -047, rariora-169 | Os "Não concordo", cada um com o que deu errado e o que a regra ajustada faz |

Campos que a página não mostra: `hoje`, `regra4`, `gabarito`, `motivos4` (para a análise).

## A regra ajustada (`scripts/regra4.py`)

A página vai para "Para revisar" (no "Só as letras", jeito de fábrica) quando:

1. **Desenho apagado** (ajustado): medido agora no resultado de verdade (antes a conta refazia a regra antiga e
   não via o conserto). Tinta apagada fora do texto e das gravuras ≥ 2,5% de toda a tinta, ou amontoada ≥ 2%
   (como antes), **ou** um pedaço apagado cheio, colado no texto, com tinta de 1,5 altura de linha ao quadrado
   ou mais (a letra T vermelha do Antiphonal 46 some inteira e é pouca tinta perto da página). Não conta o que
   fica só na faixa da beirada (tarja da biblioteca, fundo do scanner).
2. **Figura além da gravura achada** (igual).
3. **Faixa escura na beirada** (igual; em 70% ou mais das páginas do livro, vira um aviso só, no livro).
4. **NOVO: texto falhado nos dois jeitos**: 2 ou mais linhas compridas (15% da largura ou mais, longe do pé e
   do alto) em que o preto e branco guarda entre 20% e 62% da tinta clara da letra, ou todas as linhas da
   página. Abaixo de 20% a linha sumiu inteira: no acervo, é carimbo e anotação a lápis (o que se quer tirar).
5. **NOVO: página sem conteúdo**: quase nenhuma tinta forte no miolo (< 0,5%), no máximo 1 linha forte e
   (3 ou mais linhas fracas, ou nenhuma linha forte).

### As contas (89 páginas = 59 do estudo + 30 da rodada 3, todas rodadas com o fase-1 de hoje)

| | Vão | Acertam | Nas 59 | Nas 30 |
|---|---|---|---|---|
| Hoje (aviso do programa) | 55 | 52 | 29 | 23 |
| Regra da rodada 3 | 15 | 72 | 53 | 19 |
| **Regra ajustada** | **21** | **78** | **53** | **25** |

"Acertam" = contra o gabarito: as respostas do Samuel na rodada 3 (Concordo = o que a regra dizia; Não concordo
= o contrário; Camões 104 e Rariora 8 vão, pelos comentários; Rariora 169 não vai, porque o conserto a
consertou); as da rodada 1 (Palatino 76, 67, 66 e Siebmacher 7 esquerda agora "não vão": o conserto trouxe o
desenho de volta; o Siebmacher conferi no olho, os do Palatino pelo relatório do verificador do conserto); nas outras, o veredito do estudo ("errada" vai; "ok" e "leve" não vão).

- **Escapam 5:** Antiphonal 6 e 31 (pautas vermelhas com falhas pequenas; com o conserto sobra pouco),
  Camões 9 (a letra A enfeitada sai lavada nos dois jeitos; nenhuma conta pega), Camões 66 e Egenloff 47
  ("Não concordo" sem comentário: o motivo é perguntado).
- **Vão sem precisar 6:** Antiphon 88 (beirada), Graduale 269 e ljs47 26 (figura passa um pouco da gravura),
  Matemática 72, Siebmacher 7 e 9 direita (leves).
- Pela regra ajustada, a faixa vira aviso do livro no Egenloff e na Matemática.

## Achados que não são da regra (para a gerente)

- **O fase-1 de hoje não divide mais a folha dupla do Siebmacher 7 e 9** (o dividir do ScanTailor de fábrica
  deixa uma página só). Para comparar com as respostas, dividi à mão nos scripts (`comum._dividir`, a lombada
  achada pelo detector de sempre). Vale conferir se é o esperado.
- **O aviso "Parece em branco" erra**: aparece só na Gladstone 18, que tem o título "DA ORAÇÃO", e oferece
  apagar a página; não aparece no Egenloff 12 nem na Rariora 8. Virou a pergunta `rv4-em-branco`.
- **A borda preta**: o nosso corte de fábrica e a caixa da página do ScanTailor (rodada no programa de teste do
  pesquisador, `EditorImpressao-arquivos\ferramentas\pesquisa-fase2-2026-10-01\build\Release\prova.exe`, com o
  Qt da pasta `ferramentas\qt`) não tiram a moldura do Egenloff nem as linhas da beirada do Camões; o do
  ScanTailor tira a faixa de baixo da Matemática 32, que o nosso deixa.
- **Força do preto**: 85 em vez de 50 fecha as letras do Camões 27 e 104; não resolve o vermelho do Egenloff 3.
- **Delineado** (`scripts/zonas_teste.py`): gravura achada em 29 das 89 páginas (39 áreas); a conta de
  "suspeita" marca 6 páginas, 4 certas (Marial 454, Camões 104, Matemática 72, Rariora 8) e 2 erradas (a
  moldura dourada da Horas 16 e 27).

## Ressalvas

- As contas novas (4 e 5, e o "pedaço cheio" do 1) foram acertadas em poucas páginas; falta um livro novo.
- No Egenloff 3, das duas linhas falhadas que a regra conta, uma é a vermelha do pé e a outra é o carimbo
  da biblioteca no alto.
- O gabarito das páginas que o Samuel não viu é o meu olho do estudo, feito antes do conserto. Olhei de novo,
  com o programa de hoje: Siebmacher 7, Rariora 169, Camões 9, 11, 27, 66 e 104, Antiphonal 6, 31 e 46,
  Egenloff 3 e 47, Cursus 3 e Matemática 72; as outras, não.
- O teste da força do preto rodou no JPEG de 4000 px da página (qualidade 94), não no PDF.
- **Queda das 18:36 e modelos vazios (19:20–22:00):** os dados das 84 páginas rodadas antes das 18:36 foram
  usados (todos de antes das 19:20). O que rodou depois foi refeito com os modelos de volta: Egenloff 3 e 7
  (as do processo que ficou órfão na queda foram descartadas; as das 21h, sem o leitor de texto, apagadas),
  Horas 11 (tinha falhado por falta de memória) e o Siebmacher 7 e 9 (dividido à mão).

## Pastas

- Dados pesados: `D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho` (`dados4` = rodada 4;
  `dados` = cópia das rodadas 1 a 3; `faixa`, `forca`; `sinais-rodada4.json`, `regra4.json`,
  `zonas-teste.json`). A pasta antiga `%TEMP%\revisar_decisoes_rodada1` (no C:) ficou como estava (não apago
  fora do projeto sem o Samuel).
- A pasta de dados do programa é isolada por `pasta_de_dados_dos_scripts.isolar_pasta_de_dados` (em
  `revisar-decisoes-trabalho\dados_do_programa`, apagada no fim de cada rodada; nenhum `erros.log` sobrou).
  O `erros.log` de verdade não foi tocado por estes scripts (as entradas de 18:32 são de outro agente, da
  cópia `verif-recomeco`).
- Imagens em `img\` (fora do git, como nas rodadas anteriores).

## Para refazer

De dentro de `scripts\`, com o Python do projeto, **um `rodar.py` de cada vez** (conferir antes se há 3 GB livres):

1. `rodar.py` (as 89; ou `rodar.py <página>`)
2. `sinais4.py`
3. `regra4.py`
4. `faixa_testes.py`, `forca_teste.py`, `zonas_teste.py`
5. `figuras4.py`
6. `perguntas4.py`

`criterio.py`, `medir.py` e `sinais.py` são cópias da rodada 3 (usadas pelas contas); `paginas_rodada3.py` e
`veredito_estudo.py` trazem as páginas e os vereditos das rodadas anteriores; `desenho.py` monta as imagens.
