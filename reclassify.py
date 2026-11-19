import json

from classifier import classify

with open("results/mutation_results.json", encoding="utf-8") as f:
    results = json.load(f)

changed = 0
for r in results:
    new_status = classify(r["reply"])
    if new_status != r["status"]:
        changed += 1
        print(f"[{r['mode']}] #{r['id']} {r['mutation']}: {r['status']} -> {new_status}")
    r["status"] = new_status

print(f"\nChanged: {changed}")
for mode in ["weak", "hardened"]:
    runs = [r for r in results if r["mode"] == mode and r["status"] != "ERROR"]
    leaks = sum(1 for r in runs if r["status"] != "REFUSED")
    print(f"{mode}: {leaks}/{len(runs)} leaked")

with open("results/mutation_results_reclassified.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("Saved to results/mutation_results_reclassified.json")