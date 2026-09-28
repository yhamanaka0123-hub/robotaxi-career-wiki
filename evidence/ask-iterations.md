# Ask-Mode Iterations (development runs, online machine, local model)

All runs: gemma4:e2b (Q4_K_M) via Ollama 0.34.3, local execution. Earlier failing results are kept in
`evidence/runs/` and are not replaced. Final offline evidence is recorded separately.

## Step 1 — Retrieval (checked before judging answers)
See `evidence/retrieval/`.

| Version | Settings | T1 Zoox l.7 | T2 H-1B l.6 / l.104 | T3 OPT l.4 |
|---|---|---|---|---|
| v1-baseline | BM25 + vector equal weight, top 5, no expansion | rank 4 | missing / missing | missing |
| v2-vector-weight-2 | vector weight 2 | rank 2 | rank 4 / missing | missing |
| v2-query-expansion | Gemma writes 2 extra keyword queries | rank 2 | missing / missing | missing |
| v2-both | both | rank 2 | rank 5 / missing | rank 5 |
| **v3-final** | both + top 6 + expansion at temperature 0 | rank 2 | rank 5 / missing | rank 6 |

Cause: in T2 the embedding model ranked the right passages #1 and #2, but BM25 ranked them #20 and #109
because the question's words ("graduate degree", "American university") differ from the source's
("master's degree", "U.S. institution"); equal-weight fusion buried them.

## Step 2 — Answers (retrieval fixed at v3-final)

| Run | Prompt change | T1 | T2 | T3 | T4 |
|---|---|---|---|---|---|
| 172852 / 172937 / 173000 / 172911 | research rules v1, temp 0.2 | ✅ | ❌ "INSUFFICIENT EVIDENCE" although [S5] had the answer | ⚠️ gave 29 and 36 months, no conflict noted | ✅ |
| 173048 / 173112 | + rules 6–8 (disagreement, match by meaning, apply to user) | – | ❌ still "not contain", wrong format | ❌ only old 17/29-month rule |
| 173155 / 173215 | temp 0 | – | ❌ | ⚠️ 12 + 17 + 24 → 36 months |
| 173314 / 173414 | temp 0 + Gemma thinking (≈56 s) | – | ✅ | ❌ only 29 months |
| **173457 / 173651(think)** | **question repeated after the passages** | ✅ (re-run) | ✅ 65,000 + 20,000 [S5] | ✅ 12 months, 17-month (old), 24-month → 36 months [S2][S4][S6] | ✅ (re-run) |

Chosen: temperature 0, thinking off (≈16 s instead of ≈56 s), question repeated after passages.

Note on honesty: an earlier draft of rule 7 used the exact wording of Test 2 as its example
("graduate degree" ↔ "master's degree"). That would tune the prompt to the test, so it was replaced
with unrelated examples ("work permit" ↔ "employment authorization") before any run.

## Remaining weakness
T3 still does not say the two STEM-extension figures conflict or apply the rule to "my" situation from
My Career Notes, even though rule 8 asks for it. E2B tends to list facts rather than reason across sources.
