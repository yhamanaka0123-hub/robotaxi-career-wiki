# Robotaxi Career Wiki — a personal wiki CLI with local Gemma + RAG

A personal wiki for one question I actually have: **how do I get a strategy / BD job in the robotaxi
industry as an international MBA student who needs H-1B sponsorship?** It combines public sources on
the industry and US work visas with my own career notes, and a command-line harness I built that
talks to a **local Gemma model with no internet**.

`wiki` has five commands: `chat` (a personal assistant), `ask` (cited factual answers), `search`
(raw passages, no model), `ingest` (build the wiki), and `status`.

**Quick links:**
[CLI code](wiki_cli/) · [Wiki vault](vault/) · [index.md](vault/index.md) · [Source Catalog](vault/Source%20Catalog.md) ·
[Four ask-mode evidence cards](#evidence) · [Mode checks](evidence/cards/Mode%20Checks.md) ·
[Offline transcript](evidence/offline/20260927-180516/transcript.txt) · [Screenshots](evidence/screenshots/)

---

## 1. Purpose and sources

**Intended use:** plan my recruiting (target companies, visa timeline) and check facts before I use them
in networking or interviews.

| Source ID | Original (unchanged) in `vault/raw/` | Wiki note | Origin |
|---|---|---|---|
| `wiki-robotaxi` | `Robotaxi - Wikipedia.md` | `wiki/Industry/Robotaxi Industry.md` | Wikipedia rev 1376189687, CC BY-SA 4.0 |
| `wiki-waymo` | `Waymo - Wikipedia.md` | `wiki/Companies/Waymo.md` | Wikipedia rev 1375874211, CC BY-SA 4.0 |
| `wiki-zoox` | `Zoox - Wikipedia.md` | `wiki/Companies/Zoox.md` | Wikipedia rev 1375140099, CC BY-SA 4.0 |
| `wiki-h1b` | `H-1B visa - Wikipedia.md` | `wiki/Visas/H-1B Visa.md` | Wikipedia rev 1376524309, CC BY-SA 4.0 |
| `wiki-opt` | `Optional Practical Training - Wikipedia.md` | `wiki/Visas/Optional Practical Training.md` | Wikipedia rev 1372810333, CC BY-SA 4.0 |
| `personal-career-notes` | `My Career Notes.md` | `wiki/Career/My Career Plan.md` | my own notes |

- Wikipedia articles were downloaded once, online, by [`tools/fetch_wikipedia.py`](tools/fetch_wikipedia.py)
  (plain-text extract, saved byte-for-byte; SHA-256 checked after every step). The file extension is `.md`
  only so Obsidian can open and link them; the text is the unmodified extract.
- [`sources.json`](sources.json) is the machine catalog: source ID → raw file, URL + revision, license,
  **readable note name**, and topic aliases. The human version is [`vault/Source Catalog.md`](vault/Source%20Catalog.md).
- How originals connect to pages: every note has `source_id` / `source_file` / `source_url` properties,
  each key fact ends with a link to the raw file and section (`— [[raw/Zoox - Wikipedia|…]] § History`),
  and a **Sources** section at the bottom.

## 2. Setup and device

### Device (measured, see `evidence/offline/.../transcript.txt` step 0)

| | |
|---|---|
| OS | Windows 11 Pro 10.0.26200, with WSL2 Ubuntu 26.04 LTS (kernel 6.18.33.2) for the CLI |
| CPU | AMD Ryzen 7 PRO 7840U, 8 cores / 16 threads |
| RAM | 14.7 GB total on the host (WSL is given 7.1 GB). Free while testing: **0.9–1.2 GB** (browser etc. open) |
| GPU | AMD Radeon 780M, integrated, shared memory. **Not used**: Ollama reports `size_vram: 0`, so inference is CPU-only |
| Disk | C: 276 GB free |

### Model and runtime

| | |
|---|---|
| Generation model | **`gemma4:e2b`** (Gemma 4 E2B, 5.1B total parameters), **Q4_K_M**, Ollama digest `7fbdbf8f5e45`, 7.2 GB file |
| Embedding model | `embeddinggemma` (EmbeddingGemma 308M, BF16), 621 MB file |
| Runtime | **Ollama 0.34.3** for Windows, reached from WSL at `http://localhost:11434` |
| Harness | Python 3.14.4, **standard library only** (no pip packages) |
| Official source | [Gemma docs](https://ai.google.dev/gemma/docs/core); weights from the Ollama library (`ollama pull gemma4:e2b`, `ollama pull embeddinggemma`) |

**Why E2B:** this is a CPU-only laptop with 14.7 GB RAM that is also running a browser and other apps.
E2B is the smallest Gemma 4 model, and it answered all four tests (see evidence) at 15–25 s per answer.
E4B needs about 1.6 GB more just to load (4.5 vs 2.9 GB in the Gemma docs), and I had only 0.9–1.2 GB free. I also expect it to be slower on CPU. I did not measure E4B.
26B A4B needs more than 14 GB just to load. Note that Ollama's `gemma4:e2b` is bigger than the "~2.9 GB at
Q4_0" figure in the Gemma docs: the Ollama build is Q4_K_M and includes the vision and audio encoders.

### Measured memory and time (local, offline)

| Measurement | Value | How |
|---|---|---|
| Model memory reported by runtime | gemma4:e2b **6.87 GB** (context 8192) + embeddinggemma **0.68 GB** | `GET /api/ps` (transcript step 2) |
| Model process on Windows | `llama-server`: 3.78 GB private, 1.69 GB resident | `Get-Process` after an ask (rest is memory-mapped / paged) |
| CLI process | ≈ 38 MB max RSS | `/usr/bin/time` |
| Ingest, all 6 sources | 290–422 s (35–90 s per note + ≈ 40 s to embed 242 passages) | `evidence/runs/*-ingest.md` |
| Ingest, 1 source offline | **102.7 s** (63.4 s Gemma, rest re-indexing) | transcript step 2 |
| Ask (one answer) | **20–28 s wall** (≈ 3 s query expansion + 16–25 s answer) | transcript steps 4–7 |
| Chat turn | 13–18 s without lookup, 30–38 s with lookup | chat transcript |
| First call after idle | +17 s to load the model | development test |

### Install (while online)

```bash
# 1. Install Ollama (Windows app: https://ollama.com/download) and pull the models
ollama pull gemma4:e2b
ollama pull embeddinggemma
# 2. If the CLI runs in WSL and Ollama on Windows: let WSL reach Windows localhost
#    C:\Users\<you>\.wslconfig  ->  [wsl2]  networkingMode=mirrored   then: wsl --shutdown
# 3. Get the project (Python 3.10+ only, no packages)
git clone <this repo> personal-wiki && cd personal-wiki
./wiki status          # checks runtime and model
# 4. Build the search index (.index/ is not committed). Reviewed notes are kept, so this
#    only re-embeds the 242 raw passages (~45 s); Gemma is not called.
./wiki ingest ./vault/raw
```

Before going offline, `./wiki status` must show the model, quantization, and `embeddings ok`.

### Commands

```bash
./wiki --help                                    # commands, configuration, required inputs
./wiki ingest ./vault/raw                        # all sources -> notes, index.md, Source Catalog, search index
./wiki ingest "./vault/raw/Zoox - Wikipedia.md" --force   # one source; --force regenerates a reviewed note
./wiki search "H-1B cap master's degree"         # original passages + paths, no model answer
./wiki ask "Which company owns Zoox?" --mode local
./wiki chat                                      # Navi; /help /notes /ask /save /reset /exit
./wiki status
./tools/offline_demo.sh                          # the full offline demonstration, saved to evidence/offline/
python3 tools/retrieval_check.py <label>         # retrieval-only check of the four tests
```

Settings can be overridden with environment variables (`WIKI_MODEL`, `WIKI_TOP_K`, `WIKI_VECTOR_WEIGHT`,
`WIKI_QUERY_EXPANSION`, `WIKI_ASK_THINK`, `WIKI_OLLAMA_URL`). Errors are handled: a missing path prints
`Missing file: …`, and a stopped runtime prints `Local model unavailable: … Start Ollama …` within ~10 s.
**Online mode:** not implemented; `--mode online` exits with a message. Local is the only mode.

## 3. Architecture

| Part | What it is here | Code |
|---|---|---|
| **Model** | Gemma 4 E2B. It only turns the text my code sends into text; it does not read files or remember anything | [`llm.py`](wiki_cli/llm.py) (the only file that calls Ollama) |
| **Retrieval tool** | Local index of 242 raw-source passages; BM25 + EmbeddingGemma vectors, fused by reciprocal rank | [`sources.py`](wiki_cli/sources.py), [`retrieval.py`](wiki_cli/retrieval.py) |
| **RAG workflow** | Retrieve passages → put them in the prompt with research rules → Gemma answers with `[S#]` citations | [`ask.py`](wiki_cli/ask.py) |
| **Harness** | Everything around it: mode selection, instructions per mode, chat history, when to retrieve, prompt assembly, citation checks, errors, saved evidence | [`__main__.py`](wiki_cli/__main__.py), [`chat.py`](wiki_cli/chat.py), [`ingest.py`](wiki_cli/ingest.py), [`evidence.py`](wiki_cli/evidence.py) |
| **CLI** | The `./wiki` launcher + argparse subcommands | [`wiki`](wiki), [`__main__.py`](wiki_cli/__main__.py) |

Instructions are plain files, and the harness loads the right one for each mode:
[`persona.md`](instructions/persona.md) (chat voice and real capabilities),
[`wiki-instructions.md`](instructions/wiki-instructions.md) (research rules for ask),
[`chat-router.md`](instructions/chat-router.md), [`query-expansion.md`](instructions/query-expansion.md),
[`ingest-instructions.md`](instructions/ingest-instructions.md).

### One path traced: `./wiki ask "Which company owns Zoox, and how much did it pay to acquire it?"`

1. `wiki` → `python3 -m wiki_cli` → `main()` parses `ask`, checks `--mode local`, and prints the model line from `llm.runtime_info()`.
2. `ask.run_ask()` loads the index (`.index/passages.jsonl`, `vectors.json`) and warns if a raw file changed since indexing.
3. `expand_queries()` sends `query-expansion.md` + the question to Gemma (temperature 0). It gets back
   `["Zoox ownership", "Zoox acquisition details"]`.
4. `retrieve_for_question()` runs `Index.search()` for all 3 queries. Each search computes BM25 over the passage
   text, embeds the query with EmbeddingGemma, computes cosine similarity against the 242 stored vectors, and
   fuses the two rankings (`1/(60+rank_bm25) + 2·1/(60+rank_vector)`). It keeps the best 6 passages.
5. The prompt is: **system** = `wiki-instructions.md`; **user** = question + passages numbered `[S1]…[S6]`
   with source path and section + the question repeated. That is ≈ 1,300 tokens, sent to `llm.chat()` with no
   chat history and no persona.
6. `check_citations()` parses the `[S#]` citations. It flags citations to passages that were not retrieved,
   sentences without a citation, and numbers that do not appear in the cited passage.
7. The CLI prints the answer, all 6 sources (`*` marks the cited ones), and the check. `evidence.save_run()`
   writes `evidence/runs/<time>-ask.json` and `.md`.

### How each mode differs (enforced in code)

| | chat | ask | search |
|---|---|---|---|
| Instructions | `persona.md` | `wiki-instructions.md` | none |
| Conversation history | last 6 messages | **never** | – |
| Retrieval | only when needed: an edit request ("make that shorter", "translate…") skips it by rule; otherwise `chat-router.md` asks Gemma for `{"notes": bool, "query"}`; `/notes` forces it | always (+ query expansion) | always |
| Model call | yes, temperature 0.7 | yes, temperature 0 | **no** (works with Ollama stopped: BM25 only) |
| Output | reply + sources if retrieved | answer + `[S#]` citations + automatic check, or `INSUFFICIENT EVIDENCE` | passages + paths + line numbers |

Chat history is kept only in memory and in the evidence transcript. It is never indexed, so a claim made
in chat cannot become evidence for ask (tested: [Mode Checks §4](evidence/cards/Mode%20Checks.md)).
`/save` writes a draft to `evidence/drafts/`, outside the vault, with a "not source evidence" header.

## 4. Design choices

- **Passages:** the text is split by section headings (`== History ==` / `## Situation`); References and
  External links sections are skipped. Paragraphs within one section are grouped up to about 900 characters
  (≈ 225 tokens), and each passage keeps its path, section path, and **line numbers**, so a citation can be
  checked by opening the raw file at that line.
- **Context sent to Gemma:** ask sends 6 passages, ≈ 1,300 prompt tokens total, in an 8,192-token window. Chat
  sends 4 passages plus 6 history messages. Ingest sends the full introduction plus the first paragraph of
  each section, up to 7,000 characters (≈ 1,750 tokens). The whole wiki is never sent.
- **Retrieval method:** hybrid, because the tests showed each method alone misses something. BM25 finds exact
  names and numbers; embeddings handle paraphrases. The final settings came from measurements, not guesses.
  Vector weight 2, top 6, and Gemma-written extra queries fixed Tests 2 and 3
  ([retrieval v1 → v3](evidence/ask-iterations.md)).
- **Research rules (ask):** answer only from the passages; cite each sentence; reply `INSUFFICIENT EVIDENCE`
  when the passages do not answer; report disagreement; match by meaning, not wording; neutral voice. The
  question is repeated after the passages, because that fixed a false "insufficient" answer from E2B.
- **Persona (chat):** "Navi", an upbeat, practical MBA-classmate voice, with an honest list of what it can and
  cannot do. It must cite wiki facts and label its own ideas as suggestions.
- **Model settings that changed results:** temperature 0 for ask and ingest (same answer on reruns).
  `think: false`: Gemma 4 thinking fixed Test 2 but broke Test 3 and took 56 s instead of 16 s, so it is
  off by default (`WIKI_ASK_THINK=1` turns it on).

### Wiki naming, folders, links, and re-ingestion

- **Filenames come from `sources.json`, never from the model**: `Waymo.md`, `H-1B Visa.md`,
  `My Career Plan.md`. The first heading equals the filename. Machine IDs (`wiki-zoox`, passage IDs)
  live only in properties and the catalog.
- **Folders:** `wiki/Industry`, `wiki/Companies`, `wiki/Visas`, `wiki/Career`. These are the four kinds of
  things the wiki is about. `raw/` holds the originals. Code, index, logs, and tests live outside `vault/`.
- **Links are grounded:** a related-note link is kept only if the source text actually mentions the other
  topic (catalog aliases). The reason shown next to each link is Gemma's explanation when it proposed the
  link, or else the source sentence quoted. This removed a meaningless Waymo → H-1B link from the first run
  ([review log](evidence/review-log.md)).
- **Re-ingest without duplicates:** the harness finds a note by its `source_id` property. That works even if
  the note was moved or renamed, and the harness rewrites that same file. Notes marked `reviewed: true` are
  kept as they are unless you pass `--force`. Checked three ways: a full re-ingest (6 notes "updated"), a
  single re-ingest of a reviewed note ("kept", identical checksums), and an offline `--force` re-ingest of
  Zoox (still 6 notes).
- **Link check:** every `[[wikilink]]` in the vault resolves to exactly one file; no duplicate note names; every note's first heading equals its filename (checked by script).
- **Review:** each generated note was compared against the raw text. Corrections were made in the wiki, never
  in `raw/`. Examples: Gemma left out the current 24-month STEM OPT rule, wrote a summary claim the notes
  did not make, and explained a Zoox→Waymo link with its own guess instead of the source. My own review also
  made a mistake: I wrongly "corrected" a statistic that Gemma had copied correctly, then reverted it after
  re-checking the source. See [evidence/review-log.md](evidence/review-log.md).

### Obsidian

Open `vault/` itself as the vault (on Windows: `C:\Users\yhama\personal-wiki\vault`).
Note: I first tried to open it through `\\wsl.localhost\Ubuntu\…`. Obsidian cannot watch WSL network paths
(`EISDIR`), so the project lives on `C:` and WSL uses the symlink `~/personal-wiki`.

| Screenshot | Shows |
|---|---|
| [obsidian-index.png](evidence/screenshots/obsidian-index.png) | `index.md` landing page grouped by topic, with short descriptions |
| [obsidian-note-top.png](evidence/screenshots/obsidian-note-top.png), [obsidian-note-bottom.png](evidence/screenshots/obsidian-note-bottom.png) | `wiki/Career/My Career Plan`: matching heading, source properties, key facts with source links, related notes with reasons, Sources |
| [obsidian-raw-source.png](evidence/screenshots/obsidian-raw-source.png) | After clicking the source link: the original `raw/My Career Notes` |
| [obsidian-graph.png](evidence/screenshots/obsidian-graph.png) | Graph view, **filter `path:wiki/`, Attachments off**: 6 readable labels; My Career Plan links to all topics; Waymo–Zoox–Robotaxi Industry; H-1B Visa–OPT |
| [obsidian-graph-all.png](evidence/screenshots/obsidian-graph-all.png) | Unfiltered: notes, index, Source Catalog, and raw originals |

Traces checked in Obsidian:
1. `index` → [[My Career Plan]] → Sources link → `raw/My Career Notes` (screenshots above).
2. Through a related note: [[My Career Plan]] → Related notes → [[Optional Practical Training]]
   ([obsidian-trace-related-note.png](evidence/screenshots/obsidian-trace-related-note.png)) → fact source link →
   `raw/Optional Practical Training - Wikipedia` ([obsidian-trace-raw-source.png](evidence/screenshots/obsidian-trace-raw-source.png)).
   The raw text on screen shows the 115,651 "non-STEM" sentence that I first wrongly "corrected" (see review log).

## 5. Evidence

All runs used **gemma4:e2b Q4_K_M via Ollama 0.34.3, local, with the internet disconnected**, on the data above.
Proof of offline: [transcript step 0](evidence/offline/20260927-180516/transcript.txt)
(`ping: Network is unreachable`, `https://www.google.com unreachable`). Terminal screenshots from the same offline run:
[proof of offline](evidence/screenshots/offline-01-proof.png) · [ask tests 2–3](evidence/screenshots/offline-02-ask-tests.png) · [chat: "make that shorter" + made-up claim](evidence/screenshots/offline-03-chat.png) · [end of run](evidence/screenshots/offline-99-end.png).

| Test | Question | Result | Card |
|---|---|---|---|
| 1 · one source | Which company owns Zoox, and how much did it pay to acquire it? | ✅ Amazon, over $1.2 billion, June 26, 2020 [S2] | [Test 1](evidence/cards/Test%201%20-%20Zoox%20Owner.md) |
| 2 · different wording | If I finish a graduate degree at an American university, is there a separate H-1B quota…? | ✅ 65,000 + 20,000 for U.S. master's or higher = 85,000 [S5] | [Test 2](evidence/cards/Test%202%20-%20Graduate%20H-1B%20Quota.md) |
| 3 · two sources | After I graduate from my MBA, how long can I work on OPT before I need an H-1B? | ⚠️ Partial: 12 months, then 24-month STEM extension → 36 months [S2][S6], but it also lists the outdated 17-month rule without flagging it and does not apply my notes | [Test 3](evidence/cards/Test%203%20-%20OPT%20Before%20H-1B.md) |
| 4 · unsupported | Does Moove sponsor H-1B visas for its employees? | ✅ `INSUFFICIENT EVIDENCE` | [Test 4](evidence/cards/Test%204%20-%20Moove%20Sponsorship.md) |

- **Chat and search checks:** [Mode Checks](evidence/cards/Mode%20Checks.md). Covers capability questions with no
  lookup, a draft followed by "make that shorter" using the conversation, search with no generated answer, and a
  claim made only in chat that is not used by ask.
- **Improvement history (failures kept):** [retrieval v1 → v3](evidence/retrieval/) and
  [answer iterations](evidence/ask-iterations.md). Every earlier run is still in `evidence/runs/`.
- **Offline demonstration:** [`tools/offline_demo.sh`](tools/offline_demo.sh) →
  [transcript](evidence/offline/20260927-180516/transcript.txt). It covers help, status, ingest, search, the
  four asks, chat, ask after chat, and error messages.
- Test expectations are in [`tests/questions.md`](tests/questions.md), outside the searchable vault.

## 6. Reflection

**A real failure: the assistant believed an unverified claim.** In the offline chat check I typed a
*made-up test sentence* (not a real statement by anyone): "my manager told me Moove will definitely sponsor my H-1B." Navi answered "Since the sponsorship is secured…" and
suggested dropping the sponsorship concern. My own notes say the opposite: I should recruit elsewhere
*because* I need a sponsor. The router also ran an unneeded lookup and showed four unrelated H-1B passages.

- **Cause:** the persona only forbids *inventing* personal facts. It says nothing about facts the user states
  in chat. A 2B-scale model follows the latest message strongly. The retrieved passages did not contradict the
  claim directly, so nothing pushed back.
- **Proposed improvement:** add a rule to `persona.md`: "Treat new facts the user states in chat as unverified;
  say they are not in the wiki yet and offer `/save`." Also have the router pull `My Career Notes` whenever a
  message concerns the user's own situation, so the reply can point out the conflict. Then rerun Mode Check §4.

**A second limitation: outdated evidence and single-source reasoning (Test 3).** The H-1B article still
describes the 2008 17-month STEM extension, which conflicts with the OPT article's 2016 24-month rule. E2B
listed both without saying which is current, and did not apply my "STEM OPT eligible" note. A concrete fix
would be to store the section date or revision in each passage and tell the model to prefer the newer rule.
Another option is to try E4B for ask only, if memory allows.

---
*Sources: Wikipedia articles are CC BY-SA 4.0 (links and revisions in the catalog). Model weights are not
included in this repository.*
