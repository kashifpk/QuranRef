<style scoped>
tr:hover {
  cursor: pointer;
}
</style>

<template>

  <v-table density="comfortable" hover >
    <thead>
      <tr class="table-heading">
        <th>SNo.</th>
        <th>Surah Name</th>
        <th class="hidden-sm hidden-xs">Translated Name (EN)</th>
        <th>Ayas</th>
        <th class="hidden-xs">Rukus</th>
        <th class="hidden-xs">Nuzool</th>
        <th>Arabic Name</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="surah in store.surahInfo" @click="goToSurah(surah.surah_number)" >
        <td>
          {{ surah.surah_number }}
        </td>
        <td>
          {{ surah.english_name }}
        </td>
        <td class="hidden-xs hidden-sm">
          {{ surah.translated_name }}
        </td>
        <td>{{ surah.total_ayas }}</td>
        <td class="hidden-xs">{{ surah.rukus }}</td>
        <td class="hidden-xs">{{ surah.nuzool_order }} ({{ surah.nuzool_location }})</td>
        <td class="ar" style="text-align: right">
          {{ surah.arabic_name }}
        </td>
      </tr>
    </tbody>
  </v-table>
</template>

<script setup lang="ts">
import { VTable } from 'vuetify/components';
import { useRouter } from 'vue-router';
import { useStore } from '../store'

const store = useStore()
const router = useRouter()

const goToSurah = (surahNumber: number) => {
  router.push({ name: 'surah_view', params: { surah_number: surahNumber.toString() } })
}
</script>

