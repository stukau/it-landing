#!/usr/bin/env python3
"""Build llms.txt (index for AI assistants) and llms-full.txt (full text of key pages).

Run from the repo root after changing service pages, the home FAQ or the blog list:

    python3 tools/build_llms.py
"""
import html
import json
import os
import re

from build_en import POSTS_EN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://aikrok.com"
SLUGS = ["razrabotka-saytov", "telegram-boty", "mobilnye-prilozheniya",
         "crm-i-avtomatizaciya", "analitika-i-dashbordy", "ai-agenty"]


def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def wr(p, s):
    open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)


def meta(h, name):
    return html.unescape(re.search(r'<meta name="%s" content="([^"]*)"' % name, h).group(1))


def h1(h):
    return html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", h, flags=re.S).group(1))).strip()


def to_md(fragment):
    """Very small HTML -> Markdown converter for the article markup used on this site."""
    t = fragment
    t = re.sub(r'<p><a [^>]*class="btn[^>]*>.*?</a></p>', "", t, flags=re.S)
    t = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>',
               lambda m: "[%s](%s)" % (m.group(2), m.group(1) if m.group(1).startswith("http") else BASE + m.group(1)), t, flags=re.S)
    t = re.sub(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", r"**\1**\n\2\n", t, flags=re.S)
    t = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n### \1\n", t, flags=re.S)
    t = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n#### \1\n", t, flags=re.S)
    t = re.sub(r"</?strong>", "**", t)
    t = re.sub(r"<li>(.*?)</li>", r"- \1", t, flags=re.S)
    t = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = "\n".join(l.strip() for l in t.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def service(path):
    h = rd(path.strip("/") + "/index.html")
    body = h[h.index('<main class="article">'):h.index("</main>")]
    return h1(h), meta(h, "description"), to_md(body)


def home_faq(path):
    h = rd(path)
    g = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', h, flags=re.S).group(1))["@graph"]
    faq = next(n for n in g if n["@type"] == "FAQPage")["mainEntity"]
    apps = [n for n in g if n["@type"] in ("SoftwareApplication", "WebApplication")]
    return faq, apps


def blog_posts():
    b = rd("blog/index.html")
    out = []
    for m in re.finditer(r'<a class="post-card" href="([^"]+)/" data-tag="([^"]+)">(.*?)</a>', b, flags=re.S):
        title = html.unescape(re.search(r"<h2>(.*?)</h2>", m.group(3), flags=re.S).group(1).strip())
        desc = html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<p>(.*?)</p>", m.group(3), flags=re.S).group(1)).strip())
        out.append((m.group(1), m.group(2), title, desc))
    return out


ru = [(s,) + service(f"/services/{s}/") for s in SLUGS]
en = [(s,) + service(f"/en/services/{s}/") for s in SLUGS]
faq_ru, apps_ru = home_faq("index.html")
faq_en, apps_en = home_faq("en/index.html")
posts = blog_posts()

# ------------------------------------------------------------------ llms.txt
L = []
L.append("# AiKrok")
L.append("")
L.append("> AiKrok — команда разработки IT-решений для малого и среднего бизнеса: сайты, Telegram-боты и Mini Apps, "
         "мобильные приложения (iOS, Android), AI-агенты и автоматизация процессов, внедрение CRM, аналитика и дашборды. "
         "Вникают в бизнес-задачу и запускают первую рабочую версию (MVP) за 2 недели.")
L.append("")
L.append("AiKrok is a development team building IT solutions for small and medium businesses: websites, Telegram bots and "
         "Mini Apps, iOS/Android apps, AI agents and process automation, CRM implementation, analytics and dashboards. "
         "First working version (MVP) in 2 weeks.")
L.append("")
L.append("Ключевые факты / Key facts:")
L.append("")
L.append("- Сайт / Website: https://aikrok.com/ (русский), https://aikrok.com/en/ (English)")
L.append("- Контакты / Contact: info@aikrok.com, Telegram https://t.me/yuri_admin")
L.append("- Языки работы / Working languages: русский, English, español, français")
L.append("- Сроки / Timeline: первая рабочая версия (MVP) за 2 недели; далее развитие этапами")
L.append("- Ориентиры цен на Telegram-ботов / Indicative Telegram bot prices: информационный бот $200–600; "
         "бот с данными и сценариями $800–3 000; с интеграциями и платежами $2 500–8 000; бот с ИИ от $3 000")
L.append("- Консультация и оценка задачи бесплатны / Consultation and estimate are free")
L.append("- Полный текст ключевых страниц / Full text of key pages: https://aikrok.com/llms-full.txt")
L.append("")
L.append("## Услуги")
L.append("")
for s, title, desc, _ in ru:
    L.append(f"- [{title}]({BASE}/services/{s}/): {desc}")
L.append("")
L.append("## Services (English)")
L.append("")
for s, title, desc, _ in en:
    L.append(f"- [{title}]({BASE}/en/services/{s}/): {desc}")
L.append("")
L.append("## Примеры работ / Portfolio")
L.append("")
for a in apps_ru:
    L.append(f"- [{a['name']}]({a['url']}): {a['description']}")
L.append("")
L.append("## Основные страницы")
L.append("")
L.append(f"- [Главная]({BASE}/): услуги, примеры работ, процесс, частые вопросы, контакты")
L.append(f"- [Услуги]({BASE}/services/): все шесть направлений")
L.append(f"- [Home (English)]({BASE}/en/): services, portfolio, process, FAQ, contact")
if POSTS_EN:
    L.append(f"- [Blog (English)]({BASE}/en/blog/): the same articles in English")
L.append(f"- [Блог]({BASE}/blog/): {len(posts)} практических статей об автоматизации бизнеса, AI-агентах, Telegram-ботах, CRM и аналитике")
L.append("")
L.append("## Блог")
L.append("")
for slug, tag, title, desc in posts:
    L.append(f"- [{title}]({BASE}/blog/{slug}/): {desc}")
L.append("")
if all(slug in POSTS_EN for slug, _, _, _ in posts):
    L.append("## Blog (English)")
    L.append("")
    for slug, tag, title, desc in posts:
        L.append(f"- [{POSTS_EN[slug]['title']}]({BASE}/en/blog/{slug}/): {POSTS_EN[slug]['description']}")
    L.append("")
wr("llms.txt", "\n".join(L))

# ------------------------------------------------------------------ llms-full.txt
F = []
F.append("# AiKrok — полный текст ключевых страниц / full text of key pages")
F.append("")
F.append("> Источник: https://aikrok.com/. Этот файл собран из страниц сайта для ИИ-ассистентов и поисковых систем. "
         "Контакты: info@aikrok.com, Telegram https://t.me/yuri_admin.")
F.append("")
F.append("## Частые вопросы")
F.append("")
for q in faq_ru:
    F.append(f"**{q['name']}**")
    F.append(q["acceptedAnswer"]["text"])
    F.append("")
F.append("## Примеры работ")
F.append("")
for a in apps_ru:
    F.append(f"- **{a['name']}** ({a['url']}): {a['description']}")
F.append("")
for s, title, desc, body in ru:
    F.append(f"## {title}")
    F.append("")
    F.append(f"URL: {BASE}/services/{s}/")
    F.append("")
    F.append(body)
    F.append("")
F.append("---")
F.append("")
F.append("# AiKrok in English")
F.append("")
F.append("## Frequently asked questions")
F.append("")
for q in faq_en:
    F.append(f"**{q['name']}**")
    F.append(q["acceptedAnswer"]["text"])
    F.append("")
F.append("## Portfolio")
F.append("")
for a in apps_en:
    F.append(f"- **{a['name']}** ({a['url']}): {a['description']}")
F.append("")
for s, title, desc, body in en:
    F.append(f"## {title}")
    F.append("")
    F.append(f"URL: {BASE}/en/services/{s}/")
    F.append("")
    F.append(body)
    F.append("")
wr("llms-full.txt", "\n".join(F))
print("llms ok:", len("\n".join(L)), "/", len("\n".join(F)), "chars;", len(posts), "posts")
