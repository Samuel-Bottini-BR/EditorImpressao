// Detector de gravura do ScanTailor Advanced (modo Misto), exposto em C para ctypes.
//
// Copyright (C) 2026  Editor de Impressao (ligacao)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// Funcoes em C puro (sem classes C++ na fronteira) para a DLL nao depender da
// versao do Python: core/gravura_scantailor.py chama por ctypes.
//
// SEGURO MUDAR: acrescentar funcoes novas.
// ARRISCADO: mudar a assinatura de st_gravura_detectar() ou os codigos de erro
//   sem mudar core/gravura_scantailor.py junto (ctypes nao confere tipos). Se mudar,
//   suba ST_GRAVURA_VERSAO_API: o Python recusa DLL de versao diferente.

#ifndef ST_GRAVURA_H_
#define ST_GRAVURA_H_

#ifdef _WIN32
#define ST_GRAVURA_API __declspec(dllexport)
#else
#define ST_GRAVURA_API __attribute__((visibility("default")))
#endif

#define ST_GRAVURA_VERSAO_API 1

// De onde veio o codigo (o compilar_detector_gravura.py passa a versao e o commit).
#ifndef ST_GRAVURA_ORIGEM
#define ST_GRAVURA_ORIGEM "ScanTailor Advanced (versao nao informada)"
#endif

// Formato dos pontos de entrada.
#define ST_GRAVURA_CINZA 1  // 1 byte por ponto
#define ST_GRAVURA_RGB 3    // 3 bytes por ponto, vermelho-verde-azul
#define ST_GRAVURA_BGR 5    // 3 bytes por ponto, azul-verde-vermelho (o do OpenCV)

#define ST_GRAVURA_OK 0
#define ST_GRAVURA_ERRO_PARAMETRO 1
#define ST_GRAVURA_ERRO_MEMORIA 2
#define ST_GRAVURA_ERRO_INTERNO 3

#ifdef __cplusplus
extern "C" {
#endif

// Versao desta interface (ST_GRAVURA_VERSAO_API).
ST_GRAVURA_API int st_gravura_versao_api(void);

// Texto dizendo de onde veio o codigo (repositorio, versao, commit).
ST_GRAVURA_API const char* st_gravura_origem(void);

// Acha as gravuras de uma pagina, como o modo Misto do ScanTailor Advanced.
//
// pixels, largura, altura, passo: a pagina, 8 bits por canal, linha a linha
//   (passo = bytes por linha). formato: ST_GRAVURA_CINZA, ST_GRAVURA_RGB ou
//   ST_GRAVURA_BGR.
// dpiX, dpiY: DPI do sistema de trabalho (a pagina, se transformacao for NULL).
//   O detector reduz tudo para 300 DPI; o DPI errado muda o resultado.
// transformacao: NULL (a pagina ja esta pronta) ou 6 numeros m11 m12 m21 m22 dx dy
//   (QTransform) levando a pagina para o sistema de trabalho do ScanTailor.
// retangulo: NULL (a pagina inteira) ou x, y, largura, altura do retangulo de
//   trabalho, no sistema de trabalho. A mascara sai com esse tamanho.
// normalizarIluminacao: 1 = como o padrao do ScanTailor no modo Misto.
// forma: 0 = desligado, 1 = livre (padrao), 2 = retangular.
// sensibilidade: 0 a 100 (so vale na forma retangular; padrao 100).
// maisSensivel: 1 = "maior sensibilidade de busca" (padrao 0).
// mascara, passoMascara: saida, 1 byte por ponto: 255 = gravura, 0 = resto.
// erro, tamanhoErro: texto do erro, se houver.
//
// Devolve ST_GRAVURA_OK ou um dos codigos de erro. Nunca deixa excecao escapar.
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
                                       int tamanhoErro);

#ifdef __cplusplus
}
#endif

#endif  // ST_GRAVURA_H_
