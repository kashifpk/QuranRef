import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import WordDetails from './WordDetails.vue'
import type { TokenInfo } from '../type_defs'

const token: TokenInfo = {
  position: 4, text: 'ٱلرَّحِيمِ', text_simple: 'الرحيم', tag: 'N', root: 'رحم', lemma: 'رَحِيم',
  features: 'ROOT:رحم|LEM:رَحِيم|MS|GEN|ADJ',
  segments: [
    { form: 'ٱل', tag: 'P', features: 'DET|PREF|LEM:ال' },
    { form: 'رَّحِيمِ', tag: 'N', features: 'ROOT:رحم|LEM:رَحِيم|MS|GEN|ADJ' },
  ],
  glosses: { english: 'the Most Merciful' },
}

function mountDetails(t: TokenInfo | null) {
  const Stub = { template: '<div />' }
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: Stub },
      { name: 'lemma_view', path: '/lemma/:lemma', component: Stub },
      { name: 'root_view', path: '/root/:root', component: Stub },
    ],
  })
  return mount(WordDetails, { props: { token: t }, global: { plugins: [router] } })
}

describe('WordDetails', () => {
  it('shows the word, its part of speech, meaning, lemma and root links, and segments', () => {
    const wrapper = mountDetails(token)
    expect(wrapper.find('.word-details-arabic').text()).toBe('ٱلرَّحِيمِ')
    expect(wrapper.find('.word-details-pos').text()).toBe('Noun')
    expect(wrapper.text()).toContain('the Most Merciful')
    const links = wrapper.findAll('a.word-details-link')
    expect(links.map((l) => l.attributes('href'))).toEqual([
      `/lemma/${encodeURIComponent('رَحِيم')}`,
      `/root/${encodeURIComponent('رحم')}`,
    ])
    expect(wrapper.findAll('.word-details-segment')).toHaveLength(2)
  })

  it('renders nothing without a token', () => {
    expect(mountDetails(null).find('.word-details').exists()).toBe(false)
  })
})
