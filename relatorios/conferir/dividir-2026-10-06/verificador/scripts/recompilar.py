"""Verificador 2.1: recompila a st_ferramentas.dll a partir das fontes da COPIA
git archive (trabalho/novo), numa pasta de rascunho PROPRIA (argv[2]),
sem tocar na DLL do programa nem na pasta de rascunho do implementador.
So LE o Qt e o Boost da pasta de ferramentas (sem baixar)."""
import subprocess, sys
from pathlib import Path
NOVO = Path(sys.argv[1]).resolve()
RASC = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(NOVO))
import compilar_detector_gravura as base
import compilar_st_ferramentas as cs
ferr = cs.pasta_de_ferramentas_padrao()
cmake = base.achar_cmake()
base.conferir_visual_studio()
qt = base.garantir_qt(ferr, cmake, False)
boost = base.garantir_boost(ferr, cmake, False)
print("qt", qt, "boost", boost, flush=True)
subprocess.run([str(cmake), "-S", str(cs.PASTA_LIGACAO), "-B", str(RASC), "-G", "Visual Studio 17 2022", "-A", "x64",
                f"-DCMAKE_PREFIX_PATH={qt.as_posix()}", f"-DBOOST_INCLUDEDIR={boost.as_posix()}",
                f"-DST_FERRAMENTAS_ORIGEM={base.texto_de_origem()}"], check=True)
subprocess.run([str(cmake), "--build", str(RASC), "--config", "Release", "--parallel", "4"], check=True)
print("DLL", RASC / "Release" / "st_ferramentas.dll", (RASC / "Release" / "st_ferramentas.dll").is_file())
