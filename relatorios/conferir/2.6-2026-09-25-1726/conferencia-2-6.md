# Conferência do item 2.6: Tamanho final da página em cm/mm (R7)

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

<div class="faixa falta"><p><strong>Falta a opinião do verificador.</strong> As imagens abaixo ainda não foram conferidas por ele: esta página ainda não está pronta para o Samuel.</p></div>

Gerada em 25/09/2026 às 17:26, com 1 página-gabarito do item 2.6. O **depois** é o programa de hoje: cada página foi aberta sozinha (o PDF de uma página do gabarito, com as camadas originais) e passou pelo mesmo caminho do botão "Confirmar e processar", com o que a análise automática do programa decidiu, no filtro **Mágico pro**. O Mágico pro é o filtro mais parecido com o CamScanner, que é o resultado-alvo do plano.

Teste **de olho**: quem decide é o Samuel, olhando.

Em cada página: **a página inteira** e, embaixo, **o detalhe ampliado** do ponto que importa (o retângulo rosa). **Clique** numa imagem para abrir em tamanho cheio. A explicação completa está no fim, em "Como ler esta página".

## 1. Schön Neues Modell Buch - Johann Siebmacher, página 7 do PDF

**O que olhar:** R7: tamanho final A4 com margem certa para encadernar (página do teste do ScanTailor)

`siebmacher_p007`. Processada em 4,2 segundos (a análise automática levou mais 0,5 segundo).

> **Atenção:** esta página ainda está *a confirmar*: o Samuel precisa dizer se ela é a página certa antes de ela virar gabarito fixo. Observação do gabarito: É a página do teste do ScanTailor. Mas o print 'Pagina: 7' do Vamos recapitular é a p. 9 do PDF (as duas são do mesmo tipo: texto com moldura de ornamentos, folha deitada).

> **Atenção:** o programa dividiu esta folha em 2 páginas. No Resultado elas aparecem lado a lado, separadas por uma faixa cinza.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p007.png" target="_blank"><img src="paineis/01-siebmacher_p007-1-original.jpg" width="239" alt="1. Original"></a></td><td><b>2. Resultado: Mágico pro</b><a href="resultado/siebmacher_p007.png" target="_blank"><img src="paineis/01-siebmacher_p007-2-resultado.jpg" width="239" alt="2. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p007.png" target="_blank"><img src="paineis/01-siebmacher_p007-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Resultado: Mágico pro</b><a href="resultado/siebmacher_p007.png" target="_blank"><img src="paineis/01-siebmacher_p007-2-resultado-detalhe.jpg" width="239" alt="2. Resultado: Mágico pro"></a></td></tr>
</table>

## Como ler esta página

- Cada página tem duas faixas: **a página inteira** e, logo abaixo, **o detalhe ampliado** do ponto que o gabarito manda olhar. O retângulo rosa na página inteira mostra de onde o detalhe saiu, em cada coluna.
- As colunas vêm sempre nesta ordem: **Original** (a página do gabarito, como foi escaneada), **Rodada anterior** (quando houver), **Resultado**, e as referências que existem para aquela página: **CamScanner Mágico Pro** e **ScanTailor 24/09**.
- **Clique** em qualquer imagem para abrir em tamanho cheio.
- Quadriculado cinza no detalhe é pedaço que não existe naquela imagem (por exemplo, a margem que o programa cortou).

## Como esta página foi feita

- **Comando:** `.venv\Scripts\python.exe conferencia.py 2.6`
- **Pasta:** `D:\programas\EditorImpressao\relatorios\conferir\2.6-2026-09-25-1726`. Nela, `resultado\` tem o resultado de cada página em tamanho cheio (é o que o `--comparar-com` lê numa conferência futura), `paineis\` tem as imagens reduzidas desta página e `dados.json` tem os números crus. O original fica no gabarito (`gabarito\paginas\`); as referências recortadas, em `relatorios\conferir\_referencias\`.
- **O caminho do programa:** `TarefaAnalise.run` (a análise automática: dividir, ângulo, bordas, cor) e depois `TarefaProcessar.run`, que chama `processar`, o mesmo que o botão "Confirmar e processar" dispara. As caixas da tela "O que fazer" ficaram como o programa traz (dividir, limpar, endireitar, cortar as bordas, achar gravura e letra), a 300 DPI. O resultado é a imagem que o programa gravou no PDF de saída, sem desenhar de novo.
- **Antes das páginas**, o mesmo aquecimento que o programa faz ao ligar: levou 1,7 segundo, fora dos tempos de cada página. Detector de gravura e letra: carregado.
- **Como o detalhe é achado em cada coluna:** o programa corta as bordas e endireita a página, e as referências têm outro enquadramento; por isso o detalhe não sai da mesma fração de cada imagem, e sim do mesmo ponto do livro, achado alinhando cada imagem com o original pelos pontos em comum (SIFT e RANSAC, do OpenCV). Quando o alinhamento não dá certeza, o bloco da página avisa.
- **Levou** 8,0 segundos no total.
- **Versões:** Python 3.14.3 · PyMuPDF 1.28.0 · OpenCV 5.0.0 · numpy 2.5.1
