<style>

.aya-container {
  margin: 16px 0;
  padding: 15px;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.aya-container:hover {
  background-color: rgba(209, 255, 209, 0.3);
}

.arabic-section {
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
}

.arabic-text {
  font-size: 24pt;
  line-height: 2;
  font-family: 'Amiri', 'Traditional Arabic', serif;
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

.translation-item {
  padding: 8px 0;
  margin-bottom: 10px;
}

.translation-label {
  font-size: 10pt;
  color: #666;
  margin-bottom: 4px;
  text-transform: capitalize;
}

.translation-text {
  font-size: 14pt;
  line-height: 1.6;
}

.highlighted-word {
  background-color: #4CAF50 !important;
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
</style>

<template>
  <v-card class="aya-container" elevation="0">
    <!-- Arabic Section at the top -->
    <div class="arabic-section">
      <div class="ar">
        <v-chip class="aya-number-badge" size="small" color="primary">
          <span class="en" v-if="!displaySurahName">{{ ayaNumber }}</span>
          <span v-else>
            <span class="en">{{ ayaNumber }}</span>
            <span class="ar mx-2">{{ surahInfo?.arabic_name }}</span>
          </span>
        </v-chip>
        <div class="arabic-text" v-html="highlightedArabicText"></div>
      </div>
    </div>
    
    <!-- Translations Section below -->
    <div class="translations-section" v-if="translationTexts.length > 0">
      <v-row>
        <v-col 
          v-for="translation in translationTexts" 
          :key="`${translation.language}-${translation.textType}`"
          :cols="translationColumnSize"
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
        </v-col>
      </v-row>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { VCard, VRow, VCol, VChip } from 'vuetify/components';
import type { SurahInfo, AyaInfo } from '../type_defs';
import { useStore } from '../store'

interface AyaViewProps {
  aya: AyaInfo;
  displaySurahName: boolean;
  highlightWord?: string;
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

// Get all translation texts (excluding Arabic)
const translationTexts = computed(() => {
  const translations: Array<{language: string, textType: string, text: string}> = [];
  
  if (props.aya.texts) {
    Object.entries(props.aya.texts).forEach(([language, textTypes]) => {
      if (language !== 'arabic') {
        Object.entries(textTypes).forEach(([textType, text]) => {
          translations.push({
            language,
            textType, 
            text: text as string
          });
        });
      }
    });
  }
  
  return translations;
});

// Compute column size for translations based on their count
const translationColumnSize = computed(() => {
  const count = translationTexts.value.length;
  if (count === 1) return 12; // Full width for single translation
  if (count === 2) return 6;  // Half width for two translations
  if (count === 3) return 4;  // Third width for three translations
  return 6; // For 4+ translations, use half width (2 per row)
});

// Get CSS class for translation language
const getTranslationClass = (language: string) => {
  const langMap: Record<string, string> = {
    'urdu': 'ur',
    'english': 'en', 
    'arabic': 'ar'
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
  
  console.log('Highlighting word:', props.highlightWord, '-> cleaned:', cleanWord);
  console.log('In text (first 100 chars):', arabicText.substring(0, 100));
  console.log('Clean text (first 100 chars):', cleanText.substring(0, 100));
  
  // Find the position of the clean word in the clean text
  const cleanWordIndex = cleanText.indexOf(cleanWord);
  
  if (cleanWordIndex === -1) {
    console.log('Word not found in clean text');
    return arabicText;
  }
  
  console.log('Found clean word at index:', cleanWordIndex);
  
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
    console.log('Could not map positions');
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
  
  const result = beforeWord + '<span class="highlighted-word">' + wordToHighlight + '</span>' + afterWord;
  console.log('Highlighted result:', result);
  
  return result;
});


</script>

