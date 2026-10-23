"""Verificador tp23 (23/10/2026): o papel da área "Tinta com a cor" (item 2.18).

Resposta do Samuel à tc23-1: "As duas: escolher o papel em cada área ('papel branco'
ou 'papel como o resto da página')".
  "papel branco"                  = o de fábrica, tem de sair igual ao de antes ponto por ponto;
  "papel como o resto da página"  = o que não é tinta dentro da área fica como o filtro da página;
                                    só a tinta segue o A ("cor como no livro") ou o B ("cor escurecida").

Cada página passa pelo caminho inteiro de livro novo com os ajustes de fábrica
(core.pipeline.analisar_projeto + processar, os mesmos do programa): girar -> dividir ->
endireitar -> cortar -> filtro; a área marcada à mão vai por cima da marcação que o
programa acha sozinho, como na tela. Só páginas que vão ser impressas: Horas 13,
Escola 7, Opus Majus 3 (folha de rosto) e Graduale 221 (rubricas vermelhas).
As áreas são MINHAS (areas.json, as mesmas do tc23), não as do implementador.

As contas usam a imagem guardada dentro do PDF, no tamanho dela (sem reamostrar).

USO (um modo por processo; --raiz = a worktree do código que se quer rodar):
    python papel.py somas        --raiz <wt> <saida.json>
    python papel.py json-antigo  --raiz <wt antiga> <pasta>
    python papel.py abrir-antigo --raiz <wt nova> <pasta>
    python papel.py papel        --raiz <wt nova> <pasta>      (números e fotos dos 4 jeitos)
    python papel.py cruzadas     --raiz <wt nova> <pasta>      (a de cima manda; o "tirar")
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
_DADOS = Path(tempfile.gettempdir()) / "vtp23_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)

PAGINAS = {
    "horas_p013": "Livro de Horas 13",
    "escola_p007": "Na Escola de Jesus 7",
    "opusmajus_p003": "Opus Majus 3 (folha de rosto)",
    "graduale_p221": "Graduale 221 (rubricas vermelhas)",
}
FILTROS = ("preto_e_branco", "original", "melhorar")
NOME_FILTRO = {"preto_e_branco": "Preto e branco", "original": "Original", "melhorar": "Melhorar"}


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
    """Acrescenta as regiões por cima da marcação da máquina, como a tela faz."""
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


def _regiao(tipo_nome, area, escura=None, papel=None, tirar=False, forma="retangulo"):
    """escura/papel None = não mexe no campo (o código antigo não tem `papel_da_pagina`)."""
    from core import selecao as s
    tipo = {"cor": s.TINTA_COR, "preta": s.TINTA_PRETA, "pintar": s.PINTAR}[tipo_nome]
    if forma == "traco":
        x0, y0, x1, y1 = area
        meio = (y0 + y1) / 2
        r = s.Regiao(tipo=tipo, forma=s.TRACO, pontos=[(x0, meio), ((x0 + x1) / 2, meio), (x1, meio)],
                     origem=s.MAO, espessura=0.04)
    else:
        r = s.Regiao(tipo=tipo, pontos=[area[:2], area[2:]], origem=s.MAO)
    if tirar:
        r.operacao = s.SUBTRAIR
    if tipo_nome == "pintar":
        r.cor = "#ffe0a0"
    if escura is not None:
        r.tinta_escurecida = escura
    if papel is not None:
        r.papel_da_pagina = papel          # só existe no código novo
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


def _guardada(pdf: Path):
    """A maior imagem guardada na 1a página do PDF, em BGR, no tamanho dela."""
    import cv2
    import fitz
    import numpy as np
    with fitz.open(str(pdf)) as doc:
        infos = doc[0].get_images(full=True)
        melhor = max(infos, key=lambda i: i[2] * i[3])
        pix = fitz.Pixmap(doc, melhor[0])
        if pix.n - pix.alpha < 3 or pix.colorspace is None or pix.colorspace.n != 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        if pix.alpha:
            pix = fitz.Pixmap(pix, 0)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3]
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR).copy(), (melhor[8] if len(melhor) > 8 else "")


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
    return {k: tuple(v) for k, v in json.loads((AQUI.parent / "areas.json").read_text(encoding="utf-8")).items()
            if k in PAGINAS}


def casos_de_fabrica(area):
    """Os casos que têm de sair iguais no antigo e no novo: o papel nunca é tocado (de fábrica)."""
    x0, y0, x1, y1 = area
    meio = ((x0 + x1) / 2, y0, x1, (y0 + y1) / 2)
    return {
        "A": [_regiao("cor", area, escura=False)],
        "B": [_regiao("cor", area, escura=True)],
        # A e B que se cruzam + tinta preta + pintar por cima + um "tirar" do pincel
        "combo": [_regiao("cor", area, escura=False), _regiao("cor", meio, escura=True),
                  _regiao("cor", (x0, y0, (x0 + x1) / 2, y1), forma="traco", tirar=True),
                  _regiao("preta", (x0, min(0.95, y1 + 0.05), x1, min(0.99, y1 + 0.12))),
                  _regiao("pintar", (x0, max(0.0, y0 - 0.04), x0 + 0.08, y0))],
    }


def m_somas(raiz, saida):
    areas = _areas()
    res = json.loads(saida.read_text(encoding="utf-8")) if saida.is_file() else {}
    pasta = _DADOS / ("somas-" + saida.stem)
    pasta.mkdir(parents=True, exist_ok=True)
    for pid in PAGINAS:
        for filtro in FILTROS:
            for nome, regioes in casos_de_fabrica(areas[pid]).items():
                chave = f"{pid}|{filtro}|{nome}"
                if chave in res:
                    continue
                pdf, _ = rodar(raiz, pid, filtro, regioes, pasta, nome)
                res[chave] = _somas(pdf)
                saida.write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf-8")
                print(chave, "ok", flush=True)
    return 0


def m_json_antigo(raiz, pasta):
    """No código ANTIGO: grava o projeto.json (como o programa grava) com o combo e as somas."""
    pasta.mkdir(parents=True, exist_ok=True)
    areas = _areas()
    somas = {}
    for pid, filtro in (("horas_p013", "original"), ("escola_p007", "preto_e_branco"),
                        ("opusmajus_p003", "melhorar"), ("graduale_p221", "original")):
        pdf, projeto = rodar(raiz, pid, filtro, casos_de_fabrica(areas[pid])["combo"], pasta, "antigo")
        (pasta / f"{pid}-projeto.json").write_text(json.dumps(projeto.para_dicionario(), ensure_ascii=False, indent=1), encoding="utf-8")
        somas[pid] = _somas(pdf)
        print(pid, filtro, "gravado", flush=True)
    (pasta / "somas-antigo.json").write_text(json.dumps(somas, indent=1), encoding="utf-8")


def m_abrir_antigo(raiz, pasta):
    """No código NOVO: abre o projeto.json gravado pelo antigo (sem a chave) e processa."""
    from core.pipeline import processar
    from core.selecao import TINTA_COR
    from modelos import Projeto
    antigo = json.loads((pasta / "somas-antigo.json").read_text(encoding="utf-8"))
    out = {}
    for pid in antigo:
        texto = (pasta / f"{pid}-projeto.json").read_text(encoding="utf-8")
        projeto = Projeto.de_dicionario(json.loads(texto))
        pdf = pasta / f"{pid}-reaberto-novo.pdf"
        projeto.caminho_saida = str(pdf)
        regs = [r for p in projeto.paginas for r in p.obter_selecao().regioes if r.tipo == TINTA_COR]
        processar(projeto)
        out[pid] = {"chave_papel_no_json_antigo": "papel_da_pagina" in texto,
                    "papel_ao_abrir": [r.papel_da_pagina for r in regs],
                    "cor_ao_abrir": [r.tinta_escurecida for r in regs],
                    "igual_ao_antigo": _somas(pdf) == antigo[pid]}
        print(pid, out[pid], flush=True)
    (pasta / "abrir-antigo.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def _fora(h, w, area, folga=4):
    import numpy as np
    x0, y0, x1, y1 = int(area[0] * w), int(area[1] * h), int(area[2] * w), int(area[3] * h)
    dentro = np.zeros((h, w), bool)
    dentro[max(0, y0 - folga):y1 + folga, max(0, x0 - folga):x1 + folga] = True
    caixa = np.zeros((h, w), bool)
    caixa[y0 + folga:y1 - folga, x0 + folga:x1 - folga] = True
    return ~dentro, caixa


def _numeros(iS, iAb, iAp, iBb, iBp, area):
    """Contas de uma página e um filtro. 'tinta' = o que não é branco puro no A + papel branco
    (lá o programa pinta o papel de 255); 'papel' = o branco puro do A + papel branco."""
    import numpy as np
    h, w = iS.shape[:2]
    fora, caixa = _fora(h, w, area)
    dif = lambda a, b: np.any(a != b, axis=2)  # noqa: E731
    papel = caixa & np.all(iAb == 255, axis=2)
    tinta = caixa & ~np.all(iAb == 255, axis=2)
    cinza = lambda im, m: round(float(im[m].mean()), 1) if m.any() else None  # noqa: E731
    escuro_novo = papel & (iAp.min(axis=2) < 100)          # papel que virou preto/escuro (b-10)
    return {
        "pontos_na_area": int(caixa.sum()), "pontos_de_tinta": int(tinta.sum()), "pontos_de_papel": int(papel.sum()),
        "fora_da_area_diferentes_do_sem_area": {k: int((dif(iS, im) & fora).sum()) for k, im in
                                                (("A_branco", iAb), ("A_pagina", iAp), ("B_branco", iBb), ("B_pagina", iBp))},
        "papel_igual_ao_sem_area_pct": {"A_pagina": round(100 * float((~dif(iS, iAp) & papel).sum()) / max(1, papel.sum()), 2),
                                        "B_pagina": round(100 * float((~dif(iS, iBp) & papel).sum()) / max(1, papel.sum()), 2)},
        "tinta_igual_ao_papel_branco_pct": {"A": round(100 * float((~dif(iAb, iAp) & tinta).sum()) / max(1, tinta.sum()), 2),
                                            "B": round(100 * float((~dif(iBb, iBp) & tinta).sum()) / max(1, tinta.sum()), 2)},
        "A_pagina_igual_ao_sem_area_na_area_toda_pct": round(100 * float((~dif(iS, iAp) & caixa).sum()) / max(1, caixa.sum()), 2),
        "cinza_do_papel": {"sem_area": cinza(iS, papel), "A_branco": cinza(iAb, papel), "A_pagina": cinza(iAp, papel)},
        "papel_que_fica_escuro_no_A_pagina": int(escuro_novo.sum()),
    }


def m_papel(raiz, pasta):
    """Números e fotos: sem área, A + papel branco, A + papel da página, B + papel branco,
    B + papel da página, em Original, Melhorar e Preto e branco."""
    import cv2
    import numpy as np
    sys.path.insert(0, str(raiz / "relatorios" / "fase2-novas" / "scripts"))
    import antes_depois as ad
    pasta.mkdir(parents=True, exist_ok=True)
    tmp = _DADOS / "papel-pdfs"
    tmp.mkdir(parents=True, exist_ok=True)
    areas = _areas()
    numeros = {}
    for pid, nome in PAGINAS.items():
        area = areas[pid]
        for filtro in ("original", "melhorar", "preto_e_branco"):
            casos = (("sem", []), ("Ab", [_regiao("cor", area, False, False)]), ("Ap", [_regiao("cor", area, False, True)]),
                     ("Bb", [_regiao("cor", area, True, False)]), ("Bp", [_regiao("cor", area, True, True)]))
            pdfs, proj = {}, None
            for rot, regs in casos:
                pdfs[rot], p = rodar(raiz, pid, filtro, regs, tmp, rot)
                proj = proj or p
            imgs = {k: _guardada(v)[0] for k, v in pdfs.items()}
            tam = {im.shape for im in imgs.values()}
            if len(tam) == 1:
                n = _numeros(imgs["sem"], imgs["Ab"], imgs["Ap"], imgs["Bb"], imgs["Bp"], area)
            else:
                n = {"tamanhos_diferentes": [str(t) for t in tam]}
            n["filtros_das_imagens"] = {k: _guardada(v)[1] for k, v in pdfs.items()}
            numeros[f"{pid}|{filtro}"] = n
            print(pid, filtro, json.dumps(n, ensure_ascii=False), flush=True)
            if filtro == "melhorar" and pid not in ("horas_p013", "graduale_p221"):
                continue                       # fotos do Melhorar só em duas páginas (as contas, em todas)
            frase = _caminho(proj)
            marc = f" + área \"tinta com a cor\" marcada à mão em {tuple(round(v, 2) for v in area)}"
            fn = NOME_FILTRO[filtro]
            paineis = [(f"{nome}: {fn}, sem área", imgs["sem"], frase),
                       ("A \"cor como no livro\" + \"papel branco\" (de fábrica)", imgs["Ab"], frase + marc + ", A, papel branco"),
                       ("A \"cor como no livro\" + \"papel como o resto da página\"", imgs["Ap"], frase + marc + ", A, papel como o resto da página"),
                       ("B \"cor escurecida\" + \"papel branco\"", imgs["Bb"], frase + marc + ", B, papel branco"),
                       ("B \"cor escurecida\" + \"papel como o resto da página\"", imgs["Bp"], frase + marc + ", B, papel como o resto da página")]
            cv2.imwrite(str(pasta / f"{pid}-{filtro}-pagina.jpg"), ad._lado_a_lado(paineis, altura=1000), [cv2.IMWRITE_JPEG_QUALITY, 85])
            h, w = imgs["sem"].shape[:2]
            x0, y0, x1, y1 = int(area[0] * w), int(area[1] * h), int(area[2] * w), int(area[3] * h)
            mx, my = int(0.03 * w), int(0.02 * h)          # um pouco de fora em volta, para ver a borda da área
            x0, y0, x1, y1 = max(0, x0 - mx), max(0, y0 - my), min(w, x1 + mx), min(h, y1 + my)
            tiras = []
            for titulo, im, fr in paineis:
                ped = im[y0:y1, x0:x1]
                lg = min(1400, max(900, ped.shape[1]))
                ped = cv2.resize(ped, (lg, int(ped.shape[0] * lg / ped.shape[1])),
                                 interpolation=cv2.INTER_AREA if ped.shape[1] > lg else cv2.INTER_NEAREST)
                tiras.append(ad._faixa(ped, [titulo] + ad._quebrar(fr, lg)))
            lg = max(t.shape[1] for t in tiras)
            tiras = [cv2.copyMakeBorder(t, 0, 10, 0, lg - t.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)) for t in tiras]
            cv2.imwrite(str(pasta / f"{pid}-{filtro}-ampliado.jpg"), np.vstack(tiras), [cv2.IMWRITE_JPEG_QUALITY, 88])
            if filtro == "preto_e_branco":
                # b-10: a letra de perto, 4 vezes, papel branco x papel da página (A)
                cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                ys, xs = np.nonzero(np.any(imgs["Ab"][y0:y1, x0:x1] != 255, axis=2))
                if len(xs):
                    cx, cy = int(np.median(xs)) + x0, int(np.median(ys)) + y0
                r = max(40, min(140, (y1 - y0) // 2))
                pa = slice(max(0, cy - r), cy + r), slice(max(0, cx - 2 * r), cx + 2 * r)
                tiras = []
                for titulo, im in (("A + papel branco", imgs["Ab"]), ("A + papel como o resto da página", imgs["Ap"]),
                                   ("B + papel branco", imgs["Bb"]), ("B + papel como o resto da página", imgs["Bp"])):
                    ped = cv2.resize(im[pa], None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
                    tiras.append(ad._faixa(ped, [f"{nome}, Preto e branco: {titulo} (ampliado 4 vezes)"] + ad._quebrar(frase + marc, ped.shape[1])))
                lg = max(t.shape[1] for t in tiras)
                tiras = [cv2.copyMakeBorder(t, 0, 10, 0, lg - t.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)) for t in tiras]
                cv2.imwrite(str(pasta / f"{pid}-preto_e_branco-letra-de-perto.jpg"), np.vstack(tiras), [cv2.IMWRITE_JPEG_QUALITY, 90])
    (pasta / "numeros-papel.json").write_text(json.dumps(numeros, indent=1, ensure_ascii=False), encoding="utf-8")


def m_cruzadas(raiz, pasta):
    """Duas áreas que se cruzam (a última desenhada manda) e o "tirar" do pincel, no Original
    (onde o papel da página e o papel branco se distinguem bem) e no Preto e branco."""
    import cv2
    import numpy as np
    sys.path.insert(0, str(raiz / "relatorios" / "fase2-novas" / "scripts"))
    import antes_depois as ad
    pasta.mkdir(parents=True, exist_ok=True)
    tmp = _DADOS / "cruzadas-pdfs"
    tmp.mkdir(parents=True, exist_ok=True)
    out = {}
    for pid, filtro in (("horas_p013", "original"), ("graduale_p221", "original"), ("horas_p013", "preto_e_branco")):
        x0, y0, x1, y1 = _areas()[pid]
        toda = (x0, y0, x1, y1)
        cx = (x0 + x1) / 2
        esq, dir_ = (x0, y0, cx + 0.1, y1), (cx - 0.1, y0, x1, y1)
        G = lambda regs, rot: _guardada(rodar(raiz, pid, filtro, regs, tmp, rot)[0])[0]  # noqa: E731
        sem = G([], "sem")
        ref = {j: G([_regiao("cor", toda, j[0] == "B", j[1] == "p")], "ref" + j) for j in ("Ab", "Ap", "Bb", "Bp")}
        casos = {
            "Ap_esq_depois_Ab_dir": ([_regiao("cor", esq, False, True), _regiao("cor", dir_, False, False)], ("Ap", "Ab", "Ab")),
            "Ab_esq_depois_Ap_dir": ([_regiao("cor", esq, False, False), _regiao("cor", dir_, False, True)], ("Ab", "Ap", "Ap")),
            "Bp_esq_depois_Ab_dir": ([_regiao("cor", esq, True, True), _regiao("cor", dir_, False, False)], ("Bp", "Ab", "Ab")),
            "Ab_esq_depois_Bp_dir": ([_regiao("cor", esq, False, False), _regiao("cor", dir_, True, True)], ("Ab", "Bp", "Bp")),
        }
        h, w = sem.shape[:2]
        X = lambda f: int(f * w)  # noqa: E731
        Y0, Y1 = int(y0 * h) + 4, int(y1 * h) - 4
        faixas = {"so_esquerda": (X(x0) + 4, X(dir_[0]) - 4), "cruzada": (X(dir_[0]) + 4, X(esq[2]) - 4),
                  "so_direita": (X(esq[2]) + 4, X(x1) - 4)}
        r_pg = {}
        imgs_cruz = {}
        for nome, (regs, esperado) in casos.items():
            img = G(regs, nome)
            imgs_cruz[nome] = img
            r = {}
            for (f, (c0, c1)), esp in zip(faixas.items(), esperado):
                ped = img[Y0:Y1, c0:c1]
                iguais = [j for j in ref if np.array_equal(ped, ref[j][Y0:Y1, c0:c1])]
                r[f] = {"esperado": esp, "igual_a": iguais, "certo": esp in iguais}
            r_pg[nome] = r
            print(pid, filtro, nome, r, flush=True)
        # o "tirar" do pincel: área Ap (e Bp) inteira e, por cima, um traço de pincel "tirar"
        # da mesma ferramenta; onde passou o pincel, a página volta a ser a sem área
        tir = {}
        for j in ("Ap", "Bp"):
            regs = [_regiao("cor", toda, j[0] == "B", True), _regiao("cor", toda, j[0] == "B", True, tirar=True, forma="traco")]
            img = G(regs, "tirar" + j)
            imgs_cruz["tirar" + j] = img
            from core.selecao import Selecao
            m_tir = Selecao([_regiao("cor", toda, forma="traco")]).mascara(h, w, regs[0].tipo)
            m_area = np.zeros((h, w), bool)
            m_area[Y0:Y1, X(x0) + 4:X(x1) - 4] = True
            m_tir_dentro = cv2.erode(m_tir.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & m_area
            m_resto = m_area & ~cv2.dilate(m_tir.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
            tir[j] = {"onde_tirou_igual_ao_sem_area_pct": round(100 * float(np.all(img == sem, axis=2)[m_tir_dentro].mean()), 2),
                      "onde_tirou_igual_a_area_pct": round(100 * float(np.all(img == ref[j], axis=2)[m_tir_dentro].mean()), 2),
                      "resto_da_area_igual_a_area_pct": round(100 * float(np.all(img == ref[j], axis=2)[m_resto].mean()), 2),
                      "pontos_onde_tirou": int(m_tir_dentro.sum())}
            print(pid, filtro, "tirar", j, tir[j], flush=True)
        r_pg["tirar"] = tir
        out[f"{pid}|{filtro}"] = r_pg
        # foto: os quatro cruzamentos e os dois "tirar"
        mx = int(0.03 * w)
        ya, yb = max(0, int(y0 * h) - 20), min(h, int(y1 * h) + 20)
        xa, xb = max(0, X(x0) - mx), min(w, X(x1) + mx)
        frase = _caminho(rodar(raiz, pid, filtro, [], tmp, "sem2")[1])
        titulos = {"Ap_esq_depois_Ab_dir": "1a à esquerda: A + papel da página; 2a (por cima) à direita: A + papel branco",
                   "Ab_esq_depois_Ap_dir": "1a à esquerda: A + papel branco; 2a (por cima) à direita: A + papel da página",
                   "Bp_esq_depois_Ab_dir": "1a à esquerda: B + papel da página; 2a (por cima) à direita: A + papel branco",
                   "Ab_esq_depois_Bp_dir": "1a à esquerda: A + papel branco; 2a (por cima) à direita: B + papel da página",
                   "tirarAp": "A + papel da página, e o pincel \"tirar\" passado no meio",
                   "tirarBp": "B + papel da página, e o pincel \"tirar\" passado no meio"}
        tiras = []
        for k, t in titulos.items():
            ped = imgs_cruz[k][ya:yb, xa:xb]
            lg = min(1400, max(900, ped.shape[1]))
            ped = cv2.resize(ped, (lg, int(ped.shape[0] * lg / ped.shape[1])), interpolation=cv2.INTER_AREA if ped.shape[1] > lg else cv2.INTER_NEAREST)
            tiras.append(ad._faixa(ped, [f"{PAGINAS[pid]}, {NOME_FILTRO[filtro]}: {t}"] + ad._quebrar(frase, lg)))
        lg = max(t.shape[1] for t in tiras)
        tiras = [cv2.copyMakeBorder(t, 0, 10, 0, lg - t.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)) for t in tiras]
        cv2.imwrite(str(pasta / f"{pid}-{filtro}-cruzadas-e-tirar.jpg"), np.vstack(tiras), [cv2.IMWRITE_JPEG_QUALITY, 86])
    (pasta / "cruzadas.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo")
    ap.add_argument("saida", type=Path)
    ap.add_argument("--raiz", type=Path, required=True)
    a = ap.parse_args()
    raiz = a.raiz.resolve()
    sys.path.insert(0, str(raiz))
    os.chdir(raiz)
    {"somas": m_somas, "json-antigo": m_json_antigo, "abrir-antigo": m_abrir_antigo,
     "papel": m_papel, "cruzadas": m_cruzadas}[a.modo](raiz, a.saida.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
