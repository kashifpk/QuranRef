<template>
  <v-card class="word-ayas-component mb-4" elevation="2">
    <v-card-title 
      class="ar cursor-pointer bg-success text-white" 
      @click="getAyas"
    >
      <v-chip class="me-3" color="white" text-color="success">
        {{ word.count }}
      </v-chip>
      {{ word.word }}
    </v-card-title>
    
    <v-card-text 
      v-if="wordAyas.length > 0" 
      class="pa-0 bg-surface"
    >
      <div v-for="aya in wordAyas" :key="aya.aya_key" class="ar">
        <aya-view 
          :aya="aya" 
          :display-surah-name="true"
          :highlight-word="word.word"
        ></aya-view>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch, defineProps } from 'vue';
import { VCard, VCardTitle, VCardText, VChip } from 'vuetify/components';
import { useStore } from '../store';
import AyaView from './AyaView.vue';

const props = defineProps({
  word: {
    type: Object,
    required: true
  }
});

const store = useStore();
const wordAyas = ref<any[]>([]);

// Watch for changes in arabicTextType or selectedTranslations
watch(() => store.arabicTextType, () => {
  wordAyas.value = [];
});

watch(() => store.selectedTranslations, () => {
  wordAyas.value = [];
}, { deep: true });

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
  }
};
</script>

<style scoped>
.word-ayas-component {
  margin-bottom: 15px;
}

.cursor-pointer {
  cursor: pointer;
}

.ar {
  direction: rtl;
  text-align: right;
}
</style>