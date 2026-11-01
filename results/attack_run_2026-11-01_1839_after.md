# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-01 18:39
- BROKE after review: **13**
- HELD after review: **43**

Verdicts use the same targets and judgment rules as the before run. The
100,000-character validation change does not affect any attack-set input;
the 60,000-character MF08 text remains under the limit.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `b758e409-dd79-473b-91e0-9da063b116b6` | unsure | 0.355 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `6de83490-cf4f-4922-af8b-15720fdc5753` | unsure | 0.572 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `5fa378d9-9853-4514-8a6d-fc64e0e25d70` | unsure | 0.633 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `5285332d-5cab-4913-a963-da7b3474eb2d` | unsure | 0.585 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `d627b2ff-31dc-4beb-9feb-1178a0a579f6` | unsure | 0.441 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `5b95a27c-2d91-4870-9097-08b5312c7e67` | unsure | 0.477 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `6a765fa6-3386-4afe-8f58-598cb13a0295` | unsure | 0.581 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `c656c6ba-6d29-45fc-abde-79168296e8ed` | unsure | 0.419 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `d323e167-8526-4b5a-aeb9-9479be6ee17b` | unsure | 0.634 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `858ef7d7-8efc-4dc0-ab4e-6203b5e3ac1e` | ai | 0.754 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `666c9fbc-c74c-48ca-9a24-8a4b5cc15115` | unsure | 0.553 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `fe53f8b5-2d5f-4adb-9d9f-0e244ede76d2` | unsure | 0.640 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c6f3812b-cdea-44db-b755-9b7d6ac13760` | unsure | 0.645 | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | `f84bf6c7-0a86-4f34-9639-0031f04c926c` | ai | 0.681 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `a77b3432-72b0-464a-8bd7-1b6c969234ed` | ai | 0.707 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `5daca2f0-76c7-4b1b-a6f2-4794cb6a0cd2` | ai | 0.686 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `3da98db9-4382-48f8-9b1d-d1a2206e56ac` | ai | 0.755 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `a4ac852d-c72e-4741-a6cc-02733efd715b` | unsure | 0.444 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c30c1ca1-a0ed-4b97-a00b-3f372b17fe56` | unsure | 0.435 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c9ab4cbc-8118-41a7-8fa6-0cbb07a84d97` | unsure | 0.377 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `8edfba6a-ac61-47c4-931f-cd14747c3a61` | unsure | 0.542 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `ec8d29bd-d95d-4489-bde4-a03e5f9d5834` | unsure | 0.559 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `fbe7ae5e-b9e9-4240-8b36-3001c4219835` | unsure | 0.606 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `50e439d4-3d10-4718-ac99-f00e39146ddb` | unsure | 0.524 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `e3b962f0-daf1-4c36-aaff-eb35cf1a2357` | human | 0.250 | HELD |
| MF04 | malformed | text is only punctuation | 200 | `44b6d72b-e211-48d3-9082-4c1441dddd71` | human | 0.256 | HELD |
| MF05 | malformed | text is a very long single word | 200 | `095ce2cc-d5ef-4e09-b572-0d291b33a2d5` | unsure | 0.582 | HELD |
| MF06 | malformed | text is emoji only | 200 | `67026caa-f94f-48b9-be38-0a9a6e8f3e05` | ai | 0.748 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `95045cf6-7d83-4df6-948d-a97ffdac9bc4` | ai | 0.703 | HELD |
| MF08 | malformed | text is 60,000 characters | 200 | `82f2d35f-f705-4053-bb09-60926040d0f1` | ai | 0.857 | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `8a9798cc-db0a-40ca-9115-751a443f716b` | human | 0.190 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `201f4a3f-1bf9-4f9a-ad23-6815ee38a850` | human | 0.190 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `d732e041-e429-4d26-a369-78ba053ce980` | human | 0.190 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `53743631-d2c8-4ec6-bfb9-ef33f12b93d9` | human | 0.190 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `f48d72b4-3c7c-4f28-9d13-bfad4fe9f87d` | human | 0.190 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 9 | 1 |
| `false_positive` | 8 | 4 | 4 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "b758e409-dd79-473b-91e0-9da063b116b6",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.35475,
  "model_score": 0.1635,
  "style_score": 0.546,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "6de83490-cf4f-4922-af8b-15720fdc5753",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.57225,
  "model_score": 0.5943,
  "style_score": 0.5502,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "5fa378d9-9853-4514-8a6d-fc64e0e25d70",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.63255,
  "model_score": 0.6662,
  "style_score": 0.5989,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "5285332d-5cab-4913-a963-da7b3474eb2d",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.58525,
  "model_score": 0.6114,
  "style_score": 0.5591,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "d627b2ff-31dc-4beb-9feb-1178a0a579f6",
  "creator_id": "attacker_EV05",
  "guess": "unsure",
  "confidence": 0.44099999999999995,
  "model_score": 0.3212,
  "style_score": 0.5608,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "5b95a27c-2d91-4870-9097-08b5312c7e67",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.47675,
  "model_score": 0.5727,
  "style_score": 0.3808,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "6a765fa6-3386-4afe-8f58-598cb13a0295",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5809,
  "model_score": 0.5862,
  "style_score": 0.5756,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c656c6ba-6d29-45fc-abde-79168296e8ed",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.41919999999999996,
  "model_score": 0.2452,
  "style_score": 0.5932,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "d323e167-8526-4b5a-aeb9-9479be6ee17b",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.63385,
  "model_score": 0.7042,
  "style_score": 0.5635,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "858ef7d7-8efc-4dc0-ab4e-6203b5e3ac1e",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.75445,
  "model_score": 0.9792,
  "style_score": 0.5297,
  "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "666c9fbc-c74c-48ca-9a24-8a4b5cc15115",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.55255,
  "model_score": 0.6175,
  "style_score": 0.4876,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "fe53f8b5-2d5f-4adb-9d9f-0e244ede76d2",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.6396999999999999,
  "model_score": 0.7387,
  "style_score": 0.5407,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c6f3812b-cdea-44db-b755-9b7d6ac13760",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.6445000000000001,
  "model_score": 0.8051,
  "style_score": 0.4839,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "f84bf6c7-0a86-4f34-9639-0031f04c926c",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.68055,
  "model_score": 0.8329,
  "style_score": 0.5282,
  "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "a77b3432-72b0-464a-8bd7-1b6c969234ed",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.70695,
  "model_score": 0.8005,
  "style_score": 0.6134,
  "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "5daca2f0-76c7-4b1b-a6f2-4794cb6a0cd2",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.68585,
  "model_score": 0.8814,
  "style_score": 0.4903,
  "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "3da98db9-4382-48f8-9b1d-d1a2206e56ac",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.7546,
  "model_score": 0.8816,
  "style_score": 0.6276,
  "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "a4ac852d-c72e-4741-a6cc-02733efd715b",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.44409999999999994,
  "model_score": 0.3223,
  "style_score": 0.5659,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c30c1ca1-a0ed-4b97-a00b-3f372b17fe56",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.43520000000000003,
  "model_score": 0.4625,
  "style_score": 0.4079,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c9ab4cbc-8118-41a7-8fa6-0cbb07a84d97",
  "creator_id": "attacker_PI02",
  "guess": "unsure",
  "confidence": 0.37715000000000004,
  "model_score": 0.2044,
  "style_score": 0.5499,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "8edfba6a-ac61-47c4-931f-cd14747c3a61",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.54245,
  "model_score": 0.5943,
  "style_score": 0.4906,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "ec8d29bd-d95d-4489-bde4-a03e5f9d5834",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.5587500000000001,
  "model_score": 0.4998,
  "style_score": 0.6177,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "fbe7ae5e-b9e9-4240-8b36-3001c4219835",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.60555,
  "model_score": 0.6401,
  "style_score": 0.571,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "50e439d4-3d10-4718-ac99-f00e39146ddb",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.52425,
  "model_score": 0.5583,
  "style_score": 0.4902,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "e3b962f0-daf1-4c36-aaff-eb35cf1a2357",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.25,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "The signals suggest this text may be human-written; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "44b6d72b-e211-48d3-9082-4c1441dddd71",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.2556,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "The signals suggest this text may be human-written; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "095ce2cc-d5ef-4e09-b572-0d291b33a2d5",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.5821500000000001,
  "model_score": 0.9976,
  "style_score": 0.1667,
  "label": "The signals are inconclusive; this is not a determination of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "67026caa-f94f-48b9-be38-0a9a6e8f3e05",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.7484500000000001,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "95045cf6-7d83-4df6-948d-a97ffdac9bc4",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.7032,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "82f2d35f-f705-4053-bb09-60926040d0f1",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.857,
  "model_score": 0.9876,
  "style_score": 0.7264,
  "label": "The signals suggest this text may be AI-generated; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "8a9798cc-db0a-40ca-9115-751a443f716b",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.1903,
  "model_score": 0.0287,
  "style_score": 0.3519,
  "label": "The signals suggest this text may be human-written; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "201f4a3f-1bf9-4f9a-ad23-6815ee38a850",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.1903,
  "model_score": 0.0287,
  "style_score": 0.3519,
  "label": "The signals suggest this text may be human-written; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "d732e041-e429-4d26-a369-78ba053ce980",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.1903,
  "model_score": 0.0287,
  "style_score": 0.3519,
  "label": "The signals suggest this text may be human-written; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "53743631-d2c8-4ec6-bfb9-ef33f12b93d9",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.1903,
  "model_score": 0.0287,
  "style_score": 0.3519,
  "label": "The signals suggest this text may be human-written; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "f48d72b4-3c7c-4f28-9d13-bfad4fe9f87d",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.1903,
  "model_score": 0.0287,
  "style_score": 0.3519,
  "label": "The signals suggest this text may be human-written; this is not proof of authorship.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```
