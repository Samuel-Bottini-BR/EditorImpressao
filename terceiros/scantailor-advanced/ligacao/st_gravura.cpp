// Detector de gravura do ScanTailor Advanced, como DLL chamada por ctypes.
//
// Copyright (C) 2019  Joseph Artsimovich <joseph.artsimovich@gmail.com>, 4lex4 <4lex49@zoho.com>
//   (todas as funcoes entre as marcas "COPIADO SEM MUDANCA" abaixo)
// Copyright (C) 2026  Editor de Impressao (so a ligacao: a classe de apoio, process(),
//   processPictureZones() sem as zonas da janela, e a funcao em C no fim do arquivo)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// O QUE E ESTE ARQUIVO
//   O ScanTailor Advanced acha as gravuras ("picture zones" do modo Misto) dentro de
//   src/core/filters/output/OutputGenerator.cpp, em metodos da classe interna
//   OutputGenerator::Processor. Aquela classe depende da janela inteira (projeto,
//   configuracoes, zonas desenhadas a mao, imagens de depuracao). Aqui ela e
//   trocada por uma classe com o MESMO NOME e so os membros que as funcoes do
//   detector usam; as funcoes em si vem copiadas letra por letra de
//   ../referencia/OutputGenerator.cpp (v1.2.1), entre as marcas
//   "COPIADO SEM MUDANCA (linhas X-Y)". O teste
//   tests/test_gravura_scantailor.py confere que cada bloco copiado continua
//   identico ao original.
//
// O QUE E SEGURO MUDAR
//   So a ligacao (fora das marcas). Mudar qualquer coisa dentro das marcas deixa
//   de ser "o codigo original do ScanTailor" e quebra o teste de copia fiel.
//
// O QUE E ARRISCADO
//   - A ordem das etapas em process() espelha processImpl() e
//     processWithoutDewarping() do original (modo Misto, sem desentortar):
//     trocar a ordem muda a mascara.
//   - A imagem de entrada vira QImage::Format_RGB32 (colorida) ou Indexed8 com
//     paleta cinza (cinza), como o ScanTailor carrega um PNG. Outro formato pode
//     mudar a conversao para cinza.
//   - O filtro de Wiener do original fica de fora porque no padrao do ScanTailor
//     o coeficiente e 0 (nao faz nada; ColorCommonOptions.cpp).
//   - A pagina e sempre "preto no branco". O ScanTailor tem uma deteccao
//     automatica (BlackOnWhiteEstimator) que as vezes decide que a pagina e
//     "claro no escuro" e a inverte; ela nao foi trazida (na Horas 11 de 24/09
//     foi essa inversao que estragou a iluminura).

#include "st_gravura.h"

#include <AdjustBrightness.h>
#include <BackgroundColorCalculator.h>
#include <BinaryImage.h>
#include <BinaryThreshold.h>
#include <Dpi.h>
#include <GrayImage.h>
#include <GrayRasterOp.h>
#include <Grayscale.h>
#include <Morphology.h>
#include <PolygonRasterizer.h>
#include <PolynomialSurface.h>
#include <Scale.h>
#include <SeedFill.h>
#include <Transform.h>

#include <QColor>
#include <QImage>
#include <QPolygonF>
#include <QRect>
#include <QRectF>
#include <QSize>
#include <QTransform>
#include <algorithm>
#include <cstring>
#include <exception>
#include <new>
#include <stdexcept>
#include <vector>

#include "DebugImages.h"
#include "EstimateBackground.h"
#include "NullTaskStatus.h"
#include "PictureShapeOptions.h"
#include "TaskStatus.h"

using namespace imageproc;

namespace output {
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
  // image: a pagina (sistema de coordenadas "original" do ScanTailor).
  // xform: da pagina para o sistema de trabalho (no original, ImageTransformation::transform()).
  // workingRect: o retangulo de trabalho, ja no sistema de trabalho (m_workingBoundingRect).
  // dpi: o DPI do sistema de trabalho (no original, o DPI de saida).
  Processor(const QImage& image,
            const QTransform& xform,
            const QRect& workingRect,
            const Dpi& dpi,
            const PictureShapeOptions& pictureShapeOptions,
            bool normalizeIllumination);

  // As etapas de processImpl() + processWithoutDewarping() (modo Misto) ate a mascara
  // de gravuras ("bwMask" logo depois de processPictureZones()). Branco = gravura.
  BinaryImage process();

 private:
  GrayImage normalizeIlluminationGray(const QImage& input,
                                      const QPolygonF& areaToConsider,
                                      const QTransform& xform,
                                      const QRect& targetRect,
                                      GrayImage* background = nullptr) const;

  GrayImage detectPictures(const GrayImage& input300dpi) const;

  BinaryImage estimateBinarizationMask(const GrayImage& graySource,
                                       const QRect& sourceRect,
                                       const QRect& sourceSubRect) const;

  void processPictureZones(BinaryImage& mask, const GrayImage& image);

  QImage transformToWorkingCs(bool normalize) const;

  // No original m_xform e um ImageTransformation; as funcoes copiadas so chamam
  // m_xform.transform().
  struct XformDaLigacao {
    QTransform m_transform;
    const QTransform& transform() const { return m_transform; }
  };

  XformDaLigacao m_xform;
  Dpi m_dpi;
  PictureShapeOptions m_pictureShapeOptions;
  bool m_normalizeIllumination;
  QRect m_workingBoundingRect;
  QPolygonF m_preCropAreaInOriginalCs;
  QPolygonF m_outCropAreaInOriginalCs;
  QImage m_inputOrigImage;
  GrayImage m_inputGrayImage;
  bool m_colorOriginal;
  NullTaskStatus m_nullStatus;
  const TaskStatus& m_status;
  DebugImages* const m_dbg;
  QColor m_outsideBackgroundColor;
};

namespace {
// ===== COPIADO SEM MUDANCA (linhas 366-386) =====
struct RaiseAboveBackground {
  static uint8_t transform(uint8_t src, uint8_t dst) {
    // src: orig
    // dst: background (dst >= src)
    if (dst - src < 1) {
      return 0xff;
    }
    const unsigned orig = src;
    const unsigned background = dst;
    return static_cast<uint8_t>((orig * 255 + background / 2) / background);
  }
};

struct CombineInverted {
  static uint8_t transform(uint8_t src, uint8_t dst) {
    const unsigned dilated = dst;
    const unsigned eroded = src;
    const unsigned res = 255 - (255 - dilated) * eroded / 255;
    return static_cast<uint8_t>(res);
  }
};
// ===== FIM DO COPIADO =====

// ===== COPIADO SEM MUDANCA (linhas 782-985) =====
const int MultiplyDeBruijnBitPosition[32] = {0,  1,  28, 2,  29, 14, 24, 3, 30, 22, 20, 15, 25, 17, 4,  8,
                                             31, 27, 13, 23, 21, 19, 16, 7, 26, 12, 18, 6,  11, 5,  10, 9};

const int MultiplyDeBruijnBitPosition2[32] = {0, 9,  1,  10, 13, 21, 2,  29, 11, 14, 16, 18, 22, 25, 3, 30,
                                              8, 12, 20, 28, 15, 17, 24, 7,  19, 27, 23, 6,  26, 5,  4, 31};

/**
 * aka "Count the consecutive zero bits (trailing) on the right with multiply and lookup"
 * from Bit Twiddling Hacks By Sean Eron Anderson
 *
 * https://graphics.stanford.edu/~seander/bithacks.html#ZerosOnRightMultLookup
 */
inline int countConsecutiveZeroBitsTrailing(uint32_t v) {
  return MultiplyDeBruijnBitPosition[((uint32_t) ((v & -signed(v)) * 0x077CB531U)) >> 27];
}

/**
 * aka "Find the log base 2 of an N-bit integer in O(lg(N)) operations with multiply and lookup"
 * from Bit Twiddling Hacks By Sean Eron Anderson
 *
 * https://graphics.stanford.edu/~seander/bithacks.html#IntegerLogDeBruijn
 */
inline int findPositionOfTheHighestBitSet(uint32_t v) {
  v |= v >> 1;  // first round down to one less than a power of 2
  v |= v >> 2;
  v |= v >> 4;
  v |= v >> 8;
  v |= v >> 16;
  return MultiplyDeBruijnBitPosition2[(uint32_t) (v * 0x07C4ACDDU) >> 27];
}

std::vector<QRect> findRectAreas(const BinaryImage& mask, BWColor contentColor, int sensitivity) {
  if (mask.isNull()) {
    return {};
  }

  std::vector<QRect> areas;

  const int w = mask.width();
  const int h = mask.height();
  const int wpl = mask.wordsPerLine();
  const int lastWordIdx = (w - 1) >> 5;
  const int lastWordBits = w - (lastWordIdx << 5);
  const int lastWordUnusedBits = 32 - lastWordBits;
  const uint32_t lastWordMask = ~uint32_t(0) << lastWordUnusedBits;
  const uint32_t modifier = (contentColor == WHITE) ? ~uint32_t(0) : 0;
  const uint32_t* const data = mask.data();

  const uint32_t* line = data;
  // create list of filled continuous blocks on each line
  for (int y = 0; y < h; ++y, line += wpl) {
    QRect area;
    area.setTop(y);
    area.setBottom(y);
    bool areaFound = false;
    for (int i = 0; i <= lastWordIdx; ++i) {
      uint32_t word = line[i] ^ modifier;
      if (i == lastWordIdx) {
        // The last (possibly incomplete) word.
        word &= lastWordMask;
      }
      if (word) {
        if (!areaFound) {
          area.setLeft((i << 5) + 31 - findPositionOfTheHighestBitSet(~line[i]));
          areaFound = true;
        }
        area.setRight(((i + 1) << 5) - 1);
      } else {
        if (areaFound) {
          uint32_t v = line[i - 1];
          if (v) {
            area.setRight(area.right() - countConsecutiveZeroBitsTrailing(~v));
          }
          areas.emplace_back(area);
          areaFound = false;
        }
      }
    }
    if (areaFound) {
      uint32_t v = line[lastWordIdx];
      if (v) {
        area.setRight(area.right() - countConsecutiveZeroBitsTrailing(~v));
      }
      areas.emplace_back(area);
    }
  }

  // join adjacent blocks of areas
  bool join = true;
  int overlap = 16;
  while (join) {
    join = false;
    std::vector<QRect> tmp;
    for (QRect area : areas) {
      // take an area and try to join with something in tmp
      QRect enlArea(area.adjusted(-overlap, -overlap, overlap, overlap));
      bool intersected = false;
      std::vector<QRect> tmp2;
      for (QRect ta : tmp) {
        QRect enlTA(ta.adjusted(-overlap, -overlap, overlap, overlap));
        if (enlArea.intersects(enlTA)) {
          intersected = true;
          join = true;
          tmp2.push_back(area.united(ta));
        } else {
          tmp2.push_back(ta);
        }
      }
      if (!intersected) {
        tmp2.push_back(area);
      }
      tmp = tmp2;
    }
    areas = tmp;
  }

  const auto percent = (float) (sensitivity / 100.);
  if (percent < 1.) {
    for (QRect& area : areas) {
      int wordWidth = area.width() >> 5;

      int left = area.left();
      int leftWord = left >> 5;
      int right = area.x() + area.width();
      int rightWord = right >> 5;
      int top = area.top();
      int bottom = area.bottom();

      const uint32_t* pdata = mask.data();

      const auto criterium = (int) (area.width() * percent);
      const auto criteriumWord = (int) (wordWidth * percent);

      // cut the dirty upper lines
      for (int y = top; y < bottom; y++) {
        line = pdata + wpl * y;

        int mword = 0;

        for (int k = leftWord; k < rightWord; k++) {
          if (!line[k]) {
            mword++;  // count the totally white words
          }
        }

        if (mword > criteriumWord) {
          area.setTop(y);
          break;
        }
      }

      // cut the dirty bottom lines
      for (int y = bottom; y > top; y--) {
        line = pdata + wpl * y;

        int mword = 0;

        for (int k = leftWord; k < rightWord; k++) {
          if (!line[k]) {
            mword++;
          }
        }

        if (mword > criteriumWord) {
          area.setBottom(y);
          break;
        }
      }

      for (int x = left; x < right; x++) {
        int mword = 0;

        for (int y = top; y < bottom; y++) {
          if (WHITE == mask.getPixel(x, y)) {
            mword++;
          }
        }

        if (mword > criterium) {
          area.setLeft(x);
          break;
        }
      }

      for (int x = right; x > left; x--) {
        int mword = 0;

        for (int y = top; y < bottom; y++) {
          if (WHITE == mask.getPixel(x, y)) {
            mword++;
          }
        }

        if (mword > criterium) {
          area.setRight(x);
          break;
        }
      }

      area = area.intersected(mask.rect());
    }
  }
  return areas;
}
// ===== FIM DO COPIADO =====

// ===== COPIADO SEM MUDANCA (linhas 1206-1212) =====
QSize to300dpi(const QSize& size, const Dpi& sourceDpi) {
  const double hscale = 300.0 / sourceDpi.horizontal();
  const double vscale = 300.0 / sourceDpi.vertical();
  const int width = qRound(size.width() * hscale);
  const int height = qRound(size.height() * vscale);
  return QSize(std::max(1, width), std::max(1, height));
}
// ===== FIM DO COPIADO =====
}  // namespace

// ---------------------------------------------------------------------------
// LIGACAO: construtor. Faz o que o original faz em initParams(), calcAreas() e
// initFilterData() para as partes que o detector usa.
//  - Area da pagina a considerar (m_preCropAreaInOriginalCs) e area de corte
//    (m_outCropAreaInOriginalCs): a imagem inteira. No ScanTailor e a caixa da
//    pagina; para uma pagina ja cortada pelo nosso programa, e a imagem toda.
//  - Cinza: toGrayscale() do proprio ScanTailor (FilterData.cpp).
//  - "Preto no branco": sempre (padrao do ScanTailor para paginas impressas).
// ---------------------------------------------------------------------------
OutputGenerator::Processor::Processor(const QImage& image,
                                      const QTransform& xform,
                                      const QRect& workingRect,
                                      const Dpi& dpi,
                                      const PictureShapeOptions& pictureShapeOptions,
                                      const bool normalizeIllumination)
    : m_dpi(dpi),
      m_pictureShapeOptions(pictureShapeOptions),
      m_normalizeIllumination(normalizeIllumination),
      m_workingBoundingRect(workingRect),
      m_inputOrigImage(image),
      m_inputGrayImage(toGrayscale(image)),
      m_colorOriginal(false),
      m_status(m_nullStatus),
      m_dbg(nullptr) {
  m_xform.m_transform = xform;
  m_preCropAreaInOriginalCs = QPolygonF(QRectF(image.rect()));
  m_outCropAreaInOriginalCs = m_preCropAreaInOriginalCs;
  m_colorOriginal = !m_inputOrigImage.allGray();
}

// ---------------------------------------------------------------------------
// LIGACAO: process(). Mesma ordem do original:
//   processImpl():             cor dominante do fundo (so usada fora da pagina);
//   processWithoutDewarping(): transformToWorkingCs(normalizar) -> [Wiener, coef. 0 = nada]
//                              -> bwMask preto -> processPictureZones(bwMask, GrayImage(...)).
//
// Atalho (nao muda o resultado): a cor dominante do fundo so pinta os pontos do
// retangulo de trabalho que caem FORA da pagina. Sem transformacao e com o
// retangulo dentro da pagina, nenhum ponto cai fora, e a conta (~0,1 s por
// pagina) e pulada. A cor posta no lugar e opaca, como a do original, para
// transform() seguir o mesmo caminho (RGB32) do ScanTailor.
// ---------------------------------------------------------------------------
BinaryImage OutputGenerator::Processor::process() {
  const bool nadaCaiForaDaPagina
      = m_xform.transform().isIdentity() && m_inputOrigImage.rect().contains(m_workingBoundingRect);
  if (nadaCaiForaDaPagina) {
    m_outsideBackgroundColor = QColor(Qt::white);
  } else {
    m_outsideBackgroundColor = BackgroundColorCalculator::calcDominantBackgroundColor(
        m_colorOriginal ? m_inputOrigImage : m_inputGrayImage, m_outCropAreaInOriginalCs);
  }

  QImage maybeNormalized = transformToWorkingCs(m_normalizeIllumination);
  m_status.throwIfCancelled();

  BinaryImage bwMask(m_workingBoundingRect.size(), BLACK);
  processPictureZones(bwMask, GrayImage(maybeNormalized));
  return bwMask;
}

// ---------------------------------------------------------------------------
// LIGACAO: processPictureZones() sem as zonas da janela (original: linhas 2540-2569).
// Forma livre: igual ao original (estimateBinarizationMask).
// Forma retangular: o original acha os retangulos com findRectAreas(), guarda cada
// um como zona "pintar" (ZONEPAINTER2) e depois modifyBinarizationMask() pinta a
// zona de branco na mascara. Aqui os retangulos sao pintados direto na mascara,
// com o mesmo PolygonRasterizer.
// ---------------------------------------------------------------------------
void OutputGenerator::Processor::processPictureZones(BinaryImage& mask, const GrayImage& image) {
  if (m_pictureShapeOptions.getPictureShape() != OFF_SHAPE) {
    mask = estimateBinarizationMask(image, m_workingBoundingRect, m_workingBoundingRect);
  }
  if (m_pictureShapeOptions.getPictureShape() == RECTANGULAR_SHAPE) {
    std::vector<QRect> areas = findRectAreas(mask, WHITE, m_pictureShapeOptions.getSensitivity());
    mask.fill(BLACK);
    for (const QRect& area : areas) {
      PolygonRasterizer::fill(mask, WHITE, QPolygonF(QRectF(area)), Qt::WindingFill);
    }
  }
}

// ===== COPIADO SEM MUDANCA (linhas 1893-1926) =====
GrayImage OutputGenerator::Processor::normalizeIlluminationGray(const QImage& input,
                                                                const QPolygonF& areaToConsider,
                                                                const QTransform& xform,
                                                                const QRect& targetRect,
                                                                GrayImage* background) const {
  GrayImage toBeNormalized = transformToGray(input, xform, targetRect, OutsidePixels::assumeWeakNearest());
  if (m_dbg) {
    m_dbg->add(toBeNormalized, "toBeNormalized");
  }

  m_status.throwIfCancelled();

  QPolygonF transformedConsiderationArea = xform.map(areaToConsider);
  transformedConsiderationArea.translate(-targetRect.topLeft());

  const PolynomialSurface bgPs = estimateBackground(toBeNormalized, transformedConsiderationArea, m_status, m_dbg);
  m_status.throwIfCancelled();

  GrayImage bgImg(bgPs.render(toBeNormalized.size()));
  if (m_dbg) {
    m_dbg->add(bgImg, "background");
  }
  if (background) {
    *background = bgImg;
  }
  m_status.throwIfCancelled();

  grayRasterOp<RaiseAboveBackground>(bgImg, toBeNormalized);
  if (m_dbg) {
    m_dbg->add(bgImg, "normalized_illumination");
  }
  m_status.throwIfCancelled();
  return bgImg;
}
// ===== FIM DO COPIADO =====

// ===== COPIADO SEM MUDANCA (linhas 1928-1973) =====
BinaryImage OutputGenerator::Processor::estimateBinarizationMask(const GrayImage& graySource,
                                                                 const QRect& sourceRect,
                                                                 const QRect& sourceSubRect) const {
  assert(sourceRect.contains(sourceSubRect));

  // If we need to strip some of the margins from a grayscale
  // image, we may actually do it without copying anything.
  // We are going to construct a QImage from existing data.
  // That image won't own that data, but graySource is not
  // going anywhere, so it's fine.

  GrayImage trimmedImage;

  if (sourceRect == sourceSubRect) {
    trimmedImage = graySource;  // Shallow copy.
  } else {
    // Sub-rectangle in input image coordinates.
    QRect relativeSubrect(sourceSubRect);
    relativeSubrect.moveTopLeft(sourceSubRect.topLeft() - sourceRect.topLeft());

    const int stride = graySource.stride();
    const int offset = relativeSubrect.top() * stride + relativeSubrect.left();

    trimmedImage = GrayImage(QImage(graySource.data() + offset, relativeSubrect.width(), relativeSubrect.height(),
                                    stride, QImage::Format_Indexed8));
  }

  m_status.throwIfCancelled();

  const QSize downscaledSize(to300dpi(trimmedImage.size(), m_dpi));

  // A 300dpi version of trimmedImage.
  GrayImage downscaledInput(scaleToGray(trimmedImage, downscaledSize));
  trimmedImage = GrayImage();  // Save memory.
  m_status.throwIfCancelled();

  // Light areas indicate pictures.
  GrayImage pictureAreas(detectPictures(downscaledInput));
  downscaledInput = GrayImage();  // Save memory.
  m_status.throwIfCancelled();

  const BinaryThreshold threshold(48);
  // Scale back to original size.
  pictureAreas = scaleToGray(pictureAreas, sourceSubRect.size());
  return BinaryImage(pictureAreas, threshold);
}
// ===== FIM DO COPIADO =====

// ===== COPIADO SEM MUDANCA (linhas 2108-2184) =====
GrayImage OutputGenerator::Processor::detectPictures(const GrayImage& input300dpi) const {
  // We stretch the range of gray levels to cover the whole
  // range of [0, 255].  We do it because we want text
  // and background to be equally far from the center
  // of the whole range.  Otherwise text printed with a big
  // font will be considered a picture.
  GrayImage stretched(stretchGrayRange(input300dpi, 0.01, 0.01));
  if (m_dbg) {
    m_dbg->add(stretched, "stretched");
  }

  m_status.throwIfCancelled();

  GrayImage eroded(erodeGray(stretched, QSize(3, 3), 0x00));
  if (m_dbg) {
    m_dbg->add(eroded, "eroded");
  }

  m_status.throwIfCancelled();

  GrayImage dilated(dilateGray(stretched, QSize(3, 3), 0xff));
  if (m_dbg) {
    m_dbg->add(dilated, "dilated");
  }

  stretched = GrayImage();  // Save memory.
  m_status.throwIfCancelled();

  grayRasterOp<CombineInverted>(dilated, eroded);
  GrayImage grayGradient(dilated);
  dilated = GrayImage();
  eroded = GrayImage();
  if (m_dbg) {
    m_dbg->add(grayGradient, "grayGradient");
  }

  m_status.throwIfCancelled();

  GrayImage marker(erodeGray(grayGradient, QSize(35, 35), 0x00));
  if (m_dbg) {
    m_dbg->add(marker, "marker");
  }

  m_status.throwIfCancelled();

  seedFillGrayInPlace(marker, grayGradient, CONN8);
  GrayImage reconstructed(marker);
  marker = GrayImage();
  if (m_dbg) {
    m_dbg->add(reconstructed, "reconstructed");
  }

  m_status.throwIfCancelled();

  grayRasterOp<GRopInvert<GRopSrc>>(reconstructed, reconstructed);
  if (m_dbg) {
    m_dbg->add(reconstructed, "reconstructed_inverted");
  }

  m_status.throwIfCancelled();

  GrayImage holesFilled(createFramedImage(reconstructed.size()));
  seedFillGrayInPlace(holesFilled, reconstructed, CONN8);
  reconstructed = GrayImage();
  if (m_dbg) {
    m_dbg->add(holesFilled, "holesFilled");
  }

  if (m_pictureShapeOptions.isHigherSearchSensitivity()) {
    GrayImage stretched2(stretchGrayRange(holesFilled, 5.0, 0.01));
    if (m_dbg) {
      m_dbg->add(stretched2, "stretched2");
    }
    return stretched2;
  }
  return holesFilled;
}
// ===== FIM DO COPIADO =====

// ===== COPIADO SEM MUDANCA (linhas 2583-2606) =====
QImage OutputGenerator::Processor::transformToWorkingCs(bool normalize) const {
  QImage dst;
  if (normalize) {
    dst = normalizeIlluminationGray(m_inputGrayImage, m_preCropAreaInOriginalCs, m_xform.transform(),
                                    m_workingBoundingRect);
    if (m_colorOriginal) {
      assert(dst.format() == QImage::Format_Indexed8);
      QImage colorImg = transform(m_inputOrigImage, m_xform.transform(), m_workingBoundingRect,
                                  OutsidePixels::assumeColor(m_outsideBackgroundColor));
      adjustBrightnessGrayscale(colorImg, dst);
      dst = colorImg;
    }
  } else {
    if (!m_colorOriginal) {
      dst = transformToGray(m_inputGrayImage, m_xform.transform(), m_workingBoundingRect,
                            OutsidePixels::assumeColor(m_outsideBackgroundColor));
    } else {
      dst = transform(m_inputOrigImage, m_xform.transform(), m_workingBoundingRect,
                      OutsidePixels::assumeColor(m_outsideBackgroundColor));
    }
  }
  m_status.throwIfCancelled();
  return dst;
}
// ===== FIM DO COPIADO =====
}  // namespace output

// ---------------------------------------------------------------------------
// LIGACAO: as funcoes em C chamadas pelo Python (core/gravura_scantailor.py).
// ---------------------------------------------------------------------------
namespace {
void escreverErro(char* erro, int tamanhoErro, const char* texto) {
  if (erro && tamanhoErro > 0) {
    std::strncpy(erro, texto, static_cast<size_t>(tamanhoErro) - 1);
    erro[tamanhoErro - 1] = '\0';
  }
}

// Bytes por ponto de cada formato de entrada (ST_GRAVURA_CINZA, _RGB, _BGR).
int bytesPorPonto(int formato) {
  switch (formato) {
    case ST_GRAVURA_CINZA:
      return 1;
    case ST_GRAVURA_RGB:
    case ST_GRAVURA_BGR:
      return 3;
    default:
      return 0;
  }
}

// Monta a QImage no formato em que o ScanTailor carrega um PNG: colorida em
// Format_RGB32; cinza em Indexed8 com paleta cinza (a GrayImage do ScanTailor).
// Copia os pixels: o QImage final nao aponta para a memoria do Python.
QImage montarImagem(const unsigned char* pixels, int largura, int altura, int passo, int formato) {
  if (formato == ST_GRAVURA_CINZA) {
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
  const QImage::Format formatoQt = (formato == ST_GRAVURA_BGR) ? QImage::Format_BGR888 : QImage::Format_RGB888;
  const QImage embrulho(pixels, largura, altura, passo, formatoQt);
  QImage img = embrulho.convertToFormat(QImage::Format_RGB32);
  if (img.isNull()) {
    throw std::bad_alloc();
  }
  return img;
}
}  // namespace

extern "C" {

ST_GRAVURA_API int st_gravura_versao_api(void) {
  return ST_GRAVURA_VERSAO_API;
}

ST_GRAVURA_API const char* st_gravura_origem(void) {
  return ST_GRAVURA_ORIGEM;
}

ST_GRAVURA_API int st_gravura_detectar(const unsigned char* pixels,
                                       int largura,
                                       int altura,
                                       int passo,
                                       int formato,
                                       int dpiX,
                                       int dpiY,
                                       const double* transformacao,
                                       const int* retangulo,
                                       int normalizarIluminacao,
                                       int forma,
                                       int sensibilidade,
                                       int maisSensivel,
                                       unsigned char* mascara,
                                       int passoMascara,
                                       char* erro,
                                       int tamanhoErro) {
  try {
    if (!pixels || !mascara || largura <= 0 || altura <= 0 || dpiX <= 0 || dpiY <= 0
        || bytesPorPonto(formato) == 0 || passo < largura * bytesPorPonto(formato) || forma < 0 || forma > 2) {
      escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_GRAVURA_ERRO_PARAMETRO;
    }

    const QImage imagem = montarImagem(pixels, largura, altura, passo, formato);

    QTransform xform;  // identidade: a pagina ja esta no sistema de trabalho
    if (transformacao) {
      xform = QTransform(transformacao[0], transformacao[1], transformacao[2], transformacao[3], transformacao[4],
                         transformacao[5]);
    }
    QRect retTrabalho = xform.mapRect(QRectF(imagem.rect())).toRect();
    if (retangulo) {
      retTrabalho = QRect(retangulo[0], retangulo[1], retangulo[2], retangulo[3]);
    }
    if (retTrabalho.width() <= 0 || retTrabalho.height() <= 0 || passoMascara < retTrabalho.width()) {
      escreverErro(erro, tamanhoErro, "retangulo de trabalho invalido");
      return ST_GRAVURA_ERRO_PARAMETRO;
    }

    output::PictureShapeOptions opcoes;
    opcoes.setPictureShape(static_cast<output::PictureShape>(forma));
    opcoes.setSensitivity(sensibilidade);
    opcoes.setHigherSearchSensitivity(maisSensivel != 0);

    output::OutputGenerator::Processor processador(imagem, xform, retTrabalho, Dpi(dpiX, dpiY), opcoes,
                                                   normalizarIluminacao != 0);
    const BinaryImage bw = processador.process();

    // BinaryImage: bit 1 = preto (fundo/texto), bit 0 = branco (gravura), do bit mais alto para o mais baixo.
    const int w = bw.width();
    const int h = bw.height();
    const int wpl = bw.wordsPerLine();
    const uint32_t* linha = bw.data();
    for (int y = 0; y < h; ++y, linha += wpl) {
      unsigned char* saida = mascara + static_cast<size_t>(y) * passoMascara;
      for (int x = 0; x < w; ++x) {
        const uint32_t bit = (linha[x >> 5] >> (31 - (x & 31))) & 1u;
        saida[x] = bit ? 0 : 255;
      }
    }
    return ST_GRAVURA_OK;
  } catch (const std::bad_alloc&) {
    escreverErro(erro, tamanhoErro, "memoria insuficiente");
    return ST_GRAVURA_ERRO_MEMORIA;
  } catch (const std::exception& e) {
    escreverErro(erro, tamanhoErro, e.what());
    return ST_GRAVURA_ERRO_INTERNO;
  } catch (...) {
    escreverErro(erro, tamanhoErro, "erro desconhecido");
    return ST_GRAVURA_ERRO_INTERNO;
  }
}

}  // extern "C"
