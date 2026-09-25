<template>
  <div class="tafsir-panel">
    <div v-if="loading" class="tafsir-loading"><i class="pi pi-spin pi-spinner"></i> Loading tafsir...</div>
    <div v-for="entry in entries" :key="entry.slug" class="tafsir-entry">
      <div class="tafsir-head">
        <span class="tafsir-name">{{ entry.name }}</span>
        <span v-if="entry.passage && entry.passage.aya_keys.length > 1" class="tafsir-range en">
          covers {{ entry.passage.from_key }} to {{ entry.passage.to_key }}
        </span>
      </div>
      <div
        v-if="entry.passage"
        class="tafsir-text"
        :class="{ rtl: isRtl(entry.passage.language) }"
        v-html="entry.passage.text"
      ></div>
      <div v-else class="tafsir-missing">No passage for this aya.</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import type { TafsirPassage } from '../type_defs';

// Shows the passages of the selected tafsirs that cover one aya.
const props = defineProps<{ ayaKey: string; slugs: string[] }>();

interface Entry {
  slug: string;
  name: string;
  passage: TafsirPassage | null;
}

const entries = ref<Entry[]>([]);
const loading = ref(false);

function isRtl(language: string) {
  return ['urdu', 'arabic', 'persian', 'sindhi', 'pashto'].includes(language);
}

async function load() {
  loading.value = true;
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
  const results: Entry[] = [];
  for (const slug of props.slugs) {
    try {
      const resp = await fetch(`${baseUrl}/tafsir/${encodeURIComponent(slug)}/${props.ayaKey}`);
      if (resp.ok) {
        const passage: TafsirPassage = await resp.json();
        results.push({ slug, name: passage.name, passage });
      } else {
        results.push({ slug, name: slug, passage: null });
      }
    } catch (error) {
      console.error('Failed to load tafsir:', error);
      results.push({ slug, name: slug, passage: null });
    }
  }
  entries.value = results;
  loading.value = false;
}

watch(() => [props.ayaKey, props.slugs.join(',')], load, { immediate: true });
</script>

<style scoped>
.tafsir-panel {
  margin: 0.5rem 0 1rem;
  padding: 0.75rem 1rem;
  border-left: 3px solid var(--p-primary-color, #4caf50);
  background: rgba(76, 175, 80, 0.04);
  border-radius: 0 6px 6px 0;
  text-align: left;
  direction: ltr;
}

.tafsir-loading,
.tafsir-missing {
  color: var(--p-text-muted-color);
  font-size: 0.875rem;
}

.tafsir-entry + .tafsir-entry {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--p-content-border-color, #e0e0e0);
}

.tafsir-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.tafsir-name {
  font-weight: 600;
  color: var(--p-primary-color);
}

.tafsir-range {
  font-size: 0.75rem;
  color: var(--p-text-muted-color);
}

.tafsir-text {
  line-height: 1.7;
  font-size: 1rem;
}

.tafsir-text.rtl {
  direction: rtl;
  text-align: right;
  font-size: 1.15rem;
}

.tafsir-text :deep(p) {
  margin: 0 0 0.75rem;
}

.tafsir-text :deep(h1),
.tafsir-text :deep(h2),
.tafsir-text :deep(h3) {
  font-size: 1.05rem;
  margin: 0.75rem 0 0.25rem;
}

.en {
  direction: ltr;
}
</style>
