<template>
  <v-text-field
    v-model="searchTerm"
    label="Search"
    append-inner-icon="mdi-magnify"
    variant="outlined"
    density="comfortable"
    single-line
    hide-details
    color="green"
    bg-color="white"
    @click:append-inner="doSearch"
    @keyup.enter="doSearch"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { VTextField } from 'vuetify/components';

const router = useRouter();
const searchTerm = ref('');

const doSearch = () => {
  if (searchTerm.value.trim()) {
    router.push({ name: 'search', params: { search_term: searchTerm.value } });
  }
};
</script>