import { mande } from "mande"
import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { useStorage } from '@vueuse/core'
import type { SurahInfo, UserInfo } from "./type_defs"


export const useStore = defineStore('quranref_store', () => {
  const surahInfo = ref<SurahInfo[]>([]);
  const arabicTextType = useStorage('quranref-arabic-text-type', 'simple');
  const availableTextTypes = ref<string[]>([]);
  const availableTranslations = ref<[string, string][]>([]);
  const selectedTranslations = useStorage('quranref-selected-translations', [] as [string, string][]);

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
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  }

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

    // Loading states
    surahInfoLoading,
    textTypesLoading,

    // Getters
    selectedTranslationsString,

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
