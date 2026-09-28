# Test 3 - OPT Before H-1B

| | |
|---|---|
| Question | After I graduate from my MBA, how long can I work in the US on OPT before I need an H-1B? |
| Test type | Question connecting two sources (personal notes + OPT article) |
| Mode | `wiki ask ... --mode local` (standalone: no chat history, no persona) |
| Execution | **local, internet disconnected** — see [offline transcript](../offline/20260927-180516/transcript.txt) |
| Model | gemma4:e2b (5.1B, Q4_K_M, digest 7fbdbf8f5e45) via Ollama 0.34.3 |
| Retrieval | hybrid (BM25 + EmbeddingGemma, RRF), 3 queries; top 6; queries: 'After I graduate from my MBA, how long can I work in the US on OPT before I need an H-1B?', 'OPT duration post-MBA', 'OPT transition to H-1B' |
| Time | 25.0 s answer generation · 1389 prompt tokens · 123 output tokens |
| Raw record | [20260927-180828-ask.md](../runs/20260927-180828-ask.md) · [20260927-180828-ask.json](../runs/20260927-180828-ask.json) |

## Expected evidence (written before testing, in `tests/questions.md`)

`raw/My Career Notes.md` lines 9-11 ("UC Berkeley Haas MBA ... graduating in May 2027", "eligible for STEM OPT") and `raw/Optional Practical Training - Wikipedia.md` line 4 ("24-month extension ... a total of 36 months of OPT"). Expected answer: up to 36 months, because I am STEM OPT eligible.

## Retrieved passages

PASS — both expected passages were retrieved: [S3] career notes and [S6] OPT line 4. Also retrieved: [S4] H-1B line 169-170 with the outdated 2008 17-month rule (the known risk written down before testing).

| Cite | Source path | Section | Lines | Passage (start) |
|---|---|---|---|---|
| S1 | `raw/Optional Practical Training - Wikipedia.md` | Support of the OPT program > Pathway to High-Skilled Immigration | 172-172 | Economists point out that OPT is a vital pathway for the high-skilled workforce in the United States. It serves as a primary step toward the H-1B visa; about 34… |
| S2 | `raw/Optional Practical Training - Wikipedia.md` | OPT Statistics > Number of OPT Students by Country | 41-42 | Since the Optional Practical Training program duration is a year for most people (though the STEM extension and cap gap allow for longer OPTs under some circums… |
| S3 | `raw/My Career Notes.md` | Situation | 9-11 | - I am an international student in the UC Berkeley Haas MBA program, graduating in May 2027. - I am eligible for STEM OPT after graduation. - I will need H-1B v… |
| S4 | `raw/H-1B visa - Wikipedia.md` | History > Executive action history > STEM Optional Practical Training extension and cap-gap extension | 169-170 | On April 2, 2008, Homeland Security Secretary Michael Chertoff announced a 17-month extension to Optional Practical Training for STEM students, as part of the H… |
| S5 | `raw/H-1B visa - Wikipedia.md` | Introduction | 9-9 | In 2025, the Trump administration imposed a $100,000 fee for filing for an H-1B visa starting September 2025 with exemptions for change of status, including tho… |
| S6 | `raw/Optional Practical Training - Wikipedia.md` | Introduction | 4-4 | On March 11, 2016, the Department of Homeland Security published a final rule allowing certain F-1 students who receive STEM degrees and who meet other specifie… |

## Actual Gemma answer

> The duration of OPT depends on the type of degree and extensions available. For most people, the Optional Practical Training program duration is a year [S2]. STEM students can potentially have a longer OPT period due to extensions; for STEM students, there was a 17-month extension for OPT as part of the H-1B Cap-Gap Regulations [S4]. Furthermore, certain F-1 students who receive STEM degrees and meet other requirements can apply for a 24-month extension of their post-completion OPT, resulting in a total of 36 months of OPT [S6].

Automatic citation check: `WARN: some claims lack matching citations`

## Citation check by hand (opened each cited passage in the raw file)

| Claim in answer | Cited | Supported by the cited passage? |
|---|---|---|
| The duration of OPT depends on the type of degree and extensions available. | none | no citation — general framing sentence; flagged by the automatic check |
| OPT is a year for most people | S2 | yes — lines 41-42 |
| 2008: 17-month STEM extension, part of the H-1B Cap-Gap Regulations | S4 | yes — line 169 (but outdated) |
| 24-month extension, total of 36 months for STEM graduates | S6 | yes — line 4 |

## Assessment

**PARTIAL PASS.** The key fact (36 months total with the 24-month STEM extension) is correct and cited. Failures: (1) it did not use [S3] to apply the rule to me ("you are STEM OPT eligible, so up to 36 months"), although rule 8 asks for this; (2) it lists the old 17-month rule without saying the 2016 24-month rule replaced it; (3) one uncited opening sentence. Cause: the E2B model lists facts from passages instead of reasoning across them; the H-1B article contains outdated text.
