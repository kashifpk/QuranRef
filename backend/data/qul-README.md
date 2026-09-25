# QUL data files

Files downloaded from the Quranic Universal Library (https://qul.tarteel.ai/resources)
go in `backend/data/qul/`, which is gitignored because QUL states no license for them.

Word-by-word meanings (JSON), imported with `quranref-cli db import-word-glosses`:

- English: resource 92, `db import-word-glosses english data/qul/<file>.json`
- Urdu: resource 93, `db import-word-glosses urdu data/qul/<file>.json`

Other resources used by later features are listed in the project README.
