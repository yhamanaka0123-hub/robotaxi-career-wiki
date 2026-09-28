# Test 2 - Graduate H-1B Quota

| | |
|---|---|
| Question | If I finish a graduate degree at an American university, is there a separate H-1B quota I can apply under? |
| Test type | Answerable question phrased differently from the source |
| Mode | `wiki ask ... --mode local` (standalone: no chat history, no persona) |
| Execution | **local, internet disconnected** — see [offline transcript](../offline/20260927-180516/transcript.txt) |
| Model | gemma4:e2b (5.1B, Q4_K_M, digest 7fbdbf8f5e45) via Ollama 0.34.3 |
| Retrieval | hybrid (BM25 + EmbeddingGemma, RRF), 3 queries; top 6; queries: 'If I finish a graduate degree at an American university, is there a separate H-1B quota I can apply under?', 'H-1B visa quota', 'post-graduate employment visa eligibility' |
| Time | 21.2 s answer generation · 1474 prompt tokens · 99 output tokens |
| Raw record | [20260927-180759-ask.md](../runs/20260927-180759-ask.md) · [20260927-180759-ask.json](../runs/20260927-180759-ask.json) |

## Expected evidence (written before testing, in `tests/questions.md`)

`raw/H-1B visa - Wikipedia.md` line 6 (also line 104): "...capped at 65,000, with an additional 20,000 visas available for individuals who have earned a master's degree or higher from a U.S. institution, for a total of 85,000."

## Retrieved passages

PASS — line 6 is inside [S5] (lines 5-6), ranked 5th of 6. Line 104 was not retrieved. The question says "graduate degree at an American university"; the source says "master's degree or higher from a U.S. institution". In the first version of retrieval (v1) neither passage was in the top 5 — see `evidence/retrieval/`.

| Cite | Source path | Section | Lines | Passage (start) |
|---|---|---|---|---|
| S1 | `raw/H-1B visa - Wikipedia.md` | Eligibility and application process > Employment | 21-21 | To maintain H-1B visa status, visa holders must maintain employment with their sponsoring employer. If employment ends, the individual must either leave the U.S… |
| S2 | `raw/H-1B visa - Wikipedia.md` | History > The Immigration Act of 1990 | 124-124 | President George H. W. Bush signed the Immigration Act of 1990 into law by on November 20, 1990. The H-1 visa was split into the H-1A visa for nurses, and the H… |
| S3 | `raw/H-1B visa - Wikipedia.md` | Eligibility and application process > Specialty occupation | 17-17 | H-1B visas, as defined by United States Code, are those jobs that require a "theoretical and practical application of a body of highly specialized knowledge" an… |
| S4 | `raw/H-1B visa - Wikipedia.md` | Criticism > Limitations for entrepreneurs and self-employed consultants | 355-355 | Entrepreneurs do not qualify for the H-1B visa. The United States immigration system's EB-5 visa program does permit foreign entrepreneurs to apply for a green … |
| S5 | `raw/H-1B visa - Wikipedia.md` | Introduction | 5-6 | (B) attainment of a bachelor's degree or higher degree in the specific specialty (or its equivalent) as a minimum for entry into the occupation in the United St… |
| S6 | `raw/H-1B visa - Wikipedia.md` | Maintaining status > Dependents of visa holders | 81-82 | H-1B visa holders can bring immediate family members, such as their spouse and children under 21, to the United States as dependents under the H-4 visa category… |

## Actual Gemma answer

> The number of initial H-1B visas available each fiscal year is capped at 65,000, with an additional 20,000 visas available for individuals who have earned a master's degree or higher from a U.S. institution, for a total of 85,000 [S5]. This additional allocation is for individuals who have earned a master's degree or higher from a U.S. institution [S5].

Automatic citation check: `ok: every sentence cites a retrieved passage`

## Citation check by hand (opened each cited passage in the raw file)

| Claim in answer | Cited | Supported by the cited passage? |
|---|---|---|
| regular cap of 65,000 initial H-1B visas per fiscal year | S5 | yes — line 6 |
| additional 20,000 for master's degree or higher from a U.S. institution | S5 | yes — line 6 |
| total of 85,000 | S5 | yes — line 6 |

## Assessment

**PASS.** Correct and cited. It answers "is there a separate quota" implicitly (it describes the extra 20,000) rather than saying "yes" first, and the second sentence repeats the first. History: with the first research rules this same retrieval produced a wrong "INSUFFICIENT EVIDENCE" (run 20260927-172937, kept). Fixed by repeating the question after the passages — see `evidence/ask-iterations.md`.
