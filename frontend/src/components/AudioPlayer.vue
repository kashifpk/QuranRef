<template>
  <div v-if="store.audioCurrent" class="audio-player">
    <div class="audio-info">
      <i class="pi pi-volume-up"></i>
      <span class="audio-key en">{{ store.audioCurrent }}</span>
      <span v-if="surahName" class="audio-surah">{{ surahName }}</span>
    </div>
    <div class="audio-controls">
      <Button icon="pi pi-step-backward" text rounded size="small" :disabled="!hasPrev" v-tooltip.top="'Previous aya'" @click="store.prevAya()" />
      <Button :icon="store.audioPlaying ? 'pi pi-pause' : 'pi pi-play'" rounded size="small" :aria-label="store.audioPlaying ? 'Pause' : 'Play'" @click="store.toggleAya(store.audioCurrent!)" />
      <Button icon="pi pi-step-forward" text rounded size="small" :disabled="!hasNext" v-tooltip.top="'Next aya'" @click="store.nextAya()" />
      <Button icon="pi pi-times" text rounded size="small" v-tooltip.top="'Stop'" @click="store.stopAudio()" />
    </div>
    <div class="audio-options">
      <Select
        v-model="store.reciter"
        :options="RECITERS"
        optionLabel="name"
        optionValue="id"
        size="small"
        class="reciter-select"
      />
      <label class="continuous-option">
        <Checkbox v-model="store.audioContinuous" :binary="true" inputId="audio-continuous" />
        <span>Continue to the next aya</span>
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Select from 'primevue/select';
import { RECITERS } from '../audio';
import { useStore } from '../store';

const store = useStore();

const surahName = computed(() => {
  if (!store.audioCurrent) return '';
  const surah = store.surahInfo[Number(store.audioCurrent.split(':')[0]) - 1];
  return surah ? surah.english_name : '';
});

const position = computed(() => store.audioPlaylist.indexOf(store.audioCurrent ?? ''));
const hasPrev = computed(() => position.value > 0);
const hasNext = computed(() => position.value !== -1 && position.value < store.audioPlaylist.length - 1);
</script>

<style scoped>
.audio-player {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 900;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 0.5rem 1rem;
  background: var(--p-content-background, #fff);
  border-top: 1px solid var(--p-content-border-color, #ddd);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.08);
}

.audio-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--p-primary-color);
}

.audio-key {
  font-weight: 600;
}

.audio-surah {
  color: var(--p-text-muted-color);
  font-size: 0.875rem;
}

.audio-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.audio-options {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.reciter-select {
  min-width: 14rem;
}

.continuous-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--p-text-muted-color);
}

.en {
  direction: ltr;
}
</style>
