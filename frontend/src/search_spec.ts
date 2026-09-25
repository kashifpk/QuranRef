export type Translation = [string, string]

const ARABIC_SCRIPT = /[؀-ۿ]/

/**
 * Decide which text a search term should be matched against.
 *
 * Terms in Arabic script search the diacritic-free Arabic text. Anything else
 * searches a translation: an English one the reader has selected, else the
 * first selected translation, else the first English translation available.
 */
export function pickSearchSpec(
  term: string,
  selected: Translation[],
  available: Translation[],
): string {
  if (ARABIC_SCRIPT.test(term)) return 'arabic:simple-clean'
  const preferred =
    selected.find((t) => t[0] === 'english') ||
    selected[0] ||
    available.find((t) => t[0] === 'english') ||
    available[0]
  return preferred ? `${preferred[0]}:${preferred[1]}` : 'english:maududi'
}

export function describeSearchSpec(spec: string): string {
  const [language, textType] = spec.split(':', 2)
  const pretty = (s: string) =>
    s.split('-').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
  return `${pretty(language)} (${pretty(textType || '')})`
}
