"""A janela de VERDADE, fora da tela (1280 x 657, o tamanho do notebook do Kaique a 150%), no
caminho do Kaique do zero e sem nada marcado (obra de 26/10/2026, etapa 7: o "está certo" com
resposta e os avisos): o "La vida eterna" (uma CÓPIA; o original só é lido) → Automático só com
"Dividir" (pelo clique) → o ícone "Para revisar" (clique) → clique no primeiro cartão → "está
certo" três vezes (o tique, o contador, a próxima dúvida) → o cartão com os botões do aviso →
"ver as N em tela cheia" → "Confirmar e processar": a "Antes de processar" (continuar assim
mesmo) e a janela de salvar (fechada sem processar) → de volta aos livros, o livro aberto com o
"Para revisar: N" e o "Ver todas as páginas" em "só as que precisam de atenção".

Cliques por mensagens nativas do Windows (PostMessage), prints por PrintWindow
(relatorios/obra-etapa3/roteiro/base.py). Dados e TEMP numa pasta de saida_teste/, nunca a pasta
de dados do Samuel. Guarda o PID e fecha só a própria janela (WM_CLOSE). Nunca processa: a
janela de salvar é fechada sem "Processar".

Uso (na worktree):
    .venv\\Scripts\\python.exe relatorios\\obra-etapa7\\roteiro\\prints.py <worktree> <prefixo>
<worktree> = o código a abrir (esta worktree, ou a cópia do código antigo para o "antes");
<prefixo> = "depois" ou "antes". Prints em relatorios/obra-etapa7/prints/.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

WORKTREE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RAIZ
PREFIXO = sys.argv[2] if len(sys.argv) > 2 else "depois"
PRINTS = RAIZ / "relatorios" / "obra-etapa7" / "prints"
TRAB = RAIZ / "saida_teste" / "obra-etapa7" / f"janela-{PREFIXO}"
LIVRO = Path(r"D:/Livros para editar/2 - TEOLOGIA/Escatologia/La vida eterna y La profundidad del alma.pdf")
NUMEROS: dict[str, str] = {}


def _p(widget, nome: str, so_cliente: bool = True):
    return base.print_window(widget, PRINTS / f"{PREFIXO}-{nome}.png", so_cliente=so_cliente)


def _esperar_ate(condicao, segundos=60.0) -> bool:
    for _ in range(int(segundos / 0.2)):
        if condicao():
            return True
        base.esperar(0.2)
    return condicao()


def _rodape(tela) -> tuple[int, int, int]:
    """(conferidas, de quantas, com dúvida) do rodapé (o texto inteiro, que fica no balão: na
    barra cheia o rótulo à vista pode estar encurtado)."""
    rotulo = tela.rotulo_do_livro
    texto = rotulo.toolTip() or rotulo.text()
    m = re.search(r"(\d+) de (\d+) conferidas · (\d+) com dúvida", texto)
    return tuple(int(x) for x in m.groups()) if m else (-1, -1, -1)


def _dividir_pelo_automatico(janela, tela):
    """O Automático só com "Dividir", no livro todo, pelo clique (como nas etapas 4 a 6)."""
    from PySide6.QtCore import QPoint

    from core import automatico as A

    tela.paineis.abrir("automatico")
    base.esperar(0.8)
    painel = tela.paineis.automatico
    lista = painel.lista
    item = next((lista.item(i) for i in range(lista.count())
                 if lista.item(i).data(0x0100) == A.DIVIDIR), None)
    if item is None:
        item = next(lista.item(i) for i in range(lista.count())
                    if lista.item(i).text().startswith(A.NOMES[A.DIVIDIR]))
    ret = lista.visualItemRect(item)
    base.clique(janela, lista.viewport(), QPoint(ret.left() + 14, ret.center().y()))
    base.esperar(0.8)
    base.conferir(painel.estado.marcadas == {A.DIVIDIR}, "Automático: só 'Dividir' marcado, pelo clique")
    base.clique(janela, painel.botao_rodar)
    _esperar_ate(lambda: janela.projeto.dividir_folhas and len(janela.projeto.paginas) > 300, 600)
    base.esperar(3.0)
    tela.paineis.fechar()
    base.esperar(1.0)


def _abrir_o_para_revisar(janela, tela):
    """Clique no ícone "Para revisar" da coluna da direita."""
    icones = tela.paineis.icones
    ret = icones.retangulos().get("revisar")
    base.clique(janela, icones, ret.center())
    base.esperar(1.5)
    base.conferir(tela.paineis.aberto == "revisar", "clique no ícone: o 'Para revisar' abriu")


def _clicar_no_cartao(janela, painel, linha: int = 0):
    lista = painel.lista
    ret = lista.visualItemRect(lista.item(linha))
    from PySide6.QtCore import QPoint
    base.clique(janela, lista.viewport(), QPoint(ret.center().x(), ret.top() + 14))
    base.esperar(2.0)


def main() -> None:
    from PySide6.QtWidgets import QApplication

    (RAIZ / "saida_teste" / "obra-etapa7").mkdir(parents=True, exist_ok=True)
    (RAIZ / "saida_teste" / "obra-etapa7" / f"pid-prints-{PREFIXO}.txt").write_text(str(os.getpid()))
    print("PID deste processo:", os.getpid(), flush=True)
    base.preparar(str(WORKTREE), str(TRAB))
    PRINTS.mkdir(parents=True, exist_ok=True)
    livro = TRAB / "La vida eterna.pdf"
    shutil.copy2(LIVRO, livro)                     # o original só é lido
    janela = base.nova_janela(1280, 657)
    janela.abrir_livro(str(livro))
    base.esperar(2.0)
    tela = janela.tela_conferir
    _esperar_ate(lambda: getattr(janela, "medida_ao_abrir", None) is None
                 or not janela.medida_ao_abrir.isRunning(), 240)
    base.esperar(1.0)
    projeto = janela.projeto
    base.conferir(not projeto.dividir_folhas and not projeto.cortar_bordas and not projeto.limpar,
                  "abrir sem nada marcado")
    _dividir_pelo_automatico(janela, tela)
    base.esperar(3.0)
    novo = hasattr(tela, "esta_certo")
    conf, total, duv = _rodape(tela)
    NUMEROS["rodapé depois de dividir"] = f"{conf} de {total} conferidas · {duv} com dúvida"
    _p(janela, "01-dividido")

    # o "Para revisar" e o primeiro cartão
    _abrir_o_para_revisar(janela, tela)
    painel = tela.paineis.para_revisar
    NUMEROS["Para revisar (painel)"] = str(painel._paginas)
    NUMEROS["ícone do Para revisar"] = str(tela.paineis.icones.contagem)
    _p(janela, "02-para-revisar-aberto")
    _clicar_no_cartao(janela, painel, 0)
    primeira = tela.indice_pagina
    base.conferir(not tela.trabalha_com_folhas, f"clique no cartão: na página {primeira + 1}, fora do Dividir")
    if novo:
        textos = [b.text() for b in painel.botoes_do_cartao if b.isVisibleTo(painel)]
        base.conferir(bool(textos), f"o cartão da página {primeira + 1} tem os botões do aviso: {textos}")
    _p(janela, "03-cartao-com-os-botoes-do-aviso")

    # "está certo" três vezes
    for vez in range(1, 4):
        antes_pagina = tela.indice_pagina
        antes = _rodape(tela)
        base.clique(janela, tela.botao_esta_certo)
        base.esperar(2.5)
        depois = _rodape(tela)
        conferida = bool(getattr(tela.tira._miniaturas[antes_pagina], "conferida", False))
        base.conferir(projeto.paginas[antes_pagina].revisada,
                      f"'está certo' {vez}: a página {antes_pagina + 1} ficou conferida (gravado)")
        base.conferir(conferida, f"'está certo' {vez}: tique na miniatura da página {antes_pagina + 1}")
        base.conferir(depois[0] == antes[0] + 1,
                      f"'está certo' {vez}: o contador subiu ({antes[0]} -> {depois[0]} de {depois[1]})")
        base.conferir(tela.indice_pagina != antes_pagina,
                      f"'está certo' {vez}: foi para a próxima dúvida (página {tela.indice_pagina + 1})")
        _p(janela, f"04-esta-certo-{vez}")

    # um cartão com aviso de botões (o da vez agora)
    if novo:
        textos = [b.text() for b in painel.botoes_do_cartao if b.isVisibleTo(painel)]
        NUMEROS["botões no cartão da vez"] = ", ".join(textos)

    # "ver as N em tela cheia"
    if hasattr(painel, "botao_tela_cheia"):
        n = _rodape(tela)[2]
        base.conferir(painel.botao_tela_cheia.text() == f"ver as {n} em tela cheia",
                      f"o botão diz o número do rodapé: '{painel.botao_tela_cheia.text()}'")
        base.clique(janela, painel.botao_tela_cheia)
        base.esperar(4.0)
        base.conferir(tela.pilha_da_tela.currentWidget() is tela.todas and tela.todas.so_atencao,
                      "'ver as N em tela cheia': a grade só com as que precisam de atenção")
        NUMEROS["grade (só as que precisam)"] = tela.todas.botao_atencao.text()
        _p(janela, "05-ver-as-N-em-tela-cheia")
        tela._voltar_das_todas(None)
        base.esperar(1.5)
    else:
        tela.abrir_todas_as_paginas()
        base.esperar(3.0)
        NUMEROS["grade (só as que precisam)"] = tela.todas.botao_atencao.text()
        tela._voltar_das_todas(None)
        base.esperar(1.0)

    NUMEROS["rodapé antes de processar (texto inteiro, o do balão)"] = tela.rotulo_do_livro.toolTip()
    NUMEROS["rodapé antes de processar (o que se vê, painel aberto)"] = tela.rotulo_do_livro.text()
    NUMEROS["Para revisar (painel), antes de processar"] = str(painel._paginas)

    # "Confirmar e processar": a "Antes de processar" e a janela de salvar (fechada sem processar)
    from ui.janela_confirmar import JanelaConfirmar
    from ui.janela_dos_avisos import JanelaDosAvisos

    def continuar(w):
        NUMEROS["Antes de processar"] = w.rotulo.text()
        w.botao_continuar.click()

    def salvar(w):
        NUMEROS["janela de salvar"] = (w.aviso_conferir.rotulo.text() if w.aviso_conferir.isVisible()
                                       else "(sem aviso de páginas)")

    txt = PRINTS / f"{PREFIXO}-textos-das-janelas.txt"
    base.quando_abrir_janela(JanelaDosAvisos, f"{PREFIXO}-06-antes-de-processar", PRINTS, txt,
                             depois=continuar, fechar=False)
    base.quando_abrir_janela(JanelaConfirmar, f"{PREFIXO}-07-janela-de-salvar", PRINTS, txt,
                             depois=salvar, fechar=True, espera_ms=2500)
    base.clique(janela, tela.botao_processar)
    base.esperar(12.0)
    base.conferir(not any(isinstance(w, JanelaConfirmar) and w.isVisible()
                          for w in QApplication.topLevelWidgets()), "a janela de salvar fechou sem processar")

    # de volta aos livros: o livro aberto
    janela._sair_da_conferencia()
    base.esperar(2.0)
    import projetos
    resumo = projetos.ler_resumo(janela.resumo.pasta)
    janela.tela_inicio.abrir_o_livro(resumo)
    base.esperar(3.0)
    aberto = janela.tela_inicio.livro_aberto
    NUMEROS["livro aberto"] = aberto.para_revisar.text()
    _p(janela, "08-livro-aberto")
    base.clique(janela, aberto.botao_todas)
    base.esperar(3.0)
    base.clique(janela, aberto.todas.botao_atencao)
    base.esperar(3.0)
    NUMEROS["livro aberto: Ver todas as páginas"] = aberto.todas.botao_atencao.text()
    _p(janela, "09-livro-aberto-so-as-que-precisam")

    with open(PRINTS / f"{PREFIXO}-numeros.txt", "w", encoding="utf-8") as f:
        for chave, valor in NUMEROS.items():
            f.write(f"{chave}: {valor}\n")
    for chave, valor in NUMEROS.items():
        print(f"  {chave}: {valor}", flush=True)
    base.fechar(janela)
    base.gravar_resultados(TRAB)


if __name__ == "__main__":
    main()
