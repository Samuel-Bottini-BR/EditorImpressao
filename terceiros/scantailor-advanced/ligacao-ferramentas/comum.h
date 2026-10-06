// Ajudantes da ligacao st_ferramentas, usados por todas as ferramentas.
//
// Copyright (C) 2026  Editor de Impressao (ligacao)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// O QUE TEM AQUI
//   - escreverErro(): copia o texto do erro para o buffer do Python;
//   - protegido(): roda a ferramenta e transforma QUALQUER excecao num codigo de
//     erro (uma excecao C++ atravessando o ctypes derruba o programa);
//   - binariaDeBytes() / bytesDeBinaria(): a imagem em preto e branco do
//     programa (1 byte por ponto, 0 = preto) <-> imageproc::BinaryImage do
//     ScanTailor (1 bit por ponto, bit 1 = PRETO, do bit mais alto para o mais
//     baixo de cada palavra de 32 bits, como em BinaryImage.h).
//
// ARRISCADO MUDAR
//   - A ordem dos bits em binariaDeBytes/bytesDeBinaria: errada, a imagem sai
//     espelhada em grupos de 32 pontos (o teste de ida e volta pega).
//   - O limite de 128 em binariaDeBytes: e o BinaryThreshold(128) do ScanTailor
//     (abaixo de 128 = preto).
//   - Os bits depois da largura, na ultima palavra de cada linha, ficam em 0
//     (branco): o ScanTailor conta com isso em varias funcoes.

#ifndef ST_FERRAMENTAS_COMUM_H_
#define ST_FERRAMENTAS_COMUM_H_

#include <BWColor.h>
#include <BinaryImage.h>

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <exception>
#include <new>

#include "st_ferramentas.h"

namespace st_ferramentas {

inline void escreverErro(char* erro, int tamanho, const char* texto) {
  if (!erro || tamanho <= 0) {
    return;
  }
  std::strncpy(erro, texto ? texto : "", static_cast<size_t>(tamanho) - 1);
  erro[tamanho - 1] = '\0';
}

// Roda f() (que devolve um codigo ST_FERRAMENTAS_*) sem deixar excecao escapar.
template <typename F>
int protegido(char* erro, int tamanhoErro, F&& f) {
  try {
    return f();
  } catch (const std::bad_alloc&) {
    escreverErro(erro, tamanhoErro, "memoria insuficiente");
    return ST_FERRAMENTAS_ERRO_MEMORIA;
  } catch (const std::exception& e) {
    escreverErro(erro, tamanhoErro, e.what());
    return ST_FERRAMENTAS_ERRO_INTERNO;
  } catch (...) {
    escreverErro(erro, tamanhoErro, "erro desconhecido");
    return ST_FERRAMENTAS_ERRO_INTERNO;
  }
}

// Bytes (0 = preto) -> BinaryImage do ScanTailor (bit 1 = preto).
inline imageproc::BinaryImage binariaDeBytes(const unsigned char* pixels, int largura, int altura, int passo) {
  imageproc::BinaryImage bw(largura, altura, imageproc::WHITE);  // tudo 0 (branco), inclusive a sobra
  uint32_t* linha = bw.data();
  const int wpl = bw.wordsPerLine();
  const uint32_t msb = uint32_t(1) << 31;
  for (int y = 0; y < altura; ++y, linha += wpl) {
    const unsigned char* origem = pixels + static_cast<size_t>(y) * passo;
    for (int x = 0; x < largura; ++x) {
      if (origem[x] < 128) {
        linha[x >> 5] |= msb >> (x & 31);
      }
    }
  }
  return bw;
}

// BinaryImage do ScanTailor (bit 1 = preto) -> bytes (0 = preto, 255 = branco).
inline void bytesDeBinaria(const imageproc::BinaryImage& bw, unsigned char* saida, int passo) {
  const int w = bw.width();
  const int h = bw.height();
  const int wpl = bw.wordsPerLine();
  const uint32_t* linha = bw.data();
  for (int y = 0; y < h; ++y, linha += wpl) {
    unsigned char* destino = saida + static_cast<size_t>(y) * passo;
    for (int x = 0; x < w; ++x) {
      const uint32_t bit = (linha[x >> 5] >> (31 - (x & 31))) & 1u;
      destino[x] = bit ? 0 : 255;
    }
  }
}

}  // namespace st_ferramentas

#endif  // ST_FERRAMENTAS_COMUM_H_
