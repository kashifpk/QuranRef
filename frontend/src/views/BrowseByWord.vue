<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="ar text-center">
            Browse by Arabic Letters
          </v-card-title>
          
          <v-card-text>
            <div class="letters-grid ar text-center">
              <v-btn
                v-for="letter in letters"
                :key="letter"
                :variant="letter === selectedLetter ? 'flat' : 'outlined'"
                :color="letter === selectedLetter ? 'green' : 'default'"
                size="large"
                class="ma-1 ar-letter"
                @click="getWords(letter)"
              >
                {{ letter }}
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="words.length > 0">
      <v-col cols="12">
        <v-card>
          <v-card-title class="ar">
            Words starting with "{{ selectedLetter }}"
          </v-card-title>
          
          <v-card-text>
            <div class="words-list ar">
              <word-ayas 
                v-for="word in words" 
                :key="word[0]"
                :word="{ word: word[0], count: word[1] }" 
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular
          indeterminate
          color="green"
          size="64"
        />
        <p class="mt-4">Loading...</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAsyncState } from '@vueuse/core';
import { VContainer, VRow, VCol, VCard, VCardTitle, VCardText, VBtn, VProgressCircular } from 'vuetify/components';
import WordAyas from '../components/WordAyas.vue';

const selectedLetter = ref('');

// Use VueUse for better async state management
const {
  state: letters,
  isLoading: lettersLoading
} = useAsyncState(
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
  execute: loadWords
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
.letters-grid {
  font-size: 18pt;
  font-weight: bold;
}

.ar-letter {
  min-width: 60px !important;
  min-height: 60px !important;
  font-size: 18pt !important;
  font-weight: bold !important;
}

.words-list {
  font-size: 24pt;
  font-weight: bold;
  text-align: right;
}
</style>