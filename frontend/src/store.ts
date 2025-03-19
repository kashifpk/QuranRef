import { mande } from "mande"
import { defineStore } from "pinia"
import { ref, computed } from "vue"
// import { ImportMeta } from "vite"
import type { SurahInfo } from "./type_defs"


export const useStore = defineStore('quranref_store', () => {
  const surahInfo = ref<SurahInfo[]>([]);
  const arabicTextType = ref<string>('simple');
  const availableTextTypes = ref<string[]>([]);
  const availableTranslations = ref<[string, string][]>([]);
  const selectedTranslations = ref<[string, string][]>([]);

  // Computed properties (getters)
  const selectedTranslationsString = computed(() => {
    let s = '';
    for (const tr of selectedTranslations.value) {
      s += tr[0] + ',' + tr[1] + '_';
    }

    if (s.length > 0) {
      s = s.slice(0, -1);
    }

    return s;
  });

  // Actions
  async function loadSurahInfo() {
    const url = import.meta.env.VITE_API_BASE_URL + "/surahs"
    const surahsApi = mande(url)
    const response = await surahsApi.get()

    surahInfo.value = response as SurahInfo[];
  }

  async function loadTextTypes() {
    const url = import.meta.env.VITE_API_BASE_URL + "/text-types"
    const api = mande(url)
    const response = await api.get()

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
    // State
    surahInfo,
    arabicTextType,
    availableTextTypes,
    availableTranslations,
    selectedTranslations,

    // Getters
    selectedTranslationsString,

    // Actions
    loadSurahInfo,
    loadTextTypes,
    setArabicTextType,
    addTranslation,
    removeTranslation
  }
})
