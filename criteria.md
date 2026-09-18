# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

---

## 4. Something about your chunks

Of the 5 chunks printed by `python app.py chunks -n 5`, at least 4 name their
own subject — a reader can tell what thread question the chunk is answering
from the chunk's text alone, without reading the chunk before or after it.



**Why this target:**
I picked 4 of 5 rather than 5 of 5 because my chunker produces some question-only chunks from each thread's THREAD line, and a chunk that's just a question can't stand on its own by nature. Requiring all five would penalize a structural feature of my corpus rather than measuring chunk size. Four of five keeps the majority standing alone while allowing for those question-only chunks



---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->

## 5. Answers keep the disagreement between replies

For the 2 of my 5 test questions whose threads contain replies that qualify or
contradict each other, the answer names the condition the replies disagree
about rather than presenting one reply as settled fact. Both of the 2 have to
do this.

**Why this target:**
Only two of my five questions land on threads where the replies disagree:
laundry timing, where reply 1 says Tuesday and Wednesday mornings in every
building and reply 2 says it depends which building you're in, and meal plan
tiers, where reply 1 says get the middle tier unless your building has a
kitchen and reply 2 says the highest tier almost never makes sense. The other
three threads have replies that add to each other instead of arguing. So the
number is 2 because that's how many cases exist, not because 2 felt safe, and
I require both rather than 1 of 2 because with only two cases a target of 1
would pass on a coin flip. I'm measuring whether the answer names the
condition — the building, or whether you have a kitchen — because that's the
thing the replies actually disagree about, and it's something I can look for
in the text rather than having to judge how balanced an answer feels.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
