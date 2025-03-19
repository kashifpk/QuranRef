<template>
  <div class="search-results-component">
    <br />
    <div class="row" v-for="aya in searchResults" :key="aya.key">
      <aya-view :aya="aya" :display-surah-name="true"></aya-view>
    </div>
    <div v-if="loading" class="loading">
      <p>Loading results...</p>
    </div>
    <div v-if="!loading && searchResults.length === 0" class="no-results">
      <p>No results found for "{{ searchTerm }}"</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useStore } from '../store';
import AyaView from '../components/AyaView.vue';

const route = useRoute();
const store = useStore();
const searchResults = ref<any[]>([]);
const loading = ref(false);
const searchTerm = ref(route.params.search_term as string);

// Function to get search results
const getSearchResults = async () => {
  loading.value = true;
  searchResults.value = [];

  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    let requestUrl = `${baseUrl}/search/${searchTerm.value}/arabic,${store.arabicTextType}`;

    if (store.selectedTranslationsString) {
      requestUrl += `/${store.selectedTranslationsString}`;
    } else {
      requestUrl += '/none';
    }

    const response = await fetch(requestUrl);
    const data = await response.json();
    searchResults.value = data;
  } catch (error) {
    console.error('Error fetching search results:', error);
  } finally {
    loading.value = false;
  }
};

// Watch for route changes
watch(() => route.params.search_term, (newVal) => {
  searchTerm.value = newVal as string;
  getSearchResults();
});

// Watch for changes in arabicTextType or selectedTranslations
watch(() => store.arabicTextType, () => {
  getSearchResults();
});

watch(() => store.selectedTranslations, () => {
  getSearchResults();
}, { deep: true });

onMounted(() => {
  getSearchResults();
});
</script>

<style scoped>
.search-results-component {
  text-align: right;
}

.loading, .no-results {
  text-align: center;
  margin: 20px 0;
  font-size: 1.2em;
}
</style>