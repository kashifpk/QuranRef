<style scoped>
tr:hover {
  cursor: pointer;
}
</style>

<template>

  <div>
    <v-table v-if="store.surahInfo && store.surahInfo.length > 0" density="comfortable" hover >
      <thead>
        <tr class="table-heading">
          <th>SNo.</th>
          <th>Surah Name</th>
          <th class="d-none d-md-table-cell">Translated Name (EN)</th>
          <th>Ayas</th>
          <th class="d-none d-sm-table-cell">Rukus</th>
          <th class="d-none d-sm-table-cell">Nuzool</th>
          <th>Arabic Name</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="surah in store.surahInfo" @click="goToSurah(surah.surah_number)" :key="surah.surah_number">
          <td>
            {{ surah.surah_number }}
          </td>
          <td>
            {{ surah.english_name }}
          </td>
          <td class="d-none d-md-table-cell">
            {{ surah.translated_name }}
          </td>
          <td>{{ surah.total_ayas }}</td>
          <td class="d-none d-sm-table-cell">{{ surah.rukus }}</td>
          <td class="d-none d-sm-table-cell">{{ surah.nuzool_order }} ({{ surah.nuzool_location }})</td>
          <td class="ar" style="text-align: right">
            {{ surah.arabic_name }}
          </td>
        </tr>
      </tbody>
    </v-table>
    <div v-else-if="store.surahInfoLoading">Loading Surahs...</div>
    <div v-else>No Surahs found</div>
  </div>
</template>

<script setup lang="ts">
import { VTable } from 'vuetify/components';
import { useRouter } from 'vue-router';
import { onMounted, watch } from 'vue';
import { useStore } from '../store'

const store = useStore()
const router = useRouter()

onMounted(() => {
  console.log('SurahList mounted, surahInfo count:', store.surahInfo.length)
})

watch(() => store.surahInfo, (newValue) => {
  console.log('SurahList: surahInfo changed, new count:', newValue ? newValue.length : 0)
}, { deep: true })

const goToSurah = (surahNumber: number) => {
  router.push({ name: 'surah_view', params: { surah_number: surahNumber.toString() } })
}
</script>

