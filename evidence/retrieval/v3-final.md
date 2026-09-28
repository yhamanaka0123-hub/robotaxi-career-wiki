# Retrieval check: v3-final

top_k=6, chunk_chars=900, vector_weight=2.0, query_expansion=True

## Test 1: Which company owns Zoox, and how much did it pay to acquire it?
method: hybrid (BM25 + EmbeddingGemma, RRF), 3 queries
queries: ['Which company owns Zoox, and how much did it pay to acquire it?', 'Zoox ownership', 'Zoox acquisition details']

1. `raw/Zoox - Wikipedia.md § Progress and competition (lines 23-23)` score=0.0487 bm25#1 vec#2 — 'In December 2018, Zoox became the first company to gain approval for providing self-drivin'
2. `raw/Zoox - Wikipedia.md § History (lines 7-7)` score=0.0484 bm25#4 vec#1 — 'In January 2019, Zoox appointed a new CEO, Aicha Evans, who was previously the Chief Strat'
3. `raw/Zoox - Wikipedia.md § Introduction (lines 1-1)` score=0.0474 bm25#4 vec#3 — 'Zoox, Inc. is an American technology company subsidiary of Amazon developing driverless ve'
4. `raw/Zoox - Wikipedia.md § History (lines 6-6)` score=0.0469 bm25#6 vec#3 — 'Zoox was founded in 2014 by Australian artist-designer Tim Kentley-Klay and Jesse Levinson'
5. `raw/Zoox - Wikipedia.md § Progress and competition (lines 31-31)` score=0.0464 bm25#2 vec#6 — 'On November 18, 2025, Zoox launched its robotaxi service to the public in San Francisco, m'
6. `raw/Zoox - Wikipedia.md § Progress and competition (lines 24-24)` score=0.046 bm25#8 vec#4 — 'On March 20, 2019, Tesla, Inc. filed a lawsuit against Zoox and several now-former Tesla e'
- expected wiki-zoox line 7: FOUND at rank 2

## Test 2: If I finish a graduate degree at an American university, is there a separate H-1B quota I can apply under?
method: hybrid (BM25 + EmbeddingGemma, RRF), 3 queries
queries: ['If I finish a graduate degree at an American university, is there a separate H-1B quota I can apply under?', 'H-1B visa quota', 'post-graduate employment visa eligibility']

1. `raw/H-1B visa - Wikipedia.md § Eligibility and application process > Employment (lines 21-21)` score=0.0472 bm25#1 vec#5 — 'To maintain H-1B visa status, visa holders must maintain employment with their sponsoring '
2. `raw/H-1B visa - Wikipedia.md § History > The Immigration Act of 1990 (lines 124-124)` score=0.0469 bm25#4 vec#4 — 'President George H. W. Bush signed the Immigration Act of 1990 into law by on November 20,'
3. `raw/H-1B visa - Wikipedia.md § Eligibility and application process > Specialty occupation (lines 17-17)` score=0.0457 bm25#7 vec#5 — 'H-1B visas, as defined by United States Code, are those jobs that require a "theoretical a'
4. `raw/H-1B visa - Wikipedia.md § Criticism > Limitations for entrepreneurs and self-employed consultants (lines 355-355)` score=0.0453 bm25#11 vec#4 — "Entrepreneurs do not qualify for the H-1B visa. The United States immigration system's EB-"
5. `raw/H-1B visa - Wikipedia.md § Introduction (lines 5-6)` score=0.0453 bm25#20 vec#1 — "(B) attainment of a bachelor's degree or higher degree in the specific specialty (or its e"
6. `raw/H-1B visa - Wikipedia.md § Maintaining status > Dependents of visa holders (lines 81-82)` score=0.0453 bm25#3 vec#8 — 'H-1B visa holders can bring immediate family members, such as their spouse and children un'
- expected wiki-h1b line 6: FOUND at rank 5
- expected wiki-h1b line 104: MISSING from top-k

## Test 3: After I graduate from my MBA, how long can I work in the US on OPT before I need an H-1B?
method: hybrid (BM25 + EmbeddingGemma, RRF), 3 queries
queries: ['After I graduate from my MBA, how long can I work in the US on OPT before I need an H-1B?', 'OPT duration post-MBA', 'OPT transition to H-1B']

1. `raw/Optional Practical Training - Wikipedia.md § Support of the OPT program > Pathway to High-Skilled Immigration (lines 172-172)` score=0.0492 bm25#1 vec#1 — 'Economists point out that OPT is a vital pathway for the high-skilled workforce in the Uni'
2. `raw/Optional Practical Training - Wikipedia.md § OPT Statistics > Number of OPT Students by Country (lines 41-42)` score=0.0492 bm25#1 vec#1 — 'Since the Optional Practical Training program duration is a year for most people (though t'
3. `raw/My Career Notes.md § Situation (lines 9-11)` score=0.0487 bm25#1 vec#2 — '- I am an international student in the UC Berkeley Haas MBA program, graduating in May 202'
4. `raw/H-1B visa - Wikipedia.md § History > Executive action history > STEM Optional Practical Training extension and cap-gap extension (lines 169-170)` score=0.0476 bm25#5 vec#2 — 'On April 2, 2008, Homeland Security Secretary Michael Chertoff announced a 17-month extens'
5. `raw/H-1B visa - Wikipedia.md § Introduction (lines 9-9)` score=0.0464 bm25#4 vec#5 — 'In 2025, the Trump administration imposed a $100,000 fee for filing for an H-1B visa start'
6. `raw/Optional Practical Training - Wikipedia.md § Introduction (lines 4-4)` score=0.046 bm25#10 vec#3 — 'On March 11, 2016, the Department of Homeland Security published a final rule allowing cer'
- expected personal-career-notes line 10: FOUND at rank 3
- expected wiki-opt line 4: FOUND at rank 6

## Test 4: Does Moove sponsor H-1B visas for its employees?
method: hybrid (BM25 + EmbeddingGemma, RRF), 3 queries
queries: ['Does Moove sponsor H-1B visas for its employees?', 'Moove H-1B visa sponsorship', 'H-1B visa sponsorship policy']

1. `raw/My Career Notes.md § Recruiting plan (lines 18-19)` score=0.0492 bm25#1 vec#1 — '- I should recruit at other companies too, not only Moove, because I need an employer that'
2. `raw/H-1B visa - Wikipedia.md § Introduction (lines 5-6)` score=0.0482 bm25#5 vec#1 — "(B) attainment of a bachelor's degree or higher degree in the specific specialty (or its e"
3. `raw/H-1B visa - Wikipedia.md § Eligibility and application process > Employment (lines 21-21)` score=0.0481 bm25#3 vec#2 — 'To maintain H-1B visa status, visa holders must maintain employment with their sponsoring '
4. `raw/H-1B visa - Wikipedia.md § Maintaining status > Dual intent (lines 76-77)` score=0.0479 bm25#4 vec#2 — 'H-1B visas are considered "dual intent" because it is a temporary visa which gives visa ho'
5. `raw/My Career Notes.md § Current role (lines 4-6)` score=0.0466 bm25#3 vec#5 — '- I am a Business Development Intern at Moove.\n- Moove is a fleet operations partner for r'
6. `raw/H-1B visa - Wikipedia.md § Criticism > Limitations for entrepreneurs and self-employed consultants (lines 355-355)` score=0.0439 bm25#11 vec#7 — "Entrepreneurs do not qualify for the H-1B visa. The United States immigration system's EB-"
