"""A atualizacao pela internet do Editor de Impressao (Velopack).

Etapa 3 da frente do notebook do Kaique, 16/11/2026, mudada em 17/11/2026.
Decisoes do Samuel: D-706 (atualizar "como funciona com apps", sem
reinstalar), D-713 (vem do GitHub publico do projeto), D-714 (publicada de
proposito), D-715/D-720 (com o programa aberto: aviso com "Reiniciar agora" e
"Depois"), D-718/D-719 (se falhar, volta para a versao anterior, mostra a frase
combinada e guarda o erro num registro que a gerente le daqui; nenhuma senha
dentro do programa), D-723 (Velopack), D-724 (assinatura gratis conferida antes
de instalar), D-727 (tudo dentro do instalador: o Visual C++ vai no pacote).
De 17/11/2026: D-732 ("não, faz quando o programa é aberto": a versao nova e
procurada quando o programa ABRE, nao mais quando o computador liga), D-733
(jeito 1: uma pergunta do Windows na primeira abertura cria o AJUDANTE, uma
tarefa do Windows que roda como o sistema e que a conta comum pode mandar
rodar; depois, nenhuma pergunta por atualizacao nem na volta), D-734 (com
"Depois", entra na proxima vez que o Kaique abrir, com uma espera curta antes
da janela; fechar nao troca nada), D-735 (a pergunta da primeira abertura
aparece sempre, com ou sem a senha dos testes), D-736 (aberto por um teste a
distancia, nao procura; o Samuel manda atualizar de longe pelo mesmo ajudante).

POR QUE O AJUDANTE (achado B1, 16/11): o .msi "PerMachine" do Velopack roda os
ganchos de instalar/atualizar/desinstalar SEM licenca de administrador
(CustomAction Impersonate="yes"). Por isso a tarefa nao pode mais nascer no
gancho de instalar: nasce na pergunta do Windows da primeira abertura.

COMO FUNCIONA, DO COMECO AO FIM
1. Instalacao: o gancho (ao_instalar) so anota. Nada que pede administrador.
2. Primeira abertura (preparar_na_primeira_abertura, chamada pela janela da
   senha, ui/testes_a_distancia_ui.py): UMA pergunta do Windows ("Deseja
   permitir...?"), pela mesma peca dos testes a distancia
   (core.testes_a_distancia.Executor). Dentro dela roda este .exe com
   --preparar-o-computador (preparar_como_administrador): cria o ajudante
   (criar_tarefa, xml_da_tarefa) e a tarefa "desfazer" que o apaga ao
   desinstalar (criar_as_tarefas; D-731, 17/11/2026), instala o Visual C++ de dentro do pacote se
   faltar e tira a instalacao antiga do Inno (preparar_o_computador). Se o
   Kaique digitou a senha, os passos dos testes a distancia vao na MESMA
   pergunta (core.testes_a_distancia.ligar, sem mudanca).
3. Toda abertura do programa do Kaique (procurar_ao_abrir, chamado por
   ui/aviso_de_atualizacao.ligar_na_janela): manda o ajudante rodar
   (schtasks /Run, sem pergunta: a tarefa deixa a conta comum mandar rodar).
4. O ajudante roda como o proprio sistema (SYSTEM), sem janela:
   EditorImpressao.exe --procurar-atualizacao -> rodar_ao_ligar (o nome ficou
   da etapa 3; hoje roda quando o ajudante e chamado, nunca ao ligar):
   - prepara o computador (Visual C++ e o Inno, se ainda faltar);
   - confere o resultado da ultima troca (situacao);
   - procura a versao nova (procurar_e_preparar): confere a ASSINATURA antes de
     baixar; baixa so o que mudou; programa aberto -> "pendente" (a tela
     avisa); programa fechado -> pede ao Velopack para trocar e reabrir
     escondido em --conferir-a-versao-nova. Como roda como SYSTEM, troca em
     Arquivos de Programas sem perguntar nada.
5. "Reiniciar agora" (D-720) e a proxima abertura depois do "Depois" (D-734)
   usam a mesma funcao, trocar_e_reabrir: um PowerShell escondido, na conta do
   Kaique, espera este processo sair, manda o ajudante rodar (agora com o
   programa fechado, ele troca), espera a troca e reabre o programa na conta
   do Kaique com --depois-da-troca (o ajudante, como SYSTEM, nao pode abrir a
   janela dele).
6. --conferir-a-versao-nova (conferir_e_refazer_o_ajudante): o teste rapido da
   versao nova; se falhar, volta para a anterior (D-718); se passar, refaz o
   ajudante (o XML pode ter mudado de uma versao para outra; antes era o
   gancho de atualizar, que nao tem licenca, B1).
7. A tela (ui/aviso_de_atualizacao.py) pergunta o_que_avisar de tempos em
   tempos: "versao-nova" -> o aviso com os dois botoes; "falhou" -> a frase da
   D-719, uma vez so.
8. Na conta dos testes a distancia (e_a_conta_de_testes, D-736): nada disso
   roda sozinho. O Samuel manda atualizar de longe pelo mesmo ajudante
   (comando_de_longe_para_atualizar).

ONDE FICAM AS COISAS
- estado.json e atualizacao.log em %ProgramData%\\EditorImpressao\\atualizacao\\
  (pasta_do_estado). Por que ali, e nao no %LOCALAPPDATA% do Kaique: o
  ajudante roda como SYSTEM, e a conta dos testes a distancia (por onde a
  gerente le, D-719) nao enxerga a pasta do Kaique; o ProgramData todas as
  contas leem.
- Os projetos do Kaique ficam em %LOCALAPPDATA%\\EditorImpressao
  (historico.pasta_de_dados). O Velopack troca a pasta do programa, mas NAO so
  ela: quando a pasta do programa nao aceita gravacao (a janela do Kaique, sem
  administrador, em Arquivos de Programas), ele usa uma pasta de reserva,
  %LOCALAPPDATA%\\<nome do pacote>, e grava ali Update.exe e packages\\ a cada
  abertura; e o desinstalador do .msi limpa %LOCALAPPDATA%\\<nome do pacote>
  (prova de 17/11/2026, relatorios/velopack-pasta-2026-11-17/). Por isso o
  nome do pacote (versao.ID_DO_PACOTE, "EditorImpressaoPrograma") NUNCA e o
  nome da pasta dos projetos (D-763; tests/test_nome_do_pacote.py): a pasta de
  reserva e uma pasta so do Velopack, e os projetos ficam fora do alcance dele.

A REGRA NUM LUGAR SO (CLAUDE.md §11.12): o que fazer com uma versao nova e
procurar_e_preparar; o que a tela avisa e o_que_avisar (que usa situacao); uma
falha e sempre registrar_falha; a assinatura e sempre
assinatura.conferir_versao; "o programa esta aberto" e marcar_programa_aberto
(a janela) / ha_programa_aberto (o ajudante); "chamar o ajudante" e sempre
comando_de_rodar_a_tarefa; "trocar e reabrir" e sempre trocar_e_reabrir; "e a
conta de testes" e sempre e_a_conta_de_testes; a pergunta do Windows e sempre
a peca dos testes a distancia (core.testes_a_distancia.Executor). A unica
entrada pela linha de comando e atender_linha_de_comando (main.py chama uma vez).

Nada aqui importa Qt nem ui/. O velopack so e importado quando o programa foi
instalado por ele (instalado_pelo_velopack) ou num dos modos escondidos: pelo
codigo (.venv) e nos testes, nada muda e nada fica mais lento.

Arriscado mudar: NOME_DA_TAREFA e os argumentos (o ajudante ja criado no
notebook chama exatamente estes); QUEM_PODE_MANDAR_RODAR (tirar o "AU" deixa a
conta do Kaique e a de testes sem poder chamar o ajudante; dar mais que ler e
executar deixaria a conta comum MUDAR uma tarefa que roda como SYSTEM);
FRASE_DA_FALHA (palavras combinadas com o Samuel, D-719); a ordem "assinatura
antes de baixar"; o "portatil nao mexe no Windows" (no PC do Samuel ha uma
instalacao do Inno de 01/09 que um ensaio nao pode tirar).
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
# D-733: o modo que roda DENTRO da pergunta do Windows da primeira abertura
# (ja como administrador): cria o ajudante, o Visual C++ e tira o Inno.
ARG_PREPARAR = "--preparar-o-computador"
# D-734: o programa reaberto por trocar_e_reabrir. Abre a janela normalmente;
# so serve para nao tentar trocar de novo nesta abertura (sem ele, uma troca
# que nao comecou reabriria o programa sem fim).
ARG_DEPOIS_DA_TROCA = "--depois-da-troca"

# O ajudante (D-714, D-733): a tarefa do Windows, numa pasta propria do
# Agendador. Mudou em 17/11 (D-732): nao tem mais hora para rodar (nada de
# "ao ligar o computador"); so roda quando alguem manda (schtasks /Run).
NOME_DA_TAREFA = "EditorImpressao\\Procurar versao nova"
# Quem pode o que na tarefa (SDDL): administradores e o sistema, tudo; as
# contas comuns que entraram no Windows (AU, "Authenticated Users": a do
# Kaique e a de testes), SO ler e mandar rodar (GRGX). Sem o AU, a conta do
# Kaique nao conseguiria chamar o ajudante ao abrir o programa (D-733) e o
# Samuel nao conseguiria mandar atualizar de longe (D-736).
QUEM_PODE_MANDAR_RODAR = "D:(A;;FA;;;BA)(A;;FA;;;SY)(A;;GRGX;;;AU)"

# trocar_e_reabrir (D-720 "Reiniciar agora", D-734 "Depois"): quanto o
# PowerShell escondido espera a troca antes de reabrir o programa de qualquer
# jeito (na versao que estiver), e quanto espera a mais quando a versao nova
# falhou e o Velopack esta voltando para a anterior (D-718).
LIMITE_DA_TROCA_S = 300
ESPERA_DA_VOLTA_S = 60

# A marca de "o programa esta aberto" (um mutex com nome, do Windows). A
# janela cria; a tarefa (que roda como SYSTEM, em outra sessao) so consulta.
MARCA_DE_ABERTO = "Global\\EditorImpressao-programa-aberto"
# D-748 (Samuel, 17/11/2026: "Sim"): a janelinha da D-742 segura esta marca
# (um mutex so da sessao do Kaique) do comeco ao fim. O brasao girando
# (ui/brasao_girando.antes_de_mostrar) poe a MARCA_DE_ABERTO, que faz a
# janelinha sumir, e so aparece quando esta marca sumiu: os dois nunca ficam
# juntos na tela.
MARCA_DA_JANELINHA = "Local\\EditorImpressao-janelinha"

# Os textos da tela (portugues, sem jargao, sem emoji; CLAUDE.md §3).
TITULO_DA_VERSAO_NOVA = "Versão nova do programa"
FRASE_DA_VERSAO_NOVA = (
    "Chegou uma versão nova do Editor de Impressão.\n\n"
    "Salve o seu trabalho e reinicie o programa para usar a versão nova.\n\n"
    "Se escolher \"Depois\", a versão nova entra sozinha na próxima vez que você abrir o programa.")
# D-742 (Samuel, 17/11/2026: "Sim"), palavra por palavra: a janelinha da
# abertura em que a versao nova entra (D-734, depois do "Depois").
TEXTO_DA_JANELINHA = "Atualizando o programa, espere um pouco..."
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


def fonte_da_linha(argumentos: list[str], de_teste: Callable[[], "Fonte | None"] | None = None) -> Fonte:
    """A UNICA escolha de onde vem as versoes, nos modos escondidos (o ajudante, o conferir).

    1. --fonte <pasta> (o ensaio e os testes passam na linha de comando);
    2. senao, a fonte de teste da etapa 5 (fonte_de_teste: um arquivo que so
       o administrador grava; no notebook do Kaique ele nao existe);
    3. senao, o GitHub do projeto (Fonte.padrao()).
    Em todos os casos a assinatura e conferida igual (D-724).
    """
    if ARG_FONTE in argumentos:
        posicao = argumentos.index(ARG_FONTE)
        if posicao + 1 < len(argumentos):
            return Fonte(argumentos[posicao + 1])
    return (de_teste or fonte_de_teste)() or Fonte.padrao()


# A fonte de teste da etapa 5 (pedido da gerente, 17/11/2026): para a etapa 5
# testar a atualizacao de mentira no programa INSTALADO de verdade, sem
# publicar no GitHub. So vale se o arquivo for do administrador ou do sistema
# (o dono do arquivo): uma conta comum consegue criar arquivo no ProgramData,
# mas ele fica com ela de dona, e e ignorado. Mesmo valendo, so entra versao
# com a assinatura do Samuel (D-724). O Kaique nunca tem este arquivo.
ARQUIVO_DA_FONTE_DE_TESTE = "fonte-de-teste.txt"
DONOS_ACEITOS = ("S-1-5-32-544", "S-1-5-18")  # Administradores, o sistema


def caminho_da_fonte_de_teste() -> Path:
    """%ProgramData%\\EditorImpressao\\fonte-de-teste.txt (lido na hora: os testes trocam a variavel)."""
    return pasta_do_estado().parent / ARQUIVO_DA_FONTE_DE_TESTE


def _dono_do_arquivo(caminho: Path) -> str | None:
    """O SID do dono do arquivo ("S-1-5-32-544"...), ou None se nao deu para ler. So Windows."""
    if sys.platform != "win32":
        return None
    import ctypes
    from ctypes import wintypes

    advapi32, kernel32 = ctypes.windll.advapi32, ctypes.windll.kernel32
    dono, descritor = ctypes.c_void_p(), ctypes.c_void_p()
    # SE_FILE_OBJECT = 1, OWNER_SECURITY_INFORMATION = 1
    if advapi32.GetNamedSecurityInfoW(wintypes.LPCWSTR(str(caminho)), 1, 1, ctypes.byref(dono),
                                      None, None, None, ctypes.byref(descritor)) != 0:
        return None
    texto = wintypes.LPWSTR()
    try:
        if not advapi32.ConvertSidToStringSidW(dono, ctypes.byref(texto)):
            return None
        sid = texto.value
        kernel32.LocalFree(texto)
        return sid
    finally:
        kernel32.LocalFree(descritor)


def fonte_de_teste(dono: Callable[[Path], str | None] = _dono_do_arquivo) -> "Fonte | None":
    """A fonte de teste da etapa 5, ou None (o normal: o arquivo nao existe).

    O arquivo tem uma linha: a pasta com as versoes de mentira (como a pasta do
    ensaio). Ignorado, com uma linha no registro, se: o dono nao e o
    administrador nem o sistema, ou a linha nao e uma pasta que existe.
    """
    arquivo = caminho_da_fonte_de_teste()
    try:
        if not arquivo.is_file():
            return None
        linhas = arquivo.read_text(encoding="utf-8-sig").strip().splitlines()
    except OSError:
        return None
    if dono(arquivo) not in DONOS_ACEITOS:
        registrar(f"fonte de teste ignorada: {arquivo} não é do administrador")
        return None
    pasta = linhas[0].strip().strip('"') if linhas else ""
    if not pasta or not Path(pasta).is_dir():
        registrar(f"fonte de teste ignorada: \"{pasta}\" não é uma pasta")
        return None
    registrar(f"fonte de teste (etapa 5): as versões vêm de {pasta}")
    return Fonte(pasta)


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
       "Depois", D-715/D-720); com "Depois", na proxima vez que o Kaique abrir
       o programa (D-734), trocar_e_reabrir chama o ajudante de novo com o
       programa fechado, e ele chega aqui e troca.
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
        registrar(f"versão {alvo.Version} baixada; o programa está aberto: entra no \"Reiniciar agora\" "
                  "ou na próxima vez que o programa abrir")
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
# O que o ajudante faz quando e chamado (a tarefa do Windows, como SYSTEM)
# ---------------------------------------------------------------------------

def rodar_ao_ligar(fonte: Fonte, gerente=None, preparar: Callable[[object], None] | None = None,
                   programa_aberto: Callable[[], bool] | None = None,
                   conferir: Callable[[Fonte, str], int] | None = None) -> int:
    """--procurar-atualizacao: o que o ajudante faz. Devolve o codigo de saida (0 = sem erro).

    O nome ficou da etapa 3 (os testes antigos chamam por ele). Desde 17/11
    (D-732) o ajudante NAO roda ao ligar o computador: roda quando o programa
    abre (procurar_ao_abrir), no "Reiniciar agora" e na abertura depois do
    "Depois" (trocar_e_reabrir) e quando o Samuel manda de longe (D-736).
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


def _marca_existe(nome: str) -> bool:
    """O mutex `nome` existe agora (alguem o segura)? Fora do Windows: False."""
    if sys.platform != "win32":
        return False
    import ctypes

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenMutexW(0x00100000, False, nome)  # SYNCHRONIZE
    if handle:
        kernel32.CloseHandle(handle)
        return True
    return False


def ha_programa_aberto() -> bool:
    """Alguma janela do programa esta aberta (em qualquer conta)?

    Desde 17/11/2026 (D-748), o brasao girando tambem conta: enquanto ele gira,
    o programa esta abrindo, e o ajudante nao troca os arquivos por baixo dele.
    """
    return _marca_existe(MARCA_DE_ABERTO)


def ha_janelinha() -> bool:
    """A janelinha "Atualizando o programa..." (D-742) esta na tela, ou se montando? (D-748)

    Le MARCA_DA_JANELINHA na hora da chamada (os testes trocam o nome).
    """
    return _marca_existe(MARCA_DA_JANELINHA)


def _rodar(comando: list[str], tempo: int = 120) -> tuple[int, str]:
    """Roda um comando do Windows sem janela; (codigo, saida). Nunca levanta."""
    try:
        feito = subprocess.run(comando, capture_output=True, text=True, timeout=tempo,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return feito.returncode, (feito.stdout + feito.stderr).strip()
    except (OSError, subprocess.SubprocessError) as erro:
        return -1, str(erro)


# ---------------------------------------------------------------------------
# Trocar e reabrir: "Reiniciar agora" (D-720) e a abertura depois do "Depois" (D-734)
# ---------------------------------------------------------------------------

def script_da_janelinha(marca: str = MARCA_DE_ABERTO, limite_s: int | None = None,
                        marca_da_janelinha: str | None = None) -> str:
    """D-742: o PowerShell da janelinha "Atualizando o programa, espere um pouco...".

    ONDE ELA VIVE: a troca acontece FORA do programa (o .exe tem de ter saido
    para o Velopack trocar os arquivos dele), num PowerShell escondido na
    conta do Kaique (script_de_trocar_e_reabrir). A janelinha e uma janela do
    Windows (Windows Forms) aberta por esse mesmo PowerShell, numa linha de
    execucao separada (um "runspace" STA). Por isso ela nao espera nada da
    troca nem a troca espera por ela: um erro nela nao impede a troca nem a
    volta para a anterior (D-718).

    Como ela e: pequena, no meio da tela, por cima, sem titulo e SEM botao
    (ControlBox desligado; nenhum Button), so o texto TEXTO_DA_JANELINHA.
    Some quando o programa abre: quando a marca de "programa aberto"
    (`marca`, a mesma de marcar_programa_aberto) aparece, ou, no pior caso,
    depois de `limite_s` (o tempo inteiro da troca, da volta e da abertura).
    Se o programa ja abriu enquanto ela se montava, ela nem aparece.
    Medido no PC do Samuel (17/11/2026): a primeira letra do Windows Forms
    num processo novo leva uns 5,5 s, entao a janelinha aparece uns 6 s
    depois de o programa sair; a etapa 5 mede no notebook.
    D-748 (17/11/2026): a primeira coisa que ela faz e pegar a
    MARCA_DA_JANELINHA, e so a solta depois de fechar. O brasao girando poe a
    marca do programa aberto e espera esta sumir antes de aparecer. A ordem
    (cada um poe a sua marca ANTES de olhar a do outro) garante que os dois
    nunca ficam juntos: ou a janelinha ve o brasao e nem aparece, ou o brasao
    ve a janelinha e espera ela fechar.
    `marca`, `limite_s` e `marca_da_janelinha` so mudam nos testes.
    Arriscado: ShowDialog em vez de Show + DoEvents (o teste deixaria de poder
    trocar a janela por uma de mentira); tirar o limite (a janelinha ficaria
    para sempre se o programa nao abrir); pegar a MARCA_DA_JANELINHA depois
    de olhar a marca de aberto (os dois poderiam aparecer juntos).
    """
    limite = limite_s if limite_s is not None else LIMITE_DA_TROCA_S + ESPERA_DA_VOLTA_S + 120
    minha = marca_da_janelinha if marca_da_janelinha is not None else MARCA_DA_JANELINHA
    return "\n".join([
        "$ErrorActionPreference = 'SilentlyContinue'",
        "Add-Type -AssemblyName System.Windows.Forms",
        "Add-Type -AssemblyName System.Drawing",
        "$janela = New-Object System.Windows.Forms.Form",
        "$janela.Text = ''",
        "$janela.ControlBox = $false",
        "$janela.FormBorderStyle = 'FixedDialog'",
        "$janela.StartPosition = 'CenterScreen'",
        "$janela.ShowInTaskbar = $false",
        "$janela.TopMost = $true",
        "$janela.ClientSize = New-Object System.Drawing.Size(400, 90)",
        "$texto = New-Object System.Windows.Forms.Label",
        f"$texto.Text = {_aspas_do_powershell(TEXTO_DA_JANELINHA)}",
        "$texto.Dock = 'Fill'",
        "$texto.TextAlign = 'MiddleCenter'",
        "$texto.Font = New-Object System.Drawing.Font('Segoe UI', 11)",
        "$janela.Controls.Add($texto)",
        # D-748: a marca da janelinha ANTES de olhar se o programa ja abriu
        f"$minha = [System.Threading.Mutex]::new($false, {_aspas_do_powershell(minha)})",
        "$aberto = $null",
        # o programa ja abriu enquanto a janelinha se montava: ela nem aparece (nada pisca)
        f"if ([System.Threading.Mutex]::TryOpenExisting({_aspas_do_powershell(marca)}, [ref]$aberto))"
        " { $aberto.Dispose() } else {",
        "  $janela.Show()",
        f"  $fim = (Get-Date).AddSeconds({int(limite)})",
        "  while ((Get-Date) -lt $fim) {",
        f"    if ([System.Threading.Mutex]::TryOpenExisting({_aspas_do_powershell(marca)}, [ref]$aberto))"
        " { $aberto.Dispose(); break }",
        "    [System.Windows.Forms.Application]::DoEvents()",
        "    Start-Sleep -Milliseconds 200",
        "  }",
        "}",
        "$janela.Close()",
        "$minha.Dispose()",
    ])


def _linhas_da_janelinha() -> tuple[list[str], list[str]]:
    """D-742: o que script_de_trocar_e_reabrir acrescenta no comeco e no fim quando ha janelinha.

    Comeco: abre a janelinha numa linha de execucao separada (STA, como o
    Windows Forms pede) e segue sem esperar. Fim (depois de reabrir o
    programa): espera a janelinha sumir sozinha, para este PowerShell nao
    sair antes e leva-la junto.
    """
    inicio = [
        "$jRun = [runspacefactory]::CreateRunspace(); $jRun.ApartmentState = 'STA'; $jRun.Open()",
        "$jPs = [powershell]::Create(); $jPs.Runspace = $jRun",
        f"[void]$jPs.AddScript({_aspas_do_powershell(script_da_janelinha())})",
        "$jEspera = $jPs.BeginInvoke()",
    ]
    fim = ["try { [void]$jPs.EndInvoke($jEspera) } catch { }", "$jRun.Close()"]
    return inicio, fim


def script_de_trocar_e_reabrir(exe: Path, pid: int, arquivo_do_estado: Path, janelinha: bool = False) -> str:
    """O PowerShell que troca a versao e reabre o programa NA CONTA DO KAIQUE.

    Por que um PowerShell a parte, e nao este programa: a troca mexe nos
    arquivos de <raiz>\\current, e este .exe mora la; ele precisa ter saido.
    Por que nao o ajudante: ele roda como SYSTEM, e o que o SYSTEM abre nao
    aparece na tela do Kaique.

    Na ordem:
    1. espera este processo (pid) sair: a janela ja gravou o trabalho e a
       marca de "programa aberto" some junto (ha_programa_aberto);
    2. manda o ajudante rodar (comando_de_rodar_a_tarefa): com o programa
       fechado, ele confere a assinatura e troca (procurar_e_preparar);
    3. espera a troca: enquanto o estado for "pendente" com o ajudante
       rodando, ou "aplicando" (o Velopack trocando e o teste rapido), ate
       LIMITE_DA_TROCA_S; se a versao nova nao passou no teste rapido, espera
       mais ESPERA_DA_VOLTA_S (a volta para a anterior, D-718);
    4. reabre o programa com ARG_DEPOIS_DA_TROCA (na versao que estiver).
    Nenhum passo pede administrador: nenhuma pergunta do Windows (D-733).
    `janelinha` (D-742, so a abertura depois do "Depois"; o "Reiniciar agora"
    fica como era): antes do passo 1 abre a janelinha (script_da_janelinha)
    e, depois do passo 4, espera ela sumir. Os passos 1 a 4 ficam iguais,
    letra por letra.
    """
    pasta, nome = NOME_DA_TAREFA.rsplit("\\", 1)
    rodar = " ".join(_aspas_do_powershell(p) for p in comando_de_rodar_a_tarefa()[1:])
    estado = _aspas_do_powershell(str(arquivo_do_estado))
    linhas = [
        "$ErrorActionPreference = 'SilentlyContinue'",
        f"Wait-Process -Id {int(pid)} -Timeout 120",
        f"& schtasks {rodar} | Out-Null",
        "$rodou = ($LASTEXITCODE -eq 0)",
        f"$fim = (Get-Date).AddSeconds({LIMITE_DA_TROCA_S})",
        "$fase = ''",
        "if ($rodou) {",
        "  Start-Sleep -Seconds 3",
        "  while ((Get-Date) -lt $fim) {",
        "    $fase = ''; $tipo = ''",
        f"    try {{ $e = Get-Content -Raw -LiteralPath {estado} | ConvertFrom-Json; $fase = $e.fase;"
        " $tipo = $e.tipo } catch { }",
        f"    $tarefa = (Get-ScheduledTask -TaskPath {_aspas_do_powershell(chr(92) + pasta + chr(92))}"
        f" -TaskName {_aspas_do_powershell(nome)}).State",
        # o ajudante terminou sem trocar (sem internet, assinatura recusada...):
        # nao espera o limite inteiro. "Queued" = ainda vai comecar.
        "    if ($fase -eq 'pendente' -and \"$tarefa\" -ne 'Running' -and \"$tarefa\" -ne 'Queued') { break }",
        "    if ($fase -ne 'pendente' -and $fase -ne 'aplicando') { break }",
        "    Start-Sleep -Seconds 2",
        "  }",
        # so a versao que nao passou no teste rapido volta para a anterior (D-718)
        f"  if ($fase -eq 'falhou' -and $tipo -eq 'teste') {{ Start-Sleep -Seconds {ESPERA_DA_VOLTA_S} }}",
        "}",
        f"Start-Process -FilePath {_aspas_do_powershell(str(exe))}"
        f" -ArgumentList {_aspas_do_powershell(ARG_DEPOIS_DA_TROCA)}",
    ]
    if janelinha:
        inicio, fim = _linhas_da_janelinha()
        linhas = [linhas[0], *inicio, *linhas[1:], *fim]
    return "\n".join(linhas)


def _aspas_do_powershell(texto: str) -> str:
    """Texto entre aspas simples do PowerShell (a aspa simples dobra)."""
    return "'" + str(texto).replace("'", "''") + "'"


def _lancar_escondido(script: str) -> None:
    """Roda o script num PowerShell escondido e solto (nao espera; sobrevive a este processo).

    O script vai em -EncodedCommand (UTF-16 em base64): nada de arquivo
    provisorio para apagar depois.
    """
    import base64

    codificado = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    subprocess.Popen(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                      "-WindowStyle", "Hidden", "-EncodedCommand", codificado],
                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                     | getattr(subprocess, "DETACHED_PROCESS", 0))


def trocar_e_reabrir(lancar: Callable[[str], None] = _lancar_escondido, exe: Path | None = None,
                     pid: int | None = None, janelinha: bool = False) -> bool:
    """A UNICA forma de trocar para a versao ja baixada e reabrir o programa.

    Usada pelo "Reiniciar agora" (D-720; a janela ja fechou gravando) e pela
    abertura depois do "Depois" (D-734, trocar_antes_de_abrir; a janela nem
    abriu; so esta com a janelinha da D-742). Quem chama tem de sair logo: o
    script espera este processo sair.
    Devolve False se nao deu para comecar (o programa segue na versao de hoje).
    """
    exe = exe or (pasta_do_programa() / Path(sys.executable).name)
    try:
        lancar(script_de_trocar_e_reabrir(exe, pid or os.getpid(), pasta_do_estado() / "estado.json",
                                          janelinha=janelinha))
        registrar("trocar e reabrir: o ajudante foi chamado; o programa volta sozinho")
        return True
    except Exception as erro:  # noqa: BLE001 - nunca derruba a janela
        registrar(f"trocar e reabrir não começou: {type(erro).__name__}: {erro}")
        return False


def aplicar_agora_e_reabrir(trocar: Callable[[], bool] | None = None) -> bool:
    """O botao "Reiniciar agora" (D-720): troca para a versao ja baixada e reabre.

    A janela ja foi fechada (e gravou o trabalho) antes de chamar isto. Antes
    de 17/11 o proprio Velopack trocava daqui (apply_updates_and_restart) e,
    como o programa mora em Arquivos de Programas, o Windows perguntava
    "Deseja permitir...?". Agora quem troca e o ajudante (D-733): nenhuma
    pergunta. Devolve False se a troca nao comecou.
    """
    return (trocar or trocar_e_reabrir)()


def trocar_antes_de_abrir(argumentos: list[str], instalado: Callable[[], bool] | None = None,
                          conta_de_testes: Callable[[], bool] | None = None,
                          portatil: Callable[[], bool] | None = None,
                          ler: Callable[[], dict] = ler_estado,
                          versao_atual: Callable[[], str] | None = None,
                          trocar: Callable[[], bool] | None = None) -> bool:
    """D-734: com "Depois", a versao nova entra na proxima vez que o Kaique abrir.

    Chamada por atender_linha_de_comando ANTES de qualquer janela. True = a
    troca comecou e este processo tem de sair sem abrir a janela: o
    trocar_e_reabrir reabre o programa ja na versao nova (a "espera curta
    antes da janela"). False = abre normalmente.

    So troca se: e o programa instalado (nao portatil), nao e a conta dos
    testes a distancia (D-736), nao e a reabertura de uma troca
    (ARG_DEPOIS_DA_TROCA, para nunca ficar reabrindo sem fim) e ha versao nova
    ja baixada e conferida esperando (situacao == "versao-nova"). Fechar o
    programa nao troca nada: so esta abertura e o "Reiniciar agora" trocam.
    """
    if ARG_DEPOIS_DA_TROCA in argumentos:
        return False
    if not (instalado or instalado_pelo_velopack)():
        return False
    if (conta_de_testes or e_a_conta_de_testes)() or (portatil or e_portatil)():
        return False
    o_que, detalhe = situacao(ler(), (versao_atual or versao_que_roda)())
    if o_que != "versao-nova":
        return False
    registrar(f"abrindo o programa: a versão {detalhe} estava esperando (\"Depois\"); trocando antes da janela")
    # D-742: so nesta abertura aparece a janelinha "Atualizando o programa...".
    return (trocar or (lambda: trocar_e_reabrir(janelinha=True)))()


# ---------------------------------------------------------------------------
# Chamar o ajudante: ao abrir (D-732) e de longe (D-736)
# ---------------------------------------------------------------------------

def comando_de_rodar_a_tarefa() -> list[str]:
    """O comando que manda o ajudante rodar (um lugar so: abrir, trocar, de longe).

    Nao pede administrador: a tarefa deixa as contas comuns mandarem rodar
    (QUEM_PODE_MANDAR_RODAR). Volta logo; o ajudante roda por tras.
    """
    return ["schtasks", "/Run", "/TN", NOME_DA_TAREFA]


def e_a_conta_de_testes(usuario: str | None = None) -> bool:
    """O programa esta rodando na conta dos testes a distancia (D-717, D-736)?

    A conta tem nome fixo (core.testes_a_distancia.NOME_DA_CONTA). E a unica
    regra de "aberto por um teste a distancia".
    """
    from core.testes_a_distancia import NOME_DA_CONTA

    nome = usuario if usuario is not None else (os.environ.get("USERNAME") or "")
    return nome.strip().lower() == NOME_DA_CONTA.lower()


def procurar_ao_abrir(rodar: Callable[[list[str]], tuple[int, str]] = _rodar,
                      conta_de_testes: Callable[[], bool] | None = None,
                      portatil: Callable[[], bool] | None = None) -> bool:
    """D-732: o programa abriu; manda o ajudante procurar a versao nova.

    Chamada por ui/aviso_de_atualizacao.ligar_na_janela (so no programa
    instalado). Nada na tela: o ajudante procura e baixa por tras; se chegar
    versao nova com o programa aberto, a janela avisa (D-715). Nao procura na
    conta dos testes a distancia (D-736) nem no pacote portatil do ensaio.
    True se o ajudante foi chamado.
    """
    if (conta_de_testes or e_a_conta_de_testes)():
        return False
    if (portatil or e_portatil)():
        return False
    codigo, saida = rodar(comando_de_rodar_a_tarefa())
    if codigo != 0:
        registrar(f"abrir o programa: não consegui chamar o ajudante ({saida})")
    return codigo == 0


def comando_de_longe_para_atualizar(endereco: str) -> str:
    """D-736: o que o Samuel roda no PC dele para o notebook do Kaique atualizar.

    Entra pela conta de testes (o comando de longe, D-705) e manda o MESMO
    ajudante rodar: mesma assinatura (D-724), mesma volta se falhar (D-718).
    Se o Kaique estiver com o programa aberto, a versao fica "pendente" e a
    janela dele mostra o aviso de salvar e reiniciar (D-715, D-720, D-734).
    O registro do que aconteceu: comando_de_longe_para_ler_o_registro.
    """
    from core.testes_a_distancia import NOME_DA_CONTA

    partes = comando_de_rodar_a_tarefa()
    return f'ssh {NOME_DA_CONTA}@{endereco} {" ".join(partes[:-1])} "{partes[-1]}"'


def comando_de_longe_para_ler_o_registro(endereco: str) -> str:
    """D-719/D-736: ler daqui o registro da atualizacao do notebook do Kaique."""
    from core.testes_a_distancia import NOME_DA_CONTA

    return (f'ssh {NOME_DA_CONTA}@{endereco} type '
            '"C:\\ProgramData\\EditorImpressao\\atualizacao\\atualizacao.log"')


# ---------------------------------------------------------------------------
# O ajudante: a tarefa do Windows (D-714, D-733), criada na primeira abertura
# ---------------------------------------------------------------------------

def xml_da_tarefa(exe: Path) -> str:
    """O XML do ajudante: como o proprio sistema (SYSTEM, S-1-5-18), em
    prioridade baixa (7), sem janela, roda <exe> --procurar-atualizacao.

    Mudou em 17/11 (D-732, D-733): SEM hora para rodar (nada de "ao ligar o
    computador"); so quando alguem manda (comando_de_rodar_a_tarefa). E com o
    SecurityDescriptor QUEM_PODE_MANDAR_RODAR: as contas comuns (a do Kaique,
    a de testes) podem mandar rodar, mas nao mudar a tarefa.

    Nao exige rede para comecar: sem rede, a procura so registra e sai.
    """
    from xml.sax.saxutils import escape

    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Editor de Impressão: procura e instala a versão nova quando o programa pede.</Description>
    <SecurityDescriptor>{QUEM_PODE_MANDAR_RODAR}</SecurityDescriptor>
  </RegistrationInfo>
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
    <AllowStartOnDemand>true</AllowStartOnDemand>
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


def criar_tarefa(exe: Path | None = None, rodar: Callable[[list[str]], tuple[int, str]] = _rodar) -> bool:
    """Cria (ou refaz) o ajudante. Precisa de administrador: so roda dentro da
    pergunta da primeira abertura (preparar_como_administrador) ou como SYSTEM
    depois de uma troca (conferir_e_refazer_o_ajudante)."""
    import tempfile

    exe = exe or (pasta_do_programa() / Path(sys.executable).name)
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "tarefa.xml"
        arquivo.write_text(xml_da_tarefa(exe), encoding="utf-16")
        codigo, saida = rodar(["schtasks", "/Create", "/TN", NOME_DA_TAREFA, "/XML", str(arquivo), "/F"])
    registrar(f"criar a tarefa do Windows: {'certo' if codigo == 0 else 'NÃO deu certo'} ({saida})")
    return codigo == 0


def rodar_tarefa_agora(rodar: Callable[[list[str]], tuple[int, str]] = _rodar) -> bool:
    """Manda o ajudante rodar uma vez, ja (o mesmo comando de procurar_ao_abrir)."""
    codigo, saida = rodar(comando_de_rodar_a_tarefa())
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
                                rodar: Callable[[list[str], int], tuple[int, str]] = _rodar) -> bool:
    """O Visual C++ oficial que vai dentro do pacote (D-727), em silencio, so se faltar.

    Devolve False so quando tentou instalar e deu erro (D-749: a preparacao
    conta como nao feita); sem o instalador no pacote ou sem precisar, True.
    """
    exe = pasta / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_NOME
    if not exe.is_file():
        registrar(f"Visual C++: o pacote não tem {exe} (não instalei)")
        return True
    do_pacote = (pasta / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_VERSAO).read_text(encoding="utf-8").strip() \
        if (pasta / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_VERSAO).is_file() else "0.0.0"
    instalada = ler()
    if not precisa_do_visual_c(instalada, do_pacote):
        return True
    codigo, _saida = rodar([str(exe), "/install", "/quiet", "/norestart"], 600)
    # 0 = instalou; 1638 = ja havia uma mais nova; 3010 = instalou e pede reiniciar
    certo = codigo in (0, 1638, 3010)
    registrar(f"Visual C++ {do_pacote}: {'instalado' if certo else 'NÃO instalado'} (código {codigo})")
    return certo


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
                            rodar: Callable[[list[str], int], tuple[int, str]] = _rodar) -> bool:
    """Tira a instalacao do Inno Setup (a de 28/10), se existir (D-723).

    Devolve False so quando tentou tirar e o desinstalador deu erro (D-749).
    Quando o caminho nao parece seguro, nao tira DE PROPOSITO e devolve True:
    perguntar de novo a cada abertura nao mudaria nada.
    """
    antiga = achar()
    if antiga is None:
        return True
    comando = comando_para_tirar_o_inno(antiga, pasta_nova)
    if comando is None:
        registrar(f"instalação antiga em {antiga['pasta']}: NÃO tirei (o caminho não parece seguro)")
        return True
    codigo, saida = rodar(comando, 900)
    registrar(f"instalação antiga em {antiga['pasta']}: {'tirada' if codigo == 0 else 'NÃO tirada'} "
              f"(código {codigo}) {saida}")
    return codigo == 0


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


def preparar_o_computador(gerente) -> bool:
    """O que a tarefa faz antes de procurar: Visual C++ e a instalacao antiga.

    So numa instalacao de verdade (nao portatil): o ensaio roda um pacote
    portatil no PC do Samuel, que tem uma instalacao do Inno de 01/09 que nao
    pode ser tirada por um ensaio. Devolve False se uma das duas deu erro
    (D-749); as duas sempre sao tentadas.
    """
    if e_portatil(gerente):
        return True
    pasta = pasta_do_programa()
    visual_c = instalar_visual_c_se_faltar(pasta)
    inno = tirar_instalacao_antiga(pasta.parent)
    return visual_c is not False and inno is not False


# ---------------------------------------------------------------------------
# A pergunta do Windows da primeira abertura (D-733, D-735)
# ---------------------------------------------------------------------------

def preparar_como_administrador(gerente=None, criar: Callable[[], bool] | None = None,
                                preparar: Callable[[object], None] | None = None,
                                portatil: Callable[[object], bool] | None = None) -> int:
    """--preparar-o-computador: o que roda DENTRO da pergunta do Windows da
    primeira abertura, ja como administrador (D-733). Devolve o codigo de saida.

    Cria as tarefas do programa (criar_as_tarefas: o ajudante e a tarefa
    "desfazer", D-731) e faz o resto que pede licenca, pela mesma
    regra de sempre (preparar_o_computador: o Visual C++ de dentro do pacote,
    se faltar, e a instalacao antiga do Inno). Nunca no pacote portatil do
    ensaio (e_portatil). Tudo vai para o registro da atualizacao.

    D-749 (Samuel, 17/11/2026: "Sim"): devolve 0 SO se tudo deu certo. Se uma
    parte deu erro no meio (uma tarefa nao foi criada, o Visual C++ ou o
    desinstalador do Inno falhou, ou um erro inesperado), devolve 1: o passo
    da pergunta anota esse codigo e a primeira abertura conta a preparacao
    como nao feita (a pergunta volta, preparo_deu_certo). `preparar` que
    devolve None (nada a dizer) conta como certo.
    """
    try:
        gerente = gerente or criar_gerente(Fonte.padrao())
    except Exception as erro:  # noqa: BLE001
        registrar(f"preparar o computador: não consegui perguntar ao Velopack ({erro}); não mexi em nada")
        return 1
    if (portatil or e_portatil)(gerente):
        registrar("preparar o computador: pacote portátil, não mexi no Windows")
        return 0
    try:
        certo = (criar or criar_as_tarefas)()
        preparado = (preparar or preparar_o_computador)(gerente)
    except Exception as erro:  # noqa: BLE001 - erro no meio: conta como nao feito (D-749)
        registrar(f"preparar o computador: erro no meio ({type(erro).__name__}: {erro}); conta como não feito")
        return 1
    return 0 if certo and preparado is not False else 1


def criar_as_tarefas() -> bool:
    """As duas tarefas que a pergunta da primeira abertura cria (ja como administrador).

    1. o ajudante da atualizacao (criar_tarefa, D-733);
    2. a tarefa "desfazer" (core.testes_a_distancia.preparar_o_desfazer;
       D-731, pergunta (a) do relatorio da construcao, 17/11/2026): existe
       SEMPRE, com ou sem os testes a distancia, e e ela quem apaga o
       ajudante ao desinstalar (o gancho de desinstalar roda sem
       administrador e nao consegue; ver ao_desinstalar). Se os testes ja
       foram ligados, ela ja tem o desfazer inteiro e fica como esta.
    True so se as duas deram certo; cada uma vai para o registro.
    """
    from core import testes_a_distancia

    certo = criar_tarefa()
    desfazer = testes_a_distancia.preparar_o_desfazer()
    registrar(f"criar a tarefa do desfazer (D-731): {'certo' if desfazer.ok else 'NÃO deu certo'}"
              f" ({desfazer.mensagem})")
    return certo and desfazer.ok


def arquivo_do_preparo() -> Path:
    """D-749: onde o passo da pergunta anota como o --preparar-o-computador terminou."""
    return pasta_do_estado() / "preparo.txt"


def passo_de_preparar_o_computador(exe: Path | None = None, marca: str = ""):
    """O passo da pergunta da primeira abertura: roda este .exe com
    --preparar-o-computador, escondido, e espera ele terminar.

    E um Passo da peca dos testes a distancia (core.testes_a_distancia.Passo),
    para ir na MESMA pergunta do Windows que o ligar usa (uma regra so para
    "pedir licenca", CLAUDE.md §11.12). Nao para a pergunta se der errado:
    quem anota o que deu certo e o proprio --preparar-o-computador, no
    registro da atualizacao; os passos dos testes a distancia, se houver
    senha, continuam.

    D-749 (17/11/2026): o passo anota em arquivo_do_preparo() "<marca>
    comecou" antes de rodar e "<marca> <codigo de saida>" depois. A `marca`
    (nova a cada pergunta) separa esta vez de uma anotacao velha. Quem le e
    preparo_deu_certo: so "<marca> 0" e preparacao feita.
    """
    from core.testes_a_distancia import Passo

    exe = exe or (pasta_do_programa() / Path(sys.executable).name)
    arquivo = arquivo_do_preparo()
    anotar = f"Set-Content -LiteralPath {_aspas_do_powershell(str(arquivo))} -Encoding ASCII -Value"
    return Passo("Preparar o computador: o ajudante da atualização, o Visual C++ e tirar a instalação "
                 "antiga (D-733)",
                 f"try {{ New-Item -ItemType Directory -Force -Path {_aspas_do_powershell(str(arquivo.parent))}"
                 f" | Out-Null; {anotar} {_aspas_do_powershell(marca + ' comecou')};"
                 f" $p = Start-Process -FilePath {_aspas_do_powershell(str(exe))}"
                 f" -ArgumentList {_aspas_do_powershell(ARG_PREPARAR)} -WindowStyle Hidden -Wait -PassThru;"
                 f" {anotar} ({_aspas_do_powershell(marca + ' ')} + $p.ExitCode) }}"
                 " catch { }")


def preparo_deu_certo(marca: str, resultado) -> bool:
    """D-749 (Samuel, 17/11/2026: "Sim"): o "Sim" da pergunta do Windows terminou com a preparacao feita?

    A UNICA regra de "o computador esta preparado". Le o que o passo anotou
    nesta vez (a `marca` desta pergunta):
    - "<marca> 0": o --preparar-o-computador terminou sem erro -> feito;
    - "<marca> comecou" (parou no meio) ou outro codigo -> NAO feito;
    - nada desta vez (o Windows nem chegou ao passo, ou a peca de mentira dos
      testes, que nao roda nada): vale o resultado da pergunta inteira.
    """
    try:
        conteudo = arquivo_do_preparo().read_text(encoding="utf-8-sig", errors="replace").strip()
    except OSError:
        conteudo = ""
    if marca and conteudo.startswith(marca + " "):
        return conteudo[len(marca) + 1:].strip() == "0"
    return bool(getattr(resultado, "ok", False))


def preparar_na_primeira_abertura(senha: str):
    """A pergunta do Windows da primeira abertura (D-733, D-735). Devolve o
    Resultado da peca dos testes a distancia (core.testes_a_distancia.Resultado).

    Aparece SEMPRE, com ou sem a senha (D-735):
    - com a senha: chama core.testes_a_distancia.ligar (a porta unica, sem
      mudanca) com a peca que fala com o Windows "acrescida" do passo de
      preparar o computador. Assim o preparo e os passos dos testes vao numa
      pergunta so, e ligar continua guardando o estado e escolhendo o aviso;
    - sem a senha ("Agora não", ou a opcao desligada): so o passo de preparar,
      na mesma peca (executor_atual), numa pergunta so.
    Se o Kaique disser "Nao", fica anotado no registro e a pergunta volta na
    proxima abertura (D-741, falta_a_pergunta_do_windows); com o "Sim" E a
    preparacao feita (preparo_deu_certo, D-749), a marca fica gravada e ela
    nunca mais aparece. "Sim" com a preparacao parada no meio: volta tambem.
    Quem chama: ui/testes_a_distancia_ui.primeira_vez_se_preciso.
    """
    import uuid

    from core import testes_a_distancia as td

    marca = uuid.uuid4().hex                          # D-749: esta pergunta
    preparo = [passo_de_preparar_o_computador(marca=marca)]
    base = td.executor_atual()

    class _ComOPreparo(td.Executor):
        """A mesma peca de hoje, com o preparo antes dos passos que ela receber."""

        def aplicar(self, passos, senha_dos_testes):
            return base.aplicar([*preparo, *passos], senha_dos_testes)

    if senha:
        td.definir_executor(_ComOPreparo())
        try:
            resultado = td.ligar(senha)
        finally:
            td.definir_executor(base)
    else:
        resultado = base.aplicar(preparo, "")
    if resultado.cancelado:
        registrar("primeira abertura: o Kaique disse \"Não\" à pergunta do Windows; o ajudante da "
                  "atualização não foi criado; a pergunta volta na próxima abertura (D-741)")
        return resultado
    if not resultado.ok:
        registrar(f"primeira abertura: a pergunta do Windows não deu certo ({resultado.mensagem})")
    # D-741: com o "Sim" e a preparacao feita, nunca mais pergunta. D-749 (17/11/2026): se a
    # preparacao deu erro no meio, conta como nao feita e a pergunta volta, como depois do "Nao".
    if not preparo_deu_certo(marca, resultado):
        registrar("primeira abertura: o Kaique disse \"Sim\", mas a preparação do computador não terminou "
                  "bem; conta como não feita e a pergunta volta na próxima abertura (D-749)")
        return resultado
    import configuracoes

    configuracoes.escrever(CHAVE_PERGUNTA_DO_WINDOWS_RESPONDIDA, True)
    return resultado


# D-741: a marca de "a pergunta do Windows da primeira abertura ja teve o Sim"
# (configuracoes.PADROES; por conta do Windows, como a marca da senha).
CHAVE_PERGUNTA_DO_WINDOWS_RESPONDIDA = "atualizacao_computador_preparado"


def falta_a_pergunta_do_windows() -> bool:
    """D-741 (Samuel, 17/11/2026: "Sim"): a pergunta do Windows da primeira abertura ainda nao teve o "Sim"?

    A UNICA regra de "ela aparece de novo nesta abertura". Depois de um "Nao",
    volta a cada abertura do programa instalado, ate o "Sim"; depois do "Sim",
    nunca mais. D-749: um "Sim" cuja preparacao deu erro no meio conta como
    nao feito (a marca nao e gravada). Quem marca e preparar_na_primeira_abertura; quem pergunta e
    ui/testes_a_distancia_ui.primeira_vez_se_preciso (que ja deixa de fora o
    codigo, D-728, e a conta de testes, D-736).
    """
    import configuracoes

    return not configuracoes.ler(CHAVE_PERGUNTA_DO_WINDOWS_RESPONDIDA)


# ---------------------------------------------------------------------------
# Os ganchos do Velopack e a entrada pela linha de comando
# ---------------------------------------------------------------------------

def ao_instalar(_versao: str, portatil: Callable[[], bool] = e_portatil) -> None:
    """Gancho do Velopack, depois de instalar: so anota.

    Ate 16/11 criava a tarefa aqui. Achado B1: o .msi roda este gancho SEM
    licenca de administrador, e a tarefa nunca nasceria. Desde 17/11 (D-733)
    o ajudante nasce na pergunta do Windows da primeira abertura
    (preparar_na_primeira_abertura). `portatil` ficou para quem ja chamava assim.
    """
    registrar(f"instalada a versão {_versao}")


def ao_atualizar(_versao: str, portatil: Callable[[], bool] = e_portatil) -> None:
    """Gancho do Velopack, depois de atualizar: nada que peca licenca (achado B1).

    Refazer o ajudante (o XML pode mudar de uma versao para outra) passou para
    conferir_e_refazer_o_ajudante, que roda como SYSTEM logo depois da troca.
    """


def ao_desinstalar(_versao: str, portatil: Callable[[], bool] = e_portatil) -> None:
    """Gancho do Velopack, antes de desinstalar: desfaz os testes a distancia e apaga a tarefa.

    Os projetos ficam. Nunca no portatil.
    D-731 (17/11/2026; alternativa B da D-733): este gancho roda SEM licenca de
    administrador e e morto depois de 30 s. Por isso ele so MANDA rodar a
    tarefa "desfazer" que o ligar dos testes a distancia criou (ela roda como o
    sistema, por tras, e tira o OpenSSH se foi nosso, a regra, a conta e o
    perfil) e volta logo. Sem a tarefa (os testes nunca ligados), so anota.
    Desde 17/11/2026 (D-731, pergunta (a)): a tarefa "desfazer" existe sempre
    (nasce na pergunta da primeira abertura, criar_as_tarefas) e apaga tambem
    o ajudante da atualizacao e a si mesma. O apagar_tarefa daqui ficou (sem
    administrador ele falha, e o registro anota); quem apaga de fato e o desfazer.
    """
    if not portatil():
        from core import testes_a_distancia

        feito = testes_a_distancia.mandar_desfazer()
        registrar(f"desfazer os testes à distância (D-731): {'mandado' if feito.ok else 'NÃO mandado'}"
                  f" ({feito.mensagem})")
        apagar_tarefa()


def conferir_e_refazer_o_ajudante(fonte: Fonte, versao_atual: str,
                                  conferir: Callable[[Fonte, str], int] | None = None,
                                  criar: Callable[[], bool] | None = None,
                                  portatil: Callable[[], bool] | None = None) -> int:
    """--conferir-a-versao-nova: o teste rapido (conferir_versao_nova) e, se a
    versao nova passou, refaz o ajudante com o XML desta versao.

    Roda como SYSTEM (o Velopack o reabre do ajudante, depois de trocar), por
    isso pode refazer a tarefa sem perguntar nada (antes era o gancho de
    atualizar, sem licenca: achado B1). Nunca no portatil do ensaio.
    """
    codigo = (conferir or conferir_versao_nova)(fonte, versao_atual)
    if codigo == 0 and not (portatil or e_portatil)():
        (criar or criar_tarefa)()
    return codigo


def _rodar_o_velopack() -> None:
    """VelopackApp: atende os ganchos (o processo sai depois deles) e volta logo no resto.

    set_auto_apply_on_startup(False): a troca nunca acontece ao abrir a
    janela pelo proprio Velopack (pediria a licenca de administrador ao
    Kaique); quem troca e o ajudante (D-733), chamado por trocar_e_reabrir.
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

    No programa instalado, antes de abrir a janela, olha se ha versao nova
    esperando do "Depois" (D-734, trocar_antes_de_abrir): se a troca comecou,
    devolve 0 e o programa sai sem janela; o trocar_e_reabrir o reabre ja na
    versao nova.
    """
    argumentos = list(argv[1:])
    primeiro = argumentos[0] if argumentos else ""
    if primeiro == ARG_TESTE_RAPIDO:
        return teste_rapido()
    nossos = (ARG_PROCURAR, ARG_CONFERIR_NOVA, ARG_PREPARAR)
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
    if primeiro == ARG_PREPARAR:
        return preparar_como_administrador()
    if primeiro == ARG_CONFERIR_NOVA:
        try:
            atual = criar_gerente(fonte).get_current_version()
        except Exception as erro:  # noqa: BLE001
            registrar(f"não consegui ler a versão para conferir: {erro}")
            return 1
        return conferir_e_refazer_o_ajudante(fonte, atual)
    try:
        if trocar_antes_de_abrir(argumentos):
            return 0
    except Exception as erro:  # noqa: BLE001 - o programa abre mesmo assim, na versao de hoje
        registrar(f"abrir o programa: não consegui olhar a versão esperando: {type(erro).__name__}: {erro}")
    return None
