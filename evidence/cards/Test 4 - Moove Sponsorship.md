# Test 4 - Moove Sponsorship

| | |
|---|---|
| Question | Does Moove sponsor H-1B visas for its employees? |
| Test type | Plausible question the wiki cannot answer |
| Mode | `wiki ask ... --mode local` (standalone: no chat history, no persona) |
| Execution | **local, internet disconnected** — see [offline transcript](../offline/20260927-180516/transcript.txt) |
| Model | gemma4:e2b (5.1B, Q4_K_M, digest 7fbdbf8f5e45) via Ollama 0.34.3 |
| Retrieval | hybrid (BM25 + EmbeddingGemma, RRF), 3 queries; top 6; queries: 'Does Moove sponsor H-1B visas for its employees?', 'Moove H-1B visa sponsorship', 'H-1B visa sponsorship policy' |
| Time | 15.8 s answer generation · 1209 prompt tokens · 26 output tokens |
| Raw record | [20260927-180847-ask.md](../runs/20260927-180847-ask.md) · [20260927-180847-ask.json](../runs/20260927-180847-ask.json) |

## Expected evidence (written before testing, in `tests/questions.md`)

No source says whether Moove sponsors H-1B visas. Career notes only say I work at Moove and need a sponsoring employer. Expected: an explicit insufficient-evidence statement, no guess.

## Retrieved passages

As expected, the closest passages were retrieved ([S1], [S5] career notes about Moove and sponsorship; H-1B passages about sponsorship in general). None states Moove's policy.

| Cite | Source path | Section | Lines | Passage (start) |
|---|---|---|---|---|
| S1 | `raw/My Career Notes.md` | Recruiting plan | 18-19 | - I should recruit at other companies too, not only Moove, because I need an employer that will sponsor my H-1B. - Companies I am considering: AV companies, inc… |
| S2 | `raw/H-1B visa - Wikipedia.md` | Introduction | 5-6 | (B) attainment of a bachelor's degree or higher degree in the specific specialty (or its equivalent) as a minimum for entry into the occupation in the United St… |
| S3 | `raw/H-1B visa - Wikipedia.md` | Eligibility and application process > Employment | 21-21 | To maintain H-1B visa status, visa holders must maintain employment with their sponsoring employer. If employment ends, the individual must either leave the U.S… |
| S4 | `raw/H-1B visa - Wikipedia.md` | Maintaining status > Dual intent | 76-77 | H-1B visas are considered "dual intent" because it is a temporary visa which gives visa holders the option to apply for permanent residency. Employers often sup… |
| S5 | `raw/My Career Notes.md` | Current role | 4-6 | - I am a Business Development Intern at Moove. - Moove is a fleet operations partner for robotaxi companies. - My work covers international expansion strategy a… |
| S6 | `raw/H-1B visa - Wikipedia.md` | Criticism > Limitations for entrepreneurs and self-employed consultants | 355-355 | Entrepreneurs do not qualify for the H-1B visa. The United States immigration system's EB-5 visa program does permit foreign entrepreneurs to apply for a green … |

## Actual Gemma answer

> INSUFFICIENT EVIDENCE
> The provided passages do not state whether Moove sponsors H-1B visas for its employees.

Automatic citation check: `insufficient evidence (reported by model)`

## Citation check by hand (opened each cited passage in the raw file)

| Claim in answer | Cited | Supported by the cited passage? |
|---|---|---|
| INSUFFICIENT EVIDENCE — passages do not state whether Moove sponsors | — | correct: verified that no raw file contains Moove + sponsorship policy |

## Assessment

**PASS.** Explicit insufficient-evidence response; no guess. Also re-checked after typing the made-up test claim "my manager told me Moove will definitely sponsor my H-1B" in chat: ask still answered INSUFFICIENT EVIDENCE (see `Mode Checks.md`).
