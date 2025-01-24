<style scoped>

.aya-content {
  flex-direction: row-reverse;
}

.aya-content:hover {
  background-color: rgba(209, 255, 209, 0.5);
}

.surah-en {
  font-size: 11pt;
}

.en-num {
  font-size: 11pt;
  vertical-align: bottom;
  padding-top: 10px;
}

.col-sm-6, col-lg-6, col-lg-4 {
  float: right;
}

.aya-content {
  margin-top: 5px;
  padding: 5px;
}
</style>

<template>
  <v-row class="aya-content">

    <v-col class="p-3 ar" >
      <span class="en float-end ms-4" v-if="!displaySurahName">
        <v-chip>{{ ayaNumber }}</v-chip>
      </span>
      <span class="float-end m-4" v-else>
        <v-chip>
          <span class="en">{{ ayaNumber }}</span>
          &nbsp;&nbsp;&nbsp;
          <span class="ar" style="font-size: 14pt;">{{ surahInfo?.arabic_name }}</span>
        </v-chip>
      </span>
      {{ aya.texts?.arabic?.uthmani }}
    </v-col>
    <v-col v-if="aya.texts.urdu" class="p-3 ur" >
      {{ aya.texts?.urdu?.maududi }}
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { VRow, VCol, VChip } from 'vuetify/components';
import type { SurahInfo, AyaInfo } from '../type_defs';
import { useStore } from '../store'

interface AyaViewProps {
  aya: AyaInfo;
  displaySurahName: boolean;
}

const store = useStore();
const props = defineProps<AyaViewProps>();
const surahInfo = ref<SurahInfo>();

// const arabicDigits = {
//   '0': '٠',
//   '1': '١',
//   '2': '٢',
//   '3': '٣',
//   '4': '٤',
//   '5': '٥',
//   '6': '٦',
//   '7': '٧',
//   '8': '٨',
//   '9': '٩'
// }

onMounted(() => {
  surahInfo.value = store.surahInfo[parseInt(props.aya.aya_key.split(':')[0]) - 1];
});

// const surahNumber = computed(() => {
//   return props.aya.aya_key.split(':')[0];
// });

const ayaNumber = computed(() => {
  return props.aya.aya_key.split(':')[1];
});

// const colSize = computed(() => {
//   return 'col-xs-12 col-md-6 col-lg-4';
// });


</script>

