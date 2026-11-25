"""Mutações da volta 3 do atualizador novo (24/11/2026): TODAS as de antes, de novo, e as das proteções novas
(D-811 a D-813, D-827: cada proteção com o teste que a acusa quando desligada).

De onde vêm as listas: `relatorios/atualizador-novo/mutacoes.py` (as do implementador), `quem-tenta-quebrar-1/provas/
mutacoes_qtq.py` (as 17 do primeiro "quem tenta quebrar") e `quem-tenta-quebrar-2/provas/mutacoes_qtq2.py` (as 26 V do
segundo), importadas dos arquivos deles (nada copiado à mão). Para cada uma:
- o trecho existe uma vez no código de agora: roda como está;
- o trecho mudou porque a proteção mudou de lugar ou de jeito: a MESMA proteção desligada no código novo (`NO_CODIGO_NOVO`,
  com o porquê);
- a proteção saiu de propósito com o desenho da emenda do Fable (`SAIU`, com o porquê e o teste que cobra o contrário).
Depois, as proteções novas da volta 3 (`NOVAS`).

Roda NO LUGAR (o primeiro argumento é a pasta do ramo: a trava dos donos precisa do git do ramo, que uma cópia feita
com `git archive` não tem; a primeira tentativa numa cópia parou na conferência sem mutação por isso). Cada mutação:
troca o trecho (que tem de aparecer uma vez só), roda os arquivos de teste do atualizador (com `-x`) e devolve o
arquivo como estava (num `finally`; depois, `git status` tem de estar limpo). "SOBREVIVEU" = nenhum teste falhou.
Uso: python mutacoes_volta3.py <pasta do ramo>
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
AQUI = Path(__file__).resolve().parent
RELATORIOS = AQUI.parent
A, W, F, U = "atualizacao.py", "core/windows.py", "core/fases_da_atualizacao.py", "ui/aviso_de_atualizacao.py"
C, P = "core/conversa_com_o_velopack.py", "regras_dos_agentes/porteiro.py"
TESTES = ["tests/test_atualizador_volta4.py", "tests/test_atualizador_volta3.py", "tests/test_atualizador_d851.py", "tests/test_fases_da_atualizacao.py", "tests/test_atualizador_novo.py",
          "tests/test_atualizador_volta2.py", "tests/test_decisoes_atualizacao.py",
          "tests/test_atualizador_volta3_de_verdade.py", "tests/test_windows_preparo_do_computador.py",
          "tests/test_decisoes_ajudante_da_atualizacao.py", "tests/test_decisoes_preparo_d749.py",
          "tests/test_velopack_de_verdade.py", "tests/test_porteiro_licenca_que_acrescenta.py",
          "tests/test_decisoes_testes_a_distancia.py", "tests/test_trava_windows.py", "tests/test_windows_peca.py"]


def _carregar(caminho: Path, nome: str):
    """Importa a lista de um script de mutações de antes (eles leem a raiz do primeiro argumento)."""
    guardado = sys.argv
    sys.argv = [str(caminho), str(RAIZ)]
    try:
        spec = importlib.util.spec_from_file_location(nome, caminho)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
    finally:
        sys.argv = guardado
    return modulo


IMPL = _carregar(RELATORIOS / "mutacoes.py", "mutacoes_impl")
QTQ1 = _carregar(RELATORIOS / "quem-tenta-quebrar-1" / "provas" / "mutacoes_qtq.py", "mutacoes_qtq1")
QTQ2 = _carregar(RELATORIOS / "quem-tenta-quebrar-2" / "provas" / "mutacoes_qtq2.py", "mutacoes_qtq2")
# Volta 4: as 14 do terceiro "quem tenta quebrar" também.
QTQ3 = _carregar(RELATORIOS / "quem-tenta-quebrar-3" / "provas" / "mutacoes_qtq3.py", "mutacoes_qtq3")

# A mesma proteção, no código novo: nome da mutação de antes -> (porquê, arquivo, trecho, troca).
NO_CODIGO_NOVO = {
    "1 sem licença não procura": ("a regra da abertura ficou num lugar só (_ao_abrir)", F,
                                  "    if not e.pasta_grava:\n", "    if False:\n"),
    "9 outra janela aberta não troca": ("só a janela conferida pelo caminho é 'outra janela' (M7 b)", A,
                                        "        if conferidas:\n", "        if False:\n"),
    "11 a volta só com pacote assinado": ("a volta usa a assinatura guardada com a última boa (D-844)", A,
                                          "        if motivo is not None:\n            return fases.VoltaPedida(False, "
                                          "f\"a versão guardada {ef.para} não tem a assinatura",
                                          "        if False:\n            return fases.VoltaPedida(False, "
                                          "f\"a versão guardada {ef.para} não tem a assinatura"),
    "G1 a troca em curso não vira falha": ("sem a anotação da troca: o atualizador rodando faz sair sem janela", F,
                                           "    if e.troca_em_curso:\n", "    if False:\n"),
    "M1 reabrir o que falha depois de fechar": ("a reabertura leva a frase (D-845) e não reabre com outra janela", F,
                                                "        return replace(estado, fase=Fase.PARADO), efeitos + frase + "
                                                "[ReabrirOPrograma()]",
                                                "        return replace(estado, fase=Fase.PARADO), efeitos + frase"),
    "Q4 motor: 'esta no lugar' sempre sim": ("a conferência pede o motor de uma versão (volta 2)", A,
                                             "    return not ocr_kraken.conferir_motor(ocr_kraken.pasta_do_motor_"
                                             "instalado(raiz, versao_do_motor),\n"
                                             "                                         versao_do_motor)",
                                             "    return True"),
    "Q7 licenca da pasta: nao confere o arquivo de dentro (manifesto)": (
        "quem pede diz qual arquivo de dentro conferir (as duas pastas)", W,
        "    if conferir_dentro is not None and Path(conferir_dentro).is_file():", "    if False:"),
    "Q10 o disco: a versao que falhou nao entra em 'nao tentar'": ("a única que reprova é `reprovar`", A,
                                                                   "        b[\"reprovadas\"] = sorted(set("
                                                                   "reprovadas_do_bilhete(b)) | {versao_reprovada})",
                                                                   "        b[\"reprovadas\"] = sorted(set("
                                                                   "reprovadas_do_bilhete(b)))"),
    "Q16 a linha de comando da reabertura vale mais que a anotacao": (
        "a linha de comando da reabertura é o que diz que o Velopack reabriu a de antes (D-839)", A,
        "                de, para = argumentos[i + 1], argumentos[i + 2]", "                pass"),
    "V2 G1: em curso abre a janela em vez de sair": ("o mesmo, na regra nova", F,
                                                     "saio sem janela\"), Sair(0)]", "saio sem janela\")]"),
    "V3 G1: o Update.exe cujo caminho não deu para ler não conta": (
        "M7 a: o sem caminho virou 'não deu para saber'; a mutação o dá como parado", W,
        "    return None if any(not caminho_conferido(c) for _, c in achados) else False", "    return False"),
    "V5 G1: o executor pergunta também na reabertura com linha de comando": (
        "a pergunta só fora da reabertura (a da troca e, desde a volta 4, a da volta)", A,
        "        if not fora and not reaberto and (pendente or",
        "        if not fora and (pendente or"),
    "Q6 a reabertura pelo Velopack também pergunta se o atualizador roda (e sai, se ele ainda estiver saindo)": (
        "o mesmo do V5, no código da volta 4", A,
        "        if not fora and not reaberto and (pendente or",
        "        if not fora and (pendente or"),
    "Q1 motor: sem a conferencia do espaco livre": (
        "volta 4: o motor pergunta o espaço pela conta única (espaco_livre_basta)", A,
        "            cabe, tem = espaco_livre_basta(destino.parent, precisa, livre)\n            if not cabe:",
        "            cabe, tem = espaco_livre_basta(destino.parent, precisa, livre)\n            if False:"),
    "V26 a falha de teste não põe a versão em 'não tentar'": (
        "volta 4: a reprovação é posta antes de escolher entre a volta e a frase (3)", F,
        "        reprovada = replace(estado, nao_tentar=_com_mais(estado.nao_tentar, estado.nova))",
        "        reprovada = estado"),
    "Q1 a guarda apaga também a assinatura da versão mais nova que está chegando": (
        "volta 4: a limpeza só apaga as versões mais velhas", A,
        "        if v and (v == versao_boa or fases._mais_nova(v, versao_boa)):",
        "        if v and v == versao_boa:"),
    "Q4 D-839: a frase da troca recusada aparece também quando a troca deu certo": (
        "volta 4: a mesma condição, separada da volta", F,
        "    if e.reaberto_para and not e.reaberto_voltando and e.versao == e.reaberto_de and \\\n"
        "            _mais_nova(e.reaberto_para, e.versao):",
        "    if e.reaberto_para and not e.reaberto_voltando and \\\n"
        "            _mais_nova(e.reaberto_para, e.reaberto_de):"),
    "Q13 a cópia com a soma errada deixa o .chegando (460 MB) no disco": (
        "volta 4: a soma pela conta única", A,
        "        if assinatura.soma_sha256(origem, copiar_para=chegando) != soma_assinada:\n"
        "            chegando.unlink(missing_ok=True)\n",
        "        if assinatura.soma_sha256(origem, copiar_para=chegando) != soma_assinada:\n"),
    "Q14 a volta reabre com os argumentos da troca normal (a anterior acha que a troca foi recusada)": (
        "volta 4: a volta leva a marca dela", A,
        "        argumentos = ([ARG_VOLTANDO, de, para] if volta else",
        "        argumentos = ([ARG_CONFERIR_NOVA, para, de] if volta else"),
    "V6 M1: a conferência antes de fechar sempre diz 'pode'": ("a conferência roda por trás (M2)", A,
                                                              "            self._por_tras(lambda: self.evento("
                                                              "self.conferencia_da_troca(self._achada)))",
                                                              "            self._por_tras(lambda: self.evento("
                                                              "fases.TrocaConferida(True)))"),
    "V7 M1: a troca que falha depois de fechar não reabre": ("o mesmo que M1 acima", F,
                                                            "        return replace(estado, fase=Fase.PARADO), efeitos "
                                                            "+ frase + [ReabrirOPrograma()]",
                                                            "        return replace(estado, fase=Fase.PARADO), efeitos "
                                                            "+ frase"),
    "V10 M2: pacote sem o motor-exigido.json conta como motor no lugar (anunciar)": (
        "o 'não diz' é None (D-843 separa o motor que falta do pacote que não diz)", A,
        "motor_da_nova=None if motor is None else bool(self._motor_no_lugar(motor))",
        "motor_da_nova=True if motor is None else bool(self._motor_no_lugar(motor))"),
    "V20 D-840: outra janela sem a frase": ("a frase é o MostrarFalha do 'não deu agora' (D-846)", F,
                                            "                MostrarFalha(NAO_DEU_AGORA, motivo_da_tela="
                                            "MOTIVO_OUTRA_JANELA, sempre=True),\n",
                                            ""),
    "V21 D-841: outra janela sem o aviso de novo": ("o mesmo evento, sem o aviso", F,
                                                    "sempre=True),\n                MostrarVersaoNova(estado.nova)]",
                                                    "sempre=True)]"),
    "V22 D-840: 'não deu para saber' (sem a lista) também mostra a frase da outra janela": (
        "a conferência devolve a chave do motivo", A,
        "                                        motivo_da_tela=fases.MOTIVO_SEM_LISTA)",
        "                                        outra_janela=True, motivo_da_tela=fases.MOTIVO_OUTRA_JANELA)"),
    "V25 a ponte: a frase da outra janela não aparece": ("a ponte mostra toda frase pela escolha única", U,
                                                        "atualizacao.frase_da_falha(ef.tipo, ef.motivo_da_tela)",
                                                        "atualizacao.FRASE_DA_FALHA"),
}

# A proteção saiu de propósito com o desenho novo (a emenda do Fable): nome -> o porquê e o teste do que vale hoje.
SAIU = {
    "M4 a troca só com a anotação gravada": "a troca não depende mais do bilhete (emenda, A e M5); o contrário é "
                                            "cobrado por test_m5_o_bilhete_preso_nao_impede_a_troca_do_reiniciar_agora",
    "M4 nada procurado sem o estado gravando": "a emenda manda continuar atualizando (M4); o contrário é cobrado por "
                                               "test_m4_o_bilhete_que_nao_grava_nao_para_a_atualizacao e pela N7",
    "V1 G1: 'não deu para saber' conta como 'a troca acabou' (anota falha)": "a anotação da troca saiu; nada é anotado "
                                                                           "numa troca (test_g1_sem_saber...)",
    "V14 M4: a troca é pedida mesmo sem a anotação gravada": "o mesmo do 'M4 a troca só com a anotação gravada'",
    "V15 M4: o estado sempre 'aceita gravação'": "a conferência de gravar o estado em toda abertura saiu (leve 4)",
    "V16 M4: sem o estado gravando, procura mesmo assim": "o mesmo do 'M4 nada procurado sem o estado gravando'",
    "Q17 a anotacao velha (de outra versao) nao e apagada": "a anotação da troca saiu: não há anotação velha "
                                                            "(a abertura olha o disco)",
}
# O trecho de antes ainda existe, mas a proteção mudou de lugar: vai pelo equivalente.
FORCAR = {"9 outra janela aberta não troca"}

# As proteções novas da volta 3: (nome, arquivo, trecho, troca).
NOVAS = [
    ("N1 G1/A: rodando o que não é a última boa, o teste antes da janela", F,
     "    if _precisa_do_teste(e):\n", "    if False:\n"),
    ("N2 D-844: a volta pela pasta da última boa, sem internet", A,
     "            self.velopack.baixar(str(pasta), v)", "            self.velopack.baixar(self.fonte.endereco, v)"),
    ("N3 D-844: a guarda confere a soma da cópia", A,
     "        if assinatura.soma_sha256(origem, copiar_para=chegando) != soma_assinada:",
     "        if assinatura.soma_sha256(origem, copiar_para=chegando) and False:"),
    ("N4 a guarda copia para o nome provisório", A,
     "    chegando = pasta / (nome + \".chegando\")", "    chegando = pasta / nome"),
    ("N5 M1: a assinatura recusada não reprova", F,
     "            MostrarFalha(FALHA_RECUSADA, id_da_falha(FALHA_RECUSADA, estado.nova))]\n\n    if isinstance(e, Baixou)",
     "            MostrarFalha(FALHA_RECUSADA, id_da_falha(FALHA_RECUSADA, estado.nova)), Reprovar(estado.nova, \"x\")]"
     "\n\n    if isinstance(e, Baixou)"),
    ("N6 G1: a frase (1) só rodando a última boa", F,
     "    if e.ultima_boa and e.versao == e.ultima_boa and reprovadas_mais_novas and not novo.sem_janela:",
     "    if reprovadas_mais_novas and not novo.sem_janela:"),
    ("N7 M4: a abertura volta a exigir que o bilhete grave", A,
     "        grava = False if fora else self._pasta_grava(self.raiz)",
     "        grava = False if fora else (self._pasta_grava(self.raiz) and gravar_estado(ler_estado()))"),
    ("N8 M2: a conferência no fio de quem clicou", A,
     "            self._por_tras(lambda: self.evento(self.conferencia_da_troca(self._achada)))",
     "            (lambda f: f())(lambda: self.evento(self.conferencia_da_troca(self._achada)))"),
    ("N9 M3: o 'não deu agora' sem a frase (D-845)", F,
     "            MostrarFalha(NAO_DEU_AGORA, motivo_da_tela=e.motivo_da_tela or MOTIVO_ERRO, sempre=True)]",
     "            ]"),
    ("N10 M5: com outra janela aberta no fechar, reabre", F,
     "        if e.outra_janela:\n            # Volta 3, M5", "        if False:\n            # Volta 3, M5"),
    ("N11 M3/M5: a reabertura sem a frase", F,
     "        return replace(estado, fase=Fase.PARADO), efeitos + frase + [ReabrirOPrograma()]",
     "        return replace(estado, fase=Fase.PARADO), efeitos + [ReabrirOPrograma()]"),
    ("N12 M6: o motor novo sem a frase (D-843)", F,
     "                MostrarFalha(FALHA_MOTOR, id_da_falha(FALHA_MOTOR, estado.nova))]", "                ]"),
    ("N13 M7 b: o processo sem caminho pode trocar", A, "        if outras:\n", "        if False:\n"),
    ("N14 M7 a: o Update.exe sem caminho volta a contar como rodando", W,
     "    return None if any(not caminho_conferido(c) for _, c in achados) else False",
     "    return True if any(not caminho_conferido(c) for _, c in achados) else False"),
    ("N15 M8: o título da caixa (D-846)", U,
     "            self._avisar(self.janela, atualizacao.TITULO_DA_FALHA,\n",
     "            self._avisar(self.janela, atualizacao.TITULO_DA_VERSAO_NOVA,\n"),
    ("N16 L1: os testes no ProgramData de verdade", "tests/conftest.py",
     "    os.environ[\"PROGRAMDATA\"] = str(_ESTA_RODADA / \"ProgramData\")", "    pass"),
    ("N17 L3: o erro fora do previsto na troca engolido", A,
     "        except Exception as erro:  # noqa: BLE001\n            pedida = fases.TrocaPedida(False, f\"erro inesperado",
     "        except ZeroDivisionError as erro:  # noqa: BLE001\n            pedida = fases.TrocaPedida(False, f\"erro "
     "inesperado"),
    ("N18 L4: a abertura regrava o bilhete", A,
     "        bilhete = ler_estado()\n        de = para = \"\"",
     "        bilhete = ler_estado()\n        gravar_estado(bilhete)\n        de = para = \"\""),
    ("N19 M4: a pergunta única sem a pasta do registro", W,
     "        return dar_licenca_aos_usuarios(do_registro, do_registro / \"atualizacao.log\")",
     "        return da_raiz"),
    ("N20 a licença na pasta com arquivo ligado", W,
     "    if ligacoes:\n        return _falhou(", "    if False:\n        return _falhou("),
    ("N21 a pasta do registro que é um atalho", W,
     "    if e_atalho(mae) or e_atalho(pasta):\n        raise OSError(f\"a pasta do registro da atualização é um atalho "
     "para outro lugar ({pasta})\")\n    pasta.mkdir(parents=True, exist_ok=True)\n    if e_atalho(mae) or e_atalho(pasta):",
     "    pasta.mkdir(parents=True, exist_ok=True)\n    if False:"),
    ("N22 D-769: a guarda sem janela vai por trás (o processo sai antes)", F,
     "GuardarUltimaBoa(estado.nova, por_tras=not estado.sem_janela)", "GuardarUltimaBoa(estado.nova, por_tras=True)"),
    ("N23 a volta só com uma última boa diferente (sem ela: a frase 3 e para, D-857)", F,
     "        if estado.anterior and estado.anterior != estado.nova:\n            return (replace(reprovada, fase=Fase.VOLTANDO),",
     "        if True:\n            return (replace(reprovada, fase=Fase.VOLTANDO),"),
    ("N24 o bilhete só com as duas chaves", A,
     "    limpo = {k: lido[k] for k in CHAVES_DO_BILHETE if k in lido}", "    limpo = dict(lido)"),
    ("N25 D-839: a troca recusada pelo Windows sem a frase", F,
     "                              \"quando ela for achada de novo\")] + _frase(novo, FALHA_TROCA, e.reaberto_para)",
     "                              \"quando ela for achada de novo\")]"),
    ("N26 D-844: a última boa sem a assinatura ao lado conta", A,
     "               if v and assinatura.nome_do_arquivo_da_assinatura(versao.ID_DO_PACOTE, v) in nomes]",
     "               if v]"),
    ("N27 a assinatura da versão que chega não é guardada", A,
     "            motivo = conferir_assinatura_do(self.fonte, self._achada, self._chave,\n"
     "                                            guardar_em=pasta_da_ultima_boa(self.raiz))",
     "            motivo = conferir_assinatura_do(self.fonte, self._achada, self._chave)"),
    ("N28 o pendente é perguntado sem a licença", A,
     "        pendente = self._pendente() if grava else \"\"", "        pendente = self._pendente()"),
    # Volta 3, segunda parte (D-851): a última boa copiada de packages; baixada só se não estiver lá.
    # (N29 a N31 eram do download da D-851, que a D-857 tirou: saíram com ele.)
    ("N32 D-848: o pacote trocado no Reiniciar agora com a frase da D-845", F,
     "                MostrarFalha(FALHA_RECUSADA, id_da_falha(FALHA_RECUSADA, estado.nova), sempre=True)]",
     "                MostrarFalha(NAO_DEU_AGORA, motivo_da_tela=MOTIVO_ERRO, sempre=True)]"),
    # Volta 4: as três regras do Samuel, o "Sim" ao fechar, o pacote esperando, a rede na assinatura, L1 e L5.
    ("P1 D-855: a volta sem a marca --voltando", A,
     "        argumentos = ([ARG_VOLTANDO, de, para] if volta else", "        argumentos = ([] if volta else"),
    ("P2 D-855: a reaberta da volta recusada testa de novo", F,
     "    if e.reaberto_voltando and e.reaberto_de and e.versao == e.reaberto_de:", "    if False:"),
    ("P3 D-863: a volta recusada não deixa a marca de sem volta", F,
     "                            f\"{e.versao}): não tento de novo\"), MarcarSemVolta(e.versao)]",
     "                            f\"{e.versao}): não tento de novo\")]"),
    ("P4 D-863: a marca de sem volta não é olhada", F,
     "    if e.versao == e.ultima_boa or e.aprovada or e.sem_volta:", "    if e.versao == e.ultima_boa or e.aprovada:"),
    ("P5 D-863: a volta que nem pode ser pedida não marca", F,
     "    efeitos: list[Efeito] = [Registrar(motivo), MarcarSemVolta(estado.nova)] + _frase(estado, FALHA_VOLTA, estado.nova)",
     "    efeitos: list[Efeito] = [Registrar(motivo)] + _frase(estado, FALHA_VOLTA, estado.nova)"),
    ("P6 D-856: a marca de aprovada não é posta", F,
     "                MarcarAprovada(estado.nova), GuardarUltimaBoa(estado.nova, por_tras=not estado.sem_janela)]",
     "                GuardarUltimaBoa(estado.nova, por_tras=not estado.sem_janela)]"),
    ("P7 D-856: a marca de aprovada não é olhada", F,
     "    if e.versao == e.ultima_boa or e.aprovada or e.sem_volta:", "    if e.versao == e.ultima_boa or e.sem_volta:"),
    ("P8 D-856: a guarda não confere o espaço", A,
     "        if not cabe:\n            return (f\"falta espaço para guardar", "        if False:\n            return (f\"falta espaço para guardar"),
    ("P9 D-857: a primeira versão do .msi é testada", F,
     "    return bool(e.ultima_boa) or e.pacote_da_versao", "    return True"),
    ("P10 D-857: sem última boa, a falha não mostra a frase (3)", F,
     "        fase_nova, efeitos = _volta_que_nao_deu(reprovada, f\"{motivo}; não há versão guardada para voltar\")",
     "        fase_nova, efeitos = replace(reprovada, fase=Fase.MOTOR), [GarantirMotor()]"),
    ("P11 D-858: o Sim ao fechar sem a frase", F,
     "            return replace(estado, fase=Fase.PARADO), efeitos + [GuardarFrase(NAO_DEU_AGORA, estado.nova,",
     "            return replace(estado, fase=Fase.PARADO), efeitos + [] or efeitos + [GuardarFrase(NAO_DEU_AGORA, estado.nova,"),
    ("P12 D-864: o Sim ao fechar com outra janela usa o motivo genérico", F,
     "            motivo_da_tela = MOTIVO_HAVIA_OUTRA_JANELA if e.outra_janela else (e.motivo_da_tela or MOTIVO_ERRO)",
     "            motivo_da_tela = e.motivo_da_tela or MOTIVO_ERRO"),
    ("P13 D-859: sem internet o pacote esperando não é oferecido", F,
     "            if estado.pendente and _mais_nova(estado.pendente, estado.versao) and \\",
     "            if False and \\"),
    ("P14 D-859: o pacote esperando reprovado é oferecido", F,
     "                    estado.pendente not in estado.nao_tentar:", "                    True:"),
    ("P15 a rede que não responde vira recusada", F,
     "        if e.sem_rede:\n            # Volta 4", "        if False:\n            # Volta 4"),
    ("P16 a fonte de pasta inacessível conta como 'não existe'", A,
     "            if not Path(self.endereco).is_dir():\n                raise ConnectionError",
     "            if False:\n                raise ConnectionError"),
    ("P17 L1: a assinatura da última boa antes do pacote conferido", A,
     "        os.replace(chegando, pasta / nome)\n        _gravar_texto_inteiro(pasta / nome_da_assinatura, texto)",
     "        _gravar_texto_inteiro(pasta / nome_da_assinatura, texto)\n        os.replace(chegando, pasta / nome)"),
    ("P18 a assinatura que chega fica com o nome da última boa", A,
     "            _gravar_texto_inteiro(Path(guardar_em) / (nome + \".chegando\"), texto)",
     "            _gravar_texto_inteiro(Path(guardar_em) / nome, texto)"),
]


def _rodar_uma(nome: str, arquivo: str, de: str, para: str) -> str:
    """Desliga uma proteção, roda os testes e devolve a linha do resultado."""
    caminho = RAIZ / arquivo
    original = caminho.read_bytes()
    texto = original.decode("utf-8")
    if "\r\n" in texto:
        de, para = de.replace("\n", "\r\n"), para.replace("\n", "\r\n")
    n = texto.count(de)
    if n != 1:
        return f"[ERRO DA MUTAÇÃO] {nome}: o trecho aparece {n} vezes"
    try:
        caminho.write_bytes(texto.replace(de, para).encode("utf-8"))
        feito = subprocess.run([sys.executable, "-m", "pytest", *TESTES, "-q", "-p", "no:cacheprovider", "-x",
                                f"--basetemp={RAIZ / 'saida_teste' / 'mut3-tmp'}"],
                               cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               env={**os.environ, "PROGRAMDATA": str(RAIZ / "saida_teste" / "mut3-pd")})
    finally:
        caminho.write_bytes(original)
    fim = (feito.stdout.strip().splitlines() or ["?"])[-1]
    falhou = [linha for linha in feito.stdout.splitlines() if linha.startswith(("FAILED", "ERROR"))][:1]
    if feito.returncode == 0:
        return f"SOBREVIVEU  {nome} | {fim}"
    return f"acusada     {nome} | {fim} | {falhou[0][:170] if falhou else ''}"


def main() -> int:
    linhas: list[str] = []
    contas = {"acusada": 0, "SOBREVIVEU": 0, "saiu": 0, "erro": 0}

    def anotar(linha: str) -> None:
        linhas.append(linha)
        print(linha, flush=True)
        for chave in contas:
            if linha.startswith(chave) or (chave == "erro" and linha.startswith("[ERRO")) or \
                    (chave == "saiu" and linha.startswith("saiu")):
                contas[chave] += 1

    # `--so N26,Q4`: só essas (pelo primeiro nome), de todas as listas; a saída vai para outro arquivo, e a rodada
    # inteira continua guardada no de sempre.
    so = sys.argv[sys.argv.index("--so") + 1].split(",") if "--so" in sys.argv else None

    def de_antes(rotulo: str, lista, quatro: bool) -> None:
        anotar(f"== {rotulo}")
        for item in lista:
            nome, arquivo, de, para = item[:4]
            if so is not None and nome.split()[0] not in so:
                continue
            texto = (RAIZ / arquivo).read_text(encoding="utf-8").replace("\r\n", "\n")
            if texto.count(de) == 1 and nome not in FORCAR:
                anotar(_rodar_uma(nome, arquivo, de, para))
            elif nome in NO_CODIGO_NOVO:
                porque, arq2, de2, para2 = NO_CODIGO_NOVO[nome]
                anotar(_rodar_uma(f"{nome} (no código novo: {porque})", arq2, de2, para2))
            elif nome in SAIU:
                anotar(f"saiu        {nome} | {SAIU[nome]}")
            else:
                anotar(f"[ERRO DA MUTAÇÃO] {nome}: o trecho não existe mais e não há o equivalente")

    # Antes de tudo, sem mutação nenhuma, os testes juntos têm de passar (senão "acusada" não quer dizer nada: um teste
    # que falha sozinho acusaria todas). Foi assim que se achou que as frases "já vistas" vazavam de um teste para outro.
    base = subprocess.run([sys.executable, "-m", "pytest", *TESTES, "-q", "-p", "no:cacheprovider",
                           f"--basetemp={RAIZ / 'saida_teste' / 'mut3-tmp'}"], cwd=RAIZ, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env={**os.environ, "PROGRAMDATA": str(RAIZ / "saida_teste" / "mut3-pd")})
    anotar(f"== sem mutação: {(base.stdout.strip().splitlines() or ['?'])[-1]}")
    if base.returncode != 0:
        anotar("PAROU: sem mutação os testes já falham")
        # (com `--so`, no arquivo da segunda rodada: uma rodada que parou não apaga a rodada inteira guardada)
        (AQUI / ("mutacoes_volta3-resultado.txt" if so is None else "mutacoes_volta3-resultado-segunda-rodada.txt")
         ).write_text("\n".join(linhas) + "\n", encoding="utf-8")
        return 1
    # As listas de antes (com `--so`, `de_antes` só roda as escolhidas).
    if True:
        de_antes("mutacoes.py (as do implementador)", IMPL.MUTACOES, False)
        de_antes("mutacoes_qtq.py (as 17 do primeiro quem tenta quebrar)", QTQ1.MUTACOES, True)
        de_antes("mutacoes_qtq2.py (as 26 V do segundo quem tenta quebrar)", QTQ2.MUTACOES, True)
        de_antes("mutacoes_qtq3.py (as 14 do terceiro quem tenta quebrar)", QTQ3.MUTACOES, True)
    anotar("== as proteções novas da volta 3" + (f" (só {', '.join(so)})" if so else ""))
    for nome, arquivo, de, para in NOVAS:
        if so is None or nome.split()[0] in so:
            anotar(_rodar_uma(nome, arquivo, de, para))
    resumo = (f"{contas['acusada']} acusadas, {contas['SOBREVIVEU']} sobreviveram, {contas['saiu']} saíram com o "
              f"desenho (com o porquê), {contas['erro']} erros de mutação")
    anotar(resumo)
    saida = "mutacoes_volta3-resultado.txt" if so is None else "mutacoes_volta3-resultado-segunda-rodada.txt"
    (AQUI / saida).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return contas["SOBREVIVEU"] + contas["erro"]


if __name__ == "__main__":
    raise SystemExit(main())
