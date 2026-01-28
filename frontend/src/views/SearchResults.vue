<template>
  <div class="search-results">
    <Card>
      <template #title>
        Search Results for "{{ searchTerm }}"
      </template>
      <template #content>
        <div v-if="loading" class="loading-state">
          <ProgressSpinner strokeWidth="4" />
          <p>Loading results...</p>
        </div>

        <Message v-else-if="searchResults.length === 0" severity="info" :closable="false">
          No results found for "{{ searchTerm }}"
        </Message>

        <div v-else class="results-list ar">
          <aya-view
            v-for="aya in searchResults"
            :key="aya.key"
            :aya="aya"
            :display-surah-name="true"
            :highlight-word="cleanedSearchTerm"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useStore } from '../store';
import { useAsyncState } from '@vueuse/core';
import Card from 'primevue/card';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import AyaView from '../components/AyaView.vue';

const route = useRoute();
const store = useStore();
const searchTerm = ref(route.params.search_term as string);

// Clean search term for highlighting (remove diacritics and normalize)
const cleanedSearchTerm = computed(() => {
  const aarab = ['ِ', 'ْ', 'َ', 'ُ', 'ّ', 'ٍ', 'ً', 'ٌ'];

  let cleaned = '';
  for (const ch of searchTerm.value) {
    if (!aarab.includes(ch)) {
      cleaned += ch;
    }
  }

  // Normalize Arabic characters (handle different encodings)
  cleaned = cleaned
    .replace(/ک/g, 'ك') // Persian/Urdu kaf to Arabic kaf
    .replace(/ی/g, 'ي') // Persian/Urdu yeh to Arabic yeh
    .replace(/ە/g, 'ه') // Other forms of heh
    .trim();

  return cleaned;
});

// Use VueUse for better async state management
const {
  state: searchResults,
  isLoading: loading,
  execute: executeSearch,
} = useAsyncState(
  async () => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL;

    // Use cleaned search term and search against simple-clean text
    const encodedSearchTerm = encodeURIComponent(cleanedSearchTerm.value);
    let requestUrl = `${baseUrl}/search/${encodedSearchTerm}/arabic:simple-clean`;

    // For display, we want the user's selected Arabic text type and translations
    let displayLanguages = `arabic:${store.arabicTextType}`;
    if (store.selectedTranslationsString) {
      displayLanguages += `_${store.selectedTranslationsString}`;
    }

    requestUrl += `/${displayLanguages}`;

    const response = await fetch(requestUrl);
    return await response.json();
  },
  [],
  { immediate: false }
);

// Watch for route changes
watch(
  () => route.params.search_term,
  (newVal) => {
    searchTerm.value = newVal as string;
    executeSearch();
  }
);

// Watch for changes in arabicTextType or selectedTranslations
watch(
  () => store.arabicTextType,
  () => {
    executeSearch();
  }
);

watch(
  () => store.selectedTranslations,
  () => {
    executeSearch();
  },
  { deep: true }
);

onMounted(() => {
  executeSearch();
});
</script>

<style scoped>
.search-results {
  max-width: 1200px;
  margin: 0 auto;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}

.loading-state p {
  color: #666;
}

.dark-mode .loading-state p {
  color: #999;
}

.results-list {
  text-align: right;
}

.ar {
  direction: rtl;
  text-align: right;
}
</style>
