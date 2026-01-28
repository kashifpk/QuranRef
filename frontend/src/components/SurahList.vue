<template>
  <div class="surah-list">
    <DataTable
      v-if="store.surahInfo && store.surahInfo.length > 0"
      :value="store.surahInfo"
      :loading="store.surahInfoLoading"
      sortMode="single"
      removableSort
      :rowHover="true"
      selectionMode="single"
      @rowSelect="onRowSelect"
      responsiveLayout="scroll"
      class="surah-table"
    >
      <Column field="surah_number" header="SNo." sortable style="width: 80px" />
      <Column field="english_name" header="Surah Name" sortable />
      <Column
        field="translated_name"
        header="Translated Name (EN)"
        sortable
        class="hide-on-mobile"
      />
      <Column field="total_ayas" header="Ayas" sortable style="width: 80px" />
      <Column
        field="rukus"
        header="Rukus"
        sortable
        style="width: 80px"
        class="hide-on-small"
      />
      <Column class="hide-on-small" header="Nuzool" sortable style="width: 140px">
        <template #body="{ data }">
          {{ data.nuzool_order }} ({{ data.nuzool_location }})
        </template>
      </Column>
      <Column field="arabic_name" header="Arabic Name" style="text-align: right">
        <template #body="{ data }">
          <span class="ar" style="text-align: right; display: block">{{ data.arabic_name }}</span>
        </template>
      </Column>
    </DataTable>

    <div v-else-if="store.surahInfoLoading" class="loading-state">
      <ProgressSpinner strokeWidth="4" />
      <p>Loading Surahs...</p>
    </div>

    <Message v-else severity="info" :closable="false">
      No Surahs found
    </Message>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from '../store';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';

const store = useStore();
const router = useRouter();

onMounted(() => {
  console.log('SurahList mounted, surahInfo count:', store.surahInfo.length);
});

watch(
  () => store.surahInfo,
  (newValue) => {
    console.log('SurahList: surahInfo changed, new count:', newValue ? newValue.length : 0);
  },
  { deep: true }
);

const onRowSelect = (event: { data: { surah_number: number } }) => {
  router.push({ name: 'surah_view', params: { surah_number: event.data.surah_number.toString() } });
};
</script>

<style scoped>
.surah-list {
  width: 100%;
}

.surah-table {
  cursor: pointer;
}

.surah-table :deep(.p-datatable-tbody > tr) {
  cursor: pointer;
  transition: background-color 0.2s;
}

.surah-table :deep(.p-datatable-tbody > tr:hover) {
  background: rgba(76, 175, 80, 0.08) !important;
}

.surah-table :deep(.p-datatable-header) {
  background: transparent;
  border: none;
}

.surah-table :deep(.p-datatable-thead > tr > th) {
  background: #f8f9fa;
  font-weight: 600;
  color: #1B5E20;
}

.dark-mode .surah-table :deep(.p-datatable-thead > tr > th) {
  background: #2d2d2d;
  color: #81C784;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}

.loading-state p {
  color: #666;
}

/* Responsive column hiding */
@media (max-width: 960px) {
  .surah-table :deep(.hide-on-mobile) {
    display: none !important;
  }
}

@media (max-width: 640px) {
  .surah-table :deep(.hide-on-small) {
    display: none !important;
  }
}
</style>
