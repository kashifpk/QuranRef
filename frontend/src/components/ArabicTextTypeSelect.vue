<template>
  <div class="arabic-text-select">
    <label class="select-label">Arabic Text Style</label>
    <Select
      v-model="selectedType"
      :options="textTypes"
      placeholder="Select style"
      @change="changeTextType"
      class="w-full"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useStore } from '../store';
import Select from 'primevue/select';

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
watch(
  () => store.arabicTextType,
  (newValue) => {
    selectedType.value = newValue;
  }
);

const changeTextType = () => {
  store.setArabicTextType(selectedType.value);
};
</script>

<style scoped>
.arabic-text-select {
  width: 100%;
}

.select-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--app-text, #666);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dark-mode .select-label {
  color: #999;
}

.w-full {
  width: 100%;
}
</style>
