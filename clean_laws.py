
import json
import re
from pathlib import Path

source = Path("qonunradar_laws.json")
output = Path("qonunradar_laws_clean.json")

data = json.loads(source.read_text(encoding="utf-8"))

unwanted_lines = {
    "Ҳужжатга таклиф юбориш",
    "Аудиони тинглаш",
    "Ҳужжат элементидан ҳавола олиш",
    "Улашиш",
    "Telegram",
    "Facebook",
    "Twitter",
    "Instagram",
    "PDF-faylidagi rasmiy manba",
}

def clean_text(text):
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line in unwanted_lines:
            continue

        cleaned.append(line)

    result = "\n".join(cleaned)
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result

# Support either a list or a dictionary containing laws.
laws = data if isinstance(data, list) else data.get("laws", [])

for law in laws:
    if law.get("full_text"):
        law["full_text"] = clean_text(law["full_text"])
        law["verified"] = False

output.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Cleaned dataset saved:", output)
print("Records processed:", len(laws))
