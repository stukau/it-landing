#!/usr/bin/env python3
"""Build the English version of the site under /en/.

Run from the repo root after editing index.html or i18n.js:

    python3 tools/build_en.py

- /en/index.html is generated from index.html + the `en` block of i18n.js
- /en/services/ pages are generated from the content below
- hreflang links and RU/EN switch links are added to the Russian pages (idempotent)

Then run tools/build_llms.py to refresh llms.txt and llms-full.txt.
"""
import html
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://aikrok.com"
TODAY = "2026-11-25"
CSS_V, BLOG_CSS_V, I18N_V = "15", "3", "9"
OG = BASE + "/og-image-en.png"


def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def wr(p, s):
    full = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(s)


def ld(graph):
    body = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=4)
    body = "\n".join("    " + l for l in body.split("\n"))
    return '<script type="application/ld+json">\n' + body + "\n    </script>"


def hreflang(ru, en):
    return (f'<link rel="alternate" hreflang="ru" href="{ru}">\n'
            f'    <link rel="alternate" hreflang="en" href="{en}">\n'
            f'    <link rel="alternate" hreflang="x-default" href="{en}">')


def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


ORG = {"@type": "Organization", "@id": BASE + "/#organization", "name": "AiKrok", "url": BASE + "/"}

TAGS_EN = {"AI-агенты": "AI Agents", "Автоматизация": "Automation", "CRM": "CRM", "Telegram-боты": "Telegram Bots",
           "Аналитика": "Analytics", "Сайты": "Websites", "Приложения": "Apps"}
FRAG_KEYS = ["title", "description", "cta_title", "cta_text", "body"]


def en_posts():
    """English blog translations from tools/blog_en/<slug>.html -> {slug: {title, description, ...}}."""
    d = os.path.join(ROOT, "tools", "blog_en")
    out = {}
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not f.endswith(".html"):
            continue
        t = open(os.path.join(d, f), encoding="utf-8").read()
        parts = re.split(r"<!--(%s)-->\n?" % "|".join(FRAG_KEYS), t)
        frag = {parts[i]: parts[i + 1].strip("\n") for i in range(1, len(parts) - 1, 2)}
        assert list(frag) == FRAG_KEYS, (f, list(frag))
        for k in FRAG_KEYS[:4]:
            frag[k] = frag[k].strip()
        out[f[:-5]] = frag
    return out


POSTS_EN = en_posts()

# ---------------------------------------------------------------- translations
js = rd("i18n.js")
js = js[:js.index("function setLanguage")]
_T = json.loads(subprocess.check_output(
    ["node", "-e", js + ";process.stdout.write(JSON.stringify({en: translations.en, ru: translations.ru}))"], text=True))
EN, RU = _T["en"], _T["ru"]

# Products from the portfolio, published as structured data so search engines and
# AI assistants can connect them to AiKrok. (i18n key, schema type, category, OS, url)
APPS = [
    ("p4", "SoftwareApplication", "FinanceApplication", "iOS", "https://apps.apple.com/ge/app/submap-subscription-tracker/id6767109129"),
    ("p7", "SoftwareApplication", "FinanceApplication", "iOS", "https://apps.apple.com/app/my-stash-budget-receipts/id6812665710"),
    ("p8", "SoftwareApplication", "GameApplication", "iOS", "https://apps.apple.com/app/echo-the-dark-is-listening/id6797635978"),
    ("p9", "SoftwareApplication", "GameApplication", "iOS", "https://apps.apple.com/app/petalstorm/id6770308644"),
    ("p10", "SoftwareApplication", "GameApplication", "iOS", "https://apps.apple.com/app/tochki/id6812648131"),
    ("p6", "WebApplication", "LifestyleApplication", "Telegram", "https://georgia-rent-search.fly.dev"),
    ("p5", "WebApplication", "BusinessApplication", "Web", "https://ai-visibility-seven-chi.vercel.app"),
    ("p2", "WebApplication", "FinanceApplication", "Telegram", "https://aitrxbot.com"),
]


def app_nodes(t, lang):
    return [{"@type": typ, "name": t[k + "_title"], "description": t[k + "_desc"], "url": url,
             "applicationCategory": cat, "operatingSystem": os_, "inLanguage": lang,
             "author": {"@id": BASE + "/#organization"}} for k, typ, cat, os_, url in APPS]

SERVICES = [
    dict(
        slug="razrabotka-saytov", short="Websites & Landing Pages", more="website development",
        h1="Website and Landing Page Development",
        title="Website & Landing Page Development for Business — AiKrok",
        desc="Landing pages, corporate websites and online stores for small and medium businesses: responsive, SEO-ready, with analytics and AI-search readiness. First version in 2 weeks.",
        lead="We build websites that do a job for the business: bring in leads, explain the product, and are easy for search engines and AI assistants to read. We start with a first working version and grow it as real data comes in.",
        what=[
            "<strong>Landing pages</strong> — one-pagers for a product launch, a service or an ad campaign.",
            "<strong>Corporate websites</strong> — services, case studies, blog, contacts, several languages.",
            "<strong>Online stores</strong> — catalog, cart, payments, order notifications.",
            "<strong>SEO foundation</strong> — page structure, meta tags, schema.org markup, sitemap and robots.txt.",
            "<strong>AI-search readiness</strong> — llms.txt and structured data so ChatGPT and other assistants read the site correctly.",
            "<strong>Analytics and forms</strong> — tracking, goals, leads delivered to a messenger or CRM.",
        ],
        fit=[
            "you need to test demand for a product or service quickly;",
            "the old website brings no leads and looks bad on a phone;",
            "the site is missing from search results and from AI assistants' answers;",
            "leads from the site get lost in a mailbox nobody reads.",
        ],
        price="The cost depends on the number of pages, language versions, design and integrations (payments, CRM, catalog). A landing page with a lead form usually fits into the first two-week version; corporate sites and stores are built in stages. You get an itemized estimate after a short, free discussion of the task.",
        cases=[
            ("AI Visibility Scanner", "a web service that scans a site, runs queries through an LLM and shows what AI assistants know about the business."),
            ("Corporate websites under NDA", "we will show and explain them during a consultation."),
        ],
        faq=[
            ("How long does it take to build a website?", "A landing page usually takes up to two weeks including copy and a lead form. A corporate site or an online store is built in stages: we launch a minimal working version first, then add sections and integrations."),
            ("Is SEO included?", "The technical foundation is: heading structure, meta tags, structured data, sitemap, robots.txt, responsive layout and loading speed. Ongoing promotion — articles, links, keyword work — is discussed separately."),
            ("Can the website be connected to a CRM and messengers?", "Yes. Form submissions can go straight to a CRM, a managers' Telegram chat or a spreadsheet, so they don't get lost in email."),
            ("What does preparing a site for AI search mean?", "A set of technical steps — llms.txt, schema.org markup, a robots.txt open to AI crawlers and clearly structured copy — so that ChatGPT and other assistants can read the site and mention the company in their answers."),
        ],
    ),
    dict(
        slug="telegram-boty", short="Telegram Bots & AI Assistants", more="Telegram bot development",
        h1="Telegram Bot and AI Assistant Development",
        title="Telegram Bot & Mini App Development for Business — AiKrok",
        desc="Custom Telegram bots: booking, sales, support, loyalty programs, Mini Apps and AI-powered bots. CRM and payment integrations. MVP in 2 weeks.",
        lead="We build bots around a specific business scenario — from a simple menu and booking to an AI assistant that understands a customer's question, answers from your company documents and creates a deal in your CRM.",
        what=[
            "<strong>Booking and scheduling</strong> — timetable, reminders, rescheduling and cancellation.",
            "<strong>Sales and support</strong> — answers to frequent questions, lead qualification, handover to a manager.",
            "<strong>AI-powered bots</strong> — understanding free text and answering from your knowledge base.",
            "<strong>Telegram Mini Apps</strong> — a full interface inside Telegram, no App Store or Google Play needed.",
            "<strong>Loyalty programs</strong> — bonuses, broadcasts, winning customers back.",
            "<strong>Internal bots</strong> — requests, approvals and reports for your team.",
            "<strong>Integrations</strong> — CRM, payments, spreadsheets, accounting systems.",
        ],
        fit=[
            "an administrator spends hours on bookings and reminder calls;",
            "leads arrive at night and on weekends and go unanswered;",
            "customers keep asking the same questions in a messenger;",
            "you need an app for customers, but releasing it in the stores is slow and expensive.",
        ],
        price="The price of a bot is defined by the level of the task. Our indicative ranges: an informational bot with a menu — about $200–600, a bot with data and scenarios — $800–3,000, a bot with integrations and payments — $2,500–8,000, an AI-powered bot — from $3,000. Running costs after launch are a server and, for AI bots, the language model. You get an estimate for your task after a free consultation.",
        cases=[
            ("Batumi Rent", "a Telegram Mini App for long-term rentals: a channel parser, an LLM that turns raw posts into structured listings, deduplication that merges repeats, and alerts for subscribers when new matches appear."),
            ("AI Trading Bot (aitrxbot.com)", "a Telegram bot with an AI assistant for market analysis and trading signals."),
        ],
        faq=[
            ("How much does a Telegram bot cost?", "Roughly from $200–600 for an informational bot with a menu to $3,000 and up for an AI-powered bot with integrations. The price depends on scenarios, integrations and how accurate the answers must be; you get an itemized estimate after we go through the task."),
            ("How fast can a bot be launched?", "The first version covering the main scenario usually launches in two weeks. Complex integrations and AI are added in the following stages."),
            ("How is a custom bot different from one made in a bot builder?", "A builder is fine for a simple menu and standard scenarios. Custom development is needed when you require integrations with your systems, non-standard logic, AI or a Mini App."),
            ("Bot, Mini App or mobile app — which one?", "If your customers already use Telegram and you need booking, a catalog or an account area, a Mini App is usually faster and cheaper than an app. A standalone app is justified when you need offline mode, access to device features or a presence in the stores."),
            ("Can the bot be connected to a CRM?", "Yes. The bot can create deals, update customer records and hand the conversation over to a manager together with the chat history."),
        ],
    ),
    dict(
        slug="mobilnye-prilozheniya", short="Mobile Applications", more="mobile app development",
        h1="Mobile App Development for iOS and Android",
        title="iOS & Android Mobile App Development — AiKrok",
        desc="Mobile apps for business: from an MVP that validates an idea to a finished product in the App Store. Account areas, catalogs, booking, AI features. First version in 2 weeks.",
        lead="We develop apps for iOS and Android — from a first version that tests an idea to a product in the store. Our team's own apps are published in the App Store, so we have gone from idea to review and release more than once.",
        what=[
            "<strong>MVP</strong> — a first version with one key feature done properly.",
            "<strong>Customer apps</strong> — account areas, catalogs, booking, delivery.",
            "<strong>AI features</strong> — receipt and screenshot recognition, voice input.",
            "<strong>On-device data</strong> — when it matters that data never leaves the phone.",
            "<strong>Monetization</strong> — subscriptions and in-app purchases.",
            "<strong>Publishing</strong> — preparing for review and releasing to the App Store and Google Play.",
        ],
        fit=[
            "you have a product idea and need to test it on real users;",
            "customers need an account area or booking always at hand;",
            "you need device features: camera, voice, notifications, offline work;",
            "it is unclear what pays off better — an app or a Telegram Mini App.",
        ],
        price="The cost depends on the number of platforms, screens, the backend and integrations. We suggest starting with an MVP — one key feature, real integrations and minimal analytics — and growing it based on results. You get an estimate after a free consultation.",
        cases=[
            ("SubMap", "an iOS app that keeps subscriptions under control: voice input, screenshot parsing, renewal reminders and spending analytics."),
            ("My Stash", "an iOS app for family finances: accounts in any currency, budgets with reminders, AI receipt scanning; all data stays on the device."),
            ("ECHO, Petalstorm and Tochki", "three iOS games in the App Store: a puzzle with generative sound, an arcade with Game Center and in-app purchases, and a two-player game over Bluetooth and Wi‑Fi with no internet."),
        ],
        faq=[
            ("What can you build in two weeks?", "A first version with one key feature done properly: a working scenario, error handling and minimal analytics. Extra sections and secondary features are deliberately left for later stages."),
            ("Do you build for both iOS and Android?", "Yes. Which platform to start with, and whether you need the second one right away, depends on your audience — we discuss it during the consultation."),
            ("An app or a Telegram Mini App?", "A Mini App is faster and cheaper if your customers already use Telegram. An app is justified when you need offline mode, the camera, voice input, push notifications outside the messenger or a presence in the stores."),
            ("Will you help with publishing in the stores?", "Yes. We prepare the materials, go through review and publish the app; after launch we stay in touch and ship updates."),
        ],
    ),
    dict(
        slug="crm-i-avtomatizaciya", short="CRM & Automation", more="CRM implementation",
        h1="CRM Implementation and Sales Automation",
        title="CRM Implementation & Sales Automation for Small Business — AiKrok",
        desc="CRM setup and implementation for small and medium businesses: sales funnels, messenger and telephony integrations, mailings, automatic reports. So that no lead is lost.",
        lead="We set up and implement a CRM so that the team actually uses it and the business stops losing leads and customers. We automate the routine around sales: funnels, reminders, mailings and reports.",
        what=[
            "<strong>Choosing a CRM</strong> — for your processes and team size, not just “the most popular one”.",
            "<strong>Sales funnels</strong> — stages, tasks and reminders without manual control.",
            "<strong>Messenger integration</strong> — every conversation in one customer record.",
            "<strong>Telephony</strong> — calls and recordings in the deal record.",
            "<strong>Mailings</strong> — segments, sequences, winning customers back.",
            "<strong>Automatic reports</strong> — a daily summary for the owner, for example in Telegram.",
            "<strong>AI in CRM</strong> — automatic tags from conversations, call summaries.",
        ],
        fit=[
            "leads are tracked in spreadsheets and chats, and some of them get lost;",
            "you bought a CRM, but managers don't fill it in;",
            "it is unclear at which stage deals fall through;",
            "the owner assembles a report by hand from several systems.",
        ],
        price="The cost of implementation depends on the system chosen, the number of users, the number of integrations and the state of the data to be migrated. We start with one process — usually incoming leads — and expand step by step. You get an itemized estimate after a free review.",
        cases=[
            ("CRM implementations under NDA", "we will show and explain them during a consultation."),
        ],
        faq=[
            ("Where does a CRM implementation start?", "With a review of the current process: where leads come from, who handles them and how, and where they get lost. Only then do we choose a system and set up the funnel."),
            ("Why doesn't the team use the CRM, and what can be done?", "Most often because the system adds work instead of removing it. What helps: deals created automatically from messengers and calls, a minimum of required fields, and training the team on real scenarios."),
            ("Can a CRM be connected to Telegram and WhatsApp?", "Yes. Messenger conversations land in the customer record, and the manager replies from a single window."),
            ("Does a very small team need a CRM?", "If there are a few leads a day handled by one person, a spreadsheet and a bot may be enough. A CRM pays off when leads grow, several managers appear or you need to see the whole funnel."),
        ],
    ),
    dict(
        slug="analitika-i-dashbordy", short="Analytics & Dashboards", more="analytics and dashboards",
        h1="Data Analytics and Dashboards for Business",
        title="Data Analytics & Dashboards for Business — AiKrok",
        desc="We bring data from ads, CRM, inventory and spreadsheets into one picture: owner dashboards, automatic reports, metrics and KPIs, AI analytics.",
        lead="We bring data from different sources into one picture, so the owner can see what is happening in the business and decide by the numbers rather than by gut feeling.",
        what=[
            "<strong>Data collection</strong> — ads, CRM, inventory, spreadsheets, payment systems.",
            "<strong>Dashboards</strong> — key metrics on one screen, updated automatically.",
            "<strong>Automatic reports</strong> — a daily or weekly summary in Telegram or by email.",
            "<strong>Metrics and KPIs</strong> — we help pick the indicators that really drive decisions.",
            "<strong>AI analytics</strong> — questions to your data in plain language.",
            "<strong>Forecasts</strong> — sales estimates where there is enough data for them.",
        ],
        fit=[
            "the report is assembled by hand from several spreadsheets and takes hours;",
            "numbers in the ad account, the CRM and accounting don't match;",
            "the owner learns about a problem a month later instead of the next day;",
            "the data exists, but nobody uses it.",
        ],
        price="The cost depends on the number of data sources, their quality and how complex the calculations are. A first version — one dashboard with the main metrics from one or two sources — usually fits into a two-week stage. You get an estimate after a free review.",
        cases=[
            ("Trading Analytics Dashboard", "an interactive panel for a trader: win rate by coin and trade type, take-profit statistics, monthly trends; the data updates automatically."),
        ],
        faq=[
            ("Where to start if the data is scattered across spreadsheets?", "With one question you need answered every day — for example, how many leads came in yesterday and at what cost. We collect the sources for it and build the first dashboard, then add the rest."),
            ("Which metrics does an owner need?", "About ten is usually enough: revenue, leads, conversion, average order value, acquisition cost, stock, receivables. The exact set depends on the business."),
            ("Do we need an expensive BI system for this?", "Not always. For a small business a lightweight dashboard and a daily summary in Telegram are often enough. Heavy BI platforms are justified with many sources and many users."),
            ("Can we ask questions about our data in plain text?", "Yes — with a language model connected to your data. It is important to limit it to verified sources so that it doesn't make numbers up."),
        ],
    ),
    dict(
        slug="ai-agenty", short="AI Agents & Business Automation", more="AI agent development",
        h1="AI Agent Development and Business Automation",
        title="AI Agent Development & Business Process Automation — AiKrok",
        desc="AI agents for small and medium businesses: lead processing, customer support, knowledge base (RAG), documents, CRM and accounting integrations. We start with one process.",
        lead="We build AI agents — digital employees that process leads, advise customers, fill in your CRM and connect your services together. We start with one process and expand step by step.",
        what=[
            "<strong>Lead processing</strong> — qualifying leads around the clock and handing them to a manager.",
            "<strong>Customer support</strong> — answers from a knowledge base with escalation to a human.",
            "<strong>Knowledge base (RAG)</strong> — the AI answers from your company's documents.",
            "<strong>Documents</strong> — invoice recognition, contract drafts, deadline tracking.",
            "<strong>Integrations</strong> — CRM, accounting systems, spreadsheets, messengers.",
            "<strong>Process automation</strong> — on n8n, Make or custom code, depending on the task.",
            "<strong>Error protection</strong> — the agent does not invent prices, deadlines or terms.",
        ],
        fit=[
            "managers spend time on repetitive questions and initial qualification;",
            "leads outside working hours go unanswered;",
            "company knowledge sits in scattered documents and newcomers take a long time to get up to speed;",
            "data is copied between systems by hand.",
        ],
        price="An agent's price has three layers: one-off development, monthly costs for the model and server, and support. The budget is driven most by the number of integrations, the quality of the source documents and the accuracy required. You get an estimate for your task after a free consultation.",
        cases=[
            ("Batumi Rent", "an LLM pipeline: a parser collects posts from channels, the model turns them into structured listings, and deduplication merges repeats."),
            ("AI Visibility Scanner", "a service that scans a site, runs queries through an LLM and returns a score for how visible the business is in AI assistants' answers."),
        ],
        faq=[
            ("How is an AI agent different from a chatbot?", "A chatbot follows predefined buttons and scenarios. An agent understands free text, chooses the action itself — answer, clarify, create a deal, hand over to a human — and works with your systems."),
            ("Which process should we automate first?", "One with a lot of repetitive manual work and a clear outcome: initial lead processing, answers to frequent questions, moving data between systems. One process — one first version."),
            ("How do you stop an agent from making things up?", "The agent answers only from verified sources, takes prices and terms from your systems rather than from memory, and hands the conversation to a human when unsure. Plus tests on real questions before launch."),
            ("Is it safe to share company data with AI?", "It depends on the data and the requirements. Options include cloud models with contractual guarantees or open models on your own server — we choose based on how sensitive the data is."),
            ("How much does an AI agent cost?", "From a few hundred dollars for automation on a ready-made platform to tens of thousands for a system integrated with accounting and its own model. Plus monthly costs for the model, server and support."),
        ],
    ),
]

HOME_FAQ = [
    ("How much does development cost?", "It depends on the task: an informational Telegram bot is roughly $200–600, an AI-powered bot with integrations starts at $3,000; websites, apps, CRM and analytics are estimated after a short discussion. You get an itemized estimate before work begins, and the consultation is free."),
    ("What does “MVP in 2 weeks” mean?", "A first working version with one key feature done properly: a real scenario, error handling and minimal analytics. Secondary features are deliberately postponed and added as the product proves itself."),
    ("What do you need from us to start?", "Tell us about the business and the problem. We ask questions, dig in and propose a solution with a price and timeline. You don't need to write a specification in advance."),
    ("Do you support the project after launch?", "Yes. We deploy, train your team and stay in touch: fixing, improving and extending the solution."),
    ("Which languages do you work in?", "English, Russian, Spanish and French."),
]

ALTS = {
    "Дашборд торговой аналитики: Win Rate, сделки и тренды по месяцам": "Trading analytics dashboard: win rate, trades and monthly trends",
    "AI-бот для трейдинга": "AI trading bot",
    "SubMap — трекер подписок": "SubMap — subscription tracker",
    "My Stash — семейный бюджет и чеки": "My Stash — family budget and receipts",
    "ECHO: The Dark Is Listening — игра-головоломка": "ECHO: The Dark Is Listening — puzzle game",
    "Petalstorm — казуальная аркада": "Petalstorm — casual arcade",
    "Tochki — игра «Точки» на тетрадном листе": "Tochki — the pencil-and-paper dots game",
    "Batumi Rent — промо-ролик": "Batumi Rent — promo video",
    'aria-label="Меню"': 'aria-label="Menu"',
}

# ---------------------------------------------------------------- /en/ home
HOME_TITLE = "AiKrok — Websites, Telegram Bots, AI Agents & CRM for Business"
HOME_DESC = ("AiKrok — IT solutions for small and medium businesses: websites, mobile apps, Telegram bots, "
             "AI agents, CRM and analytics. We dig into the task and ship a first version (MVP) in 2 weeks. Free consultation.")


def build_home():
    h = rd("index.html")

    def text(key, is_html):
        v = EN[key]
        return v if is_html else html.escape(v, quote=False)

    def repl(m):
        key = m.group(3)
        if key not in EN:
            return m.group(0)
        is_html = 'data-i18n-html="true"' in m.group(1)
        return m.group(1) + text(key, is_html) + m.group(5)

    h = re.sub(r'(<(\w+)\b[^>]*\bdata-i18n="(\w+)"[^>]*>)(.*?)(</\2>)', repl, h, flags=re.S)
    for tag in re.findall(r'<[^>]*data-i18n-ph="\w+"[^>]*>', h):
        key = re.search(r'data-i18n-ph="(\w+)"', tag).group(1)
        h = h.replace(tag, re.sub(r'placeholder="[^"]*"', 'placeholder="%s"' % html.escape(EN[key], quote=True), tag))
    for tag in re.findall(r'<[^>]*data-i18n-aria="\w+"[^>]*>', h):
        key = re.search(r'data-i18n-aria="(\w+)"', tag).group(1)
        h = h.replace(tag, re.sub(r'aria-label="[^"]*"', 'aria-label="%s"' % html.escape(EN[key], quote=True), tag))
    for ru, en in ALTS.items():
        assert ru in h, ru
        h = h.replace(ru, en)

    # head
    h = h.replace('<html lang="ru">', '<html lang="en">', 1)
    h = re.sub(r'(<title data-i18n="page_title">)[^<]*', r"\g<1>" + HOME_TITLE.replace("&", "&amp;"), h, count=1)
    esc = lambda s: html.escape(s, quote=True)
    h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(HOME_DESC), h, count=1)
    h = re.sub(r'<link rel="canonical"[^>]*>(\s*<link rel="alternate"[^>]*>)*',
               f'<link rel="canonical" href="{BASE}/en/">\n    ' + hreflang(BASE + "/", BASE + "/en/"), h, count=1)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*', r"\g<1>" + BASE + "/en/", h, count=1)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(HOME_TITLE), h, count=1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*',
               lambda m: m.group(1) + esc("Websites, apps, Telegram bots, AI agents, CRM and analytics. MVP in 2 weeks. Free consultation."), h, count=1)
    h = h.replace('content="ru_RU"', 'content="en_US"', 1)
    h = h.replace(BASE + "/og-image.png", OG)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*', lambda m: m.group(1) + esc(HOME_TITLE), h, count=1)
    h = re.sub(r'(<meta name="twitter:description" content=")[^"]*',
               lambda m: m.group(1) + esc("Websites, apps, Telegram bots, AI agents, CRM and analytics. MVP in 2 weeks."), h, count=1)
    org = dict(ORG, logo={"@type": "ImageObject", "url": BASE + "/favicon-192.png", "width": 192, "height": 192},
               description="IT solutions for small and medium businesses: websites, mobile apps, Telegram bots, AI agents and business automation, CRM systems, data analytics",
               email="info@aikrok.com", sameAs=["https://t.me/yuri_admin"],
               hasOfferCatalog={"@type": "OfferCatalog", "name": "AiKrok services", "itemListElement": [
                   {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["h1"], "url": f"{BASE}/en/services/{s['slug']}/"}} for s in SERVICES]})
    graph = [org,
             {"@type": "WebPage", "@id": BASE + "/en/#webpage", "url": BASE + "/en/", "name": HOME_TITLE, "inLanguage": "en",
              "isPartOf": {"@id": BASE + "/#website"}, "about": {"@id": BASE + "/#organization"}},
             {"@type": "FAQPage", "mainEntity": [
                 {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in HOME_FAQ]}]
    graph += app_nodes(EN, "en")
    h, n = re.subn(r'<script type="application/ld\+json">.*?</script>', lambda m: ld(graph), h, count=1, flags=re.S)
    assert n == 1

    # language switcher state
    h = h.replace('<button class="lang-btn active" data-lang="ru">', '<button class="lang-btn" data-lang="ru">', 1)
    h = h.replace('<button class="lang-btn" data-lang="en">', '<button class="lang-btn active" data-lang="en">', 1)

    # service links -> English service pages
    for s in SERVICES:
        h, n = re.subn(r'<a href="services/%s/" class="service-example service-more">[^<]*</a>' % s["slug"],
                       '<a href="/en/services/%s/" class="service-example service-more-en only-en">Learn more: %s &rarr;</a>' % (s["slug"], s["more"]),
                       h, count=1)
        assert n == 1, s["slug"]

    # FAQ in English, blog teaser (Russian-only) removed
    faq = """<!-- FAQ -->
<section class="faq-section-en only-en">
    <div class="container">
        <h2 class="section-title">Frequently asked questions</h2>
        <div class="faq">
%s
        </div>
    </div>
</section>

""" % "\n".join("            <details><summary>%s</summary><p>%s</p></details>" % (q, a) for q, a in HOME_FAQ)
    a, b = h.index("<!-- FAQ (Russian-only) -->"), h.index("<!-- CTA -->")
    teaser = ""
    cards = re.findall(r'<a class="blog-teaser-card" href="blog/([^"/]+)/">\s*<span class="blog-teaser-tag">([^<]+)</span>', h[a:b])
    if cards and all(slug in POSTS_EN for slug, _ in cards):
        teaser = """<!-- Blog -->
<section class="blog-teaser-en only-en">
    <div class="container">
        <h2 class="section-title">From the blog</h2>
        <p class="section-subtitle">Prices, timelines and typical mistakes — no fluff and no made-up numbers</p>
        <div class="blog-teaser-grid">
%s
        </div>
        <div class="blog-teaser-more">
            <a href="/en/blog/" class="btn btn-outline btn-lg">All articles</a>
        </div>
    </div>
</section>

""" % "\n".join("""            <a class="blog-teaser-card" href="/en/blog/%s/">
                <span class="blog-teaser-tag">%s</span>
                <h3>%s</h3>
            </a>""" % (slug, TAGS_EN[tag], html.escape(POSTS_EN[slug]["title"], quote=False)) for slug, tag in cards)
    h = h[:a] + faq + teaser + h[b:]
    if POSTS_EN:
        h = h.replace('href="blog/"', 'href="/en/blog/"')
    else:
        h = re.sub(r'\s*<a href="blog/"[^>]*>[^<]*</a>', "", h)

    # absolute asset paths (the page lives one level deeper)
    h = re.sub(r'\b(src|href|poster)="(?!https?:|/|#|mailto:)([^"]+)"', r'\1="/\2"', h)
    h = h.replace("fetch('icons.svg')", "fetch('/icons.svg')")
    h = re.sub(r"styles\.css\?v=\d+", "styles.css?v=" + CSS_V, h)
    h = re.sub(r"i18n\.js\?v=\d+", "i18n.js?v=" + I18N_V, h)

    left = sorted(set(re.findall(r"[А-Яа-яЁё][А-Яа-яЁё \-]*", re.sub(r"<!--.*?-->", "", h, flags=re.S))))
    assert not left, left
    wr("en/index.html", h)


# ---------------------------------------------------------------- /en/services/
HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{url}">
    {alt}
    <link rel="icon" href="/favicon.ico" sizes="32x32">
    <link rel="icon" href="/favicon-192.png" type="image/png" sizes="192x192">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{ogtitle}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="{og}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:locale" content="en_US">
    <meta property="og:site_name" content="AiKrok">
    <meta name="twitter:card" content="summary_large_image">
    {ld}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/styles.css?v={cssv}">
    <link rel="stylesheet" href="/blog/blog.css?v={bcssv}">
</head>
<body>

<header class="header">
    <div class="container header-inner">
        <a href="/en/" class="logo">
            <div class="logo-text-wrap">
                <span class="logo-text"><span class="logo-ai">Ai</span><span class="logo-krok">Krok</span></span>
                <span class="logo-subtitle">step by step</span>
            </div>
            <img src="/logo-mark.png?v=2" class="logo-mark" alt="" width="44" height="44">
        </a>
        <nav class="nav">
            <a href="/en/services/">Services</a>
            <a href="/en/#portfolio">Portfolio</a>
            <a href="/en/#process">How we work</a>{blog_link}
            <a href="/en/#contact">Contact</a>
        </nav>
        <div class="header-right">
            <div class="lang-switcher">
                <a class="lang-btn" href="{ru_path}" hreflang="ru">RU</a>
                <a class="lang-btn active" href="{en_path}" hreflang="en">EN</a>
            </div>
            <a href="/en/#contact" class="btn btn-primary btn-sm">Discuss a project</a>
        </div>
    </div>
</header>
"""

FOOT = """
<footer class="footer">
    <div class="container footer-inner">
        <div class="footer-brand">
            <a href="/en/" class="logo">
                <div class="logo-text-wrap">
                    <span class="logo-text"><span class="logo-ai">Ai</span><span class="logo-krok">Krok</span></span>
                    <span class="logo-subtitle">step by step</span>
                </div>
                <img src="/logo-mark.png?v=2" class="logo-mark" alt="" width="44" height="44">
            </a>
            <p>IT solutions for business: websites, bots, apps, CRM, analytics, and AI agents</p>
        </div>
        <div class="footer-links">
            <a href="/en/services/">Services</a>
            <a href="/en/#portfolio">Portfolio</a>
            <a href="/en/#process">How we work</a>{blog_link}
            <a href="/en/#contact">Contact</a>
        </div>
        <div class="footer-contacts">
            <a href="https://t.me/yuri_admin" target="_blank" rel="noopener">Telegram</a>
            <a href="mailto:info@aikrok.com">info@aikrok.com</a>
        </div>
    </div>
    <div class="container">
        <div class="footer-bottom">
            <p>&copy; 2026 aikrok. All rights reserved.</p>
        </div>
    </div>
</footer>

</body>
</html>
"""


BLOG_LINK = '\n            <a href="/en/blog/">Blog</a>' if POSTS_EN else ""
FOOT = FOOT.replace("{blog_link}", BLOG_LINK)


def head(title, desc, path, graph, ogtitle):
    e = lambda s: html.escape(s, quote=True)
    return HEAD.format(title=e(title), desc=e(desc), url=BASE + "/en" + path, ogtitle=e(ogtitle), og=OG,
                       alt=hreflang(BASE + path, BASE + "/en" + path), ld=ld(graph),
                       cssv=CSS_V, bcssv=BLOG_CSS_V, ru_path=path, en_path="/en" + path, blog_link=BLOG_LINK)


def li(items):
    return "\n".join("        <li>" + x + "</li>" for x in items)


def build_services():
    for s in SERVICES:
        path = f"/services/{s['slug']}/"
        url = BASE + "/en" + path
        graph = [
            {"@type": "Service", "@id": url + "#service", "name": s["h1"], "serviceType": s["short"],
             "description": s["desc"], "url": url, "provider": ORG, "inLanguage": "en"},
            crumbs([("Home", BASE + "/en/"), ("Services", BASE + "/en/services/"), (s["short"], url)]),
            {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in s["faq"]]},
        ]
        e = lambda t: html.escape(t, quote=False)
        ru_page = rd(f"services/{s['slug']}/index.html")
        rel = [x for x in re.findall(r'<li><a href="/blog/([^"/]+)/">', ru_page) if x in POSTS_EN]
        related = ""
        if rel:
            related = "    <h2>Related articles</h2>\n    <ul>\n" + li(
                '<a href="/en/blog/%s/">%s</a>' % (x, e(POSTS_EN[x]["title"])) for x in rel) + "\n    </ul>\n\n"
        body = f"""
<div class="article-header">
    <div class="breadcrumbs"><a href="/en/">Home</a> / <a href="/en/services/">Services</a> / {e(s['short'])}</div>
    <h1>{e(s['h1'])}</h1>
</div>

<main class="article">
    <p class="article-lead">{s['lead']}</p>
    <p><a href="/en/#contact" class="btn btn-primary btn-lg">Discuss a project</a></p>

    <h2>What we do</h2>
    <ul>
{li(s['what'])}
    </ul>

    <h2>When you need it</h2>
    <ul>
{li(s['fit'])}
    </ul>

    <h2>How the work goes</h2>
    <ol>
        <li><strong>We listen.</strong> You tell us about your business and the problem — we ask questions and dig in.</li>
        <li><strong>We propose.</strong> What to do, how much it costs and how long it takes — broken down by stage.</li>
        <li><strong>We build.</strong> With interim demos, so you see progress at every stage. The first working version is ready in 2 weeks.</li>
        <li><strong>We launch and support.</strong> We deploy, train your team and stay in touch after launch.</li>
    </ol>

    <h2>Timeline and cost</h2>
    <p>{s['price']}</p>

    <h2>Our work</h2>
    <ul>
{li('<strong>' + e(n) + '</strong> — ' + d for n, d in s['cases'])}
    </ul>
    <p><a href="/en/#portfolio">All examples &rarr;</a></p>

    <h2>Questions and answers</h2>
    <div class="faq">
{chr(10).join('        <details><summary>' + q + '</summary><p>' + a + '</p></details>' for q, a in s['faq'])}
    </div>

{related}    <h2>Other services</h2>
    <ul class="link-chips">
{li('<a href="/en/services/' + o['slug'] + '/">' + e(o['short']) + '</a>' for o in SERVICES if o is not s)}
    </ul>
</main>

<div class="article-cta">
    <h2>Tell us about your challenge</h2>
    <p>We'll respond within a day, suggest solutions and estimate timelines. Free consultation.</p>
    <a href="/en/#contact" class="btn btn-primary btn-lg">Discuss a project</a>
</div>
"""
        wr(f"en/services/{s['slug']}/index.html", head(s["title"], s["desc"], path, graph, s["h1"]) + body + FOOT)

    url = BASE + "/en/services/"
    graph = [crumbs([("Home", BASE + "/en/"), ("Services", url)]),
             {"@type": "ItemList", "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "name": s["short"], "url": f"{url}{s['slug']}/"} for i, s in enumerate(SERVICES)]}]
    cards = "\n".join(f"""    <a class="post-card" href="/en/services/{s['slug']}/">
        <h2>{html.escape(s['short'], quote=False)}</h2>
        <p>{s['lead']}</p>
    </a>""" for s in SERVICES)
    wr("en/services/index.html", head(
        "AiKrok Services — Websites, Bots, Apps, CRM, Analytics, AI Agents",
        "AiKrok services for small and medium businesses: websites, Telegram bots and AI assistants, mobile apps, CRM, analytics and AI agents. First version in 2 weeks.",
        "/services/", graph, "AiKrok Services") + f"""
<section class="blog-hero">
    <div class="container">
        <h1>Services</h1>
        <p>Six directions — one goal: solve your business challenge through IT</p>
    </div>
</section>

<main class="post-list">
{cards}
</main>

<div class="article-cta">
    <h2>Not sure what exactly you need?</h2>
    <p>Tell us about the task — we'll propose a solution and estimate the timeline. Free consultation.</p>
    <a href="/en/#contact" class="btn btn-primary btn-lg">Discuss a project</a>
</div>
""" + FOOT)


# ---------------------------------------------------------------- Russian pages: hreflang + switch link
def patch_ru():
    h = rd("index.html")
    if 'hreflang="en"' not in h:
        h = h.replace(f'<link rel="canonical" href="{BASE}/">',
                      f'<link rel="canonical" href="{BASE}/">\n    ' + hreflang(BASE + "/", BASE + "/en/"), 1)
    h = re.sub(r"styles\.css\?v=\d+", "styles.css?v=" + CSS_V, h)
    h = re.sub(r"i18n\.js\?v=\d+", "i18n.js?v=" + I18N_V, h)
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, flags=re.S)
    data = json.loads(m.group(1))
    data["@graph"] = [n for n in data["@graph"] if n["@type"] not in ("SoftwareApplication", "WebApplication")] + app_nodes(RU, "ru")
    h = h[:m.start()] + ld(data["@graph"]) + h[m.end():]
    wr("index.html", h)

    for path in ["/services/"] + [f"/services/{s['slug']}/" for s in SERVICES]:
        p = path.strip("/") + "/index.html"
        h = rd(p)
        if 'hreflang="en"' not in h:
            canon = f'<link rel="canonical" href="{BASE}{path}">'
            assert canon in h, p
            h = h.replace(canon, canon + "\n    " + hreflang(BASE + path, BASE + "/en" + path), 1)
            h = h.replace('        <div class="header-right">\n', f"""        <div class="header-right">
            <div class="lang-switcher">
                <a class="lang-btn active" href="{path}" hreflang="ru">RU</a>
                <a class="lang-btn" href="/en{path}" hreflang="en">EN</a>
            </div>
""", 1)
            wr(p, h)


def patch_sitemap():
    sm = rd("sitemap.xml")
    if "/en/" not in sm:
        urls = ["/en/", "/en/services/"] + [f"/en/services/{s['slug']}/" for s in SERVICES]
        add = "".join(f"""    <url>
        <loc>{BASE}{u}</loc>
        <lastmod>{TODAY}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>{'1.0' if u == '/en/' else '0.9'}</priority>
    </url>
""" for u in urls)
        marker = f"    <url>\n        <loc>{BASE}/blog/</loc>"
        assert marker in sm
        wr("sitemap.xml", sm.replace(marker, add + marker, 1))


if __name__ == "__main__":
    patch_ru()
    build_home()
    build_services()
    patch_sitemap()
    print("en build ok")
