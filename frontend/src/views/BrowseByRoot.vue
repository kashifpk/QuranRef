<template>
  <div class="browse-by-root">
    <Card>
      <template #title>
        <span>Browse by Root</span>
      </template>
      <template #content>
        <p class="hint">Pick the first letter of a root. Roots group every word derived from the same letters.</p>
        <div class="letters-grid ar">
          <Button
            v-for="letter in letters"
            :key="letter"
            :label="letter"
            :severity="letter === selectedLetter ? 'success' : 'secondary'"
            :outlined="letter !== selectedLetter"
            size="large"
            class="letter-btn ar"
            @click="getRoots(letter)"
          />
        </div>
      </template>
    </Card>

    <Card v-if="roots.length > 0" class="roots-card">
      <template #title>
        <span>Roots starting with "<span class="ar">{{ selectedLetter }}</span>"</span>
      </template>
      <template #content>
        <div class="roots-grid ar">
          <router-link
            v-for="[root, count] in roots"
            :key="root"
            :to="{ name: 'root_view', params: { root } }"
            class="root-chip"
          >
            <span class="root-text">{{ Array.from(root).join(' ') }}</span>
            <span class="root-count">{{ count }}</span>
          </router-link>
        </div>
      </template>
    </Card>

    <div v-if="loading" class="loading-state">
      <ProgressSpinner strokeWidth="4" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAsyncState } from '@vueuse/core';
import Card from 'primevue/card';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';

const selectedLetter = ref('');
const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const { state: letters, isLoading: lettersLoading } = useAsyncState(
  async () => (await fetch(`${baseUrl}/letters`)).json() as Promise<string[]>,
  [] as string[],
  { immediate: true }
);

const { state: roots, isLoading: rootsLoading, execute: loadRoots } = useAsyncState(
  async (letter: string) =>
    (await fetch(`${baseUrl}/roots-by-letter/${encodeURIComponent(letter)}`)).json() as Promise<[string, number][]>,
  [] as [string, number][],
  { immediate: false }
);

const loading = computed(() => lettersLoading.value || rootsLoading.value);

const getRoots = (letter: string) => {
  selectedLetter.value = letter;
  loadRoots(0, letter);
};
</script>

<style scoped>
.browse-by-root {
  max-width: 1200px;
  margin: 0 auto;
}

.hint {
  margin: 0 0 1rem;
  color: var(--p-text-muted-color, #666);
}

.letters-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.letter-btn {
  min-width: 60px !important;
  min-height: 60px !important;
  font-size: 1.25rem !important;
  font-weight: bold !important;
}

.roots-card {
  margin-top: 1.5rem;
}

.roots-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.root-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--p-content-border-color, #ddd);
  border-radius: 999px;
  text-decoration: none;
  color: inherit;
}

.root-chip:hover {
  border-color: var(--p-primary-color, #4caf50);
  background: rgba(76, 175, 80, 0.08);
}

.root-text {
  font-size: 1.4rem;
  letter-spacing: 0.08em;
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
}

.root-count {
  font-size: 0.75rem;
  color: var(--p-text-muted-color, #666);
  direction: ltr;
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
