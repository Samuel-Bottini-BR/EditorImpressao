// st_ferramentas: as ferramentas de imagem do ScanTailor Advanced, numa DLL so,
// expostas em C para o Python chamar por ctypes (item M9 da Fase 2).
//
// Copyright (C) 2026  Editor de Impressao (ligacao)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// Funcoes em C puro (sem classes C++ na fronteira) para a DLL nao depender da
// versao do Python. Quem chama: core/st_ferramentas.py (carrega a DLL) e um
// modulo por ferramenta (core/pontinhos_scantailor.py, core/dividir_scantailor.py,
// core/endireitar_scantailor.py).
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
// 4 = reservado para as caixas da pagina e do conteudo (ramo fase2-caixa-conteudo,
//     12/10/2026, ainda nao juntado). Quem juntar os dois ramos sobe para 6.
// 5 = 20/10/2026: + o preto e branco do ScanTailor (st_ferramentas_preto_e_branco,
//     item 2.8, em saida.cpp); o que ja existia nao mudou.
// 6 = 20/10/2026: + as cores do ScanTailor (st_ferramentas_cores, item 2.11, em
//     saida.cpp); o que ja existia nao mudou.
// 7 = 21/10/2026: + o desentortar do ScanTailor (st_ferramentas_desentortar,
//     item 2.12, em desentortar.cpp); o que ja existia nao mudou.
// 8 = 22/10/2026: o desentortar recebe a pagina com o papel do scan em volta e
//     o corte como medida (corteX..corteAltura); a saida tem o tamanho do corte
//     (escolha do Samuel na Central, 22/10: "cortar uma vez so, no fim", como o
//     ScanTailor). O resto nao mudou.
#define ST_FERRAMENTAS_VERSAO_API 8

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

// PRETO E BRANCO DO SCANTAILOR (a saida "Black and white" dele, item 2.8; a cola
// esta em saida.cpp, com as funcoes de OutputGenerator.cpp copiadas sem mudanca
// e os dez jeitos de src/imageproc/Binarize.cpp).
//
// pixels, largura, altura, passo, canais: a pagina ja preparada pelo programa
//   (girada, cortada), como no dividir (1 = cinza; 3 = azul, verde, vermelho).
// dpiX, dpiY: o DPI da imagem (muda a suavizacao Savitzky-Golay).
// metodo: o BinarizationMethod do ScanTailor: 0 Otsu, 1 Sauvola, 2 Wolf,
//   3 Fox, 4 Window, 5 Bradley, 6 Grad, 7 EdgePlus, 8 BlurDiv, 9 EdgeDiv.
// ajusteDoLimiar: o "thresholdAdjustment" (-100 a 100 na tela dele; 0 de
//   fabrica). Mais = mais preto.
// janela: windowSize (200 de fabrica). coefSauvola: 0,34 de fabrica.
//   coefWolf: 0,3. wolfMinimo, wolfMaximo: 1 e 254.
// normalizar, savitzkyGolay, morfologica: 1 = ligado (os tres ligados de fabrica).
// saida, passoSaida: o preto e branco, 1 byte por ponto: 0 = preto, 255 = branco.
// erro, tamanhoErro: texto do erro, se houver.
//
// So le a pagina. Devolve ST_FERRAMENTAS_OK ou um codigo de erro.
// Nunca deixa excecao escapar.
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
                                                     int tamanhoErro);

// AS CORES DO SCANTAILOR (item 2.11; cola em saida.cpp): "letras com a cor delas"
// (Color segmentation, src/imageproc/ColorSegmenter.cpp) e "reduzir cores"
// (Posterize, src/imageproc/Posterizer.cpp), sem mudanca.
//
// pixels, largura, altura, passo, canais: a pagina (1 = cinza; 3 = azul, verde,
//   vermelho). Com segmentar = 1, a pagina preparada ANTES do filtro (a cor das
//   letras sai dela); com segmentar = 0, a pagina ja filtrada, a posterizar.
// pretoEBranco, passoPretoEBranco: so com segmentar = 1: o preto e branco da
//   pagina, 1 byte por ponto (menor que 128 = preto). Cada peca preta e pintada
//   com a cor dela; o resto sai branco.
// dpiX, dpiY: o DPI (o tamanho do ruido que a segmentacao tira acompanha o DPI).
// normalizar: 1 = iguala a luz da pagina antes de tirar as cores (o de fabrica do
//   preto e branco do ScanTailor).
// ruido: "Reduce noise" (7 de fabrica). ajusteVermelho/Verde/Azul: 0 de fabrica.
// posterizar, nivel (4 de fabrica), normalizarCores (0), forcarPretoEBranco (1):
//   as opcoes do "Posterize".
// saida, passoSaida: o resultado em cor, 3 bytes por ponto (azul, verde, vermelho).
// Devolve ST_FERRAMENTAS_OK ou um codigo de erro. Nunca deixa excecao escapar.
ST_FERRAMENTAS_API int st_ferramentas_cores(const unsigned char* pixels,
                                            int largura,
                                            int altura,
                                            int passo,
                                            int canais,
                                            const unsigned char* pretoEBranco,
                                            int passoPretoEBranco,
                                            int dpiX,
                                            int dpiY,
                                            int normalizar,
                                            int segmentar,
                                            int ruido,
                                            int ajusteVermelho,
                                            int ajusteVerde,
                                            int ajusteAzul,
                                            int posterizar,
                                            int nivel,
                                            int normalizarCores,
                                            int forcarPretoEBranco,
                                            unsigned char* saida,
                                            int passoSaida,
                                            char* erro,
                                            int tamanhoErro);

// DESENTORTAR A PAGINA CURVA PERTO DA LOMBADA (item 2.12): o "Dewarping" do
// ScanTailor (src/dewarping, sem mudanca; a ordem em desentortar.cpp).
//
// pixels, largura, altura, passo, canais: a pagina ja dividida e endireitada,
//   AINDA SEM O CORTE, com o papel do proprio scan em volta (canais 1 = cinza;
//   3 = azul, verde, vermelho, como o OpenCV). Versao 8, 22/10/2026.
// dpiX, dpiY: o DPI da imagem (o TextLineTracer reduz para 200 DPI por ele).
// modo: 1 = automatico (AUTO, pelas linhas do texto); 3 = pelas margens
//   (MARGINAL). Os numeros sao os de output::DewarpingMode. 0 (desligado, o de
//   fabrica) nao chega aqui: o Python nem chama.
// lado: 0 = pagina unica, 1 = esquerda, 2 = direita (PageId::SubPage).
// profundidade: a "Depth perception" do ScanTailor, de 1,0 a 3,0 (2,0 de fabrica).
// endireitarDepois: o "post deskew" (1 de fabrica; so vale no "pelas margens").
// corteX, corteY, corteLargura, corteAltura: o corte medido pelo programa, em
//   pontos da pagina recebida: e a pagina de saida do ScanTailor (m_outRect).
//   Largura ou altura 0 = a pagina inteira (sem corte). Tem de caber na pagina.
// conteudoX, conteudoY, conteudoLargura, conteudoAltura: a caixa do conteudo
//   (m_contentRect), em pontos da pagina recebida; largura ou altura 0 = o corte.
// saida, passoSaida: a pagina desentortada JA RECORTADA pelo corte (corteLargura
//   x corteAltura), com os mesmos canais. O corte e feito uma vez, aqui, como no
//   ScanTailor: o desentortar le os pontos da pagina inteira.
// achouCurvas: 1 se as curvas achadas nao sao as do modelo "sem curva".
// anguloDepois: o angulo do endireitar depois, em graus (0 se nao endireitou).
// Devolve ST_FERRAMENTAS_OK ou um codigo de erro. Nunca deixa excecao escapar.
ST_FERRAMENTAS_API int st_ferramentas_desentortar(const unsigned char* pixels,
                                                  int largura,
                                                  int altura,
                                                  int passo,
                                                  int canais,
                                                  int dpiX,
                                                  int dpiY,
                                                  int modo,
                                                  int lado,
                                                  double profundidade,
                                                  int endireitarDepois,
                                                  int corteX,
                                                  int corteY,
                                                  int corteLargura,
                                                  int corteAltura,
                                                  int conteudoX,
                                                  int conteudoY,
                                                  int conteudoLargura,
                                                  int conteudoAltura,
                                                  unsigned char* saida,
                                                  int passoSaida,
                                                  int* achouCurvas,
                                                  double* anguloDepois,
                                                  char* erro,
                                                  int tamanhoErro);

#ifdef __cplusplus
}
#endif

#endif  // ST_FERRAMENTAS_H_
