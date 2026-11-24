"""Prova EXECUTADA (quem tenta quebrar, volta 2): o laço da D-841 ("Reiniciar agora" com outra janela aberta -> a frase
-> o aviso de novo), pela ponte da tela DE VERDADE (janela Qt fora da tela) e o executor e a regra de verdade. As caixas
são de mentira e respondem na hora ("Reiniciar agora" sempre; o "entendi" da frase), como um Kaique que clica sem
fechar a outra janela. Conta quantas vezes o aviso volta até parar, e a profundidade de chamadas a cada volta."""
import json, os, sys, inspect
from pathlib import Path
os.environ["QT_QPA_PLATFORM"] = "offscreen"
R = Path(r"D:\programas\EditorImpressao\rascunho-qtq2\laco")
os.environ["PROGRAMDATA"] = str(R / "pd"); os.environ["LOCALAPPDATA"] = str(R / "local")
(R / "local").mkdir(parents=True, exist_ok=True)
sys.path.insert(0, r"D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo")
from PySide6.QtWidgets import QApplication, QWidget
import atualizacao
from core import fases_da_atualizacao as fases
from ui import aviso_de_atualizacao as aviso
app = QApplication.instance() or QApplication([])
janela = QWidget()
a = atualizacao.Atualizacao(velopack=object(), raiz=R / "raiz", por_tras=lambda f: f(), pasta_grava=lambda r: True,
                            garantir_motor=lambda: True, motor_no_lugar=lambda v: True)
a.conferencia_da_troca = lambda v: fases.TrocaConferida(False, "há outra janela do programa aberta: x", outra_janela=True)
a._estado = fases.Estado(fase=fases.Fase.PRONTA, versao="1.1.0", nova="1.2.0")
voltas, fundo = [], []
def perguntar(*_a, **_k):
    voltas.append(1); fundo.append(len(inspect.stack(0)))
    return len(voltas) < 5000
ponte = aviso.PonteDaTela(janela, a, perguntar=perguntar, avisar=lambda *x, **k: None)
a.ligar_a_tela(ponte.receber)
a._para_a_tela(fases.MostrarVersaoNova("1.2.0"))
reg = atualizacao.caminho_do_registro().read_text(encoding="utf-8").splitlines() if atualizacao.caminho_do_registro().exists() else []
texto = json.dumps({"vezes que o aviso apareceu": len(voltas), "profundidade na 1a, 2a, 10a e última": [fundo[0], fundo[1], fundo[9], fundo[-1]],
                    "fase no fim": a.estado.fase.value,
                    "linhas de erro no registro": [l for l in reg if "erro inesperado" in l][:2]}, ensure_ascii=False, indent=1)
Path(__file__).with_name("prova_laco_d841-resultado.txt").write_text(texto, encoding="utf-8"); print(texto)
