# Compila st_ferramentas.dll: as ferramentas de imagem do ScanTailor Advanced
# numa DLL so (item M9 da Fase 2). Hoje: limpar pontinhos.
#
# Nao rode direto: use  .venv\Scripts\python.exe compilar_st_ferramentas.py
# (ele acha o Qt, o Boost e o Visual Studio e passa as variaveis abaixo).
#
# - TODO o codigo de ../src (o do ScanTailor, sem mudanca) vira uma biblioteca
#   estatica, com as mesmas opcoes do CMakeLists.txt raiz do ScanTailor Advanced
#   no MSVC: C++17, NOMINMAX, _SECURE_SCL=0, BOOST_MULTI_INDEX_DISABLE_SERIALIZATION
#   (e _USE_MATH_DEFINES, que math/ e dewarping/ pedem). O vinculador so puxa
#   para a DLL o que as funcoes em C usam: trazer arquivo novo para ../src nao
#   muda as ferramentas que ja existem.
# - Cada ferramenta e um .cpp desta pasta (GLOB abaixo): acrescentar um nao pede
#   mexer aqui.
# - Qt: o mesmo Qt 6.11 que o PySide6 traz (Core, Gui e Xml). A DLL nao leva o
#   Qt dentro: usa as DLLs do Qt que ja estao na pasta do PySide6.
#
# A st_gravura.dll (item 1.2, pasta ../ligacao) continua compilada a parte, pelo
# compilar_detector_gravura.py, e NAO e afetada por este arquivo.
#
# ARRISCADO:
# - trocar a versao do Qt sem trocar a do PySide6 (a DLL passa a pedir um Qt que
#   o programa nao tem);
# - ST_PASTAS_DE_CABECALHO: o ScanTailor inclui os cabecalhos so pelo nome, de
#   varias pastas. Ao trazer os filtros de geometria (page_split, deskew,
#   select_content), cada um tem Settings.h, Task.h etc. com o MESMO nome; ponha
#   so a pasta do filtro cuja cola precisa dela, para nao pegar o Settings.h
#   errado (no ScanTailor cada filtro e uma biblioteca separada pelo mesmo motivo).

cmake_minimum_required(VERSION 3.16)
project(st_ferramentas LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(BOOST_INCLUDEDIR "" CACHE PATH "Pasta com boost/ (so cabecalhos)")
set(ST_FERRAMENTAS_ORIGEM "ScanTailor Advanced" CACHE STRING "Texto de origem gravado na DLL")

find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Xml)

set(ST_SRC "${CMAKE_CURRENT_SOURCE_DIR}/../src")
file(GLOB_RECURSE st_fontes CONFIGURE_DEPENDS "${ST_SRC}/*.cpp")

set(ST_PASTAS_DE_CABECALHO
    "${ST_SRC}"
    "${ST_SRC}/foundation"
    "${ST_SRC}/math"
    "${ST_SRC}/imageproc"
    "${ST_SRC}/core"
    "${ST_SRC}/core/filters/output")

add_library(st_ferramentas_scantailor STATIC ${st_fontes})
target_include_directories(st_ferramentas_scantailor PUBLIC ${ST_PASTAS_DE_CABECALHO} "${BOOST_INCLUDEDIR}")
target_compile_definitions(st_ferramentas_scantailor PUBLIC
    NOMINMAX _SECURE_SCL=0 BOOST_MULTI_INDEX_DISABLE_SERIALIZATION _USE_MATH_DEFINES)
target_link_libraries(st_ferramentas_scantailor PUBLIC Qt6::Core Qt6::Gui Qt6::Xml)

file(GLOB ligacao_fontes CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.h")
add_library(st_ferramentas SHARED ${ligacao_fontes})
target_compile_definitions(st_ferramentas PRIVATE "ST_FERRAMENTAS_ORIGEM=\"${ST_FERRAMENTAS_ORIGEM}\"")
target_link_libraries(st_ferramentas PRIVATE st_ferramentas_scantailor)
if (MSVC)
  # Tira da DLL o codigo que ninguem chama.
  target_link_options(st_ferramentas PRIVATE /OPT:REF /OPT:ICF)
endif()
