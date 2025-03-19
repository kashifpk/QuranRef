<template>
  <div class="panel panel-success col-xs-12 word-ayas-component">
    <div class="panel-heading ar" @click="getAyas">
      <h3 class="panel-title ar">
        <span class="badge en">{{ word.count }}</span>
        &nbsp;&nbsp;&nbsp;
        {{ word.word }}
      </h3>
    </div>
    <div class="panel-body bg-info" v-if="wordAyas.length > 0">
      <div class="row ar" v-for="aya in wordAyas" :key="aya.key">
        <aya-view :aya="aya" :display-surah-name="true"></aya-view>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineProps } from 'vue';
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
      let requestUrl = `${baseUrl}/ayas-by-word/${props.word.word}/arabic,${store.arabicTextType}`;

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

.panel-heading {
  cursor: pointer;
}

.badge {
  background-color: #337ab7;
}
</style>