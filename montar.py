#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta o blog da Scale Sales em HTML estatico.

  python3 montar.py            # remonta todos os artigos de fonte/ e o indice
  python3 montar.py <arquivo>  # monta um artigo so (e refaz o indice)

Cada artigo e um .md em fonte/ com cabecalho de metadados:

    ---
    titulo: ...
    resumo: ...            (uma frase; vira a meta description)
    secao: Inteligencia Artificial
    data: 2026-10-22
    slug: meu-artigo
    capa: img/abertura/kC.webp     (opcional, relativo a raiz do site)
    fontes: Nome|url · Nome|url    (opcional, vira a lista de fontes no pe)
    ---
    corpo em markdown

Markdown aceito: ##, ###, paragrafo, - lista, 1. lista, > citacao
(com "-- autor" na ultima linha), **negrito**, *italico*, [texto](url),
:::nota ... ::: e :::marcos ... ::: (lista numerada em cartoes).
"""
import io, os, re, sys, html, json, datetime

AQUI  = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.join(AQUI, "fonte")
SITE  = "https://scalesales.com.br"
BASE  = "/blog"            # onde o blog mora no servidor
ASSET = "/novo"            # onde moram as imagens do site
DIAG  = "https://scalesales.com.br/leadflow/diagnostico-scale-v2/"

MESES = ["janeiro","fevereiro","março","abril","maio","junho","julho",
         "agosto","setembro","outubro","novembro","dezembro"]


# ---------------------------------------------------------------- markdown
def em_linha(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" rel="noopener">\1</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', t)
    return t


def corpo_html(txt):
    saida, linhas, i = [], txt.split("\n"), 0
    while i < len(linhas):
        ln = linhas[i].rstrip()

        if not ln.strip():
            i += 1; continue

        if ln.startswith(":::"):                       # blocos especiais
            tipo = ln[3:].strip() or "nota"
            bloco, i = [], i + 1
            while i < len(linhas) and not linhas[i].startswith(":::"):
                bloco.append(linhas[i]); i += 1
            i += 1
            itens = [b.strip() for b in bloco if b.strip()]
            if tipo == "marcos":
                li = "".join('<li><i>%02d</i><span>%s</span></li>' % (n + 1, em_linha(re.sub(r'^[-*]\s*', '', x)))
                             for n, x in enumerate(itens))
                saida.append('<ul class="lista-marco">%s</ul>' % li)
            else:
                saida.append('<div class="nota">%s</div>' %
                             "".join('<p>%s</p>' % em_linha(x) for x in itens))
            continue

        if ln.startswith("### "):
            saida.append("<h3>%s</h3>" % em_linha(ln[4:])); i += 1; continue
        if ln.startswith("## "):
            saida.append("<h2>%s</h2>" % em_linha(ln[3:])); i += 1; continue

        if ln.startswith("> "):
            bloco = []
            while i < len(linhas) and linhas[i].startswith("> "):
                bloco.append(linhas[i][2:].rstrip()); i += 1
            autor = ""
            if bloco and bloco[-1].startswith("-- "):
                autor = "<cite>%s</cite>" % em_linha(bloco.pop()[3:])
            saida.append("<blockquote>%s%s</blockquote>" %
                         (em_linha(" ".join(bloco)), autor))
            continue

        if re.match(r'^[-*] ', ln):
            bloco = []
            while i < len(linhas) and re.match(r'^[-*] ', linhas[i]):
                bloco.append(linhas[i][2:].rstrip()); i += 1
            saida.append("<ul>%s</ul>" % "".join("<li>%s</li>" % em_linha(x) for x in bloco))
            continue

        if re.match(r'^\d+\. ', ln):
            bloco = []
            while i < len(linhas) and re.match(r'^\d+\. ', linhas[i]):
                bloco.append(re.sub(r'^\d+\.\s*', '', linhas[i]).rstrip()); i += 1
            saida.append("<ol>%s</ol>" % "".join("<li>%s</li>" % em_linha(x) for x in bloco))
            continue

        bloco = []
        while i < len(linhas) and linhas[i].strip() and not re.match(r'^(#{2,3} |[-*] |\d+\. |> |:::)', linhas[i]):
            bloco.append(linhas[i].rstrip()); i += 1
        saida.append("<p>%s</p>" % em_linha(" ".join(bloco)))
    return "\n".join(saida)


def ler(caminho):
    t = io.open(caminho, encoding="utf-8").read()
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', t, re.S)
    if not m:
        sys.exit("ERRO: %s nao tem cabecalho ---" % caminho)
    meta = {}
    for ln in m.group(1).split("\n"):
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip()
    for campo in ("titulo", "resumo", "secao", "data", "slug"):
        if not meta.get(campo):
            sys.exit("ERRO: %s sem '%s'" % (os.path.basename(caminho), campo))
    meta["corpo"] = m.group(2)
    return meta


def por_extenso(d):
    a = datetime.date(*[int(x) for x in d.split("-")])
    return "%d de %s de %d" % (a.day, MESES[a.month - 1], a.year)


def minutos(txt):
    return max(2, round(len(re.sub(r'<[^>]+>', '', txt).split()) / 220))


# ---------------------------------------------------------------- gabarito
TOPO = '''<div class="topo"><div class="w topo__i">
  <a href="{site}/"><img src="{a}/img/logo-footer.png" alt="Scale Sales" width="150" height="44" class="marca"></a>
  <a class="topo__c" href="{diag}">Diagn&oacute;stico gratuito</a>
</div></div>'''

RODAPE = '''<footer class="rodape"><div class="w rodape__i">
  <img src="{a}/img/logo-footer.png" alt="Scale Sales" width="140" height="41" class="marca">
  <span>Engenharia de Receita &middot; <a href="{site}/" style="color:inherit">scalesales.com.br</a></span>
</div></footer>'''

CONVITE = '''<div class="cx">
  <div>
    <h2>Descubra onde o seu dinheiro est&aacute; vazando.</h2>
    <p>Diagn&oacute;stico gratuito da sua opera&ccedil;&atilde;o comercial. Sem apresenta&ccedil;&atilde;o de produto.</p>
  </div>
  <a class="cta" href="{diag}">Quero o diagn&oacute;stico gratuito <i>&#8599;</i></a>
</div>'''

PAGINA = '''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titulo_tag}</title>
<meta name="description" content="{resumo}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="author" content="Alberto Castilo">
<meta name="theme-color" content="#120727">
<link rel="icon" href="{a}/img/favicon-scale.png" type="image/png">
<meta property="og:type" content="{ogtipo}">
<meta property="og:site_name" content="Scale Sales">
<meta property="og:locale" content="pt_BR">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{resumo}">
<meta property="og:image" content="{ogimg}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{titulo}">
<meta name="twitter:description" content="{resumo}">
<meta name="twitter:image" content="{ogimg}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{b}/estilo.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
{topo}
<main>
{conteudo}
</main>
{rodape}
</body>
</html>
'''


def pagina(**k):
    k.setdefault("ogtipo", "article")
    k["topo"]   = TOPO.format(site=SITE, a=ASSET, diag=DIAG)
    k["rodape"] = RODAPE.format(site=SITE, a=ASSET)
    k["a"], k["b"] = ASSET, BASE
    return PAGINA.format(**k)


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- artigo
def montar_artigo(meta):
    url    = "%s%s/%s/" % (SITE, BASE, meta["slug"])
    ogimg  = "%s%s/%s/capa.jpg" % (SITE, BASE, meta["slug"])
    if not os.path.exists(os.path.join(AQUI, meta["slug"], "capa.jpg")):
        ogimg = "%s%s/img/og-scale-escuderia.jpg" % (SITE, ASSET)
    corpo  = corpo_html(meta["corpo"])

    fontes = ""
    if meta.get("fontes"):
        itens = []
        for p in meta["fontes"].split("·"):
            p = p.strip()
            if "|" in p:
                n, u = p.split("|", 1)
                itens.append('<li><a href="%s" rel="noopener nofollow" target="_blank">%s</a></li>'
                             % (esc(u.strip()), esc(n.strip())))
        if itens:
            fontes = '<h2>Fontes</h2><ul>%s</ul>' % "".join(itens)

    capa = ""
    if meta.get("capa"):
        capa = ('<figure class="capa col"><img src="%s/%s" alt="%s" width="1408" height="768" '
                'fetchpriority="high"></figure>' % (ASSET, meta["capa"].lstrip("/"), esc(meta["titulo"])))

    ld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Article", "@id": url + "#artigo",
             "headline": meta["titulo"][:110], "description": meta["resumo"],
             "datePublished": meta["data"], "dateModified": meta["data"],
             "inLanguage": "pt-BR", "image": ogimg,
             "articleSection": meta["secao"],
             "mainEntityOfPage": {"@type": "WebPage", "@id": url},
             "author": {"@type": "Person", "name": "Alberto Castilo",
                        "jobTitle": "Fundador e CEO da Scale Sales",
                        "url": SITE + "/"},
             "publisher": {"@type": "Organization", "name": "Scale Sales",
                           "url": SITE + "/",
                           "logo": {"@type": "ImageObject",
                                    "url": SITE + ASSET + "/img/logo-footer.png"}}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Scale Sales", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + BASE + "/"},
                {"@type": "ListItem", "position": 3, "name": meta["titulo"], "item": url}]}
        ]}, ensure_ascii=False)

    conteudo = '''<header class="cab"><div class="col">
  <nav class="trilha"><a href="{site}/">Scale Sales</a> &middot; <a href="{b}/">Blog</a> &middot; {secao}</nav>
  <p class="olho">{secao}</p>
  <h1>{titulo}</h1>
  <p class="resumo">{resumo}</p>
  <div class="ficha">
    <img src="{a}/img/socios/beto.webp" alt="" width="40" height="40" loading="lazy">
    <span><b>Alberto Castilo</b> &middot; fundador da Scale Sales</span>
    <span>&middot;</span><time datetime="{data}">{data_txt}</time>
    <span>&middot;</span><span>{min} min de leitura</span>
  </div>
</div>{capa}</header>

<article><div class="col">
{corpo}
{fontes}
{convite}
<div class="autor">
  <img src="{a}/img/socios/beto.webp" alt="Alberto Castilo" width="62" height="62" loading="lazy">
  <div><b>Alberto Castilo</b><p>Fundador e CEO da Scale Sales. Vinte anos e mais de 120 opera&ccedil;&otilde;es
  construindo a estrutura comercial que aumenta o resultado de quem j&aacute; vende.</p></div>
</div>
</div></article>'''.format(site=SITE, a=ASSET, b=BASE, secao=esc(meta["secao"]),
                           titulo=esc(meta["titulo"]), resumo=esc(meta["resumo"]),
                           data=meta["data"], data_txt=por_extenso(meta["data"]),
                           min=minutos(corpo), capa=capa, corpo=corpo, fontes=fontes,
                           convite=CONVITE.format(diag=DIAG))

    titulo_tag = meta["titulo"]
    if len(titulo_tag) < 46:
        titulo_tag += " | Scale Sales"
    htm = pagina(titulo_tag=esc(titulo_tag), titulo=esc(meta["titulo"]),
                 resumo=esc(meta["resumo"]), url=url, ogimg=ogimg, ld=ld, conteudo=conteudo)

    destino = os.path.join(AQUI, meta["slug"])
    os.makedirs(destino, exist_ok=True)
    io.open(os.path.join(destino, "index.html"), "w", encoding="utf-8").write(htm)
    return url


# ---------------------------------------------------------------- indice
def montar_indice(metas):
    metas = sorted(metas, key=lambda m: m["data"], reverse=True)
    cartoes = "".join(
        '<a class="cartao" href="{b}/{slug}/"><p class="olho">{secao}</p>'
        '<h2>{titulo}</h2><p>{resumo}</p><span>{data}</span></a>'.format(
            b=BASE, slug=m["slug"], secao=esc(m["secao"]), titulo=esc(m["titulo"]),
            resumo=esc(m["resumo"]), data=por_extenso(m["data"]))
        for m in metas) or '<div class="vazio">Os primeiros artigos saem nos pr&oacute;ximos dias.</div>'

    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Blog",
        "@id": SITE + BASE + "/#blog", "name": "Blog da Scale Sales",
        "url": SITE + BASE + "/", "inLanguage": "pt-BR",
        "description": "Inteligência artificial, vendas e estruturação comercial, "
                       "lidos por quem opera.",
        "publisher": {"@type": "Organization", "name": "Scale Sales", "url": SITE + "/"},
        "blogPost": [{"@type": "BlogPosting", "headline": m["titulo"],
                      "url": "%s%s/%s/" % (SITE, BASE, m["slug"]),
                      "datePublished": m["data"]} for m in metas[:30]]
    }, ensure_ascii=False)

    conteudo = '''<header class="capa-blog"><div class="w">
  <p class="olho">Blog da Scale Sales</p>
  <h1>O que est&aacute; acontecendo na IA, lido por quem opera vendas.</h1>
  <p class="resumo" style="max-width:62ch">Todo dia a gente acompanha o que mudou no mundo da intelig&ecirc;ncia
  artificial e escreve o que isso significa, na pr&aacute;tica, para a opera&ccedil;&atilde;o comercial de uma
  empresa brasileira. Sem hype e sem futurologia.</p>
</div></header>
<div class="w"><div class="grade">{cartoes}</div>{convite}<div style="height:60px"></div></div>'''.format(
        cartoes=cartoes, convite=CONVITE.format(diag=DIAG))

    htm = pagina(titulo_tag="Blog da Scale Sales &middot; IA, vendas e opera&ccedil;&atilde;o comercial",
                 titulo="Blog da Scale Sales",
                 resumo="Intelig&ecirc;ncia artificial, vendas e estrutura&ccedil;&atilde;o comercial, "
                        "lidos por quem opera. Todo dia.",
                 url=SITE + BASE + "/",
                 ogimg=SITE + ASSET + "/img/og-scale-escuderia.jpg",
                 ld=ld, conteudo=conteudo, ogtipo="website")
    io.open(os.path.join(AQUI, "index.html"), "w", encoding="utf-8").write(htm)


def main():
    arquivos = sys.argv[1:] or sorted(
        os.path.join(FONTE, f) for f in os.listdir(FONTE) if f.endswith(".md"))
    metas = [ler(a) for a in arquivos]
    todos = {m["slug"]: m for m in metas}
    for f in sorted(os.listdir(FONTE)):            # o indice sempre ve tudo
        if f.endswith(".md"):
            m = ler(os.path.join(FONTE, f))
            todos.setdefault(m["slug"], m)
    for m in metas:
        print("artigo:", montar_artigo(m))
    montar_indice(list(todos.values()))
    print("indice: %s%s/ (%d artigos)" % (SITE, BASE, len(todos)))


if __name__ == "__main__":
    main()
