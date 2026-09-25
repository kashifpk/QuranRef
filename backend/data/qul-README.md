# QUL data files

Files downloaded from the Quranic Universal Library (https://qul.tarteel.ai/resources)
go in `backend/data/qul/`, which is gitignored because QUL states no license for them.

Word-by-word meanings (JSON), imported with `quranref-cli db import-word-glosses`:

- English: resource 92, `db import-word-glosses english data/qul/<file>.json`
- Urdu: resource 93, `db import-word-glosses urdu data/qul/<file>.json`
- Transliteration: transliteration resource 71, `db import-word-glosses transliteration data/qul/<file>.json`

Also downloaded for the topic and related-verse features: ayah topics (topics.db), ayah themes (ayah-themes.db), similar ayahs (matching-ayah.json), Mutashabihat (a zip despite its .bz2 name), Quran metadata (juz, hizb, rub, manzil, ruku, sajda, ayah, surah names) and surah information in English and Urdu.

Tafsirs: pick any tafsir at https://qul.tarteel.ai/resources/tafsir, download the JSON export into `backend/data/qul/tafsir/`, and import it with

```bash
uv run quranref-cli qul import-tafsir data/qul/tafsir/<file>.json --slug <short-id> --name "<display name>" --language <language> --author "<author>" --license "<terms noted on the resource page>"
```

The JSON maps `surah:aya` keys to either `{"text": ..., "ayah_keys": [...]}` (a passage, possibly covering several ayas) or a string naming the aya whose passage covers it. Check the terms on each resource page before using a tafsir in production.

Other resources used by later features are listed in the project README.
