# The UW collections behind the test set

The test pages are drawn from four collections held by the UW–Madison Libraries / UW Digital Collections Center (UWDC). Source material is almost entirely high-resolution TIFF scans; the challenge distributes web-friendly derivatives. This page is background for participants — knowing what these documents *are* helps you transcribe them.

## Wisconsin Land Survey Field Notes (`survey_notes`)

https://search.library.wisc.edu/digital/ASurveyNotes

The original field notebooks from the U.S. public land survey of Wisconsin, roughly 1830s–1860s: surveyors walking section lines and recording bearings, chain distances, witness trees, soil and timber notes. A mixed collection of field notes and accompanying plat maps — **only the field notes are in scope**; plat maps are not transcribed.

What makes them hard: hand-drawn tables and column layouts, terse domain abbreviations (`N 40 E`, `sec.`, chain/link units), pencil on weathered paper, sketches and diagrams interleaved with text. These notebooks still get real patron use (property research, ecological baselines), which is why they anchor the challenge. If you fine-tune on anything, ~100 curated pages of the drawn tables could yield significant gains here.

## Max Kade Institute German letters (`kade_letters`)

https://digital.library.wisc.edu/1711.dl/KadeLetters

Correspondence of German immigrants to Wisconsin, 19th–early 20th century, held by the Max Kade Institute. Written largely in **Kurrent** — the pre-1940 German cursive script whose letterforms differ fundamentally from English cursive (an English-trained recognizer does not transfer). Some letters in the collection (notably the Sternberger and Seifert correspondence) have existing transcriptions produced by the MKI's Kurrent reading group, which is part of what makes verified ground truth possible for this category. The Alfred Escher correspondence (see [RESOURCES.md](../RESOURCES.md)) is the closest public training match.

## Dominy Craftsmen account books (`dominy_accounts`)

https://digital.library.wisc.edu/1711.dl/Dominy

Account books of the Dominy family of East Hampton woodworkers and clockmakers, late 18th–19th century. Dense ledger layouts: names, dates, goods, and pre-decimal currency in ruled columns. The challenge here is less the handwriting than **preserving tabular content faithfully in reading order**.

## Native American treaty documents (`treaties_microfilm`)

https://digital.library.wisc.edu/1711.dl/TreatiesMicro

19th-century handwritten documents relating to Native American treaties in Wisconsin, digitized **from microfilm** — meaning low contrast, blown highlights, and film artifacts on top of formal 19th-century clerical hands. This category is in the test set specifically to measure robustness to degraded reproduction media, which is a large fraction of what real archives hold.

## Why these four

Together they cover what actually varies in the archives: different hands and eras, prose vs. tabular layouts, direct scans vs. microfilm, English vs. German. The macro-averaged metric makes each category count equally — a deployable pipeline has to handle all of it.
