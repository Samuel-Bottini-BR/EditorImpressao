// Limpar pontinhos: o Despeckle do ScanTailor Advanced, chamado do Python.
//
// Copyright (C) 2026  Editor de Impressao (so esta ligacao)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// O QUE FAZ
//   Recebe o preto e branco do programa, converte para a imagem de 1 bit do
//   ScanTailor e chama Despeckle::despeckleInPlace() - o mesmo que o ScanTailor
//   chama na saida (OutputGenerator.cpp, maybeDespeckleInPlace, com o nivel do
//   controle "Despeckle" de 0,5 a 3,5). O codigo do Despeckle esta em
//   ../src/core/Despeckle.cpp, copiado SEM MUDANCA da v1.2.1; aqui so ha a
//   conversao de ida e volta.
//
// COMO O SCANTAILOR DECIDE (em palavras, de Despeckle.cpp)
//   Cada peca de tinta (pontos pretos ligados) grande o bastante fica. Uma peca
//   pequena so fica se estiver PERTO de uma peca que fica e nao for muito maior
//   que ela - por isso o pingo do "i" e a virgula perto da letra sobrevivem e o
//   pontinho solto no papel sai. A distancia de cima para baixo vale o dobro da
//   de lado. A forca mexe em tres numeros: o tamanho a partir do qual a peca
//   fica sempre (7, 12 ou 17 pontos a 300 DPI nas forcas 1, 2 e 3), quao perto
//   ela tem de estar, e quao grande a vizinha tem de ser.
//
// O QUE E ARRISCADO
//   - O DPI: os numeros acima sao a 300 DPI e acompanham o DPI (dpiFactor =
//     menor DPI / 300). DPI errado = forca errada.
//   - A forca 0 desliga no ScanTailor (maybeDespeckleInPlace nao chama nada);
//     aqui a forca fora de 0,5..3,5 e recusada, e quem quer desligar nao chama.

#include <Despeckle.h>
#include <Dpi.h>

#include "NullTaskStatus.h"
#include "comum.h"
#include "st_ferramentas.h"

using imageproc::BinaryImage;

extern "C" {

ST_FERRAMENTAS_API int st_ferramentas_pontinhos(const unsigned char* entrada,
                                                int largura,
                                                int altura,
                                                int passoEntrada,
                                                int dpiX,
                                                int dpiY,
                                                double forca,
                                                unsigned char* saida,
                                                int passoSaida,
                                                char* erro,
                                                int tamanhoErro) {
  return st_ferramentas::protegido(erro, tamanhoErro, [&]() -> int {
    if (!entrada || !saida || largura <= 0 || altura <= 0 || passoEntrada < largura || passoSaida < largura
        || dpiX <= 0 || dpiY <= 0 || !(forca >= 0.5 && forca <= 3.5)) {
      st_ferramentas::escreverErro(erro, tamanhoErro, "parametros invalidos");
      return ST_FERRAMENTAS_ERRO_PARAMETRO;
    }
    BinaryImage bw = st_ferramentas::binariaDeBytes(entrada, largura, altura, passoEntrada);
    NullTaskStatus semCancelar;
    Despeckle::despeckleInPlace(bw, Dpi(dpiX, dpiY), forca, semCancelar, nullptr);
    st_ferramentas::bytesDeBinaria(bw, saida, passoSaida);
    return ST_FERRAMENTAS_OK;
  });
}

}  // extern "C"
