# Conferência do item fase1: Fase 1 inteira (1.1 a 1.6): separar o escrito do fundo

<style>
body { max-width: 120rem; }
body > p, body > ul, body > ol, body > blockquote, body > pre, body > h1,
body > h2, body > h3, body > .faixa { max-width: 58rem; }
table.paineis { display: table; width: 100%; table-layout: fixed; border-collapse: separate;
  border-spacing: 10px 0; margin: .3em 0 1.3em; font-size: .92rem; }
table.paineis td { border: none; padding: 0 0 .9em; vertical-align: top; }
table.paineis td b { display: block; font-weight: 620; padding: .2em 0 .3em; }
table.paineis img { display: block; width: auto; height: auto; max-width: 100%;
  max-height: 82vh; margin: 0; }
table.paineis .falta { display: block; padding: 2.5em 1em; background: #f1efec; color: #55524d;
  border-radius: 6px; }
.faixa { padding: .8em 1.1em; border-radius: 8px; margin: 1em 0 1.4em; }
.faixa p { margin: 0; }
.faixa.falta { background: #fff1c2; border: 1px solid #e0b400; color: #3d3000; }
.faixa.pronta { background: #dff3e2; border: 1px solid #5aa469; color: #123d1c; }
@media (prefers-color-scheme: dark) {
  table.paineis .falta { background: #262421; color: #b0aca6; }
  .faixa.falta { background: #3d3200; border-color: #8a6d00; color: #fff1c2; }
  .faixa.pronta { background: #173d20; border-color: #3f7a4c; color: #dff3e2; }
}
</style>

<div class="faixa pronta"><p><strong>PRONTO PARA CONFERIR.</strong> O verificador olhou as imagens e escreveu a opinião dele logo abaixo, com as ressalvas. Quem marca o item no plano é o Samuel.</p></div>

Gerada em 28/09/2026 às 17:45, com 32 páginas-gabarito do item fase1. O **depois** são imagens já prontas, da pasta `relatorios\conferir\fase1-2026-09-28-1644`. São as imagens da rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro, reaproveitadas sem processar de novo. A coluna **Rodada anterior** mostra as imagens de `relatorios\conferir\fase1-2026-09-28-1611` (rodada de 28/09/2026 às 16:11, do programa no filtro Mágico pro), para ver o que a mudança de código mudou.

Teste **de olho**: quem decide é o Samuel, olhando.

Em cada página: **a página inteira** e, embaixo, **o detalhe ampliado** do ponto que importa (o retângulo rosa). **Clique** numa imagem para abrir em tamanho cheio. A explicação completa está no fim, em "Como ler esta página".

## Opinião do verificador

> **DEFEITO CONHECIDO: MOLDURA DOURADA E ILUMINURA.** Até a Fase 1 ficar pronta, a moldura dourada com furinhos (Horas 26 e 27) e a iluminura apagada (Horas 11) são defeito conhecido do filtro. Vão ser resolvidos nos itens 1.2, 1.4 e 1.5 (decisão do Samuel, 28/09). **Nesta página, não olhe a cor: olhe só o corte das bordas.**

### O que está sendo conferido

O conserto do **corte de bordas** (bug da conferência 6.7, opção (a) do Samuel: só **"não comer conteúdo"**; "seguir a beirada do papel" fica para a Fase 2). A coluna **Rodada anterior** é o programa antes do conserto (28/09, 16:11) e a coluna **Resultado** é depois do conserto (28/09, 16:44). As duas rodadas foram feitas no Mágico pro, com as mesmas 32 páginas. As imagens não foram processadas de novo para esta página.

### Em uma frase

**PRONTO PARA CONFERIR.** O corte parou de comer o conteúdo na página da queixa (Escola 35: o "37" e o começo das linhas saem inteiros). Também parou de cortar números de página, assinaturas do pé e pedaços de moldura em mais umas vinte páginas. Nenhuma página perdeu nada, porque o corte só cresceu. Mas vieram **duas pioras pequenas** (Marial 7 e Palatino 67), e **ficaram duas sobras** do defeito antigo, no Graduale. O Samuel precisa ver essas quatro para decidir.

### Para o Samuel conferir em 10 minutos

1. **Escola 35**: no pé, à direita, o **"37"** agora está inteiro (antes saía "3"). Na margem esquerda, do "Deus criou" para baixo, **o começo das linhas** está inteiro (antes era comido).
2. **Opus Majus 11 e 165**: no pé, os números **"[ xi ]"** e **"[ 143 ]"** agora estão inteiros (antes saíam cortados ao meio).
3. **Marial 7** (piora): na **borda direita, de cima a baixo**, entrou uma **faixa escura nova**, de 1,5 a 2,5 mm de largura.
4. **Palatino 67** (piora): na **terceira linha de letras** ("5 ꝛ ꝑ ꝝ t9"), apareceu uma **caixa cinza-clara** em volta da linha.
5. **Graduale 222, 221 e 223** (não mudou): no **alto à esquerda do 222**, a ponta de cima da **primeira clave** continua cortada. No **alto à direita do 221 e do 223**, o **fim do número da folha** ("C vi…", "C viij") continua cortado.
6. **Rhetorica 18** (piora pequena): amplie o meio do texto. **A orla das letras ficou um pouco mais cinza.** De longe, não se nota.

### O que foi conferido por máquina

- **Testes automáticos:** os **699 passaram**, incluindo os 5 novos do corte (`tests/test_corte_nao_come_conteudo.py`).
- **As rodadas mostram o código de hoje:** refiz só o corte e o endireitar das 32 páginas, sem filtro e sem gravar nada, uma vez com o código de antes (o do git) e outra com o de hoje. O tamanho das imagens bateu ponto por ponto com as duas rodadas.
- **O corte só cresceu:** nenhuma página ficou menor. 30 de 32 ficaram maiores, de 0,2% a 5,7% em área. A Horas 26 e o Opus Majus 3 ficaram iguais.
- **Peças de tinta partidas pela borda do corte:** caíram de **94 para 25**. Contei com uma máscara de tinta minha, diferente da do programa, e ela conta também as sujeirinhas e os fios da beirada. Por isso o número não é o mesmo do implementador (109 para 6). Das 25 que sobram, quase todas são fio da beirada ou sujeira. **Mas há letra entre elas:** o fim do número da folha do Graduale 221 e 223 e o pé do endereço do site da Escola 35. A frase "nenhuma é letra" **não se confirma**.
- **Tinta encostada na beirada da imagem final:** diminuiu em 20 páginas e só aumentou no **Marial 7** (a faixa escura).
- **"Papel acinzentado" da Rhetorica 18:** subiu de 6,5% para 10,0% na minha medida. A piora está na parte da página que já existia antes (de 6,5% para 10,3%). Na faixa nova de margem ela é quase nula (0,4%). Então **a causa não é a margem nova que entrou**.
- **O detector de gravura e letra muda com o enquadramento:** rodei **só o detector** (sem filtro) nos dois enquadramentos.
  - Na **Palatino 67**, com o corte novo, ele marca a linha "5 ꝛ ꝑ ꝝ t9" como **gravura** (antes, como letra). Isso explica a caixa cinza.
  - Na **Rhetorica 18**, com o corte novo, ele marca uma região de **"papel" que cobre quase a página toda**. Antes, só a coluna das notas da margem era "papel". É a **causa provável** do acinzentado, **não provada**: provar exigiria processar de novo com o filtro, o que não pode ser feito agora, porque o filtro está sendo mexido.
- **O ângulo de endireitar mudou 0,1 grau em 8 páginas:** ele é medido na página já cortada, que agora é maior. A Palatino 67 passou a ser girada (antes não era).

### O que foi conferido por olho

Abri e olhei as 32 páginas das duas rodadas, lado a lado, e as quatro bordas de cada uma, ampliadas. Nos pontos da lista de 10 minutos, comparei com o original.

<img src="verificador/01-escola35.jpg" width="560" alt="Escola 35: o 37 e o comeco das linhas, antes e depois">

<img src="verificador/02-opus-numeros.jpg" width="640" alt="Opus Majus 11 e 165: numero de pagina antes e depois">

<img src="verificador/03-marial7-borda-direita.jpg" width="640" alt="Marial 7: faixa escura nova na borda direita">

<img src="verificador/04-palatino67-caixa.jpg" width="640" alt="Palatino 67: caixa cinza em volta da linha">

<img src="verificador/05-graduale-sobras.jpg" width="640" alt="Graduale: numero da folha e clave que continuam cortados">

<img src="verificador/06-rhetorica18-orla.jpg" width="560" alt="Rhetorica 18: orla das letras um pouco mais cinza">

**Página por página** (a Horas 26 entra mesmo sem ter mudado, porque é uma das páginas da queixa):

- **Palatino 5:** o "L" de LIBRO e o "A" final de GIOVAMBATTISTA, antes cortados na borda, saem inteiros, e a moldura oval ganhou folga. O fundo do retrato continua marrom: é regra da Fase 1, ainda não feita.
- **Palatino 7:** a assinatura **"A ii"** do pé, antes cortada, aparece inteira.
- **Palatino 9:** o **"A iii"** do pé, antes partido pela borda, está inteiro.
- **Palatino 10:** a barra de fora da moldura da direita, antes cortada, está inteira.
- **Palatino 57:** o **"D iii"** do pé está inteiro, e a moldura da direita também.
- **Palatino 66:** quase igual (menos de meio milímetro a mais).
- **Palatino 67:** a moldura da direita está inteira. **Piorou:** apareceu a caixa cinza-clara em volta da linha "5 ꝛ ꝑ ꝝ t9".
- **Marial 7:** o texto está igual. **Piorou:** entrou uma faixa escura de 1,5 a 2,5 mm em toda a borda direita.
- **Graduale 221:** o alto da clave e do número da folha agora está inteiro. **O fim do número continua cortado à direita** (como antes).
- **Graduale 222:** ganhou papel dos dois lados, e as claves da esquerda estão inteiras (já estavam antes). **A ponta de cima da primeira clave continua cortada** (como antes). A beirada escura da direita ficou um pouco mais larga.
- **Graduale 223:** o alto do número da folha agora está inteiro. **O fim do número continua cortado à direita.**
- **Horas 11:** o ornamento do alto e a moldura da direita, antes cortados, estão inteiros. A iluminura está apagada: é o defeito conhecido.
- **Horas 13:** mais papel em cima e embaixo. Entrou um fiozinho da beirada do papel embaixo, à direita.
- **Horas 14:** mais papel em cima e embaixo, e a moldura da TABLE ganhou folga.
- **Horas 26:** **igual**. O corte continua sem seguir a beirada do papel, o que fica para a Fase 2 (decisão do Samuel).
- **Horas 27:** a moldura dourada da direita, antes estreitada pelo corte, está inteira. Tem mais papel embaixo.
- **Horas 47:** os ornamentos do alto e do pé da moldura, antes cortados, estão inteiros.
- **Escola 7:** "CRISTÃ" e o fim das linhas da direita, antes encostados na borda, saem inteiros.
- **Escola 35:** o "37" e o começo das linhas saem inteiros. **O pé do endereço do site continua encostando na borda de baixo** (como antes), mas esse endereço vai ser apagado no item 6.4.
- **Siebmacher 7 e 9:** praticamente iguais. A linha preta grossa da direita é a beirada da folha e já estava lá antes.
- **Rhetorica 18:** os fios da moldura e o "lunt" do pé ganharam folga. **A orla das letras ficou um pouco mais cinza.**
- **Rhetorica 73:** quase igual.
- **Boécio 3:** mais papel em cima, e o título ganhou folga.
- **Boécio 7:** o pé ("A 4", "Immiſ"), antes encostado na borda de baixo, ganhou folga.
- **Boécio 8:** o "Nihil" do pé está inteiro. Entraram manchinhas marrons da margem direita.
- **Boécio 22:** o começo das linhas da esquerda e o "Edibus" do pé ganharam folga. Tem uma manchinha marrom na margem direita.
- **Opus Majus 11:** o "[ xi ]" do pé está inteiro.
- **Opus Majus 20:** quase igual. A foto da estátua continua lavada de branco, mas esse é um bug do filtro, já na lista.
- **Opus Majus 165:** o "[ 143 ]" do pé está inteiro, e o fim das linhas ganhou folga.
- **Opus Majus 256:** as notas das margens ("Principium cycli…" à esquerda, "April.", "Mart." à direita), antes cortadas, saem inteiras.
- **Opus Majus 3:** não mudou nada.

### Ressalvas

- **O teste de velocidade não foi rodado**: foi combinado assim, porque o Samuel precisa deixar o PC quieto. Pela regra 6 do plano, ele ainda tem de ser feito antes de aprovar. Há só um indício, que não é medição: a soma do tempo por página nas duas conferências foi de 290 s antes e 268 s depois, com o PC em uso.
- **A tela não foi testada.** A prévia usa a mesma função do PDF, mas não abri o programa. O bug da prévia (110 DPI) cortar diferente do PDF continua na Lista de bugs e não foi conferido aqui.
- **Duas pioras novas:** a faixa escura do Marial 7 e a caixa cinza da Palatino 67. **Uma piora pequena:** o cinza nas letras da Rhetorica 18. As duas últimas vêm do detector, que marca a página de outro jeito quando o enquadramento muda. Não é defeito do corte em si, mas foi o corte que as trouxe.
- **Duas sobras do defeito antigo**, que não pioraram nem melhoraram: a clave do alto do Graduale 222 e o fim do número da folha do Graduale 221 e 223.
- Para conferir o Rhetorica 18 e o Palatino 67, rodei **só o detector** (sem o filtro, sem gravar imagem nenhuma). O arquivo do filtro não mudou desde 25/09, então nada da outra mudança entrou nesta conferência.
- **Horas 26 e 27** (a queixa do Samuel de "não seguir a margem do papel") **não foram consertadas de propósito**: ficam para a Fase 2.

## 1. Giovambattista Palatino cittadino romano, página 5 do PDF

**O que olhar:** R1: papel branco, letras e gravura (retrato) intactas

`palatino_p005`. Processada em 4,0 segundos (a análise automática levou mais 0,5 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p005.jpg" target="_blank"><img src="paineis/01-palatino_p005-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-1-original-detalhe.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-2-anterior-detalhe.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-3-resultado-detalhe.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p005.jpg" target="_blank"><img src="paineis/01-palatino_p005-4-scantailor-detalhe.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 2. Giovambattista Palatino cittadino romano, página 7 do PDF

**O que olhar:** R1: papel branco, letras intactas; tem mancha de outra página (marcada de azul no documento)

`palatino_p007`. Processada em 3,3 segundos (a análise automática levou mais 0,5 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-2-anterior-detalhe.jpg" width="239" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-3-resultado-detalhe.jpg" width="239" alt="3. Resultado: Mágico pro"></a></td><td></td></tr>
</table>

## 3. Giovambattista Palatino cittadino romano, página 9 do PDF

**O que olhar:** R1: papel branco, letras e gravura intactas; borda preta em volta do texto

`palatino_p009`. Processada em 3,9 segundos (a análise automática levou mais 0,5 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-1-original-detalhe.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-2-anterior-detalhe.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-3-resultado-detalhe.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-4-scantailor-detalhe.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 4. Giovambattista Palatino cittadino romano, página 10 do PDF

**O que olhar:** R2: sumir com a sombra do verso (folha só de letras)

`palatino_p010`. Processada em 3,8 segundos (a análise automática levou mais 0,5 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 5. Giovambattista Palatino cittadino romano, página 57 do PDF

**O que olhar:** R3: margens iguais / centralizar (texto mais à esquerda, moldura em volta)

`palatino_p057`. Processada em 3,6 segundos (a análise automática levou mais 0,3 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 6. Giovambattista Palatino cittadino romano, página 66 do PDF

**O que olhar:** R4: tirar as manchas vermelhas sem mexer no título

`palatino_p066`. Processada em 3,7 segundos (a análise automática levou mais 0,3 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 7. Giovambattista Palatino cittadino romano, página 67 do PDF

**O que olhar:** R4: manchas no papel amarelado (circuladas de laranja no documento), 'mesmo problema da anterior' (p. 66)

`palatino_p067`. Processada em 3,3 segundos (a análise automática levou mais 0,3 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-2-anterior-detalhe.jpg" width="239" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-3-resultado-detalhe.jpg" width="239" alt="3. Resultado: Mágico pro"></a></td><td></td></tr>
</table>

## 8. Marial de sermoens - Frei Balthasar Paez. (1), página 7 do PDF

**O que olhar:** R2 / item 6.1: letras do verso aparecendo através do papel. (No Vamos recapitular, o 'Livro 4' também cita linhas tortas, centralizar, papel branco, mancha amarronzada embaixo à direita e margens.)

`marial_p007`. Processada em 8,0 segundos (a análise automática levou mais 0,2 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/marial_p007.png" target="_blank"><img src="paineis/08-marial_p007-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/marial_p007.png" target="_blank"><img src="paineis/08-marial_p007-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/marial_p007.png" target="_blank"><img src="paineis/08-marial_p007-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/marial_p007.png" target="_blank"><img src="paineis/08-marial_p007-1-original-detalhe.jpg" width="487" alt="1. Original"></a></td></tr>
<tr><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/marial_p007.png" target="_blank"><img src="paineis/08-marial_p007-2-anterior-detalhe.jpg" width="487" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Mágico pro</b><a href="resultado/marial_p007.png" target="_blank"><img src="paineis/08-marial_p007-3-resultado-detalhe.jpg" width="487" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 9. Graduale - Saeculum XIV, página 221 do PDF

**O que olhar:** R5/R6: endireitar a partitura torta, manter as linhas vermelhas e os neumas, papel branco, tirar manchas

`graduale_p221`. Processada em 13,4 segundos (a análise automática levou mais 0,3 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/graduale_p221.png" target="_blank"><img src="paineis/09-graduale_p221-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/graduale_p221.png" target="_blank"><img src="paineis/09-graduale_p221-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/graduale_p221.png" target="_blank"><img src="paineis/09-graduale_p221-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/graduale_p221.png" target="_blank"><img src="paineis/09-graduale_p221-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/graduale_p221.png" target="_blank"><img src="paineis/09-graduale_p221-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/graduale_p221.png" target="_blank"><img src="paineis/09-graduale_p221-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 10. Graduale - Saeculum XIV, página 222 do PDF

**O que olhar:** R3: aumentar a margem do lado direito

`graduale_p222`. Processada em 15,1 segundos (a análise automática levou mais 0,3 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/graduale_p222.png" target="_blank"><img src="paineis/10-graduale_p222-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/graduale_p222.png" target="_blank"><img src="paineis/10-graduale_p222-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/graduale_p222.png" target="_blank"><img src="paineis/10-graduale_p222-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/graduale_p222.png" target="_blank"><img src="paineis/10-graduale_p222-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/graduale_p222.png" target="_blank"><img src="paineis/10-graduale_p222-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/graduale_p222.png" target="_blank"><img src="paineis/10-graduale_p222-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 11. Graduale - Saeculum XIV, página 223 do PDF

**O que olhar:** R3: mais margem do lado esquerdo (página seguinte da 222)

`graduale_p223`. Processada em 14,1 segundos (a análise automática levou mais 0,3 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/graduale_p223.png" target="_blank"><img src="paineis/11-graduale_p223-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/graduale_p223.png" target="_blank"><img src="paineis/11-graduale_p223-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/graduale_p223.png" target="_blank"><img src="paineis/11-graduale_p223-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/graduale_p223.png" target="_blank"><img src="paineis/11-graduale_p223-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/graduale_p223.png" target="_blank"><img src="paineis/11-graduale_p223-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/graduale_p223.png" target="_blank"><img src="paineis/11-graduale_p223-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 12. Livro de Horas - Luís XIV, página 11 do PDF

**O que olhar:** R6: letras nas cores originais no meio da iluminura, papel branco, gravura intacta, pôr ou tirar margem

`horas_p011`. Processada em 15,8 segundos (a análise automática levou mais 0,4 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p011.png" target="_blank"><img src="paineis/12-horas_p011-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p011.png" target="_blank"><img src="paineis/12-horas_p011-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p011.png" target="_blank"><img src="paineis/12-horas_p011-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/horas_p011.jpg" target="_blank"><img src="paineis/12-horas_p011-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p011.png" target="_blank"><img src="paineis/12-horas_p011-1-original-detalhe.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p011.png" target="_blank"><img src="paineis/12-horas_p011-2-anterior-detalhe.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p011.png" target="_blank"><img src="paineis/12-horas_p011-3-resultado-detalhe.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/horas_p011.jpg" target="_blank"><img src="paineis/12-horas_p011-4-scantailor-detalhe.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 13. Livro de Horas - Luís XIV, página 13 do PDF

**O que olhar:** R6: manter o texto, as cores (vermelho e azul) e a borda dourada (o documento chama de 'borda prata'); centralizar; papel branco

`horas_p013`. Processada em 26,7 segundos (a análise automática levou mais 0,4 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p013.png" target="_blank"><img src="paineis/13-horas_p013-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p013.png" target="_blank"><img src="paineis/13-horas_p013-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p013.png" target="_blank"><img src="paineis/13-horas_p013-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/horas_p013.jpg" target="_blank"><img src="paineis/13-horas_p013-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p013.png" target="_blank"><img src="paineis/13-horas_p013-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p013.png" target="_blank"><img src="paineis/13-horas_p013-2-anterior-detalhe.jpg" width="239" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p013.png" target="_blank"><img src="paineis/13-horas_p013-3-resultado-detalhe.jpg" width="239" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/horas_p013.jpg" target="_blank"><img src="paineis/13-horas_p013-4-scantailor-detalhe.jpg" width="239" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 14. Livro de Horas - Luís XIV, página 14 do PDF

**O que olhar:** R3: centralizar (margem muito à esquerda)

`horas_p014`. Processada em 25,6 segundos (a análise automática levou mais 0,3 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p014.png" target="_blank"><img src="paineis/14-horas_p014-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p014.png" target="_blank"><img src="paineis/14-horas_p014-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p014.png" target="_blank"><img src="paineis/14-horas_p014-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p014.png" target="_blank"><img src="paineis/14-horas_p014-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p014.png" target="_blank"><img src="paineis/14-horas_p014-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p014.png" target="_blank"><img src="paineis/14-horas_p014-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 15. Livro de Horas - Luís XIV, página 26 do PDF

**O que olhar:** CamScanner: calendário NOVEMBRE (comparar com o Mágico Pro)

`horas_p026`. Processada em 19,0 segundos (a análise automática levou mais 0,3 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p026.png" target="_blank"><img src="paineis/15-horas_p026-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p026.png" target="_blank"><img src="paineis/15-horas_p026-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p026.png" target="_blank"><img src="paineis/15-horas_p026-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. CamScanner Mágico Pro</b><a href="../_referencias/camscanner/horas_p026-28-82-548-860.png" target="_blank"><img src="paineis/15-horas_p026-4-camscanner.jpg" width="115" alt="4. CamScanner Mágico Pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p026.png" target="_blank"><img src="paineis/15-horas_p026-1-original-detalhe.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p026.png" target="_blank"><img src="paineis/15-horas_p026-2-anterior-detalhe.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p026.png" target="_blank"><img src="paineis/15-horas_p026-3-resultado-detalhe.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. CamScanner Mágico Pro</b><a href="../_referencias/camscanner/horas_p026-28-82-548-860.png" target="_blank"><img src="paineis/15-horas_p026-4-camscanner-detalhe.jpg" width="115" alt="4. CamScanner Mágico Pro"></a></td></tr>
</table>

## 16. Livro de Horas - Luís XIV, página 27 do PDF

**O que olhar:** CamScanner: calendário DECEMBRE (comparar com o Mágico Pro)

`horas_p027`. Processada em 18,8 segundos (a análise automática levou mais 0,3 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p027.png" target="_blank"><img src="paineis/16-horas_p027-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p027.png" target="_blank"><img src="paineis/16-horas_p027-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p027.png" target="_blank"><img src="paineis/16-horas_p027-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. CamScanner Mágico Pro</b><a href="../_referencias/camscanner/horas_p027-24-92-552-851.png" target="_blank"><img src="paineis/16-horas_p027-4-camscanner.jpg" width="115" alt="4. CamScanner Mágico Pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p027.png" target="_blank"><img src="paineis/16-horas_p027-1-original-detalhe.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p027.png" target="_blank"><img src="paineis/16-horas_p027-2-anterior-detalhe.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p027.png" target="_blank"><img src="paineis/16-horas_p027-3-resultado-detalhe.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. CamScanner Mágico Pro</b><a href="../_referencias/camscanner/horas_p027-24-92-552-851.png" target="_blank"><img src="paineis/16-horas_p027-4-camscanner-detalhe.jpg" width="115" alt="4. CamScanner Mágico Pro"></a></td></tr>
</table>

## 17. Livro de Horas - Luís XIV, página 47 do PDF

**O que olhar:** R6: gravura e texto, papel branco, tirar margem da esquerda, sem perder qualidade

`horas_p047`. Processada em 24,5 segundos (a análise automática levou mais 0,3 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p047.png" target="_blank"><img src="paineis/17-horas_p047-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p047.png" target="_blank"><img src="paineis/17-horas_p047-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p047.png" target="_blank"><img src="paineis/17-horas_p047-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/horas_p047.jpg" target="_blank"><img src="paineis/17-horas_p047-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/horas_p047.png" target="_blank"><img src="paineis/17-horas_p047-1-original-detalhe.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/horas_p047.png" target="_blank"><img src="paineis/17-horas_p047-2-anterior-detalhe.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/horas_p047.png" target="_blank"><img src="paineis/17-horas_p047-3-resultado-detalhe.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/horas_p047.jpg" target="_blank"><img src="paineis/17-horas_p047-4-scantailor-detalhe.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 18. Na escola de Jesus - Catecismo explicado com imagens, página 7 do PDF

**O que olhar:** R5/R8: endireitar as linhas tortas, mais margem à esquerda, papel branco mantendo a cor das letras e da gravura, tirar o endereço do site

`escola_p007`. Processada em 8,2 segundos (a análise automática levou mais 0,1 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/escola_p007.png" target="_blank"><img src="paineis/18-escola_p007-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/escola_p007.png" target="_blank"><img src="paineis/18-escola_p007-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/escola_p007.png" target="_blank"><img src="paineis/18-escola_p007-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/escola_p007.jpg" target="_blank"><img src="paineis/18-escola_p007-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/escola_p007.png" target="_blank"><img src="paineis/18-escola_p007-1-original-detalhe.jpg" width="487" alt="1. Original"></a></td></tr>
<tr><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/escola_p007.png" target="_blank"><img src="paineis/18-escola_p007-2-anterior-detalhe.jpg" width="487" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Mágico pro</b><a href="resultado/escola_p007.png" target="_blank"><img src="paineis/18-escola_p007-3-resultado-detalhe.jpg" width="487" alt="3. Resultado: Mágico pro"></a></td></tr>
<tr><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/escola_p007.jpg" target="_blank"><img src="paineis/18-escola_p007-4-scantailor-detalhe.jpg" width="487" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 19. Na escola de Jesus - Catecismo explicado com imagens, página 35 do PDF

**O que olhar:** CamScanner: é a página das fotos 'escola_p037' (número impresso 37; pergunta 30, Adão e Eva expulsos do Paraíso)

`escola_p035`. Processada em 8,2 segundos (a análise automática levou mais 0,2 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/escola_p035.png" target="_blank"><img src="paineis/19-escola_p035-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/escola_p035.png" target="_blank"><img src="paineis/19-escola_p035-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/escola_p035.png" target="_blank"><img src="paineis/19-escola_p035-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. CamScanner Mágico Pro</b><a href="../_referencias/camscanner/escola_p037-75-241-501-830.png" target="_blank"><img src="paineis/19-escola_p035-4-camscanner.jpg" width="115" alt="4. CamScanner Mágico Pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/escola_p035.png" target="_blank"><img src="paineis/19-escola_p035-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/escola_p035.png" target="_blank"><img src="paineis/19-escola_p035-2-anterior-detalhe.jpg" width="239" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Mágico pro</b><a href="resultado/escola_p035.png" target="_blank"><img src="paineis/19-escola_p035-3-resultado-detalhe.jpg" width="239" alt="3. Resultado: Mágico pro"></a></td><td><b>4. CamScanner Mágico Pro</b><a href="../_referencias/camscanner/escola_p037-75-241-501-830.png" target="_blank"><img src="paineis/19-escola_p035-4-camscanner-detalhe.jpg" width="239" alt="4. CamScanner Mágico Pro"></a></td></tr>
</table>

## 20. Schön Neues Modell Buch - Johann Siebmacher, página 7 do PDF

**O que olhar:** R7: tamanho final A4 com margem certa para encadernar (página do teste do ScanTailor)

`siebmacher_p007`. Processada em 3,3 segundos (a análise automática levou mais 0,5 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

> **Atenção:** o programa dividiu esta folha em 2 páginas. No Resultado elas aparecem lado a lado, separadas por uma faixa cinza.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p007.png" target="_blank"><img src="paineis/20-siebmacher_p007-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/siebmacher_p007.png" target="_blank"><img src="paineis/20-siebmacher_p007-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/siebmacher_p007.png" target="_blank"><img src="paineis/20-siebmacher_p007-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p007.png" target="_blank"><img src="paineis/20-siebmacher_p007-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/siebmacher_p007.png" target="_blank"><img src="paineis/20-siebmacher_p007-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/siebmacher_p007.png" target="_blank"><img src="paineis/20-siebmacher_p007-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 21. Schön Neues Modell Buch - Johann Siebmacher, página 9 do PDF

**O que olhar:** R7: tamanho final A4 com margem certa para encadernar (página do print do Vamos recapitular, assinada 'J. Sibmacher')

`siebmacher_p009`. Processada em 3,5 segundos (a análise automática levou mais 0,5 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

> **Atenção:** o programa dividiu esta folha em 2 páginas. No Resultado elas aparecem lado a lado, separadas por uma faixa cinza.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p009.png" target="_blank"><img src="paineis/21-siebmacher_p009-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/siebmacher_p009.png" target="_blank"><img src="paineis/21-siebmacher_p009-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/siebmacher_p009.png" target="_blank"><img src="paineis/21-siebmacher_p009-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p009.png" target="_blank"><img src="paineis/21-siebmacher_p009-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/siebmacher_p009.png" target="_blank"><img src="paineis/21-siebmacher_p009-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/siebmacher_p009.png" target="_blank"><img src="paineis/21-siebmacher_p009-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 22. Rhetorica Christiana -  Fray Diego Valadés, página 18 do PDF

**O que olhar:** Teste do ScanTailor de 24/09: página de texto ('Præfatio') com notas na margem; papel branco com o texto 'o mais vivo possível'

`rhetorica_p018`. Processada em 3,8 segundos (a análise automática levou mais 0,5 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p018.png" target="_blank"><img src="paineis/22-rhetorica_p018-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/rhetorica_p018.png" target="_blank"><img src="paineis/22-rhetorica_p018-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/rhetorica_p018.png" target="_blank"><img src="paineis/22-rhetorica_p018-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/rhetorica_p018.png" target="_blank"><img src="paineis/22-rhetorica_p018-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p018.png" target="_blank"><img src="paineis/22-rhetorica_p018-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/rhetorica_p018.png" target="_blank"><img src="paineis/22-rhetorica_p018-2-anterior-detalhe.jpg" width="239" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Mágico pro</b><a href="resultado/rhetorica_p018.png" target="_blank"><img src="paineis/22-rhetorica_p018-3-resultado-detalhe.jpg" width="239" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/rhetorica_p018.png" target="_blank"><img src="paineis/22-rhetorica_p018-4-scantailor-detalhe.jpg" width="239" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 23. Rhetorica Christiana -  Fray Diego Valadés, página 73 do PDF

**O que olhar:** Teste do ScanTailor de 24/09: esquema com chaves e dois ornamentos ('Pars secunda', número impresso 49); na lista de 18/07, 'gravura de traço fino'

`rhetorica_p073`. Processada em 4,9 segundos (a análise automática levou mais 0,4 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p073.png" target="_blank"><img src="paineis/23-rhetorica_p073-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/rhetorica_p073.png" target="_blank"><img src="paineis/23-rhetorica_p073-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/rhetorica_p073.png" target="_blank"><img src="paineis/23-rhetorica_p073-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p073.png" target="_blank"><img src="paineis/23-rhetorica_p073-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/rhetorica_p073.png" target="_blank"><img src="paineis/23-rhetorica_p073-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/rhetorica_p073.png" target="_blank"><img src="paineis/23-rhetorica_p073-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 24. Sobre a Consolação da Filosofia - Severino Boécio, página 3 do PDF

**O que olhar:** R9: folha de rosto com gravura (IHS); o marcador não separa direito letra e gravura (item 2 do TESTE 1)

`boecio_p003`. Processada em 1,8 segundo (a análise automática levou mais 0,0 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/boecio_p003.png" target="_blank"><img src="paineis/24-boecio_p003-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/boecio_p003.png" target="_blank"><img src="paineis/24-boecio_p003-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/boecio_p003.png" target="_blank"><img src="paineis/24-boecio_p003-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/boecio_p003.png" target="_blank"><img src="paineis/24-boecio_p003-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/boecio_p003.png" target="_blank"><img src="paineis/24-boecio_p003-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/boecio_p003.png" target="_blank"><img src="paineis/24-boecio_p003-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 25. Sobre a Consolação da Filosofia - Severino Boécio, página 7 do PDF

**O que olhar:** R9/margens: a margem não aumenta para o lado direito; ver a parte de cima do papel (itens 3 e 4 do TESTE 1)

`boecio_p007`. Processada em 1,8 segundo (a análise automática levou mais 0,1 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/boecio_p007.png" target="_blank"><img src="paineis/25-boecio_p007-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/boecio_p007.png" target="_blank"><img src="paineis/25-boecio_p007-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/boecio_p007.png" target="_blank"><img src="paineis/25-boecio_p007-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/boecio_p007.png" target="_blank"><img src="paineis/25-boecio_p007-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/boecio_p007.png" target="_blank"><img src="paineis/25-boecio_p007-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/boecio_p007.png" target="_blank"><img src="paineis/25-boecio_p007-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 26. Sobre a Consolação da Filosofia - Severino Boécio, página 8 do PDF

**O que olhar:** R9/preto e branco: letras perdendo qualidade no preto e branco (item 5 do TESTE 1); também é a 'Pagina original: 8' do Vamos recapitular (linhas retas e folha branca)

`boecio_p008`. Processada em 2,4 segundos (a análise automática levou mais 0,1 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/boecio_p008.png" target="_blank"><img src="paineis/26-boecio_p008-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/boecio_p008.png" target="_blank"><img src="paineis/26-boecio_p008-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/boecio_p008.png" target="_blank"><img src="paineis/26-boecio_p008-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/boecio_p008.png" target="_blank"><img src="paineis/26-boecio_p008-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/boecio_p008.png" target="_blank"><img src="paineis/26-boecio_p008-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/boecio_p008.png" target="_blank"><img src="paineis/26-boecio_p008-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 27. Sobre a Consolação da Filosofia - Severino Boécio, página 22 do PDF

**O que olhar:** R9: quantos cm vão para cada lado da borda (item 1) e marcador que não seleciona exatamente as letras (item 2 do TESTE 1)

`boecio_p022`. Processada em 2,2 segundos (a análise automática levou mais 0,1 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/boecio_p022.png" target="_blank"><img src="paineis/27-boecio_p022-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/boecio_p022.png" target="_blank"><img src="paineis/27-boecio_p022-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/boecio_p022.png" target="_blank"><img src="paineis/27-boecio_p022-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/boecio_p022.png" target="_blank"><img src="paineis/27-boecio_p022-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/boecio_p022.png" target="_blank"><img src="paineis/27-boecio_p022-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/boecio_p022.png" target="_blank"><img src="paineis/27-boecio_p022-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 28. opusmajustransla01baco, página 11 do PDF

**O que olhar:** Fase 1.1 (tirar o fundo de PDF com camadas): texto corrido, abertura da Introdução. O fundo é só papel, em baixa resolução; todo o texto está na camada de cima. Caso normal.

`opusmajus_p011`. Processada em 3,1 segundos (a análise automática levou mais 0,7 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p011.png" target="_blank"><img src="paineis/28-opusmajus_p011-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/opusmajus_p011.png" target="_blank"><img src="paineis/28-opusmajus_p011-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/opusmajus_p011.png" target="_blank"><img src="paineis/28-opusmajus_p011-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p011.png" target="_blank"><img src="paineis/28-opusmajus_p011-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/opusmajus_p011.png" target="_blank"><img src="paineis/28-opusmajus_p011-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/opusmajus_p011.png" target="_blank"><img src="paineis/28-opusmajus_p011-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 29. opusmajustransla01baco, página 3 do PDF

**O que olhar:** Fase 1.1: folha de rosto com título em vermelho. As letras (vermelhas e pretas) e o emblema estão na camada de cima, com a cor original. O fundo vem em resolução cheia e tem o carimbo da biblioteca, um tique de lápis e 'fantasmas' claros das letras: ao tirar o fundo, o carimbo some e as letras têm de continuar vermelhas.

`opusmajus_p003`. Processada em 3,1 segundos (a análise automática levou mais 1,1 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p003.png" target="_blank"><img src="paineis/29-opusmajus_p003-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/opusmajus_p003.png" target="_blank"><img src="paineis/29-opusmajus_p003-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/opusmajus_p003.png" target="_blank"><img src="paineis/29-opusmajus_p003-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p003.png" target="_blank"><img src="paineis/29-opusmajus_p003-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/opusmajus_p003.png" target="_blank"><img src="paineis/29-opusmajus_p003-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/opusmajus_p003.png" target="_blank"><img src="paineis/29-opusmajus_p003-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 30. opusmajustransla01baco, página 20 do PDF

**O que olhar:** Fase 1.1: foto (estátua de Roger Bacon). Os tons da foto estão só no fundo, em baixa resolução; a camada de cima tem os pontinhos pretos da foto e a legenda. Jogando o fundo fora, a foto vira um pontilhado duro: caso que o programa precisa perceber para não estragar a foto.

`opusmajus_p020`. Processada em 5,0 segundos (a análise automática levou mais 0,6 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p020.png" target="_blank"><img src="paineis/30-opusmajus_p020-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/opusmajus_p020.png" target="_blank"><img src="paineis/30-opusmajus_p020-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/opusmajus_p020.png" target="_blank"><img src="paineis/30-opusmajus_p020-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p020.png" target="_blank"><img src="paineis/30-opusmajus_p020-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/opusmajus_p020.png" target="_blank"><img src="paineis/30-opusmajus_p020-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/opusmajus_p020.png" target="_blank"><img src="paineis/30-opusmajus_p020-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 31. opusmajustransla01baco, página 165 do PDF

**O que olhar:** Fase 1.1: texto com dois diagramas geométricos de traço fino (Fig. 7 e 8). O fundo é só papel; texto e diagramas estão na camada de cima. Caso fácil com figura: os traços finos não podem sumir.

`opusmajus_p165`. Processada em 4,1 segundos (a análise automática levou mais 0,6 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p165.png" target="_blank"><img src="paineis/31-opusmajus_p165-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/opusmajus_p165.png" target="_blank"><img src="paineis/31-opusmajus_p165-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/opusmajus_p165.png" target="_blank"><img src="paineis/31-opusmajus_p165-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p165.png" target="_blank"><img src="paineis/31-opusmajus_p165-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/opusmajus_p165.png" target="_blank"><img src="paineis/31-opusmajus_p165-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/opusmajus_p165.png" target="_blank"><img src="paineis/31-opusmajus_p165-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## 32. opusmajustransla01baco, página 256 do PDF

**O que olhar:** Fase 1.1: tabela grande numa folha dobrável deitada (tamanho de página diferente das outras), com linhas finas e números pequenos. A tabela está na camada de cima; o fundo tem o papel, a marca da dobra e 'fantasmas' claros das linhas.

`opusmajus_p256`. Processada em 6,1 segundos (a análise automática levou mais 0,7 segundo), na rodada de 28/09/2026 às 16:44, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p256.png" target="_blank"><img src="paineis/32-opusmajus_p256-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/opusmajus_p256.png" target="_blank"><img src="paineis/32-opusmajus_p256-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/opusmajus_p256.png" target="_blank"><img src="paineis/32-opusmajus_p256-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p256.png" target="_blank"><img src="paineis/32-opusmajus_p256-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1611/resultado/opusmajus_p256.png" target="_blank"><img src="paineis/32-opusmajus_p256-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/opusmajus_p256.png" target="_blank"><img src="paineis/32-opusmajus_p256-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## Como ler esta página

- Cada página tem duas faixas: **a página inteira** e, logo abaixo, **o detalhe ampliado** do ponto que o gabarito manda olhar. O retângulo rosa na página inteira mostra de onde o detalhe saiu, em cada coluna.
- As colunas vêm sempre nesta ordem: **Original** (a página do gabarito, como foi escaneada), **Rodada anterior** (quando houver), **Resultado**, e as referências que existem para aquela página: **CamScanner Mágico Pro** e **ScanTailor 24/09**.
- **Clique** em qualquer imagem para abrir em tamanho cheio.
- Quadriculado cinza no detalhe é pedaço que não existe naquela imagem (por exemplo, a margem que o programa cortou).
- A foto do CamScanner é uma captura da tela do celular: a página tem só uns 520 pontos de largura. Serve para comparar a cor e o branco do papel, não o detalhe (ampliada, ela fica borrada).

## Como esta página foi feita

- **Comando:** `.venv\Scripts\python.exe conferencia.py fase1 --paginas palatino_p005,palatino_p007,palatino_p009,palatino_p010,palatino_p057,palatino_p066,palatino_p067,marial_p007,graduale_p221,graduale_p222,graduale_p223,horas_p011,horas_p013,horas_p014,horas_p026,horas_p027,horas_p047,escola_p007,escola_p035,siebmacher_p007,siebmacher_p009,rhetorica_p018,rhetorica_p073,boecio_p003,boecio_p007,boecio_p008,boecio_p022,opusmajus_p011,opusmajus_p003,opusmajus_p020,opusmajus_p165,opusmajus_p256 --pasta-depois relatorios\conferir\fase1-2026-09-28-1644 --comparar-com relatorios\conferir\fase1-2026-09-28-1611 --opiniao C:/Users/fotog/AppData/Local/Temp/claude/d--programas/e4642c9c-e61b-4a83-8212-99957ed37365/scratchpad/opiniao-corte.md`
- **Pasta:** `D:\programas\EditorImpressao\relatorios\conferir\fase1-2026-09-28-1745`. Nela, `resultado\` tem o resultado de cada página em tamanho cheio (é o que o `--comparar-com` lê numa conferência futura), `paineis\` tem as imagens reduzidas desta página e `dados.json` tem os números crus. O original fica no gabarito (`gabarito\paginas\`); as referências recortadas, em `relatorios\conferir\_referencias\`.
- **Como o detalhe é achado em cada coluna:** o programa corta as bordas e endireita a página, e as referências têm outro enquadramento; por isso o detalhe não sai da mesma fração de cada imagem, e sim do mesmo ponto do livro, achado alinhando cada imagem com o original pelos pontos em comum (SIFT e RANSAC, do OpenCV). Quando o alinhamento não dá certeza, o bloco da página avisa.
- **Levou** 50,7 segundos no total.
- **Versões:** Python 3.14.3 · PyMuPDF 1.28.0 · OpenCV 5.0.0 · numpy 2.5.1
