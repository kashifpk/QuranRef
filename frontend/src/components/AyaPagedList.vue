<template>
  <div class="aya-paged-list">
    <p v-if="total !== null" class="list-summary">{{ total }} {{ total === 1 ? 'aya' : 'ayas' }}</p>
    <aya-view
      v-for="aya in ayas"
      :key="aya.aya_key"
      :aya="aya"
      :display-surah-name="true"
    />
    <div v-if="total !== null && ayas.length < total" class="show-more">
      <Button :label="`Show more (${total - ayas.length} left)`" outlined :loading="loading" @click="loadMore" />
    </div>
    <div v-if="loading && ayas.length === 0" class="loading-state"><ProgressSpinner strokeWidth="4" /></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import AyaView from './AyaView.vue';
import { useStore } from '../store';
import type { AyaInfo, AyaPage } from '../type_defs';

// Renders a paged list of ayas from an endpoint that returns AyaPage
// (for example /topic/{id}/ayas or /phrase/{id}/ayas).
const props = defineProps<{ endpoint: string; pageSize?: number }>();
const store = useStore();
const ayas = ref<AyaInfo[]>([]);
const total = ref<number | null>(null);
const loading = ref(false);
const size = props.pageSize ?? 50;

async function fetchPage(offset: number) {
  loading.value = true;
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(
      `${baseUrl}${props.endpoint}?languages=${encodeURIComponent(store.textLanguagesSpec)}&offset=${offset}&limit=${size}`
    );
    if (!resp.ok) return;
    const page: AyaPage = await resp.json();
    total.value = page.total;
    ayas.value = offset === 0 ? page.ayas : ayas.value.concat(page.ayas);
  } catch (error) {
    console.error('Failed to load ayas:', error);
  } finally {
    loading.value = false;
  }
}

function loadMore() {
  fetchPage(ayas.value.length);
}

watch(() => [props.endpoint, store.textLanguagesSpec], () => fetchPage(0), { immediate: true });
</script>

<style scoped>
.list-summary {
  color: var(--p-text-muted-color, #666);
  margin: 0.5rem 0;
}

.show-more {
  display: flex;
  justify-content: center;
  margin: 1rem 0;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 2rem;
}
</style>
