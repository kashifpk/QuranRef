<template>
  <div class="study-panel">
    <div v-if="loading" class="study-loading"><ProgressSpinner strokeWidth="4" style="width: 2rem; height: 2rem" /></div>
    <template v-else>
      <div v-if="topics && topics.topics.length" class="study-section">
        <span class="study-label">Topics</span>
        <router-link v-for="t in topics.topics" :key="t.id" :to="{ name: 'topic_view', params: { id: t.id } }" class="study-chip">{{ t.name }}</router-link>
      </div>
      <div v-if="topics && topics.themes.length" class="study-section">
        <span class="study-label">Theme</span>
        <span v-for="th in topics.themes" :key="th.id" class="study-theme">
          {{ th.theme }}
          <span class="theme-range">({{ th.surah_number }}:{{ th.aya_from }}<template v-if="th.aya_to !== th.aya_from">-{{ th.aya_to }}</template>)</span>
        </span>
      </div>
      <div v-if="related && related.phrases.length" class="study-section">
        <span class="study-label">Recurring phrases</span>
        <router-link v-for="p in related.phrases" :key="p.id" :to="{ name: 'phrase_view', params: { id: p.id } }" class="study-chip ar">
          {{ p.text }} <span class="chip-count">{{ p.aya_count }}</span>
        </router-link>
      </div>
      <div v-if="related && related.similar.length" class="study-section similar">
        <span class="study-label">Similar ayas</span>
        <div v-for="s in related.similar" :key="s.aya_key" class="similar-row">
          <router-link :to="ayaLink(s.aya_key)" class="similar-key">{{ s.aya_key }}</router-link>
          <Tag severity="secondary" class="similar-score">{{ s.score }}%</Tag>
          <span class="similar-text ar">{{ arabicOf(s) }}</span>
          <span v-if="translationOf(s)" class="similar-translation">{{ translationOf(s) }}</span>
        </div>
      </div>
      <p v-if="isEmpty" class="study-empty">No topics or related ayas recorded for this aya.</p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import { useStore } from '../store';
import type { AyaTopics, RelatedInfo, SimilarAya } from '../type_defs';

const props = defineProps<{ ayaKey: string }>();
const store = useStore();
const topics = ref<AyaTopics | null>(null);
const related = ref<RelatedInfo | null>(null);
const loading = ref(true);

const isEmpty = computed(
  () =>
    !!topics.value && !!related.value &&
    topics.value.topics.length === 0 && topics.value.themes.length === 0 &&
    related.value.similar.length === 0 && related.value.phrases.length === 0
);

function ayaLink(key: string) {
  const [surah, aya] = key.split(':');
  return { name: 'surah_view', params: { surah_number: surah }, query: { aya } };
}

function arabicOf(s: SimilarAya): string {
  const arabic = s.texts.arabic || {};
  return arabic[store.arabicTextType] || Object.values(arabic)[0] || '';
}

function translationOf(s: SimilarAya): string {
  for (const [language, byType] of Object.entries(s.texts)) {
    if (language !== 'arabic') return Object.values(byType)[0] || '';
  }
  return '';
}

onMounted(async () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
  try {
    const [t, r] = await Promise.all([
      fetch(`${baseUrl}/aya-topics/${props.ayaKey}`),
      fetch(`${baseUrl}/related/${props.ayaKey}?languages=${encodeURIComponent(store.textLanguagesSpec)}`),
    ]);
    topics.value = t.ok ? await t.json() : { topics: [], themes: [] };
    related.value = r.ok ? await r.json() : { similar: [], phrases: [] };
  } catch (error) {
    console.error('Failed to load study data:', error);
    topics.value = { topics: [], themes: [] };
    related.value = { similar: [], phrases: [] };
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.study-panel {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px dashed var(--p-content-border-color, #ddd);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.study-loading {
  display: flex;
  justify-content: center;
}

.study-section {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.study-section.similar {
  flex-direction: column;
  align-items: stretch;
}

.study-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--p-text-muted-color, #666);
  margin-right: 0.25rem;
}

.study-chip {
  padding: 0.15rem 0.55rem;
  border: 1px solid var(--p-content-border-color, #ddd);
  border-radius: 999px;
  text-decoration: none;
  color: inherit;
}

.study-chip:hover {
  border-color: var(--p-primary-color, #4caf50);
}

.chip-count {
  color: var(--p-text-muted-color, #666);
  font-size: 0.75rem;
  direction: ltr;
  display: inline-block;
}

.study-theme {
  color: var(--p-text-color);
}

.theme-range {
  color: var(--p-text-muted-color, #666);
}

.similar-row {
  display: grid;
  grid-template-columns: auto auto 1fr;
  gap: 0.5rem 0.75rem;
  align-items: baseline;
  padding: 0.25rem 0;
}

.similar-key {
  color: var(--p-primary-color, #4caf50);
  text-decoration: none;
  font-weight: bold;
}

.similar-text {
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
  font-size: 1.3rem;
}

.similar-translation {
  grid-column: 3;
  color: var(--p-text-muted-color, #666);
}

.study-empty {
  margin: 0;
  color: var(--p-text-muted-color, #666);
}

.ar {
  direction: rtl;
  text-align: right;
}
</style>
