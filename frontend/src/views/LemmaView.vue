<template>
  <div class="lemma-view">
    <Card v-if="info" class="lemma-header">
      <template #content>
        <div class="lemma-head">
          <h1 class="ar lemma-title">{{ info.lemma }}</h1>
          <div class="lemma-meta">
            <Tag severity="secondary">{{ posLabel }}</Tag>
            <Tag severity="success">{{ info.count }} occurrences</Tag>
            <router-link v-if="info.root" :to="{ name: 'root_view', params: { root: info.root } }" class="root-link">
              root <span class="ar">{{ info.root }}</span>
            </router-link>
          </div>
        </div>
        <div v-if="meaningLanguages.length" class="meanings">
          <div v-for="language in meaningLanguages" :key="language" class="meaning-language">
            <div class="meaning-label">Meanings used ({{ language }})</div>
            <div class="meaning-chips">
              <Chip
                v-for="m in info.meanings[language]"
                :key="m.gloss"
                :label="`${m.gloss} (${m.count})`"
              />
            </div>
          </div>
        </div>
        <p v-else class="no-meanings">No word-by-word meanings imported yet.</p>
      </template>
    </Card>

    <div v-if="info" class="occurrences">
      <aya-view
        v-for="occ in visibleOccurrences"
        :key="`${occ.aya_key}-${occ.position}`"
        :aya="toAyaInfo(occ)"
        :display-surah-name="true"
        :highlight-word="occ.text_simple"
      />
      <div v-if="visibleCount < info.occurrences.length" class="show-more">
        <Button :label="`Show more (${info.occurrences.length - visibleCount} left)`" outlined @click="visibleCount += pageSize" />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <ProgressSpinner strokeWidth="4" />
    </div>
    <Card v-if="notFound"><template #content>Lemma not found.</template></Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import Card from 'primevue/card';
import Tag from 'primevue/tag';
import Chip from 'primevue/chip';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import AyaView from '../components/AyaView.vue';
import { useStore } from '../store';
import type { AyaInfo, LemmaInfo, LemmaOccurrence } from '../type_defs';
import { POS_LABELS } from '../type_defs';

const props = defineProps<{ lemma: string }>();
const store = useStore();

const info = ref<LemmaInfo | null>(null);
const loading = ref(false);
const notFound = ref(false);
const pageSize = 50;
const visibleCount = ref(pageSize);

const posLabel = computed(() => (info.value ? POS_LABELS[info.value.pos] || info.value.pos : ''));
const meaningLanguages = computed(() => (info.value ? Object.keys(info.value.meanings) : []));
const visibleOccurrences = computed(() => info.value?.occurrences.slice(0, visibleCount.value) ?? []);

function toAyaInfo(occ: LemmaOccurrence): AyaInfo {
  return { aya_key: occ.aya_key, texts: { arabic: { [store.arabicTextType]: occ.aya_text } } };
}

async function load() {
  loading.value = true;
  notFound.value = false;
  info.value = null;
  visibleCount.value = pageSize;
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(
      `${baseUrl}/lemma/${encodeURIComponent(props.lemma)}?text_type=${encodeURIComponent(store.arabicTextType)}`
    );
    if (resp.status === 404) {
      notFound.value = true;
      return;
    }
    info.value = await resp.json();
  } catch (error) {
    console.error('Failed to load lemma:', error);
  } finally {
    loading.value = false;
  }
}

watch(() => [props.lemma, store.arabicTextType], load, { immediate: true });
</script>

<style scoped>
.lemma-view {
  max-width: 1200px;
  margin: 0 auto;
}

.lemma-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.lemma-title {
  font-size: 2.5rem;
  margin: 0;
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
}

.lemma-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.root-link {
  color: var(--p-primary-color, #4caf50);
  text-decoration: none;
}

.root-link:hover {
  text-decoration: underline;
}

.meanings {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.meaning-label {
  font-size: 0.8rem;
  text-transform: capitalize;
  color: var(--p-text-muted-color, #666);
  margin-bottom: 0.25rem;
}

.meaning-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.no-meanings {
  margin: 1rem 0 0;
  color: var(--p-text-muted-color, #666);
}

.occurrences {
  margin-top: 1rem;
}

.show-more {
  display: flex;
  justify-content: center;
  margin: 1rem 0;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 3rem;
}

.ar {
  direction: rtl;
}
</style>
