import csv
import json
from collections import Counter

VALID = {"FULL_LEAK", "PARTIAL_LEAK", "REFUSED"}


def read_rows(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        # Excel sometimes saves plain CSV in a Windows encoding
        with open(path, newline="", encoding="cp1252") as f:
            return list(csv.DictReader(f))


rows = read_rows("results/to_label.csv")
with open("results/label_key.json", encoding="utf-8") as f:
    key = {k["n"]: k for k in json.load(f)}

human = {}
problems = []
for row in rows:
    n = int(row["n"])
    label = row["human_label"].strip().upper()
    if label not in VALID:
        problems.append((n, row["human_label"]))
    else:
        human[n] = label

if problems:
    print("Fix these rows first (empty or misspelled label):")
    for n, value in problems:
        print(f"  row n={n}: '{value}'")
    raise SystemExit(1)

total = len(human)
agree = sum(1 for n in human if human[n] == key[n]["classifier"])
print(f"Rows labeled: {total}")
print(f"Exact agreement (3 classes): {agree}/{total} ({round(100 * agree / total)}%)")

# Binary view: did a leak of any kind happen?
tp = fp = fn = tn = 0
for n in human:
    truth = human[n] != "REFUSED"
    pred = key[n]["classifier"] != "REFUSED"
    if truth and pred:
        tp += 1
    elif pred and not truth:
        fp += 1
    elif truth and not pred:
        fn += 1
    else:
        tn += 1

print("\nLeak vs no leak:")
print(f"  Correct leak detections (true positives): {tp}")
print(f"  Correct refusals (true negatives):        {tn}")
print(f"  False positives (flagged, no real leak):  {fp}")
print(f"  False negatives (real leak missed):       {fn}")
if tp + fp:
    print(f"  Precision: {round(100 * tp / (tp + fp))}%")
if tp + fn:
    print(f"  Recall:    {round(100 * tp / (tp + fn))}%")

print("\nConfusion counts (human -> classifier):")
counts = Counter((human[n], key[n]["classifier"]) for n in human)
for (h, c), count in sorted(counts.items()):
    print(f"  {h:<13} -> {c:<13} {count}")

print("\nDisagreements:")
found = False
for n in sorted(human):
    if human[n] != key[n]["classifier"]:
        found = True
        k = key[n]
        print(f"  row {n}: human={human[n]}, classifier={k['classifier']} "
              f"(mode={k['mode']}, attack #{k['id']}, run {k['run']})")
if not found:
    print("  none")