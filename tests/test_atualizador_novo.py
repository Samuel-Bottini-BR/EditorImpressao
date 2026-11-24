"""O executor do atualizador novo (atualizacao.py, 23/11/2026, D-830) pelos caminhos de verdade, com as duas peças de
fora de mentira SÓ NA BORDA.

O que é de mentira aqui (e por quê, D-767): a peça do Windows (`WindowsFalso`: a pergunta do Windows, a lista de
processos) e a peça do Velopack (`VelopackFalso`: procurar, baixar, trocar). Cada uma só ANOTA o que lhe pediram e
devolve o que o teste manda. Todo o resto é o de verdade: a regra (`core/fases_da_atualizacao.py`), o executor, o
`estado.json` e o registro no disco (numa pasta de prova), as assinaturas (com uma chave de prova, pela conferência
única `assinatura.conferir_versao`), a soma do pacote baixado, os textos da tela. O que mexe no Windows de verdade só
conta como pronto na prova à vista com o Samuel (ONDE-PAREI, "O que ficou para a prova à vista").

As proteções do plano (seção 11), uma prova cada, que FALHA quando a proteção é desligada (o nome diz qual):
(1) sem licença não procura; (2) a assinatura antes de baixar; (3) a soma do arquivo baixado antes de trocar; (4) o
motor antes de anunciar e antes de trocar; (5) a licença é o último passo; (6) o ajudante antigo sai antes da licença;
(7) a conta de testes não procura nem pergunta; (8) a versão que falhou não é tentada de novo; (9) outra janela aberta
não troca; (10) a troca só depois de a janela fechar; (11) a volta só com pacote assinado; (12) pelo código nada roda;
(13) só `trocar_para` chama a troca do Velopack.
"""

from __future__ import annotations

import ast
import json
import sys
import warnings
from pathlib import Path

import pytest

import assinatura
import atualizacao
import versao
from core import conversa_com_o_velopack as conversa
from core import fases_da_atualizacao as fases
from core import windows

from tests.ajudante_do_atualizador import (ANTERIOR, ATUAL, NOVA, OUTRA_CHAVE, PACOTE, PUBLICA, Prova, _ate_o_aviso,
                                          _estado, _publicar, _registro, programdata_de_prova)  # noqa: F401

RAIZ_DO_REPOSITORIO = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _programdata(programdata_de_prova):
    """O estado.json e o registro numa pasta de prova (a fixture do ajudante)."""


# ---------------------------------------------------------------------------------------------------------------------
# A primeira abertura e a pergunta do Windows
# ---------------------------------------------------------------------------------------------------------------------

def test_protecao_1_sem_licenca_pergunta_ao_windows_e_nao_procura(tmp_path):
    """D-735/D-741/D-806/D-834: a pasta do programa não aceita gravação → a pergunta do Windows é feita DENTRO da
    abertura (antes de `abrir` voltar, isto é, antes do brasão e da janela, que o main.py só abre depois), e com o
    "Não" nada é procurado nem baixado. Desligar a proteção (procurar sem a licença) faria `procurar` aparecer."""
    p = Prova(tmp_path, grava=False, licenca="disse_nao")
    assert p.abrir() is None
    assert p.win.pedidos == [["apagar_tarefa", "instalar_visual_c", "tirar_instalacao_do_inno",
                              "dar_licenca_aos_usuarios"]]
    assert p.vp.chamadas == []
    assert p.atual.estado.fase is fases.Fase.PARADO
    assert "disse Não" in _registro()


def test_d741_depois_do_nao_a_pergunta_volta_na_proxima_abertura(tmp_path):
    """D-741 ("Sim": a pergunta volta a cada abertura até o "Sim"): duas aberturas com a pasta sem a licença, duas
    perguntas. Nada é anotado como "preparado": o que vale é o teste de gravar de cada abertura."""
    p = Prova(tmp_path, grava=False, licenca="disse_nao")
    p.abrir()
    p.atual = atualizacao.Atualizacao(windows=p.win, velopack=p.vp, raiz=p.raiz,
                                      fonte=atualizacao.Fonte(str(p.fonte_pasta)), por_tras=lambda t: t(),
                                      pasta_grava=lambda r: False, chave_publica=PUBLICA)
    p.abrir()
    assert len(p.win.pedidos) == 2


def test_d749_sim_com_a_pasta_ainda_sem_gravar_conta_como_nao_feito(tmp_path):
    """D-749 ("Sim": a preparação pela metade conta como não feita): disse Sim, o trabalho com licença terminou, mas
    a pasta continua sem aceitar gravação (um passo falhou) → nada é procurado; a próxima abertura pergunta de novo."""
    p = Prova(tmp_path, grava=False, licenca="comecou")
    p.win.depois_do_sim = None                       # o preparo não deixou a pasta gravável
    p.abrir()
    assert p.vp.chamadas == []
    assert p.atual.estado.fase is fases.Fase.PARADO


def test_d733_com_o_sim_prepara_e_procura_sem_outra_pergunta(tmp_path):
    """D-733 ("1": uma pergunta só, na primeira abertura): com o "Sim" e a pasta aceitando gravação depois, o motor,
    a procura, a assinatura e o download seguem sozinhos, por trás, sem outra pergunta; o aviso vai para a janela."""
    p = Prova(tmp_path, grava=False, licenca="comecou")
    assert p.abrir() is None
    assert len(p.win.pedidos) == 1
    assert p.vp.nomes() == ["procurar", "baixar"]
    p.ligar_a_tela()
    assert p.tipos_na_tela() == ["MostrarVersaoNova"]


def test_protecoes_5_e_6_a_ordem_dos_passos_da_pergunta(tmp_path):
    """D-838 e o plano 4.4: o ajudante antigo (a tarefa que rodava como o sistema um programa desta pasta) sai PRIMEIRO,
    antes de a pasta aceitar gravação de Usuários (6); a licença da pasta é o ÚLTIMO passo (5, D-749: a peça para no
    primeiro passo que falha, então a pasta só fica gravável se tudo antes deu certo)."""
    passos = atualizacao.passos_do_preparo()
    assert [p.tipo for p in passos] == ["apagar_tarefa", "instalar_visual_c", "tirar_instalacao_do_inno",
                                        "dar_licenca_aos_usuarios"]
    assert passos[0].dados == {"nome": atualizacao.NOME_DA_TAREFA} == {"nome": "EditorImpressao\\Procurar versao nova"}


def test_protecao_7_conta_de_testes_nao_pergunta_nem_procura(tmp_path, monkeypatch):
    """D-736/D-741: aberto na conta dos testes à distância, nada pergunta e nada procura (e a janela não recebe nada)."""
    monkeypatch.setenv("USERNAME", "EditorTestes")
    p = Prova(tmp_path, grava=False)
    assert p.abrir() is None
    assert p.win.pedidos == [] and p.vp.chamadas == []
    assert p.atual.estado.fase is fases.Fase.FORA


def test_o_portatil_nao_pergunta_nem_procura(tmp_path):
    """O pacote portátil do ensaio (o `.portable` na raiz, como o Velopack o reconhece) não mexe no computador."""
    p = Prova(tmp_path, grava=False)
    (p.raiz / ".portable").write_text("", encoding="utf-8")
    p.abrir()
    assert p.win.pedidos == [] and p.vp.chamadas == []


# ---------------------------------------------------------------------------------------------------------------------
# Procurar, a assinatura, o motor, baixar
# ---------------------------------------------------------------------------------------------------------------------

def test_protecao_2_assinatura_errada_nao_baixa_e_avisa_com_a_frase_2(tmp_path):
    """D-724 e D-778 (frase 2): a versão publicada sem a assinatura do Samuel não é baixada, e a janela mostra
    "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do Samuel..." (uma vez). Volta 3
    (emenda do Fable: "só o teste rápido reprovado põe uma versão em 'não tentar'"): ela não vai para "não tentar"; é
    conferida de novo na próxima abertura (a assinatura é um arquivo pequeno)."""
    p = Prova(tmp_path, chave_da_nova=OUTRA_CHAVE)
    p.abrir()
    p.ligar_a_tela()
    assert p.vp.nomes() == ["procurar"]
    assert "reprovadas" not in _estado()
    assert [(type(e).__name__, getattr(e, "tipo", "")) for e in p.tela] == [("MostrarFalha", "recusada")]
    assert atualizacao.FRASES_DA_FALHA["recusada"] == atualizacao.FRASE_DA_FALHA_SEM_ASSINATURA


def test_protecao_4a_motor_fora_do_lugar_nada_e_procurado_nem_anunciado(tmp_path):
    """D-790/D-833 ("motor do Kraken tudo ou nada continua"): sem o motor no lugar, nada é procurado nem anunciado."""
    p = Prova(tmp_path, motor=False)
    p.abrir()
    p.ligar_a_tela()
    assert p.vp.chamadas == [] and p.tela == []


def test_protecao_8_a_versao_que_falhou_nao_e_baixada_de_novo(tmp_path):
    """D-718: a versão que já falhou (anotada em "não tentar") é achada, mas não é conferida nem baixada de novo."""
    atualizacao.gravar_estado({"reprovadas": [NOVA]})       # volta 3: a chave do bilhete é "reprovadas"
    p = Prova(tmp_path)
    p.abrir()
    assert p.vp.nomes() == ["procurar"]


def test_sem_internet_nao_e_falha_e_nao_avisa(tmp_path):
    """Sem internet (o Velopack não consegue procurar): só uma linha no registro; nada na tela, nada anotado."""
    p = Prova(tmp_path, erro_ao_procurar="sem internet")
    p.abrir()
    p.ligar_a_tela()
    assert p.tela == [] and "falha" not in _estado()
    assert "sem internet" in _registro()


# ---------------------------------------------------------------------------------------------------------------------
# "Reiniciar agora", "Depois" e o fechar
# ---------------------------------------------------------------------------------------------------------------------

def test_d720_reiniciar_agora_fecha_a_janela_e_so_depois_troca(tmp_path):
    """D-715/D-720/D-828 e a proteção 10: "Reiniciar agora" → a janela fecha pelo caminho de sempre (grava) → só
    então a troca, com a janelinha do Velopack e a reabertura na versão nova (o teste rápido antes da janela)."""
    p = _ate_o_aviso(tmp_path)
    ordem = []

    def tela(ef):
        if isinstance(ef, fases.FecharJanela):
            ordem.append("janela fechou")
            p.atual.evento(fases.JanelaFechou(True))

    p.atual.ligar_a_tela(tela)
    p.vp.trocar = lambda e, v, reabrir, args: ordem.append(("trocar", v.versao, reabrir, tuple(args)))
    p.atual.evento(fases.Escolheu(True))
    assert ordem == ["janela fechou", ("trocar", NOVA, True,
                                       (atualizacao.ARG_CONFERIR_NOVA, ATUAL, NOVA, atualizacao.ARG_FONTE,
                                        str(p.fonte_pasta)))]
    assert _estado() == {}          # volta 3: nada é anotado antes de trocar (a abertura seguinte olha o disco)


def test_protecao_10_a_janela_que_nao_fecha_nao_troca(tmp_path):
    """A janela recusou fechar no "Reiniciar agora": nada é trocado, e o clique tem resposta (volta 3, D-845: "Não deu
    para atualizar agora: o programa não conseguiu fechar..."); ao fechar depois, a pergunta "Atualizar agora?"."""
    p = _ate_o_aviso(tmp_path)
    vistos = []

    def tela(ef):
        vistos.append(type(ef).__name__)
        if isinstance(ef, fases.FecharJanela):
            p.atual.evento(fases.JanelaFechou(False))

    p.atual.ligar_a_tela(tela)
    p.atual.evento(fases.Escolheu(True))
    assert "trocar" not in p.vp.nomes()
    p.atual.evento(fases.Fechando())
    assert vistos == ["FecharJanela", "MostrarFalha", "PerguntarAoFechar"]


def test_d831_depois_e_sim_ao_fechar_troca_sem_janela(tmp_path):
    """D-769/D-794/D-831: "Depois" → nada agora; ao fechar, "Atualizar agora?" → "Sim" → a troca é pedida com a
    reabertura SEM janela (só o teste rápido; nada abre na tela depois)."""
    p = _ate_o_aviso(tmp_path)
    p.atual.evento(fases.Escolheu(False))
    assert "trocar" not in p.vp.nomes()
    p.atual.evento(fases.Fechando())
    assert p.tipos_na_tela()[-1] == "PerguntarAoFechar"
    p.atual.evento(fases.RespondeuAoFechar(True))
    troca = [c for c in p.vp.chamadas if c[0] == "trocar"]
    assert troca == [("trocar", NOVA, True, (atualizacao.ARG_CONFERIR_NOVA, ATUAL, NOVA, atualizacao.ARG_SEM_JANELA,
                                             atualizacao.ARG_FONTE, str(p.fonte_pasta)))]


def test_d794_nao_ao_fechar_fecha_sem_trocar(tmp_path):
    """D-794: "Não" ao fechar → fecha sem trocar; o aviso volta na próxima abertura (a versão continua publicada)."""
    p = _ate_o_aviso(tmp_path)
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(False))
    assert "trocar" not in p.vp.nomes() and "tentando" not in _estado()


def test_fechar_sem_versao_pronta_nao_pergunta(tmp_path):
    """Sem versão pronta (nenhuma publicada), fechar não pergunta nada."""
    p = Prova(tmp_path, publicar_nova=False)
    p.abrir()
    p.ligar_a_tela()
    p.atual.evento(fases.Fechando())
    assert p.tela == []


def test_protecao_3_pacote_trocado_depois_de_baixar_nao_troca(tmp_path):
    """D-724 (a soma do arquivo baixado, logo antes de trocar): com a pasta aceitando gravação de Usuários, outra conta
    poderia trocar o pacote em `packages\\` depois do download; a soma dele não é a assinada → não troca e fica no
    registro. Volta 3: não vai para "não tentar" (só o teste rápido reprova)."""
    p = _ate_o_aviso(tmp_path)
    (p.raiz / "packages" / f"{PACOTE}-{NOVA}-full.nupkg").write_bytes(b"trocado por outra conta")
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" not in p.vp.nomes()
    assert "soma assinada" in _registro() and "reprovadas" not in _estado()


def test_protecao_4b_motor_fora_do_lugar_na_hora_de_trocar_nao_troca(tmp_path):
    """D-790/D-833: o motor saiu do lugar entre o aviso e a troca → não troca (sem a versão nova perder o motor)."""
    p = _ate_o_aviso(tmp_path)
    p.motor["no_lugar"] = False
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" not in p.vp.nomes()


def test_protecao_9_outra_janela_aberta_nao_troca(tmp_path):
    """Outra janela do programa aberta (o Velopack a fecharia à força, com o que estivesse nela): não troca. A lista de
    processos é pedida deixando de fora este processo e os que ele abriu."""
    p = _ate_o_aviso(tmp_path, outras=[(7, "C:\\Arquivos\\current\\EditorImpressao.exe")])
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" not in p.vp.nomes()
    assert p.win.perguntas_de_processos == [(p.raiz / "current", 4242)]
    assert "outra janela" in _registro()


# ---------------------------------------------------------------------------------------------------------------------
# A reabertura pelo Velopack, o teste rápido e a volta
# ---------------------------------------------------------------------------------------------------------------------

def test_d718_reaberto_na_versao_nova_que_passa_no_teste(tmp_path):
    """D-718: reaberto na versão nova (`--conferir-a-versao-nova <de> <para>`), o teste rápido roda antes da janela
    (volta 3: porque a versão que roda não é a última boa guardada); passou → o pacote dela é guardado como a última
    boa (D-844) e a abertura segue (o motor, a procura)."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)
    assert p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL) is None
    assert atualizacao.ler_ultima_boa(p.raiz) == ATUAL
    assert p.vp.nomes() == ["procurar"]


def test_d718_teste_que_falha_volta_para_a_anterior_assinada(tmp_path):
    """D-718/D-778/D-844: a versão nova não passou no teste rápido → vai para "não tentar"; a volta é PELO PACOTE
    GUARDADO da última boa (volta 3: a pasta `ultima-boa` é o endereço do `baixar`, sem internet; nenhum programa do
    Velopack à mão), com a assinatura guardada conferida, troca pela troca única e sai sem abrir a janela (o Velopack
    abre a anterior). Nada é anotado antes de a volta acontecer (a frase 1 é derivada depois)."""
    p = Prova(tmp_path, teste=(False, "código 1"), ultima_boa=ANTERIOR)
    saida = p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    assert saida == 0
    assert p.vp.nomes() == ["pacote_da_versao", "baixar", "trocar"]
    assert p.vp.chamadas[1] == ("baixar", ANTERIOR, str(atualizacao.pasta_da_ultima_boa(p.raiz)))
    assert p.vp.chamadas[-1] == ("trocar", ANTERIOR, True, (atualizacao.ARG_FONTE, str(p.fonte_pasta)))
    assert _estado() == {"reprovadas": [ATUAL]}


def test_protecao_11_a_volta_sem_a_assinatura_nao_troca_e_avisa_com_a_frase_3(tmp_path):
    """D-724/D-778 (frase 3): a última boa guardada sem a assinatura certa (volta 3: a assinatura guardada com o
    pacote) → não copia nem troca; a janela (a da versão nova, que abre se conseguir) mostra "A atualização não deu
    certo e o programa não conseguiu voltar sozinho..."."""
    p = Prova(tmp_path, teste=(False, "código 1"), ultima_boa=ANTERIOR)
    pasta = atualizacao.pasta_da_ultima_boa(p.raiz)
    conteudo = (pasta / atualizacao.nome_do_pacote(ANTERIOR)).read_bytes()
    _publicar(pasta, ANTERIOR, conteudo, OUTRA_CHAVE)              # a assinatura guardada passa a ser de outra chave
    saida = p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    p.ligar_a_tela()
    assert saida is None
    assert "baixar" not in p.vp.nomes() and "trocar" not in p.vp.nomes()
    assert _estado()["reprovadas"] == [ATUAL]
    assert [getattr(e, "tipo", "") for e in p.tela if isinstance(e, fases.MostrarFalha)] == ["volta"]


def test_a_troca_que_nao_aconteceu_avisa_uma_vez(tmp_path):
    """O Velopack não conseguiu trocar (arquivo preso) e reabriu a versão de antes com os mesmos argumentos: mostra a
    frase da D-839 uma vez; na abertura seguinte não mostra de novo. Volta 3 (M1): a versão NÃO vai para "não
    tentar" (a troca que não aconteceu não é falha de versão; o aviso volta)."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ATUAL)
    p.abrir(atualizacao.ARG_CONFERIR_NOVA, ATUAL, NOVA)
    p.ligar_a_tela()
    assert [getattr(e, "tipo", "") for e in p.tela] == ["troca"]
    assert "reprovadas" not in _estado()
    q = Prova(tmp_path / "outra", publicar_nova=False, ultima_boa=ATUAL)
    q.abrir()
    q.ligar_a_tela()
    assert q.tela == []


def test_d769_reabertura_sem_janela_que_passa_sai_sem_janela(tmp_path):
    """D-769: depois do "Sim" ao fechar, o Velopack reabre com `--sem-janela`: o teste passa e o processo sai (0) sem
    abrir a janela; a próxima abertura já é na versão nova."""
    p = Prova(tmp_path, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)
    assert p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL, atualizacao.ARG_SEM_JANELA) == 0
    assert p.vp.chamadas == []
    assert atualizacao.ler_ultima_boa(p.raiz) == ATUAL     # volta 3: guardada nesta linha, antes de sair


def test_a_tarefa_antiga_do_ajudante_so_anota_e_sai():
    """O ajudante antigo (se sobrar num computador) chama o programa com `--procurar-atualizacao`: o programa novo
    anota e sai, sem procurar nada."""
    assert atualizacao.atender_linha_de_comando(["EditorImpressao.exe", atualizacao.ARG_PROCURAR]) == 0
    assert "ajudante antigo" in _registro()


# ---------------------------------------------------------------------------------------------------------------------
# A tela recebe só o que deve, uma vez
# ---------------------------------------------------------------------------------------------------------------------

def test_d719_a_falha_vai_para_a_janela_uma_vez_so_nesta_conta(tmp_path):
    """D-719/D-778: a falha chega à janela uma vez (esperando na fila até a janela abrir); a abertura seguinte, na
    mesma conta, não a mostra de novo. Volta 3: a frase (1) é derivada (rodando a última boa, com a versão mais nova
    reprovada), não anotada."""
    atualizacao.gravar_estado({"reprovadas": [NOVA]})
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ATUAL)
    p.abrir()
    assert p.tela == []                       # a janela ainda não abriu: espera na fila
    p.ligar_a_tela()
    assert [(type(e).__name__, e.tipo) for e in p.tela] == [("MostrarFalha", "teste")]
    q = Prova(tmp_path / "outra", publicar_nova=False, ultima_boa=ATUAL)
    q.abrir()
    q.ligar_a_tela()
    assert q.tela == []


def test_d835_e_d778_os_textos_da_tela_palavra_por_palavra():
    """D-835 (os textos curtos) e D-778 (as três frases), palavra por palavra, e cada falha com a sua frase."""
    assert atualizacao.FRASE_DA_VERSAO_NOVA.endswith(
        "Se escolher \"Depois\", você pode atualizar quando fechar o programa.")
    assert (atualizacao.TITULO_AO_FECHAR, atualizacao.FRASE_AO_FECHAR) == (
        "Atualizar agora?", "Quer atualizar o programa agora, ao fechar?")
    assert (atualizacao.BOTAO_SIM_AO_FECHAR, atualizacao.BOTAO_NAO_AO_FECHAR) == ("Sim", "Não")
    assert (atualizacao.BOTAO_REINICIAR, atualizacao.BOTAO_DEPOIS) == ("Reiniciar agora", "Depois")
    assert atualizacao.FRASES_DA_FALHA == {
        "teste": "A atualização não deu certo. O programa voltou para a versão anterior e continua funcionando. "
                 "Avise o Samuel.",
        # D-839 (Samuel, 24/11/2026: "sim"): a troca que não aconteceu tem frase própria (era a (1) da D-778).
        "troca": "A atualização não deu certo. O programa continua na versão de antes e funcionando. Avise o Samuel.",
        "recusada": "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do Samuel. O "
                    "programa continua funcionando. Avise o Samuel.",
        "volta": "A atualização não deu certo e o programa não conseguiu voltar sozinho. Não desinstale nada. Avise "
                 "o Samuel.",
        # D-843 (Samuel, 24/11/2026: "vamos fazer b e colocamos isso no plano").
        "motor": "Esta versão precisa de um motor novo. Avise o Samuel."}
    assert "próxima vez que você abrir" not in atualizacao.FRASE_DA_VERSAO_NOVA     # o texto antigo saiu


# ---------------------------------------------------------------------------------------------------------------------
# Pelo código, e a troca por um lugar só
# ---------------------------------------------------------------------------------------------------------------------

def test_protecao_12_pelo_codigo_nada_roda(tmp_path, monkeypatch):
    """Pelo código (o atalho "(desenvolvimento)" e os testes): nada da atualização roda, nada é gravado no
    ProgramData, nenhum executor para a janela, e o velopack nem é importado."""
    monkeypatch.delitem(sys.modules, "velopack", raising=False)
    assert atualizacao.atender_linha_de_comando(["main.py"]) is None
    assert atualizacao.da_abertura() is None
    assert "velopack" not in sys.modules
    assert not (tmp_path / "ProgramData").exists()


def _chamadas_de(nome: str) -> list[tuple[str, str]]:
    """(arquivo, função em volta) de cada chamada `<algo>.<nome>(...)` nos arquivos .py do programa (não os testes)."""
    achadas = []
    for caminho in RAIZ_DO_REPOSITORIO.glob("**/*.py"):
        relativo = caminho.relative_to(RAIZ_DO_REPOSITORIO).as_posix()
        if relativo.startswith((".claude/", "tests/", "velhos/", "relatorios/", "historico/", "saida_teste/",
                                ".venv/", "terceiros/")):
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")           # arquivos de outros com escape velho no texto
                arvore = ast.parse(caminho.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for funcao in [n for n in ast.walk(arvore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            for no in ast.walk(funcao):
                if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute) and no.func.attr == nome:
                    achadas.append((relativo, funcao.name))
    return sorted(set(achadas))


def test_protecao_13_so_um_lugar_chama_a_troca_do_velopack():
    """A troca do Velopack (`wait_exit_then_apply_updates`) é chamada só em `conversa_com_o_velopack.trocar`; e a troca
    da peça (`velopack.trocar`) só em `atualizacao.Atualizacao.trocar_para`, que confere antes (a soma assinada, o
    motor, outra janela). Lido pela árvore de todo o programa."""
    assert _chamadas_de("wait_exit_then_apply_updates") == [("core/conversa_com_o_velopack.py", "trocar")]
    assert [c for c in _chamadas_de("trocar") if c[0] != "tests"] == [("atualizacao.py", "trocar_para")]


def test_os_tres_caminhos_da_troca_passam_pela_mesma_conferencia(tmp_path, monkeypatch):
    """§11.12 (regra num lugar só): o "Reiniciar agora", o "Sim" ao fechar e a volta chegam todos a `trocar_para`."""
    caminhos = []
    original = atualizacao.Atualizacao.trocar_para

    def anotar(self, v, de, para, **kw):
        caminhos.append((de, para, kw.get("sem_janela", False), kw.get("volta", False)))
        return original(self, v, de, para, **kw)

    monkeypatch.setattr(atualizacao.Atualizacao, "trocar_para", anotar)
    p = _ate_o_aviso(tmp_path / "a")
    p.atual.ligar_a_tela(lambda ef: isinstance(ef, fases.FecharJanela) and p.atual.evento(fases.JanelaFechou(True)))
    p.atual.evento(fases.Escolheu(True))
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData-b"))   # cada computador com o seu estado
    q = _ate_o_aviso(tmp_path / "b")
    q.atual.evento(fases.Escolheu(False))
    q.atual.evento(fases.Fechando())
    q.atual.evento(fases.RespondeuAoFechar(True))
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData-c"))
    r = Prova(tmp_path / "c", teste=(False, "x"), ultima_boa=ANTERIOR)
    r.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    assert caminhos == [(ATUAL, NOVA, False, False), (ATUAL, NOVA, True, False), (ATUAL, ANTERIOR, False, True)]


def test_d832_a_troca_usa_a_janelinha_do_velopack(monkeypatch):
    """D-832 ("pode ser velopack"): a peça pede a troca SEM o modo silencioso (a janelinha do Velopack aparece) e com
    os argumentos da reabertura; nunca a troca automática na abertura. A biblioteca é trocada por uma de mentira só
    para ver o pedido (a troca de verdade só na prova à vista)."""
    pedidos = []

    class Gerente:
        def __init__(self, fonte, opcoes, localizador=None):
            pass

        def wait_exit_then_apply_updates(self, pedido, silent, restart, restart_args):
            pedidos.append((pedido, silent, restart, list(restart_args)))

    class App:
        def __getattr__(self, nome):
            def anotar(*a):
                pedidos.append((nome, a))
                return self
            return anotar

    falso = type("vp", (), {"UpdateManager": Gerente, "UpdateOptions": lambda **k: k, "App": App,
                            "GithubSource": lambda e: e})
    monkeypatch.setattr(conversa, "_velopack", lambda: falso)
    v = conversa.VersaoDoVelopack(PACOTE, NOVA, "x.nupkg", "ab", 2, pedido="o pedido")
    conversa.trocar("C:/fonte", v, True, ["--a", "b"])
    assert pedidos == [("o pedido", False, True, ["--a", "b"])]
    pedidos.clear()
    conversa.atender_ganchos(print, print, print)
    assert ("set_auto_apply_on_startup", (False,)) in pedidos


def test_o_indice_publicado_tem_o_nome_do_empacotar():
    """O nome do índice que a volta lê é o mesmo que o publicar põe (o programa não importa o empacotar.py)."""
    import empacotar

    assert atualizacao.NOME_DO_INDICE_PUBLICADO == empacotar.NOME_DO_INDICE


def test_o_teste_de_gravar_cria_e_apaga(tmp_path):
    """O "preparado?" é o teste de gravar de verdade: numa pasta que aceita, True, e nada fica para trás; numa que não
    existe, False."""
    assert atualizacao.pasta_aceita_gravacao(tmp_path) is True
    assert list(tmp_path.iterdir()) == []
    assert atualizacao.pasta_aceita_gravacao(tmp_path / "nao-existe") is False


def test_d731_o_atualizador_novo_nao_poe_tarefa_no_windows():
    """D-731 ("o notebook fica como era antes de instalar"; substitui as provas do ajudante e da tarefa "desfazer" da
    primeira abertura, que saíram com eles, D-836): a única coisa com tarefa do Windows na pergunta da primeira
    abertura é APAGAR o ajudante antigo; nada é criado. Desinstalar apaga a pasta do programa inteira (o Velopack), e
    não sobra tarefa do atualizador."""
    passos = atualizacao.passos_do_preparo()
    assert [p.tipo for p in passos if "tarefa" in p.tipo] == ["apagar_tarefa"]
    assert not any(p.tipo in ("criar_tarefa", "script") for p in passos)


def test_d732_a_procura_e_so_ao_abrir_nada_roda_por_tras_depois():
    """D-732 ("não, faz quando o programa é aberto"; a correção das 20:42: o "de 5 em 5 minutos" era do código antigo):
    a janela não tem relógio de procurar; a procura só nasce da abertura (a regra: `Procurar` só depois de
    `MotorConferido`, que só vem da abertura, do preparo ou da versão nova conferida)."""
    import ui.aviso_de_atualizacao as aviso

    assert not hasattr(aviso, "INTERVALO_MS") and not hasattr(aviso, "VigiaDaAtualizacao")
    arvore = ast.parse(Path(aviso.__file__).read_text(encoding="utf-8"))
    assert "QTimer" not in {n.id for n in ast.walk(arvore) if isinstance(n, ast.Name)}
