// Endireitar a pagina: o SkewFinder do ScanTailor Advanced, chamado do Python.
//
// Copyright (C) 2026  Editor de Impressao (so esta ligacao; o trecho marcado
//   "COPIADO SEM MUDANCA" e do ScanTailor Advanced, Joseph Artsimovich e 4lex4)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// O QUE FAZ (item 2.2 da Fase 2, decisao G4 (b) do Samuel, 05/10/2026)
//   Recebe a pagina (cinza ou colorida) e o DPI, e devolve o angulo que o
//   ScanTailor acharia sozinho: o que o deskew::Task do ScanTailor faz numa
//   pagina nova (src/core/filters/deskew/Task.cpp; o original esta em
//   ../referencia/deskew/Task.cpp, NAO compilado), na mesma ordem:
//     1. a pagina cinza e a geometria: as linhas do construtor de FilterData
//        (src/core/FilterData.cpp, linhas 12-13):
//          m_grayImage(toGrayscale(m_origImage)), m_xform(image.rect(), Dpm(image))
//     2. Task::updateFilterData (Task.cpp, linhas 278-286): o limiar Otsu so
//        dentro da pagina e a deteccao "claro no escuro"
//        (BlackOnWhiteEstimator, ligada de fabrica no ScanTailor:
//        ApplicationSettings::DEFAULT_BLACK_ON_WHITE_DETECTION = true). Pagina
//        "claro no escuro" e medida invertida (FilterData.cpp, linhas 31-37);
//     3. Task::process (Task.cpp, linhas 117-163): preto e branco na area da
//        pagina, giro de 90 graus (zero aqui: quem gira e o programa, antes),
//        LIMPEZA DAS SOMBRAS HORIZONTAIS COMPRIDAS (cleanup, abaixo, copiado
//        sem mudanca), SkewFinder::findSkew (o padrao do ScanTailor e o
//        "pelo conteudo": deskew::Settings, m_algoContentBased(true)) e o
//        angulo so vale com confianca >= Skew::GOOD_CONFIDENCE (2,0); senao 0.
//   A correcao "obliqua" (ObliqueFinder) vem desligada de fabrica no ScanTailor
//   e NAO foi trazida.
//
// O SENTIDO DO ANGULO
//   Devolvemos o angulo como o ScanTailor o aplica (uiData.effectiveDeskewAngle
//   = -skew.angle(): o "post rotation" do ImageTransformation dele). O Python
//   (core/endireitar_scantailor.py) troca para o sentido do programa (o do
//   OpenCV); o teste com uma folha de mentira girada confere.
//
// O QUE E ARRISCADO
//   - O DPI: so muda a limpeza das sombras (o tijolo de 200 x 14 pontos e a
//     150 DPI; a imagem e reduzida a menos de 200 DPI antes). O SkewFinder em si
//     trabalha nos pontos da imagem (reduz 2 e 4 vezes), entao o TAMANHO da
//     imagem muda o resultado - o programa passa sempre a pagina na resolucao
//     do PDF (core/pipeline.py).
//   - Trocar o trecho copiado: o teste tests/test_endireitar_scantailor.py
//     confere que ele e igual as linhas 222-271 do original.

#include <BinaryImage.h>
#include <BinaryThreshold.h>
#include <Dpi.h>
#include <Dpm.h>
#include <GrayImage.h>
#include <Grayscale.h>
#include <Morphology.h>
#include <OrthogonalRotation.h>
#include <PolygonRasterizer.h>
#include <RasterOp.h>
#include <ReduceThreshold.h>
#include <SeedFill.h>
#include <SkewFinder.h>
#include <UpscaleIntegerTimes.h>

#include <QImage>
#include <QPolygonF>
#include <QRect>
#include <QRectF>
#include <QSize>

#include "BlackOnWhiteEstimator.h"
#include "ImageTransformation.h"
#include "NullTaskStatus.h"
#include "TaskStatus.h"
#include "comum.h"
#include "st_ferramentas.h"

namespace deskew {
using namespace imageproc;

// Uma classe com o MESMO nome e as mesmas tres funcoes "static" do
// deskew::Task do ScanTailor (src/core/filters/deskew/Task.h), para o trecho
// abaixo compilar sem mudar uma letra. O resto do Task (a janela, o projeto)
// nao vem.
class Task {
 public:
  static void cleanup(const TaskStatus& status, imageproc::BinaryImage& img, const Dpi& dpi);

  static int from150dpi(int size, int targetDpi);

  static QSize from150dpi(const QSize& size, const Dpi& targetDpi);
};

// ---- COPIADO SEM MUDANCA de src/core/filters/deskew/Task.cpp (linhas 222-271) ----
void Task::cleanup(const TaskStatus& status, BinaryImage& image, const Dpi& dpi) {
  // We don't have to clean up every piece of garbage.
  // The only concern are the horizontal shadows, which we remove here.

  Dpi reducedDpi(dpi);
  BinaryImage reducedImage;

  {
    ReduceThreshold reductor(image);
    while (reducedDpi.horizontal() >= 200 && reducedDpi.vertical() >= 200) {
      reductor.reduce(2);
      reducedDpi = Dpi(reducedDpi.horizontal() / 2, reducedDpi.vertical() / 2);
    }
    reducedImage = reductor.image();
  }

  status.throwIfCancelled();

  const QSize brick(from150dpi(QSize(200, 14), reducedDpi));
  BinaryImage opened(openBrick(reducedImage, brick, BLACK));
  reducedImage.release();

  status.throwIfCancelled();

  BinaryImage seed(upscaleIntegerTimes(opened, image.size(), WHITE));
  opened.release();

  status.throwIfCancelled();

  BinaryImage garbage(seedFill(seed, image, CONN8));
  seed.release();

  status.throwIfCancelled();

  rasterOp<RopSubtract<RopDst, RopSrc>>(image, garbage);
}  // Task::cleanup

int Task::from150dpi(int size, int targetDpi) {
  const int newSize = (size * targetDpi + 75) / 150;
  if (newSize < 1) {
    return 1;
  }
  return newSize;
}

QSize Task::from150dpi(const QSize& size, const Dpi& targetDpi) {
  const int width = from150dpi(size.width(), targetDpi.horizontal());
  const int height = from150dpi(size.height(), targetDpi.vertical());
  return QSize(width, height);
}
// ---- FIM DO TRECHO COPIADO --------------------------------------------------
}  // namespace deskew

using imageproc::BinaryImage;
using imageproc::BinaryThreshold;
using imageproc::GrayImage;
using imageproc::GrayscaleHistogram;
using imageproc::PolygonRasterizer;
using imageproc::Skew;
using imageproc::SkewFinder;

extern "C" {

ST_FERRAMENTAS_API int st_ferramentas_endireitar(const unsigned char* pixels,
                                                 int largura,
                                                 int altura,
                                                 int passo,
                                                 int canais,
                                                 int dpiX,
                                                 int dpiY,
                                                 double* angulo,
                                                 double* anguloBruto,
                                                 double* confianca,
                                                 int* pretoNoBranco,
                                                 char* erro,
                                                 int tamanhoErro) {
  return st_ferramentas::protegido(erro, tamanhoErro, [&]() -> int {
    if (!pixels || !angulo || !anguloBruto || !confianca || !pretoNoBranco || largura <= 0 || altura <= 0
        || (canais != 1 && canais != 3) || passo < largura * canais || dpiX <= 0 || dpiY <= 0) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_FERRAMENTAS_ERRO_PARAMETRO;
    }
    NullTaskStatus status;

    // A pagina como o ScanTailor a abriria do disco (os pontos so sao lidos) e
    // o DPI gravado nela. 3 canais = a ordem do OpenCV (azul, verde, vermelho).
    QImage pagina(pixels, largura, altura, passo, canais == 1 ? QImage::Format_Grayscale8 : QImage::Format_BGR888);
    const Dpm dpm{Dpi(dpiX, dpiY)};
    pagina.setDotsPerMeterX(dpm.horizontal());
    pagina.setDotsPerMeterY(dpm.vertical());

    // 1. FilterData (FilterData.cpp, linhas 12-13).
    const GrayImage cinza(imageproc::toGrayscale(pagina));
    const ImageTransformation xform(pagina.rect(), Dpm(pagina));

    // 2. Task::updateFilterData (Task.cpp, linhas 278-286), com a deteccao
    //    "claro no escuro" ligada (o padrao do ScanTailor).
    BinaryImage mascara(cinza.size(), imageproc::BLACK);
    PolygonRasterizer::fillExcept(mascara, imageproc::WHITE, xform.resultingPreCropArea(), Qt::WindingFill);
    const bool pretoSobreBranco = BlackOnWhiteEstimator::isBlackOnWhite(cinza, xform, status, nullptr);
    const BinaryThreshold limiar = BinaryThreshold::otsuThreshold(GrayscaleHistogram(cinza, mascara));
    // FilterData::grayImageBlackOnWhite / bwThresholdBlackOnWhite (FilterData.cpp, linhas 31-37).
    const GrayImage cinzaPretoNoBranco = pretoSobreBranco ? cinza : cinza.inverted();
    const BinaryThreshold limiarPretoNoBranco = pretoSobreBranco ? limiar : BinaryThreshold(256 - int(limiar));

    // 3. Task::process (Task.cpp, linhas 117-163), sem a correcao obliqua.
    const QRectF areaDaImagem(xform.transformBack().mapRect(xform.resultingRect()));
    const QRect areaLimitada(areaDaImagem.toRect().intersected(pagina.rect()));
    *pretoNoBranco = pretoSobreBranco ? 1 : 0;
    if (!areaLimitada.isValid()) {
      *angulo = 0.0;
      *anguloBruto = 0.0;
      *confianca = 0.0;
      return ST_FERRAMENTAS_OK;
    }
    BinaryImage girada(imageproc::orthogonalRotation(
        BinaryImage(cinzaPretoNoBranco, areaLimitada, limiarPretoNoBranco), xform.preRotation().toDegrees()));
    const QSize dpmSemGiro(Dpm(pagina).toSize());
    const Dpm dpmGirado(xform.preRotation().rotate(dpmSemGiro));
    deskew::Task::cleanup(status, girada, Dpi(dpmGirado));

    SkewFinder skewFinder;
    skewFinder.setResolutionRatio((double) dpmGirado.horizontal() / dpmGirado.vertical());
    const Skew skew(skewFinder.findSkew(girada));

    *anguloBruto = -skew.angle();
    *confianca = skew.confidence();
    *angulo = (skew.confidence() >= Skew::GOOD_CONFIDENCE) ? -skew.angle() : 0.0;
    return ST_FERRAMENTAS_OK;
  });
}

}  // extern "C"
