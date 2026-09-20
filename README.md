# The Unofficial Guide

**Nicolas** · Corpus: `advice_threads`

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

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

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**

**2.**

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

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

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
