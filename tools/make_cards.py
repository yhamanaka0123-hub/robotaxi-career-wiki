"""Build the four ask-mode evidence cards from saved offline run records (no model calls).
Retrieved passages and answers are copied verbatim from evidence/runs/*.json;
the expectation and the human assessment are written by hand below."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNS = ROOT / "evidence" / "runs"
OUT = ROOT / "evidence" / "cards"
TRANSCRIPT = "../offline/20260927-180516/transcript.txt"

CARDS = [
    {
        "file": "Test 1 - Zoox Owner.md", "run": "20260927-180735-ask",
        "type": "Direct question answered by one source",
        "expected": "`raw/Zoox - Wikipedia.md` line 7: \"On June 26, 2020, Amazon and Zoox signed a definitive merger agreement, under which Amazon acquired Zoox as a wholly owned subsidiary for over $1.2 billion.\"",
        "retrieval": "PASS — the expected passage (line 7) is [S2]. [S3] (line 1, \"subsidiary of Amazon\") also supports ownership.",
        "claims": [
            ("Amazon acquired Zoox as a wholly owned subsidiary", "S2", "yes — line 7"),
            ("merger agreement signed on June 26, 2020", "S2", "yes — line 7"),
            ("for over $1.2 billion", "S2", "yes — line 7"),
        ],
        "verdict": "**PASS.** Correct, complete, every claim cited to the right passage. No outside knowledge used.",
    },
    {
        "file": "Test 2 - Graduate H-1B Quota.md", "run": "20260927-180759-ask",
        "type": "Answerable question phrased differently from the source",
        "expected": "`raw/H-1B visa - Wikipedia.md` line 6 (also line 104): \"...capped at 65,000, with an additional 20,000 visas available for individuals who have earned a master's degree or higher from a U.S. institution, for a total of 85,000.\"",
        "retrieval": "PASS — line 6 is inside [S5] (lines 5-6), ranked 5th of 6. Line 104 was not retrieved. The question says \"graduate degree at an American university\"; the source says \"master's degree or higher from a U.S. institution\". In the first version of retrieval (v1) neither passage was in the top 5 — see `evidence/retrieval/`.",
        "claims": [
            ("regular cap of 65,000 initial H-1B visas per fiscal year", "S5", "yes — line 6"),
            ("additional 20,000 for master's degree or higher from a U.S. institution", "S5", "yes — line 6"),
            ("total of 85,000", "S5", "yes — line 6"),
        ],
        "verdict": "**PASS.** Correct and cited. It answers \"is there a separate quota\" implicitly (it describes the extra 20,000) rather than saying \"yes\" first, and the second sentence repeats the first. "
                   "History: with the first research rules this same retrieval produced a wrong \"INSUFFICIENT EVIDENCE\" (run 20260927-172937, kept). Fixed by repeating the question after the passages — see `evidence/ask-iterations.md`.",
    },
    {
        "file": "Test 3 - OPT Before H-1B.md", "run": "20260927-180828-ask",
        "type": "Question connecting two sources (personal notes + OPT article)",
        "expected": "`raw/My Career Notes.md` lines 9-11 (\"UC Berkeley Haas MBA ... graduating in May 2027\", \"eligible for STEM OPT\") and `raw/Optional Practical Training - Wikipedia.md` line 4 (\"24-month extension ... a total of 36 months of OPT\"). Expected answer: up to 36 months, because I am STEM OPT eligible.",
        "retrieval": "PASS — both expected passages were retrieved: [S3] career notes and [S6] OPT line 4. Also retrieved: [S4] H-1B line 169-170 with the outdated 2008 17-month rule (the known risk written down before testing).",
        "claims": [
            ("The duration of OPT depends on the type of degree and extensions available.", "none", "no citation — general framing sentence; flagged by the automatic check"),
            ("OPT is a year for most people", "S2", "yes — lines 41-42"),
            ("2008: 17-month STEM extension, part of the H-1B Cap-Gap Regulations", "S4", "yes — line 169 (but outdated)"),
            ("24-month extension, total of 36 months for STEM graduates", "S6", "yes — line 4"),
        ],
        "verdict": "**PARTIAL PASS.** The key fact (36 months total with the 24-month STEM extension) is correct and cited. Failures: (1) it did not use [S3] to apply the rule to me (\"you are STEM OPT eligible, so up to 36 months\"), although rule 8 asks for this; "
                   "(2) it lists the old 17-month rule without saying the 2016 24-month rule replaced it; (3) one uncited opening sentence. Cause: the E2B model lists facts from passages instead of reasoning across them; the H-1B article contains outdated text.",
    },
    {
        "file": "Test 4 - Moove Sponsorship.md", "run": "20260927-180847-ask",
        "type": "Plausible question the wiki cannot answer",
        "expected": "No source says whether Moove sponsors H-1B visas. Career notes only say I work at Moove and need a sponsoring employer. Expected: an explicit insufficient-evidence statement, no guess.",
        "retrieval": "As expected, the closest passages were retrieved ([S1], [S5] career notes about Moove and sponsorship; H-1B passages about sponsorship in general). None states Moove's policy.",
        "claims": [
            ("INSUFFICIENT EVIDENCE — passages do not state whether Moove sponsors", "—", "correct: verified that no raw file contains Moove + sponsorship policy"),
        ],
        "verdict": "**PASS.** Explicit insufficient-evidence response; no guess. Also re-checked after typing the made-up test claim \"my manager told me Moove will definitely sponsor my H-1B\" in chat: ask still answered INSUFFICIENT EVIDENCE (see `Mode Checks.md`).",
    },
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for c in CARDS:
        r = json.loads((RUNS / f"{c['run']}.json").read_text())
        m = r["model"]
        lines = [
            f"# {c['file'][:-3]}", "",
            "| | |", "|---|---|",
            f"| Question | {r['question']} |",
            f"| Test type | {c['type']} |",
            "| Mode | `wiki ask ... --mode local` (standalone: no chat history, no persona) |",
            f"| Execution | **local, internet disconnected** — see [offline transcript]({TRANSCRIPT}) |",
            f"| Model | {m['model']} ({m.get('parameters')}, {m.get('quantization')}, digest {m.get('digest')}) via Ollama {m.get('runtime_version')} |",
            f"| Retrieval | {r['retrieval_method']}; top {r['settings']['top_k']}; queries: {', '.join(repr(q) for q in r['queries'])} |",
            f"| Time | {r['timing_seconds']} s answer generation · {r['prompt_tokens']} prompt tokens · {r['output_tokens']} output tokens |",
            f"| Raw record | [{c['run']}.md](../runs/{c['run']}.md) · [{c['run']}.json](../runs/{c['run']}.json) |",
            "", "## Expected evidence (written before testing, in `tests/questions.md`)", "", c["expected"],
            "", "## Retrieved passages", "", c["retrieval"], "",
            "| Cite | Source path | Section | Lines | Passage (start) |", "|---|---|---|---|---|",
        ]
        for h in r["retrieved"]:
            text = h["text"].replace("\n", " ").replace("|", "\\|")
            lines.append(f"| {h['cite']} | `{h['path']}` | {h['section']} | {h['lines']} | {text[:160]}… |")
        lines += ["", "## Actual Gemma answer", "", *["> " + l for l in r["answer"].splitlines()], "",
                  f"Automatic citation check: `{r['citation_check']['status']}`", "",
                  "## Citation check by hand (opened each cited passage in the raw file)", "",
                  "| Claim in answer | Cited | Supported by the cited passage? |", "|---|---|---|"]
        lines += [f"| {a} | {b} | {v} |" for a, b, v in c["claims"]]
        lines += ["", "## Assessment", "", c["verdict"], ""]
        (OUT / c["file"]).write_text("\n".join(lines), encoding="utf-8")
        print("wrote", c["file"])


if __name__ == "__main__":
    main()
