"""Mutações da volta 5 do atualizador novo (25/11/2026): cada proteção nova ou consertada desta volta, desligada uma de
cada vez, tem de ser acusada por algum teste (D-811 a D-813, D-827).

Roda NO LUGAR (o primeiro argumento é a pasta do ramo). Cada mutação: troca o trecho (que tem de aparecer uma vez só),
roda os arquivos de teste do atualizador UM POR VEZ (regra de 19/10), na ordem da lista, e para no primeiro que acusa;
devolve o arquivo como estava num `finally` (depois, `git status` tem de estar limpo). "SOBREVIVEU" = nenhum teste
falhou. A primeira linha é a rodada SEM mutação (tem de dar "nenhum teste falhou" em todos).
Uso: python mutacoes_volta5.py <pasta do ramo>
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
PY = r"D:\programas\EditorImpressao\.venv\Scripts\python.exe"
A, W, F = "atualizacao.py", "core/windows.py", "core/fases_da_atualizacao.py"
TESTES = ["tests/test_decisoes_atualizacao_volta5.py", "tests/test_atualizador_volta5.py",
          "tests/test_fases_da_atualizacao.py", "tests/test_atualizador_volta4.py", "tests/test_atualizador_novo.py",
          "tests/test_atualizador_volta2.py", "tests/test_atualizador_volta3.py", "tests/test_decisoes_atualizacao.py",
          "tests/test_atualizador_d851.py", "tests/test_decisoes_ajudante_da_atualizacao.py",
          "tests/test_atualizador_volta3_de_verdade.py", "tests/test_velopack_de_verdade.py"]

MUTACOES = [
    ("V1", "D-868: a frase de antes da janela volta para a fila da janela", A,
     "            if mostrar is None and not isinstance(ef, fases.MostrarFalha):",
     "            if mostrar is None:"),
    ("V2", "a frase da caixa conta como vista mesmo sem o OK", A,
     "        if self._caixa(ef):\n            if not ef.sempre:",
     "        self._caixa(ef)\n        if True:\n            if not ef.sempre:"),
    ("V3", "a frase da caixa não é guardada antes de aparecer (se a caixa não aparece, ou se o programa morre com ela "
           "na tela, a frase se perde)", A,
     "        if not ef.sempre:\n            guardar_frase_pelo_nome(ef.tipo, ef.nome, ef.motivo_da_tela)",
     "        if not ef.sempre:\n            pass"),
    ("V4", "a caixa é chamada sem área de trabalho à vista", W,
     "    if a_vista is not True:\n        return _falhou(",
     "    if a_vista is not True and False:\n        return _falhou("),
    ("V5", "qualquer volta da caixa (não só o OK) conta como 'viu'", W,
     "    if volta == _IDOK:", "    if volta != 0:"),
    ("V6", "a reprovada é testada de novo em toda abertura", F,
     "    if versao == ultima_boa or aprovada or versao in nao_tentar:",
     "    if versao == ultima_boa or aprovada:"),
    ("V7", "a caixa vem antes da reprovação ficar no bilhete", F,
     "        efeitos = [Reprovar(estado.nova, f\"a versão {estado.nova} não passou no teste rápido ({e.detalhe})\")]\n"
     "        efeitos += _frase(reprovada, FALHA_REPROVADA, estado.nova)",
     "        efeitos = _frase(reprovada, FALHA_REPROVADA, estado.nova)\n"
     "        efeitos += [Reprovar(estado.nova, f\"a versão {estado.nova} não passou no teste rápido ({e.detalhe})\")]"),
    ("V8", "a reprovada não para: procura nesta abertura", F,
     "        return replace(reprovada, fase=Fase.PARADO), efeitos + ([Sair(0)] if estado.sem_janela else [])",
     "        if estado.sem_janela:\n            return replace(reprovada, fase=Fase.PARADO), efeitos + [Sair(0)]\n"
     "        return replace(reprovada, fase=Fase.MOTOR), efeitos + [GarantirMotor()]"),
    ("V9", "M1: a frase guardada aparece sempre, verdade ou não", F,
     "        if _frase_guardada_vale(tipo, nome, e.versao):", "        if True:"),
    ("V10", "M1: a frase da reprovada aparece mesmo com uma versão por cima", F,
     "        return not _mais_nova(versao_que_roda, v)", "        return True"),
    ("V11", "M2: a conferência da troca não olha o Update.exe", A,
     "        if not tem_o_atualizador(self.raiz):\n            return fases.TrocaConferida(",
     "        if False:\n            return fases.TrocaConferida("),
    ("V12", "M2: sem o Update.exe, o 'Reiniciar agora' leva à pergunta ao fechar", F,
     "        if e.motivo_da_tela == MOTIVO_SEM_ATUALIZADOR:", "        if False:"),
    ("V13", "M2: a frase própria vira a da D-845 ('Tente ao fechar')", A,
     "        if motivo_da_tela == fases.MOTIVO_SEM_ATUALIZADOR:\n            return FRASE_SEM_ATUALIZADOR\n", ""),
    ("V14", "M2: o motivo do pedido que falha vem do texto, não do disco", A,
     "            motivo_da_tela = fases.MOTIVO_ATUALIZADOR if tem_o_atualizador(self.raiz) else "
     "fases.MOTIVO_SEM_ATUALIZADOR",
     "            motivo_da_tela = fases.MOTIVO_ATUALIZADOR"),
    ("V15", "M5/X11: o 404 do GitHub deixa de ser 'não existe'", A,
     "raise FileNotFoundError(f\"{nome} não está publicado na versão {versao_do_arquivo}\") from erro",
     "raise ConnectionError(f\"{nome} não está publicado na versão {versao_do_arquivo}\") from erro"),
    ("V16", "M5/X18: a assinatura guardada do pacote esperando não é conferida", A,
     "        motivo = assinatura.conferir_versao(texto, assinatura.VersaoAssinada(versao.ID_DO_PACOTE, v, nome, sha256),\n"
     "                                            self._chave)\n        if motivo is not None:\n"
     "            self.evento(fases.Assinatura(False, motivo))",
     "        motivo = None\n        if motivo is not None:\n            self.evento(fases.Assinatura(False, motivo))"),
    ("V17", "a caixa do Windows com outro texto que não o da escolha única", A,
     "        r = self.windows.mostrar_caixa_do_windows(TITULO_DA_FALHA, frase_da_falha(ef.tipo, ef.motivo_da_tela))",
     "        r = self.windows.mostrar_caixa_do_windows(TITULO_DA_FALHA, ef.tipo)"),
    ("V18", "a caixa do Windows com outro título", A,
     "        r = self.windows.mostrar_caixa_do_windows(TITULO_DA_FALHA, frase_da_falha(ef.tipo, ef.motivo_da_tela))",
     "        r = self.windows.mostrar_caixa_do_windows(\"Erro\", frase_da_falha(ef.tipo, ef.motivo_da_tela))"),
    ("V19", "a frase da D-868 com outras palavras", A,
     "FRASE_DA_VERSAO_REPROVADA = \"A versão nova não funcionou. Não desinstale nada. Avise o Samuel.\"",
     "FRASE_DA_VERSAO_REPROVADA = \"A versão nova não funcionou. Avise o Samuel.\""),
    ("V21", "leve 1: o registro da guarda que falha volta a dizer que o teste roda de novo", F,
     "\"boa de antes continua, e a versão não é testada de novo (já está aprovada)\"",
     "\"boa de antes continua; o teste roda de novo na próxima abertura\""),
    ("V22", "leve 2: o pacote esperando volta a dizer 'publicada [...]: baixando'", F,
     "                     \"baixar\" if estado.pendente == estado.nova else",
     "                     \"baixar\" if False else"),
    ("V20", "a frase da reprovada não é mostrada (só reprovada no bilhete)", F,
     "        efeitos += _frase(reprovada, FALHA_REPROVADA, estado.nova)\n", ""),
]


def rodar_os_testes() -> str:
    """Os arquivos um por vez; devolve o primeiro que acusou (ou "nenhum teste falhou")."""
    pasta = RAIZ / "saida_teste" / "v5" / "pytest" / "mutacoes"
    pasta.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(TESTES):
        r = subprocess.run([PY, "-m", "pytest", t, "-q", "-x", "-p", "no:cacheprovider", f"--basetemp={pasta / str(i)}"],
                           cwd=str(RAIZ), capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            linhas = [l for l in r.stdout.splitlines() if l.startswith(("FAILED", "ERROR"))]
            return f"ACUSADA por {t}: {linhas[0] if linhas else r.stdout.splitlines()[-1:]}"
    return "nenhum teste falhou"


def main() -> None:
    saida = [f"SEM MUTACAO: {rodar_os_testes()}"]
    print(saida[-1], flush=True)
    for nome, porque, arq, trecho, troca in MUTACOES:
        caminho = RAIZ / arq
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
    status = subprocess.run(["git", "-C", str(RAIZ), "status", "--short", "--", A, W, F], capture_output=True,
                            text=True).stdout
    saida.append(f"git status dos arquivos mexidos depois: {status.strip() or 'limpo'}")
    Path(__file__).with_name("mutacoes_volta5-resultado.txt").write_text("\n".join(saida) + "\n", encoding="utf-8")
    print(saida[-1])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
