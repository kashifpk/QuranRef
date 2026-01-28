<template>
  <Dialog
    v-model:visible="visible"
    header="Text Settings"
    :modal="true"
    :style="{ width: '800px', maxWidth: '95vw' }"
    :breakpoints="{ '960px': '95vw' }"
    class="text-settings-dialog"
  >
    <Tabs value="0">
      <TabList>
        <Tab value="0">Arabic Style</Tab>
        <Tab value="1">Translations</Tab>
      </TabList>
      <TabPanels>
        <!-- Arabic Text Style Tab -->
        <TabPanel value="0">
          <div class="arabic-style-section">
            <p class="section-description">
              Select the Arabic text style. Preview shows Bismillah (1:1) in each style.
            </p>

            <div class="style-options">
              <div
                v-for="style in availableStyles"
                :key="style"
                class="style-option"
                :class="{ selected: selectedStyle === style }"
                @click="selectStyle(style)"
              >
                <div class="style-header">
                  <RadioButton
                    :modelValue="selectedStyle"
                    :value="style"
                    :inputId="style"
                    @update:modelValue="selectStyle"
                  />
                  <label :for="style" class="style-name">{{ formatStyleName(style) }}</label>
                </div>
                <div class="bismillah-preview ar">
                  {{ bismillahPreviews[style] || 'Loading...' }}
                </div>
              </div>
            </div>
          </div>
        </TabPanel>

        <!-- Translations Tab -->
        <TabPanel value="1">
          <div class="translations-section">
            <p class="section-description">
              Select translations to display. Choose a language to see available translations.
            </p>

            <div class="translations-layout">
              <!-- Language List -->
              <div class="language-list">
                <div class="list-header">Languages</div>
                <Listbox
                  v-model="selectedLanguage"
                  :options="languages"
                  optionLabel="name"
                  optionValue="code"
                  class="language-listbox"
                  :pt="{ list: { style: 'max-height: 350px' } }"
                >
                  <template #option="{ option }">
                    <div class="language-option">
                      <span>{{ option.name }}</span>
                      <Badge
                        v-if="getSelectedCountForLanguage(option.code) > 0"
                        :value="getSelectedCountForLanguage(option.code)"
                        severity="success"
                      />
                    </div>
                  </template>
                </Listbox>
              </div>

              <!-- Translations for Selected Language -->
              <div class="translator-list">
                <div class="list-header">
                  {{ selectedLanguage ? formatLanguageName(selectedLanguage) : 'Select a language' }}
                </div>
                <div v-if="selectedLanguage" class="translators">
                  <div
                    v-for="translator in getTranslatorsForLanguage(selectedLanguage)"
                    :key="`${selectedLanguage}-${translator}`"
                    class="translator-option"
                  >
                    <Checkbox
                      :modelValue="isTranslationSelected(selectedLanguage, translator)"
                      :binary="true"
                      :inputId="`${selectedLanguage}-${translator}`"
                      @update:modelValue="toggleTranslation(selectedLanguage, translator, $event)"
                    />
                    <label :for="`${selectedLanguage}-${translator}`" class="translator-name">
                      {{ formatTranslatorName(translator) }}
                    </label>
                  </div>
                </div>
                <div v-else class="no-selection">
                  <i class="pi pi-arrow-left"></i>
                  <span>Select a language from the list</span>
                </div>
              </div>
            </div>

            <!-- Selected Translations Summary -->
            <div v-if="store.selectedTranslations.length > 0" class="selected-summary">
              <div class="summary-header">
                <span>Selected Translations ({{ store.selectedTranslations.length }})</span>
                <Button
                  label="Clear All"
                  icon="pi pi-trash"
                  severity="danger"
                  text
                  size="small"
                  @click="clearAllTranslations"
                />
              </div>
              <div class="selected-chips">
                <Chip
                  v-for="(tr, index) in store.selectedTranslations"
                  :key="`chip-${tr[0]}-${tr[1]}`"
                  :label="`${formatLanguageName(tr[0])}: ${formatTranslatorName(tr[1])}`"
                  removable
                  @remove="store.removeTranslation(index)"
                />
              </div>
            </div>
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>

    <template #footer>
      <Button label="Close" icon="pi pi-check" @click="visible = false" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useStore } from '../store';
import { mande } from 'mande';
import Dialog from 'primevue/dialog';
import Tabs from 'primevue/tabs';
import TabList from 'primevue/tablist';
import Tab from 'primevue/tab';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';
import RadioButton from 'primevue/radiobutton';
import Listbox from 'primevue/listbox';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import Badge from 'primevue/badge';
import Chip from 'primevue/chip';

const store = useStore();

const visible = defineModel<boolean>('visible', { default: false });

const selectedStyle = ref(store.arabicTextType);
const selectedLanguage = ref<string | null>(null);
const bismillahPreviews = ref<Record<string, string>>({});
const textTypesData = ref<Record<string, string[]>>({});

// Computed: Available Arabic styles
const availableStyles = computed(() => store.availableTextTypes);

// Computed: Languages with translations
const languages = computed(() => {
  const langs: { code: string; name: string }[] = [];

  for (const [lang, translators] of Object.entries(textTypesData.value)) {
    if (lang !== 'arabic' && Array.isArray(translators) && translators.length > 0) {
      langs.push({
        code: lang,
        name: formatLanguageName(lang)
      });
    }
  }

  // Sort alphabetically by name
  return langs.sort((a, b) => a.name.localeCompare(b.name));
});

// Format style name for display
function formatStyleName(style: string): string {
  return style
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Format language name for display
function formatLanguageName(lang: string): string {
  const langNames: Record<string, string> = {
    english: 'English',
    urdu: 'Urdu',
    arabic: 'Arabic',
    persian: 'Persian/Farsi',
    turkish: 'Turkish',
    indonesian: 'Indonesian',
    malay: 'Malay',
    french: 'French',
    german: 'German',
    spanish: 'Spanish',
    russian: 'Russian',
    chinese: 'Chinese',
    japanese: 'Japanese',
    bengali: 'Bengali',
    hindi: 'Hindi',
    tamil: 'Tamil',
    thai: 'Thai',
    korean: 'Korean',
    dutch: 'Dutch',
    italian: 'Italian',
    portuguese: 'Portuguese',
    swedish: 'Swedish',
    bosnian: 'Bosnian',
    albanian: 'Albanian',
    azerbaijani: 'Azerbaijani',
    kazakh: 'Kazakh',
    kurdish: 'Kurdish',
    pashto: 'Pashto',
    sindhi: 'Sindhi',
    somali: 'Somali',
    swahili: 'Swahili',
    tajik: 'Tajik',
    tatar: 'Tatar',
    uzbek: 'Uzbek',
    uyghur: 'Uyghur',
    hausa: 'Hausa',
    yoruba: 'Yoruba',
    amharic: 'Amharic',
    divehi: 'Divehi',
    malayalam: 'Malayalam',
    telugu: 'Telugu',
    marathi: 'Marathi',
    gujarati: 'Gujarati',
    oromo: 'Oromo',
    assamese: 'Assamese',
    chechen: 'Chechen',
  };

  return langNames[lang.toLowerCase()] || lang.charAt(0).toUpperCase() + lang.slice(1);
}

// Format translator name for display
function formatTranslatorName(translator: string): string {
  return translator
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Get translators for a language
function getTranslatorsForLanguage(lang: string): string[] {
  return textTypesData.value[lang] || [];
}

// Get count of selected translations for a language
function getSelectedCountForLanguage(lang: string): number {
  return store.selectedTranslations.filter(tr => tr[0] === lang).length;
}

// Check if a translation is selected
function isTranslationSelected(lang: string, translator: string): boolean {
  return store.selectedTranslations.some(
    tr => tr[0] === lang && tr[1] === translator
  );
}

// Toggle translation selection
function toggleTranslation(lang: string, translator: string, selected: boolean) {
  if (selected) {
    store.addTranslation([lang, translator]);
  } else {
    const index = store.selectedTranslations.findIndex(
      tr => tr[0] === lang && tr[1] === translator
    );
    if (index !== -1) {
      store.removeTranslation(index);
    }
  }
}

// Clear all selected translations
function clearAllTranslations() {
  while (store.selectedTranslations.length > 0) {
    store.removeTranslation(0);
  }
}

// Select Arabic style
function selectStyle(style: string) {
  selectedStyle.value = style;
  store.setArabicTextType(style);
}

// Load Bismillah previews for all styles
async function loadBismillahPreviews() {
  if (availableStyles.value.length === 0) return;

  try {
    const stylesParam = availableStyles.value.map(s => `arabic:${s}`).join('_');
    const url = `${import.meta.env.VITE_API_BASE_URL}/text/1/${stylesParam}`;
    const api = mande(url);
    const response = await api.get() as any[];

    // Get first aya (Bismillah)
    if (response && response.length > 0) {
      const bismillah = response[0];
      if (bismillah.texts?.arabic) {
        bismillahPreviews.value = bismillah.texts.arabic;
      }
    }
  } catch (error) {
    console.error('Failed to load Bismillah previews:', error);
  }
}

// Load text types data
async function loadTextTypes() {
  try {
    const url = `${import.meta.env.VITE_API_BASE_URL}/text-types`;
    const api = mande(url);
    const response = await api.get() as Record<string, string[]>;
    textTypesData.value = response;
  } catch (error) {
    console.error('Failed to load text types:', error);
  }
}

// Watch for dialog visibility to load data
watch(visible, async (newValue) => {
  if (newValue) {
    selectedStyle.value = store.arabicTextType;

    if (Object.keys(textTypesData.value).length === 0) {
      await loadTextTypes();
    }

    if (Object.keys(bismillahPreviews.value).length === 0 && availableStyles.value.length > 0) {
      await loadBismillahPreviews();
    }
  }
});

// Load data when store text types are loaded
watch(() => store.availableTextTypes, async (newValue) => {
  if (newValue.length > 0 && Object.keys(bismillahPreviews.value).length === 0) {
    await loadBismillahPreviews();
  }
});

onMounted(async () => {
  if (store.availableTextTypes.length === 0) {
    await store.loadTextTypes();
  }
  await loadTextTypes();
});
</script>

<style>
.text-settings-dialog .p-dialog-content {
  padding: 0;
}

.text-settings-dialog .p-tabs {
  padding: 0;
}

.text-settings-dialog .p-tabpanels {
  padding: 1.5rem;
}

.text-settings-dialog .p-tablist {
  background: #f8f9fa;
}

.dark-mode .text-settings-dialog .p-tablist {
  background: #2d2d2d;
}

.section-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.dark-mode .section-description {
  color: #999;
}

/* Arabic Style Section */
.arabic-style-section {
  max-height: 500px;
  overflow-y: auto;
}

.style-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.style-option {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.style-option:hover {
  border-color: #81C784;
  background: rgba(76, 175, 80, 0.05);
}

.style-option.selected {
  border-color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
}

.dark-mode .style-option {
  border-color: #444;
}

.dark-mode .style-option:hover {
  border-color: #81C784;
  background: rgba(76, 175, 80, 0.15);
}

.dark-mode .style-option.selected {
  border-color: #4CAF50;
  background: rgba(76, 175, 80, 0.2);
}

.style-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.style-name {
  font-weight: 600;
  cursor: pointer;
}

.bismillah-preview {
  font-size: 1.5rem;
  line-height: 2;
  font-family: 'AlQalam', 'Amiri', serif;
  color: #1B5E20;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 4px;
}

.dark-mode .bismillah-preview {
  color: #81C784;
  background: rgba(0, 0, 0, 0.2);
}

/* Translations Section */
.translations-layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1rem;
  min-height: 300px;
}

@media (max-width: 600px) {
  .translations-layout {
    grid-template-columns: 1fr;
  }
}

.language-list,
.translator-list {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.dark-mode .language-list,
.dark-mode .translator-list {
  border-color: #444;
}

.list-header {
  padding: 0.75rem 1rem;
  font-weight: 600;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.dark-mode .list-header {
  background: #2d2d2d;
  border-color: #444;
}

.language-listbox {
  border: none !important;
  border-radius: 0 !important;
}

.language-listbox .p-listbox-option {
  padding: 0.75rem 1rem !important;
}

.language-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
}

.translators {
  padding: 0.5rem;
  max-height: 350px;
  overflow-y: auto;
}

.translator-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.translator-option:hover {
  background: rgba(76, 175, 80, 0.1);
}

.translator-name {
  cursor: pointer;
}

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  color: #999;
  gap: 0.5rem;
}

.no-selection i {
  font-size: 2rem;
}

/* Selected Summary */
.selected-summary {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.dark-mode .selected-summary {
  border-color: #444;
}

.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.selected-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
</style>
