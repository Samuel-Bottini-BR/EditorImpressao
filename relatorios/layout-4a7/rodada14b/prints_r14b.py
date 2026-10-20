"""Prints da janela de verdade para as duas perguntas refeitas da rodada 14 (909 e 910).

Mesma montagem de prints_r14.py (programa deste ramo, com o painel Filtro da etapa 4; cópia do
Boécio; janela fora da tela em 1280 x 657). As opções que ainda não existem são só trocas de texto
ou de visibilidade feitas AQUI, na hora da foto.
Uso: python prints_r14b.py <pasta_de_saida>   (arquivo descartável do agente de layout)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prints_r14 as r  # noqa: E402
from prints_layout import abrir_o_livro, esperar, nova_janela  # noqa: E402

from PySide6.QtCore import QRect  # noqa: E402


def q_pedaco(janela, tela) -> None:
    """909: o "só neste pedaço" refeito."""
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    print("\n909 só neste pedaço")
    tela.trilha.escolher("cortar")
    tela.paineis.fechar()
    pagina = janela.projeto.paginas[tela.indice_pagina]
    if pagina.filtro != PRETO_E_BRANCO:
        tela._escolher_filtro(PRETO_E_BRANCO)
        esperar(5)
    tela.paineis.abrir("filtro")
    esperar(4)
    painel = tela.paineis.filtro_da_pagina
    for chave in ("ajuste", "letras", "limpar", "mais"):
        painel.partes[chave].abrir(False)
    parte = painel.partes["pedaco"]
    parte.abrir(True)
    esperar(1)
    painel.rolagem.ensureWidgetVisible(parte, 0, 0)
    esperar(0.8)
    primeiro = painel.botoes_do_pedaco[""]

    def foto(nome, titulo):
        esperar(0.6)
        cena = r.Cena(janela)
        ret = r.com_folga(r.no_janela(parte, janela), 6, janela)
        cena.ampliado(nome + "-ampliado", ret, titulo)
        cena.inteira(nome, [r.no_janela(parte, janela)])

    foto("23-rodada14b-pedaco-hoje", "Hoje")
    # A: o botão de cima sai, e o pedaço começa no Original
    primeiro.setVisible(False)
    painel.filtro_pedaco = ORIGINAL
    painel._acertar_pedaco()
    foto("23-rodada14b-pedaco-a", "A: o pedaço começa no Original")
    # B: o botão de cima sai, e nenhum vem aceso
    painel.filtro_pedaco = "nenhum"
    painel._acertar_pedaco()
    parte.definir_resumo("nenhum escolhido")
    foto("23-rodada14b-pedaco-b", "B: nenhum aceso; só ganha filtro se você escolher")
    # C: fica o botão, com outro nome
    primeiro.setVisible(True)
    primeiro.setText("igual ao resto da página")
    painel.filtro_pedaco = ""
    painel._acertar_pedaco()
    parte.definir_resumo("igual ao resto da página")
    foto("23-rodada14b-pedaco-c", "C: fica o botão, com o nome “igual ao resto da página”")
    primeiro.setText("o mesmo da página")
    painel._acertar_pedaco()
    tela.paineis.fechar()


def q_mao(janela, tela) -> None:
    """910: a "Conta" do Endireitar com o ângulo posto à mão, sem esconder os ângulos."""
    from core.pipeline import angulos_medidos
    from ui.tela_conferir import texto_dos_angulos_medidos

    print("\n910 conta com o ângulo à mão")
    tela.trilha.escolher("endireitar")
    tela.paineis.abrir("props")
    esperar(4)
    rolagem = tela.paineis.propriedades.rolagem.verticalScrollBar()
    linha = tela.rotulo_angulos_medidos
    pagina = janela.projeto.paginas[tela.indice_pagina]
    medidos = texto_dos_angulos_medidos(angulos_medidos(janela.projeto, pagina))
    print("     ângulos medidos:", medidos)

    def foto(nome, titulo):
        rolagem.setValue(rolagem.maximum())
        esperar(0.6)
        botao = r.botao_com_texto(tela.paineis.propriedades, "usar o ângulo do programa")
        ret = r.com_folga(r.juntar(r.no_janela(tela.rotulo_conta_do_endireitar, janela),
                                   r.no_janela(linha, janela)), 14, janela)
        ret = ret.united(r.no_janela(botao, janela).adjusted(0, -14, 0, 0))
        ret.setTop(r.no_janela(tela.campo_angulo, janela).top() - 30
                   if hasattr(tela, "campo_angulo") else ret.top())
        cena = r.Cena(janela)
        cena.ampliado(nome + "-ampliado", ret, titulo)
        cena.inteira(nome, [ret])

    foto("23-rodada14b-mao-antes", "Antes de girar à mão")
    tela.botao_angulo_horario.click()
    esperar(4)
    foto("23-rodada14b-mao-hoje", "Hoje, depois de girar à mão: a linha dos ângulos some")
    angulo = pagina.angulo_manual
    texto_mao = f"{angulo:+.1f}°".replace(".", ",") if angulo is not None else "?"
    # A: a linha continua, e outra diz o seu
    linha.setText(f"{medidos}\nVocê girou à mão: {texto_mao}. As contas voltam com "
                  "“usar o ângulo do programa”.")
    foto("23-rodada14b-mao-a", "A: os dois ângulos continuam, e uma linha diz o seu")
    # B: os três numa linha só
    linha.setText(f"{medidos} · à mão {texto_mao} (vale)")
    foto("23-rodada14b-mao-b", "B: os três ângulos numa linha, com o que vale")
    # C: a linha continua como antes de girar
    linha.setText(medidos)
    foto("23-rodada14b-mao-c", "C: a linha continua igual à de antes de girar")
    tela.botao_angulo_anti_horario.click()
    esperar(3)


def principal(destino: Path) -> None:
    r.SAIDA = destino
    janela = nova_janela()
    tela = abrir_o_livro(janela, dividir=True)
    tela.ir_para_pagina(4)
    esperar(6)
    q_pedaco(janela, tela)
    q_mao(janela, tela)
    janela.close()
    esperar(1)


if __name__ == "__main__":
    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    principal(destino)
    print("FIM", flush=True)
