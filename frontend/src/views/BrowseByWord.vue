<template>
  <div class="browse-by-word">
    <Card>
      <template #title>
        <span class="ar">Browse by Arabic Letters</span>
      </template>
      <template #content>
        <div class="letters-grid ar">
          <Button
            v-for="letter in letters"
            :key="letter"
            :label="letter"
            :severity="letter === selectedLetter ? 'success' : 'secondary'"
            :outlined="letter !== selectedLetter"
            size="large"
            class="letter-btn ar"
            @click="getWords(letter)"
          />
        </div>
      </template>
    </Card>

    <Card v-if="words.length > 0" class="words-card">
      <template #title>
        <span class="ar">Words starting with "{{ selectedLetter }}"</span>
      </template>
      <template #content>
        <div class="words-list ar">
          <word-ayas v-for="word in words" :key="word[0]" :word="{ word: word[0], count: word[1] }" />
        </div>
      </template>
    </Card>

    <div v-if="loading" class="loading-state">
      <ProgressSpinner strokeWidth="4" />
      <p>Loading...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAsyncState } from '@vueuse/core';
import Card from 'primevue/card';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import WordAyas from '../components/WordAyas.vue';

const selectedLetter = ref('');

// Use VueUse for better async state management
const { state: letters, isLoading: lettersLoading } = useAsyncState(
  async () => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    const response = await fetch(`${baseUrl}/letters`);
    return await response.json();
  },
  [],
  { immediate: true }
);

const {
  state: words,
  isLoading: wordsLoading,
  execute: loadWords,
} = useAsyncState(
  async (letter: string) => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    const response = await fetch(`${baseUrl}/words-by-letter/${letter}`);
    return await response.json();
  },
  [],
  { immediate: false }
);

const loading = computed(() => lettersLoading.value || wordsLoading.value);

const getWords = (letter: string) => {
  selectedLetter.value = letter;
  loadWords(0, letter);
};
</script>

<style scoped>
.browse-by-word {
  max-width: 1200px;
  margin: 0 auto;
}

.letters-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.letter-btn {
  min-width: 60px !important;
  min-height: 60px !important;
  font-size: 1.25rem !important;
  font-weight: bold !important;
}

.words-card {
  margin-top: 1.5rem;
}

.words-list {
  font-size: 1.5rem;
  font-weight: bold;
  text-align: right;
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

.ar {
  direction: rtl;
  text-align: right;
}
</style>
