"""Prova: o Automatico e o "nao dividir esta" deixam a folha nao dividida de jeitos diferentes."""
import sys
sys.path.insert(0, sys.argv[1])
from modelos import Projeto, ConfigFolha, ConfigPagina
from core import automatico as A
from core import dividir_a_mao as D
from historico_acoes import montar_acao, aplicar

def livro():
    p = Projeto(caminho_entrada="x.pdf")
    p.folhas = [ConfigFolha(indice=0, dividir=True, posicao_corte=0.5)]
    p.paginas = [ConfigPagina(indice=0, folha=0, metade="esquerda"),
                 ConfigPagina(indice=1, folha=0, metade="direita")]
    return p

# 1) "nao dividir esta" (o caminho da tela)
p = livro()
campos = D.campos_para_juntar(p, 0)
acao = montar_acao(p, "nao_dividir", "folha", [0], campos, "x")
aplicar(p, acao, acao.depois)
print("A MAO :", len(p.paginas), "paginas na lista;", [(q.metade, q.apagada) for q in p.paginas],
      "; ativas:", len(p.paginas_ativas))

# 2) o Automatico mede a folha como de uma pagina so
p = livro()
m = A.MedidaDaFolha(indice=0, dividir=False, posicao_corte=0.5, confianca_corte=0.9,
                    e_paisagem=False, sobra=None, angulo_detectado=0.0, confianca_angulo=1.0,
                    alertas=[], partes=[])
g = A._Gravador(p)
A._dividir(p, A.Pedido(etapas=[A.DIVIDIR]), {0: m}, A._Puladas(p, []), g)
print("AUTO  :", len(p.paginas), "paginas na lista;", [(q.metade, q.apagada) for q in p.paginas],
      "; ativas:", len(p.paginas_ativas))
