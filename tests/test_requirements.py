"""O requirements.txt lista as bibliotecas de que o programa precisa.

Numa instalacao do zero (pip install -r requirements.txt), o que faltar ali
nao e instalado - e varias partes do programa se desligam CALADAS quando a
biblioteca falta, em vez de dar erro. Por isso o teste: o erro nao aparece
em lugar nenhum, so o resultado piora.

(A biblioteca markdown, dos relatorios, tem o seu teste em test_relatorio.py.)
"""

from __future__ import annotations

from pathlib import Path

REQUIREMENTS = Path(__file__).resolve().parent.parent / "requirements.txt"


def _nomes_no_requirements() -> list[str]:
    """Os nomes de pacote do requirements.txt, em minusculas, sem versao."""
    nomes = []
    for linha in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        linha = linha.split("#", 1)[0].strip()
        if linha:
            for separador in (">=", "==", "<=", "~=", ">", "<"):
                linha = linha.split(separador, 1)[0]
            nomes.append(linha.strip().lower())
    return nomes


def test_onnxruntime_esta_no_requirements():
    """Bug de 28/09/2026: o onnxruntime roda as duas redes neurais do
    programa - o detector de gravura e letra (core/detectar_regioes.py) e a
    selecao por clique (core/rede_selecao.py) - e nao estava no
    requirements.txt. Sem ele, os dois se desligam sem avisar: o import fica
    dentro de um try, de proposito, para o programa continuar funcionando."""
    assert "onnxruntime" in _nomes_no_requirements()


def test_o_codigo_ainda_usa_o_onnxruntime():
    """Se um dia o core deixar de usar o onnxruntime, a linha do
    requirements.txt vira peso morto (e este teste avisa)."""
    raiz = REQUIREMENTS.parent
    usam = [nome for nome in ("core/detectar_regioes.py", "core/rede_selecao.py")
            if "import onnxruntime" in (raiz / nome).read_text(encoding="utf-8")]

    assert usam == ["core/detectar_regioes.py", "core/rede_selecao.py"]
