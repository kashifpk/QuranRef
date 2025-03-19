<template>
  <div class="browse-by-word-component">
    <div class="row">
      <div class="col-xs-12 letters_list ar" style="text-align: left;">
        <button class="btn ar"
                v-for="letter in letters"
                :key="letter"
                :class="{ 'btn-success': letter === selectedLetter, 'btn-default': letter !== selectedLetter }"
                @click="getWords(letter)">
          {{ letter }}
        </button>
      </div>
    </div>

    <div class="words_list ar" style="text-align: left;">
      <div class="row" v-for="word in words" :key="word[0]">
        <word-ayas :word="{ word: word[0], count: word[1] }" />
      </div>
    </div>

    <div v-if="loading" class="loading">
      <p>Loading...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import WordAyas from '../components/WordAyas.vue';

const letters = ref<string[]>([]);
const selectedLetter = ref('');
const words = ref<[string, number][]>([]);
const loading = ref(false);

onMounted(() => {
  getLetters();
});

const getLetters = async () => {
  loading.value = true;
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    const response = await fetch(`${baseUrl}/letters`);
    const data = await response.json();
    letters.value = data;
  } catch (error) {
    console.error('Error fetching letters:', error);
  } finally {
    loading.value = false;
  }
};

const getWords = async (letter: string) => {
  selectedLetter.value = letter;
  loading.value = true;
  words.value = [];

  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    const response = await fetch(`${baseUrl}/words-by-letter/${letter}`);
    const data = await response.json();
    words.value = data;
  } catch (error) {
    console.error('Error fetching words:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.browse-by-word-component {
  margin: 20px;
}

.letters_list, .words_list {
  font-size: 30pt;
  font-weight: bold;
}

.btn {
  margin: 2px;
  padding: 10px;
  min-width: 50px;
  font-weight: bold;
  font-size: 14pt;
  text-align: center;
}

.loading {
  text-align: center;
  margin: 20px 0;
  font-size: 1.2em;
}
</style>