"""Print 3 (n0411-caderno-pagina-em-branco; D-604): numeração das folhas do caderno com lugar sem
página, num livro DIVIDIDO.

Gradus Primus (cópia), aberto do zero; Automático só com "Dividir folhas ao meio" (opções de
fábrica) no livro todo. Depois, a janela do Automático na etapa 7 "Montar cadernos" (20 páginas
por caderno, o de fábrica), indo às folhas do fim até a que tem lugar sem página. Prints da
janela (grab) e o texto de cima das folhas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comum  # noqa: E402

RAIZ = str(AQUI.parent)
CRU = AQUI / "cru" / ("p3" if len(sys.argv) < 2 else "p3-" + sys.argv[1])
CRU.mkdir(parents=True, exist_ok=True)
NOTAS: dict = {}


def nota(chave, valor):
    NOTAS[chave] = valor
    print(chave, "=>", json.dumps(valor, ensure_ascii=False, default=str), flush=True)
    (CRU / "notas.json").write_text(json.dumps(NOTAS, ensure_ascii=False, indent=1, default=str),
                                    encoding="utf-8")


def esperar_folha(folhas, limite=400):
    comum.esperar(0.5)
    s = comum.ate(lambda: not folhas.calculando() and folhas.faces() is not None, limite, 0.3)
    comum.esperar(1.0)
    return s


def linhas(folhas) -> dict:
    return {lado: folhas.rotulos[lado].text() + folhas.numeros_das_paginas[lado].text()
            for lado in ("frente", "verso")}


def main():
    livro = sys.argv[1] if len(sys.argv) > 1 else "gradus"
    comum.preparar(RAIZ, "p3" if livro == "gradus" else f"p3-{livro}")
    from core import automatico as A

    pdf = AQUI / "livros" / ("gradus.pdf" if livro == "gradus" else "righetti.pdf")
    j = comum.nova_janela()
    j.abrir_livro(str(pdf))
    nota("abrir (s)", comum.esperar_tela(j))
    projeto = j.projeto
    nota("folhas", len(projeto.folhas))
    if livro == "righetti":
        # o Righetti vem deitado no scan: girar todas as folhas ¼ à esquerda (como no print 1)
        from core import girar
        tela = j.tela_conferir
        tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
        tela._girar_esquerda()
        comum.esperar(1.0)
        nota("rotacao", sorted({f.rotacao for f in projeto.folhas}))
    estado = j.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    nota("rodou o dividir", j.rodar_o_automatico(esperar=True, perguntar=False))
    comum.esperar(2.0)
    nota("paginas depois de dividir", len(projeto.paginas_ativas))
    nota("folhas divididas", sum(1 for f in projeto.folhas if f.dividir))
    comum.foto(j, CRU / "00-livro-dividido.png")

    estado.marcadas = {A.DIVIDIR, A.CADERNOS}
    grande = j.abrir_o_automatico(A.CADERNOS)
    grande.resize(1280, 657)
    grande.move(0, 0)
    comum.esperar(2.0)
    folhas = grande.folhas_do_caderno
    nota("folha 1 (s)", esperar_folha(folhas))
    nota("total de folhas", folhas.total())
    nota("folha 1", linhas(folhas))
    comum.foto(grande, CRU / "01-folha-1.png")
    # até a última folha
    for _ in range(folhas.total() + 2):
        if not folhas.botao_seguinte.isEnabled():
            break
        folhas.botao_seguinte.click()
        comum.esperar(0.1)
    nota("ultima (s)", esperar_folha(folhas))
    nota("ultima folha", linhas(folhas))
    comum.foto(grande, CRU / "02-ultima-folha.png")
    achou = "em branco" in "".join(linhas(folhas).values()) or "sem página" in "".join(linhas(folhas).values())
    n = 0
    while not achou and n < 40:
        folhas.botao_anterior.click()
        nota(f"voltou {n + 1} (s)", esperar_folha(folhas))
        texto = linhas(folhas)
        nota(f"voltou {n + 1}", texto)
        achou = "em branco" in "".join(texto.values()) or "sem página" in "".join(texto.values())
        n += 1
    nota("achou folha com lugar sem pagina", achou)
    comum.foto(grande, CRU / "03-folha-com-lugar-sem-pagina.png")
    # a vizinha seguinte também, para comparar
    if folhas.botao_seguinte.isEnabled():
        folhas.botao_seguinte.click()
        esperar_folha(folhas)
        nota("a seguinte", linhas(folhas))
        comum.foto(grande, CRU / "04-a-seguinte.png")
    comum.fechar(j)


if __name__ == "__main__":
    main()
