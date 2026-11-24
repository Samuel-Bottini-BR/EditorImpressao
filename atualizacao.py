"""A atualização pela internet do Editor de Impressão (Velopack): o executor do atualizador novo (23/11/2026).

DE ONDE VEM. O Samuel decidiu refazer o atualizador (D-830, "refazer") no desenho simples que o Fable propôs: o único
ato com licença é dar à pasta do programa a licença de Modificar para Usuários, uma vez, na primeira abertura, antes da
janela. Depois disso o próprio programa, na conta do Kaique, procura (só ao abrir, D-732), confere a assinatura do Samuel
(D-724), confere o motor do Kraken (D-790, D-833), baixa e pede ao Velopack para trocar; o Velopack espera o programa
sair, troca, mostra a janelinha dele (D-832) e reabre na conta do Kaique. Nenhum processo nosso roda como o sistema,
nenhum script do PowerShell nosso (o único PowerShell que sobra é o da peça do Windows para ler a tarefa do ajudante
antigo no passo 1 da pergunta; ver o ONDE-PAREI, volta 2), nenhuma marca, nenhum canal entre contas. O plano inteiro, com as decisões e a leitura do Velopack,
está em `relatorios/atualizador-novo/ONDE-PAREI.md`.

AS PEÇAS (CLAUDE.md §11.12, ponto 1: uma peça só para cada conversa com o que está fora)
    a regra        `core/fases_da_atualizacao.py`: `proxima_fase(estado, evento) -> (estado, efeitos)`, sem disco nem
                   rede nem Windows. Decide TUDO o que acontece.
    o Windows      `core/windows.py`: a pergunta do Windows e os passos com licença, a lista de processos, o teste
                   rápido num processo à parte, o dono de um arquivo.
    o Velopack     `core/conversa_com_o_velopack.py`: o único que importa `velopack` (a trava cobra).
    o executor     ESTE arquivo: roda os efeitos que a regra devolve, chamando as duas peças acima, e devolve o que
                   aconteceu como evento novo (`Atualizacao.evento`). Aqui moram também o que é só do disco: o
                   `estado.json` e o registro (`%ProgramData%\\EditorImpressao\\atualizacao\\`, D-719), a última boa
                   (`<raiz>\\ultima-boa\\`, D-844), o teste de gravar na pasta do programa, o motor do Kraken no lugar dele, a fonte de teste e a linha de comando.
    a tela         `ui/aviso_de_atualizacao.py`: só transforma o clique em evento e o efeito em caixa.

CAMINHO -> FUNÇÃO (§11.12; volta 3, emenda do Fable: a abertura deriva o estado do que existe)
    abrir o programa                main.py -> atender_linha_de_comando -> Atualizacao.abrir (lê a versão que roda,
                                    ler_ultima_boa, o pendente do Velopack, o atualizador rodando, o bilhete) ->
                                    proxima_fase(Abriu)
    a pergunta do Windows           efeito PedirLicenca -> core.windows.comecar_pedido_de_licenca(passos_do_preparo())
    a espera do preparo (por trás)  efeito EsperarPreparo -> PedidoDeLicenca.esperar + pasta_aceita_gravacao
    o motor do Kraken               efeito GarantirMotor -> garantir_o_motor (o único que mexe em motor-kraken\\)
    procurar / assinatura / baixar  Procurar, ConferirAssinatura, Baixar -> conversa_com_o_velopack + conferir_assinatura_do
    "Reiniciar agora" / "Depois"    ui -> Escolheu -> ConferirTroca (por trás) -> Atualizacao.conferencia_da_troca (a
                                    ÚNICA conferência) -> TrocaConferida; pode: FecharJanela -> ui fecha a janela ->
                                    JanelaFechou -> Trocar; não pode: MostrarFalha(NAO_DEU_AGORA, motivo) -> ui mostra
                                    frase_da_falha (D-840 com outra janela, e o aviso volta, D-841; D-845 nos outros)
    fechar o programa               ui/janela_principal.closeEvent -> ui.ao_fechar -> Fechando -> PerguntarAoFechar ->
                                    RespondeuAoFechar -> Trocar
    a troca (qualquer caminho)      efeito Trocar e a volta -> trocar_para (a ÚNICA; confere a soma assinada do
                                    arquivo baixado, o motor e se há outra janela aberta) -> conversa_com_o_velopack.trocar
    a versão que ainda não passou   Abriu(versão != última boa) -> RodarTesteRapido -> TesteRapido -> passou:
                                    GuardarUltimaBoa -> guardar_ultima_boa (a ÚNICA que guarda o pacote); não passou:
                                    Reprovar -> reprovar (a ÚNICA que põe em "não tentar") + Voltar
    a volta para a anterior         efeito Voltar -> Atualizacao._voltar (o pacote guardado, sem internet) -> trocar_para
    uma frase na tela               efeito MostrarFalha -> ui -> frase_da_falha (a ÚNICA escolha do texto); sem janela,
                                    GuardarFrase -> guardar_frase (no bilhete, para a próxima abertura)
    o bilhete (estado.json)         mudar_o_bilhete (a ÚNICA escrita; só "reprovadas" e "frase")

NADA PELO CÓDIGO. Pelo atalho "(desenvolvimento)" e nos testes o programa não está instalado pelo Velopack
(`instalado_pelo_velopack`): `atender_linha_de_comando` devolve None sem importar o velopack, e nada roda.

Seguro mexer: as frases do registro (sem número de decisão: o porteiro barra, K04). Arriscado: os textos da tela
(palavras combinadas com o Samuel: D-719, D-778, D-835, D-839, D-840, D-843, D-845, D-846); `NOME_DA_TAREFA` (o nome do ajudante antigo que o preparo
apaga); a ordem dos passos do preparo (`passos_do_preparo`: a licença da pasta é o ÚLTIMO, D-749, e o ajudante antigo
sai ANTES dela); qualquer caminho que chame a troca do Velopack sem passar por `trocar_para`.
"""

from __future__ import annotations

import json
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable

import assinatura
import versao
from core import fases_da_atualizacao as fases

# ---------------------------------------------------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------------------------------------------------

# D-713: o projeto continua público; as versões vêm dos "Releases" dele.
REPOSITORIO = "https://github.com/Samuel-Bottini-BR/EditorImpressao"

# A linha de comando (atendida por atender_linha_de_comando, antes de qualquer janela).
ARG_TESTE_RAPIDO = "--teste-rapido"            # a versão instalada abre? (num processo à parte, sem janela)
ARG_CONFERIR_NOVA = "--conferir-a-versao-nova"  # reaberto pelo Velopack: <de> <para> vêm logo depois
ARG_SEM_JANELA = "--sem-janela"                # a reabertura do "Sim" ao fechar: só confere, nada na tela (D-769)
ARG_FONTE = "--fonte"                          # só o ensaio e os testes: as versões vêm de uma pasta
# O argumento com que o ajudante antigo (uma tarefa do Windows que rodava como o sistema, até 23/11/2026) chamava o
# programa. Só para ser reconhecido: se uma tarefa antiga sobrar num computador, o programa novo anota e sai.
ARG_PROCURAR = "--procurar-atualizacao"
# O nome do ajudante antigo no Agendador do Windows. O preparo do computador o apaga (D-838: "o programa novo só
# apaga sozinho a tarefa antiga do ajudante, se achar"), porque ele rodava como o sistema um programa da pasta que
# passa a aceitar gravação de Usuários. O desfazer dos testes à distância (core/testes_a_distancia.py) também o apaga.
NOME_DA_TAREFA = "EditorImpressao\\Procurar versao nova"

# O índice que o publicar põe em cada versão (o mesmo de empacotar.NOME_DO_INDICE; o programa não importa o
# empacotar.py, e um teste cobra que os dois são iguais).
NOME_DO_INDICE_PUBLICADO = "releases.win.json"

# O Visual C++ oficial que vai DENTRO do pacote (D-727), posto pelo empacotar.py em <programa>\\instalar\\.
PASTA_DO_QUE_SE_INSTALA = "instalar"
VC_REDIST_NOME = "vc_redist.x64.exe"
VC_REDIST_VERSAO = "vc_redist.versao.txt"

# O programa reaberto pela atualização (volta 2, M1) cria este arquivo logo ao começar: é o sinal de vida que a peça
# do Windows espera para dar o "abrir de novo" como feito (`windows.lancar_solto`).
ARG_SINAL_DE_VIDA = "--sinal-de-vida"

# Os textos da tela (português, sem jargão, sem emoji; CLAUDE.md §3). Palavras combinadas com o Samuel.
TITULO_DA_VERSAO_NOVA = "Versão nova do programa"
FRASE_DA_VERSAO_NOVA = (                                             # D-715; a última frase é a da D-835
    "Chegou uma versão nova do Editor de Impressão.\n\n"
    "Salve o seu trabalho e reinicie o programa para usar a versão nova.\n\n"
    "Se escolher \"Depois\", você pode atualizar quando fechar o programa.")
BOTAO_REINICIAR = "Reiniciar agora"                                  # D-720
BOTAO_DEPOIS = "Depois"
TITULO_AO_FECHAR = "Atualizar agora?"                                # D-835, palavra por palavra
FRASE_AO_FECHAR = "Quer atualizar o programa agora, ao fechar?"
BOTAO_SIM_AO_FECHAR = "Sim"
BOTAO_NAO_AO_FECHAR = "Não"
TITULO_DA_FALHA = "Atualização"
# D-778 (Samuel, 18/11/2026: "A"): uma frase para cada falha. A (1) é a da D-719.
FRASE_DA_FALHA = ("A atualização não deu certo. O programa voltou para a versão anterior "
                  "e continua funcionando. Avise o Samuel.")
FRASE_DA_FALHA_SEM_ASSINATURA = ("Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do "
                                 "Samuel. O programa continua funcionando. Avise o Samuel.")
FRASE_DA_FALHA_SEM_VOLTA = ("A atualização não deu certo e o programa não conseguiu voltar sozinho. "
                            "Não desinstale nada. Avise o Samuel.")
# D-839 (Samuel, 24/11/2026: "sim"): o Windows não deixou trocar e o programa nunca saiu da versão de antes. A (1),
# "voltou para a versão anterior", fica só para a versão nova que entrou, falhou no teste e voltou.
FRASE_DA_FALHA_SEM_TROCA = ("A atualização não deu certo. O programa continua na versão de antes e funcionando. "
                            "Avise o Samuel.")
# D-843 (Samuel, 24/11/2026: "vamos fazer b e colocamos isso no plano"): a versão nova pede um motor do Kraken que
# não está no lugar; ela não é anunciada nem trocada.
FRASE_DO_MOTOR_NOVO = "Esta versão precisa de um motor novo. Avise o Samuel."
# D-840 (Samuel, 24/11/2026: "sim"): "Reiniciar agora" com outra janela do programa aberta.
FRASE_DA_OUTRA_JANELA = "Feche a outra janela do programa e clique de novo."
# D-845 (Samuel, 24/11/2026: "ok"): todo outro "não deu" do "Reiniciar agora", com o motivo em português simples.
FRASE_NAO_DEU_AGORA = "Não deu para atualizar agora: {motivo}. Tente ao fechar o programa."
# Os motivos (texto de tela que o Samuel ainda não aprovou palavra por palavra: estão em "Perguntas para o Samuel" do
# ONDE-PAREI da volta 3). A chave é a da regra (`fases.MOTIVOS`); um teste cobra que toda chave tem o texto.
MOTIVOS_DA_TELA = {
    fases.MOTIVO_SEM_VERSAO: "a versão nova ainda não terminou de chegar",
    fases.MOTIVO_PACOTE_SUMIU: "o arquivo da versão nova sumiu do computador",
    fases.MOTIVO_PACOTE_INCOMPLETO: "o arquivo da versão nova está incompleto",
    fases.MOTIVO_MOTOR: "falta no computador uma peça que a versão nova precisa",
    fases.MOTIVO_SEM_LISTA: "o Windows não mostrou quais programas estão abertos",
    fases.MOTIVO_SEM_CONFERIR: "há um programa aberto que pode ser outra janela do Editor de Impressão",
    fases.MOTIVO_NAO_FECHOU: "o programa não conseguiu fechar",
    fases.MOTIVO_ATUALIZADOR: "o atualizador do programa não começou",
    fases.MOTIVO_ERRO: "aconteceu um erro inesperado",
    fases.MOTIVO_OUTRA_JANELA: "há outra janela do programa aberta",     # (usa a frase da D-840, nunca esta)
}
# Qual frase para cada tipo (a regra num lugar só; a tela só chama `frase_da_falha`).
FRASES_DA_FALHA = {fases.FALHA_TESTE: FRASE_DA_FALHA, fases.FALHA_TROCA: FRASE_DA_FALHA_SEM_TROCA,
                   fases.FALHA_RECUSADA: FRASE_DA_FALHA_SEM_ASSINATURA, fases.FALHA_VOLTA: FRASE_DA_FALHA_SEM_VOLTA,
                   fases.FALHA_MOTOR: FRASE_DO_MOTOR_NOVO}


def frase_da_falha(tipo: str, motivo_da_tela: str = "") -> str:
    """A frase da tela para um efeito `MostrarFalha` (a ÚNICA escolha; a caixa tem sempre o título TITULO_DA_FALHA,
    "Atualização", D-846). O "não deu agora": com outra janela aberta, a da D-840; senão, a da D-845 com o motivo."""
    if tipo == fases.NAO_DEU_AGORA:
        if motivo_da_tela == fases.MOTIVO_OUTRA_JANELA:
            return FRASE_DA_OUTRA_JANELA
        return FRASE_NAO_DEU_AGORA.format(motivo=MOTIVOS_DA_TELA.get(motivo_da_tela,
                                                                     MOTIVOS_DA_TELA[fases.MOTIVO_ERRO]))
    return FRASES_DA_FALHA.get(tipo, FRASE_DA_FALHA_SEM_TROCA)

# O arquivo que o teste de gravar cria e apaga na raiz (o Velopack faz o mesmo com outro nome, ".velopack_dir_test").
ARQUIVO_DO_TESTE_DE_GRAVAR = ".editor_teste_de_gravar"


# ---------------------------------------------------------------------------------------------------------------------
# O estado e o registro (C:\ProgramData\EditorImpressao\atualizacao)
# ---------------------------------------------------------------------------------------------------------------------

def pasta_do_estado() -> Path:
    """%ProgramData%\\EditorImpressao\\atualizacao (lida na hora: os testes trocam a variável). Ali, e não na pasta da
    conta, porque a gerente lê o registro por outra conta (D-719); toda conta lê o ProgramData."""
    base = os.environ.get("PROGRAMDATA") or "C:\\ProgramData"
    return Path(base) / "EditorImpressao" / "atualizacao"


def caminho_do_registro() -> Path:
    """O registro que a gerente lê de longe (D-719)."""
    return pasta_do_estado() / "atualizacao.log"


def registrar(texto: str) -> None:
    """Anota uma linha no registro da atualização. Nunca levanta. Se o arquivo não aceita (foi criado por outra conta,
    como o do ajudante antigo no PC do Samuel), a linha vai para o erros.log de sempre."""
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
    """O bilhete da atualização (estado.json; {} se não existe ou está estragado). Desde a volta 3 (emenda do Fable,
    "a verdade vem do disco, não do bilhete") ele guarda SÓ duas coisas: `reprovadas` (as versões que não passaram no
    teste rápido: não são tentadas de novo) e `frase` (a frase a mostrar uma vez, de um processo que não tinha janela).
    Nada mais decide nada: a versão boa, o que está baixado e se a troca está acontecendo vêm do disco e do Windows
    (`Atualizacao.abrir`). As chaves de antes (`nao_tentar`, `falha`, `tentando`) são ignoradas e somem na próxima
    gravação."""
    try:
        lido = json.loads((pasta_do_estado() / "estado.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return lido if isinstance(lido, dict) else {}


def gravar_estado(estado: dict) -> bool:
    """Grava o estado.json inteiro de uma vez (arquivo provisório + troca). False (e uma linha no registro) se o disco
    não aceitou; nunca levanta."""
    try:
        pasta = pasta_do_estado()
        pasta.mkdir(parents=True, exist_ok=True)
        provisorio = pasta / "estado.json.gravando"
        provisorio.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
        provisorio.replace(pasta / "estado.json")
        return True
    except OSError as erro:
        registrar(f"não consegui gravar o estado da atualização: {erro}")
        return False


# As duas únicas chaves do bilhete (volta 3). Arriscado: pôr outra (o bilhete voltaria a decidir coisas).
CHAVES_DO_BILHETE = ("reprovadas", "frase")


def _agora() -> str:
    """A hora de agora, como vai para o disco."""
    return datetime.now().isoformat(timespec="seconds")


def mudar_o_bilhete(mudar: Callable[[dict], None]) -> bool:
    """A ÚNICA escrita do bilhete: lê, deixa só as duas chaves (`CHAVES_DO_BILHETE`), aplica `mudar` e grava. Só é
    chamada quando há o que anotar (uma reprovação, uma frase), nunca em toda abertura (volta 2, leve 4: aberturas que
    regravavam o arquivo inteiro desfaziam o que a outra anotava). Devolve se o disco aceitou; se não, o programa
    continua atualizando e o registro diz (volta 3, M4)."""
    lido = ler_estado()
    limpo = {k: lido[k] for k in CHAVES_DO_BILHETE if k in lido}
    mudar(limpo)
    return gravar_estado(limpo)


def reprovadas_do_bilhete(estado: dict) -> tuple[str, ...]:
    """As versões reprovadas no teste rápido, lidas do bilhete (só os textos)."""
    lidas = estado.get("reprovadas") if isinstance(estado.get("reprovadas"), list) else []
    return tuple(sorted({str(v) for v in lidas if isinstance(v, str)}))


def reprovar(versao_reprovada: str, motivo: str) -> bool:
    """A ÚNICA forma de pôr uma versão em "não tentar" (volta 3, M1: só o teste rápido reprovado faz isso). Anota no
    bilhete e no registro (a gerente lê). Devolve se o bilhete aceitou."""
    def mudar(b: dict) -> None:
        b["reprovadas"] = sorted(set(reprovadas_do_bilhete(b)) | {versao_reprovada})

    gravou = mudar_o_bilhete(mudar)
    registrar(f"FALHOU no teste rápido a versão {versao_reprovada}: {motivo}"
              + ("" if gravou else " (a reprovação NÃO ficou gravada: o estado não aceitou)"))
    return gravou


def guardar_frase(tipo: str, versao_da_frase: str, motivo_da_tela: str = "") -> bool:
    """Guarda no bilhete a frase a mostrar uma vez na próxima abertura com janela (o processo que a viu não tinha
    janela). O nome leva a hora: a mesma frase de novo, noutro dia, aparece de novo."""
    nome = f"{fases.id_da_falha(tipo, versao_da_frase)}-{_agora()}"
    gravou = mudar_o_bilhete(lambda b: b.update(frase={"tipo": tipo, "nome": nome, "motivo": motivo_da_tela}))
    if not gravou:
        registrar(f"a frase \"{tipo}\" da versão {versao_da_frase} não ficou guardada para a próxima abertura")
    return gravou


def frase_do_bilhete(estado: dict) -> tuple[str, str, str] | None:
    """(tipo, nome, motivo) da frase guardada no bilhete, ou None."""
    frase = estado.get("frase") if isinstance(estado.get("frase"), dict) else {}
    tipo, nome = frase.get("tipo"), frase.get("nome")
    if not (isinstance(tipo, str) and isinstance(nome, str) and tipo and nome):
        return None
    motivo = frase.get("motivo") if isinstance(frase.get("motivo"), str) else ""
    return tipo, nome, motivo


# ---------------------------------------------------------------------------------------------------------------------
# A última boa: a última versão que passou no teste rápido, guardada com o pacote dela (volta 3, D-844)
# ---------------------------------------------------------------------------------------------------------------------
# <raiz>\ultima-boa\ guarda o pacote (.nupkg) da última versão que passou no teste rápido e a assinatura do Samuel
# dele. A volta para a anterior usa esse pacote: segundos, sem internet (D-844). A última boa é DERIVADA desta pasta
# (`ler_ultima_boa`): a versão mais nova que tem ali o pacote E a assinatura. Mora na raiz da instalação (a pasta que os
# Usuários podem modificar depois do preparo; o desinstalador do Velopack apaga a raiz inteira, com ela). Quem escreve
# nela: só `guardar_ultima_boa` (o pacote) e `conferir_assinatura_do` (a assinatura da versão que está chegando, guardada
# ao conferir, para guardar o pacote dela depois não precisar de internet). Arriscado: dar o nome final ao pacote antes
# de conferir a soma (uma cópia pela metade viraria a "última boa").

PASTA_DA_ULTIMA_BOA = "ultima-boa"


def nome_do_pacote(versao_do_pacote: str) -> str:
    """O nome do pacote completo de uma versão, como o Velopack o chama ("<id>-<versão>-full.nupkg")."""
    return f"{versao.ID_DO_PACOTE}-{versao_do_pacote}-full.nupkg"


def pasta_da_ultima_boa(raiz: Path) -> Path:
    """<raiz>\\ultima-boa."""
    return Path(raiz) / PASTA_DA_ULTIMA_BOA


def _versao_do_nome(nome: str) -> str:
    """A versão escrita no nome de um arquivo da pasta da última boa ("<id>-<v>-full.nupkg", "<id>-<v>.assinatura",
    com ou sem ".chegando"/".gravando"); "" se não é de lá."""
    prefixo = f"{versao.ID_DO_PACOTE}-"
    if not nome.startswith(prefixo):
        return ""
    resto = nome[len(prefixo):]
    for fim in ("-full.nupkg", ".assinatura"):
        if fim in resto:
            v = resto.split(fim)[0]
            return v if fases._numeros(v) else ""
    return ""


def ler_ultima_boa(raiz: Path) -> str:
    """A última boa: a versão mais nova que tem em `<raiz>\\ultima-boa` o pacote e a assinatura ("" = nenhuma). Só lista
    a pasta (não soma o pacote: isso é feito ao guardar e de novo pelo Velopack ao voltar). Nunca levanta."""
    try:
        nomes = {p.name for p in pasta_da_ultima_boa(raiz).iterdir() if p.is_file()}
    except OSError:
        return ""
    achadas = [v for v in (_versao_do_nome(n) for n in nomes if n.endswith("-full.nupkg"))
               if v and assinatura.nome_do_arquivo_da_assinatura(versao.ID_DO_PACOTE, v) in nomes]
    return max(achadas, key=fases._numeros) if achadas else ""


def _gravar_texto_inteiro(caminho: Path, texto: str) -> None:
    """Grava um texto pequeno de uma vez (provisório + troca), BYTE POR BYTE como veio (em UTF-8, sem trocar o fim de
    linha: gravado como texto, o Windows troca cada "
" por "

", e uma assinatura publicada com "

" virava
    "


" e deixava de ser lida; achado pela mutação N27 da volta 3). Levanta OSError."""
    provisorio = caminho.with_name(caminho.name + ".gravando")
    provisorio.write_bytes(texto.encode("utf-8"))
    provisorio.replace(caminho)


def _ler_texto(caminho: Path) -> str:
    """Lê um texto pequeno byte por byte (o par de `_gravar_texto_inteiro`: sem trocar o fim de linha). Levanta
    OSError."""
    return caminho.read_bytes().decode("utf-8", errors="replace")


def _copiar_somando(origem: Path, destino: Path) -> str:
    """Copia `origem` para `destino` e devolve a soma SHA256 do que foi lido (uma leitura só). Levanta OSError."""
    import hashlib

    soma = hashlib.sha256()
    with origem.open("rb") as de, destino.open("wb") as para:
        while True:
            pedaco = de.read(4 * 1024 * 1024)
            if not pedaco:
                break
            soma.update(pedaco)
            para.write(pedaco)
    return soma.hexdigest()


def guardar_ultima_boa(raiz: Path, versao_boa: str, fonte: "Fonte", chave_publica: str | None = None) -> str | None:
    """Guarda o pacote da versão que passou no teste rápido como a última boa (D-844). None = guardado e conferido;
    senão, o motivo. Nunca levanta.
    1. O pacote vem de `<raiz>\\packages\\` (o Velopack baixa a versão nova para lá, manager.rs 405-481, a troca não o
       apaga, e a abertura guarda o da versão atual: app.rs, `cleanup_old_packages_from_list`). O .msi NÃO o põe lá
       (conferido nas tabelas do nosso .msi): nesse caso quem chama baixa antes (`Atualizacao._baixar_a_que_roda`).
    2. A assinatura: a guardada ao conferir (em `ultima-boa\\`) ou, sem ela, a publicada (a fonte). Tem de ser do
       Samuel e afirmar este pacote.
    3. Copia para `<nome>.chegando` somando; só com a soma assinada dá o nome final (uma troca de nome no mesmo disco).
    4. Só então apaga os arquivos das outras versões (menos a assinatura de uma mais nova, que está chegando)."""
    pasta = pasta_da_ultima_boa(raiz)
    nome = nome_do_pacote(versao_boa)
    nome_da_assinatura = assinatura.nome_do_arquivo_da_assinatura(versao.ID_DO_PACOTE, versao_boa)
    origem = Path(raiz) / "packages" / nome
    if not origem.is_file():
        return f"o pacote da {versao_boa} não está em {origem.parent}"
    try:
        texto = _ler_texto(pasta / nome_da_assinatura)
    except OSError:
        try:
            texto = fonte.ler(versao_boa, nome_da_assinatura).decode("utf-8", errors="replace")
        except OSError as erro:
            return f"não achei a assinatura da {versao_boa} ({erro})"
    lido = assinatura.ler_assinatura(texto)
    if lido is None:
        return "o arquivo da assinatura não está no formato esperado"
    soma_assinada = lido[0].sha256.lower()
    motivo = assinatura.conferir_versao(texto, assinatura.VersaoAssinada(versao.ID_DO_PACOTE, versao_boa, nome,
                                                                         soma_assinada), chave_publica)
    if motivo is not None:
        return motivo
    chegando = pasta / (nome + ".chegando")
    try:
        pasta.mkdir(parents=True, exist_ok=True)
        _gravar_texto_inteiro(pasta / nome_da_assinatura, texto)
        if _copiar_somando(origem, chegando) != soma_assinada:
            chegando.unlink(missing_ok=True)
            return "a cópia do pacote não tem a soma assinada pelo Samuel"
        os.replace(chegando, pasta / nome)
    except OSError as erro:
        try:
            chegando.unlink(missing_ok=True)
        except OSError:
            pass
        return f"não consegui guardar o pacote ({erro})"
    for outro in list(pasta.iterdir()):
        if outro.name in (nome, nome_da_assinatura):
            continue
        if outro.name.endswith(".assinatura") and fases._mais_nova(_versao_do_nome(outro.name), versao_boa):
            continue                                   # a assinatura de uma versão mais nova, que está chegando
        try:
            outro.unlink()
        except OSError:
            pass
    return None


# ---------------------------------------------------------------------------------------------------------------------
# De onde vêm as versões (o GitHub do projeto, ou uma pasta no ensaio)
# ---------------------------------------------------------------------------------------------------------------------

class Fonte:
    """O lugar das versões publicadas: o GitHub do projeto (`Fonte.padrao()`, sem senha: D-713, D-719) ou, no ensaio
    e nos testes, uma pasta. A assinatura e o índice de uma versão ficam AO LADO do pacote: no GitHub, no mesmo
    "Release" (etiqueta v<versão>); na pasta, na mesma pasta. O Velopack recebe só o `endereco`."""

    def __init__(self, endereco: str):
        self.endereco = str(endereco)

    @classmethod
    def padrao(cls) -> "Fonte":
        return cls(REPOSITORIO)

    @property
    def e_github(self) -> bool:
        return self.endereco.startswith("https://github.com/")

    def endereco_do_arquivo(self, versao_do_arquivo: str, nome: str) -> str:
        """Onde está um arquivo publicado de uma versão (pacote, assinatura, índice)."""
        if self.e_github:
            return f"{self.endereco}/releases/download/v{versao_do_arquivo}/{nome}"
        return str(Path(self.endereco) / nome)

    def ler(self, versao_do_arquivo: str, nome: str, limite: int = 1_000_000) -> bytes:
        """Lê um arquivo pequeno publicado (a assinatura, o índice). Levanta OSError se não achar."""
        endereco = self.endereco_do_arquivo(versao_do_arquivo, nome)
        if not self.e_github:
            return Path(endereco).read_bytes()[:limite]
        import urllib.request

        with urllib.request.urlopen(endereco, timeout=60) as resposta:
            return resposta.read(limite)


def fonte_da_linha(argumentos: list[str], de_teste: Callable[[], "Fonte | None"] | None = None) -> Fonte:
    """A ÚNICA escolha de onde vêm as versões: 1. `--fonte <pasta>` (o ensaio e os testes); 2. a fonte de teste do
    administrador (`fonte_de_teste`; no notebook do Kaique não existe); 3. o GitHub do projeto. Em todos os casos a
    assinatura é conferida igual (D-724)."""
    if ARG_FONTE in argumentos:
        posicao = argumentos.index(ARG_FONTE)
        if posicao + 1 < len(argumentos):
            return Fonte(argumentos[posicao + 1])
    return (de_teste or fonte_de_teste)() or Fonte.padrao()


def _argumentos_da_fonte(fonte: Fonte) -> list[str]:
    """Repassa o `--fonte` do ensaio ao programa que o Velopack reabre."""
    return [] if fonte.e_github else [ARG_FONTE, fonte.endereco]


# A fonte de teste da etapa 5 (17/11/2026): para testar a atualização no programa INSTALADO sem publicar no GitHub. Só
# vale se o arquivo for do administrador ou do sistema (o dono, lido pela peça do Windows): uma conta comum consegue
# criar arquivo no ProgramData, mas fica ela de dona, e é ignorado. Mesmo valendo, só entra versão assinada (D-724).
ARQUIVO_DA_FONTE_DE_TESTE = "fonte-de-teste.txt"
DONOS_ACEITOS = ("S-1-5-32-544", "S-1-5-18")  # Administradores, o sistema


def caminho_da_fonte_de_teste() -> Path:
    """%ProgramData%\\EditorImpressao\\fonte-de-teste.txt (lido na hora: os testes trocam a variável)."""
    return pasta_do_estado().parent / ARQUIVO_DA_FONTE_DE_TESTE


def _dono_pela_peca(caminho: Path) -> str | None:
    """O dono do arquivo, pela peça do Windows (fora do Windows: None)."""
    if sys.platform != "win32":
        return None
    from core import windows

    return windows.dono_do_arquivo(caminho)


def fonte_de_teste(dono: Callable[[Path], str | None] = _dono_pela_peca) -> "Fonte | None":
    """A fonte de teste, ou None (o normal: o arquivo não existe). Ignorada, com uma linha no registro, se o dono não é
    o administrador nem o sistema, ou se a linha não é uma pasta que existe."""
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
    registrar(f"fonte de teste: as versões vêm de {pasta}")
    return Fonte(pasta)


# ---------------------------------------------------------------------------------------------------------------------
# Onde o programa está (só o disco)
# ---------------------------------------------------------------------------------------------------------------------

def pasta_do_programa() -> Path:
    """A pasta do EditorImpressao.exe (no Velopack, <raiz>\\current)."""
    return Path(sys.executable).resolve().parent


def instalado_pelo_velopack() -> bool:
    """O programa empacotado está numa instalação do Velopack (ou num pacote portátil dele)? O Velopack acha a
    instalação pelo manifesto `current\\sq.version` (locator.rs: `ManifestPath: root_dir.join("current")
    .join("sq.version")`). Pelo código (.venv, testes) é False: nada de Velopack, nada de aviso."""
    pasta = pasta_do_programa()
    return bool(getattr(sys, "frozen", False)) and pasta.name.lower() == "current" and (pasta / "sq.version").is_file()


def e_portatil(raiz: Path | None = None) -> bool:
    """O pacote PORTÁTIL do Velopack (uma pasta solta, o ensaio no PC do Samuel)? É o que o Velopack diz pelo arquivo
    `.portable` na raiz (locator.rs: `IsPortable: root_dir.join(".portable").exists()`). Portátil nunca pergunta ao
    Windows nem procura: não mexe no computador."""
    raiz = raiz if raiz is not None else pasta_do_programa().parent
    return (Path(raiz) / ".portable").exists()


def pasta_aceita_gravacao(raiz: Path) -> bool:
    """O "preparado?" (D-741, D-749): a conta que abriu consegue criar um arquivo na raiz da instalação AGORA? É o
    mesmo teste que o Velopack faz para decidir se a troca vai pedir licença ao Windows (misc.rs,
    `is_directory_writable`: abre `.velopack_dir_test` com apagar-ao-fechar; locator.rs 152-176 e apply_windows_impl.rs
    decidem por ele), com outro nome de arquivo. `os.O_TEMPORARY` é o apagar-ao-fechar do Windows. Por que não
    `os.access`: no Windows ele só olha o atributo "só leitura" (documentação do Python, `os.access`). Nunca levanta."""
    caminho = Path(raiz) / ARQUIVO_DO_TESTE_DE_GRAVAR
    try:
        descritor = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_TEMPORARY", 0))
    except OSError:
        return False
    os.close(descritor)
    if not hasattr(os, "O_TEMPORARY"):                 # fora do Windows (só nos testes)
        caminho.unlink(missing_ok=True)
    return True


def e_a_conta_de_testes(usuario: str | None = None) -> bool:
    """O programa está rodando na conta dos testes à distância (D-717, D-736)? A conta tem nome fixo
    (core.testes_a_distancia.NOME_DA_CONTA). A única regra de "aberto por um teste à distância"."""
    from core.testes_a_distancia import NOME_DA_CONTA

    nome = usuario if usuario is not None else (os.environ.get("USERNAME") or "")
    return nome.strip().lower() == NOME_DA_CONTA.lower()


# ---------------------------------------------------------------------------------------------------------------------
# As regras do preparo do computador (o lado com licença, core/windows.py, roda estas)
# ---------------------------------------------------------------------------------------------------------------------

def passos_do_preparo() -> list:
    """Os passos da pergunta do Windows, NESTA ORDEM (a peça para no primeiro que falha):
    1. apagar o ajudante antigo, se existir (D-838; ele rodava como o sistema um programa desta pasta: tem de sair
       ANTES de a pasta aceitar gravação de Usuários);
    2. instalar o Visual C++ de dentro do programa, se faltar (D-727);
    3. tirar a instalação antiga do Inno, se houver (D-723);
    4. por último, dar a Usuários a licença de Modificar na pasta do programa (D-837). Por ser o último, a pasta só
       aceita gravação se tudo antes deu certo: a preparação pela metade conta como não feita (D-749).
    Arriscado: mudar a ordem."""
    from core import windows

    return [windows.passo_apagar_tarefa(NOME_DA_TAREFA), windows.passo_instalar_visual_c(),
            windows.passo_tirar_instalacao_do_inno(), windows.passo_dar_licenca_aos_usuarios()]


def precisa_do_visual_c(instalada: tuple[int, int, int] | None, do_pacote: str) -> bool:
    """Roda o vc_redist se não há Visual C++ ou se o instalado é mais velho que o do pacote."""
    if instalada is None:
        return True
    try:
        maior, menor, build = (int(x) for x in do_pacote.split(".")[:3])
    except ValueError:
        return False
    return (maior, menor, build) > tuple(instalada)


def versao_do_visual_c_do_pacote(pasta: Path) -> str | None:
    """A versão do Visual C++ que vem no pacote, lida do arquivo da versão em <pasta>\\instalar\\; None se ele não existe.

    A LEITURA ÚNICA desse arquivo (passo 2, volta 8; CLAUDE.md §11.12: "um dado é lido e gravado por uma função só").
    Quem escreve é a montagem (empacotar.preparar_pasta_para_o_velopack, em UTF-8). Quem lê: a conferência do publicar
    (empacotar.conferir_pasta_pronta) e o programa instalado (instalar_visual_c_se_faltar). UTF-8, trocando o que não
    é UTF-8 pela marca de troca, sem os espaços e a quebra de linha das pontas. Um erro do disco ao ler sobe."""
    arquivo = Path(pasta) / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_VERSAO
    if not arquivo.is_file():
        return None
    return arquivo.read_text(encoding="utf-8", errors="replace").strip()


def instalar_visual_c_se_faltar(pasta: Path, ler: Callable[[], tuple | None],
                                rodar: Callable[[list[str], int], tuple[int, str]]) -> bool:
    """A regra do Visual C++ (D-727): o oficial que vai dentro do pacote, em silêncio, só se faltar; e CONFERE lendo de
    novo a versão instalada. False só quando tentou instalar e não ficou instalado (D-749). Sem o instalador no pacote
    ou sem precisar: True. Sem o arquivo da versão, "0.0.0" (só instala se não há Visual C++ nenhum), como antes.
    Quem chama: o passo `instalar_visual_c` da peça do Windows, com a licença (`ler` e `rodar` são dela)."""
    exe = Path(pasta) / PASTA_DO_QUE_SE_INSTALA / VC_REDIST_NOME
    if not exe.is_file():
        registrar(f"Visual C++: o pacote não tem {exe} (não instalei)")
        return True
    lida = versao_do_visual_c_do_pacote(Path(pasta))
    do_pacote = "0.0.0" if lida is None else lida
    if not precisa_do_visual_c(ler(), do_pacote):
        return True
    codigo, saida = rodar([str(exe), "/install", "/quiet", "/norestart"], 900)
    # 0 = instalou; 1638 = já havia uma mais nova; 3010 = instalou e pede reiniciar
    if codigo not in (0, 1638, 3010):
        registrar(f"Visual C++ {do_pacote}: NÃO instalado (código {codigo}) {saida}")
        return False
    if precisa_do_visual_c(ler(), do_pacote):
        registrar(f"Visual C++ {do_pacote}: o instalador terminou (código {codigo}), mas o Windows não mostra a versão "
                  "instalada; conta como não instalado")
        return False
    registrar(f"Visual C++ {do_pacote}: instalado (código {codigo})")
    return True


def achar_instalacao_do_inno(ler_chave: Callable[[], dict | None]) -> dict | None:
    """A instalação antiga do Inno Setup (a de 28/10 do Kaique), ou None: {"pasta", "desinstalador"} tirados do que a
    chave dela no registro diz (`ler_chave`, a leitura da peça do Windows)."""
    dados = ler_chave()
    if not dados:
        return None
    desinstalador = str(dados.get("UninstallString") or "").strip().strip('"')
    pasta = str(dados.get("InstallLocation") or "").strip().strip('"')
    if not desinstalador or not pasta:
        return None
    return {"pasta": Path(pasta), "desinstalador": Path(desinstalador)}


def comando_para_tirar_o_inno(antiga: dict, pasta_nova: Path) -> list[str] | None:
    """O comando que tira a instalação antiga, ou None se for arriscado demais.

    O desinstalador do Inno tira só o que ele instalou e as pastas _internal, motor-kraken e tesseract DENTRO da pasta
    dele ([UninstallDelete] do instalador.iss): nunca o %LOCALAPPDATA%\\EditorImpressao (os projetos do Kaique). Recusa
    se: o desinstalador não está dentro da pasta antiga, não é um unins*.exe, a pasta antiga é a mesma (ou contém) a do
    programa novo, ou é (ou contém) a pasta de dados da conta."""
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


# ---------------------------------------------------------------------------------------------------------------------
# O motor do Kraken no lugar dele (D-788; 4 consertos, 21/11/2026; atualizador novo: na conta de quem abriu)
# ---------------------------------------------------------------------------------------------------------------------

# Folga de espaço além do tamanho aberto do motor (o disco nunca fica cheio por causa dele).
FOLGA_DO_MOTOR_BYTES = 500 * 1024 * 1024


# O que o pacote de uma versão diz do motor (o publicar o põe dentro dele: empacotar.PASTA_NO_NUPKG +
# empacotar.NOME_DO_MOTOR_EXIGIDO; o programa não importa o empacotar.py, e um teste cobra que são iguais).
CAMINHO_DO_MOTOR_EXIGIDO_NO_PACOTE = "lib/app/motor-exigido.json"


def motor_exigido_pelo_pacote(arquivo: Path) -> int | None:
    """A versão do motor do Kraken que o pacote (`.nupkg`) de uma versão pede, lida do `motor-exigido.json` de dentro
    dele (volta 2, achado M2; D-833: "a versão nova só é anunciada com o motor DELA no lugar"). None se o pacote não
    abre, não tem o arquivo ou ele não diz um número. Quem chama confere a soma assinada do pacote antes de confiar."""
    import zipfile

    try:
        with zipfile.ZipFile(arquivo) as z:
            lido = json.loads(z.read(CAMINHO_DO_MOTOR_EXIGIDO_NO_PACOTE).decode("utf-8"))
        numero = lido.get("versao") if isinstance(lido, dict) else None
        return int(numero) if isinstance(numero, int) and not isinstance(numero, bool) else None
    except (OSError, KeyError, ValueError, zipfile.BadZipFile):
        return None


def motor_esta_no_lugar(raiz: Path | None = None, versao_do_motor: int | None = None) -> bool:
    """O motor do Kraken que este programa pede está inteiro no lugar dele (core/ocr_kraken.pasta_do_motor_instalado)?

    A regra única de "o motor está no lugar" (D-790, D-833). `versao_do_motor`: o motor de QUAL versão (a que vai
    entrar, lida do pacote dela: `motor_exigido_pelo_pacote`); None = o que este programa pede. Pelo código, no
    portátil ou fora de uma instalação do Velopack: True (o motor ali não é o da instalação, e nada é trocado). A
    conferência é a única do motor (core/ocr_kraken.conferir_motor: a ficha e o tamanho de cada arquivo)."""
    from core import ocr_kraken

    if raiz is None:
        if not instalado_pelo_velopack() or e_portatil():
            return True
        raiz = pasta_do_programa().parent
    versao_do_motor = ocr_kraken.VERSAO_DO_MOTOR if versao_do_motor is None else versao_do_motor
    return not ocr_kraken.conferir_motor(ocr_kraken.pasta_do_motor_instalado(raiz, versao_do_motor),
                                         versao_do_motor)


def _apagar_pasta_do_motor(pasta: Path) -> bool:
    """Apaga uma pasta de motor que ESTA função criou (a .chegando ou a estragada posta de lado). True se sumiu.

    shutil.rmtree no Windows não entra em atalho de pasta (junção): desde o Python 3.8 tira só o atalho (documentação
    do shutil). Só se chama com caminhos dentro de <raiz>\\motor-kraken\\."""
    import shutil

    shutil.rmtree(pasta, ignore_errors=True)
    return not pasta.exists()


def garantir_o_motor(raiz: Path | None = None, pacote: Path | None = None,
                     livre: Callable[[Path], int] | None = None) -> bool:
    """Põe o motor do Kraken no lugar dele, se ainda não estiver (D-788, D-727). True = o motor está no lugar.

    O ÚNICO lugar que mexe em <raiz>\\motor-kraken\\. Roda na conta de quem abriu o programa, por trás (a pasta do
    programa aceita gravação depois do preparo), nunca no portátil.
    1. Se o motor já confere (core/ocr_kraken.conferir_motor), nada.
    2. Senão, pega o arquivo do motor que veio no instalador: <current>\\instalar\\motor-kraken-<v>.zip
       (versao.arquivo_do_motor, o nome único). Sem ele: registra e devolve False (nada é anunciado nem trocado).
    3. Confere o espaço livre (o tamanho aberto mais FOLGA_DO_MOTOR_BYTES) antes de começar.
    4. Abre em <raiz>\\motor-kraken\\.chegando-<v> (o zipfile tira unidade, barras do começo e ".." dos nomes; um
       arquivo com a soma interna errada dá erro), confere com conferir_motor, e só então dá o nome final (um
       renomear no mesmo disco). Um motor estragado que estava no nome final é posto de lado e apagado antes.
    Qualquer erro: apaga o .chegando, registra e devolve False; nunca levanta; o nome final nunca fica pela metade.
    `livre` (os bytes livres do disco de um caminho) só muda nos testes. Nesta entrega não baixa motor da internet
    (D-790 fica para depois). Arriscado: abrir direto no nome final (um motor pela metade passaria pelo "está no
    lugar"); apagar fora de <raiz>\\motor-kraken\\."""
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
    except Exception as erro:  # noqa: BLE001 - QUALQUER erro: apaga, registra, devolve False
        sobrou = not _apagar_pasta_do_motor(chegando)
        registrar(f"motor do Kraken: não deu para pôr no lugar ({type(erro).__name__}: {erro})"
                  + ("; sobrou a pasta provisória" if sobrou else ""))
        return False
    registrar(f"motor do Kraken {versao_do_motor} posto em {destino}")
    return True


# ---------------------------------------------------------------------------------------------------------------------
# A assinatura e o teste rápido
# ---------------------------------------------------------------------------------------------------------------------

def conferir_assinatura_do(fonte: Fonte, alvo, chave_publica: str | None = None,
                           guardar_em: Path | None = None) -> str | None:
    """None se a versão `alvo` tem a assinatura certa do Samuel; senão, o motivo (D-724). `alvo`: o que o Velopack vai
    baixar (`conversa_com_o_velopack.VersaoDoVelopack`, ou um objeto com PackageId/Version/FileName/SHA256).
    `guardar_em` (volta 3): a pasta da última boa; com a assinatura certa, ela é guardada ali, para a versão nova virar a
    última boa depois do teste sem precisar de internet (`guardar_ultima_boa`). Não guardar não muda a resposta."""
    pacote = getattr(alvo, "pacote", None) or alvo.PackageId
    v = getattr(alvo, "versao", None) or alvo.Version
    arquivo = getattr(alvo, "arquivo", None) or alvo.FileName
    sha = getattr(alvo, "sha256", None) or alvo.SHA256
    nome = assinatura.nome_do_arquivo_da_assinatura(pacote, v)
    try:
        texto = fonte.ler(v, nome).decode("utf-8", errors="replace")
    except OSError as erro:
        return f"não achei a assinatura da versão {v} ({erro})"
    motivo = assinatura.conferir_versao(texto, assinatura.VersaoAssinada(pacote, v, arquivo, sha), chave_publica)
    if motivo is None and guardar_em is not None:
        try:
            Path(guardar_em).mkdir(parents=True, exist_ok=True)
            _gravar_texto_inteiro(Path(guardar_em) / nome, texto)
        except OSError as erro:
            registrar(f"a assinatura da {v} não ficou guardada (guardar a versão depois vai precisar de internet): "
                      f"{erro}")
    return motivo


def teste_rapido() -> int:
    """--teste-rapido: a versão instalada abre? (0 = sim). Sem janela.

    Importa o que o programa precisa para abrir (a janela, o processamento) e confere que as peças que vão dentro do
    pacote estão no lugar: os modelos e as DLLs (nos caminhos que o próprio código procura) e, no programa empacotado,
    o Tesseract ao lado do .exe e o motor do Kraken (achado e conferido pelas funções únicas de core/ocr_kraken; no
    programa instalado, em <raiz>\\motor-kraken\\<versão>). O que faltar vai para o registro."""
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
            from core import ocr_kraken

            motor = ocr_kraken.achar_pasta_do_motor()
            if motor is None:
                problemas.append("falta o motor do Kraken em " + ", ".join(map(str, ocr_kraken.lugares_do_motor())))
            else:
                problemas += ocr_kraken.conferir_motor(motor)
    except Exception as erro:  # noqa: BLE001 - qualquer erro aqui é "não abre"
        problemas.append(f"erro ao abrir: {type(erro).__name__}: {erro}")
    if problemas:
        registrar("teste rápido da versão instalada: " + "; ".join(problemas))
        return 1
    return 0


# ---------------------------------------------------------------------------------------------------------------------
# O executor
# ---------------------------------------------------------------------------------------------------------------------

def _por_tras(trabalho: Callable[[], object]) -> None:
    """Roda `trabalho` num fio solto (daemon), que não é o da tela e morre com o programa (fechar no meio não segura a
    saída; o trabalho com licença é outro processo e termina sozinho)."""
    threading.Thread(target=trabalho, name="atualizacao", daemon=True).start()


class Atualizacao:
    """O executor de uma abertura do programa instalado (ver o topo do arquivo). Um por processo
    (`da_abertura`).

    Tudo o que fala com o mundo de fora entra pelos argumentos, e os testes trocam só a borda: `windows` (a peça
    `core.windows`), `velopack` (`core.conversa_com_o_velopack`), `raiz` (a raiz da instalação), `fonte`, `por_tras`
    (quem roda o trabalho por trás; os testes rodam na hora), `pasta_grava` (o teste de gravar), `garantir_motor` e
    `motor_no_lugar` (o motor de uma versão), `teste` (o teste rápido) e `chave_publica` (os testes assinam com uma
    chave deles; no programa é sempre a do Samuel). A lógica entre eles é a de verdade.

    Como roda: `evento(e)` pede a fase nova à regra (`fases.proxima_fase`, sob a tranca) e roda os efeitos, no fio de
    quem mandou o evento; o resultado de cada efeito volta como evento novo. Alguns efeitos começam um fio por trás (o
    motor, a espera do preparo, o teste rápido e a guarda da última boa com a janela aberta, a conferência da troca do
    "Reiniciar agora"): tudo o que vem depois deles roda nesse fio, e a janela nunca espera. Os efeitos de tela vão
    para a janela por `ligar_a_tela`; os que chegam antes de a janela abrir esperam numa fila."""

    def __init__(self, *, windows=None, velopack=None, raiz: Path | None = None, fonte: Fonte | None = None,
                 por_tras: Callable[[Callable[[], object]], None] = _por_tras,
                 pasta_grava: Callable[[Path], bool] = pasta_aceita_gravacao,
                 garantir_motor: Callable[[], bool] | None = None,
                 motor_no_lugar: Callable[[], bool] | None = None,
                 teste: Callable[[], tuple[bool, str]] | None = None,
                 chave_publica: str | None = None) -> None:
        if windows is None:
            from core import windows
        if velopack is None:
            from core import conversa_com_o_velopack as velopack
        self.windows, self.velopack = windows, velopack
        self.raiz = Path(raiz) if raiz is not None else pasta_do_programa().parent
        self.fonte = fonte or Fonte.padrao()
        self._por_tras, self._pasta_grava = por_tras, pasta_grava
        self._garantir_motor = garantir_motor or (lambda: garantir_o_motor(self.raiz, self.raiz / "current"))
        self._motor_no_lugar = motor_no_lugar or (lambda versao_do_motor: motor_esta_no_lugar(self.raiz,
                                                                                              versao_do_motor))
        self._teste = teste or self._rodar_teste_rapido
        self._chave = chave_publica              # None = a do Samuel (assinatura.CHAVE_PUBLICA_DO_SAMUEL)
        self._estado = fases.Estado()
        self._tranca = threading.RLock()
        self._tela: Callable[[object], None] | None = None
        self._fila_da_tela: list = []
        self._achada = None                      # a versão achada (conversa_com_o_velopack.VersaoDoVelopack)
        self._somas_assinadas: dict[str, str] = {}
        self._pedido = None                      # o PedidoDeLicenca em andamento
        self.saida: int | None = None            # o efeito Sair: o código de saída, sem abrir a janela

    # ---- a regra e os efeitos

    @property
    def estado(self) -> fases.Estado:
        """A fase de agora (só para ler)."""
        return self._estado

    def evento(self, e) -> None:
        """Um acontecimento: a regra decide e os efeitos rodam. Nunca levanta (um erro inesperado vai para o
        registro; a janela continua)."""
        with self._tranca:
            novo, efeitos = fases.proxima_fase(self._estado, e)
            self._estado = novo
        for efeito in efeitos:
            try:
                self._fazer(efeito)
            except Exception as erro:  # noqa: BLE001 - a atualização nunca derruba o programa
                registrar(f"erro inesperado em {type(efeito).__name__}: {type(erro).__name__}: {erro}")

    def _fazer(self, ef) -> None:
        """Roda UM efeito (o despacho é por tipo; cada tipo tem a sua função)."""
        if isinstance(ef, fases.Registrar):
            registrar(ef.texto)
        elif isinstance(ef, fases.PedirLicenca):
            self._pedir_licenca()
        elif isinstance(ef, fases.EsperarPreparo):
            self._por_tras(self._esperar_preparo)
        elif isinstance(ef, fases.GarantirMotor):
            self._por_tras(self._conferir_o_motor)
        elif isinstance(ef, fases.Procurar):
            self._procurar()
        elif isinstance(ef, fases.ConferirAssinatura):
            self._conferir_assinatura()
        elif isinstance(ef, fases.Baixar):
            self._baixar()
        elif isinstance(ef, fases.Trocar):
            self._trocar(ef)
        elif isinstance(ef, fases.RodarTesteRapido):
            self._na_linha_ou_por_tras(ef.antes_da_janela, self._testar)
        elif isinstance(ef, fases.GuardarUltimaBoa):
            self._na_linha_ou_por_tras(not ef.por_tras, lambda: self._guardar(ef.versao))
        elif isinstance(ef, fases.Reprovar):
            reprovar(ef.versao, ef.motivo)
        elif isinstance(ef, fases.GuardarFrase):
            guardar_frase(ef.tipo, ef.versao, ef.motivo_da_tela)
        elif isinstance(ef, fases.Voltar):
            self.evento(self._voltar(ef))
        elif isinstance(ef, fases.ConferirTroca):
            # Volta 3, M2: a conferência (a soma do pacote inteiro, ~460 MB) roda por trás; a janela continua
            # respondendo e fecha quando ela termina (FecharJanela, entregue no fio da tela pela PonteDaTela).
            self._por_tras(lambda: self.evento(self.conferencia_da_troca(self._achada)))
        elif isinstance(ef, fases.ReabrirOPrograma):
            self._reabrir()
        elif isinstance(ef, fases.Sair):
            self.saida = ef.codigo
        elif isinstance(ef, (fases.MostrarVersaoNova, fases.MostrarFalha, fases.FecharJanela,
                             fases.PerguntarAoFechar)):
            self._para_a_tela(ef)
        else:
            registrar(f"efeito desconhecido: {ef!r}")

    def _na_linha_ou_por_tras(self, na_linha: bool, trabalho: Callable[[], object]) -> None:
        """Roda `trabalho` agora, neste fio (antes da janela, ou na reabertura sem janela, que sai logo depois), ou por
        trás (a janela abre enquanto ele roda)."""
        if na_linha:
            trabalho()
        else:
            self._por_tras(trabalho)

    # ---- a tela

    def ligar_a_tela(self, mostrar: Callable[[object], None]) -> None:
        """A janela abriu: daqui em diante os efeitos de tela vão para `mostrar` (ui/aviso_de_atualizacao.py), e os
        que esperavam na fila vão agora."""
        with self._tranca:
            self._tela = mostrar
            fila, self._fila_da_tela = self._fila_da_tela, []
        for ef in fila:
            self._para_a_tela(ef)

    def _para_a_tela(self, ef) -> None:
        """Entrega um efeito de tela à janela (ou guarda na fila). A frase de abertura só vai se esta conta ainda não a
        viu, e é marcada vista ao ir (uma vez só, D-719); a resposta a um clique (`sempre`) vai toda vez."""
        with self._tranca:
            if self._tela is None:
                self._fila_da_tela.append(ef)
                return
            mostrar = self._tela
        if isinstance(ef, fases.MostrarFalha) and not ef.sempre:
            if ef.nome in ler_vistos():
                return
            gravar_visto(ef.nome)
        mostrar(ef)

    # ---- os efeitos, um a um

    def _pedir_licenca(self) -> None:
        """A pergunta do Windows, ANTES da janela (D-806, D-834): volta logo depois da resposta."""
        self._pedido = self.windows.comecar_pedido_de_licenca(passos_do_preparo())
        if self._pedido.comecou:
            self.evento(fases.LicencaRespondida("comecou"))
            return
        r = self._pedido.resposta_da_pergunta
        desfecho = "disse_nao" if r.desfecho == self.windows.DISSE_NAO else "falhou"
        self.evento(fases.LicencaRespondida(desfecho, f"{r.motivo} {r.detalhe}".strip()))

    def _esperar_preparo(self) -> None:
        """Por trás: espera o trabalho com licença e testa DE NOVO se a pasta aceita gravação (o que vale é o teste,
        nunca o que o trabalho anotou, D-749)."""
        r = self._pedido.esperar()
        if not r.deu_certo:
            registrar(f"o trabalho com licença do preparo: {r.desfecho}: {r.motivo} {r.detalhe}".strip())
        self.evento(fases.PreparoTerminou(self._pasta_grava(self.raiz), f"{r.desfecho}: {r.motivo}"))

    def _conferir_o_motor(self) -> None:
        """Por trás: o motor do Kraken no lugar (põe, se faltar)."""
        no_lugar = bool(self._garantir_motor())
        self.evento(fases.MotorConferido(no_lugar, "" if no_lugar else "veja as linhas de cima do registro"))

    def _procurar(self) -> None:
        """Pergunta ao Velopack se há versão nova (sem internet: não é falha, só registro)."""
        try:
            self._achada = self.velopack.procurar(self.fonte.endereco)
        except Exception as erro:  # noqa: BLE001 - a peça só levanta ErroDoVelopack; qualquer outro é igual
            self.evento(fases.Procurou(None, str(erro) or type(erro).__name__))
            return
        self.evento(fases.Procurou(None if self._achada is None else self._achada.versao))

    def _conferir_assinatura(self) -> None:
        """A assinatura do Samuel na versão achada, ANTES de baixar (D-724). A soma assinada fica guardada para a
        conferência de antes da troca (`trocar_para`), e a assinatura, na pasta da última boa (volta 3: para guardar
        esta versão depois do teste, sem internet)."""
        motivo = conferir_assinatura_do(self.fonte, self._achada, self._chave, guardar_em=pasta_da_ultima_boa(self.raiz))
        if motivo is None:
            self._somas_assinadas[self._achada.versao] = self._achada.sha256
        self.evento(fases.Assinatura(motivo is None, motivo or ""))

    def _baixar(self) -> None:
        """Baixa a versão achada (o Velopack confere tamanho e soma) e diz se o motor que ela pede está no lugar
        (True/False), ou None se o pacote não diz qual pede (D-833, D-843)."""
        try:
            self.velopack.baixar(self.fonte.endereco, self._achada)
        except Exception as erro:  # noqa: BLE001
            self.evento(fases.Baixou(False, str(erro) or type(erro).__name__))
            return
        motor = motor_exigido_pelo_pacote(self.raiz / "packages" / self._achada.arquivo)
        self.evento(fases.Baixou(True, motor_da_nova=None if motor is None else bool(self._motor_no_lugar(motor))))

    def _testar(self) -> None:
        """O teste rápido da versão que roda, e o resultado como evento."""
        passou, detalhe = self._teste()
        self.evento(fases.TesteRapido(passou, detalhe))

    def _guardar(self, versao_boa: str) -> None:
        """Guarda o pacote da versão que passou no teste como a última boa (D-844), e o resultado como evento.

        D-851 (Samuel, 24/11/2026): "a última versão boa deve ser guardada copiando o pacote que já está na pasta
        packages\\ do programa [...] sem internet; baixar só se o arquivo não estiver lá." Conferido (volta 3, segunda
        parte; `volta3-provas/prova_packages-resultado.txt`): depois de cada troca o pacote da versão que roda está em
        `packages\\` (o Velopack o baixa para lá e a troca não o apaga); depois do .msi, NÃO está (o .msi não tem
        arquivo nenhum em `packages\\`: lido nas tabelas do nosso .msi da 1.1.0). Então: se está lá, só a cópia
        conferida (`guardar_ultima_boa`, sem internet); se não está, baixa pelo Velopack (`_baixar_a_que_roda`) e
        então a mesma cópia conferida."""
        motivo = None
        if not (self.raiz / "packages" / nome_do_pacote(versao_boa)).is_file():
            motivo = self._baixar_a_que_roda(versao_boa)
        if motivo is None:
            motivo = guardar_ultima_boa(self.raiz, versao_boa, self.fonte, self._chave)
        self.evento(fases.UltimaBoaGuardada(motivo is None, motivo or ""))

    def _baixar_a_que_roda(self, v: str) -> str | None:
        """Baixa para `packages\\` o pacote da versão que roda, quando ele não está lá (D-851; o caso do .msi). None =
        baixado; senão, o motivo. O tamanho e a soma vêm do índice publicado da versão (`releases.win.json`, como o
        publicar põe ao lado do pacote); a assinatura do Samuel tem de afirmar esse pacote (D-724) e fica guardada na
        pasta da última boa; o Velopack confere o tamanho e a soma do que baixou (manager.rs 537-561). Precisa de
        internet: sem ela, nada é guardado e a próxima abertura tenta de novo (o teste roda de novo, por trás)."""
        nome = nome_do_pacote(v)
        try:
            indice = json.loads(self.fonte.ler(v, NOME_DO_INDICE_PUBLICADO).decode("utf-8-sig"))
        except (OSError, ValueError) as erro:
            return f"o pacote da {v} não está em packages e o índice publicado não deu para ler ({erro})"
        itens = [a for a in (indice.get("Assets") or []) if isinstance(a, dict) and a.get("FileName") == nome]
        if not itens:
            return f"o pacote da {v} não está em packages e o índice publicado não tem {nome}"
        item = itens[0]
        try:
            alvo = self.velopack.pacote_da_versao(versao.ID_DO_PACOTE, v, nome, str(item.get("SHA256") or ""),
                                                  str(item.get("SHA1") or ""), int(item.get("Size") or 0))
        except Exception as erro:  # noqa: BLE001
            return f"não deu para montar o pedido da {v}: {erro}"
        motivo = conferir_assinatura_do(self.fonte, alvo, self._chave, guardar_em=pasta_da_ultima_boa(self.raiz))
        if motivo is not None:
            return f"o pacote publicado da {v} não tem a assinatura certa: {motivo}"
        try:
            self.velopack.baixar(self.fonte.endereco, alvo)
        except Exception as erro:  # noqa: BLE001
            return f"não consegui baixar o pacote da {v}: {erro}"
        return None

    def _trocar(self, ef) -> None:
        """O efeito Trocar: pela troca única (`trocar_para`). Um erro fora do previsto lá dentro vira "não pedida"
        (volta 3, leve 3: sem isto o "Reiniciar agora" fechava sem reabrir)."""
        try:
            pedida = self.trocar_para(self._achada, ef.de, ef.para, reabrir=True,
                                      sem_janela=ef.reabrir == fases.REABRIR_SEM_JANELA)
        except Exception as erro:  # noqa: BLE001
            pedida = fases.TrocaPedida(False, f"erro inesperado ao pedir a troca: {type(erro).__name__}: {erro}",
                                       motivo_da_tela=fases.MOTIVO_ERRO)
        self.evento(pedida)

    def conferencia_da_troca(self, v) -> "fases.TrocaConferida":
        """A CONFERÊNCIA ÚNICA de toda troca (o "Reiniciar agora" a faz por trás ANTES de fechar a janela, volta 2, M1,
        e volta 3, M2; e `trocar_para` a faz de novo logo antes de pedir). Devolve o evento `TrocaConferida` (pode,
        motivo, recusada, outra_janela, motivo_da_tela). Confere, nesta ordem:
        1. o pacote baixado está em `<raiz>\\packages\\` (com a raiz aceitando gravação, é onde o Velopack o põe:
           locator.rs 154-158) e a soma SHA256 DELE é a que a assinatura do Samuel afirma (conferida nesta abertura).
           Com a pasta aceitando gravação de Usuários, outra conta poderia trocar o arquivo depois de baixado; e o
           Velopack não confere de novo um arquivo que já está lá (manager.rs 413-416). Senão: recusada;
        2. o motor do Kraken que ESSA versão pede (o `motor-exigido.json` de dentro do pacote, já conferido pela soma)
           está no lugar (D-790, D-833);
        3. não há OUTRA janela do programa aberta (o Velopack a fecharia à força, com o que estivesse nela:
           apply_windows_impl.rs 159). Só o processo cujo caminho foi lido e está na pasta conta como "outra janela"
           (a frase da D-840); o que tem o nome de um programa da pasta mas o caminho não deu para ler é "não deu para
           conferir" (volta 3, M7: a frase da D-845, nunca a da outra janela). Sem a lista do Windows: não troca. Este
           processo e os que ele abriu (o servidor de páginas, o brasão) não contam."""
        if v is None:
            return fases.TrocaConferida(False, "não há versão baixada nesta abertura",
                                        motivo_da_tela=fases.MOTIVO_SEM_VERSAO)
        assinada = self._somas_assinadas.get(v.versao)
        arquivo = self.raiz / "packages" / v.arquivo
        if not assinada:
            return fases.TrocaConferida(False, f"a versão {v.versao} não teve a assinatura conferida nesta abertura",
                                        recusada=True)
        try:
            soma = assinatura.soma_sha256(arquivo)
        except OSError as erro:
            return fases.TrocaConferida(False, f"o pacote baixado não está em {arquivo.parent} ({erro})",
                                        motivo_da_tela=fases.MOTIVO_PACOTE_SUMIU)
        if soma.lower() != assinada.lower():
            return fases.TrocaConferida(False, "o pacote baixado não tem a soma assinada pelo Samuel (foi trocado "
                                               "depois de baixar)", recusada=True)
        motor = motor_exigido_pelo_pacote(arquivo)
        if motor is None:
            return fases.TrocaConferida(False, f"o pacote da versão {v.versao} não diz que motor do Kraken pede",
                                        motivo_da_tela=fases.MOTIVO_PACOTE_INCOMPLETO)
        if not self._motor_no_lugar(motor):
            return fases.TrocaConferida(False, f"o motor do Kraken {motor}, que a versão {v.versao} pede, não está no "
                                               "lugar", motivo_da_tela=fases.MOTIVO_MOTOR)
        outras = self.windows.programas_rodando_de(self.raiz / "current",
                                                   menos_a_familia_de=self.windows.numero_deste_processo())
        if outras is None:
            return fases.TrocaConferida(False, "não deu para saber se há outra janela do programa aberta",
                                        motivo_da_tela=fases.MOTIVO_SEM_LISTA)
        conferidas = [c for _, c in outras if self.windows.caminho_conferido(c)]
        if conferidas:
            return fases.TrocaConferida(False, "há outra janela do programa aberta: " + ", ".join(conferidas),
                                        outra_janela=True, motivo_da_tela=fases.MOTIVO_OUTRA_JANELA)
        if outras:
            return fases.TrocaConferida(False, "há um programa aberto com o nome de um da pasta, e o caminho dele não "
                                               "deu para ler: " + ", ".join(c for _, c in outras),
                                        motivo_da_tela=fases.MOTIVO_SEM_CONFERIR)
        return fases.TrocaConferida(True)

    def trocar_para(self, v, de: str, para: str, *, reabrir: bool, sem_janela: bool = False,
                    volta: bool = False) -> "fases.TrocaPedida":
        """A ÚNICA troca do programa (o "Reiniciar agora", o "Sim" ao fechar e a volta passam aqui). Devolve o evento
        `TrocaPedida`. Primeiro a conferência única (`conferencia_da_troca`); então pede
        (`conversa_com_o_velopack.trocar`). Nada é anotado antes (volta 3: a abertura seguinte olha o disco; o bilhete
        não decide a troca). O programa reaberto recebe `--conferir-a-versao-nova <de> <para>` (e `--sem-janela` no
        "Sim" ao fechar): se o Velopack não trocar, ele reabre a versão de antes com esse mesmo pedido (apply.rs
        56-60), e é assim que ela sabe que a troca não aconteceu (a frase da D-839). Na volta, nada (abre a anterior
        como uma abertura comum)."""
        c = self.conferencia_da_troca(v)
        if not c.pode:
            return fases.TrocaPedida(False, c.motivo, c.recusada, c.outra_janela, c.motivo_da_tela)
        argumentos = [] if volta else [ARG_CONFERIR_NOVA, de, para] + ([ARG_SEM_JANELA] if sem_janela else [])
        argumentos += _argumentos_da_fonte(self.fonte)
        try:
            self.velopack.trocar(self.fonte.endereco, v, reabrir, argumentos)
        except Exception as erro:  # noqa: BLE001
            return fases.TrocaPedida(False, f"o Velopack não aceitou a troca: {erro}",
                                     motivo_da_tela=fases.MOTIVO_ATUALIZADOR)
        return fases.TrocaPedida(True)

    def _reabrir(self) -> None:
        """Abre o programa de novo (volta 2, M1: o "Reiniciar agora" cuja troca não pôde ser pedida depois de a janela
        fechar). Pela peça do Windows (`lancar_solto`), que só dá certo quando o programa aberto deu sinal de vida
        (ele cria o arquivo do sinal logo ao começar: `ARG_SINAL_DE_VIDA`). Se não der, fica no registro."""
        try:
            pasta = self.windows.criar_pasta_de_troca()
        except OSError as erro:
            registrar(f"não consegui reabrir o programa: {erro}")
            return
        try:
            sinal = pasta / "sinal-de-vida"
            r = self.windows.lancar_solto([sys.executable, ARG_SINAL_DE_VIDA, str(sinal)], sinal, 60)
            registrar("o programa foi aberto de novo" if r.deu_certo
                      else f"não consegui reabrir o programa: {r.motivo} {r.detalhe}".strip())
        finally:
            self.windows.apagar_pasta_de_troca(pasta)

    def _voltar(self, ef) -> "fases.VoltaPedida":
        """A volta para a última boa (D-718, D-844): o pacote GUARDADO em `<raiz>\\ultima-boa\\`, sem internet. Confere
        que a assinatura guardada é do Samuel e afirma esse pacote; o Velopack copia o pacote para `packages\\`
        conferindo o tamanho e a soma que a assinatura afirma (a fonte de pasta do Velopack: sources/file.rs 37-48,
        `download_release_entry` copia o arquivo; manager.rs 537-561 confere); e a troca vai pela troca única. Só
        pacote assinado (D-724). Sem o pacote guardado: não dá (e a frase (3) da D-778 aparece)."""
        pasta = pasta_da_ultima_boa(self.raiz)
        pacote = versao.ID_DO_PACOTE
        nome = nome_do_pacote(ef.para)
        try:
            texto = _ler_texto(pasta / assinatura.nome_do_arquivo_da_assinatura(pacote, ef.para))
            tamanho = (pasta / nome).stat().st_size
        except OSError as erro:
            return fases.VoltaPedida(False, f"a versão {ef.para} não está guardada ({erro})")
        lido = assinatura.ler_assinatura(texto)
        if lido is None:
            return fases.VoltaPedida(False, f"a assinatura guardada da {ef.para} não está no formato esperado")
        sha256 = lido[0].sha256.lower()
        motivo = assinatura.conferir_versao(texto, assinatura.VersaoAssinada(pacote, ef.para, nome, sha256),
                                            self._chave)
        if motivo is not None:
            return fases.VoltaPedida(False, f"a versão guardada {ef.para} não tem a assinatura certa: {motivo}")
        try:
            v = self.velopack.pacote_da_versao(pacote, ef.para, nome, sha256, "", tamanho)
            self.velopack.baixar(str(pasta), v)
        except Exception as erro:  # noqa: BLE001
            return fases.VoltaPedida(False, f"o Velopack não aceitou o pacote guardado da {ef.para}: {erro}")
        self._somas_assinadas[ef.para] = sha256
        pedida = self.trocar_para(v, ef.de, ef.para, reabrir=ef.reabrir, volta=True)
        return fases.VoltaPedida(pedida.certa, pedida.motivo)

    def _rodar_teste_rapido(self) -> tuple[bool, str]:
        """O --teste-rapido num processo à parte, pela peça do Windows (um erro grave nele não derruba este)."""
        r = self.windows.rodar_e_esperar([sys.executable, ARG_TESTE_RAPIDO], limite_s=300)
        return r.deu_certo, f"código {r.dados.get('codigo')} {r.motivo}".strip()

    def _pendente(self) -> str:
        """A versão baixada esperando a troca, pelo Velopack ("" = nenhuma, ou não deu para saber: fica no registro)."""
        try:
            return self.velopack.pendente(self.fonte.endereco) or ""
        except Exception as erro:  # noqa: BLE001
            registrar(f"não deu para saber se há versão baixada esperando: {erro}")
            return ""

    # ---- a abertura

    def abrir(self, argumentos: list[str]) -> int | None:
        """A abertura (antes do brasão e da janela). Lê o que EXISTE agora (volta 3, emenda do Fable: a verdade vem do
        disco) e manda à regra: a versão que roda, a última boa (`ler_ultima_boa`), o pacote baixado esperando (o
        Velopack), se o atualizador do Velopack está rodando (só quando há troca possível e o programa não foi
        reaberto por ele), o pedido da reabertura (a linha de comando), as reprovadas e a frase do bilhete. Devolve o
        código de saída quando este processo sai sem janela, ou None para o programa abrir normalmente."""
        bilhete = ler_estado()
        de = para = ""
        if ARG_CONFERIR_NOVA in argumentos:
            i = argumentos.index(ARG_CONFERIR_NOVA)
            if len(argumentos) > i + 2:
                de, para = argumentos[i + 1], argumentos[i + 2]
        conta_de_testes, portatil = e_a_conta_de_testes(), e_portatil(self.raiz)
        fora = conta_de_testes or portatil
        grava = False if fora else self._pasta_grava(self.raiz)
        ultima = "" if fora else ler_ultima_boa(self.raiz)
        # Sem a licença na pasta nenhuma troca nossa acontece (o Velopack pediria licença): nem se pergunta.
        pendente = self._pendente() if grava else ""
        em_curso: bool | None = False
        if not fora and ARG_CONFERIR_NOVA not in argumentos and (pendente or (ultima and versao.VERSAO != ultima)):
            # Volta 2, G1: o atualizador do Velopack roda do pedido da troca até reabrir; o clique no atalho nesse
            # tempo abre a versão de antes (ou a nova antes da conferência). A reabertura dele traz o pedido na linha
            # de comando e não pergunta (o atualizador que a abriu ainda pode estar saindo).
            em_curso = self.windows.atualizador_do_velopack_rodando(self.raiz)
        self.evento(fases.Abriu(instalado=True, conta_de_testes=conta_de_testes, portatil=portatil,
                                pasta_grava=grava, versao=versao.VERSAO, ultima_boa=ultima,
                                nao_tentar=reprovadas_do_bilhete(bilhete), pendente=pendente,
                                troca_em_curso=em_curso, reaberto_de=de, reaberto_para=para,
                                sem_janela=ARG_SEM_JANELA in argumentos, frase_guardada=frase_do_bilhete(bilhete)))
        return self.saida


# As falhas já mostradas NESTA conta do Windows (para mostrar uma vez só): na pasta de dados da conta.
def _arquivo_dos_vistos() -> Path:
    """O arquivo das falhas já vistas (importa a pasta de dados só aqui: na hora de mostrar, com a janela aberta)."""
    from historico import pasta_de_dados

    return pasta_de_dados() / "atualizacao-avisos-vistos.json"


def ler_vistos() -> set[str]:
    """As falhas que esta conta já viu."""
    try:
        return set(json.loads(_arquivo_dos_vistos().read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        return set()


def gravar_visto(nome: str) -> None:
    """Marca a falha como vista nesta conta (nunca levanta)."""
    try:
        _arquivo_dos_vistos().write_text(json.dumps(sorted(ler_vistos() | {nome})), encoding="utf-8")
    except OSError:
        pass


# ---------------------------------------------------------------------------------------------------------------------
# Os ganchos do Velopack e a entrada pela linha de comando
# ---------------------------------------------------------------------------------------------------------------------

def ao_instalar(_versao) -> None:
    """Gancho do Velopack, depois de instalar: só anota (o .msi roda os ganchos SEM licença de administrador; a
    preparação é na primeira abertura)."""
    registrar(f"instalada a versão {_versao}")


def ao_atualizar(_versao) -> None:
    """Gancho do Velopack, depois de atualizar: só anota (a conferência da versão nova é na reabertura)."""
    registrar(f"atualizada para a versão {_versao}")


def ao_desinstalar(_versao, portatil: Callable[[], bool] = e_portatil) -> None:
    """Gancho do Velopack, antes de desinstalar: manda rodar o "desfazer" dos testes à distância, SE ele existir
    (D-731; sem os testes ligados, a tarefa não existe e só fica a linha no registro). O atualizador novo não pôs nada
    no Windows: o desinstalador do Velopack apaga a pasta do programa inteira, com o motor dentro. Nunca no portátil."""
    if portatil():
        return
    from core import testes_a_distancia

    feito = testes_a_distancia.mandar_desfazer()
    registrar(f"desfazer os testes à distância: {'mandado' if feito.ok else 'não mandado'} ({feito.mensagem})")


_DESTA_ABERTURA: Atualizacao | None = None


def da_abertura() -> Atualizacao | None:
    """O executor desta abertura (None pelo código, no portátil, na conta de testes, ou se a atualização nem começou):
    a janela o pega para ligar a tela (ui/aviso_de_atualizacao.ligar_na_janela)."""
    return _DESTA_ABERTURA


def atender_linha_de_comando(argv: list[str]) -> int | None:
    """A ÚNICA entrada da atualização (main.py chama antes do brasão e de qualquer janela).

    Devolve o código de saída quando o processo sai sem janela (o teste rápido; a reabertura sem janela; a volta), ou
    None para o programa abrir normalmente. Pelo código (.venv) e sem argumento do Velopack: não importa o velopack,
    não faz nada."""
    global _DESTA_ABERTURA
    argumentos = list(argv[1:])
    if ARG_SINAL_DE_VIDA in argumentos:              # reaberto pela atualização: o sinal de vida, antes de tudo
        i = argumentos.index(ARG_SINAL_DE_VIDA)
        if i + 1 < len(argumentos):
            try:
                Path(argumentos[i + 1]).write_bytes(b"")
            except OSError as erro:
                registrar(f"não consegui dar o sinal de vida: {erro}")
        del argumentos[i:i + 2]
    primeiro = argumentos[0] if argumentos else ""
    if primeiro == ARG_TESTE_RAPIDO:
        return teste_rapido()
    if primeiro == ARG_PROCURAR:
        registrar("o ajudante antigo chamou o programa: nada a fazer (o atualizador novo não usa ajudante)")
        return 0
    ganchos = any(a.startswith("--veloapp") for a in argumentos)
    if not instalado_pelo_velopack() and not ganchos:
        return None
    from core import conversa_com_o_velopack

    try:
        conversa_com_o_velopack.atender_ganchos(ao_instalar, ao_atualizar, ao_desinstalar)
    except conversa_com_o_velopack.ErroDoVelopack as erro:
        registrar(str(erro))                             # o programa abre mesmo assim
    if not instalado_pelo_velopack():
        return None
    try:
        _DESTA_ABERTURA = Atualizacao(fonte=fonte_da_linha(argumentos))
        saida = _DESTA_ABERTURA.abrir(argumentos)
    except Exception as erro:  # noqa: BLE001 - o programa abre mesmo assim, na versão de hoje
        registrar(f"abrir o programa: a atualização não começou: {type(erro).__name__}: {erro}")
        _DESTA_ABERTURA = None
        return None
    if _DESTA_ABERTURA.estado.fase is fases.Fase.FORA:
        _DESTA_ABERTURA = None
    return saida
