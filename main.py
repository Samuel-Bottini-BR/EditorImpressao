"""Editor de Impressão - ponto de entrada.

Recupera PDFs de livros antigos escaneados e prepara para reimpressao.
"""

from __future__ import annotations

import sys
import traceback


def main() -> int:
    """Sobe o QApplication, arma a rede de seguranca contra excecao nao
    tratada (regra 3.3: nunca stack trace na tela) e abre a janela principal.
    Se o programa foi chamado com um caminho de PDF (associacao de arquivo do
    instalador), abre esse livro direto."""
    # Tela de carregamento (D-744, D-745, D-747, 17/11/2026): o brasao girando
    # aparece JA, antes dos imports pesados, num processo a parte que gira
    # liso enquanto este carrega; some quando a janela principal aparece (logo
    # abaixo, depois do janela.show()). Nos testes e na conta dos testes a
    # distancia nao aparece. Ver ui/tela_de_carregamento.py.
    from ui.tela_de_carregamento import abrir_o_brasao

    brasao_girando = abrir_o_brasao()

    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QMessageBox

    import brasao
    from registro import registrar_erro

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Editor de Impressão")
    # O icone do programa e o brasao inteiro, desenhado do vetor em cada
    # tamanho (D-746): vale para todas as janelas e para a barra de tarefas.
    app.setWindowIcon(QIcon(str(brasao.ICONE)))

    # Obra 26/10 (etapa 9a, teste do Kaique): a rodinha do mouse so muda
    # numero/lista depois de clicar nele; e os textos do proprio Qt em
    # portugues (ui/rodinha.py, ui/dialogos_de_arquivo.py).
    from ui import rodinha
    from ui.dialogos_de_arquivo import traduzir_o_qt

    rodinha.instalar_no_programa(app)
    traduzir_o_qt(app)

    # Aquece em segundo plano o import pesado que o filtro Preto e branco
    # faria sob demanda - ver core/aquecimento.py para o motivo.
    from core.aquecimento import aquecer_em_segundo_plano

    aquecer_em_segundo_plano()

    # Sobe ja os servidores de paginas (core/paginas_em_outro_processo.py),
    # para a primeira pagina nao esperar por eles.
    from core.paginas_em_outro_processo import iniciar_em_segundo_plano

    iniciar_em_segundo_plano()

    # Rede de seguranca final: qualquer erro nao tratado vira aviso em
    # portugues e o programa continua aberto (regra 3.3).
    def tratar(tipo, valor, rastro) -> None:
        registrar_erro("não tratado", "".join(traceback.format_exception(tipo, valor, rastro)))
        # Botao "entendi" (ui.perguntas): a funcao pronta do Qt punha "OK"
        # sem traducao (tests/test_botoes_em_portugues.py).
        from ui import perguntas

        perguntas.avisar(
            None, "Um momento",
            "Aconteceu um problema inesperado, mas o programa continua funcionando.",
            icone=QMessageBox.Information)

    sys.excepthook = tratar

    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.show()
    # A janela principal apareceu: o brasao girando some (D-744). Pelo laco do
    # Qt, para a janela ja estar desenhada quando ele sumir.
    QTimer.singleShot(0, brasao_girando.fechar)

    # Primeira abertura do programa (D-721): uma janela pequena pede "a senha
    # dos testes a distancia". So aparece uma vez; depois, da para por a senha
    # nas Configuracoes. So no programa instalado pelo instalador (D-728): pelo
    # codigo nao mostra nada e nao marca nada, com a mesma regra da atualizacao
    # (atualizacao.instalado_pelo_velopack). Desde 17/11 (D-733, D-735), logo
    # depois dela vem SEMPRE uma pergunta do Windows, que cria o ajudante da
    # atualizacao (com a senha, os testes a distancia vao na mesma pergunta).
    # Ver ui/testes_a_distancia_ui.py.
    from ui.testes_a_distancia_ui import primeira_vez_se_preciso

    primeira_vez_se_preciso(janela)

    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".pdf"):
        janela.abrir_livro(sys.argv[1])

    # Atualizacao (etapa 3 da frente do Kaique): manda o ajudante procurar a
    # versao nova (D-732, "quando o programa e aberto") e liga o aviso da versao
    # nova e o da atualizacao que falhou (D-715, D-719, D-720). Vem DEPOIS da
    # primeira abertura de proposito: na primeira vez, o ajudante nasce nela.
    # So no programa instalado pelo Velopack; pelo codigo nao faz nada. Ver
    # ui/aviso_de_atualizacao.py.
    from ui.aviso_de_atualizacao import ligar_na_janela

    ligar_na_janela(janela)

    return app.exec()


if __name__ == "__main__":
    # Servidor de paginas (30/09/2026): o programa desenha as paginas do PDF
    # num processo a parte, para a janela nunca congelar - ver
    # core/paginas_em_outro_processo.py. Empacotado, esse processo e este mesmo
    # .exe com este argumento: tem de ser atendido AQUI, antes de qualquer
    # janela (senao abriria uma segunda janela do programa).
    if len(sys.argv) > 3 and sys.argv[1] == "--servidor-de-paginas":
        from core.paginas_em_outro_processo import servir

        servir(sys.argv[2], sys.argv[3])
        raise SystemExit(0)
    # Tela de carregamento (D-744): o processo do brasao girando, aberto pelo
    # main() abaixo (ui/tela_de_carregamento.py). Atendido AQUI, antes de
    # tudo, para nao abrir outra janela do programa.
    if len(sys.argv) > 2 and sys.argv[1] == "--brasao-girando":
        from ui.brasao_girando import rodar_sozinho

        raise SystemExit(rodar_sozinho(sys.argv[2]))
    # Conferência dos detectores de texto, sem janela (item 1.3): prova que o
    # programa EMPACOTADO acha o docTR, o Tesseract e o motor do Kraken. Ver
    # core/ocr_diagnostico.py. Não é usada pelo Kaique.
    if len(sys.argv) > 1 and sys.argv[1] == "--conferir-ocr":
        from core.ocr_diagnostico import linha_de_comando

        raise SystemExit(linha_de_comando(sys.argv[2:]))
    # Atualizacao pela internet (Velopack; etapa 3 da frente do Kaique): os
    # ganchos de instalar/desinstalar, os modos sem janela (o ajudante procura
    # a versao nova, conferir a versao nova, preparar o computador dentro da
    # pergunta do Windows) e, no programa instalado, a troca antes da janela
    # quando ha versao nova esperando do "Depois" (D-734). Pelo codigo e sem
    # argumento nosso nao faz nada. Ver atualizacao.py.
    from atualizacao import atender_linha_de_comando

    codigo = atender_linha_de_comando(sys.argv)
    if codigo is not None:
        raise SystemExit(codigo)
    raise SystemExit(main())
