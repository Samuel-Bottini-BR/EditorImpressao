"""Modelos de dados do Editor de Impressão.

Uma observacao sobre a estrutura, que se afasta de proposito da especificacao:

A especificacao prévia uma única lista de ConfigPagina. Na pratica existem dois
niveis diferentes, e mistura-los complicaria a interface:

  - FOLHA  = o que veio no PDF de entrada. E onde moram dividir, posição do
             corte, rotação e recorte. E o que a aba "Onde cortar" mostra.
  - PAGINA = o que vai sair no PDF final. Uma folha dividida vira DUAS páginas.
             E onde mora o filtro, que a especificacao exige que seja por
             página. E o que a aba "Filtro" mostra.

Assim "livro todo em preto e branco, só a capa em Mágico pro" cai naturalmente,
e a tira de miniaturas de cada aba mostra exatamente a unidade que aquela aba
edita.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from typing import Any

from core.filtros import FILTROS, ORIGINAL, PRETO_E_BRANCO, TIRAR_FUNDO
from core.misto import FORA_DO_TEXTO_PADRAO, LETRAS_NA_MOLDURA_PADRAO, PAPEL_DA_GRAVURA_PADRAO
from core.pontinhos_scantailor import DESLIGADO as PONTINHOS_DESLIGADO
from core.pontinhos_scantailor import DO_PROJETO_ANTIGO as PONTINHOS_DO_PROJETO_ANTIGO
from core.pontinhos_scantailor import PADRAO as PONTINHOS_PADRAO
from core.dividir_scantailor import JEITO_DO_PROJETO_ANTIGO as DIVIDIR_DO_PROJETO_ANTIGO
from core.dividir_scantailor import JEITO_DO_LIVRO_NOVO as DIVIDIR_DO_LIVRO_NOVO
from core.endireitar_scantailor import JEITO_DO_PROJETO_ANTIGO as ENDIREITAR_DO_PROJETO_ANTIGO
from core.endireitar_scantailor import PADRAO as ENDIREITAR_DO_LIVRO_NOVO
from core.ordem_do_preparo import ORDEM_DO_LIVRO_NOVO, ORDEM_DO_PROJETO_ANTIGO

METADE_INTEIRA = "inteira"
METADE_ESQUERDA = "esquerda"
METADE_DIREITA = "direita"


@dataclass
class ConfigFolha:
    """Uma folha do PDF de entrada."""

    indice: int
    dividir: bool = True
    posicao_corte: float = 0.5       # 0.0 a 1.0, relativo a largura
    confianca_corte: float = 0.0     # 0.0 a 1.0
    rotacao: int = 0                 # 0, 90, 180, 270
    angulo_detectado: float = 0.0    # so para o alerta "muito torta"
    confianca_angulo: float = 0.0
    apagada: bool = False
    e_paisagem: bool = True
    alertas: list[str] = field(default_factory=list)
    revisada: bool = False

    # Item 2.1 (decisao G2 (a) do Samuel, 05/10/2026: "trocando numa folha se
    # um ficar ruim"): o jeito de dividir SO desta folha, por cima do livro
    # (Projeto.dividir_como). None = segue o livro. Valores: os codigos de
    # core/dividir_scantailor.JEITOS ("programa", "scantailor"); nunca o
    # texto da tela. Quem troca: a aba "Onde cortar" (ui/tela_conferir.py),
    # que recalcula posicao_corte com o jeito novo
    # (core.pipeline.recalcular_divisao). Projeto antigo nao tem o campo:
    # volta None (segue o livro, que no projeto antigo e "programa").
    dividir_como: str | None = None

    # Item 2.1 (decisao G3 (b) do Samuel, 05/10/2026: o "corte da sobra" do
    # ScanTailor como opcao, desligada): (esquerda, direita) = a parte da
    # folha que FICA, em fracao da largura, achada pelo automatico do
    # ScanTailor quando ele ve "uma pagina + sobra" (core.pipeline.achar_sobra,
    # core/dividir_scantailor.sobra_da_folha). So vale
    # com Projeto.cortar_sobra ligado, em folha NAO dividida e sem giro de 90
    # (core.pipeline.faixa_da_sobra). None = nada a cortar. Calculada na
    # analise; nao ha como mexer a mao (ainda). Seguro mudar: nada aqui.
    sobra: tuple[float, float] | None = None

    @property
    def precisa_revisao(self) -> bool:
        return bool(self.alertas) and not self.revisada


@dataclass
class ConfigPagina:
    """Uma página do PDF de saida."""

    indice: int                      # posicao no livro final, comecando em 0
    folha: int                       # de qual folha de entrada ela veio
    metade: str = METADE_INTEIRA     # inteira | esquerda | direita

    # Recorte e angulo moram na PAGINA, e nao na folha, porque o pipeline os
    # aplica depois da divisao: cada metade tem a sua sombra de lombada de um
    # lado so, e pode estar torta de um jeito diferente da outra.
    recorte: tuple[float, float, float, float] | None = None  # None = automatico
    angulo_manual: float | None = None                        # None = automatico

    # Item 2.2 (decisao G4 (b) do Samuel, 05/10/2026: "O do ScanTailor de
    # fabrica; [...] mas eu vou ter a opcao de escolher"): a conta do
    # endireitar AUTOMATICO so desta pagina, por cima do livro
    # (Projeto.endireitar_como). None = segue o livro. Valores: os codigos de
    # core/endireitar_scantailor.JEITOS ("scantailor", "programa"); nunca o
    # texto da tela. So vale quando angulo_manual e None (o angulo a mao
    # ganha de qualquer conta). Projeto antigo nao tem o campo: volta None.
    # Seguro mudar: nada aqui.
    endireitar_como: str | None = None

    # Problema 2 do plano (redesenho do fluxo): a página nasce em Original,
    # nunca com um filtro já aplicado sozinho - o Samuel decide quando
    # aplicar algo. TelaOpcoes ainda deixa escolher outro filtro padrão para
    # o livro inteiro antes de começar; PRETO_E_BRANCO segue sendo o padrão
    # de `filtro_valido()`, que é outra coisa (corrigir valor inválido salvo).
    filtro: str = ORIGINAL

    # Problema 5 do plano: qual dos 3 algoritmos o Preto e branco usa nesta
    # página - "auto" deixa o programa decidir sozinho pela espessura do
    # traço (ver core/filtros.py::escolher_algoritmo_automatico); os outros
    # valores vêm de ALGORITMOS_PB (sauvola/otsu/wolf), escolha manual ou
    # "usar em todas". Só importa quando `filtro` é Preto e branco.
    algoritmo_preto_branco: str = "auto"

    # "Limpar pontinhos" SO desta pagina, por cima do livro
    # (Projeto.limpar_pontinhos); None = segue o livro. Decisao do Samuel
    # (06/10/2026, P7): "Eu vou poder ligar e desligar esse apagador de
    # pingos? e selecionar o pouco, normal ou muito, ou selecionar o nosso".
    # Valores: os codigos internos de core.pontinhos_scantailor.ESCOLHAS
    # ("desligado", "nosso", "st_pouco", "st_normal", "st_muito"; nunca o
    # texto da tela, que e provisorio). So muda a imagem da pagina em Preto
    # e branco (com ou sem "So as letras").
    #
    # Substitui a caixinha "limpar poeirinha" (Problema 5 do plano, campo
    # `despeckle`: True = o nosso, False = nada). Projeto antigo abre como
    # estava (_migrar): a pagina com a caixinha desligada vira "desligado"; a
    # ligada segue o livro, que no projeto antigo e "nosso"
    # (Projeto.de_dicionario). O "despeckle" do arquivo antigo e descartado
    # depois de traduzido. Seguro mudar: nada aqui (None e o que faz a
    # pagina seguir o livro).
    limpar_pontinhos: str | None = None

    # Os tres ajustes de filtro, cada um de 0 a 100 com 50 no meio. Ficam
    # separados de proposito: trocar de filtro e voltar tem que devolver o
    # ajuste que AQUELE filtro tinha, sem herdar o do outro.
    forca_preto: int = 50            # Preto e branco - "Força do preto"
    clareza_melhorar: int = 50       # Melhorar       - "Clareza do fundo"
    intensidade_magico: int = 50     # Mágico pro     - "Intensidade"

    apagada: bool = False
    tem_cor: bool = False
    alertas: list[str] = field(default_factory=list)
    revisada: bool = False

    # Onde cada tratamento vale nesta pagina: gravura aqui, letra ali, papel no
    # resto. Guardado como lista de formas, e nao como imagem, para o arquivo
    # de projeto continuar pequeno e a mesma marcacao valer em qualquer DPI.
    # Vazia quer dizer "trate a pagina inteira do mesmo jeito", que e como o
    # programa sempre funcionou - projetos antigos continuam abrindo.
    selecao: list[dict[str, Any]] = field(default_factory=list)

    # Item 1.2 (decisao do Samuel, 30/09/2026): "Quero poder trocar tambem so
    # numa pagina (ex.: so a pagina da estatua do Opus Majus), sem mudar o
    # livro inteiro." gravura_forma e a forma do contorno da gravura SO desta
    # pagina ("livre" ou "retangular"), por cima da do livro
    # (Projeto.gravura_forma); None = segue o livro. E o controle "Esta
    # pagina tem foto" da aba Marcar (ui/tela_conferir.py).
    #
    # gravura_feita_com: com que opcoes a parte da selecao que a MAQUINA
    # marcou foi feita (core.detectar_regioes.assinatura_da_gravura). Nao e
    # escolha de ninguem: e o que deixa core/pipeline.garantir_selecao saber
    # que as opcoes mudaram e refazer so a parte automatica, mantendo a
    # marcacao a mao. "" = feita antes deste campo existir (projeto antigo):
    # fica como esta, a menos que a pessoa mude as opcoes do livro (ai
    # ui/janela_principal marca para refazer). Seguro mudar: nada, o valor e
    # interno. Projeto antigo sem os dois campos abre com os padroes.
    gravura_forma: str | None = None
    gravura_feita_com: str = ""

    # Decisao D2 do Samuel (02/10/2026): "Sim, pode mudar (com copia de
    # seguranca dos projetos)" - as zonas ficam presas a FOLHA ORIGINAL.
    # `selecao` continua, na memoria, em fracao da pagina preparada (a tela e
    # o pipeline nao mudam); geometria_das_zonas diz em que preparo da pagina
    # (giro de 90, divisao, corte, angulo, proporcao da folha) essas fracoes
    # valem. None = ainda nao anotada (projeto de antes de 05/10/2026, ou
    # pagina nunca desenhada): as fracoes valem na pagina de agora, como
    # sempre. Quem anota e leva as zonas quando o preparo muda:
    # core/zonas_na_folha.acompanhar, chamado por core/pipeline ao desenhar.
    # No projeto.json a pagina ganha tambem "zonas_na_folha" (as zonas na
    # folha original; ver Projeto.para_dicionario). Seguro mudar: nada aqui;
    # e interno. Arriscado: apagar este campo sem apagar a selecao junto.
    geometria_das_zonas: dict[str, Any] | None = None

    # Modo Misto ("So as letras" no Preto e branco), SO desta pagina, por cima
    # do livro (os campos de mesmo nome em Projeto; None = segue o livro).
    # Pedido do Samuel (conferencia 10, P1 (a)): "para o livro (tela 'O que
    # fazer') e para a pagina (aba Filtro)". Os valores e o que cada um faz:
    # core/misto.py (CAMPOS_DO_MISTO, opcoes_da_pagina). So mudam a imagem da
    # pagina em Preto e branco. Projeto antigo, sem os campos: None (segue o
    # livro, que tambem vem desligado). Seguro mudar: nada aqui (o padrao
    # None e o que faz a pagina seguir o livro).
    misto_so_as_letras: bool | None = None
    misto_fora_do_texto: str | None = None
    misto_papel_da_gravura: str | None = None
    misto_letras_na_moldura: str | None = None

    # Problema 1, opcoes B e C do plano: depois que `recorte` decide o
    # tamanho da FOLHA final, estes dois decidem o tamanho e a posicao do
    # CONTEUDO escaneado dentro dela - independentes um do outro e do
    # recorte. 1.0/centro (x=y=0.0 aqui significa "sem deslocamento", nao
    # fracao de pagina) e o padrao: comportamento identico a hoje, conteudo
    # do tamanho da folha, sem sobra. Ver `ui/widgets/visualizador.py`
    # (`guias_ativas`, `encaixar_no_ima`) para a logica de posicionar.
    conteudo_escala: float = 1.0
    conteudo_deslocamento: tuple[float, float] = (0.0, 0.0)

    # Item 2/4 do teste do Boecio (secao 3a do plano): o tamanho de folha
    # FINAL que o usuario escolheu no dialogo "tamanho..." - independente do
    # `recorte`. None (padrao) quer dizer "a folha tem o tamanho do
    # recorte", que e o comportamento de sempre; projetos salvos antes deste
    # campo existir abrem iguais. Quando setado, `core/folha.py::compor_na_folha`
    # cola o recorte (conteudo) centralizado dentro de uma folha branca desse
    # tamanho - nunca o contrario (o recorte NUNCA e esticado/recentralizado
    # so por causa do tamanho de folha escolhido, que era o bug relatado).
    tamanho_folha_cm: tuple[float, float] | None = None

    @property
    def precisa_revisao(self) -> bool:
        return bool(self.alertas) and not self.revisada

    def obter_selecao(self):
        """A selecao desta pagina, ja como objeto."""
        from core.selecao import Selecao

        return Selecao.de_lista(self.selecao)

    def guardar_selecao(self, selecao) -> None:
        self.selecao = selecao.para_lista()


@dataclass
class Projeto:
    """Um livro sendo trabalhado.

    As opções do livro inteiro (as caixinhas da tela "O que fazer") moram
    aqui; o que é de cada folha e de cada página mora em ConfigFolha e
    ConfigPagina. Campo do item 1.1 (29/09/2026):

    tem_camadas: o PDF vem com as camadas do Internet Archive (fundo + texto
        recortado por cima)? Detectado pelo programa ao abrir e na análise;
        não é escolha da pessoa. É ele que faz o filtro "Tirar o fundo"
        aparecer (core.filtros.filtros_do_livro).

    Projetos salvos antes de 29/09 não têm o campo, e os salvos na primeira
    ligação do 1.1 (commit bb54b7d) têm também "tirar_fundo_sozinho", a
    caixinha que saiu por decisão do Samuel: os dois abrem normalmente (campo
    que falta ganha o padrão, campo que sobra é ignorado - ver de_dicionario)
    e nenhum vem com o fundo tirado, porque o fundo só sai na página com o
    filtro "Tirar o fundo" escolhido.
    """

    caminho_entrada: str
    caminho_saida: str = ""
    nome: str = ""

    # Dividir as folhas em duas paginas. Decisao do Samuel G2 (a),
    # 05/10/2026: "So quando o Kaique pedir, livro a livro" - livro NOVO nao
    # divide (False de fabrica; ate o item 2.1 era True). Projeto salvo antes
    # sempre tem o campo e volta como estava (de_dicionario).
    dividir_folhas: bool = False
    # Item 2.1: COMO dividir, quando dividir_folhas esta ligado: "o do
    # programa" (core/dividir.py, procura a lombada nas folhas deitadas) ou
    # "o do ScanTailor" (core/dividir_scantailor.py, o automatico dele).
    # Codigos de core/dividir_scantailor.JEITOS. Cada folha pode trocar so
    # nela (ConfigFolha.dividir_como). Projeto salvo antes do campo volta com
    # "programa" (era o unico jeito; de_dicionario). De fabrica, no livro
    # NOVO: "o do ScanTailor" - decisao do Samuel de 07/10/2026 ("Ao marcar
    # 'Dividir folhas ao meio', qual jeito vem escolhido?" -> "O do
    # ScanTailor"); ate entao era "programa". O do programa continua opcao.
    # Arriscado: trocar o setdefault de de_dicionario junto (o projeto
    # antigo reaberto mudaria de jeito).
    dividir_como: str = DIVIDIR_DO_LIVRO_NOVO
    # Item 2.1, decisao G3 (b): o "corte da sobra" do ScanTailor (tira a
    # beirada da folha vizinha que entrou na foto), DESLIGADO de fabrica. So
    # nas folhas que nao sao divididas. Ver ConfigFolha.sobra.
    cortar_sobra: bool = False
    limpar: bool = True
    filtro_padrao: str = ORIGINAL
    endireitar: bool = True
    # Item 2.2, decisao G4 (b) do Samuel (05/10/2026): a conta do endireitar
    # automatico do livro. De fabrica, no livro NOVO, "a do ScanTailor"
    # (core/endireitar_scantailor.py, o SkewFinder original); "a do
    # programa" (core/endireitar.detectar_angulo) continua opcao, e cada
    # pagina pode trocar so nela (ConfigPagina.endireitar_como). Projeto
    # salvo antes do campo volta com "programa" (de_dicionario): era a unica
    # conta, e o livro antigo tem de sair identico ("o programa [...] vai ter
    # que ser capaz de abrir arquivos de versoes anteriores", Samuel,
    # 05/10/2026). Arriscado: trocar o setdefault de de_dicionario (o projeto
    # antigo reaberto mudaria de angulo).
    endireitar_como: str = ENDIREITAR_DO_LIVRO_NOVO
    # Item 2.2, G6 (Samuel, 09/10/2026, "Endireitar antes de cortar (como o
    # ScanTailor): pode comecar?" -> "Pode comecar"): a ordem do preparo
    # (core/ordem_do_preparo.py). Livro NOVO: "endireitar_antes" (girar 90 ->
    # dividir -> endireitar a pagina inteira -> achar o corte na pagina reta
    # -> cortar). Projeto salvo antes do campo volta "cortar_antes"
    # (de_dicionario) e sai IDENTICO ao de antes. Nao e opcao da tela: nasce
    # com o livro e acompanha o projeto (ui/janela_principal.
    # _trazer_opcoes_salvas). Arriscado: trocar o setdefault de de_dicionario
    # (o projeto antigo mudaria de corte e as zonas dele andariam).
    ordem_do_preparo: str = ORDEM_DO_LIVRO_NOVO
    cortar_bordas: bool = True
    montar_cadernos: bool = False
    paginas_por_caderno: int = 20
    qualidade_dpi: int = 300

    # Descobrir sozinho onde estao gravura, letra e papel, para tratar cada
    # area do seu jeito. Desligar faz o filtro voltar a tratar a folha inteira
    # igual, que e como o programa funcionava antes.
    detectar_regioes: bool = True

    # Item 1.1 do Plano Definitivo: "tirar o fundo" de PDF que ja vem com
    # camadas (Internet Archive: fundo embaixo, texto recortado por cima; ver
    # core/camadas.py). tem_camadas e FATO do PDF, nao escolha: o programa olha
    # a estrutura do arquivo ao abrir (core.camadas.pdf_tem_camadas,
    # milissegundos, sem desenhar pagina) e na analise, e o valor salvo no
    # projeto nao manda (e refeito a cada abertura).
    #
    # Decisao do Samuel (29/09/2026, depois de ver a primeira ligacao): "Pagina
    # sempre abre em 'Original', sem mexer. Em PDF com camadas, 'Tirar o fundo'
    # vira mais uma opcao na lista de filtros." A ESCOLHA mora, entao, no filtro
    # de cada pagina (ConfigPagina.filtro = core.filtros.TIRAR_FUNDO) e no
    # filtro do livro (filtro_padrao), como a de qualquer filtro. A caixinha
    # "Tirar o fundo sozinho" (campo tirar_fundo_sozinho, commit bb54b7d) saiu.
    #
    # Seguro mudar: nada aqui muda imagem sozinho; quem decide pagina a pagina
    # e core/pipeline.py (usa_tirar_fundo).
    tem_camadas: bool = False

    # Item 1.1: a pergunta "Este livro tem fundo separado. Quer tirar o
    # fundo?" ja foi feita neste projeto? Decisao do Samuel (29/09/2026,
    # Registro de mudancas): ela aparece "uma vez por livro, inclusive nos que
    # ele ja tem: na proxima vez que abrir, e depois nao pergunta mais". Projeto
    # antigo, gravado antes deste campo, volta com False (= ainda nao
    # perguntou) - campo novo autorizado por essa decisao. Qualquer resposta
    # conta (Sim, Nao, Esc, X). Quem pergunta e grava: ui/janela_principal.py
    # (abrir_livro, _resposta_do_aviso_do_fundo). Seguro mudar: nada; o
    # campo so decide se a pergunta aparece, nunca mexe em pagina.
    perguntou_fundo: bool = False

    # Item 1.2: as opcoes do detector de gravuras do ScanTailor Advanced, por
    # livro. Decisao do Samuel (30/09/2026, Registro de mudancas): "o programa
    # tem que ter essas opcoes para o usuario conseguir usar". Os padroes sao
    # os do proprio ScanTailor no modo Misto (os do teste de 24/09). Quem le e
    # core/pipeline.escolha_da_gravura (que tambem corrige valor invalido
    # vindo do arquivo); quem mostra e ui/tela_opcoes.py ("Gravuras e fotos").
    #   gravura_forma: "livre" (seguindo o desenho), "retangular" (em
    #       retangulo, bom para fotos) ou "desligada" (nao procurar gravura:
    #       e o botao de desligar da regra 8 do plano);
    #   gravura_sensibilidade: 0 a 100, so vale na forma retangular;
    #   gravura_mais_sensivel: "maior sensibilidade de busca" (acha tambem
    #       imagens claras);
    #   gravura_normalizar: igualar a luz da pagina antes de procurar.
    # Projeto antigo, sem estes campos, abre com os padroes (de_dicionario).
    # Mudar num livro com trabalho so vale ao clicar "Conferir", e a gravura
    # achada sozinha e refeita (ui/janela_principal._analise_pronta).
    gravura_forma: str = "livre"
    gravura_sensibilidade: int = 100
    gravura_mais_sensivel: bool = False
    gravura_normalizar: bool = True

    # Preto e branco: a moldura dourada e a iluminura tambem em preto e branco
    # (desenho de traco preto)? Emenda do Samuel a regra do Preto e branco
    # (conferencia 3, 30/09/2026, cartao N2): "Mantem a cor original (como o
    # ANTES); traco preto so se eu escolher" - e "gostaria de ter a opcao de
    # fazer isso em outras ocasioes e em outros livros". De fabrica False (a
    # cor original); projeto antigo, sem o campo, abre com False
    # (de_dicionario). Campo novo por livro autorizado por essa decisao. Quem
    # mostra e ui/tela_opcoes.py (caixinha no grupo dos filtros); quem usa e
    # core/pipeline._filtrar -> core.filtros.aplicar_filtro_com_selecao
    # (decoracao_em_preto_e_branco). So muda a imagem das paginas em Preto e
    # branco com moldura ou iluminura marcada como gravura.
    pb_decoracao_em_preto_e_branco: bool = False

    # Modo Misto, por livro: a caixinha "So as letras" do Preto e branco
    # (conferencia 10, P1 (a): "para o livro (tela 'O que fazer') e para a
    # pagina (aba Filtro)") e as tres escolhas dele, com os padroes de fabrica
    # que o Samuel escolheu: A "Guardar a tinta forte" (conferencia 14), o
    # papel de dentro da gravura branco (conferencia 12, P2 (a)) e as letras da
    # moldura com a cor delas e o papel branco atras (conferencia 12, P4 (a)).
    # Cada pagina pode trocar so nela (os campos de mesmo nome em ConfigPagina).
    # Os valores possiveis e o que fazem: core/misto.py. Projeto antigo, sem
    # os campos, abre com o Misto desligado (de_dicionario; regra do Samuel,
    # conferencia 14: "o programa [...] vai ter que ser capaz de abrir arquivos
    # de versoes anteriores"). Quem mostra: ui/tela_opcoes.py (grupo dos
    # filtros); quem usa: core/pipeline._filtrar. Seguro mudar: os padroes
    # (sao decisao do Samuel; os de fabrica moram em core/misto.py).
    misto_so_as_letras: bool = False
    misto_fora_do_texto: str = FORA_DO_TEXTO_PADRAO
    misto_papel_da_gravura: str = PAPEL_DA_GRAVURA_PADRAO
    misto_letras_na_moldura: str = LETRAS_NA_MOLDURA_PADRAO

    # "Limpar pontinhos" do livro, no Preto e branco e no "So as letras".
    # De fabrica: PONTINHOS_PADRAO (core/pontinhos_scantailor.PADRAO). Em
    # 06/10 (P7) era o do ScanTailor "pouco"; desde 07/10 o do ScanTailor so
    # vale quando a pessoa escolhe ("so deve ser usado se for selecionado
    # junto, e nao como automatico junto do preto e branco", Samuel), e o de
    # fabrica e "nosso" ou "desligado" (falta o Samuel dizer qual; a troca e
    # uma linha la). Escolhas: desligado, o nosso, pouco, normal, muito
    # (core/pontinhos_scantailor.py,
    # ESCOLHAS: codigos internos, nunca o texto da tela). Cada pagina pode
    # trocar so nela (ConfigPagina.limpar_pontinhos). Projeto salvo antes
    # deste campo abre com "nosso" (de_dicionario): era o que ele usava, e um
    # livro ja conferido nao muda sem o Samuel saber. Quem mostra:
    # ui/tela_opcoes.py (grupo dos filtros) e ui/tela_conferir.py (aba
    # Filtro); quem usa: core/pipeline._filtrar. Seguro mudar: nada aqui (o
    # de fabrica mora em core/pontinhos_scantailor.PADRAO).
    limpar_pontinhos: str = PONTINHOS_PADRAO

    folhas: list[ConfigFolha] = field(default_factory=list)
    paginas: list[ConfigPagina] = field(default_factory=list)
    criado_em: str = ""

    # Fatos do livro INTEIRO, ditos uma vez: "este livro tem uma página
    # por folha", "foi escaneado em qualidade baixa". Sao alertas que
    # valiam para quase toda página e viraram ruido no contador.
    observacoes: list[str] = field(default_factory=list)

    # --- conveniencias ----------------------------------------------------

    @property
    def paginas_ativas(self) -> list[ConfigPagina]:
        """As paginas que vao para o PDF.

        Uma folha NAO dividida sai UMA vez, inteira, se alguma das paginas
        dela nao estiver apagada; so some do PDF se a pessoa apagou TODAS as
        paginas da folha. As outras paginas saem se nao estiverem apagadas.

        Historia (item 2.1, 06/10/2026): o "nao dividir esta" da aba Onde
        cortar so desligava ConfigFolha.dividir, e as DUAS paginas da folha
        continuavam na lista - cada uma desenhava a folha inteira, e o PDF
        saia com a folha repetida. O primeiro conserto tirava sempre a metade
        da direita, e uma folha com a ESQUERDA apagada sumia inteira do PDF
        (parecer do verificador, 06/10: a pagina de rosto do Gradus Primus do
        Samuel). Agora fica a primeira pagina NAO apagada da folha (que o
        pipeline desenha inteira: a metade so vale com a folha dividida), e e
        o mesmo que o fase-1 fazia quando so uma das duas estava viva. A
        lista de paginas nao muda (o desfazer e as acoes guardam paginas pela
        posicao). Ver metade_sobrando. Arriscado: voltar a escolher sempre a
        mesma metade (a folha some quando ela esta apagada)."""
        ativas: list[ConfigPagina] = []
        folhas_que_ja_sairam: set[int] = set()
        for pagina in self.paginas:
            if pagina.apagada:
                continue
            if self._de_folha_nao_dividida(pagina):
                if pagina.folha in folhas_que_ja_sairam:
                    continue
                folhas_que_ja_sairam.add(pagina.folha)
            ativas.append(pagina)
        return ativas

    def _de_folha_nao_dividida(self, pagina: ConfigPagina) -> bool:
        """A pagina e uma das metades (esquerda/direita) de uma folha que nao
        esta dividida? (ela desenha a folha inteira)"""
        if pagina.metade == METADE_INTEIRA or not 0 <= pagina.folha < len(self.folhas):
            return False
        return not self.folhas[pagina.folha].dividir

    def metade_sobrando(self, pagina: ConfigPagina) -> bool:
        """A pagina fica fora do PDF por repetir a folha? (folha nao
        dividida, e outra pagina nao apagada da mesma folha, antes dela, ja
        leva a folha inteira). Pagina apagada nao conta como sobrando: ela
        esta fora por ter sido apagada."""
        if pagina.apagada or not self._de_folha_nao_dividida(pagina):
            return False
        for outra in self.paginas:
            if outra is pagina:
                return False
            if outra.folha == pagina.folha and not outra.apagada:
                return True
        return False

    @property
    def total_apagadas(self) -> int:
        return sum(1 for p in self.paginas if p.apagada)

    @property
    def so_cadernos(self) -> bool:
        """Caminho rapido: nenhuma alteracao de imagem, só reordenar."""
        return (
            self.montar_cadernos
            and not self.dividir_folhas
            and not self.limpar
            and not self.endireitar
            and not self.cortar_bordas
            and self.total_apagadas == 0
        )

    @property
    def alguma_funcao_marcada(self) -> bool:
        return any(
            (self.dividir_folhas, self.limpar, self.endireitar,
             self.cortar_bordas, self.montar_cadernos)
        )

    def pendentes_de_revisao(self) -> int:
        return sum(1 for f in self.folhas if f.precisa_revisao) + sum(
            1 for p in self.paginas if p.precisa_revisao
        )

    # --- serializacao -----------------------------------------------------

    def para_dicionario(self) -> dict[str, Any]:
        """O projeto pronto para o projeto.json.

        Decisao D2 (02/10/2026): cada pagina com zonas e geometria anotada
        ganha "zonas_na_folha" (as zonas na folha original, a verdade); a
        "selecao" em fracao da pagina fica junto, como copia para o programa
        instalado de antes (ver core/zonas_na_folha.py). A conta e so na hora
        de gravar: a memoria nao muda.
        """
        return Projeto.para_o_disco(self.fotografar())

    def fotografar(self) -> dict[str, Any]:
        """A primeira metade de para_dicionario: uma COPIA do projeto como
        esta agora (dataclasses.asdict), sem as zonas na folha. E a parte que
        tem de ser feita no fio que mexe no projeto (a janela); a segunda
        (para_o_disco) pode ir para o fio de gravar
        (projetos.salvar_estado_por_tras, R1 de 05/10/2026). Arriscado:
        devolver algo que nao seja copia (o fio de gravar leria o projeto
        enquanto a janela o muda)."""
        from core.zonas_na_folha import TRANCA_DAS_ZONAS

        # A trava das zonas: a previa (outro fio) pode estar levando as zonas
        # de uma pagina para o preparo novo (zonas_na_folha.acompanhar troca a
        # selecao E a geometria juntas). Sem a trava, o arquivo poderia sair
        # com a selecao de antes e a geometria de depois.
        with TRANCA_DAS_ZONAS:
            return asdict(self)

    @staticmethod
    def para_o_disco(dados: dict[str, Any]) -> dict[str, Any]:
        """A segunda metade de para_dicionario: acrescenta "zonas_na_folha"
        a cada pagina de uma fotografia (fotografar). Mexe so na fotografia,
        que e uma copia: pode rodar em qualquer fio. Devolve a mesma."""
        from core.zonas_na_folha import para_o_disco

        # tuplas viram listas no JSON; guardamos assim mesmo e convertemos na volta
        for pagina in dados.get("paginas", []):
            try:
                para_o_disco(pagina)
            except Exception:  # noqa: BLE001 - sem a copia na folha, grava como antes
                pagina.pop("zonas_na_folha", None)
        return dados

    @staticmethod
    def de_dicionario(dados: dict[str, Any]) -> "Projeto":
        """Reconstroi o projeto, tolerando arquivos de versões anteriores.

        Campos que sumiram entre uma versão e outra sao descartados, e os que
        surgiram ganham o padrão. Sem isso, reabrir um projeto antigo derrubaria
        o programa - e o usuário perderia o trabalho por causa de um campo.
        Exemplo: tem_camadas (item 1.1, 29/09/2026) falta nos projetos
        antigos e volta False; tirar_fundo_sozinho (a caixinha da primeira
        ligacao do 1.1, que saiu) sobra nos projetos dessa rodada e e
        descartado (testado em tests/test_tirar_fundo_no_programa.py).
        """
        from core.zonas_na_folha import do_disco

        folhas = [ConfigFolha(**_so_campos_conhecidos(ConfigFolha, _migrar_folha(f)))
                  for f in dados.pop("folhas", [])]
        # D2 (02/10/2026): "zonas_na_folha" volta para fracao da pagina aqui,
        # com a geometria anotada (core/zonas_na_folha.do_disco). Pagina de
        # projeto antigo (sem o campo) passa como sempre.
        paginas = [ConfigPagina(**_so_campos_conhecidos(ConfigPagina, _migrar(do_disco(p))))
                   for p in dados.pop("paginas", [])]
        # "Limpar pontinhos" (06/10/2026): projeto gravado antes deste campo
        # usava o nosso - continua com ele (a pagina que tinha a caixinha
        # "limpar poeirinha" desligada ja voltou "desligado", em _migrar).
        dados.setdefault("limpar_pontinhos", PONTINHOS_DO_PROJETO_ANTIGO)
        # Item 2.1 (06/10/2026): o livro novo nao divide mais (dividir_folhas
        # de fabrica virou False), mas o projeto salvo SEM o campo (nao
        # deveria existir: asdict sempre grava) era de quando o de fabrica
        # dividia - continua dividindo. E o jeito de dividir de quem nao tem
        # o campo e o do programa (era o unico). "O programa vai ter que ser
        # capaz de abrir arquivos de versoes anteriores" (Samuel, 05/10).
        dados.setdefault("dividir_folhas", True)
        dados.setdefault("dividir_como", DIVIDIR_DO_PROJETO_ANTIGO)
        # Item 2.2 (07/10/2026): o projeto gravado antes do endireitar do
        # ScanTailor endireitava pela conta do programa - continua com ela.
        dados.setdefault("endireitar_como", ENDIREITAR_DO_PROJETO_ANTIGO)
        # Item 2.2, G6 (09/10/2026): o projeto gravado antes da ordem nova
        # cortava antes de endireitar - continua assim, ponto por ponto.
        dados.setdefault("ordem_do_preparo", ORDEM_DO_PROJETO_ANTIGO)
        projeto = Projeto(**_so_campos_conhecidos(Projeto, dados))
        projeto.folhas = folhas
        projeto.paginas = paginas
        return projeto


def _so_campos_conhecidos(classe, dados: dict[str, Any]) -> dict[str, Any]:
    validos = {c.name for c in fields(classe)}
    return {k: v for k, v in dados.items() if k in validos}


def _migrar_folha(dados: dict[str, Any]) -> dict[str, Any]:
    """Uma folha do projeto.json de volta ao formato da memoria: a sobra
    (item 2.1) e tupla, e o JSON grava lista. Folha de projeto antigo (sem
    os campos do item 2.1) passa como esta: os campos ganham o padrao."""
    sobra = dados.get("sobra")
    if isinstance(sobra, list):
        dados["sobra"] = tuple(sobra) if len(sobra) == 2 else None
    return dados


def _migrar(dados: dict[str, Any]) -> dict[str, Any]:
    """JSON não tem tupla; devolve os recortes ao formato original."""
    valor = dados.get("recorte")
    if isinstance(valor, list):
        dados["recorte"] = tuple(valor)

    # Mesma migração para o tamanho de folha escolhido (item 2/4 do teste do
    # Boécio, seção 3a do plano) - None fica None, so lista vira tupla.
    tamanho = dados.get("tamanho_folha_cm")
    if isinstance(tamanho, list):
        dados["tamanho_folha_cm"] = tuple(tamanho)

    # Projetos gravados antes do medidor deslizante guardavam a forca do preto
    # como palavra. Traduzimos para o numero equivalente, senao reabrir um
    # trabalho antigo quebraria.
    antigas = {"mais_fraco": 15, "normal": 50, "mais_escuro": 85}
    forca = dados.get("forca_preto")
    if isinstance(forca, str):
        dados["forca_preto"] = antigas.get(forca, 50)

    # campos que nao existiam na versao anterior
    for campo in ("clareza_melhorar", "intensidade_magico"):
        dados.setdefault(campo, 50)

    # A caixinha "limpar poeirinha" (despeckle) virou a escolha "Limpar
    # pontinhos" (06/10/2026). Pagina gravada antes, com a caixinha
    # desligada, continua sem limpar; ligada, segue o livro (que no projeto
    # antigo e "nosso", ver Projeto.de_dicionario) - sai igual a antes.
    if "limpar_pontinhos" not in dados and dados.get("despeckle") is False:
        dados["limpar_pontinhos"] = PONTINHOS_DESLIGADO

    return dados


@dataclass
class Acao:
    """Uma alteracao feita pelo usuario, para desfazer e refazer.

    Guardamos a ACAO, não uma copia do projeto: com centenas de páginas, copiar
    o estado a cada mexida seria pesado demais. Assim o desfazer e ilimitado.
    """

    momento: str
    tipo: str
    alvo: str                  # "folha" ou "pagina"
    indices: list[int]
    antes: dict[str, Any]
    depois: dict[str, Any]
    descricao: str

    @staticmethod
    def nova(
        tipo: str, alvo: str, indices: list[int],
        antes: dict[str, Any], depois: dict[str, Any], descricao: str,
    ) -> "Acao":
        return Acao(
            momento=datetime.now().isoformat(timespec="seconds"),
            tipo=tipo, alvo=alvo, indices=list(indices),
            antes=dict(antes), depois=dict(depois), descricao=descricao,
        )

    def para_dicionario(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def de_dicionario(dados: dict[str, Any]) -> "Acao":
        return Acao(**dados)


def nome_de_arquivo_seguro(nome: str) -> str:
    """Tira do nome os caracteres que o Windows não aceita em arquivo."""
    proibidos = '<>:"/\\|?*'
    limpo = "".join("-" if c in proibidos else c for c in nome).strip(" .")
    return limpo or "livro"


def nome_de_saida_sugerido(projeto: "Projeto") -> str:
    """Nome de arquivo proposto, já com a extensao.

    O sufixo conta o que foi feito, para o Kaique diferenciar duas versoes do
    mesmo livro na mesma pasta.
    """
    from core.filtros import NOMES_AMIGAVEIS

    base = nome_de_arquivo_seguro(projeto.nome or "livro")

    if projeto.montar_cadernos:
        sufixo = "cadernos"
    elif projeto.limpar and projeto.filtro_padrao == TIRAR_FUNDO:
        # item 1.1: "livro - tirar o fundo.pdf" soaria como ordem; o arquivo
        # diz como o livro saiu
        sufixo = "sem fundo"
    elif projeto.limpar:
        sufixo = NOMES_AMIGAVEIS.get(projeto.filtro_padrao, projeto.filtro_padrao).lower()
    else:
        sufixo = "arrumado"

    return f"{base} - {sufixo}.pdf"


def filtro_valido(filtro: str) -> str:
    return filtro if filtro in FILTROS else PRETO_E_BRANCO
