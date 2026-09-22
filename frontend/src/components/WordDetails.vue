<template>
  <div class="word-details" v-if="token">
    <div class="word-details-head">
      <span class="word-details-arabic ar">{{ token.text }}</span>
      <span class="word-details-pos">{{ posLabel }}</span>
    </div>
    <div class="word-details-glosses" v-if="glossEntries.length">
      <div v-for="[language, gloss] in glossEntries" :key="language" class="word-details-gloss">
        <span class="word-details-label">{{ language }}</span>
        <span>{{ gloss }}</span>
      </div>
    </div>
    <div class="word-details-links">
      <router-link v-if="token.lemma" :to="{ name: 'lemma_view', params: { lemma: token.lemma } }" class="word-details-link">
        <span class="word-details-label">Lemma</span>
        <span class="ar">{{ token.lemma }}</span>
      </router-link>
      <router-link v-if="token.root" :to="{ name: 'root_view', params: { root: token.root } }" class="word-details-link">
        <span class="word-details-label">Root</span>
        <span class="ar">{{ token.root }}</span>
      </router-link>
    </div>
    <div class="word-details-segments">
      <div v-for="(segment, index) in token.segments" :key="index" class="word-details-segment">
        <span class="ar segment-form">{{ segment.form }}</span>
        <span class="segment-features">{{ segment.tag }} {{ segment.features }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { TokenInfo } from '../type_defs';
import { POS_LABELS } from '../type_defs';

const props = defineProps<{ token: TokenInfo | null }>();

const posLabel = computed(() => (props.token ? POS_LABELS[props.token.tag] || props.token.tag : ''));

const glossEntries = computed(() => (props.token ? Object.entries(props.token.glosses) : []));
</script>

<style scoped>
.word-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 220px;
  max-width: 320px;
}

.word-details-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
}

.word-details-arabic {
  font-size: 1.8rem;
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
}

.word-details-pos {
  font-size: 0.8rem;
  color: var(--p-text-muted-color, #666);
}

.word-details-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--p-text-muted-color, #666);
  margin-right: 0.5rem;
}

.word-details-gloss,
.word-details-link {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.word-details-link {
  color: var(--p-primary-color, #4caf50);
  text-decoration: none;
  font-size: 1.1rem;
}

.word-details-link:hover {
  text-decoration: underline;
}

.word-details-links {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.word-details-segments {
  border-top: 1px solid var(--p-content-border-color, #ddd);
  padding-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.word-details-segment {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.segment-form {
  font-size: 1.1rem;
}

.segment-features {
  color: var(--p-text-muted-color, #666);
  direction: ltr;
  text-align: left;
  word-break: break-all;
}

.ar {
  direction: rtl;
}
</style>
