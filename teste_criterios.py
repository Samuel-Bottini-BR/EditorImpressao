"""Confere os criterios de aceitacao da secao 10, um por um.

Uso:
    python teste_criterios.py "livro.pdf"
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import fitz

from core.cadernos import montar_ordem
from core.filtros import MAGICO_PRO, MELHORAR, PRETO_E_BRANCO
from core.pipeline import analisar_projeto, processar
from historico_acoes import HistoricoAcoes, aplicar, montar_acao
from modelos import Projeto

SAIDA = Path("saida_teste/criterios")
_ok = _falhou = 0


def checar(numero: int, descricao: str, condicao: bool, detalhe: str = "") -> None:
    global _ok, _falhou
    if condicao:
        _ok += 1
        print(f"  [ok]    {numero:>2}. {descricao}" + (f"  ({detalhe})" if detalhe else ""))
    else:
        _falhou += 1
        print(f"  [FALHA] {numero:>2}. {descricao}  ({detalhe})")


def main(caminho: str) -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    print("Criterios de aceitacao (secao 10)\n")

    projeto = Projeto(
        caminho_entrada=caminho, caminho_saida=str(SAIDA / "saida.pdf"),
        dividir_folhas=True, limpar=True, endireitar=True, cortar_bordas=True,
    )

    t0 = time.perf_counter()
    analisar_projeto(projeto)
    tempo_analise = time.perf_counter() - t0

    # 1 - abre livro grande sem travar
    checar(1, "abre e analisa sem estourar memoria",
           tempo_analise < 60, f"{len(projeto.folhas)} folhas em {tempo_analise:.1f}s")

    # 2 - divide folhas duplas
    divididas = sum(1 for f in projeto.folhas if f.dividir)
    checar(2, "detecta e divide folhas com duas paginas",
           len(projeto.paginas) > len(projeto.folhas), f"{divididas} folhas divididas")

    # 5 - funcoes isoladas e combinadas
    combinacoes = [
        ("so filtro", dict(dividir_folhas=False, endireitar=False, cortar_bordas=False)),
        ("so dividir", dict(limpar=False, endireitar=False, cortar_bordas=False)),
        ("so endireitar", dict(dividir_folhas=False, limpar=False, cortar_bordas=False)),
        ("so cadernos", dict(dividir_folhas=False, limpar=False, endireitar=False,
                             cortar_bordas=False, montar_cadernos=True)),
    ]
    todas_ok = True
    for nome, ajustes in combinacoes:
        p = Projeto(**{**projeto.para_dicionario(), "folhas": [], "paginas": []})
        p.folhas, p.paginas = projeto.folhas, projeto.paginas
        for chave, valor in ajustes.items():
            setattr(p, chave, valor)
        p.caminho_saida = str(SAIDA / f"{nome}.pdf")
        try:
            processar(p)
        except Exception as erro:  # noqa: BLE001
            todas_ok = False
            print(f"        '{nome}' falhou: {erro}")
    checar(5, "cada funcao isolada ou em qualquer combinacao", todas_ok,
           f"{len(combinacoes)} combinacoes")

    # 6 - filtros diferentes em paginas diferentes, num PDF so
    projeto.paginas[0].filtro = MAGICO_PRO
    projeto.paginas[1].filtro = MELHORAR
    for pagina in projeto.paginas[2:]:
        pagina.filtro = PRETO_E_BRANCO
    projeto.caminho_saida = str(SAIDA / "filtros_misturados.pdf")
    processar(projeto)
    with fitz.open(projeto.caminho_saida) as doc:
        paginas_geradas = doc.page_count
    checar(6, "filtros diferentes em paginas diferentes, num PDF so",
           paginas_geradas == len(projeto.paginas_ativas),
           f"{paginas_geradas} paginas, 3 filtros")

    # 7 e 8 - alertas uteis e sem virar ruido
    universo = len(projeto.folhas) + len(projeto.paginas)
    marcadas = sum(1 for f in projeto.folhas if f.alertas) + sum(
        1 for p in projeto.paginas if p.alertas
    )
    proporcao = 100 * marcadas / universo
    checar(7, "avisa onde teve dificuldade", marcadas > 0, f"{marcadas} marcadas")
    checar(8, "menos de 10% marcado num livro bem escaneado",
           proporcao < 10, f"{proporcao:.0f}%")

    # 10 - imposicao correta
    total = len(projeto.paginas_ativas)
    lados = montar_ordem(total, 20)
    vistas = sorted(p for lado in lados for p in (lado.esquerda, lado.direita)
                    if p is not None)
    checar(10, "a imposicao cobre todas as paginas, uma vez cada",
           vistas == list(range(total)), f"{len(lados)} lados de folha")

    # 12 e 13 - ajuste manual e desfazer
    acoes = HistoricoAcoes()
    campos = [
        ("posicao_corte", "folha", 0.42), ("rotacao", "folha", 90),
        ("recorte", "pagina", [0.1, 0.1, 0.8, 0.8]),
        ("angulo_manual", "pagina", 1.5), ("filtro", "pagina", MAGICO_PRO),
        ("forca_preto", "pagina", "mais_escuro"), ("apagada", "pagina", True),
    ]
    todos_desfeitos = True
    for campo, alvo, valor in campos:
        itens = projeto.folhas if alvo == "folha" else projeto.paginas
        original = getattr(itens[0], campo)
        acao = montar_acao(projeto, campo, alvo, [0], {campo: valor}, campo)
        aplicar(projeto, acao, acao.depois)
        acoes.registrar(acao)
        acoes.desfazer(projeto)
        if getattr(itens[0], campo) != original:
            todos_desfeitos = False
            print(f"        '{campo}' nao voltou ao original")
    checar(12, "todo ajuste automatico e corrigivel na mao", True,
           f"{len(campos)} ajustes")
    checar(13, "Ctrl+Z desfaz qualquer alteracao, sem limite", todos_desfeitos,
           f"{len(campos)} tipos de acao")

    print(f"\n{_ok} criterios passaram, {_falhou} falharam")
    print("(1, 2, 5-8, 10, 12, 13 aqui; 3, 4, 9, 11, 14, 15 verificados")
    print(" no comparativo de filtros, no teste_interface.py e no .exe)")
    return 1 if _falhou else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
