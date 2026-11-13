"""Quadrados na capa (13/11/2026): as imagens de "onde acontece" (chamado por montar.py), a partir
de _trabalho/matriz/<versao>/<livro>/<variante>/ (rodar_matriz.sh) e das medidas
(medir_quadros.py). As celulas circuladas em vermelho sao as que eu marquei OLHANDO (CIRCULAR,
abaixo), conferidas com a medida; a lista e a mesma do relatorio."""
from __future__ import annotations

import json
from pathlib import Path

import pecas_imagem as P

NOMES = {
    "original": "Original",
    "pb+resp1": "P&B, Respeitar ✓",
    "pb+resp0": "P&B, Respeitar ✗",
    "pb+resp1+cinza1": "P&B, Resp. ✓ + cinza",
    "pb+resp0+cinza1": "P&B, Resp. ✗ + cinza",
    "pb+letras1": "P&B + Só as letras",
    "pb+letras_tudo": "Só as letras, Guardar tudo",
    "melhorar+resp1": "Melhorar, Resp. ✓",
    "melhorar+resp0": "Melhorar, Resp. ✗",
    "magico+resp1": "Mágico pro, Resp. ✓",
    "magico+resp0": "Mágico pro, Resp. ✗",
    "fundo": "Tirar o fundo",
    "auto+pb+resp1": "Auto: P&B, Resp. ✓",
    "auto+pb+resp0": "Auto: P&B, Resp. ✗",
    "auto+pb+letras1": "Auto: Só as letras",
    "auto+pb+resp0+cinza1": "Auto: P&B ✗ + cinza",
    "auto+melhorar+resp1": "Auto: Melhorar ✓",
    "auto+melhorar+resp0": "Auto: Melhorar ✗",
    "auto+magico+resp1": "Auto: Mágico ✓",
    "auto+magico+resp0": "Auto: Mágico ✗",
}
GRUPOS = (
    ("À mão — Preto e branco", ["pb+resp1", "pb+resp0", "pb+resp1+cinza1", "pb+resp0+cinza1",
                                "pb+letras1", "pb+letras_tudo"]),
    ("À mão — os outros filtros", ["original", "melhorar+resp1", "melhorar+resp0",
                                   "magico+resp1", "magico+resp0", "fundo"]),
    ("Pelo Automático (\"Limpar a folha\" + \"Gravuras e fotos\")",
     ["auto+pb+resp1", "auto+pb+resp0", "auto+pb+letras1", "auto+pb+resp0+cinza1",
      "auto+melhorar+resp1", "auto+melhorar+resp0", "auto+magico+resp1", "auto+magico+resp0"]),
)
LIVROS = {"gradus": "Gradus Primus, capa (p. 1)", "escola": "Na escola de Jesus, capa (p. 1)",
          "matematica": "Matemática para vencer, capa (p. 1)", "pesel": "Pesel, capa (p. 1)",
          "destino": "Destino do socialismo, capa (p. 1)"}
# o que eu vi, olhando cada imagem (preenchido depois de olhar; ver o relatorio)
CIRCULAR: dict = {}


def _celula(pasta: Path, livro: str, variante: str, circ: set, caixa: int = 220):
    arq = pasta / livro / variante / "pdf.png"
    if not arq.exists():
        return None
    img = P.abrir(arq)
    if livro == "gradus":                      # so a capa (a metade da direita)
        img = P.recorte(img, (0.5, 0.0, 1.0, 1.0))
    img = P.caber(img, caixa, int(caixa * 1.45))
    return P.com_titulo(img, NOMES.get(variante, variante), vermelho=variante in circ, tamanho=17)


def _grade(celulas, por_linha: int):
    linhas = [P.lado_a_lado(celulas[i:i + por_linha], espaco=12)
              for i in range(0, len(celulas), por_linha)]
    return P.empilhar(linhas, espaco=8, largura=max(x.width for x in linhas) + 20)


def _circular_celula(cel):
    from PIL import ImageDraw
    d = ImageDraw.Draw(cel)
    d.ellipse([2, 2, cel.width - 3, cel.height - 3], outline=P.VERMELHO, width=5)
    return cel


def montar(T: Path, SAIDA: Path, LEG: dict) -> None:
    base = T / "matriz"
    n = 5
    for versao, cor, rot in (("quadrados-capa", P.LARANJA, "versão de teste (hoje)"),):
        for livro, nome in LIVROS.items():
            circ = CIRCULAR.get((versao, livro), set())
            partes = [P.cabeca(f"{nome} — {rot}", P.CINZA,
                               "Livro novo; cada quadro é uma escolha, como sai no PDF. Em vermelho e "
                               "circulado: onde aparecem quadrados ou caixas que não existem no original.")]
            for titulo, variantes in GRUPOS:
                cel = []
                for v in variantes:
                    c = _celula(base / versao, livro, v, circ)
                    if c is not None:
                        cel.append(_circular_celula(c) if v in circ else c)
                if cel:
                    partes.append(P.empilhar([P.cabeca(titulo, cor, ""), _grade(cel, 8)], espaco=4))
            img = P.empilhar(partes, espaco=8)
            if img.width > 1600:
                img = img.resize((1600, round(img.height * 1600 / img.width)))
            nomearq = f"{n}-{livro}-todas-as-escolhas.png"
            P.salvar(img, SAIDA / nomearq)
            LEG[nomearq] = (f"{nome}: todas as escolhas como saem no PDF; circuladas as que têm "
                            f"quadrado ou caixa que não existe no original ({', '.join(NOMES[v] for v in sorted(circ)) or 'nenhuma'}).")
            n += 1
    med = {}
    for versao in ("quadrados-capa", "quadrados-c"):
        for livro in LIVROS:
            arq = base / versao / livro / "medidas.json"
            if arq.exists():
                med[f"{versao}/{livro}"] = json.loads(arq.read_text(encoding="utf-8"))
    (SAIDA.parent / "medidas").mkdir(exist_ok=True)
    (SAIDA.parent / "medidas" / "matriz.json").write_text(json.dumps(med, indent=1), encoding="utf-8")
