import { mande } from "mande"
import { defineStore } from "pinia"
import { ref, computed, watch } from "vue"
import { useStorage } from '@vueuse/core'
import type { SurahInfo, UserInfo, Bookmark, BookmarksData, TokenInfo, TopicSummary, Structure, CollectionSummary, TafsirResource } from "./type_defs"
import { extractAyaRefs } from "./note_refs"
import { ayaAudioUrl, DEFAULT_RECITER } from "./audio"


export const useStore = defineStore('quranref_store', () => {
  const surahInfo = ref<SurahInfo[]>([]);
  const arabicTextType = useStorage('quranref-arabic-text-type', 'simple');
  const availableTextTypes = ref<string[]>([]);
  const availableTranslations = ref<[string, string][]>([]);
  const selectedTranslations = useStorage('quranref-selected-translations', [] as [string, string][]);

  // Word-by-word reading mode and the language of the per-word meanings shown under each word
  const wordByWord = useStorage('quranref-word-by-word', false);
  const glossLanguage = useStorage('quranref-gloss-language', 'english');
  const showTransliteration = useStorage('quranref-show-transliteration', false);

  // Per-aya word morphology, fetched on demand and kept for the session
  const ayaWordsCache = new Map<string, TokenInfo[]>();

  async function loadAyaWords(ayaKey: string): Promise<TokenInfo[]> {
    const cached = ayaWordsCache.get(ayaKey);
    if (cached) return cached;
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    try {
      const resp = await fetch(baseUrl + '/aya-words/' + ayaKey);
      if (!resp.ok) return [];
      const tokens: TokenInfo[] = await resp.json();
      ayaWordsCache.set(ayaKey, tokens);
      return tokens;
    } catch (error) {
      console.error('Failed to load aya words:', error);
      return [];
    }
  }

  // The full topic list, fetched once per session
  const topics = ref<TopicSummary[]>([]);
  const topicsLoading = ref(false);

  async function loadTopics(): Promise<TopicSummary[]> {
    if (topics.value.length > 0) return topics.value;
    topicsLoading.value = true;
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      const resp = await fetch(baseUrl + '/topics');
      if (resp.ok) topics.value = await resp.json();
    } catch (error) {
      console.error('Failed to load topics:', error);
    } finally {
      topicsLoading.value = false;
    }
    return topics.value;
  }

  // Mushaf structure tables (juz, hizb, rub, manzil, ruku), fetched once
  const structure = ref<Structure | null>(null);

  async function loadStructure(): Promise<Structure | null> {
    if (structure.value) return structure.value;
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      const resp = await fetch(baseUrl + '/structure');
      if (resp.ok) structure.value = await resp.json();
    } catch (error) {
      console.error('Failed to load structure:', error);
    }
    return structure.value;
  }

  // Language spec for aya texts: the Arabic style plus the selected translations
  const textLanguagesSpec = computed(() => {
    const spec = 'arabic:' + arabicTextType.value;
    return selectedTranslationsString.value ? spec + '_' + selectedTranslationsString.value : spec;
  });

  // Dark mode state (persisted to localStorage)
  // On first visit, follow system preference; thereafter use the stored value
  const hasStoredPreference = localStorage.getItem('quranref-dark-mode') !== null;
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const darkMode = useStorage('quranref-dark-mode', hasStoredPreference ? false : systemPrefersDark);

  // Initialize theme on app load
  function initializeTheme() {
    if (darkMode.value) {
      document.documentElement.classList.add('dark-mode');
    } else {
      document.documentElement.classList.remove('dark-mode');
    }
  }

  // Toggle dark/light mode
  function toggleDarkMode() {
    darkMode.value = !darkMode.value;
    initializeTheme();
  }

  // Computed properties (getters)
  const selectedTranslationsString = computed(() => {
    let s = '';
    for (const tr of selectedTranslations.value) {
      s += tr[0] + ':' + tr[1] + '_';
    }

    if (s.length > 0) {
      s = s.slice(0, -1);
    }

    return s;
  });

  // Auth state
  const currentUser = ref<UserInfo | null>(null);
  const authLoading = ref(false);

  async function checkAuth() {
    authLoading.value = true;
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      const response = await fetch(baseUrl + '/auth/me', { credentials: 'include' });
      const data = await response.json();
      currentUser.value = data.user;
    } catch (error) {
      console.error('Failed to check auth:', error);
      currentUser.value = null;
    } finally {
      authLoading.value = false;
    }
  }

  function login() {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    window.location.href = baseUrl + '/auth/login';
  }

  async function logout() {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      await fetch(baseUrl + '/auth/logout', { method: 'POST', credentials: 'include' });
      currentUser.value = null;
      readingBookmark.value = null;
      noteBookmarks.value = [];
      collections.value = [];
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  }

  // --- Bookmarks ---
  const readingBookmark = ref<Bookmark | null>(null);
  const noteBookmarks = ref<Bookmark[]>([]);
  const bookmarksLoading = ref(false);

  async function loadBookmarks() {
    if (!currentUser.value) return;
    bookmarksLoading.value = true;
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      const resp = await fetch(baseUrl + '/bookmarks', { credentials: 'include' });
      if (resp.ok) {
        const data: BookmarksData = await resp.json();
        readingBookmark.value = data.reading;
        noteBookmarks.value = data.notes;
      }
    } catch (error) {
      console.error('Failed to load bookmarks:', error);
    } finally {
      bookmarksLoading.value = false;
    }
  }

  async function setReadingBookmark(ayaKey: string) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(baseUrl + '/bookmarks/reading', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ aya_key: ayaKey }),
    });
    if (resp.ok) {
      readingBookmark.value = await resp.json();
    }
  }

  async function deleteReadingBookmark() {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(baseUrl + '/bookmarks/reading', {
      method: 'DELETE',
      credentials: 'include',
    });
    if (resp.ok) {
      readingBookmark.value = null;
    }
  }

  async function addNoteBookmark(ayaKey: string, note: string) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(baseUrl + '/bookmarks/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ aya_key: ayaKey, note }),
    });
    if (resp.ok) {
      const bookmark: Bookmark = await resp.json();
      noteBookmarks.value.unshift(bookmark);
    }
  }

  async function updateNoteBookmark(id: number, note: string) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(baseUrl + `/bookmarks/notes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ note }),
    });
    if (resp.ok) {
      const updated: Bookmark = await resp.json();
      const idx = noteBookmarks.value.findIndex(b => b.id === id);
      if (idx !== -1) noteBookmarks.value[idx] = updated;
    }
  }

  async function deleteNoteBookmark(id: number) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(baseUrl + `/bookmarks/notes/${id}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    if (resp.ok) {
      noteBookmarks.value = noteBookmarks.value.filter(b => b.id !== id);
    }
  }

  function isReadingBookmark(ayaKey: string): boolean {
    return readingBookmark.value?.aya_key === ayaKey;
  }

  function getNotesForAya(ayaKey: string): Bookmark[] {
    return noteBookmarks.value.filter(b => b.aya_key === ayaKey);
  }

  // Notes on other ayas whose text mentions this aya as @surah:aya
  function getBacklinksForAya(ayaKey: string): Bookmark[] {
    return noteBookmarks.value.filter(
      b => b.aya_key !== ayaKey && extractAyaRefs(b.note).includes(ayaKey)
    );
  }

  // --- Collections (curated lists of ayas) ---
  const collections = ref<CollectionSummary[]>([]);
  const collectionsLoading = ref(false);
  const apiBase = () => import.meta.env.VITE_API_BASE_URL || '/api/v1';
  const jsonHeaders = { 'Content-Type': 'application/json' };

  async function loadCollections() {
    if (!currentUser.value) return;
    collectionsLoading.value = true;
    try {
      const resp = await fetch(apiBase() + '/collections', { credentials: 'include' });
      if (resp.ok) collections.value = await resp.json();
    } catch (error) {
      console.error('Failed to load collections:', error);
    } finally {
      collectionsLoading.value = false;
    }
  }

  async function createCollection(name: string, description = ''): Promise<CollectionSummary | null> {
    const resp = await fetch(apiBase() + '/collections', {
      method: 'POST',
      headers: jsonHeaders,
      credentials: 'include',
      body: JSON.stringify({ name, description }),
    });
    if (!resp.ok) return null;
    const created: CollectionSummary = await resp.json();
    collections.value.unshift(created);
    return created;
  }

  async function updateCollection(
    id: number,
    patch: { name?: string; description?: string }
  ): Promise<CollectionSummary | null> {
    const resp = await fetch(apiBase() + `/collections/${id}`, {
      method: 'PUT',
      headers: jsonHeaders,
      credentials: 'include',
      body: JSON.stringify(patch),
    });
    if (!resp.ok) return null;
    const updated: CollectionSummary = await resp.json();
    const idx = collections.value.findIndex(c => c.id === id);
    if (idx !== -1) collections.value[idx] = updated;
    return updated;
  }

  async function deleteCollection(id: number): Promise<boolean> {
    const resp = await fetch(apiBase() + `/collections/${id}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    if (resp.ok) collections.value = collections.value.filter(c => c.id !== id);
    return resp.ok;
  }

  async function addToCollection(id: number, ayaKey: string, note = ''): Promise<boolean> {
    const resp = await fetch(apiBase() + `/collections/${id}/items`, {
      method: 'POST',
      headers: jsonHeaders,
      credentials: 'include',
      body: JSON.stringify({ aya_key: ayaKey, note }),
    });
    const summary = collections.value.find(c => c.id === id);
    if (resp.ok && summary && !summary.aya_keys.includes(ayaKey)) {
      summary.aya_keys.push(ayaKey);
      summary.item_count += 1;
    }
    return resp.ok;
  }

  async function removeAyaFromCollection(id: number, ayaKey: string): Promise<boolean> {
    const resp = await fetch(apiBase() + `/collections/${id}/items/by-aya/${ayaKey}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    const summary = collections.value.find(c => c.id === id);
    if (resp.ok && summary) {
      summary.aya_keys = summary.aya_keys.filter(k => k !== ayaKey);
      summary.item_count = summary.aya_keys.length;
    }
    return resp.ok;
  }

  function collectionsForAya(ayaKey: string): CollectionSummary[] {
    return collections.value.filter(c => c.aya_keys.includes(ayaKey));
  }

  // --- Tafsir selection (passages shown under an aya on request) ---
  const tafsirs = ref<TafsirResource[]>([]);
  const tafsirsLoading = ref(false);
  const selectedTafsirs = useStorage<string[]>('quranref-tafsirs', []);

  async function loadTafsirs(): Promise<TafsirResource[]> {
    if (tafsirs.value.length > 0) return tafsirs.value;
    tafsirsLoading.value = true;
    try {
      const resp = await fetch(apiBase() + '/tafsirs');
      if (resp.ok) tafsirs.value = await resp.json();
    } catch (error) {
      console.error('Failed to load tafsirs:', error);
    } finally {
      tafsirsLoading.value = false;
    }
    return tafsirs.value;
  }

  function toggleTafsir(slug: string, selected: boolean) {
    const others = selectedTafsirs.value.filter(s => s !== slug);
    selectedTafsirs.value = selected ? [...others, slug] : others;
  }

  // --- Recitation audio (one file per aya from everyayah.com) ---
  const reciter = useStorage('quranref-reciter', DEFAULT_RECITER);
  const audioContinuous = useStorage('quranref-audio-continuous', true);
  const audioCurrent = ref<string | null>(null);
  const audioPlaying = ref(false);
  const audioPlaylist = ref<string[]>([]);
  let audioEl: HTMLAudioElement | null = null;

  function audioElement(): HTMLAudioElement | null {
    if (audioEl) return audioEl;
    if (typeof Audio === 'undefined') return null;
    audioEl = new Audio();
    audioEl.preload = 'auto';
    audioEl.addEventListener('play', () => { audioPlaying.value = true; });
    audioEl.addEventListener('pause', () => { audioPlaying.value = false; });
    audioEl.addEventListener('error', () => { audioPlaying.value = false; });
    audioEl.addEventListener('ended', () => {
      if (audioContinuous.value && !nextAya()) stopAudio();
    });
    return audioEl;
  }

  function startPlayback(el: HTMLAudioElement) {
    const started = el.play();
    if (started && typeof started.catch === 'function') {
      started.catch((error: unknown) => {
        console.error('Playback failed:', error);
        audioPlaying.value = false;
      });
    }
  }

  // Play one aya. A playlist (the surah, a collection...) enables continuous play.
  function playAya(ayaKey: string, playlist?: string[]): boolean {
    const url = ayaAudioUrl(reciter.value, ayaKey);
    const el = audioElement();
    if (!url || !el) return false;
    if (playlist) audioPlaylist.value = playlist;
    else if (!audioPlaylist.value.includes(ayaKey)) audioPlaylist.value = [ayaKey];
    audioCurrent.value = ayaKey;
    el.src = url;
    startPlayback(el);
    return true;
  }

  function pauseAudio() {
    audioEl?.pause();
  }

  function resumeAudio() {
    if (!audioEl || !audioCurrent.value) return;
    if (audioEl.ended) audioEl.currentTime = 0;
    startPlayback(audioEl);
  }

  function stopAudio() {
    if (audioEl) {
      audioEl.pause();
      audioEl.removeAttribute('src');
      audioEl.load();
    }
    audioCurrent.value = null;
    audioPlaying.value = false;
  }

  function toggleAya(ayaKey: string, playlist?: string[]) {
    if (audioCurrent.value === ayaKey) {
      if (audioPlaying.value) pauseAudio();
      else resumeAudio();
    } else {
      playAya(ayaKey, playlist);
    }
  }

  function nextAya(): boolean {
    const index = audioPlaylist.value.indexOf(audioCurrent.value ?? '');
    const next = index === -1 ? undefined : audioPlaylist.value[index + 1];
    return next ? playAya(next) : false;
  }

  function prevAya(): boolean {
    const index = audioPlaylist.value.indexOf(audioCurrent.value ?? '');
    const prev = index > 0 ? audioPlaylist.value[index - 1] : undefined;
    return prev ? playAya(prev) : false;
  }

  // Switching reciter mid-aya restarts the aya with the new voice
  watch(reciter, () => {
    if (audioCurrent.value && audioPlaying.value) playAya(audioCurrent.value);
  });

  // Loading state for surah info
  const surahInfoLoading = ref(false);

  // Action to load surah info
  async function loadSurahInfo() {
    surahInfoLoading.value = true;
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      const url = baseUrl + "/surahs"
      const surahsApi = mande(url)
      const response = await surahsApi.get()
      surahInfo.value = response as SurahInfo[];
    } catch (error) {
      console.error('Failed to load surah info:', error);
    } finally {
      surahInfoLoading.value = false;
    }
  }

  // Loading state for text types
  const textTypesLoading = ref(false);

  // Action to load text types
  async function loadTextTypes() {
    textTypesLoading.value = true;
    try {
      const url = import.meta.env.VITE_API_BASE_URL + "/text-types"
      const api = mande(url)
      const response = await api.get() as any;

      // Set available text types for Arabic
      if (response && response.arabic) {
        availableTextTypes.value = response.arabic;
      }

      // Set available translations
      const translations: [string, string][] = [];
      for (const lang in response) {
        if (lang !== 'arabic') {
          for (const translator of response[lang]) {
            translations.push([lang, translator]);
          }
        }
      }
      availableTranslations.value = translations;
    } catch (error) {
      console.error('Failed to load text types:', error);
    } finally {
      textTypesLoading.value = false;
    }
  }

  // Methods to update state
  function setArabicTextType(textType: string) {
    arabicTextType.value = textType;
  }

  function addTranslation(translation: [string, string]) {
    // Check if translation already exists
    const exists = selectedTranslations.value.some(
      tr => tr[0] === translation[0] && tr[1] === translation[1]
    );

    if (!exists) {
      selectedTranslations.value.push(translation);
    }
  }

  function removeTranslation(index: number) {
    selectedTranslations.value.splice(index, 1);
  }

  return {
    // Auth
    currentUser,
    authLoading,
    checkAuth,
    login,
    logout,

    // State
    surahInfo,
    arabicTextType,
    availableTextTypes,
    availableTranslations,
    selectedTranslations,
    darkMode,
    wordByWord,
    glossLanguage,
    showTransliteration,
    loadAyaWords,
    topics,
    topicsLoading,
    loadTopics,
    structure,
    loadStructure,
    textLanguagesSpec,

    // Loading states
    surahInfoLoading,
    textTypesLoading,

    // Getters
    selectedTranslationsString,

    // Bookmarks
    readingBookmark,
    noteBookmarks,
    bookmarksLoading,
    loadBookmarks,
    setReadingBookmark,
    deleteReadingBookmark,
    addNoteBookmark,
    updateNoteBookmark,
    deleteNoteBookmark,
    isReadingBookmark,
    getNotesForAya,
    getBacklinksForAya,

    // Collections
    collections,
    collectionsLoading,
    loadCollections,
    createCollection,
    updateCollection,
    deleteCollection,
    addToCollection,
    removeAyaFromCollection,
    collectionsForAya,

    // Tafsir
    tafsirs,
    tafsirsLoading,
    selectedTafsirs,
    loadTafsirs,
    toggleTafsir,

    // Recitation audio
    reciter,
    audioContinuous,
    audioCurrent,
    audioPlaying,
    audioPlaylist,
    playAya,
    pauseAudio,
    resumeAudio,
    stopAudio,
    toggleAya,
    nextAya,
    prevAya,

    // Actions
    loadSurahInfo,
    loadTextTypes,
    setArabicTextType,
    addTranslation,
    removeTranslation,
    initializeTheme,
    toggleDarkMode
  }
})
