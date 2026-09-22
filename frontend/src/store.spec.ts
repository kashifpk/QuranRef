import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from './store'

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

beforeEach(() => {
  localStorage.clear()
  document.documentElement.classList.remove('dark-mode')
  setActivePinia(createPinia())
})

describe('selected translations', () => {
  it('builds the language spec string the API expects', () => {
    const store = useStore()
    store.addTranslation(['english', 'maududi'])
    store.addTranslation(['urdu', 'maududi'])
    expect(store.selectedTranslationsString).toBe('english:maududi_urdu:maududi')
  })

  it('is empty when nothing is selected', () => {
    expect(useStore().selectedTranslationsString).toBe('')
  })

  it('ignores duplicates and removes by index', () => {
    const store = useStore()
    store.addTranslation(['english', 'maududi'])
    store.addTranslation(['english', 'maududi'])
    store.addTranslation(['urdu', 'jalandhry'])
    expect(store.selectedTranslations).toHaveLength(2)
    store.removeTranslation(0)
    expect(store.selectedTranslations).toEqual([['urdu', 'jalandhry']])
  })
})

describe('dark mode', () => {
  it('toggles the dark-mode class on the root element', () => {
    const store = useStore()
    const before = document.documentElement.classList.contains('dark-mode')
    store.toggleDarkMode()
    expect(document.documentElement.classList.contains('dark-mode')).toBe(!before)
    store.toggleDarkMode()
    expect(document.documentElement.classList.contains('dark-mode')).toBe(before)
  })
})

describe('text types', () => {
  it('splits Arabic text types from translations', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        jsonResponse({
          arabic: ['simple', 'uthmani'],
          english: ['maududi'],
          urdu: ['maududi', 'jalandhry'],
        }),
      ),
    )
    const store = useStore()
    await store.loadTextTypes()
    expect(store.availableTextTypes).toEqual(['simple', 'uthmani'])
    expect(store.availableTranslations).toEqual([
      ['english', 'maududi'],
      ['urdu', 'maududi'],
      ['urdu', 'jalandhry'],
    ])
    vi.unstubAllGlobals()
  })
})

describe('bookmarks', () => {
  it('answers lookups from the loaded bookmark state', () => {
    const store = useStore()
    store.readingBookmark = {
      id: 1, bookmark_type: 'reading', aya_key: '2:255', note: '',
      created_at: '', updated_at: '',
    }
    store.noteBookmarks = [
      { id: 2, bookmark_type: 'note', aya_key: '1:1', note: 'a', created_at: '', updated_at: '' },
      { id: 3, bookmark_type: 'note', aya_key: '1:1', note: 'b', created_at: '', updated_at: '' },
      { id: 4, bookmark_type: 'note', aya_key: '3:1', note: 'c', created_at: '', updated_at: '' },
    ]
    expect(store.isReadingBookmark('2:255')).toBe(true)
    expect(store.isReadingBookmark('1:1')).toBe(false)
    expect(store.getNotesForAya('1:1').map((b) => b.id)).toEqual([2, 3])
    expect(store.getNotesForAya('9:9')).toEqual([])
  })

  it('clears user state on logout', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse({ ok: true })))
    const store = useStore()
    store.currentUser = { id: 1, email: 'a@b.c', name: 'A', picture_url: '' }
    store.noteBookmarks = [
      { id: 2, bookmark_type: 'note', aya_key: '1:1', note: 'a', created_at: '', updated_at: '' },
    ]
    await store.logout()
    expect(store.currentUser).toBeNull()
    expect(store.noteBookmarks).toEqual([])
    vi.unstubAllGlobals()
  })
})
