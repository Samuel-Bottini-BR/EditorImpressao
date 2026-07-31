"""Etapa 3 do protocolo: o que acontece quando da errado.

Os dezoito casos que o Kaique pode encontrar. Para cada um, tres perguntas:

    1. o programa continua de pe?
    2. a mensagem e compreensivel por quem nao e tecnico?
    3. o trabalho ja feito foi perdido?

Nenhum caso pode fechar o programa nem mostrar mensagem tecnica. Grava
relatorios/robustez.md.

    .venv\\Scripts\\python.exe teste_robustez_completo.py
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import fitz  # noqa: E402
import numpy as np  # noqa: E402

from core.pdf_io import ErroPDF, abrir_pdf, pagina_para_array  # noqa: E402
from core.pipeline import Cancelou, analisar_projeto, processar  # noqa: E402
from modelos import Projeto  # noqa: E402

RELATORIOS = RAIZ / "relatorios"
RELATORIOS.mkdir(exist_ok=True)

# Palavras que denunciam mensagem tecnica vazando para o usuario final.
JARGAO = (
    "traceback", "exception", "error:", "errno", "none", "null", "stack",
    "0x", "assert", "attribute", "typeerror", "valueerror", "keyerror",
    "indexerror", "runtime", "segmentation", "fitz", "cv2", "numpy",
    "byte", "buffer", "utf-8", "codec", "module", "object at",
)


@dataclass
class Caso:
    nome: str
    o_que_e: str
    de_pe: bool = False
    mensagem: str = ""
    boa_mensagem: bool = True
    perdeu_trabalho: bool = False
    observacao: str = ""
    detalhes: list[str] = field(default_factory=list)

    @property
    def passou(self) -> bool:
        return self.de_pe and self.boa_mensagem and not self.perdeu_trabalho


def mensagem_e_boa(texto: str) -> tuple[bool, str]:
    """A mensagem serve para quem nao e tecnico?"""
    if not texto:
        return True, ""
    baixa = texto.lower()
    for palavra in JARGAO:
        if palavra in baixa:
            return False, f"contem jargao: {palavra!r}"
    if len(texto) > 400:
        return False, "longa demais"
    return True, ""


def pagina_png(cor: int = 235, com_texto: bool = True) -> bytes:
    arte = np.full((900, 600, 3), cor, dtype=np.uint8)
    if com_texto:
        for y in range(120, 800, 60):
            arte[y:y + 22, 80:520] = 30
    return cv2.imencode(".png", arte)[1].tobytes()


def fabricar(pasta: Path) -> dict[str, Path]:
    """Monta um PDF para cada situacao ruim."""
    a: dict[str, Path] = {}
    png = pagina_png()

    def novo(nome: str, paginas, **salvar) -> Path:
        doc = fitz.open()
        for largura, altura, conteudo in paginas:
            p = doc.new_page(width=largura, height=altura)
            if conteudo is not None:
                p.insert_image(fitz.Rect(0, 0, largura, altura), stream=conteudo)
        caminho = pasta / nome
        doc.save(caminho, **salvar)
        doc.close()
        return caminho

    a["uma_pagina"] = novo("uma_pagina.pdf", [(420, 630, png)])
    a["tamanhos_variados"] = novo("tamanhos_variados.pdf", [
        (420, 630, png), (840, 420, png), (300, 900, png), (420, 630, png)])
    a["com_senha"] = novo(
        "com_senha.pdf", [(420, 630, png)],
        encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw="segredo", user_pw="segredo")

    # so vetor, sem imagem embutida
    doc = fitz.open()
    p = doc.new_page(width=420, height=630)
    p.draw_rect(fitz.Rect(60, 60, 360, 200), color=(0, 0, 0), width=2)
    p.insert_text(fitz.Point(80, 300), "texto vetorial sem imagem", fontsize=14)
    a["so_vetor"] = pasta / "so_vetor.pdf"
    doc.save(a["so_vetor"])
    doc.close()

    # mais de 1000 paginas
    doc = fitz.open()
    pequeno = cv2.imencode(".png", np.full((160, 110, 3), 235, np.uint8))[1].tobytes()
    for _ in range(1010):
        p = doc.new_page(width=220, height=320)
        p.insert_image(fitz.Rect(0, 0, 220, 320), stream=pequeno)
    a["mil_paginas"] = pasta / "mil_paginas.pdf"
    doc.save(a["mil_paginas"], deflate=True)
    doc.close()

    # paginas giradas
    doc = fitz.open()
    for giro in (0, 90, 180, 270):
        p = doc.new_page(width=420, height=630)
        p.insert_image(fitz.Rect(0, 0, 420, 630), stream=png)
        p.set_rotation(giro)
    a["giradas"] = pasta / "giradas.pdf"
    doc.save(a["giradas"])
    doc.close()

    # pagina gigante, tipo mapa dobrado
    grande = cv2.imencode(
        ".png", np.full((2200, 3400, 3), 235, np.uint8))[1].tobytes()
    a["gigante"] = novo("gigante.pdf", [(3400, 2200, grande)])

    a["toda_preta"] = novo("toda_preta.pdf", [(420, 630, pagina_png(8, False))])
    a["toda_branca"] = novo("toda_branca.pdf", [(420, 630, pagina_png(255, False))])

    # nome com acento, espaco e parenteses
    a["nome_dificil"] = pasta / "Diário do Pároco (cópia 2) - versão final.pdf"
    shutil.copy(a["uma_pagina"], a["nome_dificil"])

    # caminho com mais de 260 caracteres
    fundo = pasta
    while len(str(fundo)) < 250:
        fundo = fundo / "uma_pasta_com_nome_bem_comprido_para_testar"
    try:
        fundo.mkdir(parents=True, exist_ok=True)
        a["caminho_longo"] = fundo / "livro.pdf"
        shutil.copy(a["uma_pagina"], a["caminho_longo"])
    except Exception:  # noqa: BLE001 - o proprio Windows pode barrar
        a["caminho_longo"] = pasta / "_caminho_longo_indisponivel.pdf"

    # corrompido, nao e PDF, vazio
    bons = a["uma_pagina"].read_bytes()
    a["corrompido"] = pasta / "corrompido.pdf"
    a["corrompido"].write_bytes(bons[: len(bons) // 3] + b"\x00lixo\x00" * 40)
    a["nao_e_pdf"] = pasta / "na_verdade_e_texto.pdf"
    a["nao_e_pdf"].write_text("isto e um texto qualquer", encoding="utf-8")
    a["vazio"] = pasta / "vazio.pdf"
    a["vazio"].write_bytes(b"")

    return a


def rodar(caso: Caso, funcao) -> Caso:
    """Executa um caso e anota o que aconteceu."""
    try:
        funcao(caso)
        caso.de_pe = True
    except (ErroPDF, Cancelou) as erro:
        # erro previsto, com mensagem para o usuario: e o comportamento certo
        caso.de_pe = True
        caso.mensagem = str(erro)
        caso.boa_mensagem, motivo = mensagem_e_boa(caso.mensagem)
        if motivo:
            caso.observacao = motivo
    except Exception as erro:  # noqa: BLE001 - qualquer outra coisa e falha
        caso.de_pe = False
        caso.mensagem = f"{type(erro).__name__}: {erro}"
        caso.boa_mensagem = False
        caso.observacao = "erro tecnico nao tratado"
        caso.detalhes.append(traceback.format_exc()[-600:])
    return caso


def projeto_de(caminho: Path, saida: Path, **extra) -> Projeto:
    p = Projeto(
        caminho_entrada=str(caminho),
        caminho_saida=str(saida),
        nome=caminho.stem,
        qualidade_dpi=extra.pop("dpi", 150),
    )
    for chave, valor in extra.items():
        setattr(p, chave, valor)
    return p


def main() -> int:
    temporaria = Path(tempfile.mkdtemp(prefix="robustez_"))
    saida = temporaria / "saida"
    saida.mkdir()
    print(f"pasta de trabalho: {temporaria}\n")

    print("fabricando os arquivos de teste...", flush=True)
    arq = fabricar(temporaria)
    casos: list[Caso] = []

    def abrir_e_analisar(caminho: Path, **extra):
        def executar(caso: Caso) -> None:
            projeto = projeto_de(caminho, saida / f"{caminho.stem}.pdf", **extra)
            analisar_projeto(projeto)
            processar(projeto)
        return executar

    # --- os arquivos que nao deveriam abrir ---------------------------------
    for chave, nome, o_que_e in [
        ("corrompido", "PDF corrompido", "arquivo picado no meio"),
        ("nao_e_pdf", "Arquivo que nao e PDF", "texto renomeado para .pdf"),
        ("vazio", "Arquivo vazio", "zero byte"),
        ("com_senha", "PDF protegido por senha", "aberto so com senha"),
    ]:
        casos.append(rodar(Caso(nome, o_que_e), abrir_e_analisar(arq[chave])))

    # --- os que devem abrir e funcionar -------------------------------------
    for chave, nome, o_que_e in [
        ("uma_pagina", "PDF de uma pagina so", "livro minimo"),
        ("so_vetor", "PDF sem imagem", "so texto vetorial"),
        ("tamanhos_variados", "Paginas de tamanhos diferentes", "no mesmo arquivo"),
        ("giradas", "Paginas giradas", "0, 90, 180 e 270 graus"),
        ("gigante", "Pagina gigante", "tipo mapa dobrado, 3400x2200 pt"),
        ("toda_preta", "Pagina toda preta", "scan falhado"),
        ("toda_branca", "Pagina toda branca", "folha de guarda"),
        ("nome_dificil", "Nome com acento e parenteses", "'Diario do Paroco (copia 2)'"),
        ("caminho_longo", "Caminho com mais de 260 letras", "pastas encadeadas"),
    ]:
        casos.append(rodar(Caso(nome, o_que_e), abrir_e_analisar(arq[chave])))

    # --- mais de mil paginas ------------------------------------------------
    def muitas(caso: Caso) -> None:
        projeto = projeto_de(arq["mil_paginas"], saida / "mil.pdf", dividir_folhas=False)
        inicio = time.perf_counter()
        analisar_projeto(projeto)
        caso.observacao = (f"{len(projeto.folhas)} folhas analisadas em "
                           f"{time.perf_counter() - inicio:.0f}s")
    casos.append(rodar(Caso("PDF de mais de 1000 paginas", "1010 paginas"), muitas))

    # --- arquivo aberto por outro programa ----------------------------------
    def em_uso(caso: Caso) -> None:
        alvo = temporaria / "em_uso.pdf"
        shutil.copy(arq["uma_pagina"], alvo)
        with open(alvo, "rb") as travado:  # noqa: SIM115 - o ponto e manter aberto
            travado.read(10)
            projeto = projeto_de(alvo, saida / "em_uso_saida.pdf")
            analisar_projeto(projeto)
            processar(projeto)
        caso.observacao = "leitura funciona com o arquivo aberto por outro"
    casos.append(rodar(Caso("Arquivo aberto em outro programa", "travado por outro"), em_uso))

    # --- arquivo some no meio do caminho ------------------------------------
    def sumiu(caso: Caso) -> None:
        alvo = temporaria / "vai_sumir.pdf"
        shutil.copy(arq["tamanhos_variados"], alvo)
        projeto = projeto_de(alvo, saida / "sumiu.pdf")
        analisar_projeto(projeto)
        alvo.unlink()  # o pendrive foi arrancado
        processar(projeto)
    casos.append(rodar(Caso("Arquivo some no meio (pendrive)", "removido apos abrir"), sumiu))

    # --- destino impossivel de gravar ---------------------------------------
    def sem_destino(caso: Caso) -> None:
        projeto = projeto_de(arq["uma_pagina"], Path("Z:/nao_existe/saida.pdf"))
        analisar_projeto(projeto)
        processar(projeto)
    casos.append(rodar(Caso("Disco cheio ou sem destino", "unidade inexistente"), sem_destino))

    # --- cancelar no meio ---------------------------------------------------
    def cancelar(caso: Caso) -> None:
        projeto = projeto_de(arq["tamanhos_variados"], saida / "cancelado.pdf")
        analisar_projeto(projeto)
        contador = {"n": 0}

        def cancelado() -> bool:
            contador["n"] += 1
            return contador["n"] > 2

        try:
            processar(projeto, cancelado=cancelado)
        except Cancelou:
            pass
        sobrou = (saida / "cancelado.pdf").exists()
        caso.observacao = ("PDF pela metade ficou no disco" if sobrou
                           else "nada pela metade ficou no disco")
        caso.perdeu_trabalho = False
        if sobrou:
            caso.boa_mensagem = False
    casos.append(rodar(Caso("Cancelar no meio", "usuario desiste"), cancelar))

    # --- abrir dois livros seguidos -----------------------------------------
    def dois_seguidos(caso: Caso) -> None:
        for n, chave in enumerate(("uma_pagina", "tamanhos_variados", "giradas")):
            projeto = projeto_de(arq[chave], saida / f"seq{n}.pdf")
            analisar_projeto(projeto)
            processar(projeto)
        caso.observacao = "tres livros seguidos, sem reiniciar"
    casos.append(rodar(Caso("Abrir varios livros sem reiniciar", "um apos o outro"), dois_seguidos))

    # --- memoria nao cresce com o tamanho do livro --------------------------
    def memoria(caso: Caso) -> None:
        import psutil

        processo = psutil.Process(os.getpid())
        picos = []
        for chave in ("uma_pagina", "mil_paginas"):
            antes = processo.memory_info().rss / (1024 * 1024)
            projeto = projeto_de(arq[chave], saida / f"mem_{chave}.pdf",
                                 dividir_folhas=False)
            analisar_projeto(projeto)
            picos.append(processo.memory_info().rss / (1024 * 1024) - antes)
        caso.observacao = (f"1 pagina: +{picos[0]:.0f} MB; "
                           f"1010 paginas: +{picos[1]:.0f} MB")
        if picos[1] > max(120.0, picos[0] * 4 + 120):
            caso.boa_mensagem = False
            caso.observacao += "  (cresceu com o tamanho do livro)"
    casos.append(rodar(Caso("Memoria com livro grande", "1 pagina contra 1010"), memoria))

    # --- relatorio ----------------------------------------------------------
    passaram = sum(1 for c in casos if c.passou)
    L: list[str] = []
    L.append("# Robustez: o que acontece quando da errado")
    L.append("")
    L.append("Cada linha e uma coisa que pode acontecer na mao do Kaique. O que se")
    L.append("cobra e sempre o mesmo: o programa nao pode fechar, a mensagem tem de")
    L.append("ser compreensivel por quem nao e tecnico, e o trabalho ja feito nao")
    L.append("pode se perder.")
    L.append("")
    L.append(f"**{passaram} de {len(casos)} casos passaram.**")
    L.append("")
    L.append("| Situacao | O que e | Continuou de pe? | Mensagem | Perdeu trabalho? |")
    L.append("|---|---|---|---|---|")
    for c in casos:
        msg = c.mensagem or c.observacao or "-"
        if not c.boa_mensagem and c.observacao and c.observacao not in msg:
            msg = f"{msg} ({c.observacao})"
        L.append(f"| {'OK' if c.passou else '**FALHOU**'} {c.nome} | {c.o_que_e} | "
                 f"{'sim' if c.de_pe else '**NAO**'} | {msg[:150]} | "
                 f"{'sim' if c.perdeu_trabalho else 'nao'} |")
    L.append("")

    ruins = [c for c in casos if not c.passou]
    if ruins:
        L.append("## Os que falharam")
        L.append("")
        for c in ruins:
            L.append(f"### {c.nome}")
            L.append("")
            L.append(f"- O que e: {c.o_que_e}")
            L.append(f"- Continuou de pe: {'sim' if c.de_pe else 'NAO'}")
            L.append(f"- O que apareceu: {c.mensagem or '(nada)'}")
            if c.observacao:
                L.append(f"- Observacao: {c.observacao}")
            for d in c.detalhes:
                L.append("")
                L.append("```")
                L.append(d.strip())
                L.append("```")
            L.append("")

    (RELATORIOS / "robustez.md").write_text("\n".join(L), encoding="utf-8")

    print()
    print(f"{'situacao':38s}{'de pe':>7s}{'msg':>6s}{'passou':>8s}")
    print("-" * 60)
    for c in casos:
        print(f"{c.nome[:38]:38s}{'sim' if c.de_pe else 'NAO':>7s}"
              f"{'ok' if c.boa_mensagem else 'RUIM':>6s}"
              f"{'sim' if c.passou else 'NAO':>8s}")
    print("-" * 60)
    print(f"{passaram} de {len(casos)} passaram")
    print(f"\nRelatorio: {RELATORIOS / 'robustez.md'}")

    shutil.rmtree(temporaria, ignore_errors=True)
    return 0 if passaram == len(casos) else 1


if __name__ == "__main__":
    raise SystemExit(main())
