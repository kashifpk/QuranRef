import { describe, expect, it } from 'vitest'
import { markerLabel, segmentsOf } from './structure'

describe('segmentsOf', () => {
  it('parses the surah ranges in surah order', () => {
    expect(
      segmentsOf({
        number: 1, verses_count: 148, first_verse_key: '1:1', last_verse_key: '2:141',
        verse_mapping: { '2': '1-141', '1': '1-7' },
      }),
    ).toEqual([
      { surah: 1, from: 1, to: 7 },
      { surah: 2, from: 1, to: 141 },
    ])
  })

  it('accepts a single aya span', () => {
    expect(
      segmentsOf({ number: 1, verses_count: 1, first_verse_key: '1:1', last_verse_key: '1:1', verse_mapping: { '1': '1' } }),
    ).toEqual([{ surah: 1, from: 1, to: 1 }])
  })
})

describe('markerLabel', () => {
  it('lists the units that begin, juz first', () => {
    expect(
      markerLabel({ aya_number: 142, juz_start: 2, hizb_start: 3, rub_start: 9, manzil_start: null, ruku_start: 17, sajda: null }),
    ).toBe('Juz 2 · Hizb 3 · Rub 9 · Ruku 17')
    expect(markerLabel({ aya_number: 5, juz_start: null, hizb_start: null, rub_start: null, manzil_start: null, ruku_start: null, sajda: 'required' })).toBe('')
  })
})
