"""
Inputs for the five acceptance criteria in criteria.md.

The human-style samples below are synthetic examples written for testing. They
are useful for exercising the evaluation workflow, but are not anyone's
personal writing or ground-truth human-authored samples.
"""

_HUMAN_STYLE_TEXTS = [
    "I missed the bus by about thirty seconds, which was annoying because I "
    "could see it pulling away. I walked the rest of the way and got coffee "
    "from the place on the corner instead.",
    "The first version of the flyer looked fine on my screen, but the printer "
    "made the blue much darker. We changed the background and tried again "
    "after lunch.",
    "My neighbor keeps a little table of extra tomatoes by the gate. I took "
    "two yesterday and left a jar of the lemon jam my sister made.",
    "I don't mind rainy days, unless I have to carry groceries home. The paper "
    "bag split near the crosswalk, and an orange rolled under a parked car.",
    "We started the meeting late because the room was locked. Nobody seemed "
    "too bothered; people used the time to compare notes about the new schedule.",
    "I thought the old chair was beyond repair, but my uncle tightened two "
    "bolts and replaced a strip of fabric. It is still lopsided, just less so.",
    "The garden looked rough after the frost. A few plants survived near the "
    "wall, and the mint has somehow taken over the patch again.",
    "I usually make a list before shopping and still forget one thing. This "
    "time it was rice, so dinner became eggs and whatever vegetables were left.",
    "There was a tiny crack in the mug when I bought it, but I kept using it "
    "for pencils. The handle finally came off while I was cleaning the desk.",
    "We took the longer trail because the shorter one was muddy. It took an "
    "extra hour, but we saw a heron standing perfectly still by the water.",
]

_AI_STYLE_TEXTS = [
    "A successful project begins with a clear plan. The plan identifies the "
    "main goal, breaks the work into manageable tasks, and assigns "
    "responsibilities. Regular check-ins help the team notice problems early "
    "and adjust before deadlines are missed.",
    "Public libraries play an important role in their communities. They "
    "provide access to books, technology, and learning resources for people "
    "of all ages. By creating welcoming spaces and offering useful programs, "
    "libraries support education and connection.",
    "Preparing for a job interview can help candidates communicate their "
    "experience with confidence. Researching the organization, reviewing "
    "common questions, and preparing thoughtful examples are practical steps. "
    "A follow-up message can also leave a positive impression.",
    "Cities can make transportation more accessible by improving sidewalks, "
    "expanding reliable public transit, and creating safer routes for "
    "cyclists. These changes give residents more choices and can reduce "
    "congestion in busy neighborhoods.",
    "Good communication helps a team work through challenges. When people "
    "share progress, ask questions, and give specific feedback, they can "
    "identify misunderstandings sooner. This creates a stronger foundation "
    "for collaboration and better results.",
]

_LABEL_RANGE_TEXTS = [
    "Petrichor, susurrus, defenestration, ultracrepidarian, callipygian, "
    "susurration, apricity, and nudiustertian.",
    _AI_STYLE_TEXTS[0],
    "We the People of the United States, in Order to form a more perfect "
    "Union, establish Justice, insure domestic Tranquility, provide for the "
    "common defence, promote the general Welfare, and secure the Blessings "
    "of Liberty to ourselves and our Posterity, do ordain and establish this "
    "Constitution for the United States of America.",
]

SCENARIOS = [
    {
        "name": "synthetic human-style proxy (not personal writing)",
        "criterion": 1,
        "target": "≤ 1 AI guess of 10 in each trial",
        "provenance_note": (
            "Synthetic human-style examples supplied by the instructor for "
            "testing; they do not establish the personal-writing criterion."
        ),
        "texts": _HUMAN_STYLE_TEXTS,
    },
    {
        "name": "score spread (synthetic text groups)",
        "criterion": 2,
        "target": "AI median at least 0.20 above human-style median in each trial",
        "provenance_note": (
            "AI group is generated text; human-style group is synthetic and "
            "not verified human-authored."
        ),
        "groups": {
            "ai_generated": _AI_STYLE_TEXTS,
            "human_style_synthetic": _HUMAN_STYLE_TEXTS[:5],
        },
    },
    {
        "name": "label coverage across score range",
        "criterion": 3,
        "target": "all 3 labels in each trial",
        "texts": _LABEL_RANGE_TEXTS,
    },
    {
        "name": "three real appeal flows",
        "criterion": 4,
        "target": "3 of 3 appeals recorded; original decisions unchanged",
        "appeals": [
            {
                "text": "The hallway light flickered twice before it went out. "
                "I found a replacement bulb in the kitchen drawer and left "
                "the old one on the counter.",
                "reasoning": "This is a test appeal for an existing evaluation decision.",
            },
            {
                "text": "Our group moved the meeting to Thursday because two "
                "people were traveling. I sent the updated calendar invite "
                "after everyone agreed.",
                "reasoning": "Please review this test decision; the text is only a fixture.",
            },
            {
                "text": "The parcel arrived a day early, although the box was "
                "dented on one corner. Nothing inside was damaged.",
                "reasoning": "I am submitting a test appeal to verify the audit trail.",
            },
        ],
    },
    {
        "name": "invalid and oversized text inputs",
        "criterion": 5,
        "target": "5 of 5 rejected with 400/413 and logged",
        "bodies": [
            {"creator_id": "eval_bad_missing"},
            {"text": None, "creator_id": "eval_bad_null"},
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": " \t\n ", "creator_id": "eval_bad_whitespace"},
            {"text": "x" * 100001, "creator_id": "eval_bad_oversized"},
        ],
    },
]


def validate() -> list[str]:
    """Complain about malformed scenarios before the evaluation starts."""
    problems = []
    criteria = []

    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        criterion = scenario.get("criterion")
        if criterion in criteria:
            problems.append(f"criterion {criterion} appears more than once")
        criteria.append(criterion)

        input_kinds = [
            key for key in ("texts", "bodies", "groups", "appeals")
            if key in scenario
        ]
        if len(input_kinds) != 1:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') must have exactly "
                "one of texts, bodies, groups, or appeals"
            )
            continue

        kind = input_kinds[0]
        if kind == "texts":
            texts = scenario["texts"]
            if not texts:
                problems.append(f"scenario {i} has no texts")
            for j, text in enumerate(texts, 1):
                if not isinstance(text, str) or not text.strip():
                    problems.append(f"scenario {i}, text {j} is empty or not a string")

        elif kind == "bodies":
            bodies = scenario["bodies"]
            if not bodies:
                problems.append(f"scenario {i} has no request bodies")
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(f"scenario {i}, body {j} is not a dict")

        elif kind == "groups":
            groups = scenario["groups"]
            if not isinstance(groups, dict) or len(groups) < 2:
                problems.append(f"scenario {i} needs at least two text groups")
                continue
            for group_name, texts in groups.items():
                if not texts:
                    problems.append(f"scenario {i}, group '{group_name}' is empty")
                for j, text in enumerate(texts, 1):
                    if not isinstance(text, str) or not text.strip():
                        problems.append(
                            f"scenario {i}, group '{group_name}', text {j} "
                            "is empty or not a string"
                        )

        else:
            appeals = scenario["appeals"]
            if not appeals:
                problems.append(f"scenario {i} has no appeals")
            for j, appeal in enumerate(appeals, 1):
                if not isinstance(appeal, dict):
                    problems.append(f"scenario {i}, appeal {j} is not a dict")
                    continue
                if not isinstance(appeal.get("text"), str) or not appeal["text"].strip():
                    problems.append(f"scenario {i}, appeal {j} has no non-empty text")
                if not isinstance(appeal.get("reasoning"), str) or not appeal["reasoning"].strip():
                    problems.append(
                        f"scenario {i}, appeal {j} has no non-empty reasoning"
                    )

    if sorted(c for c in criteria if isinstance(c, int)) != [1, 2, 3, 4, 5]:
        problems.append("scenarios must include each criterion number 1 through 5 once")
    return problems
