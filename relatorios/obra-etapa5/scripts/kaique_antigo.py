"""Reversao do teste do Kaique no CODIGO ANTIGO (7fb3e4a): corte a mao, folha do tamanho do
corte, 'Mover conteudo' das Bordas e arrastar 10% para a esquerda -> medir o PDF."""
import sys, copy, uuid
from pathlib import Path
raiz = Path(sys.argv[1]).resolve(); sys.path.insert(0, str(raiz))
import tests.test_decisoes_mover as T   # as mesmas paginas e medidas da prova nova
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPoint
app = QApplication([])
import projetos
d = Path(sys.argv[2]) / uuid.uuid4().hex[:6]; (d / "proj").mkdir(parents=True)
projetos.pasta_dos_projetos = lambda: d / "proj"
from ui.janela_principal import JanelaPrincipal
j = JanelaPrincipal(); j.resize(1280, 657)
j.abrir_livro(T._pdf(d / "livro.pdf")); j.show()
tela = j.tela_conferir
tela.escolher_ferramenta("cortar")
tela._mover_recorte((0.04, 0.04, 0.92, 0.92))
tela._mudar_tamanho_da_folha((round(T.LARGURA * 0.92 / T.DPI * 2.54, 2), round(T.ALTURA * 0.92 / T.DPI * 2.54, 2)))
vis = tela.visualizadores["bordas"]
T._esperar(lambda: vis._pixmap is not None)
antes = T._caixa_da_tinta(T._gerar(j, d, "antes")[0])
tela.botao_mover_conteudo.setChecked(True); tela._alternar_mover_conteudo()
T._esperar(lambda: vis._pixmap is not None); T._assentar(10); vis.grab()
c = vis._area.center()
T._arrastar(vis, c, QPoint(c.x() - int(vis._area.width() * 0.10), c.y()))
depois = T._caixa_da_tinta(T._gerar(j, d, "depois")[0])
print("caixa do texto no PDF antes :", [round(v, 3) for v in antes])
print("caixa do texto no PDF depois:", [round(v, 3) for v in depois])
print("deslocamento gravado:", j.projeto.paginas[0].conteudo_deslocamento)
print("ANDOU" if depois[0] < antes[0] - 0.05 else "NAO ANDOU (o defeito do teste do Kaique)")
j.previas.parar(); j.close()
