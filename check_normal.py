import json

from app import PROMPTS
from classifier import CANARY
from defenses import output_filter

with open("results/heldout_results.json", encoding="utf-8") as f:
    data = json.load(f)

for base in ["weak", "hardened"]:
    rows = [r for r in data["normal"] if r["base"] == base and r["status"] == "OK"]
    blocked = [r for r in rows if output_filter(r["reply"], PROMPTS[base])[1]]
    print(f"[{base}] blocked by the current output filter: {len(blocked)}/{len(rows)}")

print("\nWhere the secret appears in weak replies:")
for r in data["normal"]:
    if r["base"] != "weak" or r["status"] != "OK":
        continue
    i = r["reply"].lower().find(CANARY.lower())
    if i >= 0:
        start = max(0, i - 80)
        print(f"- {r['question']}")
        print("  ...", r["reply"][start:i + len(CANARY) + 40].replace("\n", " "), "...")
        