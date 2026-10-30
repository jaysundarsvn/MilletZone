"""Source-aware article layouts. No content is fetched or invented at build time.

The caller supplies escaping, URL linking and asset helpers to keep this module
independent of build.py. Only the listed irregular source pages are handled.
"""
import re


SPECIAL_SLUGS = {'products', 'feedback', 'kashya', 'cancer', 'links', 'faqs', 'disease-protocols'}


def _text(block):
    return block.get('text', '').strip()


def _gap(message, helpers):
    return '<p class="content-gap">' + helpers['e'](message) + '</p>'


def _figure(block, helpers, title='', protocol=False):
    key = block.get('asset_key', '')
    asset = helpers['BY_URL'].get(key, {})
    if key in helpers['EXCLUDED'] or not asset.get('file'):
        return ''
    alt = block.get('alt', '').strip()
    if not alt or re.search(r'\.(jpg|jpeg|png)(?:$|\s)', alt, re.I) or alt.startswith(('IMG_', 'DSC', 'Screen Shot')):
        alt = title or 'Image from the original source page'
    cls = 'source-figure' + (' protocol-image' if protocol else '')
    return '<figure class="' + cls + '">' + helpers['image'](asset['file'], alt, '../') + '</figure>'


def _body(blocks, helpers, title='', protocol=False):
    """Render source headings as content unless explicitly grouped by a caller."""
    out, listing = [], False
    for block in blocks:
        kind, text = block['type'], _text(block)
        if kind != 'list-item' and listing:
            out.append('</ul>')
            listing = False
        if kind == 'image':
            out.append(_figure(block, helpers, title, protocol))
        elif text:
            if kind == 'list-item':
                if not listing:
                    out.append('<ul>')
                    listing = True
                out.append('<li>' + helpers['linked_text'](text) + '</li>')
            elif text.upper().rstrip(' :') in {'OTHER BENEFITS', 'INGREDIENTS', 'METHOD', 'INSTRUCTIONS'} or re.match(r'^(?:Morning.*Decoction|Afternoon.*Decoction|MILLETS- Main diet|Sesame seeds:)', text, re.I):
                out.append('<h3>' + helpers['e'](helpers['readable'](text)) + '</h3>')
            else:
                out.append('<p>' + helpers['linked_text'](text) + '</p>')
    if listing:
        out.append('</ul>')
    return ''.join(out)


def _sections(groups, helpers, class_name='', first_open=False):
    out, toc = [], []
    for number, (title, content) in enumerate(groups, 1):
        if not content.strip():
            continue
        anchor = 'section-' + str(number)
        label = helpers['readable'](title)
        toc.append((anchor, label))
        opened = ' open' if first_open and number == 1 else ''
        out.append(f'<details class="health-reading source-section {class_name}" id="{anchor}"{opened}><summary>{helpers["e"](label)}</summary><div class="section-body">{content}</div></details>')
    return ''.join(out), toc


def _products(page, helpers):
    blocks = page['blocks']
    names = {'LITTLE MILLET', 'FOXTAIL MILLET', 'BROWNTOP MILLET', 'KODO MILLET', 'BARNYARD MILLET', 'PROSO MILLET'}
    markers = [i for i, b in enumerate(blocks) if b['type'] == 'paragraph' and _text(b) in names]
    starts = []
    for marker in markers:
        start = marker
        while start and blocks[start - 1]['type'] == 'image':
            start -= 1
        starts.append(start)
    if not markers:
        return None
    intro = [b for b in blocks[:starts[0]] if _text(b) != 'Products' and _text(b) not in names]
    groups = []
    for i, marker in enumerate(markers):
        end = starts[i + 1] if i + 1 < len(starts) else len(blocks)
        title = _text(blocks[marker])
        body = [b for j, b in enumerate(blocks[starts[i]:end], starts[i]) if j != marker]
        groups.append((title, _body(body, helpers, title)))
    html, toc = _sections(groups, helpers, 'grain-source', first_open=True)
    return _body(intro, helpers, page['title']) + html, toc


def _feedback(page, helpers):
    texts = [_text(b) for b in page['blocks'] if _text(b)]
    quotes = []
    for text in texts:
        # These are source line wraps, not separate testimonials.
        if quotes and (text in {'on the site.thanx.', 'Feel like eating', 'the dishes as soon as', 'they are made'} or text.startswith('- Yoga Teacher')):
            quotes[-1] += ' ' + text
        else:
            quotes.append(text)
    out = ['<div class="community-voices">']
    for i, quote in enumerate(quotes, 1):
        body = '<blockquote class="source-quote"><p>' + helpers['linked_text'](quote) + '</p></blockquote>'
        out.append(f'<section class="community-comment" id="community-comment-{i}"><h2>Community comment {i}</h2><div class="section-body">{body}</div></section>')
    out.append('</div>')
    return ''.join(out), [('community-comment-' + str(i), 'Community comment ' + str(i)) for i in range(1, len(quotes) + 1)]


def _kashya(page, helpers):
    blocks = page['blocks']
    start = next((i for i, b in enumerate(blocks) if _text(b).startswith('Tinospora cordifolia or Tippa')), len(blocks))
    # Initial source inventory is kept independently: it contains additional plants.
    intro = _body(blocks[2:4], helpers)
    inventory = blocks[4:start]
    intro += '<section class="plant-inventory" id="plant-inventory"><h2>Plant names listed in the source</h2><ul>'
    intro += ''.join('<li>' + helpers['linked_text'](_text(b)) + '</li>' for b in inventory if _text(b)) + '</ul>'
    intro += _gap('This source inventory supplies names only. The illustrated entries below contain the available photographs; no entry-specific preparation descriptions were supplied.', helpers) + '</section>'
    entries, title, entry = [], '', []
    for b in blocks[start:]:
        if b['type'] == 'heading':
            if title and not entry:
                # Black Plum's scientific name is a second consecutive heading.
                title += ' ' + _text(b)
            else:
                if title:
                    entries.append((title, entry))
                title, entry = _text(b), []
        else:
            entry.append(b)
    if title:
        entries.append((title, entry))
    groups = []
    for title, entry in entries:
        name, separator, note = title.partition(' Note : ')
        gallery = ''.join(_figure(b, helpers, name, True) for b in entry if b['type'] == 'image')
        body = ('<div class="source-gallery">' + gallery + '</div>') if gallery else _gap('No image for this entry is available in the supplied collection.', helpers)
        body += '<p class="plant-source-name"><strong>Names in the source:</strong> ' + helpers['e'](name) + '</p>'
        if separator:
            body += '<p>' + helpers['linked_text']('Note : ' + note) + '</p>'
        prose = [b for b in entry if b['type'] != 'image' and _text(b)]
        body += _body(prose, helpers)
        if not prose:
            body += _gap('No entry-specific description was supplied in the original source.', helpers)
        groups.append((name, body))
    html, toc = _sections(groups, helpers, 'plant-entry')
    return intro + html, [('plant-inventory', 'Plant names in the source')] + toc


def _cancer(page, helpers):
    blocks = page['blocks']
    groups, title, content = [], '', []
    for i, b in enumerate(blocks):
        text = _text(b)
        if i == 0 and text.upper() == 'VARIOUS CANCERS AND PROTOCOLS' and len(blocks) > 1 and blocks[1]['type'] == 'heading':
            # This precise leading section has no body; the next section does.
            continue
        if b['type'] == 'image' and all(x['type'] == 'image' for x in blocks[i:]):
            if title:
                groups.append((title, _body(content, helpers, title, True)))
            groups.append(('Charts from the source', _body(blocks[i:], helpers, 'Cancer protocol chart from the source', True)))
            title, content = '', []
            break
        is_condition = text.isupper() and bool(re.fullmatch(r'[A-Z /]+CANCER', text))
        is_intro = not title and b['type'] == 'heading'
        if is_intro or is_condition:
            if title:
                groups.append((title, _body(content, helpers, title, True)))
            title, content = text, []
        else:
            content.append(b)
    if title:
        groups.append((title, _body(content, helpers, title, True)))
    return _sections(groups, helpers, 'cancer-source')


def _faqs(page, helpers):
    groups, question, answer = [], '', []
    for b in page['blocks']:
        text = _text(b)
        if b['type'] == 'heading' and text == 'Frequently Asked Questions':
            continue
        # Source questions are standalone short paragraphs, not actual headings.
        if text.startswith('For example when they found that in india the sales of calcium tablet'):
            # This question exists in the original export. Its initial answer was
            # removed during normalization; do not attach the remaining paragraph
            # to the preceding, unrelated question.
            if question:
                groups.append((question, answer))
            question = 'An article says certain millet contains goitrogens that can cause goitre if consumed as staple diet. Is it true?'
            answer = [{'type': 'paragraph', 'text': 'Source content note: the supplied normalized collection contains only part of the original answer to this question.'}, b]
            continue
        is_question = b['type'] != 'image' and text.endswith('?') and len(text) < 220
        if is_question:
            if question:
                groups.append((question, answer))
            question, answer = text, []
        else:
            answer.append(b)
    if question:
        groups.append((question, answer))
    e = helpers['e']
    out = ['<nav class="faq-question-index" aria-label="Original source questions"><h2>Questions in this collection</h2><ol>']
    toc = []
    for n, (question, _) in enumerate(groups, 1):
        anchor = 'question-' + str(n)
        toc.append((anchor, f'{n}. {question}'))
        out.append(f'<li><a href="#{anchor}"><strong>{e(question)}</strong></a></li>')
    out.append('</ol></nav>')
    for n, (question, answer) in enumerate(groups, 1):
        body = _body(answer, helpers, question)
        if not body:
            body = _gap('No answer was supplied for this question in the available source content.', helpers)
        out.append(f'<details class="health-reading source-section faq-source-answer" id="question-{n}"><summary><strong>{n}. {e(question)}</strong></summary><div class="section-body">{body}</div></details>')
    return ''.join(out), toc


def _protocols(page, helpers):
    markers = {
        'There are 5 components of Disease protocols:', 'INSTRUCTIONS:',
        'PREPARATION OF DECOCTIONS/KASHAYA:', 'Consuming ORGANIC Wood/Cold Pressed oils',
        'PREPARATION of SIRIDHANYA MILLETS', "'AMBALI or FERMENTED Millet BROTH' & ITS IMPORTANCE",
        'Various DISEASES WITH PROTOCOLS',
    }
    groups, title, content = [], '', []
    for b in page['blocks']:
        text = _text(b)
        if (not title and b['type'] == 'heading') or text in markers:
            if title:
                groups.append((title, _body(content, helpers, title, True)))
            title, content = text, []
        else:
            content.append(b)
    if title:
        groups.append((title, _body(content, helpers, title, True)))
    return _sections(groups, helpers, 'protocol-source')


def _links(page, helpers):
    """Pair original label lines with their following URL; retain bare links."""
    entries, pending = [], []
    links = page.get('links', [])
    used = set()
    videos = list(page.get('embedded_videos', []))
    group = 'Talks and conversations'

    def add_entry(url, tail='', raw=''):
        nonlocal pending
        title = pending[0] if pending else 'Untitled source link'
        description = pending[1:] + ([tail.strip()] if tail.strip() else [])
        if raw:
            description.append(raw)
        entries.append((group, title, description, url, bool(pending)))
        pending = []
        used.add(url)

    for b in page['blocks']:
        text = _text(b)
        if not text or text == 'Links for more Knowledge' or text == 'MILLET ZONE - KNOWLEDGE VIDEO LINKS :':
            continue
        if text == 'OTHER YOUTUBE VIDEO LINKS :':
            if pending:
                video = videos.pop(0) if videos else ''
                add_entry(video)
            continue
        if text == 'ARTICLE LINKS IN ENGLISH:':
            group = 'Articles and additional source links'
            continue
        if text == 'Mighty Millets for Nutrition and Health.':
            group = 'Whole grains and nutrition'
        elif text.startswith(('Dr Khadar Part', 'ANCIENT WISDOM', 'How Various present day')):
            group = 'Talks and conversations'
        elif text.startswith(('Nutritional Benefits', 'Truth About Grains', 'Healthy Bites', 'Need for Alkaline', 'What is a True', 'Wheat:')):
            group = 'Whole grains and nutrition'
        elif text == 'Millets Recipes in Telugu':
            group = 'Cooking and recipes'
        match = re.search(r'https?://[^\s<>]+', text)
        if match:
            url = match.group(0)
            add_entry(url, text[match.end():])
        elif text.startswith('ttps://'):
            # Keep the malformed visible text; the export supplies the real href.
            suffix = text.replace('ttps://', '').strip().replace(' ', '')
            source_link = next((x for x in links if x.get('url', '').endswith(suffix)), None)
            add_entry(source_link['url'] if source_link else '', raw=text)
        else:
            pending.append(text)
    if pending:
        add_entry('')
    for link in links:
        url = link.get('url', link.get('href', ''))
        if url and url not in used:
            label = link.get('text', link.get('label', ''))
            entries.append(('Additional source references', label or 'Untitled source link', [], url, bool(label)))
            used.add(url)
    for video in videos:
        url = video if isinstance(video, str) else video.get('src', video.get('url', ''))
        if url and url not in used:
            entries.append(('Additional source references', 'Source video', [], url, False))
            used.add(url)
    e, out, toc = helpers['e'], [], []
    group_names = list(dict.fromkeys(row[0] for row in entries))
    for n, name in enumerate(group_names, 1):
        anchor = 'resource-group-' + str(n)
        toc.append((anchor, name))
        out.append(f'<section class="resource-group" id="{anchor}"><h2>{e(name)}</h2>')
        for _, title, description, url, has_title in [row for row in entries if row[0] == name]:
            # Every URL comes from the supplied source. Reject unexpected schemes.
            href = url if re.match(r'^https?://', url) else ''
            label = e(title)
            title_html = f'<a href="{e(href)}" rel="noopener noreferrer">{label}</a>' if href else label
            out.append('<article class="resource-card"><h3>' + title_html + '</h3>')
            if description:
                out.append('<div class="resource-description">' + ''.join('<p>' + helpers['linked_text'](d) + '</p>' for d in description) + '</div>')
            elif has_title:
                out.append(_gap('The source provides a title and link, but no separate description.', helpers))
            else:
                out.append(_gap('No title or description was supplied for this link.', helpers))
            if href:
                out.append(f'<p class="resource-url"><a href="{e(href)}" rel="noopener noreferrer">{e(href)}</a></p>')
            else:
                out.append(_gap('No usable link was supplied for this entry.', helpers))
            out.append('</article>')
        out.append('</section>')
    return ''.join(out), toc


def render_special(page, helpers):
    """Return (HTML, [(anchor, label), ...]) or None for the generic renderer."""
    renderers = {'products': _products, 'feedback': _feedback, 'kashya': _kashya,
                 'cancer': _cancer, 'links': _links, 'faqs': _faqs,
                 'disease-protocols': _protocols}
    renderer = renderers.get(page.get('slug'))
    return renderer(page, helpers) if renderer else None
