# -*- coding: utf-8 -*-
"""VoltRide programmatic SEO generator (v3: 30 models).
Run inside the site folder:   python3 build_models.py

Reads  models.json (list of models) and model_texts.json (optional hand-written text by id).
Writes <id>.html for every model (no Product schema: FAQPage + BreadcrumbList only), rebuilds sitemap.xml, refreshes the models section of blog.html,
the MODEL_PRESETS block of index.html and the PRECACHE list of sw.js.
"""
import hashlib, html, json, math, os, re

BASE = "https://voltride-4qj.pages.dev"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATE = "2026-10-20"      # publication date shown on model pages
MOD = "2026-10-24"       # sitemap lastmod for pages touched on this date
LEGAL_LIMIT = 25
EXTREME_SPEED = 80   # at/above this we treat the model as outside "trottinette" territory

raw = json.load(open(os.path.join(ROOT, "models.json"), encoding="utf-8"))
MODELS = raw["models"]
BY_ID = {m["id"]: m for m in MODELS}
TEXTS_PATH = os.path.join(ROOT, "model_texts.json")
TEXTS = json.load(open(TEXTS_PATH, encoding="utf-8")) if os.path.exists(TEXTS_PATH) else {}

CLASS_AR = {"budget": "اقتصادي", "commuter": "تنقل يومي", "sport": "رياضي", "performance": "عالي الأداء"}
CLASS_HEAD = {"budget": "اقتصادية", "commuter": "للتنقل اليومي", "sport": "رياضية", "performance": "عالية الأداء"}
BRANDS = {"xiaomi": "Xiaomi", "segway": "Segway-Ninebot", "navee": "Navee", "niu": "NIU", "kukirin": "KuKirin",
          "ecoxtrem": "Ecoxtrem", "dualtron": "Dualtron", "vsett": "Vsett", "apollo": "Apollo", "kaabo": "Kaabo",
          "gotrax": "Gotrax", "inokim": "Inokim", "nami": "Nami", "teverun": "Teverun"}
GUIDES = ["guides/not-charging.html", "guides/battery-range.html", "guides/error-codes.html"]
# (path, priority, lastmod)
SPRINT = "2026-10-26"
SW_VERSION = "voltride-v13"
IMAGES = {"article-9.html": "electric-scooter-winter-range-voltride.jpg", "fr/article-9.html": "electric-scooter-winter-range-voltride.jpg", "en/article-9.html": "electric-scooter-winter-range-voltride.jpg", "article-10.html": "scooter-accessories.jpg"}
# (path, priority, lastmod) - dates are set per page on purpose (only pages really touched get a new lastmod)
TODAY = "2026-10-27"
STATIC_URLS = [("", "1.0", TODAY), ("blog.html", "0.9", TODAY), ("about.html", "0.6", TODAY), ("contact.html", "0.5", DATE),
               ("privacy.html", "0.5", SPRINT)] + \
              [(g, "0.8", SPRINT) for g in GUIDES] + \
              [(f"article-{i}.html", "0.8", DATE) for i in range(1, 9)] + \
              [(f"article-{i}.html", "0.8", SPRINT) for i in (9, 10)] + \
              [("fr/article-9.html", "0.7", SPRINT), ("en/article-9.html", "0.7", SPRINT),
               ("fr/privacy.html", "0.3", SPRINT), ("fr/contact.html", "0.3", SPRINT),
               ("en/privacy.html", "0.3", SPRINT), ("en/contact.html", "0.3", SPRINT),
               ("fr/blog.html", "0.5", TODAY), ("en/blog.html", "0.5", TODAY),
               ("fr/about.html", "0.5", TODAY), ("en/about.html", "0.5", TODAY),
               ("fr/article-11.html", "0.7", TODAY)]


def esc(s):
    return html.escape(str(s), quote=True)


def num(v):
    return "%g" % v


def brand(m):
    return BRANDS.get(m["id"].split("-")[0], m["name"].split()[0])


def wh(m):
    return m["voltage"] * m["ah"]


def tier(m):
    s = m["speed"]
    return "ok" if s <= LEGAL_LIMIT else "extreme" if s >= EXTREME_SPEED else "over"


def estimate(m, weight, terrain, mode, speed):
    """Mirror of calculate() in index.html."""
    usable = wh(m) * 0.9
    wf = 1 + (weight - 75) * 0.0045
    sf = 1 + max(0, speed - 20) * 0.035
    tf = {"flat": 1, "mixed": 1.12, "hills": 1.30}[terrain]
    mf = {"eco": 0.88, "balanced": 1, "sport": 1.14}[mode]
    motor = m["motor"]
    mof = 1.10 if motor >= 1500 else 1.05 if motor >= 800 else 1
    cap = 90 if motor >= 1500 else 60 if motor >= 800 else 45
    cons = min(cap, max(7, 12.5 * wf * sf * tf * mf * mof))
    return usable / cons, cons


def scenarios(m):
    sp = min(LEGAL_LIMIT, m["speed"])
    rows = [
        ("خفيف ومريح", "راكب 60 كغ، طريق مستوٍ، نمط اقتصادي", estimate(m, 60, "flat", "eco", sp)),
        ("استعمال عادي", "راكب 75 كغ، طريق مختلط، نمط متوازن", estimate(m, 75, "mixed", "balanced", sp)),
        ("ظروف صعبة", "راكب 90 كغ، مرتفعات، نمط متوازن", estimate(m, 90, "hills", "balanced", sp)),
    ]
    return rows, sp


RANK = {m["id"]: i + 1 for i, m in enumerate(sorted(MODELS, key=lambda x: -wh(x)))}


def similar(m, n=4):
    others = sorted((x for x in MODELS if x["id"] != m["id"]), key=lambda x: abs(wh(x) - wh(m)))
    return others[:n]


def gen_text(m):
    """Fallback text for models without hand-written text: built from category + numbers."""
    cat, w, mo = m["category"], wh(m), m["motor"]
    mid = estimate(m, 75, "mixed", "balanced", min(LEGAL_LIMIT, m["speed"]))[0]
    cls = CLASS_AR[cat]
    summary = (f"{m['name']} من فئة {cls}: بطارية {num(m['voltage'])}V × {num(m['ah'])}Ah (نحو {w:.0f} Wh، "
               f"المرتبة {RANK[m['id']]} من {len(MODELS)} في الطاقة بين الموديلات المدرجة عندنا) ومحرك {num(mo)} واط.")
    if mid < 15:
        dist = "رحلات قصيرة جداً (حتى نحو 8–10 كم ذهاباً وإياباً)"
    elif mid < 30:
        dist = "رحلات يومية قصيرة إلى متوسطة"
    elif mid < 60:
        dist = "رحلات يومية متوسطة إلى طويلة"
    else:
        dist = "مسافات طويلة، وربما أسبوعاً من الاستعمال الخفيف بين شحنتين"
    fit = {
        "budget": f"من يريد سكوتراً بسيطاً وخفيفاً بميزانية صغيرة لـ{dist}.",
        "commuter": f"التنقل اليومي في المدينة: {dist}.",
        "sport": f"من يريد عزماً وسرعة أكبر من سكوترات التنقل: {dist}.",
        "performance": f"المستخدم الخبير الباحث عن القوة والمدى: {dist}.",
    }[cat]
    not_fit = {
        "budget": "الراكب الثقيل، أو الطرق المرتفعة، أو من يقطع مسافات طويلة يومياً.",
        "commuter": "من يحتاج قوة كبيرة في المنحدرات الحادة أو يسلك مسارات ترابية.",
        "sport": "من يحمل سكوتره كل يوم على الدرج، أو يريد الالتزام بالحد 25 كم/س دون ضبط السرعة.",
        "performance": "التنقل اليومي الخفيف، والمبتدئون، ومن لا يستطيع حمل سكوتر ثقيل أو تخزينه.",
    }[cat]
    off = {
        "budget": "مصمم للأسفلت الناعم والمسافات القصيرة. تحقق من نوع الإطار (هوائي أو مصمت) فهو يحدد تحمّله للحفر، ولا ننصح به للمسارات الترابية.",
        "commuter": "للأسفلت والطرق المدنية. يتحمل الحفر الصغيرة والأرصفة المنخفضة بحذر، وليس للمسارات الوعرة.",
        "sport": "يتحمل الطرق المتشققة والمسارات الترابية الخفيفة أفضل من سكوترات التنقل. قد تختلف النسخ في التعليق وعرض الإطار، فتحقق من نسختك قبل الاعتماد عليه خارج الأسفلت.",
        "performance": "قوة المحرك تسمح بالمسارات والطلعات القوية، لكن الوزن الكبير والسرعات العالية يتطلبان خبرة وخوذة وحماية كاملة. استعمله في أرض خاصة أو مسارات مسموحة.",
    }[cat]
    if mo <= 350:
        off += " ومحركه الصغير يتعب في المنحدرات الحادة مع الراكب الثقيل."
    elif mo >= 4000:
        off += " وقدرته الكبيرة تعني تسارعاً عنيفاً، فلا تجرّبها دون تدرّج."
    return {"summary": summary, "fit": fit, "not_fit": not_fit, "offroad": off}


def text_for(m):
    t = gen_text(m)
    t.update(TEXTS.get(m["id"], {}))
    return t


def svg(m):
    tire = {"budget": 4, "commuter": 5, "sport": 7, "performance": 9}[m["category"]]
    body = {"budget": 4, "commuter": 5, "sport": 6, "performance": 8}[m["category"]]
    return f'''<svg class="hero-svg" viewBox="0 0 320 170" role="img" aria-labelledby="svgT svgD" xmlns="http://www.w3.org/2000/svg">
<title id="svgT">رسم توضيحي عام لسكوتر كهربائي</title>
<desc id="svgD">رسم أصلي مبسّط من VoltRide لا يمثل شكل الموديل الفعلي.</desc>
<ellipse cx="160" cy="152" rx="130" ry="6" fill="currentColor" opacity=".12"/>
<circle cx="70" cy="124" r="24" fill="none" stroke="currentColor" stroke-width="{tire}" opacity=".85"/>
<circle cx="70" cy="124" r="6" fill="currentColor"/>
<circle cx="250" cy="124" r="24" fill="none" stroke="currentColor" stroke-width="{tire}" opacity=".85"/>
<circle cx="250" cy="124" r="6" fill="currentColor"/>
<rect x="52" y="106" width="190" height="{body}" rx="{body/2}" fill="var(--cyan)"/>
<path d="M238 110 L262 34" stroke="var(--cyan)" stroke-width="{body}" stroke-linecap="round" fill="none"/>
<path d="M246 32 L282 26" stroke="currentColor" stroke-width="6" stroke-linecap="round" fill="none"/>
<circle cx="268" cy="38" r="5" fill="var(--amber)"/>
<path d="M70 124 L52 108" stroke="currentColor" stroke-width="3" opacity=".6"/>
</svg>'''


def legal_block(m):
    sp, t = m["speed"], tier(m)
    if t == "extreme":
        return ('<div class="warning"><h3>⚖️ لا يندرج ضمن التروتينيت المنظَّم</h3>'
                f'<p>سرعته المعلنة (نحو {sp} كم/س) تفوق كثيراً الحد المنشور للتروتينيت. بحسب ما نشرته الصحافة المغربية عن المرسوم 2.25.145 فالحد الأقصى <strong>25 كم/س</strong>. '
                'لا نملك مصدراً مؤكداً عن تصنيف مركبة بهذه المواصفات في المغرب، لذلك <strong>لا تستعملها في الطرق العامة</strong> قبل أن تسأل الجهات المختصة (النقل أو الأمن الوطني أو شركة تأمين). '
                'راجع <a href="article-7.html">مقال القانون</a> لما هو مؤكد وما هو غير مؤكد.</p></div>')
    if t == "over":
        return ('<div class="warning"><h3>⚖️ سرعته المعلنة تتجاوز 25 كم/س</h3>'
                f'<p>سرعة {esc(m["name"])} المعلنة نحو {sp} كم/س، بينما الحد المنشور في الصحافة المغربية عن المرسوم 2.25.145 هو <strong>25 كم/س</strong> للتروتينيت. '
                'قد تتيح بعض النسخ ضبط السرعة عبر التطبيق أو الإعدادات (تحقق من نسختك)، ولا نجزم بمدى كفاية ذلك قانونياً. '
                'قدّرنا المدى أعلاه على سرعة 25 كم/س لأنها المرجع الواقعي داخل المدينة. راجع <a href="article-7.html">مقال القانون</a>.</p></div>')
    return ('<div class="tip"><h3>⚖️ ضمن الحد المنشور للسرعة</h3>'
            f'<p>سرعة {esc(m["name"])} المعلنة نحو {sp} كم/س، أي ضمن الحد <strong>25 كم/س</strong> المنشور في الصحافة المغربية عن المرسوم 2.25.145. '
            'تبقى شروط أخرى كالخوذة ومنع السماعات والمعدات، وبعضها لم نتأكد من تفاصيله. راجع <a href="article-7.html">مقال القانون</a>.</p></div>')


def faqs(m, rows):
    mid = rows[1][2][0]
    days = max(1, math.floor(mid / 10))
    sp, t = m["speed"], tier(m)
    if t == "extreme":
        a3 = "سرعته وقدرته أعلى بكثير من الحد المنشور للتروتينيت (25 كم/س) بحسب الصحافة المغربية، ولا نملك مصدراً مؤكداً عن تصنيفه. لا تستعمله في الطرق العامة قبل الاستفسار لدى الجهات المختصة."
    elif t == "over":
        a3 = f"سرعته المعلنة (نحو {sp} كم/س) تتجاوز الحد المنشور 25 كم/س للتروتينيت. قد تتيح نسخ ضبط السرعة، لكن تحقق من الجهات المختصة ولا تعتمد على هذا الموقع وحده."
    else:
        a3 = f"سرعته المعلنة (نحو {sp} كم/س) ضمن الحد المنشور 25 كم/س، لكن الخوذة إلزامية ومنع السماعات ساريان بحسب ما نُشر، فراجع مقال القانون."
    return [
        ("كم مرة أحتاج لشحنه؟",
         f"بحسب تقدير VoltRide (سيناريو الاستعمال العادي: مدى نحو {mid:.0f} كم)، إن كنت تقطع نحو 10 كم يومياً فقد يكفيك شحن كل {days} {'يوم' if days == 1 else 'أيام'} تقريباً. الرقم تقريبي، ويتأثر بوزنك وطريقك. الأفضل ألا تنزل البطارية إلى الصفر باستمرار."),
        ("كيف أطيل عمر بطاريته؟",
         "تجنب الشحن في الحرارة العالية، ولا تترك البطارية فارغة أو ممتلئة أسابيع طويلة، واستعمل الشاحن الأصلي أو المطابق، واتبع توصية الشركة لموديلك. التفاصيل في مقال أخطاء تقصّر عمر البطارية."),
        ("هل يمكنني استعماله في طرق المغرب قانونياً؟", a3),
    ]


def page(m):
    slug = m["id"]
    t = text_for(m)
    rows, sp = scenarios(m)
    energy = wh(m)
    mid = rows[1][2][0]
    url = f"{BASE}/{slug}.html"
    title = f"كم مدى {m['name']} الواقعي؟ تقدير VoltRide للمغرب"
    desc = (f"تقدير مدى {m['name']} في ثلاثة سيناريوهات (60 و75 و90 كغ) انطلاقاً من بطارية {num(m['voltage'])}V {num(m['ah'])}Ah، "
            f"مع المواصفات المرجعية وملاحظة قانونية حول السرعة.")
    fq = faqs(m, rows)
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
    ld_crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "VoltRide", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": "المدونة", "item": BASE + "/blog.html"},
        {"@type": "ListItem", "position": 3, "name": m["name"], "item": url}]}
    js = lambda o: json.dumps(o, ensure_ascii=False, indent=1)

    srows = "\n".join(
        f'<tr><td><strong>{esc(n)}</strong><br><small>{esc(d)}</small></td><td class="winner">{r:.0f} كم</td><td>{c:.1f} Wh/كم</td></tr>'
        for n, d, (r, c) in rows)
    extra = ""
    if m["speed"] > LEGAL_LIMIT:
        r_max, _ = estimate(m, 75, "flat", "balanced", m["speed"])
        extra = (f'<p class="updated">للمقارنة فقط: عند السرعة القصوى المعلنة ({m["speed"]} كم/س) على طريق مستوٍ بوزن 75 كغ، '
                 f'يهبط التقدير إلى نحو {r_max:.0f} كم، ولا يصلح هذا الاستعمال في الطرق العامة بحسب الحد المنشور.</p>')
    low_conf = ""
    if m["motor"] >= 1500:
        low_conf = ('<div class="note"><h3>ثقة أقل في التقدير</h3><p>نموذج VoltRide مبسّط، ويقلّ ضبطه كلما كبر المحرك وزادت السرعة. '
                    'اعتبر الأرقام هنا حدّاً أعلى نظرياً، وصحّحها بتجربتك عبر «معامل الواقع».</p></div>')
    faq_html = "\n".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in fq)
    sim = similar(m)
    sim_links = " • ".join(f'<a href="{x["id"]}.html">{esc(x["name"])}</a>' for x in sim)
    battery_note = (f"طاقة بطاريته نحو {energy:.0f} Wh، وهي المرتبة {RANK[slug]} من {len(MODELS)} بين الموديلات المدرجة عندنا.")

    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b1220">
<title>{esc(title)} | VoltRide</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:locale" content="ar_MA">
<meta property="og:site_name" content="VoltRide">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon-192.png">
<link rel="icon" type="image/png" href="icon-192.png">
<link rel="stylesheet" href="site.css">
<script type="application/ld+json">
{js(ld_faq)}
</script>
<script type="application/ld+json">
{js(ld_crumb)}
</script>
<script src="site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">انتقل إلى المحتوى</a>
<div class="wrap">
<header class="site-nav">
  <a class="brand" href="index.html"><i>⚡</i>VoltRide</a>
  <nav class="links" aria-label="صفحات الموقع">
    <a href="index.html">التطبيق</a><a href="blog.html">المدونة</a><a href="about.html">حول</a><a href="privacy.html">الخصوصية</a><a href="contact.html">اتصل بنا</a>
  </nav>
</header>
<a href="blog.html" class="back">← العودة للمدونة</a>
<main id="main">
<article>
<h1>كم مدى {esc(m["name"])} الواقعي؟ تقدير VoltRide للمغرب</h1>
<div class="meta">📅 {DATE} • ✍️ فريق VoltRide • فئة: {CLASS_AR[m["category"]]}</div>
{svg(m)}
<p>الرقم المكتوب على علبة أي سكوتر هو مدى «مثالي» يُقاس غالباً لراكب خفيف وطريق مستوٍ وسرعة معتدلة، لذلك يبدو الواقع أقل منه. هنا نعرض <strong>تقدير VoltRide</strong> لمدى {esc(m["name"])} في ثلاثة سيناريوهات، محسوباً من مواصفات البطارية. هو تقدير نظري وليس قياساً ميدانياً. {esc(t["summary"])}</p>

<h2>📋 المواصفات المرجعية</h2>
<div class="table-wrap">
<table>
<tr><th>الفولت</th><th>السعة</th><th>الطاقة</th><th>قوة المحرك</th><th>السرعة القصوى المعلنة</th><th>المدى المتوقع (استعمال عادي)</th></tr>
<tr><td>{num(m["voltage"])} V</td><td>{num(m["ah"])} Ah</td><td>{energy:.0f} Wh</td><td>{num(m["motor"])} W</td><td>{num(m["speed"])} كم/س</td><td class="winner">≈ {mid:.0f} كم</td></tr>
</table>
</div>
<p class="updated">مواصفات مرجعية لم نتحقق منها بعد من صفحة الشركة، وقد تختلف النسخ (الفولت والسعة والقدرة) من سوق إلى آخر. راجع بيانات سكوترك الفعلي. {esc(battery_note)}</p>

<h2>📏 ثلاثة سيناريوهات للمدى (تقدير VoltRide)</h2>
<div class="table-wrap">
<table>
<tr><th>السيناريو</th><th>المدى المقدّر</th><th>الاستهلاك</th></tr>
{srows}
</table>
</div>
<p class="updated">محسوبة على سرعة {sp} كم/س، و90% من طاقة البطارية قابلة للاستعمال. كيف نحسب؟ اقرأ المنهجية في <a href="about.html">صفحة حول</a>.</p>
{extra}
{low_conf}

{legal_block(m)}

<h2>🏞️ ملاءمة الطرق الوعرة</h2>
<p>{esc(t["offroad"])}</p>
<div class="tip"><p><strong>يناسب:</strong> {esc(t["fit"])}<br><strong>لا يناسب:</strong> {esc(t["not_fit"])}</p></div>

<h2>❓ أسئلة شائعة</h2>
<div class="faq">
{faq_html}
</div>

<h2>🔗 اقرأ أيضاً</h2>
<ul>
<li><a href="article-8.html">كم تكلفة شحن السكوتر الكهربائي شهرياً؟</a></li>
<li><a href="article-4.html">5 أخطاء شائعة تقصّر عمر بطارية سكوترك</a></li>
<li><a href="article-1.html">10 نصائح لزيادة مدى سكوترك</a></li>
<li><a href="article-7.html">قانون التروتينيت في المغرب: ما الذي تؤكده المصادر؟</a></li>
<li><a href="article-5.html">كيف تختار سكوترك الأول؟</a></li>
</ul>
<p class="updated">موديلات قريبة في طاقة البطارية: {sim_links}</p>

<div class="cta">
<h3>⚡ احسب المدى الحقيقي لسكوترك الآن</h3>
<p>سنعبّئ الحاسبة بمواصفات {esc(m["name"])} لتعدّل وزنك وطريقك وترى النتيجة فوراً، ثم صحّحها برحلاتك الفعلية.</p>
<a href="index.html?model={slug}">احسب الآن ←</a>
</div>
</article>
</main>
<footer>
<a href="index.html">الرئيسية</a><a href="blog.html">المدونة</a><a href="about.html">حول</a><a href="privacy.html">الخصوصية</a><a href="contact.html">اتصل بنا</a>
<a href="#" onclick="if(window.VoltConsent){{VoltConsent.open();}}return false;">إعدادات الكوكيز</a>
<p>© 2026 VoltRide • الصور توضيحية</p>
</footer>
</div>
</body>
</html>
'''


def replace_block(text, start, end, block, fallback_before):
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    new = f"{start}\n{block}\n{end}"
    if pat.search(text):
        return pat.sub(lambda _: new, text)
    i = text.index(fallback_before)
    return text[:i] + new + "\n" + text[i:]


def read(name):
    return open(os.path.join(ROOT, name), encoding="utf-8").read()


def write(name, s):
    open(os.path.join(ROOT, name), "w", encoding="utf-8").write(s)


def main():
    # remove stale model pages that are no longer in models.json
    ids = {m["id"] for m in MODELS}
    for m in MODELS:
        write(f"{m['id']}.html", page(m))
    print("pages written:", len(MODELS))

    # sitemap
    urls = STATIC_URLS + [(f"{m['id']}.html", "0.7", MOD) for m in MODELS]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    sm += [f"  <url><loc>{BASE}/{p}</loc><lastmod>{lm}</lastmod><priority>{pr}</priority>"
           + (f"<image:image><image:loc>{BASE}/{IMAGES[p]}</image:loc></image:image>" if p in IMAGES else "")
           + "</url>" for p, pr, lm in urls]
    assert len({u[0] for u in urls}) == len(urls), "duplicate sitemap URL"
    sm.append("</urlset>\n")
    write("sitemap.xml", "\n".join(sm))
    print("sitemap urls:", len(urls))

    # blog section grouped by category
    parts = ['<h2 class="center" style="margin:30px 0 6px;font-size:21px">🛴 مدى الموديلات: تقدير VoltRide</h2>',
             '<p class="center updated" style="margin-bottom:14px">تقديرات نظرية لثلاثين موديلاً بحسب مواصفاتها المرجعية، وليست اختبارات ميدانية.</p>']
    for cat in ("budget", "commuter", "sport", "performance"):
        group = [m for m in MODELS if m["category"] == cat]
        if not group:
            continue
        parts.append(f'<h2 style="margin:22px 0 10px;font-size:17px;color:var(--cyan)">سكوترات {CLASS_HEAD[cat]} ({len(group)})</h2>')
        for m in group:
            r = estimate(m, 75, "mixed", "balanced", min(LEGAL_LIMIT, m["speed"]))[0]
            parts.append(f'<a href="{m["id"]}.html" class="article-card"><span class="cat">{CLASS_AR[cat]}</span>'
                         f'<h2>كم مدى {esc(m["name"])} الواقعي؟</h2>'
                         f'<p>بطارية {num(m["voltage"])}V {num(m["ah"])}Ah: تقدير نحو {r:.0f} كم في الاستعمال العادي، مع سيناريوهات وملاحظة قانونية.</p>'
                         f'<div class="meta">📅 20 أكتوبر 2026</div></a>')
    write("blog.html", replace_block(read("blog.html"), "<!--MODELS:START-->", "<!--MODELS:END-->", "\n".join(parts), "</main>"))

    # index presets
    presets = {m["id"]: {"name": m["name"], "voltage": m["voltage"], "ah": m["ah"], "motor": m["motor"]} for m in MODELS}
    block = "const MODEL_PRESETS = " + json.dumps(presets, ensure_ascii=False) + ";"
    write("index.html", replace_block(read("index.html"), "/*MODELS:START*/", "/*MODELS:END*/", block, "const scooters = ["))

    # internal-link section at the bottom of the calculator screen (crawlable text links to every model page)
    links = "\n".join(f'      <a href="{m["id"]}.html">{esc(m["name"])}</a>' for m in MODELS)
    write("index.html", replace_block(read("index.html"), "<!--LINKS:START-->", "<!--LINKS:END-->", links, "</nav>"))
    print("index internal links:", len(MODELS))

    # catalog array (scooters) in index.html, generated from models.json
    # field mapping: motor -> power, category -> cat. 'range' (claimed) is intentionally omitted:
    # index.html fills it with a VoltRide estimate flagged rangeEst.
    scoot = [{"id": m["id"], "name": m["name"], "cat": m["category"], "speed": m["speed"], "power": m["motor"],
              "voltage": m["voltage"], "ah": m["ah"], "price": m["price"]} for m in MODELS]
    arr = "const scooters = [\n  " + ",\n  ".join(json.dumps(s, ensure_ascii=False) for s in scoot) + "\n];"
    t = read("index.html")
    if "/*SCOOTERS:START*/" in t:
        t = replace_block(t, "/*SCOOTERS:START*/", "/*SCOOTERS:END*/", arr, "let lang = ")
    else:
        t = re.sub(r"const scooters = \[.*?\n\];", lambda _: "/*SCOOTERS:START*/\n" + arr + "\n/*SCOOTERS:END*/", t, count=1, flags=re.S)
    write("index.html", t)
    print("catalog scooters:", len(scoot))

    # service worker precache + automatic cache version
    base_files = ["./", "index.html", "offline.html", "manifest.json", "site.css", "site.js",
                  "icon-192.png", "icon-512.png", "icon-maskable-192.png", "icon-maskable-512.png",
                  "blog.html", "about.html", "privacy.html", "contact.html"] + [f"article-{i}.html" for i in range(1, 11)] + GUIDES + sorted(set(IMAGES.values()))
    files = base_files + [f"{m['id']}.html" for m in MODELS]
    sw = read("sw.js")
    lst = "const PRECACHE = [\n  " + ",\n  ".join(", ".join(f'"{f}"' for f in files[i:i + 4]) for i in range(0, len(files), 4)) + "\n];"
    sw = re.sub(r"const PRECACHE = \[.*?\];", lambda _: lst, sw, flags=re.S)
    sw = re.sub(r'const VERSION = "[^"]*";', f'const VERSION = "{SW_VERSION}";', sw)
    write("sw.js", sw)
    print("sw cache version:", SW_VERSION)


if __name__ == "__main__":
    main()
