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

---

## Milestone 4, steps 1 and 2: retrieval check and top-k

Ran three of my five questions through `python app.py retrieve` and read the
chunks that came back.

| Question | Best distance | Top chunk | Has the expected fact? |
|---|---|---|---|
| How much do commuter lockers cost? | 0.349 | thread_commuting, reply 2: "lockers you can rent for $20 a year" | yes |
| When can you change your meal plan? | 0.214 | thread_meal_plan_tier, reply 3: "only change it once and only in the first ten days" | yes |
| How late is the library open? | 0.383 | thread_sleep_schedule, reply 2: "The library being open until 2am is a trap" | yes |

All three put the right chunk at #1. What the rest of the results looked like:

- **Lockers:** #1 at 0.349, then a jump to 0.694. Results 2–5 were bike,
  laundry and parking threads — commuting-adjacent, sharing words like
  "commute" and "cost", but none of them mention lockers.
- **Meal plan:** all four meal-plan replies came back together (0.214–0.488),
  then a jump to 0.724 for an unrelated pass/fail thread. Attaching the thread
  question pulled the whole discussion into range.
- **Library:** #1 was the sleep thread with the actual 2am fact. Results 2–5
  were all study-spot chunks (0.51–0.59) that say "library" repeatedly but
  never give hours. This is the clearest case of sharing words rather than
  meaning, and it's the question I expected to be hardest.

**Top-k: leaving it at 5.** The answer was at #1 in all three cases and
results 2–5 added context without burying it. Going to 3 would still work;
going higher would pull in more near-misses like the study-spot chunks.
Checked rather than defaulted.

---

## Milestone 4, step 3: the relevance cutoff

Best distance for each of my five questions and each of the five in
`OUT_OF_SCOPE`, from `python app.py retrieve`:

| Question | In corpus? | Best distance |
|---|---|---|
| Which mornings is dorm laundry free? | yes | 0.2037 |
| When can you change your meal plan? | yes | 0.2142 |
| How many sessions is the counselling sleep workshop? | yes | 0.3419 |
| How much do commuter lockers cost? | yes | 0.3492 |
| How late is the library open? | yes | 0.3829 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.8075 |
| How do I write a for loop in Rust? | no | 0.8348 |
| Who won the 1994 World Cup? | no | 0.8934 |
| What is the capital of Mongolia? | no | 0.8935 |
| How do I change the oil in a diesel engine? | no | 0.8964 |

**Two groups, no overlap.** In corpus: 0.204–0.383. Out of corpus:
0.808–0.896. The gap runs from 0.383 to 0.808, which is 0.42 wide, and its
midpoint is 0.595.

**Cutoff: 0.6, left where the starter had it.** It sits almost exactly at the
midpoint of my gap, with 0.22 of margin above my worst real question and 0.21
below my closest out-of-corpus one. Anything from about 0.45 to 0.75 would
separate these ten, so 0.6 isn't the only defensible number — it's the most
balanced one, and now it's a measurement rather than a default I never checked.

**What I got wrong in criterion 3.** I predicted ibuprofen and a Rust for loop
might slip under the cutoff, because they sit near my sleep, counselling and
laptop threads. They are in fact the two closest out-of-corpus questions
(0.8075 and 0.8348), so the reasoning held — but they're nowhere near
crossing 0.6, so all five should be refused rather than the 4 of 5 I targeted.

**When I would change this number:**
- If my in-corpus questions scored high (0.55–0.70), I'd raise it or the gate
  would refuse questions I have answers for.
- If out-of-corpus questions scored low, I'd lower it or unrelated questions
  would reach the model.
- If the two groups overlapped, no cutoff would separate them and I'd report
  the overlap instead of pretending a number fixed it.
- Any time I change chunking or the embedding model, because that moves the
  distances underneath the cutoff. Mine already moved once: the parking
  question went from 0.111 under the paragraph split to 0.280 under
  reply-plus-question.

**Changed the cutoff to 0.5** rather than leaving it at 0.6. Both sit in the
gap, but my five out-of-corpus questions (Mongolia, diesel engines, the World
Cup, ibuprofen, Rust) are obviously unrelated to student life, and a question
that was merely off-topic — something about a university, just not mine —
would land nearer my corpus than any of them did. 0.5 leaves room for that
case and still clears my worst real question (the library one, 0.383) by 0.12.
Verified against all ten: 5/5 in-corpus questions pass the gate, 5/5
out-of-corpus questions are refused.
