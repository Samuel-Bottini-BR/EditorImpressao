# Onde estamos — Editor de Impressão

Escrito em 04/08/2026. Registra o que foi feito nesta conversa, o que foi
pedido, o que foi perguntado, e o que falta para o programa estar pronto.

---

## 1. O que é o programa, e para quem

Aplicativo de Windows que recupera PDFs de livros antigos escaneados e os
prepara para reimpressão em cadernos. Projeto do Pe. Rosenei, de um instituto
de preservação de livros.

**Quem usa é o Kaique, impressor, sem formação técnica.** Ele nunca vê
"Sauvola", "k" ou "deskew" — vê "Força do preto", "Melhorar", "girar a folha".
Duas versões anteriores fracassaram: uma travava, a outra dava qualidade ruim.
Daí vêm as regras rígidas do projeto.

O fluxo é: arrasta o PDF, marca o que quer fazer, confere página a página,
escolhe onde salvar, processa. Quatro filtros: Original, Preto e branco,
Melhorar e Mágico pro.

---

## 2. O que você me pediu nesta conversa

Foram três pedidos, nesta ordem:

1. **"vamos continuar o trabalho do editor de impressão"**
2. **"porque você continua travando, porque não vai até o final?"**
3. **"me da um resumo de tudo que tu fez agora em arquivo md, as perguntas que
   me fez os prints que eu te mandei, os pedidos que eu te fiz em toda a
   conversa, as questões que tu perguntou para mim e o que falta para o
   programa estar pronto"**

O segundo pedido era uma correção, e é o mais importante dos três. Eu havia
parado duas vezes para perguntar por onde seguir em vez de fazer o trabalho.
A partir dali passei a escolher o caminho sozinho, dentro da fronteira de
autonomia que o projeto define, e a executar até o fim. Ficou anotado na minha
memória permanente para valer nas próximas conversas.

---

## 3. O que eu perguntei, e o que você respondeu

Duas perguntas, ambas antes da sua correção.

**Pergunta 1 — "Por onde continuamos?"**

Ofereci quatro caminhos: conferir a página de imagens que estava sem revisão;
atacar o serrilhado do Boécio (8 casos); atacar o fundo que escurece (7 casos);
ou o entupimento das letras no Catecismo (3 casos).

> **Você respondeu:** conferir a página de imagens primeiro.

**Pergunta 2 — "O que faço com o `o-que-mudou.html`?"**

Ofereci: corrigir os textos e commitar; corrigir e ir atrás do problema do
BRODERIES; só commitar como estava; ou não commitar ainda.

> **Você respondeu:** corrigir os textos e commitar.

Depois dessas duas veio a sua correção, e não perguntei mais nada.

---

## 4. Sobre os prints

**Nesta conversa você não me mandou nenhum print.** As dez imagens que eu abri
não vieram de você: elas estavam embutidas dentro do arquivo
`relatorios/o-que-mudou.html`, que o próprio projeto tinha gerado às 09:15 de
hoje e que ainda não havia sido conferido por ninguém. Eu extraí as dez do
arquivo e as abri uma a uma.

Os prints que existem no projeto e que são fonte de requisito são outros: são
as capturas de tela que o **Kaique** deixou junto das queixas dele, na pasta
`Desktop\BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros`. Elas estão listadas na
seção 6, junto de cada queixa.

---

## 5. O que eu fiz

### 5.1 Retomada do contexto

Localizei o projeto em `Desktop\EditorImpressao` e reconstruí onde o trabalho
havia parado. O último commit era de hoje às 09:05 — *"Folha em branco para de
sair mais escura e mais suja"* —, e havia um arquivo não commitado gerado dez
minutos depois: `relatorios/o-que-mudou.html`, uma página de conferência visual
com dez imagens.

Descobri também que **cinco dos nove relatórios estavam desatualizados**:
Graduale, Horas, Marial, BRODERIES e Siebmacher foram medidos entre 00:58 e
01:23, mas o `core/filtros.py` mudou às 08:37. Os números daqueles cinco livros
descrevem um programa que não existe mais.

### 5.2 Conferência das dez imagens

Segui a regra do projeto: abrir todas as imagens antes de dizer que funcionou,
e julgar contra a página, não contra a legenda de quem implementou.

Abri as dez. Em seis lugares a legenda prometia mais do que eu conseguia
enxergar no tamanho normal, então ampliei essas regiões de 2 a 3,4 vezes e
olhei de novo. **Oito conferem, uma confere com ressalva, uma não confere.**

| # | Quadro | Veredito |
|---|---|---|
| 1 | Letra arredondada (Rhetorica p334) | confere — a borda tem meio-tom e fecha redonda |
| 2 | Papel branco, mancha do verso fora (Boécio p33) | confere, com ressalva |
| 3 | Risca do vinco (Graduale p536) | confere — a faixa de papel saiu, nada de conteúdo foi cortado |
| 4 | Inicial preservada (Graduale p108) | confere — a capitular está inteira |
| 5 | Xilogravura é gravura (Rhetorica p112) | confere |
| 6 | Mancha do papel não é gravura (Rhetorica p223) | confere |
| 7 | Iluminura sai inteira (Horas p95) | confere — só dava para ver ampliado |
| 8 | Foto do bordado (BRODERIES p73) | **não confere** |
| 9 | Gravura e texto na mesma página (Catecismo p118) | confere — conferido em três pontos |
| 10 | Capa é foto (Palatino p134) | confere |

**A ressalva do quadro 2.** A mancha do verso sumiu, o papel ficou branco e
nenhuma letra foi comida — a legenda só promete isso e cumpre. Mas ampliado
quatro vezes, o papel branco tem uma dúzia de pontos escuros de 3 a 8 pixels
espalhados e sobra um véu esverdeado na borda direita. É sujeira que ficou.

**O que não confere no quadro 8.** A legenda dizia que só as legendas impressas
viram texto. Ampliado, não é isso: o **título impresso** "POINT DE VANNIER OU
POINT DE BRIQUES." está dentro do vermelho, tratado como foto; e das quatro
caixas de legenda do pé, três saem azuis e a quarta sai vermelha. É texto
impresso do mesmo tipo, no mesmo fundo pardo, decidido de dois jeitos na mesma
folha.

**Um achado de fora do roteiro.** No quadro 7, as rubricas vermelhas da
iluminura — *Secreta.*, *Præfatio…*, *Communio.*, *Postcommunio.* — estão
marcadas como letra. No preto e branco elas vão sair pretas. É a mesma perda de
rubricação vermelha já anotada no Graduale, agora aparecendo num segundo livro.

### 5.3 Correção e commit

Commit `07b550e`. A legenda do quadro 8 passou a dizer o que a imagem mostra; o
fecho da página passou a listar o caso do BRODERIES junto dos outros problemas
que já estavam assumidos, e ganhou um parágrafo sobre a rubricação do Livro de
Horas. Só texto: nenhum filtro, detector ou régua foi tocado.

### 5.4 Diagnóstico do fundo que escurece

Escolhi este grupo por ser o maior que se espalha por vários livros — sete
ocorrências em quatro livros —, o que costuma indicar causa única.

Reproduzi as seis páginas reprovadas e medi o fundo **depois de cada passo** do
Melhorar e do Mágico pro, sempre na mesma região de papel tirada do original.
O resultado foi unânime: quem escurece é um passo só, o **realce de saturação**
do Mágico pro.

| Página | Classe | Fundo original | Queda causada pela saturação |
|---|---|---|---|
| BRODERIES 16 | vazia | 91,5 | 13,4 |
| BRODERIES 46 | ilustração | 153,8 | 6,3 |
| BRODERIES 76 | ilustração | 156,4 | 6,5 |
| Palatino 1 | ilustração | 81,2 | 10,0 |
| Rhetorica 446 | vazia | 201,9 | 11,0 |
| Boécio 50 | vazia | 145,5 | 15,9 |

Todos os outros passos são neutros ou clareiam. No Boécio, o achatamento da
iluminação chega a subir o fundo de 145,5 para 154,4 — e a saturação joga para
138,6. E o Melhorar, que não tem esse passo, **passa nas seis páginas**.

**Por que acontece.** O passo multiplica o S do HSV mantendo o V. Isso preserva
o brilho, mas não a luminância: o cinza é 0,299 R + 0,587 G + 0,114 B, com o
maior peso no verde, e numa cor quente subir a saturação empurra verde e azul
para baixo. Papel envelhecido é sempre amarelo-pardo. Então o papel escurece —
que é exatamente a queixa do Kaique sobre o amarelado.

**A correção que preparei** é medir a mesma coisa em LAB: multiplicar `a` e `b`,
que são os dois eixos de cor, e não tocar em `L`. Matiz igual, cor mais forte,
luminância no lugar — que é o que "cor mais viva" deveria significar. O passo
vizinho, o contraste local, já trabalha em LAB pelo mesmo motivo.

**A correção ainda não foi aplicada.** Está escrita e pronta, com o experimento
montado para medi-la contra a versão de hoje nas seis páginas reprovadas e em
quatro páginas de controle — rubricação do Graduale, iluminura do Horas,
estampa do Catecismo e texto corrido do Marial —, onde a cor **tem** de
continuar subindo, senão a troca custa aquilo para que o filtro existe.

### 5.5 Linha de base

Como cinco dos nove relatórios estavam desatualizados, pus a régua para rodar
sobre o acervo inteiro antes de mexer em qualquer coisa. **Estava em andamento
quando esta conversa foi interrompida** — livro 2 de 9. São cerca de 33 minutos.

Sem esse "antes" honesto, o "depois" não quer dizer nada.

---

## 6. O que o Kaique pediu, e onde está cada pedido

As queixas estão nos `.txt` que ele deixou junto dos prints, em
`Desktop\BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros`. São a fonte de
requisito do projeto.

| Queixa, nas palavras dele | Situação |
|---|---|
| "as letras estão ficando pixeladas, precisamos que elas fiquem mais arredondadas, mais nítidas" | **Atendido e conferido na imagem** (quadro 1). O raio da nitidez era largo demais e desenhava um halo em vez de afiar. |
| "o magico pro está deixando muito pixelado a imagem" | **Atendido e conferido**, mesma causa da anterior. |
| "as vezes a parte de trás fica com uma mancha da parte da frente" | **Atendido e conferido** (quadro 2), com a ressalva dos pontinhos que ficaram. |
| "o programa não localizou as bordas corretamente" | **Atendido e conferido em dois casos** (quadros 3 e 4): a risca do vinco e a inicial que era cortada. |
| "queremos que fique branco a pagina e só a letras pretas" (Preto e branco) | **Atendido em número** — o fundo do Preto e branco mede 253,8 numa escala em que 255 é branco. Mas a queixa original era de uma página que ficou *menos legível* que o original, e isso levou à comparação dos 18 binarizadores: a conclusão foi que **não existe vencedor único, a escolha certa depende da página**. Continua em aberto. |
| "no filtro mágico pro o fundo deveria remover o amarelado e deixar totalmente branco, e preservar as cores dos textos e imagens" | **Em curso.** É exatamente o trabalho da seção 5.4. Hoje o Mágico pro deixa o fundo em torno de 226 contra 255 de alvo. |
| "colocar botão clicável nas paginas que o programa não tem certeza" | Os alertas laranja existem e são contados nos relatórios. **Não verifiquei se há o botão clicável.** |
| "pode dar problema na sequência dos cadernos? como ter certeza sem olhar folha por folha?" | Existe `core/cadernos.py` com instruções de impressão. **Não verifiquei nesta conversa.** |
| "o livro já foi recortado ao meio, sobra dos lados uma parte branca que devia ser recortada" | **Não verifiquei nesta conversa.** É caso diferente do quadro 3. |
| "a barra de scroll devia ser preta para ficar com visualização mais fácil" | **Não verifiquei nesta conversa.** |

---

## 7. O que falta para o programa estar pronto

### 7.1 A régua tem de zerar

O critério de aceitação do projeto é duro e é um só: **nenhuma página pode sair
pior do que entrou, em nenhum filtro.** Hoje esse número não é zero.

Pela última medição completa eram 25 ocorrências. Essa contagem está sendo
refeita agora, e vai mudar — cinco livros foram medidos com código antigo.
Agrupadas por causa, eram assim:

| Causa | Ocorrências | Onde |
|---|---|---|
| Borda virou degrau | 8 | Boécio 9, 17, 33, 41; BRODERIES 76 |
| Fundo escureceu | 7 | BRODERIES 16, 46, 76; Palatino 1; Rhetorica 446; Boécio 50 |
| Fundo ficou mais sujo | 6 | Graduale 1, 126, 750; Boécio 1 |
| Letras entupiram | 3 | Catecismo 199, nos três filtros |
| Borda borrou | 1 | BRODERIES 46 |

O grupo do fundo que escurece está diagnosticado e com a correção pronta. Os
outros quatro ainda não foram investigados.

Sobre o grupo do serrilhado: **todas as páginas do Boécio têm rampa original
entre 0,70 e 0,86**, abaixo da faixa saudável antes de qualquer tratamento — é
um scan de baixa resolução, 4 MB para 50 folhas. Ampliada, a letra sai redonda.
Falta decidir se ali o defeito é do filtro ou da própria régua, que penalizada
uma queda relativa num número que já nasce fora da faixa.

### 7.2 Os dois achados de hoje

- **BRODERIES:** título impresso e uma das quatro legendas saem como foto,
  enquanto as outras três saem como texto — na mesma folha, no mesmo fundo.
  Provavelmente a mesma causa da folha do Siebmacher que sai tratada como foto.
- **Rubricação vermelha virando preto**, agora em dois livros. A causa suspeita
  já está escrita: a conversão para cinza trata vermelho como escuro. O DoxaPy
  oferece oito métodos de conversão a investigar.

### 7.3 Pendências já anotadas em `melhorias.md`

- **A medida de transição está contaminada.** Ela conta pixels de tom
  intermediário na página inteira, e papel ruidoso infla o número. Precisa
  contar só junto do contorno da letra. Não muda nenhum veredito já dado, mas
  muda a magnitude e vai contaminar toda comparação futura.
- **Falta um número para "guardou a sujeira".** O Otsu marca zero pioras, mas
  guarda o dobro de tinta do Sauvola — em papel envelhecido isso quer dizer
  manter a mancha como se fosse letra, e **nenhum critério atual pega isso**.
  Enquanto esse número não existir, a régua pode aprovar o filtro errado.
- **Escolha do binarizador por página.** No Palatino, de letra gótica pesada, o
  Otsu sai sólido enquanto o Sauvola quebra o traço; em outras páginas se
  inverte. Hoje o programa usa um só para tudo.

### 7.4 Fora da imagem

Quatro pedidos do Kaique da lista acima não foram verificados nesta conversa e
não têm evidência de conferência: o botão clicável nas páginas incertas, a
garantia da sequência dos cadernos sem olhar folha por folha, o recorte do
livro que já veio cortado ao meio, e a barra de rolagem preta.

### 7.5 Duas coisas pequenas de arrumação

- **O `CLAUDE.md` está desatualizado num ponto:** diz que o acervo de teste está
  em `Desktop\BIBLIOTECA DO FIM DOS TEMPOS`. Os PDFs não estão mais lá — estão
  em `Desktop\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE`. Na pasta antiga
  ficaram só as queixas e os prints do Kaique. O `avaliar.py` já sabe disso e
  procura nos dois lugares; o texto é que não acompanhou.
- **O repositório não tem identidade de git configurada.** Os commits vêm sendo
  feitos passando nome e e-mail por variável de ambiente a cada vez.

---

## 8. Como isso é medido, e a regra que não muda

O protocolo do projeto é: **medir antes, uma mudança por vez, medir de novo, e
reverter se qualquer número piorar.** Se a mudança parecer valer a pena mesmo
assim, não reverter por conta própria — apresentar os dois resultados.

E antes de julgar qualquer resultado visual: **abrir todas as imagens.**
Percentual não é veredito, e expectativa escrita por quem implementou não é
critério de acerto. Essa regra existe porque já foi reportado "10 de 10
corretas" tendo olhado uma imagem — seis estavam erradas.

Fora da imagem, o que já está de pé: **124 testes automatizados** em `tests\`, e
**20 de 20 casos de robustez** — PDF corrompido, protegido por senha, arquivo
que some no meio, disco cheio, livro de 1010 páginas, cancelar no meio. Em
nenhum deles o programa fecha, e em nenhum deles se perde trabalho já feito.
