"""Rola a coluna da tela da vez até o fim (arrasto nativo na barra) e, se pedido, clica na caixinha com esse texto."""
import sys, time
import v
P = v.P
q = ('(lambda d: [(sb.mapTo(jp, sb.rect().topLeft()).x()*d, sb.mapTo(jp, sb.rect().topLeft()).y()*d, sb.width()*d, sb.height()*d, '
     'sb.value(), sb.maximum(), sb.pageStep()) for sb in jp.findChildren(QtWidgets.QScrollBar) if sb.isVisible() and '
     'sb.orientation()==__import__("PySide6.QtCore").QtCore.Qt.Vertical])(jp.devicePixelRatioF())')
barras = eval(v.s(q))
if barras:
    x, y, w, h, val, mx, pg = barras[0]
    comp = max(h * pg / (mx + pg), 20)
    de = y + (h - comp) * (val / mx if mx else 0) + comp / 2
    P.arrastar_em(P.principal(), int(x + w / 2), int(de), int(x + w / 2), int(y + h - comp / 2 - 2), passos=20)
    time.sleep(1.5)
if len(sys.argv) > 1 and sys.argv[1]:
    it = [i for i in v.itens(classes=("QCheckBox",)) if i[2].startswith(sys.argv[1])][0]
    P.clicar_em(P.principal(), it[5] + 12, it[6] + it[8] // 2); time.sleep(1.5)
    print("marcada:", [i[4] for i in v.itens(classes=("QCheckBox",)) if i[2].startswith(sys.argv[1])])
if len(sys.argv) > 2:
    print(v.foto(sys.argv[2]))
