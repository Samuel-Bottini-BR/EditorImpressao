"""Desliga cada proteção do atualizador novo, uma por vez, e mostra que o teste dela FALHA (D-811 a D-813, D-827).

Uso (na pasta da cópia): `.venv\\Scripts\\python.exe relatorios\\atualizador-novo\\mutacoes.py`. Para cada mutação: troca
um trecho do código (o texto exato, que tem de existir uma vez só), roda só o teste que protege, anota se falhou e
DEVOLVE o arquivo como estava (mesmo se der erro no meio). A saída vai para a tela e para `mutacoes-resultado.txt` ao
lado deste arquivo. Nada do Windows, do Velopack ou do disco de fora é tocado. Não é parte do programa (fica em
relatorios/, fora do que vai para o Kaique).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
F, A, W, C = "core/fases_da_atualizacao.py", "atualizacao.py", "core/windows.py", "core/conversa_com_o_velopack.py"
T = "tests/test_atualizador_novo.py"

MUTACOES = [
    ("1 sem licença não procura", F, "    if not abriu.pasta_grava:\n", "    if False:\n",
     T + "::test_protecao_1_sem_licenca_pergunta_ao_windows_e_nao_procura"),
    ("2 assinatura antes de baixar", F,
     "    if isinstance(e, Assinatura) and f is Fase.CONFERINDO:\n        if e.certa:",
     "    if isinstance(e, Assinatura) and f is Fase.CONFERINDO:\n        if True:",
     T + "::test_protecao_2_assinatura_errada_nao_baixa_e_avisa_com_a_frase_2"),
    ("3 soma do arquivo baixado antes de trocar", A, "        if soma.lower() != assinada.lower():",
     "        if False:", T + "::test_protecao_3_pacote_trocado_depois_de_baixar_nao_troca"),
    ("4a motor antes de anunciar", F,
     "        if e.no_lugar:\n            return replace(estado, fase=Fase.PROCURANDO), [Procurar()]",
     "        if True:\n            return replace(estado, fase=Fase.PROCURANDO), [Procurar()]",
     T + "::test_protecao_4a_motor_fora_do_lugar_nada_e_procurado_nem_anunciado"),
    ("4b motor antes de trocar", A, "        if not self._motor_no_lugar(motor):", "        if False:",
     T + "::test_protecao_4b_motor_fora_do_lugar_na_hora_de_trocar_nao_troca"),
    ("5 a licença é o último passo", A,
     "    return [windows.passo_apagar_tarefa(NOME_DA_TAREFA), windows.passo_instalar_visual_c(),\n"
     "            windows.passo_tirar_instalacao_do_inno(), windows.passo_dar_licenca_aos_usuarios()]",
     "    return [windows.passo_apagar_tarefa(NOME_DA_TAREFA), windows.passo_dar_licenca_aos_usuarios(),\n"
     "            windows.passo_instalar_visual_c(), windows.passo_tirar_instalacao_do_inno()]",
     T + "::test_protecoes_5_e_6_a_ordem_dos_passos_da_pergunta"),
    ("6 o ajudante antigo sai antes da licença", A,
     "    return [windows.passo_apagar_tarefa(NOME_DA_TAREFA), windows.passo_instalar_visual_c(),",
     "    return [windows.passo_instalar_visual_c(),",
     T + "::test_protecoes_5_e_6_a_ordem_dos_passos_da_pergunta"),
    ("7 a conta de testes não pergunta nem procura", F,
     "    if not e.instalado or e.conta_de_testes or e.portatil:", "    if not e.instalado or e.portatil:",
     T + "::test_protecao_7_conta_de_testes_nao_pergunta_nem_procura"),
    ("8 a versão que falhou não é tentada de novo", F, "        if e.versao in estado.nao_tentar:",
     "        if False:", T + "::test_protecao_8_a_versao_que_falhou_nao_e_baixada_de_novo"),
    ("9 outra janela aberta não troca", A, "        if outras:\n", "        if False:\n",
     T + "::test_protecao_9_outra_janela_aberta_nao_troca"),
    ("10 a troca só depois de a janela fechar", F,
     "    if isinstance(e, JanelaFechou) and f is Fase.FECHANDO:\n        if e.fechou:",
     "    if isinstance(e, JanelaFechou) and f is Fase.FECHANDO:\n        if True:",
     T + "::test_protecao_10_a_janela_que_nao_fecha_nao_troca"),
    ("11 a volta só com pacote assinado", A,
     "        if motivo is not None:\n            return fases.VoltaPedida(False, f\"a versão {ef.para} não tem a assinatura",
     "        if False:\n            return fases.VoltaPedida(False, f\"a versão {ef.para} não tem a assinatura",
     T + "::test_protecao_11_a_volta_sem_a_assinatura_nao_troca_e_avisa_com_a_frase_3"),
    ("12 pelo código nada roda", A, "    if not instalado_pelo_velopack() and not ganchos:\n        return None\n",
     "", T + "::test_protecao_12_pelo_codigo_nada_roda"),
    ("13 só trocar_para chama a troca", A,
     "            self.velopack.baixar(self.fonte.endereco, self._achada)\n",
     "            self.velopack.baixar(self.fonte.endereco, self._achada)\n"
     "            self.velopack.trocar(self.fonte.endereco, self._achada, True, [])\n",
     T + "::test_protecao_13_so_um_lugar_chama_a_troca_do_velopack"),
    ("D-749 o preparo vale pelo teste de gravar, não pelo que o trabalho disse", A,
     "        self.evento(fases.PreparoTerminou(self._pasta_grava(self.raiz), f\"{r.desfecho}: {r.motivo}\"))",
     "        self.evento(fases.PreparoTerminou(r.deu_certo, f\"{r.desfecho}: {r.motivo}\"))",
     "tests/test_decisoes_preparo_d749.py::test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta"),
    ("D-832 a janelinha do Velopack (sem o modo silencioso)", C, "versao.pedido, silent=False,",
     "versao.pedido, silent=True,", T + "::test_d832_a_troca_usa_a_janelinha_do_velopack"),
    ("D-837 a licença que só acrescenta: a herança", W, "    if depois.protegida != antes.protegida:\n",
     "    if False:\n", "tests/test_windows_preparo_do_computador.py::test_d837_o_que_tira_ou_nao_acrescenta_e_acusado"),
    ("D-837 o porteiro: nada de tirar dentro da função", "regras_dos_agentes/porteiro.py",
     # (volta 2: a lista do "nunca" é usada em dois lugares, a linha e o texto em pedaços; desliga-se a lista)
     "    r\"/inheritance|/setowner|/remove|/deny|/reset|/restore|/substitute|/setintegritylevel|/save|:r\\b\", re.I)",
     "    r\"(?!x)x\", re.I)",
     "tests/test_porteiro_licenca_que_acrescenta.py::test_d837_tirar_negar_trocar_dono_ou_heranca_e_acusado_ate_na_funcao"),
    ("D-837 o porteiro: a exceção é uma função só", "regras_dos_agentes/porteiro.py",
     "        return arq.caminho == arquivo and arq.funcao(n) == funcao",
     "        return arq.caminho == arquivo",
     "tests/test_porteiro_licenca_que_acrescenta.py::test_d837_a_funcao_que_so_acrescenta_passa_so_na_peca"),
    # Volta 2 (os achados de quem tentou quebrar): cada conserto desligado.
    ("G1 a troca em curso não vira falha", F, "e.troca_em_curso is not False:", "False:",
     "tests/test_atualizador_volta2.py::test_g1_abrir_pelo_atalho_no_meio_da_troca_nao_anota_falha_e_sai_sem_janela"),
    ("M1 conferir antes de fechar", F,
     "            return replace(estado, fase=Fase.CONFERINDO_TROCA), [ConferirTroca()]",
     "            return replace(estado, fase=Fase.FECHANDO), [FecharJanela()]",
     "tests/test_atualizador_volta2.py::test_m1_reiniciar_agora_que_nao_pode_trocar_nao_fecha_a_janela"),
    ("M1 reabrir o que falha depois de fechar", F,
     "[ReabrirOPrograma()] if estado.trocando_com_janela else []", "[]",
     "tests/test_atualizador_volta2.py::test_m1_a_troca_que_falha_depois_de_fechar_reabre_o_programa"),
    ("M2 o motor da versão que entra (na troca)", A, "        if not self._motor_no_lugar(motor):",
     "        if not self._motor_no_lugar(None):",
     "tests/test_atualizador_volta2.py::test_m2_a_volta_confere_o_motor_da_anterior_e_volta"),
    ("M2 o motor da versão nova (no anúncio)", F, "        if e.certo and not e.motor_da_nova:", "        if False:",
     "tests/test_atualizador_volta2.py::test_m2_a_versao_nova_sem_o_motor_dela_nao_e_anunciada"),
    ("M4 a troca só com a anotação gravada", A, "        if not anotar_tentativa(de, para, volta):",
     "        if anotar_tentativa(de, para, volta) and False:",
     "tests/test_atualizador_volta2.py::test_m4_com_o_estado_que_nao_grava_nada_e_procurado_nem_trocado"),
    ("M4 nada procurado sem o estado gravando", F, "        if e.no_lugar and not estado.estado_grava:",
     "        if False:",
     "tests/test_atualizador_volta2.py::test_m4_com_o_estado_que_nao_grava_nada_e_procurado_nem_trocado"),
    ("leve 2 nenhuma licença a mais", W, "        if not veio_de_antes(nova) and not", "        if False and not",
     "tests/test_atualizador_volta2.py::test_leve2_uma_licenca_a_mais_na_pasta_e_acusada"),
    ("leve 2 o porteiro: só a linha do experimento", "regras_dos_agentes/porteiro.py",
     "            elif _PEDIDO_DE_LICENCA.search(linha) and not e_a_linha_provada(n):", "            elif False:",
     "tests/test_atualizador_volta2.py::test_leve2_o_porteiro_acusa_o_que_a_d837_nao_deixa"),
    ("leve 2 o porteiro: a ferramenta em pedaços", "regras_dos_agentes/porteiro.py",
     "        if m and not ja_na_linha and \\", "        if False and \\",
     "tests/test_atualizador_volta2.py::test_leve2_o_porteiro_acusa_o_que_a_d837_nao_deixa"),
    ("leve 2 o porteiro: quem chama a licença", "regras_dos_agentes/porteiro.py",
     "        if _CHAMA_A_LICENCA.search(linha) and", "        if False and",
     "tests/test_atualizador_volta2.py::test_leve2_o_porteiro_acusa_o_que_a_d837_nao_deixa"),
    ("leve 3 a família pela hora em que nasceu", W, "                if filho in criados and pai in criados and",
     "                if False and filho in criados and pai in criados and",
     "tests/test_atualizador_volta2.py::test_leve3_a_familia_respeita_a_hora_em_que_cada_um_nasceu"),
    ("a trava: velopack só no dono", "tests/test_trava_windows.py", '            "velopack": "Velopack"}', "}",
     "tests/test_trava_windows.py::test_velopack_so_no_dono"),
]


def rodar() -> int:
    """Roda todas as mutações; devolve quantas NÃO fizeram o teste falhar (0 = todas as proteções acusam)."""
    linhas, sobreviventes = [], 0
    for nome, arquivo, de, para, teste in MUTACOES:
        caminho = RAIZ / arquivo
        original = caminho.read_bytes()
        texto = original.decode("utf-8")
        if "\r\n" in texto:                       # a cópia do Windows guarda o fim de linha do Windows
            de, para = de.replace("\n", "\r\n"), para.replace("\n", "\r\n")
        if texto.count(de) != 1:
            linhas.append(f"[ERRO DA MUTAÇÃO] {nome}: o trecho aparece {texto.count(de)} vezes em {arquivo}")
            sobreviventes += 1
            continue
        try:
            caminho.write_bytes(texto.replace(de, para).encode("utf-8"))
            feito = subprocess.run([sys.executable, "-m", "pytest", teste, "-q", "-x", "-p", "no:cacheprovider"],
                                   cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")
        finally:
            caminho.write_bytes(original)
        falhou = feito.returncode != 0
        sobreviventes += not falhou
        ultima = (feito.stdout.strip().splitlines() or [""])[-1]
        linhas.append(f"[{'FALHOU (a proteção acusa)' if falhou else 'PASSOU (NÃO acusa!)'}] {nome} -> {teste} | "
                      f"{ultima}")
    saida = "\n".join(linhas) + f"\n\n{len(MUTACOES) - sobreviventes} de {len(MUTACOES)} mutações acusadas.\n"
    print(saida)
    (Path(__file__).parent / "mutacoes-resultado.txt").write_text(saida, encoding="utf-8")
    return sobreviventes


if __name__ == "__main__":
    raise SystemExit(rodar())
