"""A DLL comum das ferramentas do ScanTailor (item M9 da Fase 2, 06/10/2026).

Testes de máquina:
- DLL ausente ou quebrada: o módulo diz "indisponível" e não derruba nada;
- a DLL abre, é da versão certa e diz de onde veio;
- os tipos das funções no Python (ASSINATURAS) batem com o st_ferramentas.h;
- cópia fiel: TODO arquivo de terceiros/scantailor-advanced/src é o do
  ScanTailor Advanced v1.2.1, sem mudança (somas tiradas do git do ScanTailor);
- a st_gravura.dll do item 1.2 continua a mesma (soma do arquivo).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from core import st_ferramentas as st

RAIZ = Path(__file__).resolve().parent.parent
TERCEIROS = RAIZ / "terceiros" / "scantailor-advanced"
CABECALHO = TERCEIROS / "ligacao-ferramentas" / "st_ferramentas.h"
SOMAS = TERCEIROS / "somas-v1.2.1.txt"

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


# ------------------------------------------------------------- sem a DLL

def test_dll_ausente_fica_indisponivel(tmp_path):
    biblioteca = st.BibliotecaScanTailor(tmp_path / "nao_existe.dll")
    assert not biblioteca.disponivel
    assert "não foram encontradas" in biblioteca.motivo_indisponivel
    assert biblioteca.funcao("st_ferramentas_pontinhos") is None
    assert biblioteca.origem is None


def test_dll_quebrada_fica_indisponivel(tmp_path):
    falsa = tmp_path / "st_ferramentas.dll"
    falsa.write_bytes(b"isto nao e uma DLL")
    biblioteca = st.BibliotecaScanTailor(falsa)
    assert not biblioteca.disponivel
    assert "não abriram" in biblioteca.motivo_indisponivel
    assert biblioteca.detalhe_indisponivel


def test_trava_de_dpi_e_tamanho():
    assert st.motivo_de_recusa(1000, 1000, 300, 300) is None
    assert st.motivo_de_recusa(1000, 1000, 29, 300) is not None
    assert st.motivo_de_recusa(1000, 1000, 300, 2401) is not None
    assert st.motivo_de_recusa(12000, 11000, 300, 300) is not None     # 132 MP
    assert st.motivo_de_recusa(0, 10, 300, 300) is not None


def test_dpi_inteiro():
    assert st.dpi_inteiro(300) == (300, 300)
    assert st.dpi_inteiro((299.6, 150.2)) == (300, 150)
    with pytest.raises(ValueError):
        st.dpi_inteiro(0)


# ------------------------------------------------------------- com a DLL

@precisa_da_dll
def test_abre_versao_e_origem():
    assert "v1.2.1" in st.origem()
    assert "5eaac1884cdc" in st.origem()
    assert st.padrao().funcao("st_ferramentas_pontinhos") is not None


# ------------------------------------------------------------- o .h e o Python

def test_versao_do_python_e_a_do_cabecalho():
    texto = CABECALHO.read_text(encoding="utf-8")
    achado = re.search(r"#define ST_FERRAMENTAS_VERSAO_API (\d+)", texto)
    assert achado and int(achado.group(1)) == st.VERSAO_API


def test_assinaturas_batem_com_o_cabecalho():
    """Cada função do .h está em ASSINATURAS com o mesmo número de argumentos (e vice-versa).
    Um argumento a mais ou a menos no ctypes vira travamento, não mensagem."""
    texto = CABECALHO.read_text(encoding="utf-8")
    no_cabecalho = {}
    for nome, argumentos in re.findall(r"ST_FERRAMENTAS_API [^;(]*?\b(st_ferramentas_\w+)\(([^)]*)\);",
                                       texto, flags=re.S):
        argumentos = argumentos.strip()
        no_cabecalho[nome] = 0 if argumentos in ("", "void") else len(argumentos.split(","))
    assert no_cabecalho, "não achei nenhuma função no st_ferramentas.h"
    assert set(no_cabecalho) == set(st.ASSINATURAS)
    for nome, quantos in no_cabecalho.items():
        assert len(st.ASSINATURAS[nome][1]) == quantos, nome


# ------------------------------------------------------------- cópia fiel

def _somas_do_original() -> dict[str, str]:
    somas = {}
    for linha in SOMAS.read_text(encoding="utf-8").splitlines():
        if linha.startswith("#") or not linha.strip():
            continue
        soma, caminho = linha.split(maxsplit=1)
        somas[caminho.strip()] = soma
    return somas


def test_codigo_do_scantailor_sem_mudanca():
    """Cada arquivo de src/ (sem o CR que o git deste PC põe) tem a soma do
    original v1.2.1, e não há arquivo a mais nem a menos. As somas foram tiradas
    do próprio git do ScanTailor (git show v1.2.1:<arquivo>), não da nossa cópia."""
    somas = _somas_do_original()
    no_projeto = sorted(p.relative_to(TERCEIROS).as_posix()
                        for p in (TERCEIROS / "src").rglob("*") if p.is_file())
    assert sorted(somas) == no_projeto
    mudados = [rel for rel in no_projeto
               if hashlib.sha256((TERCEIROS / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
               != somas[rel]]
    assert mudados == []


def test_o_despeckle_esta_entre_os_conferidos():
    somas = _somas_do_original()
    for rel in ("src/core/Despeckle.cpp", "src/core/Despeckle.h",
                "src/imageproc/ConnectivityMap.cpp", "src/imageproc/InfluenceMap.cpp"):
        assert rel in somas


# ------------------------------------------------------------- o 1.2 não mudou

# SHA-256 da core/nativo/st_gravura.dll do item 1.2, a de core/nativo/st_gravura.txt
# (compilada em 28/09/2026). A DLL comum fica AO LADO dela e não a substitui:
# este teste pega quem recompilar ou trocar a do 1.2 sem querer. Se a st_gravura
# for recompilada de propósito, conferir as máscaras do gabarito antes de mudar
# esta soma.
SHA256_ST_GRAVURA = "833d03db094e4f8a6ff811491f30b603f78558e1ec7b452b2f08b0c2bee4193f"


def test_a_dll_do_1_2_nao_mudou():
    dll = RAIZ / "core" / "nativo" / "st_gravura.dll"
    assert hashlib.sha256(dll.read_bytes()).hexdigest() == SHA256_ST_GRAVURA
