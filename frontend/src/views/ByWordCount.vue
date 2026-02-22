<template>
  <div class="by-word-count">
    <!-- Header Section -->
    <Card class="header-card">
      <template #title>
        <div class="page-title">
          <i class="pi pi-sort-numeric-down"></i>
          <span>Words by Frequency</span>
        </div>
      </template>
      <template #subtitle>
        Explore Quranic words organized by how frequently they appear
      </template>
    </Card>

    <!-- Quick Stats -->
    <div class="stats-row" v-if="wordCounts.length > 0">
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-value">{{ totalUniqueWords.toLocaleString() }}</div>
            <div class="stat-label">Unique Words</div>
          </div>
        </template>
      </Card>
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-value">{{ wordCounts.length }}</div>
            <div class="stat-label">Frequency Levels</div>
          </div>
        </template>
      </Card>
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-value">{{ highestCount.toLocaleString() }}</div>
            <div class="stat-label">Max Occurrences</div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Main Content Tabs -->
    <Card class="main-content-card">
      <template #content>
        <Tabs v-model:value="activeTab">
          <TabList>
            <Tab value="top">Top Words</Tab>
            <Tab value="browse">Browse by Count</Tab>
          </TabList>

          <TabPanels>
            <!-- Top Words Tab -->
            <TabPanel value="top">
              <div class="tab-content">
                <p class="tab-description">
                  The most frequently occurring words in the Quran. Click any word to see the verses where it appears.
                </p>

                <div v-if="loadingTop" class="loading-state">
                  <ProgressSpinner strokeWidth="4" />
                  <p>Loading top words...</p>
                </div>

                <div v-else class="words-list ar">
                  <WordAyas
                    v-for="word in mostCommonWords"
                    :key="word[0]"
                    :word="{ word: word[0], count: word[1] }"
                  />
                </div>
              </div>
            </TabPanel>

            <!-- Browse by Count Tab -->
            <TabPanel value="browse">
              <div class="tab-content">
                <p class="tab-description">
                  Select a frequency to see all words that appear exactly that many times.
                </p>

                <!-- Count Range Chips -->
                <div class="range-chips">
                  <Chip
                    v-for="range in countRanges"
                    :key="range.label"
                    :label="`${range.label} (${range.counts.length})`"
                    :class="{ 'range-selected': selectedRange === range.label }"
                    @click="selectRange(range)"
                  />
                </div>

                <!-- Count Selector within Range -->
                <div v-if="selectedRange && currentRangeCounts.length > 0" class="count-selector">
                  <div class="count-chips">
                    <Button
                      v-for="countInfo in currentRangeCounts"
                      :key="countInfo.count"
                      :label="String(countInfo.count)"
                      :severity="selectedCount === countInfo.count ? 'success' : 'secondary'"
                      :outlined="selectedCount !== countInfo.count"
                      size="small"
                      :badge="String(countInfo.word_count)"
                      badgeSeverity="contrast"
                      @click="selectCount(countInfo.count)"
                    />
                  </div>
                </div>

                <!-- Words for Selected Count -->
                <div v-if="selectedCount" class="selected-count-header">
                  <h3>
                    Words appearing exactly <Tag severity="success">{{ selectedCount }}</Tag> times
                    <span class="word-total">({{ words.length }} words)</span>
                  </h3>
                </div>

                <div v-if="loadingWords" class="loading-state">
                  <ProgressSpinner strokeWidth="4" />
                  <p>Loading words...</p>
                </div>

                <div v-else-if="words.length > 0" class="words-list ar">
                  <WordAyas
                    v-for="word in words"
                    :key="word[0]"
                    :word="{ word: word[0], count: word[1] }"
                  />
                </div>

                <div v-else-if="selectedCount" class="empty-state">
                  <i class="pi pi-inbox"></i>
                  <p>No words found with count {{ selectedCount }}</p>
                </div>
              </div>
            </TabPanel>


          </TabPanels>
        </Tabs>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import Card from 'primevue/card';
import Tabs from 'primevue/tabs';
import TabList from 'primevue/tablist';
import Tab from 'primevue/tab';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';
import Tag from 'primevue/tag';
import Chip from 'primevue/chip';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import WordAyas from '../components/WordAyas.vue';

interface WordCountInfo {
  count: number;
  word_count: number;
}

interface CountRange {
  label: string;
  min: number;
  max: number;
  counts: WordCountInfo[];
}

const activeTab = ref('top');
const mostCommonWords = ref<[string, number][]>([]);
const words = ref<[string, number][]>([]);
const wordCounts = ref<WordCountInfo[]>([]);
const selectedRange = ref<string | null>(null);
const selectedCount = ref<number | null>(null);

const loadingTop = ref(false);
const loadingWords = ref(false);
const loadingCounts = ref(false);

// Computed stats
const totalUniqueWords = computed(() =>
  wordCounts.value.reduce((sum, wc) => sum + wc.word_count, 0)
);

const highestCount = computed(() =>
  wordCounts.value.length > 0 ? wordCounts.value[0].count : 0
);

// Group counts into ranges
const countRanges = computed<CountRange[]>(() => {
  const ranges: CountRange[] = [
    { label: '1-5', min: 1, max: 5, counts: [] },
    { label: '6-20', min: 6, max: 20, counts: [] },
    { label: '21-50', min: 21, max: 50, counts: [] },
    { label: '51-100', min: 51, max: 100, counts: [] },
    { label: '101-500', min: 101, max: 500, counts: [] },
    { label: '500+', min: 501, max: Infinity, counts: [] },
  ];

  for (const wc of wordCounts.value) {
    for (const range of ranges) {
      if (wc.count >= range.min && wc.count <= range.max) {
        range.counts.push(wc);
        break;
      }
    }
  }

  // Sort counts within each range
  for (const range of ranges) {
    range.counts.sort((a, b) => a.count - b.count);
  }

  return ranges.filter(r => r.counts.length > 0);
});

const currentRangeCounts = computed(() => {
  if (!selectedRange.value) return [];
  const range = countRanges.value.find(r => r.label === selectedRange.value);
  return range ? range.counts : [];
});

// API calls
const baseUrl = import.meta.env.VITE_API_BASE_URL;

const fetchTopWords = async () => {
  loadingTop.value = true;
  try {
    const response = await fetch(`${baseUrl}/top-most-frequent-words/40`);
    mostCommonWords.value = await response.json();
  } catch (error) {
    console.error('Error fetching top words:', error);
  } finally {
    loadingTop.value = false;
  }
};

const fetchWordCounts = async () => {
  loadingCounts.value = true;
  try {
    const response = await fetch(`${baseUrl}/available-word-counts`);
    wordCounts.value = await response.json();
  } catch (error) {
    console.error('Error fetching word counts:', error);
  } finally {
    loadingCounts.value = false;
  }
};

const fetchWordsByCount = async (count: number) => {
  loadingWords.value = true;
  words.value = [];
  try {
    const response = await fetch(`${baseUrl}/words-by-count/${count}`);
    words.value = await response.json();
  } catch (error) {
    console.error('Error fetching words by count:', error);
  } finally {
    loadingWords.value = false;
  }
};

// Actions
const selectRange = (range: CountRange) => {
  selectedRange.value = range.label;
  selectedCount.value = null;
  words.value = [];
};

const selectCount = (count: number) => {
  selectedCount.value = count;
  fetchWordsByCount(count);
};

// Watch tab changes to load data
watch(activeTab, (newTab) => {
  if (newTab === 'top' && mostCommonWords.value.length === 0) {
    fetchTopWords();
  } else if (newTab === 'browse' && wordCounts.value.length === 0) {
    fetchWordCounts();
  }
});

onMounted(() => {
  fetchTopWords();
  fetchWordCounts();
});
</script>

<style scoped>
.by-word-count {
  max-width: 1200px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 1.5rem;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
}

.page-title i {
  color: #4CAF50;
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}

.stat-card :deep(.p-card-body) {
  padding: 1rem;
}

.stat-card :deep(.p-card-content) {
  padding: 0;
}

.stat-content {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #4CAF50;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

.dark-mode .stat-label {
  color: #999;
}

/* Main Content */
.main-content-card :deep(.p-card-content) {
  padding: 0;
}

.tab-content {
  padding: 1.5rem;
}

.tab-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.dark-mode .tab-description {
  color: #999;
}

/* Range Chips */
.range-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.range-chips :deep(.p-chip) {
  cursor: pointer;
  transition: all 0.2s;
}

.range-chips :deep(.p-chip:hover) {
  background: rgba(76, 175, 80, 0.15);
}

.range-chips :deep(.p-chip.range-selected) {
  background: #4CAF50;
  color: white;
}

/* Count Selector */
.count-selector {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(76, 175, 80, 0.05);
  border-radius: 0.5rem;
}

.dark-mode .count-selector {
  background: rgba(76, 175, 80, 0.1);
}

.count-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.count-chips :deep(.p-button) {
  min-width: 60px;
}

/* Selected Count Header */
.selected-count-header {
  margin-bottom: 1rem;
}

.selected-count-header h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 1.1rem;
  margin: 0;
}

.word-total {
  color: #666;
  font-weight: normal;
  font-size: 0.9rem;
}

.dark-mode .word-total {
  color: #999;
}

/* Words List */
.words-list {
  font-size: 1.5rem;
  font-weight: bold;
}

/* Loading State */
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

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #999;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* Arabic text */
.ar {
  direction: rtl;
  text-align: right;
}
</style>
