import { mande } from "mande"
import { defineStore } from "pinia"
import { ref } from "vue"
// import { ImportMeta } from "vite"
import type { SurahInfo } from "./type_defs"


export const useStore = defineStore('quranref_store', () => {
  const surahInfo = ref<SurahInfo[]>([]);

  async function loadSurahInfo() {
    const url = import.meta.env.VITE_API_BASE_URL + "/surahs"
    const surahsApi = mande(url)
    const response = await surahsApi.get()

    surahInfo.value = response as SurahInfo[];
  }

  return { surahInfo, loadSurahInfo }
})
