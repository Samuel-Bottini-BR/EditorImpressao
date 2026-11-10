import time
import piloto as P


def caixas_abertas(espera=2.0):
    fim = time.time() + espera
    while time.time() < fim:
        cx = [j for j in P.mapa() if j['classe'] in ('QMessageBox',)]
        if cx:
            return cx
        time.sleep(0.3)
    return []


def fechar_caixa(cx):
    for nome in ('entendi', 'OK', 'Ok', 'fechar'):
        try:
            P.clicar(nome, titulo=cx['titulo'], espera=1)
            return
        except LookupError:
            pass
    P.tecla(0x1B, cx['hwnd']); time.sleep(1)
