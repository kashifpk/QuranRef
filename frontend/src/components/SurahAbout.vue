<template>
  <Card v-if="info" class="surah-about">
    <template #content>
      <div class="about-head">
        <button type="button" class="about-toggle" @click="open = !open">
          <i :class="open ? 'pi pi-chevron-down' : 'pi pi-chevron-right'"></i>
          <span>About this surah</span>
        </button>
        <div v-if="open && info.available.length > 1" class="about-languages">
          <Button
            v-for="lang in info.available"
            :key="lang"
            :label="languageLabel(lang)"
            size="small"
            :text="lang !== info.language"
            :outlined="lang === info.language"
            @click="load(lang)"
          />
        </div>
      </div>
      <div v-show="open" class="about-text" :class="{ ur: info.language === 'urdu' }" v-html="info.text"></div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import type { SurahInfoText } from '../type_defs';

const props = defineProps<{ surahNumber: number }>();
const info = ref<SurahInfoText | null>(null);
const open = ref(false);

function languageLabel(lang: string) {
  return { english: 'English', urdu: 'اردو' }[lang] || lang;
}

async function load(language = 'english') {
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const resp = await fetch(`${baseUrl}/surah-info/${props.surahNumber}?language=${language}`);
    info.value = resp.ok ? await resp.json() : null;
  } catch (error) {
    console.error('Failed to load surah info:', error);
    info.value = null;
  }
}

watch(() => props.surahNumber, () => { open.value = false; load(); }, { immediate: true });
</script>

<style scoped>
.surah-about {
  margin-bottom: 1rem;
}

.about-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.about-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font: inherit;
  color: inherit;
  padding: 0;
}

.about-text {
  margin-top: 0.75rem;
  line-height: 1.7;
}

.about-text :deep(h2) {
  font-size: 1.1rem;
  margin: 1rem 0 0.25rem;
}

.about-text.ur {
  direction: rtl;
  text-align: right;
  font-size: 1.15rem;
}
</style>
