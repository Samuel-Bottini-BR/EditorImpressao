// A saida do ScanTailor Advanced (o "Output" dele), chamada do Python: o preto e
// branco com os dez jeitos de binarizar (item 2.8 da Fase 2, 20/10/2026).
//
// Copyright (C) 2019  Joseph Artsimovich <joseph.artsimovich@gmail.com>, 4lex4 <4lex49@zoho.com>
//   (todas as funcoes entre as marcas "COPIADO SEM MUDANCA" abaixo)
// Copyright (C) 2026  Editor de Impressao (so a ligacao: a classe de apoio, preparar(),
//   pretoEBranco() e a funcao em C no fim do arquivo)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// O QUE E ESTE ARQUIVO
//   No ScanTailor, o preto e branco da pagina e feito dentro de
//   src/core/filters/output/OutputGenerator.cpp, em metodos da classe interna
//   OutputGenerator::Processor (que depende do projeto, da janela e das
//   configuracoes). Como no item 1.2 (../ligacao/st_gravura.cpp), aqui ela e
//   trocada por uma classe com o MESMO NOME e so os membros que as funcoes
//   copiadas usam; as funcoes vem copiadas letra por letra de
//   ../referencia/OutputGenerator.cpp (v1.2.1), entre as marcas
//   "COPIADO SEM MUDANCA (linhas X-Y)". O teste tests/test_preto_e_branco_scantailor.py
//   confere que cada bloco continua identico ao original.
//
// A ORDEM (a mesma de processWithoutDewarping(), modo "preto e branco", linhas 1283-1323)
//   1. transformToWorkingCs(normalizar): iguala a luz (estima o fundo e divide
//      por ele) - "Equalize illumination", LIGADO de fabrica no ScanTailor;
//   2. [filtro de Wiener: coeficiente 0 de fabrica = nao faz nada; fica de fora]
//   3. smoothToGrayscale(): suavizacao Savitzky-Golay - LIGADA de fabrica;
//   4. binarize(): um dos dez jeitos (BlackWhiteOptions), com o ajuste do limiar;
//   5. morphologicalSmoothInPlace(): suavizacao morfologica - LIGADA de fabrica.
//   Os pontinhos (Despeckle) NAO estao aqui: no programa eles sao a escolha
//   "Limpar a sujeira", que ja existe (pontinhos.cpp).
//
// O QUE E SEGURO MUDAR
//   So a ligacao (fora das marcas).
//
// O QUE E ARRISCADO
//   - Mudar qualquer coisa dentro das marcas (deixa de ser o codigo do ScanTailor
//     e quebra o teste de copia fiel).
//   - A pagina chega ja girada e cortada pelo programa: o sistema de trabalho e a
//     propria imagem (transformacao identidade, area = a imagem inteira). Por
//     isso binarize(imagem, area) do original vira binarize(imagem): no original,
//     com a area cobrindo a imagem inteira, e exatamente esse o caminho
//     (linhas 2412-2420).
//   - A imagem de entrada vira QImage::Format_RGB32 (colorida) ou Indexed8 com
//     paleta cinza (cinza), como o ScanTailor carrega um PNG (igual ao 1.2).

#include <AdjustBrightness.h>
#include <Binarize.h>
#include <BinaryImage.h>
#include <BinaryThreshold.h>
#include <Dpi.h>
#include <GrayImage.h>
#include <GrayRasterOp.h>
#include <Grayscale.h>
#include <Morphology.h>
#include <PolynomialSurface.h>
#include <SavGolFilter.h>
#include <Transform.h>

#include <QColor>
#include <QImage>
#include <QPolygonF>
#include <QRect>
#include <QRectF>
#include <QSize>
#include <QTransform>
#include <QtGlobal>
#include <algorithm>
#include <cassert>
#include <cstring>
#include <new>
#include <vector>

#include "BlackWhiteOptions.h"
#include "DebugImages.h"
#include "EstimateBackground.h"
#include "NullTaskStatus.h"
#include "TaskStatus.h"
#include "comum.h"
#include "st_ferramentas.h"

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
  // image: a pagina ja girada e cortada pelo programa (o sistema de trabalho e ela mesma).
  // dpi: o DPI da imagem (no original, o DPI de saida).
  // opcoes: as opcoes do preto e branco do ScanTailor (metodo, limiar, janela, k...).
  Processor(const QImage& image, const Dpi& dpi, const BlackWhiteOptions& opcoes);

  // Passo 1 da ordem acima: a pagina com a luz igualada (ou nao).
  QImage preparar(bool normalizar) const;

  // Passos 3 a 5: o preto e branco (bit 1 = preto).
  BinaryImage pretoEBranco(const QImage& preparada, bool savitzkyGolay, bool morfologica) const;

 private:
  GrayImage normalizeIlluminationGray(const QImage& input,
                                      const QPolygonF& areaToConsider,
                                      const QTransform& xform,
                                      const QRect& targetRect,
                                      GrayImage* background = nullptr) const;

  QImage transformToWorkingCs(bool normalize) const;

  BinaryThreshold adjustThreshold(BinaryThreshold threshold) const;

  void morphologicalSmoothInPlace(BinaryImage& binImg) const;

  BinaryImage binarize(const QImage& image) const;

  // No original m_xform e um ImageTransformation; as funcoes copiadas so chamam
  // m_xform.transform().
  struct XformDaLigacao {
    QTransform m_transform;
    const QTransform& transform() const { return m_transform; }
  };

  // No original m_colorParams e um ColorParams; as funcoes copiadas so chamam
  // m_colorParams.blackWhiteOptions().
  struct ColorParamsDaLigacao {
    BlackWhiteOptions m_bw;
    const BlackWhiteOptions& blackWhiteOptions() const { return m_bw; }
  };

  XformDaLigacao m_xform;
  Dpi m_dpi;
  ColorParamsDaLigacao m_colorParams;
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
}  // namespace

// ---------------------------------------------------------------------------
// LIGACAO: construtor. Faz o que o original faz em initParams(), calcAreas() e
// initFilterData() para as partes usadas aqui:
//  - sistema de trabalho = a propria imagem (identidade), area da pagina = a
//    imagem inteira (a pagina ja vem cortada pelo programa);
//  - cinza: toGrayscale() do proprio ScanTailor (FilterData.cpp);
//  - "preto no branco": sempre (o claro no escuro e o item 2.9, feito antes e
//    depois daqui, como o ScanTailor faz: inverte na entrada e na saida);
//  - cor de fora da pagina: branco (nenhum ponto cai fora: identidade).
// ---------------------------------------------------------------------------
OutputGenerator::Processor::Processor(const QImage& image, const Dpi& dpi, const BlackWhiteOptions& opcoes)
    : m_dpi(dpi),
      m_workingBoundingRect(image.rect()),
      m_inputOrigImage(image),
      m_inputGrayImage(toGrayscale(image)),
      m_colorOriginal(false),
      m_status(m_nullStatus),
      m_dbg(nullptr),
      m_outsideBackgroundColor(Qt::white) {
  m_colorParams.m_bw = opcoes;
  m_preCropAreaInOriginalCs = QPolygonF(QRectF(image.rect()));
  m_colorOriginal = !m_inputOrigImage.allGray();
}

QImage OutputGenerator::Processor::preparar(const bool normalizar) const {
  return transformToWorkingCs(normalizar);
}

// LIGACAO: o trecho "BW mask" de processWithoutDewarping() (linhas 1301-1323),
// sem a area de conteudo (a pagina inteira) e sem as imagens de depuracao.
BinaryImage OutputGenerator::Processor::pretoEBranco(const QImage& preparada,
                                                     const bool savitzkyGolay,
                                                     const bool morfologica) const {
  QImage maybeSmoothed = savitzkyGolay ? smoothToGrayscale(preparada, m_dpi) : preparada;
  m_status.throwIfCancelled();
  BinaryImage bwContent = binarize(maybeSmoothed);
  maybeSmoothed = QImage();  // Save memory.
  m_status.throwIfCancelled();
  if (morfologica) {
    morphologicalSmoothInPlace(bwContent);
  }
  return bwContent;
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

// ===== COPIADO SEM MUDANCA (linhas 2186-2192) =====
BinaryThreshold OutputGenerator::Processor::adjustThreshold(BinaryThreshold threshold) const {
  const int adjusted = threshold + m_colorParams.blackWhiteOptions().thresholdAdjustment();

  // Hard-bounding threshold values is necessary for example
  // if all the content went into the picture mask.
  return BinaryThreshold(qBound(30, adjusted, 225));
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

// ===== COPIADO SEM MUDANCA (linhas 2304-2403) =====
BinaryImage OutputGenerator::Processor::binarize(const QImage& image) const {
  if ((image.format() == QImage::Format_Mono) || (image.format() == QImage::Format_MonoLSB)) {
    return BinaryImage(image);
  }

  const BlackWhiteOptions& blackWhiteOptions = m_colorParams.blackWhiteOptions();
  const BinarizationMethod binarizationMethod = blackWhiteOptions.getBinarizationMethod();

  BinaryImage binarized;
  switch (binarizationMethod) {
    case T_OTSU: {
      GrayscaleHistogram hist(image);
      const BinaryThreshold bwThresh(BinaryThreshold::otsuThreshold(hist));

      binarized = BinaryImage(image, adjustThreshold(bwThresh));
      break;
    }
    case T_SAUVOLA: {
      const double thresholdDelta = blackWhiteOptions.thresholdAdjustment();
      const QSize windowsSize = QSize(blackWhiteOptions.getWindowSize(), blackWhiteOptions.getWindowSize());
      const double thresholdCoef = blackWhiteOptions.getSauvolaCoef();

      binarized = binarizeSauvola(image, windowsSize, thresholdCoef, thresholdDelta);
      break;
    }
    case T_WOLF: {
      const double thresholdDelta = blackWhiteOptions.thresholdAdjustment();
      const QSize windowsSize = QSize(blackWhiteOptions.getWindowSize(), blackWhiteOptions.getWindowSize());
      const auto lowerBound = (unsigned char) blackWhiteOptions.getWolfLowerBound();
      const auto upperBound = (unsigned char) blackWhiteOptions.getWolfUpperBound();
      const double thresholdCoef = blackWhiteOptions.getWolfCoef();

      binarized = binarizeWolf(image, windowsSize, lowerBound, upperBound, thresholdCoef, thresholdDelta);
      break;
    }
    case T_FOX: {
      const double thresholdDelta = blackWhiteOptions.thresholdAdjustment();
      const QSize windowsSize = QSize(blackWhiteOptions.getWindowSize(), blackWhiteOptions.getWindowSize());
      const auto lowerBound = (unsigned char) blackWhiteOptions.getWolfLowerBound();
      const auto upperBound = (unsigned char) blackWhiteOptions.getWolfUpperBound();
      const double thresholdCoef = blackWhiteOptions.getWolfCoef();

      binarized = binarizeFox(image, windowsSize, lowerBound, upperBound, thresholdCoef, thresholdDelta);
      break;
    }
    case T_WINDOW: {
      const double thresholdDelta = blackWhiteOptions.thresholdAdjustment();
      const QSize windowsSize = QSize(blackWhiteOptions.getWindowSize(), blackWhiteOptions.getWindowSize());
      const auto lowerBound = (unsigned char) blackWhiteOptions.getWolfLowerBound();
      const auto upperBound = (unsigned char) blackWhiteOptions.getWolfUpperBound();
      const double thresholdCoef = blackWhiteOptions.getWolfCoef();

      binarized = binarizeWindow(image, windowsSize, lowerBound, upperBound, thresholdCoef, thresholdDelta);
      break;
    }
    case T_BRADLEY: {
      const double thresholdDelta = blackWhiteOptions.thresholdAdjustment();
      const QSize windowsSize = QSize(blackWhiteOptions.getWindowSize(), blackWhiteOptions.getWindowSize());
      const double thresholdCoef = blackWhiteOptions.getSauvolaCoef();

      binarized = binarizeBradley(image, windowsSize, thresholdCoef, thresholdDelta);
      break;
    }
    case T_GRAD: {
      const double thresholdDelta = blackWhiteOptions.thresholdAdjustment();
      const QSize windowsSize = QSize(blackWhiteOptions.getWindowSize(), blackWhiteOptions.getWindowSize());
      const auto lowerBound = (unsigned char) blackWhiteOptions.getWolfLowerBound();
      const auto upperBound = (unsigned char) blackWhiteOptions.getWolfUpperBound();
      const double thresholdCoef = blackWhiteOptions.getWolfCoef();

      binarized = binarizeGrad(image, windowsSize, lowerBound, upperBound, thresholdCoef, thresholdDelta);
      break;
    }
    case T_EDGEPLUS: {
      const double thresholdDelta = blackWhiteOptions.thresholdAdjustment();
      const QSize windowsSize = QSize(blackWhiteOptions.getWindowSize(), blackWhiteOptions.getWindowSize());
      const double thresholdCoef = blackWhiteOptions.getSauvolaCoef();

      binarized = binarizeEdgeDiv(image, windowsSize, thresholdCoef, 0.0, thresholdDelta);
      break;
    }
    case T_BLURDIV: {
      const double thresholdDelta = blackWhiteOptions.thresholdAdjustment();
      const QSize windowsSize = QSize(blackWhiteOptions.getWindowSize(), blackWhiteOptions.getWindowSize());
      const double thresholdCoef = blackWhiteOptions.getSauvolaCoef();

      binarized = binarizeEdgeDiv(image, windowsSize, 0.0, thresholdCoef, thresholdDelta);
      break;
    }
    case T_EDGEDIV: {
      const double thresholdDelta = blackWhiteOptions.thresholdAdjustment();
      const QSize windowsSize = QSize(blackWhiteOptions.getWindowSize(), blackWhiteOptions.getWindowSize());
      const double thresholdCoef = blackWhiteOptions.getSauvolaCoef();

      binarized = binarizeEdgeDiv(image, windowsSize, thresholdCoef, thresholdCoef, thresholdDelta);
      break;
    }
  }
  return binarized;
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
// LIGACAO: a funcao em C chamada pelo Python (core/preto_e_branco_scantailor.py).
// ---------------------------------------------------------------------------
namespace {
// A pagina do Python numa QImage, no formato em que o ScanTailor carrega um PNG
// (o mesmo montarImagem do 1.2): canais 1 = Indexed8 com paleta cinza;
// canais 3 = azul, verde, vermelho (OpenCV) -> Format_RGB32. Copia os pontos.
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
}  // namespace

extern "C" {

ST_FERRAMENTAS_API int st_ferramentas_preto_e_branco(const unsigned char* pixels,
                                                     int largura,
                                                     int altura,
                                                     int passo,
                                                     int canais,
                                                     int dpiX,
                                                     int dpiY,
                                                     int metodo,
                                                     int ajusteDoLimiar,
                                                     int janela,
                                                     double coefSauvola,
                                                     double coefWolf,
                                                     int wolfMinimo,
                                                     int wolfMaximo,
                                                     int normalizar,
                                                     int savitzkyGolay,
                                                     int morfologica,
                                                     unsigned char* saida,
                                                     int passoSaida,
                                                     char* erro,
                                                     int tamanhoErro) {
  return st_ferramentas::protegido(erro, tamanhoErro, [&]() -> int {
    if (!pixels || !saida || largura <= 0 || altura <= 0 || (canais != 1 && canais != 3)
        || passo < largura * canais || passoSaida < largura || dpiX <= 0 || dpiY <= 0 || metodo < output::T_OTSU
        || metodo > output::T_EDGEDIV || janela < 3 || !(coefSauvola > 0) || !(coefWolf > 0) || wolfMinimo < 0
        || wolfMaximo > 255 || wolfMinimo > wolfMaximo) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_FERRAMENTAS_ERRO_PARAMETRO;
    }
    output::BlackWhiteOptions opcoes;  // os de fabrica do ScanTailor; abaixo, so o que o Python pediu
    opcoes.setBinarizationMethod(static_cast<output::BinarizationMethod>(metodo));
    opcoes.setThresholdAdjustment(ajusteDoLimiar);
    opcoes.setWindowSize(janela);
    opcoes.setSauvolaCoef(coefSauvola);
    opcoes.setWolfCoef(coefWolf);
    opcoes.setWolfLowerBound(wolfMinimo);
    opcoes.setWolfUpperBound(wolfMaximo);
    opcoes.setNormalizeIllumination(normalizar != 0);
    opcoes.setSavitzkyGolaySmoothingEnabled(savitzkyGolay != 0);
    opcoes.setMorphologicalSmoothingEnabled(morfologica != 0);

    const QImage imagem = montarImagem(pixels, largura, altura, passo, canais);
    output::OutputGenerator::Processor processador(imagem, Dpi(dpiX, dpiY), opcoes);
    const QImage preparada = processador.preparar(opcoes.normalizeIllumination());
    const BinaryImage bw = processador.pretoEBranco(preparada, opcoes.isSavitzkyGolaySmoothingEnabled(),
                                                    opcoes.isMorphologicalSmoothingEnabled());
    st_ferramentas::bytesDeBinaria(bw, saida, passoSaida);
    return ST_FERRAMENTAS_OK;
  });
}

}  // extern "C"
