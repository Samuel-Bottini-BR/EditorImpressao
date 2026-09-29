# Compila st_gravura.dll: o detector de gravura do ScanTailor Advanced.
#
# Nao rode direto: use  .venv\Scripts\python.exe compilar_detector_gravura.py
# (ele acha o Qt, o Boost e o Visual Studio e passa as variaveis abaixo).
#
# - As bibliotecas do ScanTailor (../src) sao compiladas como estao, com as
#   mesmas opcoes do CMakeLists.txt raiz do ScanTailor Advanced no MSVC:
#   C++17, NOMINMAX, _SECURE_SCL=0, BOOST_MULTI_INDEX_DISABLE_SERIALIZATION.
# - Elas viram uma biblioteca estatica; o vinculador so puxa para a DLL o que
#   st_gravura.cpp usa.
# - Qt: o mesmo Qt 6.11 que o PySide6 traz (Core, Gui e Xml). A DLL nao leva o
#   Qt dentro: usa as DLLs do Qt que ja estao na pasta do PySide6.
#
# ARRISCADO: trocar a versao do Qt aqui sem trocar a do PySide6 (a DLL passa a
# pedir um Qt que o programa nao tem).

cmake_minimum_required(VERSION 3.16)
project(st_gravura LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(BOOST_INCLUDEDIR "" CACHE PATH "Pasta com boost/ (so cabecalhos)")
set(ST_GRAVURA_ORIGEM "ScanTailor Advanced" CACHE STRING "Texto de origem gravado na DLL")

find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Xml)

set(ST_SRC "${CMAKE_CURRENT_SOURCE_DIR}/../src")
file(GLOB st_fontes CONFIGURE_DEPENDS
    "${ST_SRC}/foundation/*.cpp"
    "${ST_SRC}/math/*.cpp"
    "${ST_SRC}/imageproc/*.cpp"
    "${ST_SRC}/core/*.cpp"
    "${ST_SRC}/core/filters/output/*.cpp")

add_library(st_scantailor STATIC ${st_fontes})
target_include_directories(st_scantailor PUBLIC
    "${ST_SRC}"
    "${ST_SRC}/foundation"
    "${ST_SRC}/math"
    "${ST_SRC}/imageproc"
    "${ST_SRC}/core"
    "${ST_SRC}/core/filters/output"
    "${BOOST_INCLUDEDIR}")
target_compile_definitions(st_scantailor PUBLIC
    NOMINMAX _SECURE_SCL=0 BOOST_MULTI_INDEX_DISABLE_SERIALIZATION)
target_link_libraries(st_scantailor PUBLIC Qt6::Core Qt6::Gui Qt6::Xml)

add_library(st_gravura SHARED st_gravura.cpp st_gravura.h)
target_compile_definitions(st_gravura PRIVATE "ST_GRAVURA_ORIGEM=\"${ST_GRAVURA_ORIGEM}\"")
target_link_libraries(st_gravura PRIVATE st_scantailor)
if (MSVC)
  # Tira da DLL o codigo que ninguem chama.
  target_link_options(st_gravura PRIVATE /OPT:REF /OPT:ICF)
endif()
