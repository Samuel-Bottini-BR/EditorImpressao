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


class Info:
    def __init__(self, alvo: Pacote):
        self.TargetFullRelease = alvo


class GerenteFalso:
    """O UpdateManager do Velopack de mentira: anota o que lhe pediram."""

    def __init__(self, atual: str = "1.1.0", nova: str | None = "1.2.0", portatil: bool = False,
                 erro: Exception | None = None):
        self.atual = atual
        self.alvo = Pacote(nova) if nova else None
        self.portatil = portatil
        self.erro = erro
        self.baixou = False
        self.trocou: list = []

    def get_current_version(self):
        return self.atual

    def get_is_portable(self):
        return self.portatil

    def check_for_updates(self):
        if self.erro:
            raise self.erro
        return Info(self.alvo) if self.alvo else None

    def download_updates(self, info):
        self.baixou = True

    def wait_exit_then_apply_updates(self, alvo, silent=False, restart=True, restart_args=None):
        self.trocou.append((alvo.Version, silent, restart, list(restart_args or [])))


def _servidor(tmp_path: Path, alvo: Pacote, chave: bytes = CHAVE) -> atualizacao.Fonte:
    """Uma pasta com o arquivo da assinatura da versao alvo (o servidor de mentira)."""
    pasta = tmp_path / "servidor"
    pasta.mkdir(exist_ok=True)
    v = assinatura.VersaoAssinada(alvo.PackageId, alvo.Version, alvo.FileName, alvo.SHA256)
    nome = assinatura.nome_do_arquivo_da_assinatura(alvo.PackageId, alvo.Version)
    (pasta / nome).write_text(assinatura.escrever_assinatura(chave, v), encoding="utf-8")
    return atualizacao.Fonte(str(pasta))


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


def test_d714_a_tarefa_roda_ao_ligar_como_o_sistema_sem_janela():
    xml = atualizacao.xml_da_tarefa(Path(r"C:\Program Files\EditorImpressao\current\EditorImpressao.exe"))
    assert "<BootTrigger>" in xml and "<UserId>S-1-5-18</UserId>" in xml
    assert f"<Arguments>{atualizacao.ARG_PROCURAR}</Arguments>" in xml
    assert "<Priority>7</Priority>" in xml          # prioridade baixa
    assert "<RunOnlyIfNetworkAvailable>false" in xml  # a 1a rodada instala o Visual C++ sem internet
    assert "current\\EditorImpressao.exe" in xml


def test_d714_criar_e_apagar_a_tarefa_pelo_schtasks():
    pedidos = []

    def rodar(comando, tempo=120):
        pedidos.append(comando)
        return 0, "ok"

    assert atualizacao.criar_tarefa(Path("C:/x/EditorImpressao.exe"), rodar=rodar)
    assert atualizacao.apagar_tarefa(rodar=rodar)
    assert pedidos[0][:4] == ["schtasks", "/Create", "/TN", atualizacao.NOME_DA_TAREFA]
    assert pedidos[1][:4] == ["schtasks", "/Delete", "/TN", atualizacao.NOME_DA_TAREFA]


# ---------------------------------------------------------------------------
# D-724: a assinatura, antes de baixar
# ---------------------------------------------------------------------------

def test_d724_versao_com_assinatura_errada_e_recusada_antes_de_baixar(tmp_path):
    gerente = GerenteFalso()
    fonte = _servidor(tmp_path, gerente.alvo, chave=bytes(range(1, 33)))   # assinada por outro
    feito = atualizacao.procurar_e_preparar(gerente, fonte, lambda: False, chave_publica=PUBLICA)
    assert feito == "recusada"
    assert not gerente.baixou and gerente.trocou == []
    estado = atualizacao.ler_estado()
    assert estado["fase"] == "falhou" and estado["tipo"] == "recusada" and "1.2.0" in estado["nao_tentar"]
    assert "assinatura recusada" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")


def test_d724_versao_sem_arquivo_de_assinatura_e_recusada(tmp_path):
    gerente = GerenteFalso()
    (tmp_path / "vazio").mkdir()
    feito = atualizacao.procurar_e_preparar(gerente, atualizacao.Fonte(str(tmp_path / "vazio")),
                                            lambda: False, chave_publica=PUBLICA)
    assert feito == "recusada" and not gerente.baixou


def test_d724_pacote_trocado_depois_de_assinado_e_recusado(tmp_path):
    """A assinatura e da soma do pacote: se o pacote publicado for outro, recusa."""
    gerente = GerenteFalso()
    fonte = _servidor(tmp_path, gerente.alvo)
    gerente.alvo.SHA256 = "cd" * 32
    assert atualizacao.procurar_e_preparar(gerente, fonte, lambda: False, chave_publica=PUBLICA) == "recusada"
    assert not gerente.baixou


def test_d724_versao_que_ja_falhou_nao_e_tentada_de_novo(tmp_path):
    gerente = GerenteFalso()
    fonte = _servidor(tmp_path, gerente.alvo, chave=bytes(range(1, 33)))
    atualizacao.procurar_e_preparar(gerente, fonte, lambda: False, chave_publica=PUBLICA)
    assert atualizacao.procurar_e_preparar(gerente, fonte, lambda: False, chave_publica=PUBLICA) == "ja-falhou"


# ---------------------------------------------------------------------------
# D-714 / D-715 / D-720: programa fechado troca; aberto fica pendente
# ---------------------------------------------------------------------------

def test_d714_programa_fechado_baixa_e_troca_e_reabre_escondido_para_conferir(tmp_path):
    gerente = GerenteFalso()
    fonte = _servidor(tmp_path, gerente.alvo)
    assert atualizacao.procurar_e_preparar(gerente, fonte, lambda: False, chave_publica=PUBLICA) == "aplicando"
    assert gerente.baixou
    assert gerente.trocou == [("1.2.0", True, True, [atualizacao.ARG_CONFERIR_NOVA])]
    estado = atualizacao.ler_estado()
    assert (estado["fase"], estado["nova"], estado["anterior"]) == ("aplicando", "1.2.0", "1.1.0")


def test_d715_programa_aberto_fica_pendente_e_a_tela_avisa(tmp_path):
    gerente = GerenteFalso()
    fonte = _servidor(tmp_path, gerente.alvo)
    assert atualizacao.procurar_e_preparar(gerente, fonte, lambda: True, chave_publica=PUBLICA) == "pendente"
    assert gerente.baixou and gerente.trocou == [], "com o programa aberto não pode trocar"
    assert atualizacao.o_que_avisar(atualizacao.ler_estado(), "1.1.0", set()) == ("versao-nova", "1.2.0")


def test_d720_depois_do_depois_a_tarefa_troca_quando_o_computador_liga(tmp_path):
    """Com "Depois", na proxima vez que o computador liga (programa fechado) a tarefa troca."""
    gerente = GerenteFalso()
    fonte = _servidor(tmp_path, gerente.alvo)
    atualizacao.procurar_e_preparar(gerente, fonte, lambda: True, chave_publica=PUBLICA)
    assert atualizacao.procurar_e_preparar(gerente, fonte, lambda: False, chave_publica=PUBLICA) == "aplicando"


def test_sem_internet_nao_e_falha_e_nao_avisa():
    gerente = GerenteFalso(erro=OSError("sem rede"))
    assert atualizacao.rodar_ao_ligar(atualizacao.Fonte("x"), gerente=gerente, preparar=lambda g: None,
                                      programa_aberto=lambda: False) == 1
    assert atualizacao.o_que_avisar(atualizacao.ler_estado(), "1.1.0", set()) is None
    assert "sem rede" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


class JanelaFalsa:
    """Basta para o vigia: um QWidget de verdade que anota o close()."""

    def __init__(self):
        from PySide6.QtWidgets import QWidget

        class _J(QWidget):
            fechou = 0

            def close(self):  # noqa: D401
                type(self).fechou += 1
                return True

        self.widget = _J()


def _vigia(estado: dict, respostas: list[bool], pedidos: list, avisos: list, aplicou: list):
    from ui.aviso_de_atualizacao import VigiaDaAtualizacao

    def perguntar(pai, titulo, texto, sim="Sim", nao="Não", padrao_sim=False):
        pedidos.append((titulo, texto, sim, nao, padrao_sim))
        return respostas.pop(0)

    def avisar(pai, titulo, texto, botao="entendi", icone=None):
        avisos.append((titulo, texto))

    janela = JanelaFalsa().widget
    vigia = VigiaDaAtualizacao(janela, ler_estado=lambda: estado, versao_atual=lambda: "1.1.0",
                               perguntar=perguntar, avisar=avisar, aplicar=lambda: aplicou.append(1) or True)
    return vigia, janela


def test_d720_o_aviso_tem_reiniciar_agora_e_depois_e_depois_nao_troca(app):
    pedidos, avisos, aplicou = [], [], []
    vigia, janela = _vigia({"fase": "pendente", "nova": "1.2.0", "anterior": "1.1.0"}, [False], pedidos,
                           avisos, aplicou)
    fechou_antes = type(janela).fechou
    vigia.olhar()
    assert len(pedidos) == 1
    titulo, texto, sim, nao, padrao_sim = pedidos[0]
    assert (sim, nao) == ("Reiniciar agora", "Depois")
    assert padrao_sim is False, "o Enter fica no \"Depois\""
    assert "Salve o seu trabalho" in texto and "próxima vez que o computador ligar" in texto
    assert aplicou == [] and type(janela).fechou == fechou_antes, "\"Depois\" não troca nem fecha"
    vigia.olhar()
    assert len(pedidos) == 1, "depois do \"Depois\" o aviso não volta nesta abertura"


def test_d720_reiniciar_agora_fecha_gravando_e_so_depois_troca(app):
    pedidos, avisos, aplicou = [], [], []
    vigia, janela = _vigia({"fase": "pendente", "nova": "1.2.0", "anterior": "1.1.0"}, [True], pedidos,
                           avisos, aplicou)
    fechou_antes = type(janela).fechou
    vigia.olhar()
    assert type(janela).fechou == fechou_antes + 1, "fecha pela janela (o closeEvent grava o trabalho)"
    assert aplicou == [1]


def test_os_textos_do_aviso_sem_emoji_e_com_acento():
    for texto in (atualizacao.FRASE_DA_VERSAO_NOVA, atualizacao.FRASE_DA_FALHA, atualizacao.TITULO_DA_VERSAO_NOVA,
                  atualizacao.BOTAO_REINICIAR, atualizacao.BOTAO_DEPOIS, atualizacao.TITULO_DA_FALHA):
        assert all(ord(c) < 0x2000 for c in texto), texto
    assert "versão" in atualizacao.FRASE_DA_VERSAO_NOVA


def test_pelo_codigo_o_aviso_nao_liga():
    from ui.aviso_de_atualizacao import ligar_na_janela

    assert ligar_na_janela(object(), instalado=lambda: False) is None


# ---------------------------------------------------------------------------
# D-718 / D-719: a falha volta e avisa
# ---------------------------------------------------------------------------

def test_d719_a_frase_da_falha_e_a_combinada():
    assert atualizacao.FRASE_DA_FALHA == ("A atualização não deu certo. O programa voltou para a versão anterior "
                                          "e continua funcionando. Avise o Samuel.")


def test_d719_a_falha_aparece_na_tela_uma_vez_so(app):
    atualizacao.registrar_falha("teste", "1.1.0", "1.2.0", "de mentira")
    pedidos, avisos, aplicou = [], [], []
    vigia, _ = _vigia(atualizacao.ler_estado(), [], pedidos, avisos, aplicou)
    vigia.olhar()
    vigia.olhar()
    assert avisos == [(atualizacao.TITULO_DA_FALHA, atualizacao.FRASE_DA_FALHA)]
    assert pedidos == [] and aplicou == []


def test_d719_o_erro_vai_para_o_registro_no_programdata(_programdata_de_mentira):
    atualizacao.registrar_falha("troca", "1.1.0", "1.2.0", "motivo de mentira")
    registro = _programdata_de_mentira / "EditorImpressao" / "atualizacao" / "atualizacao.log"
    assert registro == atualizacao.caminho_do_registro()
    assert "FALHOU (troca)" in registro.read_text(encoding="utf-8")


def test_d718_versao_nova_que_nao_passa_no_teste_volta_para_a_anterior():
    atualizacao.gravar_estado({"fase": "aplicando", "nova": "1.2.0", "anterior": "1.1.0"})
    voltou = []
    codigo = atualizacao.conferir_versao_nova(atualizacao.Fonte("x"), "1.2.0", teste=lambda: (False, "quebrada"),
                                              voltar=lambda fonte, anterior: voltou.append(anterior) or True)
    assert codigo == 1 and voltou == ["1.1.0"]
    assert atualizacao.o_que_avisar(atualizacao.ler_estado(), "1.1.0", set())[0] == "falhou"


def test_d718_versao_nova_que_passa_no_teste_fica():
    atualizacao.gravar_estado({"fase": "aplicando", "nova": "1.2.0", "anterior": "1.1.0"})
    codigo = atualizacao.conferir_versao_nova(atualizacao.Fonte("x"), "1.2.0", teste=lambda: (True, ""),
                                              voltar=lambda *a: pytest.fail("não pode voltar"))
    assert codigo == 0 and atualizacao.ler_estado()["fase"] == "ok"
    assert atualizacao.o_que_avisar(atualizacao.ler_estado(), "1.2.0", set()) is None


def test_d718_troca_desfeita_pelo_velopack_conta_como_falha():
    """Estava "aplicando" a 1.2.0 e o programa continua na 1.1.0: o Velopack devolveu a anterior."""
    atualizacao.gravar_estado({"fase": "aplicando", "nova": "1.2.0", "anterior": "1.1.0"})
    assert atualizacao.situacao(atualizacao.ler_estado(), "1.1.0") == ("falhou", "troca-1.2.0")
    gerente = GerenteFalso(nova=None)
    atualizacao.rodar_ao_ligar(atualizacao.Fonte("x"), gerente=gerente, preparar=lambda g: None,
                               programa_aberto=lambda: False)
    assert atualizacao.ler_estado()["tipo"] == "troca"


def _pacote_publicado(pasta: Path, versao_do_pacote: str, chave: bytes) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{versao.ID_DO_PACOTE}-{versao_do_pacote}-full.nupkg"
    (pasta / nome).write_bytes(b"pacote da " + versao_do_pacote.encode())
    v = assinatura.VersaoAssinada(versao.ID_DO_PACOTE, versao_do_pacote, nome,
                                  assinatura.soma_sha256(pasta / nome))
    (pasta / assinatura.nome_do_arquivo_da_assinatura(versao.ID_DO_PACOTE, versao_do_pacote)).write_text(
        assinatura.escrever_assinatura(chave, v), encoding="utf-8")
    return pasta / nome


def test_d718_a_volta_so_aceita_o_pacote_assinado(tmp_path):
    _pacote_publicado(tmp_path / "servidor", "1.1.0", CHAVE)
    aplicados = []
    certo = atualizacao.voltar_para_a_anterior(atualizacao.Fonte(str(tmp_path / "servidor")), "1.1.0",
                                               tmp_path / "trabalho", aplicar=aplicados.append,
                                               chave_publica=PUBLICA)
    assert certo and len(aplicados) == 1 and aplicados[0].read_bytes() == b"pacote da 1.1.0"
    # agora assinado por outra chave: nao volta
    _pacote_publicado(tmp_path / "falso", "1.1.0", bytes(range(1, 33)))
    aplicados.clear()
    assert not atualizacao.voltar_para_a_anterior(atualizacao.Fonte(str(tmp_path / "falso")), "1.1.0",
                                                  tmp_path / "trabalho2", aplicar=aplicados.append,
                                                  chave_publica=PUBLICA)
    assert aplicados == []


# ---------------------------------------------------------------------------
# D-719: nenhum token ou senha dentro do programa
# ---------------------------------------------------------------------------

def test_d719_nenhum_token_dentro_do_programa():
    arquivos = [RAIZ / n for n in ("atualizacao.py", "assinatura.py", "versao.py", "main.py")]
    arquivos.append(RAIZ / "ui" / "aviso_de_atualizacao.py")
    proibidos = re.compile(r"ghp_|github_pat_|gho_|access_token\s*=|Authorization|HttpHeader|--token")
    for arquivo in arquivos:
        texto = arquivo.read_text(encoding="utf-8")
        assert not proibidos.search(texto), arquivo.name
    assert "velopack.GithubSource(self.endereco)" in (RAIZ / "atualizacao.py").read_text(encoding="utf-8")
    assert atualizacao.Fonte.padrao().endereco == "https://github.com/Samuel-Bottini-BR/EditorImpressao"


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
    assert arquivo.name == "EditorImpressao-1.2.0.assinatura"


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


def test_d723_o_pacote_portatil_do_ensaio_nunca_mexe_no_windows(monkeypatch):
    monkeypatch.setattr(atualizacao, "tirar_instalacao_antiga", lambda *a, **k: pytest.fail("tirou o Inno"))
    monkeypatch.setattr(atualizacao, "instalar_visual_c_se_faltar", lambda *a, **k: pytest.fail("rodou o vc_redist"))
    atualizacao.preparar_o_computador(GerenteFalso(portatil=True))


def test_d723_instalacao_de_verdade_prepara_o_computador(monkeypatch):
    feito = []
    monkeypatch.setattr(atualizacao, "tirar_instalacao_antiga", lambda *a, **k: feito.append("inno"))
    monkeypatch.setattr(atualizacao, "instalar_visual_c_se_faltar", lambda *a, **k: feito.append("vc"))
    atualizacao.preparar_o_computador(GerenteFalso(portatil=False))
    assert feito == ["vc", "inno"]


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
