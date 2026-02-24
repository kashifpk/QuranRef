<template>
  <Card class="aya-container">
    <template #content>
      <!-- Bookmark indicators -->
      <div class="bookmark-indicators" v-if="store.currentUser">
        <i
          v-if="store.isReadingBookmark(props.aya.aya_key)"
          class="pi pi-bookmark-fill reading-indicator"
          v-tooltip.top="'Reading position'"
        ></i>
        <i
          v-if="ayaNotes.length > 0"
          class="pi pi-file-edit note-indicator"
          v-tooltip.top="ayaNotes.length + ' note' + (ayaNotes.length > 1 ? 's' : '')"
        ></i>
      </div>

      <!-- Actions button (top-right, hover only) -->
      <div class="aya-actions" v-if="store.currentUser">
        <Button
          icon="pi pi-ellipsis-v"
          text
          rounded
          size="small"
          class="aya-actions-btn"
          @click="togglePopover"
        />
        <Popover ref="popoverRef">
          <div class="aya-popover-menu">
            <button
              class="popover-item"
              @click="handleToggleReading"
            >
              <i :class="store.isReadingBookmark(props.aya.aya_key) ? 'pi pi-bookmark-fill' : 'pi pi-bookmark'"></i>
              <span>{{ store.isReadingBookmark(props.aya.aya_key) ? 'Remove reading position' : 'Set as reading position' }}</span>
            </button>
            <button
              class="popover-item"
              @click="showNoteDialog = true; popoverRef?.hide()"
            >
              <i class="pi pi-file-edit"></i>
              <span>Add note bookmark</span>
            </button>
          </div>
        </Popover>
      </div>

      <!-- Add Note Dialog -->
      <Dialog
        v-model:visible="showNoteDialog"
        header="Add Note Bookmark"
        :modal="true"
        :style="{ width: '400px' }"
      >
        <div class="note-dialog-content">
          <p class="note-aya-ref">{{ props.aya.aya_key }} — {{ surahInfo?.english_name }}</p>
          <Textarea
            v-model="noteText"
            rows="4"
            class="note-textarea"
            placeholder="Write your note..."
            autofocus
          />
        </div>
        <template #footer>
          <Button label="Cancel" text @click="showNoteDialog = false" />
          <Button label="Save" @click="handleAddNote" :disabled="!noteText.trim()" />
        </template>
      </Dialog>

      <!-- Arabic Section at the top -->
      <div class="arabic-section">
        <div class="ar">
          <Tag class="aya-number-badge" severity="success">
            <span class="en" v-if="!displaySurahName">{{ ayaNumber }}</span>
            <span v-else>
              <span class="en">{{ ayaNumber }}</span>
              <span class="ar mx-2">{{ surahInfo?.arabic_name }}</span>
            </span>
          </Tag>
          <div class="arabic-text" v-html="highlightedArabicText"></div>
        </div>
      </div>

      <!-- Translations Section below -->
      <div class="translations-section" v-if="translationTexts.length > 0">
        <div class="translations-grid" :class="translationGridClass">
          <div
            v-for="translation in translationTexts"
            :key="`${translation.language}-${translation.textType}`"
            class="translation-item"
          >
            <div class="translation-label">
              {{ translation.language }} - {{ translation.textType }}
            </div>
            <div
              class="translation-text"
              :class="getTranslationClass(translation.language)"
            >
              {{ translation.text }}
            </div>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import Card from 'primevue/card';
import Tag from 'primevue/tag';
import Button from 'primevue/button';
import Popover from 'primevue/popover';
import Dialog from 'primevue/dialog';
import Textarea from 'primevue/textarea';
import type { SurahInfo, AyaInfo } from '../type_defs';
import { useStore } from '../store';

interface AyaViewProps {
  aya: AyaInfo;
  displaySurahName: boolean;
  highlightWord?: string;
}

const store = useStore();
const props = defineProps<AyaViewProps>();
const surahInfo = ref<SurahInfo>();
const popoverRef = ref();
const showNoteDialog = ref(false);
const noteText = ref('');

const ayaNotes = computed(() => store.getNotesForAya(props.aya.aya_key));

const togglePopover = (event: Event) => {
  popoverRef.value?.toggle(event);
};

const handleToggleReading = async () => {
  popoverRef.value?.hide();
  if (store.isReadingBookmark(props.aya.aya_key)) {
    await store.deleteReadingBookmark();
  } else {
    await store.setReadingBookmark(props.aya.aya_key);
  }
};

const handleAddNote = async () => {
  if (noteText.value.trim()) {
    await store.addNoteBookmark(props.aya.aya_key, noteText.value.trim());
    noteText.value = '';
    showNoteDialog.value = false;
  }
};

onMounted(() => {
  surahInfo.value = store.surahInfo[parseInt(props.aya.aya_key.split(':')[0]) - 1];
});

const ayaNumber = computed(() => {
  return props.aya.aya_key.split(':')[1];
});

// Get all translation texts (excluding Arabic)
const translationTexts = computed(() => {
  const translations: Array<{ language: string; textType: string; text: string }> = [];

  if (props.aya.texts) {
    Object.entries(props.aya.texts).forEach(([language, textTypes]) => {
      if (language !== 'arabic') {
        Object.entries(textTypes).forEach(([textType, text]) => {
          translations.push({
            language,
            textType,
            text: text as string,
          });
        });
      }
    });
  }

  return translations;
});

// Compute grid class based on translation count
const translationGridClass = computed(() => {
  const count = translationTexts.value.length;
  if (count === 1) return 'cols-1';
  if (count === 2) return 'cols-2';
  if (count === 3) return 'cols-3';
  return 'cols-2';
});

// Get CSS class for translation language
const getTranslationClass = (language: string) => {
  const langMap: Record<string, string> = {
    urdu: 'ur',
    english: 'en',
    arabic: 'ar',
  };
  return langMap[language.toLowerCase()] || 'en';
};

// Highlight the selected word in Arabic text
const highlightedArabicText = computed(() => {
  const arabicText = props.aya.texts?.arabic?.[store.arabicTextType] || '';

  if (!props.highlightWord || !arabicText) {
    return arabicText;
  }

  // Arabic diacritics (harakat) - same as used in old project
  const aarab = ['ِ', 'ْ', 'َ', 'ُ', 'ّ', 'ٍ', 'ً', 'ٌ'];

  // Clean the search word (remove diacritics)
  let cleanWord = '';
  for (const ch of props.highlightWord) {
    if (!aarab.includes(ch)) {
      cleanWord += ch;
    }
  }

  // Clean the text (remove diacritics)
  let cleanText = '';
  for (const ch of arabicText) {
    if (!aarab.includes(ch)) {
      cleanText += ch;
    }
  }

  // Find the position of the clean word in the clean text
  const cleanWordIndex = cleanText.indexOf(cleanWord);

  if (cleanWordIndex === -1) {
    return arabicText;
  }

  // Now we need to find the corresponding position in the original text
  // We'll map clean text positions to original text positions
  const cleanToOriginalMap: number[] = [];

  for (let i = 0; i < arabicText.length; i++) {
    if (!aarab.includes(arabicText[i])) {
      cleanToOriginalMap.push(i);
    }
  }

  // Find start and end positions in original text
  const originalStart = cleanToOriginalMap[cleanWordIndex];
  const originalEnd = cleanToOriginalMap[cleanWordIndex + cleanWord.length - 1];

  if (originalStart === undefined || originalEnd === undefined) {
    return arabicText;
  }

  // Find the actual end of the word including any trailing diacritics
  let actualEnd = originalEnd + 1;
  while (actualEnd < arabicText.length && aarab.includes(arabicText[actualEnd])) {
    actualEnd++;
  }

  // Highlight the word
  const beforeWord = arabicText.substring(0, originalStart);
  const wordToHighlight = arabicText.substring(originalStart, actualEnd);
  const afterWord = arabicText.substring(actualEnd);

  return beforeWord + '<span class="highlighted-word">' + wordToHighlight + '</span>' + afterWord;
});
</script>

<style>
.aya-container {
  margin: 16px 0;
  border-radius: 8px;
  transition: background-color 0.3s;
  position: relative;
}

.aya-container:hover {
  background-color: rgba(76, 175, 80, 0.05);
}

.aya-container .p-card-body {
  padding: 1rem;
}

.aya-container .p-card-content {
  padding: 0;
  position: relative;
}

/* Bookmark indicators (top-right) */
.bookmark-indicators {
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  gap: 4px;
  z-index: 2;
}

.reading-indicator {
  color: #4CAF50;
  font-size: 1rem;
}

.note-indicator {
  color: #FF9800;
  font-size: 1rem;
}

/* Actions button (top-left, hover only) */
.aya-actions {
  position: absolute;
  top: 0;
  left: 0;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 2;
}

.aya-container:hover .aya-actions {
  opacity: 1;
}

.aya-actions-btn {
  color: var(--p-text-muted-color) !important;
}

/* Popover menu */
.aya-popover-menu {
  display: flex;
  flex-direction: column;
  min-width: 200px;
}

.popover-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--p-text-color);
  border-radius: var(--p-content-border-radius);
  text-align: left;
}

.popover-item:hover {
  background: var(--p-content-hover-background);
}

.popover-item i {
  color: var(--p-primary-color);
  font-size: 1rem;
}

/* Note dialog */
.note-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.note-aya-ref {
  margin: 0;
  color: var(--p-text-muted-color);
  font-size: 0.875rem;
}

.note-textarea {
  width: 100%;
}

.arabic-section {
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
}

.dark-mode .arabic-section {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.arabic-text {
  font-size: 24pt;
  line-height: 2;
  font-family: 'AlQalam', 'Amiri', 'Traditional Arabic', serif;
  direction: rtl;
  text-align: right;
}

.aya-number-badge {
  display: inline-block;
  margin-left: 15px;
  vertical-align: middle;
}

.translations-section {
  padding: 10px 0;
}

.translations-grid {
  display: grid;
  gap: 1rem;
}

.translations-grid.cols-1 {
  grid-template-columns: 1fr;
}

.translations-grid.cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.translations-grid.cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

@media (max-width: 768px) {
  .translations-grid.cols-2,
  .translations-grid.cols-3 {
    grid-template-columns: 1fr;
  }
}

.translation-item {
  padding: 8px 0;
}

.translation-label {
  font-size: 10pt;
  color: #666;
  margin-bottom: 4px;
  text-transform: capitalize;
}

.dark-mode .translation-label {
  color: #999;
}

.translation-text {
  font-size: 14pt;
  line-height: 1.6;
}

.highlighted-word {
  background-color: #4caf50 !important;
  color: white !important;
  padding: 2px 6px !important;
  border-radius: 3px !important;
  font-weight: bold !important;
  display: inline !important;
}

.ar {
  direction: rtl;
  text-align: right;
}

.ur {
  direction: rtl;
  text-align: right;
}

.en {
  direction: ltr;
  text-align: left;
}

.mx-2 {
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}
</style>
