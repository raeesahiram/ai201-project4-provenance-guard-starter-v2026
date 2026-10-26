# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. **Request arrives at Flask** on `POST /submit` as a JSON object containing
   `text` and `creator_id`.
2. **Input validation in `app.py::submit`** checks that both fields are
   non-empty strings. Invalid input is rejected with `400` and an audit-log
   rejection entry.
3. **`detector.model_signal` in `detector.py`** runs the local language model
   over the text and adds a 0–1 predictability-based score; higher means more
   AI-like. If the model is unavailable, the route returns `503`.
4. **`stylometry.style_signal` in `stylometry.py`** is intended to add a
   second 0–1 score based on text shape rather than meaning. It currently
   returns the fixed placeholder `0.5`, so it does not yet distinguish
   submissions.
5. **`scoring.combine_signals` in `scoring.py`** averages the two scores using
   the configured weights, currently 0.5 for each. Disagreement pulls the
   result toward the middle rather than letting either score decide alone.
6. **`scoring.score_to_label`** compares the combined score with the configured
   thresholds and adds a machine-readable guess and reader-facing label.
7. **`audit.log_decision` in `audit.py`** records the content ID, creator,
   guesses, scores, label, and status; then Flask returns that decision as
   JSON.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:**

`detector.py` uses a local GPT-2 language model to estimate perplexity: how
surprised the model is by the text. It maps lower perplexity (more predictable
text) to a higher AI-likelihood score.

**Why that might differ between human and AI writing:**

Generated text is often made from likely next-word choices, so it may be
predictable to a language model. Human writing can be less predictable because
of unusual word choices, abrupt turns, or specific details.

**What it can't see:**

It cannot see who wrote the text. Predictability is not authorship: ordinary,
plain writing, including writing by a second-language learner, can be
predictable and score as AI-like. Conversely, unusual or ornate human writing
can score as human-like. It also does not understand whether a claim is true
or whether the writer used AI.

### Signal two — the style signal

**What it measures:**

`stylometry.py` is designed to measure the text's shape without reading its
meaning: variation in sentence lengths, vocabulary repetition
(type-token ratio), and punctuation density. Its intended output is a 0–1
score where higher means more AI-like. The current `style_signal` is still a
stub that always returns `0.5`; those measurements are not implemented yet.

**Why that might differ between human and AI writing:**

Generated prose can use a more even sentence rhythm and narrower vocabulary
than an individual writer's naturally uneven style. Sentence-length variation,
repeated words, and punctuation patterns may therefore differ on average.
They are tendencies, not reliable rules about an individual author.

**What it can't see:**

It cannot see meaning, authorship, or whether a text is true. A person can
change the measured shape without changing the ideas—for example, by breaking
sentences up, adding typos, or including a quotation. Those changes can move
the score without changing who wrote the work.

### A false-positive trace

Imagine a real writer who uses plain, common words and short, regular
sentences. The model finds that writing predictable and returns
`model_score = 0.82`. The current style stub returns `style_score = 0.50`.
With the current equal weights, the combined score is
`(0.5 × 0.82) + (0.5 × 0.50) = 0.66`. Since `AI_THRESHOLD` is `0.65`, the
reader sees the `ai` guess and this label:

> The signals suggest this text may be AI-generated; this is not proof of authorship.

This is a false positive: the writer wrote the text themselves, but
predictability pushed the score into the AI band. The intended remedy is to
appeal with the content ID and their reasoning. **The appeal contract is
described below, but `POST /appeal` is not implemented yet and currently
returns `501`; the writer cannot complete that path in the running service
today.**

### Endpoint contracts

`POST /submit`

**Request JSON fields**

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `text` | string | yes | The text to score; must not be empty or whitespace-only |
| `creator_id` | string | yes | The submitting writer's identifier; must not be empty or whitespace-only |

**Successful response fields (`200`)**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | Generated UUID used to refer to this submission, including in an appeal |
| `guess` | string | Machine-readable category: `human`, `unsure`, or `ai` |
| `confidence` | number | The combined score from 0.0 to 1.0; currently the same value as `combined_score`, not a calibrated probability |
| `label` | string | Reader-facing sentence explaining the result |
| `model_score` | number | Detector signal score from 0.0 to 1.0 |
| `style_score` | number | Style signal score from 0.0 to 1.0 |
| `combined_score` | number | Weighted combination of the two signal scores |

Invalid or missing fields return `400` with `error` and `message`. Text too short for the detector returns `400` with `error: "invalid_text"` and a `message`. If the detector cannot load, the route returns `503` with `error: "detector_unavailable"` and a `message`.

`POST /appeal`

**Request JSON fields**

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `content_id` | string | yes | The ID returned by `/submit` for the decision being challenged |
| `reasoning` | string | yes | The writer's explanation of why they are appealing |

**Intended successful response fields (`200`)**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | The decision under appeal |
| `status` | string | `under_review`, confirming the appeal was recorded |
| `message` | string | Confirmation that the appeal was received |

The intended handler should return `400` for missing or invalid fields and
`404` when the content ID has no decision to appeal. It should append an
appeal entry rather than overwrite the original decision. This is a design
contract, not current runtime behavior: `POST /appeal` still returns `501`.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**

Take the weighted average of the model and style scores. Higher values from
either signal raise the combined AI-likelihood score; when they disagree,
averaging moderates the result instead of allowing one signal to override the
other.

**The numbers:**

`WEIGHT_MODEL_SIGNAL = 0.5`; `WEIGHT_STYLE_SIGNAL = 0.5`. The current
thresholds are `HUMAN_THRESHOLD = 0.35` and `AI_THRESHOLD = 0.65`.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

For example, a predictable human-written passage could score `0.82` on the
model signal while the style stub returns `0.50`. The equal-weight average is
`0.66`, which lands just inside the AI band. Averaging moderates the model
score but does not prevent this false positive; the stub currently provides
no independent evidence to counter it.

---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00–0.35 inclusive | The signals suggest this text may be human-written; this is not proof of authorship. |
| unsure | greater than 0.35 and less than 0.65 | The signals are inconclusive; this is not a determination of authorship. |
| high-confidence AI | 0.65–1.00 inclusive | The signals suggest this text may be AI-generated; this is not proof of authorship. |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->
It says plainly that the signals did not reach a conclusion and avoids treating
uncertainty as an accusation.


---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "...", "creator_id": "..."}'
```

```json

```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json

```

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
