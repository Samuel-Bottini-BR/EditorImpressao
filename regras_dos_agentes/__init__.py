"""As regras dos agentes do Editor de Impressão, por programa (passo 0 do plano da parte do Windows, 19/11/2026).

Não é parte do programa do Kaique: nada de `core/`, `ui/` ou da raiz importa daqui, e o pacote não importa nada do
programa (só lê os arquivos como texto). Nasceu das decisões do Samuel de 18 e 19/11/2026:

- D-784, o pacote de regras de cada trabalho: `catalogo.py` (todas as regras), `tabela_arquivos.py` (arquivo →
  etiquetas) e `montar_pacote.py` (monta o pacote de um pedido a partir da lista de arquivos);
- D-791, o porteiro: `porteiro.py` (as 24 conferências da proposta das regras, §5.1, com a numeração da tabela de lá) e
  `excecoes.py` (a lista de exceções, um item por lugar, que só diminui e só ganha item com o "sim" do Samuel);
- D-792, o formulário da entrega: `formulario.py` (F1 a F20 e as perguntas das etiquetas, nas três etapas, e os seis
  campos do relatório de quem tenta quebrar);
- a conferência antes do commit: `python -m regras_dos_agentes antes-do-commit` (em `__main__.py`), chamada por
  `ganchos/pre-commit` (a gerente liga com `git config core.hooksPath ganchos`; o teste no GitHub é quem garante,
  porque o git não avisa quando o gancho falta);
- `texto_para_o_samuel.py`: o texto curto do "sim" à lista, contado da própria lista;
- `repositorio_de_prova.py`: um repositório git de verdade numa pasta, para as provas e para quem tenta quebrar.

Peças únicas (CLAUDE.md §11.12, ponto 1): toda conversa com o git passa por `conversa_com_o_git.py`; com o GitHub, por
`conversa_com_o_github.py`; toda leitura de código Python, por `leitura_do_codigo.py`; o Livro de decisões, por
`livro.py`; o pedido (papel, partida, lista de arquivos), por `pedido.py`. Ninguém aqui chama o git ou o `gh` por
conta própria.

Como usar (linha de comando): `python -m regras_dos_agentes --help`.

Seguro mexer: textos de explicação, acrescentar linha na tabela, acrescentar regra no catálogo. Arriscado: a escolha
das regras do pacote (`montar_pacote.escolher_regras`), as buscas do porteiro (cada mudança precisa da prova dela em
`tests/test_conferencias_*.py`: acusa o errado e não acusa o certo) e a comparação com a lista de exceções.
"""
