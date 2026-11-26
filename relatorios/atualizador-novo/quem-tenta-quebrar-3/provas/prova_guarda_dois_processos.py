"""Prova EXECUTADA (quem tenta quebrar 3, 24/11/2026): dois processos de verdade guardando a mesma última boa ao
mesmo tempo (o que acontece quando o Kaique clica duas vezes no atalho logo depois de uma troca: as duas aberturas
passam no teste rápido e as duas guardam o pacote, por trás).

O que `guardar_ultima_boa` confere: a soma do que LEU de `packages\\` (`_copiar_somando`), não o que ficou escrito no
destino. O segundo processo abre o mesmo `<nome>.chegando` com "wb" (apaga o que o primeiro já escreveu) e os dois
escrevem no mesmo arquivo. Pergunta: o arquivo que fica com o nome final é o pacote certo, e o que cada processo diz?

Tudo em `saida_teste\\qtq3\\dois`; a função é a do ramo, de verdade; a chave é a de prova. Repete 5 vezes (corrida).
Uso: python prova_guarda_dois_processos.py (saída em prova_guarda_dois_processos-resultado.txt)
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAMO))
sys.path.insert(0, str(RAMO / "tests"))
os.environ["PROGRAMDATA"] = str(RAMO / "saida_teste" / "qtq3" / "programdata-falso")
R = RAMO / "saida_teste" / "qtq3" / "dois"

import assinatura  # noqa: E402
import atualizacao  # noqa: E402
import versao  # noqa: E402
from ajudante_do_atualizador import CHAVE, PUBLICA  # noqa: E402

PACOTE = versao.ID_DO_PACOTE
FILHO = """
import sys, os, json
sys.path.insert(0, r'{ramo}')
os.environ['PROGRAMDATA'] = r'{pd}'
import atualizacao
m = atualizacao.guardar_ultima_boa(r'{raiz}', '1.2.0', atualizacao.Fonte('x'), open(r'{chave}').read())
print(json.dumps(m))
"""


def main() -> None:
    if R.exists():
        shutil.rmtree(R)
    R.mkdir(parents=True)
    dados = io.BytesIO()
    with zipfile.ZipFile(dados, "w", zipfile.ZIP_STORED) as z:
        z.writestr("lib/app/motor-exigido.json", json.dumps({"versao": 1}))
        z.writestr("lib/app/enchimento.bin", os.urandom(200 * 1024 * 1024))
    pacote = dados.getvalue()
    sha = hashlib.sha256(pacote).hexdigest()
    nome = atualizacao.nome_do_pacote("1.2.0")
    texto = assinatura.escrever_assinatura(CHAVE, assinatura.VersaoAssinada(PACOTE, "1.2.0", nome, sha))
    chave = R / "chave.txt"
    chave.write_text(PUBLICA, encoding="utf-8")
    resultados = []
    for rodada in range(1, 6):
        raiz = R / f"rodada{rodada}"
        (raiz / "packages").mkdir(parents=True)
        (raiz / "packages" / nome).write_bytes(pacote)
        boa = atualizacao.pasta_da_ultima_boa(raiz)
        boa.mkdir()
        (boa / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.2.0")).write_bytes(texto.encode())
        codigo = FILHO.format(ramo=RAMO, pd=os.environ["PROGRAMDATA"], raiz=raiz, chave=chave)
        p1 = subprocess.Popen([sys.executable, "-c", codigo], stdout=subprocess.PIPE, text=True)
        chegando = boa / (nome + ".chegando")
        for _ in range(2000):
            if chegando.exists() and chegando.stat().st_size > (40 + 20 * rodada) * 2**20:
                break
            time.sleep(0.005)
        p2 = subprocess.Popen([sys.executable, "-c", codigo], stdout=subprocess.PIPE, text=True)
        r1, r2 = p1.communicate()[0].strip(), p2.communicate()[0].strip()
        final = boa / nome
        soma_final = hashlib.sha256(final.read_bytes()).hexdigest() if final.exists() else None
        resultados.append({
            "rodada": rodada, "processo 1 devolveu": r1, "processo 2 devolveu": r2,
            "ler_ultima_boa (o que a abertura seguinte e a volta usam)": atualizacao.ler_ultima_boa(raiz),
            "o pacote guardado tem a soma assinada?": soma_final == sha,
            "arquivos na ultima-boa": sorted(p.name for p in boa.iterdir())})
        shutil.rmtree(raiz)
    texto_saida = json.dumps(resultados, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_guarda_dois_processos-resultado.txt").write_text(texto_saida, encoding="utf-8")
    print(texto_saida)
    shutil.rmtree(R)


if __name__ == "__main__":
    main()
