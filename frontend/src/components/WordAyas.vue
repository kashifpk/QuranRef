<template>
  <Card class="word-ayas-component">
    <template #header>
      <div class="word-header ar" @click="getAyas">
        <Tag severity="contrast" class="word-count">{{ word.count }}</Tag>
        <span class="word-text">{{ word.word }}</span>
        <i class="pi pi-chevron-down expand-icon" :class="{ rotated: wordAyas.length > 0 }"></i>
      </div>
    </template>

    <template #content v-if="wordAyas.length > 0">
      <div class="ayas-list">
        <div v-for="aya in wordAyas" :key="aya.aya_key" class="ar">
          <aya-view :aya="aya" :display-surah-name="true" :highlight-word="word.word" />
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import Card from 'primevue/card';
import Tag from 'primevue/tag';
import { useStore } from '../store';
import AyaView from './AyaView.vue';

const props = defineProps({
  word: {
    type: Object,
    required: true,
  },
});

const store = useStore();
const wordAyas = ref<any[]>([]);

// Watch for changes in arabicTextType or selectedTranslations
watch(
  () => store.arabicTextType,
  () => {
    wordAyas.value = [];
  }
);

watch(
  () => store.selectedTranslations,
  () => {
    wordAyas.value = [];
  },
  { deep: true }
);

const getAyas = async () => {
  if (wordAyas.value.length === 0) {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      let requestUrl = `${baseUrl}/ayas-by-word/${props.word.word}/arabic:${store.arabicTextType}`;

      if (store.selectedTranslationsString) {
        requestUrl += `_${store.selectedTranslationsString}`;
      }

      const response = await fetch(requestUrl);
      const data = await response.json();
      wordAyas.value = data;
    } catch (error) {
      console.error('Error fetching ayas:', error);
    }
  } else {
    // Toggle collapse
    wordAyas.value = [];
  }
};
</script>

<style scoped>
.word-ayas-component {
  margin-bottom: 1rem;
}

.word-ayas-component :deep(.p-card-header) {
  padding: 0;
}

.word-ayas-component :deep(.p-card-body) {
  padding: 0;
}

.word-ayas-component :deep(.p-card-content) {
  padding: 0;
}

.word-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
  color: white;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 1.5rem;
  font-weight: bold;
}

.word-header:hover {
  background: linear-gradient(135deg, #43a047 0%, #4caf50 100%);
}

.word-count {
  font-size: 0.875rem;
}

.word-text {
  flex: 1;
}

.expand-icon {
  transition: transform 0.2s;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.ayas-list {
  padding: 1rem;
  background: var(--app-surface, #fff);
}

.dark-mode .ayas-list {
  background: var(--app-surface, #1e1e1e);
}

.ar {
  direction: rtl;
  text-align: right;
}
</style>
