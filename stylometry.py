"""
Signal two: the style signal.

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

The measurements describe the text without interpreting its meaning. The
style score combines sentence-length variation and vocabulary repetition.
Punctuation density is also reported as a diagnostic, but is not included in
the score because punctuation frequency alone has no dependable direction.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation appears per word?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── Text-shape measurements ──────────────────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies, relative to the mean sentence length.

    Returns:
        The coefficient of variation (sample standard deviation / mean).
        Returns 0.0 when fewer than two sentences have words.
    """
    lengths = [len(words(sentence)) for sentence in sentences(text)]
    lengths = [length for length in lengths if length > 0]
    if len(lengths) < 2:
        return 0.0

    mean_length = statistics.mean(lengths)
    return statistics.stdev(lengths) / mean_length


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words.

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    This measure tends to fall as text gets longer, so it is length-sensitive.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    How much punctuation there is, relative to the number of words.

    Returns:
        Punctuation characters per word; returns 0.0 when there are no words.
    """
    word_count = len(words(text))
    if not word_count:
        return 0.0
    punctuation_count = sum(
        1 for character in text if not character.isalnum() and not character.isspace()
    )
    return punctuation_count / word_count


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.**

    The score averages two bounded measurements. Low sentence-length
    variation and repeated vocabulary each raise the AI-like score. With
    fewer than two sentences, sentence variation is treated as neutral.

    Punctuation density is reported separately; its direction is too
    ambiguous to include without calibration data.
    """
    tokens = words(text)
    if not tokens:
        return 0.5

    sentence_lengths = [
        len(words(sentence)) for sentence in sentences(text)
    ]
    sentence_lengths = [length for length in sentence_lengths if length > 0]
    if len(sentence_lengths) < 2:
        variation_score = 0.5
    else:
        variation = statistics.stdev(sentence_lengths) / statistics.mean(sentence_lengths)
        variation_score = 1.0 / (1.0 + variation)

    repetition_score = 1.0 - type_token_ratio(text)
    return round((variation_score + repetition_score) / 2.0, 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    print("\nPunctuation density is diagnostic and is not included in style_signal.")
