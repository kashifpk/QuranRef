import { describe, expect, it } from 'vitest'
import { describeSearchSpec, pickSearchSpec } from './search_spec'

describe('pickSearchSpec', () => {
  it('searches the Arabic text for Arabic script', () => {
    expect(pickSearchSpec('الله', [['english', 'maududi']], [])).toBe('arabic:simple-clean')
  })

  it('prefers a selected English translation for other scripts', () => {
    expect(pickSearchSpec('merciful', [['urdu', 'maududi'], ['english', 'sahih']], [])).toBe(
      'english:sahih',
    )
  })

  it('falls back to the first selected, then the first available English, then a default', () => {
    expect(pickSearchSpec('rahmet', [['urdu', 'maududi']], [['english', 'sahih']])).toBe(
      'urdu:maududi',
    )
    expect(pickSearchSpec('merciful', [], [['urdu', 'maududi'], ['english', 'sahih']])).toBe(
      'english:sahih',
    )
    expect(pickSearchSpec('merciful', [], [])).toBe('english:maududi')
  })
})

describe('describeSearchSpec', () => {
  it('renders a readable label', () => {
    expect(describeSearchSpec('arabic:simple-clean')).toBe('Arabic (Simple Clean)')
    expect(describeSearchSpec('english:maududi')).toBe('English (Maududi)')
  })
})
