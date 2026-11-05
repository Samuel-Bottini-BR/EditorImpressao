"""Verificador 04/11: D-604 (cada lado da folha do caderno diz as paginas do livro), nos tres
lugares: etapa 7 do Automatico, tela grande de caderno, "Montar para imprimir" (pela tela final,
depois de processar de verdade). Livro do acervo: Boecio (50 paginas), 20 paginas por caderno."""
import time
from pathlib import Path

import comum as C
from comum import anotar, conferir, p

WT = r"D:\programas\EditorImpressao\.claude\worktrees\caderno-numeros"


def esperado(n_paginas, por_caderno=20):
    """A conta da dobra, feita aqui a mao (independente do programa): para cada caderno de k
    lugares (k = por_caderno, o ultimo arredondado para cima ao multiplo de 4), a folha f tem
    frente = (k - 2f + 2, 2f - 1) e verso = (2f, k - 2f + 1), em numeros do caderno; o que passa
    do fim do livro e 'em branco'."""
    folhas = []
    inicio = 0
    while inicio < n_paginas:
        resto = n_paginas - inicio
        k = por_caderno if resto >= por_caderno else ((resto + 3) // 4) * 4
        for f in range(1, k // 4 + 1):
            def num(x):
                return str(inicio + x) if inicio + x <= n_paginas else "em branco"
            folhas.append(((num(k - 2 * f + 2), num(2 * f - 1)), (num(2 * f), num(k - 2 * f + 1))))
        inicio += k
    return folhas


def linhas(rotulos, numeros):
    return {lado: rotulos[lado].text() + numeros[lado].text() for lado in ("frente", "verso")}


def bate(texto, par):
    a, b = par
    return f"páginas {a} e {b}" in texto


def esperar_folha(folhas, limite=240):
    t = time.time(); C.base.esperar(0.5)
    while time.time() - t < limite and (folhas.calculando() or folhas.faces() is None):
        C.base.esperar(0.3)
    C.base.esperar(0.8)


def main():
    j, porteiro = C.abrir(WT, "6-caderno-numeros", "Sobre a Consolação da Filosofia - Severino Boécio.pdf")
    from core import automatico as A
    n = len([q for q in j.projeto.paginas if not q.apagada])
    esp = esperado(n)
    anotar("conta feita a mao", {"paginas": n, "folhas": len(esp), "folha 1": esp[0], "folha 2": esp[1],
                                 "ultimas": esp[-3:]})

    # 1. etapa 7 do Automatico (Montar cadernos), 20 por caderno
    estado = j.estado_do_automatico
    estado.marcadas = {A.CADERNOS}
    estado.opcoes["paginas_por_caderno"] = 20
    grande = j.abrir_o_automatico(A.CADERNOS); C.base.esperar(2)
    folhas = grande.folhas_do_caderno
    esperar_folha(folhas)
    l1 = linhas(folhas.rotulos, folhas.numeros_das_paginas)
    anotar("etapa 7 folha 1", l1)
    conferir(bate(l1["frente"], esp[0][0]) and bate(l1["verso"], esp[0][1]), f"etapa 7, folha 1: {l1}")
    conferir(l1["frente"].startswith(f"Folha 1 de {len(esp)} — frente"), "o 'Folha 1 de N — frente' continua")
    p(grande, "etapa7-folha-1")
    C.base.clique(grande, folhas.botao_seguinte)
    logo = linhas(folhas.rotulos, folhas.numeros_das_paginas)
    anotar("etapa 7 folha 2 logo depois do clique", logo)
    esperar_folha(folhas)
    l2 = linhas(folhas.rotulos, folhas.numeros_das_paginas)
    conferir(bate(l2["frente"], esp[1][0]) and bate(l2["verso"], esp[1][1]), f"etapa 7, folha 2: {l2}")
    conferir(bate(logo["frente"], esp[1][0]), "a folha 2 troca na hora (logo depois do clique)")
    p(grande, "etapa7-folha-2")
    # anda ate a folha 6 (comeco do caderno 2) e ate a ultima
    for alvo in (6, len(esp)):
        while folhas.posicao + 1 < alvo and folhas.botao_seguinte.isEnabled():
            C.base.clique(grande, folhas.botao_seguinte); C.base.esperar(0.15)
        esperar_folha(folhas)
        la = linhas(folhas.rotulos, folhas.numeros_das_paginas)
        anotar(f"etapa 7 folha {folhas.posicao + 1}", la)
        e = esp[folhas.posicao]
        conferir(bate(la["frente"], e[0]) and bate(la["verso"], e[1]), f"etapa 7, folha {folhas.posicao + 1}: {la} (esperado {e})")
        p(grande, f"etapa7-folha-{folhas.posicao + 1}")
    # a penultima (lugar em branco, se houver)
    C.base.clique(grande, folhas.botao_anterior); esperar_folha(folhas)
    la = linhas(folhas.rotulos, folhas.numeros_das_paginas); e = esp[folhas.posicao]
    anotar(f"etapa 7 folha {folhas.posicao + 1}", la)
    conferir(bate(la["frente"], e[0]) and bate(la["verso"], e[1]), f"etapa 7, folha {folhas.posicao + 1}: {la} (esperado {e})")
    p(grande, f"etapa7-folha-{folhas.posicao + 1}")

    # 2. tela grande de caderno
    folhas.posicao = 0; folhas.pedir(agora=True); esperar_folha(folhas)
    C.base.clique(grande, folhas.botao_tela_cheia); C.base.esperar(3)
    tela = folhas.tela_grande
    lt = linhas(tela.rotulos, tela.numeros_das_paginas)
    anotar("tela grande folha 1", lt)
    conferir(bate(lt["frente"], esp[0][0]) and bate(lt["verso"], esp[0][1]), f"tela grande, folha 1: {lt}")
    p(tela, "tela-grande-folha-1")
    C.base.clique(tela, tela.botao_proxima); esperar_folha(folhas); C.base.esperar(1)
    lt = linhas(tela.rotulos, tela.numeros_das_paginas)
    conferir(bate(lt["frente"], esp[1][0]) and bate(lt["verso"], esp[1][1]), f"tela grande, folha 2: {lt}")
    p(tela, "tela-grande-folha-2")
    tela.reject(); C.base.esperar(0.5)
    grande.reject(); C.base.esperar(1.5)

    # 3. processar de verdade e "montar para imprimir em A4" da tela final
    from ui.janela_principal import FINAL
    destino = C.base.TRAB / "saida" / "Boecio-pronto.pdf"
    fim = C.processar(j, destino)
    conferir(fim == FINAL and destino.exists(), f"processou: {destino.name} existe")
    p(j, "tela-final")
    tf = j.tela_final
    C.base.clique(j, tf.botao_montar); C.base.esperar(2)
    dialogo = tf.dialogo_impressao
    from core import impressao as imp
    o = dialogo.opcoes() if hasattr(dialogo, "opcoes") else None
    anotar("montar: opcoes de fabrica", {"formato": getattr(o, "formato", None),
                                         "por caderno": getattr(o, "paginas_por_caderno", None)})

    def quieta():
        return (not dialogo._relogio_da_previa.isActive()
                and not (dialogo.tarefa_previa is not None and dialogo.tarefa_previa.isRunning())
                and not dialogo._previa_pendente and not dialogo.bolinha_da_previa.carregando
                and dialogo.folha_na_tela is not None)

    def esperar(limite=180):
        t = time.time(); C.base.esperar(0.5)
        while time.time() - t < limite and not quieta():
            C.base.esperar(0.3)
        C.base.esperar(0.8)

    esperar()
    if o is not None and getattr(o, "paginas_por_caderno", 20) != 20:
        o.paginas_por_caderno = 20; dialogo.definir_opcoes(o); esperar()
    lm = linhas(dialogo.rotulos_da_face, dialogo.paginas_da_face)
    anotar("montar folha 1", {"texto": lm, "paginas do pdf": dialogo.paginas_do_livro})
    p(dialogo, "montar-para-imprimir-folha-1")
    # no livreto a primeira folha do Montar segue a mesma dobra (20 por caderno)?
    conferir(bate(lm["frente"], esp[0][0]) and bate(lm["verso"], esp[0][1]), f"montar para imprimir, folha 1: {lm}")
    C.base.clique(dialogo, dialogo.botao_folha_seguinte)
    logo = linhas(dialogo.rotulos_da_face, dialogo.paginas_da_face)
    esperar()
    lm2 = linhas(dialogo.rotulos_da_face, dialogo.paginas_da_face)
    anotar("montar folha 2", {"logo": logo, "depois": lm2})
    conferir(bate(lm2["frente"], esp[1][0]) and bate(lm2["verso"], esp[1][1]), f"montar para imprimir, folha 2: {lm2}")
    p(dialogo, "montar-para-imprimir-folha-2")
    dialogo.reject(); C.base.esperar(1)
    C.fechar(j)


if __name__ == "__main__":
    main()
