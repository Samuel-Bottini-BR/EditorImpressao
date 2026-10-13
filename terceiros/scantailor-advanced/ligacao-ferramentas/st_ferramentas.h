// st_ferramentas: as ferramentas de imagem do ScanTailor Advanced, numa DLL so,
// expostas em C para o Python chamar por ctypes (item M9 da Fase 2).
//
// Copyright (C) 2026  Editor de Impressao (ligacao)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// Funcoes em C puro (sem classes C++ na fronteira) para a DLL nao depender da
// versao do Python. Quem chama: core/st_ferramentas.py (carrega a DLL) e um
// modulo por ferramenta (core/pontinhos_scantailor.py, core/dividir_scantailor.py,
// core/endireitar_scantailor.py, core/caixas_scantailor.py).
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
// 2 = 06/10/2026: + dividir (st_ferramentas_dividir); os pontinhos nao mudaram.
// 3 = 06/10/2026: + endireitar (st_ferramentas_endireitar, item 2.2); os
//     pontinhos e o dividir nao mudaram.
// 4 = 12/10/2026: + as caixas da pagina e do conteudo (st_ferramentas_caixas,
//     itens 2.13 e 2.5); as tres de antes nao mudaram.
#define ST_FERRAMENTAS_VERSAO_API 4

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

// DIVIDIR A FOLHA (PageLayoutEstimator do ScanTailor,
// src/core/filters/page_split/PageLayoutEstimator.cpp, sem mudanca; a cola esta
// em dividir.cpp).
//
// pixels, largura, altura, passo: a folha, linha a linha (passo = bytes por
//   linha). canais = 1 (cinza) ou 3 (azul, verde, vermelho: a ordem do OpenCV).
// dpiX, dpiY: o DPI da imagem (o ScanTailor reduz a 300 e a 150 DPI por ele).
// modo: o page_split::LayoutType do ScanTailor: 0 automatico, 1 uma pagina sem
//   corte, 2 uma pagina + sobra, 3 duas paginas.
// tipo (saida): o que o ScanTailor achou (PageLayout::Type): 0 uma pagina sem
//   corte, 1 uma pagina com sobra (2 cortes: o da esquerda e o da direita),
//   2 duas paginas (1 corte: a divisao).
// numCortes (saida): 0, 1 ou 2.
// cortes (saida, 8 numeros): x1, y1, x2, y2 de cada corte, em pontos da folha,
//   com as pontas nas bordas de cima e de baixo. A linha pode ser inclinada.
//   O que sobra (corte que nao existe) fica 0.
// erro, tamanhoErro: texto do erro, se houver.
//
// So le a imagem. Devolve ST_FERRAMENTAS_OK ou um codigo de erro.
// Nunca deixa excecao escapar.
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
                                              int tamanhoErro);

// ENDIREITAR A PAGINA (SkewFinder do ScanTailor, src/imageproc/SkewFinder.cpp,
// com a limpeza das sombras horizontais de src/core/filters/deskew/Task.cpp;
// tudo sem mudanca; a cola esta em endireitar.cpp).
//
// pixels, largura, altura, passo, canais: a pagina, como no dividir (1 = cinza,
//   3 = azul, verde, vermelho, a ordem do OpenCV).
// dpiX, dpiY: o DPI da imagem (so muda a limpeza das sombras compridas).
// angulo (saida): o angulo que o ScanTailor aplicaria, em graus, no sentido
//   DELE (o "post rotation"); 0 quando a confianca fica abaixo de 2,0
//   (Skew::GOOD_CONFIDENCE).
// anguloBruto (saida): o angulo achado, mesmo com confianca baixa.
// confianca (saida): a confianca do SkewFinder (2,0 ou mais = boa).
// pretoNoBranco (saida): 1 se a pagina foi vista como preto no branco, 0 se
//   "claro no escuro" (medida invertida, como o ScanTailor faz).
// erro, tamanhoErro: texto do erro, se houver.
//
// So le a imagem. Devolve ST_FERRAMENTAS_OK ou um codigo de erro.
// Nunca deixa excecao escapar.
ST_FERRAMENTAS_API int st_ferramentas_endireitar(const unsigned char* pixels,
                                                 int largura,
                                                 int altura,
                                                 int passo,
                                                 int canais,
                                                 int dpiX,
                                                 int dpiY,
                                                 double* angulo,
                                                 double* anguloBruto,
                                                 double* confianca,
                                                 int* pretoNoBranco,
                                                 char* erro,
                                                 int tamanhoErro);

// A CAIXA DA PAGINA E A CAIXA DO CONTEUDO (a etapa "Select Content" do
// ScanTailor: PageFinder e ContentBoxFinder de src/core/filters/select_content/,
// sem mudanca; a cola esta em caixas.cpp). Itens 2.13 e 2.5 do plano.
//
// pixels, largura, altura, passo, canais: a pagina, como no dividir (1 = cinza,
//   3 = azul, verde, vermelho, a ordem do OpenCV), JA girada e endireitada.
// dpiX, dpiY: o DPI da imagem. Os dois achadores levam a pagina a 150 DPI por
//   ele: DPI errado muda as caixas (e DPI baixo demais amplia a pagina e deixa
//   a conta varias vezes mais lenta).
// modoPagina: 0 = desligada (a "pagina" e a folha inteira; o de fabrica do
//   ScanTailor), 1 = automatica (PageFinder: tira a faixa preta do scanner).
// ajustarCantos: 1 = o "Fine Tune Page Corners" do ScanTailor (so vale com
//   modoPagina 1; de fabrica 0).
// larguraEsperadaMm, alturaEsperadaMm, tolerancia: o tamanho esperado da
//   pagina (so vale com modoPagina 1). De fabrica 0, 0 e 0,1 (sem tamanho
//   esperado). A tolerancia vai de 0 a 1.
// modoConteudo: 0 = desligada (o "conteudo" e a caixa da pagina), 1 =
//   automatica (ContentBoxFinder, o de fabrica do ScanTailor).
// claroNoEscuro: -1 = o ScanTailor decide (BlackOnWhiteEstimator, o de fabrica
//   dele), 0 = tratar como preto no branco, 1 = tratar como claro no escuro
//   (a conta e feita na pagina invertida).
// pagina (saida, 4 numeros): x0, y0, x1, y1 da caixa da pagina, em pontos da
//   imagem (x1, y1 = a beirada de fora: largura = x1 - x0).
// conteudo (saida, 4 numeros): a caixa do conteudo ja cortada pela caixa da
//   pagina (o que o ScanTailor guarda). Tudo 0 quando nao ha conteudo.
// conteudoBruto (saida, 4 numeros): o que o ContentBoxFinder devolveu, ANTES
//   do corte pela caixa da pagina (pode passar dela; ver caixas.cpp).
// tamanhoConteudoMm (saida, 2 numeros): largura e altura do conteudo em mm
//   (PhysSizeCalc do ScanTailor). 0 e 0 quando nao ha conteudo.
// achouConteudo (saida): 1 se ha caixa do conteudo, 0 se a pagina nao tem
//   conteudo (em branco).
// pretoNoBranco (saida): 1 se a pagina foi tratada como preto no branco.
// milissegundos (saida, 3 numeros): o tempo do preparo (cinza, claro no
//   escuro, limiar), o da caixa da pagina e o da caixa do conteudo.
// erro, tamanhoErro: texto do erro, se houver.
//
// So le a imagem. Devolve ST_FERRAMENTAS_OK ou um codigo de erro.
// Nunca deixa excecao escapar.
ST_FERRAMENTAS_API int st_ferramentas_caixas(const unsigned char* pixels,
                                             int largura,
                                             int altura,
                                             int passo,
                                             int canais,
                                             int dpiX,
                                             int dpiY,
                                             int modoPagina,
                                             int ajustarCantos,
                                             double larguraEsperadaMm,
                                             double alturaEsperadaMm,
                                             double tolerancia,
                                             int modoConteudo,
                                             int claroNoEscuro,
                                             double* pagina,
                                             double* conteudo,
                                             double* conteudoBruto,
                                             double* tamanhoConteudoMm,
                                             int* achouConteudo,
                                             int* pretoNoBranco,
                                             double* milissegundos,
                                             char* erro,
                                             int tamanhoErro);

#ifdef __cplusplus
}
#endif

#endif  // ST_FERRAMENTAS_H_
