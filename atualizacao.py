"""A atualizacao pela internet do Editor de Impressao (Velopack).

Etapa 3 da frente do notebook do Kaique, 16/11/2026. Decisoes do Samuel:
D-706 (atualizar "como funciona com apps", sem reinstalar), D-713 (vem do
GitHub publico do projeto), D-714 (publicada de proposito; "o programa pega
sozinho, toda vez que o pc inicializar em segundo plano"), D-715/D-720 (com o
programa aberto: aviso com "Reiniciar agora" e "Depois"; com "Depois", entra
quando o computador ligar de novo), D-718/D-719 (se falhar, volta para a
versao anterior, mostra a frase combinada e guarda o erro num registro que a
gerente le daqui; nenhuma senha dentro do programa), D-723 (Velopack), D-724
(assinatura gratis conferida antes de instalar), D-727 (tudo dentro do
instalador: o Visual C++ vai no pacote).

COMO FUNCIONA, DO COMECO AO FIM
1. Instalacao (uma vez, com a licenca de administrador que o Kaique da ao
   instalar): o Velopack chama o gancho de "depois de instalar" (ao_instalar),
   que cria a tarefa do Windows (xml_da_tarefa) e a roda uma vez na hora.
2. A tarefa roda como o proprio sistema (SYSTEM), ao ligar o computador, sem
   janela: EditorImpressao.exe --procurar-atualizacao -> rodar_ao_ligar:
   - prepara o computador (preparar_o_computador): instala o Visual C++ que vai
     DENTRO do pacote, se faltar; tira a instalacao antiga do Inno Setup;
   - confere o resultado da ultima troca (situacao) e, se a versao nova ainda
     nao passou no teste rapido, faz o teste (conferir_versao_nova);
   - procura a versao nova (procurar_e_preparar): confere a ASSINATURA antes de
     baixar; baixa so o que mudou; se o programa esta aberto, deixa "pendente"
     (a tela avisa); se esta fechado, pede ao Velopack para trocar e reabrir
     escondido em --conferir-a-versao-nova.
3. --conferir-a-versao-nova (conferir_versao_nova): roda o teste rapido da
   versao nova (--teste-rapido, sem janela). Se falhar, volta para a anterior
   (voltar_para_a_anterior: o pacote da anterior, conferido pela assinatura, e
   aplicado pelo proprio Update.exe do Velopack) e registra a falha.
4. A tela (ui/aviso_de_atualizacao.py) pergunta o_que_avisar de tempos em
   tempos: "versao-nova" -> o aviso com os dois botoes; "falhou" -> a frase da
   D-719, uma vez so.

ONDE FICAM AS COISAS
- estado.json e atualizacao.log em %ProgramData%\\EditorImpressao\\atualizacao\\
  (pasta_do_estado). Por que ali, e nao no %LOCALAPPDATA% do Kaique: a tarefa
  roda como SYSTEM, e a conta dos testes a distancia (por onde a gerente le,
  D-719) nao enxerga a pasta do Kaique; o ProgramData todas as contas leem.
- Os projetos do Kaique (%LOCALAPPDATA%\\EditorImpressao) nunca sao tocados:
  o Velopack troca so a pasta do programa.

A REGRA NUM LUGAR SO (CLAUDE.md §11.12): o que fazer com uma versao nova e
procurar_e_preparar; o que a tela avisa e o_que_avisar (que usa situacao); uma
falha e sempre registrar_falha; a assinatura e sempre
assinatura.conferir_versao; "o programa esta aberto" e marcar_programa_aberto
(a janela) / ha_programa_aberto (a tarefa). A unica entrada pela linha de
comando e atender_linha_de_comando (main.py chama uma vez).

Nada aqui importa Qt nem ui/. O velopack so e importado quando o programa foi
instalado por ele (instalado_pelo_velopack) ou num dos modos escondidos: pelo
codigo (.venv) e nos testes, nada muda e nada fica mais lento.

Arriscado mudar: NOME_DA_TAREFA e os argumentos (a tarefa ja criada no
notebook chama exatamente estes); FRASE_DA_FALHA (palavras combinadas com o
Samuel, D-719); a ordem "assinatura antes de baixar"; o "% portatil nao mexe
no Windows" de preparar_o_computador (no PC do Samuel ha uma instalacao do Inno
de 01/09 que um ensaio nao pode tirar).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

import assinatura
import versao

# ---------------------------------------------------------------------------
# Constantes (o que outros lugares e a tarefa do Windows ja usam)
# ---------------------------------------------------------------------------

# D-713: o projeto continua publico; as versoes vem dos "Releases" dele.
REPOSITORIO = "https://github.com/Samuel-Bottini-BR/EditorImpressao"

# Os modos escondidos (sem janela), atendidos por atender_linha_de_comando.
ARG_PROCURAR = "--procurar-atualizacao"
ARG_CONFERIR_NOVA = "--conferir-a-versao-nova"
ARG_TESTE_RAPIDO = "--teste-rapido"
# So para o ensaio e os testes: de onde vem as versoes (uma pasta, em vez do
# GitHub). O programa do Kaique nunca recebe isto: a tarefa chama sem.
ARG_FONTE = "--fonte"

# A tarefa do Windows (D-714). Dentro de uma pasta propria do Agendador.
NOME_DA_TAREFA = "EditorImpressao\\Procurar versao nova"
# Minutos depois de ligar o computador (deixa a rede e o Windows assentarem).
ATRASO_DEPOIS_DE_LIGAR = "PT3M"

# A marca de "o programa esta aberto" (um mutex com nome, do Windows). A
# janela cria; a tarefa (que roda como SYSTEM, em outra sessao) so consulta.
MARCA_DE_ABERTO = "Global\\EditorImpressao-programa-aberto"

# Os textos da tela (portugues, sem jargao, sem emoji; CLAUDE.md §3).
TITULO_DA_VERSAO_NOVA = "Versão nova do programa"
FRASE_DA_VERSAO_NOVA = (
    "Chegou uma versão nova do Editor de Impressão.\n\n"
    "Salve o seu trabalho e reinicie o programa para usar a versão nova.\n\n"
    "Se escolher \"Depois\", a versão nova entra sozinha na próxima vez que o computador ligar.")
BOTAO_REINICIAR = "Reiniciar agora"
BOTAO_DEPOIS = "Depois"
TITULO_DA_FALHA = "Atualização"
# D-719, palavra por palavra (opcao "1" do Samuel, 16/11/2026). Vale para toda
# falha: assinatura recusada, troca que nao deu certo, versao nova que nao abre.
FRASE_DA_FALHA = ("A atualização não deu certo. O programa voltou para a versão anterior "
                  "e continua funcionando. Avise o Samuel.")

# A instalacao antiga, do Inno Setup (instalador.iss): o AppId fixo dela. O
# Windows a guarda em ...\\Uninstall\\{AppId}_is1.
APPID_DO_INNO = "{7C4E1B92-3A5D-4F18-9B6C-2E8A5D0F3C71}"
CHAVE_DO_INNO = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APPID_DO_INNO}_is1"

# O Visual C++ oficial que vai DENTRO do pacote (D-727), posto pelo
# empacotar.py (preparar_pasta_para_o_velopack) em <programa>\\instalar\\.
PASTA_DO_QUE_SE_INSTALA = "instalar"
VC_REDIST_NOME = "vc_redist.x64.exe"
VC_REDIST_VERSAO = "vc_redist.versao.txt"
CHAVE_DO_VISUAL_C = "SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64"


# ---------------------------------------------------------------------------
# Onde fica o estado e o registro (C:\ProgramData\EditorImpressao\atualizacao)
# ---------------------------------------------------------------------------

def pasta_do_estado() -> Path:
    """%ProgramData%\\EditorImpressao\\atualizacao (lida na hora: os testes trocam a variavel)."""
    base = os.environ.get("PROGRAMDATA") or "C:\\ProgramData"
    return Path(base) / "EditorImpressao" / "atualizacao"


def caminho_do_registro() -> Path:
    """O registro que a gerente le pelo comando de longe (D-719)."""
    return pasta_do_estado() / "atualizacao.log"


def registrar(texto: str) -> None:
    """Anota uma linha no registro da atualizacao. Nunca levanta.

    Quem roda como SYSTEM (a tarefa) grava em %ProgramData%. A janela do
    Kaique nao tem licenca para mudar o arquivo que o SYSTEM criou: ai a linha
    vai para o erros.log de sempre (registro.registrar_erro).
    """
    linha = f"{datetime.now().isoformat(timespec='seconds')} | versão {versao.VERSAO} | {texto}\n"
    try:
        caminho = caminho_do_registro()
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if caminho.exists() and caminho.stat().st_size > 2_000_000:
            caminho.replace(caminho.with_suffix(".antigo.log"))
        with caminho.open("a", encoding="utf-8") as arquivo:
            arquivo.write(linha)
    except OSError:
        try:
            from registro import registrar_erro

            registrar_erro("atualização", texto)
        except Exception:  # noqa: BLE001 - o registro nunca derruba nada
            pass


def ler_estado() -> dict:
    """O estado.json da atualizacao ({} se nao existe ou esta estragado)."""
    try:
        return json.loads((pasta_do_estado() / "estado.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def gravar_estado(estado: dict) -> None:
    """Grava o estado.json inteiro de uma vez (arquivo provisorio + troca)."""
    pasta = pasta_do_estado()
    pasta.mkdir(parents=True, exist_ok=True)
    provisorio = pasta / "estado.json.gravando"
    provisorio.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
    provisorio.replace(pasta / "estado.json")


def registrar_falha(tipo: str, versao_atual: str, versao_nova: str, motivo: str) -> None:
    """A UNICA forma de anotar que a atualizacao falhou (D-718, D-719).

    tipo: "recusada" (assinatura), "troca" (o Velopack nao conseguiu trocar e
    devolveu a anterior), "teste" (a versao nova nao passou no teste rapido).
    Grava no estado (a tela mostra FRASE_DA_FALHA uma vez por falha, pelo id)
    e no registro (a gerente le). A versao que falhou entra em "nao_tentar":
    a tarefa nao a baixa de novo a cada vez que o computador liga.
    """
    estado = ler_estado()
    nao_tentar = sorted(set(estado.get("nao_tentar", [])) | {versao_nova})
    gravar_estado({"fase": "falhou", "id": f"{tipo}-{versao_nova}", "tipo": tipo,
                   "nova": versao_nova, "anterior": versao_atual, "motivo": motivo,
                   "quando": datetime.now().isoformat(timespec="seconds"), "nao_tentar": nao_tentar})
    registrar(f"FALHOU ({tipo}) a atualização para a {versao_nova}; continua a {versao_atual}: {motivo}")


# ---------------------------------------------------------------------------
# A decisao: em que pe esta a atualizacao, e o que a tela avisa
# ---------------------------------------------------------------------------

def _mais_nova(a: str, b: str) -> bool:
    """a e mais nova que b? (versoes fora do formato contam como nao)."""
    try:
        return versao.numeros(a) > versao.numeros(b)
    except ValueError:
        return False


def situacao(estado: dict, versao_atual: str) -> tuple[str, str | None]:
    """Em que pe esta a atualizacao, lendo so o estado e a versao que roda.

    Devolve (o que e, detalhe):
    - ("falhou", id)          uma falha anotada (registrar_falha), ou uma troca
                              que o Velopack desfez (estava "aplicando" a nova e
                              o programa continua na anterior);
    - ("conferir", versao)    a versao nova ja esta no lugar, mas ainda nao
                              passou no teste rapido;
    - ("versao-nova", versao) baixada e conferida, esperando o programa fechar;
    - ("nada", None).
    Usada pela tarefa (rodar_ao_ligar) e pela tela (o_que_avisar): as duas
    decidem pela mesma conta.
    """
    fase = estado.get("fase")
    nova = estado.get("nova") or ""
    if fase == "falhou":
        return "falhou", estado.get("id") or f"falha-{nova}"
    if fase in ("pendente", "aplicando") and nova:
        if nova == versao_atual:
            return "conferir", nova
        if fase == "aplicando":
            return "falhou", f"troca-{nova}"
        if _mais_nova(nova, versao_atual):
            return "versao-nova", nova
    return "nada", None


def o_que_avisar(estado: dict, versao_atual: str, ja_vistos: set[str]) -> tuple[str, str] | None:
    """O que a janela aberta tem de mostrar agora (None = nada).

    ("versao-nova", versao): o aviso com "Reiniciar agora" e "Depois" (D-720).
    ("falhou", id): a frase da D-719, uma vez so por falha (ja_vistos guarda
    os ids ja mostrados nesta conta).
    """
    o_que, detalhe = situacao(estado, versao_atual)
    if o_que == "versao-nova":
        return "versao-nova", detalhe
    if o_que == "falhou" and detalhe not in ja_vistos:
        return "falhou", detalhe
    return None


# ---------------------------------------------------------------------------
# De onde vem as versoes (o GitHub do projeto, ou uma pasta no ensaio)
# ---------------------------------------------------------------------------

class Fonte:
    """O lugar das versoes publicadas.

    No Kaique: o GitHub do projeto (Fonte.padrao()), sem senha nem token
    (D-719; o projeto e publico, D-713). No ensaio e nos testes: uma pasta,
    como o Velopack aceita ("servidor de mentira").

    O arquivo da assinatura de uma versao fica AO LADO do pacote: no GitHub,
    no mesmo "Release" (etiqueta v<versao>); na pasta, na mesma pasta.
    """

    def __init__(self, endereco: str):
        self.endereco = str(endereco)

    @classmethod
    def padrao(cls) -> "Fonte":
        return cls(REPOSITORIO)

    @property
    def e_github(self) -> bool:
        return self.endereco.startswith("https://github.com/")

    def para_o_velopack(self):
        """O que se passa ao UpdateManager do Velopack."""
        if self.e_github:
            import velopack

            return velopack.GithubSource(self.endereco)
        return self.endereco

    def endereco_do_arquivo(self, versao_do_arquivo: str, nome: str) -> str:
        """Onde esta um arquivo publicado de uma versao (pacote ou assinatura)."""
        if self.e_github:
            return f"{self.endereco}/releases/download/v{versao_do_arquivo}/{nome}"
        return str(Path(self.endereco) / nome)

    def ler(self, versao_do_arquivo: str, nome: str, limite: int = 1_000_000) -> bytes:
        """Le um arquivo pequeno publicado (a assinatura). Levanta OSError se nao achar."""
        endereco = self.endereco_do_arquivo(versao_do_arquivo, nome)
        if not self.e_github:
            return Path(endereco).read_bytes()[:limite]
        import urllib.request

        with urllib.request.urlopen(endereco, timeout=60) as resposta:
            return resposta.read(limite)

    def baixar(self, versao_do_arquivo: str, nome: str, destino: Path) -> Path:
        """Baixa (ou copia) um arquivo publicado grande (um pacote inteiro) para destino."""
        import shutil

        destino.parent.mkdir(parents=True, exist_ok=True)
        endereco = self.endereco_do_arquivo(versao_do_arquivo, nome)
        if not self.e_github:
            shutil.copyfile(endereco, destino)
            return destino
        import urllib.request

        with urllib.request.urlopen(endereco, timeout=600) as resposta, open(destino, "wb") as saida:
            shutil.copyfileobj(resposta, saida)
        return destino


def fonte_da_linha(argumentos: list[str]) -> Fonte:
    """--fonte <pasta> (so no ensaio e nos testes); sem ele, o GitHub."""
    if ARG_FONTE in argumentos:
        posicao = argumentos.index(ARG_FONTE)
        if posicao + 1 < len(argumentos):
            return Fonte(argumentos[posicao + 1])
    return Fonte.padrao()


# ---------------------------------------------------------------------------
# O Velopack (so importado quando e preciso)
# ---------------------------------------------------------------------------

def pasta_do_programa() -> Path:
    """A pasta do EditorImpressao.exe (no Velopack, <raiz>\\current)."""
    return Path(sys.executable).resolve().parent


def update_exe() -> Path:
    """O Update.exe do Velopack (<raiz>\\Update.exe, um nivel acima de current)."""
    return pasta_do_programa().parent / "Update.exe"


def instalado_pelo_velopack() -> bool:
    """O programa empacotado esta numa instalacao do Velopack (ou num portatil dele)?

    Pelo codigo (.venv, testes) e False: nada de Velopack, nada de aviso.
    """
    return bool(getattr(sys, "frozen", False)) and update_exe().is_file()


def criar_gerente(fonte: Fonte, permitir_voltar: bool = False):
    """O UpdateManager do Velopack para esta fonte."""
    import velopack

    opcoes = velopack.UpdateOptions(AllowVersionDowngrade=permitir_voltar, MaximumDeltasBeforeFallback=10)
    return velopack.UpdateManager(fonte.para_o_velopack(), opcoes)


def versao_que_roda() -> str:
    """A versao instalada (a do Velopack, que e a do versao.py com que foi empacotada)."""
    if instalado_pelo_velopack():
        try:
            return criar_gerente(Fonte.padrao()).get_current_version()
        except Exception as erro:  # noqa: BLE001
            registrar(f"não consegui ler a versão instalada: {erro}")
    return versao.VERSAO


def _versao_assinada_do(alvo) -> assinatura.VersaoAssinada:
    """O que a assinatura tem de afirmar para o pacote que o Velopack vai baixar."""
    return assinatura.VersaoAssinada(alvo.PackageId, alvo.Version, alvo.FileName, alvo.SHA256)


def conferir_assinatura_do(fonte: Fonte, alvo, chave_publica: str | None = None) -> str | None:
    """None se a versao 'alvo' (VelopackAsset) tem a assinatura certa; senao, o motivo."""
    nome = assinatura.nome_do_arquivo_da_assinatura(alvo.PackageId, alvo.Version)
    try:
        texto = fonte.ler(alvo.Version, nome).decode("utf-8", errors="replace")
    except OSError as erro:
        return f"não achei a assinatura da versão {alvo.Version} ({erro})"
    return assinatura.conferir_versao(texto, _versao_assinada_do(alvo), chave_publica)


# ---------------------------------------------------------------------------
# O que fazer com uma versao nova (a regra, num lugar so)
# ---------------------------------------------------------------------------

def procurar_e_preparar(gerente, fonte: Fonte, programa_aberto: Callable[[], bool],
                        chave_publica: str | None = None,
                        argumentos_da_volta: list[str] | None = None) -> str:
    """Procura a versao nova e deixa tudo pronto. Devolve o que aconteceu:

    "nada-novo" | "ja-falhou" | "recusada" | "pendente" | "aplicando".

    1. Pergunta ao Velopack se ha versao nova (check_for_updates).
    2. Se essa versao ja falhou antes (registrar_falha), nao tenta de novo.
    3. Confere a ASSINATURA antes de baixar (D-724). Se nao confere, recusa:
       nada e baixado, registra a falha, a tela avisa uma vez.
    4. Baixa so o que mudou (download_updates; o Velopack confere a soma).
    5. Programa aberto: fica "pendente" (a tela mostra "Reiniciar agora" /
       "Depois", D-715/D-720); com "Depois", na proxima vez que o computador
       ligar a tarefa chega aqui com o programa fechado e troca.
    6. Programa fechado: anota "aplicando" e pede ao Velopack para trocar
       assim que este processo sair, reabrindo escondido em
       --conferir-a-versao-nova (o teste rapido). Quem chamou tem de sair logo.

    gerente: o UpdateManager do Velopack (nos testes, um falso com os mesmos
    metodos). Erros de rede sobem para quem chamou (rodar_ao_ligar), que os
    registra sem aviso na tela: sem internet nao e falha de atualizacao.
    """
    versao_atual = gerente.get_current_version()
    info = gerente.check_for_updates()
    if info is None:
        registrar(f"procurei: nenhuma versão nova (esta é a {versao_atual})")
        return "nada-novo"
    alvo = info.TargetFullRelease
    if not _mais_nova(alvo.Version, versao_atual):
        registrar(f"procurei: a publicada ({alvo.Version}) não é mais nova que a {versao_atual}")
        return "nada-novo"
    estado = ler_estado()
    if alvo.Version in estado.get("nao_tentar", []):
        registrar(f"a versão {alvo.Version} já falhou antes; espero uma mais nova")
        return "ja-falhou"
    motivo = conferir_assinatura_do(fonte, alvo, chave_publica)
    if motivo is not None:
        registrar_falha("recusada", versao_atual, alvo.Version, f"assinatura recusada: {motivo}")
        return "recusada"
    registrar(f"versão {alvo.Version} publicada e assinada pelo Samuel: baixando")
    gerente.download_updates(info)
    base = {"nova": alvo.Version, "anterior": versao_atual, "nao_tentar": estado.get("nao_tentar", []),
            "quando": datetime.now().isoformat(timespec="seconds")}
    if programa_aberto():
        gravar_estado({"fase": "pendente", **base})
        registrar(f"versão {alvo.Version} baixada; o programa está aberto: entra quando ele fechar "
                  "(\"Reiniciar agora\") ou quando o computador ligar de novo")
        return "pendente"
    gravar_estado({"fase": "aplicando", **base})
    registrar(f"versão {alvo.Version} baixada; trocando (o programa está fechado)")
    gerente.wait_exit_then_apply_updates(alvo, silent=True, restart=True,
                                         restart_args=[ARG_CONFERIR_NOVA, *(argumentos_da_volta or [])])
    return "aplicando"


# ---------------------------------------------------------------------------
# Depois de trocar: o teste rapido e, se falhar, a volta (D-718)
# ---------------------------------------------------------------------------

def teste_rapido() -> int:
    """--teste-rapido: a versao instalada abre? (0 = sim). Sem janela.

    Importa o que o programa precisa para abrir (a janela, o processamento) e
    confere que as pecas que vao dentro do pacote estao no lugar: os modelos e
    as DLLs (nos caminhos que o proprio codigo procura, como o empacotar.py), e
    no programa empacotado o motor do Kraken e o Tesseract ao lado do .exe.
    O que faltar vai para o registro.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    problemas: list[str] = []
    try:
        import ui.janela_principal  # noqa: F401 - abrir a janela importa isto
        from core import detectar_regioes, gravura_scantailor, ocr_doctr, rede_selecao, st_ferramentas

        for arquivo in (detectar_regioes.CAMINHO_MODELO, rede_selecao.CODIFICADOR, rede_selecao.DECODIFICADOR,
                        ocr_doctr.CAMINHO_MODELO, gravura_scantailor.CAMINHO_DLL, st_ferramentas.CAMINHO_DLL):
            if not Path(arquivo).is_file():
                problemas.append(f"falta {arquivo}")
        if getattr(sys, "frozen", False):
            pasta = pasta_do_programa()
            for relativo in ("motor-kraken/python/python.exe", "tesseract/tesseract.exe"):
                if not (pasta / relativo).is_file():
                    problemas.append(f"falta {relativo}")
    except Exception as erro:  # noqa: BLE001 - qualquer erro aqui e "nao abre"
        problemas.append(f"erro ao abrir: {type(erro).__name__}: {erro}")
    if problemas:
        registrar("teste rápido da versão instalada: " + "; ".join(problemas))
        return 1
    return 0


def rodar_teste_rapido() -> tuple[bool, str]:
    """Roda o --teste-rapido num processo a parte (um erro grave nao derruba quem pergunta)."""
    try:
        feito = subprocess.run([sys.executable, ARG_TESTE_RAPIDO], timeout=300,
                               env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return feito.returncode == 0, f"código {feito.returncode}"
    except (OSError, subprocess.SubprocessError) as erro:
        return False, str(erro)


def voltar_para_a_anterior(fonte: Fonte, versao_anterior: str, pasta_de_trabalho: Path | None = None,
                           aplicar: Callable[[Path], None] | None = None,
                           chave_publica: str | None = None) -> bool:
    """Volta para a versao anterior (D-718). True se a volta foi pedida ao Velopack.

    Baixa o pacote inteiro da anterior (continua publicado), CONFERE a
    assinatura dele (a volta tambem so aceita versao assinada pelo Samuel) e
    pede ao Update.exe do Velopack que o aplique quando este processo sair
    (apply --package; a troca e a mesma da atualizacao, com a pasta de reserva).
    """
    pacote = versao.ID_DO_PACOTE
    nome = f"{pacote}-{versao_anterior}-full.nupkg"
    pasta = pasta_de_trabalho or (pasta_do_estado() / "volta")
    try:
        texto = fonte.ler(versao_anterior, assinatura.nome_do_arquivo_da_assinatura(pacote, versao_anterior))
        arquivo = fonte.baixar(versao_anterior, nome, pasta / nome)
    except OSError as erro:
        registrar(f"não consegui buscar a versão {versao_anterior} para voltar: {erro}")
        return False
    esperado = assinatura.VersaoAssinada(pacote, versao_anterior, nome, assinatura.soma_sha256(arquivo))
    motivo = assinatura.conferir_versao(texto.decode("utf-8", errors="replace"), esperado, chave_publica)
    if motivo is not None:
        registrar(f"não voltei para a {versao_anterior}: {motivo}")
        return False
    (aplicar or _aplicar_pacote_quando_sair)(arquivo)
    registrar(f"voltando para a versão {versao_anterior}")
    return True


def _aplicar_pacote_quando_sair(arquivo: Path) -> None:
    """Update.exe apply --package: espera este processo sair e troca (sem reabrir)."""
    subprocess.Popen([str(update_exe()), "apply", "--silent", "--norestart",
                      "--waitPid", str(os.getpid()), "--package", str(arquivo)],
                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                     | getattr(subprocess, "DETACHED_PROCESS", 0))


def conferir_versao_nova(fonte: Fonte, versao_atual: str,
                         teste: Callable[[], tuple[bool, str]] = rodar_teste_rapido,
                         voltar: Callable[[Fonte, str], bool] | None = None) -> int:
    """--conferir-a-versao-nova: a versao que acabou de entrar abre? Se nao, volta.

    0 = a versao nova passou; 1 = falhou (e a volta foi pedida ou registrada).
    """
    estado = ler_estado()
    anterior = estado.get("anterior") or ""
    certo, detalhe = teste()
    if certo:
        gravar_estado({"fase": "ok", "nova": versao_atual, "anterior": anterior,
                       "nao_tentar": estado.get("nao_tentar", []),
                       "quando": datetime.now().isoformat(timespec="seconds")})
        registrar(f"versão {versao_atual} instalada e conferida (teste rápido certo)")
        return 0
    registrar_falha("teste", anterior, versao_atual, f"a versão nova não passou no teste rápido ({detalhe})")
    if anterior:
        (voltar or voltar_para_a_anterior)(fonte, anterior)
    return 1


# ---------------------------------------------------------------------------
# O que roda quando o computador liga (a tarefa do Windows, como SYSTEM)
# ---------------------------------------------------------------------------

def rodar_ao_ligar(fonte: Fonte, gerente=None, preparar: Callable[[object], None] | None = None,
                   programa_aberto: Callable[[], bool] | None = None,
                   conferir: Callable[[Fonte, str], int] | None = None) -> int:
    """--procurar-atualizacao. Devolve o codigo de saida (0 = sem erro).

    Nunca mostra janela. Sem internet: registra e sai (nao e falha).
    """
    try:
        gerente = gerente or criar_gerente(fonte)
        (preparar or preparar_o_computador)(gerente)
        atual = gerente.get_current_version()
        estado = ler_estado()
        o_que, detalhe = situacao(estado, atual)
        if o_que == "conferir":
            return (conferir or conferir_versao_nova)(fonte, atual)
        if o_que == "falhou" and estado.get("fase") == "aplicando":
            registrar_falha("troca", atual, estado.get("nova", "?"),
                            "o Velopack não conseguiu trocar e devolveu a versão anterior")
        procurar_e_preparar(gerente, fonte, programa_aberto or ha_programa_aberto,
                            argumentos_da_volta=_argumentos_da_fonte(fonte))
        return 0
    except Exception as erro:  # noqa: BLE001 - sem rede, GitHub fora do ar...
        registrar(f"não consegui procurar a versão nova: {type(erro).__name__}: {erro}")
        return 1


def _argumentos_da_fonte(fonte: Fonte) -> list[str]:
    """Repassa o --fonte do ensaio ao processo que o Velopack reabre."""
    return [] if fonte.e_github else [ARG_FONTE, fonte.endereco]


# ---------------------------------------------------------------------------
# A marca de "programa aberto" (mutex do Windows)
# ---------------------------------------------------------------------------

_MARCA = None  # o handle do mutex, segurado enquanto a janela esta aberta


def marcar_programa_aberto() -> None:
    """A janela chama ao abrir: cria o mutex MARCA_DE_ABERTO (some sozinho ao fechar)."""
    global _MARCA
    if _MARCA is not None or sys.platform != "win32":
        return
    import ctypes

    _MARCA = ctypes.windll.kernel32.CreateMutexW(None, False, MARCA_DE_ABERTO) or None


def ha_programa_aberto() -> bool:
    """Alguma janela do programa esta aberta (em qualquer conta)?"""
    if sys.platform != "win32":
        return False
    import ctypes

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenMutexW(0x00100000, False, MARCA_DE_ABERTO)  # SYNCHRONIZE
    if handle:
        kernel32.CloseHandle(handle)
        return True
    return False


# ---------------------------------------------------------------------------
# "Reiniciar agora" (D-720)
# ---------------------------------------------------------------------------

def aplicar_agora_e_reabrir(gerente=None) -> bool:
    """Troca para a versao ja baixada e reabre o programa (o botao "Reiniciar agora").

    A janela ja foi fechada (e gravou o trabalho) antes de chamar isto. O
    Velopack troca e reabre; como o programa mora em Arquivos de Programas, o
    Windows pode perguntar "Deseja permitir...?" (ressalva da etapa 5).
    Devolve False se nao havia versao baixada (nada muda).
    """
    try:
        gerente = gerente or criar_gerente(Fonte.padrao())
        pendente = gerente.get_update_pending_restart()
        if pendente is None:
            registrar("\"Reiniciar agora\": não achei a versão baixada")
            return False
        registrar(f"\"Reiniciar agora\": trocando para a {pendente.Version}")
        gerente.apply_updates_and_restart(pendente)
        return True
    except Exception as erro:  # noqa: BLE001
        registrar(f"\"Reiniciar agora\" não deu certo: {type(erro).__name__}: {erro}")
        return False


# ---------------------------------------------------------------------------
# A tarefa do Windows (D-714), criada pela instalacao
# ---------------------------------------------------------------------------

def xml_da_tarefa(exe: Path) -> str:
    """O XML da tarefa: ao ligar o computador (com 3 minutos de atraso), como o
    proprio sistema (SYSTEM, S-1-5-18), em prioridade baixa (7), sem janela,
    roda <exe> --procurar-atualizacao.

    Nao exige rede para comecar: a primeira rodada (logo depois de instalar)
    tambem instala o Visual C++ de dentro do pacote, que nao precisa de
    internet (D-727); sem rede, a procura so registra e sai.
    """
    from xml.sax.saxutils import escape

    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Editor de Impressão: procura e instala a versão nova quando o computador liga.</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>{ATRASO_DEPOIS_DE_LIGAR}</Delay>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Sistema">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Sistema">
    <Exec>
      <Command>{escape(str(exe))}</Command>
      <Arguments>{ARG_PROCURAR}</Arguments>
    </Exec>
  </Actions>
</Task>
"""


def _rodar(comando: list[str], tempo: int = 120) -> tuple[int, str]:
    """Roda um comando do Windows sem janela; (codigo, saida). Nunca levanta."""
    try:
        feito = subprocess.run(comando, capture_output=True, text=True, timeout=tempo,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return feito.returncode, (feito.stdout + feito.stderr).strip()
    except (OSError, subprocess.SubprocessError) as erro:
        return -1, str(erro)


def criar_tarefa(exe: Path | None = None, rodar: Callable[[list[str]], tuple[int, str]] = _rodar) -> bool:
    """Cria (ou refaz) a tarefa do Windows. Precisa de administrador."""
    import tempfile

    exe = exe or (pasta_do_programa() / Path(sys.executable).name)
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "tarefa.xml"
        arquivo.write_text(xml_da_tarefa(exe), encoding="utf-16")
        codigo, saida = rodar(["schtasks", "/Create", "/TN", NOME_DA_TAREFA, "/XML", str(arquivo), "/F"])
    registrar(f"criar a tarefa do Windows: {'certo' if codigo == 0 else 'NÃO deu certo'} ({saida})")
    return codigo == 0


def rodar_tarefa_agora(rodar: Callable[[list[str]], tuple[int, str]] = _rodar) -> bool:
    """Roda a tarefa uma vez, ja (logo depois de instalar: Visual C++ e a instalacao antiga)."""
    codigo, saida = rodar(["schtasks", "/Run", "/TN", NOME_DA_TAREFA])
    registrar(f"rodar a tarefa agora: {'certo' if codigo == 0 else 'NÃO deu certo'} ({saida})")
    return codigo == 0


def apagar_tarefa(rodar: Callable[[list[str]], tuple[int, str]] = _rodar) -> bool:
    """Apaga a tarefa (ao desinstalar)."""
    codigo, saida = rodar(["schtasks", "/Delete", "/TN", NOME_DA_TAREFA, "/F"])
    registrar(f"apagar a tarefa do Windows: {'certo' if codigo == 0 else 'NÃO deu certo'} ({saida})")
    return codigo == 0


# ---------------------------------------------------------------------------
# Preparar o computador (como SYSTEM): Visual C++ e a instalacao antiga
# ---------------------------------------------------------------------------

def _ler_versao_do_visual_c() -> tuple[int, int, int] | None:
    """A maior versao do Visual C++ 2015-2022 x64 instalada (as duas vistas do registro), ou None.

    Mesma chave e mesma regra do instalador.iss (secao [Code]), que a
    Microsoft documenta.
    """
    import winreg

    achadas = []
    for vista in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, CHAVE_DO_VISUAL_C, 0, winreg.KEY_READ | vista) as chave:
                if winreg.QueryValueEx(chave, "Installed")[0] != 1:
                    continue
                achadas.append(tuple(int(winreg.QueryValueEx(chave, nome)[0]) for nome in ("Major", "Minor", "Bld")))
        except OSError:
            continue
    return max(achadas) if achadas else None


def precisa_do_visual_c(instalada: tuple[int, int, int] | None, do_pacote: str) -> bool:
    """Roda o vc_redist se nao ha Visual C++ ou se o instalado e mais velho que o do pacote."""
    if instalada is None:
        return True
    try:
        maior, menor, build = (int(x) for x in do_pacote.split(".")[:3])
    except ValueError:
        return False
    return (maior, menor, build) > instalada


def instalar_visual_c_se_faltar(pasta: Path, ler: Callable[[], tuple | None] = _ler_versao_do_visual_c,
                                rodar: Callable[[list[str], int], tuple[int, str]] = _rodar) -> None:
    """O Visual C++ oficial que vai dentro do pacote (D-727), em silencio, so se faltar."""
    exe = pasta / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_NOME
    if not exe.is_file():
        registrar(f"Visual C++: o pacote não tem {exe} (não instalei)")
        return
    do_pacote = (pasta / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_VERSAO).read_text(encoding="utf-8").strip() \
        if (pasta / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_VERSAO).is_file() else "0.0.0"
    instalada = ler()
    if not precisa_do_visual_c(instalada, do_pacote):
        return
    codigo, _saida = rodar([str(exe), "/install", "/quiet", "/norestart"], 600)
    # 0 = instalou; 1638 = ja havia uma mais nova; 3010 = instalou e pede reiniciar
    certo = codigo in (0, 1638, 3010)
    registrar(f"Visual C++ {do_pacote}: {'instalado' if certo else 'NÃO instalado'} (código {codigo})")


def achar_instalacao_do_inno(ler_chave: Callable[[], dict | None] | None = None) -> dict | None:
    """A instalacao antiga do Inno Setup (a de 28/10 do Kaique), ou None.

    Devolve {"pasta", "desinstalador"} lidos de ...\\Uninstall\\{AppId}_is1.
    """
    dados = (ler_chave or _ler_chave_do_inno)()
    if not dados:
        return None
    desinstalador = (dados.get("UninstallString") or "").strip().strip('"')
    pasta = (dados.get("InstallLocation") or "").strip().strip('"')
    if not desinstalador or not pasta:
        return None
    return {"pasta": Path(pasta), "desinstalador": Path(desinstalador)}


def _ler_chave_do_inno() -> dict | None:
    import winreg

    for vista in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, CHAVE_DO_INNO, 0, winreg.KEY_READ | vista) as chave:
                return {nome: winreg.QueryValueEx(chave, nome)[0] for nome in ("UninstallString", "InstallLocation")}
        except OSError:
            continue
    return None


def comando_para_tirar_o_inno(antiga: dict, pasta_nova: Path) -> list[str] | None:
    """O comando que tira a instalacao antiga, ou None se for arriscado demais.

    O desinstalador do Inno tira so o que ele instalou e as pastas _internal,
    motor-kraken e tesseract DENTRO da pasta dele ([UninstallDelete] do
    instalador.iss, igual no de 28/10): nunca o %LOCALAPPDATA%\\EditorImpressao
    (os projetos do Kaique). Recusa se: o desinstalador nao esta dentro da
    pasta antiga, nao e um unins*.exe, ou a pasta antiga e a mesma (ou contem)
    a do programa novo.
    """
    pasta = Path(antiga["pasta"]).resolve()
    desinstalador = Path(antiga["desinstalador"]).resolve()
    nova = Path(pasta_nova).resolve()
    if desinstalador.parent != pasta or not desinstalador.name.lower().startswith("unins"):
        return None
    if nova == pasta or pasta in nova.parents:
        return None
    dados = os.environ.get("LOCALAPPDATA")
    if dados and (pasta == Path(dados).resolve() or Path(dados).resolve() in pasta.parents):
        return None
    return [str(desinstalador), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]


def tirar_instalacao_antiga(pasta_nova: Path, achar: Callable[[], dict | None] = achar_instalacao_do_inno,
                            rodar: Callable[[list[str], int], tuple[int, str]] = _rodar) -> None:
    """Tira a instalacao do Inno Setup (a de 28/10), se existir (D-723)."""
    antiga = achar()
    if antiga is None:
        return
    comando = comando_para_tirar_o_inno(antiga, pasta_nova)
    if comando is None:
        registrar(f"instalação antiga em {antiga['pasta']}: NÃO tirei (o caminho não parece seguro)")
        return
    codigo, saida = rodar(comando, 900)
    registrar(f"instalação antiga em {antiga['pasta']}: {'tirada' if codigo == 0 else 'NÃO tirada'} "
              f"(código {codigo}) {saida}")


def e_portatil(gerente=None) -> bool:
    """O programa e um pacote PORTATIL do Velopack (uma pasta solta, sem instalar)?

    A UNICA regra de "mexer no Windows ou nao": portatil (o ensaio no PC do
    Samuel) nunca cria tarefa, nunca roda o Visual C++, nunca tira o Inno.
    Na duvida (nao deu para perguntar ao Velopack), conta como portatil: nao mexe.
    Achado no ensaio de 16/11: o gancho "depois de atualizar" do pacote
    portatil tentou criar a tarefa (o Windows negou; nada foi criado).
    """
    try:
        return bool((gerente or criar_gerente(Fonte.padrao())).get_is_portable())
    except Exception:  # noqa: BLE001
        return True


def preparar_o_computador(gerente) -> None:
    """O que a tarefa faz antes de procurar: Visual C++ e a instalacao antiga.

    So numa instalacao de verdade (nao portatil): o ensaio roda um pacote
    portatil no PC do Samuel, que tem uma instalacao do Inno de 01/09 que nao
    pode ser tirada por um ensaio.
    """
    if e_portatil(gerente):
        return
    pasta = pasta_do_programa()
    instalar_visual_c_se_faltar(pasta)
    tirar_instalacao_antiga(pasta.parent)


# ---------------------------------------------------------------------------
# Os ganchos do Velopack e a entrada pela linha de comando
# ---------------------------------------------------------------------------

def ao_instalar(_versao: str, portatil: Callable[[], bool] = e_portatil) -> None:
    """Gancho do Velopack, depois de instalar: cria a tarefa e a roda uma vez (nunca no portatil)."""
    registrar(f"instalada a versão {_versao}")
    if portatil():
        return
    if criar_tarefa():
        rodar_tarefa_agora()


def ao_atualizar(_versao: str, portatil: Callable[[], bool] = e_portatil) -> None:
    """Gancho do Velopack, depois de atualizar: refaz a tarefa (o XML pode ter mudado). Nunca no portatil."""
    if not portatil():
        criar_tarefa()


def ao_desinstalar(_versao: str, portatil: Callable[[], bool] = e_portatil) -> None:
    """Gancho do Velopack, antes de desinstalar: desfaz os testes a distancia e apaga a tarefa.

    Os projetos ficam. Nunca no portatil.
    D-731 (17/11/2026; alternativa B da D-733): este gancho roda SEM licenca de
    administrador e e morto depois de 30 s. Por isso ele so MANDA rodar a
    tarefa "desfazer" que o ligar dos testes a distancia criou (ela roda como o
    sistema, por tras, e tira o OpenSSH se foi nosso, a regra, a conta e o
    perfil) e volta logo. Sem a tarefa (os testes nunca ligados), so anota.
    """
    if not portatil():
        from core import testes_a_distancia

        feito = testes_a_distancia.mandar_desfazer()
        registrar(f"desfazer os testes à distância (D-731): {'mandado' if feito.ok else 'NÃO mandado'}"
                  f" ({feito.mensagem})")
        apagar_tarefa()


def _rodar_o_velopack() -> None:
    """VelopackApp: atende os ganchos (o processo sai depois deles) e volta logo no resto.

    set_auto_apply_on_startup(False): a troca nunca acontece ao abrir a
    janela (pediria a licenca de administrador ao Kaique); quem troca e a
    tarefa, ou o "Reiniciar agora".
    """
    import velopack

    (velopack.App()
     .set_auto_apply_on_startup(False)
     .on_after_install_fast_callback(ao_instalar)
     .on_after_update_fast_callback(ao_atualizar)
     .on_before_uninstall_fast_callback(ao_desinstalar)
     .run())


def atender_linha_de_comando(argv: list[str]) -> int | None:
    """A UNICA entrada da atualizacao (main.py chama antes de qualquer janela).

    Devolve o codigo de saida dos modos escondidos, ou None para o programa
    abrir normalmente. Pelo codigo (.venv) e sem argumento nosso: nao importa
    o velopack, nao faz nada.
    """
    argumentos = list(argv[1:])
    primeiro = argumentos[0] if argumentos else ""
    if primeiro == ARG_TESTE_RAPIDO:
        return teste_rapido()
    nossos = (ARG_PROCURAR, ARG_CONFERIR_NOVA)
    if primeiro not in nossos and not instalado_pelo_velopack() \
            and not any(a.startswith("--veloapp") for a in argumentos):
        return None
    try:
        _rodar_o_velopack()
    except Exception as erro:  # noqa: BLE001 - o programa abre mesmo assim
        registrar(f"Velopack não iniciou: {type(erro).__name__}: {erro}")
        if primeiro not in nossos:
            return None
    fonte = fonte_da_linha(argumentos)
    if primeiro == ARG_PROCURAR:
        return rodar_ao_ligar(fonte)
    if primeiro == ARG_CONFERIR_NOVA:
        try:
            atual = criar_gerente(fonte).get_current_version()
        except Exception as erro:  # noqa: BLE001
            registrar(f"não consegui ler a versão para conferir: {erro}")
            return 1
        return conferir_versao_nova(fonte, atual)
    return None
