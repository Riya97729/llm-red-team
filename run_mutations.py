import json
import time
from collections import defaultdict

from classifier import classify
from mutator import MUTATIONS
from run_attacks import ask_with_retry, load_attacks, DELAY


def run_mode(mode, attacks):
    results = []
    for a in attacks:
        for name, mutate in MUTATIONS.items():
            prompt = mutate(a["prompt"])
            reply = ask_with_retry(prompt, mode)
            status = classify(reply)
            print(f"[{mode}] #{a['id']:>2} {name:<10} {status}")
            results.append({
                "mode": mode,
                "id": a["id"],
                "mutation": name,
                "category": a["category"],
                "prompt": prompt,
                "reply": reply,
                "status": status,
            })
            time.sleep(DELAY)
    return results


def summarize(results, mode):
    runs = [r for r in results if r["mode"] == mode]
    valid = [r for r in runs if r["status"] != "ERROR"]
    errors = len(runs) - len(valid)
    if not valid:
        print(f"\n{mode}: no valid results")
        return
    leaks = sum(1 for r in valid if r["status"] != "REFUSED")
    print(f"\n=== {mode.upper()}: {leaks}/{len(valid)} leaked "
          f"({round(100 * leaks / len(valid))}%), errors: {errors} ===")
    by_mut = defaultdict(lambda: [0, 0])
    for r in valid:
        by_mut[r["mutation"]][1] += 1
        if r["status"] != "REFUSED":
            by_mut[r["mutation"]][0] += 1
    for name, (leaked, total) in by_mut.items():
        print(f"  {name:<10} {leaked}/{total}")


if __name__ == "__main__":
    attacks = load_attacks()
    all_results = []
    for mode in ["weak", "hardened"]:
        all_results += run_mode(mode, attacks)

    with open("results/mutation_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    summarize(all_results, "weak")
    summarize(all_results, "hardened")
    print("\nSaved to results/mutation_results.json")