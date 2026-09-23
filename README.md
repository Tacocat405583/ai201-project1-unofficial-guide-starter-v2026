# The Unofficial Guide

**Nicolas** · Corpus: `advice_threads`

---

# Unit 1

## What This Does

I picked the `advice_threads` corpus because I thought it would be more
challenging than `campus_life`. It's 23 question-and-answer threads where
students ask about college life and several people reply, often disagreeing
with each other. The system answers practical "how does this work" or
"should I do this" questions, drawing on those replies. Some examples:

- "Is a parking permit worth it?"
- "When is laundry free in the dorms?"
- "What happens if I hand in an assignment late?"
- "How do I deal with a roommate who has guests over late?"

## Chunking Strategy

**Chunk size:** one reply plus its thread question — 131 to 280 characters on
this corpus (201 on average), 75 chunks in total. There's no character count in
the code; the size comes from the structure of the threads.

**Overlap:** 0. Every chunk repeats its thread question instead, which does the
job overlap normally does: it carries the context a reply needs to make sense.

Each `advice_threads` file is a `THREAD: <question>` line followed by 3–5
replies separated by blank lines. When I measured them, the replies were
95–222 characters (median 144) and the thread questions 35–68. No reply comes
close to 800 characters, so there is never a reason to cut inside one. The
problem with these documents isn't length, it's that a reply on its own
usually doesn't say what it's about: "Street parking on Verrill is legal and
free and unmarked" never mentions a permit, and "Two you actually turn up to
beats six you signed up for at the fair" never mentions clubs. So
`split_documents` keeps each reply whole and puts the thread question in front
of it, and the question is never a chunk by itself.

I didn't get here first time. Three versions, measured with `python app.py index`
and `python app.py chunks`:

| Version | Chunks | Shortest | Longest | What went wrong |
|---|---|---|---|---|
| Starter, `fallback_split` (800 chars, 120 overlap) | 26 | 2 | 793 | Most threads stayed whole in one chunk; the few that got cut were cut mid-sentence, leaving a 2-character fragment |
| Paragraph split (first try) | 98 | 35 | 222 | Every thread question became its own chunk with no answer in it, and the replies lost their subject. 0 of 5 sampled chunks stood on their own |
| Reply + thread question (final) | 75 | 131 | 280 | — |

The paragraph split's problem showed up in retrieval. For
`python app.py retrieve "is a parking permit worth it"`:

| | Paragraph split | Reply + thread question |
|---|---|---|
| #1 result | the question-only chunk, distance 0.111, no answer in it | parking reply 3, 0.280 |
| Parking replies in the top 5 | 2 of 3 — reply 1 missing | all 3, at #1–#3 |

The best distance got worse, but the old best match was a chunk with nothing
in it to answer from. Now every top result contains an answer.

I considered a 125-character minimum instead, but 16 of the 75 replies are
under 125 and they're complete thoughts — one of them, "The library being open
until 2am is a trap", is the answer to one of my test questions. A minimum
would have dropped it or merged it with an unrelated reply. I also considered
keeping each thread whole (23 chunks), which would keep disagreeing replies
together but make every chunk cover several ideas at once. That's the
alternative I'd try if my disagreement criterion (5) fails.

## Sample Chunks

From `python app.py chunks -n 5`.

**Chunk 1** — source: `thread_bike_commute.txt#0` — produced by: `chunker.py::split_documents`

```
THREAD: Is a bike worth it for a 20 minute walk commute?
--- reply 1 (14 votes) ---
Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.
```

**Chunk 2** — source: `thread_first_gen.txt#1` — produced by: `chunker.py::split_documents`

```
THREAD: Anything specific for first-generation students?
--- reply 2 (41 votes) ---
The thing I'd say: the unwritten rules are the hard part, not the coursework. Ask about the unwritten rules explicitly. People are happy to explain them and nobody volunteers them.
```

**Chunk 3** — source: `thread_laptop_specs.txt#2` — produced by: `chunker.py::split_documents`

```
THREAD: How much laptop do I actually need for CS courses?
--- reply 3 (12 votes) ---
I did two years on an 8GB machine and it was fine until the last project, at which point it very much wasn't. 16 is the answer.
```

**Chunk 4** — source: `thread_parking.txt#1` — produced by: `chunker.py::split_documents`

```
THREAD: Worth getting a parking permit?
--- reply 2 (21 votes) ---
Street parking on Verrill is legal and free and unmarked, which is why half the upper years do it.
```

**Chunk 5** — source: `thread_sleep_schedule.txt#1` — produced by: `chunker.py::split_documents`

```
THREAD: Everyone says fix your sleep. Does it actually matter?
--- reply 2 (37 votes) ---
The library being open until 2am is a trap. It's a resource, not a schedule.
```

## Sample Answer

**Question:** Which mornings is dorm laundry free?

**Answer:**

```
$ python app.py ask "Which mornings is dorm laundry free?"
  (best distance 0.204, cutoff 0.5)

According to `thread_laundry_timing.txt`, dorm laundry is free on Tuesday and
Wednesday mornings in every building (reply 1). However, reply 2 notes that
whether this is a problem depends heavily on your building, since Morrow has
more machines per person than Fenwick.

Sources retrieved: thread_laundry_timing.txt, thread_roommate_conflict.txt, thread_sleep_schedule.txt
```

I tightened the grounding instruction in `generate.py` to get that second
sentence. With the starter's rules the same question answered "Dorm laundry is
free on Tuesday and Wednesday mornings in every building." — true to reply 1,
but it dropped reply 2 entirely and stated a contested claim as settled. My
documents are discussion threads where people disagree, so I added a rule:
where the replies disagree, or where one says the answer depends on something,
name the condition instead of presenting one reply as fact. That's criterion 5,
and the default prompt was failing it.

**My relevance cutoff:** 0.5

I ran all five of my test questions and all five in `OUT_OF_SCOPE` through
`python app.py retrieve` and wrote down the best distance for each. The two
groups didn't overlap: everything my corpus covers came back between 0.204 and
0.383, and everything it doesn't between 0.808 and 0.896, leaving an empty band
0.42 wide between them.

The starter's 0.6 sits almost exactly at the midpoint of that band (0.595), so
it would have worked. I put the cutoff at the low end of the gap instead,
because my five out-of-corpus questions are *obviously* unrelated to student
life — a question that was merely off-topic, about some other university,
would land much nearer my corpus than a diesel engine does, and 0.6 would let
it through. At 0.5 the gate still clears my worst real question (the library
one, 0.383) by 0.12, and all ten questions land on the correct side.

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

## How I Used AI

I used Claude Code in VS Code throughout, and a separate Claude chat to check
my work.

**1. The chunker.** I had Claude Code replace the starter's fixed-window
chunker with a paragraph split — cut on blank lines, one chunk per paragraph.
It worked, and the result was worse than it looked: `advice_threads` went to
98 chunks, and 23 of them were bare `THREAD:` question lines with no answer in
them. `python app.py retrieve "is a parking permit worth it"` then ranked one
of those empty question chunks first at 0.111, and parking reply 1 didn't make
the top 5 at all. The fix I asked for next was mine: keep one chunk per reply,
but paste the thread question on the front of every one, and never emit the
question by itself. That's the chunker I shipped — 75 chunks, 131–280
characters, all three parking replies back at #1–#3.

**2. Judging my own chunks.** I pasted three finished chunks into a separate
Claude chat and asked what question each could answer on its own, and what was
missing if it couldn't. I deliberately included the sleep-thread chunk that
holds my library-hours fact ("The library being open until 2am is a trap"),
because I suspected it was the weakest one. The replies were a useful
correction to my own optimism: not every chunk was as self-contained as I
thought. I didn't change the chunker over it — I wrote the weak spots into my
notes instead and left them to be measured in unit 2, since retrieval had
already found that chunk at 0.383.

One thing I did not use AI for, on purpose: picking the relevance cutoff.
Claude recommended keeping the starter's 0.6, which sits at the midpoint of my
measured gap. I went with 0.5 instead, because my five out-of-corpus questions
are so obviously unrelated (diesel engines, the World Cup) that the midpoint
flatters the gate — a question that was merely off-topic would land much
closer than they did.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

Five questions, three runs each, response cache off. The raw file is
`results/run_2026-09-23_0221_before.md`, produced by `run_eval.py::main` on
2026-09-23 against the `advice_threads` corpus at top-k 5 and cutoff 0.5. That
file is one row per question; this table is one row per criterion.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks name their own subject | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Answers keep the disagreement between replies | 2 of 2 | 0/2 | 1/2 | 0/2 | MISSED |

Criteria 1, 3 and 4 carry the same number in all three columns because all
three are measured by one deterministic pass. Retrieval is the same query
against the same index every time, the gate is a comparison against a fixed
number, and `app.py chunks -n 5` samples by stride rather than at random. There
is one measurement for each and it goes in all three columns. Criterion 5 is
the one that depends on what the model wrote, and it is the one that moves.

The 15 answers behind criteria 2 and 5 are three separate model calls per
question — `run_eval.py::run_once` passes `cache=False` on purpose — so they
are three real answers rather than one answer read three times.

### Criterion 1 — retrieved chunks contain the answer

Measured by `scorer.py::retrieval_contains` over the results of
`store.py::search`: does any of the five chunks that came back contain the
`expects` string from `questions.py`? All five questions hit on all three runs.

The hardest of the five was the locker question, where the answer lives in a
reply that never says "cost" or "how much". This is `store.py::search` for
"How much do commuter lockers cost?", printed by `app.py::cmd_retrieve`:

```
#   distance   source                           preview
1   0.3492     thread_commuting.txt             THREAD: Commuting an hour each way — is it survivabl...
2   0.6942     thread_bike_commute.txt          THREAD: Is a bike worth it for a 20 minute walk comm...
3   0.6951     thread_bike_commute.txt          THREAD: Is a bike worth it for a 20 minute walk comm...
4   0.7180     thread_laundry_timing.txt        THREAD: When is laundry actually free in the dorms? ...
5   0.7237     thread_parking.txt               THREAD: Worth getting a parking permit? --- reply 3 ...

Gate: best distance 0.349 is under the 0.5 cutoff
```

And the full text of hit 1 — the chunk that `expects: "20"` matched against:

```
THREAD: Commuting an hour each way — is it survivable?
--- reply 2 (21 votes) ---
The commuter lounge in the student centre has lockers you can rent for $20 a year and it changes the experience completely.
```

The gap between hit 1 at 0.349 and hit 2 at 0.694 is the thread question doing
the work. `chunker.py::split_documents` attaches it to every reply, so the
locker reply carries the word "commuting" even though the reply itself is about
lockers.

### Criterion 2 — every answer names a source

Measured by reading all 15 answer texts in the transcript section of
`results/run_2026-09-23_0221_before.md`, written by `run_eval.py::write_report`.
Every one of the 15 names a `.txt` file inside the answer itself, not only in
the "Sources retrieved" line that `app.py` prints separately. 5 of 5 on each of
the three runs.

Three of them, produced by `generate.py::answer_from_chunks`:

```
According to `thread_meal_plan_tier.txt`, you can only change your meal plan once and only in the first ten days.
```

```
The counselling sleep workshop is four sessions, according to `thread_sleep_schedule.txt`.
```

```
Based on the documents, the library is open until 2 am (*thread_sleep_schedule.txt*).
```

They differ in how they phrase the citation — backticks, a trailing "according
to", italics in parentheses — but all three name the file.

### Criterion 3 — the gate stops out-of-corpus questions

Produced by `run_eval.py::check_out_of_scope`, which puts each question in
`questions.py::OUT_OF_SCOPE` through `store.py::search` and then
`gate.py::check` at the 0.5 cutoff. Refused 5 of 5:

```
| Out-of-scope question                                       | Best distance | Gate    |
| What is the capital of Mongolia?                            | 0.893         | refused |
| How do I change the oil in a diesel engine?                 | 0.896         | refused |
| Who won the 1994 World Cup?                                 | 0.893         | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.807         | refused |
| How do I write a for loop in Rust?                          | 0.835         | refused |
```

In unit 1 I expected ibuprofen and the Rust question to be the near ones,
because a headache sits close to my sleep and counselling replies and Rust sits
close to the laptop-for-CS thread. They were the two closest — 0.807 and 0.835
— but both are more than 0.3 above the cutoff, nowhere near crossing it.

### Criterion 4 — chunks name their own subject

Produced by `app.py::cmd_chunks` over `chunker.py::split_documents`, which
prints 5 of the 75 chunks by stride across the corpus. The test is whether a
reader can tell what thread question the chunk answers from the chunk alone.
All 5 do, because every chunk opens with its `THREAD:` line:

```
Chunk 1  |  source: thread_bike_commute.txt#0  |  produced by: chunker.py::split_documents
THREAD: Is a bike worth it for a 20 minute walk commute?
--- reply 1 (14 votes) ---
Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.

Chunk 2  |  source: thread_first_gen.txt#1  |  produced by: chunker.py::split_documents
THREAD: Anything specific for first-generation students?
--- reply 2 (41 votes) ---
The thing I'd say: the unwritten rules are the hard part, not the coursework. Ask about the unwritten rules explicitly. People are happy to explain them and nobody volunteers them.

Chunk 3  |  source: thread_laptop_specs.txt#2  |  produced by: chunker.py::split_documents
THREAD: How much laptop do I actually need for CS courses?
--- reply 3 (12 votes) ---
I did two years on an 8GB machine and it was fine until the last project, at which point it very much wasn't. 16 is the answer.

Chunk 4  |  source: thread_parking.txt#1  |  produced by: chunker.py::split_documents
THREAD: Worth getting a parking permit?
--- reply 2 (21 votes) ---
Street parking on Verrill is legal and free and unmarked, which is why half the upper years do it.

Chunk 5  |  source: thread_sleep_schedule.txt#1  |  produced by: chunker.py::split_documents
THREAD: Everyone says fix your sleep. Does it actually matter?
--- reply 2 (37 votes) ---
The library being open until 2am is a trap. It's a resource, not a schedule.
```

Chunk 5 is the one I looked at hardest. "The library being open until 2am is a
trap" would be unreadable on its own — a trap for what? — but with the thread
question attached you can tell it is answering whether fixing your sleep
matters. That is the test as I wrote it, so it counts.

### Criterion 5 — answers keep the disagreement between replies

Measured by reading the answers to the two questions whose threads contain
replies that qualify each other, from the transcript in
`results/run_2026-09-23_0221_before.md`. The test is whether the answer names
the condition the replies disagree about.

Laundry, where reply 1 says every building and reply 2 says it depends which
building you are in. Three answers from `generate.py::answer_from_chunks`, same
question, same chunks, best distance 0.204 every time:

```
run 1: According to `thread_laundry_timing.txt`, laundry is free on Tuesday and Wednesday mornings in every building.

run 2: Dorm laundry is free on Tuesday and Wednesday mornings in every building (from thread_laundry_timing.txt). However, one reply notes that availability heavily depends on your building (from thread_laundry_timing.txt).

run 3: According to `thread_laundry_timing.txt`, dorm laundry is free on Tuesday and Wednesday mornings in every building.
```

Run 2 names the building condition. Runs 1 and 3 state "in every building" as
settled fact and drop it entirely.

Meal plan, where reply 1 says get the middle tier unless your building has a
kitchen and reply 2 says the highest tier almost never makes sense:

```
run 1: According to `thread_meal_plan_tier.txt`, you can only change your meal plan once and only in the first ten days.

run 2: According to `thread_meal_plan_tier.txt`, you can only change your meal plan once and only during the first ten days.

run 3: According to `thread_meal_plan_tier.txt`, you can only change your meal plan once and only in the first ten days.
```

None of the three name the kitchen condition, so this half failed on all three
runs. Scored together: 0 of 2 on run 1, 1 of 2 on run 2, 0 of 2 on run 3.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion | Verdict | How I decided |
| --- | --------- | ------- | ------------- |
| 1   |           |         |               |
| 2   |           |         |               |
| 3   |           |         |               |
| 4   |           |         |               |
| 5   |           |         |               |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
