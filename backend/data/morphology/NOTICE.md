# Quranic Arabic Corpus morphology data

`quran-morphology.txt` is the morphological annotation of the Quran from the
Quranic Arabic Corpus, version 0.4, by Kais Dukes (http://corpus.quran.com),
in the Arabic-script form published at https://github.com/mustafa0x/quran-morphology,
which converts the Buckwalter transliteration to Arabic and applies a number of
root, lemma and tag corrections listed in that repository.

The Quranic Arabic Corpus is released under the GNU General Public License.
The corpus asks that any use clearly indicate it as the source and link to
http://corpus.quran.com. QuranRef does both in its footer.

Import into the graph with:

    uv run quranref-cli db import-morphology data/morphology/quran-morphology.txt
