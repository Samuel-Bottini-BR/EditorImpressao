"""Rodada pelo caminho inteiro do programa (implementador B, 22/10/2026).

PARA QUÊ
    Regra do Samuel de 21/10/2026: "todo teste de imagem e antes/depois leva a
    página pelo caminho inteiro do programa na ordem do livro novo (dividir →
    endireitar → cortar → filtro), com os ajustes de fábrica, até a ferramenta
    testada". Aqui isso é literal: cada página-gabarito vira um livro novo
    (Projeto de fábrica + core.pipeline.analisar_projeto) e passa pelo
    core.pipeline.processar, o mesmo que gera o PDF do Kaique. Nada é chamado
    por fora do programa.

    1. somas  --saida X.json  pid [pid ...]
       A soma (SHA-256) dos pontos de cada página do PDF gerado, em Original,
       Preto e branco e Melhorar, tudo de fábrica. Rodado no código antigo
       (--raiz da outra worktree) e no novo: tem de dar igual (prova de que
       "desligado de fábrica" = livro já começado sai igual).
    2. livro  --saida pasta  --nome N  --campos '{"margens_iguais": true}'  pid [pid ...]
       Junta as páginas num livro só (na ordem dada), processa com e sem os
       campos do projeto trocados, e grava o PDF de cada um e uma folha de
       contato (antes em cima, depois embaixo, mesma escala), dizendo por onde
       a página passou e com quais opções.

Só páginas que vão ser impressas (regra de 21/10): o gabarito não tem capa,
lombada nem contracapa de couro.

USO (da pasta da worktree; um processo por vez, por causa da memória)
    python relatorios\\fase2-novas\\scripts\\rodada_processar.py somas --saida s.json horas_p013
    python relatorios\\fase2-novas\\scripts\\rodada_processar.py --raiz <outra worktree> somas ...

Lê o gabarito (somente leitura). A pasta de dados do programa vai para uma
pasta temporária: nada é escrito na pasta real do Samuel.
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
RAIZ_PADRAO = AQUI.parents[3]

_DADOS = Path(tempfile.gettempdir()) / "fase2_novas_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)


def _preparar(raiz: Path) -> None:
    sys.path.insert(0, str(raiz))


def _gabarito(raiz: Path, pid: str) -> Path:
    caminho = raiz / "gabarito" / "paginas" / f"{pid}.pdf"
    if not caminho.is_file():          # worktree sem a junção: o da worktree nova
        caminho = RAIZ_PADRAO / "gabarito" / "paginas" / f"{pid}.pdf"
    return caminho


def _livro(pids: list[str], raiz: Path, destino: Path) -> Path:
    """Um PDF com as páginas do gabarito na ordem dada (cópia, sem mexer)."""
    import fitz

    saida = fitz.open()
    for pid in pids:
        with fitz.open(str(_gabarito(raiz, pid))) as um:
            saida.insert_pdf(um)
    saida.save(str(destino))
    saida.close()
    return destino


def _projeto_de_fabrica(entrada: Path, saida: Path):
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(saida), nome=entrada.stem)
    return analisar_projeto(projeto)


def _somas_do_pdf(caminho: Path) -> list[str]:
    import fitz

    somas = []
    with fitz.open(str(caminho)) as doc:
        for pagina in doc:
            h = hashlib.sha256(f"{pagina.rect.width:.3f}x{pagina.rect.height:.3f}".encode())
            for info in pagina.get_images(full=True):
                pix = fitz.Pixmap(doc, info[0])
                h.update(f"{pix.width}x{pix.height}x{pix.n}".encode())
                h.update(pix.samples)
            somas.append(h.hexdigest())
    return somas


FILTROS = ("original", "preto_e_branco", "melhorar")


def somas(pids: list[str], raiz: Path, saida: Path) -> dict:
    from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO
    from core.pipeline import processar

    codigos = {"original": ORIGINAL, "preto_e_branco": PRETO_E_BRANCO, "melhorar": MELHORAR}
    resultado = json.loads(saida.read_text(encoding="utf-8")) if saida.is_file() else {}
    with tempfile.TemporaryDirectory(dir=str(_DADOS)) as tmp:
        for pid in pids:
            for nome in FILTROS:
                pdf = Path(tmp) / f"{pid}-{nome}.pdf"
                projeto = _projeto_de_fabrica(_gabarito(raiz, pid), pdf)
                projeto.filtro_padrao = codigos[nome]
                for pagina in projeto.paginas:
                    pagina.filtro = codigos[nome]
                processar(projeto)
                for i, soma in enumerate(_somas_do_pdf(pdf)):
                    resultado[f"{pid}|{nome}|{i}"] = soma
                pdf.unlink(missing_ok=True)
            saida.write_text(json.dumps(resultado, indent=1, sort_keys=True), encoding="utf-8")
            print(pid, "ok", flush=True)
    return resultado


def _por_onde_passou(projeto) -> str:
    """A frase de cada imagem: por onde a página passou e com quais opções."""
    from core.filtros import NOMES_AMIGAVEIS

    partes = [
        "dividir: " + ("sim" if projeto.dividir_folhas else "não (de fábrica)"),
        "endireitar: " + ("sim, " + projeto.endireitar_como if projeto.endireitar else "não"),
        "cortar as bordas: " + ("sim" if projeto.cortar_bordas else "não"),
        "filtro: " + NOMES_AMIGAVEIS.get(projeto.filtro_padrao, projeto.filtro_padrao),
    ]
    if getattr(projeto, "margens_iguais", False):
        partes.append("margens iguais: SIM ({} mm, alinhamento {})".format(
            "/".join(f"{v:g}" for v in projeto.margens_mm), "/".join(projeto.margens_alinhamento)))
    return " → ".join(partes)


def livro(pids: list[str], raiz: Path, pasta: Path, nome: str, campos: dict,
          campos_antes: dict | None = None) -> dict:
    """Antes (campos_antes) e depois (campos) do mesmo livro, pelo processar."""
    import fitz
    from core.pipeline import processar

    pasta.mkdir(parents=True, exist_ok=True)
    entrada = _livro(pids, raiz, pasta / f"{nome}-entrada.pdf")
    numeros = {"paginas": pids}
    for rotulo, troca in (("antes", campos_antes or {}), ("depois", campos)):
        pdf = pasta / f"{nome}-{rotulo}.pdf"
        projeto = _projeto_de_fabrica(entrada, pdf)
        for chave, valor in troca.items():
            if chave.startswith("pagina."):
                for pagina in projeto.paginas:
                    setattr(pagina, chave[len("pagina."):], valor)
            else:
                setattr(projeto, chave, valor)
        processar(projeto)
        with fitz.open(str(pdf)) as doc:
            numeros[rotulo] = {
                "por_onde_passou": _por_onde_passou(projeto),
                "tamanhos_cm": [[round(p.rect.width / 72 * 2.54, 2), round(p.rect.height / 72 * 2.54, 2)]
                                for p in doc],
                "avisos": {str(i): list(p.alertas) for i, p in enumerate(projeto.paginas_ativas)
                           if p.alertas},
            }
    (pasta / f"{nome}.json").write_text(json.dumps(numeros, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
    folha_de_contato(pasta, nome, numeros)
    return numeros


def folha_de_contato(pasta: Path, nome: str, numeros: dict, altura_cm_por_linha: float = 9.0) -> Path:
    """Antes numa linha, depois na outra, todas as páginas na MESMA escala
    (1 cm do papel = o mesmo tanto de pontos), com uma moldura cinza em volta
    de cada página para ver o tamanho dela e a frase de por onde passou."""
    import cv2
    import fitz
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    pontos_por_cm = 20
    linhas = []
    fonte = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 18)
    negrito = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 20)
    for rotulo in ("antes", "depois"):
        pedacos = []
        with fitz.open(str(pasta / f"{nome}-{rotulo}.pdf")) as doc:
            for i, pagina in enumerate(doc):
                pix = pagina.get_pixmap(dpi=pontos_por_cm * 2.54)
                img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3].copy()
                img = cv2.copyMakeBorder(img, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(150, 150, 150))
                legenda = Image.new("RGB", (img.shape[1], 30), "white")
                l, a = numeros[rotulo]["tamanhos_cm"][i]
                ImageDraw.Draw(legenda).text((4, 4), f"p. {i + 1}: {l:.1f} x {a:.1f} cm",
                                             fill="black", font=fonte)
                img = np.vstack([np.asarray(legenda), img])
                pedacos.append(img)
        altura = max(p.shape[0] for p in pedacos)
        pedacos = [cv2.copyMakeBorder(p, 0, altura - p.shape[0], 0, 14, cv2.BORDER_CONSTANT,
                                      value=(255, 255, 255)) for p in pedacos]
        linha = np.hstack(pedacos)
        titulo = Image.new("RGB", (linha.shape[1], 64), "white")
        desenho = ImageDraw.Draw(titulo)
        desenho.text((4, 2), rotulo.upper(), fill="black", font=negrito)
        desenho.text((4, 32), numeros[rotulo]["por_onde_passou"], fill="black", font=fonte)
        linhas.append(np.vstack([np.asarray(titulo), linha]))
    largura = max(l.shape[1] for l in linhas)
    linhas = [cv2.copyMakeBorder(l, 0, 24, 0, largura - l.shape[1], cv2.BORDER_CONSTANT,
                                 value=(255, 255, 255)) for l in linhas]
    final = cv2.cvtColor(np.vstack(linhas), cv2.COLOR_RGB2BGR)
    destino = pasta / f"{nome}-contato.png"
    cv2.imwrite(str(destino), final)
    return destino


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analisador.add_argument("--raiz", type=Path, default=RAIZ_PADRAO,
                            help="a worktree cujo código roda (de fábrica: esta)")
    sub = analisador.add_subparsers(dest="modo", required=True)
    a = sub.add_parser("somas")
    a.add_argument("--saida", type=Path, required=True)
    a.add_argument("pids", nargs="+")
    b = sub.add_parser("livro")
    b.add_argument("--saida", type=Path, required=True)
    b.add_argument("--nome", required=True)
    b.add_argument("--campos", required=True, help="JSON dos campos trocados no depois")
    b.add_argument("--campos-antes", default="{}", help="JSON dos campos trocados no antes")
    b.add_argument("pids", nargs="+")
    opcoes = analisador.parse_args()
    _preparar(opcoes.raiz.resolve())
    if opcoes.modo == "somas":
        somas(opcoes.pids, opcoes.raiz, opcoes.saida)
    else:
        print(json.dumps(livro(opcoes.pids, opcoes.raiz, opcoes.saida, opcoes.nome,
                               json.loads(opcoes.campos), json.loads(opcoes.campos_antes)),
                         ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
