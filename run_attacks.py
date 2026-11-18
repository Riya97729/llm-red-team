import json
import time
from collections import defaultdict

from app import ask_llm
from classifier import classify

REPEATS = 3     # har attack kitni baar bhejna hai
DELAY = 3.0     # do calls ke beech ruk-na (rate limit se bachne ke liye)
MAX_RETRIES = 3


def load_attacks():
    with open("attacks/attacks.json", encoding="utf-8") as f:
        return json.load(f)


def ask_with_retry(prompt, mode):
    reply = ask_llm(prompt, mode)
    tries = 0
    while reply.startswith("Error:") and tries < MAX_RETRIES:
        tries += 1
        wait = 10 * tries
        print(f"   error, retry {tries}/{MAX_RETRIES} after {wait}s...")
        time.sleep(wait)
        reply = ask_llm(prompt, mode)
    return reply


def run_mode(mode, attacks):
    results = []
    for a in attacks:
        for run in range(1, REPEATS + 1):
            reply = ask_with_retry(a["prompt"], mode)
            status = classify(reply)
            print(f"[{mode}] #{a['id']:>2} run{run} {a['category']:<18} {status}")
            results.append({
                "mode": mode,
                "id": a["id"],
                "run": run,
                "category": a["category"],
                "owasp": a["owasp"],
                "prompt": a["prompt"],
                "reply": reply,
                "status": status,
            })
            time.sleep(DELAY)
    return results


def pct(n, total):
    return round(100 * n / total) if total else 0


def summarize(results, mode):
    all_runs = [r for r in results if r["mode"] == mode]
    valid = [r for r in all_runs if r["status"] != "ERROR"]
    errors = len(all_runs) - len(valid)
    total = len(valid)
    if total == 0:
        print(f"\n{mode}: no valid results")
        return
    full = sum(1 for r in valid if r["status"] == "FULL_LEAK")
    partial = sum(1 for r in valid if r["status"] == "PARTIAL_LEAK")

    print(f"\n=== {mode.upper()} ({total} valid runs, errors: {errors}) ===")
    print(f"  Full leak:    {full}/{total} ({pct(full, total)}%)")
    print(f"  Partial leak: {partial}/{total} ({pct(partial, total)}%)")
    print(f"  Any leak:     {full + partial}/{total} ({pct(full + partial, total)}%)")

    by_cat = defaultdict(lambda: [0, 0, 0])   # full, partial, total
    for r in valid:
        by_cat[r["category"]][2] += 1
        if r["status"] == "FULL_LEAK":
            by_cat[r["category"]][0] += 1
        elif r["status"] == "PARTIAL_LEAK":
            by_cat[r["category"]][1] += 1
    for cat, (f, p, t) in by_cat.items():
        print(f"  {cat:<18} full {f}/{t}   partial {p}/{t}")


if __name__ == "__main__":
    attacks = load_attacks()
    all_results = []
    for mode in ["weak", "hardened"]:
        all_results += run_mode(mode, attacks)

    with open("results/results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    summarize(all_results, "weak")
    summarize(all_results, "hardened")
    print("\nSaved to results/results.json")