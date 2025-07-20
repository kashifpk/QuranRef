<template>
  <v-select
    v-model="selectedType"
    :items="textTypes"
    label="Arabic Text Style"
    variant="outlined"
    density="comfortable"
    color="green"
    bg-color="white"
    hide-details
    @update:model-value="changeTextType"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useStore } from '../store';
import { VSelect } from 'vuetify/components';

const store = useStore();
const selectedType = ref(store.arabicTextType);
const textTypes = ref<string[]>([]);

onMounted(async () => {
  // Load text types if they're not already loaded
  if (store.availableTextTypes.length === 0) {
    await store.loadTextTypes();
  }
  textTypes.value = store.availableTextTypes;
  selectedType.value = store.arabicTextType;
});

// Watch for changes in the store's arabicTextType
watch(() => store.arabicTextType, (newValue) => {
  selectedType.value = newValue;
});

const changeTextType = () => {
  store.setArabicTextType(selectedType.value);
};
</script>