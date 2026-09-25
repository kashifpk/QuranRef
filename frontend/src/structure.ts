import type { StructureUnit, SurahMarker, UnitKind } from './type_defs'

export interface Segment {
  surah: number
  from: number
  to: number
}

export const UNIT_LABELS: Record<UnitKind, string> = {
  juz: 'Juz',
  hizb: 'Hizb',
  rub: 'Rub',
  manzil: 'Manzil',
  ruku: 'Ruku',
}

/** The surah ranges a unit covers, in reading order. */
export function segmentsOf(unit: StructureUnit): Segment[] {
  return Object.entries(unit.verse_mapping)
    .map(([surah, span]) => {
      const [from, to] = span.split('-').map(Number)
      return { surah: Number(surah), from, to: to ?? from }
    })
    .sort((a, b) => a.surah - b.surah)
}

/** Short text for a marker shown before an aya, for example "Juz 2 · Ruku 3". */
export function markerLabel(marker: SurahMarker): string {
  const parts: string[] = []
  if (marker.juz_start) parts.push(`Juz ${marker.juz_start}`)
  if (marker.manzil_start) parts.push(`Manzil ${marker.manzil_start}`)
  if (marker.hizb_start) parts.push(`Hizb ${marker.hizb_start}`)
  if (marker.rub_start) parts.push(`Rub ${marker.rub_start}`)
  if (marker.ruku_start) parts.push(`Ruku ${marker.ruku_start}`)
  return parts.join(' · ')
}
