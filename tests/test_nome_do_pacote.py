r"""O nome interno do pacote do Velopack nunca e o nome da pasta dos projetos (D-763).

Teste de reversao (CLAUDE.md §4.7) do defeito achado em 17/11/2026 pela prova
da pasta de reserva (ramo velopack-pasta-2026-11-17,
relatorios/velopack-pasta-2026-11-17/relatorio.md): o nome do pacote
(versao.ID_DO_PACOTE) era "EditorImpressao", o MESMO nome da pasta onde moram
os projetos do Kaique (historico.pasta_de_dados, %LOCALAPPDATA%\EditorImpressao).
O Velopack usa LocalAppData\<nome do pacote> como pasta de reserva quando a
pasta do programa nao aceita gravacao (a cada abertura na conta do Kaique ele
punha ali Update.exe e packages\), e o desinstalador do .msi apaga uma pasta
LocalAppData\<...> inteira: na prova de 17/11 apagou um projeto de mentira.
A prova repetida (relatorios/nome-pacote-2026-11-17/) mostrou que, na 1.2.161,
essa limpeza recebe o TITULO do pacote (em 17/11 o titulo era igual ao nome);
o Velopack mais novo tem outra limpeza (UserCleanupDeferred), que apaga
LocalAppData\<nome> de proposito. Por isso nem o nome nem o titulo podem ser o
nome da pasta dos projetos. No codigo de antes (ID_DO_PACOTE =
"EditorImpressao") os tres primeiros testes falham.

A regra do nome mora num lugar so: versao.ID_DO_PACOTE. Todo o resto le dali
(o --packId do vpk, os nomes dos .nupkg e das assinaturas, a volta para a
versao anterior). Por isso o quarto teste cobra que o --packId e esse valor.

O quinto cobra que as duas pontas do Velopack (o velopack do pip, que roda no
programa, e o vpk, que monta o instalador e leva a limpeza do desinstalador)
estao presas na mesma versao, a da prova de 17/11. Subir de versao exige
repetir a prova.

Seguro mudar: o nome novo, desde que continue diferente da pasta dos dados e
antes da primeira instalacao de verdade (ver o comentario em versao.py).
Arriscado: afrouxar estes testes.
"""

from __future__ import annotations

import re
from pathlib import Path, PureWindowsPath

import empacotar
import historico
import versao

RAIZ = Path(__file__).resolve().parent.parent


def test_d763_o_nome_do_pacote_nunca_e_o_nome_da_pasta_dos_projetos():
    """Defeito de 17/11/2026: id do pacote = "EditorImpressao" = pasta dos projetos."""
    pasta_dos_dados = historico.pasta_de_dados().name
    assert versao.ID_DO_PACOTE.casefold() != pasta_dos_dados.casefold(), (
        f"o nome do pacote ({versao.ID_DO_PACOTE!r}) e o da pasta dos projetos ({pasta_dos_dados!r}): "
        "o Velopack gravaria na pasta dos projetos, e um Velopack mais novo a apagaria ao desinstalar")


def test_d763_a_pasta_de_reserva_do_velopack_fica_fora_da_pasta_dos_projetos():
    """A pasta que o Velopack monta (LocalAppData + nome do pacote) nao e a dos
    projetos nem fica dentro dela, em nenhum LocalAppData."""
    local = PureWindowsPath(r"C:\Users\Kaique\AppData\Local")
    dados = local / historico.pasta_de_dados().name
    reserva = local / versao.ID_DO_PACOTE
    assert not re.search(r"[\\/:]", versao.ID_DO_PACOTE), "o nome do pacote nao pode ter barra nem dois-pontos"
    for pasta in (reserva, reserva / "packages", reserva / "Update.exe"):
        texto = str(pasta).casefold()
        assert texto != str(dados).casefold()
        assert not texto.startswith(str(dados).casefold() + "\\"), f"{pasta} fica dentro de {dados}"


def test_d763_a_limpeza_do_desinstalador_fica_fora_da_pasta_dos_projetos():
    """Achado da prova repetida (17/11/2026, relatorios/nome-pacote-2026-11-17/): o .msi do
    vpk 1.2.161 passa a limpeza do desinstalador o TITULO do pacote, e nao o nome
    (no modelo do WiX dele, RustAppId = {{AppTitle}}); ela apaga LocalAppData\\<titulo>
    e Temp\\velopack_<titulo>. Na prova de 17/11 o titulo era igual ao nome, por isso
    pareceu ser o nome. Entao o titulo (empacotar.TITULO_DO_PACOTE) tambem nunca pode
    ser o nome da pasta dos projetos. No codigo antigo este teste falha pelo nome
    (a parte do titulo passaria: o titulo nao mudou; ela e a trava para o futuro)."""
    local = PureWindowsPath(r"C:\Users\Kaique\AppData\Local")
    dados = str(local / historico.pasta_de_dados().name).casefold()
    assert not re.search(r"[\\/:]", empacotar.TITULO_DO_PACOTE)
    for nome in (empacotar.TITULO_DO_PACOTE, versao.ID_DO_PACOTE):
        limpa = str(local / nome).casefold()
        assert limpa != dados and not limpa.startswith(dados + "\\"), nome
    comando = empacotar.comando_do_vpk(Path("vpk.exe"), Path("pasta"), Path("saida"), "1.2.3")
    assert comando[comando.index("--packTitle") + 1] == empacotar.TITULO_DO_PACOTE


def test_d763_o_packid_do_vpk_e_o_nome_do_pacote():
    """O instalador leva exatamente versao.ID_DO_PACOTE (um lugar so)."""
    comando = empacotar.comando_do_vpk(Path("vpk.exe"), Path("pasta"), Path("saida"), "1.2.3")
    assert comando[comando.index("--packId") + 1] == versao.ID_DO_PACOTE
    assert empacotar.nupkg_inteiro(Path("saida"), "1.2.3").name == f"{versao.ID_DO_PACOTE}-1.2.3-full.nupkg"


def test_d763_o_velopack_e_o_vpk_presos_na_versao_da_prova():
    """O velopack do pip (requirements.txt) e o vpk (empacotar.VERSAO_DO_VPK) na
    mesma versao, a provada em 17/11/2026 (1.2.161)."""
    assert empacotar.VERSAO_DO_VPK == "1.2.161", "subir de versao exige repetir a prova de 17/11"
    texto = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
    presos = re.findall(r"^velopack==(\S+)\s*$", texto, flags=re.MULTILINE)
    assert presos == [empacotar.VERSAO_DO_VPK]
    assert f"--version {empacotar.VERSAO_DO_VPK}" in empacotar.COMO_INSTALAR_O_VPK
