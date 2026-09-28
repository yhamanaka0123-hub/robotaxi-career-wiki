# Test 1 - Zoox Owner

| | |
|---|---|
| Question | Which company owns Zoox, and how much did it pay to acquire it? |
| Test type | Direct question answered by one source |
| Mode | `wiki ask ... --mode local` (standalone: no chat history, no persona) |
| Execution | **local, internet disconnected** — see [offline transcript](../offline/20260927-180516/transcript.txt) |
| Model | gemma4:e2b (5.1B, Q4_K_M, digest 7fbdbf8f5e45) via Ollama 0.34.3 |
| Retrieval | hybrid (BM25 + EmbeddingGemma, RRF), 3 queries; top 6; queries: 'Which company owns Zoox, and how much did it pay to acquire it?', 'Zoox ownership', 'Zoox acquisition details' |
| Time | 17.8 s answer generation · 1272 prompt tokens · 38 output tokens |
| Raw record | [20260927-180735-ask.md](../runs/20260927-180735-ask.md) · [20260927-180735-ask.json](../runs/20260927-180735-ask.json) |

## Expected evidence (written before testing, in `tests/questions.md`)

`raw/Zoox - Wikipedia.md` line 7: "On June 26, 2020, Amazon and Zoox signed a definitive merger agreement, under which Amazon acquired Zoox as a wholly owned subsidiary for over $1.2 billion."

## Retrieved passages

PASS — the expected passage (line 7) is [S2]. [S3] (line 1, "subsidiary of Amazon") also supports ownership.

| Cite | Source path | Section | Lines | Passage (start) |
|---|---|---|---|---|
| S1 | `raw/Zoox - Wikipedia.md` | Progress and competition | 23-23 | In December 2018, Zoox became the first company to gain approval for providing self-driving transport services to the public in California. By July 2018, accord… |
| S2 | `raw/Zoox - Wikipedia.md` | History | 7-7 | In January 2019, Zoox appointed a new CEO, Aicha Evans, who was previously the Chief Strategy Officer at Intel. On June 26, 2020, Amazon and Zoox signed a defin… |
| S3 | `raw/Zoox - Wikipedia.md` | Introduction | 1-1 | Zoox, Inc. is an American technology company subsidiary of Amazon developing driverless vehicles that provide mobility as a service. It is headquartered in Fost… |
| S4 | `raw/Zoox - Wikipedia.md` | History | 6-6 | Zoox was founded in 2014 by Australian artist-designer Tim Kentley-Klay and Jesse Levinson, son of Apple Incorporated chairman Arthur D. Levinson, who was devel… |
| S5 | `raw/Zoox - Wikipedia.md` | Progress and competition | 31-31 | On November 18, 2025, Zoox launched its robotaxi service to the public in San Francisco, marking a significant step in the company’s commercial progress. Operat… |
| S6 | `raw/Zoox - Wikipedia.md` | Progress and competition | 24-24 | On March 20, 2019, Tesla, Inc. filed a lawsuit against Zoox and several now-former Tesla employees (who left Tesla for employment at Zoox) alleging theft of Tes… |

## Actual Gemma answer

> Amazon acquired Zoox as a wholly owned subsidiary in a merger agreement signed on June 26, 2020, for over $1.2 billion [S2].

Automatic citation check: `ok: every sentence cites a retrieved passage`

## Citation check by hand (opened each cited passage in the raw file)

| Claim in answer | Cited | Supported by the cited passage? |
|---|---|---|
| Amazon acquired Zoox as a wholly owned subsidiary | S2 | yes — line 7 |
| merger agreement signed on June 26, 2020 | S2 | yes — line 7 |
| for over $1.2 billion | S2 | yes — line 7 |

## Assessment

**PASS.** Correct, complete, every claim cited to the right passage. No outside knowledge used.
