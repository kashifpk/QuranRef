# QUL data files

Files downloaded from the Quranic Universal Library (https://qul.tarteel.ai/resources)
go in `backend/data/qul/`, which is gitignored because QUL states no license for them.

Word-by-word meanings (JSON), imported with `quranref-cli db import-word-glosses`:

- English: resource 92, `db import-word-glosses english data/qul/<file>.json`
- Urdu: resource 93, `db import-word-glosses urdu data/qul/<file>.json`
- Transliteration: transliteration resource 71, `db import-word-glosses transliteration data/qul/<file>.json`

Also downloaded for the topic and related-verse features: ayah topics (topics.db), ayah themes (ayah-themes.db), similar ayahs (matching-ayah.json), Mutashabihat (a zip despite its .bz2 name), Quran metadata (juz, hizb, rub, manzil, ruku, sajda, ayah, surah names) and surah information in English and Urdu.

Other resources used by later features are listed in the project README.
