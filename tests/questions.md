# Ask-Mode Test Set (written before implementing retrieval)

Kept outside `vault/` so the harness can never retrieve this answer key.
All four are run with `wiki ask ... --mode local`, independent of chat history.

## Test 1 — direct, one source
**Question:** Which company owns Zoox, and how much did it pay to acquire it?
**Expected source:** `vault/raw/Zoox - Wikipedia.md`, line 7
> On June 26, 2020, Amazon and Zoox signed a definitive merger agreement, under which Amazon acquired Zoox as a wholly owned subsidiary for over $1.2 billion.

**Expected answer:** Amazon; over $1.2 billion (agreement signed June 26, 2020).

## Test 2 — paraphrased wording
**Question:** If I finish a graduate degree at an American university, is there a separate H-1B quota I can apply under?
**Expected source:** `vault/raw/H-1B visa - Wikipedia.md`, line 6 (also line 104)
> The number of initial H-1B visas issued each fiscal year is capped at 65,000, with an additional 20,000 visas available for individuals who have earned a master's degree or higher from a U.S. institution, for a total of 85,000.

**Expected answer:** Yes — 20,000 additional visas for U.S. master's-or-higher holders, on top of the regular 65,000 cap (85,000 total).
**Wording check:** question says "graduate degree at an American university" / "separate quota"; source says "master's degree or higher from a U.S. institution" / "additional 20,000".

## Test 3 — connects two sources
**Question:** After I graduate from my MBA, how long can I work in the US on OPT before I need an H-1B?
**Expected sources:**
- `vault/raw/My Career Notes.md` — "UC Berkeley Haas MBA program, graduating in May 2027" and "I am eligible for STEM OPT after graduation."
- `vault/raw/Optional Practical Training - Wikipedia.md`, line 4
> ...apply for a 24-month extension of their post-completion OPT, giving STEM graduates a total of 36 months of OPT.

**Expected answer:** Up to 36 months total (12 months standard OPT + 24-month STEM extension), because the notes say you are STEM OPT eligible. Should cite both sources.
**Known risk:** `H-1B visa - Wikipedia.md` line 169 describes the older 17-month extension ("up to 29 months"). If retrieval picks that passage, the answer may be outdated — record it if it happens.

## Test 4 — unsupported (expected: insufficient evidence)
**Question:** Does Moove sponsor H-1B visas for its employees?
**Why unsupported:** The career notes say I work at Moove and need H-1B sponsorship, but no source says whether Moove sponsors. Wikipedia sources do not mention Moove.
**Expected answer:** An explicit statement that the sources do not say whether Moove sponsors H-1B visas. Must not guess.
