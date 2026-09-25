<template>
  <div class="read-unit">
    <Card class="unit-header">
      <template #content>
        <div class="unit-head">
          <Button icon="pi pi-chevron-left" text rounded :disabled="!hasPrev" @click="go(-1)" v-tooltip.bottom="'Previous'" />
          <div class="unit-title">
            <h1>{{ label }} {{ n }}</h1>
            <span v-if="unit" class="unit-range">{{ unit.first_verse_key }} to {{ unit.last_verse_key }}, {{ unit.verses_count }} ayas</span>
          </div>
          <Button icon="pi pi-chevron-right" text rounded :disabled="!hasNext" @click="go(1)" v-tooltip.bottom="'Next'" />
        </div>
      </template>
    </Card>

    <div v-for="seg in segments" :key="seg.surah" class="unit-segment">
      <router-link :to="{ name: 'surah_view', params: { surah_number: seg.surah }, query: { aya: seg.from } }" class="segment-header">
        <span class="ar segment-arabic">{{ surahName(seg.surah)?.arabic_name }}</span>
        <span class="segment-english">{{ surahName(seg.surah)?.english_name }} {{ seg.from }}<template v-if="seg.to !== seg.from">-{{ seg.to }}</template></span>
      </router-link>
      <aya-view v-for="aya in texts[seg.surah] || []" :key="aya.aya_key" :aya="aya" :display-surah-name="false" :playlist="playlist" />
    </div>

    <div v-if="loading" class="loading-state"><ProgressSpinner strokeWidth="4" /></div>
    <Card v-if="notFound"><template #content>No such {{ label.toLowerCase() }}.</template></Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import AyaView from '../components/AyaView.vue';
import { useStore } from '../store';
import { UNIT_LABELS, segmentsOf, type Segment } from '../structure';
import type { AyaInfo, StructureUnit, UnitKind } from '../type_defs';

const props = defineProps<{ unit: UnitKind; n: string | number }>();
const store = useStore();
const router = useRouter();

const unit = ref<StructureUnit | null>(null);
const segments = ref<Segment[]>([]);
const texts = ref<Record<number, AyaInfo[]>>({});
const loading = ref(false);
const notFound = ref(false);

const label = computed(() => UNIT_LABELS[props.unit] || props.unit);
// Recitation order across the segments (aya 0, the bismillah line, has no file of its own)
const playlist = computed(() =>
  segments.value
    .flatMap((seg) => (texts.value[seg.surah] || []).map((a) => a.aya_key))
    .filter((key) => Number(key.split(':')[1]) > 0)
);
const total = computed(() => store.structure?.[props.unit]?.length ?? 0);
const hasPrev = computed(() => Number(props.n) > 1);
const hasNext = computed(() => Number(props.n) < total.value);

function surahName(surah: number) {
  return store.surahInfo[surah - 1];
}

function go(delta: number) {
  router.push({ name: 'read_unit', params: { unit: props.unit, n: Number(props.n) + delta } });
}

async function load() {
  loading.value = true;
  notFound.value = false;
  unit.value = null;
  texts.value = {};
  try {
    if (store.surahInfo.length === 0) await store.loadSurahInfo();
    const structure = await store.loadStructure();
    const found = structure?.[props.unit]?.find((u) => u.number === Number(props.n)) || null;
    if (!found) {
      notFound.value = true;
      return;
    }
    unit.value = found;
    segments.value = segmentsOf(found);
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    await Promise.all(
      segments.value.map(async (seg) => {
        const resp = await fetch(`${baseUrl}/text/${seg.surah}:${seg.from}-${seg.to}/${store.textLanguagesSpec}`);
        if (resp.ok) texts.value[seg.surah] = await resp.json();
      })
    );
  } catch (error) {
    console.error('Failed to load unit:', error);
  } finally {
    loading.value = false;
  }
}

watch(() => [props.unit, props.n, store.textLanguagesSpec], load, { immediate: true });
</script>

<style scoped>
.read-unit {
  max-width: 1200px;
  margin: 0 auto;
}

.unit-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.unit-title {
  text-align: center;
}

.unit-title h1 {
  margin: 0;
  font-size: 1.6rem;
}

.unit-range {
  font-size: 0.85rem;
  color: var(--p-text-muted-color, #666);
}

.unit-segment {
  margin-top: 1rem;
}

.segment-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  background: rgba(76, 175, 80, 0.12);
  text-decoration: none;
  color: inherit;
}

.segment-arabic {
  font-size: 1.6rem;
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
}

.segment-english {
  color: var(--p-text-muted-color, #666);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.ar {
  direction: rtl;
}
</style>
