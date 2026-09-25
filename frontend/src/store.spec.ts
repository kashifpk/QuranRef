import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
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

describe('word by word', () => {
  it('is off by default and remembers the meaning language', async () => {
    const store = useStore()
    expect(store.wordByWord).toBe(false)
    expect(store.glossLanguage).toBe('english')
    store.wordByWord = true
    store.glossLanguage = 'urdu'
    await nextTick()
    expect(JSON.parse(localStorage.getItem('quranref-word-by-word') || 'false')).toBe(true)
    expect(localStorage.getItem('quranref-gloss-language')).toBe('urdu')
  })

  it('fetches the words of an aya once and caches them', async () => {
    const tokens = [{ position: 1, text: 'بِسْمِ', text_simple: 'بسم', tag: 'N', root: 'سمو',
      lemma: 'اسْم', features: '', segments: [], glosses: {} }]
    const fetchMock = vi.fn(async (_input: RequestInfo | URL) => jsonResponse(tokens))
    vi.stubGlobal('fetch', fetchMock)
    const store = useStore()
    expect(await store.loadAyaWords('1:1')).toEqual(tokens)
    expect(await store.loadAyaWords('1:1')).toEqual(tokens)
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(String(fetchMock.mock.calls[0][0])).toContain('/aya-words/1:1')
    vi.unstubAllGlobals()
  })
})

describe('note backlinks and collections', () => {
  const note = (id: number, aya_key: string, text: string) => ({
    id,
    bookmark_type: 'note' as const,
    aya_key,
    note: text,
    created_at: '2026-09-25T00:00:00Z',
    updated_at: '2026-09-25T00:00:00Z',
  })

  it('finds notes on other ayas that mention this aya', () => {
    const store = useStore()
    store.noteBookmarks = [
      note(1, '1:1', 'Compare with @2:255 and @1:3'),
      note(2, '2:255', 'The throne verse itself mentions @2:255'),
      note(3, '3:3', 'Nothing here'),
    ]
    expect(store.getBacklinksForAya('2:255').map((n) => n.id)).toEqual([1])
    expect(store.getBacklinksForAya('1:3').map((n) => n.id)).toEqual([1])
    expect(store.getBacklinksForAya('3:3')).toEqual([])
  })

  it('tracks collection membership after adding and removing an aya', async () => {
    const store = useStore()
    store.currentUser = { id: 1, email: 'a@b.c', name: 'A', picture_url: '' }
    const calls: string[] = []
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        calls.push(`${init?.method ?? 'GET'} ${url}`)
        if (url.endsWith('/collections') && !init?.method) {
          return jsonResponse([
            { id: 7, name: 'Mercy', description: '', item_count: 1, aya_keys: ['1:1'], created_at: '', updated_at: '' },
          ])
        }
        if (url.endsWith('/collections/7/items')) {
          return jsonResponse({ id: 99, aya_key: '1:3', note: '', position: 1, created_at: '' }, 201)
        }
        return new Response(null, { status: 204 })
      })
    )
    await store.loadCollections()
    expect(store.collectionsForAya('1:1').map((c) => c.name)).toEqual(['Mercy'])
    expect(store.collectionsForAya('1:3')).toEqual([])

    await store.addToCollection(7, '1:3')
    expect(store.collectionsForAya('1:3').map((c) => c.id)).toEqual([7])
    expect(store.collections[0]!.item_count).toBe(2)

    await store.removeAyaFromCollection(7, '1:1')
    expect(store.collectionsForAya('1:1')).toEqual([])
    expect(store.collections[0]!.aya_keys).toEqual(['1:3'])
    expect(calls).toContain('DELETE /api/v1/collections/7/items/by-aya/1:1')
    vi.unstubAllGlobals()
  })
})
