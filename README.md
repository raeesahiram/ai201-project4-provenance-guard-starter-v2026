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
4. **`stylometry.style_signal` in `stylometry.py`** adds a second 0–1 score
   from sentence-length variation, vocabulary repetition, and punctuation
   density, without interpreting meaning.
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
| AI-style conventional sample | 0.3751 | 0.4450 | Close agreement; both remain in the unsure band |
| Personal-style sample (authorship not independently verified) | 0.5331 | 0.4596 | Signals split by 0.0735; the average is 0.49635 |
| Borderline-style sample (not ground truth) | 0.4216 | 0.4785 | Close agreement; both remain in the unsure band |

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
(`1 - ratio`) so repeated vocabulary raises the score. It also measures
punctuation characters per word and normalizes that rate as
`min(density / 0.2, 1.0)`. The style score is the equal-weight mean of these
three components; higher means more AI-like. If there are fewer than two
sentences, variation contributes a neutral `0.5`.

**Why that might differ between human and AI writing:**

Generated prose can use a more even sentence rhythm, narrower vocabulary,
and more regular punctuation than an individual writer's naturally uneven
style. Sentence-length variation, repeated words, and punctuation density may
therefore differ on average. These are tendencies, not reliable rules about
an individual author; the punctuation direction and its `0.2` saturation
point are heuristic choices, not calibrated authorship evidence.

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
| Original AI-generated conventional paragraph | 0.6651 | 0.5277 | 0.59640 | Signals disagree; average stays unsure |
| Human-written Dickens excerpt | 0.9583 | 0.6574 | 0.80785 | Both signals lean AI-like, despite known human authorship |
| Formal human-written Constitution excerpt | 0.9853 | 0.5128 | 0.74905 | Both signals combine above the AI threshold |
| Lightly edited AI-generated paragraph | 0.5432 | 0.5529 | 0.54805 | Both signals stay in the unsure range |

The Dickens excerpt is a clear failure case: both scores lean AI-like for
known human writing. The formal Constitution excerpt also lands in the AI
band. These examples show that neither score is proof of authorship.

### A false-positive trace

The U.S. Constitution preamble excerpt is human-written, but the model
returned `model_score = 0.9853` for it. The style signal returned
`style_score = 0.5128`. With equal weights, the combined score was
`(0.5 × 0.9853) + (0.5 × 0.5128) = 0.74905`. Since
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
`0.5128` on the style signal. Their equal-weight average, `0.74905`, is lower
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
| `human` | “Petrichor, susurrus, defenestration, ultracrepidarian, callipygian…” | 0.34275 | `5675a1d2-ebd8-446f-acee-01059cef0c74` |
| `unsure` | “A successful project begins with a clear plan. The plan identifies the main goal…” | 0.59640 | `40853339-e6a2-4059-9997-3a14ca04a619` |
| `ai` | The human-written U.S. Constitution preamble excerpt shown below | 0.74905 | `34674feb-1ad3-4e28-8099-862cae549213` |

The `ai` result is a known false positive. The human-band probe is unusual
text and is not a claim about its authorship. These results show all three
score bands are reachable, not that the detector reliably identifies authors.
As a boundary check, `0.51` maps to `unsure`, while `0.95` maps to `ai`; the
label is based on score ranges, not a flip at `0.5`.


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
  -d '{"text":"We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, provide for the common defence, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and establish this Constitution for the United States of America.","creator_id":"final-label-ai"}'
```

```json
{
  "combined_score": 0.74905,
  "confidence": 0.74905,
  "content_id": "34674feb-1ad3-4e28-8099-862cae549213",
  "guess": "ai",
  "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
  "model_score": 0.9853,
  "style_score": 0.5128
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id":"34674feb-1ad3-4e28-8099-862cae549213","reasoning":"I wrote this text myself and request review of the AI label."}'
```

```json
{
  "content_id": "34674feb-1ad3-4e28-8099-862cae549213",
  "message": "Your appeal has been received and is under review.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl -sS "http://127.0.0.1:5000/log" | python -c \
  'import json,sys; print(json.dumps([e for e in json.load(sys.stdin)["entries"] if e.get("content_id") == "34674feb-1ad3-4e28-8099-862cae549213"], indent=2))'
```

```json
[
  {
    "combined_score": 0.74905,
    "content_id": "34674feb-1ad3-4e28-8099-862cae549213",
    "creator_id": "final-label-ai",
    "guess": "ai",
    "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
    "model_score": 0.9853,
    "status": "decided",
    "style_score": 0.5128,
    "timestamp": "2026-10-26T02:57:51+00:00"
  },
  {
    "content_id": "34674feb-1ad3-4e28-8099-862cae549213",
    "creator_id": "final-label-ai",
    "event": "appeal",
    "reasoning": "I wrote this text myself and request review of the AI label.",
    "status": "under_review",
    "timestamp": "2026-10-26T02:57:58+00:00"
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

- *What I asked for:* Help implement `POST /submit` using the existing
  detector and audit helpers, while keeping `/ping` unchanged.
- *What came back:* A route that validates the JSON fields, calls both
  signals, combines and labels their scores, generates a content ID, and
  records the decision. It also handles invalid input and detector failures.
- *What I changed:* I verified `/ping`, exercised successful and failing
  requests, and kept the explicit `400`/`503` responses and audit logging.
  I made sure the response exposes both signal scores as well as the combined
  score so later evaluations can inspect each stage.

**Moment 2**

- *What I asked for:* Help build the style signal, choose how it combines
  sentence shape, vocabulary repetition, and punctuation, and check the
  proposed scoring rule against clearly AI-like, human, formal, and lightly
  edited examples.
- *What came back:* A normalized style score and a simple 50/50 weighted
  average in `scoring.py::combine_signals`. The calibration showed that the
  model could score known human writing as AI-like and that the style score
  did not reliably correct it.
- *What I changed:* I kept the equal weights as a transparent starting rule
  and documented the false-positive results rather than claiming reliable
  detection. I added punctuation density as a normalized third style
  component, while documenting its heuristic direction and saturation point
  rather than treating them as calibrated authorship evidence. I also used
  the detected model-load race to add synchronization and rechecked
  concurrent submissions.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 100 per day

**Why those numbers and not others:**
A real writer can submit several revisions in a short session and still stay
within five per minute; the daily cap allows regular work with room for
revisions. A script sending variations to map thresholds is throttled after
five quick submissions and cannot continue indefinitely across the day.

**What a caller counts as:** A `creator_id`. This ties the limit to the
submitting account rather than a shared network address, so writers on the
same network don't consume one another's allowance.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

---

## Attack Run — Before

Ran all 56 inputs from `attack_set` on 2026-11-01. Results are in
[`results/attack_run_2026-11-01_1821.md`](./results/attack_run_2026-11-01_1821.md).
I marked **13 BROKE** and **43 HELD**. An evasion was BROKE when it avoided an
AI label; a false-positive case was BROKE when known human writing got an AI
label. The remaining cases were HELD when the service rejected, rate-limited,
or handled the input without an attack success. The first five shared-creator
flood submissions were within the configured allowance; the seven excess
submissions were rate-limited.

**Ten audit log entries from the run**

```json
{"timestamp":"2026-11-01T23:20:58+00:00","content_id":"3e4d53c1-d964-4a96-96d8-7c1e8fb2d492","creator_id":"attacker_EV01","guess":"unsure","model_score":0.1635,"style_score":0.546,"combined_score":0.35475,"label":"The signals are inconclusive; this is not a determination of authorship.","status":"decided"}
{"timestamp":"2026-11-01T23:20:59+00:00","content_id":"e1d24679-4589-4d73-867b-77af6abd0349","creator_id":"attacker_EV09","guess":"unsure","model_score":0.7042,"style_score":0.5635,"combined_score":0.63385,"label":"The signals are inconclusive; this is not a determination of authorship.","status":"decided"}
{"timestamp":"2026-11-01T23:20:59+00:00","content_id":"080c5126-f731-49d5-8f50-527902c831de","creator_id":"attacker_EV10","guess":"ai","model_score":0.9792,"style_score":0.5297,"combined_score":0.75445,"label":"The signals suggest this text may be AI-generated; this is not proof of authorship.","status":"decided"}
{"timestamp":"2026-11-01T23:20:59+00:00","content_id":"6ddfd4b2-1c60-4ba4-8e96-af9006fc463b","creator_id":"attacker_FP04","guess":"ai","model_score":0.8329,"style_score":0.5282,"combined_score":0.68055,"label":"The signals suggest this text may be AI-generated; this is not proof of authorship.","status":"decided"}
{"timestamp":"2026-11-01T23:20:59+00:00","content_id":"190157df-ba39-4e82-8521-569c2a978786","creator_id":"attacker_FP05","guess":"ai","model_score":0.8005,"style_score":0.6134,"combined_score":0.70695,"label":"The signals suggest this text may be AI-generated; this is not proof of authorship.","status":"decided"}
{"timestamp":"2026-11-01T23:20:59+00:00","content_id":"c68ef87b-dda9-40ae-a84d-bae452690d63","creator_id":"attacker_FP06","guess":"ai","model_score":0.8814,"style_score":0.4903,"combined_score":0.68585,"label":"The signals suggest this text may be AI-generated; this is not proof of authorship.","status":"decided"}
{"timestamp":"2026-11-01T23:20:59+00:00","content_id":"981168e6-0df3-4523-9993-21ed1906bc1b","creator_id":"attacker_FP07","guess":"ai","model_score":0.8816,"style_score":0.6276,"combined_score":0.7546,"label":"The signals suggest this text may be AI-generated; this is not proof of authorship.","status":"decided"}
{"timestamp":"2026-11-01T23:20:59+00:00","content_id":"a84878aa-14d8-44e2-a552-99b4014b37a8","creator_id":"attacker_MF03","guess":"human","model_score":0.0,"style_score":0.5,"combined_score":0.25,"label":"The signals suggest this text may be human-written; this is not proof of authorship.","status":"decided"}
{"timestamp":"2026-11-01T23:21:00+00:00","content_id":"ebc38858-bd8c-4b63-b8ab-b695b3d21be9","creator_id":"attacker_MF08","guess":"ai","model_score":0.9876,"style_score":0.7264,"combined_score":0.857,"label":"The signals suggest this text may be AI-generated; this is not proof of authorship.","status":"decided"}
{"timestamp":"2026-11-01T23:21:00+00:00","creator_id":"attacker_flood","event":"rejected","status":"rejected","reason":"rate_limited","limit":"5 per 1 minute"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

FP07: deliberately repetitive genuine human writing received an AI label with
a combined score of 0.7546. This is the strongest false positive in the run
and illustrates the risk of treating a score as proof of authorship.

---

## Run Log and Verdicts

Ran `python run_eval.py --label before` for three trials without changing the
scenarios between trials. The complete JSON response and audit-log output for
every case in every trial is in
[`results/run_2026-11-01_1832_before.md`](./results/run_2026-11-01_1832_before.md).
The report was produced by `run_eval.py::main`; submissions came from
`app.py::submit`, appeals from `app.py::appeal`, and audit checks from
`app.py::get_log`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Human-writing false positives (synthetic proxy) | ≤ 1 AI guess of 10 | 0/10 | 0/10 | 0/10 | PROXY ONLY (NUMERIC MET) |
| 2. Score spread | AI median ≥ 0.20 above human-style median | gap 0.1648 | gap 0.1648 | gap 0.1648 | PROXY ONLY (NUMERIC MISSED) |
| 3. All three labels reachable | 3 of 3 labels | 3/3 | 3/3 | 3/3 | MET |
| 4. Appeal changes status and is recorded | 3 of 3 appeals | 3/3 | 3/3 | 3/3 | MET |
| 5. Invalid and oversized input is rejected and logged | 5 of 5 | 4/5 | 4/5 | 4/5 | MISSED |

The false-positive and score-spread human-style samples are synthetic
instructor test fixtures, not the instructor's personal writing or verified
human-authored work. Their results exercise the workflow but do not validate
those authorship-dependent criteria. Criterion 2's observed median gap was
below its unchanged 0.20 target. Criterion 5 missed because the 100,001-
character request returned `200` and was logged as a decision instead of
being rejected.

**Actual JSON from Trial 1** (the linked report contains the complete output
for every input in all three trials):

Criterion 1 — first of ten synthetic human-style submissions:

```json
{
  "status": 200,
  "response": {
    "combined_score": 0.6013999999999999,
    "confidence": 0.6013999999999999,
    "content_id": "0acb3fae-70b2-4384-aa8b-b2c8cbc36b53",
    "guess": "unsure",
    "label": "The signals are inconclusive; this is not a determination of authorship.",
    "model_score": 0.6824,
    "style_score": 0.5204
  }
}
```

Criterion 2 — one AI-generated sample and one synthetic human-style sample:

```json
[
  {
    "status": 200,
    "response": {
      "combined_score": 0.50175,
      "confidence": 0.50175,
      "content_id": "73e7ab7c-4a10-412c-aced-8cccc577a86f",
      "guess": "unsure",
      "label": "The signals are inconclusive; this is not a determination of authorship.",
      "model_score": 0.435,
      "style_score": 0.5685
    },
    "group": "ai_generated"
  },
  {
    "status": 200,
    "response": {
      "combined_score": 0.6013999999999999,
      "confidence": 0.6013999999999999,
      "content_id": "e6ef9ff7-aade-42b6-9f2b-f7bcc35f1de3",
      "guess": "unsure",
      "label": "The signals are inconclusive; this is not a determination of authorship.",
      "model_score": 0.6824,
      "style_score": 0.5204
    },
    "group": "human_style_synthetic"
  }
]
```

Criterion 3 — one response for each reachable label:

```json
[
  {
    "status": 200,
    "response": {
      "combined_score": 0.28375,
      "confidence": 0.28375,
      "content_id": "ca5ffa90-72a1-4f7c-9b0d-211dcbe77f33",
      "guess": "human",
      "label": "The signals suggest this text may be human-written; this is not proof of authorship.",
      "model_score": 0.0675,
      "style_score": 0.5
    },
    "sent": "Petrichor, susurrus, defenestration, ultracrepidarian, callipygian, susurration, apricity, and nudiu"
  },
  {
    "status": 200,
    "response": {
      "combined_score": 0.50175,
      "confidence": 0.50175,
      "content_id": "d6c15d13-ac69-4e9b-87a5-a0b0457745b1",
      "guess": "unsure",
      "label": "The signals are inconclusive; this is not a determination of authorship.",
      "model_score": 0.435,
      "style_score": 0.5685
    },
    "sent": "A successful project begins with a clear plan. The plan identifies the main goal, breaks the work in"
  },
  {
    "status": 200,
    "response": {
      "combined_score": 0.74905,
      "confidence": 0.74905,
      "content_id": "f2d6ae17-aff5-4ab2-a85a-3cf96d0bd84e",
      "guess": "ai",
      "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
      "model_score": 0.9853,
      "style_score": 0.5128
    },
    "sent": "We the People of the United States, in Order to form a more perfect Union, establish Justice, insure"
  }
]
```

Criterion 4 — appeal response and audit evidence for a real content ID:

```json
{
  "sent": "text length=139; creator_id=eval_appeal_t1_1",
  "content_id": "186b55a0-affe-43af-9b0e-d38c5466b069",
  "submission": {
    "status": 200,
    "response": {
      "combined_score": 0.5468999999999999,
      "confidence": 0.5468999999999999,
      "content_id": "186b55a0-affe-43af-9b0e-d38c5466b069",
      "guess": "unsure",
      "label": "The signals are inconclusive; this is not a determination of authorship.",
      "model_score": 0.6949,
      "style_score": 0.3989
    }
  },
  "audit_before_status": 200,
  "audit_before_error": null,
  "decision_before": {
    "combined_score": 0.5468999999999999,
    "content_id": "186b55a0-affe-43af-9b0e-d38c5466b069",
    "creator_id": "eval_appeal_t1_1",
    "guess": "unsure",
    "label": "The signals are inconclusive; this is not a determination of authorship.",
    "model_score": 0.6949,
    "status": "decided",
    "style_score": 0.3989,
    "timestamp": "2026-11-01T23:32:51+00:00"
  },
  "appeal": {
    "status": 200,
    "response": {
      "content_id": "186b55a0-affe-43af-9b0e-d38c5466b069",
      "message": "Your appeal has been received and is under review.",
      "status": "under_review"
    }
  },
  "audit_after_status": 200,
  "audit_after_error": null,
  "decision_after": {
    "combined_score": 0.5468999999999999,
    "content_id": "186b55a0-affe-43af-9b0e-d38c5466b069",
    "creator_id": "eval_appeal_t1_1",
    "guess": "unsure",
    "label": "The signals are inconclusive; this is not a determination of authorship.",
    "model_score": 0.6949,
    "status": "decided",
    "style_score": 0.3989,
    "timestamp": "2026-11-01T23:32:51+00:00"
  },
  "appeal_entry": {
    "content_id": "186b55a0-affe-43af-9b0e-d38c5466b069",
    "creator_id": "eval_appeal_t1_1",
    "event": "appeal",
    "reasoning": "This is a test appeal for an existing evaluation decision.",
    "status": "under_review",
    "timestamp": "2026-11-01T23:32:51+00:00"
  },
  "checks": {
    "submission_succeeded": true,
    "appeal_returned_200_under_review": true,
    "appeal_was_appended": true,
    "original_decision_unchanged": true
  }
}
```

Criterion 5 — the oversized request was accepted instead of rejected:

```json
{
  "status": 200,
  "sent": "text length=100001; creator_id=eval_bad_oversized",
  "response": {
    "combined_score": 0.5821500000000001,
    "confidence": 0.5821500000000001,
    "content_id": "24067fff-b0eb-4e84-838e-4031b5e3d4ef",
    "guess": "unsure",
    "label": "The signals are inconclusive; this is not a determination of authorship.",
    "model_score": 0.9976,
    "style_score": 0.1667
  },
  "rejection_entry": null
}
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

The score and label outcomes were identical across all three trials for the
same inputs; content IDs and audit timestamps naturally differed. This run
showed no score instability.

Criterion 2 missed because the AI-generated and synthetic human-style groups
had medians of 0.5740 and 0.4092, a 0.1648 gap rather than the required 0.20.
The model signal and style signal together did not separate these fixtures
enough; this is only a proxy result because the human-style samples are not
verified human writing. Criterion 5 missed at the route: `app.py::submit`
validates missing and blank text but does not enforce the criterion's
100,000-character maximum, so the 100,001-character sample was scored and
logged as a decision. Criterion 1's numeric count met the target on synthetic
proxies, but cannot establish a false-positive rate on the instructor's own
writing.

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
