<template>
  <div>
    <div class="text-white text-body-2 mb-1">Arabic Text Style</div>
    <v-select
      v-model="selectedType"
      :items="textTypes"
      placeholder="Select style"
      variant="outlined"
      density="compact"
      color="green-darken-3"
      bg-color="white"
      hide-details
      persistent-placeholder
      @update:model-value="changeTextType"
    />
  </div>
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