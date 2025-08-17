<template>
  <v-card flat color="transparent">
    <div class="text-white text-body-2 mb-1">Add Translation</div>
    <v-select
      v-model="selectedTranslation"
      :items="availableTranslationOptions"
      placeholder="Select translation"
      variant="outlined"
      density="compact"
      color="green-darken-3"
      bg-color="white"
      hide-details
      persistent-placeholder
      @update:model-value="addTranslation"
      clearable
    />

    <v-list v-if="selectedTranslations.length > 0" class="mt-2" density="compact">
      <v-list-item
        v-for="(tr, index) in selectedTranslations"
        :key="`selected-${tr[0]}-${tr[1]}`"
        class="selected-translation"
      >
        <template v-slot:prepend>
          <v-icon icon="mdi-translate" color="green-lighten-5" />
        </template>
        
        <v-list-item-title class="text-white">
          {{ tr[0] }}-{{ tr[1] }}
        </v-list-item-title>

        <template v-slot:append>
          <v-btn
            icon="mdi-close"
            size="small"
            color="red"
            variant="text"
            @click="removeTranslation(index)"
          />
        </template>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useStore } from '../store';
import { VCard, VSelect, VList, VListItem, VListItemTitle, VBtn, VIcon } from 'vuetify/components';

const store = useStore();
const selectedTranslation = ref('');
const selectedTranslations = computed(() => store.selectedTranslations);

// Computed property to create option objects for v-select
const availableTranslationOptions = computed(() => {
  return store.availableTranslations
    .filter(tr => {
      return !store.selectedTranslations.some(
        selectedTr => selectedTr[0] === tr[0] && selectedTr[1] === tr[1]
      );
    })
    .map(tr => ({
      title: `${tr[0]}-${tr[1]}`,
      value: `${tr[0]}-${tr[1]}`
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
.selected-translation {
  background-color: rgba(0, 128, 0, 0.1);
  border-radius: 4px;
  margin-bottom: 4px;
}
</style>