"""
Turning two numbers into one, and one number into something a person can read.

`combine_signals` is where your false-positive decision from Milestone 1
actually gets made. Everything above it — the labels, the appeal path — is
downstream of a number this function produced.

`score_to_label` is where you stop writing for a machine and start writing for
a person. A score of 0.62 means nothing to a writer.

⚠️ Your README's **Signals and Scoring** section has to name the file and
function holding your combining rule. The grader checks your code against what
you claim, so that line should read `scoring.py::combine_signals`.
"""

import config


def combine_signals(model_score: float, style_score: float) -> float:
    """
    Combine two 0–1 signals into one 0–1 score.

    Both inputs point the same way: higher means more likely AI. Your output
    should too.

    Args:
        model_score: from `detector.model_signal` — how predictable the text is.
        style_score: from `stylometry.style_signal` — the shape of the text.

    Returns:
        A float from 0.0 (confidently human) to 1.0 (confidently AI).

    This function uses the weights in config.py. A weighted average makes
    disagreement pull toward the middle rather than letting either signal
    override the other.

    The weights are equal (0.5 each), so this is the arithmetic mean.
    """
    return (
        config.WEIGHT_MODEL_SIGNAL * model_score
        + config.WEIGHT_STYLE_SIGNAL * style_score
    )


def score_to_label(score: float) -> tuple[str, str]:
    """
    Turn a score into a guess and the text a reader actually sees.

    Returns:
        (guess, label_text) — where `guess` is a short machine-readable string
        like "ai" / "human" / "unsure", and `label_text` is the full sentence
        shown to a person.

    Labels use the thresholds in config.py and avoid presenting the score as
    proof of authorship.
    """
    if score >= config.AI_THRESHOLD:
        return (
            "ai",
            "The signals suggest this text may be AI-generated; this is not "
            "proof of authorship.",
        )
    if score <= config.HUMAN_THRESHOLD:
        return (
            "human",
            "The signals suggest this text may be human-written; this is not "
            "proof of authorship.",
        )
    return (
        "unsure",
        "The signals are inconclusive; this is not a determination of authorship.",
    )


def label_ranges() -> list[tuple[str, str]]:
    """
    The score range each label covers. Your README needs these beside the
    label text — given to you so the numbers can't drift apart from config.py.
    """
    return [
        (
            "high-confidence human",
            f"0.00 – {config.HUMAN_THRESHOLD:.2f} (inclusive)",
        ),
        (
            "unsure",
            f"above {config.HUMAN_THRESHOLD:.2f} and below {config.AI_THRESHOLD:.2f}",
        ),
        (
            "high-confidence AI",
            f"{config.AI_THRESHOLD:.2f} – 1.00 (inclusive)",
        ),
    ]
