"""Etapa 2, item 2: o programa EMPACOTADO abre um livro novo e trabalha, pelo caminho inteiro.

Área escondida do Windows (lancar.py), pasta de dados nova e própria, a pasta de saída já apontada para
uma pasta minha (configuracoes.json, "ultima_pasta_de_saida": senão a sugestão seria Documentos\\Editor de
Impressão). Livro: cópia das folhas 21 a 30 do Righetti, já de pé (duas páginas por folha, borda preta).

Passos, como o Kaique: abrir o PDF (o .exe recebe o caminho, como no "abrir com" do Windows), na tela do
livro aberto apertar "Rodar o automático...", marcar Dividir, Endireitar, Cortar e Limpar (o resto
desmarcado), "Rodar", ir à área de trabalho ("Continuar"), "Confirmar e processar", "Processar", esperar
"Ficou pronto!", fechar (WM_CLOSE). Prints e a lista do que o leitor de tela vê em cada passo.

Uso: python item2_novo.py <exe> <pasta de trabalho do item 2> <pdf>
"""
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import piloto_uia as P

exe, trab, pdf = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
prints = trab / "prints"
(trab / "saida").mkdir(parents=True, exist_ok=True)
cfg = trab / "dados" / "EditorImpressao" / "configuracoes.json"
cfg.parent.mkdir(parents=True, exist_ok=True)
cfg.write_text(json.dumps({"ultima_pasta_de_saida": str(trab / "saida")}, ensure_ascii=False), encoding="utf-8")
P.abrir_log(trab / "anotacoes.txt")
ETAPAS = ("Dividir folhas ao meio", "Endireitar folhas tortas", "Cortar as bordas", "Limpar a folha")
t0 = time.time()
proc = P.lancar_exe(exe, trab / "dados", trab / "temp", [pdf])
w = None
try:
    w = P.janela_principal(proc.pid)
    P.anotar("janela apareceu", round(time.time() - t0, 1))
    rodar = P.achar(w, "Rodar o automático", "Button", contem=True, limite=180)
    P.anotar("livro aberto", round(time.time() - t0, 1))
    time.sleep(3)
    P.print_janela(w, prints / "i01-livro-aberto.png")
    rodar.invoke()
    time.sleep(3)
    auto = P.esperar_janela(proc.pid, "Automático", limite=20)
    alvo = auto if auto is not None else w
    P.print_janela(alvo, prints / "i02-automatico-antes.png")
    P.descrever(alvo, prints / "i02-automatico-antes.txt")
    for e in alvo.descendants(control_type="CheckBox"):
        nome = e.element_info.name or ""
        if not e.is_visible():
            continue
        quer = any(nome.startswith(x) for x in ETAPAS)
        try:
            ligada = e.get_toggle_state() == 1
        except Exception:
            ligada = None
        if nome.split(" —")[0] in ("Dividir folhas ao meio", "Endireitar folhas tortas", "Cortar as bordas",
                                   "Limpar a folha", "Gravuras e fotos", "Margens iguais", "Montar cadernos"):
            if ligada is not None and ligada != quer:
                e.toggle()
                time.sleep(0.4)
            P.anotar("caixinha", [nome, "era", ligada, "ficou", e.get_toggle_state()])
    time.sleep(1)
    P.print_janela(alvo, prints / "i03-automatico-marcado.png")
    P.descrever(alvo, prints / "i03-automatico-marcado.txt")
    botao = P.achar(alvo, "Rodar ", "Button", contem=True, limite=10)
    P.anotar("botão", botao.element_info.name)
    t1 = time.time()
    botao.invoke()
    time.sleep(4)
    # espera a medida do Automático acabar (a tela de andamento some e a janela volta)
    fim = time.time() + 900
    while time.time() < fim:
        try:
            P.achar(w, "Continuar", "Button", limite=2)
            break
        except Exception:
            pass
        try:
            P.achar(w, "Confirmar e processar", "Button", limite=2)
            break
        except Exception:
            pass
    P.anotar("automático rodou", round(time.time() - t1, 1))
    time.sleep(5)
    P.descrever_tudo(proc.pid, prints, "i04-depois-do-rodar")
    for x in reversed(P.janelas_do_processo(proc.pid)):
        if x.window_text() == "Automático":
            try:
                P.apertar(x, "Fechar")
            except Exception:
                pass
    try:
        P.apertar(w, "Continuar", limite=5)
    except Exception:
        pass
    botao = P.achar(w, "Confirmar e processar", "Button", limite=120)
    time.sleep(15)
    P.print_janela(w, prints / "i05-area-de-trabalho.png")
    P.descrever(w, prints / "i05-area-de-trabalho.txt")
    botao.invoke()
    time.sleep(3)
    aviso = P.esperar_janela(proc.pid, "Antes de processar", limite=10)
    if aviso is not None:
        P.print_janela(aviso, prints / "i06-antes-de-processar.png")
        P.apertar(aviso, "continuar assim mesmo")
        time.sleep(2)
    conf = None
    for x in reversed(P.janelas_do_processo(proc.pid)):
        try:
            P.achar(x, "Processar", "Button", limite=2)
            conf = x
            break
        except Exception:
            pass
    P.print_janela(conf, prints / "i07-confirmar.png")
    P.apertar(conf, "Processar")
    t2 = time.time()
    P.achar(w, "Ficou pronto!", "Text", limite=1800)
    P.anotar("processou", round(time.time() - t2, 1))
    time.sleep(2)
    P.print_janela(w, prints / "i08-pronto.png")
    P.descrever(w, prints / "i08-pronto.txt")
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
