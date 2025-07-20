<style scoped>
</style>

<template>
  <v-container>
    <v-row>
      <v-col>

        <div class="ar text-success" style="font-size: larger; font-weight: bold;">
              وَلَقَدْ يَسَّرْنَا ٱلْقُرْءَانَ لِلذِّكْرِ فَهَلْ مِن مُّدَّكِر
        </div>
        <div class="ur text-primary d-none d-md-block">
          ہم نے اِس قرآن کو نصیحت کے لیے آسان ذریعہ بنا دیا ہے، پھر کیا ہے کوئی نصیحت قبول کرنے والا؟
        <br />
        We have made the Qur'an easy to derive lessons from. Is there, then, any who will take heed?
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <surah-list></surah-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
  import { VContainer, VRow, VCol } from 'vuetify/components';
  import { onMounted } from 'vue'
  import { useStore } from '../store'
  import SurahList from './SurahList.vue';

  const store = useStore()

  onMounted(async () => {
    console.log('HomeView mounted, loading Surah info...')
    try {
      await store.loadSurahInfo()
      console.log('Surah info loaded, count:', store.surahInfo.length)
    } catch (error) {
      console.error('Failed to load Surah info:', error)
    }
  })

</script>