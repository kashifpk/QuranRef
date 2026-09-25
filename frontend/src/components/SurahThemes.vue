<template>
  <Card v-if="themes.length" class="surah-themes">
    <template #content>
      <button type="button" class="themes-toggle" @click="open = !open">
        <i :class="open ? 'pi pi-chevron-down' : 'pi pi-chevron-right'"></i>
        <span>Themes in this surah ({{ themes.length }})</span>
      </button>
      <ol v-show="open" class="themes-list">
        <li v-for="th in themes" :key="th.id">
          <a :href="`?aya=${th.aya_from}`" @click.prevent="$emit('goto', th.aya_from)">
            <span class="theme-range">{{ th.aya_from }}<template v-if="th.aya_to !== th.aya_from">-{{ th.aya_to }}</template></span>
            {{ th.theme }}
          </a>
        </li>
      </ol>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import Card from 'primevue/card';
import type { ThemeInfo } from '../type_defs';

const props = defineProps<{ surahNumber: number }>();
defineEmits<{ goto: [aya: number] }>();
const themes = ref<ThemeInfo[]>([]);
const open = ref(false);

watch(
  () => props.surahNumber,
  async (n) => {
    themes.value = [];
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
      const resp = await fetch(`${baseUrl}/themes/${n}`);
      if (resp.ok) themes.value = await resp.json();
    } catch (error) {
      console.error('Failed to load themes:', error);
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.surah-themes {
  margin-bottom: 1rem;
}

.themes-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font: inherit;
  color: inherit;
  padding: 0;
}

.themes-list {
  margin: 0.75rem 0 0;
  padding-left: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.themes-list a {
  color: inherit;
  text-decoration: none;
}

.themes-list a:hover {
  color: var(--p-primary-color, #4caf50);
}

.theme-range {
  color: var(--p-text-muted-color, #666);
  margin-right: 0.5rem;
  font-variant-numeric: tabular-nums;
}
</style>
