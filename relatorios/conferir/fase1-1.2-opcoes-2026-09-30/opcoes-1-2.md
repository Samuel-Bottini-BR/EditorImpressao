# Item 1.2: as opções de "Gravuras e fotos", página por página

Rodada de 30/09/2026, feita pelo implementador. **Não é o parecer do verificador.** É teste de **olho**: quem decide é o Samuel.

**Aviso da Fase 1:** moldura e iluminura continuam defeito conhecido até o fim da Fase 1 (itens 1.4 e 1.5). No Preto e branco, a moldura sair em desenho preto e branco é a **regra nova do filtro**, feita por outro implementador em `core/filtros.py`. Esta rodada só olha **onde o programa acha a gravura**.

## Em uma frase

Nenhuma combinação de opções é melhor que a de fábrica nas 9 páginas juntas. O Graduale 222 e a moldura da Horas 13 foram consertados no detector e ficam bons com a opção de fábrica. A foto do Opus Majus 20 fica boa com "Esta página tem foto" (ou "Este livro tem fotos"). O título da Horas 26 nenhuma opção resolve: fica para o item 1.5.

## Como olhar

Uma folha por página e por filtro, em `folhas\`:

- `folhas\<página>-magico_pro.jpg`: o original e o resultado de cada combinação, no Mágico pro;
- `folhas\<página>-preto_e_branco.jpg`: a mesma coisa, no Preto e branco;
- `folhas\<página>-gravura.jpg`: onde o programa achou a gravura em cada combinação, pintado de vermelho.

Cada quadro diz a combinação e **quanto da página virou gravura**. Os resultados em tamanho cheio estão em `resultado\`.

## As combinações (10 por página, em vez de 24)

| | Na tela "O que fazer" |
|---|---|
| Antes | o detector antigo (só como referência) |
| **A** | **Achar gravuras, seguindo o desenho** (de fábrica): sem imagens claras, com a luz igualada |
| B | A + "Procurar também imagens claras" |
| C | A sem "Igualar a luz da página antes" |
| D | A + imagens claras, sem igualar a luz |
| E | "Este livro tem fotos", sensibilidade 100 |
| F | "Este livro tem fotos", sensibilidade 70 |
| G | "Este livro tem fotos", sensibilidade 40 |
| H | E + imagens claras |
| I | E sem igualar a luz |

Por que não as 24: a sensibilidade só vale com "Este livro tem fotos", porque o ScanTailor só a usa no retângulo. As 3 sensibilidades no contorno livre dariam o mesmo resultado 3 vezes. "Imagens claras" e "igualar a luz" entram sozinhas e juntas no contorno livre (a forma de fábrica), e sozinhas no retângulo a 100.

## Quanto da página virou gravura (Mágico pro)

| Página | Antes | **A** | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|---|---|
| Graduale 222 | 0% | **0%** | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| Horas 13 | 4% | **6%** | 9% | 5% | 36% | 35% | 34% | 15% | 56% | 35% |
| Horas 26 | 1% | **24%** | 24% | 24% | 22% | 49% | 21% | 21% | 49% | 49% |
| Opus Majus 20 | 88% | **74%** | 91% | 75% | 91% | 92% | 91% | 91% | 92% | 92% |
| Horas 11 | 0% | **81%** | 87% | 81% | 87% | 90% | 80% | 81% | 100% | 90% |
| Horas 27 | 1% | **7%** | 27% | 7% | 33% | 16% | 15% | 15% | 48% | 17% |
| Palatino 9 | 11% | **0%** | 24% | 0% | 37% | 0% | 0% | 0% | 34% | 0% |
| Palatino 67 | 2% | **0%** | 1% | 0% | 47% | 0% | 0% | 0% | 48% | 0% |
| Marial 153 | 0% | **0%** | 13% | 9% | 13% | 13% | 0% | 0% | 13% | 13% |

## Página por página

**Graduale 222 (pauta virando gravura): resolvido no detector, em todas as combinações.** A pauta não é mais gravura (antes do conserto: 14% na forma de fábrica e 100% com fotos). A caixa que o modelo de layout desenha em volta da partitura é julgada escrita, e ali a escrita ganha da gravura. A faixa escura da beirada direita também sai. Mágico pro e Preto e branco voltam a sair como o detector antigo. Melhor: **A** (todas iguais).

**Horas 13 (moldura): resolvido do lado do detector na A.** Antes, só a beirada de dentro da faixa dourada era gravura. Agora a faixa inteira é: o dourado coberto passou de 37% para 88%. Continua o triângulo pequeno sobre "pag. 54". Com fotos (E a I), a gravura pega o papel em volta da moldura (15% a 56% da página). B pega também um pedaço da beirada do alto. Melhor: **A**. Como a moldura sai no Preto e branco é a regra nova do filtro (outro implementador). Visto nas folhas: o título vermelho "TABLE" e "CONTENU EN CE LIVRE" some no Preto e branco em **todas** as combinações, até na do detector antigo. Isso é do filtro, não do detector.

**Horas 26 (título "NOVEMBRE." dentro da gravura): nenhuma opção resolve.** A, B, C, D, F e G põem o título junto com a moldura. E, H e I põem ainda o papel em volta. **Fica para o item 1.5**, decisão do Samuel. O motivo: o título está colado na moldura, e o detector de gravura sozinho não sabe que aquilo é texto. Isso se resolve juntando com o OCR, que sabe onde há texto. Melhor aqui: **A** (moldura cheia).

**Opus Majus 20 (a estátua): resolvido com "tem foto".** Na A a estátua fica fora da gravura: sai lavada, o vão escuro sai pontilhado e aparece um bloco branco ao lado. **E, F, G, H e I (com fotos) saem bons, quase como o original.** B e D também (imagens claras), mas estragam outras páginas (abaixo). Melhor: **E**. No programa, isso é "Esta página tem foto" na aba Marcar, ou "Este livro tem fotos" para o Opus Majus inteiro.

**Horas 11 (iluminura): boa em todas.** A iluminura sai inteira e colorida, e o centro fica branco com as letras coloridas. H marca a página inteira (100%). Melhor: **A** (ou E).

**Horas 27 (moldura): boa em A e C.** A moldura inteira é gravura. B, D e H pegam papel em volta. Melhor: **A**.

**Palatino 9: boa em A, C, E, F, G e I** (0%: a inicial "Q" é tratada como traço, e a tira creme entre os fios não volta). B, D e H marcam a moldura e o papel (24% a 37%). Melhor: **A**.

**Palatino 67: boa em A, C, E, F, G e I.** B deixa uma mancha cinza perto de "5 ꝛ ꝑ ꝝ t9". D e H marcam metade da página. Melhor: **A**.

**Marial 153 (página de texto): boa em A, F e G** (0%). B, D, E, H e I marcam 13% da página como gravura, e C deixa o canto cinza. Melhor: **A**.

## Recomendação (o Samuel decide)

1. **Manter a de fábrica: A**, que é "Achar gravuras e fotos" seguindo o desenho, sem "imagens claras" e com "igualar a luz". Ela é a melhor ou empata em 8 das 9 páginas. Não mudei nenhum padrão.
2. **"Procurar também imagens claras" não deve vir marcada.** Ela resolve o Opus 20, mas põe gravura no texto do Marial 153, no Palatino 9 e 67 e no papel da Horas 27.
3. **Opus Majus:** marcar "Este livro tem fotos" no livro inteiro. As outras páginas do Opus Majus que olhei na rodada anterior (3, 11, 165, 256) saem iguais com e sem. Ou marcar "Esta página tem foto" só na 20.
4. **Sensibilidade:** 100 é bom para foto. 70 e 40 mudam pouco no Opus 20 e só ajudam quando o retângulo pega papel (Horas 13, 26). Deixar 100.
5. **Título da Horas 26:** item 1.5 (OCR).

## Ressalvas

- Rodada feita com a máquina dividida com outro agente: os tempos não valem como medida oficial. Nas 9 páginas, o processar muda pouco entre as combinações. A exceção é o Marial 153 nas que marcam 13% da página (B, C, D, E, H, I): até +10 s.
- O Preto e branco destas folhas já tem a regra nova do filtro (a moldura em desenho). Ela não é minha: o que olhar ali é só onde a gravura está.
- A "Esta página tem foto" foi testada pela função e pela tela sem janela (foto da aba Marcar), não com mouse de verdade.
