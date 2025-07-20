<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-center">
            Search Results for "{{ searchTerm }}"
          </v-card-title>
          
          <v-card-text>
            <v-row v-if="loading">
              <v-col cols="12" class="text-center">
                <v-progress-circular
                  indeterminate
                  color="green"
                  size="64"
                />
                <p class="mt-4">Loading results...</p>
              </v-col>
            </v-row>

            <v-row v-else-if="searchResults.length === 0">
              <v-col cols="12" class="text-center">
                <v-alert type="info" variant="tonal">
                  No results found for "{{ searchTerm }}"
                </v-alert>
              </v-col>
            </v-row>

            <v-row v-else>
              <v-col cols="12">
                <div class="search-results-list" style="text-align: right;">
                  <aya-view 
                    v-for="aya in searchResults" 
                    :key="aya.key"
                    :aya="aya" 
                    :display-surah-name="true"
                    :highlight-word="cleanedSearchTerm"
                    class="mb-4"
                  />
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useStore } from '../store';
import { useAsyncState } from '@vueuse/core';
import { VContainer, VRow, VCol, VCard, VCardTitle, VCardText, VProgressCircular, VAlert } from 'vuetify/components';
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
    .replace(/ک/g, 'ك')  // Persian/Urdu kaf to Arabic kaf
    .replace(/ی/g, 'ي')  // Persian/Urdu yeh to Arabic yeh
    .replace(/ە/g, 'ه')  // Other forms of heh
    .trim();
  
  console.log('Original search term:', searchTerm.value);
  console.log('Cleaned search term:', cleaned);
  
  return cleaned;
});

// Use VueUse for better async state management
const {
  state: searchResults,
  isLoading: loading,
  execute: executeSearch
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
    
    console.log('Search URL:', requestUrl);
    console.log('Original search term:', searchTerm.value);
    console.log('Cleaned search term:', cleanedSearchTerm.value);

    const response = await fetch(requestUrl);
    return await response.json();
  },
  [],
  { immediate: false }
);

// Watch for route changes
watch(() => route.params.search_term, (newVal) => {
  searchTerm.value = newVal as string;
  executeSearch();
});

// Watch for changes in arabicTextType or selectedTranslations
watch(() => store.arabicTextType, () => {
  executeSearch();
});

watch(() => store.selectedTranslations, () => {
  executeSearch();
}, { deep: true });

onMounted(() => {
  executeSearch();
});
</script>