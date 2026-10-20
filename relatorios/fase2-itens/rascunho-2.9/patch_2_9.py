"""Aplica as mudanças do item 2.9 em core/pipeline.py e modelos.py (rodar da worktree)."""
from pathlib import Path

p = Path("core/pipeline.py")
t = p.read_text(encoding="utf-8")

# 1. a assinatura da gravura leva a caixinha (só quando ligada)
old = '''    if not pagina.selecao or not getattr(pagina, "gravura_feita_com", ""):
        return False
    return pagina.gravura_feita_com != assinatura_da_gravura(*escolha_da_gravura(projeto, pagina))'''
new = '''    if not pagina.selecao or not getattr(pagina, "gravura_feita_com", ""):
        return False
    return pagina.gravura_feita_com != _assinatura_da_gravura_da_pagina(projeto, pagina)


def _assinatura_da_gravura_da_pagina(projeto: Projeto, pagina: ConfigPagina) -> str:
    """A assinatura das opcoes com que a gravura desta pagina e achada
    (core.detectar_regioes.assinatura_da_gravura) e, desde o item 2.9, a
    caixinha "Letra clara em fundo escuro": com ela ligada, o detector ve a
    pagina invertida (como no ScanTailor), e a assinatura ganha
    claro_no_escuro.SUFIXO_DA_GRAVURA. Desligada, a assinatura e a de sempre
    (nenhum livro ja comecado refaz a marcacao). Arriscado: por o sufixo
    sempre (todas as paginas refariam a gravura)."""
    from core.detectar_regioes import assinatura_da_gravura

    assinatura = assinatura_da_gravura(*escolha_da_gravura(projeto, pagina))
    if claro_no_escuro.ligado(pagina):
        assinatura += claro_no_escuro.SUFIXO_DA_GRAVURA
    return assinatura'''
assert old in t, 1
t = t.replace(old, new)

old = '''    pagina.gravura_feita_com = assinatura_da_gravura(detector, opcoes)'''
new = '''    pagina.gravura_feita_com = _assinatura_da_gravura_da_pagina(projeto, pagina)   # item 2.9'''
assert old in t, 2
t = t.replace(old, new)

# 2. _filtrar inverte na entrada e na saida
old = '''def _filtrar(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray,
             dpi: float | None = None, dpi_do_scan: float | None = None) -> tuple[np.ndarray, bool]:
    """Etapa 4: o filtro da pagina, com a marcacao de gravura/letra/papel.
'''
new = '''def _filtrar(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray,
             dpi: float | None = None, dpi_do_scan: float | None = None) -> tuple[np.ndarray, bool]:
    """Etapa 4: o filtro da pagina, com a marcacao de gravura/letra/papel.

    Item 2.9 (20/10/2026, Samuel P9 (a)): pagina com a caixinha "Letra clara
    em fundo escuro" (core.claro_no_escuro) passa invertida por todo o
    caminho abaixo - marcacao de gravura inclusive - e o resultado e invertido
    de novo, como o ScanTailor faz (initFilterData e o fim da saida). Original
    e "Tirar o fundo" nao mudam (inverter duas vezes daria a mesma pagina).
    Caixinha desmarcada (o de fabrica): nenhuma conta a mais.
'''
assert old in t, 3
t = t.replace(old, new)

old = '''    if not projeto.limpar:
        _anotar_tinta_forte_fora(pagina, False)
        return img, False
    if pagina.filtro == TIRAR_FUNDO:'''
new = '''    if not projeto.limpar:
        _anotar_tinta_forte_fora(pagina, False)
        return img, False
    if claro_no_escuro.ligado(pagina) and pagina.filtro not in (ORIGINAL, TIRAR_FUNDO):
        saida, monocromatica = _filtrar_preto_no_branco(
            projeto, pagina, claro_no_escuro.inverter(img), dpi, dpi_do_scan)
        return claro_no_escuro.inverter(saida), monocromatica
    return _filtrar_preto_no_branco(projeto, pagina, img, dpi, dpi_do_scan)


def _filtrar_preto_no_branco(projeto: Projeto, pagina: ConfigPagina, img: np.ndarray,
                             dpi: float | None = None,
                             dpi_do_scan: float | None = None) -> tuple[np.ndarray, bool]:
    """O corpo de _filtrar (ver a explicacao la): a pagina tratada como letra
    escura em papel claro. Chamado direto, ou com a pagina ja invertida
    (item 2.9). Arriscado: chamar daqui fora sem passar por _filtrar (a
    caixinha "Letra clara em fundo escuro" deixaria de valer)."""
    if pagina.filtro == TIRAR_FUNDO:'''
assert old in t, 4
t = t.replace(old, new)

old = '''from core import dividir_scantailor, endireitar_scantailor, linhas_do_texto, misto, pontinhos_scantailor'''
assert old in t, 5
t = t.replace(old, old + '''
from core import claro_no_escuro''', 1)
p.write_text(t, encoding="utf-8", newline="\n")

m = Path("modelos.py")
t = m.read_text(encoding="utf-8")
old = '''    algoritmo_preto_branco: str = "auto"'''
new = '''    algoritmo_preto_branco: str = "auto"
    # Item 2.9 (Samuel P9 (a), 05/10/2026): a caixinha "Letra clara em fundo
    # escuro" desta pagina, marcada a mao (core.claro_no_escuro). Desmarcada de
    # fabrica; projeto salvo antes abre desmarcado (campo que falta ganha o
    # padrao). Arriscado: vir marcada (a pagina sairia com as cores trocadas
    # no tratamento).
    claro_no_escuro: bool = False'''
assert old in t, 6
t = t.replace(old, new)
m.write_text(t, encoding="utf-8", newline="\n")
print("ok")
