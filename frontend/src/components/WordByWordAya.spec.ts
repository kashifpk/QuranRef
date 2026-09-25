import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import WordByWordAya from './WordByWordAya.vue'
import type { TokenInfo } from '../type_defs'

const tokens: TokenInfo[] = [
  {
    position: 1, text: 'بِسْمِ', text_simple: 'بسم', tag: 'N', root: 'سمو', lemma: 'اسْم',
    features: 'ROOT:سمو|LEM:اسْم', segments: [], glosses: { english: 'In (the) name', urdu: 'نام سے', transliteration: "bis'mi" },
  },
  {
    position: 2, text: 'ٱللَّهِ', text_simple: 'الله', tag: 'N', root: 'أله', lemma: 'اللَّه',
    features: 'PN', segments: [], glosses: { english: '(of) Allah' },
  },
]

describe('WordByWordAya', () => {
  it('renders the words in order with the meaning in the chosen language', () => {
    const wrapper = mount(WordByWordAya, { props: { tokens, glossLanguage: 'english' } })
    const words = wrapper.findAll('.wbw-word')
    expect(words.map((w) => w.find('.wbw-arabic').text())).toEqual(['بِسْمِ', 'ٱللَّهِ'])
    expect(words.map((w) => w.find('.wbw-gloss').text())).toEqual(['In (the) name', '(of) Allah'])
  })

  it('omits the meaning when the language has none', () => {
    const wrapper = mount(WordByWordAya, { props: { tokens, glossLanguage: 'urdu' } })
    const words = wrapper.findAll('.wbw-word')
    expect(words[0].find('.wbw-gloss').text()).toBe('نام سے')
    expect(words[1].find('.wbw-gloss').exists()).toBe(false)
  })

  it('shows the transliteration only when asked', () => {
    const off = mount(WordByWordAya, { props: { tokens, glossLanguage: 'english' } })
    expect(off.find('.wbw-translit').exists()).toBe(false)
    const on = mount(WordByWordAya, {
      props: { tokens, glossLanguage: 'english', showTransliteration: true },
    })
    const lines = on.findAll('.wbw-word').map((w) => w.find('.wbw-translit'))
    expect(lines[0].text()).toBe("bis'mi")
    expect(lines[1].exists()).toBe(false)
  })

  it('emits the clicked token and marks the selected one', async () => {
    const wrapper = mount(WordByWordAya, {
      props: { tokens, glossLanguage: 'english', selectedPosition: 2 },
    })
    await wrapper.findAll('.wbw-word')[0].trigger('click')
    const emitted = wrapper.emitted('select')
    expect(emitted).toHaveLength(1)
    expect(emitted![0][0]).toEqual(tokens[0])
    expect(wrapper.findAll('.wbw-word')[1].classes()).toContain('selected')
  })
})
