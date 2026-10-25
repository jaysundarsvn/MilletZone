# Content migration notes

The normalized [content.json](./content.json) preserves 25 non-order source pages from [the original export](../millet_zone_vscode/export/data/pages.json), captured on 25 October 2026. The original export is unchanged. Every page keeps its original source URL; image blocks keep their source `asset_key`. The 12 recipe detail pages and recipe index are all present.

## Editorial scope and exclusions

- The order page, prices, flour surcharges, bundles, shipping charges, product-list and order prompts, and purchase links are excluded.
- The products page is presented as an educational millet guide. Grain names, photographs, source nutrition figures and attributed descriptions remain; unrelated oils, copper plates, jaggery, honey, seed powder and toiletries catalog sections are omitted.
- Sales testimonials, homepage promotional fragments, Wix gallery placeholders, stale component anchors, repeated decorative images and exact adjacent extraction duplicates are omitted. Homepage duplicate history/health paragraphs appear once.
- Identical recipe steps occurring in separate recipes remain: the rice page contains multiple complete recipes. No serving counts, preparation durations, calorie calculations or missing instructions have been invented.
- Explicit rhetoric discouraging medical treatment and unsupported allegations about healthcare/corporate conspiracies are omitted. Remaining health material must be displayed as attributed historical source content with the `health_claims` notice, never as newly verified editorial advice. This includes about, home, millet guide, FAQs, health notes, protocols, plant references and health testimonials.
- Therapeutic claims are unverified; no clinical review was performed. Cancer recovery timelines, disease cures, organ cleansing, claimed glucose-release periods and similar assertions must not appear as homepage promises or recommendation snippets. Attribution does not establish accuracy. Health archive material is not a substitute for medical care.
- Feedback is attributed to the original community page; identities and outcomes are not independently verified.
- Source replacement-character punctuation was normalized to apostrophes; whitespace was collapsed. Original wording and recipe quantities otherwise remain. Some source grammar and terminology are retained.
- Learning-resource URLs have trailing nonbreaking-space encodings removed and duplicate/misattached language links removed. External links were not independently validated. Source labels can disagree about video language.

## Incomplete or uncertain content

- **Cookies:** the misleading original `copy-of-whole-grain-bread-with-siri` slug becomes `cookies-with-siri-dhanya`. It is a distinct Foxtail cookie page, not a bread duplicate. Only Foxtail flour, chickpea flour, suji and ghee are supplied; quantities and method are absent.
- **Bread:** the heading names Browntop millet while ingredients and method name Foxtail. The ingredient list says two cups of wheat flour but the method references another cup. Retain the source and show this inconsistency; do not silently choose values.
- **Upma/pongal:** the detail page supplies a pongal method; it does not supply a separate complete upma recipe. The page title now reflects the available pongal recipe.
- **Nutrition:** the products page lists nutrient figures but does not establish their serving basis, testing method, raw/cooked state or provenance. Do not label them per 100 g or otherwise imply a verified basis. The figures are source values pending review.
- **Allergens:** bread, poori and cookies contain wheat; some recipes include milk, curd, ghee, nuts or sesame. Do not apply blanket gluten-free, vegan or allergy-safe labels to the recipe collection.
- **Preparation:** soaking and water ratios differ by recipe. Those source-specific instructions remain. No food-safety or nutritional verification was performed, including fermentation and botanical-use instructions.
- **Health protocol introduction:** an unfinished ?Text to be expanded? placeholder was removed. References to PDF books remain as source context, but no book PDFs were supplied.
- **Contact:** the main Gachibowli/Shaikpet details remain as a source listing. Outlet 2 remains explicitly inactive. ?Coming up? locations are labeled historical proposals with opening status unconfirmed. Source hours/contact details have not been independently confirmed.
- **Media:** the extraction report lists 164 unique image URLs, 151 downloaded images and 13 not downloaded. Some remaining source assets may therefore be unavailable. Embedded video links are preserved, not downloaded.

## Normalization counts

- adjacent extraction duplicate: 49
- commerce or stale anchor link: 3
- commerce text: 6
- decorative image: 78
- duplicate link: 19
- empty block: 2
- homepage duplicate paragraph: 1
- homepage sales copy: 34
- order page excluded: 1
- product promotion: 21
- sales testimonial or treatment-displacing claim: 15
- stock gallery image: 10
- template or navigation text: 16
- treatment-displacing rhetoric: 4
- unrelated catalog section: 30
- unsupported treatment or conspiracy rhetoric: 4

| Source page | Source blocks | Retained blocks |
| --- | ---: | ---: |
| upma-and-pongal-with-siri | 21 | 19 |
| feedback | 35 | 14 |
| about | 68 | 58 |
| rice-with-siri-dhanya | 157 | 148 |
| spicy-dishes-with-siri-dhanya | 50 | 48 |
| natural-health-tips | 127 | 123 |
| links | 110 | 86 |
| whole-grain-bread-with-siri-dhanya | 41 | 40 |
| faqs | 66 | 57 |
| roti-s-with-siri-dhanya | 30 | 29 |
| disease | 820 | 819 |
| biryani-and-pulav-with-siri-dhanya | 106 | 103 |
| copy-of-whole-grain-bread-with-siri | 15 | 10 |
| lemon-rice-with-siri-dhanya | 30 | 29 |
| home | 98 | 48 |
| disease-protocols | 161 | 113 |
| products | 144 | 80 |
| kashya | 105 | 105 |
| idly-with-siri-dhanya | 29 | 27 |
| recipes | 51 | 48 |
| dosa-with-siri-dhanya | 20 | 17 |
| poori-with-siri-dhanya | 17 | 16 |
| cancer | 250 | 250 |
| contact-us | 55 | 50 |
| sweets-with-siri-dhanya | 57 | 56 |
