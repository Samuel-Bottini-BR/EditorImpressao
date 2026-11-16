"""A assinatura das versoes para o Kaique (assinatura.py; decisao D-724).

As contas sao o codigo de referencia da RFC 8032 (Ed25519). A prova de que
estao certas: os vetores de teste da propria RFC, secao 7.1 (TEST 1, 2 e 3):
chave privada -> chave publica e assinatura exatas, e a conferencia aceita a
assinatura certa e recusa a mexida.
"""

from __future__ import annotations

import pytest

import assinatura as a

# RFC 8032, secao 7.1 (chave privada, chave publica, mensagem, assinatura)
VETORES = [
    ("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
     "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
     "",
     "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"),
    ("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
     "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
     "72",
     "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"),
    ("c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
     "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025",
     "af82",
     "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a"),
]


@pytest.mark.parametrize("privada, publica, mensagem, esperada", VETORES)
def test_vetores_da_rfc_8032(privada, publica, mensagem, esperada):
    chave = bytes.fromhex(privada)
    msg = bytes.fromhex(mensagem)
    assert a.secret_to_public(chave).hex() == publica
    assert a.sign(chave, msg).hex() == esperada
    assert a.verify(bytes.fromhex(publica), msg, bytes.fromhex(esperada))


@pytest.mark.parametrize("privada, publica, mensagem, esperada", VETORES)
def test_assinatura_mexida_e_recusada(privada, publica, mensagem, esperada):
    assinatura = bytearray(bytes.fromhex(esperada))
    assinatura[5] ^= 1
    assert not a.verify(bytes.fromhex(publica), bytes.fromhex(mensagem), bytes(assinatura))
    assert not a.verify(bytes.fromhex(publica), bytes.fromhex(mensagem) + b"x", bytes.fromhex(esperada))


def _versao(**trocas):
    base = dict(pacote="EditorImpressao", versao="1.2.0", arquivo="EditorImpressao-1.2.0-full.nupkg",
                sha256="ab" * 32)
    base.update(trocas)
    return a.VersaoAssinada(**base)


def test_arquivo_de_assinatura_ida_e_volta():
    chave = bytes(range(32))
    publica = a.secret_to_public(chave).hex()
    texto = a.escrever_assinatura(chave, _versao())
    assert a.conferir_versao(texto, _versao(), publica) is None


@pytest.mark.parametrize("trocas, trecho", [
    ({"versao": "1.3.0"}, "versão"),
    ({"sha256": "cd" * 32}, "soma"),
    ({"arquivo": "Outro-1.2.0-full.nupkg"}, "arquivo"),
    ({"pacote": "Outro"}, "pacote"),
])
def test_assinatura_de_outra_coisa_e_recusada(trocas, trecho):
    """A assinatura vale so para o que ela afirma: outra versao, outra soma
    (o pacote foi trocado), outro arquivo ou outro programa = recusa."""
    chave = bytes(range(32))
    publica = a.secret_to_public(chave).hex()
    texto = a.escrever_assinatura(chave, _versao())
    motivo = a.conferir_versao(texto, _versao(**trocas), publica)
    assert motivo is not None and trecho in motivo


def test_chave_errada_e_recusada():
    """Assinada por outra chave (quem nao e o Samuel) = recusa."""
    publica_do_samuel = a.secret_to_public(bytes(range(32))).hex()
    texto_de_outro = a.escrever_assinatura(bytes(range(1, 33)), _versao())
    motivo = a.conferir_versao(texto_de_outro, _versao(), publica_do_samuel)
    assert motivo == "a assinatura não confere com a chave do Samuel"


def test_texto_mexido_e_recusado():
    chave = bytes(range(32))
    publica = a.secret_to_public(chave).hex()
    texto = a.escrever_assinatura(chave, _versao()).replace("1.2.0", "1.9.0")
    assert a.conferir_versao(texto, _versao(versao="1.9.0", arquivo="EditorImpressao-1.9.0-full.nupkg"),
                             publica) is not None
    assert a.conferir_versao("qualquer coisa", _versao(), publica) is not None


def test_a_chave_publica_do_programa_existe_e_e_valida():
    """A chave publica que vai dentro do programa e uma chave Ed25519 de 32 bytes."""
    chave = bytes.fromhex(a.CHAVE_PUBLICA_DO_SAMUEL)
    assert len(chave) == 32 and a.point_decompress(chave) is not None


def test_arquivo_da_chave_privada_ida_e_volta(tmp_path):
    chave = a.nova_chave_privada()
    arquivo = tmp_path / "chave.txt"
    arquivo.write_text(a.texto_da_chave_privada(chave), encoding="utf-8")
    assert a.ler_chave_privada(arquivo) == chave
    (tmp_path / "outra.txt").write_text("nada\n", encoding="utf-8")
    with pytest.raises(ValueError):
        a.ler_chave_privada(tmp_path / "outra.txt")


def test_a_chave_privada_mora_fora_do_repositorio():
    """D-724: a chave nunca vai para o GitHub. O lugar padrao fica fora da
    pasta do projeto."""
    from pathlib import Path

    raiz = Path(a.__file__).resolve().parent
    assert raiz not in a.caminho_da_chave().resolve().parents
