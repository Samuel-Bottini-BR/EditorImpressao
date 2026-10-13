// Teste do pesquisador (12/10/2026), NAO faz parte do programa.
//
// O que faz: roda, numa imagem de pagina, as duas contas da etapa "Select
// Content" do ScanTailor Advanced v1.2.1, com o codigo original (GPL-3):
//   - a caixa da PAGINA (PageFinder::findPageBox, item 2.13 do plano), com e
//     sem o "Fine Tune Page Corners";
//   - a caixa do CONTEUDO (ContentBoxFinder::findContentBox, item 2.5), na
//     folha inteira e dentro de cada caixa da pagina (como o ScanTailor faz
//     quando as duas estao ligadas: select_content/Task.cpp).
// Imprime uma linha JSON por imagem. Uso: caixas <png> <dpi> [<png> <dpi> ...]
//
// E o mesmo jeito do teste de 01/10 (ferramentas/pesquisa-fase2-2026-10-01/
// prova.cpp); liga na biblioteca que aquele teste ja compilou (st_tudo.lib),
// sem recompilar o ScanTailor.
#include <QImage>
#include <chrono>
#include <cstdio>

#include "BinaryThreshold.h"
#include "Dpi.h"
#include "FilterData.h"
#include "GrayImage.h"
#include "ImageMetadata.h"
#include "ImageTransformation.h"
#include "NullTaskStatus.h"
#include "OrthogonalRotation.h"
#include "ProjectPages.h"
#include "filters/select_content/ContentBoxFinder.h"
#include "filters/select_content/PageFinder.h"

using namespace imageproc;
using namespace select_content;

// "Cola" exigida pela biblioteca (o dividir usa); copiada de
// src/core/ProjectPages.cpp, linhas 205-214, sem mudanca. Nao e chamada aqui.
int ProjectPages::adviseNumberOfLogicalPages(const ImageMetadata& metadata, const OrthogonalRotation rotation) {
  const QSize size(rotation.rotate(metadata.size()));
  const QSize dpi(rotation.rotate(metadata.dpi().toSize()));

  if (size.width() * dpi.height() > size.height() * dpi.width()) {
    return 2;
  } else {
    return 1;
  }
}

static void caixa(const char* nome, const QRectF& r, bool virgula = true) {
  std::printf("\"%s\": [%.1f, %.1f, %.1f, %.1f]%s", nome, r.left(), r.top(), r.right(), r.bottom(),
              virgula ? ", " : "");
}

int main(int argc, char** argv) {
  for (int i = 1; i + 1 < argc; i += 2) {
    QImage img(QString::fromLocal8Bit(argv[i]));
    const int dpi = atoi(argv[i + 1]);
    if (img.isNull()) {
      std::printf("{\"arquivo\": \"%s\", \"erro\": \"nao abriu\"}\n", argv[i]);
      continue;
    }
    img = img.convertToFormat(QImage::Format_RGB32);
    const ImageTransformation xform(QRectF(img.rect()), Dpi(dpi, dpi));
    NullTaskStatus status;
    const GrayImage gray(img);
    const BinaryThreshold otsu = BinaryThreshold::otsuThreshold(gray.toQImage());
    FilterData data(FilterData(img), xform);
    data.updateImageParams(ImageSettings::PageParams(otsu, true));

    const auto t = std::chrono::steady_clock::now();
    const QRectF folha(img.rect());
    const QRectF pagina = PageFinder::findPageBox(status, data, false, QSizeF(), 0.1, nullptr);
    const QRectF paginaCantos = PageFinder::findPageBox(status, data, true, QSizeF(), 0.1, nullptr);
    const QRectF conteudoFolha = ContentBoxFinder::findContentBox(status, data, folha, nullptr);
    const QRectF conteudoPagina = ContentBoxFinder::findContentBox(status, data, pagina, nullptr);
    const QRectF conteudoCantos = ContentBoxFinder::findContentBox(status, data, paginaCantos, nullptr);
    const double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t).count();

    std::printf("{\"arquivo\": \"%s\", \"largura\": %d, \"altura\": %d, \"dpi\": %d, ", argv[i], img.width(),
                img.height(), dpi);
    caixa("pagina", pagina);
    caixa("pagina_cantos", paginaCantos);
    caixa("conteudo_folha", conteudoFolha);
    caixa("conteudo_na_pagina", conteudoPagina);
    caixa("conteudo_na_pagina_cantos", conteudoCantos);
    std::printf("\"ms\": %.0f}\n", ms);
    std::fflush(stdout);
  }
  return 0;
}
