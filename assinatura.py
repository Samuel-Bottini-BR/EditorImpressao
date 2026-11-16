"""A assinatura que prova que a versao para o Kaique e nossa (decisao D-724).

O que e, em portugues: o PC do Samuel tem uma chave secreta (a "privada"), que
nunca sai de la e nunca vai para o GitHub. Com ela, o comando de publicar
(publicar_versao_kaique.py) "assina" cada versao: escreve um arquivo pequeno
(EditorImpressao-<versao>.assinatura) que diz o nome do pacote, a versao e a
soma SHA-256 do arquivo do programa, e uma assinatura dessas linhas. O
programa do Kaique leva so a parte publica da chave (CHAVE_PUBLICA_DO_SAMUEL,
abaixo) e, ANTES de baixar e instalar, confere a assinatura e a soma. Quem nao
tem a chave privada nao consegue fazer uma assinatura que passe - nem quem
entrasse na conta do GitHub.

O metodo: Ed25519 (RFC 8032), o mesmo das atualizacoes do Mac (Sparkle), do
minisign, do WinSparkle e do TUF. As contas abaixo sao o codigo de referencia
da propria RFC 8032, secao 6 (licenca BSD simplificada do IETF Trust), copiado
sem mudar a matematica - so com os nomes em ingles da RFC, para comparar linha
a linha. A prova de que esta certo: tests/test_assinatura.py, com os vetores de
teste da secao 7.1 da RFC. Por que nao uma biblioteca: o .venv nao tem nenhuma
de assinatura (a "cryptography" nao esta instalada) e trocar ou acrescentar
biblioteca pede o "sim" da gerente (CLAUDE.md §6). Se um dia ela entrar, este
modulo pode chamar a dela: o formato do arquivo e o mesmo Ed25519.

Este codigo nao e de "tempo constante": serve para CONFERIR (dados publicos) e
para assinar no PC do Samuel (ninguem mede o tempo la). Nao use para outra coisa.

Arriscado mudar: as contas (qualquer troca quebra os vetores da RFC);
MENSAGEM_V1 e o jeito de montar a mensagem (as versoes ja assinadas deixariam
de conferir); CHAVE_PUBLICA_DO_SAMUEL (so muda junto com a chave privada, e o
programa do Kaique deixa de aceitar as versoes assinadas com a velha).
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# A chave publica do Samuel (32 bytes, em hexadecimal). Criada em 16/11/2026
# por publicar_versao_kaique.py --criar-chave; a privada esta fora do
# repositorio (ver pasta_da_chave). E a unica que o programa aceita.
# ---------------------------------------------------------------------------
CHAVE_PUBLICA_DO_SAMUEL = "b2c4094c50df2da671333390c5cc2a66b4f25217697c0e92a7206ae9e5caf34a"

# ---------------------------------------------------------------------------
# Ed25519 - codigo de referencia da RFC 8032, secao 6
# ---------------------------------------------------------------------------


def sha512(s: bytes) -> bytes:
    return hashlib.sha512(s).digest()


# Base field Z_p
p = 2**255 - 19


def modp_inv(x: int) -> int:
    return pow(x, p - 2, p)


# Curve constant
d = -121665 * modp_inv(121666) % p

# Group order
q = 2**252 + 27742317777372353535851937790883648493


def sha512_modq(s: bytes) -> int:
    return int.from_bytes(sha512(s), "little") % q


# Points are represented as tuples (X, Y, Z, T) of extended coordinates,
# with x = X/Z, y = Y/Z, x*y = T/Z
def point_add(P, Q):
    A, B = (P[1] - P[0]) * (Q[1] - Q[0]) % p, (P[1] + P[0]) * (Q[1] + Q[0]) % p
    C, D = 2 * P[3] * Q[3] * d % p, 2 * P[2] * Q[2] % p
    E, F, G, H = B - A, D - C, D + C, B + A
    return (E * F, G * H, F * G, E * H)


# Computes Q = s * P
def point_mul(s: int, P):
    Q = (0, 1, 1, 0)  # Neutral element
    while s > 0:
        if s & 1:
            Q = point_add(Q, P)
        P = point_add(P, P)
        s >>= 1
    return Q


def point_equal(P, Q) -> bool:
    # x1 / z1 == x2 / z2  <==>  x1 * z2 == x2 * z1
    if (P[0] * Q[2] - Q[0] * P[2]) % p != 0:
        return False
    if (P[1] * Q[2] - Q[1] * P[2]) % p != 0:
        return False
    return True


# Square root of -1
modp_sqrt_m1 = pow(2, (p - 1) // 4, p)


# Compute corresponding x-coordinate, with low bit corresponding to sign,
# or return None on failure
def recover_x(y: int, sign: int):
    if y >= p:
        return None
    # (o "% p" daqui e o unico acrescimo a RFC: sem ele, y = p-1 daria um
    # multiplo de p diferente de zero e a comparacao "x2 == 0" falharia)
    x2 = (y * y - 1) * modp_inv(d * y * y + 1) % p
    if x2 == 0:
        if sign:
            return None
        return 0
    # Compute square root of x2
    x = pow(x2, (p + 3) // 8, p)
    if (x * x - x2) % p != 0:
        x = x * modp_sqrt_m1 % p
    if (x * x - x2) % p != 0:
        return None
    if (x & 1) != sign:
        x = p - x
    return x


# Base point
g_y = 4 * modp_inv(5) % p
g_x = recover_x(g_y, 0)
G = (g_x, g_y, 1, g_x * g_y % p)


def point_compress(P) -> bytes:
    zinv = modp_inv(P[2])
    x = P[0] * zinv % p
    y = P[1] * zinv % p
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def point_decompress(s: bytes):
    if len(s) != 32:
        raise ValueError("Invalid input length for decompression")
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = recover_x(y, sign)
    if x is None:
        return None
    return (x, y, 1, x * y % p)


def secret_expand(secret: bytes):
    if len(secret) != 32:
        raise ValueError("Bad size of private key")
    h = sha512(secret)
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= (1 << 254)
    return (a, h[32:])


def secret_to_public(secret: bytes) -> bytes:
    (a, _dummy) = secret_expand(secret)
    return point_compress(point_mul(a, G))


def sign(secret: bytes, msg: bytes) -> bytes:
    a, prefix = secret_expand(secret)
    A = point_compress(point_mul(a, G))
    r = sha512_modq(prefix + msg)
    R = point_mul(r, G)
    Rs = point_compress(R)
    h = sha512_modq(Rs + A + msg)
    s = (r + h * a) % q
    return Rs + int.to_bytes(s, 32, "little")


def verify(public: bytes, msg: bytes, signature: bytes) -> bool:
    if len(public) != 32:
        return False
    if len(signature) != 64:
        return False
    A = point_decompress(public)
    if not A:
        return False
    Rs = signature[:32]
    R = point_decompress(Rs)
    if not R:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= q:
        return False
    h = sha512_modq(Rs + public + msg)
    sB = point_mul(s, G)
    hA = point_mul(h, A)
    return point_equal(sB, point_add(R, hA))


# ---------------------------------------------------------------------------
# O arquivo da assinatura de uma versao (nosso formato, simples de ler)
# ---------------------------------------------------------------------------

# A primeira linha da mensagem assinada. Se o formato mudar um dia, muda o v1
# (e o programa passa a aceitar as duas), nunca o sentido desta.
MENSAGEM_V1 = "Editor de Impressao - versao para o Kaique - assinatura v1"


@dataclass(frozen=True)
class VersaoAssinada:
    """O que o arquivo .assinatura de uma versao afirma."""

    pacote: str      # o ID do pacote do Velopack (versao.ID_DO_PACOTE)
    versao: str      # "1.2.0"
    arquivo: str     # "EditorImpressao-1.2.0-full.nupkg"
    sha256: str      # soma do arquivo, em hexadecimal minusculo


def nome_do_arquivo_da_assinatura(pacote: str, versao: str) -> str:
    """'EditorImpressao-1.2.0.assinatura': o nome publicado ao lado do pacote."""
    return f"{pacote}-{versao}.assinatura"


def _mensagem(v: VersaoAssinada) -> bytes:
    """As linhas que a assinatura cobre (tudo o que o arquivo afirma)."""
    return "\n".join([MENSAGEM_V1, v.pacote, v.versao, v.arquivo, v.sha256.lower(), ""]).encode("utf-8")


def escrever_assinatura(chave_privada: bytes, v: VersaoAssinada) -> str:
    """O texto do arquivo .assinatura de uma versao (assinado com a chave privada)."""
    assinatura = sign(chave_privada, _mensagem(v))
    return (f"{MENSAGEM_V1}\n"
            f"pacote: {v.pacote}\n"
            f"versao: {v.versao}\n"
            f"arquivo: {v.arquivo}\n"
            f"sha256: {v.sha256.lower()}\n"
            f"assinatura: {assinatura.hex()}\n")


def ler_assinatura(texto: str) -> tuple[VersaoAssinada, bytes] | None:
    """(o que o arquivo afirma, a assinatura) ou None se o texto nao for um
    arquivo de assinatura nosso. Nao confere nada: ver conferir_versao."""
    linhas = [linha.strip() for linha in texto.strip().splitlines()]
    if len(linhas) != 6 or linhas[0] != MENSAGEM_V1:
        return None
    campos = {}
    for linha in linhas[1:]:
        nome, separador, valor = linha.partition(": ")
        if not separador:
            return None
        campos[nome] = valor.strip()
    if set(campos) != {"pacote", "versao", "arquivo", "sha256", "assinatura"}:
        return None
    try:
        assinatura = bytes.fromhex(campos["assinatura"])
    except ValueError:
        return None
    return VersaoAssinada(campos["pacote"], campos["versao"], campos["arquivo"], campos["sha256"]), assinatura


def conferir_versao(texto: str, esperado: VersaoAssinada,
                    chave_publica_hex: str | None = None) -> str | None:
    """A UNICA conferencia de assinatura do programa. None = confere; senao, o
    motivo da recusa (em portugues, para o registro).

    Confere: (1) o arquivo e uma assinatura nossa; (2) a assinatura bate com a
    chave publica do Samuel; (3) o que ela afirma (pacote, versao, nome do
    arquivo e soma SHA-256) e EXATAMENTE o que o Velopack vai baixar.
    Quem chama: atualizacao.procurar_e_preparar (antes de baixar),
    atualizacao.voltar_para_a_anterior (antes de voltar) e
    publicar_versao_kaique (confere a propria assinatura antes de publicar).
    """
    lido = ler_assinatura(texto)
    if lido is None:
        return "o arquivo da assinatura não está no formato esperado"
    afirmado, assinatura = lido
    try:
        chave = bytes.fromhex(chave_publica_hex or CHAVE_PUBLICA_DO_SAMUEL)
    except ValueError:
        return "a chave pública do programa está estragada"
    if not verify(chave, _mensagem(afirmado), assinatura):
        return "a assinatura não confere com a chave do Samuel"
    if afirmado.pacote != esperado.pacote:
        return f"a assinatura é de outro pacote ({afirmado.pacote})"
    if afirmado.versao != esperado.versao:
        return f"a assinatura é da versão {afirmado.versao}, e a versão nova é a {esperado.versao}"
    if afirmado.arquivo != esperado.arquivo:
        return f"a assinatura é do arquivo {afirmado.arquivo}, e o pacote é {esperado.arquivo}"
    if afirmado.sha256.lower() != esperado.sha256.lower():
        return "a soma do pacote não é a que foi assinada (o arquivo foi trocado)"
    return None


def soma_sha256(arquivo: Path) -> str:
    """A soma SHA-256 de um arquivo, em hexadecimal minusculo (lendo aos pedacos)."""
    h = hashlib.sha256()
    with open(arquivo, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# A chave privada (so no PC do Samuel)
# ---------------------------------------------------------------------------

CABECALHO_DA_CHAVE = "Editor de Impressao - CHAVE PRIVADA DE ASSINATURA (nunca no git, nunca no GitHub)"


def pasta_da_chave() -> Path:
    """Onde a chave privada mora no PC do Samuel: %APPDATA%\\EditorImpressao-publicar\\.

    Fora do repositorio de proposito (D-724: "nunca no GitHub"). A copia de
    reserva no HD externo e feita a mao pela gerente.
    """
    base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(base) / "EditorImpressao-publicar"


def caminho_da_chave() -> Path:
    return pasta_da_chave() / "chave-privada-da-assinatura.txt"


def ler_chave_privada(arquivo: Path) -> bytes:
    """Le a chave privada (32 bytes). Levanta ValueError se o arquivo nao for uma chave nossa."""
    linhas = [linha.strip() for linha in Path(arquivo).read_text(encoding="utf-8").splitlines() if linha.strip()]
    if len(linhas) < 2 or linhas[0] != CABECALHO_DA_CHAVE:
        raise ValueError(f"{arquivo} não é uma chave de assinatura do Editor de Impressão")
    chave = bytes.fromhex(linhas[1])
    if len(chave) != 32:
        raise ValueError(f"{arquivo}: a chave não tem 32 bytes")
    return chave


def texto_da_chave_privada(chave: bytes) -> str:
    """O conteudo do arquivo da chave privada."""
    return (f"{CABECALHO_DA_CHAVE}\n{chave.hex()}\n"
            f"chave publica (vai dentro do programa): {secret_to_public(chave).hex()}\n")


def nova_chave_privada() -> bytes:
    """32 bytes do gerador seguro do sistema (os.urandom)."""
    return os.urandom(32)
