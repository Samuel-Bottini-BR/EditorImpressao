// st_ferramentas: o que e comum a todas as ferramentas (versao e origem).
//
// Copyright (C) 2026  Editor de Impressao (ligacao)
// Use of this source code is governed by the GNU GPLv3 license that can be found in the LICENSE file.
//
// Cada ferramenta mora no seu proprio .cpp desta pasta (pontinhos.cpp, ...).
// Aqui so ficam as duas funcoes que o Python chama ao abrir a DLL.

#include "st_ferramentas.h"

extern "C" {

ST_FERRAMENTAS_API int st_ferramentas_versao_api(void) {
  return ST_FERRAMENTAS_VERSAO_API;
}

ST_FERRAMENTAS_API const char* st_ferramentas_origem(void) {
  return ST_FERRAMENTAS_ORIGEM;
}

}  // extern "C"
