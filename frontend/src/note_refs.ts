// Aya references written in notes as @surah:aya (the same form MarkdownNote turns into links).
const AYA_REF_RE = /@(\d{1,3}):(\d{1,3})/g;

// Distinct aya keys referenced in a note, in order of first appearance.
export function extractAyaRefs(text: string): string[] {
  const found: string[] = [];
  for (const match of text.matchAll(AYA_REF_RE)) {
    const key = `${Number(match[1])}:${Number(match[2])}`;
    if (!found.includes(key)) found.push(key);
  }
  return found;
}
