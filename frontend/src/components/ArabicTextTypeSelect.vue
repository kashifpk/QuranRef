<template>
  <div class="arabic-text-type-component">
    <div class="form-group">
      <form class="sidebar-form">
        <select class="form-control" size="1" v-model="selectedType" id="arabic_text_type"
                placeholder="Select arabic style..."
                @change="changeTextType">
          <option v-for="tt in textTypes" :key="tt">{{ tt }}</option>
        </select>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useStore } from '../store';

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

<style scoped>
.sidebar-form {
  border: 0px;
  margin: 10px 10px
}

select {
  border-radius: 3px;
  border: 1px solid #00d600;
}
</style>