"""Verificador tc23 (23/10/2026): a "Tinta com a cor original" em dois jeitos (2.18).

A = "cor como no livro" (de fabrica, tem de sair igual ao de antes, ponto por ponto);
B = "cor escurecida" (brilho pela metade e cor 25% mais forte).

Cada pagina passa pelo caminho inteiro de livro novo, com os ajustes de fabrica
(core.pipeline.analisar_projeto + processar, os mesmos do programa): girar ->
dividir -> endireitar -> cortar -> filtro; a area marcada a mao vai por cima da
marcacao que o programa acha sozinho, como na tela. So paginas que vao ser
impressas (Horas 13, Escola 7, Opus Majus 3, Horas 11 = folha de rosto com o
titulo vermelho e azul, Graduale 221 = rubricas vermelhas no meio do texto).

As areas sao MINHAS (nao as do implementador), para a prova nao depender das dele.

USO (um modo por processo; --raiz = a worktree do codigo que se quer rodar):
    python tinta.py previa  --raiz <wt> <pasta>
    python tinta.py somas   --raiz <wt> <saida.json>
    python tinta.py json-antigo  --raiz <wt antiga> <pasta>     (grava projeto.json pelo codigo antigo + somas)
    python tinta.py abrir-antigo --raiz <wt nova> <pasta>       (abre os projeto.json antigos no codigo novo + somas)
    python tinta.py b       --raiz <wt nova> <pasta>            (numeros da B e fotos)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve()
_DADOS = Path(tempfile.gettempdir()) / "vtc23_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)

# (pagina, nome, areas TINTA_COR em fracao da pagina pronta (x0, y0, x1, y1))
PAGINAS = {
    "horas_p013": "Livro de Horas 13",
    "escola_p007": "Na Escola de Jesus 7",
    "opusmajus_p003": "Opus Majus 3 (folha de rosto)",
    "horas_p011": "Livro de Horas 11 (folha de rosto)",
    "graduale_p221": "Graduale 221 (rubricas vermelhas)",
}
AREAS: dict[str, tuple] = {}     # preenchido depois da previa (ver areas.json)
FILTROS = ("preto_e_branco", "original", "melhorar")


def _gab(raiz: Path, pid: str) -> Path:
    return raiz / "gabarito" / "paginas" / f"{pid}.pdf"


def _codigo(nome):
    from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO
    return {"original": ORIGINAL, "preto_e_branco": PRETO_E_BRANCO, "melhorar": MELHORAR}[nome]


def _projeto(raiz, pid, pdf, filtro):
    from core.pipeline import analisar_projeto
    from modelos import Projeto
    entrada = _gab(raiz, pid)
    projeto = analisar_projeto(Projeto(caminho_entrada=str(entrada), caminho_saida=str(pdf), nome=entrada.stem))
    projeto.filtro_padrao = _codigo(filtro)
    for pagina in projeto.paginas:
        pagina.filtro = _codigo(filtro)
    return projeto


def _marcar(projeto, regioes):
    """Acrescenta as regioes por cima da marcacao da maquina, como a tela faz."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        for pagina in projeto.paginas_ativas:
            renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
            marcacao = pagina.obter_selecao()
            for r in regioes:
                marcacao.acrescentar(r)
            pagina.guardar_selecao(marcacao)
    finally:
        doc.close()


def _regiao(tipo_nome, area, escura=None):
    from core import selecao as s
    tipo = {"cor": s.TINTA_COR, "preta": s.TINTA_PRETA, "pintar": s.PINTAR}[tipo_nome]
    r = s.Regiao(tipo=tipo, pontos=[area[:2], area[2:]], origem=s.MAO)
    if tipo_nome == "pintar":
        r.cor = "#ffe0a0"
    if escura is not None:
        r.tinta_escurecida = escura        # so existe no codigo novo
    return r


def _somas(pdf: Path) -> list[str]:
    import fitz
    out = []
    with fitz.open(str(pdf)) as doc:
        for pagina in doc:
            h = hashlib.sha256(f"{pagina.rect.width:.3f}x{pagina.rect.height:.3f}".encode())
            for info in pagina.get_images(full=True):
                pix = fitz.Pixmap(doc, info[0])
                h.update(f"{pix.width}x{pix.height}x{pix.n}".encode())
                h.update(pix.samples)
            out.append(h.hexdigest())
    return out


def _imagem(pdf: Path, dpi=200):
    import cv2
    import fitz
    import numpy as np
    with fitz.open(str(pdf)) as doc:
        pix = doc[0].get_pixmap(dpi=dpi)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3]
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR).copy()


def _caminho(projeto) -> str:
    from core.filtros import NOMES_AMIGAVEIS
    giros = sorted({int(f.rotacao) % 360 for f in projeto.folhas})
    return " -> ".join([
        "girar: " + (", ".join(f"{g} graus" for g in giros) if any(giros) else "0 (não precisou)"),
        "dividir: " + ("sim" if projeto.dividir_folhas else "não (de fábrica)"),
        "endireitar: " + ("sim" if projeto.endireitar else "não"),
        "cortar as bordas: " + ("sim" if projeto.cortar_bordas else "não"),
        "filtro: " + NOMES_AMIGAVEIS.get(projeto.filtro_padrao, projeto.filtro_padrao),
    ])


def rodar(raiz, pid, filtro, regioes, pasta: Path, rotulo: str):
    from core.pipeline import processar
    pdf = pasta / f"{pid}-{filtro}-{rotulo}.pdf"
    projeto = _projeto(raiz, pid, pdf, filtro)
    if regioes:
        _marcar(projeto, regioes)
    processar(projeto)
    return pdf, projeto


def _areas():
    return {k: tuple(v) for k, v in json.loads((AQUI.parent / "areas.json").read_text(encoding="utf-8")).items()}


def casos_a(pid, area, novo: bool):
    """Os casos que tem de sair iguais no antigo e no novo (so A, nunca B)."""
    x0, y0, x1, y1 = area
    meio = ((x0 + x1) / 2, y0, x1, (y0 + y1) / 2)
    kw = {"escura": False} if False else {}
    um = [_regiao("cor", area, **kw)]
    # combinado: duas A que se cruzam + uma tinta preta + um pintar por cima
    combo = [_regiao("cor", area), _regiao("cor", meio),
             _regiao("preta", (x0, min(0.95, y1 + 0.05), x1, min(0.99, y1 + 0.12))),
             _regiao("pintar", (x0, max(0.0, y0 - 0.04), x0 + 0.08, y0))]
    return {"um": um, "combo": combo}


def m_previa(raiz, pasta):
    import cv2
    pasta.mkdir(parents=True, exist_ok=True)
    for pid in PAGINAS:
        pdf, _ = rodar(raiz, pid, "original", [], pasta, "previa")
        img = _imagem(pdf, 100)
        h, w = img.shape[:2]
        for i in range(1, 10):
            cv2.line(img, (int(w * i / 10), 0), (int(w * i / 10), h), (0, 200, 0), 1)
            cv2.line(img, (0, int(h * i / 10)), (w, int(h * i / 10)), (0, 200, 0), 1)
            cv2.putText(img, str(i), (int(w * i / 10) + 2, 14), 0, 0.45, (0, 120, 0), 1)
            cv2.putText(img, str(i), (2, int(h * i / 10) - 2), 0, 0.45, (0, 120, 0), 1)
        cv2.imwrite(str(pasta / f"{pid}-grade.jpg"), img)
        print(pid, w, h, flush=True)


def m_somas(raiz, saida):
    areas = _areas()
    res = json.loads(saida.read_text(encoding="utf-8")) if saida.is_file() else {}
    with tempfile.TemporaryDirectory(dir=str(_DADOS)) as tmp:
        for pid in PAGINAS:
            for filtro in FILTROS:
                for nome, regioes in casos_a(pid, areas[pid], False).items():
                    if nome == "combo" and filtro == "melhorar":
                        continue
                    chave = f"{pid}|{filtro}|{nome}"
                    if chave in res:
                        continue
                    pdf, _ = rodar(raiz, pid, filtro, regioes, Path(tmp), nome)
                    res[chave] = _somas(pdf)
                    pdf.unlink(missing_ok=True)
                    saida.write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf-8")
                    print(chave, "ok", flush=True)
    return 0


def m_json_antigo(raiz, pasta):
    """No codigo ANTIGO: grava o projeto.json (como o programa grava) com uma area A e as somas."""
    pasta.mkdir(parents=True, exist_ok=True)
    areas = _areas()
    somas = {}
    for pid in ("horas_p013", "escola_p007", "opusmajus_p003", "horas_p011"):
        pdf, projeto = rodar(raiz, pid, "preto_e_branco", casos_a(pid, areas[pid], False)["combo"], pasta, "antigo")
        (pasta / f"{pid}-projeto.json").write_text(json.dumps(projeto.para_dicionario(), ensure_ascii=False, indent=1), encoding="utf-8")
        somas[pid] = _somas(pdf)
        print(pid, "gravado", flush=True)
    (pasta / "somas-antigo.json").write_text(json.dumps(somas, indent=1), encoding="utf-8")


def m_abrir_antigo(raiz, pasta):
    """No codigo NOVO: abre o projeto.json gravado pelo antigo (sem a chave) e processa."""
    from core.pipeline import processar
    from core.selecao import TINTA_COR
    from modelos import Projeto
    antigo = json.loads((pasta / "somas-antigo.json").read_text(encoding="utf-8"))
    out = {}
    for pid in antigo:
        texto = (pasta / f"{pid}-projeto.json").read_text(encoding="utf-8")
        tem_chave = "tinta_escurecida" in texto
        projeto = Projeto.de_dicionario(json.loads(texto))
        pdf = pasta / f"{pid}-reaberto-novo.pdf"
        projeto.caminho_saida = str(pdf)
        jeitos = [r.tinta_escurecida for p in projeto.paginas for r in p.obter_selecao().regioes if r.tipo == TINTA_COR]
        processar(projeto)
        s = _somas(pdf)
        out[pid] = {"chave_no_json_antigo": tem_chave, "jeitos_ao_abrir": jeitos,
                    "igual_ao_antigo": s == antigo[pid]}
        print(pid, out[pid], flush=True)
    (pasta / "abrir-antigo.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def m_b(raiz, pasta):
    """Numeros da B e as fotos (so codigo novo)."""
    import cv2
    import numpy as np
    sys.path.insert(0, str(raiz / "relatorios" / "fase2-novas" / "scripts"))
    import antes_depois as ad
    pasta.mkdir(parents=True, exist_ok=True)
    tmp = pasta / "_pdfs"
    tmp.mkdir(exist_ok=True)
    areas = _areas()
    numeros = {}
    for pid, nome in PAGINAS.items():
        area = areas[pid]
        for filtro in ("preto_e_branco", "original"):
            sem, proj = rodar(raiz, pid, filtro, [], tmp, "sem")
            a, _ = rodar(raiz, pid, filtro, [_regiao("cor", area, False)], tmp, "A")
            b, _ = rodar(raiz, pid, filtro, [_regiao("cor", area, True)], tmp, "B")
            iS, iA, iB = (_imagem(p, 200) for p in (sem, a, b))
            h, w = iA.shape[:2]
            x0, y0, x1, y1 = int(area[0] * w), int(area[1] * h), int(area[2] * w), int(area[3] * h)
            dentro = np.zeros((h, w), bool)
            dentro[max(0, y0 - 3):y1 + 3, max(0, x0 - 3):x1 + 3] = True     # 3 pontos de folga na beirada
            difAB = np.any(iA != iB, axis=2)
            difSB = np.any(iS != iB, axis=2)
            labA = cv2.cvtColor(iA, cv2.COLOR_BGR2LAB).astype(float)
            labB = cv2.cvtColor(iB, cv2.COLOR_BGR2LAB).astype(float)
            caixa = np.zeros((h, w), bool)
            caixa[y0:y1, x0:x1] = True
            tinta = caixa & (labA[..., 0] < 200)
            papel = caixa & np.all(iA >= 250, axis=2)
            cromaA = np.hypot(labA[..., 1] - 128, labA[..., 2] - 128)
            cromaB = np.hypot(labB[..., 1] - 128, labB[..., 2] - 128)
            colorida = tinta & (cromaA > 15)
            numeros[f"{pid}|{filtro}"] = {
                "fora_da_area_A_x_B_pontos_diferentes": int(np.count_nonzero(difAB & ~dentro)),
                "fora_da_area_sem_x_B_pontos_diferentes": int(np.count_nonzero(difSB & ~dentro)),
                "brilho_tinta_A": round(float(labA[..., 0][tinta].mean()), 1),
                "brilho_tinta_B": round(float(labB[..., 0][tinta].mean()), 1),
                "razao_brilho_B_sobre_A": round(float(labB[..., 0][tinta].mean() / max(1, labA[..., 0][tinta].mean())), 3),
                "forca_cor_A_tinta_colorida": round(float(cromaA[colorida].mean()), 1) if colorida.any() else None,
                "forca_cor_B_tinta_colorida": round(float(cromaB[colorida].mean()), 1) if colorida.any() else None,
                "papel_da_area_igual_em_A_e_B": bool(not np.any(difAB & papel)),
                "pontos_de_tinta": int(tinta.sum()),
            }
            print(pid, filtro, numeros[f"{pid}|{filtro}"], flush=True)
            # fotos
            orig = _imagem(rodar(raiz, pid, "original", [], tmp, "orig")[0], 200) if filtro == "preto_e_branco" else iS
            frase = _caminho(proj)
            marc = f" + área \"tinta com a cor, papel branco\" marcada à mão em {tuple(round(v, 2) for v in area)}"
            paineis = [(f"{nome}: o livro (Original, sem área)", orig, _caminho(proj).replace(frase.split('filtro: ')[-1], 'Original') if filtro != 'original' else frase),
                       (f"{'Preto e branco' if filtro == 'preto_e_branco' else 'Original'}, sem área", iS, frase),
                       ("A: \"cor como no livro\" (de fábrica)", iA, frase + marc + ", jeito A"),
                       ("B: \"cor escurecida\"", iB, frase + marc + ", jeito B")]
            if filtro == "original":
                paineis = paineis[1:]
            cv2.imwrite(str(pasta / f"{pid}-{filtro}-pagina.jpg"), ad._lado_a_lado(paineis, altura=1000), [cv2.IMWRITE_JPEG_QUALITY, 85])
            tiras = []
            for titulo, im, fr in paineis:
                ped = im[y0:y1, x0:x1]
                lg = min(1400, max(900, ped.shape[1]))
                ped = cv2.resize(ped, (lg, int(ped.shape[0] * lg / ped.shape[1])), interpolation=cv2.INTER_AREA if ped.shape[1] > lg else cv2.INTER_CUBIC)
                tiras.append(ad._faixa(ped, [titulo] + ad._quebrar(fr, lg)))
            lg = max(t.shape[1] for t in tiras)
            tiras = [cv2.copyMakeBorder(t, 0, 10, 0, lg - t.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)) for t in tiras]
            cv2.imwrite(str(pasta / f"{pid}-{filtro}-ampliado.jpg"), np.vstack(tiras), [cv2.IMWRITE_JPEG_QUALITY, 88])
    (pasta / "numeros-b.json").write_text(json.dumps(numeros, indent=1, ensure_ascii=False), encoding="utf-8")


def m_cruzadas(raiz, pasta):
    """Duas areas que se cruzam: a ultima desenhada manda (A depois de B e B depois de A)."""
    import numpy as np
    pasta.mkdir(parents=True, exist_ok=True)
    tmp = pasta / "_pdfs"
    tmp.mkdir(exist_ok=True)
    pid = "horas_p011"
    x0, y0, x1, y1 = _areas()[pid]
    esq, dir_ = (x0, y0, (x0 + x1) / 2 + 0.1, y1), ((x0 + x1) / 2 - 0.1, y0, x1, y1)
    so_a = _imagem(rodar(raiz, pid, "preto_e_branco", [_regiao("cor", (x0, y0, x1, y1), False)], tmp, "soA")[0])
    so_b = _imagem(rodar(raiz, pid, "preto_e_branco", [_regiao("cor", (x0, y0, x1, y1), True)], tmp, "soB")[0])
    ab = _imagem(rodar(raiz, pid, "preto_e_branco", [_regiao("cor", esq, False), _regiao("cor", dir_, True)], tmp, "AdepoisB")[0])
    ba = _imagem(rodar(raiz, pid, "preto_e_branco", [_regiao("cor", esq, True), _regiao("cor", dir_, False)], tmp, "BdepoisA")[0])
    h, w = ab.shape[:2]
    X = lambda f: int(f * w)  # noqa: E731
    Y0, Y1 = int(y0 * h) + 3, int(y1 * h) - 3
    faixas = {"so_esquerda": (X(x0) + 3, X(dir_[0]) - 3), "cruzada": (X(dir_[0]) + 3, X(esq[2]) - 3), "so_direita": (X(esq[2]) + 3, X(x1) - 3)}
    out = {}
    for nome, img, esperado in (("A_esq_depois_B_dir", ab, {"so_esquerda": "A", "cruzada": "B", "so_direita": "B"}),
                                ("B_esq_depois_A_dir", ba, {"so_esquerda": "B", "cruzada": "A", "so_direita": "A"})):
        r = {}
        for f, (c0, c1) in faixas.items():
            ped = img[Y0:Y1, c0:c1]
            igual_a = bool(np.array_equal(ped, so_a[Y0:Y1, c0:c1]))
            igual_b = bool(np.array_equal(ped, so_b[Y0:Y1, c0:c1]))
            r[f] = {"esperado": esperado[f], "igual_a_A": igual_a, "igual_a_B": igual_b,
                    "certo": (igual_a if esperado[f] == "A" else igual_b)}
        out[nome] = r
        print(nome, r, flush=True)
    (pasta / "cruzadas.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo")
    ap.add_argument("saida", type=Path)
    ap.add_argument("--raiz", type=Path, required=True)
    a = ap.parse_args()
    raiz = a.raiz.resolve()
    sys.path.insert(0, str(raiz))
    os.chdir(raiz)
    {"previa": m_previa, "somas": m_somas, "json-antigo": m_json_antigo, "abrir-antigo": m_abrir_antigo,
     "b": m_b, "cruzadas": m_cruzadas}[a.modo](raiz, a.saida.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
