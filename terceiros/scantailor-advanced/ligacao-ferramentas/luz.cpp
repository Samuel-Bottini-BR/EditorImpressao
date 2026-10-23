// Igualar a luz e suavizar (item 2.17): as contas do ScanTailor Advanced, chamadas do Python.
//
// Copyright (C) 2019  Joseph Artsimovich <joseph.artsimovich@gmail.com>, 4lex4 <4lex49@zoho.com>
//   (todas as funcoes entre as marcas "COPIADO SEM MUDANCA" abaixo)
// Copyright (C) 2026  Editor de Impressao (so a ligacao: a classe de apoio e as funcoes em C)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// O QUE FAZ (o que o ScanTailor faz na saida, OutputGenerator.cpp, processWithoutDewarping)
//   - IGUALAR A LUZ ("Equalize illumination"): transformToWorkingCs(true) -
//     acha o fundo da pagina como uma superficie suave (EstimateBackground),
//     divide o cinza por ele (RaiseAboveBackground) e, na pagina colorida,
//     ajusta o brilho de cada ponto pelo cinza igualado (adjustBrightnessGrayscale).
//   - SUAVIZAR O CINZA (Savitzky-Golay, smoothToGrayscale): antes de binarizar,
//     com a janela e o grau que o ScanTailor escolhe pelo DPI.
//   - SUAVIZAR O PRETO E BRANCO (morphologicalSmoothInPlace): depois de
//     binarizar, tira os dentinhos e os buraquinhos da borda das letras.
//   - FILTRO DE WIENER (wienerColorFilterInPlace): tira o chuvisco da imagem
//     colorida, com o coeficiente dado (0 = nada, o de fabrica do ScanTailor).
//   As funcoes vem copiadas letra por letra de ../referencia/OutputGenerator.cpp
//   (v1.2.1), entre as marcas; o teste tests/test_luz_scantailor.py confere.
//
// O QUE E SEGURO MUDAR: so a ligacao (fora das marcas).
// O QUE E ARRISCADO
//   - A imagem vira QImage Format_RGB32 (colorida) ou Indexed8 cinza, como o
//     ScanTailor carrega um PNG (igual a st_gravura.cpp): outro formato muda a
//     conversao para cinza.
//   - A area considerada para o fundo e a pagina inteira (no ScanTailor, a
//     caixa da pagina; para a pagina ja cortada pelo programa, e a imagem toda).
//   - A classe de apoio tem o MESMO NOME da do ScanTailor
//     (output::OutputGenerator::Processor), para as funcoes copiadas compilarem
//     sem mudar uma letra. Nao pode haver outra cola nesta DLL com o mesmo nome
//     no mesmo namespace: na juncao de 23/10/2026 (com o saida.cpp do 2.8 e o
//     desentortar.cpp do 2.12, que tem a mesma classe) tudo daqui foi posto
//     dentro de `namespace st_luz`, como o desentortar.cpp faz com o
//     st_desentortar. Nada dentro das marcas mudou.

#include <AdjustBrightness.h>
#include <BinaryImage.h>
#include <Dpi.h>
#include <GrayImage.h>
#include <GrayRasterOp.h>
#include <Grayscale.h>
#include <Morphology.h>
#include <PolynomialSurface.h>
#include <SavGolFilter.h>
#include <Transform.h>
#include <WienerFilter.h>

#include <QColor>
#include <QImage>
#include <QPolygonF>
#include <QRect>
#include <QRectF>
#include <QSize>
#include <QTransform>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <vector>

#include "DebugImages.h"
#include "EstimateBackground.h"
#include "NullTaskStatus.h"
#include "TaskStatus.h"
#include "comum.h"
#include "st_ferramentas.h"

using namespace imageproc;

namespace st_luz {  // juncao de 23/10/2026: separa da classe de mesmo nome do saida.cpp
namespace output {
// ---------------------------------------------------------------------------
// LIGACAO: a classe que faz o papel de OutputGenerator::Processor. So os
// membros que as funcoes copiadas usam, com o mesmo nome e o mesmo sentido.
// ---------------------------------------------------------------------------
class OutputGenerator {
 public:
  class Processor;
};

class OutputGenerator::Processor {
 public:
  explicit Processor(const QImage& image);

  QImage igualar() const { return transformToWorkingCs(true); }

  void suavizarPretoEBranco(BinaryImage& bw) const { morphologicalSmoothInPlace(bw); }

 private:
  GrayImage normalizeIlluminationGray(const QImage& input,
                                      const QPolygonF& areaToConsider,
                                      const QTransform& xform,
                                      const QRect& targetRect,
                                      GrayImage* background = nullptr) const;

  QImage transformToWorkingCs(bool normalize) const;

  void morphologicalSmoothInPlace(BinaryImage& binImg) const;

  struct XformDaLigacao {
    QTransform m_transform;
    const QTransform& transform() const { return m_transform; }
  };

  XformDaLigacao m_xform;
  QRect m_workingBoundingRect;
  QPolygonF m_preCropAreaInOriginalCs;
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
// ===== COPIADO SEM MUDANCA (linhas 1004-1050) =====
void hitMissReplaceAllDirections(BinaryImage& img,
                                 const char* const pattern,
                                 const int patternWidth,
                                 const int patternHeight) {
  hitMissReplaceInPlace(img, WHITE, pattern, patternWidth, patternHeight);

  std::vector<char> patternData(static_cast<unsigned long long int>(patternWidth * patternHeight), ' ');
  char* const newPattern = &patternData[0];

  // Rotate 90 degrees clockwise.
  const char* p = pattern;
  int newWidth = patternHeight;
  int newHeight = patternWidth;
  for (int y = 0; y < patternHeight; ++y) {
    for (int x = 0; x < patternWidth; ++x, ++p) {
      const int newX = patternHeight - 1 - y;
      const int newY = x;
      newPattern[newY * newWidth + newX] = *p;
    }
  }
  hitMissReplaceInPlace(img, WHITE, newPattern, newWidth, newHeight);

  // Rotate upside down.
  p = pattern;
  newWidth = patternWidth;
  newHeight = patternHeight;
  for (int y = 0; y < patternHeight; ++y) {
    for (int x = 0; x < patternWidth; ++x, ++p) {
      const int newX = patternWidth - 1 - x;
      const int newY = patternHeight - 1 - y;
      newPattern[newY * newWidth + newX] = *p;
    }
  }
  hitMissReplaceInPlace(img, WHITE, newPattern, newWidth, newHeight);
  // Rotate 90 degrees counter-clockwise.
  p = pattern;
  newWidth = patternHeight;
  newHeight = patternWidth;
  for (int y = 0; y < patternHeight; ++y) {
    for (int x = 0; x < patternWidth; ++x, ++p) {
      const int newX = y;
      const int newY = patternWidth - 1 - x;
      newPattern[newY * newWidth + newX] = *p;
    }
  }
  hitMissReplaceInPlace(img, WHITE, newPattern, newWidth, newHeight);
}
// ===== FIM DO COPIADO =====
}  // namespace

// smoothToGrayscale mora no namespace sem nome do original; aqui fica
// visivel para a funcao em C (o corpo e o mesmo, letra por letra).
// ===== COPIADO SEM MUDANCA (linhas 1178-1196) =====
QImage smoothToGrayscale(const QImage& src, const Dpi& dpi) {
  const int minDpi = std::min(dpi.horizontal(), dpi.vertical());
  int window;
  int degree;
  if (minDpi <= 200) {
    window = 5;
    degree = 3;
  } else if (minDpi <= 400) {
    window = 7;
    degree = 4;
  } else if (minDpi <= 800) {
    window = 11;
    degree = 4;
  } else {
    window = 11;
    degree = 2;
  }
  return savGolFilter(src, QSize(window, window), degree, degree);
}
// ===== FIM DO COPIADO =====

// ---------------------------------------------------------------------------
// LIGACAO: construtor. A pagina ja esta no sistema de trabalho (identidade),
// a area considerada e a imagem inteira, nada cai fora dela (a cor de fora,
// branca, nunca e usada). Cinza: toGrayscale() do ScanTailor (FilterData.cpp).
// ---------------------------------------------------------------------------
OutputGenerator::Processor::Processor(const QImage& image)
    : m_workingBoundingRect(image.rect()),
      m_inputOrigImage(image),
      m_inputGrayImage(toGrayscale(image)),
      m_colorOriginal(!image.allGray()),
      m_status(m_nullStatus),
      m_dbg(nullptr),
      m_outsideBackgroundColor(Qt::white) {
  m_preCropAreaInOriginalCs = QPolygonF(QRectF(image.rect()));
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

// ===== COPIADO SEM MUDANCA (linhas 2220-2302) =====
void OutputGenerator::Processor::morphologicalSmoothInPlace(BinaryImage& binImg) const {
  // When removing black noise, remove small ones first.

  {
    const char pattern[]
        = "XXX"
          " - "
          "   ";
    hitMissReplaceAllDirections(binImg, pattern, 3, 3);
  }

  m_status.throwIfCancelled();

  {
    const char pattern[]
        = "X ?"
          "X  "
          "X- "
          "X- "
          "X  "
          "X ?";
    hitMissReplaceAllDirections(binImg, pattern, 3, 6);
  }

  m_status.throwIfCancelled();

  {
    const char pattern[]
        = "X ?"
          "X ?"
          "X  "
          "X- "
          "X- "
          "X- "
          "X  "
          "X ?"
          "X ?";
    hitMissReplaceAllDirections(binImg, pattern, 3, 9);
  }

  m_status.throwIfCancelled();

  {
    const char pattern[]
        = "XX?"
          "XX?"
          "XX "
          "X+ "
          "X+ "
          "X+ "
          "XX "
          "XX?"
          "XX?";
    hitMissReplaceAllDirections(binImg, pattern, 3, 9);
  }

  m_status.throwIfCancelled();

  {
    const char pattern[]
        = "XX?"
          "XX "
          "X+ "
          "X+ "
          "XX "
          "XX?";
    hitMissReplaceAllDirections(binImg, pattern, 3, 6);
  }

  m_status.throwIfCancelled();

  {
    const char pattern[]
        = "   "
          "X+X"
          "XXX";
    hitMissReplaceAllDirections(binImg, pattern, 3, 3);
  }

  if (m_dbg) {
    m_dbg->add(binImg, "edges_smoothed");
  }
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
}  // namespace st_luz

// ---------------------------------------------------------------------------
// LIGACAO: as funcoes em C chamadas pelo Python (core/luz_scantailor.py).
// ---------------------------------------------------------------------------
namespace {
// A imagem como o ScanTailor carrega um PNG (igual a st_gravura.cpp):
// colorida em Format_RGB32 (a entrada e azul, verde, vermelho: a do OpenCV);
// cinza em Indexed8 com paleta cinza. Copia os pixels.
QImage montarImagem(const unsigned char* pixels, int largura, int altura, int passo, int canais) {
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

// Devolve a imagem ao Python no mesmo formato da entrada (canais 1 ou 3, BGR).
void escreverImagem(const QImage& img, int canais, unsigned char* saida, int passoSaida) {
  if (canais == 1) {
    const QImage cinza = (img.format() == QImage::Format_Indexed8 || img.format() == QImage::Format_Grayscale8)
                             ? img
                             : QImage(toGrayscale(img));
    for (int y = 0; y < cinza.height(); ++y) {
      std::memcpy(saida + static_cast<size_t>(y) * passoSaida, cinza.constScanLine(y),
                  static_cast<size_t>(cinza.width()));
    }
    return;
  }
  const QImage bgr = img.convertToFormat(QImage::Format_BGR888);
  for (int y = 0; y < bgr.height(); ++y) {
    std::memcpy(saida + static_cast<size_t>(y) * passoSaida, bgr.constScanLine(y),
                static_cast<size_t>(bgr.width()) * 3);
  }
}

bool parametrosValidos(const unsigned char* pixels, int largura, int altura, int passo, int canais,
                       const unsigned char* saida, int passoSaida) {
  return pixels && saida && largura > 0 && altura > 0 && (canais == 1 || canais == 3)
         && passo >= largura * canais && passoSaida >= largura * canais;
}
}  // namespace

extern "C" {

ST_FERRAMENTAS_API int st_ferramentas_igualar_luz(const unsigned char* pixels,
                                                  int largura,
                                                  int altura,
                                                  int passo,
                                                  int canais,
                                                  unsigned char* saida,
                                                  int passoSaida,
                                                  char* erro,
                                                  int tamanhoErro) {
  return st_ferramentas::protegido(erro, tamanhoErro, [&]() -> int {
    if (!parametrosValidos(pixels, largura, altura, passo, canais, saida, passoSaida)) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_FERRAMENTAS_ERRO_PARAMETRO;
    }
    const st_luz::output::OutputGenerator::Processor processador(montarImagem(pixels, largura, altura, passo, canais));
    escreverImagem(processador.igualar(), canais, saida, passoSaida);
    return ST_FERRAMENTAS_OK;
  });
}

ST_FERRAMENTAS_API int st_ferramentas_suavizar_cinza(const unsigned char* pixels,
                                                     int largura,
                                                     int altura,
                                                     int passo,
                                                     int canais,
                                                     int dpiX,
                                                     int dpiY,
                                                     unsigned char* saida,
                                                     int passoSaida,
                                                     char* erro,
                                                     int tamanhoErro) {
  return st_ferramentas::protegido(erro, tamanhoErro, [&]() -> int {
    // a saida e sempre cinza (1 byte por ponto), qualquer que seja a entrada
    if (!pixels || !saida || largura <= 0 || altura <= 0 || (canais != 1 && canais != 3)
        || passo < largura * canais || passoSaida < largura || dpiX <= 0 || dpiY <= 0) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_FERRAMENTAS_ERRO_PARAMETRO;
    }
    const QImage suave
        = st_luz::output::smoothToGrayscale(montarImagem(pixels, largura, altura, passo, canais), Dpi(dpiX, dpiY));
    escreverImagem(suave, 1, saida, passoSaida);
    return ST_FERRAMENTAS_OK;
  });
}

ST_FERRAMENTAS_API int st_ferramentas_suavizar_preto_e_branco(const unsigned char* entrada,
                                                              int largura,
                                                              int altura,
                                                              int passoEntrada,
                                                              unsigned char* saida,
                                                              int passoSaida,
                                                              char* erro,
                                                              int tamanhoErro) {
  return st_ferramentas::protegido(erro, tamanhoErro, [&]() -> int {
    if (!entrada || !saida || largura <= 0 || altura <= 0 || passoEntrada < largura || passoSaida < largura) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_FERRAMENTAS_ERRO_PARAMETRO;
    }
    BinaryImage bw = st_ferramentas::binariaDeBytes(entrada, largura, altura, passoEntrada);
    const st_luz::output::OutputGenerator::Processor processador(QImage(1, 1, QImage::Format_RGB32));
    processador.suavizarPretoEBranco(bw);
    st_ferramentas::bytesDeBinaria(bw, saida, passoSaida);
    return ST_FERRAMENTAS_OK;
  });
}

ST_FERRAMENTAS_API int st_ferramentas_wiener(const unsigned char* pixels,
                                             int largura,
                                             int altura,
                                             int passo,
                                             int canais,
                                             int janela,
                                             double coeficiente,
                                             unsigned char* saida,
                                             int passoSaida,
                                             char* erro,
                                             int tamanhoErro) {
  return st_ferramentas::protegido(erro, tamanhoErro, [&]() -> int {
    if (!parametrosValidos(pixels, largura, altura, passo, canais, saida, passoSaida) || janela < 3
        || !(coeficiente >= 0.0 && coeficiente <= 1.0)) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_FERRAMENTAS_ERRO_PARAMETRO;
    }
    QImage img = montarImagem(pixels, largura, altura, passo, canais);
    // o que o ScanTailor faz em processWithoutDewarping, linhas 1288-1291
    wienerColorFilterInPlace(img, QSize(janela, janela), coeficiente);
    escreverImagem(img, canais, saida, passoSaida);
    return ST_FERRAMENTAS_OK;
  });
}

}  // extern "C"
