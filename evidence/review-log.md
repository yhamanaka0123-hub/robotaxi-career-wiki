# Wiki Review Log

Generated notes were checked line by line against the unchanged originals in `vault/raw/`.
Corrections were made in `vault/wiki/`, never in `vault/raw/`. After review, each note's frontmatter
was set to `reviewed: true`, so a later `wiki ingest` keeps the reviewed text unless `--force` is used.

## Ingest run 1 (evidence/runs/20260927-172036-ingest.md) — problems found, fixed in code

| Note | Problem | Fix |
|---|---|---|
| Waymo | Linked to [[H-1B Visa]] with the reason "This note is not directly connected to Waymo" — a meaningless link | Code: a related link is kept only if the source text actually mentions the other topic (`aliases` in `sources.json`) |
| Robotaxi Industry, My Career Plan | Missing links: Robotaxi had none; the career note only linked Waymo although the notes mention Zoox, H-1B, OPT | Code: add links for every mention, quoting the source sentence as the reason |
| My Career Plan | Written as "the author" | Code: personal notes are written in the first person |
| index.md | H-1B description cut at "U.S." (abbreviation treated as a sentence end) | Code: sentence splitter ignores periods after capitals |

## Ingest run 2 (evidence/runs/20260927-172658-ingest.md) — manual corrections

| Note | Generated text | Source says | Correction |
|---|---|---|---|
| Optional Practical Training | "In 2021, there were 115,651 new **non-STEM** OPT authorizations" | line 29: "In 2021, there were 115,651 new OPT authorizations" | ~~Removed the invented "non-STEM"~~ **Reverted — this was my review error, see below** |
| Optional Practical Training | Listed only the 2008 **17-month** STEM extension (outdated) | line 4: 2016 rule allows a **24-month** extension, "a total of 36 months of OPT"; replaces the 17-month extension | Added the 24-month / 36-month fact |
| My Career Plan | Summary said I work on strategy "for robotaxi companies" (not stated) | lines 4–6: BD intern at Moove; Moove is a fleet operations partner for robotaxi companies; work covers international expansion and GTM execution | Reworded to match the source |
| My Career Plan | Recruiting fact dropped the reason | line 18: "…because I need an employer that will sponsor my H-1B" | Restored the reason |

## Offline demo re-ingest (evidence/runs/20260927-180711-ingest.md, `--force`, offline)

The offline demo regenerated `Zoox.md` in place (same filename, still 6 notes). Diff against the
reviewed version: wording changes only, all facts identical. One correction:

| Note | Generated text | Source says | Correction |
|---|---|---|---|
| Zoox | Link to [[Waymo]]: "similar to the work done by Waymo" (model's inference) | "This launch directly accelerates Zoox's competition against Waymo" | Reason now states the competition, as in the source (line 31: the Nov 2025 San Francisco launch). My first fix wrongly said "Las Vegas"; caught by re-checking line 31 and corrected. |

## Correction of my own review (found while taking Obsidian screenshots)

I first marked "non-STEM" as invented by Gemma because I only checked line 29 of the OPT article.
Line 1 (Introduction, the section Gemma cited) says: "In 2021, there were 115,651 new **non-STEM** OPT
authorizations, a 105% increase from a decade prior." Gemma copied it correctly, so I restored the original
wording. The raw article is inconsistent with itself (line 1 says "non-STEM", line 29 does not).
Lesson: check every occurrence of a number in the source, not just the first one I find.

## Checked and correct (no change)
- Waymo: 10 US metro areas, 3,871 robotaxis, 500,000 paid rides/week, 200 million miles, $11B by 2024, $16B at $126B valuation (lines 1, 3); co-CEOs since April 2021 (line 45).
- Zoox: Amazon subsidiary, Foster City HQ, ~50 robotaxis (Jan 2026), founded 2014, first CA approval Dec 2018, $800M at $3.2B.
- Robotaxi Industry: SAE level 4/5 definition, 2023 congestion, 2018 Uber fatality, 2025 financial loss, AAA 13%, costs $400,000 / $180,000 / $0.30 per mile.
- H-1B Visa: 65,000 + 20,000 = 85,000 cap (line 6), 3-year initial / 6-year max stay, INA definition (line 2), 583,420 (2019), 265,777 approvals (2022).

## Known limitation kept visible
`H-1B visa - Wikipedia.md` line 169 still describes the old 17-month STEM extension ("up to 29 months"),
which conflicts with the OPT article. The original is kept unchanged; the OPT note records the current rule.
