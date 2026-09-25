<template>
  <div class="phrase-view">
    <Card v-if="phrase">
      <template #content>
        <div class="phrase-head">
          <div class="phrase-text ar">{{ phrase.text }}</div>
          <div class="phrase-meta">
            <Tag severity="success">{{ phrase.aya_count }} ayas</Tag>
            <span class="phrase-source">first at <router-link :to="ayaLink(phrase.source_aya)">{{ phrase.source_aya }}</router-link></span>
          </div>
        </div>
      </template>
    </Card>
    <aya-paged-list v-if="phrase" :endpoint="`/phrase/${id}/ayas`" />
    <Card v-if="notFound"><template #content>Phrase not found.</template></Card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import Card from 'primevue/card';
import Tag from 'primevue/tag';
import AyaPagedList from '../components/AyaPagedList.vue';
import type { PhraseInfo } from '../type_defs';

const props = defineProps<{ id: string }>();
const phrase = ref<PhraseInfo | null>(null);
const notFound = ref(false);

function ayaLink(key: string) {
  const [surah, aya] = key.split(':');
  return { name: 'surah_view', params: { surah_number: surah }, query: { aya } };
}

async function load() {
  phrase.value = null;
  notFound.value = false;
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(`${baseUrl}/phrase/${encodeURIComponent(props.id)}`);
    if (resp.status === 404) {
      notFound.value = true;
      return;
    }
    phrase.value = await resp.json();
  } catch (error) {
    console.error('Failed to load phrase:', error);
  }
}

watch(() => props.id, load, { immediate: true });
</script>

<style scoped>
.phrase-view {
  max-width: 1200px;
  margin: 0 auto;
}

.phrase-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.phrase-text {
  font-size: 2rem;
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
}

.phrase-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.phrase-source {
  color: var(--p-text-muted-color, #666);
  font-size: 0.9rem;
}

.phrase-source a {
  color: var(--p-primary-color, #4caf50);
}

.ar {
  direction: rtl;
  text-align: right;
}
</style>
