"""SEGUNDA CONFERENCIA: (A) processar ate "Ficou pronto!" no programa novo; (B) abrir no programa
novo um projeto gravado pelo programa da primeira conferencia (36b9e32, sem o campo novo da marcacao).
Uso: q5_processar_e_antigo.py processar | antigo    (o antigo roda com VERIF_DADOS = trabalho/dados_teste)
Guarda o resultado em trabalho/segunda-extra.json (lido pelo segunda.py)."""
import json, sys, time
import fitz
import v
P = v.P
EXTRA = P.BASE / "trabalho" / "segunda-extra.json"
extra = json.loads(EXTRA.read_text(encoding="utf-8")) if EXTRA.exists() else {}
v.fechar(); v.abrir()
if sys.argv[1] == "processar":
    print("reabriu o pedaco do Antiphonal em", v.continuar_projeto("44a49"), "s")
    v.aba("Filtro"); time.sleep(2); v.ir_pagina(3); v.esperar_medida(120); v.esperar_ocioso(120)
    print(v.curto())
    v.clicar("Confirmar e processar", classe="QPushButton", espera=3)
    frase = [it["texto"] for it in P.janela("Antes de processar")["itens"] if it["classe"] == "QLabel"][0]
    print("lista:", frase, v.linhas_da_lista())
    v.foto("r2-processar-1-lista", P.janela("Antes de processar")["hwnd"])
    v.botao_da_caixa("Antes de processar", "continuar assim mesmo", espera=3)
    v.botao_da_caixa("Confirmar e processar", "Processar", espera=1)
    t0 = time.time()
    while time.time() - t0 < 300:
        if v.caixas():
            print("caixa:", v.caixas()[0][0]); v.botao_da_caixa("", "salvar como", parte=True); continue
        if "Final" in v.s("type(jp.telas.currentWidget()).__name__"):
            break
        time.sleep(0.5)
    seg = round(time.time() - t0)
    time.sleep(1.5)
    rotulos = [x[2] for x in v.itens(classes=("QLabel",)) if x[5] > 0]
    print("tela final em", seg, "s:", rotulos[:3]); v.foto("r2-processar-2-ficou-pronto")
    pasta = P.DADOS / "home" / "Editor de Impressão"
    pdf = sorted(pasta.glob("*.pdf"), key=lambda p: p.stat().st_mtime)[-1]
    paginas = len(fitz.open(pdf))
    erros = v.erros_log()
    print("PDF:", pdf.name, paginas, "paginas | erros.log:", repr(erros[-200:]))
    extra["processar_ok"] = bool("Ficou pronto!" in rotulos and paginas == 6 and not erros.strip())
    extra["processar_frase"] = (f"Com aviso pendente, \"continuar assim mesmo\" e \"Processar\": \"Ficou pronto!\" em {seg} s, PDF com {paginas} páginas, erros.log vazio."
                                if extra["processar_ok"] else f"NÃO deu certo: tela {rotulos[:2]}, {paginas} páginas, erros.log {erros[-120:]!r}")
else:
    r = v.continuar_projeto("219a225")
    print("reabriu o Graduale da primeira conferencia em", r, "s;", v.s("(tc.projeto.reforcar_texto_falhado, tc.projeto.misto_fora_do_texto)"))
    print("avisos guardados:", v.s("[(p.indice+1, list(p.alertas)) for p in tc.projeto.paginas if p.alertas]"))
    v.aba("Marcar"); time.sleep(1); v.ir_pagina(3); time.sleep(3)
    a = v.marcado(); time.sleep(25); v.esperar_ocioso(120); b = v.marcado()
    print("p3 na aba Marcar: ao chegar", a, "| 25 s depois", b)
    v.foto("r2-antigo-marcar")
    v.aba("Filtro"); time.sleep(1); v.esperar_medida(120); v.esperar_ocioso(120); print(v.curto())
    erros = v.erros_log()
    print("erros.log:", repr(erros[-300:]))
    igual = eval(a)[:2] == eval(b)[:2]
    extra["antigo_frase"] = (f"abriu em {r} s, as áreas da aba Marcar ficaram como estavam ({eval(a)[0]} áreas ao chegar e 25 segundos depois) e o erros.log ficou vazio."
                             if igual and not erros.strip() else f"ATENÇÃO: ao chegar {a}, depois {b}; erros.log {erros[-120:]!r}.")
EXTRA.write_text(json.dumps(extra, indent=1, ensure_ascii=False), encoding="utf-8")
v.fechar()
