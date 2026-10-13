// A caixa da pagina e a caixa do conteudo: o PageFinder e o ContentBoxFinder do
// ScanTailor Advanced (a etapa "Select Content"), chamados do Python.
//
// Copyright (C) 2026  Editor de Impressao (so esta ligacao; o trecho marcado
//   "COPIADO SEM MUDANCA" e do ScanTailor Advanced, Joseph Artsimovich e 4lex4)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// O QUE FAZ (itens 2.13 e 2.5 da Fase 2; decisoes G7 (a) e G8 (a) do Samuel,
// 05/10/2026: as duas como opcao, DESLIGADAS de fabrica)
//   Recebe a pagina (cinza ou colorida) e o DPI, e devolve as duas caixas que
//   o ScanTailor acharia, com o codigo dele SEM MUDANCA:
//     - a caixa da PAGINA: select_content::PageFinder::findPageBox
//       (../src/core/filters/select_content/PageFinder.cpp): a folha sem a
//       faixa preta do scanner (item 2.13);
//     - a caixa do CONTEUDO: select_content::ContentBoxFinder::findContentBox
//       (../src/core/filters/select_content/ContentBoxFinder.cpp), procurada
//       DENTRO da caixa da pagina (item 2.5);
//     - o tamanho do conteudo em mm: select_content::PhysSizeCalc (o numero
//       que o ScanTailor guarda e que as margens, item 2.4, usam).
//   Aqui so ha a montagem do que o select_content::Task do ScanTailor faz numa
//   pagina que ainda nao tem caixa nenhuma (src/core/filters/select_content/
//   Task.cpp, linhas 72-152; o original esta em ../referencia/select_content/
//   Task.cpp, NAO compilado), na mesma ordem:
//     1. o FilterData da pagina (../src/core/FilterData.cpp, sem mudanca): o
//        cinza e a geometria. Sem giro nem endireitar por dentro: quem gira e
//        endireita e o programa, ANTES de chamar (como no ScanTailor, em que o
//        Select Content vem depois do Deskew). Por isso as caixas saem direto
//        em pontos da imagem recebida.
//     2. "claro no escuro" e o limiar: o que o deskew::Task::updateFilterData
//        deixa pronto para as etapas seguintes (../referencia/deskew/Task.cpp,
//        linhas 273-290): BlackOnWhiteEstimator (ligado de fabrica no
//        ScanTailor) e o limiar Otsu dentro da pagina. Os dois achadores so
//        usam o "claro no escuro" (leem data.grayImageBlackOnWhite()).
//     3. a caixa da pagina (Task.cpp, linhas 95-109): automatica = PageFinder;
//        desligada = a folha inteira; se sair fora da folha, a folha inteira.
//     4. a caixa do conteudo (Task.cpp, linhas 129-147): automatica =
//        ContentBoxFinder dentro da caixa da pagina; desligada = a propria
//        caixa da pagina; e o corte "contentRect &= pageRect" (linhas 142-144).
//   O modo "a mao" do ScanTailor nao vem: no programa, a mao e o recorte que a
//   pessoa ja desenha na aba Bordas.
//
// O QUE NAO E OBVIO NO CODIGO ORIGINAL (nao consertamos nada: a regra e o
// codigo original)
//   - ContentBoxFinder.cpp, linhas 102-103: o retangulo da pagina a 150 DPI e
//     montado com (esquerda, cima, DIREITA, BAIXO) onde o Qt espera (esquerda,
//     cima, largura, altura). Quando a caixa da pagina nao comeca no canto, a
//     procura do conteudo passa um pouco da pagina a direita e embaixo. O
//     corte do passo 4 ("&= pageRect") devolve a caixa para dentro. Por isso
//     devolvemos as DUAS: `conteudo` (o que o ScanTailor guarda) e
//     `conteudoBruto` (o que o achador devolveu, antes do corte).
//   - PageFinder.cpp calcula CINCO preto e branco (linhas 58-62) e, sem
//     tamanho esperado, usa so um (o Sauvola, linha 76). E tempo jogado fora.
//   - Os dois achadores levam a pagina a 150 DPI pelo DPI informado: com DPI
//     baixo demais (72 num PDF que nao diz a resolucao de verdade) a pagina e
//     AMPLIADA, o resultado muda e a conta fica varias vezes mais lenta.
//
// O QUE E ARRISCADO
//   - O DPI (ver acima): e o que mais muda o resultado.
//   - `claroNoEscuro`: 0 (tratar como preto no branco) e o que as conferencias
//     de 12/10 mostraram ao Samuel; -1 (detectar) e o de fabrica do ScanTailor.
//   - A ordem dos numeros das caixas: x0, y0, x1, y1 (esquerda, cima, direita,
//     baixo), em pontos; x1 e y1 ja sao a beirada de fora (largura = x1 - x0).
//   - Trocar o trecho copiado: o teste tests/test_caixas_scantailor.py confere
//     que ele e igual as linhas 48-51 do original.

#include <BinaryImage.h>
#include <BinaryThreshold.h>
#include <Dpi.h>
#include <Dpm.h>
#include <GrayImage.h>
#include <Grayscale.h>
#include <PolygonRasterizer.h>

#include <QImage>
#include <QRectF>
#include <QSizeF>
#include <chrono>

#include "BlackOnWhiteEstimator.h"
#include "FilterData.h"
#include "ImageSettings.h"
#include "ImageTransformation.h"
#include "NullTaskStatus.h"
#include "comum.h"
#include "filters/select_content/ContentBoxFinder.h"
#include "filters/select_content/PageFinder.h"
#include "filters/select_content/PhysSizeCalc.h"
#include "st_ferramentas.h"

using imageproc::BinaryImage;
using imageproc::BinaryThreshold;
using imageproc::GrayImage;
using imageproc::GrayscaleHistogram;
using imageproc::PolygonRasterizer;

// ---- COPIADO SEM MUDANCA de src/core/ImageSettings.cpp (linhas 48-51) -------
// Os dois construtores de ImageSettings::PageParams que o FilterData usa (o
// limiar e o "claro no escuro" da pagina). ImageSettings.cpp inteiro puxaria o
// projeto e as miniaturas do ScanTailor; o original esta em
// ../referencia/ImageSettings.cpp e o teste confere que este trecho e igual.
ImageSettings::PageParams::PageParams() : m_bwThreshold(0), m_blackOnWhite(true) {}

ImageSettings::PageParams::PageParams(const BinaryThreshold& bwThreshold, bool blackOnWhite)
    : m_bwThreshold(bwThreshold), m_blackOnWhite(blackOnWhite) {}
// ---- FIM DO TRECHO COPIADO --------------------------------------------------

namespace {

using Relogio = std::chrono::steady_clock;

double milissegundosDesde(const Relogio::time_point& inicio) {
  return std::chrono::duration<double, std::milli>(Relogio::now() - inicio).count();
}

void gravarCaixa(double* destino, const QRectF& r) {
  destino[0] = r.left();
  destino[1] = r.top();
  destino[2] = r.right();
  destino[3] = r.bottom();
}

void zerarCaixa(double* destino) {
  destino[0] = destino[1] = destino[2] = destino[3] = 0.0;
}

}  // namespace

extern "C" {

ST_FERRAMENTAS_API int st_ferramentas_caixas(const unsigned char* pixels,
                                             int largura,
                                             int altura,
                                             int passo,
                                             int canais,
                                             int dpiX,
                                             int dpiY,
                                             int modoPagina,
                                             int ajustarCantos,
                                             double larguraEsperadaMm,
                                             double alturaEsperadaMm,
                                             double tolerancia,
                                             int modoConteudo,
                                             int claroNoEscuro,
                                             double* pagina,
                                             double* conteudo,
                                             double* conteudoBruto,
                                             double* tamanhoConteudoMm,
                                             int* achouConteudo,
                                             int* pretoNoBranco,
                                             double* milissegundos,
                                             char* erro,
                                             int tamanhoErro) {
  return st_ferramentas::protegido(erro, tamanhoErro, [&]() -> int {
    if (!pixels || !pagina || !conteudo || !conteudoBruto || !tamanhoConteudoMm || !achouConteudo || !pretoNoBranco
        || !milissegundos || largura <= 0 || altura <= 0 || (canais != 1 && canais != 3) || passo < largura * canais
        || dpiX <= 0 || dpiY <= 0 || (modoPagina != 0 && modoPagina != 1) || (modoConteudo != 0 && modoConteudo != 1)
        || claroNoEscuro < -1 || claroNoEscuro > 1 || !(larguraEsperadaMm >= 0.0) || !(alturaEsperadaMm >= 0.0)
        || !(tolerancia >= 0.0) || !(tolerancia <= 1.0)) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_FERRAMENTAS_ERRO_PARAMETRO;
    }
    NullTaskStatus status;
    Relogio::time_point inicio = Relogio::now();

    // A pagina como o ScanTailor a abriria do disco (os pontos so sao lidos) e
    // o DPI gravado nela. 3 canais = a ordem do OpenCV (azul, verde, vermelho).
    QImage imagem(pixels, largura, altura, passo, canais == 1 ? QImage::Format_Grayscale8 : QImage::Format_BGR888);
    const Dpm dpm{Dpi(dpiX, dpiY)};
    imagem.setDotsPerMeterX(dpm.horizontal());
    imagem.setDotsPerMeterY(dpm.vertical());

    // 1. FilterData (FilterData.cpp, linha 13): o cinza e a geometria.
    FilterData data(imagem);

    // 2. deskew::Task::updateFilterData (deskew/Task.cpp, linhas 273-290).
    {
      const GrayImage& cinza = data.grayImage();
      BinaryImage mascara(cinza.size(), imageproc::BLACK);
      PolygonRasterizer::fillExcept(mascara, imageproc::WHITE, data.xform().resultingPreCropArea(), Qt::WindingFill);
      bool pretoSobreBranco = true;
      if (claroNoEscuro < 0) {
        pretoSobreBranco = BlackOnWhiteEstimator::isBlackOnWhite(data.grayImage(), data.xform(), status, nullptr);
      } else {
        pretoSobreBranco = (claroNoEscuro == 0);
      }
      const ImageSettings::PageParams novos(BinaryThreshold::otsuThreshold(GrayscaleHistogram(cinza, mascara)),
                                            pretoSobreBranco);
      data.updateImageParams(novos);
      *pretoNoBranco = pretoSobreBranco ? 1 : 0;
    }
    milissegundos[0] = milissegundosDesde(inicio);

    // 3. A caixa da pagina (select_content/Task.cpp, linhas 95-109).
    inicio = Relogio::now();
    QRectF pageRect;
    if (modoPagina == 1) {  // MODE_AUTO
      pageRect = select_content::PageFinder::findPageBox(status, data, ajustarCantos != 0,
                                                         QSizeF(larguraEsperadaMm, alturaEsperadaMm), tolerancia,
                                                         nullptr);
    } else {  // MODE_DISABLED
      pageRect = data.xform().resultingRect();
    }
    if (!data.xform().resultingRect().intersected(pageRect).isValid()) {
      pageRect = data.xform().resultingRect();
    }
    milissegundos[1] = milissegundosDesde(inicio);

    // 4. A caixa do conteudo (select_content/Task.cpp, linhas 129-147).
    inicio = Relogio::now();
    QRectF contentRect;
    if (modoConteudo == 1) {  // MODE_AUTO
      contentRect = select_content::ContentBoxFinder::findContentBox(status, data, pageRect, nullptr);
    } else {  // MODE_DISABLED
      contentRect = pageRect;
    }
    const QRectF bruto(contentRect);
    if (contentRect.isValid()) {
      contentRect &= pageRect;
    }
    milissegundos[2] = milissegundosDesde(inicio);

    gravarCaixa(pagina, pageRect);
    if (bruto.isValid()) {
      gravarCaixa(conteudoBruto, bruto);
    } else {
      zerarCaixa(conteudoBruto);
    }
    if (contentRect.isValid()) {
      gravarCaixa(conteudo, contentRect);
      const QSizeF mm = select_content::PhysSizeCalc(data.xform()).sizeMM(contentRect);
      tamanhoConteudoMm[0] = mm.width();
      tamanhoConteudoMm[1] = mm.height();
      *achouConteudo = 1;
    } else {
      // Pagina sem conteudo (em branco, ou tudo virou "sombra").
      zerarCaixa(conteudo);
      tamanhoConteudoMm[0] = tamanhoConteudoMm[1] = 0.0;
      *achouConteudo = 0;
    }
    return ST_FERRAMENTAS_OK;
  });
}

}  // extern "C"
