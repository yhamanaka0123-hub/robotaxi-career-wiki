# Wiki Page Rules (ingest)

You turn one source document into material for one wiki note about the subject named below.

Rules:
1. Use only the source text provided. Do not add outside knowledge.
2. Write for a person browsing their notes: plain, clear English.
3. "summary": 2–3 sentences on what the subject is and why it matters.
4. "facts": 5–8 specific, checkable facts (dates, numbers, names, places). Copy numbers exactly as written in the source. For each fact, give the section heading it came from, exactly as shown in the source (use "Introduction" for text before the first heading).
5. "related": pick only from the list of other notes provided. For each, give one sentence explaining the real connection, based on the source text. If there is no real connection, leave it out. An empty list is fine.

Reply with JSON only, in this shape:
{"summary": "...", "facts": [{"fact": "...", "section": "..."}], "related": [{"note": "...", "why": "..."}]}
