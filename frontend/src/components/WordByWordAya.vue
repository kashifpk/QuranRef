<template>
  <div class="wbw-row ar" dir="rtl">
    <button
      v-for="token in tokens"
      :key="token.position"
      type="button"
      class="wbw-word"
      :class="{ selected: token.position === selectedPosition }"
      @click="$emit('select', token, $event)"
    >
      <span class="wbw-arabic">{{ token.text }}</span>
      <span class="wbw-translit" v-if="showTransliteration && token.glosses.transliteration">{{ token.glosses.transliteration }}</span>
      <span class="wbw-gloss" v-if="token.glosses[glossLanguage]">{{ token.glosses[glossLanguage] }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import type { TokenInfo } from '../type_defs';

defineProps<{
  tokens: TokenInfo[];
  glossLanguage: string;
  showTransliteration?: boolean;
  selectedPosition?: number | null;
}>();

defineEmits<{
  select: [token: TokenInfo, event: MouseEvent];
}>();
</script>

<style scoped>
.wbw-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.5rem;
  direction: rtl;
  justify-content: flex-start;
}

.wbw-word {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid transparent;
  border-radius: 6px;
  background: none;
  cursor: pointer;
  color: inherit;
  font: inherit;
}

.wbw-word:hover,
.wbw-word.selected {
  border-color: var(--p-primary-color, #4caf50);
  background: rgba(76, 175, 80, 0.08);
}

.wbw-arabic {
  font-size: 24pt;
  line-height: 1.6;
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
  direction: rtl;
}

.wbw-translit {
  font-size: 0.75rem;
  font-style: italic;
  color: var(--p-text-muted-color, #666);
  direction: ltr;
}

.wbw-gloss {
  font-size: 0.8rem;
  color: var(--p-text-muted-color, #666);
  direction: ltr;
  text-align: center;
  max-width: 9rem;
}
</style>
