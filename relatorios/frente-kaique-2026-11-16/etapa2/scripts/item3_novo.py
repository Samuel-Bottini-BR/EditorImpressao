"""Etapa 2, item 3: o projeto feito pelo programa de 28/10 aberto no programa EMPACOTADO de hoje.

Área escondida do Windows (lancar.py); pasta de dados = cópia da pasta de dados do programa de 28/10
(novo3\\dados). Passos, como o Kaique faria: clica no cartão do livro na tela "Seus livros", espera a
área de trabalho, aperta "Confirmar e processar", segue os avisos ("continuar assim mesmo"), aperta
"Processar"; se já existir o PDF de antes, escolhe "salvar como ... (2)" (o de antes fica intacto);
espera "Ficou pronto!", e fecha a janela (WM_CLOSE).

Uso: python item3_novo.py <exe> <pasta de trabalho do item 3>
"""
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import piloto_uia as P

exe, trab = Path(sys.argv[1]), Path(sys.argv[2])
prints = trab / "prints"
P.abrir_log(trab / "anotacoes.txt")
proc = P.lancar_exe(exe, trab / "dados", trab / "temp")
w = None
try:
    t0 = time.time()
    w = P.janela_principal(proc.pid)
    P.achar(w, "righetti-14-folhas", "Text", limite=60)
    P.anotar("tela dos livros", round(time.time() - t0, 1))
    P.print_janela(w, prints / "n01-seus-livros.png")
    cartao = P.achar(w, "righetti-14-folhas", "Text")
    P.clicar(w, cartao)
    t1 = time.time()
    # a tela do livro aberto (como o UPDF): "Continuar" leva à área de trabalho
    continuar = P.achar(w, "Continuar", "Button", limite=180)
    time.sleep(3)
    P.anotar("abriu o livro", round(time.time() - t1, 1))
    P.print_janela(w, prints / "n02-livro-aberto.png")
    continuar.invoke()
    t1 = time.time()
    botao = P.achar(w, "Confirmar e processar", "Button", limite=180)
    time.sleep(12)          # as prévias chegam
    P.anotar("área de trabalho", round(time.time() - t1, 1))
    P.print_janela(w, prints / "n02b-area-de-trabalho.png")
    P.descrever(w, prints / "n02b-area-de-trabalho.txt")
    botao.invoke()
    time.sleep(3)
    P.descrever_tudo(proc.pid, prints, "n03-depois-de-confirmar")
    aviso = P.esperar_janela(proc.pid, "Antes de processar", limite=10)
    if aviso is not None:
        P.apertar(aviso, "continuar assim mesmo")
        time.sleep(2)
        P.descrever_tudo(proc.pid, prints, "n04-depois-dos-avisos")
    conf = None
    for x in reversed(P.janelas_do_processo(proc.pid)):
        try:
            P.achar(x, "Processar", "Button", limite=2)
            conf = x
            break
        except Exception:
            pass
    if conf is None:
        raise RuntimeError("não achei a janela com o botão Processar")
    P.print_janela(conf, prints / "n05-confirmar.png")
    P.apertar(conf, "Processar")
    time.sleep(2)
    for x in reversed(P.janelas_do_processo(proc.pid)):
        if "Já existe" in (x.window_text() or ""):
            P.print_janela(x, prints / "n06-ja-existe.png")
            P.apertar(x, "salvar como", contem=True)
    t2 = time.time()
    P.achar(w, "Ficou pronto!", "Text", limite=1800)
    P.anotar("processou", round(time.time() - t2, 1))
    time.sleep(2)
    P.print_janela(w, prints / "n07-pronto.png")
    P.descrever(w, prints / "n07-pronto.txt")
except Exception:
    P.anotar("ERRO", traceback.format_exc())
    try:
        P.descrever_tudo(proc.pid, prints, "erro")
    except Exception:
        pass
finally:
    if w is not None:
        P.fechar(w)
    try:
        proc.wait(60)
    except Exception:
        proc.kill()
        P.anotar("tive de encerrar o processo que eu abri")
    P.anotar("saiu", proc.returncode)
