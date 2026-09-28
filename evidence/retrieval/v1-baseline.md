# Retrieval check: v1-baseline

top_k=5, chunk_chars=900, vector_weight=1.0, query_expansion=False

## Test 1: Which company owns Zoox, and how much did it pay to acquire it?
method: hybrid (BM25 + EmbeddingGemma, RRF)
queries: ['Which company owns Zoox, and how much did it pay to acquire it?']

1. `raw/Zoox - Wikipedia.md § Progress and competition (lines 23-23)` score=0.0325 bm25#1 vec#2 — 'In December 2018, Zoox became the first company to gain approval for providing self-drivin'
2. `raw/Zoox - Wikipedia.md § Introduction (lines 1-1)` score=0.0315 bm25#4 vec#3 — 'Zoox, Inc. is an American technology company subsidiary of Amazon developing driverless ve'
3. `raw/Zoox - Wikipedia.md § Progress and competition (lines 31-31)` score=0.0313 bm25#2 vec#6 — 'On November 18, 2025, Zoox launched its robotaxi service to the public in San Francisco, m'
4. `raw/Zoox - Wikipedia.md § History (lines 7-7)` score=0.0311 bm25#8 vec#1 — 'In January 2019, Zoox appointed a new CEO, Aicha Evans, who was previously the Chief Strat'
5. `raw/Zoox - Wikipedia.md § Technology (lines 17-18)` score=0.0308 bm25#3 vec#7 — 'Zoox develops autonomous, battery-electric vehicles targeted at the robotaxi market. The c'
- expected wiki-zoox line 7: FOUND at rank 4

## Test 2: If I finish a graduate degree at an American university, is there a separate H-1B quota I can apply under?
method: hybrid (BM25 + EmbeddingGemma, RRF)
queries: ['If I finish a graduate degree at an American university, is there a separate H-1B quota I can apply under?']

1. `raw/H-1B visa - Wikipedia.md § History > The H-1B Visa Reform Act of 2004 (lines 142-143)` score=0.0307 bm25#1 vec#10 — 'The H-1B Visa Reform Act of 2004 was a part of the Consolidated Appropriations Act, 2005, '
2. `raw/H-1B visa - Wikipedia.md § Maintaining status > Dependents of visa holders (lines 81-82)` score=0.0306 bm25#3 vec#8 — 'H-1B visa holders can bring immediate family members, such as their spouse and children un'
3. `raw/H-1B visa - Wikipedia.md § Eligibility and application process > Specialty occupation (lines 17-17)` score=0.0303 bm25#7 vec#5 — 'H-1B visas, as defined by United States Code, are those jobs that require a "theoretical a'
4. `raw/H-1B visa - Wikipedia.md § History > The Immigration Act of 1990 (lines 124-124)` score=0.0303 bm25#6 vec#6 — 'President George H. W. Bush signed the Immigration Act of 1990 into law by on November 20,'
5. `raw/H-1B visa - Wikipedia.md § History > The American Competitiveness in the 21st Century Act of 2000 (lines 132-133)` score=0.0298 bm25#2 vec#13 — 'On October 17, 2000, President Bill Clinton signed into law the American Competitiveness i'
- expected wiki-h1b line 6: MISSING from top-k
- expected wiki-h1b line 104: MISSING from top-k

## Test 3: After I graduate from my MBA, how long can I work in the US on OPT before I need an H-1B?
method: hybrid (BM25 + EmbeddingGemma, RRF)
queries: ['After I graduate from my MBA, how long can I work in the US on OPT before I need an H-1B?']

1. `raw/My Career Notes.md § Situation (lines 9-11)` score=0.0325 bm25#1 vec#2 — '- I am an international student in the UC Berkeley Haas MBA program, graduating in May 202'
2. `raw/Optional Practical Training - Wikipedia.md § Introduction (lines 1-1)` score=0.0304 bm25#2 vec#10 — 'In the United States, Optional Practical Training (OPT) is a period during which undergrad'
3. `raw/H-1B visa - Wikipedia.md § History > Executive action history > STEM Optional Practical Training extension and cap-gap extension (lines 169-170)` score=0.03 bm25#11 vec#3 — 'On April 2, 2008, Homeland Security Secretary Michael Chertoff announced a 17-month extens'
4. `raw/Optional Practical Training - Wikipedia.md § Support of the OPT program > Pathway to High-Skilled Immigration (lines 172-172)` score=0.0297 bm25#4 vec#11 — 'Economists point out that OPT is a vital pathway for the high-skilled workforce in the Uni'
5. `raw/Optional Practical Training - Wikipedia.md § Program Structure > OPT Requirements (lines 12-16)` score=0.0268 bm25#24 vec#7 — 'Any F-1 visa international student who graduates from a U.S college or university qualifie'
- expected personal-career-notes line 10: FOUND at rank 1
- expected wiki-opt line 4: MISSING from top-k

## Test 4: Does Moove sponsor H-1B visas for its employees?
method: hybrid (BM25 + EmbeddingGemma, RRF)
queries: ['Does Moove sponsor H-1B visas for its employees?']

1. `raw/My Career Notes.md § Recruiting plan (lines 18-19)` score=0.0328 bm25#1 vec#1 — '- I should recruit at other companies too, not only Moove, because I need an employer that'
2. `raw/H-1B visa - Wikipedia.md § Maintaining status > Dual intent (lines 76-77)` score=0.0318 bm25#4 vec#2 — 'H-1B visas are considered "dual intent" because it is a temporary visa which gives visa ho'
3. `raw/My Career Notes.md § Current role (lines 4-6)` score=0.0313 bm25#3 vec#5 — '- I am a Business Development Intern at Moove.\n- Moove is a fleet operations partner for r'
4. `raw/H-1B visa - Wikipedia.md § Criticism > Limitations for entrepreneurs and self-employed consultants (lines 355-355)` score=0.029 bm25#11 vec#7 — "Entrepreneurs do not qualify for the H-1B visa. The United States immigration system's EB-"
5. `raw/H-1B visa - Wikipedia.md § Annual cap (lines 104-111)` score=0.0289 bm25#5 vec#14 — 'The H-1B visa program is subject to an annual cap of 65,000 visas, with an additional 20,0'
