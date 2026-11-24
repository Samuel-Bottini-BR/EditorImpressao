"""Mutações do terceiro "quem tenta quebrar" (24/11/2026; D-811, D-827): proteções que EU escolhi, desligadas uma de
cada vez numa CÓPIA do ramo (feita com `git archive` em `saida_teste\\qtq3\\copia`; o ramo de verdade nunca é mexido).

Para cada uma: troca o trecho (tem de aparecer uma vez só), roda os arquivos de teste do atualizador UM POR VEZ (para
no primeiro que falha) e devolve o arquivo. "SOBREVIVEU" = nenhum arquivo falhou. Antes de tudo, a conferência sem
mutação: os mesmos arquivos passam na cópia (sem isso "acusada" não quer dizer nada). Fica de fora só o
`test_trava_windows.py` (precisa do git do ramo, que a cópia não tem; nenhuma mutação aqui é da trava).
Uso: python mutacoes_qtq3.py <pasta da cópia>
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

COPIA = Path(sys.argv[1]).resolve()
PY = sys.executable
A, F = "atualizacao.py", "core/fases_da_atualizacao.py"
TESTES = ["tests/test_atualizador_volta3.py", "tests/test_atualizador_d851.py", "tests/test_fases_da_atualizacao.py",
          "tests/test_atualizador_novo.py", "tests/test_atualizador_volta2.py", "tests/test_decisoes_atualizacao.py",
          "tests/test_atualizador_volta3_de_verdade.py", "tests/test_decisoes_ajudante_da_atualizacao.py",
          "tests/test_decisoes_preparo_d749.py", "tests/test_velopack_de_verdade.py",
          "tests/test_windows_preparo_do_computador.py", "tests/test_decisoes_testes_a_distancia.py"]

MUTACOES = [
    ("Q1 a guarda apaga também a assinatura da versão mais nova que está chegando", A,
     "        if outro.name.endswith(\".assinatura\") and fases._mais_nova(_versao_do_nome(outro.name), versao_boa):\n"
     "            continue",
     "        if False:\n            continue"),
    ("Q2 a última boa é a MAIS VELHA da pasta", A,
     "    return max(achadas, key=fases._numeros) if achadas else \"\"",
     "    return min(achadas, key=fases._numeros) if achadas else \"\""),
    ("Q3 a volta não confere a assinatura guardada", A,
     "        motivo = assinatura.conferir_versao(texto, assinatura.VersaoAssinada(pacote, ef.para, nome, sha256),\n"
     "                                            self._chave)\n",
     "        motivo = None\n"),
    ("Q4 D-839: a frase da troca recusada aparece também quando a troca deu certo", F,
     "    if e.reaberto_para and e.versao == e.reaberto_de and _mais_nova(e.reaberto_para, e.versao):",
     "    if e.reaberto_para and _mais_nova(e.reaberto_para, e.reaberto_de):"),
    ("Q5 a frase guardada é 'mostrada' na reabertura sem janela (e marcada vista sem ninguém ver)", F,
     "    if e.frase_guardada and e.frase_guardada[0] in TIPOS_DE_FALHA and not novo.sem_janela:",
     "    if e.frase_guardada and e.frase_guardada[0] in TIPOS_DE_FALHA:"),
    ("Q6 a reabertura pelo Velopack também pergunta se o atualizador roda (e sai, se ele ainda estiver saindo)", A,
     "        if not fora and ARG_CONFERIR_NOVA not in argumentos and (pendente or (ultima and versao.VERSAO != ultima)):",
     "        if not fora and (pendente or (ultima and versao.VERSAO != ultima)):"),
    ("Q7 D-848: a frase 2 no 'Reiniciar agora' só aparece uma vez (o segundo clique fica sem resposta)", F,
     "                MostrarFalha(FALHA_RECUSADA, id_da_falha(FALHA_RECUSADA, estado.nova), sempre=True)]",
     "                MostrarFalha(FALHA_RECUSADA, id_da_falha(FALHA_RECUSADA, estado.nova))]"),
    ("Q8 a versão sem assinatura conferida nesta abertura pode ser trocada", A,
     "        if not assinada:\n",
     "        if False:\n"),
    ("Q9 a frase guardada sem a hora no nome (a mesma frase noutro dia não aparece)", A,
     "    nome = f\"{fases.id_da_falha(tipo, versao_da_frase)}-{_agora()}\"",
     "    nome = f\"{fases.id_da_falha(tipo, versao_da_frase)}\""),
    ("Q10 D-719: a frase de abertura aparece em toda abertura (não uma vez)", A,
     "            if ef.nome in ler_vistos():\n                return\n",
     "            if False:\n                return\n"),
    ("Q11 D-840: com outra janela aberta, a frase da D-845 no lugar da D-840", A,
     "        if motivo_da_tela == fases.MOTIVO_OUTRA_JANELA:\n            return FRASE_DA_OUTRA_JANELA\n",
     "        if False:\n            return FRASE_DA_OUTRA_JANELA\n"),
    ("Q12 a janela que não fechou fica sem frase (clique sem resposta)", F,
     "        return replace(estado, fase=Fase.DEPOIS), [\n"
     "            Registrar(\"\\\"Reiniciar agora\\\": a janela não fechou; nada foi trocado (a pergunta vem ao fechar)\"),\n"
     "            MostrarFalha(NAO_DEU_AGORA, motivo_da_tela=MOTIVO_NAO_FECHOU, sempre=True)]",
     "        return replace(estado, fase=Fase.DEPOIS), [\n"
     "            Registrar(\"\\\"Reiniciar agora\\\": a janela não fechou; nada foi trocado (a pergunta vem ao fechar)\")]"),
    ("Q13 a cópia com a soma errada deixa o .chegando (460 MB) no disco", A,
     "        if _copiar_somando(origem, chegando) != soma_assinada:\n            chegando.unlink(missing_ok=True)\n",
     "        if _copiar_somando(origem, chegando) != soma_assinada:\n"),
    ("Q14 a volta reabre com os argumentos da troca normal (a anterior acha que a troca foi recusada)", A,
     "        argumentos = [] if volta else [ARG_CONFERIR_NOVA, de, para]",
     "        argumentos = [ARG_CONFERIR_NOVA, para, de] if volta else [ARG_CONFERIR_NOVA, de, para]"),
]


def rodar_testes() -> str | None:
    """O primeiro arquivo que falha, ou None. Um arquivo por vez."""
    ambiente = dict(os.environ, PROGRAMDATA=str(COPIA / "saida_teste" / "pd"))
    for i, t in enumerate(TESTES):
        base = COPIA / "saida_teste" / "pt" / f"m{i}"
        base.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run([PY, "-m", "pytest", t, "-q", "-x", "-p", "no:cacheprovider", f"--basetemp={base}"],
                           cwd=COPIA, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=ambiente)
        if r.returncode != 0:
            fim = [l for l in r.stdout.splitlines() if l.startswith(("FAILED", "ERROR"))][:2]
            return f"{t}: {' | '.join(fim) or r.stdout[-300:]}"
    return None


def main() -> None:
    linhas = []
    sem = rodar_testes()
    linhas.append(f"SEM MUTAÇÃO: {'todos passam' if sem is None else 'FALHA ' + sem}")
    print(linhas[-1], flush=True)
    if sem is not None:
        Path(__file__).with_name("mutacoes_qtq3-resultado.txt").write_text("\n".join(linhas), encoding="utf-8")
        return
    for nome, arquivo, de, para in MUTACOES:
        caminho = COPIA / arquivo
        original = caminho.read_text(encoding="utf-8")
        if original.count(de) != 1:
            linhas.append(f"{nome}: ERRO (o trecho aparece {original.count(de)} vezes)")
            print(linhas[-1], flush=True)
            continue
        try:
            caminho.write_text(original.replace(de, para), encoding="utf-8", newline="\n")
            r = rodar_testes()
        finally:
            caminho.write_text(original, encoding="utf-8", newline="\n")
        linhas.append(f"{nome}: {'SOBREVIVEU' if r is None else 'ACUSADA por ' + r}")
        print(linhas[-1], flush=True)
    Path(__file__).with_name("mutacoes_qtq3-resultado.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
