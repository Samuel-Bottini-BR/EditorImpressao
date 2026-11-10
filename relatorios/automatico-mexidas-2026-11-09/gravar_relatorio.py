"""Grava o relatório do verificador (09/11/2026) nos três formatos (CLAUDE.md §2), a partir
do texto abaixo e de resultados.json (o que test_verificador_mexidas.py anotou).

    .venv\\Scripts\\python.exe relatorios/automatico-mexidas-2026-11-09/gravar_relatorio.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent.parent))

import relatorio  # noqa: E402

R = json.loads((AQUI / "resultados.json").read_text(encoding="utf-8"))


def perg(chave: str) -> str:
    ps = R[chave]["perguntas"]
    return "não perguntou" if not ps else "perguntou: \"" + ps[0]["texto"] + "\""


def linha1(etapa: str, nome: str, marcada: str, desmarcada: str, guarda: str) -> str:
    p = R[f"caso1/{etapa}/marcada_pular"]
    t = R[f"caso1/{etapa}/marcada_rodar_tambem"]
    d = R[f"caso1/{etapa}/desmarcada"]
    q = [x["quantas"] for x in p["perguntas"]]
    return (f"| {nome} | {marcada} | {'sim, ' + str(q[0]) + ' página(s)' if q else 'não'} | "
            f"{'ficou' if p['o_feito_a_mao_ficou'] else 'NÃO ficou'}"
            f"{' (página igual no PDF)' if p['pagina_igual_no_pdf'] else ''} | "
            f"{'passou por cima' if not t['o_feito_a_mao_ficou'] else 'ficou (não há o que passar por cima)'} | "
            f"{desmarcada}: {'não perguntou' if not d['perguntas'] else 'PERGUNTOU'}, "
            f"{guarda} {'ficou' if d['o_feito_a_mao_ficou'] else 'NÃO ficou'} | "
            f"{p['paginas_do_pdf'][1]} / {'vazio' if not (p['erros_log_novo'] + t['erros_log_novo'] + d['erros_log_novo']).strip() else 'COM ERRO'} |")


def filtros(chave: str) -> str:
    fs = R[chave]["filtro_de_cada_pagina_no_pdf"]
    comum = max(set(fs), key=fs.count)
    outras = [f"pág. {i + 1}: {f}" for i, f in enumerate(fs) if f != comum]
    return f"todas em {comum}" + (" menos " + ", ".join(outras) if outras else "")


def cad(chave: str) -> str:
    c = R[chave]["cadernos"]
    ok = c["na_ordem_certa"] and c.get("todas_as_paginas_uma_vez", True)
    return (f"{c['folhas_do_pdf']} lados de folha no PDF dos cadernos, "
            + ("na ordem certa da dobra, todas as páginas uma vez só" if ok else "ORDEM ERRADA"))


def log(chave: str) -> str:
    v = R[chave]
    return "erros.log vazio, nenhum erro" if not v["erros_log_novo"].strip() and not v["excecoes"] else "DEU ERRO"


g1 = R["caso1/girar_e_dividir/deitada_endireitada"]
g2 = R["caso1/girar_e_dividir/em_pe_deitada"]
c2 = R["caso2"]
volta = c2["ao_voltar_ao_automatico"]

TEXTO = f"""# Automático e páginas mexidas: o aviso pergunta quando deve?

Verificador, 09/11/2026. Teste de **máquina** (não precisa de olho). Ramo `obra-2026-10-26`
(cópia `obra-juncao`). Nenhuma janela abriu na tela: tudo rodou com a janela principal escondida
(offscreen). Nenhuma linha do programa foi mudada.

## Em poucas palavras

- **Mexida à mão: o aviso funciona.** Filtro (também o Preto e branco escolhido à mão), cortar,
  endireitar e dividir: o Automático com aquela etapa pergunta "1 página foi mexida à mão...",
  "Pular" deixa a página como estava (igual no PDF, ponto por ponto) e "Rodar nelas também" passa
  por cima. Com a etapa desmarcada, não pergunta e o que foi feito à mão fica.
- **Marcar, mover e girar à mão nunca entram no aviso**, mas também não se perdem: o Automático
  não tem etapa que passe por cima deles (a marcação à mão, o tamanho e lugar do conteúdo e o giro
  ficaram iguais em todas as rodadas). Uma ressalva no girar, abaixo.
- **O caso do Samuel funciona:** filtro em 3 páginas, depois só "Montar cadernos" no livro todo
  → não pergunta nada, as 3 páginas continuam com o filtro, os cadernos saem com todas as
  páginas na ordem certa, sem erro. Também no livro de verdade (Boécio, 50 páginas).
- **Rodada do Automático por cima de outra rodada: hoje não pergunta.** Filtro em 3 páginas e
  depois outro filtro no livro todo → as 3 páginas trocam de filtro sem aviso. Pela D-660 (nova,
  09/11) ele deveria perguntar: **errado pela D-660 (ainda não construída)**.
- **Cuidado (sem decisão escrita):** depois da rodada em 3 páginas, ao voltar ao Automático a
  caixinha "Limpar a folha" já vem marcada. Se só se marcar "Montar cadernos" e rodar no livro
  todo, o filtro vai para as 24 páginas, sem perguntar.
- Os testes que já existiam do aviso: **16 de 16 passaram**.

## Como foi testado

Pelo caminho de verdade: a janela principal do programa (escondida), o livro aberto como o
Kaique abre, as mexidas feitas pelos mesmos comandos que os botões da área de trabalho chamam,
o painel do Automático com as etapas marcadas e o "Rodar". Só a caixa da pergunta foi trocada
por uma resposta fixa ("Pular" ou "Rodar nelas também"), como os testes do programa já fazem; o
texto anotado é o que a caixa mostraria. No fim, o PDF foi gerado como o "Confirmar e processar"
grava. O filtro de cada página foi conferido **no PDF** (comparando com o mesmo livro gerado
todo em cada filtro), e a ordem dos cadernos lendo o número de cada página impresso nela.
Erros: o `erros.log` da rodada (pasta de dados separada) e qualquer erro inesperado.

Livros: um livro de teste feito para isso (24 páginas, cada uma com o seu número em
quadradinhos; e um de 4 folhas para o caso 1) e o **Boécio** do acervo (50 páginas, só lido).

Script: `relatorios/automatico-mexidas-2026-11-09/test_verificador_mexidas.py` (36 casos;
todos passaram). O que cada caso viu, em detalhe: `resultados.json`, na mesma pasta.

## Caso 1: mudança à mão, uma etapa por vez

O que se esperava (D-004, 28/09: "Automático em livro já mexido à mão: o programa pergunta se
quer pular as páginas mexidas."; D-485: o filtro escolhido à mão conta): com a etapa mexida
marcada, pergunta; "Pular" mantém; etapa desmarcada, não pergunta e a página fica.

| Mexida à mão | Automático com | Perguntou? | "Pular" | "Rodar nelas também" | Etapa desmarcada | Páginas do PDF / erros |
|---|---|---|---|---|---|---|
{linha1("filtro", "Filtro (Melhorar à mão)", "Limpar em Preto e branco", "Endireitar + Cortar", "o Melhorar")}
{linha1("filtro_pb", "Preto e branco à mão (e força do preto)", "Limpar em Melhorar", "Endireitar + Cortar", "o Preto e branco")}
{linha1("cortar", "Cortar (corte à mão)", "Cortar as bordas", "Endireitar + Limpar", "o corte")}
{linha1("endireitar", "Endireitar (1,5 grau à mão)", "Endireitar", "Cortar + Limpar", "o ângulo")}
{linha1("dividir", "Dividir (linha posta à mão)", "Dividir", "Endireitar + Cortar + Limpar", "a linha")}
{linha1("marcar", "Marcar (gravura marcada à mão)", "Limpar + Gravuras e fotos", "Endireitar + Cortar", "a marcação")}
{linha1("mover", "Mover (conteúdo em 80%)", "Margens iguais", "Endireitar + Cortar + Limpar", "o tamanho")}
{linha1("girar", "Girar (1/4 à direita)", "Dividir + Endireitar + Cortar + Limpar", "só Montar cadernos", "o giro")}

Notas:

- "Rodar nelas também" (filtro, cortar, endireitar, dividir): o valor à mão sai e a marca de
  mexida também; o Automático passa a valer na página. Dividir: as 2 páginas da folha dividida à
  mão contam (pergunta "2 páginas"); com "Pular" a linha fica em 0,47, com "Rodar" o programa põe
  a dele.
- Marcar, mover e girar: **não perguntam**, mesmo com "Rodar nelas também" não há nada a passar
  por cima: a gravura marcada à mão, o conteúdo em 80% e o giro ficaram. No Livro não há decisão
  dizendo que essas três devem entrar no aviso (o código conta só dividir, endireitar, cortar e
  filtro). **Certo** pelo que está escrito.
- **Ressalva do girar (sem decisão escrita):** o giro não entra no aviso do Dividir. Página que
  veio deitada no PDF e foi posta em pé à mão: o Dividir **não** a partiu ({g1['paginas_da_folha_girada_depois']}
  página, certo). Mas uma página em pé que a pessoa deitou à mão (fica larga, como uma folha
  aberta) foi partida em {g2['paginas_da_folha_girada_depois']} pelo Dividir, sem perguntar. É um caso raro
  (não há motivo para deitar uma página em pé), por isso só fica anotado. É por isso que a linha
  "Girar" da tabela tem 6 páginas no PDF (a folha dupla e a página deitada, as duas partidas).

Veredito do caso 1: **certo** (D-004, D-485).

## Caso 2: o caso do Samuel

Automático só nas páginas 4, 8 e 12, só com "Limpar a folha" em Preto e branco. Depois,
Automático no livro todo só com "Montar cadernos".

O que se esperava (D-589: o que não está marcado não é feito; D-660: "Rodar no livro todo só o
'Montar cadernos', depois de um filtro em algumas páginas, funciona sem erro e não mexe no filtro
delas"): sem pergunta, as 3 páginas com o filtro, cadernos certos, sem erro.

O que aconteceu:

- Primeira rodada: {"não perguntou" if not c2["perguntas_na_1a_rodada"] else "PERGUNTOU"} (nada mexido à mão).
- Ao voltar ao Automático: a caixinha "Limpar a folha" vem marcada ("{volta['situacoes']['limpar']}").
- Segunda rodada (só "Montar cadernos"): {perg("caso2")}.
- Filtro no PDF: {filtros("caso2")}.
- Cadernos: {cad("caso2")} (24 páginas em cadernos de 20: um de 20 e um de 4).
- {log("caso2")}.
- Livro de verdade (Boécio, 50 páginas, o mesmo caminho): {perg("acervo_boecio/caso2")};
  as páginas 4, 8 e 12 continuam em Preto e branco e as outras no Original (filtro que vale em cada página do projeto); {cad("acervo_boecio/caso2")}
  (cadernos de 20, 20 e 12; a ordem conferida achando cada metade entre as páginas do PDF);
  {log("acervo_boecio/caso2")}.

Veredito do caso 2: **certo** (D-589, D-660).

### Variação 2b: sem desmarcar o "Limpar a folha" que voltou marcado

Se depois da primeira rodada a pessoa só marca "Montar cadernos" (o "Limpar a folha" já estava
marcado) e roda no livro todo: {perg("caso2b")}; filtro no PDF: {filtros("caso2b")};
{cad("caso2b")}; {log("caso2b")}.

Não estraga as 3 páginas (continuam em Preto e branco), mas o filtro vai para o livro inteiro sem
aviso. Isso depende da pergunta ainda aberta das caixinhas depois de rodar (D-628,
`n0411-caixinhas-depois-de-rodar`; Samuel, 04/11: "elas tem que voltar todas desmarcadas"):
**sem decisão escrita** até essa resposta.

## Caso 3: a segunda rodada tem outro filtro

O mesmo do caso 2, só que a segunda rodada no livro todo tem "Limpar a folha" em Melhorar +
"Montar cadernos".

O que se esperava: D-660 (Samuel, 09/11: "mas caso o o automatico for mudar alguma coisa que foi
feito na ultima rodada ele deve perguntar."): perguntar antes de trocar o filtro das 3 páginas, e
"Pular" as manter.

O que aconteceu: {perg("caso3/pular")}. Filtro no PDF: {filtros("caso3/pular")}: as páginas 4, 8
e 12 perderam o Preto e branco. {cad("caso3/pular")}. {log("caso3/pular")}.

Veredito do caso 3: **errado pela D-660 (ainda não construída)**. Funciona sem erro, mas troca o
filtro da rodada anterior sem perguntar.

Por que (no código): a contagem do aviso (`core/automatico.paginas_mexidas`) só conta a marca de
mexida à mão; a página em que o Automático rodou só nela (`ConfigPagina.automatico`) é tirada da
conta de propósito (`_filtro_trocado_na_pagina`). Para reproduzir: abrir um livro, Automático
"nas escolhidas" (3 páginas) só com "Limpar a folha" em Preto e branco, "Rodar"; depois
Automático "no livro todo" com "Limpar a folha" em Melhorar, "Rodar" → nenhuma caixa aparece e as
3 páginas saem em Melhorar.

## Caso 4: mistura

Uma página mexida à mão (Mágico pro escolhido à mão) + as 3 páginas da primeira rodada (Preto e
branco) + segunda rodada no livro todo com "Limpar a folha" em Melhorar + "Montar cadernos".

O que se esperava: D-004 pergunta da página mexida à mão; D-660 também das 3 da rodada anterior
(contagem 4).

| Como | Perguntou | "Pular" | "Rodar nelas também" |
|---|---|---|---|
| página 6 mexida à mão antes da 1ª rodada | {R["caso4/mao_antes/pular"]["perguntas"][0]["quantas"]} página | {filtros("caso4/mao_antes/pular")} | {filtros("caso4/mao_antes/rodar_tambem")} |
| página 8 (uma das 3) mexida à mão depois da 1ª rodada | {R["caso4/mao_numa_das_3/pular"]["perguntas"][0]["quantas"]} página | {filtros("caso4/mao_numa_das_3/pular")} | {filtros("caso4/mao_numa_das_3/rodar_tambem")} |
| Boécio, página 6 à mão | {R["acervo_boecio/caso4"]["perguntas"][0]["quantas"]} página | página 6 em Mágico pro, as outras em Melhorar (no projeto) | (não rodado) |

Cadernos: em todos, {cad("caso4/mao_antes/pular")}; no Boécio, {cad("acervo_boecio/caso4")}.
Erros: nenhum (erros.log vazio em todos).

Veredito do caso 4: a parte da mão está **certa** (D-004: conta 1, "Pular" mantém o Mágico pro,
"Rodar" passa por cima). A parte da rodada anterior está **errada pela D-660 (ainda não
construída)**: a contagem é 1, não 4, e as páginas 4, 8 e 12 vão para Melhorar mesmo com
"Pular". A página 8 mexida à mão depois da rodada conta como mexida (certo).

## Caso 5: os testes que já existiam

`pytest tests/test_decisoes_automatico.py tests/test_decisoes.py
tests/test_automatico_pular_depois_de_dividir.py -q -k "d004 or mexid or pular or d607"`:
**16 passaram**, 44 de fora pelo filtro (como a gerente viu).

## Resumo dos vereditos

- Caso 1 (à mão, uma etapa por vez): **certo**. Marcar, mover e girar não entram no aviso e não
  se perdem; ressalva do girar + Dividir anotada (sem decisão escrita).
- Caso 2 (filtro em 3 páginas, depois só cadernos): **certo**, também no Boécio.
- Variação 2b ("Limpar" volta marcado e vai para o livro todo): **sem decisão escrita** (espera a
  pergunta das caixinhas, D-628).
- Caso 3 (outro filtro na segunda rodada): **errado pela D-660 (ainda não construída)**.
- Caso 4 (mistura): mão **certo**; rodada anterior **errado pela D-660 (ainda não construída)**.
- Caso 5: **16 de 16 passaram**.
- Nenhum erro, nenhum `erros.log`, nenhum PDF com página a mais ou a menos, cadernos sempre na
  ordem da dobra.
"""

if __name__ == "__main__":
    saida = relatorio.gravar(TEXTO, AQUI / "relatorio-automatico-mexidas",
                             titulo="Automático e páginas mexidas")
    for tipo, caminho in saida.items():
        print(tipo, caminho)
