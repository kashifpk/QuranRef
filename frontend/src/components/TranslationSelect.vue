<template>
  <div class="translation-select">
    <div class="form-group sidebar-form">
      <select class="form-control" size="1" v-model="selectedTranslation"
              placeholder="Select translation"
              @change="addTranslation">
        <option v-for="tr in availableTranslations" :key="`${tr[0]}-${tr[1]}`">{{ tr[0] }}-{{ tr[1] }}</option>
      </select>
    </div>

    <div class="row selected-translation" v-for="(tr, index) in selectedTranslations" :key="`selected-${tr[0]}-${tr[1]}`">
      <div class="col-xs-9" style="padding-top: 8px;">
        <span class="page">{{ tr[0] }}-{{ tr[1] }}</span>
      </div>
      <div class="col-xs-2">
        <button class="btn btn-danger" @click="removeTranslation(index)">
          <i class="fa fa-remove"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useStore } from '../store';

const store = useStore();
const selectedTranslation = ref('');
const selectedTranslations = computed(() => store.selectedTranslations);

// Computed property to filter out already selected translations
const availableTranslations = computed(() => {
  return store.availableTranslations.filter(tr => {
    return !store.selectedTranslations.some(
      selectedTr => selectedTr[0] === tr[0] && selectedTr[1] === tr[1]
    );
  });
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
.sidebar-form {
  border: 0px;
  margin: 10px 10px
}

select {
  border-radius: 3px;
  border: 1px solid #00d600;
}

.translation-select {
  text-align: left;
  color: #fff;
}

select, .btn {
  box-shadow: none;
  border: 1px solid transparent;
  height: 35px;
  -webkit-transition: all .3s ease-in-out;
  -o-transition: all .3s ease-in-out;
  transition: all .3s ease-in-out
}

select {
  color: #666;
  border-top-left-radius: 2px;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 2px
}

.btn {
  border-top-left-radius: 0;
  border-top-right-radius: 2px;
  border-bottom-right-radius: 2px;
  border-bottom-left-radius: 0
}

.selected-translation {
  margin: 10px 10px;
  background-color: #006800;
}
</style>