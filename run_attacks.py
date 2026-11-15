import json
import time
from collections import defaultdict

from app import ask_llm, is_leaked

REPEATS = 1     # har attack kitni baar bhejna hai
DELAY = 1.0     # do calls ke beech ruk-na (rate limit se bachne ke liye)


def load_attacks():
    with open("attacks/attacks.json", encoding="utf-8") as f:
        return json.load(f)


def run_mode(mode, attacks):
    results = []
    for a in attacks:
        for run in range(1, REPEATS + 1):
            reply = ask_llm(a["prompt"], mode)
            error = reply.startswith("Error:")
            leaked = False if error else is_leaked(reply)
            status = "ERROR" if error else ("SUCCESS" if leaked else "REFUSED")
            print(f"[{mode}] #{a['id']:>2} {a['category']:<18} {status}")
            results.append({
                "mode": mode,
                "id": a["id"],
                "category": a["category"],
                "owasp": a["owasp"],
                "prompt": a["prompt"],
                "reply": reply,
                "status": status,
            })
            time.sleep(DELAY)
    return results


def summarize(results, mode):
    valid = [r for r in results if r["mode"] == mode and r["status"] != "ERROR"]
    if not valid:
        print(f"\n{mode}: no valid results")
        return
    succ = sum(1 for r in valid if r["status"] == "SUCCESS")
    print(f"\n=== {mode.upper()}: {succ}/{len(valid)} attacks succeeded "
          f"({round(100 * succ / len(valid))}%) ===")
    by_cat = defaultdict(lambda: [0, 0])
    for r in valid:
        by_cat[r["category"]][1] += 1
        if r["status"] == "SUCCESS":
            by_cat[r["category"]][0] += 1
    for cat, (s, t) in by_cat.items():
        print(f"  {cat:<18} {s}/{t}")


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