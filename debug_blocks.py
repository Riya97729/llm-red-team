import json

from app import PROMPTS
from classifier import CANARY, CANARY_B64, normalize
from defenses import word_windows

REFUSAL_TEXT = "Sorry, I can't help with that."

with open("results/heldout_results.json", encoding="utf-8") as f:
    data = json.load(f)

for r in data["normal"]:
    if not r.get("output_blocked"):
        continue
    reply = r["reply"]
    prompt = PROMPTS[r["base"]]
    norm_reply = normalize(reply)
    norm_canary = normalize(CANARY)
    print(f"[{r['base']}] {r['question']}")
    print("  canary exact:     ", CANARY.lower() in reply.lower())
    print("  canary spelled:   ", norm_canary in norm_reply)
    print("  canary reversed:  ", norm_canary[::-1] in norm_reply)
    print("  canary base64:    ", CANARY_B64 in reply)
    print("  prompt overlap:   ", sorted(word_windows(reply) & word_windows(prompt))[:2])
    print("  overlap, refusal removed:",
          sorted(word_windows(reply) & word_windows(prompt.replace(REFUSAL_TEXT, "")))[:2])