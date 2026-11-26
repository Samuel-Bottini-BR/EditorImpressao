"""Quem tenta quebrar 4 (24/11/2026): proteções desligadas uma de cada vez, numa CÓPIA do ramo (D-811, D-827).

A cópia é feita com `git archive` do commit em `saida_teste\\qtq4\\copia` (o ramo nunca é mexido). Para cada mutação:
troca um trecho de um arquivo da cópia (o trecho tem de existir, senão a mutação é "não aplicada"), roda os arquivos de
teste do atualizador UM POR VEZ e para no primeiro que acusar; volta o arquivo como era. "Sobreviveu" = nenhum teste
acusou a proteção desligada. Sem mutação, os arquivos passam na cópia (a linha "SEM MUTACAO").
Uso: python mutacoes_qtq4.py   (saída em mutacoes_qtq4-resultado.txt)
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tarfile
import io
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
COPIA = RAMO / "saida_teste" / "qtq4" / "copia"
TMP = RAMO / "saida_teste" / "qtq4" / "pytest-mut"
PY = r"D:\programas\EditorImpressao\.venv\Scripts\python.exe"
COMMIT = "5dfcdc9d"
ARQUIVOS = ["tests/test_atualizador_volta4.py", "tests/test_fases_da_atualizacao.py", "tests/test_atualizador_volta3.py",
            "tests/test_atualizador_novo.py", "tests/test_atualizador_volta2.py", "tests/test_atualizador_d851.py",
            "tests/test_atualizador_volta3_de_verdade.py", "tests/test_decisoes_atualizacao.py",
            "tests/test_decisoes_ajudante_da_atualizacao.py", "tests/test_velopack_de_verdade.py"]

F = "core/fases_da_atualizacao.py"
A = "atualizacao.py"
MUTACOES = [
    # (nome, o que desliga, arquivo, trecho de hoje, trecho desligado)
    ("X1", "a marca de aprovada não é olhada (D-856)", F,
     "if e.versao == e.ultima_boa or e.aprovada or e.sem_volta:", "if e.versao == e.ultima_boa or e.sem_volta:"),
    ("X2", "a marca de sem volta não é olhada (D-863)", F,
     "if e.versao == e.ultima_boa or e.aprovada or e.sem_volta:", "if e.versao == e.ultima_boa or e.aprovada:"),
    ("X3", "a reabertura com --voltando não põe a marca de sem volta", F,
     "f\"{e.versao}): não tento de novo\"), MarcarSemVolta(e.versao)]", "f\"{e.versao}): não tento de novo\")]"),
    ("X4", "a volta que não deu não põe a marca de sem volta", F,
     "efeitos: list[Efeito] = [Registrar(motivo), MarcarSemVolta(estado.nova)] + _frase(",
     "efeitos: list[Efeito] = [Registrar(motivo)] + _frase("),
    ("X5", "a primeira versão do .msi também é testada (D-857)", F,
     "return bool(e.ultima_boa) or e.pacote_da_versao", "return True"),
    ("X6", "a marca de aprovada não é posta quando passa", F,
     "MarcarAprovada(estado.nova), GuardarUltimaBoa(estado.nova", "GuardarUltimaBoa(estado.nova"),
    ("X7", "a marca de aprovada DEPOIS da guarda (D-856: antes)", F,
     "MarcarAprovada(estado.nova), GuardarUltimaBoa(estado.nova, por_tras=not estado.sem_janela)]",
     "GuardarUltimaBoa(estado.nova, por_tras=not estado.sem_janela), MarcarAprovada(estado.nova)]"),
    ("X8", "o executor não grava a marca (o efeito vira nada)", A,
     "            marcar(self.raiz, MARCA_APROVADA, ef.versao)", "            pass"),
    ("X9", "sem rede na assinatura volta a ser 'recusada' (a frase 2)", F,
     "        if e.sem_rede:\n", "        if False:\n"),
    ("X10", "o executor não diz 'sem rede' (OSError vira recusada)", A,
     "self.evento(fases.Assinatura(False, str(erro) or type(erro).__name__, sem_rede=True))",
     "self.evento(fases.Assinatura(False, str(erro) or type(erro).__name__))"),
    ("X11", "o 404 do GitHub deixa de ser 'não existe'", A,
     "raise FileNotFoundError(f\"{nome} não está publicado na versão {versao_do_arquivo}\") from erro",
     "raise ConnectionError(f\"{nome} não está publicado na versão {versao_do_arquivo}\") from erro"),
    ("X12", "a fonte de pasta que não existe vira 'não existe' (frase 2) em vez de 'sem rede'", A,
     "raise ConnectionError(f\"a fonte {self.endereco} não está acessível\")",
     "raise FileNotFoundError(f\"a fonte {self.endereco} não está acessível\")"),
    ("X13", "o 'Sim' ao fechar que não troca não guarda a frase (D-858)", F,
     "            return replace(estado, fase=Fase.PARADO), efeitos + [GuardarFrase(NAO_DEU_AGORA, estado.nova,\n"
     "                                                                              motivo_da_tela)]",
     "            return replace(estado, fase=Fase.PARADO), efeitos"),
    ("X14", "o motivo da outra janela no 'Sim' ao fechar vira o da D-840 (D-864)", F,
     "motivo_da_tela = MOTIVO_HAVIA_OUTRA_JANELA if e.outra_janela else",
     "motivo_da_tela = MOTIVO_OUTRA_JANELA if e.outra_janela else"),
    ("X15", "o texto da D-864 trocado", A,
     "fases.MOTIVO_HAVIA_OUTRA_JANELA: \"havia outra janela do programa aberta\"",
     "fases.MOTIVO_HAVIA_OUTRA_JANELA: \"o programa estava aberto em outra janela\""),
    ("X16", "sem internet, o pacote esperando não é oferecido (D-859)", F,
     "            if estado.pendente and _mais_nova(estado.pendente, estado.versao) and \\",
     "            if False and estado.pendente and _mais_nova(estado.pendente, estado.versao) and \\"),
    ("X17", "o pacote esperando reprovado é oferecido de novo", F,
     "                    estado.pendente not in estado.nao_tentar:", "                    True:"),
    ("X18", "a assinatura guardada do pacote esperando não é conferida", A,
     "        motivo = assinatura.conferir_versao(texto, assinatura.VersaoAssinada(versao.ID_DO_PACOTE, v, nome, sha256),\n"
     "                                            self._chave)\n        if motivo is not None:\n"
     "            self.evento(fases.Assinatura(False, motivo))",
     "        motivo = None\n        if motivo is not None:\n            self.evento(fases.Assinatura(False, motivo))"),
    ("X19", "a guarda não confere o espaço (D-856)", A,
     "        if not cabe:\n            return (f\"falta espaço", "        if False:\n            return (f\"falta espaço"),
    ("X20", "a volta sem a marca --voltando (a do G1)", A,
     "argumentos = ([ARG_VOLTANDO, de, para] if volta else", "argumentos = ([] if volta else"),
    ("X21", "a abertura não lê o --voltando", A,
     "        voltando = ARG_VOLTANDO in argumentos\n", "        voltando = False\n"),
    ("X22", "a reabertura com --voltando que DEU CERTO também vira 'não conseguiu voltar'", F,
     "    if e.reaberto_voltando and e.reaberto_de and e.versao == e.reaberto_de:",
     "    if e.reaberto_voltando and e.reaberto_de:"),
    ("X23", "a reabertura com --voltando testa de novo (sem o desvio dela)", F,
     "    if e.reaberto_voltando and e.reaberto_de and e.versao == e.reaberto_de:",
     "    if False:"),
    ("X24", "sem última boa, o teste que falha não mostra a frase (3) (D-857)", F,
     "    efeitos: list[Efeito] = [Registrar(motivo), MarcarSemVolta(estado.nova)] + _frase(estado, FALHA_VOLTA, estado.nova)",
     "    efeitos: list[Efeito] = [Registrar(motivo), MarcarSemVolta(estado.nova)]"),
    ("X25", "a guarda tenta baixar sem o pacote em packages (o download da D-851)", A,
     "    if not origem.is_file():\n        return f\"o pacote da {versao_boa} não está em",
     "    if not origem.is_file() and False:\n        return f\"o pacote da {versao_boa} não está em"),
    ("X26", "Q1: a guarda apaga também a assinatura da versão mais nova que chega", A,
     "        if v and (v == versao_boa or fases._mais_nova(v, versao_boa)):",
     "        if v and v == versao_boa:"),
    ("X27", "Q2: a última boa escolhida é a mais velha", A,
     "    return max(achadas, key=fases._numeros) if achadas else \"\"",
     "    return min(achadas, key=fases._numeros) if achadas else \"\""),
    ("X28", "Q9: a frase guardada sem a hora no nome", A,
     "    nome = f\"{fases.id_da_falha(tipo, versao_da_frase)}-{_agora()}\"",
     "    nome = f\"{fases.id_da_falha(tipo, versao_da_frase)}\""),
    ("X29", "Q13: a cópia com a soma errada não apaga o .chegando", A,
     "        if assinatura.soma_sha256(origem, copiar_para=chegando) != soma_assinada:\n            chegando.unlink(missing_ok=True)",
     "        if assinatura.soma_sha256(origem, copiar_para=chegando) != soma_assinada:\n            pass"),
    ("X30", "o 'Sim' ao fechar com o pacote trocado guarda a frase com motivo em vez da (2) (D-848)", F,
     "            if e.recusada:\n                return replace(estado, fase=Fase.PARADO), efeitos + [GuardarFrase(FALHA_RECUSADA, estado.nova)]",
     "            if False:\n                return replace(estado, fase=Fase.PARADO), efeitos + [GuardarFrase(FALHA_RECUSADA, estado.nova)]"),
]


def copiar() -> None:
    if COPIA.exists():
        shutil.rmtree(COPIA)
    COPIA.mkdir(parents=True)
    dados = subprocess.run(["git", "-C", str(RAMO), "archive", COMMIT], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(dados)) as t:
        t.extractall(COPIA, filter="data")


def rodar_testes(rotulo: str) -> str:
    (TMP / rotulo).mkdir(parents=True, exist_ok=True)      # o pytest cria a pasta dele, mas não a de cima
    for i, arquivo in enumerate(ARQUIVOS):
        r = subprocess.run([PY, "-m", "pytest", arquivo, "-q", "-x", "-p", "no:cacheprovider",
                            f"--basetemp={TMP / rotulo / str(i)}"], cwd=str(COPIA), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            falhou = [l for l in r.stdout.splitlines() if l.startswith("FAILED") or l.startswith("ERROR")]
            return f"ACUSADA por {arquivo}: {falhou[0] if falhou else r.stdout.splitlines()[-1:]}"
    return "SOBREVIVEU (nenhum dos arquivos acusou)"


def main() -> None:
    copiar()
    linhas = [f"cópia de {COMMIT} em {COPIA}", "SEM MUTACAO: " + rodar_testes("base")]
    print(linhas[-1], flush=True)
    for nome, o_que, arquivo, de, para in MUTACOES:
        caminho = COPIA / arquivo
        original = caminho.read_text(encoding="utf-8")
        if original.count(de) != 1:
            linhas.append(f"{nome} ({o_que}): NÃO APLICADA (o trecho aparece {original.count(de)} vezes)")
        else:
            caminho.write_text(original.replace(de, para), encoding="utf-8")
            try:
                linhas.append(f"{nome} ({o_que}): " + rodar_testes(nome))
            finally:
                caminho.write_text(original, encoding="utf-8")
        print(linhas[-1], flush=True)
    Path(__file__).with_name("mutacoes_qtq4-resultado.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
