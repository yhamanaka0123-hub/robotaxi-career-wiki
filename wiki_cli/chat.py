"""Chat mode: Navi, the personal assistant.

Per turn: slash command? -> router decides if notes are needed -> (retrieve) ->
persona + recent conversation + (passages) -> local Gemma -> reply + sources.
Conversation history is context only; it is never saved as source evidence.
"""
import datetime
import json
import re
import sys

from . import ask, config, evidence, llm, prompts
from .retrieval import Index

CHAT_TOP_K = 4
# Messages about the user themself ("based on my background") must also search the personal notes;
# otherwise a company name in the request pulls only that company's passages.
ABOUT_ME = re.compile(r"\b(my|me|mine|myself)\b|\bI\b|私|自分", re.I)
PERSONAL_SOURCE = "personal-career-notes"
# Requests to edit the previous reply never need the wiki; decided in code, before asking the model.
EDIT_REQUEST = re.compile(
    r"^(make (it|that|this)|shorten|shorter|longer|rewrite|rephrase|simplify|translate|summari[sz]e (it|that)|"
    r"more (formal|casual|concise)|less formal|turn (it|that) into|in (japanese|english)|短く|長く|翻訳|言い換え)",
    re.I)
HELP = """Chat commands:
  /help            show this list
  /notes <query>   force a wiki lookup for your next reply
  /ask <question>  run a strict, standalone ask (no chat history, no persona)
  /save            save Navi's last reply as a draft (evidence/drafts/, not a source)
  /reset           clear the conversation
  /exit            quit"""


class ChatSession:
    def __init__(self, out=print):
        self.out = out
        self.system = prompts.load_instructions("persona")
        self.router_rules = prompts.load_instructions("chat-router")
        self.history: list[dict] = []
        self.index = None
        self.info = llm.runtime_info()
        self.transcript: list[str] = []
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        config.EVIDENCE.mkdir(parents=True, exist_ok=True)
        self.transcript_path = config.EVIDENCE / f"{stamp}-chat.md"
        self._log(f"# Chat session {stamp}\n\n- **Mode:** chat (persona: Navi)\n"
                  f"- **Model:** {evidence.model_line(self.info)}\n")

    # ----- decisions -----

    def route(self, message: str) -> dict:
        """Decide whether this turn needs the wiki: edits of the last reply are handled in code;
        otherwise Gemma decides using the router rules and the most recent turns."""
        if self.history and EDIT_REQUEST.search(message.strip()):
            return {"notes": False, "query": "", "by": "rule: edit of previous reply"}
        recent = "\n".join(f"{m['role']}: {m['content'][:300]}" for m in self.history[-2:])
        r = llm.chat([{"role": "system", "content": self.router_rules},
                      {"role": "user", "content": f"Recent conversation:\n{recent or '(none)'}\n\n"
                                                  f"Latest message: {message}"}],
                     temperature=0.0, json_mode=True)
        try:
            d = json.loads(r["text"])
            return {"notes": bool(d.get("notes")), "query": str(d.get("query") or message), "by": "router"}
        except json.JSONDecodeError:
            return {"notes": False, "query": "", "by": "router (unreadable reply)"}

    def retrieve(self, query: str, message: str = "") -> list[dict]:
        self.index = self.index or Index()
        hits, _ = self.index.search(query, k=CHAT_TOP_K)
        if ABOUT_ME.search(message) and not any(h["passage"].source_id == PERSONAL_SOURCE for h in hits):
            mine, _ = self.index.search(f"my background current role situation goals {query}", k=40)
            mine = [h for h in mine if h["passage"].source_id == PERSONAL_SOURCE][:2]
            hits = mine + hits[: CHAT_TOP_K - len(mine)]
        return hits

    # ----- one turn -----

    def turn(self, message: str, force_query: str | None = None) -> str:
        self.out("  (Navi is thinking… replies take 15–40 s on this laptop; please wait)")
        decision = ({"notes": True, "query": force_query, "by": "/notes"} if force_query
                    else self.route(message))
        hits = self.retrieve(decision["query"], message) if decision["notes"] else []

        user_content = message
        if hits:
            user_content += ("\n\n---\nWiki passages retrieved for this message (cite as [S1] etc.; "
                             "they are the only verified facts):\n\n" + prompts.format_passages(hits))
        messages = ([{"role": "system", "content": self.system}]
                    + self.history[-config.CHAT_HISTORY_TURNS:]
                    + [{"role": "user", "content": user_content}])
        result = llm.chat(messages, temperature=config.CHAT_TEMPERATURE)
        reply = result["text"]

        # history keeps the plain message, not the passages, to save context space
        self.history += [{"role": "user", "content": message},
                         {"role": "assistant", "content": reply}]

        check = ask.check_citations(reply, hits) if hits else None
        route_note = (f"notes lookup: yes — query “{decision['query']}” ({decision['by']})" if hits
                      else f"notes lookup: no ({decision['by']})")
        self.out(f"\nNavi › {reply}\n")
        if hits:
            self.out("  Sources:")
            for n, h in enumerate(hits, start=1):
                self.out(f"    [S{n}] {h['passage'].label()}")
            if check["invalid"]:
                self.out(f"  ! cites passages that were not retrieved: {check['invalid']}")
        self.out(f"  ({route_note} · {result['seconds']}s)\n")

        self._log(f"\n**You:** {message}\n\n_{route_note}_\n\n**Navi:** {reply}\n")
        if hits:
            self._log("\nSources shown:\n" + "\n".join(
                f"- [S{n}] `{h['passage'].label()}`" for n, h in enumerate(hits, start=1)) + "\n")
        return reply

    # ----- commands -----

    def save_last(self) -> None:
        last = next((m["content"] for m in reversed(self.history) if m["role"] == "assistant"), None)
        if not last:
            self.out("Nothing to save yet.")
            return
        config.DRAFTS.mkdir(parents=True, exist_ok=True)
        path = config.DRAFTS / f"{datetime.datetime.now():%Y%m%d-%H%M%S}-draft.md"
        path.write_text("<!-- Generated by Navi (chat). A draft, NOT source evidence; "
                        "never indexed for ask/search. -->\n\n" + last + "\n", encoding="utf-8")
        self.out(f"Saved draft to {path.relative_to(config.ROOT)}")
        self._log(f"\n_/save → {path.relative_to(config.ROOT)}_\n")

    def handle(self, line: str) -> bool:
        """Process one input line. Returns False when the user wants to quit."""
        cmd, _, arg = line.partition(" ")
        if cmd in ("/exit", "/quit"):
            return False
        if cmd == "/help":
            self.out(HELP)
        elif cmd == "/reset":
            self.history.clear()
            self.out("Conversation cleared.")
            self._log("\n_/reset — conversation cleared_\n")
        elif cmd == "/save":
            self.save_last()
        elif cmd == "/notes":
            self.turn(arg or "Summarize what my notes say.", force_query=arg or "career notes")
        elif cmd == "/ask":
            r = ask.run_ask(arg)
            self.out(format_ask(r))
            self._log(f"\n**/ask (standalone, no chat history):** {arg}\n\n{r['answer']}\n\n"
                      f"_citation check: {r['citation_check']['status']} · saved {r['saved_to']}_\n")
        elif cmd.startswith("/"):
            self.out(f"Unknown command {cmd}. Type /help.")
        else:
            self.turn(line)
        return True

    def _log(self, text: str) -> None:
        self.transcript.append(text)
        self.transcript_path.write_text("".join(self.transcript), encoding="utf-8")


def format_ask(r: dict) -> str:
    c = r["citation_check"]
    lines = ["", r["answer"], "", "Sources:"]
    for h in r["retrieved"]:
        mark = "*" if h["cite"] in c["cited"] else " "
        lines.append(f" {mark}[{h['cite']}] {h['path']} § {h['section']} (lines {h['lines']})")
    lines += ["", f"Citation check: {c['status']}   (* = cited in answer)"]
    if c["uncited_sentences"]:
        lines.append(f"  sentences without citation: {len(c['uncited_sentences'])}")
    if c["numbers_not_in_cited_passages"]:
        lines.append(f"  numbers not found in cited passages: {c['numbers_not_in_cited_passages']}")
    lines.append(f"Saved: {r['saved_to']}")
    return "\n".join(lines)


def run_chat() -> None:
    session = ChatSession()
    interactive = sys.stdin.isatty()
    print(f"Navi · chat mode · {evidence.model_line(session.info)}")
    print("Hi! I'm Navi, your robotaxi-career assistant. Type /help for commands, /exit to quit.\n")
    while True:
        try:
            line = input("you › ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not interactive:
            print(line)  # echo piped input so transcripts read naturally
        if not line:
            continue
        try:
            if not session.handle(line):
                break
        except llm.ModelUnavailable as e:
            print(f"! {e}")
    print(f"Transcript saved: {session.transcript_path.relative_to(config.ROOT)}")
