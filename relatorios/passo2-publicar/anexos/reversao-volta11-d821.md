# Volta 11, D-821: a prova de reversão (21/11/2026)

Os dois testes mudados pela D-821 (o da volta 3, que passou a cobrar "ficou liberada na pasta", e a guarda das frases,
sem a exceção), rodados no código de antes do conserto (`1624a05a`: a frase da D-816 ainda com "em a pasta"), na
própria cópia `passo2`, antes de mexer em `publicar_versao_kaique.py`:

```text
FAILED tests/test_publicar_versao.py::test_volta3_achado1_uma_leitura_atrasada_depois_de_liberar_nunca_apaga_a_versao_liberada
FAILED tests/test_publicar_versao.py::test_volta11_nenhuma_frase_do_publicar_junta_em_ou_de_com_o_destino_a_mao
2 failed, 123 deselected in 13.14s
```

Depois do conserto (a frase pela `com_preposicao`), o arquivo inteiro: `125 passed in 92.27s`.
