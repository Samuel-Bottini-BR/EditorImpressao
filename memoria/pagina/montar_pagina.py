"""Monta memoria/pagina/index.html: a memória inteira num arquivo só, navegável e com busca.

O que é: a página que a gerente publica no claude.ai (pedido de 19/10/2026, CLAUDE.md §4.9). Ela leva dentro o
texto de todos os .md da pasta memoria/ e mostra cada um formatado, com uma lista à esquerda e uma busca.
Nada externo além de duas bibliotecas com versão fixa no jsDelivr (marked, que formata o Markdown, e DOMPurify,
que limpa o HTML).

Como rodar (da pasta do projeto), depois de mudar qualquer ficha:

    .venv\\Scripts\\python.exe memoria\\pagina\\montar_pagina.py

e depois republicar memoria/pagina/index.html no claude.ai (mesma página; ver memoria/geral/paginas-claude-ai.md).

Links: os links entre fichas abrem dentro da página. Links para fora da pasta memoria/ (plano, histórico, código)
viram links para o GitHub, no ramo RAMO_DO_GITHUB (troque com --ramo).

Seguro mudar: cores e textos do MODELO. Arriscado: o jeito de pôr o texto dentro do <script> (o "</" precisa
continuar escapado, senão um .md com "</script>" quebra a página).
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

RAMO_DO_GITHUB = "fase-1"
REPOSITORIO = "https://github.com/Samuel-Bottini-BR/EditorImpressao"

_RE_NUMERO = re.compile(r"(\d+)")


def _chave_natural(caminho: str):
    return [int(p) if p.isdigit() else p.lower() for p in _RE_NUMERO.split(caminho)]


def juntar_textos(pasta_memoria: Path) -> dict[str, str]:
    textos = {}
    for arquivo in sorted(pasta_memoria.rglob("*.md")):
        relativo = arquivo.relative_to(pasta_memoria).as_posix()
        if relativo.startswith("pagina/"):
            continue
        textos[relativo] = arquivo.read_text(encoding="utf-8", errors="replace")
    return dict(sorted(textos.items(), key=lambda par: _chave_natural(par[0])))


def montar(pasta_memoria: Path, ramo: str) -> str:
    textos = juntar_textos(pasta_memoria)
    dados = {
        "textos": textos,
        "ramo": ramo,
        "repositorio": REPOSITORIO,
        "montada_em": date.today().strftime("%d/%m/%Y"),
    }
    json_seguro = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    return MODELO.replace("__DADOS__", json_seguro)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ramo", default=RAMO_DO_GITHUB, help="ramo do GitHub para os links de fora da memória")
    args = parser.parse_args(argv)
    pasta_memoria = Path(__file__).resolve().parent.parent
    destino = pasta_memoria / "pagina" / "index.html"
    destino.write_text(montar(pasta_memoria, args.ramo), encoding="utf-8", newline="\n")
    print(f"Gravado {destino} ({destino.stat().st_size // 1024} KB, {len(juntar_textos(pasta_memoria))} arquivos)")
    return 0


MODELO = r"""<title>Memória do Editor de Impressão</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Literata:opsz,wght@7..72,500;7..72,700&family=JetBrains+Mono:wght@400&display=swap">
<style>
/* Layout: uma mesa de trabalho. Coluna estreita à esquerda com a busca e a lista das fichas (como o índice de um
   livro), e a ficha aberta à direita, em largura de leitura. No celular, a lista vira uma gaveta no alto. */
:root {
  --papel: #f6f7f5;        /* fundo: papel limpo, um pouco frio, como depois do filtro */
  --folha: #ffffff;        /* a ficha aberta */
  --tinta: #1d232b;        /* texto */
  --tinta-fraca: #59636e;  /* legendas, caminhos */
  --linha: #d9ddda;        /* divisórias */
  --azul: #1f4f8f;         /* links e destaque: tinta azul de iluminura */
  --laranja: #c4570f;      /* marca do "Para revisar": o que o programa pede para olhar */
  --laranja-fundo: #fbe9dc;
  --codigo-fundo: #eef0ee;
  --fonte-titulo: "Literata", Georgia, "Times New Roman", serif;
  --fonte-texto: "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
  --fonte-codigo: "JetBrains Mono", Consolas, "Courier New", monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --papel: #15191e; --folha: #1c2127; --tinta: #e4e7ea; --tinta-fraca: #9aa4ae; --linha: #2f363e;
    --azul: #8db6ec; --laranja: #f0955a; --laranja-fundo: #3a2618; --codigo-fundo: #252b32; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --papel: #15191e; --folha: #1c2127; --tinta: #e4e7ea; --tinta-fraca: #9aa4ae; --linha: #2f363e;
  --azul: #8db6ec; --laranja: #f0955a; --laranja-fundo: #3a2618; --codigo-fundo: #252b32; color-scheme: dark;
}
html, body { height: 100%; }
body {
  background: var(--papel); color: var(--tinta); font-family: var(--fonte-texto); font-size: 16px; line-height: 1.55;
}
.mesa {
  display: grid; grid-template-columns: minmax(240px, 300px) minmax(0, 1fr); gap: 0; min-height: 100%;
}
.lado {
  border-right: 1px solid var(--linha); padding-block: 20px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: 16px;
  position: sticky; top: env(safe-area-inset-top, 0px); height: 100vh; overflow-y: auto; box-sizing: border-box;
}
.marca { font-family: var(--fonte-titulo); font-weight: 700; font-size: 1.15rem; line-height: 1.25; margin: 0 0 4px; text-wrap: balance; }
.marca-sub { color: var(--tinta-fraca); font-size: 0.82rem; margin: 0 0 16px; }
.busca label { display: block; font-size: 0.75rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--tinta-fraca); margin-bottom: 4px; }
.busca input {
  width: 100%; box-sizing: border-box; font: inherit; padding: 8px 10px; border: 1px solid var(--linha);
  border-radius: 6px; background: var(--folha); color: var(--tinta);
}
.busca input:focus-visible, a:focus-visible, button:focus-visible { outline: 2px solid var(--azul); outline-offset: 2px; }
nav.lista { margin-top: 18px; display: grid; gap: 14px; }
nav.lista details summary { cursor: pointer; font-size: 0.75rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--tinta-fraca); }
nav.lista ul { list-style: none; margin: 6px 0 0; padding: 0; display: grid; gap: 1px; }
nav.lista a {
  display: block; padding: 3px 8px; border-radius: 4px; color: var(--tinta); text-decoration: none; font-size: 0.9rem;
  overflow-wrap: anywhere;
}
nav.lista a:hover { background: var(--codigo-fundo); }
nav.lista a[aria-current="page"] { background: var(--laranja-fundo); color: var(--tinta); box-shadow: inset 3px 0 0 var(--laranja); }
.ficha-area { min-width: 0; padding-block: 28px 64px; padding-left: max(16px, 4vw); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.caminho { font-family: var(--fonte-codigo); font-size: 0.78rem; color: var(--tinta-fraca); margin-bottom: 10px; overflow-wrap: anywhere; }
article.ficha {
  max-width: 72ch; background: var(--folha); border: 1px solid var(--linha); border-radius: 8px;
  padding: clamp(18px, 3vw, 36px);
}
article.ficha h1, article.ficha h2, article.ficha h3 { font-family: var(--fonte-titulo); line-height: 1.25; text-wrap: balance; }
article.ficha h1 { font-size: 1.7rem; margin: 0 0 12px; }
article.ficha h2 { font-size: 1.25rem; margin: 28px 0 8px; padding-top: 12px; border-top: 1px solid var(--linha); }
article.ficha h3 { font-size: 1.05rem; margin: 20px 0 6px; }
article.ficha p, article.ficha li { overflow-wrap: anywhere; }
article.ficha a { color: var(--azul); }
article.ficha blockquote { margin: 12px 0; padding: 8px 14px; border-left: 3px solid var(--laranja); background: var(--laranja-fundo); border-radius: 0 6px 6px 0; }
article.ficha code { font-family: var(--fonte-codigo); font-size: 0.86em; background: var(--codigo-fundo); padding: 1px 4px; border-radius: 3px; overflow-wrap: anywhere; }
article.ficha pre { background: var(--codigo-fundo); padding: 12px; border-radius: 6px; overflow-x: auto; }
article.ficha pre code { background: none; padding: 0; overflow-wrap: normal; }
.tabela { overflow-x: auto; margin: 12px 0; }
article.ficha table { border-collapse: collapse; font-size: 0.9rem; min-width: 100%; }
article.ficha th, article.ficha td { border: 1px solid var(--linha); padding: 6px 8px; vertical-align: top; text-align: left; }
article.ficha th { background: var(--codigo-fundo); }
article.ficha td { font-variant-numeric: tabular-nums; }
mark { background: var(--laranja-fundo); color: var(--tinta); box-shadow: 0 1px 0 var(--laranja); }
.resultados { display: grid; gap: 14px; }
.resultado a { font-weight: 700; color: var(--azul); }
.resultado .trecho { color: var(--tinta-fraca); font-size: 0.9rem; margin-top: 2px; }
.pasta ul { columns: 2 220px; padding-left: 18px; }
.aviso { color: var(--tinta-fraca); font-size: 0.85rem; }
@media (max-width: 760px) {
  .mesa { grid-template-columns: minmax(0, 1fr); }
  .lado { position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--linha); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
  nav.lista { max-height: 40vh; overflow-y: auto; }
  .ficha-area { padding-left: max(16px, env(safe-area-inset-left, 0px)); }
}
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; } }
</style>

<div class="mesa">
  <aside class="lado">
    <p class="marca">Memória do Editor de Impressão</p>
    <p class="marca-sub" id="sub">por assunto · o plano manda</p>
    <div class="busca">
      <label for="campo-busca">Procurar em toda a memória</label>
      <input id="campo-busca" type="search" placeholder="ex.: borda preta, Pesel 21, g7" autocomplete="off">
    </div>
    <nav class="lista" id="lista" aria-label="Fichas"></nav>
  </aside>
  <main class="ficha-area">
    <div class="caminho" id="caminho"></div>
    <article class="ficha" id="ficha"><p>Carregando a memória...</p></article>
  </main>
</div>

<script type="application/json" id="dados">__DADOS__</script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.1.6/dist/purify.min.js"></script>
<script>
(function () {
  const DADOS = JSON.parse(document.getElementById("dados").textContent);
  const TEXTOS = DADOS.textos;
  const CAMINHOS = Object.keys(TEXTOS);
  const GRUPOS = [
    ["Comece aqui", c => !c.includes("/") && ["INDICE.md", "LINHA-DO-TEMPO.md"].includes(c)],
    ["Itens do plano", c => c.startsWith("itens/")],
    ["Atravessam tudo", c => !c.includes("/") && !["INDICE.md", "LINHA-DO-TEMPO.md", "ONDE-PAREI.md"].includes(c)],
    ["Geral", c => c.startsWith("geral/")],
    ["Páginas de teste", c => c.startsWith("paginas-de-teste/")],
    ["Livros", c => c.startsWith("livros/")],
    ["Referências de fora", c => c.startsWith("referencias/")],
    ["Outros", c => c.startsWith("recados/") || c === "ONDE-PAREI.md"],
  ];
  const elFicha = document.getElementById("ficha");
  const elCaminho = document.getElementById("caminho");
  const elLista = document.getElementById("lista");
  const elBusca = document.getElementById("campo-busca");
  document.getElementById("sub").textContent =
    CAMINHOS.length + " arquivos · montada em " + DADOS.montada_em + " · o plano manda";

  function titulo(caminho) {
    const m = (TEXTOS[caminho] || "").match(/^#\s+(.+)$/m);
    let t = m ? m[1] : caminho;
    t = t.replace(/[*_`]/g, "");
    return t.length > 70 ? t.slice(0, 68) + "…" : t;
  }
  function rotulo(caminho) {
    if (caminho.startsWith("itens/")) return titulo(caminho);
    if (caminho.startsWith("paginas-de-teste/") || caminho.startsWith("livros/")) return titulo(caminho);
    return caminho.replace(/\.md$/, "").split("/").pop();
  }

  // Lista à esquerda
  const abertos = new Set(["Comece aqui", "Itens do plano", "Atravessam tudo", "Geral"]);
  for (const [nome, filtro] of GRUPOS) {
    const membros = CAMINHOS.filter(filtro);
    if (!membros.length) continue;
    const det = document.createElement("details");
    det.open = abertos.has(nome);
    const sum = document.createElement("summary");
    sum.textContent = nome + " (" + membros.length + ")";
    det.appendChild(sum);
    const ul = document.createElement("ul");
    for (const c of membros) {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = "#" + paraAncora(c);
      a.dataset.caminho = c;
      a.textContent = rotulo(c);
      li.appendChild(a);
      ul.appendChild(li);
    }
    det.appendChild(ul);
    elLista.appendChild(det);
  }

  // A âncora só aceita letras, números, ponto, _ ~ e -: a barra vira "~".
  function paraAncora(caminho) { return caminho.replace(/\//g, "~"); }
  function deAncora(ancora) { return decodeURIComponent(ancora).replace(/~/g, "/"); }

  function resolver(base, alvo) {
    const partes = base.split("/"); partes.pop();
    for (const p of alvo.split("/")) {
      if (p === "" || p === ".") continue;
      if (p === "..") { if (partes.length && partes[partes.length - 1] !== "..") partes.pop(); else partes.push(".."); }
      else partes.push(p);
    }
    return partes.join("/");
  }
  function linkDoGitHub(caminhoNoRepositorio) {
    const tipo = caminhoNoRepositorio.endsWith("/") ? "tree" : "blob";
    return DADOS.repositorio + "/" + tipo + "/" + DADOS.ramo + "/" + caminhoNoRepositorio.split("/").map(encodeURIComponent).join("/").replace(/%2F/g, "/");
  }

  function arrumarLinks(container, base) {
    container.querySelectorAll("a[href]").forEach(a => {
      const href = a.getAttribute("href");
      if (/^(https?:|mailto:)/i.test(href)) { a.target = "_blank"; a.rel = "noopener"; return; }
      if (href.startsWith("#")) { a.removeAttribute("href"); return; }
      const semAncora = decodeURIComponent(href.split("#")[0]);
      let alvo = resolver(base, semAncora);
      if (alvo.startsWith("../")) {
        let fora = alvo; while (fora.startsWith("../")) fora = fora.slice(3);
        a.href = linkDoGitHub(fora + (semAncora.endsWith("/") ? "/" : ""));
        a.target = "_blank"; a.rel = "noopener"; a.title = "Abre no GitHub (ramo " + DADOS.ramo + ")";
        return;
      }
      if (semAncora.endsWith("/") || (!alvo.endsWith(".md") && CAMINHOS.some(c => c.startsWith(alvo + "/")))) {
        a.href = "#" + paraAncora(alvo.replace(/\/$/, "") + "/");
        return;
      }
      if (TEXTOS[alvo] !== undefined) { a.href = "#" + paraAncora(alvo); return; }
      a.href = linkDoGitHub("memoria/" + alvo);
      a.target = "_blank"; a.rel = "noopener";
    });
    container.querySelectorAll("table").forEach(t => {
      if (t.parentElement.classList.contains("tabela")) return;
      const caixa = document.createElement("div"); caixa.className = "tabela";
      t.replaceWith(caixa); caixa.appendChild(t);
    });
  }

  function marcarNaLista(caminho) {
    elLista.querySelectorAll("a").forEach(a => {
      if (a.dataset.caminho === caminho) {
        a.setAttribute("aria-current", "page");
        const det = a.closest("details"); if (det) det.open = true;
      } else a.removeAttribute("aria-current");
    });
  }

  function mostrarPasta(pasta) {
    const membros = CAMINHOS.filter(c => c.startsWith(pasta));
    elCaminho.textContent = "memoria/" + pasta;
    elFicha.innerHTML = "<h1></h1><div class='pasta'><ul></ul></div>";
    elFicha.querySelector("h1").textContent = "Pasta " + pasta;
    const ul = elFicha.querySelector("ul");
    for (const c of membros) {
      const li = document.createElement("li"); const a = document.createElement("a");
      a.href = "#" + paraAncora(c); a.textContent = rotulo(c); li.appendChild(a); ul.appendChild(li);
    }
    marcarNaLista(null);
  }

  function mostrar(caminho) {
    if (caminho.endsWith("/")) return mostrarPasta(caminho);
    if (TEXTOS[caminho] === undefined) caminho = "INDICE.md";
    elCaminho.textContent = "memoria/" + caminho;
    const html = window.marked ? marked.parse(TEXTOS[caminho], { gfm: true }) : "<pre>" + TEXTOS[caminho].replace(/[<&]/g, s => s === "<" ? "&lt;" : "&amp;") + "</pre>";
    elFicha.innerHTML = window.DOMPurify ? DOMPurify.sanitize(html) : html;
    arrumarLinks(elFicha, caminho);
    marcarNaLista(caminho);
    window.scrollTo(0, 0);
  }

  // Busca: sem diferença de acento nem de maiúscula.
  function semAcento(s) { return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  const INDICE_BUSCA = CAMINHOS.map(c => [c, semAcento(TEXTOS[c])]);
  function escapar(s) { return s.replace(/[&<>"]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch])); }
  function buscar(termo) {
    const t = semAcento(termo.trim());
    if (t.length < 2) { mostrar(deAncora(location.hash.slice(1)) || "INDICE.md"); return; }
    const palavras = t.split(/\s+/).filter(Boolean);
    const achados = [];
    for (const [c, texto] of INDICE_BUSCA) {
      if (!palavras.every(p => texto.includes(p))) continue;
      let pontos = 0; for (const p of palavras) pontos += texto.split(p).length - 1;
      if (semAcento(c).includes(palavras[0])) pontos += 50;
      if (semAcento(titulo(c)).includes(palavras[0])) pontos += 30;
      const pos = texto.indexOf(palavras[0]);
      const original = TEXTOS[c];
      const trecho = original.slice(Math.max(0, pos - 70), pos + 150).replace(/\s+/g, " ");
      achados.push([pontos, c, trecho]);
    }
    achados.sort((a, b) => b[0] - a[0]);
    elCaminho.textContent = "busca";
    const partes = ["<h1>" + achados.length + " arquivo" + (achados.length === 1 ? "" : "s") + " com “" + escapar(termo.trim()) + "”</h1>"];
    if (!achados.length) partes.push("<p class='aviso'>Nada achado. Tente outra palavra (a busca ignora acentos).</p>");
    partes.push("<div class='resultados'>");
    for (const [, c, trecho] of achados.slice(0, 80)) {
      let tr = escapar(trecho);
      for (const p of palavras) {
        const re = new RegExp("(" + p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
        tr = tr.replace(re, "<mark>$1</mark>");
      }
      partes.push("<div class='resultado'><a href='#" + paraAncora(c) + "'>" + escapar(titulo(c)) + "</a> <span class='aviso'>" + escapar(c) + "</span><div class='trecho'>…" + tr + "…</div></div>");
    }
    partes.push("</div>");
    elFicha.innerHTML = partes.join("");
    marcarNaLista(null);
  }
  let espera = null;
  elBusca.addEventListener("input", () => { clearTimeout(espera); espera = setTimeout(() => buscar(elBusca.value), 150); });

  function rota() { elBusca.value = ""; mostrar(deAncora(location.hash.slice(1)) || "INDICE.md"); }
  window.addEventListener("hashchange", rota);
  rota();
})();
</script>
"""

if __name__ == "__main__":
    raise SystemExit(main())
