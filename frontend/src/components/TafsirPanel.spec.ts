import { afterEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import TafsirPanel from './TafsirPanel.vue'

afterEach(() => vi.unstubAllGlobals())

describe('TafsirPanel', () => {
  it('renders a passage per selected tafsir and shows the range it covers', async () => {
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/tafsir/ibn-kathir/')) {
        return new Response(JSON.stringify({
          slug: 'ibn-kathir', name: 'Ibn Kathir', language: 'english', aya_key: '1:3',
          from_key: '1:2', to_key: '1:3', aya_keys: ['1:2', '1:3'], text: '<p>Praise <b>belongs</b> to Allah.</p>',
        }), { status: 200, headers: { 'Content-Type': 'application/json' } })
      }
      return new Response('', { status: 404 })
    }))
    const wrapper = mount(TafsirPanel, { props: { ayaKey: '1:3', slugs: ['ibn-kathir', 'missing'] } })
    await flushPromises()
    const entries = wrapper.findAll('.tafsir-entry')
    expect(entries).toHaveLength(2)
    expect(entries[0]!.find('.tafsir-name').text()).toBe('Ibn Kathir')
    expect(entries[0]!.find('.tafsir-range').text()).toBe('covers 1:2 to 1:3')
    expect(entries[0]!.find('.tafsir-text b').text()).toBe('belongs')
    expect(entries[1]!.find('.tafsir-missing').exists()).toBe(true)
  })
})
