// Per-aya recitation files streamed from everyayah.com (non-commercial use with credit).
// Files are named SSSAAA.mp3 under a reciter folder, for example Alafasy_128kbps/002255.mp3.

export interface Reciter {
  id: string;
  name: string;
}

export const AUDIO_BASE = 'https://everyayah.com/data';
export const DEFAULT_RECITER = 'Alafasy_128kbps';

export const RECITERS: Reciter[] = [
  { id: 'Alafasy_128kbps', name: 'Mishary Rashid Alafasy' },
  { id: 'Abdul_Basit_Murattal_192kbps', name: 'Abdul Basit Abdul Samad (murattal)' },
  { id: 'Husary_128kbps', name: 'Mahmoud Khalil Al-Husary' },
  { id: 'Minshawy_Murattal_128kbps', name: 'Mohamed Siddiq El-Minshawi (murattal)' },
  { id: 'Abdurrahmaan_As-Sudais_192kbps', name: 'Abdurrahman As-Sudais' },
  { id: 'Saood_ash-Shuraym_128kbps', name: 'Saud Al-Shuraim' },
  { id: 'Hudhaify_128kbps', name: 'Ali Al-Hudhaify' },
  { id: 'MaherAlMuaiqly128kbps', name: 'Maher Al-Muaiqly' },
  { id: 'Abu_Bakr_Ash-Shaatree_128kbps', name: 'Abu Bakr Al-Shatri' },
  { id: 'Muhammad_Ayyoub_128kbps', name: 'Muhammad Ayyub' },
  { id: 'Yasser_Ad-Dussary_128kbps', name: 'Yasser Al-Dosari' },
  { id: 'Ghamadi_40kbps', name: 'Saad Al-Ghamdi' },
];

function pad3(n: number): string {
  return String(n).padStart(3, '0');
}

// URL of the recitation of one aya, or null for keys without a file of their own
// (the bismillah line stored as aya 0 is recited as part of the first aya).
export function ayaAudioUrl(reciter: string, ayaKey: string): string | null {
  const [surah, aya] = ayaKey.split(':').map(Number);
  if (!surah || !aya || surah > 114) return null;
  return `${AUDIO_BASE}/${reciter}/${pad3(surah)}${pad3(aya)}.mp3`;
}
