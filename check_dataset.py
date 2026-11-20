
import json

with open("qonunradar_laws_clean.json", encoding="utf-8") as f:
    data = json.load(f)

laws = data if isinstance(data, list) else data["laws"]

downloaded = [
    law for law in laws
    if (law.get("full_text") or "").strip()
]

print("Total laws:", len(laws))
print("Laws with full text:", len(downloaded))
print("Laws without text:", len(laws) - len(downloaded))

for law in downloaded:
    print(
        "Downloaded:",
        law.get("law_id"),
        len(law["full_text"]),
        "characters"
    )
