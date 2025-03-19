<template>
  <div class="browse-by-word-component">
    <h1>Words by Count</h1>

    <label for="count_select">Word count</label>
    <select class="form-control" v-model="selectedCount" @change="getWords" id="count_select">
      <option v-for="vc in validCounts" :key="vc">{{ vc }}</option>
    </select>
    <br /><br />

    <div class="words_list ar" style="text-align: left;" v-if="selectedCount">
      <div class="row" v-for="word in words" :key="word[0]">
        <word-ayas :word="{ word: word[0], count: word[1] }" />
      </div>
    </div>

    <div class="row" v-if="mostCommonWords && !selectedCount">
      <div class="panel panel-primary col-xs-12">
        <div class="panel-heading">
          Top 40 most common words
        </div>
        <div class="panel-body bg-info">
          <div class="row">
            <div class="col-xs-4 col-sm-3 col-md-2" v-for="word in mostCommonWords" :key="word[0]">
              <span class="badge">{{ word[1] }}</span>
              &nbsp;&nbsp;&nbsp;
              <span class="ar">{{ word[0] }}</span>
            </div>
          </div>
        </div>
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

const mostCommonWords = ref<[string, number][]>([]);
const selectedCount = ref<number | null>(null);
const words = ref<[string, number][]>([]);
const loading = ref(false);

// List of valid word counts from the original project
const validCounts = [
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
  26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
  49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 69, 70, 71, 72,
  73, 74, 75, 76, 77, 78, 79, 80, 82, 83, 84, 85, 86, 87, 88, 90, 91, 94, 95, 99, 101, 102,
  106, 107, 109, 111, 112, 113, 115, 116, 118, 119, 126, 127, 129, 130, 131, 133, 134, 137,
  139, 142, 146, 147, 150, 153, 156, 157, 163, 164, 165, 168, 171, 178, 182, 188, 189, 190,
  214, 217, 220, 221, 223, 229, 240, 241, 245, 250, 254, 261, 263, 265, 268, 275, 280, 287,
  294, 296, 323, 327, 337, 340, 342, 350, 373, 405, 416, 638, 646, 658, 664, 670, 810, 812,
  966, 1010, 1185, 2153, 2763
];

onMounted(() => {
  getTopMostCommonWords();
});

const getTopMostCommonWords = async () => {
  loading.value = true;
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    const response = await fetch(`${baseUrl}/top-most-frequent-words/40`);
    const data = await response.json();
    mostCommonWords.value = data;
  } catch (error) {
    console.error('Error fetching most common words:', error);
  } finally {
    loading.value = false;
  }
};

const getWords = async () => {
  if (!selectedCount.value) {
    return;
  }

  loading.value = true;
  words.value = [];

  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    const response = await fetch(`${baseUrl}/words-by-count/${selectedCount.value}`);
    const data = await response.json();
    words.value = data;
  } catch (error) {
    console.error('Error fetching words by count:', error);
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

select {
  max-width: 200px;
}

.panel-heading {
  font-weight: bold;
  font-size: 1.2em;
}
</style>