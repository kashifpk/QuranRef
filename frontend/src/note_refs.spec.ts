import { describe, expect, it } from 'vitest'
import { extractAyaRefs } from './note_refs'

describe('extractAyaRefs', () => {
  it('lists each referenced aya once, in order', () => {
    expect(extractAyaRefs('Compare @2:255 with @114:6, then @2:255 again')).toEqual(['2:255', '114:6'])
  })

  it('normalises leading zeros and ignores plain text', () => {
    expect(extractAyaRefs('see @002:05 and 2:6 without the at sign')).toEqual(['2:5'])
  })

  it('returns nothing for an empty note', () => {
    expect(extractAyaRefs('')).toEqual([])
  })
})
