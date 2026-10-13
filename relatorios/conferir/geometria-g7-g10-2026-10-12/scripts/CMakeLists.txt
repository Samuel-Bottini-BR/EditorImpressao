# Teste do pesquisador (12/10/2026): caixas.cpp. NAO faz parte do programa.
# Liga na biblioteca que o teste de 01/10 ja compilou (st_tudo.lib, o codigo
# do ScanTailor Advanced v1.2.1 sem mudanca), para nao recompilar o ScanTailor.
# Uso (ver compilar_caixas.ps1): cmake -S . -B <pasta de rascunho> -G "Visual Studio 17 2022" -A x64
#      -DCMAKE_PREFIX_PATH=<Qt 6.11.1 msvc2022_64>
cmake_minimum_required(VERSION 3.16)
project(caixas_g7_g10 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Xml)
set(FERRAMENTAS "D:/programas/EditorImpressao-arquivos/ferramentas")
set(ST "${FERRAMENTAS}/scantailor-advanced-v1.2.1/src")
set(BOOST "${FERRAMENTAS}/boost/boost_1_78_0")
set(ST_TUDO "${FERRAMENTAS}/pesquisa-fase2-2026-10-01/build/Release/st_tudo.lib")
add_executable(caixas caixas.cpp)
target_include_directories(caixas PRIVATE ${ST} ${ST}/foundation ${ST}/math ${ST}/imageproc ${ST}/core ${ST}/dewarping
  ${ST}/core/filters/page_split ${ST}/core/filters/select_content ${ST}/core/filters/deskew ${BOOST})
target_compile_definitions(caixas PRIVATE NOMINMAX _SECURE_SCL=0 BOOST_MULTI_INDEX_DISABLE_SERIALIZATION _USE_MATH_DEFINES)
target_link_libraries(caixas PRIVATE ${ST_TUDO} Qt6::Core Qt6::Gui Qt6::Xml)
