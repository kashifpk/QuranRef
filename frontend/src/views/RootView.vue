<template>
  <div class="root-view">
    <Card v-if="info">
      <template #content>
        <div class="root-head">
          <h1 class="ar root-title">{{ spacedRoot }}</h1>
          <Tag severity="success">{{ info.count }} occurrences</Tag>
          <Tag severity="secondary">{{ info.lemmas.length }} lemmas</Tag>
        </div>
        <div class="lemma-list">
          <router-link
            v-for="l in info.lemmas"
            :key="l.lemma"
            :to="{ name: 'lemma_view', params: { lemma: l.lemma } }"
            class="lemma-item"
          >
            <span class="ar lemma-text">{{ l.lemma }}</span>
            <span class="lemma-pos">{{ POS_LABELS[l.pos] || l.pos }}</span>
            <Tag severity="contrast">{{ l.count }}</Tag>
          </router-link>
        </div>
      </template>
    </Card>
    <div v-if="loading" class="loading-state"><ProgressSpinner strokeWidth="4" /></div>
    <Card v-if="notFound"><template #content>Root not found.</template></Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import Card from 'primevue/card';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';
import type { RootInfo } from '../type_defs';
import { POS_LABELS } from '../type_defs';

const props = defineProps<{ root: string }>();
const info = ref<RootInfo | null>(null);
const loading = ref(false);
const notFound = ref(false);

const spacedRoot = computed(() => (info.value ? Array.from(info.value.root).join(' ') : ''));

async function load() {
  loading.value = true;
  notFound.value = false;
  info.value = null;
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(`${baseUrl}/root/${encodeURIComponent(props.root)}`);
    if (resp.status === 404) {
      notFound.value = true;
      return;
    }
    info.value = await resp.json();
  } catch (error) {
    console.error('Failed to load root:', error);
  } finally {
    loading.value = false;
  }
}

watch(() => props.root, load, { immediate: true });
</script>

<style scoped>
.root-view {
  max-width: 900px;
  margin: 0 auto;
}

.root-head {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.root-title {
  font-size: 2.5rem;
  margin: 0;
  letter-spacing: 0.1em;
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
}

.lemma-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.lemma-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  text-decoration: none;
  color: inherit;
}

.lemma-item:hover {
  background: var(--p-content-hover-background, rgba(76, 175, 80, 0.08));
}

.lemma-text {
  font-size: 1.6rem;
  flex: 1;
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
}

.lemma-pos {
  font-size: 0.8rem;
  color: var(--p-text-muted-color, #666);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 3rem;
}

.ar {
  direction: rtl;
  text-align: right;
}
</style>
