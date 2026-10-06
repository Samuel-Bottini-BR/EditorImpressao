// st_ferramentas: as ferramentas de imagem do ScanTailor Advanced, numa DLL so,
// expostas em C para o Python chamar por ctypes (item M9 da Fase 2).
//
// Copyright (C) 2026  Editor de Impressao (ligacao)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// Funcoes em C puro (sem classes C++ na fronteira) para a DLL nao depender da
// versao do Python. Quem chama: core/st_ferramentas.py (carrega a DLL) e um
// modulo por ferramenta (hoje so core/pontinhos_scantailor.py).
//
// COMO ACRESCENTAR UMA FERRAMENTA (dividir, endireitar, caixa do conteudo,
// binarizadores, segmentacao de cor...)
//   1. traga os arquivos do ScanTailor para ../src, SEM MUDANCA, e ponha a soma
//      deles em ../somas-v1.2.1.txt (o teste confere);
//   2. escreva a cola num .cpp novo nesta pasta (um por ferramenta, como
//      pontinhos.cpp), usando os ajudantes de comum.h;
//   3. declare aqui a funcao em C, com prefixo st_ferramentas_, e suba
//      ST_FERRAMENTAS_VERSAO_API;
//   4. no Python, um modulo novo em core/ que usa core/st_ferramentas.py.
//   Nada do que ja existe precisa mudar.
//
// SEGURO MUDAR: acrescentar funcoes novas (subindo a versao).
// ARRISCADO: mudar a assinatura de uma funcao que ja existe ou os codigos de
//   erro sem mudar o Python junto (ctypes nao confere tipos: um tipo errado vira
//   travamento, nao mensagem). Se mudar, suba ST_FERRAMENTAS_VERSAO_API: o
//   Python recusa DLL de versao diferente.

#ifndef ST_FERRAMENTAS_H_
#define ST_FERRAMENTAS_H_

#ifdef _WIN32
#define ST_FERRAMENTAS_API __declspec(dllexport)
#else
#define ST_FERRAMENTAS_API __attribute__((visibility("default")))
#endif

// Versao desta interface. 1 = 06/10/2026: so os pontinhos.
#define ST_FERRAMENTAS_VERSAO_API 1

// De onde veio o codigo (o compilar_st_ferramentas.py passa a versao e o commit).
#ifndef ST_FERRAMENTAS_ORIGEM
#define ST_FERRAMENTAS_ORIGEM "ScanTailor Advanced (versao nao informada)"
#endif

// Codigos de volta, iguais para todas as funcoes (e iguais aos da st_gravura).
#define ST_FERRAMENTAS_OK 0
#define ST_FERRAMENTAS_ERRO_PARAMETRO 1
#define ST_FERRAMENTAS_ERRO_MEMORIA 2
#define ST_FERRAMENTAS_ERRO_INTERNO 3

#ifdef __cplusplus
extern "C" {
#endif

// Versao desta interface (ST_FERRAMENTAS_VERSAO_API).
ST_FERRAMENTAS_API int st_ferramentas_versao_api(void);

// Texto dizendo de onde veio o codigo (repositorio, versao, commit, Qt).
ST_FERRAMENTAS_API const char* st_ferramentas_origem(void);

// LIMPAR PONTINHOS (Despeckle do ScanTailor, src/core/Despeckle.cpp, sem mudanca).
//
// entrada, largura, altura, passoEntrada: a imagem em preto e branco, 1 byte por
//   ponto, linha a linha (passo = bytes por linha). Byte menor que 128 = PRETO
//   (tinta), o resto = branco (papel). E o preto e branco do programa (0 e 255).
// dpiX, dpiY: o DPI da imagem. O ScanTailor mede o tamanho do pontinho e a
//   distancia ate a letra em pontos a 300 DPI: o DPI errado muda o resultado.
// forca: o controle do ScanTailor, de 0,5 a 3,5 (padrao dele: 1,0).
//   1,0 = "cauteloso", 2,0 = "normal", 3,0 = "agressivo" (as tres forcas
//   antigas do ScanTailor; a conta da v1.2.1 da exatamente os mesmos numeros).
// saida, passoSaida: a imagem limpa, 1 byte por ponto: 0 = preto, 255 = branco.
//   Pode ser o mesmo buffer da entrada (a entrada e lida inteira antes).
// erro, tamanhoErro: texto do erro, se houver.
//
// So TIRA preto (nunca poe). Devolve ST_FERRAMENTAS_OK ou um codigo de erro.
// Nunca deixa excecao escapar.
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
                                                int tamanhoErro);

#ifdef __cplusplus
}
#endif

#endif  // ST_FERRAMENTAS_H_
