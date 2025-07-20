<style>

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

.highlighted-word {
  background-color: #4CAF50 !important;
  color: white !important;
  padding: 1px 3px !important;
  border-radius: 3px !important;
  font-weight: bold !important;
  display: inline !important;
}

.arabic-text .highlighted-word {
  background-color: #4CAF50 !important;
  color: white !important;
  padding: 1px 3px !important;
  border-radius: 3px !important;
  font-weight: bold !important;
  display: inline !important;
}

.arabic-text {
  font-size: 16pt;
  line-height: 1.6;
}

.translation-text {
  font-size: 14pt;
  line-height: 1.5;
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
  <v-row class="aya-content" dir="rtl">
    <!-- Translation texts (rendered first to appear on left in RTL) -->
    <v-col 
      v-for="(translation, index) in translationTexts" 
      :key="`${translation.language}-${translation.textType}`"
      :class="getTranslationClass(translation.language)"
      class="p-3"
      :cols="translationColSize"
    >
      <div class="translation-text">{{ translation.text }}</div>
    </v-col>
    
    <!-- Arabic text (rendered last to appear on right in RTL) -->
    <v-col class="p-3 ar" :cols="arabicColSize">
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
      <div class="arabic-text" v-html="highlightedArabicText"></div>
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

// Compute column sizes based on number of translations
const totalTexts = computed(() => 1 + translationTexts.value.length); // 1 for Arabic + translations
const arabicColSize = computed(() => {
  if (totalTexts.value === 1) return 12;
  if (totalTexts.value === 2) return 6;
  return 4; // For 3 or more texts
});
const translationColSize = computed(() => {
  if (totalTexts.value === 2) return 6;
  return 4; // For 3 or more texts
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
  let originalIndex = 0;
  
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

