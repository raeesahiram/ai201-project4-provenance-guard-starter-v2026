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
   second 0–1 score based on sentence-length variation and vocabulary
   repetition, without interpreting meaning.
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

**Standalone `python detector.py` checks:** The local `gpt2` model returned:

| Probe | Perplexity | `model_signal` |
|---|---:|---:|
| Assistant-generated conventional prose (AI-written) | 61.9 | 0.3751 |
| U.S. Constitution preamble excerpt (human-written) | 3.2 | 0.9853 |
| Plain, ordinary prose intended as a borderline-style example | 54.8 | 0.4216 |

The plain-prose probe is not an authorship-ground-truth sample. These three
scores did not separate AI-written from human-written text; in particular,
the known human-written excerpt scored very AI-like. This is evidence of the
signal's limitation, not evidence that the excerpt was AI-generated.

**Same three probes, both signals:**

| Probe | Model score | Style score | What happened |
|---|---:|---:|---|
| AI-style conventional sample | 0.3751 | 0.4675 | Close agreement; both remain in the unsure band |
| Personal-style sample (authorship not independently verified) | 0.5331 | 0.4215 | Signals split by 0.1116; the average is 0.4773 |
| Borderline-style sample (not ground truth) | 0.4216 | 0.4399 | Close agreement; both remain in the unsure band |

The personal-style sample is the clearest split in this set: the model leans
more AI-like than the style score. The model and style score both remain
uncertain, so the equal-weight average returns to the middle rather than
letting one decide alone.

### Signal two — the style signal

**What it measures:**

`stylometry.py` is designed to measure the text's shape without reading its
meaning. It computes the coefficient of variation for sentence word counts
(sample standard deviation divided by the mean) and the type-token ratio
(unique words divided by total words). It turns the variation into an
AI-like score with `1 / (1 + variation)` and inverts the type-token ratio
(`1 - ratio`) so repeated vocabulary raises the score. The style score is the
mean of those two values; higher means more AI-like. If there are fewer than
two sentences, variation contributes a neutral `0.5`.

Punctuation density (punctuation characters per word) is computed and printed
as a diagnostic, but is not included in the score: punctuation frequency
alone has no dependable direction without calibration evidence.

**Why that might differ between human and AI writing:**

Generated prose can use a more even sentence rhythm and narrower vocabulary
than an individual writer's naturally uneven style. Sentence-length variation,
repeated words, and punctuation patterns may therefore differ on average.
The score uses the first two tendencies; punctuation remains visible for
inspection only. These are tendencies, not reliable rules about an individual
author.

**What it can't see:**

It cannot see meaning, authorship, or whether a text is true. Type-token ratio
also falls with text length, and repeated words may be a natural feature of a
human writer. A person can change the measured shape without changing the
ideas—for example, by breaking sentences up, adding typos, or including a
quotation. Those changes can move the score without changing who wrote the
work.

**Four-input calibration (same local model and style formula):**

| Input | Model score | Style score | Combined score | Observation |
|---|---:|---:|---:|---|
| Original AI-generated conventional paragraph | 0.6651 | 0.4724 | 0.56875 | Signals disagree; average stays unsure |
| Human-written Dickens excerpt | 0.9583 | 0.5694 | 0.76385 | Both signals lean AI-like, despite known human authorship |
| Formal human-written Constitution excerpt | 0.9853 | 0.3846 | 0.68495 | Strong disagreement; average still crosses the AI threshold |
| Lightly edited AI-generated paragraph | 0.5432 | 0.3945 | 0.46885 | Both signals stay in the unsure range |

For the Constitution excerpt, the signals disagree strongly: the model score
is very AI-like while style is much lower, but the equal-weight average still
crosses the AI threshold. The Dickens excerpt is a second failure case: both
scores lean AI-like for known human writing. These examples show that neither
score is proof of authorship.

### A false-positive trace

The U.S. Constitution preamble excerpt is human-written, but the model
returned `model_score = 0.9853` for it. The style signal returned
`style_score = 0.3846`, a substantial disagreement. With equal weights, the
combined score was `(0.5 × 0.9853) + (0.5 × 0.3846) = 0.68495`. Since
`AI_THRESHOLD` is `0.65`, the reader saw the `ai` guess and this label:

> The signals suggest this text may be AI-generated; this is not proof of authorship.

This is a false positive: people wrote the passage, but its predictability
pushed the score into the AI band. The intended remedy is to appeal with the
content ID and reasoning. **The appeal contract is described below, but
`POST /appeal` records the writer's reasoning and marks the appended appeal
entry `under_review`; the original decision remains in the audit log.

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

**Successful response fields (`200`)**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | The decision under appeal |
| `status` | string | `under_review`, confirming the appeal was recorded |
| `message` | string | Confirmation that the appeal was received |

Missing or invalid fields return `400`; an unknown content ID returns `404`.
The endpoint appends an appeal entry with status `under_review`, preserving
the original decision entry (which remains `decided`) so the audit trail
shows both records in order.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**

Take the weighted average:
`combined = (0.5 × model_score) + (0.5 × style_score)`. Both signals are
intended to point in the same direction, so a high score from either raises
the combined AI-likelihood score. When they disagree, averaging pulls the
result toward the middle rather than letting either signal override the
other. I chose equal weights because neither signal has demonstrated stronger
reliability; this is deliberately simple, not a calibrated probability.

**The numbers:**

`WEIGHT_MODEL_SIGNAL = 0.5`; `WEIGHT_STYLE_SIGNAL = 0.5`. The current
thresholds are `HUMAN_THRESHOLD = 0.35` and `AI_THRESHOLD = 0.65`. This
equal-weight rule was documented before the style-score implementation was
calibrated.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

The formal Constitution excerpt scored `0.9853` on the model signal and
`0.3846` on the style signal. Their equal-weight average, `0.68495`, is lower
than the model score but still crosses the `0.65` AI threshold. Averaging
moderates disagreement; it does not guarantee a correct result.

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

**Live route checks:** Each label was returned by `POST /submit` for the
following input. A label reflects the score band, not verified authorship.

| Result | Text submitted (excerpt) | Combined score | Content ID |
|---|---|---:|---|
| `human` | “Petrichor, susurrus, defenestration, ultracrepidarian, callipygian…” | 0.21775 | `e3a5877e-4213-49fe-9906-052736e8c2bf` |
| `unsure` | “A successful project begins with a clear plan. The plan identifies the main goal…” | 0.56875 | `23e97593-b541-4a67-9f0a-228d638cfb83` |
| `ai` | The human-written U.S. Constitution preamble excerpt shown below | 0.68495 | `87ca4a72-fe58-418d-a707-75880dc62004` |

The `ai` result is a known false positive. The human-band probe is unusual
text and is not a claim about its authorship. These results show all three
score bands are reachable, not that the detector reliably identifies authors.


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
  -d '{"text":"We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, provide for the common defence, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and establish this Constitution for the United States of America.","creator_id":"readme-human-sample-style-v2"}'
```

```json
{
  "combined_score": 0.68495,
  "confidence": 0.68495,
  "content_id": "93ca2454-183a-40f3-bf03-3dd62f852898",
  "guess": "ai",
  "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
  "model_score": 0.9853,
  "style_score": 0.3846
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id":"93ca2454-183a-40f3-bf03-3dd62f852898","reasoning":"I wrote this text myself and request a review of the AI label."}'
```

```json
{
  "content_id": "93ca2454-183a-40f3-bf03-3dd62f852898",
  "message": "Your appeal has been received and is under review.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl -sS "http://127.0.0.1:5000/log" | python -c \
  'import json,sys; print(json.dumps([e for e in json.load(sys.stdin)["entries"] if e.get("content_id") == "93ca2454-183a-40f3-bf03-3dd62f852898"], indent=2))'
```

```json
[
  {
    "combined_score": 0.68495,
    "content_id": "93ca2454-183a-40f3-bf03-3dd62f852898",
    "creator_id": "readme-human-sample-style-v2",
    "guess": "ai",
    "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
    "model_score": 0.9853,
    "status": "decided",
    "style_score": 0.3846,
    "timestamp": "2026-10-26T02:42:47+00:00"
  },
  {
    "content_id": "93ca2454-183a-40f3-bf03-3dd62f852898",
    "creator_id": "readme-human-sample-style-v2",
    "event": "appeal",
    "reasoning": "I wrote this text myself and request a review of the AI label.",
    "status": "under_review",
    "timestamp": "2026-10-26T02:47:30+00:00"
  }
]
```

Two `model_score: 0.0` entries from overlapping model-initialization checks
remain in the append-only log as failed-test artifacts. Detector loading is
now synchronized; subsequent serial and simultaneous submissions returned
nonzero scores and the expected label bands.

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
