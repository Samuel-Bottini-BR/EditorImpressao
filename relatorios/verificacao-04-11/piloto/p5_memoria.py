"""Verificador 04/11: D-591 (aviso "Faltou memoria no computador..." com "tentar de novo" e
"entendi"). NAO mede memoria (outro agente mede). Livro do acervo: Boecio (50 paginas).
1) processa uma vez (PDF antigo); 2) processa de novo com uma falta de memoria FORCADA na pagina 3
(MemoryError levantado de dentro do processar de verdade, pelo aviso de andamento); o aviso aparece;
apertar "entendi" -> fica na area de trabalho, PDF antigo inteiro; 3) de novo com a falta, apertar
"tentar de novo" -> processa outra vez no mesmo nome e lugar, sem perguntar o destino."""
import hashlib
import time

import comum as C
from comum import anotar, conferir, p

WT = r"D:\programas\EditorImpressao\.claude\worktrees\memoria-pdf"
FALHAR = {"vezes": 0}


def md5(caminho):
    return hashlib.md5(caminho.read_bytes()).hexdigest()[:10] if caminho.exists() else None


def main():
    j, porteiro = C.abrir(WT, "4-memoria-pdf", "Sobre a Consolação da Filosofia - Severino Boécio.pdf")
    import ui.tarefas as T
    from ui.janela_principal import CONFERIR, FINAL
    destino = C.base.TRAB / "saida" / "Boecio.pdf"

    # 1. processar normal
    fim = C.processar(j, destino, nome_print="confirmar-1")
    conferir(fim == FINAL and destino.exists(), "1a vez: processou")
    antigo = md5(destino)
    p(j, "tela-final-1")
    C.base.clique(j, j.tela_final.findChild(type(j.tela_final.botao_montar), None) or j.tela_final.botao_montar) if False else None
    # volta para a area de trabalho pelo "voltar"/menu: abre o livro de novo (continua o projeto)
    j.abrir_livro(j.projeto.caminho_entrada); C.esperar_tela(j)

    # o processar de verdade, com a falta de memoria forcada na pagina 3 enquanto FALHAR > 0
    real = T.processar

    def processar_com_falta(projeto, progresso=None, cancelado=None):
        def prog(f, t, txt):
            if FALHAR["vezes"] > 0 and f >= 3:
                FALHAR["vezes"] -= 1
                raise MemoryError("Unable to allocate 180. MiB for an array (forcado pelo verificador)")
            if progresso:
                progresso(f, t, txt)
        return real(projeto, progresso=prog, cancelado=cancelado)
    T.processar = processar_com_falta

    # 2. falta de memoria -> "entendi"
    FALHAR["vezes"] = 1
    porteiro.escolher = ["substituir o antigo", "entendi"]
    n_caixas = len(porteiro.vistas)
    fim = C.processar(j, destino, nome_print="confirmar-2")
    t0 = time.time()
    while len(porteiro.vistas) == n_caixas and time.time() - t0 < 30:
        C.base.esperar(0.3)
    C.base.esperar(2)
    caixa = next((c for c in porteiro.vistas[n_caixas:] if c["titulo"] == "Um momento"), None)
    anotar("aviso (entendi)", caixa)
    frase = ("Faltou memória no computador: outros programas abertos estão usando quase toda a memória. "
             "Feche o que não estiver usando. Nada do seu trabalho no livro se perdeu.")
    conferir(caixa is not None and caixa["texto"] == frase, "D-591: a frase palavra por palavra")
    conferir(caixa is not None and caixa["botoes"] == ["tentar de novo", "entendi"], f"botoes: {caixa and caixa['botoes']}")
    conferir(j.telas.currentIndex() == CONFERIR, "'entendi': ficou na area de trabalho")
    conferir(md5(destino) == antigo, "o PDF antigo de mesmo nome ficou inteiro")
    sobras = [x.name for x in destino.parent.iterdir() if x.name != destino.name]
    anotar("arquivos na pasta de saida", sobras)
    conferir(not sobras, "nenhum arquivo de trabalho sobrou")
    p(j, "depois-do-entendi")

    # 3. falta de memoria -> "tentar de novo"
    FALHAR["vezes"] = 1
    porteiro.escolher = ["substituir o antigo", "tentar de novo"]
    n_caixas = len(porteiro.vistas)
    mt = destino.stat().st_mtime
    fim = C.processar(j, destino, nome_print="confirmar-3")
    t0 = time.time()
    while time.time() - t0 < 300:
        C.base.esperar(0.5)
        if len(porteiro.vistas) > n_caixas and j.telas.currentIndex() == FINAL:
            break
    C.base.esperar(3)
    anotar("depois do tentar de novo", {"caixas": porteiro.vistas[n_caixas:], "tela": j.telas.currentIndex(),
                                        "pdf mudou": destino.stat().st_mtime != mt,
                                        "caminho_saida": j.projeto.caminho_saida})
    conferir(j.telas.currentIndex() == FINAL, "'tentar de novo': processou de novo ate o fim")
    conferir(destino.exists() and destino.stat().st_mtime != mt, "o PDF novo saiu no mesmo nome e lugar")
    import fitz
    with fitz.open(destino) as d:
        conferir(d.page_count == len([q for q in j.projeto.paginas if not q.apagada]), f"PDF com {d.page_count} paginas")
    sobras = [x.name for x in destino.parent.iterdir() if x.name != destino.name]
    conferir(not sobras, f"nenhum arquivo de trabalho sobrou ({sobras})")
    p(j, "tela-final-depois-do-tentar-de-novo")
    T.processar = real
    C.fechar(j)


if __name__ == "__main__":
    main()
