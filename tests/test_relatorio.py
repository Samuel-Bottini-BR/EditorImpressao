"""A pasta de teste: uma por filtro, com data e hora, e nome que o Windows aceita."""

import relatorio


def test_pasta_por_filtro_com_data_e_hora(tmp_path):
    pasta = relatorio.pasta_de_teste("orla do branco", "magico pro", raiz=tmp_path)

    assert pasta.parent.name == "MAGICO PRO"
    assert pasta.name.endswith(" - orla do branco")
    assert pasta.is_dir()


def test_pontuacao_no_assunto_nao_derruba_o_teste():
    """Um assunto com dois pontos estourava o mkdir no fim de uma bateria.

    O assunto e escrito a mao a cada teste, entao a pontuacao aparece; o estrago
    vinha depois de todo o trabalho pesado ja feito.
    """
    assert relatorio._nome_de_pasta("letra arredondada: raio da nitidez") == (
        "letra arredondada raio da nitidez")
    assert relatorio._nome_de_pasta('recorte "novo" / antigo') == "recorte novo antigo"
    assert relatorio._nome_de_pasta("   ") == "sem assunto"


def test_filtro_desconhecido_vai_para_outros(tmp_path):
    pasta = relatorio.pasta_de_teste("qualquer coisa", raiz=tmp_path)

    assert pasta.parent.name == "OUTROS"
