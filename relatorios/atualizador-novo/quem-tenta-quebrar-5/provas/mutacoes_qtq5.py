"""Quem tenta quebrar 5 (25/11/2026): as 22 mutações do escritor (`volta5-provas/mutacoes_volta5.py`, lidas de lá sem
mudar nada) e mais as minhas (Q1 a Q14), cada uma desligando uma proteção, NUMA CÓPIA do commit feita com `git archive`
(o ramo nunca é mexido). Cada mutação: troca o trecho (tem de aparecer uma vez só), roda os arquivos de teste do
atualizador UM POR VEZ e para no primeiro que acusa. "SOBREVIVEU" = nenhum teste falhou.
Uso: python mutacoes_qtq5.py <pasta da cópia>
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

COPIA = Path(sys.argv[1]).resolve()
AQUI = Path(__file__).resolve().parent
ESCRITOR = AQUI.parents[1] / "volta5-provas" / "mutacoes_volta5.py"
ns: dict = {"__name__": "mutacoes_do_escritor"}
sys.argv = [str(ESCRITOR), str(COPIA)]
exec(compile(ESCRITOR.read_text(encoding="utf-8"), str(ESCRITOR), "exec"), ns)
A, W, F, TESTES, PY = ns["A"], ns["W"], ns["F"], ns["TESTES"], ns["PY"]

MINHAS = [
    ("Q1", "a caixa não olha os vistos (a frase já vista aparece de novo a cada abertura)", A,
     "        if isinstance(ef, fases.MostrarFalha) and not ef.sempre and ef.nome in ler_vistos():\n            return\n"
     "        if mostrar is None:",
     "        if mostrar is None:"),
    ("Q2", "o OK da caixa não grava o visto", A,
     "        if self._caixa(ef):\n            if not ef.sempre:\n                gravar_visto(ef.nome)",
     "        if self._caixa(ef):\n            if not ef.sempre:\n                pass"),
    ("Q3", "a peça ignora a bandeira WSF_VISIBLE (toda estação conta como à vista)", W,
     "        return bool(bandeiras.dwFlags & _WSF_VISIBLE)", "        return True"),
    ("Q4", "a caixa é chamada quando não deu para ler a estação (None)", W,
     "    if a_vista is not True:\n        return _falhou(", "    if a_vista is False:\n        return _falhou("),
    ("Q5", "a caixa sem MB_TOPMOST (pode nascer atrás das outras janelas)", W,
     "_MB_OK | _MB_ICONINFORMATION | _MB_SETFOREGROUND | _MB_TOPMOST)", "_MB_OK | _MB_ICONINFORMATION | _MB_SETFOREGROUND)"),
    ("Q6", "a caixa sem MB_SETFOREGROUND", W,
     "_MB_OK | _MB_ICONINFORMATION | _MB_SETFOREGROUND | _MB_TOPMOST)", "_MB_OK | _MB_ICONINFORMATION | _MB_TOPMOST)"),
    ("Q7", "D-769: a frase guardada aparece na reabertura sem janela (uma caixa depois do 'Sim' ao fechar)", F,
     "    if e.frase_guardada and e.frase_guardada[0] in TIPOS_DE_FALHA and not novo.sem_janela:",
     "    if e.frase_guardada and e.frase_guardada[0] in TIPOS_DE_FALHA:"),
    ("Q8", "D-769: a reprovada na reabertura sem janela mostra a caixa em vez de guardar", F,
     "    if estado.sem_janela:\n        return [GuardarFrase(tipo, versao, motivo_da_tela)]\n", ""),
    ("Q9", "a frase da caixa guardada com um nome novo (com a hora): o visto não a reconhece depois", A,
     "            guardar_frase_pelo_nome(ef.tipo, ef.nome, ef.motivo_da_tela)",
     "            guardar_frase(ef.tipo, fases.versao_da_falha(ef.tipo, ef.nome) or ef.nome, ef.motivo_da_tela)"),
    ("Q10", "M2: o motivo do pedido que falha é sempre 'o atualizador sumiu'", A,
     "            motivo_da_tela = fases.MOTIVO_ATUALIZADOR if tem_o_atualizador(self.raiz) else "
     "fases.MOTIVO_SEM_ATUALIZADOR",
     "            motivo_da_tela = fases.MOTIVO_SEM_ATUALIZADOR"),
    ("Q11", "M1: a frase sem versão no nome some (na dúvida, esconde)", F,
     "    v = versao_da_falha(tipo, nome)\n    if not v:\n        return True",
     "    v = versao_da_falha(tipo, nome)\n    if not v:\n        return False"),
    ("Q12", "M1: a frase da troca vale também com a versão IGUAL à que roda (a troca certa)", F,
     "    return _mais_nova(v, versao_que_roda)\n", "    return not _mais_nova(versao_que_roda, v)\n"),
    ("Q13", "a caixa conta como vista quando a volta é zero (o Windows não mostrou)", W,
     "    if volta == 0:\n        return _falhou(", "    if volta == 0:\n        return _certo()\n    if False:\n        return _falhou("),
    ("Q14", "M2 no 'Sim' ao fechar: sem o Update.exe guarda a frase da D-845 ('Tente ao fechar')", A,
     "        if motivo_da_tela == fases.MOTIVO_SEM_ATUALIZADOR:\n            return FRASE_SEM_ATUALIZADOR\n"
     "        return FRASE_NAO_DEU_AGORA",
     "        return FRASE_NAO_DEU_AGORA"),
]


def rodar_os_testes() -> str:
    pasta = COPIA / "saida_teste" / "qtq5-mut"
    pasta.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(TESTES):
        r = subprocess.run([PY, "-m", "pytest", t, "-q", "-x", "-p", "no:cacheprovider", f"--basetemp={pasta / str(i)}"],
                           cwd=str(COPIA), capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            linhas = [l for l in r.stdout.splitlines() if l.startswith(("FAILED", "ERROR"))]
            return f"ACUSADA por {t}: {linhas[0][:200] if linhas else r.stdout.splitlines()[-1:]}"
    return "nenhum teste falhou"


def main() -> None:
    so = sys.argv_extra if hasattr(sys, "argv_extra") else None
    saida = [f"SEM MUTACAO: {rodar_os_testes()}"]
    print(saida[-1], flush=True)
    for nome, porque, arq, trecho, troca in ns["MUTACOES"] + MINHAS:
        caminho = COPIA / arq
        original = caminho.read_bytes()
        texto = original.decode("utf-8").replace("\r\n", "\n")
        if texto.count(trecho) != 1:
            saida.append(f"{nome} ({porque}): ERRO o trecho aparece {texto.count(trecho)} vezes")
            print(saida[-1], flush=True)
            continue
        try:
            caminho.write_bytes(texto.replace(trecho, troca).encode("utf-8"))
            r = rodar_os_testes()
        finally:
            caminho.write_bytes(original)
        saida.append(f"{nome} ({porque}): {'SOBREVIVEU' if r == 'nenhum teste falhou' else r}")
        print(saida[-1], flush=True)
    AQUI.joinpath("mutacoes_qtq5-resultado.txt").write_text("\n".join(saida) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
