# Misto: o desenho claro não some mais

**06/10/2026 · conserto pedido pela gerente, a partir do estudo "Para revisar" · feito pelo
implementador, ramo `misto-desenho-apagado`.** PRONTO PARA CONFERIR (teste de **olho**: só você decide).

## Em poucas palavras

1. **O defeito:** no "Só as letras", jeito de fábrica "Guardar a tinta forte", o programa apagava a
   parte clara de um desenho que o detector de gravura não reconheceu. A capitular S do Palatino 76
   sumia quase inteira; o fundo da capitular M do Palatino 67 e a letra "M" do rodapé do Palatino 66
   ficavam pela metade; o diagrama vermelho do ljs47 p. 103 saía picotado.
2. **Por que acontecia:** fora das linhas de texto, o programa só guardava cada pedacinho de tinta que,
   **sozinho**, fosse tão escuro quanto as letras e não muito pequeno. Uma gravura de traço claro é feita
   de milhares de tracinhos claros e miúdos: cada um, sozinho, ia para o branco, e o desenho sumia.
3. **O conserto:** agora o programa olha o **conjunto**. Quando os tracinhos claros estão **amontoados
   junto de tinta forte** (a moldura da capitular, o traço escuro do desenho) e formam uma parte de
   verdade desse desenho, eles ficam, como no Preto e branco puro. A tinta clara **solta** (a escrita do
   verso na margem, sujeira longe de tudo) continua indo para o branco.
4. **Resultado nas 59 páginas do estudo:** 13 melhoraram, 2 ficaram iguais à vista,
   2 pioraram de leve (voltaram linhas finas da beirada da folha), e **42 saíram
   idênticas, ponto a ponto**, à de hoje. Nenhuma página ganhou mancha do verso nem fundo cinza.
5. **Tempo:** a conta nova custa no máximo 0,18 s por página (mediana 0,016 s), nas
   59 páginas. O Misto inteiro, medido antes e depois alternados no mesmo programa, somou 91,7 s
   antes e 92,8 s depois (+1,2%).
6. **"Para revisar" não muda:** o aviso continua medindo só a tinta forte; nas 59 páginas, o número que
   decide o aviso saiu igual antes e depois.

## 1. O que mudou no programa

Só `core/misto.py` (e um arquivo de testes novo). Nenhuma tela, nenhum botão, nada no projeto salvo. Só o
jeito de fábrica **"Guardar a tinta forte"** muda; "Tudo em preto e branco", "Só o texto achado" e o Preto
e branco sem "Só as letras" ficam exatamente como estavam.

A regra nova, em português comum: um amontoado de tinta fora do texto é **desenho comido** (e volta
inteiro, como no Preto e branco puro) quando

- tem tinta forte (a moldura, um traço escuro): é ela que diz "aqui tem um desenho";
- é grande (mais que uns três décimos de uma linha de texto ao quadrado): um pontinho ao lado do número
  da página não conta;
- o programa estava apagando **uma fatia de verdade** dele (pelo menos 4%): na pauta de música do
  Graduale, o que se apagava colado nas linhas era a mancha do verso, menos de 2,5% da pauta, e isso
  continua indo para o branco;
- não é uma faixa fina encostada na borda da imagem (a sombra da lombada, a beirada da folha);
- a página tem tons de cinza (num scan que já veio em preto e branco, como o Cursus p. 3, o escuro não
  separa desenho de sujeira: ali nada muda).

### O que foi tentado e não ficou (para ninguém repetir)

| Tentativa | O que deu |
|---|---|
| Só "colado na tinta forte e com bastante tinta apagada" (1 linha² de tinta apagada) | Consertava o Palatino 76 e 67, mas a letra "M" do Palatino 66 continuava pela metade. |
| Só "colado na tinta forte e grande" (sem a fatia mínima) | Consertava as quatro, mas trazia de volta a mancha do verso colada na pauta do Graduale 222 e 223 e a sujeira granulada do Cursus p. 3. |
| Separar pelo escuro de cada pedaço (comparado com o preto das letras) | No Graduale, metade da mancha do verso continuava voltando; no ljs47, parte do diagrama deixava de voltar. Não usado. |
| Separar pela forma (traço fino e comprido contra grão redondo) | Os números dos desenhos e da mancha se cruzam. Não usado. |
| Faixa na borda medida pela caixa (mais fina que uma linha) | A sombra inclinada do alto da Horas 27 escapava. Ficou a espessura média (tinta dividida pelo comprimento). |

## 2. Como foi medido

- As **59 páginas do estudo** (34 do gabarito do Misto e 25 do acervo, as mesmas do relatório de
  06/10), cada uma pelo caminho do programa: a página preparada, a marcação de gravura, o leitor de texto
  rápido, o Misto de fábrica de hoje e o Preto e branco puro. Depois, o Misto consertado com **as mesmas
  entradas** (mesmas linhas de texto, mesma marcação). Conferido: o Misto de hoje refeito por esse atalho
  sai ponto a ponto igual ao do programa nas 59.
- **Olhei todas as páginas que mudaram**, inteiras e de perto, com os cinco quadros. As 37 que não
  mudaram foram conferidas pela soma da diferença das imagens (zero).
- Veredito: **melhorou** (voltou desenho que o Preto e branco puro guarda), **igual** (mudança de poucos
  pontos, que não se vê), **piorou** (voltou mancha do verso, sujeira ou fundo cinza que o Misto de hoje
  tirava).
- Testes de máquina, arquivo por arquivo (números no fim).


## 3. As páginas que mudaram, uma por uma

Cada imagem tem cinco quadros lado a lado: **Original · Misto de hoje · Misto consertado · Preto e branco puro · Onde mudou**. O quinto quadro é uma cópia clara do original com o que mudou pintado de azul; nada foi desenhado por cima dos quatro primeiros.

### Palatino p. 76 - melhorou

A capitular S gravada voltou inteira, como no Preto e branco puro. **Olhe a letra S no alto à esquerda: no Misto de hoje só sobravam a moldura e um arco; no consertado, a letra e a paisagem atrás dela estão de volta.**

![Palatino p. 76](imagens/palatino_p076__inteira.jpg)

### Palatino p. 67 - melhorou

O fundo desenhado da capitular M voltou. **Olhe dentro do quadrado da letra M: as folhas e figuras do fundo, que tinham sumido, voltaram.**

![Palatino p. 67](imagens/palatino_p067__inteira.jpg)

### Palatino p. 66 - melhorou

A letra ornamental M do rodapé voltou inteira; a moldura ganhou o pontilhado do Preto e branco. **Olhe o "M." à esquerda no rodapé: no Misto de hoje estava pela metade; no consertado está inteiro, como no Preto e branco puro.**

![Palatino p. 66](imagens/palatino_p066__inteira.jpg)

### ljs47 p. 103 - melhorou (em parte)

Os arcos do diagrama vermelho voltaram mais inteiros; as linhas horizontais continuam picotadas. **Olhe os arcos à direita do diagrama: mais inteiros. As linhas horizontais compridas continuam com falhas (no Preto e branco puro elas saem quase inteiras).**

![ljs47 p. 103](imagens/ljs47_p103__inteira.jpg)

### Boécio p. 3 - melhorou

A hachura do carimbo da biblioteca voltou. **Olhe o escudo dentro do carimbo redondo (à direita): os tracinhos do escudo voltaram.**

![Boécio p. 3](imagens/boecio_p003__inteira.jpg)

### Opus majus p. 3 - melhorou

A hachura do fundo do selo da editora voltou. **Olhe o fundo riscado atrás do retrato no selo: voltou como no Preto e branco puro.**

![Opus majus p. 3](imagens/opusmajus_p003__inteira.jpg)

### Palatino p. 9 - melhorou

A gravura dentro da capitular Q ganhou os traços claros. **Olhe o cavaleiro dentro da letra Q: mais traços do desenho, como no Preto e branco puro.**

![Palatino p. 9](imagens/palatino_p009__inteira.jpg)

### Palatino p. 113 - melhorou

O contorno claro do pergaminho enrolado do título voltou. **Olhe o rolo de pergaminho no alto: o contorno e as dobras que faltavam voltaram.**

![Palatino p. 113](imagens/palatino_p113__inteira.jpg)

### Rhetorica p. 129 - melhorou

O pontilhado do fundo da gravura de página inteira voltou. **Olhe o fundo atrás da ave: o pontilhado do original voltou.**

![Rhetorica p. 129](imagens/rhetorica_p129__inteira.jpg)

### Siebmacher p. 7 (esquerda) - melhorou

A faixa de ornamentos ficou mais cheia, como no Preto e branco puro. **Olhe a faixa de ornamentos: pedaços claros dos arabescos voltaram.**

![Siebmacher p. 7 (esquerda)](imagens/siebmacher_p007__esquerda.jpg)

### Siebmacher p. 9 (esquerda) - melhorou

A coluna de ornamentos ficou mais cheia. **Olhe o meio da coluna de ornamentos: pedaços dos arabescos voltaram.**

![Siebmacher p. 9 (esquerda)](imagens/siebmacher_p009__esquerda.jpg)

### Antiphon p. 88 - melhorou (pouco)

Uma linha da pauta que estava apagada voltou. **Olhe a linha de cima da quarta pauta (e o começo da quinta): estava faltando no Misto de hoje.**

![Antiphon p. 88](imagens/antiphon_p088__inteira.jpg)

### Rhetorica p. 73 - melhorou (pouco)

O fio vertical da moldura ficou sem a falha. **Olhe o fio vertical à direita do texto: a falha no meio dele fechou.**

![Rhetorica p. 73](imagens/rhetorica_p073__inteira.jpg)

### Palatino p. 104 - igual

Poucos pontos no fio da tabela; não se nota. **Olhe o fio vertical da tabela: diferença de poucos pontos.**

![Palatino p. 104](imagens/palatino_p104__inteira.jpg)

### Rhetorica p. 160 - igual

O fio de baixo ficou um pouco mais cheio; não se nota. **Olhe o fio de baixo: diferença de poucos pontos.**

![Rhetorica p. 160](imagens/rhetorica_p160__inteira.jpg)

### ljs47 p. 26 - piorou (leve)

Voltaram pedaços da sombra da dobra perto da beirada direita. **Olhe a faixa vertical perto da beirada direita: pedaços da sombra da dobra voltaram, como no Preto e branco puro.**

![ljs47 p. 26](imagens/ljs47_p026__inteira.jpg)

### Siebmacher p. 9 (direita) - piorou (leve)

Voltaram linhas finas da beirada da folha, ao lado da faixa preta que já existia. **Olhe a beirada direita e a de baixo: linhas finas da borda da folha voltaram ao lado da faixa preta (que já existia no Misto de hoje).**

![Siebmacher p. 9 (direita)](imagens/siebmacher_p009__direita.jpg)


## 4. A tabela das 59 páginas

"Idêntica" = a imagem do Misto consertado é ponto a ponto igual à de hoje (soma da diferença = 0). "Pontos que voltaram" = pontos de tinta que o Misto de hoje mandava para o branco e o consertado guarda (entre parênteses, em relação a toda a tinta da página). Tempo = o Misto inteiro da página, mediana de 3 voltas alternadas antes/depois no mesmo programa. A máquina estava sendo usada por outro agente: diferenças de até 1 s, para mais ou para menos, são ruído (a conta nova sozinha custa no máximo 0,18 s; item 5 do topo).

| Página | Resultado | Pontos que voltaram | Tempo antes (s) | Tempo depois (s) |
|---|---|---|---|---|
| Antiphon p. 88 | melhorou (pouco) | 48735 (0,78%) | 7,04 | 7,92 |
| Antiphon p. 260 | idêntica | - | 12,21 | 12,83 |
| Boécio p. 3 | melhorou | 8805 (3,93%) | 0,16 | 0,14 |
| Boécio p. 7 | idêntica | - | 0,14 | 0,14 |
| Boécio p. 8 | idêntica | - | 0,14 | 0,15 |
| Boécio p. 22 | idêntica | - | 0,14 | 0,16 |
| Cursus p. 3 | idêntica | - | 0,93 | 0,93 |
| Cursus p. 314 | idêntica | - | 1,00 | 0,95 |
| Escola p. 7 | idêntica | - | 1,16 | 1,18 |
| Escola p. 35 | idêntica | - | 0,94 | 0,97 |
| Escola p. 113 | idêntica | - | 1,01 | 0,92 |
| Escola p. 197 | idêntica | - | 0,50 | 0,59 |
| Graduale p. 221 | idêntica | - | 2,15 | 2,01 |
| Graduale p. 222 | idêntica | - | 1,58 | 1,72 |
| Graduale p. 223 | idêntica | - | 1,93 | 1,95 |
| Graduale p. 269 | idêntica | - | 6,79 | 5,80 |
| Graduale p. 588 | idêntica | - | 1,96 | 1,77 |
| Horas p. 11 | idêntica | - | 5,54 | 5,30 |
| Horas p. 13 | idêntica | - | 3,03 | 3,10 |
| Horas p. 14 | idêntica | - | 2,77 | 3,01 |
| Horas p. 16 | idêntica | - | 3,50 | 3,54 |
| Horas p. 26 | idêntica | - | 3,24 | 3,19 |
| Horas p. 27 | idêntica | - | 2,94 | 3,35 |
| Horas p. 47 | idêntica | - | 3,01 | 2,99 |
| Horas p. 175 | idêntica | - | 3,36 | 3,43 |
| ljs47 p. 26 | piorou (leve) | 2708 (0,08%) | 3,02 | 2,52 |
| ljs47 p. 49 | idêntica | - | 3,34 | 3,37 |
| ljs47 p. 64 | idêntica | - | 3,89 | 4,20 |
| ljs47 p. 103 | melhorou (em parte) | 25387 (0,89%) | 1,50 | 1,57 |
| Marial p. 7 | idêntica | - | 1,54 | 1,49 |
| Marial p. 454 | idêntica | - | 2,45 | 2,65 |
| Marial p. 840 | idêntica | - | 1,33 | 1,43 |
| Matemática p. 32 | idêntica | - | 0,88 | 0,82 |
| Matemática p. 72 | idêntica | - | 1,36 | 1,33 |
| Opus majus p. 3 | melhorou | 1881 (1,82%) | 0,29 | 0,28 |
| Opus majus p. 11 | idêntica | - | 0,16 | 0,16 |
| Opus majus p. 20 | idêntica | - | 0,30 | 0,30 |
| Opus majus p. 165 | idêntica | - | 0,19 | 0,18 |
| Opus majus p. 256 | idêntica | - | 0,26 | 0,24 |
| Palatino p. 5 | idêntica | - | 0,34 | 0,34 |
| Palatino p. 7 | idêntica | - | 0,12 | 0,12 |
| Palatino p. 9 | melhorou | 3996 (0,82%) | 0,14 | 0,16 |
| Palatino p. 10 | idêntica | - | 0,17 | 0,19 |
| Palatino p. 57 | idêntica | - | 0,13 | 0,15 |
| Palatino p. 66 | melhorou | 17540 (5,27%) | 0,17 | 0,17 |
| Palatino p. 67 | melhorou | 23103 (8,65%) | 0,17 | 0,19 |
| Palatino p. 76 | melhorou | 22781 (7,85%) | 0,17 | 0,17 |
| Palatino p. 104 | igual | 152 (0,04%) | 0,17 | 0,16 |
| Palatino p. 113 | melhorou | 2151 (1,00%) | 0,12 | 0,13 |
| Pesel p. 21 | idêntica | - | 0,74 | 0,76 |
| Rhetorica p. 18 | idêntica | - | 0,22 | 0,22 |
| Rhetorica p. 34 | idêntica | - | 0,43 | 0,49 |
| Rhetorica p. 73 | melhorou (pouco) | 217 (0,05%) | 0,18 | 0,20 |
| Rhetorica p. 129 | melhorou | 50277 (6,27%) | 0,21 | 0,25 |
| Rhetorica p. 160 | igual | 690 (0,13%) | 0,23 | 0,23 |
| Siebmacher p. 7 (direita) | idêntica | - | 0,07 | 0,07 |
| Siebmacher p. 7 (esquerda) | melhorou | 4937 (2,65%) | 0,09 | 0,08 |
| Siebmacher p. 9 (direita) | piorou (leve) | 3571 (4,37%) | 0,06 | 0,09 |
| Siebmacher p. 9 (esquerda) | melhorou | 4503 (2,61%) | 0,10 | 0,10 |


## 5. Testes de máquina

Rodados arquivo por arquivo (a máquina tem pouca memória livre):

| Arquivo | Resultado |
|---|---|
| `tests/test_misto.py` | 31 passaram |
| `tests/test_misto_desenho_claro.py` (novo) | 10 passaram |
| `tests/test_misto_consertos.py` | 25 passaram |
| `tests/test_misto_na_tela.py` | 14 passaram |
| `tests/test_misto_no_programa.py` | 23 passaram |
| `tests/test_misto_no_projeto.py` | 12 passaram |
| `tests/test_alerta_pb.py` | 5 passaram |
| `tests/test_preto_e_branco_regra_30_09.py` | 15 passaram |
| `tests/test_so_neste_pedaco_no_preto_e_branco.py` | 8 passaram |
| `tests/test_decoracao_no_preto_e_branco.py` | 12 passaram |

Total: 155 passaram, nenhum falhou. Não rodei a pasta `tests/` inteira de uma vez (pouca memória).

O arquivo novo, `tests/test_misto_desenho_claro.py` (10 testes), desenha páginas de propósito: a
capitular com hachura clara (tem de ficar), a escrita clara do verso na margem (tem de ir para o branco),
o texto das linhas (não pode mudar), o aviso "Para revisar" (continua olhando só a tinta forte), o "Só o
texto achado" (continua apagando), o pontinho ao lado do número da página, a mancha colada numa pauta
grande, a sombra da lombada na borda e o scan sem tons de cinza (nada volta). Conferido: tirando do
programa cada uma das regras novas, o teste daquela regra falha.

## 6. Minha opinião

Vale a pena. As quatro páginas do defeito (Palatino 76, 67 e 66, ljs47 p. 103) melhoraram, as três do
Palatino ficaram iguais ao Preto e branco puro no desenho, e o que o Misto existe para tirar (a mancha do
verso, o fundo cinza) não voltou em nenhuma das 59. As duas pioras são leves e do mesmo tipo: linhas finas
da beirada da folha ao lado de uma faixa preta que já existia (é assunto do corte, como o estudo de 06/10
já dizia).

## 7. Ressalvas

- **Os números da regra (4% da fatia, 0,3 linha², 1/4 de linha na borda) foram acertados nestas mesmas
  59 páginas.** Pode ter "decorado" estes livros. O certo é olhar num livro que não entrou aqui antes de
  confiar de olhos fechados.
- **O ljs47 p. 103 melhorou só em parte.** As linhas horizontais compridas do diagrama, de traço vermelho
  muito claro, continuam picotadas: os pedaços delas não encostam em tinta forte, e a regra só age onde há
  tinta forte. No Preto e branco puro elas saem quase inteiras. Consertar isso pediria outra regra
  (reconhecer linha comprida e clara), que traria o risco de trazer a sombra da dobra junto.
- **Na mesma página (ljs47 p. 103), o começo de várias linhas da coluna da esquerda sai apagado** (a
  tinta ali está desbotada no original). Acontece igual no Preto e branco puro, no Misto de hoje e no
  consertado: é do preto e branco, não do Misto, e não mudou com este conserto. Vai como sugestão para a
  Lista de bugs.
- **Página com desenho colado a uma faixa preta grande** (a beirada do Palatino 76, a moldura do Palatino
  66 e 67): a moldura ganha o mesmo pontilhado que tem no Preto e branco puro. Achei que ficou igual ou
  melhor, mas é gosto.
- **Scan que já veio em preto e branco** (Cursus): o conserto não age. Se um livro assim tiver capitular
  de traço miúdo, ela continua saindo como hoje.
- O veredito é o meu olho, nas imagens reduzidas e nos recortes ampliados. Defeito muito pequeno pode ter
  escapado.
- As imagens grandes ficaram fora do git (`trabalho/`, refazem-se pelos scripts em `scripts/`:
  `rodar_base.py`, `rodar_misto.py`, `comparar.py`, `tempo.py`, `gerar_relatorio.py`).
