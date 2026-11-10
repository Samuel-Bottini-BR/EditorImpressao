import json, time
import numpy as np, cv2
import piloto as P, menus as M

ESTADO = ("(jp.telas.currentIndex(), tc.aba_atual, "
          "[ (type(p).__name__, p.isVisible()) for p in tc.findChildren(QtWidgets.QWidget) if type(p).__name__.startswith('Painel')], "
          "[w.windowTitle() for w in QtWidgets.QApplication.topLevelWidgets() if w.isVisible()], "
          "len(tc.projeto.paginas), [p.apagada for p in tc.projeto.paginas][:3], tc.indice_pagina)")


def img(nome):
    f, _, _ = P.printar(nome)
    return cv2.imdecode(np.fromfile(str(f), np.uint8), 1)


def estado():
    return P.sonda(ESTADO), len(P.erros_log())


def testar(menu, item, nome, prep=None):
    if prep:
        prep()
    e0 = estado(); a = img(f'menu-{nome}-antes')
    M.clicar_item(menu, item)
    time.sleep(1.5)
    janelas = [x[1:3] for x in P.janelas()]
    e1 = estado(); b = img(f'menu-{nome}-depois')
    dif = float(np.abs(a.astype(int) - b.astype(int)).mean())
    print(f'{menu} > {item}: estado igual={e0 == e1} erros.log mudou={e0[1] != e1[1]} diferenca da imagem={dif:.3f} janelas={janelas}')
    if e0 != e1:
        print('   antes ', e0); print('   depois', e1)
    M.fechar_menus()
    return dif
