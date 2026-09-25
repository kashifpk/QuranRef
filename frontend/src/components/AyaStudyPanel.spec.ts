import { afterEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import AyaStudyPanel from './AyaStudyPanel.vue'

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } })
}

function mountPanel(ayaKey: string) {
  const Stub = { template: '<div />' }
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: Stub },
      { name: 'surah_view', path: '/surah/:surah_number', component: Stub },
      { name: 'topic_view', path: '/topic/:id', component: Stub },
      { name: 'phrase_view', path: '/phrase/:id', component: Stub },
    ],
  })
  setActivePinia(createPinia())
  return mount(AyaStudyPanel, { props: { ayaKey }, global: { plugins: [router] } })
}

afterEach(() => vi.unstubAllGlobals())

describe('AyaStudyPanel', () => {
  it('renders topics, theme, phrases and similar ayas from the two endpoints', async () => {
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/aya-topics/')) {
        return jsonResponse({
          topics: [{ id: '1', name: 'Allah', arabic_name: 'الله', aya_count: 2, thematic: false, ontology: true, parent_id: null, thematic_parent_id: null, ontology_parent_id: null }],
          themes: [{ id: 'theme:1', theme: 'Opening praise', surah_number: 1, aya_from: 1, aya_to: 3, keywords: '' }],
        })
      }
      return jsonResponse({
        similar: [{ aya_key: '1:3', score: 80, coverage: 50, matched_words: 2, match_words: [[3, 4]], texts: { arabic: { simple: 'الرحمن الرحيم' }, english: { maududi: 'The Merciful' } } }],
        phrases: [{ id: 'phrase:1', text: 'ٱلرَّحْمَٰنِ ٱلرَّحِيمِ', source_aya: '1:1', aya_count: 2, ranges: [[3, 4]], aya_keys: [] }],
      })
    }))
    const wrapper = mountPanel('1:1')
    await flushPromises()
    expect(wrapper.find('.study-chip').text()).toBe('Allah')
    expect(wrapper.text()).toContain('Opening praise')
    expect(wrapper.text()).toContain('(1:1-3)')
    expect(wrapper.find('.similar-key').text()).toBe('1:3')
    expect(wrapper.find('.similar-score').text()).toBe('80%')
    expect(wrapper.find('.similar-text').text()).toBe('الرحمن الرحيم')
    expect(wrapper.find('.similar-translation').text()).toBe('The Merciful')
    expect(wrapper.find('a[href="/phrase/phrase%3A1"], a[href="/phrase/phrase:1"]').exists()).toBe(true)
  })

  it('says so when nothing is recorded', async () => {
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) =>
      String(input).includes('/aya-topics/') ? jsonResponse({ topics: [], themes: [] }) : jsonResponse({ similar: [], phrases: [] })))
    const wrapper = mountPanel('2:2')
    await flushPromises()
    expect(wrapper.find('.study-empty').exists()).toBe(true)
  })
})
