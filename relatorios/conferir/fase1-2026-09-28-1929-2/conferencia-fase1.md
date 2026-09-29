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

Gerada em 28/09/2026 às 19:29, com 5 páginas-gabarito do item fase1. O **depois** são imagens já prontas, da pasta `relatorios\conferir\fase1-2026-09-28-1854`. São as imagens da rodada de 28/09/2026 às 18:54, do programa no filtro Melhorar, reaproveitadas sem processar de novo. A coluna **Rodada anterior** mostra as imagens de `relatorios\conferir\_antes-conserto-anjo-2026-09-28\melhorar`, para ver o que a mudança de código mudou.

Teste **de olho**: quem decide é o Samuel, olhando.

Em cada página: **a página inteira** e, embaixo, **o detalhe ampliado** do ponto que importa (o retângulo rosa). **Clique** numa imagem para abrir em tamanho cheio. A explicação completa está no fim, em "Como ler esta página".

## Opinião do verificador

> **DEFEITO CONHECIDO: MOLDURA DOURADA E ILUMINURA.** Até a Fase 1 ficar pronta, a **moldura dourada com furinhos** (Horas 26 e 27) e a **iluminura quase toda apagada** (Horas 11) são defeito conhecido do filtro. Vão ser resolvidos nos itens 1.2, 1.4 e 1.5 (decisão do Samuel, 28/09). Estas páginas não estão aqui, e o conserto não mexe nelas.

### O que está sendo conferido

O conserto dos **quadradinhos brancos na gravura** (a roupa do anjo da Escola 35), no filtro **Melhorar**, nas 5 páginas que o Samuel pediu. A regra do resultado da Fase 1 (28/09) é esta: todo o papel branco, inclusive dentro da gravura (o fundo do retrato do Palatino 5); só pintura de verdade mantém a cor (a roupa do anjo, o céu); a foto da estátua do Opus Majus 20 fica intacta.

A coluna **Rodada anterior** é o Melhorar **sem** o conserto. O implementador a fez com o mesmo caminho do programa e o `core/filtros.py` de antes (ver `relatorios/conferir/_antes-conserto-anjo-2026-09-28/LEIA-ME.txt`). A coluna **Resultado** é o programa **com** o conserto (28/09, 18:54). As imagens não foram processadas de novo para esta página. A conferência completa, com as 32 páginas no Mágico pro e todas as ampliações, é a outra página desta mesma entrega.

### Em uma frase

**PRONTO PARA CONFERIR.** No Melhorar, o conserto faz o mesmo que no Mágico pro: a roupa do anjo e o céu voltam sem quadradinhos, o fundo do retrato do Palatino 5 fica branco, e a tabela do Opus 256 fica branca com os números inteiros. As ressalvas são as mesmas: o degrau e a estátua clara do Opus 20, e a roupa do anjo branco-azulada.

### Para o Samuel conferir em poucos minutos

1. **Escola 35:** a roupa do anjo, sem quadradinhos. Olhe a cor: sai branco-azulada, e no original é creme.
2. **Escola 7:** o céu e as nuvens, sem manchas brancas.
3. **Palatino 5:** o fundo do retrato, branco, com a hachura inteira. A barba fica mais contrastada que no original.
4. **Opus Majus 20:** a estátua volta com o sombreado. Olhe o **degrau no alto da foto** e a estátua mais clara que no original.
5. **Opus Majus 256:** a última coluna, com o "16" e o "36" inteiros, e o papel da tabela branco.

### O que eu vi (máquina e olho)

- **Máquina:**
    - as 5 páginas mudam, e as mudanças têm praticamente o mesmo tamanho das do Mágico pro;
    - o Palatino 5 sai **idêntico** nos três filtros;
    - comparado com o Mágico pro depois, o Melhorar difere em menos de 0,7% dos pontos (mais de 8 tons).

- **Olho:** abri as 5 páginas das duas colunas, lado a lado com o original, e ampliei a roupa do anjo, o alto do Opus 20 e a última coluna do Opus 256 (imagem abaixo).

<img src="verificador/10-melhorar-e-preto-e-branco.jpg" width="640" alt="Escola 35, Opus 20 e Opus 256 no Melhorar e no Preto e branco, antes e depois">

Na imagem de cima, da esquerda para a direita:

- **"9-28"** é o antes, sem o conserto;
- **"1854"** é o Melhorar depois;
- **"1855"** é o Preto e branco depois.

Na faixa de cima: Melhorar antes e depois, e Preto e branco antes e depois.

### Ressalvas

1. **Opus 20:**
    - o degrau no alto da foto: a faixa de cima fica fora da caixa do detector;
    - a estátua mais clara que no original;
    - um halo claro em volta da cabeça.

2. **Escola 35:** a roupa sai branco-azulada, e no original é creme. Isso vem do balanço de branco dentro da gravura, que já existia.
3. **Gravura pequena de traço** (figuras do Opus 165, título do Palatino 7, "O" do Boécio 8): o papel continua cinza por dentro, porque o conserto não entra nelas. Não é piora. Está explicado na conferência completa.
4. **O que não conferi:** a prévia da tela, o acervo inteiro e a velocidade (combinado: não rodar).

## 1. Giovambattista Palatino cittadino romano, página 5 do PDF

**O que olhar:** R1: papel branco, letras e gravura (retrato) intactas

`palatino_p005`. Processada em 4,9 segundos (a análise automática levou mais 0,6 segundo), na rodada de 28/09/2026 às 18:54, do programa no filtro Melhorar.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../_antes-conserto-anjo-2026-09-28/melhorar/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Melhorar</b><a href="resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-3-resultado.jpg" width="115" alt="3. Resultado: Melhorar"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p005.jpg" target="_blank"><img src="paineis/01-palatino_p005-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-1-original-detalhe.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../_antes-conserto-anjo-2026-09-28/melhorar/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-2-anterior-detalhe.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Melhorar</b><a href="resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-3-resultado-detalhe.jpg" width="115" alt="3. Resultado: Melhorar"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p005.jpg" target="_blank"><img src="paineis/01-palatino_p005-4-scantailor-detalhe.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 2. Na escola de Jesus - Catecismo explicado com imagens, página 7 do PDF

**O que olhar:** R5/R8: endireitar as linhas tortas, mais margem à esquerda, papel branco mantendo a cor das letras e da gravura, tirar o endereço do site

`escola_p007`. Processada em 11,8 segundos (a análise automática levou mais 0,2 segundo), na rodada de 28/09/2026 às 18:54, do programa no filtro Melhorar.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../_antes-conserto-anjo-2026-09-28/melhorar/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Melhorar</b><a href="resultado/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-3-resultado.jpg" width="115" alt="3. Resultado: Melhorar"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/escola_p007.jpg" target="_blank"><img src="paineis/02-escola_p007-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-1-original-detalhe.jpg" width="487" alt="1. Original"></a></td></tr>
<tr><td><b>2. Rodada anterior</b><a href="../_antes-conserto-anjo-2026-09-28/melhorar/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-2-anterior-detalhe.jpg" width="487" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Melhorar</b><a href="resultado/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-3-resultado-detalhe.jpg" width="487" alt="3. Resultado: Melhorar"></a></td></tr>
<tr><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/escola_p007.jpg" target="_blank"><img src="paineis/02-escola_p007-4-scantailor-detalhe.jpg" width="487" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 3. Na escola de Jesus - Catecismo explicado com imagens, página 35 do PDF

**O que olhar:** CamScanner: é a página das fotos 'escola_p037' (número impresso 37; pergunta 30, Adão e Eva expulsos do Paraíso)

`escola_p035`. Processada em 11,6 segundos (a análise automática levou mais 0,2 segundo), na rodada de 28/09/2026 às 18:54, do programa no filtro Melhorar.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/escola_p035.png" target="_blank"><img src="paineis/03-escola_p035-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../_antes-conserto-anjo-2026-09-28/melhorar/escola_p035.png" target="_blank"><img src="paineis/03-escola_p035-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Melhorar</b><a href="resultado/escola_p035.png" target="_blank"><img src="paineis/03-escola_p035-3-resultado.jpg" width="115" alt="3. Resultado: Melhorar"></a></td><td><b>4. CamScanner Mágico Pro</b><a href="../_referencias/camscanner/escola_p037-75-241-501-830.png" target="_blank"><img src="paineis/03-escola_p035-4-camscanner.jpg" width="115" alt="4. CamScanner Mágico Pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/escola_p035.png" target="_blank"><img src="paineis/03-escola_p035-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../_antes-conserto-anjo-2026-09-28/melhorar/escola_p035.png" target="_blank"><img src="paineis/03-escola_p035-2-anterior-detalhe.jpg" width="239" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Melhorar</b><a href="resultado/escola_p035.png" target="_blank"><img src="paineis/03-escola_p035-3-resultado-detalhe.jpg" width="239" alt="3. Resultado: Melhorar"></a></td><td><b>4. CamScanner Mágico Pro</b><a href="../_referencias/camscanner/escola_p037-75-241-501-830.png" target="_blank"><img src="paineis/03-escola_p035-4-camscanner-detalhe.jpg" width="239" alt="4. CamScanner Mágico Pro"></a></td></tr>
</table>

## 4. opusmajustransla01baco, página 20 do PDF

**O que olhar:** Fase 1.1: foto (estátua de Roger Bacon). Os tons da foto estão só no fundo, em baixa resolução; a camada de cima tem os pontinhos pretos da foto e a legenda. Jogando o fundo fora, a foto vira um pontilhado duro: caso que o programa precisa perceber para não estragar a foto.

`opusmajus_p020`. Processada em 7,1 segundos (a análise automática levou mais 1,0 segundo), na rodada de 28/09/2026 às 18:54, do programa no filtro Melhorar.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p020.png" target="_blank"><img src="paineis/04-opusmajus_p020-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../_antes-conserto-anjo-2026-09-28/melhorar/opusmajus_p020.png" target="_blank"><img src="paineis/04-opusmajus_p020-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Melhorar</b><a href="resultado/opusmajus_p020.png" target="_blank"><img src="paineis/04-opusmajus_p020-3-resultado.jpg" width="157" alt="3. Resultado: Melhorar"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p020.png" target="_blank"><img src="paineis/04-opusmajus_p020-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../_antes-conserto-anjo-2026-09-28/melhorar/opusmajus_p020.png" target="_blank"><img src="paineis/04-opusmajus_p020-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Melhorar</b><a href="resultado/opusmajus_p020.png" target="_blank"><img src="paineis/04-opusmajus_p020-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Melhorar"></a></td></tr>
</table>

## 5. opusmajustransla01baco, página 256 do PDF

**O que olhar:** Fase 1.1: tabela grande numa folha dobrável deitada (tamanho de página diferente das outras), com linhas finas e números pequenos. A tabela está na camada de cima; o fundo tem o papel, a marca da dobra e 'fantasmas' claros das linhas.

`opusmajus_p256`. Processada em 6,5 segundos (a análise automática levou mais 0,9 segundo), na rodada de 28/09/2026 às 18:54, do programa no filtro Melhorar.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p256.png" target="_blank"><img src="paineis/05-opusmajus_p256-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../_antes-conserto-anjo-2026-09-28/melhorar/opusmajus_p256.png" target="_blank"><img src="paineis/05-opusmajus_p256-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Melhorar</b><a href="resultado/opusmajus_p256.png" target="_blank"><img src="paineis/05-opusmajus_p256-3-resultado.jpg" width="157" alt="3. Resultado: Melhorar"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p256.png" target="_blank"><img src="paineis/05-opusmajus_p256-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../_antes-conserto-anjo-2026-09-28/melhorar/opusmajus_p256.png" target="_blank"><img src="paineis/05-opusmajus_p256-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Melhorar</b><a href="resultado/opusmajus_p256.png" target="_blank"><img src="paineis/05-opusmajus_p256-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Melhorar"></a></td></tr>
</table>

## Como ler esta página

- Cada página tem duas faixas: **a página inteira** e, logo abaixo, **o detalhe ampliado** do ponto que o gabarito manda olhar. O retângulo rosa na página inteira mostra de onde o detalhe saiu, em cada coluna.
- As colunas vêm sempre nesta ordem: **Original** (a página do gabarito, como foi escaneada), **Rodada anterior** (quando houver), **Resultado**, e as referências que existem para aquela página: **CamScanner Mágico Pro** e **ScanTailor 24/09**.
- **Clique** em qualquer imagem para abrir em tamanho cheio.
- Quadriculado cinza no detalhe é pedaço que não existe naquela imagem (por exemplo, a margem que o programa cortou).
- A foto do CamScanner é uma captura da tela do celular: a página tem só uns 520 pontos de largura. Serve para comparar a cor e o branco do papel, não o detalhe (ampliada, ela fica borrada).

## Como esta página foi feita

- **Comando:** `.venv\Scripts\python.exe conferencia.py fase1 --paginas palatino_p005,escola_p007,escola_p035,opusmajus_p020,opusmajus_p256 --pasta-depois relatorios\conferir\fase1-2026-09-28-1854 --comparar-com relatorios\conferir\_antes-conserto-anjo-2026-09-28\melhorar --opiniao C:/Users/fotog/AppData/Local/Temp/claude/d--programas/e4642c9c-e61b-4a83-8212-99957ed37365/scratchpad/opiniao-anjo-melhorar.md`
- **Pasta:** `D:\programas\EditorImpressao\relatorios\conferir\fase1-2026-09-28-1929-2`. Nela, `resultado\` tem o resultado de cada página em tamanho cheio (é o que o `--comparar-com` lê numa conferência futura), `paineis\` tem as imagens reduzidas desta página e `dados.json` tem os números crus. O original fica no gabarito (`gabarito\paginas\`); as referências recortadas, em `relatorios\conferir\_referencias\`.
- **Como o detalhe é achado em cada coluna:** o programa corta as bordas e endireita a página, e as referências têm outro enquadramento; por isso o detalhe não sai da mesma fração de cada imagem, e sim do mesmo ponto do livro, achado alinhando cada imagem com o original pelos pontos em comum (SIFT e RANSAC, do OpenCV). Quando o alinhamento não dá certeza, o bloco da página avisa.
- **Levou** 15,0 segundos no total.
- **Versões:** Python 3.14.3 · PyMuPDF 1.28.0 · OpenCV 5.0.0 · numpy 2.5.1
