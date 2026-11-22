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
2. Primeira abertura (preparar_ao_abrir -> preparar_na_primeira_abertura,
   rodados POR TRAS pela janela da senha, ui/testes_a_distancia_ui.py): UMA
   pergunta do Windows ("Deseja permitir...?"), pela peca unica do Windows
   (core.windows.pedir_licenca; 4 consertos, 21/11/2026). Dentro dela roda este .exe com
   --preparar-o-computador (preparar_como_administrador): cria o ajudante
   (criar_tarefa, xml_da_tarefa) e a tarefa "desfazer" que o apaga ao
   desinstalar (criar_as_tarefas; D-731, 17/11/2026), instala o Visual C++ de dentro do pacote se
   faltar e tira a instalacao antiga do Inno (preparar_o_computador). Nesta
   entrega a senha digitada nao liga os testes a distancia (D-825, opcao B).
   "Preparado" e o que o Windows mostra, lido de volta
   (o_que_falta_no_computador), nunca uma marca do programa.
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
  abertura; e o desinstalador do .msi (1.2.161) apaga %LOCALAPPDATA%\\<titulo
  do pacote> inteira (provas de 17/11/2026, relatorios/velopack-pasta-2026-11-17/
  e relatorios/nome-pacote-2026-11-17/). Por isso nem o nome do pacote
  (versao.ID_DO_PACOTE, "EditorImpressaoPrograma") nem o titulo
  (empacotar.TITULO_DO_PACOTE, "Editor de Impressão") sao o nome da pasta dos
  projetos (D-763; tests/test_nome_do_pacote.py): o que o Velopack grava e
  apaga fica em pastas so dele, e os projetos ficam fora do alcance dele.

A REGRA NUM LUGAR SO (CLAUDE.md §11.12): o que fazer com uma versao nova e
procurar_e_preparar; o que a tela avisa e o_que_avisar (que usa situacao); uma
falha e sempre registrar_falha; a assinatura e sempre
assinatura.conferir_versao; "o programa esta aberto" e marcar_programa_aberto
(a janela) / ha_programa_aberto (o ajudante); "chamar o ajudante" e sempre
comando_de_rodar_a_tarefa; "trocar e reabrir" e sempre trocar_e_reabrir; "e a
conta de testes" e sempre e_a_conta_de_testes; a pergunta do Windows e sempre
pedir_licenca_ao_windows (a peca unica, core.windows); "o computador esta
preparado" e sempre o_que_falta_no_computador (lido no Windows). A unica
entrada pela linha de comando e atender_linha_de_comando (main.py chama uma vez).
Volta 4 (22/11/2026, D-828): "o programa ainda roda?" antes de trocar e sempre
ha_programa_aberto (a marca da janela e a lista de processos do Windows); o
pedido de troca ao Velopack e sempre GerenteComAMarcaDaTroca (criar_gerente),
que so troca com a MARCA_DA_TROCA segura (segurar_a_marca_da_troca: o script
da troca ou o vigia); "ha uma troca acontecendo?" e sempre troca_em_andamento;
"o programa abre sozinho no fim" e sempre o script da troca (ou o so de
reabrir, abrir_quando_a_troca_acabar).

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
import time
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
# 4 consertos (21/11/2026): de 300 para 900 s. Com 300 s, uma troca mais demorada
# (a etapa 5 mediu de 7 a 23 min, com o motor do Kraken dentro) fazia o script
# reabrir o programa no meio; o Velopack o fechava a forca e a troca era anotada
# como falha (defeitos 3 e 4 da revisao de 18/11). Sem o motor, a conta do estudo
# da 2 a 3 min mais o teste rapido; 900 s da folga para o notebook do Kaique. O
# script para antes, assim que a troca termina. Seguro mudar: o numero (limiar).
LIMITE_DA_TROCA_S = 900
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
# Volta 4 (22/11/2026, D-828: "abrir o programa pelo atalho no meio da troca nao estraga a troca"): a MARCA DA TROCA.
# Existe enquanto uma troca de versao esta acontecendo, segurada por quem acompanha a troca do comeco ao fim: o
# script da troca na conta do Kaique ("Reiniciar agora", "Depois"; script_de_trocar_e_reabrir) ou, na troca que o
# ajudante faz sem o script (o Kaique fechou o programa durante o download; o atualizar de longe), o vigia que o
# ajudante lanca (script_do_vigia_da_troca). "Global" porque o vigia roda como o sistema, noutra sessao. Some sozinha
# quando quem a segura termina, ate se ele cair (o Windows apaga o mutex com o ultimo processo que o segura). Quem le:
# a abertura comum do programa (troca_em_andamento) e o ajudante antes de lancar o vigia (segurar_a_marca_da_troca).
# Arriscado: mudar o nome (os scripts ja lancados de uma versao seguram o nome antigo) ou tirar o "Global\\".
MARCA_DA_TROCA = "Global\\EditorImpressao-trocando"
# "Alguem vai reabrir o programa no fim da troca", na sessao do Kaique: o script da troca a segura do comeco ao fim
# (ele reabre); um clique no atalho no meio de uma troca SEM script lanca o script so de reabrir, que a pega uma vez
# so (o segundo clique ve a marca e nao lanca outro; dois ao mesmo tempo: so o que a criou reabre).
MARCA_DE_REABRIR = "Local\\EditorImpressao-vai-reabrir"
# As fases do estado.json em que a marca da troca pode existir: os dois que a seguram so comecam depois de o estado
# estar numa delas ("pendente": o script da troca so e lancado com a versao esperando; "aplicando": o ajudante grava
# antes de lancar o vigia e de pedir a troca; "falhou": a volta para a anterior, D-718, ainda acompanhada). So serve
# para nao carregar a peca do Windows (core.windows, ~30 ms) em toda abertura comum; quem decide e a marca, lida no
# Windows. Arriscado: tirar uma fase daqui (o clique no meio dessa fase deixaria de ser segurado).
FASES_EM_QUE_HA_TROCA = ("pendente", "aplicando", "falhou")

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
    """Grava o estado.json inteiro de uma vez (arquivo provisorio + troca).

    Volta 4 (22/11/2026): a troca do nome tenta de novo por ate ~3 s se o Windows disser que o arquivo esta em uso
    ou sem acesso naquele instante (um leitor que o segura aberto: um antivirus, ou um script de versao de antes, que
    le com o Get-Content; os nossos leem deixando trocar, _linha_de_ler_a_fase). Depois disso, o erro sobe como antes.
    """
    pasta = pasta_do_estado()
    pasta.mkdir(parents=True, exist_ok=True)
    provisorio = pasta / "estado.json.gravando"
    provisorio.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
    for tentativa in range(30):
        try:
            provisorio.replace(pasta / "estado.json")
            return
        except PermissionError:
            if tentativa == 29:
                raise
            time.sleep(0.1)


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
    - ("nada", None)          tambem "esperando-o-motor" (volta 2, medio 2): a versao
                              existe, mas nao pode entrar sem o motor do Kraken; nada
                              e anunciado e nada e trocado.
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


class TrocaSemAMarca(RuntimeError):
    """A troca nao pode comecar: ninguem segura a MARCA_DA_TROCA (volta 4). procurar_e_preparar a trata."""


class GerenteComAMarcaDaTroca:
    """O UpdateManager do Velopack com a nossa protecao em volta da troca (volta 4, 22/11/2026; D-779: "o que fazemos
    para ele nao dar defeito"; D-828).

    Tudo passa direto para o Velopack, menos o pedido de troca (`wait_exit_then_apply_updates`, que so
    procurar_e_preparar faz): antes, a MARCA_DA_TROCA tem de estar segura (segurar_a_marca_da_troca: o script da
    troca ja a segura, ou o vigia e lancado agora). Sem ela, levanta TrocaSemAMarca e o Velopack nem e chamado. E o
    unico jeito de o programa pedir uma troca ao Velopack (criar_gerente sempre devolve este), entao toda troca, com
    ou sem o script, tem a marca: uma regra so (CLAUDE.md §11.12). `segurar` so muda nos testes.
    Arriscado: chamar o Velopack direto para trocar (a troca ficaria sem a marca e um clique no atalho a estragaria).
    """

    def __init__(self, gerente, segurar: Callable[[], bool] | None = None) -> None:
        """Guarda o UpdateManager de verdade."""
        self._gerente = gerente
        self._segurar = segurar

    def __getattr__(self, nome: str):
        """O resto e o do Velopack, sem mudar nada."""
        return getattr(self._gerente, nome)

    def wait_exit_then_apply_updates(self, alvo, *args, **kwargs):
        """Pede a troca ao Velopack so com a marca da troca segura; senao, TrocaSemAMarca."""
        if not (self._segurar or segurar_a_marca_da_troca)():
            raise TrocaSemAMarca("não deu para segurar a marca da troca")
        return self._gerente.wait_exit_then_apply_updates(alvo, *args, **kwargs)


def criar_gerente(fonte: Fonte, permitir_voltar: bool = False):
    """O UpdateManager do Velopack para esta fonte, com a protecao da troca (GerenteComAMarcaDaTroca)."""
    import velopack

    opcoes = velopack.UpdateOptions(AllowVersionDowngrade=permitir_voltar, MaximumDeltasBeforeFallback=10)
    return GerenteComAMarcaDaTroca(velopack.UpdateManager(fonte.para_o_velopack(), opcoes))


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
                        argumentos_da_volta: list[str] | None = None,
                        motor_no_lugar: Callable[[], bool] | None = None) -> str:
    """Procura a versao nova e deixa tudo pronto. Devolve o que aconteceu:

    "nada-novo" | "ja-falhou" | "recusada" | "sem-motor" | "pendente" | "aplicando".

    1. Pergunta ao Velopack se ha versao nova (check_for_updates).
    2. Se essa versao ja falhou antes (registrar_falha), nao tenta de novo.
    3. Confere a ASSINATURA antes de baixar (D-724). Se nao confere, recusa:
       nada e baixado, registra a falha, a tela avisa uma vez.
    3b. Sem o motor do Kraken no lugar dele (motor_esta_no_lugar): NAO baixa nem anuncia a versao (volta 2, medio 2
       do relatorio 1, 21/11/2026). Ela nao pode entrar (a troca apagaria o unico arquivo do motor que veio no
       instalador), entao nao pode aparecer como pronta: um "pendente" anterior vira "esperando-o-motor", que a tela e a
       abertura leem como "nada" (situacao). Registra; o ajudante tenta de novo da proxima vez. Nenhum texto novo na tela.
    4. Baixa so o que mudou (download_updates; o Velopack confere a soma).
    5. Programa aberto: fica "pendente" (a tela mostra "Reiniciar agora" /
       "Depois", D-715/D-720); com "Depois", na proxima vez que o Kaique abrir
       o programa (D-734), trocar_e_reabrir chama o ajudante de novo com o
       programa fechado, e ele chega aqui e troca.
    6. Programa fechado: anota "aplicando" e pede ao Velopack para trocar
       assim que este processo sair, reabrindo escondido em
       --conferir-a-versao-nova (o teste rapido). Quem chamou tem de sair logo.
       Volta 4: "fechado" e conferido no Windows (ha_programa_aberto) e o pedido
       so sai com a marca da troca segura (GerenteComAMarcaDaTroca); sem ela
       (TrocaSemAMarca) volta a "pendente" e entra na proxima abertura.

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
    if not (motor_no_lugar or motor_esta_no_lugar)():
        if estado.get("fase") == "pendente":
            gravar_estado({**estado, "fase": "esperando-o-motor", "quando": datetime.now().isoformat(timespec="seconds")})
        registrar(f"versão {alvo.Version} publicada e assinada, mas o motor do Kraken ainda não está no lugar dele: "
                  "não baixo nem anuncio esta versão (tento de novo da próxima vez)")
        return "sem-motor"
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
    try:
        gerente.wait_exit_then_apply_updates(alvo, silent=True, restart=True,
                                             restart_args=[ARG_CONFERIR_NOVA, *(argumentos_da_volta or [])])
    except TrocaSemAMarca as erro:
        # Volta 4: sem a marca da troca segura, a troca nao comeca (um clique no atalho no meio a estragaria). A
        # versao continua esperando; a proxima abertura a troca pelo script, que segura a marca (D-734).
        gravar_estado({"fase": "pendente", **base})
        registrar(f"versão {alvo.Version}: não troco agora ({erro}); entra na próxima vez que o programa abrir")
        return "pendente"
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
    O que faltar vai para o registro. O motor do Kraken: achado e conferido pelas funcoes unicas de core/ocr_kraken
    (no programa instalado, em <raiz>\\motor-kraken\\<versao>; a ficha e o tamanho de cada arquivo).
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
            if not (pasta_do_programa() / "tesseract" / "tesseract.exe").is_file():
                problemas.append("falta tesseract/tesseract.exe")
            # o motor do Kraken: a busca e a conferencia unicas de core/ocr_kraken (4 consertos, 21/11/2026; antes um
            # caminho escrito aqui, current\motor-kraken, que a atualizacao sem o motor nunca tem)
            from core import ocr_kraken

            motor = ocr_kraken.achar_pasta_do_motor()
            if motor is None:
                problemas.append("falta o motor do Kraken em " + ", ".join(map(str, ocr_kraken.lugares_do_motor())))
            else:
                problemas += ocr_kraken.conferir_motor(motor)
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
                   conferir: Callable[[Fonte, str], int] | None = None,
                   motor: Callable[[], bool] | None = None) -> int:
    """--procurar-atualizacao: o que o ajudante faz. Devolve o codigo de saida (0 = sem erro).

    Antes de procurar: prepara o computador (Visual C++, Inno) e poe o motor do Kraken no lugar dele, se ainda nao
    estiver (garantir_o_motor; 4 consertos, 21/11/2026; nunca no portatil).

    O nome ficou da etapa 3 (os testes antigos chamam por ele). Desde 17/11
    (D-732) o ajudante NAO roda ao ligar o computador: roda quando o programa
    abre (procurar_ao_abrir), no "Reiniciar agora" e na abertura depois do
    "Depois" (trocar_e_reabrir) e quando o Samuel manda de longe (D-736).
    Nunca mostra janela. Sem internet: registra e sai (nao e falha).
    """
    try:
        gerente = gerente or criar_gerente(fonte)
        (preparar or preparar_o_computador)(gerente)
        if not e_portatil(gerente):
            try:
                (motor or garantir_o_motor)()
            except Exception as erro:  # noqa: BLE001 - o motor nunca impede a procura (volta 2, medio 1)
                registrar(f"motor do Kraken: erro inesperado ({type(erro).__name__}: {erro})")
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


def o_que_roda_do_programa(ler: Callable[[Path], list | None] | None = None) -> list[str] | None:
    """Os programas que rodam agora de dentro da pasta do programa (<raiz>\\current), fora este processo, lidos no
    Windows pela peca unica (core.windows.programas_rodando_de): ["EditorImpressao.exe (5648)", ...], [] se nenhum,
    None se o Windows nao deu a lista. `ler` so muda nos testes."""
    if ler is None:
        from core import windows

        ler = windows.programas_rodando_de
    lista = ler(pasta_do_programa())
    if lista is None:
        return None
    return [f"{Path(caminho).name} ({pid})" for pid, caminho in lista if pid != os.getpid()]


# Volta 4 (22/11/2026): quanto o ajudante espera o que ainda roda de `current` terminar (o programa fechando, um clique
# no atalho que sai sozinho) antes de desistir de trocar desta vez. Seguro mudar: o numero (limiar, CLAUDE.md §6).
ESPERA_O_PROGRAMA_FECHAR_S = 30


def ha_programa_aberto(roda: Callable[[], list | None] | None = None, dormir: Callable[[float], None] = time.sleep,
                       instalado: Callable[[], bool] | None = None) -> bool:
    """O programa esta aberto, ou ainda rodando? A UNICA pergunta que o ajudante faz antes de pedir a troca.

    1. A marca da janela (MARCA_DE_ABERTO; desde 17/11/2026, D-748, o brasao girando tambem a poe): aberto.
    2. Volta 4 (D-828, 22/11/2026: "o nosso programa garante que o programa terminou de fechar antes de a troca
       comecar"): no programa instalado, a lista de processos do Windows (o_que_roda_do_programa). A marca some
       quando a janela fecha, mas o processo ainda pode estar gravando; e um clique no atalho no meio da troca abre um
       processo de `current` por um instante. Sem a marca e com algo ainda rodando, espera ate
       ESPERA_O_PROGRAMA_FECHAR_S; se continuar, conta como aberto (nao troca desta vez; o registro diz o que roda).
       A lista que nao deu para ler conta como aberto: nunca se troca sem ter conferido.
    Pelo codigo (nao instalado) so a marca, como antes. `roda`, `dormir` e `instalado` so mudam nos testes.
    Arriscado: trocar sem a lista (o Velopack fecharia a forca o programa que ainda grava).
    """
    if _marca_existe(MARCA_DE_ABERTO):
        return True
    if not (instalado or instalado_pelo_velopack)():
        return False
    ler = roda or o_que_roda_do_programa
    fim = time.monotonic() + ESPERA_O_PROGRAMA_FECHAR_S
    esperou = False
    while True:
        agora = ler()
        if agora == []:
            if esperou:
                registrar("antes de trocar: o que rodava do programa terminou; pode trocar")
            return False
        if time.monotonic() >= fim:
            o_que = ", ".join(agora) if agora else "não deu para ler a lista de programas do Windows"
            registrar(f"antes de trocar: ainda roda do programa ({o_que}); não troco agora")
            return True
        if not esperou:
            o_que = ", ".join(agora) if agora else "não deu para ler a lista de programas do Windows"
            registrar(f"antes de trocar: ainda roda do programa ({o_que}); espero até "
                      f"{ESPERA_O_PROGRAMA_FECHAR_S} s")
            esperou = True
        dormir(1)


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


def _linha_de_ler_a_fase(estado: str) -> str:
    """O pedaco de PowerShell que le a fase e o tipo do estado.json (`estado` ja entre aspas do PowerShell). Lugar
    unico: o script da troca e o vigia da troca leem o estado assim. Deixa $lido = $true so se leu.
    Enquanto le (milissegundos, a cada 2 s), o arquivo nao pode ser trocado pelo nome (o Windows diz "acesso negado"
    a quem grava, mesmo deixando apagar: provado na volta 4); por isso gravar_estado tenta de novo por um instante.
    `-ErrorAction Stop`: o arquivo que nao existe (ou nao abre) vai para o catch e $lido fica falso; sem isso, com o
    'SilentlyContinue' dos scripts, o erro passava calado e "lido" valia para uma fase vazia (achado por um teste de
    verdade do vigia). Arriscado: tirar o Stop (o vigia soltaria a marca no meio da troca)."""
    return (f"try {{ $e = Get-Content -Raw -LiteralPath {estado} -ErrorAction Stop"
            " | ConvertFrom-Json -ErrorAction Stop;"
            " $fase = $e.fase; $tipo = $e.tipo; $lido = $true } catch { }")


def _linha_da_espera_da_volta() -> str:
    """O pedaco de PowerShell que espera a volta para a anterior (D-718) quando a versao nova nao passou no teste
    rapido. Lugar unico: o script da troca e o vigia da troca."""
    return f"if ($fase -eq 'falhou' -and $tipo -eq 'teste') {{ Start-Sleep -Seconds {ESPERA_DA_VOLTA_S} }}"


def _linhas_da_marca_existe() -> list[str]:
    """A funcao de PowerShell `MarcaExiste <nome>`: a marca (mutex) existe agora? "Sem licenca para abrir" quer dizer
    que EXISTE (o vigia roda como o sistema e o Windows nao deixa a conta comum abrir a marca dele): a mesma regra de
    core.windows.marca_existe. Outro erro tambem conta como "existe" (espera ate o limite; nunca reabre no meio)."""
    return [
        "function MarcaExiste([string]$nome) {",
        "  $m = $null",
        "  try { if ([System.Threading.Mutex]::TryOpenExisting($nome, [ref]$m)) { $m.Dispose(); return $true }"
        " ; return $false } catch { return $true }",
        "}",
    ]


def script_do_vigia_da_troca(arquivo_do_estado: Path) -> str:
    """O vigia da troca que o AJUDANTE faz sem o script da troca (volta 4, 22/11/2026; D-828 e o pedido da gerente:
    "a troca feita pelo ajudante sem o script tambem tem de usar a mesma marca").

    Quando: o ajudante (como o sistema) achou a versao nova com o programa fechado e nenhum script da troca rodando
    (o Kaique fechou o programa durante o download; o atualizar de longe, D-736). Ele lanca este PowerShell solto pela
    peca (na pasta do sistema; nunca de `current`) ANTES de pedir a troca ao Velopack. O vigia segura a MARCA_DA_TROCA
    enquanto o estado for "aplicando" (o Velopack trocando e o teste rapido da versao nova), ate LIMITE_DA_TROCA_S; se a
    versao nova nao passou no teste rapido, mais ESPERA_DA_VOLTA_S (a volta, D-718). So para quando LEU o estado com
    outra fase (um estado que nao deu para ler nao solta a marca antes da hora). Nao reabre nada: o sistema nao abre
    janela na tela do Kaique; quem reabre depois de um clique no atalho e o script so de reabrir
    (abrir_quando_a_troca_acabar). Nenhuma pergunta do Windows. Arriscado: soltar a marca antes de a troca acabar.
    """
    estado = _aspas_do_powershell(str(arquivo_do_estado))
    return "\n".join([
        "$ErrorActionPreference = 'SilentlyContinue'",
        f"$marcaDaTroca = [System.Threading.Mutex]::new($false, {_aspas_do_powershell(MARCA_DA_TROCA)})",
        f"$fim = (Get-Date).AddSeconds({LIMITE_DA_TROCA_S})",
        "$fase = 'aplicando'; $tipo = ''",
        "while ((Get-Date) -lt $fim) {",
        "  $lido = $false",
        "  " + _linha_de_ler_a_fase(estado),
        "  if ($lido -and $fase -ne 'aplicando') { break }",
        "  Start-Sleep -Seconds 2",
        "}",
        _linha_da_espera_da_volta(),
        "$marcaDaTroca.Dispose()",
    ])


def script_de_trocar_e_reabrir(exe: Path, pid: int, arquivo_do_estado: Path, janelinha: bool = False,
                               so_reabrir: bool = False) -> str:
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

    Volta 4 (22/11/2026, D-828): (a) a primeira linha pega a MARCA_DA_TROCA e a MARCA_DE_REABRIR e as segura ate o fim
    (este script acompanha a troca e reabre o programa): o clique no atalho nesse tempo sai em silencio
    (troca_em_andamento) e nao estraga a troca; as duas nascem antes de a peca ver o sinal de vida, entao ja existem
    quando o programa que pediu a troca sai. (b) Reabre o programa na pasta dele (Set-Location), porque a peca lanca
    este PowerShell na pasta do sistema. (c) `so_reabrir` (o clique no atalho no meio de uma troca SEM script, a do
    vigia): nao espera processo nem chama o ajudante; pega so a MARCA_DE_REABRIR (se outro ja a pegou, nao faz nada),
    espera a MARCA_DA_TROCA sumir (ate LIMITE_DA_TROCA_S + ESPERA_DA_VOLTA_S) e reabre o programa, pelas mesmas linhas.
    """
    pasta, nome = NOME_DA_TAREFA.rsplit("\\", 1)
    rodar = " ".join(_aspas_do_powershell(p) for p in comando_de_rodar_a_tarefa()[1:])
    estado = _aspas_do_powershell(str(arquivo_do_estado))
    reabrir = _aspas_do_powershell(MARCA_DE_REABRIR)
    # Reabrir o programa: as mesmas linhas nos dois jeitos. Este PowerShell nasce na pasta do sistema (a peca lanca
    # todo solto la, para nao prender `current`, volta 4); o Start-Process abre o programa na "localizacao" do
    # PowerShell, entao ela vira a pasta do programa, como o Velopack o abre (o Set-Location nao prende a pasta:
    # volta4-exp4). So reabre com $reabrir (o script so de reabrir que nao pegou a marca nao reabre: outro reabre).
    reabrir_o_programa = [
        f"Set-Location -LiteralPath {_aspas_do_powershell(str(Path(exe).parent))}",
        "if ($reabrir) { "
        f"Start-Process -FilePath {_aspas_do_powershell(str(exe))}"
        f" -ArgumentList {_aspas_do_powershell(ARG_DEPOIS_DA_TROCA)} }}",
    ]
    if so_reabrir:
        return "\n".join([
            "$ErrorActionPreference = 'SilentlyContinue'; $criada = $false; $reabrir = $false;"
            f" $marcaDeReabrir = [System.Threading.Mutex]::new($false, {reabrir}, [ref]$criada); $reabrir = $criada",
            *_linhas_da_marca_existe(),
            f"$fim = (Get-Date).AddSeconds({LIMITE_DA_TROCA_S + ESPERA_DA_VOLTA_S})",
            f"while ($reabrir -and (Get-Date) -lt $fim -and (MarcaExiste {_aspas_do_powershell(MARCA_DA_TROCA)}))"
            " { Start-Sleep -Seconds 2 }",
            *reabrir_o_programa,
        ])
    linhas = [
        "$ErrorActionPreference = 'SilentlyContinue'; $reabrir = $true;"
        f" $marcaDaTroca = [System.Threading.Mutex]::new($false, {_aspas_do_powershell(MARCA_DA_TROCA)});"
        f" $marcaDeReabrir = [System.Threading.Mutex]::new($false, {reabrir})",
        f"Wait-Process -Id {int(pid)} -Timeout 120",
        f"& schtasks {rodar} | Out-Null",
        "$rodou = ($LASTEXITCODE -eq 0)",
        f"$fim = (Get-Date).AddSeconds({LIMITE_DA_TROCA_S})",
        "$fase = ''",
        "if ($rodou) {",
        "  Start-Sleep -Seconds 3",
        "  while ((Get-Date) -lt $fim) {",
        "    $fase = ''; $tipo = ''",
        "    " + _linha_de_ler_a_fase(estado),
        f"    $tarefa = (Get-ScheduledTask -TaskPath {_aspas_do_powershell(chr(92) + pasta + chr(92))}"
        f" -TaskName {_aspas_do_powershell(nome)}).State",
        # o ajudante terminou sem trocar (sem internet, assinatura recusada...):
        # nao espera o limite inteiro. "Queued" = ainda vai comecar.
        "    if ($fase -eq 'pendente' -and \"$tarefa\" -ne 'Running' -and \"$tarefa\" -ne 'Queued') { break }",
        "    if ($fase -ne 'pendente' -and $fase -ne 'aplicando') { break }",
        "    Start-Sleep -Seconds 2",
        "  }",
        # so a versao que nao passou no teste rapido volta para a anterior (D-718)
        "  " + _linha_da_espera_da_volta(),
        "}",
        *reabrir_o_programa,
    ]
    if janelinha:
        inicio, fim = _linhas_da_janelinha()
        linhas = [linhas[0], *inicio, *linhas[1:], *fim]
    return "\n".join(linhas)


def _aspas_do_powershell(texto: str) -> str:
    """Texto entre aspas simples do PowerShell (a aspa simples dobra)."""
    return "'" + str(texto).replace("'", "''") + "'"


def _lancar_pela_peca(script: str) -> None:
    """Lanca o script da troca solto (sobrevive a este processo) pela peca unica do Windows, e so volta quando ele
    deu sinal de vida. Levanta OSError com o motivo se ele nao comecou.

    4 consertos (21/11/2026): antes era um PowerShell aberto aqui com DETACHED_PROCESS, que sai sem rodar nada
    (defeito 1 da etapa 5: o "Reiniciar agora" nao voltava, e com uma versao esperando o programa nao abria). Agora:
    core.windows.lancar_powershell_solto (o script num arquivo com a marca de UTF-8, sem a bandeira proibida, num
    grupo novo; ele grava "comecei" na primeira linha e a peca espera esse sinal; sem sinal, fecha o lancado e diz
    "falhou"). Arriscado: voltar a lancar aqui por conta propria (duas pecas para a mesma conversa com o Windows).
    """
    from core import windows

    resposta = windows.lancar_powershell_solto(script)
    if not resposta.deu_certo:
        raise OSError(f"{resposta.motivo} {resposta.detalhe}".strip())


def trocar_e_reabrir(lancar: Callable[[str], None] = _lancar_pela_peca, exe: Path | None = None,
                     pid: int | None = None, janelinha: bool = False) -> bool:
    """A UNICA forma de trocar para a versao ja baixada e reabrir o programa.

    Usada pelo "Reiniciar agora" (D-720; a janela ja fechou gravando) e pela
    abertura depois do "Depois" (D-734, trocar_antes_de_abrir; a janela nem
    abriu; so esta com a janelinha da D-742). Quem chama tem de sair logo: o
    script espera este processo sair.
    Devolve False se nao deu para comecar (o programa segue na versao de hoje).
    `lancar` so da como comecado o que conferiu (o padrao, _lancar_pela_peca, espera o sinal de vida do script e
    levanta se ele nao veio): nunca True so porque o processo nasceu.
    """
    exe = exe or exe_do_programa()
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
# A marca da troca (volta 4, 22/11/2026; D-828): abrir no meio da troca nao a estraga
# ---------------------------------------------------------------------------

ESPERA_PELA_MARCA_S = 10


def segurar_a_marca_da_troca(marca_existe: Callable[[str], bool | None] | None = None,
                             lancar: Callable[[str], None] | None = None,
                             dormir: Callable[[float], None] = time.sleep) -> bool:
    """Antes de o ajudante pedir a troca ao Velopack: a MARCA_DA_TROCA fica segura ate a troca acabar? True = pode
    trocar. Chamada so por GerenteComAMarcaDaTroca (o unico pedido de troca).

    - O script da troca ("Reiniciar agora", "Depois") ja a segura desde a primeira linha: nada a fazer.
    - Senao (a troca sem o script: o Kaique fechou o programa durante o download, o atualizar de longe), lanca o vigia
      (script_do_vigia_da_troca) solto pela peca unica (core.windows, na pasta do sistema) e CONFERE no Windows que a
      marca apareceu (ate ESPERA_PELA_MARCA_S). Sem a marca conferida: False (a troca nao comeca; a versao continua
      esperando e entra na proxima abertura, pelo script). Nunca da como segura o que nao leu.
    `marca_existe`, `lancar` e `dormir` so mudam nos testes. Le a marca pela peca (core.windows.marca_existe), que
    entende "sem licenca para abrir" como "existe".
    """
    if marca_existe is None:
        from core import windows

        marca_existe = windows.marca_existe
    if marca_existe(MARCA_DA_TROCA) is True:
        registrar("trocar: a marca da troca já está segura pelo script da troca")
        return True
    try:
        (lancar or _lancar_pela_peca)(script_do_vigia_da_troca(pasta_do_estado() / "estado.json"))
    except Exception as erro:  # noqa: BLE001 - sem o vigia, a troca so nao comeca agora
        registrar(f"trocar: não consegui lançar o vigia da troca ({type(erro).__name__}: {erro})")
        return False
    fim = time.monotonic() + ESPERA_PELA_MARCA_S
    while True:
        if marca_existe(MARCA_DA_TROCA) is True:
            registrar("trocar: o vigia segura a marca da troca até a troca acabar")
            return True
        if time.monotonic() >= fim:
            registrar("trocar: o vigia foi lançado, mas a marca da troca não apareceu no Windows")
            return False
        dormir(0.2)


def troca_em_andamento(ler: Callable[[], dict] | None = None,
                       marca_existe: Callable[[str], bool | None] | None = None) -> bool:
    """Uma troca de versao esta acontecendo agora? (a MARCA_DA_TROCA existe no Windows). A UNICA regra; quem pergunta:
    a abertura comum do programa (atender_linha_de_comando), que entao sai em silencio.

    Pula a leitura do Windows quando o estado.json nao esta numa das FASES_EM_QUE_HA_TROCA (ninguem segura a marca
    fora delas). "Nao deu para saber" (None) conta como NAO: o programa abre, como antes, e nunca fica sem abrir por
    uma leitura que falhou. `ler` e `marca_existe` so mudam nos testes.
    """
    if (ler or ler_estado)().get("fase") not in FASES_EM_QUE_HA_TROCA:
        return False
    if marca_existe is None:
        from core import windows

        marca_existe = windows.marca_existe
    return marca_existe(MARCA_DA_TROCA) is True


def abrir_quando_a_troca_acabar(lancar: Callable[[str], None] | None = None,
                                ha_quem_reabra: Callable[[], bool] | None = None) -> bool:
    """O Kaique abriu o programa pelo atalho no meio da troca: o programa abre sozinho quando a troca acabar.

    Se alguem ja vai reabrir (MARCA_DE_REABRIR: o script da troca, ou um clique anterior), nada a fazer. Senao (a troca
    do vigia, sem script), lanca o script so de reabrir (script_de_trocar_e_reabrir(so_reabrir=True)) pela peca.
    Devolve True se ha quem reabra. Nunca levanta. `lancar` e `ha_quem_reabra` so mudam nos testes.
    """
    if (ha_quem_reabra or (lambda: _marca_existe(MARCA_DE_REABRIR)))():
        registrar("abrir o programa no meio da troca: não abro agora; o programa abre sozinho quando a troca acabar")
        return True
    try:
        (lancar or _lancar_pela_peca)(script_de_trocar_e_reabrir(exe_do_programa(), os.getpid(),
                                                                 pasta_do_estado() / "estado.json", so_reabrir=True))
    except Exception as erro:  # noqa: BLE001 - nunca derruba; o Kaique pode abrir de novo depois
        registrar(f"abrir o programa no meio da troca: não abro agora, e não consegui deixar a reabertura pronta "
                  f"({type(erro).__name__}: {erro})")
        return False
    registrar("abrir o programa no meio da troca: não abro agora; o programa abre sozinho quando a troca acabar")
    return True


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

def xml_da_tarefa(exe: Path, quem_pode: str = QUEM_PODE_MANDAR_RODAR) -> str:
    """O XML do ajudante: como o proprio sistema (SYSTEM, S-1-5-18), em
    prioridade baixa (7), sem janela, roda <exe> --procurar-atualizacao.

    `quem_pode`: a licenca "quem pode mandar rodar" que vai no desenho. Quem cria a tarefa usa sempre a de fabrica
    (QUEM_PODE_MANDAR_RODAR). Vazia so na conferencia de um ajudante cuja licenca o Windows nao deixou ler
    (o_que_falta_no_computador, volta 3, item 3): a peca (core.windows.problemas_da_tarefa_criada) so confere a licenca
    quando o desenho pedido tem uma, e confere o resto (o comando, os argumentos, a conta) do mesmo jeito.
    Arriscado: criar uma tarefa com `quem_pode` vazio (a conta do Kaique nao conseguiria manda-la rodar).

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
    <SecurityDescriptor>{escape(quem_pode)}</SecurityDescriptor>
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

    exe = exe or exe_do_programa()
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


def versao_do_visual_c_do_pacote(pasta: Path) -> str | None:
    """A versao do Visual C++ que vem no pacote, lida do arquivo da versao em <pasta>\\instalar\\; None se ele nao existe.

    A LEITURA UNICA desse arquivo (passo 2, volta 8; achado 6 do relatorio 7 de quem tentou quebrar, CLAUDE.md §11.12:
    "um dado e lido e gravado por uma funcao so"). Quem escreve e a montagem (empacotar.preparar_pasta_para_o_velopack,
    em UTF-8). Quem le: a conferencia do publicar (empacotar.conferir_pasta_pronta: a versao lida tem de ser igual a da
    assinatura do Visual C++) e o programa instalado (instalar_visual_c_se_faltar: decide se instala). Antes os dois
    liam cada um do seu jeito; ficou o jeito do publicar (o que a prova a vista de 20/11 conferiu): UTF-8, trocando o
    que nao e UTF-8 pela marca de troca (nunca levanta erro de texto), e tirando os espacos e a quebra de linha das
    pontas. Um erro do disco ao ler (sem licenca, arquivo preso) sobe, como antes nos dois.
    Arriscado: ler esse arquivo noutro lugar, ou mudar o jeito so para um dos dois (a conferencia passaria a aceitar o
    que o programa do Kaique le diferente)."""
    arquivo = Path(pasta) / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_VERSAO
    if not arquivo.is_file():
        return None
    return arquivo.read_text(encoding="utf-8", errors="replace").strip()


def visual_c_que_falta(pasta: Path, ler: Callable[[], tuple | None] = _ler_versao_do_visual_c) -> str | None:
    """A versao do Visual C++ do pacote que falta instalar neste computador, ou None (nada falta).

    A REGRA UNICA de "o Visual C++ falta?" (4 consertos, 21/11/2026): quem instala (instalar_visual_c_se_faltar) a
    usa. (Desde a volta 2, medio 3, a pergunta do Windows nao a le: o ajudante completa o Visual C++ sozinho.)
    Sem o instalador no pacote, nada falta (nao ha o que instalar). A versao do pacote vem da leitura unica
    (versao_do_visual_c_do_pacote, a mesma do publicar); sem o arquivo da versao, "0.0.0" (so falta se nao ha Visual
    C++ nenhum), como antes. `ler` le o registro do Windows na hora (nunca uma anotacao).
    Arriscado: decidir "falta" de outro jeito so num dos dois lugares (a pergunta voltaria sempre, ou nunca).
    """
    if not (pasta / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_NOME).is_file():
        return None
    lida = versao_do_visual_c_do_pacote(pasta)
    do_pacote = "0.0.0" if lida is None else lida
    return do_pacote if precisa_do_visual_c(ler(), do_pacote) else None


def instalar_visual_c_se_faltar(pasta: Path, ler: Callable[[], tuple | None] = _ler_versao_do_visual_c,
                                rodar: Callable[[list[str], int], tuple[int, str]] = _rodar) -> bool:
    """O Visual C++ oficial que vai dentro do pacote (D-727), em silencio, so se faltar.

    Devolve False so quando tentou instalar e deu erro (D-749: a preparacao
    conta como nao feita); sem o instalador no pacote ou sem precisar, True.
    "Falta?" e a regra unica visual_c_que_falta.
    """
    exe = pasta / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_NOME
    if not exe.is_file():
        registrar(f"Visual C++: o pacote não tem {exe} (não instalei)")
        return True
    do_pacote = visual_c_que_falta(pasta, ler)
    if do_pacote is None:
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
# O motor do Kraken no lugar dele (D-788; 4 consertos, 21/11/2026)
# ---------------------------------------------------------------------------

# Folga de espaco alem do tamanho aberto do motor (o disco nunca fica cheio por causa dele).
FOLGA_DO_MOTOR_BYTES = 500 * 1024 * 1024


def motor_esta_no_lugar(raiz: Path | None = None) -> bool:
    """O motor do Kraken que este programa pede esta inteiro no lugar dele (core/ocr_kraken.pasta_do_motor_instalado)?

    A regra unica de "pode trocar de versao sem perder o motor" (procurar_e_preparar a pergunta antes de trocar). Pelo
    codigo, no portatil ou fora de uma instalacao do Velopack: True (o motor ali nao e o da instalacao, e nada e
    trocado). A conferencia e a unica do motor (core/ocr_kraken.conferir_motor: a ficha e o tamanho de cada arquivo).
    """
    from core import ocr_kraken

    if raiz is None:
        if not instalado_pelo_velopack() or e_portatil():
            return True
        raiz = pasta_do_programa().parent
    return not ocr_kraken.conferir_motor(ocr_kraken.pasta_do_motor_instalado(raiz))


def _apagar_pasta_do_motor(pasta: Path) -> bool:
    """Apaga uma pasta de motor que ESTA funcao criou (a .chegando ou a estragada posta de lado). True se sumiu.

    shutil.rmtree no Windows nao entra em atalho de pasta (juncao): desde o Python 3.8 tira so o atalho
    (documentacao do shutil). So se chama com caminhos dentro de <raiz>\\motor-kraken\\."""
    import shutil

    shutil.rmtree(pasta, ignore_errors=True)
    return not pasta.exists()


def garantir_o_motor(raiz: Path | None = None, pacote: Path | None = None,
                     livre: Callable[[Path], int] | None = None) -> bool:
    """Poe o motor do Kraken no lugar dele, se ainda nao estiver (D-788, D-727). True = o motor esta no lugar.

    O UNICO lugar que mexe em <raiz>\\motor-kraken\\. Roda no ajudante (como o sistema, por tras; rodar_ao_ligar),
    nunca na janela do Kaique (sem licenca para gravar em Arquivos de Programas) e nunca no portatil.
    1. Se o motor ja confere (core/ocr_kraken.conferir_motor), nada.
    2. Senao, pega o arquivo do motor que veio no instalador: <current>\\instalar\\motor-kraken-<v>.zip
       (versao.arquivo_do_motor, o nome unico). Sem ele: registra e devolve False (a troca nao acontece,
       procurar_e_preparar).
    3. Confere o espaco livre (o tamanho aberto mais FOLGA_DO_MOTOR_BYTES) antes de comecar.
    4. Abre em <raiz>\\motor-kraken\\.chegando-<v> (o zipfile tira unidade, barras do comeco e ".." dos nomes; um
       arquivo com a soma interna errada da erro), confere com conferir_motor, e so entao da o nome final (um
       renomear no mesmo disco). Um motor estragado que estava no nome final e posto de lado e apagado antes.
    Qualquer erro (do disco, do zip estragado de qualquer jeito, inesperado): apaga o .chegando, registra e devolve
    False; nunca levanta; o nome final nunca fica pela metade (volta 2, medio 1 do relatorio 1). `livre` (os
    bytes livres do disco de um caminho) so muda nos testes.
    Nesta entrega nao baixa motor da internet (D-790 fica para depois): todas as versoes pedem o motor 1.
    Arriscado: abrir direto no nome final (um motor pela metade passaria pelo "esta no lugar"); apagar fora de
    <raiz>\\motor-kraken\\.
    """
    import shutil
    import uuid
    import zipfile

    from core import ocr_kraken

    pacote = Path(pacote) if pacote is not None else pasta_do_programa()
    raiz = Path(raiz) if raiz is not None else pacote.parent
    versao_do_motor = ocr_kraken.VERSAO_DO_MOTOR
    destino = ocr_kraken.pasta_do_motor_instalado(raiz, versao_do_motor)
    if not ocr_kraken.conferir_motor(destino):
        return True
    arquivo = pacote / PASTA_DO_QUE_SE_INSTALA / versao.arquivo_do_motor(versao_do_motor)
    if not arquivo.is_file():
        registrar(f"motor do Kraken: não está em {destino} e o arquivo dele não está em {arquivo.parent}")
        return False
    chegando = destino.parent / f".chegando-{versao_do_motor}"
    try:
        _apagar_pasta_do_motor(chegando)
        with zipfile.ZipFile(arquivo) as z:
            precisa = sum(i.file_size for i in z.infolist()) + FOLGA_DO_MOTOR_BYTES
            destino.parent.mkdir(parents=True, exist_ok=True)
            tem = (livre or (lambda p: shutil.disk_usage(p).free))(destino.parent)
            if tem < precisa:
                registrar(f"motor do Kraken: falta espaço em {destino.parent} (precisa de {precisa // 2**20} MB, "
                          f"tem {tem // 2**20} MB); tento de novo depois")
                return False
            chegando.mkdir()
            z.extractall(chegando)
        problemas = ocr_kraken.conferir_motor(chegando)
        if problemas:
            raise OSError("o motor aberto não confere: " + "; ".join(problemas))
        if destino.exists():
            estragado = destino.parent / f".estragado-{versao_do_motor}-{uuid.uuid4().hex[:8]}"
            os.rename(destino, estragado)
            _apagar_pasta_do_motor(estragado)
        os.rename(chegando, destino)
    except Exception as erro:  # noqa: BLE001 - QUALQUER erro (volta 2, medio 1: zlib.error, EOFError do arquivo
        # estragado escapavam e deixavam o provisorio pela metade, sem registro): apaga, registra, devolve False
        sobrou = not _apagar_pasta_do_motor(chegando)
        registrar(f"motor do Kraken: não deu para pôr no lugar ({type(erro).__name__}: {erro})"
                  + ("; sobrou a pasta provisória" if sobrou else ""))
        return False
    registrar(f"motor do Kraken {versao_do_motor} posto em {destino}")
    return True


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
    da pergunta (passo_de_preparar_o_computador) transforma esse codigo em
    erro, a peca devolve "falhou" e a leitura do Windows diz o que falta (a
    pergunta volta, o_que_falta_no_computador). `preparar` que
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


# O pedido de licenca e quanto ele pode demorar: a preparacao pode instalar o Visual C++ (ate 10 min) e tirar o Inno
# (ate 15 min). Passou disso, a peca devolve "falhou" e a proxima abertura le o Windows como estiver.
LIMITE_DA_PREPARACAO_S = 3600


def exe_do_programa() -> Path:
    """O .exe deste programa (o que o ajudante roda e o que a pergunta do Windows abre). Lugar unico."""
    return pasta_do_programa() / Path(sys.executable).name


def passo_de_preparar_o_computador(exe: Path | None = None):
    """O UNICO passo da pergunta do Windows da primeira abertura (D-733, D-735): roda este .exe com
    --preparar-o-computador, escondido, espera ele terminar e FALHA se ele terminar com erro.

    E um passo de script da peca unica do Windows (core.windows.passo_script), feito dentro do programa aberto com a
    licenca (4 consertos, 21/11/2026; antes ia pela peca dos testes a distancia, que lia o "Nao" como "Sim"). O
    --preparar-o-computador (preparar_como_administrador) so termina com 0 se tudo deu certo (D-749); o script
    transforma qualquer outro codigo em erro, e a peca devolve "falhou" para quem pediu. Nada e anotado num arquivo:
    quem decide se o computador ficou preparado e a leitura do Windows (o_que_falta_no_computador).
    Arriscado: engolir o erro do script (try/catch sem lancar de novo): um preparo pela metade daria "deu certo".
    """
    from core import windows

    exe = exe or exe_do_programa()
    texto = ("$p = $null\n"
             f" $p = Start-Process -FilePath {_aspas_do_powershell(str(exe))}"
             f" -ArgumentList {_aspas_do_powershell(ARG_PREPARAR)} -WindowStyle Hidden -Wait -PassThru\n"
             "if ($null -eq $p) { throw 'a preparação do computador não começou' }\n"
             "if ($p.ExitCode -ne 0) { throw ('a preparação do computador terminou com o código ' + $p.ExitCode) }\n")
    return windows.passo_script("preparar o computador: o ajudante da atualização, o Visual C++ e tirar a "
                                "instalação antiga", texto, limite_s=LIMITE_DA_PREPARACAO_S)


def pedir_licenca_ao_windows(passos: list, janela: int | None = None):
    """A pergunta do Windows ("Deseja permitir...?") do atualizador: SEMPRE a peca unica, core.windows.pedir_licenca.

    `janela`: o numero da janela do programa no Windows (a dona da pergunta, trazida para a frente antes). Devolve a
    Resposta da peca (DEU_CERTO, DISSE_NAO ou FALHOU). Sob o pytest NAO pergunta nada ao Windows (devolve "falhou"):
    os testes trocam esta funcao por uma de mentira (nenhuma pergunta na tela de quem roda os testes).
    Arriscado: chamar no fio da tela (a pergunta segura a chamada ate a resposta; quem chama e o fio de tras da
    primeira abertura, ui/testes_a_distancia_ui.primeira_vez_se_preciso).
    """
    from core import windows

    if "PYTEST_CURRENT_TEST" in os.environ:
        return windows.Resposta(windows.FALHOU, "sob os testes automáticos o programa não pergunta nada ao Windows")
    return windows.pedir_licenca(passos, janela=janela, limite_s=LIMITE_DA_PREPARACAO_S + 300)


def ler_tarefa_no_windows(nome: str):
    """Le uma tarefa do Agendador pela peca unica (core.windows.ler_tarefa), sem licenca. Lugar unico de leitura das
    tarefas do atualizador (os testes trocam esta funcao)."""
    from core import windows

    return windows.ler_tarefa(nome)


def ler_o_computador(exe: Path | None = None,
                     ler_tarefa: Callable[[str], object] | None = None,
                     portatil: Callable[[], bool] | None = None) -> tuple[list[str], list[str]]:
    """A LEITURA UNICA do que a pergunta do Windows deixa no computador, LIDA NO WINDOWS agora. Devolve duas listas:
    (o que falta, o que existe mas nao deu para conferir). A primeira vazia = nada falta. Nao grava nada.

    A segunda lista (volta 3, item 2, D-826) existe para quem escreve o registro dizer so o que foi conferido de
    verdade: "existe, mas esta conta nao le" e a licenca que nao veio nao trazem a pergunta de volta, mas tambem nao
    podem virar "o computador esta preparado". Quem usa: o_que_falta_no_computador (a regra "a pergunta volta?") e
    preparar_na_primeira_abertura (a frase de desfecho do registro).

    O que e lido e a regra de "a pergunta do Windows tem de voltar?" (4 consertos, 21/11/2026; D-735, D-741, D-749).
    Antes era uma marca nas Configuracoes e um arquivo preparo.txt (anotacoes do proprio programa): o "Nao" do Windows virava
    "preparado", e a marca sobrevivia a desinstalar e reinstalar. Agora le no Agendador, pela peca unica
    (ler_tarefa_no_windows), as duas tarefas que so a pergunta cria (pedem administrador):
    1. o ajudante da atualizacao existe e e o deste programa: a conferencia da peca unica,
       core.windows.problemas_da_tarefa_criada (o comando e o .exe desta instalacao, os argumentos sao os do ajudante,
       roda como o sistema, e as contas comuns podem manda-lo rodar);
    2. a tarefa "desfazer" existe (D-731).
    O Visual C++ e a instalacao antiga do Inno NAO entram aqui (volta 2, medio 3 do relatorio 1): quem os completa e o
    proprio ajudante, como o sistema, sem perguntar nada, toda vez que roda (rodar_ao_ligar -> preparar_o_computador).
    Se entrassem, uma versao nova com um Visual C++ mais novo traria a pergunta de volta depois do "Sim" (contra a D-741:
    "Depois do 'Sim', nunca mais aparece"), antes de o ajudante instala-lo.
    "Nao deu para saber" (o Windows nao respondeu a leitura) CONTA COMO FALTA, nas duas tarefas: a pergunta volta a cada
    abertura enquanto o Windows nao deixar ler (D-826, Samuel 22/11/2026: "no caso raro a pergunta volta sempre"; D-741).
    Sem uma anotacao, "depois do Sim" e "depois do Nao" tem a mesma leitura; na volta 2 isto nao contava, e um "Nao" com
    a leitura falhando sempre nunca mais trazia a pergunta (relatorio 2 de quem tentou quebrar, (b)). "Existe, mas esta
    conta nao le" conta como existe (a tarefa so nasce na pasta do programa do Agendador, com a licenca de
    administrador, que a peca confere ao criar). No pacote portatil do ensaio nada falta (o portatil nunca mexe no
    Windows, e_portatil).
    Arriscado: escrever no registro um desfecho que nao venha desta leitura (volta 3, item 2); voltar a contar o
    Visual C++ como falta (a pergunta voltaria depois do "Sim" a cada versao com um Visual C++ novo); deixar de contar
    o "nao deu para saber" (o "Nao" deixa de voltar, D-826).
    """
    from core import testes_a_distancia, windows

    if (portatil or e_portatil)():
        return [], []
    ler = ler_tarefa or ler_tarefa_no_windows
    exe = exe or exe_do_programa()
    falta: list[str] = []
    sem_conferir: list[str] = []
    ajudante = ler(NOME_DA_TAREFA)
    if ajudante.existe is None:
        falta.append(f"não deu para ler o ajudante da atualização no Windows ({ajudante.motivo})")
    elif ajudante.existe is False:
        falta.append("o ajudante da atualização não existe no Windows")
    elif not ajudante.lida:
        sem_conferir.append("o ajudante da atualização existe, mas não deu para ler o que ele faz "
                            f"({ajudante.motivo})")
    else:
        # A conferencia da peca unica (volta 2, item 4): a mesma de quando a tarefa e criada (o comando, os argumentos,
        # quem roda e quem pode mandar rodar). Um ajudante que a conta do Kaique nao pode chamar conta como falta.
        # Com a licenca ilegivel (volta 3, item 3, D-826), a mesma peca com o desenho sem a licenca: o comando, os
        # argumentos e a conta continuam conferidos (antes nada era), e so a licenca fica dita como nao conferida.
        # O que a conferencia cobria antes de cada troca (D-827): volta 1, a conta propria (comando, argumentos, conta);
        # volta 2, a peca (os tres e a licenca; com a licenca ilegivel, nada); agora, os tres sempre e a licenca quando
        # da para ler.
        pedido = xml_da_tarefa(exe)
        if not ajudante.licenca:
            sem_conferir.append("não deu para ler a licença do ajudante da atualização (quem pode mandá-lo rodar)")
            pedido = xml_da_tarefa(exe, quem_pode="")
        falta += [f"o ajudante da atualização não é o deste programa: {p}"
                  for p in windows.problemas_da_tarefa_criada(pedido, ajudante)]
    desfazer = ler(testes_a_distancia.nome_da_tarefa_do_desfazer())
    if desfazer.existe is None:
        falta.append(f"não deu para ler a tarefa do desfazer no Windows ({desfazer.motivo})")
    elif desfazer.existe is False:
        falta.append("a tarefa que desfaz tudo ao desinstalar não existe no Windows")
    return falta, sem_conferir


def o_que_falta_no_computador(exe: Path | None = None,
                              ler_tarefa: Callable[[str], object] | None = None,
                              portatil: Callable[[], bool] | None = None) -> list[str]:
    """A REGRA UNICA de "a pergunta do Windows tem de voltar?": o que ainda falta neste computador que SO a pergunta faz,
    lido no Windows agora (vazio = nada falta). E a primeira lista da leitura unica (ler_o_computador); o que existe mas
    nao deu para conferir vai para o registro (nao traz a pergunta de volta). Quem usa: preparar_ao_abrir (antes de
    perguntar de novo) e falta_a_pergunta_do_windows.
    """
    falta, sem_conferir = ler_o_computador(exe, ler_tarefa, portatil)
    for nota in sem_conferir:
        registrar(f"{nota}; não pergunto de novo por isso")
    return falta


INTERVALO_DA_JANELA_S = 0.3


def esperar_a_janela_na_frente(janela: int, na_frente: Callable[[int], int | None] | None = None,
                               existe: Callable[[int], bool] | None = None,
                               trazer: Callable[[int], bool] | None = None,
                               minimizada: Callable[[int], bool] | None = None,
                               dormir: Callable[[float], None] = time.sleep) -> int | None:
    """Espera a janela do programa estar na frente para pedir a licenca (volta 4, 22/11/2026; D-806: "pede a licenca
    do Windows [...] enquanto a janela do programa ainda esta na frente, para a pergunta vir no meio da tela"; D-828).
    Devolve a janela que esta na frente (a do programa ou um aviso dela), que vira a dona da pergunta; None se a janela
    do programa fechou antes (nao pergunta; a proxima abertura le o Windows e pergunta de novo, D-741).

    Por que esperar: na abertura que segue um "Nao", o pedido sai uns 17 a 20 s depois do clique no atalho (o programa
    carrega e monta a janela antes), e o Windows tira do programa o direito de vir para a frente se a pessoa mexeu
    noutra janela nesse tempo (AllowSetForegroundWindow); a pergunta entao so pisca na barra (prova de 22/11).
    Como: na frente ja (o Kaique abriu e nao saiu da janela): pergunta na hora, sem esperar. Senao, UMA tentativa de
    trazer a janela (nunca com ela minimizada: nao se desfaz o que o Kaique fez) e depois so le, a cada
    INTERVALO_DA_JANELA_S, ate ela vir para a frente (o clique dele de volta no programa ou no botao da barra). Sem
    limite de tempo e sem frase na tela: roda no fio de tras, solto, que morre com o programa; a tela nao trava.
    O registro diz quando esperou e quanto. `na_frente`, `existe`, `trazer`, `minimizada` e `dormir` so mudam
    nos testes.
    Arriscado: perguntar sem esperar (volta a piscar); trazer a janela minimizada para a frente.
    """
    from core import windows

    na_frente = na_frente or windows.janela_do_programa_na_frente
    existe = existe or windows.janela_existe
    minimizada = minimizada or windows.janela_minimizada
    dona = na_frente(janela)
    if dona:
        return dona
    comeco = time.monotonic()
    registrar("primeira abertura: a janela do programa não está na frente; a pergunta do Windows espera ela voltar")
    if existe(janela) and not minimizada(janela):
        (trazer or windows.trazer_para_a_frente)(janela)
    while True:
        dona = na_frente(janela)
        if dona:
            registrar(f"primeira abertura: a janela do programa veio para a frente; a pergunta esperou "
                      f"{time.monotonic() - comeco:.0f} s")
            return dona
        if not existe(janela):
            registrar(f"primeira abertura: a janela do programa fechou antes de vir para a frente (esperou "
                      f"{time.monotonic() - comeco:.0f} s); nada foi perguntado; a pergunta volta na próxima abertura")
            return None
        dormir(INTERVALO_DA_JANELA_S)


def preparar_na_primeira_abertura(janela: int | None = None) -> list[str]:
    """A pergunta do Windows da primeira abertura (D-733, D-735), pela peca unica. Devolve o que ainda falta no
    computador depois dela, lido no Windows (vazio = o que so a pergunta faz esta feito).

    UMA pergunta so, sempre, com ou sem a senha dos testes (D-825, opcao B: nesta entrega a senha nao liga os
    testes a distancia, entao a pergunta leva so a preparacao). "Nao" (ou ninguem responde): nada muda, anotado no
    registro; a pergunta volta na proxima abertura (D-741), porque a leitura do Windows diz que as tarefas faltam. "Sim"
    com a preparacao parada no meio (D-749): a peca devolve "falhou" e fica no registro; se uma das tarefas nao nasceu, a
    leitura diz que falta e a pergunta volta; se as tarefas nasceram e o que falhou foi o Visual C++ ou o Inno, o
    ajudante os completa sozinho, como o sistema, na vez seguinte que rodar (volta 2, medio 3; D-826). Nada e gravado
    como marca. O registro: a resposta entra so como fato; a frase do desfecho (preparado, nao preparado, ja estava,
    nao deu para conferir) vem da leitura unica (ler_o_computador), nunca da resposta (volta 3, item 2).
    `janela`: a janela do programa, dona da pergunta (para ela vir no meio da tela, D-806).
    Quem chama: preparar_ao_abrir, no fio de tras da primeira abertura (nunca no fio da tela).
    """
    from core import windows

    if janela:
        # Volta 4 (D-806, D-828): so pergunta com a janela do programa na frente (senao a pergunta so pisca na barra).
        dona = esperar_a_janela_na_frente(janela)
        if dona is None:
            falta, _ = ler_o_computador()
            return falta
        janela = dona
    resposta = pedir_licenca_ao_windows([passo_de_preparar_o_computador()], janela)
    if resposta.dados.get("janela_na_frente") is False:
        # D-806: o Windows nao deixou a janela vir para a frente (o Kaique estava noutra janela): a pergunta pode ter
        # so piscado na barra de tarefas. Fica anotado; se ninguem respondeu, conta como "Nao" e volta.
        registrar("primeira abertura: a janela do programa não estava na frente quando o Windows perguntou")
    # A resposta vai ao registro so como FATO (o que o Windows devolveu). O que ela causou (a pergunta volta ou nao, o
    # computador preparado ou nao) so a leitura do Windows, logo abaixo, diz (volta 3, item 2, D-826: antes estas linhas
    # diziam "o ajudante nao foi criado; a pergunta volta" e "o que faltou o ajudante completa" sem ter lido nada).
    if resposta.desfecho == windows.DISSE_NAO:
        registrar("primeira abertura: o Kaique disse \"Não\" à pergunta do Windows (nada foi feito com a licença)")
    elif not resposta.deu_certo:
        registrar(f"primeira abertura: a preparação do computador não terminou bem ({resposta.motivo}) "
                  f"{resposta.detalhe}")
    falta, sem_conferir = ler_o_computador()
    if falta:
        registrar("primeira abertura: o computador não ficou preparado (lido no Windows: " + "; ".join(falta)
                  + "); a pergunta volta na próxima abertura")
    elif sem_conferir:
        registrar("primeira abertura: as tarefas do programa existem no Windows, mas não deu para conferir tudo ("
                  + "; ".join(sem_conferir) + "); a pergunta não volta por isso")
    elif resposta.deu_certo:
        registrar("primeira abertura: o computador está preparado (lido no Windows)")
    else:
        # Nada falta sem o "Sim" desta vez: as tarefas ja estavam no Windows (outra conta, um "Sim" de antes) ou
        # nasceram e o que falhou foi outra parte. O ajudante confere e completa o Visual C++ e a instalacao antiga
        # toda vez que roda (preparar_o_computador; D-826), entao isto e verdade em todos os casos.
        registrar("primeira abertura: as tarefas do programa já estão no Windows (lidas agora); a pergunta não volta; "
                  "o Visual C++ e a instalação antiga o ajudante confere e completa sozinho toda vez que roda")
    return falta


def preparar_ao_abrir(janela: int | None = None, primeira_vez: bool = False) -> list[str]:
    """O trabalho da primeira abertura (e das seguintes, ate o "Sim"), POR TRAS: o que a tela manda rodar num fio
    que nao e o da tela (ui/testes_a_distancia_ui.primeira_vez_se_preciso). Devolve o que ainda falta.

    - primeira_vez (nesta conta a janela da senha acabou de aparecer): pergunta ja, logo depois do clique (D-806);
    - senao: le o Windows; se nada falta, nao pergunta nada; se falta uma das tarefas (o "Nao" de antes, a preparacao
      parada antes de cria-las, o ajudante que sumiu ao reinstalar, o Windows que nao deixou ler, D-826), pergunta de
      novo (D-741, D-749).
    Se a pergunta deixou o computador preparado, manda o ajudante rodar uma vez (ele acabou de nascer; a chamada da
    abertura, ui/aviso_de_atualizacao.ligar_na_janela, veio antes e nao o achou). Nunca levanta: um erro vai para o
    registro e conta como "falta".
    """
    try:
        if not primeira_vez:
            falta = o_que_falta_no_computador()
            if not falta:
                return []
            registrar("abrir o programa: falta preparar o computador (" + "; ".join(falta)
                      + "); a pergunta do Windows aparece de novo")
        falta = preparar_na_primeira_abertura(janela)
        if not falta:
            procurar_ao_abrir()
        return falta
    except Exception as erro:  # noqa: BLE001 - o fio de tras nunca derruba o programa
        registrar(f"primeira abertura: erro inesperado ({type(erro).__name__}: {erro}); a pergunta volta")
        return [f"erro inesperado: {erro}"]


def falta_a_pergunta_do_windows() -> bool:
    """D-741 (Samuel, 17/11/2026: "Sim"): a pergunta do Windows da primeira abertura ainda tem de aparecer?

    Desde os 4 consertos (21/11/2026) e a leitura do Windows (o_que_falta_no_computador), nunca uma marca: depois
    de um "Nao", de uma preparacao pela metade (D-749) ou de o ajudante sumir, volta; com tudo no lugar, nao.
    """
    return bool(o_que_falta_no_computador())


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
    ganchos = any(a.startswith("--veloapp") for a in argumentos)
    if primeiro not in nossos and not instalado_pelo_velopack() and not ganchos:
        return None
    # Volta 4 (D-828): a abertura comum do programa instalado, no meio de uma troca de versao, sai em silencio, antes
    # do brasao e da janela (um processo de `current` aberto agora estragaria a troca), e o programa abre sozinho no
    # fim (abrir_quando_a_troca_acabar). Nunca nos modos escondidos, nos ganchos do Velopack nem no programa que o
    # proprio script da troca reabre (ARG_DEPOIS_DA_TROCA).
    if primeiro not in nossos and not ganchos and ARG_DEPOIS_DA_TROCA not in argumentos:
        try:
            if troca_em_andamento():
                abrir_quando_a_troca_acabar()
                return 0
        except Exception as erro:  # noqa: BLE001 - o programa abre mesmo assim, como antes
            registrar(f"abrir o programa: não consegui olhar se há uma troca acontecendo: {type(erro).__name__}: {erro}")
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
