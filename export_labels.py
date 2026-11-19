import csv
import json
import random

random.seed(42)

with open("results/results.json", encoding="utf-8") as f:
    results = json.load(f)

weak_full = [r for r in results if r["mode"] == "weak" and r["status"] == "FULL_LEAK"]
weak_ref = [r for r in results if r["mode"] == "weak" and r["status"] == "REFUSED"]
hardened = [r for r in results if r["mode"] == "hardened"]

sample = (
    random.sample(weak_full, 10)
    + random.sample(weak_ref, 10)
    + random.sample(hardened, 20)
)
random.shuffle(sample)

with open("results/to_label.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["n", "prompt", "reply", "human_label"])
    for i, r in enumerate(sample, start=1):
        writer.writerow([i, r["prompt"], r["reply"], ""])

key = [
    {"n": i, "mode": r["mode"], "id": r["id"], "run": r["run"], "classifier": r["status"]}
    for i, r in enumerate(sample, start=1)
]
with open("results/label_key.json", "w", encoding="utf-8") as f:
    json.dump(key, f, indent=2)

print("Saved results/to_label.csv (label this) and results/label_key.json (do not open yet)")