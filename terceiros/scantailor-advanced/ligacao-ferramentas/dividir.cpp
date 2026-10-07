// Dividir a folha: o PageLayoutEstimator do ScanTailor Advanced, chamado do Python.
//
// Copyright (C) 2026  Editor de Impressao (so esta ligacao; o trecho marcado
//   "COPIADO SEM MUDANCA" e do ScanTailor Advanced, Joseph Artsimovich e 4lex4)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// O QUE FAZ (item 2.1 da Fase 2, decisoes G2 (a) e G3 (b) do Samuel)
//   Recebe a folha (cinza ou colorida) e o DPI, e devolve onde o ScanTailor
//   cortaria: PageLayoutEstimator::estimatePageLayout() - a MESMA chamada que o
//   page_split::Task do ScanTailor faz (src/core/filters/page_split/Task.cpp,
//   linhas 121-122). O calculo esta em ../src/core/filters/page_split/
//   (PageLayoutEstimator.cpp, VertLineFinder.cpp, PageLayout.cpp), copiado SEM
//   MUDANCA da v1.2.1. Aqui so ha a montagem do que o Task recebe:
//     - a imagem cinza e a geometria: as duas linhas do construtor de
//       FilterData (src/core/FilterData.cpp, linhas 13-14):
//         m_grayImage(toGrayscale(m_origImage)), m_xform(image.rect(), Dpm(image))
//     - o limiar: o que o fix_orientation::Task poe quando a folha ainda nao
//       tem um (src/core/filters/fix_orientation/Task.cpp, linha 87):
//         BinaryThreshold::otsuThreshold(data.grayImage())
//     - sem giro de 90 graus (quem gira e o programa, antes) e sem "trim".
//   FilterData e ImageSettings NAO foram trazidos (puxariam a parte de projeto
//   e miniaturas do ScanTailor); as tres linhas acima sao as deles, iguais.
//
// COMO O SCANTAILOR DECIDE (em palavras, de PageLayoutEstimator.cpp)
//   1. Procura linhas verticais compridas (a dobra do livro, a beirada da folha
//      vizinha) com a transformada de Hough (VertLineFinder), a ~100 DPI.
//      - "duas paginas": fica com a linha mais perto do meio; linhas a mais de
//        60% do meio para a beirada nao contam.
//      - "uma pagina + sobra": as linhas perto das beiradas viram os dois cortes
//        da sobra (a beirada da folha vizinha sai).
//      - "automatico": folha mais larga que alta = duas paginas, senao uma; e,
//        com uma pagina, so corta sobra se as linhas estiverem perto da beirada.
//   2. Se nao achar linha, corta no maior espaco em branco entre colunas de
//      texto, numa copia em preto e branco a 150 DPI, endireitada de leve.
//
// O QUE E ARRISCADO
//   - O DPI: a imagem e reduzida a 300 e a 150 DPI pelo DPI informado; DPI
//     errado muda os tamanhos que o ScanTailor procura.
//   - O modo: os numeros sao os de page_split::LayoutType (LayoutType.h):
//     0 automatico, 1 uma pagina sem corte, 2 uma pagina + sobra, 3 duas
//     paginas. Mudar a ordem aqui sem mudar o Python troca o modo.
//   - A linha de corte do ScanTailor pode ser INCLINADA (a dobra fotografada
//     torta); devolvemos as duas pontas, e quem usa decide o que fazer.

#include <BinaryThreshold.h>
#include <Dpi.h>
#include <Dpm.h>
#include <GrayImage.h>
#include <Grayscale.h>

#include <QImage>
#include <QLineF>
#include <QSize>

#include "ImageMetadata.h"
#include "ImageTransformation.h"
#include "OrthogonalRotation.h"
#include "ProjectPages.h"
#include "comum.h"
#include "filters/page_split/LayoutType.h"
#include "filters/page_split/PageLayout.h"
#include "filters/page_split/PageLayoutEstimator.h"
#include "st_ferramentas.h"

// ---- COPIADO SEM MUDANCA de src/core/ProjectPages.cpp (linhas 205-214) ------
// A unica funcao de ProjectPages que o PageLayoutEstimator usa (no modo
// automatico: folha mais larga que alta = duas paginas). ProjectPages.cpp
// inteiro puxaria o projeto do ScanTailor; o teste
// tests/test_dividir_scantailor.py confere que este trecho e igual ao original.
int ProjectPages::adviseNumberOfLogicalPages(const ImageMetadata& metadata, const OrthogonalRotation rotation) {
  const QSize size(rotation.rotate(metadata.size()));
  const QSize dpi(rotation.rotate(metadata.dpi().toSize()));

  if (size.width() * dpi.height() > size.height() * dpi.width()) {
    return 2;
  } else {
    return 1;
  }
}
// ---- FIM DO TRECHO COPIADO --------------------------------------------------

using imageproc::BinaryThreshold;
using imageproc::GrayImage;
using page_split::LayoutType;
using page_split::PageLayout;
using page_split::PageLayoutEstimator;

extern "C" {

ST_FERRAMENTAS_API int st_ferramentas_dividir(const unsigned char* pixels,
                                              int largura,
                                              int altura,
                                              int passo,
                                              int canais,
                                              int dpiX,
                                              int dpiY,
                                              int modo,
                                              int* tipo,
                                              int* numCortes,
                                              double* cortes,
                                              char* erro,
                                              int tamanhoErro) {
  return st_ferramentas::protegido(erro, tamanhoErro, [&]() -> int {
    if (!pixels || !tipo || !numCortes || !cortes || largura <= 0 || altura <= 0 || (canais != 1 && canais != 3)
        || passo < largura * canais || dpiX <= 0 || dpiY <= 0 || modo < page_split::AUTO_LAYOUT_TYPE
        || modo > page_split::TWO_PAGES) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_FERRAMENTAS_ERRO_PARAMETRO;
    }

    // A folha como o ScanTailor a abriria do disco: os pontos (sem copia; so
    // lidos) e o DPI gravado nela (Dpm = pontos por metro, como no arquivo).
    // 3 canais = a ordem do OpenCV (azul, verde, vermelho).
    QImage folha(pixels, largura, altura, passo, canais == 1 ? QImage::Format_Grayscale8 : QImage::Format_BGR888);
    const Dpm dpm{Dpi(dpiX, dpiY)};
    folha.setDotsPerMeterX(dpm.horizontal());
    folha.setDotsPerMeterY(dpm.vertical());

    // O que o page_split::Task recebe (ver o topo): FilterData + fix_orientation.
    const GrayImage cinza(imageproc::toGrayscale(folha));
    const ImageTransformation geometria(folha.rect(), Dpm(folha));
    const BinaryThreshold limiar = BinaryThreshold::otsuThreshold(cinza);

    const PageLayout layout = PageLayoutEstimator::estimatePageLayout(static_cast<LayoutType>(modo), cinza,
                                                                      geometria, limiar, nullptr);

    *tipo = static_cast<int>(layout.type());  // 0 sem corte, 1 com sobra, 2 duas paginas
    const int n = layout.numCutters();
    *numCortes = n;
    for (int k = 0; k < 2; ++k) {
      double* c = cortes + 4 * k;
      if (k < n) {
        // As pontas do corte encostadas nas bordas da folha (em pontos da folha).
        const QLineF linha = layout.inscribedCutterLine(k);
        c[0] = linha.p1().x();
        c[1] = linha.p1().y();
        c[2] = linha.p2().x();
        c[3] = linha.p2().y();
      } else {
        c[0] = c[1] = c[2] = c[3] = 0.0;
      }
    }
    return ST_FERRAMENTAS_OK;
  });
}

}  // extern "C"
