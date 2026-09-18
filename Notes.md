# Notes

Working notes for the project. Not part of the submission — the README is.

---

## Milestone 1: Pick corpus and run the starter

### Corpus: `advice_threads`

Picked it over `campus_life` because it's a harder chunking problem.

- 23 question-and-answer threads, ~543 characters on average
- Each file is a `THREAD: <question>` line, then 3–5 replies formatted
  `--- reply N (X votes) ---` followed by the reply text, separated by blank lines
- Replies are uneven in length and often disagree
- The real answer tends to be spread across replies, not sitting in one place
- Most votes doesn't mean most useful: in `thread_bike_commute.txt`, reply 4
  has the fewest votes (5) but the most concrete fact (free campus bike
  registration got a stolen bike back)

Set as the default in both `.env` (`AI201_CORPUS=advice_threads`) and
`config.py`. `.env` is gitignored, so `config.py` is what anyone cloning the
repo gets.

### Example thread: `thread_bike_commute.txt`

```
THREAD: Is a bike worth it for a 20 minute walk commute?

--- reply 1 (14 votes) ---
Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.

--- reply 2 (9 votes) ---
Counterpoint, I sold mine. Between November and March the paths are either icy or salted and salt destroys a drivetrain in one season.

--- reply 3 (22 votes) ---
Both true. I keep a cheap bike for September to November and walk the rest of the year. Total cost was about $120 for the bike and I don't care what happens to it.

--- reply 4 (5 votes) ---
If you do get one, the campus does free registration and it's the only reason I got mine back after it was taken.
```

### Pipeline check

- First `ask` failed: `No index called 'campus_life__default'` — hadn't run `index` yet
- After `python app.py index`, `ask "is the housing lottery random?"` on
  `campus_life` gave a correct answer with sources (best distance 0.250, cutoff 0.6)
- Re-indexed on `advice_threads`: 23 documents

### Write this down: chunk count

```
$ python app.py --corpus advice_threads chunks -n 1
98 chunks total. Showing 1, spread across the corpus.

Paste these into your README under Sample Chunks. The rubric asks
for the source file and the function that produced them — both are
printed for you below.

======================================================================
Chunk 1  |  source: thread_bike_commute.txt#0  |  produced by: chunker.py::split_documents
======================================================================
THREAD: Is a bike worth it for a 20 minute walk commute?

For each one, ask: could someone answer a question using only this,
without reading what came before or after?
```

- **98** — with my paragraph split (`chunker.py::split_documents`), which was
  already changed when I ran this
- **26** — with the unmodified starter chunker (`chunker.py::fallback_split`,
  800-character windows), which is what the activity expects

What the numbers mean:
- **26:** most threads fit under 800 characters, so they stay whole. Only
  ~3 get cut, sometimes mid-sentence (one leaves a 2-character chunk)
- **98:** 23 question-only chunks + 75 reply chunks, one per paragraph

Note: the chunk above is only the thread's question — it can't answer
anything on its own. That's the first sign of the paragraph-split problem.
