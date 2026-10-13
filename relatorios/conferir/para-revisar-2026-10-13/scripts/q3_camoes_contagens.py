"""SEGUNDA CONFERENCIA: Camoes inteiro (forca sozinha, as tres contagens, a frase nova) e o ponto 6 no Egenloff 3."""
import time, v
from livros import LIVROS
P = v.P
v.fechar(); v.abrir()
print("Camoes abriu em", v.novo_livro(LIVROS["camoes"]), "s")
for n in (27, 104, 11, 66):
    v.ir_pagina(n); t = v.esperar_medida(180); o = v.esperar_ocioso(180); time.sleep(2)
    print(f"p{n}: medida {t} s, ocioso {o} s |", v.curto())
    if n == 27:
        print("   faixa:", v.faixa(), "medidor:", v.s("tc.medidor.valor")); v.foto("r2-camoes-27")
print("PAINEL:", v.painel()[0], "| contador de cima:", v.s("tc.botao_alertas.text()"))
print("  avisos de pagina:", v.s("dict(__import__('collections').Counter(a for p in tc.projeto.paginas for a in p.alertas_pendentes))"))
print("  avisos de folha:", v.s("dict(__import__('collections').Counter(a for f in tc.projeto.folhas for a in f.alertas_pendentes))"))
print("  paginas sem 'esta certo':", v.s("sum(1 for p in tc.projeto.paginas_ativas if not p.revisada)"), "| paginas com aviso pendente:", v.s("sum(1 for p in tc.projeto.paginas_ativas if p.alertas_pendentes)"))
print("  foto:", v.foto("r2-contagens-1-painel")[0][-40:])
v.clicar("Confirmar e processar", classe="QPushButton", espera=3)
j = P.janela("Antes de processar")
print("LISTA:", [it["texto"] for it in j["itens"] if it["classe"] == "QLabel"][0], "| linhas:", len(v.linhas_da_lista()))
print("  foto:", v.foto("r2-contagens-2-lista", j["hwnd"])[0][-40:])
v.botao_da_caixa("Antes de processar", "continuar assim mesmo", espera=3)
j = P.janela("Confirmar e processar")
print("JANELA DE SALVAR:", [it["texto"] for it in j["itens"] if it["classe"] == "QLabel" and ("confer" in it["texto"] or "vão para" in it["texto"])])
print("  foto:", v.foto("r2-contagens-3-salvar", j["hwnd"])[0][-40:])
v.botao_da_caixa("Confirmar e processar", "voltar", espera=2)
print("depois do voltar:", [c[0] for c in v.caixas()], v.s("type(jp.telas.currentWidget()).__name__"))
print("erros.log:", repr(v.erros_log()[-300:]))
# ponto 6: Egenloff 3, "usar mais escuro" e depois
v.fechar(); v.abrir()
print("Egenloff 1-14 reabriu em", v.continuar_projeto("1a14"), "s")
v.aba("Filtro"); time.sleep(2); v.ir_pagina(3); v.esperar_medida(180); v.esperar_ocioso(180); time.sleep(2)
print("PONTO 6, Egenloff 3 antes:", v.curto())
v.clicar("usar mais escuro", classe="QPushButton", espera=3); v.esperar_medida(180); v.esperar_ocioso(180); time.sleep(3)
print("  depois de 'usar mais escuro':", v.curto()); print("  faixa:", v.faixa(), "medidor:", v.s("tc.medidor.valor"))
print("  foto:", v.foto("r2-egenloff-3-forca-85")[0][-40:])
v.ctrl_z(); v.fechar()
