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

Gerada em 28/09/2026 às 20:58, com 3 páginas-gabarito do item fase1. O **depois** são imagens já prontas, da pasta `relatorios\conferir\fase1-2026-09-28-2014`. São as imagens da rodada de 28/09/2026 às 20:14, do programa no filtro Mágico pro, reaproveitadas sem processar de novo. A coluna **Rodada anterior** mostra as imagens de `relatorios\conferir\fase1-2026-09-28-1941` (rodada de 28/09/2026 às 19:41, do programa no filtro Mágico pro), para ver o que a mudança de código mudou.

Teste **de olho**: quem decide é o Samuel, olhando.

Em cada página: **a página inteira** e, embaixo, **o detalhe ampliado** do ponto que importa (o retângulo rosa). **Clique** numa imagem para abrir em tamanho cheio. A explicação completa está no fim, em "Como ler esta página".

## Opinião do verificador

> **Abra o .html, não o .pdf.** No .pdf desta página, algumas ampliações saem espremidas (um defeito do gerador de PDF dos relatórios, anotado para a Lista de bugs). No .html, todas saem no tamanho certo.

**Veredito: PRONTO PARA CONFERIR, com uma ressalva grave de velocidade.** A prévia da tela agora mostra exatamente o corte que vai para o PDF, em todas as páginas que conferi. O preço é que a **primeira** prévia de cada página ficou mais lenta, e o teste de velocidade oficial ainda precisa ser rodado antes de aprovar (regra 6 do plano: nenhum item pode deixar o programa mais lento).

> **AVISO DE DEFEITO CONHECIDO (decisão do Samuel, 28/09):** a **moldura dourada** (Horas 26 e 27) e a **iluminura** (Horas 11) ainda saem estragadas pelo Mágico pro. É defeito conhecido, que vai ser resolvido nos itens 1.2, 1.4 e 1.5. Não é deste conserto e não deve pesar na decisão sobre ele.

**As imagens desta página mostram o PDF, e o PDF não mudou.** As colunas "Rodada anterior" (19:41) e "Resultado" (20:14) são idênticas. O que mudou foi a **prévia da tela**; ela está nas ampliações v1 a v3, lá embaixo.

### Máquina ou olho

- **Máquina:** os 778 testes passam, incluindo os 4 casos novos de `test_corte_previa_igual_pdf.py`. As 32 páginas da rodada das 20:14 são idênticas, ponto por ponto, às da rodada das 19:41.
- **Máquina (prévia × PDF):** chamei a mesma função que a tela chama para a prévia (`renderizar_pagina`, a 110 DPI) e o `processar` (sem filtro, como o teste), cada um calculando sozinho, em 10 páginas do gabarito (11 páginas, porque o Siebmacher 9 se divide em duas).
  - Em todas, o corte da prévia é o mesmo do PDF.
  - O tamanho da prévia bate com o do PDF desenhado a 110 DPI, com no máximo 1 ponto de diferença de arredondamento.
  - Também medi como a prévia cortava **antes** do conserto (tabela abaixo).
- **Olho:** abri a prévia antiga, a prévia nova e o PDF lado a lado no Palatino 5, na Escola 7 e no Siebmacher 9: a prévia nova e o PDF enquadram igual. No Palatino 5, o "L" de "LIBRO" fica a 0,4 mm da beirada esquerda. É justo, mas inteiro, e é o mesmo corte do PDF que já estava em conferência.

| Página | Prévia de antes × PDF (maior diferença do corte) | Prévia de agora × PDF |
|---|---|---|
| Palatino 5 | 7,4% (a prévia mostrava mais margem à esquerda do que o PDF entregava) | igual |
| Escola 7 | 6,75% (a prévia cortava o alto e o pé que o PDF mantinha) | igual |
| Siebmacher 9 (esquerda / direita) | 0,9% / 1,15% | igual |
| Graduale 222 | 0,36% | igual |
| Opus Majus 20 | 0,15% (e o ângulo 0,3° na prévia contra 0,4° no PDF) | igual |
| Palatino 9, Palatino 66, Marial 7, Horas 26, Escola 35 | de 0 a 0,2% | igual |

### O tempo da primeira prévia (só de curiosidade, não é o teste oficial)

A primeira prévia de cada página foi medida nos dois jeitos, no mesmo PC e na mesma hora: o de antes (corte calculado na imagem de 110 DPI) e o de agora (a folha é desenhada a 300 DPI, o corte é calculado e guardado, e a imagem é reduzida para a prévia). Os números são a mediana de 2 ou 3 medidas.

| Página | Filtro | Antes | Agora | A mais |
|---|---|---|---|---|
| Palatino 5 | Original | 1,57 s | 1,69 s | +0,12 s |
| Escola 7 | Original | 1,09 s | 1,26 s | +0,17 s |
| Graduale 222 | Original | 1,17 s | 1,78 s | +0,61 s |
| Horas 26 | Original | 1,39 s | 1,68 s | +0,29 s |
| Siebmacher 9 | Original | 1,35 s | 1,65 s | +0,30 s |
| Palatino 5 | Mágico pro | 2,49 s | 3,53 s | +1,04 s |
| Escola 7 | Mágico pro | 3,05 s | 3,22 s | +0,18 s |
| Graduale 222 | Mágico pro | 2,68 s | 3,44 s | +0,76 s |

Voltar a uma página já vista não ficou mais lento: o corte fica guardado.

### Ressalvas

1. **Velocidade (grave, regra 6):** a primeira prévia de cada página ficou de 0,1 a 1,0 s mais lenta (de 6% a 52% a mais). O pré-carregamento das páginas vizinhas paga o mesmo custo. **O teste de velocidade oficial (`teste_velocidade.py`) não foi rodado**, a pedido da gerente. Ele precisa ser rodado antes de aprovar, porque a medida "trocar de página" deve piorar.
2. **Memória:** na primeira vez de cada página, a prévia segura a folha a 300 DPI (até uns 120 MB numa folha grande) em cada um dos 2 fios de prévia, então o pico de memória da prévia sobe. Não medi. Esse pico não cresce com o tamanho do livro.
3. **A janela real não foi pilotada.** Conferi pela função que a tela chama (`ui/tarefas.py` chama `renderizar_pagina`).
4. **Os cartões de filtro e a tela ampliada** usam o corte guardado. Se forem desenhados antes de a prévia daquela página terminar, calculam o corte na própria imagem pequena (70 DPI nos cartões) e podem mostrar outro corte por um instante. Deduzido lendo o código; não testei.
5. O corte guardado vale só enquanto o programa está aberto: ao reabrir, ele é calculado de novo, com o mesmo resultado. Nada muda no arquivo do projeto.
6. Pequeno, deduzido lendo o código: se o arquivo do livro for movido com o programa aberto, cada prévia passa a desenhar a folha a 300 DPI sem guardar o corte. Fica lento, mas não quebra.

### Para o Samuel conferir em 10 minutos

1. Veja as ampliações v1 e v2 abaixo: a prévia antiga, a nova e o PDF lado a lado (2 min).
2. No programa pelo atalho "(desenvolvimento)", abra o Palatino (página 5 do PDF) e a Escola de Jesus (página 7), olhe a prévia, gere o PDF dessas páginas e confira se a margem é a mesma (5 min).
3. Passe por umas 10 páginas novas, uma depois da outra, e diga se a espera ficou incômoda (3 min).

### Ampliações: a prévia de antes, a de agora e o PDF

**v1.** Palatino 5: a prévia de antes mostrava mais margem à esquerda do que o PDF entregava; a de agora é igual ao PDF.

![Palatino 5 prévias e PDF](ampliacoes/v1-palatino5-previas-e-pdf.jpg)

**v2.** Escola 7: a prévia de antes cortava o alto e o pé que o PDF mantinha; a de agora é igual ao PDF.

![Escola 7 prévias e PDF](ampliacoes/v2-escola7-previas-e-pdf.jpg)

**v3.** Siebmacher 9, página da esquerda: diferença pequena antes (1%), nenhuma agora.

![Siebmacher 9 prévias e PDF](ampliacoes/v3-siebmacher9-previas-e-pdf.jpg)

## 1. Giovambattista Palatino cittadino romano, página 5 do PDF

**O que olhar:** R1: papel branco, letras e gravura (retrato) intactas

`palatino_p005`. Processada em 7,2 segundos (a análise automática levou mais 2,8 segundos), na rodada de 28/09/2026 às 20:14, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1941/resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p005.jpg" target="_blank"><img src="paineis/01-palatino_p005-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-1-original-detalhe.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1941/resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-2-anterior-detalhe.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-3-resultado-detalhe.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p005.jpg" target="_blank"><img src="paineis/01-palatino_p005-4-scantailor-detalhe.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 2. Na escola de Jesus - Catecismo explicado com imagens, página 7 do PDF

**O que olhar:** R5/R8: endireitar as linhas tortas, mais margem à esquerda, papel branco mantendo a cor das letras e da gravura, tirar o endereço do site

`escola_p007`. Processada em 13,7 segundos (a análise automática levou mais 0,5 segundo), na rodada de 28/09/2026 às 20:14, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1941/resultado/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-3-resultado.jpg" width="115" alt="3. Resultado: Mágico pro"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/escola_p007.jpg" target="_blank"><img src="paineis/02-escola_p007-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-1-original-detalhe.jpg" width="487" alt="1. Original"></a></td></tr>
<tr><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1941/resultado/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-2-anterior-detalhe.jpg" width="487" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Mágico pro</b><a href="resultado/escola_p007.png" target="_blank"><img src="paineis/02-escola_p007-3-resultado-detalhe.jpg" width="487" alt="3. Resultado: Mágico pro"></a></td></tr>
<tr><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/escola_p007.jpg" target="_blank"><img src="paineis/02-escola_p007-4-scantailor-detalhe.jpg" width="487" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 3. Schön Neues Modell Buch - Johann Siebmacher, página 9 do PDF

**O que olhar:** R7: tamanho final A4 com margem certa para encadernar (página do print do Vamos recapitular, assinada 'J. Sibmacher')

`siebmacher_p009`. Processada em 4,6 segundos (a análise automática levou mais 0,9 segundo), na rodada de 28/09/2026 às 20:14, do programa no filtro Mágico pro.

> **Atenção:** o programa dividiu esta folha em 2 páginas. No Resultado elas aparecem lado a lado, separadas por uma faixa cinza.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p009.png" target="_blank"><img src="paineis/03-siebmacher_p009-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1941/resultado/siebmacher_p009.png" target="_blank"><img src="paineis/03-siebmacher_p009-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/siebmacher_p009.png" target="_blank"><img src="paineis/03-siebmacher_p009-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p009.png" target="_blank"><img src="paineis/03-siebmacher_p009-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1941/resultado/siebmacher_p009.png" target="_blank"><img src="paineis/03-siebmacher_p009-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/siebmacher_p009.png" target="_blank"><img src="paineis/03-siebmacher_p009-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## Como ler esta página

- Cada página tem duas faixas: **a página inteira** e, logo abaixo, **o detalhe ampliado** do ponto que o gabarito manda olhar. O retângulo rosa na página inteira mostra de onde o detalhe saiu, em cada coluna.
- As colunas vêm sempre nesta ordem: **Original** (a página do gabarito, como foi escaneada), **Rodada anterior** (quando houver), **Resultado**, e as referências que existem para aquela página: **CamScanner Mágico Pro** e **ScanTailor 24/09**.
- **Clique** em qualquer imagem para abrir em tamanho cheio.
- Quadriculado cinza no detalhe é pedaço que não existe naquela imagem (por exemplo, a margem que o programa cortou).

## Como esta página foi feita

- **Comando:** `.venv\Scripts\python.exe conferencia.py fase1 --paginas palatino_p005,escola_p007,siebmacher_p009 --pasta-depois relatorios/conferir/fase1-2026-09-28-2014 --comparar-com relatorios/conferir/fase1-2026-09-28-1941 --opiniao C:/Users/fotog/AppData/Local/Temp/claude/d--programas/e4642c9c-e61b-4a83-8212-99957ed37365/scratchpad/opiniao-3-previa-pdf.md`
- **Pasta:** `D:\programas\EditorImpressao\relatorios\conferir\fase1-2026-09-28-2058-3`. Nela, `resultado\` tem o resultado de cada página em tamanho cheio (é o que o `--comparar-com` lê numa conferência futura), `paineis\` tem as imagens reduzidas desta página e `dados.json` tem os números crus. O original fica no gabarito (`gabarito\paginas\`); as referências recortadas, em `relatorios\conferir\_referencias\`.
- **Como o detalhe é achado em cada coluna:** o programa corta as bordas e endireita a página, e as referências têm outro enquadramento; por isso o detalhe não sai da mesma fração de cada imagem, e sim do mesmo ponto do livro, achado alinhando cada imagem com o original pelos pontos em comum (SIFT e RANSAC, do OpenCV). Quando o alinhamento não dá certeza, o bloco da página avisa.
- **Levou** 14,0 segundos no total.
- **Versões:** Python 3.14.3 · PyMuPDF 1.28.0 · OpenCV 5.0.0 · numpy 2.5.1
