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
    "pb+resp1": "P&B, Respeitar sim",
    "pb+resp0": "P&B, Respeitar não",
    "pb+resp1+cinza1": "P&B, Resp. sim + cinza",
    "pb+resp0+cinza1": "P&B, Resp. não + cinza",
    "pb+letras1": "P&B + Só as letras",
    "pb+letras_tudo": "Só as letras, Guardar tudo",
    "melhorar+resp1": "Melhorar, Resp. sim",
    "melhorar+resp0": "Melhorar, Resp. não",
    "magico+resp1": "Mágico pro, Resp. sim",
    "magico+resp0": "Mágico pro, Resp. não",
    "fundo": "Tirar o fundo",
    "auto+pb+resp1": "Auto: P&B, Resp. sim",
    "auto+pb+resp0": "Auto: P&B, Resp. não",
    "auto+pb+letras1": "Auto: Só as letras",
    "auto+pb+resp0+cinza1": "Auto: P&B, Resp. não + cinza",
    "auto+melhorar+resp1": "Auto: Melhorar, Resp. sim",
    "auto+melhorar+resp0": "Auto: Melhorar, Resp. não",
    "auto+magico+resp1": "Auto: Mágico, Resp. sim",
    "auto+magico+resp0": "Auto: Mágico, Resp. não",
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
CAUSA = {
    "gradus": "Em vermelho: todo o Preto e branco. Com a marcação valendo, a caixa branca sobre \"ÓNAI\" "
              "(imagens 2 e 3); sem ela (\"Respeitar\" não), os retângulos da \"sombra\" (imagem 1). "
              "Melhorar, Mágico pro, Original e Tirar o fundo: sem quadrados.",
    "escola": "Em vermelho: o Preto e branco SEM marcação (\"Respeitar\" não): quadradinhos brancos retos na "
              "pintura, à direita (a mesma \"sombra\" do 13-01). Com a marcação, o céu claro vai a branco "
              "seguindo a forma dele: não é quadrado.",
    "matematica": "Em vermelho: o Preto e branco COM a marcação: manchas brancas em volta do título, no azul "
                  "escuro. OUTRA causa: o programa achou \"papel\" ali (já era assim antes da obra). A mesa "
                  "escura em volta do livro (foto) também ganha manchas no Melhorar e no Mágico pro.",
    "pesel": "Nenhum quadrado em nenhuma escolha (capa de tecido).",
    "destino": "Nenhum quadrado: o papel creme vai a branco, como deve.",
}
# o que eu vi, olhando cada imagem (preenchido depois de olhar; ver o relatorio)
_PB_COM_MARCACAO = {"pb+resp1", "pb+resp1+cinza1", "pb+resp0+cinza1", "pb+letras1", "pb+letras_tudo",
                    "auto+pb+resp1", "auto+pb+letras1", "auto+pb+resp0+cinza1"}
CIRCULAR: dict = {
    # Gradus: todo Preto e branco (a caixa sobre "ONAI" com a marcacao; os retangulos sem ela)
    ("quadrados-capa", "gradus"): _PB_COM_MARCACAO | {"pb+resp0", "auto+pb+resp0"},
    # Escola: so o Preto e branco sem marcacao (os quadradinhos de "sombra" na pintura)
    ("quadrados-capa", "escola"): {"pb+resp0", "auto+pb+resp0"},
    # Matematica: o Preto e branco COM marcacao (o "papel" achado no azul escuro: outra causa)
    ("quadrados-capa", "matematica"): set(_PB_COM_MARCACAO),
}


def _celula(pasta: Path, livro: str, variante: str, circ: set, caixa: int = 205):
    arq = pasta / livro / variante / "pdf.png"
    if not arq.exists():
        return None
    img = P.abrir(arq)
    if livro == "gradus":                      # so a capa (a metade da direita)
        img = P.recorte(img, (0.5, 0.0, 1.0, 1.0))
    img = P.caber(img, caixa, int(caixa * 1.45))
    if variante in circ:                       # moldura vermelha POR FORA: nao cobre a pagina
        from PIL import ImageOps
        img = ImageOps.expand(img, border=7, fill=P.VERMELHO)
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
                               "Livro novo; cada quadro é uma escolha, como sai no PDF. " + CAUSA[livro])]
            for titulo, variantes in GRUPOS:
                cel = []
                for v in variantes:
                    c = _celula(base / versao, livro, v, circ)
                    if c is not None:
                        cel.append(c)
                if cel:
                    partes.append(P.empilhar([P.cabeca(titulo, cor, ""), _grade(cel, 6)], espaco=4))
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
