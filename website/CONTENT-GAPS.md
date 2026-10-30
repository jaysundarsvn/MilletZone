# Source content gaps and section repairs

This audit compares [content.json](./content.json) with the supplied [original page export](../millet_zone_vscode/export/data/pages.json). [content_rendering.py](./content_rendering.py) reorganizes source material without inventing plant descriptions, testimonial explanations, nutritional interpretations or medical claims. The original source claims remain subject to the site's attribution notice.

## Empty sections repaired

- **Meet the millets source guide:** the initial row of grain names was navigation-like text, while the actual grain names and content were later stored as paragraphs. Six complete sections now pair Little, Foxtail, Browntop, Kodo, Barnyard and Proso with their existing names, figures, source descriptions and available images. Proso remains in this source article; its presence on the main Millets page is a separate decision.
- **Community voices:** the source stored every quotation line as a heading. Nine neutral, numbered comment summaries now contain the full source quotations. Wrapped lines are rejoined, including “I liked all the easy recipes / on the site.thanx.” and “Super Grains.... / Feel like eating / the dishes as soon as / they are made”. The final “- Yoga Teacher” attribution stays with its adjacent quotation. No new testimony or outcome claim is added.
- **Cancer protocol archive:** only the exact leading “Various CANCERS and PROTOCOLS” heading is removed because its body was empty before the next heading. The following introduction and all 14 condition sections remain. The three trailing charts are grouped separately, rather than being attributed solely to the final Uterine Cancer section. Source conditions: Breast; Lung; Bone; Brain; Blood; Kidney/Prostate; Mouth; Thyroid/Glands; Stomach; Skin; Intestinal; Oesophageal; Liver; Uterine.
- **Protocol introduction:** the five components, instructions, decoction preparation, oil references, millet preparation, Ambali discussion and related conditions are substantive groups. Consecutive labels and the condition index no longer create empty disclosures. Existing related source links remain available to the build caller.
- **Original FAQs:** 11 numbered original questions link to their answer sections. The goitrogen question had been removed by earlier normalization, although a later answer paragraph remained. Its exact original question is restored in the renderer to prevent that paragraph being attached to the preceding question. The remaining answer is labeled partial; the removed text is not recreated.

## Decoctions and plant references

The source provides an inventory of names followed by 26 illustrated entries. It supplies no entry-specific preparation or explanatory prose for those entries. Each illustrated entry now retains its source name/aliases, corresponding available photographs and an explicit missing-description note. The two consecutive Black Plum / Syzygium headings belong to one entry. Punarnava includes the existing note distinguishing the white and red varieties; it is retained beneath the images.

The illustrated entries with missing explanatory prose are:

1. Tinospora cordifolia or Tippa teega/Guduchi
2. Betel leaf/paan ki patta/Tamalapaaku
3. PEEPAL/PEEPUL Leaves/ Raavi
4. TURMERIC Root+ Plant/ Pasupu
5. PONGAMIA/Kaanuga
6. Sadaapa or Ruta g.
7. Punarnava or Boerhavia diffusa or TELLA/Erra GALIJERU
8. ALOE VERA/Kalabanda
9. MINT/Pudina
10. Coriander/Cilantro/Dhaniya
11. SENNA/Tangedu
12. Methi/Fenugreek/Menthulu
13. BRYOPHYLLUM/Rana paala
14. PAPAYA/Boppayi
15. Cynodon Dactylon/Doob/Garika
16. Cinnamon/Dalchini
17. Indian GOOSE BERRY/ AMLA/Usiri
18. Curry leaf/ Karivepaku
19. BANANA TREE TRUNK CORE/ ARATI DUTA
20. HOLY BASIL/ TULASI
21. Ash Gourd/Boodida Gummadi
22. Guava fruit & Leaf/Jaama
23. Ginger/Allam/Adrak
24. MORINGA / DRUM STICK / MUNAGA Leaves, Flowers
25. Black Plum / Kala Jamoon, / Neredu/ Syzygium jambolanum
26. Eetha / Mauritia flexuosa

These additional names occur in the initial inventory without a corresponding labeled photo entry or description on that page:

- Cactus/Prickly Pear/NagaJemudu
- Tamarind leaf sprouts (Chinta chiguru), also written Tamrind Leaves (Chintachiguru)
- Sour hibiscus/Gongura
- Neem (vepa)
- Pepper (Miriyalu)
- Bacopa monnieri (Bramhi)
- Carrot eaten raw/Juice
- Dill weed/ Shata pushpi
- Tomato juice/ leaf decoction
- Coccinea leaf decoction (Tinde)
- Paarijatam/ Nyctanthes arbor-tristis/... Harshringaar
- BEL tree leaf/Maaredu/Bilva Patra
- SARPAGANDHA/Rawolfia serpentina

No images or plant-use guidance are inferred for these names. Botanical spelling and identification are source values, not independent confirmations.

## Learning resources

Resource cards keep their original source titles, attached language lines/descriptions and URLs. Logical groups are talks, grains/nutrition, cooking, articles and additional references. A title-only record is labeled as having no separate description; no summary is generated from an unvisited destination. The caller should not append its generic link/video list on this page because this renderer includes all supplied links and the embedded video.

- “Dr KHADER's TALK - Telugu: with English SUBTITLES : 'WHAT ARE WE EATING'?” is paired with the existing embedded video URL from this page.
- “ANCIENT WISDOM & MODERN SCIENCE - PART 2 BY DR B M HEGDE” has malformed visible text (`ttps:// www.youtube.com/watch?v=9cVcVLFn2Sw`). Its original exported hyperlink is `http://www.youtube.com/watch?v=9cVcVLFn2Sw`; that href is used without replacing the destination, and the malformed source text remains visible.
- The following source records provide a URL but no supplied title or description: the Deccan Chronicle article ending `use-millets-bid-bye-to-lifestyle-disorders-surgeons-nutritionist.html`; the New Indian Express article ending `millet-does-a-rajini-rises-from-dust-to-rule-the-city-1594671.html`; the Millet Zone Facebook photo ending `388073131534667/?type=3&theater`; the Health and Love Page link ending `okra-water-the-secret-weapon-against-diabetes/?c=dhp`; and YouTube video IDs `WPhG6lx3MKU`, `RJqzNqmFejQ`, `VlpZwXvCGYw`, `ndWXeGapeog` (the last retains `&t=5s`). These remain labeled untitled source links.
- The source associates the same two video URLs (`hoX0kRoj2Qg` and `M_f-4VBskZU`) with different language labels. Both source labels are preserved; the language inconsistency is unresolved.
- Repeated water-filter descriptions are source text. Their claims are not independently verified.
- External destinations, availability, video contents and language have not been independently validated in this structural repair.

## Other known source gaps

- **Foxtail cookies:** only four ingredients; no quantities or method.
- **Whole grain millet bread:** heading names Browntop while ingredients/method use Foxtail; flour quantities disagree.
- **Upma and pongal:** source details a pongal recipe, without a separate upma method.
- **Grain nutrition figures:** no serving size or raw/cooked measurement basis supplied.
- **PDF books:** titles and email references exist, but the actual books were not supplied.

See [CONTENT-NOTES.md](./CONTENT-NOTES.md) for the earlier migration exclusions and source limitations.
