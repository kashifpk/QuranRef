import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import MarkdownNote from './MarkdownNote.vue'

function makeRouter() {
  const Stub = { template: '<div />' }
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: Stub },
      { name: 'surah_view', path: '/surah/:surah_number', component: Stub },
    ],
  })
}

function mountNote(modelValue: string, mode: 'edit' | 'display' = 'display') {
  const router = makeRouter()
  const wrapper = mount(MarkdownNote, {
    props: { modelValue, mode },
    global: { plugins: [router] },
  })
  return { wrapper, router }
}

describe('MarkdownNote display mode', () => {
  it('renders markdown with dir="auto" on paragraphs', () => {
    const { wrapper } = mountNote('Hello **world**')
    const p = wrapper.find('p')
    expect(p.exists()).toBe(true)
    expect(p.attributes('dir')).toBe('auto')
    expect(wrapper.find('strong').text()).toBe('world')
  })

  it('turns @surah:aya references into verse links', () => {
    const { wrapper } = mountNote('See @2:255 and @114:6.')
    const links = wrapper.findAll('a.aya-ref-link')
    expect(links.map((l) => l.attributes('href'))).toEqual([
      '/surah/2?aya=255',
      '/surah/114?aya=6',
    ])
    expect(links.map((l) => l.text())).toEqual(['2:255', '114:6'])
  })

  it('does not render raw HTML from the note', () => {
    const { wrapper } = mountNote('<script>alert(1)</script> plain')
    expect(wrapper.find('script').exists()).toBe(false)
    expect(wrapper.text()).toContain('plain')
  })

  it('navigates through the router when a verse link is clicked', async () => {
    const { wrapper, router } = mountNote('Go to @1:7')
    const push = vi.spyOn(router, 'push').mockResolvedValue(undefined)
    await wrapper.find('a.aya-ref-link').trigger('click')
    expect(push).toHaveBeenCalledWith('/surah/1?aya=7')
  })
})

describe('MarkdownNote edit mode', () => {
  it('emits update:modelValue as the user types', async () => {
    const { wrapper } = mountNote('', 'edit')
    const textarea = wrapper.find('textarea')
    await textarea.setValue('new text')
    expect(wrapper.emitted('update:modelValue')).toEqual([['new text']])
  })

  it('shows the preview tab content only when there is text', async () => {
    const { wrapper } = mountNote('', 'edit')
    expect(wrapper.find('.md-empty-preview').exists()).toBe(true)
    await wrapper.setProps({ modelValue: 'Some *note*' })
    expect(wrapper.find('.md-empty-preview').exists()).toBe(false)
    expect(wrapper.find('.md-preview em').text()).toBe('note')
  })
})
