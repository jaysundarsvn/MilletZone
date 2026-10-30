# Natural Health link review

**Checked: 2026-10-30. Status: recommendations only; no website links or content changed.**

Scope: the `natural-health-tips` entry in [content.json](./content.json), its seven inherited reference links and image URL fields, and every anchor in the current [generated Natural Health page](./dist/articles/natural-health-tips.html). The [original Wix page](https://mymilletzone.wixsite.com/siridhanya/natural-health-tips) is the provenance source. Link availability does not validate the surrounding health claims.

External checks used read-only HTTP GET requests with redirects followed, supplemented by retrieved page text. Internal destinations were resolved against the generated files and their actual IDs; this verifies the local output, not an unconfirmed production deployment. No emails were sent and no telephone calls were placed. A refusal, bot check, timeout, or certificate error is **uncertain**, not evidence of a dead page.

## Inherited external links and provenance

Each inherited reference occurs once in the generated page's related-links section. The source has no additional hyperlink-type content blocks or embedded videos.

| ID / current label and URL | HTTP / destination evidence | Classification and relevance | Recommendation | Approval needed |
| --- | --- | --- | --- | --- |
| E1 — [haemoglobin level](http://www.stylecraze.com/articles/hemoglobin-rich-foods/) | `301 → 200`; same path on HTTPS. Title: *Foods To Increase Hemoglobin: 27 Essential Iron-Rich Foods*; displayed update 2025-08-05. | **Relevant**, general iron/hemoglobin topic. It is a consumer article, not primary evidence for the source's specific palm-jaggery treatment claim. | **Retain as an explicitly historical reference.** An optional general-information alternative is [NIH ODS: Iron](https://ods.od.nih.gov/factsheets/Iron-Consumer/), but it must not be presented as evidence for that palm-jaggery claim. | No change proposed for retention. **Yes** before any URL/label change or replacement. |
| E2 — [fiber](https://authoritynutrition.com/why-is-fiber-good-for-you/) | `301 → 301 → 404`, ending at [Healthline's root-level path](https://www.healthline.com/why-is-fiber-good-for-you); returned HTML title *Error Page*. | **Broken** legacy redirect. Topic is relevant to the beetroot paragraph's fiber reference. | **Replace with [MedlinePlus: Dietary Fiber](https://medlineplus.gov/dietaryfiber.html)**, with a clear source label. This is general fiber information, not verification of the paragraph's other claims. | **Yes — pending.** |
| E3 — [carrots](http://www.curejoy.com/content/5-health-benefits-of-carrots/) | `301 → 301 → 404`, ending at [the non-www HTTPS path](https://curejoy.com/content/5-health-benefits-of-carrots/). Returned title *Page not found - CureJoy* and a missing-page message. | **Broken**. The source attached this link to a carrot comparison in its wheatgrass paragraph. | **Remove the broken reference.** No directly equivalent primary source was verified for that comparison; do not invent a replacement. | **Yes — pending.** |
| E4 — [sodium benzoate](http://en.wikipedia.org/wiki/Sodium_benzoate) | `301 → 200`, ending at [the HTTPS article](https://en.wikipedia.org/wiki/Sodium_benzoate). Title matches the substance. | **Relevant** terminology reference, although encyclopedic rather than primary clinical evidence. | **Retain as a historical/general reference**, without implying that it verifies every surrounding health assertion. | No change proposed for retention. **Yes** before changing HTTP to HTTPS or changing its label. |
| E5 — [MSG](http://articles.mercola.com/sites/articles/archive/2009/04/21/msg-is-this-silent-killer-lurking-in-your-kitchen-cabinets.aspx) | `301 → 200`, same HTTPS path. Article dated 2009-04-21. The publisher explicitly warns that the older article may not reflect its current position. | **Obsolete as current guidance**, although the URL works. Topic matches, but the original warning about MSG is materially different from the FDA's published assessment. | **Replace with [FDA: Questions and Answers on MSG](https://www.fda.gov/food/food-additives-petitions/questions-and-answers-monosodium-glutamate-msg)** only as clearly labeled current background. Any associated claim correction needs a separate content decision; a URL swap must not imply that FDA supports the historical warning. | **Yes — pending.** |
| E6 — [numerous health benefits](http://blogs.naturalnews.com/studies-show-3-best-pain-relievers-kitchen/) | `301 → 200`, same HTTPS host/path. Title: *Studies Show 3 of the Best Pain Relievers Are in Your Kitchen*, dated 2014-09-18. Web retrieval initially timed out; direct HTTP retrieved the article successfully. | **Uncertain as supporting evidence**, not broken. It discusses ginger, turmeric and cayenne, makes broad treatment comparisons, and is not a primary study of the specific claims in the source paragraph. | **Remove this broad reference.** If modern turmeric background is wanted, use the E7 proposal once, with an accurate label, rather than duplicate it under a vague label. | **Yes — pending.** |
| E7 — [turmeric](http://www.naturalnews.com/turmeric.html) | `301 → 200`, same HTTPS path. The destination is a topic/news index containing numerous 2016 entries, not one supporting study. | **Obsolete as a focused current reference**; broadly on topic but poorly matched to the specific claim. | **Replace with [NIH NCCIH: Turmeric—Usefulness and Safety](https://www.nccih.nih.gov/health/turmeric)**, explicitly labeled as a separate evidence overview. It does not validate the source's cancer-treatment claims. | **Yes — pending.** |
| E8 — [Original Millets Zone / Natural health notes](https://mymilletzone.wixsite.com/siridhanya/natural-health-tips) | `200`, no redirect; title *Health Tips \| siridhanya*. Original page and matching historical material retrieved. | **Relevant provenance**. The original site retains its own historical navigation, including its Order page; the redesigned site does not reproduce that purchase link. | **Retain as the original source link.** | No change proposed. Any later alteration requires approval. |

The five proposed changes are **E2, E3, E5, E6 and E7**. E1, E4 and E8 are proposed for retention. Even an HTTP-to-HTTPS cleanup is a link change and remains subject to approval.

### Proposed primary-source alternatives: verification and limits

| Candidate | Verification on the checked date | Appropriate use |
| --- | --- | --- |
| [MedlinePlus: Dietary Fiber](https://medlineplus.gov/dietaryfiber.html) | Direct HTTP `200`; National Library of Medicine page and matching title retrieved. | General fiber background for E2. |
| [FDA: Questions and Answers on MSG](https://www.fda.gov/food/food-additives-petitions/questions-and-answers-monosodium-glutamate-msg) | Full matching FDA page retrieved through the web tool. Direct HTTP was redirected to an `abuse-detection-apology.html` page returning `404`; that bot response is **not** a confirmed missing article. | FDA's own assessment for E5. Browser access should be rechecked before applying an approved change. |
| [NIH NCCIH: Turmeric](https://www.nccih.nih.gov/health/turmeric) | Direct HTTP `200`; matching evidence-and-safety overview retrieved. | General turmeric evidence context for E7, not support for a cancer cure. |
| [NIH ODS: Iron](https://ods.od.nih.gov/factsheets/Iron-Consumer/) | Matching NIH fact sheet retrieved through the web tool; direct request returned `403`. Access restrictions remain **uncertain**, not broken. | Optional general iron context for E1; not a direct substitute for the palm-jaggery claim. |

These are proposals for links, not permission to add new factual website content. No claims from these resources have been inserted into the website.

## Internal links in the generated page

All 15 distinct internal destinations resolve. Occurrences include repeated header, breadcrumb, sidebar, and footer links. **Recommendation: retain all; no changes are proposed. Approval would be required before any Natural Health link change.**

| Current `href` | Occurrences | Destination evidence | Classification |
| --- | ---: | --- | --- |
| `#main` | 1 | The current page contains `id="main"`; skip link targets the main content. | Relevant |
| `../index.html` | 4 | [Home](./dist/index.html) exists; title identifies the Siridhanya home page. | Relevant |
| `../millets.html` | 2 | [Millet guide](./dist/millets.html) exists; title identifies the five millets. | Relevant |
| `../recipes.html` | 3 | [Recipes](./dist/recipes.html) exists with the matching title. | Relevant |
| `../knowledge.html` | 4 | [Knowledge library](./dist/knowledge.html) exists with the matching title. | Relevant |
| `../about.html` | 2 | [About](./dist/about.html) exists with the matching title. | Relevant |
| `../contact.html` | 2 | [Contact](./dist/contact.html) exists with the matching title. | Relevant |
| `#section-1` | 1 | Matching ID exists at the Natural Health Tips heading. | Relevant section jump |
| `#section-2` | 1 | Matching ID exists at the Siridhanya heading. | Relevant section jump |
| `#section-3` | 1 | Matching ID exists at the heading mentioning the Facebook page. This is an **internal heading link**, not a Facebook URL. | Relevant section jump; potentially ambiguous label |
| `#section-4` | 1 | Matching ID exists at the following source heading about further articles. | Relevant section jump |
| `#section-5` | 1 | Matching ID exists at the following source disease-list heading. | Relevant section jump |
| `../faqs.html` | 1 | [FAQs](./dist/faqs.html) exists with the matching title. | Relevant |
| `../articles/links.html` | 1 | [Learning resources](./dist/articles/links.html) exists with the matching title. | Relevant |
| `../knowledge.html#reading-note` | 1 | [Knowledge source note](./dist/knowledge.html#reading-note) exists and contains `id="reading-note"`. | Relevant |

No actual Facebook destination is provided among this page's seven inherited reference URLs. Do not guess or add a profile URL from the heading alone.

## Contact actions

| Current link | Evidence | Classification / recommendation | Approval needed |
| --- | --- | --- | --- |
| `mailto:mymilletzone@gmail.com` | Syntactically valid mail link; matches the supplied contact listing. Deliverability was not tested. | **Uncertain current availability**; retain the source-listed contact. | No change proposed; yes before alteration. |
| `tel:+919492935095` | Syntactically valid telephone link; matches the supplied contact listing. Ownership/service were not tested. | **Uncertain current availability**; retain the source-listed contact. | No change proposed; yes before alteration. |

## Metadata and media URLs

These are resource references, counted separately from clickable anchors. The [favicon](./dist/favicon.svg), [stylesheet](./dist/styles.css), [script](./dist/app.js), and [rendered illustration](./dist/assets/images/natural-health-tips-95bd6d7d62.webp) all exist as nonempty local files. The canonical URL is [the intended production article](https://milletszone.com/articles/natural-health-tips.html); its path matches the generated file, but this environment's live request failed certificate verification. **Production availability is uncertain**, not proven broken. Retain the configured canonical pending deployment checks; no link change is proposed.

The seven image blocks in [content.json](./content.json) each contain a transformed `src` URL and an original `asset_key`. All 14 exact URLs were requested; the following table groups each pair by its stable Wix asset identifier. The exact full URLs remain in the unchanged source file.

| Source image / asset identifier | Transformed `src` | Original asset | Recommendation / approval |
| --- | --- | --- | --- |
| Illustration, `7103ae_d84c6c8345614aeabe5806c8434531a2` | `200`, JPEG | [Original](https://static.wixstatic.com/media/7103ae_d84c6c8345614aeabe5806c8434531a2~mv2_d_5779_2796_s_4_2.jpg): `200`, JPEG | Retain provenance and the working local image; no change. |
| Illustration, `7103ae_72cf9afd4b4443e591d1b9ea379158ff` | `200`, JPEG | [Original](https://static.wixstatic.com/media/7103ae_72cf9afd4b4443e591d1b9ea379158ff~mv2_d_5312_2080_s_2.jpg): `200`, JPEG | Retain provenance; no change. |
| Colored capsicum 1, `7103ae_b25612fd2792433a9759c303ee666472` | `403` | [Original](https://static.wixstatic.com/media/7103ae_b25612fd2792433a9759c303ee666472~mv2.jpg): `403` | **Uncertain/restricted**, not confirmed broken; no replacement or removal without approval. |
| Photo 121944, `7103ae_5f17655e69bd4065aae04dc2a200e4a5` | `403` | [Original](https://static.wixstatic.com/media/7103ae_5f17655e69bd4065aae04dc2a200e4a5~mv2.jpg): `403` | **Uncertain/restricted**; no replacement or removal without approval. |
| Photo 121726, `7103ae_fc58f68449d54b6991b5cb031b86948a` | `403` | [Original](https://static.wixstatic.com/media/7103ae_fc58f68449d54b6991b5cb031b86948a~mv2.jpg): `403` | **Uncertain/restricted**; no replacement or removal without approval. |
| Colored capsicum 2, `7103ae_25691b118a60405895e30c8351812263` | `403` | [Original](https://static.wixstatic.com/media/7103ae_25691b118a60405895e30c8351812263~mv2.jpg): `403` | **Uncertain/restricted**; no replacement or removal without approval. |
| Bottle gourd, `7103ae_2f59f75b75a6401da72326a825a710fa` | `403` | [Original](https://static.wixstatic.com/media/7103ae_2f59f75b75a6401da72326a825a710fa~mv2.jpg): `403` | **Uncertain/restricted**; no replacement or removal without approval. |

## Final counts

- **36 rendered anchor occurrences / 25 distinct destinations:** 26 occurrences of 15 internal destinations, eight external web links (seven inherited references plus provenance), and two contact actions.
- **Distinct-anchor classification:** 18 relevant, two broken, two obsolete as current references, and three uncertain (one reference's evidentiary suitability plus two contact actions).
- **HTTP availability for the eight current external web links:** six returned `200`; two ended in `404`. The initial NaturalNews web-tool timeout was resolved by successful direct retrieval.
- **Additional resources:** four local resources present; one canonical production check uncertain; 14 source image URLs checked, with four `200` and ten access-restricted `403` results.
- **Five proposed reference changes await approval (E2, E3, E5, E6, E7). Zero website links changed.**
