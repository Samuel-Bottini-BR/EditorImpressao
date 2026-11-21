# Volta 11: a frase da D-816 como sai hoje e como sairia com a contração (21/11/2026)

Tirada do código de verdade: a de hoje, da função `_frase_depois_do_pedido_de_liberar` como está em `1624a05a`; a do conserto, da mesma função com as duas junções trocadas pela `com_preposicao` (a mutação M8), numa cópia à parte. Só as duas palavras "em a"/"em o" mudam.

```text

== na pasta das provas, HOJE:
v1.1.0: pedi para liberar em a pasta C:\EditorImpressaoProva\versoes 3 e não deu para reconferir agora se ficou liberada. Depois do pedido de liberar, o publicar nunca apaga nada (uma leitura atrasada poderia apagar a versão já liberada), e NÃO apaguei. Ela pode ter ficado de dois jeitos: se ficou liberada em a pasta C:\EditorImpressaoProva\versoes 3, está inteira (tudo foi lido de volta antes do pedido) e vale: não publique de novo com v1.1.0; se ficou como rascunho, apague depois com: publicar_versao_kaique.py --apagar v1.1.0 --pasta "C:\EditorImpressaoProva\versoes 3"; e publique de novo. Para conferir qual dos dois: olhe a pasta C:\EditorImpressaoProva\versoes 3: a subpasta v1.1.0 é a liberada e .rascunho-v1.1.0 é o rascunho

== na pasta das provas, COM O CONSERTO:
v1.1.0: pedi para liberar na pasta C:\EditorImpressaoProva\versoes 3 e não deu para reconferir agora se ficou liberada. Depois do pedido de liberar, o publicar nunca apaga nada (uma leitura atrasada poderia apagar a versão já liberada), e NÃO apaguei. Ela pode ter ficado de dois jeitos: se ficou liberada na pasta C:\EditorImpressaoProva\versoes 3, está inteira (tudo foi lido de volta antes do pedido) e vale: não publique de novo com v1.1.0; se ficou como rascunho, apague depois com: publicar_versao_kaique.py --apagar v1.1.0 --pasta "C:\EditorImpressaoProva\versoes 3"; e publique de novo. Para conferir qual dos dois: olhe a pasta C:\EditorImpressaoProva\versoes 3: a subpasta v1.1.0 é a liberada e .rascunho-v1.1.0 é o rascunho

== no GitHub, HOJE:
v1.1.0: pedi para liberar em o GitHub (Samuel-Bottini-BR/EditorImpressao) e não deu para reconferir agora se ficou liberada. Depois do pedido de liberar, o publicar nunca apaga nada (uma leitura atrasada poderia apagar a versão já liberada), e NÃO apaguei. Ela pode ter ficado de dois jeitos: se ficou liberada em o GitHub (Samuel-Bottini-BR/EditorImpressao), está inteira (tudo foi lido de volta antes do pedido) e vale: não publique de novo com v1.1.0; se ficou como rascunho, apague depois com: publicar_versao_kaique.py --apagar v1.1.0; e publique de novo. Para conferir qual dos dois: gh release view v1.1.0 -R Samuel-Bottini-BR/EditorImpressao --json isDraft ("isDraft": true é rascunho; false, liberada; "release not found", não ficou nada)

== no GitHub, COM O CONSERTO:
v1.1.0: pedi para liberar no GitHub (Samuel-Bottini-BR/EditorImpressao) e não deu para reconferir agora se ficou liberada. Depois do pedido de liberar, o publicar nunca apaga nada (uma leitura atrasada poderia apagar a versão já liberada), e NÃO apaguei. Ela pode ter ficado de dois jeitos: se ficou liberada no GitHub (Samuel-Bottini-BR/EditorImpressao), está inteira (tudo foi lido de volta antes do pedido) e vale: não publique de novo com v1.1.0; se ficou como rascunho, apague depois com: publicar_versao_kaique.py --apagar v1.1.0; e publique de novo. Para conferir qual dos dois: gh release view v1.1.0 -R Samuel-Bottini-BR/EditorImpressao --json isDraft ("isDraft": true é rascunho; false, liberada; "release not found", não ficou nada)
```

O script que tirou as frases:

```python
"""Volta 11: a frase da D-816 como sai hoje e como sairia com o conserto (a pergunta ao Samuel). As duas tiradas do
codigo de verdade: a de hoje, da funcao como esta (1624a05a); a do conserto, da mesma funcao com as duas juncoes
trocadas pela com_preposicao (a mutacao M8, numa copia a parte). Uso: python frase_d816.py <copia do codigo> <saida>"""
import importlib.util, sys
from pathlib import Path

copia, saida = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(copia))
import publicar_versao_kaique as hoje  # noqa: E402

texto = (copia / "publicar_versao_kaique.py").read_bytes().decode("utf-8").replace("\r\n", "\n")
for velho, novo in (("pedi para liberar em {destino.nome} e", "pedi para liberar {com_preposicao('em', destino.nome)} e"),
                    ('se ficou liberada em "\n            f"{destino.nome}, está',
                     'se ficou liberada "\n            f"{com_preposicao(\'em\', destino.nome)}, está')):
    assert texto.count(velho) == 1, velho
    texto = texto.replace(velho, novo)
consertado = Path(saida).with_name("_publicar_com_o_conserto.py")
consertado.write_text(texto, encoding="utf-8")
spec = importlib.util.spec_from_file_location("publicar_com_o_conserto", consertado)
conserto = importlib.util.module_from_spec(spec)
sys.modules["publicar_com_o_conserto"] = conserto
spec.loader.exec_module(conserto)
consertado.unlink()
linhas = []
for rotulo, destino_hoje, destino_conserto in (
        ("na pasta das provas", hoje.DestinoPasta(Path(r"C:\EditorImpressaoProva\versoes 3")),
         conserto.DestinoPasta(Path(r"C:\EditorImpressaoProva\versoes 3"))),
        ("no GitHub", hoje.DestinoGitHub(), conserto.DestinoGitHub())):
    linhas += [f"== {rotulo}, HOJE:", hoje._frase_depois_do_pedido_de_liberar(destino_hoje, "v1.1.0"), "",
               f"== {rotulo}, COM O CONSERTO:", conserto._frase_depois_do_pedido_de_liberar(destino_conserto, "v1.1.0"), ""]
Path(saida).write_text("\n".join(linhas), encoding="utf-8")
print("ok")
```
