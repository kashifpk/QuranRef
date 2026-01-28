<template>
  <div class="home-view">
    <Card class="hero-card">
      <template #content>
        <div class="ar hero-arabic">وَلَقَدْ يَسَّرْنَا ٱلْقُرْءَانَ لِلذِّكْرِ فَهَلْ مِن مُّدَّكِر</div>
        <div class="hero-translations">
          <p class="ur">
            ہم نے اِس قرآن کو نصیحت کے لیے آسان ذریعہ بنا دیا ہے، پھر کیا ہے کوئی نصیحت قبول کرنے
            والا؟
          </p>
          <p class="en">
            We have made the Qur'an easy to derive lessons from. Is there, then, any who will take
            heed?
          </p>
        </div>
      </template>
    </Card>

    <div class="surah-list-section">
      <surah-list />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import Card from 'primevue/card';
import { useStore } from '../store';
import SurahList from './SurahList.vue';

const store = useStore();

onMounted(async () => {
  console.log('HomeView mounted, loading Surah info...');
  try {
    await store.loadSurahInfo();
    console.log('Surah info loaded, count:', store.surahInfo.length);
  } catch (error) {
    console.error('Failed to load Surah info:', error);
  }
});
</script>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-card {
  margin-bottom: 2rem;
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.05) 0%, rgba(76, 175, 80, 0.1) 100%);
}

.dark-mode .hero-card {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.15) 100%);
}

.hero-arabic {
  font-size: 1.75rem;
  font-weight: bold;
  color: #4caf50;
  margin-bottom: 1rem;
  line-height: 2;
}

.hero-translations {
  color: var(--app-text, #333);
}

.dark-mode .hero-translations {
  color: #e0e0e0;
}

.hero-translations p {
  margin: 0.5rem 0;
  line-height: 1.8;
}

.ur {
  direction: rtl;
  text-align: right;
  font-size: 1.125rem;
}

.en {
  direction: ltr;
  text-align: left;
  font-size: 1rem;
  color: #666;
}

.dark-mode .en {
  color: #999;
}

.surah-list-section {
  margin-top: 1rem;
}

.ar {
  direction: rtl;
  text-align: right;
}
</style>
