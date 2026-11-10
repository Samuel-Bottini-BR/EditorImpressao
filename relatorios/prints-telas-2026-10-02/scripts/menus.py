"""Abre um menu da barra e clica num item, so com mensagens nativas."""
import time
import piloto as P


def abrir_menu(nome):
    P.clicar(nome, titulo='Editor de Impressão', classe='menu_barra', espera=0.8)
    for _ in range(20):
        ms = [j for j in P.mapa() if j['classe'] == 'QMenu']
        if ms:
            return ms[-1]
        time.sleep(0.2)
    raise RuntimeError('menu nao abriu: ' + nome)


def itens(nome):
    m = abrir_menu(nome)
    out = [(i['texto'], i['ativo'], i.get('marcado'), i.get('submenu')) for i in m['itens'] if i['classe'] == 'acao_menu']
    fechar_menus()
    return out


def fechar_menus():
    for _ in range(4):
        ms = [j for j in P.mapa() if j['classe'] == 'QMenu']
        if not ms:
            return
        P.tecla(0x1B, ms[-1]['hwnd']); time.sleep(0.3)


def clicar_item(menu, item, print_nome=None):
    m = abrir_menu(menu)
    alvo = [i for i in m['itens'] if i['classe'] == 'acao_menu' and i['texto'] == item][0]
    if print_nome:
        P.printar(print_nome, m['hwnd'])
    P.clicar_em(m['hwnd'], int(alvo['x'] + alvo['w'] / 2), int(alvo['y'] + alvo['h'] / 2))
    time.sleep(1.2)
    return alvo


ATIVA = ("[(w.activeAction().text() if w.activeAction() else None) for w in "
         "QtWidgets.QApplication.topLevelWidgets() if isinstance(w, QtWidgets.QMenu) and w.isVisible()]")


def escolher_item(menu, item, print_nome=None, enter=True):
    """Abre o menu com clique nativo e anda com a seta para baixo ate o item
    ficar aceso; ai aperta Enter (tecla nativa). O mouse simulado nao aciona
    item de menu suspenso do Qt (testado em 02/10), o teclado sim."""
    m = abrir_menu(menu)
    time.sleep(0.5)
    for _ in range(15):
        P.tecla(0x28, m['hwnd']); time.sleep(0.35)
        acesa = P.sonda(ATIVA)
        if f"'{item}'" in acesa:
            break
    else:
        fechar_menus()
        raise RuntimeError(f'nao achei {item} em {menu}: {acesa}')
    if print_nome:
        P.printar(print_nome, m['hwnd'])
    if enter:
        P.tecla(0x0D, m['hwnd']); time.sleep(1.2)
    return m


clicar_item = escolher_item
