// Desentortar a pagina curva perto da lombada: o "Dewarping" do ScanTailor
// Advanced, chamado do Python (item 2.12 da Fase 2, 21/10/2026).
//
// Copyright (C) 2019  Joseph Artsimovich <joseph.artsimovich@gmail.com>, 4lex4 <4lex49@zoho.com>
//   (todas as funcoes entre as marcas "COPIADO SEM MUDANCA" abaixo, e todo o
//   ../src/dewarping, ../src/math/spfit e ../src/math/adiff, sem mudanca)
// Copyright (C) 2026  Editor de Impressao (so a ligacao: a classe de apoio,
//   desentortar() e a funcao em C no fim do arquivo)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// O QUE FAZ
//   No ScanTailor, o desentortar mora na etapa de saida
//   (src/core/filters/output/OutputGenerator.cpp, processWithDewarping(),
//   linhas 1532-1891): ele segue as linhas do texto (TextLineTracer) e as
//   beiradas de cima e de baixo do bloco de texto (TopBottomEdgeTracer), monta
//   com elas duas curvas (DistortionModel), imagina a folha como um pedaco de
//   cilindro entre essas curvas (CylindricalSurfaceDewarper, "profundidade"
//   2,0 de fabrica) e redesenha a pagina reta (RasterDewarper). E redesenho de
//   pontos: nao inventa detalhe.
//   Modos do ScanTailor (DewarpingOptions): OFF (o de fabrica dele e o nosso),
//   AUTO ("automatico": as curvas pelas linhas do texto), MARGINAL ("pelas
//   margens": as curvas pelas beiradas brancas de cima e de baixo, com o
//   endireitar depois) e MANUAL (malha mexida a mao; NAO foi trazido: precisa
//   de uma tela de malha que o programa nao tem).
//
// A ORDEM (a de processImpl() + processWithDewarping(), sem o resto da saida)
//   1. a cor do fundo fora da pagina (processImpl, linhas 1263-1264);
//   2. a pagina em cinza no sistema de trabalho, SEM igualar a luz (linhas
//      1544-1546; o caminho do ScanTailor no modo Cor/Cinza, em que "Equalize
//      illumination" vem desligado de fabrica: ColorCommonOptions.cpp, linha
//      13). Os filtros do programa vem DEPOIS e fazem a luz deles;
//   3. a pagina que vai ser redesenhada: a original, colorida ou cinza (linhas
//      1559-1560); o filtro de Wiener fica de fora (coeficiente 0 de fabrica);
//   4. as curvas (linhas 1639-1643: buildAutoDistortionModel ou
//      buildMarginalDistortionModel, copiadas sem mudanca);
//   5. o redesenho, com o endireitar depois (so no "pelas margens", como no
//      ScanTailor: findSkew) e a volta ao modelo "sem curva" se as curvas
//      forem impossiveis (linhas 1645-1665).
//   O preto e branco, os pontinhos e as cores do ScanTailor NAO estao aqui:
//   no programa sao os filtros, que vem depois, na pagina ja desentortada.
//
// O QUE A LIGACAO TROCA (e so isso)
//   - A classe OutputGenerator::Processor do ScanTailor depende do projeto, da
//     janela e das configuracoes. Aqui ela e trocada por uma classe com o MESMO
//     NOME e so os membros que as funcoes copiadas usam (como em saida.cpp e no
//     1.2). Para nao brigar com a de saida.cpp (mesma DLL), ela mora no
//     namespace st_desentortar::output, e nao em output.
//   - A pagina chega dividida e endireitada pelo programa, mas SEM o corte, com
//     o papel do proprio scan em volta (versao 8, 22/10/2026; antes chegava ja
//     cortada e as letras empurradas para fora do corte sumiam). A geometria
//     (m_xform) e ImageTransformation(image.rect(), dpi) com o corte do
//     programa como "post-crop" (setPostCropArea); a pagina de saida
//     (m_outRect) e o corte e a caixa do conteudo (m_contentRect) e a que o
//     Python manda (de fabrica, o proprio corte). As areas seguem calcAreas()
//     (linhas 319-363) com os de fabrica do ScanTailor (fillOffcut,
//     fillMargins). A imagem e recortada uma vez so, pelo RasterDewarper, no
//     tamanho de m_outRect, como no ScanTailor.
//   - O endireitar depois do "pelas margens" gira com o papel em volta (ver o
//     comentario no desentortar()): o angulo e o do ScanTailor, so os cantos
//     vem do scan em vez da cor do fundo.
//   - O lado da pagina (m_pageId.subPage(): unica, esquerda, direita) vem do
//     Python (a metade da folha). So o "pelas margens" e a correcao da beirada
//     do automatico usam.
//   - Utils::rotate (de src/core/filters/output/Utils.cpp, que puxaria o
//     projeto inteiro) esta copiado sem mudanca numa classe Utils so com ele.
//   - A pagina e sempre tratada como "preto no branco" (como no 1.2; a
//     caixinha "Letra clara em fundo escuro" do programa, item 2.9, vale nos
//     filtros, depois).
//
// O QUE E SEGURO MUDAR
//   So a ligacao (fora das marcas) e os comentarios.
//
// O QUE E ARRISCADO
//   - Mudar qualquer coisa dentro das marcas: deixa de ser o codigo do
//     ScanTailor e quebra o teste de copia fiel (tests/test_desentortar_scantailor.py).
//   - Por esta classe no namespace output: a de saida.cpp tem o mesmo nome e
//     outros membros; as duas na mesma DLL e no mesmo namespace = comportamento
//     indefinido (o vinculador pode juntar as duas).
//   - O DPI: o TextLineTracer reduz a pagina para 200 DPI pelo DPI dito; o DPI
//     errado muda as linhas achadas.

#include <BackgroundColorCalculator.h>
#include <BinaryImage.h>
#include <BinaryThreshold.h>
#include <Constants.h>
#include <CylindricalSurfaceDewarper.h>
#include <DistortionModel.h>
#include <DistortionModelBuilder.h>
#include <Dpi.h>
#include <Dpm.h>
#include <GrayImage.h>
#include <Grayscale.h>
#include <ImageTransformation.h>
#include <OrthogonalRotation.h>
#include <PageId.h>
#include <RasterDewarper.h>
#include <SkewFinder.h>
#include <TextLineTracer.h>
#include <TopBottomEdgeTracer.h>
#include <Transform.h>
#include <XSpline.h>
#include <imageproc/OrthogonalRotation.h>

#include <QColor>
#include <QImage>
#include <QLineF>
#include <QPointF>
#include <QPolygonF>
#include <QRect>
#include <QRectF>
#include <QString>
#include <QTransform>
#include <cmath>
#include <cstring>
#include <new>
#include <stdexcept>
#include <vector>

#include "DebugImages.h"
#include "DepthPerception.h"
#include "DewarpingOptions.h"
#include "NullTaskStatus.h"
#include "TaskStatus.h"
#include "comum.h"
#include "st_ferramentas.h"

using namespace imageproc;
using namespace dewarping;

namespace st_desentortar {
namespace output {
// O que vem do ScanTailor com o nome "output::" (DewarpingOptions, DepthPerception,
// os modos AUTO, MARGINAL...), visivel aqui sem mudar o codigo copiado.
using namespace ::output;

// ---------------------------------------------------------------------------
// LIGACAO: Utils::rotate, a unica funcao de output::Utils que o desentortar usa.
// ---------------------------------------------------------------------------
class Utils {
 public:
  static QTransform rotate(double degrees, const QRect& imageRect);
};

// ===== COPIADO SEM MUDANCA (Utils.cpp, linhas 47-58) =====
QTransform Utils::rotate(double degrees, const QRect& imageRect) {
  if (degrees == 0.0) {
    return QTransform();
  }

  QTransform rotateXform;
  const QPointF origin = QRectF(imageRect).center();
  rotateXform.translate(-origin.x(), -origin.y());
  rotateXform *= QTransform().rotate(degrees);
  rotateXform *= QTransform().translate(origin.x(), origin.y());
  return rotateXform;
}
// ===== FIM DO COPIADO =====

// ---------------------------------------------------------------------------
// LIGACAO: a classe que faz o papel de OutputGenerator::Processor.
// Tem o mesmo nome para que as funcoes copiadas compilem sem mudar uma letra.
// Cada membro tem o mesmo nome e o mesmo sentido do original.
// ---------------------------------------------------------------------------
class OutputGenerator {
 public:
  class Processor;
};

class OutputGenerator::Processor {
 public:
  // image: a pagina ja dividida e endireitada pelo programa, SEM o corte (com o
  //   papel do proprio scan em volta; versao 8, 22/10/2026).
  // dpi: o DPI da imagem. modo: AUTO ou MARGINAL. lado: a metade da folha.
  // corte: o corte medido pelo programa, em pontos da imagem (vazio = a imagem
  //   inteira): vira a pagina de saida (m_outRect), como o ScanTailor.
  // conteudo: a caixa do conteudo, em pontos da imagem (vazia = o corte).
  // endireitarDepois: o "post deskew" do ScanTailor (ligado de fabrica).
  Processor(const QImage& image,
            const Dpi& dpi,
            DewarpingMode modo,
            PageId::SubPage lado,
            const QRect& corte,
            const QRect& conteudo,
            bool endireitarDepois);

  // Os passos 1 a 5 do topo do arquivo. Devolve a pagina desentortada, ja do
  // tamanho do corte; achouCurvas = as curvas nao sao as do modelo "sem curva".
  QImage desentortar(const DepthPerception& depthPerception, bool* achouCurvas, double* anguloDepois);

 private:
  void setupTrivialDistortionModel(DistortionModel& distortionModel) const;

  static CylindricalSurfaceDewarper createDewarper(const DistortionModel& distortionModel,
                                                   const QTransform& distortionModelToTarget,
                                                   double depthPerception);

  QImage dewarp(const QTransform& origToSrc,
                const QImage& src,
                const QTransform& srcToOutput,
                const DistortionModel& distortionModel,
                const DepthPerception& depthPerception,
                const QColor& bgColor) const;

  double findSkew(const QImage& image) const;

  DistortionModel buildAutoDistortionModel(const GrayImage& warpedGrayOutput, const QTransform& toOriginal) const;

  DistortionModel buildMarginalDistortionModel() const;

  ImageTransformation m_xform;
  Dpi m_dpi;
  PageId m_pageId;
  DewarpingOptions m_dewarpingOptions;
  QImage m_inputOrigImage;
  GrayImage m_inputGrayImage;
  bool m_colorOriginal;
  QRect m_outRect;
  QRect m_contentRect;
  QRect m_workingBoundingRect;
  QRect m_contentRectInWorkingCs;
  QPolygonF m_outCropAreaInOriginalCs;
  NullTaskStatus m_nullStatus;
  const TaskStatus& m_status;
  DebugImages* const m_dbg;
  QColor m_outsideBackgroundColor;
};

// Ajudantes do original (no anonimo, como la), antes de quem os usa.
namespace {
// ===== COPIADO SEM MUDANCA (linhas 987-992) =====
void applyAffineTransform(QImage& image, const QTransform& xform, const QColor& outsideColor) {
  if (xform.isIdentity()) {
    return;
  }
  image = transform(image, xform, image.rect(), OutsidePixels::assumeWeakColor(outsideColor));
}
// ===== FIM DO COPIADO =====

// ===== COPIADO SEM MUDANCA (linhas 1067-1125) =====
void movePointToTopMargin(BinaryImage& bwImage, XSpline& spline, int idx) {
  QPointF pos = spline.controlPointPosition(idx);

  for (int j = 0; j < pos.y(); j++) {
    if (bwImage.getPixel(static_cast<int>(pos.x()), j) == WHITE) {
      int count = 0;
      int checkNum = 16;

      for (int jj = j; jj < (j + checkNum); jj++) {
        if (bwImage.getPixel(static_cast<int>(pos.x()), jj) == WHITE) {
          count++;
        }
      }

      if (count == checkNum) {
        pos.setY(j);
        spline.moveControlPoint(idx, pos);
        break;
      }
    }
  }
}

void movePointToBottomMargin(BinaryImage& bwImage, XSpline& spline, int idx) {
  QPointF pos = spline.controlPointPosition(idx);

  for (int j = bwImage.height() - 1; j > pos.y(); j--) {
    if (bwImage.getPixel(static_cast<int>(pos.x()), j) == WHITE) {
      int count = 0;
      int checkNum = 16;

      for (int jj = j; jj > (j - checkNum); jj--) {
        if (bwImage.getPixel(static_cast<int>(pos.x()), jj) == WHITE) {
          count++;
        }
      }

      if (count == checkNum) {
        pos.setY(j);

        spline.moveControlPoint(idx, pos);

        break;
      }
    }
  }
}

void drawPoint(QImage& image, const QPointF& pt) {
  QPoint pts = pt.toPoint();

  for (int i = pts.x() - 10; i < pts.x() + 10; i++) {
    for (int j = pts.y() - 10; j < pts.y() + 10; j++) {
      QPoint p1(i, j);

      image.setPixel(p1, qRgb(255, 0, 0));
    }
  }
}
// ===== FIM DO COPIADO =====

// ===== COPIADO SEM MUDANCA (linhas 1173-1176) =====
inline float vertBorderSkewAngle(const QPointF& top, const QPointF& bottom) {
  return static_cast<float>(
      std::abs(std::atan((bottom.x() - top.x()) / (bottom.y() - top.y())) * 180.0 / constants::PI));
}
// ===== FIM DO COPIADO =====
}  // namespace

OutputGenerator::Processor::Processor(const QImage& image,
                                      const Dpi& dpi,
                                      DewarpingMode modo,
                                      PageId::SubPage lado,
                                      const QRect& corte,
                                      const QRect& conteudo,
                                      bool endireitarDepois)
    : m_xform(image.rect(), dpi),
      m_dpi(dpi),
      m_pageId(ImageId(QString()), lado),
      m_dewarpingOptions(modo, endireitarDepois),
      m_inputOrigImage(image),
      m_inputGrayImage(toGrayscale(image)),
      m_colorOriginal(!image.allGray()),
      m_status(m_nullStatus),
      m_dbg(nullptr),
      m_outsideBackgroundColor(Qt::white) {
  // VERSAO 8 (22/10/2026, escolha do Samuel na Central: "Como o ScanTailor:
  // cortar uma vez so, no fim"). No ScanTailor o corte e so uma MEDIDA: a
  // geometria (m_xform) leva o escaneamento inteiro ate a pagina de saida
  // (m_outRect, que comeca em 0,0) e o RasterDewarper le os pontos do
  // escaneamento inteiro. Aqui e igual: a imagem vem SEM o corte, o corte vira
  // o "post-crop" da geometria (ImageTransformation::setPostCropArea, o mesmo
  // que o ScanTailor usa) e m_outRect/m_contentRect saem como no construtor do
  // OutputGenerator (linhas 80-89). O que o desentortar empurra para fora do
  // corte le o papel de verdade em volta, nao o branco/preto de fora da imagem.
  // ARRISCADO: voltar a mandar a pagina ja cortada (as letras da beirada somem,
  // Righetti 96 e Cursus 151 em 22/10) ou fazer o corte fora daqui e de novo
  // depois (seria cortar duas vezes, o que o Samuel recusou).
  const QRect corteNaImagem = corte.isEmpty() ? image.rect() : corte.intersected(image.rect());
  m_xform.setPostCropArea(QPolygonF(QRectF(corteNaImagem)));
  m_outRect = m_xform.resultingRect().toRect();
  const QRect conteudoNaImagem = conteudo.isEmpty() ? corteNaImagem : conteudo;
  m_contentRect = m_xform.transform().map(QRectF(conteudoNaImagem)).boundingRect().toRect().intersected(m_outRect);

  // calcAreas() (linhas 319-363), com os de fabrica do ScanTailor: "fillOffcut"
  // ligado (m_preCropArea = resultingPreCropArea, a pagina inteira na
  // coordenada da saida) e "fillMargins" ligado (o conteudo recortado pela
  // caixa do conteudo). Fica de fora so o que o desentortar nao usa.
  const QPolygonF preCropArea = m_xform.resultingPreCropArea();
  const QRect croppedContentRect = preCropArea.intersected(QRectF(m_contentRect)).boundingRect().toRect();
  const QPolygonF outCropArea = preCropArea.intersected(QRectF(m_outRect));
  const int contentMargin = m_dpi.vertical() * 20 / 300;
  m_workingBoundingRect
      = preCropArea
            .intersected(QRectF(croppedContentRect.adjusted(-contentMargin, -contentMargin, contentMargin, contentMargin)))
            .boundingRect()
            .toRect();
  m_contentRectInWorkingCs = croppedContentRect.translated(-m_workingBoundingRect.topLeft());
  m_outCropAreaInOriginalCs = m_xform.transformBack().map(outCropArea);
}

QImage OutputGenerator::Processor::desentortar(const DepthPerception& depthPerception,
                                               bool* achouCurvas,
                                               double* anguloDepois) {
  // 1. processImpl, linhas 1263-1264.
  m_outsideBackgroundColor = BackgroundColorCalculator::calcDominantBackgroundColor(
      m_colorOriginal ? m_inputOrigImage : m_inputGrayImage, m_outCropAreaInOriginalCs);

  // 2. processWithDewarping, linhas 1543-1546 (sem igualar a luz).
  GrayImage warpedGrayOutput = transformToGray(m_inputGrayImage, m_xform.transform(), m_workingBoundingRect,
                                               OutsidePixels::assumeWeakColor(m_outsideBackgroundColor));

  // 3. Linhas 1555-1560 (sem igualar a luz).
  QImage normalizedOriginal;
  const QTransform workingToOrig
      = QTransform().translate(m_workingBoundingRect.left(), m_workingBoundingRect.top()) * m_xform.transformBack();
  if (m_colorOriginal) {
    normalizedOriginal = m_inputOrigImage;
  } else {
    normalizedOriginal = m_inputGrayImage;
  }

  // 4. Linhas 1639-1644.
  DistortionModel distortionModel;
  if (m_dewarpingOptions.dewarpingMode() == AUTO) {
    distortionModel = buildAutoDistortionModel(warpedGrayOutput, workingToOrig);
  } else if (m_dewarpingOptions.dewarpingMode() == MARGINAL) {
    distortionModel = buildMarginalDistortionModel();
  }
  warpedGrayOutput = GrayImage();  // Save memory.

  // 5. Linhas 1646-1665 (sem m_settings, que guarda o angulo no projeto do
  // ScanTailor: aqui o angulo volta ao Python).
  QTransform rotateXform;
  QImage dewarped;
  try {
    dewarped = dewarp(QTransform(), normalizedOriginal, m_xform.transform(), distortionModel, depthPerception,
                      m_outsideBackgroundColor);

    const double deskewAngle = -findSkew(dewarped);
    rotateXform = Utils::rotate(deskewAngle, m_outRect);
    m_dewarpingOptions.setPostDeskewAngle(deskewAngle);
  } catch (const std::runtime_error&) {
    // Probably an impossible distortion model.  Let's fall back to a trivial one.
    setupTrivialDistortionModel(distortionModel);
    m_dewarpingOptions.setPostDeskewAngle(.0);

    dewarped = dewarp(QTransform(), normalizedOriginal, m_xform.transform(), distortionModel, depthPerception,
                      m_outsideBackgroundColor);
  }
  // O endireitar depois (so no "pelas margens"), COM O PAPEL EM VOLTA (versao 8,
  // 22/10/2026). No ScanTailor o giro e feito na pagina de saida e os cantos que
  // entram vem com a cor do fundo; la a pagina de saida tem as margens do layout
  // (10 mm dos lados, 5 mm em cima e embaixo), e os cantos caem nelas. Aqui a
  // pagina de saida e o corte rente (1 mm de folga): o canto do texto sairia.
  // Por isso, quando ha giro, o MESMO desentortar (mesmo modelo, mesmo centro,
  // mesmo angulo, medido como no ScanTailor na pagina do tamanho do corte) e
  // redesenhado numa pagina maior pela folga do giro, girado em volta do mesmo
  // centro e recortado no corte: os cantos vem do papel do scan. Sem giro (o
  // automatico, ou angulo 0), nada disso roda.
  // ARRISCADO: girar em volta de outro centro (Utils::rotate usa o centro do
  // retangulo; a pagina maior e simetrica, o centro e o mesmo) ou medir o angulo
  // na pagina maior (o angulo deixaria de ser o do ScanTailor).
  if (!rotateXform.isIdentity()) {
    const double seno = std::abs(std::sin(m_dewarpingOptions.getPostDeskewAngle() * constants::PI / 180.0));
    const int folga = static_cast<int>(std::ceil(seno * (m_outRect.width() + m_outRect.height()) / 2.0)) + 2;
    const QRect saidaDoCorte = m_outRect;
    QImage maior;
    try {
      m_outRect = QRect(0, 0, saidaDoCorte.width() + 2 * folga, saidaDoCorte.height() + 2 * folga);
      maior = dewarp(QTransform(), normalizedOriginal, m_xform.transform() * QTransform::fromTranslate(folga, folga),
                     distortionModel, depthPerception, m_outsideBackgroundColor);
    } catch (const std::runtime_error&) {
      maior = QImage();
    }
    m_outRect = saidaDoCorte;
    if (!maior.isNull()) {
      applyAffineTransform(maior, Utils::rotate(m_dewarpingOptions.getPostDeskewAngle(), maior.rect()),
                           m_outsideBackgroundColor);
      dewarped = maior.copy(folga, folga, saidaDoCorte.width(), saidaDoCorte.height());
      rotateXform = QTransform();  // ja girado
    }
  }
  // (O normalizedOriginal fica ate aqui: o redesenho com o papel em volta usa.)
  normalizedOriginal = QImage();  // Save memory.
  applyAffineTransform(dewarped, rotateXform, m_outsideBackgroundColor);

  DistortionModel semCurva;
  setupTrivialDistortionModel(semCurva);
  *achouCurvas = !distortionModel.matches(semCurva);
  *anguloDepois = m_dewarpingOptions.getPostDeskewAngle();
  return dewarped;
}

// ===== COPIADO SEM MUDANCA (linhas 2034-2106) =====
/**
 * Set up a distortion model corresponding to the content rect,
 * which will result in no distortion correction.
 */
void OutputGenerator::Processor::setupTrivialDistortionModel(DistortionModel& distortionModel) const {
  QPolygonF poly;
  if (!m_contentRect.isEmpty()) {
    poly = QRectF(m_contentRect);
  } else {
    poly << m_contentRect.topLeft() + QPointF(-0.5, -0.5);
    poly << m_contentRect.topLeft() + QPointF(0.5, -0.5);
    poly << m_contentRect.topLeft() + QPointF(0.5, 0.5);
    poly << m_contentRect.topLeft() + QPointF(-0.5, 0.5);
  }
  poly = m_xform.transformBack().map(poly);

  std::vector<QPointF> topPolyline, bottomPolyline;
  topPolyline.push_back(poly[0]);     // top-left
  topPolyline.push_back(poly[1]);     // top-right
  bottomPolyline.push_back(poly[3]);  // bottom-left
  bottomPolyline.push_back(poly[2]);  // bottom-right
  distortionModel.setTopCurve(Curve(topPolyline));
  distortionModel.setBottomCurve(Curve(bottomPolyline));
}

CylindricalSurfaceDewarper OutputGenerator::Processor::createDewarper(const DistortionModel& distortionModel,
                                                                      const QTransform& distortionModelToTarget,
                                                                      double depthPerception) {
  if (distortionModelToTarget.isIdentity()) {
    return CylindricalSurfaceDewarper(distortionModel.topCurve().polyline(), distortionModel.bottomCurve().polyline(),
                                      depthPerception);
  }

  std::vector<QPointF> topPolyline(distortionModel.topCurve().polyline());
  std::vector<QPointF> bottomPolyline(distortionModel.bottomCurve().polyline());
  for (QPointF& pt : topPolyline) {
    pt = distortionModelToTarget.map(pt);
  }
  for (QPointF& pt : bottomPolyline) {
    pt = distortionModelToTarget.map(pt);
  }
  return CylindricalSurfaceDewarper(topPolyline, bottomPolyline, depthPerception);
}

/**
 * \param origToSrc Transformation from the original image coordinates
 *                    to the coordinate system of \p src image.
 * \param srcToOutput Transformation from the \p src image coordinates
 *                      to output image coordinates.
 * \param distortionModel Distortion model.
 * \param depthPerception Depth perception.
 * \param bgColor The color to use for areas outsize of \p src.
 * \param modified_content_rect A vertically shrunk version of outputContentRect().
 *                              See function definition for more details.
 */
QImage OutputGenerator::Processor::dewarp(const QTransform& origToSrc,
                                          const QImage& src,
                                          const QTransform& srcToOutput,
                                          const DistortionModel& distortionModel,
                                          const DepthPerception& depthPerception,
                                          const QColor& bgColor) const {
  const CylindricalSurfaceDewarper dewarper(createDewarper(distortionModel, origToSrc, depthPerception.value()));

  // Model domain is a rectangle in output image coordinates that
  // will be mapped to our curved quadrilateral.
  const QRect modelDomain(distortionModel.modelDomain(dewarper, origToSrc * srcToOutput, m_outRect).toRect());
  if (modelDomain.isEmpty()) {
    GrayImage out(src.size());
    out.fill(0xff);  // white
    return out;
  }
  return RasterDewarper::dewarp(src, m_outRect.size(), dewarper, modelDomain, bgColor);
}
// ===== FIM DO COPIADO =====

// ===== COPIADO SEM MUDANCA (linhas 2490-2500) =====
double OutputGenerator::Processor::findSkew(const QImage& image) const {
  if (m_dewarpingOptions.needPostDeskew()
      && ((m_dewarpingOptions.dewarpingMode() == MARGINAL) || (m_dewarpingOptions.dewarpingMode() == MANUAL))) {
    const BinaryImage bwImage(image, BinaryThreshold::otsuThreshold(GrayscaleHistogram(image)));
    const Skew skew = SkewFinder().findSkew(bwImage);
    if ((skew.angle() != .0) && (skew.confidence() >= Skew::GOOD_CONFIDENCE)) {
      return skew.angle();
    }
  }
  return .0;
}
// ===== FIM DO COPIADO =====

// ===== COPIADO SEM MUDANCA (linhas 2608-2813) =====
DistortionModel OutputGenerator::Processor::buildAutoDistortionModel(const GrayImage& warpedGrayOutput,
                                                                     const QTransform& toOriginal) const {
  DistortionModelBuilder modelBuilder(Vec2d(0, 1));

  TextLineTracer::trace(warpedGrayOutput, m_dpi, m_contentRectInWorkingCs, modelBuilder, m_status, m_dbg);
  modelBuilder.transform(toOriginal);

  TopBottomEdgeTracer::trace(m_inputGrayImage, modelBuilder.verticalBounds(), modelBuilder, m_status, m_dbg);

  DistortionModel distortionModel = modelBuilder.tryBuildModel(m_dbg, &m_inputGrayImage.toQImage());
  if (!distortionModel.isValid()) {
    setupTrivialDistortionModel(distortionModel);
  }

  BinaryImage bwImage(m_inputGrayImage, BinaryThreshold(64));

  QTransform transform = m_xform.preRotation().transform(bwImage.size());
  QTransform invTransform = transform.inverted();

  int degrees = m_xform.preRotation().toDegrees();
  bwImage = orthogonalRotation(bwImage, degrees);

  const std::vector<QPointF>& topPolyline0 = distortionModel.topCurve().polyline();
  const std::vector<QPointF>& bottomPolyline0 = distortionModel.bottomCurve().polyline();

  std::vector<QPointF> topPolyline;
  std::vector<QPointF> bottomPolyline;

  for (auto i : topPolyline0) {
    topPolyline.push_back(transform.map(i));
  }

  for (auto i : bottomPolyline0) {
    bottomPolyline.push_back(transform.map(i));
  }

  QString stAngle;

  float maxAngle = 2.75;

  if ((m_pageId.subPage() == PageId::SINGLE_PAGE) || (m_pageId.subPage() == PageId::LEFT_PAGE)) {
    float vertSkewAngleLeft = vertBorderSkewAngle(topPolyline.front(), bottomPolyline.front());

    stAngle.setNum(vertSkewAngleLeft);


    if (vertSkewAngleLeft > maxAngle) {
      auto topX = static_cast<float>(topPolyline.front().x());
      auto bottomX = static_cast<float>(bottomPolyline.front().x());

      if (topX < bottomX) {
        std::vector<QPointF> newBottomPolyline;

        QPointF pt(topX, bottomPolyline.front().y());

        newBottomPolyline.push_back(pt);

        for (auto i : bottomPolyline) {
          newBottomPolyline.push_back(invTransform.map(i));
        }

        distortionModel.setBottomCurve(Curve(newBottomPolyline));
      } else {
        std::vector<QPointF> newTopPolyline;

        QPointF pt(bottomX, topPolyline.front().y());

        newTopPolyline.push_back(pt);

        for (auto i : topPolyline) {
          newTopPolyline.push_back(invTransform.map(i));
        }

        distortionModel.setBottomCurve(Curve(newTopPolyline));
      }
    }
  } else {
    float vertSkewAngleRight = vertBorderSkewAngle(topPolyline.back(), bottomPolyline.back());

    stAngle.setNum(vertSkewAngleRight);


    if (vertSkewAngleRight > maxAngle) {
      auto topX = static_cast<float>(topPolyline.back().x());
      auto bottomX = static_cast<float>(bottomPolyline.back().x());

      if (topX > bottomX) {
        std::vector<QPointF> newBottomPolyline;

        QPointF pt(topX, bottomPolyline.back().y());

        for (auto i : bottomPolyline) {
          newBottomPolyline.push_back(invTransform.map(i));
        }

        newBottomPolyline.push_back(pt);

        distortionModel.setBottomCurve(Curve(newBottomPolyline));
      } else {
        std::vector<QPointF> newTopPolyline;

        QPointF pt(bottomX, topPolyline.back().y());

        for (auto i : topPolyline) {
          newTopPolyline.push_back(invTransform.map(i));
        }

        newTopPolyline.push_back(pt);

        distortionModel.setBottomCurve(Curve(newTopPolyline));
      }
    }
  }
  return distortionModel;
}

DistortionModel OutputGenerator::Processor::buildMarginalDistortionModel() const {
  BinaryImage bwImage(m_inputGrayImage, BinaryThreshold(64));

  QTransform transform = m_xform.preRotation().transform(bwImage.size());
  QTransform invTransform = transform.inverted();

  int degrees = m_xform.preRotation().toDegrees();
  bwImage = orthogonalRotation(bwImage, degrees);

  DistortionModel distortionModel;
  setupTrivialDistortionModel(distortionModel);

  int maxRedPoints = 5;
  XSpline topSpline;

  const std::vector<QPointF>& topPolyline = distortionModel.topCurve().polyline();

  const QLineF topLine(transform.map(topPolyline.front()), transform.map(topPolyline.back()));

  topSpline.appendControlPoint(topLine.p1(), 0);

  if ((m_pageId.subPage() == PageId::SINGLE_PAGE) || (m_pageId.subPage() == PageId::LEFT_PAGE)) {
    for (int i = 29 - maxRedPoints; i < 29; i++) {
      topSpline.appendControlPoint(topLine.pointAt((float) i / 29.0), 1);
    }
  } else {
    for (int i = 1; i <= maxRedPoints; i++) {
      topSpline.appendControlPoint(topLine.pointAt((float) i / 29.0), 1);
    }
  }

  topSpline.appendControlPoint(topLine.p2(), 0);

  for (int i = 0; i <= topSpline.numSegments(); i++) {
    movePointToTopMargin(bwImage, topSpline, i);
  }

  for (int i = 0; i <= topSpline.numSegments(); i++) {
    topSpline.moveControlPoint(i, invTransform.map(topSpline.controlPointPosition(i)));
  }

  distortionModel.setTopCurve(Curve(topSpline));


  XSpline bottomSpline;

  const std::vector<QPointF>& bottomPolyline = distortionModel.bottomCurve().polyline();

  const QLineF bottomLine(transform.map(bottomPolyline.front()), transform.map(bottomPolyline.back()));

  bottomSpline.appendControlPoint(bottomLine.p1(), 0);

  if ((m_pageId.subPage() == PageId::SINGLE_PAGE) || (m_pageId.subPage() == PageId::LEFT_PAGE)) {
    for (int i = 29 - maxRedPoints; i < 29; i++) {
      bottomSpline.appendControlPoint(topLine.pointAt((float) i / 29.0), 1);
    }
  } else {
    for (int i = 1; i <= maxRedPoints; i++) {
      bottomSpline.appendControlPoint(topLine.pointAt((float) i / 29.0), 1);
    }
  }

  bottomSpline.appendControlPoint(bottomLine.p2(), 0);

  for (int i = 0; i <= bottomSpline.numSegments(); i++) {
    movePointToBottomMargin(bwImage, bottomSpline, i);
  }

  for (int i = 0; i <= bottomSpline.numSegments(); i++) {
    bottomSpline.moveControlPoint(i, invTransform.map(bottomSpline.controlPointPosition(i)));
  }

  distortionModel.setBottomCurve(Curve(bottomSpline));

  if (!distortionModel.isValid()) {
    setupTrivialDistortionModel(distortionModel);
  }

  if (m_dbg) {
    QImage outImage(bwImage.toQImage().convertToFormat(QImage::Format_RGB32));
    for (int i = 0; i <= topSpline.numSegments(); i++) {
      drawPoint(outImage, topSpline.controlPointPosition(i));
    }
    for (int i = 0; i <= bottomSpline.numSegments(); i++) {
      drawPoint(outImage, bottomSpline.controlPointPosition(i));
    }
    m_dbg->add(outImage, "marginal dewarping");
  }
  return distortionModel;
}
// ===== FIM DO COPIADO =====
}  // namespace output
}  // namespace st_desentortar

// ---------------------------------------------------------------------------
// LIGACAO: a funcao em C chamada pelo Python (core/desentortar_scantailor.py).
// ---------------------------------------------------------------------------
namespace {
// A pagina do Python numa QImage, no formato em que o ScanTailor carrega um PNG
// (o mesmo montarImagem de saida.cpp): canais 1 = Indexed8 com paleta cinza;
// canais 3 = azul, verde, vermelho (OpenCV) -> Format_RGB32. Copia os pontos.
QImage montarPagina(const unsigned char* pixels, int largura, int altura, int passo, int canais) {
  if (canais == 1) {
    QImage img(largura, altura, QImage::Format_Indexed8);
    if (img.isNull()) {
      throw std::bad_alloc();
    }
    img.setColorTable(createGrayscalePalette());
    for (int y = 0; y < altura; ++y) {
      std::memcpy(img.scanLine(y), pixels + static_cast<size_t>(y) * passo, static_cast<size_t>(largura));
    }
    return img;
  }
  const QImage embrulho(pixels, largura, altura, passo, QImage::Format_BGR888);
  QImage img = embrulho.convertToFormat(QImage::Format_RGB32);
  if (img.isNull()) {
    throw std::bad_alloc();
  }
  return img;
}
}  // namespace

extern "C" {

ST_FERRAMENTAS_API int st_ferramentas_desentortar(const unsigned char* pixels,
                                                  int largura,
                                                  int altura,
                                                  int passo,
                                                  int canais,
                                                  int dpiX,
                                                  int dpiY,
                                                  int modo,
                                                  int lado,
                                                  double profundidade,
                                                  int endireitarDepois,
                                                  int corteX,
                                                  int corteY,
                                                  int corteLargura,
                                                  int corteAltura,
                                                  int conteudoX,
                                                  int conteudoY,
                                                  int conteudoLargura,
                                                  int conteudoAltura,
                                                  unsigned char* saida,
                                                  int passoSaida,
                                                  int* achouCurvas,
                                                  double* anguloDepois,
                                                  char* erro,
                                                  int tamanhoErro) {
  return st_ferramentas::protegido(erro, tamanhoErro, [&]() -> int {
    if (!pixels || !saida || !achouCurvas || !anguloDepois || largura <= 0 || altura <= 0
        || (canais != 1 && canais != 3) || passo < largura * canais
        || passoSaida < ((corteLargura == 0 || corteAltura == 0) ? largura : corteLargura) * canais || dpiX <= 0
        || dpiY <= 0 || (modo != ::output::AUTO && modo != ::output::MARGINAL) || lado < PageId::SINGLE_PAGE
        || lado > PageId::RIGHT_PAGE || !(profundidade >= 1.0 && profundidade <= 3.0) || conteudoLargura < 0
        || conteudoAltura < 0 || corteLargura < 0 || corteAltura < 0 || corteX < 0 || corteY < 0
        || corteX + corteLargura > largura || corteY + corteAltura > altura) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_FERRAMENTAS_ERRO_PARAMETRO;
    }
    const QImage pagina = montarPagina(pixels, largura, altura, passo, canais);
    // O corte (vazio = a pagina inteira): o tamanho da saida (versao 8).
    const QRect corte = (corteLargura == 0 || corteAltura == 0)
                            ? QRect(0, 0, largura, altura)
                            : QRect(corteX, corteY, corteLargura, corteAltura);
    st_desentortar::output::OutputGenerator::Processor processador(
        pagina, Dpi(dpiX, dpiY), static_cast<::output::DewarpingMode>(modo), static_cast<PageId::SubPage>(lado),
        corte, QRect(conteudoX, conteudoY, conteudoLargura, conteudoAltura), endireitarDepois != 0);
    bool achou = false;
    double angulo = 0.0;
    QImage resultado = processador.desentortar(::output::DepthPerception(profundidade), &achou, &angulo);
    resultado = resultado.convertToFormat(canais == 1 ? QImage::Format_Grayscale8 : QImage::Format_RGB888);
    if (resultado.isNull() || resultado.width() != corte.width() || resultado.height() != corte.height()) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "resultado de tamanho inesperado");
      return ST_FERRAMENTAS_ERRO_INTERNO;
    }
    // A saida tem o tamanho do corte (passoSaida >= corteLargura * canais).
    for (int y = 0; y < corte.height(); ++y) {
      const unsigned char* origem = resultado.constScanLine(y);
      unsigned char* destino = saida + static_cast<size_t>(y) * passoSaida;
      if (canais == 1) {
        std::memcpy(destino, origem, static_cast<size_t>(corte.width()));
        continue;
      }
      for (int x = 0; x < corte.width(); ++x) {  // RGB -> azul, verde, vermelho (a ordem do OpenCV)
        destino[3 * x] = origem[3 * x + 2];
        destino[3 * x + 1] = origem[3 * x + 1];
        destino[3 * x + 2] = origem[3 * x];
      }
    }
    *achouCurvas = achou ? 1 : 0;
    *anguloDepois = angulo;
    return ST_FERRAMENTAS_OK;
  });
}

}  // extern "C"
