#!/usr/bin/env python3
"""
Run the five acceptance criteria three times each.

    python app.py
    python run_eval.py --label before

Scenarios are defined in scenarios.py. This runner supports submissions,
malformed request bodies, grouped score comparisons, and complete appeal
flows, including checking their audit-log effects.
"""

import argparse
import datetime as dt
import json
import statistics
import sys
from pathlib import Path

import config

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass


DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"


def describe(body):
    """A short note about the input, without dumping oversized text to the report."""
    if "text" not in body:
        return f"fields={list(body)} (missing text)"
    text = body["text"]
    if isinstance(text, str):
        return f"text length={len(text)}; creator_id={body.get('creator_id', '—')}"
    return f"text type={type(text).__name__}; creator_id={body.get('creator_id', '—')}"


def send_json(requests, method, url, body=None, timeout=90.0):
    """Send JSON and retain the actual status and parsed response in the report."""
    try:
        response = requests.request(method, url, json=body, timeout=timeout)
    except requests.RequestException as exc:
        return {"status": None, "error": f"{type(exc).__name__}: {exc}"}

    result = {"status": response.status_code}
    try:
        result["response"] = response.json() if response.content else {}
    except ValueError as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["content_type"] = response.headers.get("Content-Type")
        result["body_preview"] = response.text[:300]
    return result


def fetch_entries(requests, url, timeout):
    result = send_json(requests, "GET", f"{url}/log?limit=1000", timeout=timeout)
    if result.get("status") != 200 or not isinstance(result.get("response"), dict):
        return None, result
    entries = result["response"].get("entries")
    if not isinstance(entries, list):
        return None, result
    return entries, result


def entries_for(entries, content_id):
    if entries is None or not content_id:
        return []
    return [entry for entry in entries if entry.get("content_id") == content_id]


def submission_result(requests, url, body, timeout, sent=None, group=None):
    result = send_json(requests, "POST", f"{url}/submit", body, timeout)
    if sent is not None:
        result["sent"] = sent
    if group is not None:
        result["group"] = group
    return result


def run_appeal(requests, url, appeal, index, trial, timeout):
    creator_id = f"eval_appeal_t{trial}_{index}"
    submission = send_json(
        requests,
        "POST",
        f"{url}/submit",
        {"text": appeal["text"], "creator_id": creator_id},
        timeout,
    )
    submit_payload = submission.get("response")
    content_id = (
        submit_payload.get("content_id")
        if isinstance(submit_payload, dict)
        else None
    )
    before_entries, before_log = fetch_entries(requests, url, timeout)
    before_matches = entries_for(before_entries, content_id)
    decision_before = next(
        (entry for entry in before_matches if entry.get("status") == "decided"),
        None,
    )

    appeal_result = {"status": None, "error": "Submission did not return a content_id"}
    after_entries = before_entries
    after_log = before_log
    if submission.get("status") == 200 and isinstance(content_id, str):
        appeal_result = send_json(
            requests,
            "POST",
            f"{url}/appeal",
            {"content_id": content_id, "reasoning": appeal["reasoning"]},
            timeout,
        )
        after_entries, after_log = fetch_entries(requests, url, timeout)

    after_matches = entries_for(after_entries, content_id)
    decision_after = next(
        (entry for entry in after_matches if entry.get("status") == "decided"),
        None,
    )
    appeal_entry = next(
        (
            entry
            for entry in after_matches
            if entry.get("event") == "appeal"
            and entry.get("status") == "under_review"
        ),
        None,
    )
    appeal_was_appended = (
        decision_before is not None
        and appeal_entry is not None
        and after_matches.index(appeal_entry) > after_matches.index(decision_before)
    )
    return {
        "sent": f"text length={len(appeal['text'])}; creator_id={creator_id}",
        "content_id": content_id,
        "submission": submission,
        "audit_before_status": before_log.get("status"),
        "audit_before_error": before_log.get("error"),
        "decision_before": decision_before,
        "appeal": appeal_result,
        "audit_after_status": after_log.get("status"),
        "audit_after_error": after_log.get("error"),
        "decision_after": decision_after,
        "appeal_entry": appeal_entry,
        "checks": {
            "submission_succeeded": submission.get("status") == 200,
            "appeal_returned_200_under_review": (
                appeal_result.get("status") == 200
                and isinstance(appeal_result.get("response"), dict)
                and appeal_result["response"].get("status") == "under_review"
            ),
            "appeal_was_appended": appeal_was_appended,
            "original_decision_unchanged": (
                decision_before is not None and decision_before == decision_after
            ),
        },
    }


def run_scenario_trial(requests, scenario, url, trial, timeout):
    if "texts" in scenario:
        return [
            submission_result(
                requests,
                url,
                {
                    "text": text,
                    "creator_id": f"eval_c{scenario['criterion']}_t{trial}_{i}",
                },
                timeout,
                sent=text[:100],
            )
            for i, text in enumerate(scenario["texts"], 1)
        ]

    if "groups" in scenario:
        results = []
        for group, texts in scenario["groups"].items():
            for i, text in enumerate(texts, 1):
                results.append(
                    submission_result(
                        requests,
                        url,
                        {
                            "text": text,
                            "creator_id": (
                                f"eval_c{scenario['criterion']}_{group}_t{trial}_{i}"
                            ),
                        },
                        timeout,
                        sent=text[:100],
                        group=group,
                    )
                )
        return results

    if "appeals" in scenario:
        return [
            run_appeal(requests, url, appeal, i, trial, timeout)
            for i, appeal in enumerate(scenario["appeals"], 1)
        ]

    results = []
    for body in scenario["bodies"]:
        result = send_json(requests, "POST", f"{url}/submit", body, timeout)
        result["sent"] = describe(body)
        results.append(result)

    entries, log_result = fetch_entries(requests, url, timeout)
    for result, body in zip(results, scenario["bodies"]):
        creator_id = body.get("creator_id")
        matching = [
            entry for entry in entries or []
            if entry.get("creator_id") == creator_id
            and entry.get("event") == "rejected"
        ]
        result["rejection_entry"] = matching[-1] if matching else None
        if entries is None:
            result["audit_log_error"] = log_result
    return results


def score_trial(scenario, results):
    criterion = scenario["criterion"]

    if criterion == 1:
        ai_count = sum(
            result.get("response", {}).get("guess") == "ai"
            for result in results
            if isinstance(result.get("response"), dict)
        )
        complete = len(results) == 10 and all(
            result.get("status") == 200 for result in results
        )
        return {
            "value": f"{ai_count}/10",
            "passed": complete and ai_count <= 1,
        }

    if criterion == 2:
        group_scores = {}
        group_results = {}
        for group in ("ai_generated", "human_style_synthetic"):
            matching = [r for r in results if r.get("group") == group]
            group_results[group] = matching
            group_scores[group] = [
                r["response"]["combined_score"]
                for r in matching
                if r.get("status") == 200
                and isinstance(r.get("response"), dict)
                and isinstance(r["response"].get("combined_score"), (int, float))
            ]
        ai_scores = group_scores["ai_generated"]
        human_scores = group_scores["human_style_synthetic"]
        complete = all(
            len(group_results[group]) == 5
            and all(result.get("status") == 200 for result in group_results[group])
            for group in group_results
        )
        if len(ai_scores) != 5 or len(human_scores) != 5:
            return {"value": "incomplete score data", "passed": False}
        ai_median = statistics.median(ai_scores)
        human_median = statistics.median(human_scores)
        gap = ai_median - human_median
        return {
            "value": (
                f"AI median {ai_median:.4f}; human-style median {human_median:.4f}; "
                f"gap {gap:.4f}"
            ),
            "passed": complete and gap >= 0.20,
            "ai_median": ai_median,
            "human_style_median": human_median,
            "median_gap": gap,
        }

    if criterion == 3:
        guesses = {
            result.get("response", {}).get("guess")
            for result in results
            if isinstance(result.get("response"), dict)
        }
        reached = len(guesses.intersection({"human", "unsure", "ai"}))
        complete = len(results) == 3 and all(
            result.get("status") == 200 for result in results
        )
        return {"value": f"{reached}/3", "passed": complete and reached == 3}

    if criterion == 4:
        passed_count = sum(
            all(result.get("checks", {}).values())
            and len(result.get("checks", {})) == 4
            for result in results
        )
        complete = len(results) == 3
        return {
            "value": f"{passed_count}/3",
            "passed": complete and passed_count == 3,
        }

    passed_count = sum(
        result.get("status") in (400, 413)
        and result.get("rejection_entry") is not None
        for result in results
    )
    complete = len(results) == 5
    return {
        "value": f"{passed_count}/5",
        "passed": complete and passed_count == 5,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print(
            "The `requests` package isn't installed.\n"
            "Run: pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        import scenarios
    except ImportError:
        print("No scenarios.py found. Fill it in before running the evaluation.",
              file=sys.stderr)
        sys.exit(1)

    problems = scenarios.validate()
    if problems:
        print("scenarios.py has problems:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    try:
        health = requests.get(f"{args.url}/health", timeout=5)
        health.raise_for_status()
    except requests.RequestException as exc:
        print(f"Nothing answering at {args.url}. Start it with `python app.py`: {exc}",
              file=sys.stderr)
        sys.exit(1)

    if args.trials < 3:
        print(f"!! {args.trials} trial(s). The submission asks for three.\n")

    rows = []
    for scenario in scenarios.SCENARIOS:
        print(f"\n{scenario['name']}  (criterion {scenario['criterion']})")
        trials = []
        scores = []
        for trial in range(1, args.trials + 1):
            results = run_scenario_trial(
                requests, scenario, args.url, trial, args.timeout
            )
            score = score_trial(scenario, results)
            trials.append(results)
            scores.append(score)
            print(f"  trial {trial}: {score['value']}")
        rows.append({"scenario": scenario, "trials": trials, "scores": scores})

    write_report(rows, args)


def write_report(rows, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"run_{stamp}{label}.md"

    n = args.trials
    headers = " | ".join(f"Run {i}" for i in range(1, n + 1))
    divider = "|".join(["---"] * n)
    lines = [
        f"# Run log{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `run_eval.py::main`",
        "- Submission service: `app.py::submit`",
        "- Appeal service: `app.py::appeal`; audit checks: `app.py::get_log`",
        "- Scoring: `scoring.py::combine_signals`",
        f"- {n} trials per criterion · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Criterion | Target | " + headers + " | Verdict |",
        "|---|---|" + divider + "|---|",
    ]

    for row in rows:
        scenario = row["scenario"]
        criterion_name = f"{scenario['criterion']}. {scenario['name']}"
        values = " | ".join(score["value"] for score in row["scores"])
        passed = all(score["passed"] for score in row["scores"])
        verdict = "MET" if passed else "MISSED"
        if scenario.get("provenance_note"):
            verdict = "MISSED (PROXY ONLY)"
        lines.append(
            f"| {criterion_name} | {scenario['target']} | {values} | {verdict} |"
        )

    lines += ["", "## Dataset notes", ""]
    for row in rows:
        note = row["scenario"].get("provenance_note")
        if note:
            lines.append(f"- Criterion {row['scenario']['criterion']}: {note}")

    lines += [
        "",
        "## Real output",
        "",
        "Each section below contains the actual parsed JSON responses and, where "
        "relevant, the audit-log entries from all three trials.",
        "",
    ]
    for row in rows:
        scenario = row["scenario"]
        lines += [f"### Criterion {scenario['criterion']}: {scenario['name']}", ""]
        for trial_number, (results, score) in enumerate(
            zip(row["trials"], row["scores"]), 1
        ):
            lines += [
                f"**Trial {trial_number} — {score['value']}**",
                "",
                "```json",
                json.dumps(results, indent=2, ensure_ascii=False),
                "```",
                "",
            ]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")
    print("The report contains the five-row verdict table and trial JSON.")


if __name__ == "__main__":
    main()
