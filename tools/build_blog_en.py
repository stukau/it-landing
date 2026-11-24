#!/usr/bin/env python3
"""Build the English blog under /en/blog/ from translations in tools/blog_en/.

Each tools/blog_en/<slug>.html holds the English title, description, CTA and body of the
Russian article blog/<slug>/index.html. Run from the repo root:

    python3 tools/build_blog_en.py && python3 tools/build_en.py && python3 tools/build_llms.py
"""
import html
import json
import re

from build_en import (BASE, BLOG_CSS_V, CSS_V, FOOT, ORG, POSTS_EN, TAGS_EN, TODAY,
                      crumbs, head, hreflang, rd, wr)

MONTHS = {"января": "January", "февраля": "February", "марта": "March", "апреля": "April", "мая": "May",
          "июня": "June", "июля": "July", "августа": "August", "сентября": "September",
          "октября": "October", "ноября": "November", "декабря": "December"}
TAG2SERVICE = {"AI-агенты": "ai-agenty", "Автоматизация": "ai-agenty", "CRM": "crm-i-avtomatizaciya",
               "Telegram-боты": "telegram-boty", "Аналитика": "analitika-i-dashbordy",
               "Сайты": "razrabotka-saytov", "Приложения": "mobilnye-prilozheniya"}
CYR = re.compile(r"[Ѐ-ӿ]")
e = lambda t: html.escape(t, quote=False)


def ru_posts():
    """Russian posts in blog-index order: (slug, tag)."""
    b = rd("blog/index.html")
    return re.findall(r'<a class="post-card" href="([^"]+)/" data-tag="([^"]+)">', b)


def localize_links(body):
    def fix(m):
        href = m.group(1)
        if href.startswith("/") and not href.startswith("/en/"):
            href = "/en" + href
        return 'href="%s"' % href
    return re.sub(r'href="([^"]*)"', fix, body)


def counts(t):
    return {k: len(re.findall(k, t)) for k in ("<p>", "<h2>", "<h3>", "<li>", "<a ")}


def service_h1(slug):
    h = rd(f"en/services/{slug}/index.html")
    return re.search(r"<h1>(.*?)</h1>", h, flags=re.S).group(1).strip()


def main():
    posts = ru_posts()
    missing = [s for s, _ in posts if s not in POSTS_EN]
    assert not missing, "no translation for: %s" % missing
    by_tag = {}
    for slug, tag in posts:
        by_tag.setdefault(tag, []).append(slug)

    cards = []
    for slug, tag in posts:
        fr = POSTS_EN[slug]
        ru = rd(f"blog/{slug}/index.html")
        for k in ("title", "description", "cta_title", "cta_text", "body"):
            assert not CYR.search(fr[k]), (slug, k, CYR.search(fr[k]).group(0))
        ru_body = ru[ru.index('<main class="article">'):ru.index("</main>")]
        assert counts(ru_body) == counts(fr["body"]), (slug, counts(ru_body), counts(fr["body"]))
        assert sorted(re.findall(r'href="([^"]*)"', ru_body)) == sorted(re.findall(r'href="([^"]*)"', fr["body"])), slug

        m = re.search(r'<div class="post-meta"><span class="tag">[^<]+</span>(\d+) (\S+) (\d{4}) · (\d+) ', ru)
        date = f"{MONTHS[m.group(2)]} {int(m.group(1))}, {m.group(3)}"
        meta = f"{date} · {m.group(4)} min read"
        g = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', ru, flags=re.S).group(1))["@graph"]
        published = next(n for n in g if n["@type"] == "BlogPosting")["datePublished"]

        path = f"/blog/{slug}/"
        url = BASE + "/en" + path
        tag_en = TAGS_EN[tag]
        graph = [
            {"@type": "BlogPosting", "headline": fr["title"], "description": fr["description"], "url": url,
             "datePublished": published, "dateModified": published, "inLanguage": "en", "mainEntityOfPage": url,
             "image": BASE + "/og-image-en.png", "articleSection": tag_en, "author": ORG,
             "publisher": dict(ORG, logo={"@type": "ImageObject", "url": BASE + "/favicon-192.png"}),
             "translationOfWork": {"@type": "BlogPosting", "url": BASE + path, "inLanguage": "ru"}},
            crumbs([("Home", BASE + "/en/"), ("Blog", BASE + "/en/blog/"), (fr["title"], url)]),
        ]
        peers = by_tag[tag]
        i = peers.index(slug)
        rel = [peers[(i + k) % len(peers)] for k in range(1, min(5, len(peers)))]
        svc = TAG2SERVICE[tag]
        page = head(fr["title"] + " — AiKrok Blog", fr["description"], path, graph, fr["title"])
        page = page.replace('og:type" content="website"', 'og:type" content="article"')
        page += f"""
<div class="article-header">
    <div class="breadcrumbs"><a href="/en/">Home</a> / <a href="/en/blog/">Blog</a> / {tag_en}</div>
    <h1>{e(fr['title'])}</h1>
    <div class="post-meta"><span class="tag">{tag_en}</span>{meta}</div>
</div>

<main class="article">
{localize_links(fr['body'])}
</main>

<aside class="article-related">
    <h2>Read next</h2>
    <ul>
{chr(10).join('        <li><a href="/en/blog/' + r + '/">' + e(POSTS_EN[r]['title']) + '</a></li>' for r in rel)}
    </ul>
    <p class="article-related-service">Related service: <a href="/en/services/{svc}/">{service_h1(svc)}</a></p>
</aside>

<div class="article-cta">
    <h2>{e(fr['cta_title'])}</h2>
    <p>{e(fr['cta_text'])}</p>
    <a href="/en/#contact" class="btn btn-primary btn-lg">Discuss a project</a>
</div>
""" + FOOT
        assert not CYR.search(page), slug
        wr(f"en/blog/{slug}/index.html", page)
        cards.append(f"""    <a class="post-card" href="/en/blog/{slug}/" data-tag="{tag_en}">
        <h2>{e(fr['title'])}</h2>
        <p>{e(fr['description'])}</p>
        <div class="post-meta"><span class="tag">{tag_en}</span>{meta}</div>
    </a>""")

        # Russian article: hreflang + RU/EN switch (idempotent)
        if 'hreflang="en"' not in ru:
            canon = f'<link rel="canonical" href="{BASE}{path}">'
            assert canon in ru, slug
            ru = ru.replace(canon, canon + "\n    " + hreflang(BASE + path, url), 1)
            ru = ru.replace('        <div class="header-right">\n', f"""        <div class="header-right">
            <div class="lang-switcher">
                <a class="lang-btn active" href="{path}" hreflang="ru">RU</a>
                <a class="lang-btn" href="/en{path}" hreflang="en">EN</a>
            </div>
""", 1)
            wr(f"blog/{slug}/index.html", ru)

    # English blog index
    order = []
    for _, tag in posts:
        if TAGS_EN[tag] not in order:
            order.append(TAGS_EN[tag])
    filters = "\n".join(f'    <button class="blog-tag" data-filter="{t}" type="button">{t}</button>' for t in
                        ["AI Agents", "Automation", "Telegram Bots", "CRM", "Analytics", "Websites", "Apps"] if t in order)
    url = BASE + "/en/blog/"
    desc = "Practical articles on business automation: AI agents, Telegram bots, CRM and analytics — with examples, architecture and payback estimates."
    graph = [{"@type": "Blog", "name": "AiKrok Blog", "url": url, "description": desc, "inLanguage": "en", "publisher": ORG},
             crumbs([("Home", BASE + "/en/"), ("Blog", url)])]
    wr("en/blog/index.html", head("AiKrok Blog — Business Automation, AI Agents, Telegram Bots", desc, "/blog/", graph, "AiKrok Blog") + f"""
<section class="blog-hero">
    <div class="container">
        <h1>Blog</h1>
        <p>Business automation in practice: AI agents, bots, integrations — no marketing fluff</p>
    </div>
</section>

<div class="blog-tags" role="tablist">
    <button class="blog-tag is-active" data-filter="all" type="button">All</button>
{filters}
</div>

<main class="post-list">
{chr(10).join(cards)}
</main>
""" + FOOT.replace("</body>", """<script>
document.querySelectorAll('.blog-tag').forEach(function (btn) {
    btn.addEventListener('click', function () {
        var f = btn.dataset.filter;
        document.querySelectorAll('.blog-tag').forEach(function (b) { b.classList.toggle('is-active', b === btn); });
        document.querySelectorAll('.post-card').forEach(function (c) { c.hidden = f !== 'all' && c.dataset.tag !== f; });
    });
});
</script>

</body>"""))

    # Russian blog index: hreflang + switch
    b = rd("blog/index.html")
    if 'hreflang="en"' not in b:
        canon = f'<link rel="canonical" href="{BASE}/blog/">'
        assert canon in b
        b = b.replace(canon, canon + "\n    " + hreflang(BASE + "/blog/", url), 1)
        b = b.replace('        <div class="header-right">\n', """        <div class="header-right">
            <div class="lang-switcher">
                <a class="lang-btn active" href="/blog/" hreflang="ru">RU</a>
                <a class="lang-btn" href="/en/blog/" hreflang="en">EN</a>
            </div>
""", 1)
        wr("blog/index.html", b)

    # sitemap
    sm = rd("sitemap.xml")
    if "/en/blog/" not in sm:
        urls = ["/en/blog/"] + [f"/en/blog/{s}/" for s, _ in posts]
        add = "".join(f"""    <url>
        <loc>{BASE}{u}</loc>
        <lastmod>{TODAY}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>{'0.8' if u == '/en/blog/' else '0.7'}</priority>
    </url>
""" for u in urls)
        wr("sitemap.xml", sm.replace("</urlset>", add + "</urlset>", 1))
    print("en blog ok:", len(posts), "posts")


if __name__ == "__main__":
    main()
