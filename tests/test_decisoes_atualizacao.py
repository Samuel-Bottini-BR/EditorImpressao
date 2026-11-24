"""Provas de comportamento da atualizacao pela internet (etapa 3 da frente do Kaique).

Decisoes do Samuel provadas aqui (docs/plano/DECISOES.md), sem instalar nada
no Windows: o Velopack e trocado por um "gerente falso" com os mesmos metodos,
e as versoes publicadas ficam numa pasta (o servidor de mentira).

- D-714: a versao vem de um lugar so; o programa procura sozinho (a tarefa do
  Windows ao ligar o computador, como SYSTEM); publicar e de proposito.
- D-715/D-720: programa aberto -> fica pendente e aparece o aviso com
  "Reiniciar agora" e "Depois"; "Depois" nao troca.
- D-718/D-719: falha -> a frase combinada na tela (uma vez) e o erro no
  registro em %ProgramData%; volta para a anterior, so com pacote assinado.
- D-719: nenhuma senha ou token dentro do programa.
- D-723: a instalacao antiga (Inno) sai sem tocar nos projetos do Kaique.
- D-724: assinatura errada e recusada ANTES de baixar; publicar sem a chave
  nao roda; a chave nunca dentro do repositorio.
- D-727: o Visual C++ vai dentro do pacote; nada se baixa na hora de instalar.

Atualizador novo (23/11/2026, D-830; D-836, os testes antigos: "os que cobram as mesmas decisões passam a chamar o
caminho novo"): o "gerente falso" saiu; as provas passam pelo executor de verdade (atualizacao.Atualizacao) com só a
borda de mentira (tests/ajudante_do_atualizador.py). As que cobravam o ajudante (a tarefa do Windows que rodava como
o sistema) saíram com ele; a lista teste por teste está em relatorios/atualizador-novo/lista-dos-testes-d836.md.

Nada aqui grava no %ProgramData% de verdade: PROGRAMDATA aponta para uma
pasta temporaria em todos os testes (fixture _programdata_de_mentira).
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

import pytest

import assinatura
import atualizacao
import empacotar
import versao
from core import conversa_com_o_velopack as conversa
from core import fases_da_atualizacao as fases

RAIZ = Path(__file__).resolve().parent.parent
CHAVE = bytes(range(32))                        # chave de mentira (so nos testes)
PUBLICA = assinatura.secret_to_public(CHAVE).hex()


@pytest.fixture(autouse=True)
def _programdata_de_mentira(tmp_path, monkeypatch):
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    yield tmp_path / "ProgramData"


class Pacote:
    """Um VelopackAsset de mentira."""

    def __init__(self, versao_do_pacote: str, sha256: str = "ab" * 32):
        self.PackageId = versao.ID_DO_PACOTE
        self.Version = versao_do_pacote
        self.FileName = f"{versao.ID_DO_PACOTE}-{versao_do_pacote}-full.nupkg"
        self.SHA256 = sha256


# ---------------------------------------------------------------------------
# D-714: a versao de um lugar so
# ---------------------------------------------------------------------------

def test_d714_a_versao_vem_de_um_lugar_so():
    """O numero so esta no versao.py; o Inno e o Velopack o recebem de la."""
    versao.numeros(versao.VERSAO)
    iss = (RAIZ / "instalador.iss").read_text(encoding="utf-8")
    assert not re.search(r'#define\s+MinhaVersao\s+"', iss), "o instalador.iss voltou a ter o número escrito"
    assert "#ifndef MinhaVersao" in iss
    assert f"/DMinhaVersao={versao.VERSAO}" in empacotar.comando_do_inno(Path("ISCC.exe"), Path("x.iss"))
    vpk = empacotar.comando_do_vpk(Path("vpk.exe"), Path("pasta"), Path("saida"), versao.VERSAO)
    assert vpk[vpk.index("--packVersion") + 1] == versao.VERSAO
    # nenhum outro codigo do programa escreve o numero
    codigo = [*RAIZ.glob("*.py"), *(RAIZ / "core").rglob("*.py"), *(RAIZ / "ui").rglob("*.py")]
    achados = [p.name for p in codigo if p.name != "versao.py" and f'"{versao.VERSAO}"' in p.read_text(encoding="utf-8")]
    assert achados == []


# ---------------------------------------------------------------------------
# D-724: a assinatura, antes de baixar
# ---------------------------------------------------------------------------

def test_d724_versao_com_assinatura_errada_e_recusada_antes_de_baixar(tmp_path):
    """D-724 (adaptado pela D-836, atualizador novo 23/11/2026: o mesmo que cobrava, pelo caminho novo): a versão
    publicada com a assinatura de outra chave é recusada ANTES de baixar, e fica em "não tentar"."""
    from tests.ajudante_do_atualizador import NOVA, OUTRA_CHAVE, Prova

    p = Prova(tmp_path, chave_da_nova=OUTRA_CHAVE)
    p.abrir()
    assert "baixar" not in p.vp.nomes()
    assert NOVA in atualizacao.ler_estado()["nao_tentar"]


def test_d724_versao_sem_arquivo_de_assinatura_e_recusada(tmp_path):
    """D-724 (adaptado pela D-836): sem o arquivo da assinatura publicado, a versão é recusada e não é baixada."""
    from tests.ajudante_do_atualizador import NOVA, PACOTE, Prova

    p = Prova(tmp_path)
    (p.fonte_pasta / assinatura.nome_do_arquivo_da_assinatura(PACOTE, NOVA)).unlink()
    p.abrir()
    assert "baixar" not in p.vp.nomes()
    assert atualizacao.ler_estado()["falha"]["tipo"] == "recusada"


def test_d724_pacote_trocado_depois_de_assinado_e_recusado(tmp_path):
    """D-724 (adaptado pela D-836): o índice publicado aponta para um pacote com outra soma que a assinada (o pacote foi
    trocado depois de assinado) → recusada antes de baixar."""
    from tests.ajudante_do_atualizador import Prova

    p = Prova(tmp_path)
    p.vp.publicada = conversa.VersaoDoVelopack(p.vp.publicada.pacote, p.vp.publicada.versao, p.vp.publicada.arquivo,
                                               "cd" * 32, p.vp.publicada.tamanho)
    p.abrir()
    assert "baixar" not in p.vp.nomes()
    assert atualizacao.ler_estado()["falha"]["tipo"] == "recusada"


def test_d724_versao_que_ja_falhou_nao_e_tentada_de_novo(tmp_path):
    """D-724/D-718 (adaptado pela D-836): a versão que já falhou não é conferida nem baixada de novo."""
    from tests.ajudante_do_atualizador import NOVA, Prova

    atualizacao.gravar_estado({"nao_tentar": [NOVA]})
    p = Prova(tmp_path)
    p.abrir()
    assert p.vp.nomes() == ["procurar"]


# ---------------------------------------------------------------------------
# D-714 / D-715 / D-720: programa fechado troca; aberto fica pendente
# ---------------------------------------------------------------------------

def test_d715_programa_aberto_fica_pendente_e_a_tela_avisa(tmp_path):
    """D-715 (adaptado pela D-836): com o programa aberto, a versão baixada não é trocada sozinha; a janela recebe o
    aviso "Reiniciar agora" / "Depois"."""
    from tests.ajudante_do_atualizador import Prova

    p = Prova(tmp_path)
    p.abrir()
    p.ligar_a_tela()
    assert p.tipos_na_tela() == ["MostrarVersaoNova"]
    assert "trocar" not in p.vp.nomes()


def test_sem_internet_nao_e_falha_e_nao_avisa(tmp_path):
    """Sem internet não é falha (adaptado pela D-836): nada na tela, nada anotado como falha, uma linha no registro."""
    from tests.ajudante_do_atualizador import Prova

    p = Prova(tmp_path, erro_ao_procurar="sem internet")
    p.abrir()
    p.ligar_a_tela()
    assert p.tela == [] and "falha" not in atualizacao.ler_estado()


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


class JanelaFalsa:
    """A janela de mentira da tela (a de verdade é a QWidget da PonteDaTela; esta só conta o fechar e o esconder)."""

    def __init__(self, fecha: bool = True):
        self.fecha, self.fechou, self.escondeu = fecha, 0, 0

    def close(self):
        self.fechou += 1
        return self.fecha

    def hide(self):
        self.escondeu += 1


def test_d720_o_aviso_tem_reiniciar_agora_e_depois_e_depois_nao_troca(app, tmp_path):
    """D-720 e D-835 (adaptado pela D-836, e o texto mudado pela D-835): o aviso tem "Reiniciar agora" e "Depois", com
    a frase "Se escolher "Depois", você pode atualizar quando fechar o programa."; "Depois" não fecha nem troca."""
    avisos = []
    p, _, janela = _ponte(app, tmp_path, [False], avisos)
    assert avisos == [(atualizacao.TITULO_DA_VERSAO_NOVA, atualizacao.FRASE_DA_VERSAO_NOVA,
                       atualizacao.BOTAO_REINICIAR, atualizacao.BOTAO_DEPOIS)]
    assert "você pode atualizar quando fechar o programa" in atualizacao.FRASE_DA_VERSAO_NOVA
    assert janela.fechou == 0 and "trocar" not in p.vp.nomes()


def test_d720_reiniciar_agora_fecha_gravando_e_so_depois_troca(app, tmp_path):
    """D-720/D-828 (adaptado pela D-836): "Reiniciar agora" fecha pela janela (o closeEvent grava o trabalho) e só
    depois pede a troca; se a janela recusa fechar, nada é trocado."""
    p, _, janela = _ponte(app, tmp_path / "a", [True], [])
    assert janela.fechou == 1 and "trocar" in p.vp.nomes()
    q, _, janela = _ponte(app, tmp_path / "b", [True], [], fecha=False)
    assert janela.fechou == 1 and "trocar" not in q.vp.nomes()


def test_os_textos_do_aviso_sem_emoji_e_com_acento():
    for texto in (atualizacao.FRASE_DA_VERSAO_NOVA, atualizacao.FRASE_DA_FALHA, atualizacao.TITULO_DA_VERSAO_NOVA,
                  atualizacao.BOTAO_REINICIAR, atualizacao.BOTAO_DEPOIS, atualizacao.TITULO_DA_FALHA):
        assert all(ord(c) < 0x2000 for c in texto), texto
    assert "versão" in atualizacao.FRASE_DA_VERSAO_NOVA


def test_pelo_codigo_o_aviso_nao_liga():
    """Pelo código não há executor da atualização: a janela não liga nada (adaptado pela D-836)."""
    from ui.aviso_de_atualizacao import ao_fechar, ligar_na_janela

    assert atualizacao.da_abertura() is None
    assert ligar_na_janela(object()) is None
    ao_fechar(object())                                # sem ponte: não faz nada e não levanta


# ---------------------------------------------------------------------------
# D-718 / D-719: a falha volta e avisa
# ---------------------------------------------------------------------------

def test_d719_a_frase_da_falha_e_a_combinada():
    assert atualizacao.FRASE_DA_FALHA == ("A atualização não deu certo. O programa voltou para a versão anterior "
                                          "e continua funcionando. Avise o Samuel.")


def test_d719_a_falha_aparece_na_tela_uma_vez_so(app, tmp_path):
    """D-719/D-778 (adaptado pela D-836): a falha anotada aparece na janela com a frase do caso, uma vez só."""
    from tests.ajudante_do_atualizador import Prova

    atualizacao.anotar_falha("teste", "1.0.0", "1.2.0", "de mentira")
    avisos = []
    for pasta in ("a", "b"):
        p = Prova(tmp_path / pasta, publicar_nova=False)
        p.abrir()
        p.atual.ligar_a_tela(lambda ef: avisos.append(atualizacao.FRASES_DA_FALHA[ef.tipo]))
    assert avisos == [atualizacao.FRASE_DA_FALHA]


def test_d719_o_erro_vai_para_o_registro_no_programdata(_programdata_de_mentira):
    """D-719 (adaptado pela D-836: a função única de anotar a falha passou a se chamar `anotar_falha`): a falha vai
    para o registro em %ProgramData%\\EditorImpressao\\atualizacao\\atualizacao.log."""
    atualizacao.anotar_falha("troca", "1.1.0", "1.2.0", "motivo de mentira")
    registro = _programdata_de_mentira / "EditorImpressao" / "atualizacao" / "atualizacao.log"
    assert registro == atualizacao.caminho_do_registro()
    assert "FALHOU (troca)" in registro.read_text(encoding="utf-8")


def test_d718_versao_nova_que_nao_passa_no_teste_volta_para_a_anterior(tmp_path):
    """D-718 (adaptado pela D-836): a versão nova que não passa no teste rápido volta para a anterior (pedida ao
    Velopack) e a falha fica anotada para a janela da anterior mostrar."""
    from tests.ajudante_do_atualizador import ANTERIOR, ATUAL, Prova

    p = Prova(tmp_path, teste=(False, "quebrada"))
    assert p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL) == 0
    assert [c for c in p.vp.chamadas if c[0] == "trocar"][0][1] == ANTERIOR
    assert atualizacao.ler_estado()["falha"]["tipo"] == "teste"


def test_d718_versao_nova_que_passa_no_teste_fica(tmp_path):
    """D-718 (adaptado pela D-836): a versão nova que passa fica; nada volta e nada é anotado como falha."""
    from tests.ajudante_do_atualizador import ANTERIOR, ATUAL, Prova

    p = Prova(tmp_path, teste=(True, ""), publicar_nova=False)
    assert p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL) is None
    assert "trocar" not in p.vp.nomes() and "falha" not in atualizacao.ler_estado()


def test_d718_troca_desfeita_pelo_velopack_conta_como_falha(tmp_path):
    """D-718 (adaptado pela D-836): o Velopack reabriu a versão de antes (a troca não aconteceu) → falha "troca"."""
    from tests.ajudante_do_atualizador import ATUAL, NOVA, Prova

    p = Prova(tmp_path, publicar_nova=False)
    p.abrir(atualizacao.ARG_CONFERIR_NOVA, ATUAL, NOVA)
    assert atualizacao.ler_estado()["falha"]["tipo"] == "troca"


def test_d718_a_volta_so_aceita_o_pacote_assinado(tmp_path):
    """D-718/D-724 (adaptado pela D-836): a anterior sem a assinatura do Samuel não é baixada nem trocada."""
    from tests.ajudante_do_atualizador import ANTERIOR, ATUAL, OUTRA_CHAVE, Prova, _publicar

    p = Prova(tmp_path, teste=(False, "quebrada"))
    _publicar(p.fonte_pasta, ANTERIOR, b"pacote da versao anterior", OUTRA_CHAVE)
    p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    assert "baixar" not in p.vp.nomes() and "trocar" not in p.vp.nomes()


# ---------------------------------------------------------------------------
# D-719: nenhum token ou senha dentro do programa
# ---------------------------------------------------------------------------

def test_d719_nenhum_token_dentro_do_programa(monkeypatch):
    """D-719 (adaptado pela D-836: deixou de conferir uma palavra no texto do código e passou a conferir o que a peça
    do Velopack faz): nenhum token nos arquivos da atualização; a fonte do GitHub é criada só com o endereço público."""
    arquivos = [RAIZ / n for n in ("atualizacao.py", "assinatura.py", "versao.py", "main.py")]
    arquivos += [RAIZ / "ui" / "aviso_de_atualizacao.py", RAIZ / "core" / "conversa_com_o_velopack.py"]
    proibidos = re.compile(r"ghp_|github_pat_|gho_|access_token\s*=|Authorization|HttpHeader|--token")
    for arquivo in arquivos:
        assert not proibidos.search(arquivo.read_text(encoding="utf-8")), arquivo.name
    from core import conversa_com_o_velopack as conversa

    criadas = []
    falso = type("vp", (), {"GithubSource": lambda *a, **k: criadas.append((a, k)) or "fonte"})
    monkeypatch.setattr(conversa, "_velopack", lambda: falso)
    conversa._fonte(atualizacao.Fonte.padrao().endereco)
    assert criadas == [(("https://github.com/Samuel-Bottini-BR/EditorImpressao",), {})]


# ---------------------------------------------------------------------------
# D-724: publicar so com a chave, e a chave fora do repositorio
# ---------------------------------------------------------------------------

def test_d724_publicar_sem_a_chave_para_antes_de_tudo(tmp_path, monkeypatch):
    import publicar_versao_kaique as pub

    rodou = []
    monkeypatch.setattr(pub, "RAIZ", tmp_path / "repositorio")   # tmp_path pode estar dentro da copia
    monkeypatch.setattr(empacotar, "achar_vpk", lambda: rodou.append("vpk") or Path("vpk.exe"))
    monkeypatch.setattr(pub.subprocess, "run", lambda *a, **k: rodou.append(a))
    with pytest.raises(pub.Parou, match="não achei a chave privada"):
        pub.publicar("9.9.9", destino_pasta=tmp_path / "servidor", arquivo_da_chave=tmp_path / "nao-existe.txt")
    assert rodou == [], "nada pode rodar sem a chave"
    assert pub.main(["--pasta", str(tmp_path / "servidor"), "--chave", str(tmp_path / "nao-existe.txt")]) == 1


def test_d724_a_chave_nunca_dentro_do_repositorio(tmp_path):
    import publicar_versao_kaique as pub

    with pytest.raises(pub.Parou, match="dentro do repositório"):
        pub.criar_chave(pub.RAIZ / "chave.txt")
    with pytest.raises(pub.Parou, match="dentro do repositório"):
        pub.achar_chave(pub.RAIZ / "chave.txt")
    assert not (pub.RAIZ / "chave.txt").exists()


def test_d724_publicar_recusa_chave_que_nao_e_a_do_programa(tmp_path, monkeypatch):
    import publicar_versao_kaique as pub

    monkeypatch.setattr(pub, "RAIZ", tmp_path / "repositorio")
    arquivo = tmp_path / "chave.txt"
    arquivo.write_text(assinatura.texto_da_chave_privada(CHAVE), encoding="utf-8")
    with pytest.raises(pub.Parou, match="não é a da chave pública"):
        pub.achar_chave(arquivo)
    assert pub.achar_chave(arquivo, PUBLICA) == CHAVE


def test_d724_o_que_o_publicar_assina_o_programa_aceita(tmp_path, monkeypatch):
    import publicar_versao_kaique as pub

    nupkg = tmp_path / f"{versao.ID_DO_PACOTE}-1.2.0-full.nupkg"
    nupkg.write_bytes(b"conteudo")
    arquivo = pub.assinar_pacote(CHAVE, nupkg, "1.2.0", PUBLICA)
    alvo = Pacote("1.2.0", assinatura.soma_sha256(nupkg))
    assert atualizacao.conferir_assinatura_do(atualizacao.Fonte(str(tmp_path)), alvo, PUBLICA) is None
    assert arquivo.name == f"{versao.ID_DO_PACOTE}-1.2.0.assinatura"  # D-764 (17/11): o nome lido de versao.py, nao escrito a mao


# ---------------------------------------------------------------------------
# D-723: tirar a instalacao antiga sem tocar nos projetos; nunca no ensaio
# ---------------------------------------------------------------------------

def test_d723_o_comando_que_tira_o_inno(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    antiga = {"pasta": tmp_path / "Editor de Impressao",
              "desinstalador": tmp_path / "Editor de Impressao" / "unins000.exe"}
    nova = tmp_path / "EditorImpressao"
    comando = atualizacao.comando_para_tirar_o_inno(antiga, nova)
    assert comando[1:] == ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]
    assert atualizacao.comando_para_tirar_o_inno(antiga, antiga["pasta"]) is None, "a mesma pasta da nova"
    fora = {"pasta": antiga["pasta"], "desinstalador": tmp_path / "outro" / "unins000.exe"}
    assert atualizacao.comando_para_tirar_o_inno(fora, nova) is None
    estranho = {"pasta": antiga["pasta"], "desinstalador": antiga["pasta"] / "apagar_tudo.exe"}
    assert atualizacao.comando_para_tirar_o_inno(estranho, nova) is None
    dados = {"pasta": tmp_path / "Local" / "EditorImpressao",
             "desinstalador": tmp_path / "Local" / "EditorImpressao" / "unins000.exe"}
    assert atualizacao.comando_para_tirar_o_inno(dados, nova) is None, "nunca dentro dos projetos do Kaique"


def test_d723_o_desinstalador_do_inno_nao_apaga_os_projetos():
    """[UninstallDelete] do instalador.iss (igual no de 28/10): so pastas dentro de {app}."""
    iss = (RAIZ / "instalador.iss").read_text(encoding="utf-8")
    secao = iss.split("[UninstallDelete]", 1)[1].split("[Code]", 1)[0]
    nomes = re.findall(r'Name:\s*"([^"]+)"', secao)
    assert nomes and all(n.startswith("{app}\\") for n in nomes)
    regras = [l for l in secao.splitlines() if l.strip() and not l.lstrip().startswith(";")]
    assert not any("localappdata" in l.lower() for l in regras)


def test_d723_o_pacote_portatil_do_ensaio_nunca_mexe_no_windows(tmp_path):
    """D-723 (adaptado pela D-836): o pacote portátil do ensaio (o `.portable` na raiz) nunca pergunta ao Windows nem
    procura."""
    from tests.ajudante_do_atualizador import Prova

    p = Prova(tmp_path, grava=False)
    (p.raiz / ".portable").write_text("", encoding="utf-8")
    p.abrir()
    assert p.win.pedidos == [] and p.vp.chamadas == []
    assert atualizacao.e_portatil(p.raiz) is True and atualizacao.e_portatil(tmp_path) is False


def test_d714_a_instalacao_de_verdade_nao_cria_a_tarefa(monkeypatch):
    """B1/D-733 (adaptado pela D-836): os ganchos de instalar e de atualizar do Velopack só anotam; nenhum pede nada ao
    Windows (no desenho novo não existe tarefa nenhuma a criar)."""
    from core import windows

    for nome in ("comecar_pedido_de_licenca", "pedir_licenca", "criar_tarefa", "rodar_tarefa"):
        monkeypatch.setattr(windows, nome, lambda *a, **k: pytest.fail("o gancho falou com o Windows"))
    atualizacao.ao_instalar("1.2.0")
    atualizacao.ao_atualizar("1.2.0")
    assert "instalada a versão 1.2.0" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")


def test_d723_instalacao_de_verdade_prepara_o_computador():
    """D-723/D-727 (adaptado pela D-836: o Visual C++ e tirar o Inno passaram a ser passos da peça do Windows, na
    pergunta da primeira abertura): a pergunta leva os dois, nesta ordem, antes da licença da pasta."""
    tipos = [p.tipo for p in atualizacao.passos_do_preparo()]
    assert tipos.index("instalar_visual_c") < tipos.index("tirar_instalacao_do_inno") < \
        tipos.index("dar_licenca_aos_usuarios")


# ---------------------------------------------------------------------------
# D-727: o Visual C++ dentro do pacote; nada baixado ao instalar
# ---------------------------------------------------------------------------

def test_d727_o_vpk_nao_baixa_nada_na_hora_de_instalar():
    comando = empacotar.comando_do_vpk(Path("vpk.exe"), Path("pasta"), Path("saida"), "1.2.0")
    assert "--framework" not in comando and "-f" not in comando
    assert comando[comando.index("--instLocation") + 1] == "PerMachine" and "--msi" in comando
    assert comando[comando.index("--runtime") + 1] == "win-x64", "sem isto vai para Arquivos de Programas (x86)"


def test_d727_o_visual_c_vai_dentro_e_e_conferido_no_pacote(tmp_path):
    vc = tmp_path / "vc_redist.x64.exe"
    vc.write_bytes(b"MZ visual c")
    pecas = empacotar.PecasDosDetectores(tmp_path / "motor", tmp_path / "tess", tmp_path / "tess" / "doc",
                                         tmp_path / "tessdata", vc, "14.44.35211.0")
    pasta = tmp_path / "EditorImpressao"
    assert empacotar.preparar_pasta_para_o_velopack(pasta, pecas) == []
    assert (pasta / "instalar" / "vc_redist.x64.exe").read_bytes() == b"MZ visual c"
    assert (pasta / "instalar" / "vc_redist.versao.txt").read_text(encoding="utf-8") == "14.44.35211.0"
    esperados = empacotar.esperados_no_pacote_do_velopack(pecas)
    assert "instalar/vc_redist.x64.exe" in esperados
    nupkg = tmp_path / "p.nupkg"
    with zipfile.ZipFile(nupkg, "w") as z:
        for relativo in esperados:
            z.writestr(empacotar.PASTA_NO_NUPKG + relativo, b"x")
    assert empacotar.conferir_pacote_do_velopack(nupkg, pecas) == []
    with zipfile.ZipFile(nupkg, "w") as z:
        for relativo in esperados:
            if not relativo.endswith("vc_redist.x64.exe"):
                z.writestr(empacotar.PASTA_NO_NUPKG + relativo, b"x")
    assert empacotar.conferir_pacote_do_velopack(nupkg, pecas) == ["instalar/vc_redist.x64.exe"]


def test_d727_o_visual_c_so_roda_se_faltar(tmp_path):
    (tmp_path / "instalar").mkdir()
    (tmp_path / "instalar" / "vc_redist.x64.exe").write_bytes(b"x")
    (tmp_path / "instalar" / "vc_redist.versao.txt").write_text("14.44.35211.0", encoding="utf-8")
    rodou = []

    def rodar(comando, tempo=120):
        rodou.append(comando)
        return 0, ""

    atualizacao.instalar_visual_c_se_faltar(tmp_path, ler=lambda: (14, 50, 1), rodar=rodar)
    assert rodou == [], "já havia um mais novo"
    atualizacao.instalar_visual_c_se_faltar(tmp_path, ler=lambda: None, rodar=rodar)
    assert rodou and rodou[0][1:] == ["/install", "/quiet", "/norestart"]


# ---------------------------------------------------------------------------
# O novo nao estraga o que ja funciona (D-605): pelo codigo, nada muda
# ---------------------------------------------------------------------------

def test_pelo_codigo_a_linha_de_comando_nao_faz_nada_nem_importa_o_velopack(monkeypatch):
    monkeypatch.delitem(sys.modules, "velopack", raising=False)
    assert atualizacao.atender_linha_de_comando(["main.py"]) is None
    assert atualizacao.atender_linha_de_comando(["main.py", "livro.pdf"]) is None
    assert "velopack" not in sys.modules
    assert not atualizacao.instalado_pelo_velopack()


def test_o_main_chama_a_atualizacao_por_um_ponto_so():
    texto = (RAIZ / "main.py").read_text(encoding="utf-8")
    assert texto.count("atender_linha_de_comando(sys.argv)") == 1
    assert texto.count("ligar_na_janela(janela)") == 1
    # os modos que ja existiam continuam antes dela
    assert texto.index("--servidor-de-paginas") < texto.index("atender_linha_de_comando(sys.argv)")
    assert texto.index("--conferir-ocr") < texto.index("atender_linha_de_comando(sys.argv)")


def test_d720_depois_do_depois_a_versao_entra_ao_fechar(tmp_path):
    """Era `test_d720_depois_do_depois_a_tarefa_troca_quando_o_computador_liga` (D-714 antiga). A decisão mudou
    (D-769 "b", D-794, D-831 "a"): com "Depois", a versão entra AO FECHAR, com a pergunta "Atualizar agora?" (D-835).
    Cobra o que vale hoje (D-836): "Depois" não troca; fechar pergunta; "Sim" troca."""
    from tests.ajudante_do_atualizador import _ate_o_aviso

    p = _ate_o_aviso(tmp_path)
    p.atual.evento(fases.Escolheu(False))
    assert "trocar" not in p.vp.nomes()
    p.atual.evento(fases.Fechando())
    assert p.tipos_na_tela()[-1] == "PerguntarAoFechar"
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" in p.vp.nomes()


def _ponte(app, tmp_path, respostas: list[bool], avisos: list, fecha: bool = True):
    """A ponte da tela de verdade (ui/aviso_de_atualizacao.PonteDaTela), com as caixas de mentira e o executor de
    verdade (`Prova`) até o aviso da versão nova."""
    from PySide6.QtWidgets import QWidget

    from tests.ajudante_do_atualizador import Prova
    from ui import aviso_de_atualizacao as aviso

    import os

    os.environ["PROGRAMDATA"] = str(tmp_path / "ProgramData")     # cada computador com o seu estado (a fixture devolve)
    p = Prova(tmp_path)
    p.abrir()
    pai = QWidget()
    janela = JanelaFalsa(fecha)
    janela.pai = pai                                               # segura a janela de verdade (e a ponte) viva
    ponte = aviso.PonteDaTela(pai, p.atual,
                              perguntar=lambda j, t, x, sim, nao: avisos.append((t, x, sim, nao)) or respostas.pop(0),
                              avisar=lambda j, t, x, icone=None: avisos.append((t, x)))
    ponte.janela = janela
    pai._ponte_da_atualizacao = ponte                              # como o ligar_na_janela faz
    p.atual.ligar_a_tela(ponte.receber)
    return p, ponte, janela


def test_d835_ao_fechar_a_pergunta_curta_e_o_sim_esconde_a_janela_e_troca(app, tmp_path):
    """D-835 e D-831 (novo, D-836): ao fechar com "Depois", a caixa "Atualizar agora?" / "Quer atualizar o programa
    agora, ao fechar?" / "Sim" / "Não"; "Sim" esconde a janela e troca; "Não" não troca."""
    from ui import aviso_de_atualizacao as aviso

    avisos = []
    p, ponte, janela = _ponte(app, tmp_path / "a", [False, True], avisos)
    pai = ponte.parent()
    aviso.ao_fechar(pai)
    assert avisos[-1] == ("Atualizar agora?", "Quer atualizar o programa agora, ao fechar?", "Sim", "Não")
    assert janela.escondeu == 1 and "trocar" in p.vp.nomes()
    q, ponte, janela = _ponte(app, tmp_path / "b", [False, False], [])
    aviso.ao_fechar(ponte.parent())
    assert janela.escondeu == 0 and "trocar" not in q.vp.nomes()
