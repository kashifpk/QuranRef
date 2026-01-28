<template>
  <div class="by-word-count">
    <Card>
      <template #title>Words by Count</template>
      <template #content>
        <div class="count-selector">
          <label class="select-label">Word count</label>
          <Select
            v-model="selectedCount"
            :options="validCounts"
            placeholder="Select a count..."
            @change="getWords"
            showClear
            class="count-select"
          />
        </div>

        <div v-if="selectedCount" class="words-list ar">
          <word-ayas v-for="word in words" :key="word[0]" :word="{ word: word[0], count: word[1] }" />
        </div>

        <div v-if="mostCommonWords.length > 0 && !selectedCount" class="common-words-section">
          <Card>
            <template #title>Top 40 Most Common Words</template>
            <template #content>
              <div class="common-words-grid">
                <div v-for="word in mostCommonWords" :key="word[0]" class="common-word-item">
                  <Tag severity="info" class="word-count-badge">{{ word[1] }}</Tag>
                  <span class="ar word-text">{{ word[0] }}</span>
                </div>
              </div>
            </template>
          </Card>
        </div>

        <div v-if="loading" class="loading-state">
          <ProgressSpinner strokeWidth="4" />
          <p>Loading...</p>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Card from 'primevue/card';
import Select from 'primevue/select';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import WordAyas from '../components/WordAyas.vue';

const mostCommonWords = ref<[string, number][]>([]);
const selectedCount = ref<number | null>(null);
const words = ref<[string, number][]>([]);
const loading = ref(false);

// List of valid word counts from the original project
const validCounts = [
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
  28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
  53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78,
  79, 80, 82, 83, 84, 85, 86, 87, 88, 90, 91, 94, 95, 99, 101, 102, 106, 107, 109, 111, 112, 113,
  115, 116, 118, 119, 126, 127, 129, 130, 131, 133, 134, 137, 139, 142, 146, 147, 150, 153, 156, 157,
  163, 164, 165, 168, 171, 178, 182, 188, 189, 190, 214, 217, 220, 221, 223, 229, 240, 241, 245, 250,
  254, 261, 263, 265, 268, 275, 280, 287, 294, 296, 323, 327, 337, 340, 342, 350, 373, 405, 416, 638,
  646, 658, 664, 670, 810, 812, 966, 1010, 1185, 2153, 2763,
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
.by-word-count {
  max-width: 1200px;
  margin: 0 auto;
}

.count-selector {
  margin-bottom: 2rem;
}

.select-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--app-text, #333);
  margin-bottom: 0.5rem;
}

.dark-mode .select-label {
  color: #e0e0e0;
}

.count-select {
  max-width: 300px;
}

.words-list {
  font-size: 1.5rem;
  font-weight: bold;
  text-align: left;
}

.common-words-section {
  margin-top: 1rem;
}

.common-words-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.common-word-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: rgba(76, 175, 80, 0.05);
  border-radius: 0.5rem;
}

.dark-mode .common-word-item {
  background: rgba(76, 175, 80, 0.1);
}

.word-count-badge {
  font-size: 0.75rem;
}

.word-text {
  font-size: 1.25rem;
  font-weight: bold;
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
