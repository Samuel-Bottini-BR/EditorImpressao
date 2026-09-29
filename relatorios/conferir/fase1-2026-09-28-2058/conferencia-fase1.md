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

Gerada em 28/09/2026 às 20:58, com 1 página-gabarito do item fase1. O **depois** são imagens já prontas, da pasta `relatorios\conferir\fase1-2026-09-28-1927`. São as imagens da rodada de 28/09/2026 às 19:27, do programa no filtro Mágico pro, reaproveitadas sem processar de novo. A coluna **Rodada anterior** mostra as imagens de `relatorios\conferir\fase1-2026-09-28-1844` (rodada de 28/09/2026 às 18:44, do programa no filtro Mágico pro), para ver o que a mudança de código mudou.

Teste **de olho**: quem decide é o Samuel, olhando.

Em cada página: **a página inteira** e, embaixo, **o detalhe ampliado** do ponto que importa (o retângulo rosa). **Clique** numa imagem para abrir em tamanho cheio. A explicação completa está no fim, em "Como ler esta página".

## Opinião do verificador

**Veredito: PRONTO PARA CONFERIR.** A faixa escura que o conserto anterior do corte tinha trazido para a borda direita do Marial 7 sumiu. A borda direita voltou a ficar como era antes de todos os consertos do corte, e nenhuma outra página do gabarito mudou.

> **AVISO DE DEFEITO CONHECIDO (decisão do Samuel, 28/09):** a **moldura dourada** (Horas 26 e 27) e a **iluminura** (Horas 11) ainda saem estragadas pelo Mágico pro. É defeito conhecido, que vai ser resolvido nos itens 1.2, 1.4 e 1.5. Não é deste conserto e não deve pesar na decisão sobre ele.

### Máquina ou olho

- **Máquina:** os 778 testes passam, sem nenhuma falha. Das 32 páginas do gabarito, só o Marial 7 mudou entre a rodada das 18:44 e a das 19:27; as outras 31 saíram idênticas, ponto por ponto.
- **Máquina (a faixa):** contei os pontos escuros nos últimos 50 pontos da direita de cada linha. Antes, a faixa escura aparecia em 96% da altura, com 1 a 2,5 mm de largura. Depois, aparece em 2% da altura (só o canto de baixo), igual à rodada das 16:11, que é de antes dos consertos do corte.
- **Olho:** abri a página inteira antes e depois, e a borda direita em três alturas (alto, meio e pé), em tamanho real e ampliada 4 vezes. Também comparei o pé com a rodada das 16:11.

### O que vi

- **Marial 7, borda direita:** antes, uma faixa cinza-escura do fundo do scanner descia pela borda direita quase inteira. Depois, ela não existe mais: no lugar fica a beirada bege da folha, que é o próprio papel.
- **Marial 7, texto:** o texto da margem direita ("Ma-", "Frey", "Prouin", "encon-"), o reclamo "luqua-" e o "§2" do pé estão inteiros antes e depois.
- A página ficou 25 pontos (2 mm) mais estreita, que é exatamente a faixa que saiu.

### Ressalvas

1. **Ainda sobra escuro, mas ele já existia antes de todos os consertos do corte.** Sobram três coisas: um fio escuro de 0,3 a 0,6 mm colado na borda direita, no meio da altura; o canto de baixo à direita (a beirada da folha em "L"); e a faixa escura no pé da página, de 1 a 3 mm, mais grossa à esquerda. As três estão iguais na rodada das 16:11. Não são piora deste conserto, mas também não são papel branco; devem sair com o corte do ScanTailor (itens 2.13 e 2.14).
2. O conserto só impede que a **folga do giro** entre no escuro. Ele olha a média de cada coluna nova: se o escuro ocupar só um pedaço da coluna (um canto, por exemplo), a média pode não cair abaixo do limite, e o escuro entra mesmo assim. No gabarito, só o Marial 7 tinha o caso, então não houve outra página para testar isso.
3. No canto de baixo à direita, o giro pode voltar a levar uma lasquinha da beirada da folha, como antes do conserto do corte (o implementador avisou isso no código). Não vi nenhuma lasca com conteúdo.
4. O teste de velocidade oficial não foi rodado, a pedido da gerente.

### Para o Samuel conferir em 10 minutos

1. Nesta página, no Marial 7, compare a coluna "Rodada anterior" com a coluna "Resultado": a borda direita não pode ter mais a faixa escura (2 min).
2. Veja as ampliações logo abaixo: m2 e m3 mostram a borda direita, e m4 mostra o pé, que já era assim antes (2 min).
3. No programa pelo atalho "(desenvolvimento)", abra o Marial de sermoens, vá à página 7 no filtro Mágico pro e olhe a borda direita na prévia e no PDF gerado (5 min).

### Ampliações do ponto do conserto

**m1.** A página inteira, antes (18:44) e depois (19:27): a faixa escura da borda direita sumiu.

![Marial 7 inteira](ampliacoes/m1-pagina-inteira.jpg)

**m2.** Os 160 pontos da direita, em tamanho real, no alto, no meio e no pé.

![Marial 7 borda direita](ampliacoes/m2-borda-direita-3-alturas.jpg)

**m3.** A mesma borda ampliada 4 vezes, em três alturas. Antes é cinza-escuro; depois é a beirada bege da folha, com um fio escuro de poucos pontos no meio da altura.

![Marial 7 borda direita 4x](ampliacoes/m3-borda-direita-4x.jpg)

**m4.** O pé da página na rodada das 16:11 (antes dos consertos do corte) e depois: a faixa escura do pé já existia e continua igual.

![Marial 7 pé](ampliacoes/m4-pe-antes-dos-consertos-e-depois.jpg)

## 1. Marial de sermoens - Frei Balthasar Paez. (1), página 7 do PDF

**O que olhar:** R2 / item 6.1: letras do verso aparecendo através do papel. (No Vamos recapitular, o 'Livro 4' também cita linhas tortas, centralizar, papel branco, mancha amarronzada embaixo à direita e margens.)

`marial_p007`. Processada em 17,1 segundos (a análise automática levou mais 0,4 segundo), na rodada de 28/09/2026 às 19:27, do programa no filtro Mágico pro.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/marial_p007.png" target="_blank"><img src="paineis/01-marial_p007-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1844/resultado/marial_p007.png" target="_blank"><img src="paineis/01-marial_p007-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: Mágico pro</b><a href="resultado/marial_p007.png" target="_blank"><img src="paineis/01-marial_p007-3-resultado.jpg" width="157" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/marial_p007.png" target="_blank"><img src="paineis/01-marial_p007-1-original-detalhe.jpg" width="487" alt="1. Original"></a></td></tr>
<tr><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-1844/resultado/marial_p007.png" target="_blank"><img src="paineis/01-marial_p007-2-anterior-detalhe.jpg" width="487" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: Mágico pro</b><a href="resultado/marial_p007.png" target="_blank"><img src="paineis/01-marial_p007-3-resultado-detalhe.jpg" width="487" alt="3. Resultado: Mágico pro"></a></td></tr>
</table>

## Como ler esta página

- Cada página tem duas faixas: **a página inteira** e, logo abaixo, **o detalhe ampliado** do ponto que o gabarito manda olhar. O retângulo rosa na página inteira mostra de onde o detalhe saiu, em cada coluna.
- As colunas vêm sempre nesta ordem: **Original** (a página do gabarito, como foi escaneada), **Rodada anterior** (quando houver), **Resultado**, e as referências que existem para aquela página: **CamScanner Mágico Pro** e **ScanTailor 24/09**.
- **Clique** em qualquer imagem para abrir em tamanho cheio.
- Quadriculado cinza no detalhe é pedaço que não existe naquela imagem (por exemplo, a margem que o programa cortou).

## Como esta página foi feita

- **Comando:** `.venv\Scripts\python.exe conferencia.py fase1 --paginas marial_p007 --pasta-depois relatorios/conferir/fase1-2026-09-28-1927 --comparar-com relatorios/conferir/fase1-2026-09-28-1844 --opiniao C:/Users/fotog/AppData/Local/Temp/claude/d--programas/e4642c9c-e61b-4a83-8212-99957ed37365/scratchpad/opiniao-1-marial7.md`
- **Pasta:** `D:\programas\EditorImpressao\relatorios\conferir\fase1-2026-09-28-2058`. Nela, `resultado\` tem o resultado de cada página em tamanho cheio (é o que o `--comparar-com` lê numa conferência futura), `paineis\` tem as imagens reduzidas desta página e `dados.json` tem os números crus. O original fica no gabarito (`gabarito\paginas\`); as referências recortadas, em `relatorios\conferir\_referencias\`.
- **Como o detalhe é achado em cada coluna:** o programa corta as bordas e endireita a página, e as referências têm outro enquadramento; por isso o detalhe não sai da mesma fração de cada imagem, e sim do mesmo ponto do livro, achado alinhando cada imagem com o original pelos pontos em comum (SIFT e RANSAC, do OpenCV). Quando o alinhamento não dá certeza, o bloco da página avisa.
- **Levou** 3,2 segundos no total.
- **Versões:** Python 3.14.3 · PyMuPDF 1.28.0 · OpenCV 5.0.0 · numpy 2.5.1
