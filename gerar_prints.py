"""Os nove prints da seção 6, e a comparação com os desenhos (critério 2b).

    .venv\\Scripts\\python.exe gerar_prints.py

Grava tudo em `relatorios/prints/` e monta o `relatorios/para-conferir.html`.

Cada print é da tela DE VERDADE, com um livro do acervo aberto - não é
montagem. O de 150% roda num processo à parte, porque a escala do Qt é lida uma
vez só, quando o programa abre.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

DESTINO = RAIZ / "relatorios" / "prints"
DESENHOS = Path(r"C:\Users\fotog\Desktop\pasta do prompt")
ACERVO = Path(r"C:\Users\fotog\Desktop\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
LIVRO = ACERVO / "Sobre a Consolação da Filosofia - Severino Boécio.pdf"


def _esperar(app, segundos: float) -> None:
    fim = time.time() + segundos
    while time.time() < fim:
        app.processEvents()


def _pasta_de_projetos_temporaria():
    import projetos

    pasta = Path(tempfile.mkdtemp()) / "projetos"
    pasta.mkdir(parents=True)
    projetos.pasta_dos_projetos = lambda: pasta
    return pasta


# --- os prints --------------------------------------------------------------


def gerar(app, escala_150: bool = False) -> None:
    import projetos
    from PySide6.QtWidgets import QApplication

    from modelos import Acao, ConfigFolha, ConfigPagina, Projeto
    from ui.janela_principal import JanelaPrincipal
    from ui.tela_inicio import TelaInicio

    DESTINO.mkdir(parents=True, exist_ok=True)
    sufixo = " - 150%" if escala_150 else ""
    _pasta_de_projetos_temporaria()

    # ---------- a tela de trabalho, com um livro aberto ----------
    janela = JanelaPrincipal()
    janela.resize(1366, 768)
    janela.show()
    janela.abrir_livro(str(LIVRO))
    _esperar(app, 2)
    janela.analisar()
    _esperar(app, 50)

    tela = janela.tela_conferir
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("marcar"))
    tela.ir_para_pagina(16)
    _esperar(app, 8)

    janela.grab().save(str(DESTINO / f"1 - tela de trabalho{sufixo}.png"))
    print(f"  1 - tela de trabalho{sufixo}  "
          f"(pagina: {tela.area_imagem.height()} px de {janela.height()})")

    if escala_150:
        janela.close()
        return

    # ---------- a barra de opcoes em tres ferramentas ----------
    for numero, ferramenta in enumerate(("cor", "pincel", "zoom"), start=1):
        tela.escolher_ferramenta(ferramenta)
        _esperar(app, 1.5)
        tela.barra_opcoes.grab().save(
            str(DESTINO / f"2.{numero} - barra de opcoes - {ferramenta}.png"))
    print("  2 - barra de opcoes em tres ferramentas")

    # ---------- o painel Para revisar, agrupado por tipo ----------
    from core import analise

    projeto = janela.projeto
    for indice in (3, 9, 21):
        projeto.paginas[indice].alertas = [analise.ANGULO_SUSPEITO_]
        projeto.paginas[indice].revisada = False
    for indice in (5, 12):
        projeto.paginas[indice].alertas = [analise.COR]
        projeto.paginas[indice].revisada = False
    projeto.paginas[30].alertas = [analise.EM_BRANCO]
    projeto.paginas[30].revisada = False
    tela.atualizar()
    _esperar(app, 2)
    tela.paineis.para_revisar.grab().save(
        str(DESTINO / "4 - painel Para revisar - agrupado por tipo.png"))
    print("  4 - painel Para revisar")

    # ---------- o painel Historico, e uma acao sendo desfeita ----------
    from core.filtros import MAGICO_PRO, MELHORAR

    tela.ir_para_pagina(16)
    tela._registrar("filtro", "pagina", [16], {"filtro": MELHORAR},
                    "trocou para Melhorar")
    tela._registrar("filtro", "pagina", [17], {"filtro": MAGICO_PRO},
                    "trocou para Mágico pro")
    tela._registrar("apagada", "pagina", [18], {"apagada": True},
                    "apagou a página 19")
    _esperar(app, 3)
    tela.paineis.historico.grab().save(
        str(DESTINO / "3.1 - painel Historico - com acoes.png"))

    antes = len(janela.acoes.feitas)
    tela.desfazer()
    _esperar(app, 3)
    tela.paineis.historico.grab().save(
        str(DESTINO / "3.2 - painel Historico - uma acao desfeita.png"))
    print(f"  3 - painel Historico ({antes} acoes -> "
          f"{len(janela.acoes.feitas)} depois de desfazer)")

    # ---------- a janela de confirmacao ----------
    from modelos import nome_de_saida_sugerido
    from ui.janela_confirmar import JanelaConfirmar

    confirmar = JanelaConfirmar(projeto, nome_de_saida_sugerido(projeto), janela)
    confirmar.show()
    _esperar(app, 2)
    confirmar.grab().save(str(DESTINO / "8 - janela de confirmacao.png"))
    print(f"  8 - janela de confirmacao "
          f"({confirmar._nao_conferidas()} paginas nao conferidas)")
    confirmar.close()

    # ---------- antes e depois de fechar o programa ----------
    tela.ir_para_pagina(23)
    projeto.paginas[23].filtro = MAGICO_PRO
    projeto.paginas[23].revisada = True
    tela.atualizar()
    _esperar(app, 6)
    janela.grab().save(str(DESTINO / "7.1 - antes de fechar.png"))
    pasta_do_projeto = janela.resumo.pasta
    janela.close()
    _esperar(app, 2)

    outra = JanelaPrincipal()
    outra.resize(1366, 768)
    outra.show()
    outra.abrir_livro(str(LIVRO))
    _esperar(app, 2)
    outra.analisar()
    _esperar(app, 50)
    outra.tela_conferir.barra_abas.setCurrentIndex(
        outra.tela_conferir._abas_ativas.index("marcar"))
    _esperar(app, 8)
    outra.grab().save(str(DESTINO / "7.2 - depois de reabrir.png"))
    print(f"  7 - antes e depois de fechar "
          f"(voltou na pagina {outra.tela_conferir.indice_pagina + 1}, "
          f"filtro {outra.projeto.paginas[23].filtro}, "
          f"mesmo projeto: {outra.resumo.pasta == pasta_do_projeto})")
    outra.close()
    _esperar(app, 1)

    # ---------- a tela inicial, com cartoes ----------
    def _projeto_falso(caminho, nome, paginas, conferidas=0, pronto=False):
        p = Projeto(caminho_entrada=str(caminho), nome=Path(caminho).stem)
        p.folhas = [ConfigFolha(indice=i) for i in range(paginas)]
        p.paginas = [ConfigPagina(indice=i, folha=i) for i in range(paginas)]
        for pagina in p.paginas[:conferidas]:
            pagina.revisada = True
        resumo = projetos.criar(p, total_paginas=paginas)
        resumo.nome = nome
        resumo.pdf_gerado = pronto
        if pronto:
            resumo.caminho_saida = str(ACERVO)
        projetos.atualizar(resumo, p)
        return resumo

    livros = sorted(ACERVO.glob("*.pdf"))
    _projeto_falso(livros[8], "Consolação da Filosofia", 50, conferidas=31)
    _projeto_falso(livros[0], "Gradus primus", 140, conferidas=140, pronto=True)
    sumido = Path(tempfile.mkdtemp()) / "Gradus primus.pdf"
    sumido.write_bytes(b"Z" * 300_000)
    _projeto_falso(sumido, "Gradus primus (2)", 70)
    sumido.unlink()
    _projeto_falso(livros[4], "Gradus primus (3)", 70, conferidas=8)

    inicio = TelaInicio()
    inicio.resize(1366, 768)
    inicio.show()
    _esperar(app, 6)
    inicio.recarregar()
    _esperar(app, 4)
    inicio.grab().save(str(DESTINO / "5 - tela inicial - cartoes.png"))

    for indice in range(inicio.grade.count()):
        cartao = inicio.grade.itemAt(indice).widget()
        if getattr(cartao, "perdido", False):
            cartao.grab().save(
                str(DESTINO / "6 - cartao de PDF que saiu do lugar.png"))
            break
    print("  5 e 6 - tela inicial e cartao perdido")
    inicio.close()


def main() -> int:
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    from ui.estilo import FOLHA_DE_ESTILO

    app.setStyleSheet(FOLHA_DE_ESTILO)

    escala_150 = os.environ.get("QT_SCALE_FACTOR") == "1.5"
    print("Gerando os prints" + (" em 150%" if escala_150 else "") + "...")
    gerar(app, escala_150=escala_150)

    if not escala_150:
        # A escala do Qt e lida uma vez so, quando o programa abre: o print de
        # 150% tem de sair de OUTRO processo, senao sairia igual ao de 100%.
        print("\nAgora em 150%, num processo a parte...")
        ambiente = dict(os.environ, QT_SCALE_FACTOR="1.5")
        subprocess.run([sys.executable, str(RAIZ / "gerar_prints.py")],
                       env=ambiente, cwd=str(RAIZ), timeout=1800)
        print(f"\nPrints em: {DESTINO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
