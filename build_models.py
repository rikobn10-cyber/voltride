# -*- coding: utf-8 -*-
"""VoltRide programmatic SEO generator (v3: 30 models).
Run inside the site folder:   python3 build_models.py

Reads models.json for legacy model pages/catalogs and model_texts.json for optional editorial text. Reads model_data_v2.json for high-confidence, market-specific calculator options through the compatibility adapter.
Writes <id>.html for every model (no Product schema: FAQPage + BreadcrumbList only), preserves the hand-maintained sitemap.xml, refreshes blog.html, MODEL_PRESETS and MODEL_VARIANTS in index.html, and the PRECACHE list of sw.js.
"""
import hashlib, html, json, math, os, re
from model_data_adapter import VariantProjectionError, project_verified_variant

BASE = "https://voltride-4qj.pages.dev"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATE = "2026-10-20"      # publication date shown on model pages
MOD = "2026-10-24"       # sitemap lastmod for pages touched on this date
REFERENCE_SPEED = 25  # range-estimation benchmark only; not a universal legal limit
EXTREME_SPEED = 80   # at/above this we treat the model as outside "trottinette" territory

raw = json.load(open(os.path.join(ROOT, "models.json"), encoding="utf-8"))
MODELS = raw["models"]
BY_ID = {m["id"]: m for m in MODELS}
TEXTS_PATH = os.path.join(ROOT, "model_texts.json")
TEXTS = json.load(open(TEXTS_PATH, encoding="utf-8")) if os.path.exists(TEXTS_PATH) else {}

MODEL_DATA_V2_PATH = os.path.join(ROOT, "model_data_v2.json")
MODEL_DATA_V2 = json.load(open(MODEL_DATA_V2_PATH, encoding="utf-8"))


def build_verified_variant_options():
    """Build explicit market choices only from high-confidence, adapter-projectable V2 variants."""
    options = {}
    for model in MODEL_DATA_V2.get("models", []):
        for variant in model.get("variants", []):
            verification = variant.get("verification", {})
            if verification.get("status") != "verified_variant" or verification.get("confidence") != "high":
                continue
            for market in variant.get("market", []):
                try:
                    projection = project_verified_variant(
                        MODEL_DATA_V2, model["id"], variant["variantId"], market
                    )
                except VariantProjectionError as exc:
                    raise ValueError(
                        f"High-confidence variant cannot be projected: {model['id']} / "
                        f"{variant['variantId']} / {market}: {exc}"
                    ) from exc
                fields = projection["legacy_fields"]
                battery = variant.get("battery", {})
                source = next(iter(variant.get("sources", [])), {})
                generation = variant.get("generation") or ""
                sku = variant.get("sku") or ""
                label_parts = [market, generation, sku]
                label = " — ".join(part for part in label_parts if part)
                option = {
                    "key": f"{variant['variantId']}::{market}",
                    "variantId": variant["variantId"],
                    "market": market,
                    "label": label or variant["variantId"],
                    "generation": generation or None,
                    "sku": sku or None,
                    "voltage": fields["voltage"],
                    "ah": fields["ah"],
                    "motor": fields["motor"],
                    "energyWh": fields["energyWh"],
                    "energyWhBasis": fields["energyWhBasis"],
                    "energyWhSourceNote": battery.get("energyWhSourceNote"),
                    "speed": fields["speed"],
                    "rangeClaimKm": projection["range_claim"].get("max_km"),
                    "sourcePublisher": source.get("publisher"),
                    "sourceUrl": source.get("url"),
                }
                options.setdefault(model["id"], []).append(option)
    return options


CLASS_AR = {"budget": "اقتصادي", "commuter": "تنقل يومي", "sport": "رياضي", "performance": "عالي الأداء"}
CLASS_HEAD = {"budget": "اقتصادية", "commuter": "للتنقل اليومي", "sport": "رياضية", "performance": "عالية الأداء"}
BRANDS = {"xiaomi": "Xiaomi", "segway": "Segway-Ninebot", "navee": "Navee", "niu": "NIU", "kukirin": "KuKirin",
          "ecoxtrem": "Ecoxtrem", "dualtron": "Dualtron", "vsett": "Vsett", "apollo": "Apollo", "kaabo": "Kaabo",
          "gotrax": "Gotrax", "inokim": "Inokim", "nami": "Nami", "teverun": "Teverun"}
GUIDES = ["guides/not-charging.html", "guides/battery-range.html", "guides/error-codes.html"]
# (path, priority, lastmod)
SPRINT = "2026-10-26"
SW_VERSION = "voltride-v19"
IMAGES = {"article-9.html": "electric-scooter-winter-range-voltride.jpg", "fr/article-9.html": "electric-scooter-winter-range-voltride.jpg", "en/article-9.html": "electric-scooter-winter-range-voltride.jpg", "article-10.html": "scooter-accessories.jpg"}
# (path, priority, lastmod) - dates are set per page on purpose (only pages really touched get a new lastmod)
TODAY = "2026-10-27"
STATIC_URLS = [("", "1.0", TODAY), ("blog.html", "0.9", "2026-11-03"), ("about.html", "0.6", TODAY), ("contact.html", "0.5", DATE),
               ("privacy.html", "0.5", SPRINT)] + \
              [(g, "0.8", SPRINT) for g in GUIDES] + \
              [(f"article-{i}.html", "0.8", DATE) for i in range(1, 9)] + \
              [(f"article-{i}.html", "0.8", SPRINT) for i in (9, 10)] + \
              [("fr/article-9.html", "0.7", SPRINT), ("en/article-9.html", "0.7", SPRINT),
               ("fr/privacy.html", "0.3", SPRINT), ("fr/contact.html", "0.3", SPRINT),
               ("en/privacy.html", "0.3", SPRINT), ("en/contact.html", "0.3", SPRINT),
               ("fr/blog.html", "0.5", "2026-11-01"), ("en/blog.html", "0.5", TODAY),
               ("fr/about.html", "0.5", TODAY), ("en/about.html", "0.5", TODAY),
               ("fr/article-11.html", "0.7", "2026-10-29"),
               ("blog/charger-safety.html", "0.7", "2026-11-03"),
               ("fr/blog/securite-chargeur-trottinette.html", "0.7", "2026-11-02")]


def clean_path(p):
    """sitemap/canonical form of a page path: Cloudflare Pages serves /about for about.html and redirects the .html URL (308)."""
    return p[:-5] if p.endswith(".html") else p


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
    return "reference" if s <= REFERENCE_SPEED else "extreme" if s >= EXTREME_SPEED else "over"


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
    sp = min(REFERENCE_SPEED, m["speed"])
    rows = [
        ("خفيف ومريح", "راكب 60 كغ، طريق مستوٍ، نمط اقتصادي", estimate(m, 60, "flat", "eco", sp)),
        ("استعمال عادي", "راكب 75 كغ، طريق مختلط، نمط متوازن", estimate(m, 75, "mixed", "balanced", sp)),
        ("ظروف صعبة", "راكب 90 كغ، مرتفعات، نمط متوازن", estimate(m, 90, "hills", "balanced", sp)),
    ]
    return rows, sp


RANK = {m["id"]: i + 1 for i, m in enumerate(sorted(MODELS, key=lambda x: -wh(x)))}


def similar(m, n=4):
    others = [x for x in MODELS if x["id"] != m["id"] and x["category"] == m["category"]]
    return others[:n]



def estimate_variant(v, weight, terrain, mode):
    usable = v["energyWh"] * 0.9
    wf = 1 + (weight - 75) * 0.0045
    speed = min(REFERENCE_SPEED, v["speed"])
    sf = 1 + max(0, speed - 20) * 0.035
    tf = {"flat": 1, "mixed": 1.12, "hills": 1.30}[terrain]
    mf = {"eco": 0.88, "balanced": 1, "sport": 1.14}[mode]
    motor = v["motor"]
    mof = 1.10 if motor >= 1500 else 1.05 if motor >= 800 else 1
    cap = 90 if motor >= 1500 else 60 if motor >= 800 else 45
    consumption = min(cap, max(7, 12.5 * wf * sf * tf * mf * mof))
    return usable / consumption, consumption


def verified_variant_page_sections(variants):
    if not variants:
        pending = ('<div class="note"><h3>لم يتم التحقق من نسخة هذا الموديل بعد</h3>'
                   '<p>لا نعرض هنا مواصفات أو تقديرات مأخوذة من سجل قديم غير محسوم. '
                   'سنضيف بيانات هذا الموديل عندما تتوفر نسخة محددة وسوق ومصادر موثوقة من الشركة.</p></div>')
        return pending, pending

    spec_sections = []
    range_sections = []
    for v in variants:
        basis = ("منشورة من الشركة المصنّعة" if v["energyWhBasis"] == "manufacturer_published"
                 else "محسوبة من الجهد الاسمي × السعة")
        source = (f'<a href="{esc(v["sourceUrl"])}" target="_blank" rel="noopener noreferrer">'
                  f'{esc(v["sourcePublisher"] or "مصدر الشركة")}</a>') if v.get("sourceUrl") else "—"
        sku = f' • SKU: {esc(v["sku"])}' if v.get("sku") else ""
        generation = f' • الجيل: {esc(v["generation"])}' if v.get("generation") else ""
        claim = (f'<p class="updated">المدى المعلن من الشركة لهذه النسخة: {num(v["rangeClaimKm"])} كم. '
                 'هذا ادعاء الشركة وليس تقديراً ميدانياً.</p>') if v.get("rangeClaimKm") else (
                 '<p class="updated">لا تتوفر قيمة مدى منشورة ومتحقق منها لهذه النسخة.</p>')
        spec_sections.append(
            f'<section class="table-wrap"><h3>{esc(v["label"])}{generation}{sku}</h3>'
            '<table><tr><th>السوق</th><th>الفولت الاسمي</th><th>السعة</th><th>الطاقة</th><th>قوة المحرك الاسمية</th><th>السرعة القصوى</th></tr>'
            f'<tr><td>{esc(v["market"])}</td><td>{num(v["voltage"])} V</td><td>{num(v["ah"])} Ah</td>'
            f'<td>{num(v["energyWh"])} Wh</td><td>{num(v["motor"])} W</td><td>{num(v["speed"])} كم/س</td></tr></table>'
            f'<p class="updated">أساس الطاقة: {basis}. {esc(v.get("energyWhSourceNote") or "")}<br>المصدر: {source}</p>{claim}</section>'
        )
        scenarios = [
            ("خفيف ومريح", "راكب 60 كغ، طريق مستوٍ، نمط اقتصادي", estimate_variant(v, 60, "flat", "eco")[0]),
            ("استعمال عادي", "راكب 75 كغ، طريق مختلط، نمط متوازن", estimate_variant(v, 75, "mixed", "balanced")[0]),
            ("ظروف صعبة", "راكب 90 كغ، مرتفعات، نمط متوازن", estimate_variant(v, 90, "hills", "balanced")[0]),
        ]
        rows = "\n".join(
            f'<tr><td><strong>{name}</strong><br><small>{description}</small></td><td class="winner">≈ {range_km:.0f} كم</td></tr>'
            for name, description, range_km in scenarios
        )
        range_sections.append(
            f'<section class="table-wrap"><h3>{esc(v["label"])} — تقدير المدى</h3>'
            '<table><tr><th>السيناريو</th><th>المدى المقدّر</th></tr>'
            f'{rows}</table>'
            f'<p class="updated">التقدير مبني على {num(v["energyWh"])} Wh، مع استخدام 90% من الطاقة القابلة للاستعمال وسرعة مرجعية لا تتجاوز {REFERENCE_SPEED} كم/س (أو سرعة النسخة إذا كانت أقل). '
            'ليس اختباراً ميدانياً ولا ضماناً للمدى الفعلي.</p></section>'
        )
    return "\n".join(spec_sections), "\n".join(range_sections)


def migrate_model_page(page_html, model, variants):
    spec_html, range_html = verified_variant_page_sections(variants)
    intro = (f'<p>تختلف مواصفات {esc(model["name"])} باختلاف الجيل والسوق ورقم النسخة. '
             'نعرض أدناه فقط النسخ التي أمكن ربطها بمصادر موثوقة من الشركة المصنّعة. '
             'اختر السوق ورقم النسخة المطابقين للملصق الموجود على سكوترك قبل الاعتماد على أي رقم.</p>')
    page_html, n = re.subn(r'<p>الرقم المكتوب على علبة أي سكوتر.*?</p>', intro, page_html, count=1, flags=re.S)
    if n != 1:
        raise ValueError(f"Could not replace legacy model intro for {model['id']}")
    page_html, n = re.subn(
        r'<h2>📋 المواصفات المرجعية</h2>.*?(?=<h2>📏 ثلاثة سيناريوهات للمدى \(تقدير VoltRide\)</h2>)',
        '<h2>📋 مواصفات النسخ الموثقة حسب السوق</h2>\n' + spec_html + '\n',
        page_html, count=1, flags=re.S
    )
    if n != 1:
        raise ValueError(f"Could not replace legacy specification table for {model['id']}")
    range_block = (
        '<h2>📏 تقدير المدى حسب النسخة (منهجية VoltRide)</h2>\n' + range_html +
        '<div class="warning"><h3>تنبيه حول السرعة والقانون</h3>'
        '<p>لا تثبت السرعة المعلنة وحدها قانونية استخدام المركبة على الطرق العامة. '
        'تختلف حدود السرعة والتصنيف والترخيص والتأمين ومتطلبات الحماية حسب البلد والمدينة. '
        'تحقّق من الجهة المختصة في منطقتك قبل الاستخدام.</p></div>'
        '<p class="updated">إذا كنت تقود في المغرب، راجع <a href="/article-7">الدليل القانوني الخاص بالمغرب</a>؛ فهو لا ينطبق خارج المغرب.</p>\n'
    )
    page_html, n = re.subn(
        r'<h2>📏 ثلاثة سيناريوهات للمدى \(تقدير VoltRide\)</h2>.*?(?=<h2>🏞️ ملاءمة الطرق الوعرة</h2>)',
        range_block, page_html, count=1, flags=re.S
    )
    if n != 1:
        raise ValueError(f"Could not replace legacy range estimates for {model['id']}")
    page_html = page_html.replace("موديلات قريبة في طاقة البطارية:", "موديلات أخرى من الفئة نفسها:")
    page_html = page_html.replace(
        f'سنعبّئ الحاسبة بمواصفات {esc(model["name"])} لتعدّل وزنك وطريقك وترى النتيجة فوراً، ثم صحّحها برحلاتك الفعلية.',
        'افتح الحاسبة واختر السوق والنسخة الموثقة المطابقة لسكوترك قبل حساب المدى.'
    )
    page_html = page_html.replace(f'<a href="/?model={model["id"]}">احسب الآن ←</a>', '<a href="/">افتح الحاسبة ←</a>')
    return page_html


def gen_text(m):
    """Fallback text for models without hand-written text: built from category + numbers."""
    cat, w, mo = m["category"], wh(m), m["motor"]
    mid = estimate(m, 75, "mixed", "balanced", min(REFERENCE_SPEED, m["speed"]))[0]
    cls = CLASS_AR[cat]
    summary = (f"{m['name']} من فئة {cls}. تختلف المواصفات باختلاف الجيل والسوق ورقم النسخة؛ "
               "اعتمد فقط على مواصفات النسخة الموثقة المطابقة لسكوترك.")
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
        "sport": "من يحمل سكوتره كل يوم على الدرج، أو يحتاج سرعة قصوى أعلى من فئة هذا الموديل.",
        "performance": "التنقل اليومي الخفيف، والمبتدئون، ومن لا يستطيع حمل سكوتر ثقيل أو تخزينه.",
    }[cat]
    off = {
        "budget": "مصمم للأسفلت الناعم والمسافات القصيرة. تحقق من نوع الإطار (هوائي أو مصمت) فهو يحدد تحمّله للحفر، ولا ننصح به للمسارات الترابية.",
        "commuter": "للأسفلت والطرق المدنية. يتحمل الحفر الصغيرة والأرصفة المنخفضة بحذر، وليس للمسارات الوعرة.",
        "sport": "يتحمل الطرق المتشققة والمسارات الترابية الخفيفة أفضل من سكوترات التنقل. قد تختلف النسخ في التعليق وعرض الإطار، فتحقق من نسختك قبل الاعتماد عليه خارج الأسفلت.",
        "performance": "قوة المحرك تسمح بالمسارات والطلعات القوية، لكن الوزن الكبير والسرعات العالية يتطلبان خبرة وخوذة وحماية كاملة. استعمله في أرض خاصة أو مسارات مسموحة.",
    }[cat]
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


def speed_regulatory_note(m):
    sp, t = m["speed"], tier(m)
    local = ' إذا كنت تقود في المغرب، راجع <a href="/article-7">الدليل القانوني الخاص بالمغرب</a>؛ فهو لا ينطبق خارج المغرب.'
    if t == "extreme":
        return ('<div class="warning"><h3>⚖️ فئة أداء عالٍ — تحقّق من التصنيف المحلي</h3>'
                f'<p>السرعة القصوى المعلنة لهذا الموديل نحو {sp} كم/س، وقد تضعه قدرته وسرعته ضمن فئة مركبات مختلفة عن سكوترات التنقل الخفيف. '
                'تختلف القواعد حسب البلد والمدينة، بما في ذلك حدود السرعة والتصنيف والترخيص والتأمين ومتطلبات الحماية. '
                'لا تفترض أن استعماله على الطرق العامة مسموح؛ تحقّق من الجهة المختصة في منطقتك قبل الاستخدام.</p></div>'
                + f'<p class="updated">{local}</p>')
    if t == "over":
        return ('<div class="warning"><h3>⚖️ السرعة المعلنة أعلى من المرجع الحسابي</h3>'
                f'<p>سرعة {esc(m["name"])} المعلنة نحو {sp} كم/س، وهي أعلى من سرعة 25 كم/س التي تستخدمها VoltRide كمرجع حسابي لمقارنة تقديرات المدى. '
                'هذا الرقم ليس حداً قانونياً عالمياً؛ تختلف حدود السرعة وتصنيفات المركبات حسب البلد والمدينة. '
                'كما أن خفض السرعة عبر التطبيق لا يضمن وحده استيفاء المتطلبات المحلية. تحقّق من الجهات المختصة قبل استخدامه على الطرق العامة.</p></div>'
                + f'<p class="updated">{local}</p>')
    return ('<div class="tip"><h3>⚖️ السرعة وحدها لا تحدد قانونية الاستخدام</h3>'
            f'<p>سرعة {esc(m["name"])} المعلنة نحو {sp} كم/س، وهي لا تتجاوز المرجع الحسابي 25 كم/س المستخدم في تقديرات VoltRide. '
            'هذا لا يثبت أن المركبة مسموح بها في الطرق العامة؛ فقد تعتمد القواعد المحلية أيضاً على تصنيف المركبة والعمر والخوذة والإضاءة والتأمين. '
            'راجع المصادر الرسمية في بلدك قبل الاستخدام.</p></div>'
            + f'<p class="updated">{local}</p>')


def faqs(m, rows=None):
    return [
        ("كيف أتحقق من نسخة السكوتر التي أملكها؟",
         "قارن اسم الجيل ورقم SKU والسوق المكتوب على ملصق المنتج مع النسخة المعروضة في جدول المواصفات. لا تفترض أن موديلين بالاسم التجاري نفسه متطابقان."),
        ("هل المدى المقدّر مضمون؟",
         "لا. تقديرات VoltRide حسابية للمقارنة وليست اختباراً ميدانياً أو ضماناً. يتغير المدى الفعلي حسب وزن الراكب والحرارة والضغط والإطارات والتضاريس والسرعة وحالة البطارية."),
        ("هل يمكن استخدامه قانونياً على الطرق العامة؟",
         "لا تكفي مواصفات السرعة وحدها لتحديد قانونية الاستخدام. تختلف القواعد حسب البلد والمدينة وقد تشمل تصنيف المركبة والعمر والخوذة والإضاءة والتأمين؛ تحقّق من الجهة المحلية المختصة.")
    ]


def page(m, variant_options):
    slug = m["id"]
    variants = variant_options.get(slug, [])
    t = text_for(m)
    rows, sp = scenarios(m)
    energy = wh(m)
    mid = rows[1][2][0]
    url = f"{BASE}/{slug}"            # clean URL: Cloudflare Pages redirects *.html to the extensionless URL
    title = f"كم مدى {m['name']} الواقعي؟ تقدير VoltRide"
    if len(title + " | VoltRide") > 60:
        title = f"كم مدى {m['name']} الواقعي؟"
    desc = f"مواصفات النسخ الموثقة من {m['name']} حسب السوق، مع مصادر الشركة وتقديرات مدى نظرية توضح طريقة الحساب."
    fq = faqs(m, rows)
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
    ld_crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "VoltRide", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": "المدونة", "item": BASE + "/blog"},
        {"@type": "ListItem", "position": 3, "name": m["name"], "item": url}]}
    js = lambda o: json.dumps(o, ensure_ascii=False, indent=1)

    srows = "\n".join(
        f'<tr><td><strong>{esc(n)}</strong><br><small>{esc(d)}</small></td><td class="winner">{r:.0f} كم</td><td>{c:.1f} Wh/كم</td></tr>'
        for n, d, (r, c) in rows)
    extra = ""
    if m["speed"] > REFERENCE_SPEED:
        r_max, _ = estimate(m, 75, "flat", "balanced", m["speed"])
        extra = (f'<p class="updated">للمقارنة فقط: عند السرعة القصوى المعلنة ({m["speed"]} كم/س) على طريق مستوٍ بوزن 75 كغ، '
                 f'يهبط التقدير إلى نحو {r_max:.0f} كم. هذا سيناريو حسابي ولا يعني أن السرعة مناسبة أو مسموحة قانونياً؛ تحقّق من القواعد المحلية.</p>')
    low_conf = ""
    if m["motor"] >= 1500:
        low_conf = ('<div class="note"><h3>ثقة أقل في التقدير</h3><p>نموذج VoltRide مبسّط، ويقلّ ضبطه كلما كبر المحرك وزادت السرعة. '
                    'اعتبر الأرقام هنا حدّاً أعلى نظرياً، وصحّحها بتجربتك عبر «معامل الواقع».</p></div>')
    faq_html = "\n".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in fq)
    sim = similar(m)
    sim_links = " • ".join(f'<a href="/{x["id"]}">{esc(x["name"])}</a>' for x in sim)
    battery_note = (f"طاقة بطاريته نحو {energy:.0f} Wh، وهي المرتبة {RANK[slug]} من {len(MODELS)} بين الموديلات المدرجة عندنا.")

    page_html = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b1220">
<title>{esc(title)} | VoltRide</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:locale" content="ar">
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
  <a class="brand" href="/"><i>⚡</i>VoltRide</a>
  <nav class="links" aria-label="صفحات الموقع">
    <a href="/">التطبيق</a><a href="/blog">المدونة</a><a href="/about">حول</a><a href="/privacy">الخصوصية</a><a href="/contact">اتصل بنا</a>
  </nav>
</header>
<a href="/blog" class="back">← العودة للمدونة</a>
<main id="main">
<article>
<h1>{esc(title)}</h1>
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
<p class="updated">محسوبة على سرعة مرجعية لا تتجاوز {REFERENCE_SPEED} كم/س (أو السرعة القصوى المعلنة إذا كانت أقل)، و90% من طاقة البطارية قابلة للاستعمال. هذا مرجع حسابي للمقارنة وليس حداً قانونياً عالمياً. كيف نحسب؟ اقرأ المنهجية في <a href="/about">صفحة حول</a>.</p>
{extra}
{low_conf}

{speed_regulatory_note(m)}

<h2>🏞️ ملاءمة الطرق الوعرة</h2>
<p>{esc(t["offroad"])}</p>
<div class="tip"><p><strong>يناسب:</strong> {esc(t["fit"])}<br><strong>لا يناسب:</strong> {esc(t["not_fit"])}</p></div>

<h2>❓ أسئلة شائعة</h2>
<div class="faq">
{faq_html}
</div>

<h2>🔗 اقرأ أيضاً</h2>
<ul>
<li><a href="/article-8">كم تكلفة شحن السكوتر الكهربائي شهرياً؟</a></li>
<li><a href="/article-4">5 أخطاء شائعة تقصّر عمر بطارية سكوترك</a></li>
<li><a href="/article-1">10 نصائح لزيادة مدى سكوترك</a></li>
<li><a href="/article-7">دليل قانوني خاص بالمغرب: قواعد التروتينيت</a></li>
<li><a href="/article-5">كيف تختار سكوترك الأول؟</a></li>
</ul>
<p class="updated">موديلات قريبة في طاقة البطارية: {sim_links}</p>

<div class="cta">
<h3>⚡ احسب المدى الحقيقي لسكوترك الآن</h3>
<p>سنعبّئ الحاسبة بمواصفات {esc(m["name"])} لتعدّل وزنك وطريقك وترى النتيجة فوراً، ثم صحّحها برحلاتك الفعلية.</p>
<a href="/?model={slug}">احسب الآن ←</a>
</div>
</article>
</main>
<footer>
<a href="/">الرئيسية</a><a href="/blog">المدونة</a><a href="/about">حول</a><a href="/privacy">الخصوصية</a><a href="/contact">اتصل بنا</a>
<a href="#" onclick="if(window.VoltConsent){{VoltConsent.open();}}return false;">إعدادات الكوكيز</a>
<p>© 2026 VoltRide • الصور توضيحية</p>
</footer>
</div>
</body>
</html>
'''
    return migrate_model_page(page_html, m, variants)


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
    # Build the canonical verified V2 choices once; model pages, calculator and catalog share this projection.
    variant_options = build_verified_variant_options()

    # remove stale model pages that are no longer in models.json
    ids = {m["id"] for m in MODELS}
    for m in MODELS:
        write(f"{m['id']}.html", page(m, variant_options))
    print("pages written:", len(MODELS))

    # sitemap.xml is maintained separately; never overwrite its curated multilingual URLs.
    print("sitemap preserved")

    # blog section grouped by category
    parts = ['<h2 class="center" style="margin:30px 0 6px;font-size:21px">🛴 مواصفات موديلات VoltRide حسب السوق</h2>',
             '<p class="center updated" style="margin-bottom:14px">تظهر المواصفات فقط للنسخ التي أمكن التحقق منها من مصادر الشركة. الموديلات الأخرى قيد مراجعة النسخة والسوق.</p>']
    for cat in ("budget", "commuter", "sport", "performance"):
        group = [m for m in MODELS if m["category"] == cat]
        if not group:
            continue
        parts.append(f'<h2 style="margin:22px 0 10px;font-size:17px;color:var(--cyan)">سكوترات {CLASS_HEAD[cat]} ({len(group)})</h2>')
        for m in group:
            choices = variant_options.get(m["id"], [])
            status = f"{len(choices)} نسخة موثقة حسب السوق" if choices else "النسخة والسوق قيد التحقق"
            parts.append(f'<a href="/{m["id"]}" class="article-card"><span class="cat">{CLASS_AR[cat]}</span>'
                         f'<h2>{esc(m["name"])} — المواصفات حسب السوق</h2>'
                         f'<p>{status}. افتح صفحة الموديل لمراجعة النسخة ومصدر الشركة.</p>'
                         f'<div class="meta">📅 11 نوفمبر 2026</div></a>')
    write("blog.html", replace_block(read("blog.html"), "<!--MODELS:START-->", "<!--MODELS:END-->", "\n".join(parts), "</main>"))

    # index presets
    presets = {m["id"]: {"name": m["name"], "voltage": m["voltage"], "ah": m["ah"], "motor": m["motor"]} for m in MODELS}
    block = "const MODEL_PRESETS = " + json.dumps(presets, ensure_ascii=False) + ";"
    write("index.html", replace_block(read("index.html"), "/*MODELS:START*/", "/*MODELS:END*/", block, "const scooters = ["))
    variant_block = "const MODEL_VARIANTS = " + json.dumps(variant_options, ensure_ascii=False, separators=(",", ":")) + ";"
    write("index.html", replace_block(read("index.html"), "/*MODEL_VARIANTS:START*/", "/*MODEL_VARIANTS:END*/", variant_block, "/*SCOOTERS:START*/"))

    # internal-link section at the bottom of the calculator screen (crawlable text links to every model page)
    links = "\n".join(f'      <a href="/{m["id"]}">{esc(m["name"])}</a>' for m in MODELS)
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

    # Ride Match is generated exclusively from adapter-projectable, high-confidence V2 variants.
    # Legacy catalog values and unverified affiliate-only products are never eligible for recommendations.
    ride_models = []
    for model in MODEL_DATA_V2.get("models", []):
        variants = variant_options.get(model["id"], [])
        if not variants:
            continue
        ride_models.append({
            "id": model["id"],
            "name": model["name"],
            "cat": model["category"],
            "variants": variants,
        })
    ride_markets = sorted({variant["market"] for model in ride_models for variant in model["variants"]})
    ride_block = "const RIDE_MATCH_MODELS = " + json.dumps(ride_models, ensure_ascii=False, separators=(",", ":")) + ";\n"
    ride_block += "const RIDE_MATCH_MARKETS = " + json.dumps(ride_markets, ensure_ascii=False) + ";"
    ride_path = "ride-match.html"
    ride_html = read(ride_path)
    if "/*RIDE_VARIANTS:START*/" not in ride_html or "/*RIDE_VARIANTS:END*/" not in ride_html:
        raise ValueError("Ride Match V2 variant marker is missing")
    ride_html = replace_block(ride_html, "/*RIDE_VARIANTS:START*/", "/*RIDE_VARIANTS:END*/", ride_block, "const RIDE_MATCH_MODELS =")
    # Keep the generated page aligned with the verified-destination safety gate.
    old_cta = '''    const isAffiliate = Boolean(r.s.affiliateUrl);
    const buyUrl = isAffiliate ? r.s.affiliateUrl : `https://www.aliexpress.com/wholesale?SearchText=${encodeURIComponent(r.s.name)}`;
    const buyRel = isAffiliate ? "noopener sponsored nofollow" : "noopener nofollow";'''
    new_cta = '''    const buyUrl = `https://www.aliexpress.com/wholesale?SearchText=${encodeURIComponent(r.s.name)}`;
    const buyRel = "noopener nofollow";'''
    old_analytics = '''    const eventName = product && product.affiliateUrl ? "affiliate_click" : "marketplace_search_click";
    window.VoltAnalytics.track(eventName, {
      item_id: product ? product.id : undefined,
      link_type: product && product.affiliateUrl ? "affiliate" : "marketplace_search"
    });'''
    new_analytics = '''    window.VoltAnalytics.track("marketplace_search_click", {
      item_id: product ? product.id : undefined,
      link_type: "marketplace_search"
    });'''
    if old_cta in ride_html:
        ride_html = ride_html.replace(old_cta, new_cta, 1)
    elif new_cta not in ride_html:
        raise ValueError("Ride Match purchase CTA template was not found")
    if old_analytics in ride_html:
        ride_html = ride_html.replace(old_analytics, new_analytics, 1)
    elif new_analytics not in ride_html:
        raise ValueError("Ride Match analytics template was not found")
    write(ride_path, ride_html)
    print("Ride Match verified models:", len(ride_models))

    # service worker precache + automatic cache version
    base_files = ["./", "index.html", "offline.html", "manifest.json", "site.css", "site.js",
                  "icon-192.png", "icon-512.png", "icon-maskable-192.png", "icon-maskable-512.png",
                  "blog.html", "about.html", "privacy.html", "contact.html", "accessories.html", "en/accessories.html", "fr/accessories.html", "ride-match.html"] + [f"article-{i}.html" for i in range(1, 11)] + GUIDES + sorted(set(IMAGES.values()))
    files = base_files + [f"{m['id']}.html" for m in MODELS]
    sw = read("sw.js")
    lst = "const PRECACHE = [\n  " + ",\n  ".join(", ".join(f'"{f}"' for f in files[i:i + 4]) for i in range(0, len(files), 4)) + "\n];"
    sw = re.sub(r"const PRECACHE = \[.*?\];", lambda _: lst, sw, flags=re.S)
    sw = re.sub(r'const VERSION = "[^"]*";', f'const VERSION = "{SW_VERSION}";', sw)
    write("sw.js", sw)
    print("sw cache version:", SW_VERSION)


if __name__ == "__main__":
    main()
