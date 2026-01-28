<template>
  <div class="translation-select">
    <label class="select-label">Add Translation</label>
    <Select
      v-model="selectedTranslation"
      :options="availableTranslationOptions"
      optionLabel="title"
      optionValue="value"
      placeholder="Select translation"
      @change="addTranslation"
      showClear
      class="w-full"
    />

    <div v-if="selectedTranslations.length > 0" class="selected-translations">
      <div
        v-for="(tr, index) in selectedTranslations"
        :key="`selected-${tr[0]}-${tr[1]}`"
        class="selected-item"
      >
        <i class="pi pi-language"></i>
        <span class="translation-name">{{ tr[0] }}-{{ tr[1] }}</span>
        <Button
          icon="pi pi-times"
          severity="danger"
          text
          rounded
          size="small"
          @click="removeTranslation(index)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useStore } from '../store';
import Select from 'primevue/select';
import Button from 'primevue/button';

const store = useStore();
const selectedTranslation = ref('');
const selectedTranslations = computed(() => store.selectedTranslations);

// Computed property to create option objects for select
const availableTranslationOptions = computed(() => {
  return store.availableTranslations
    .filter((tr) => {
      return !store.selectedTranslations.some(
        (selectedTr) => selectedTr[0] === tr[0] && selectedTr[1] === tr[1]
      );
    })
    .map((tr) => ({
      title: `${tr[0]}-${tr[1]}`,
      value: `${tr[0]}-${tr[1]}`,
    }));
});

onMounted(async () => {
  // Load text types if they're not already loaded
  if (store.availableTranslations.length === 0) {
    await store.loadTextTypes();
  }
});

const addTranslation = () => {
  if (!selectedTranslation.value) {
    return;
  }

  const parts = selectedTranslation.value.split('-');
  if (parts.length === 2) {
    store.addTranslation([parts[0], parts[1]]);
    selectedTranslation.value = '';
  }
};

const removeTranslation = (index: number) => {
  store.removeTranslation(index);
};
</script>

<style scoped>
.translation-select {
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

.selected-translations {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selected-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.selected-item i {
  color: #4caf50;
}

.translation-name {
  flex: 1;
  color: var(--app-text, #333);
}

.dark-mode .translation-name {
  color: #e0e0e0;
}
</style>
