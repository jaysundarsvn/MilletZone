"""Build the Millet Zone website with Python's standard library.

The content archive is deliberately kept outside the published directory.
Run `python build.py`, then serve or publish the contents of dist/.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit, unquote, urlencode, quote
import json
import re
import shutil
from content_rendering import render_special

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
PAGES = {p['slug']: p for p in json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))}
ASSETS = json.loads((ROOT / 'assets/asset-map.json').read_text(encoding='utf-8'))
BY_URL = {v['original_url']: v for v in ASSETS.values()}
EXCLUDE_FILE = ROOT / 'assets/excluded-images.json'
EXCLUDED = json.loads(EXCLUDE_FILE.read_text(encoding='utf-8')) if EXCLUDE_FILE.exists() else {}
USED_ASSETS = set()
DOMAIN = 'https://milletszone.com'
ARROW = '<span class="arrow" aria-hidden="true">↗</span>'
HERO = 'assets/images/home-3ecb87c4f7.webp'
GRAINS = 'assets/images/biryani-and-pulav-with-siri-dhanya-bf8189f148.webp'
LOGO = 'assets/millet-zone-logo.png'
MILLET_DATA = [
    ('foxtail', 'Foxtail', 'Korralu · Kangni', 'products-7709ae2afb.webp', ['60.6 g','12.3 g','8.0 g','0.7 mg','0.11 mg','0.59 mg']),
    ('browntop', 'Browntop', 'Andu Korralu', 'products-23f702effb.webp', ['69.7 g','11.5 g','12.5 g','18.5 mg','0.027 mg','3.2 mg']),
    ('barnyard', 'Barnyard', 'Oodhalu · Jhangora', 'products-cbbc9c546b.webp', ['65.5 g','6.2 g','9.8 g','1.5 mg','0.08 mg','0.31 mg']),
    ('kodo', 'Kodo', 'Arikalu · Kodra', 'products-d6a5b9a8a2.webp', ['65.6 g','6.2 g','9.0 g','2.0 mg','0.09 mg','0.33 mg']),
    ('little', 'Little', 'Samelu · Kutki', 'products-e6821bcc45.webp', ['65.5 g','7.7 g','9.8 g','1.5 mg','0.07 mg','0.30 mg']),
]
RECIPES = [
    ('idly-with-siri-dhanya', 'Breakfast', 'idly-with-siri-dhanya-5137b84b84.webp', 'Steamed millet idli'),
    ('dosa-with-siri-dhanya', 'Breakfast', 'dosa-with-siri-dhanya-96f50c571e.webp', 'Kodo millet set dosa'),
    ('upma-and-pongal-with-siri', 'Breakfast', 'upma-and-pongal-with-siri-631793778b.webp', 'Foxtail millet pongal'),
    ('rice-with-siri-dhanya', 'Meals', None, 'Cooked millet rice'),
    ('biryani-and-pulav-with-siri-dhanya', 'Meals', None, 'Millet biryani and pulav'),
    ('spicy-dishes-with-siri-dhanya', 'Meals', None, 'Millet bisi bele bath'),
    ('lemon-rice-with-siri-dhanya', 'Meals', None, 'Millet lemon rice'),
    ('roti-s-with-siri-dhanya', 'Breads', None, 'Millet roti'),
    ('poori-with-siri-dhanya', 'Breads', None, 'Millet poori'),
    ('whole-grain-bread-with-siri-dhanya', 'Breads', None, 'Whole grain millet bread'),
    ('sweets-with-siri-dhanya', 'Sweets', 'sweets-with-siri-dhanya-d8cff313b4.webp', 'Millet sweets'),
    ('cookies-with-siri-dhanya', 'Sweets', None, 'Foxtail millet cookies'),
]
RECIPE_SLUGS = {r[0] for r in RECIPES}


def e(value):
    return escape(str(value), quote=True)


def image(path, alt, prefix='', cls='', eager=False, thumbnail=False):
    if not path:
        return ''
    if thumbnail:
        thumb = path.replace('assets/images/', 'assets/images/thumbs/')
        if (ROOT / thumb).exists():
            path = thumb
    if not (ROOT / path).exists():
        raise FileNotFoundError(f'Required image missing: {path}')
    USED_ASSETS.add(path)
    size = next((a for a in ASSETS.values() if a.get('file') == path or a.get('thumbnail') == path), {})
    width = size.get('thumbnail_width' if '/thumbs/' in path else 'width', 1600)
    height = size.get('thumbnail_height' if '/thumbs/' in path else 'height', 1100)
    return f'<img src="{prefix}{e(path)}" alt="{e(alt)}" width="{width}" height="{height}" class="{cls}" loading="{"eager" if eager else "lazy"}" decoding="async"' + (' fetchpriority="high"' if eager else '') + '>'


def first_image(slug):
    for b in PAGES[slug]['blocks']:
        if b['type'] == 'image':
            asset = BY_URL.get(b.get('asset_key', ''), {})
            if asset.get('file') and b.get('asset_key') not in EXCLUDED:
                if asset.get('width', 0) > 250 and asset.get('height', 0) > 200:
                    return asset['file']
    return GRAINS


def recipe_image(recipe):
    return 'assets/images/' + recipe[2] if recipe[2] else first_image(recipe[0])


def brand(prefix=''):
    USED_ASSETS.add(LOGO)
    return f'<a class="brand" href="{prefix}index.html" aria-label="Millet Zone home"><img class="brand-logo" src="{prefix}{LOGO}" alt="Millet Zone — Source of Siri Dhanya" width="489" height="409" decoding="async"></a>'


def header(active, prefix):
    links = [('index','Home'),('millets','The Millets'),('recipes','Recipes'),('knowledge','Knowledge'),('about','About'),('contact','Get in touch')]
    nav = ''.join(f'<a href="{prefix}{slug}.html"'+(' aria-current="page"' if active == slug else '')+(' class="nav-contact"' if slug == 'contact' else '')+f'>{label}'+(' <span aria-hidden="true">↗</span>' if slug == 'contact' else '')+'</a>' for slug,label in links)
    return f'''<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner">{brand(prefix)}<button class="menu-toggle" type="button" aria-controls="primary-nav" aria-expanded="false">Menu +</button><nav class="nav" id="primary-nav" aria-label="Main navigation" data-open="false">{nav}</nav></div></header>'''


def footer(prefix):
    return f'''<footer class="footer"><div class="wrap"><div class="footer-grid"><div class="footer-about">{brand(prefix)}<p>A place to discover Siridhanya millets, explore recipes, and keep learning.</p></div><div><h3>Explore</h3><div class="footer-list"><a href="{prefix}millets.html">The five millets</a><a href="{prefix}recipes.html">Millet recipes</a><a href="{prefix}about.html">About Millet Zone</a></div></div><div><h3>Keep learning</h3><div class="footer-list"><a href="{prefix}knowledge.html">Knowledge library</a><a href="{prefix}faqs.html">Common questions</a><a href="{prefix}articles/links.html">Videos & resources</a></div></div><div class="footer-contact"><h3>Say hello</h3><div class="footer-list"><a href="mailto:mymilletzone@gmail.com">mymilletzone@gmail.com</a><a href="tel:+919492935095">+91 94929 35095</a><span>Shaikpet, Hyderabad, India</span><a href="{prefix}contact.html">Contact details ↗</a></div></div></div><div class="footer-bottom"><span>© 2026 Millet Zone. Rooted in the goodness of Siridhanya.</span><span>Information & education <span aria-hidden="true">·</span> <a href="{prefix}knowledge.html#reading-note">About the source material</a></span></div></div></footer>'''


def write_page(path, title, description, body, active='knowledge', prefix='', social_image=HERO):
    canonical = DOMAIN + ('/' if path == 'index.html' else '/' + path)
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#264c35"><title>{e(title)} | Millet Zone</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{e(canonical)}"><meta property="og:type" content="website"><meta property="og:title" content="{e(title)} | Millet Zone"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(canonical)}"><meta property="og:image" content="{DOMAIN}/{social_image}"><link rel="icon" href="{prefix}{LOGO}" type="image/png"><link rel="stylesheet" href="{prefix}styles.css"><link rel="stylesheet" href="{prefix}carousel.css"><link rel="stylesheet" href="{prefix}refinements.css"><script src="{prefix}app.js" defer></script></head><body>{header(active,prefix)}<main id="main">{body}</main>{footer(prefix)}</body></html>'''
    html = re.sub(r'\bmillets zone\b', 'Millet Zone', html, flags=re.I)
    target = OUT / path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(html, encoding='utf-8')


def button(label, href, yellow=False, outline=False):
    return f'<a class="button{" yellow" if yellow else " outline" if outline else ""}" href="{href}">{label}{ARROW}</a>'


def intro(title, description, eyebrow, parent=None, prefix=''):
    crumb = f'<a href="{prefix}index.html">Home</a><span aria-hidden="true">/</span>'
    if parent:
        crumb += f'<a href="{prefix}{parent[0]}.html">{parent[1]}</a><span aria-hidden="true">/</span>'
    crumb_title = re.sub(r'<[^>]+>', ' ', title)
    return f'<div class="wrap"><div class="page-intro"><nav class="breadcrumbs" aria-label="Breadcrumb">{crumb}<span>{crumb_title}</span></nav><span class="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div></div>'


def millet_cards():
    return '<div class="millet-grid">' + ''.join(f'''<a class="millet-card" href="millets.html#{slug}">{image('assets/images/'+photo,name+' millet grains',thumbnail=True)}<div class="millet-card-content"><span class="number">0{i+1} / SIRIDHANYA</span><h3>{name}</h3><p>{aliases}</p><div class="card-bottom">Meet the grain {ARROW}</div></div></a>''' for i,(slug,name,aliases,photo,_) in enumerate(MILLET_DATA)) + '</div>'


def recipe_cards(recipes, filtering=False, carousel=False):
    result = '<div class="recipe-grid">'
    if carousel:
        result = '<section class="recipe-carousel" aria-label="Millet recipes" aria-roledescription="carousel" data-carousel><div class="carousel-toolbar"><p class="carousel-position" data-carousel-status role="status"></p><div><button type="button" data-carousel-prev aria-label="Previous recipes">←</button><button type="button" data-carousel-next aria-label="Next recipes">→</button></div></div><div class="recipe-grid carousel-track" data-carousel-track tabindex="0" aria-label="Recipe slides">'
    for recipe in recipes:
        slug,category,_,alt = recipe
        p = PAGES[slug]
        attributes = f' data-filter-card data-category="{category}" data-search="{e(p["title"]+" "+p["description"]+" "+category)}"' if filtering else ''
        result += f'''<a class="recipe-card" href="recipes/{slug}.html"{attributes}><div class="recipe-image">{image(recipe_image(recipe),alt,thumbnail=True)}<span class="round-arrow" aria-hidden="true">↗</span></div><div class="recipe-type">{category} · Siridhanya kitchen</div><h3>{e(p['title'])}</h3><p>{e(p['description'])}</p></a>'''
    return result + '</div>' + ('</section>' if carousel else '')


FAQS = [
    ('Which are the five Siridhanya millets?', 'The five Siridhanya millets featured by Millet Zone are Foxtail, Browntop, Barnyard, Kodo, and Little millet.'),
    ('What can I make with millets?', 'The recipe collection includes rice, roti, idli, dosa, pongal, biryani, pulav, poori, sweets, bread, and cookies. Millet rice can be served with curries, chutneys, or sambar.'),
    ('Do I need to soak millets before cooking?', 'The cooking introduction recommends soaking unpolished grains for 5–8 hours, or overnight. Individual recipes give different instructions; follow the notes for the dish you are making.'),
    ('What does “unpolished” mean?', 'The source describes unpolished millets as de-husked grains with their bran layer retained during cleaning and processing.'),
    ('How does the source suggest storing the grains?', 'The source recommends refrigerating de-husked millet grains for longer storage to reduce problems with storage pests. Its suggested consumption periods vary between one and two months.'),
]


def faq_list(items=FAQS):
    return '<div class="faq">'+''.join(f'<details><summary><span class="faq-number">{i}.</span> <strong>{e(q)}</strong></summary><div class="answer">{e(a)}</div></details>' for i,(q,a) in enumerate(items,1))+'</div>'


def contact_banner():
    return f'<div class="wrap"><section class="contact-banner"><div><span class="eyebrow">Let’s keep the conversation growing</span><h2>A little curiosity goes a long way.</h2><p>Have a question about Millet Zone? Get in touch.</p></div>{button("Say hello", "contact.html")}</section></div>'


def build_home():
    body = f'''<div class="hero-shell"><section class="hero">{image(HERO,'Millet seedheads growing among green leaves',cls='hero-image',eager=True)}<div class="wrap hero-content reveal"><span class="eyebrow">Rooted in nature. Made for everyday life.</span><h1>Small grains.<br>A world of<br><span class="serif">possibilities.</span></h1><p class="hero-copy">Discover the five Siridhanya millets, familiar recipes, and a fresh way to look at everyday food.</p><div class="actions">{button('Explore the millets','millets.html',yellow=True)}<a class="text-link" href="recipes.html">Find your next recipe {ARROW}</a></div></div><span class="hero-side-note"><i></i> THE GOODNESS OF SIRIDHANYA</span><div class="hero-foot"><span>FIVE GRAINS. COUNTLESS WAYS TO EXPLORE.</span><span>From the field to your everyday table ↙</span></div></section></div>
    <div class="wrap"><div class="millet-ribbon"><span class="ribbon-label">Meet your everyday grains</span>{''.join(f'<a href="millets.html#{s}">{n} millet</a>' for s,n,*_ in MILLET_DATA)}</div></div>
    <section class="section wrap intro"><div><span class="eyebrow">A little grain. A bigger story.</span><h2>Rediscover the<br>goodness of<br><span class="serif">Siridhanya.</span></h2><p>Foxtail, Browntop, Barnyard, Kodo, and Little millet. Get to know the five grains at the heart of Millet Zone.</p><p>From a simple bowl of rice to warm pongal and soft idli, explore familiar foods with a different grain.</p><div class="actions"><a class="text-link" href="about.html">Get to know Millet Zone {ARROW}</a></div></div><div class="intro-visual">{image(GRAINS,'A variety of millet grains in bowls')}<div class="image-caption"><span>Small grains, many possibilities.</span><span aria-hidden="true">✳</span></div></div></section>
    <section class="section tinted"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">Meet the millets</span><h2>Five grains.<br>Each with its own story.</h2></div><p>Learn their names, take a closer look, and find a place to start exploring.</p></div>{millet_cards()}<p class="section-note">Known together as Siridhanya. Explore the names and information in the original Millet Zone collection.</p></div></section>
    <section class="section wrap"><div class="section-heading"><div><span class="eyebrow">From the Siridhanya kitchen</span><h2>Familiar favourites.<br><span class="serif">A millet twist.</span></h2></div><a class="text-link" href="recipes.html">Explore all recipes {ARROW}</a></div>{recipe_cards(RECIPES[:3])}</section>
    <section class="wrap"><div class="learning-band"><div class="band-copy"><span class="eyebrow">A little knowledge, every day</span><h2>Good food starts<br>with curiosity.</h2><p>Explore cooking notes, answers to common questions, and the original learning collection.</p><div class="actions">{button('Explore the library','knowledge.html',yellow=True)}</div></div><div class="learning-links"><a class="learning-link" href="articles/recipes.html"><span class="number">01</span><div><h3>Start with the basics</h3><p>Soaking, cooking, and getting to know your grains.</p></div>{ARROW}</a><a class="learning-link" href="faqs.html"><span class="number">02</span><div><h3>Make room for questions</h3><p>A little clarity for your millet journey.</p></div>{ARROW}</a><a class="learning-link" href="articles/links.html"><span class="number">03</span><div><h3>Keep exploring</h3><p>Videos, reading, and resources from the collection.</p></div>{ARROW}</a></div></div></section>
    <section class="section wrap faq-layout"><div class="faq-intro"><span class="eyebrow">Wondering about millets?</span><h2>Let’s start with<br>the simple things.</h2><p>A few helpful answers before you head into the kitchen.</p><a class="text-link" href="faqs.html">More questions, more answers {ARROW}</a></div>{faq_list(FAQS[:4])}</section>{contact_banner()}'''
    write_page('index.html','Discover Siridhanya millets',PAGES['home']['description'],body,'index')


def build_millets():
    body = intro('Meet the <span class="serif">millets.</span>', 'Five Siridhanya grains, with their local names and a closer look at each. Start with Foxtail, Browntop, Barnyard, Kodo, or Little millet.', 'The Siridhanya collection')
    body += '<div class="wrap catalog"><nav class="grain-jump-links" aria-label="Jump to a millet">'+''.join(f'<a href="#{slug}">{name}</a>' for slug,name,*_ in MILLET_DATA)+'</nav><aside class="info-note"><strong>Reading the nutrition figures.</strong> These values are transcribed from the original millet guide. The source does not specify a serving weight or measurement basis, so they should not be treated as verified per-serving values.</aside>'
    for slug,name,aliases,photo,values in MILLET_DATA:
        pairs = list(zip(['Carbohydrates','Protein','Fibre','Niacin','Riboflavin','Thiamine'],values))
        rows = ''.join(f'<tr><th scope="row">{key}</th><td>{value}</td><th scope="row">{pairs[i+3][0]}</th><td>{pairs[i+3][1]}</td></tr>' for i,(key,value) in enumerate(pairs[:3]))
        body += f'<section class="millet-profile" id="{slug}">{image("assets/images/"+photo,name+" millet grains")}<div><span class="eyebrow">One of the five Siridhanya</span><h2>{name} millet</h2><p class="aliases">{aliases}</p><table class="nutrition"><caption>Figures recorded in the source · measurement basis unspecified</caption><tbody>{rows}</tbody></table><div class="actions">{button("Explore millet recipes", "recipes.html",outline=True)}</div></div></section>'
    body += '</div>'
    write_page('millets.html','The five Siridhanya millets',PAGES['products']['description'],body,'millets')


def build_recipes():
    body = intro('Everyday food.<br><span class="serif">A new grain.</span>','Rice, idli, dosa, pongal, and more. Find something familiar to make from the Millet Zone recipe collection.','The Siridhanya kitchen')
    filters = ''.join(f'<button type="button" class="filter-button" data-filter="{value}" aria-pressed="{str(value=="all").lower()}">{name}</button>' for value,name in [('all','All recipes'),('Breakfast','Breakfast'),('Meals','Meals'),('Breads','Breads'),('Sweets','Sweets')])
    body += f'<div class="wrap catalog"><div class="filter-bar"><div class="filters" role="group" aria-label="Filter recipes">{filters}</div><label class="search"><span aria-hidden="true">⌕</span><input type="search" data-search aria-label="Search recipes" placeholder="Find a recipe…"></label></div><p class="filter-status" data-filter-status role="status">12 recipes to explore</p>{recipe_cards(RECIPES,True,True)}<div class="empty-state" data-empty hidden><h2>No recipes found.</h2><p>Try another grain or dish, or clear the filters.</p><button type="button" data-reset class="button">Show all recipes</button></div><aside class="info-note"><strong>Before you begin.</strong> Soaking and cooking instructions vary by dish. Follow the individual recipe; missing quantities and source inconsistencies are noted where they occur. <a href="articles/recipes.html">Read the cooking introduction →</a></aside></div>'
    write_page('recipes.html','Millet recipes',PAGES['recipes']['description'],body,'recipes')


KNOWLEDGE = [('recipes','In the kitchen'),('faqs','Questions & answers'),('links','Watch & read'),('about','The grains'),('home','The original introduction'),('products','Grain reference'),('natural-health-tips','Source health reading'),('disease-protocols','Source health reading'),('cancer','Source health reading'),('kashya','Plants & decoctions'),('feedback','Community voices')]


def book_inquiry(title):
    body = f'Hello,\r\n\r\nI am interested in learning more about the book "{title}" listed on the Millet Zone website.\r\n\r\nCould you please provide additional information regarding its availability and how I can obtain it?\r\n\r\nThank you.'
    query = urlencode({'subject': f'Book Inquiry – {title}', 'body': body}, quote_via=quote)
    return 'mailto:mysirilokam@gmail.com?' + query


def book_cards():
    titles = ['Siri Jeevana Marga', 'Ambali', 'Leaves & Kashayas', 'Sirilokam']
    return '<div class="book-grid">'+''.join(f'<article class="book-card"><h3>{e(title)}</h3><a class="text-link" data-book-title="{e(title)}" href="{e(book_inquiry(title))}">Inquire about this book {ARROW}</a></article>' for title in titles)+'</div>'


def knowledge_cards():
    return '<div class="knowledge-grid">'+''.join(f'<a class="knowledge-card" href="articles/{slug}.html"><span class="eyebrow">{label}</span><h3>{e(PAGES[slug]["title"])}</h3><p>{e(PAGES[slug]["description"])}</p><span class="text-link">Read the collection {ARROW}</span></a>' for slug,label in KNOWLEDGE)+'</div>'


def build_knowledge():
    body = intro('A place to <span class="serif">keep learning.</span>','Explore cooking guidance, common questions, videos, and the original Millet Zone reading collection.','The knowledge library')
    body += '<div class="wrap catalog"><aside class="info-note" id="reading-note"><strong>A note on the source material.</strong> This library preserves information from the original Millet Zone website. Historical health and therapeutic claims are attributed to that source and have not been medically verified. They are not treatment advice or a substitute for qualified medical care. Some source material is incomplete; notes appear alongside it.</aside>'+knowledge_cards()+'<section class="book-band"><span class="eyebrow">Continue reading</span><h2>Books from the source collection</h2><p>The original website lists <em>Siri Jeevana Marga</em>, <em>Ambali</em>, <em>Leaves & Kashayas</em>, and <em>Sirilokam</em>. It directs readers to email for a free PDF copy.</p>'+book_cards()+'</section></div>'
    write_page('knowledge.html','Knowledge library','Explore the Millet Zone cooking guidance, FAQs, videos, books and attributed source reading.',body)


def build_faqs():
    body = intro('A little clarity.<br><span class="serif">A good place to start.</span>','Answers about the five Siridhanya millets, cooking, and storage, drawn from the supplied Millet Zone material.','Common questions')
    body += '<div class="wrap catalog" style="max-width:900px">'+faq_list()+'<aside class="info-note">These short answers summarize the supplied cooking, about, and FAQ pages. The original FAQ also contains unverified health claims. <a href="articles/faqs.html">Read the attributed source answers →</a></aside></div>'
    write_page('faqs.html','Frequently asked questions','Answers about Siridhanya grains, recipes, soaking and storage from the Millet Zone collection.',body)


def build_about():
    body = intro('Rooted in <span class="serif">Siridhanya.</span>','A collection of grains, recipes, and ideas from Millet Zone. A place to learn, explore, and bring familiar foods to your table.','About Millet Zone')
    body += f'<section class="wrap about-hero"><div>{image(GRAINS,"Bowls of different millet grains")}</div><div><span class="eyebrow">The golden millets</span><h2>A closer look at<br>the everyday grain.</h2><p>Millet Zone’s original collection centres on five Siridhanya millets: Foxtail, Browntop, Barnyard, Kodo, and Little millet.</p><p>It explores unpolished grains, cooking traditions, and ways to prepare rice, roti, idli, dosa, pongal, and more.</p><div class="actions">{button("Meet the five millets","millets.html")}</div></div></section><section class="wrap catalog"><div class="learning-band"><div class="band-copy"><span class="eyebrow">From the original collection</span><h2>There’s more<br>to explore.</h2><p>Read the original introduction, including its discussion of unpolished grains and its references to Dr. Khadar.</p></div><div class="learning-links"><a class="learning-link" href="articles/about.html"><span class="number">01</span><div><h3>About Siridhanya</h3><p>Read the attributed source material.</p></div>{ARROW}</a><a class="learning-link" href="articles/feedback.html"><span class="number">02</span><div><h3>Community voices</h3><p>Comments from the original feedback page.</p></div>{ARROW}</a></div></div></section>{contact_banner()}'
    write_page('about.html','About Millet Zone',PAGES['about']['description'],body,'about')


def build_contact():
    body = intro('Let’s <span class="serif">talk millets.</span>','Get in touch with Millet Zone using the contact details listed in the original website.','We’d love to hear from you')
    body += '''<div class="wrap contact-grid"><section class="contact-card"><span class="eyebrow">Get in touch</span><h2>Say hello.</h2><div class="contact-method"><small>Email</small><a href="mailto:mymilletzone@gmail.com">mymilletzone@gmail.com ↗</a></div><div class="contact-method"><small>Telephone</small><a href="tel:+919492935095">+91 94929 35095 ↗</a></div><div class="contact-method"><small>Listed hours</small><p>10:45 am – 8:00 pm<br>Closed on Sundays.</p></div></section><section class="contact-card"><span class="eyebrow">Our listed location</span><h2>Shaikpet, Hyderabad.</h2><address>#5-99/1/B, H S Dargha,<br>Beside Dell Exclusive, Pillar no. 63,<br>Near Dargha Circle–Durgamma Temple,<br>Shaikpet, Gachibowli Main Road,<br>Old Mumbai Highway,<br>Hyderabad, Telangana – 500033, India.</address><aside class="info-note">Please confirm the address and hours before visiting. The original contact page marks its second location as inactive.</aside><a class="text-link" href="articles/contact-us.html">Read the source contact details ↗</a></section></div>'''
    write_page('contact.html','Contact Millet Zone',PAGES['contact-us']['description'],body,'contact')


def readable(text):
    text = text.strip()
    if text.isupper() and len(text) > 5:
        text = text.lower().capitalize()
    for pattern,replacement in [(r'\bsiri dhanya\b','Siri Dhanya'),(r'\bsiridhanya\b','Siridhanya'),(r'\bmillet zone\b','Millet Zone')]:
        text = re.sub(pattern,replacement,text,flags=re.I)
    return text


def rewrite_link(url, prefix='../'):
    url = url.strip().rstrip('\u00a0').replace('%C2%A0','')
    if not url or url.startswith('#'):
        return None
    parsed = urlsplit(url)
    if parsed.scheme not in ('https','http','mailto','tel'):
        return None
    if 'wixsite.com' in parsed.netloc:
        slug = parsed.path.rstrip('/').split('/')[-1]
        if slug == 'order':
            return None
        if slug in ('siridhanya',''):
            return prefix+'index.html'
        if slug == 'copy-of-whole-grain-bread-with-siri':
            slug = 'cookies-with-siri-dhanya'
        if slug in RECIPE_SLUGS:
            return prefix+'recipes/'+slug+'.html'
        if slug in PAGES:
            return prefix+'articles/'+slug+'.html'
        return None
    if parsed.netloc and not re.match(r'^[a-zA-Z0-9.-]+(?::\d+)?$',parsed.netloc):
        return None
    return url


def linked_text(text):
    """Only plain text is trusted; hyperlinks are sanitized separately."""
    parts = re.split(r'(https?://[^\s<>]+)',text)
    result = ''
    for part in parts:
        if part.startswith(('http://','https://')):
            url = rewrite_link(part.rstrip('.,;)'))
            result += f'<a href="{e(url)}" rel="noopener noreferrer">{e(part)}</a>' if url else e(part)
        else:
            result += e(part)
    return result


def render_blocks(page):
    special = render_special(page, {'e': e, 'image': image, 'BY_URL': BY_URL, 'EXCLUDED': EXCLUDED, 'readable': readable, 'linked_text': linked_text})
    if special is not None:
        return special
    out, toc, group, listing = [], [], 0, False
    health = page['health_claims']
    previous_heading = None
    disclosure_open = False
    for index,b in enumerate(page['blocks']):
        kind = b['type']
        text = b.get('text','').strip()
        if kind != 'list-item' and listing:
            out.append('</ul>')
            listing = False
        if kind == 'image':
            key = b.get('asset_key','')
            asset = BY_URL.get(key,{})
            if key in EXCLUDED or not asset.get('file'):
                continue
            if asset.get('width',0)<180 or asset.get('height',0)<140:
                continue
            alt = b.get('alt','').strip()
            if not alt or re.search(r'\.(jpg|png|jpeg)$',alt,re.I):
                alt = f'Illustration from the original {page["title"]} page'
            out.append('<figure class="article-image">'+image(asset['file'],alt,'../')+'</figure>')
        elif kind == 'heading' and text:
            heading = readable(text)
            if heading == previous_heading:
                continue
            previous_heading = heading
            group += 1
            anchor = f'section-{group}'
            toc.append((anchor,heading))
            if health:
                if disclosure_open:
                    out.append('</details>')
                    disclosure_open = False
                has_content = False
                for following in page['blocks'][index+1:]:
                    if following['type'] == 'heading':
                        break
                    if following.get('text', '').strip():
                        has_content = True
                    key = following.get('asset_key', '')
                    asset = BY_URL.get(key, {})
                    if key not in EXCLUDED and asset.get('file') and asset.get('width',0) >= 180 and asset.get('height',0) >= 140:
                        has_content = True
                if has_content:
                    out.append(f'<details class="health-reading" id="{anchor}"'+(' open' if group == 1 else '')+f'><summary>{e(heading)}</summary>')
                    disclosure_open = True
                else:
                    out.append(f'<h2 id="{anchor}">{e(heading)}</h2>')
            else:
                out.append(f'<h2 id="{anchor}">{e(heading)}</h2>')
        elif kind == 'list-item' and text:
            if not listing:
                out.append('<ul>')
                listing=True
            out.append(f'<li>{linked_text(text)}</li>')
        elif text:
            if text.upper().rstrip(':') in ('INGREDIENTS','METHOD','PREPARATION','PROCEDURE'):
                out.append(f'<h3>{e(text.capitalize())}</h3>')
            else:
                out.append(f'<p>{linked_text(text)}</p>')
    if listing:
        out.append('</ul>')
    if disclosure_open:
        out.append('</details>')
    return ''.join(out),toc


RECIPE_NOTES = {
 'cookies-with-siri-dhanya':'The source lists four ingredients, but gives no quantities, oven temperature, baking time, or preparation method. This is an ingredient reference until the missing details are supplied.',
 'whole-grain-bread-with-siri-dhanya':'The source heading names Browntop millet while its ingredients and method name Foxtail. The ingredients list 2 cups of whole wheat flour; the method mentions adding another cup. These details need confirmation before using the recipe.',
 'upma-and-pongal-with-siri':'The original page is titled “Upma and Pongal”, but the detailed ingredients and method describe pongal. No separate upma method has been added.',
}


def build_article(slug):
    p = PAGES[slug]
    recipe = next((r for r in RECIPES if r[0] == slug),None)
    is_recipe = recipe is not None
    prefix = '../'
    path = ('recipes/' if is_recipe else 'articles/')+slug+'.html'
    body = intro(e(p['title']),e(p['description']),recipe[1]+' · Siridhanya kitchen' if recipe else 'From the original collection',('recipes','Recipes') if recipe else ('knowledge','Knowledge'),'../')
    content,toc = render_blocks(p)
    aside = '<aside class="article-aside"><h2>On this page</h2>'+''.join(f'<a href="#{anchor}">{e(title[:110])}</a>' for anchor,title in toc)+'<a href="../recipes.html">All recipes ↗</a><a href="../knowledge.html">Knowledge library ↗</a></aside>'
    top = ''
    if is_recipe:
        top = image(recipe_image(recipe),recipe[3],prefix,'article-hero',True)+'<button class="print-button" type="button" data-print>Print recipe ↗</button>'
        if slug in RECIPE_NOTES:
            top += '<aside class="info-note recipe-incomplete"><strong>A note on this recipe.</strong> '+e(RECIPE_NOTES[slug])+'</aside>'
    if p['health_claims']:
        top += '<aside class="info-note"><strong>Attributed source reading · claims not verified.</strong> The material below reflects the original website’s statements, not verified medical guidance. Do not use it to diagnose or treat a condition or to replace prescribed care. Discuss health decisions with a qualified clinician.</aside><div class="source-controls"><button class="filter-button" type="button" data-disclosures="open">Expand sections</button><button class="filter-button" type="button" data-disclosures="close">Collapse sections</button></div>'
    if slug == 'products':
        top += '<aside class="info-note">The source nutrition figures do not state a serving size or measurement basis. Prices and purchasing content have been excluded.</aside>'
    if slug == 'contact-us':
        top += '<aside class="info-note">The second outlet is marked inactive in the source. “Coming up” locations are historical proposals, not confirmed locations. Confirm current details by telephone.</aside>'
    link_items=[]
    for link in p.get('links',[]):
        url = rewrite_link(link.get('href',link.get('url','')))
        label = link.get('text',link.get('label',''))
        if url:
            link_items.append(f'<li><a href="{e(url)}" rel="noopener noreferrer">{e(label or url)}</a></li>')
    if link_items and slug != 'links':
        content += '<h2 id="related-links">Links from this page</h2><ul>'+''.join(dict.fromkeys(link_items))+'</ul>'
    videos = p.get('embedded_videos',[])
    if videos and slug != 'links':
        content += '<div class="video-links">'
        for i,video in enumerate(videos):
            url = video if isinstance(video,str) else video.get('src',video.get('url',''))
            match = re.search(r'(?:embed/|v=)([\w-]{11})',url)
            if match:
                content += f'<a href="https://www.youtube.com/watch?v={match[1]}" rel="noopener noreferrer"><span aria-hidden="true">▷</span> Watch source video {i+1} on YouTube ↗</a>'
        content += '</div>'
    source = f'<div class="source-line">Source: <a href="{e(p["url"])}" rel="noopener noreferrer">Original Millet Zone · {e(p["title"])}</a><br>Content captured 25 October 2026. Reorganized for reading; purchase-related material excluded.</div>'
    body += '<div class="wrap article-grid">'+aside+f'<article class="article-body article-{slug}">'+top+content+source+'</article></div>'
    write_page(path,p['title'],p['description'],body,'recipes' if recipe else 'knowledge',prefix,recipe_image(recipe) if recipe else HERO)


def main():
    OUT.mkdir(exist_ok=True)
    for name in ('styles.css','app.js','carousel.css','refinements.css'):
        shutil.copy2(ROOT/name,OUT/name)
    build_home()
    build_millets()
    build_recipes()
    build_knowledge()
    build_faqs()
    build_about()
    build_contact()
    for slug in PAGES:
        build_article(slug)
    for asset in USED_ASSETS:
        target = OUT/asset
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/asset,target)
    pages = sorted(OUT.rglob('*.html'))
    urls = [DOMAIN+('/' if p.name=='index.html' else '/'+p.relative_to(OUT).as_posix()) for p in pages]
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{u}</loc></url>' for u in urls)+'</urlset>',encoding='utf-8')
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://milletszone.com/sitemap.xml\n',encoding='utf-8')
    print(f'Built {len(pages)} pages and {len(USED_ASSETS)} images in {OUT}')


if __name__ == '__main__':
    main()
