# QonunRadar — 26 Lex.uz source dataset

This package contains **all 26 URLs you supplied** in one machine-readable manifest. The full legal text is **not included yet** because Lex.uz could not be reached from the file-generation environment. Two titles and basic metadata were checked via web viewing; the remaining titles are intentionally blank rather than guessed.

## Files
- `qonunradar_laws.json`: canonical manifest and future full-text storage.
- `sources.csv`: source inventory.
- `import_lex.py`: optional polite importer for an internet-connected machine.
- `legal_chunks.jsonl`: empty until importer runs successfully.
- `qonunradar.db`: created by importer with full-text search.

## Run
```bash
pip install -r requirements.txt
python import_lex.py --limit 2
python import_lex.py
```

The importer checks `robots.txt` and skips when access is not clearly allowed. It does not bypass anti-bot controls. It waits at least 20 seconds between downloads and can take 9+ minutes for 26 links. Check Lex.uz terms and seek permission for commercial reuse. If automated access is disallowed, request an official API/export from Adliya.

**Quality warning:** HTML extraction is heuristic. Manually inspect every imported text, remove navigation text, verify titles, legal status, article boundaries, and applicable dates. `verified` remains `false`. Never use unreviewed output to issue definitive compliance instructions.

The supplied URL language is preserved. Some links are `/ru/`, others `/uz/`, `/en/`, and others unspecified. Language is not inferred from the document body.
