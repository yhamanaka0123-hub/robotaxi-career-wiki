# Mode Checks: Chat, Search, Ask Separation

Run offline (internet disconnected) on 2026-09-27 as part of `tools/offline_demo.sh`.
Model: gemma4:e2b (5.1B, Q4_K_M) via Ollama 0.34.3, local.
Full output: [offline transcript](../offline/20260927-180516/transcript.txt) ·
chat transcript: [20260927-180848-chat.md](../runs/20260927-180848-chat.md) ·
search record: [20260927-180714-search.md](../runs/20260927-180714-search.md)

## 1. Chat: capability questions (no lookup expected)

| Input | Lookup? | Result | Pass? |
|---|---|---|---|
| `what can you help me with?` | no (router) | Introduced itself as Navi; listed brainstorming/planning, drafting, comparing Waymo vs Zoox, and pulling facts from the notes; asked where to start. No citations, no refusal. | ✅ |
| `what can we do?` | no (router) | Offered concrete starting points (industry deep dive, career strategy, H-1B/OPT, networking, interview prep). No lookup, no "insufficient evidence". | ✅ |

Minor issues: Navi said it can help "refine your resume", but it cannot read a resume unless the user pastes it. Its recruiting plan gave its own ideas (e.g. "Broaden the Net") without the "Suggestion:" label that `persona.md` asks for.

## 2. Chat: draft, then "make that shorter"

| Input | Lookup? | Result | Pass? |
|---|---|---|---|
| `draft a short plan for my recruiting this fall, based on my notes` | **yes** (router), 4 passages, all from `raw/My Career Notes.md` | 3-phase plan; facts about target roles, Waymo/Zoox, Moove experience and H-1B need cited [S1]–[S4], matching the career notes. | ✅ |
| `make that shorter` | **no** (rule: edit of previous reply) | Condensed the previous plan to 4 bullets, keeping its citations. Used the conversation, not a new search. | ✅ |

Earlier development run (online, 20260927-173750-chat.md): the router alone sent "make that shorter" to a notes lookup and showed
unrelated H-1B/OPT passages. Fixed by a rule in `wiki_cli/chat.py` (`EDIT_REQUEST`) that skips retrieval for edit requests; this offline run confirms the fix.

## 3. Search: original passages, no answer

`./wiki search "H-1B cap master's degree"` → header `search · retrieval only, no model answer`; six passages shown verbatim with
path, section and line numbers, e.g. `[S2] raw/H-1B visa - Wikipedia.md § Annual cap (lines 104-111)`:
"The H-1B visa program is subject to an annual cap of 65,000 visas, with an additional 20,000 visas available for applicants holding advanced degrees from U.S. institutions…". No generated text. ✅

Search without the model: with `WIKI_OLLAMA_URL` pointing at a closed port, `wiki search` still returns passages using
`keyword only (BM25) - embedding model unreachable` (tested during development).

## 4. A claim made only in chat is not evidence in ask

**Note:** "my manager told me Moove will definitely sponsor my H-1B" is a *made-up test sentence* written for this check. It is not a real statement by anyone at Moove, and it was never saved to the wiki.

| Step | Result |
|---|---|
| Chat: `By the way, my manager told me Moove will definitely sponsor my H-1B.` | Navi accepted it: "Having guaranteed sponsorship from Moove significantly de-risks that part of your plan." |
| Chat: `/ask Does Moove sponsor H-1B visas for its employees?` | **INSUFFICIENT EVIDENCE** — the ask pipeline gets no chat history. ✅ |
| New process: `./wiki ask "Does Moove sponsor H-1B visas for its employees?" --mode local` | **INSUFFICIENT EVIDENCE** ✅ |

The chat claim never reached ask, and it was not written to `vault/` (chat history is only kept in memory and in the evidence transcript).

**Failure found (chat):** Navi treated the user's unverified statement as settled fact ("Since the sponsorship is secured…") and
advised dropping the sponsorship concern, even though the notes say the opposite ("I should recruit at other companies too…
because I need an employer that will sponsor my H-1B"). The router also ran an unnecessary lookup and displayed four unrelated
H-1B passages that the reply did not use. See the README reflection for the proposed fix.

## 5. Live chat by the user (typed interactively, online, local model)

Screenshot: [chat-live-user.png](../screenshots/chat-live-user.png). The user typed both messages by hand.

| Input | Lookup? | Result | Pass? |
|---|---|---|---|
| `Draft a short networking message to someone on the Zoox strategy team, based on my background` | yes (router) — but **all 4 passages were from the Zoox article** | Navi said "I don't have your specific background details" and wrote a generic message. Labeled its draft "Suggestion". | ❌ retrieval |
| `make that shorter` | no (rule: edit of previous reply), 7.1 s | Shortened the previous draft using the conversation. | ✅ |

**Failure and fix.** The router's query ("draft networking message to Zoox strategy team based on background")
was dominated by "Zoox", so the career notes never ranked in the top 4. Fix in `wiki_cli/chat.py`: when a
message refers to the user ("my", "me", "I") and no personal passage was retrieved, the harness adds the two
best `My Career Notes` passages (`ABOUT_ME`, `PERSONAL_SOURCE`). Re-run of the same message after the fix
(piped input): sources were `[S1] My Career Notes § Current role`, `[S2] § Career goal`, `[S3]`/`[S4]` Zoox.
The draft now says "As a Business Development Intern at Moove, where I focus on international expansion and
go-to-market strategy…". Remaining weakness: the draft used these facts without `[S#]` markers.
