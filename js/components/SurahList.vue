<style scoped>
/* Your component styles here */
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
      <tr v-for="surah in store.surahInfo" >
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

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import { VTable } from 'vuetify/components';

import { useStore } from '../store'
const store = useStore()

</script>

