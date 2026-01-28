<template>
  <div class="surah-view">
    <Card class="surah-header">
      <template #content>
        <h1 class="ar surah-name">{{ surahInfo?.arabic_name }}</h1>
        <p class="surah-info" v-if="surahInfo">
          {{ surahInfo.english_name }} - {{ surahInfo.translated_name }}
          <span class="surah-meta">
            ({{ surahInfo.total_ayas }} verses, {{ surahInfo.nuzool_location }})
          </span>
        </p>
      </template>
    </Card>

    <div v-if="surahAyas && surahAyas.length > 0" class="ayas-list">
      <aya-view v-for="aya in surahAyas" :key="aya.aya_key" :aya="aya" :display-surah-name="false" />
    </div>

    <div v-else class="loading-state">
      <ProgressSpinner strokeWidth="4" />
      <p>Loading Surah...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { mande } from 'mande';
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useStore } from '../store';
import Card from 'primevue/card';
import ProgressSpinner from 'primevue/progressspinner';
import type { SurahInfo, AyaInfo } from '../type_defs';
import AyaView from './AyaView.vue';

const props = defineProps({
  surah_number: Number,
});

const store = useStore();
const route = useRoute();

const surahAyas = ref<AyaInfo[]>();
const surahInfo = ref<SurahInfo>();

onMounted(async () => {
  if (props.surah_number !== undefined) {
    surahInfo.value = store.surahInfo[props.surah_number - 1];
    await getSurahText();
  } else {
    console.error('surah_number is undefined');
  }
});

watch(
  () => route.params.surah_number,
  async (newVal, oldVal) => {
    console.log('route.params.surah_number changed: ', newVal, ' | was: ', oldVal);
    await getSurahText();
  }
);

// Watch for changes in Arabic text type
watch(
  () => store.arabicTextType,
  async () => {
    console.log('Arabic text type changed, refreshing surah text');
    await getSurahText();
  }
);

// Watch for changes in selected translations
watch(
  () => store.selectedTranslations,
  async () => {
    console.log('Selected translations changed, refreshing surah text');
    await getSurahText();
  },
  { deep: true }
);

const getSurahText = async () => {
  // Build the language specification using user's selections
  let languagesSpec = `arabic:${store.arabicTextType}`;

  if (store.selectedTranslationsString) {
    languagesSpec += `_${store.selectedTranslationsString}`;
  }

  const url =
    import.meta.env.VITE_API_BASE_URL + '/text/' + props.surah_number + '/' + languagesSpec;

  const surahsApi = mande(url);
  const response = await surahsApi.get();
  surahAyas.value = response as AyaInfo[];
};
</script>

<style scoped>
.surah-view {
  max-width: 1200px;
  margin: 0 auto;
}

.surah-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.surah-name {
  font-size: 2rem;
  font-weight: bold;
  color: #4caf50;
  margin: 0;
}

.surah-info {
  margin: 0.5rem 0 0;
  color: var(--app-text, #666);
}

.dark-mode .surah-info {
  color: #999;
}

.surah-meta {
  font-size: 0.875rem;
  opacity: 0.8;
}

.ayas-list {
  text-align: right;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}

.loading-state p {
  color: #666;
}

.dark-mode .loading-state p {
  color: #999;
}

.ar {
  direction: rtl;
  text-align: right;
}
</style>
