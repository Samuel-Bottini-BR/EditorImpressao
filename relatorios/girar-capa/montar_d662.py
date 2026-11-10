"""Monta as imagens da D-662 (relatorios/girar-capa) com o que gerar_d662.py gravou.

    python montar_d662.py <pasta crua (com antes/ e depois/)> <pasta de saída>

O mesmo jeito das imagens da pergunta 3 de 09/11 (relatorios/girar-capa-provas/montar_provas.py, de
onde vêm as peças: faixa colorida com o rótulo grande, legenda embaixo, páginas 18 e 19 circuladas em
vermelho). "antes/" = o programa sem o conserto (3216b885); "depois/" = com o conserto (c76d4b97).
Seguro mudar: textos e tamanhos. As fotos cruas não são mexidas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "girar-capa-provas"))
from montar_provas import (  # noqa: E402
    CORES,
    LARGURA,
    FUNDO,
    _abrir,
    _area_da_folha,
    _cabeca,
    _empilhar,
    _fonte,
    _grade,
    _salvar,
    _sem_numero,
    _tela,
)
from PIL import Image, ImageDraw  # noqa: E402

NUMEROS = [1, 18, 19, 20, 21]
EXTRA = {1: "1 (capa)"}


def _titulo(texto: str) -> Image.Image:
    t = Image.new("RGB", (LARGURA - 40, 46), FUNDO)
    ImageDraw.Draw(t).text((0, 4), texto, fill=(30, 30, 30), font=_fonte(30, True))
    return t


def _medida(estado: dict) -> str:
    partes = []
    for m in estado["medida"]:
        if m["diferenca_media"] is None:
            partes.append(f"página {m['pagina']}: tira de {m['depois'][1]}x{m['depois'][0]} pontos "
                          f"(a página inteira deitada teria {m['antes_girada'][1]}x{m['antes_girada'][0]})")
        else:
            partes.append(f"página {m['pagina']}: inteira, deitada ({m['depois'][1]}x{m['depois'][0]}, "
                          f"diferença {m['diferenca_media']} de 255)")
    return "Medida no PDF: " + "; ".join(partes) + "."


def main() -> None:
    cru, saida = Path(sys.argv[1]), Path(sys.argv[2])
    antes, depois = cru / "antes", cru / "depois"
    est_antes = json.loads((antes / "estado.json").read_text(encoding="utf-8"))
    est_depois = json.loads((depois / "estado.json").read_text(encoding="utf-8"))
    legendas: dict = {}
    situacoes = (
        ("antes", "ANTES do clique", depois, "tela-antes-dividir.png", "antes",
         "Gradus Primus (cópia). Ferramenta Dividir, vista \"Duas lado a lado\", folha 10 (páginas 18 "
         "e 19, em vermelho). A folha aparece inteira, com a linha azul no meio. Tudo em pé."),
        ("fica", "DEPOIS — programa de antes do conserto", antes, "tela-depois-dividir.png", "depois",
         "\"todas as folhas\" + ¼ à direita: as 70 folhas giram INTEIRAS e a linha azul fica no mesmo "
         "lugar; ela corta as duas páginas deitadas ao meio: cada página sai no PDF como uma tira "
         "com metade da 18 e metade da 19. " + _medida(est_antes)),
        ("pagina", "DEPOIS — com o conserto (\"Página por página também\")", depois,
         "tela-depois-dividir.png", "depois",
         "O mesmo clique: cada página deita sozinha, inteira, sem pedaço da vizinha; a capa gira "
         "inteira; a linha não muda. A folha grande do Dividir continua em pé (a tela mostra o scan); "
         "as miniaturas e o PDF mostram as páginas deitadas. " + _medida(est_depois)),
    )
    resumo = []
    for n, (chave, rotulo, pasta, tela, prefixo, legenda) in enumerate(situacoes, start=1):
        minis = [_sem_numero(m) for m in _abrir(pasta, [f"mini-{prefixo}-{i}.png" for i in NUMEROS])]
        paginas = _abrir(pasta, [f"pdf-{prefixo}-{i}.png" for i in range(1, 6)])
        img = _empilhar([
            _cabeca(rotulo, CORES[chave], legenda),
            _titulo("1) A tela do Dividir (\"Duas lado a lado\"), folha 10:"),
            _tela(pasta, tela),
            _titulo("2) As miniaturas das páginas (tira da área de trabalho):"),
            _grade(minis, NUMEROS, 5, 170, {18, 19}, moldura=False, legenda_extra=EXTRA),
            _titulo("3) As páginas como saem no PDF:"),
            _grade(paginas, NUMEROS, 5, 260, {18, 19}, legenda_extra=EXTRA),
        ])
        _salvar(img, saida / f"d662-{n}-{chave}.png", legendas, f"{rotulo}. {legenda}")
        resumo.append(_empilhar([
            _cabeca(rotulo, CORES[chave], {
                "antes": "Dividir, \"Duas lado a lado\", folha 10 (páginas 18 e 19). Tudo em pé.",
                "fica": "As folhas giram inteiras: cada página sai uma tira com metade de duas.",
                "pagina": "Cada página deita sozinha e inteira; a capa gira inteira."}[chave]),
            _area_da_folha(pasta, tela, 640),
            _grade(paginas, NUMEROS, 5, 260, {18, 19}, legenda_extra=EXTRA)], espaco=6))
    img = _empilhar([_cabeca("D-662 — resumo", (40, 40, 40),
                             "Dividir com \"Duas lado a lado\", \"todas as folhas\" + ¼ à direita. Em "
                             "cada parte: a tela do Dividir e as páginas como saem no PDF."), *resumo])
    _salvar(img, saida / "d662-resumo.png", legendas,
            "Resumo da D-662: antes do clique, o programa de antes e o programa com o conserto.")
    (saida / "d662-estado-antes-do-conserto.json").write_bytes((antes / "estado.json").read_bytes())
    (saida / "d662-estado-com-o-conserto.json").write_bytes((depois / "estado.json").read_bytes())
    (saida / "d662-legendas.json").write_text(json.dumps(legendas, ensure_ascii=False, indent=1),
                                              encoding="utf-8")
    print("ok", saida)


if __name__ == "__main__":
    main()
