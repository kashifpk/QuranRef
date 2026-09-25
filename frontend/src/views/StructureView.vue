<template>
  <div class="structure-view">
    <Card>
      <template #title>Juz, Hizb and Manzil</template>
      <template #content>
        <p class="hint">Read the Quran by its traditional divisions. A juz is a thirtieth, a hizb a sixtieth, a rub a quarter of a hizb, and a manzil one of the seven weekly portions.</p>
        <Tabs value="juz">
          <TabList>
            <Tab v-for="kind in kinds" :key="kind" :value="kind">{{ UNIT_LABELS[kind] }}</Tab>
          </TabList>
          <TabPanels>
            <TabPanel v-for="kind in kinds" :key="kind" :value="kind">
              <div class="unit-grid">
                <router-link
                  v-for="u in units(kind)"
                  :key="u.number"
                  :to="{ name: 'read_unit', params: { unit: kind, n: u.number } }"
                  class="unit-card"
                >
                  <span class="unit-number">{{ UNIT_LABELS[kind] }} {{ u.number }}</span>
                  <span class="unit-range">{{ u.first_verse_key }} to {{ u.last_verse_key }}</span>
                  <span class="unit-count">{{ u.verses_count }} ayas</span>
                </router-link>
              </div>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </template>
    </Card>
    <div v-if="!store.structure" class="loading-state"><ProgressSpinner strokeWidth="4" /></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import Card from 'primevue/card';
import Tabs from 'primevue/tabs';
import TabList from 'primevue/tablist';
import Tab from 'primevue/tab';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';
import ProgressSpinner from 'primevue/progressspinner';
import { useStore } from '../store';
import { UNIT_LABELS } from '../structure';
import type { UnitKind } from '../type_defs';

const store = useStore();
const kinds: UnitKind[] = ['juz', 'hizb', 'rub', 'manzil'];

onMounted(() => {
  store.loadStructure();
});

function units(kind: UnitKind) {
  return store.structure ? store.structure[kind] : [];
}
</script>

<style scoped>
.structure-view {
  max-width: 1100px;
  margin: 0 auto;
}

.hint {
  margin: 0 0 1rem;
  color: var(--p-text-muted-color, #666);
}

.unit-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.75rem;
}

.unit-card {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.75rem;
  border: 1px solid var(--p-content-border-color, #ddd);
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
}

.unit-card:hover {
  border-color: var(--p-primary-color, #4caf50);
  background: rgba(76, 175, 80, 0.06);
}

.unit-number {
  font-weight: bold;
}

.unit-range,
.unit-count {
  font-size: 0.8rem;
  color: var(--p-text-muted-color, #666);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 2rem;
}
</style>
